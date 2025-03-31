import re
import json
import time
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from .models import Theater, Movie

# スクレイピング対象のURL
URLS = {
    "TOHO川崎": 'https://hlo.tohotheater.jp/net/schedule/010/TNPI2000J01.do',
    "TOHOららぽーと横浜": 'https://hlo.tohotheater.jp/net/schedule/036/TNPI2000J01.do'
}

def convert_time(time_str, base_date):
    """24時台の時刻を 00時台 に変換し、必要なら日付を翌日にする"""
    match = re.match(r'(\d{1,2}):(\d{2})', time_str)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if hour >= 24:
            base_date += timedelta(days=1)
            hour -= 24
        
        # 時刻を datetime 型で返す（dateとtimeの両方）
        return datetime.combine(base_date, datetime.min.time()).replace(hour=hour, minute=minute)
    print(f"【エラー】時間フォーマットが不正: {time_str}")
    return None

def toho_fetch_and_store_movie_schedules():
    """映画スケジュールを取得し、データベースに保存"""
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(10)

    threshold_date = datetime.today().date() - timedelta(days=7)
    Movie.objects.filter(date__lt=threshold_date).delete()

    for theater_name, url in URLS.items():
        print(f"アクセスするURL: {url}")
        match = re.search(r'\/(\d+)\/', url)
        if not match:
            print(f"【エラー】劇場IDがURLから取得できません: {url}")
            continue
        theater_id = match.group(1)
        theater, _ = Theater.objects.get_or_create(id_number=theater_id, name=theater_name)

        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        today = datetime.today().date()
        base_date = today

        movie_sections = soup.find_all('div', class_='schedule-body-section-item')
        for section in movie_sections:
            title_element = section.find('h5', class_='schedule-body-title')
            if title_element:
                movie_title = title_element.text.strip()
                start_times = section.find_all('span', class_='start')
                end_times = section.find_all('span', class_='end')

                for start, end in zip(start_times, end_times):
                    start_text = start.text.strip()
                    end_text = end.text.strip()

                    start_datetime = convert_time(start_text, base_date)
                    end_datetime = convert_time(end_text, base_date)

                    if start_datetime and end_datetime:
                        Movie.objects.get_or_create(
                            title=movie_title,
                            theater=theater,
                            date=start_datetime.date(),  # 日付部分を保存
                            start_time=start_datetime.time(),  # 時刻部分を保存
                            end_time=end_datetime.time(),  # 時刻部分を保存
                        )
                    else:
                        print(f"【スキップ】不正な時刻データ: {start_text}, {end_text}")

    driver.quit()

@csrf_exempt
def get_movie_schedule(request):
    if request.method == "POST":
        data = json.loads(request.body)
        movie_title = data.get("title", "").strip()

        if not movie_title:
            return JsonResponse({"error": "映画タイトルを入力してください"}, status=400)
        
        schedule = {}
        theaters = Theater.objects.all()

        for theater in theaters:
            movies = Movie.objects.filter(title__icontains=movie_title, theater=theater)

            if movies:
                theater_schedule = []
                for movie in movies:
                    movie_info = f"{movie.title}：{movie.start_time.strftime('%H:%M')}~{movie.end_time.strftime('%H:%M')}"
                    theater_schedule.append(movie_info)

                schedule[theater.name] = theater_schedule
            else:
                schedule[theater.name] = ["上映スケジュールが見つかりません"]

        return JsonResponse(schedule)
    
    return JsonResponse({"error": "POSTリクエストのみ受け付けています"})

def home(request):
    return HttpResponse("<h1>映画スケジュール</h1>")

# スケジュールを取得し、データベースに保存する処理を実行
toho_fetch_and_store_movie_schedules()

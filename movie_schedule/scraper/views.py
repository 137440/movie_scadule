import re
import json
import time
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChoromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from .models import Theater, Movie

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_schedule.settings')
django.setup()

# スクレイピング対象のURL
URLS = {
  "TOHOシネマズ すすきの": "https://hlo.tohotheater.jp/net/schedule/089/TNPI2000J01.do",
  "TOHOシネマズ おいらせ下田": "https://hlo.tohotheater.jp/net/schedule/049/TNPI2000J01.do",
  "TOHOシネマズ 秋田": "https://hlo.tohotheater.jp/net/schedule/050/TNPI2000J01.do",
  "TOHOシネマズ 仙台": "https://hlo.tohotheater.jp/net/schedule/078/TNPI2000J01.do",
  "TOHOシネマズ 日比谷": "https://hlo.tohotheater.jp/net/schedule/081/TNPI2000J01.do",
  "TOHOシネマズ 新宿": "https://hlo.tohotheater.jp/net/schedule/076/TNPI2000J01.do",
  "TOHOシネマズ 池袋": "https://hlo.tohotheater.jp/net/schedule/084/TNPI2000J01.do",
  "TOHOシネマズ 日本橋": "https://hlo.tohotheater.jp/net/schedule/073/TNPI2000J01.do",
  "TOHOシネマズ 上野": "https://hlo.tohotheater.jp/net/schedule/080/TNPI2000J01.do",
  "TOHOシネマズ 六本木ヒルズ": "https://hlo.tohotheater.jp/net/schedule/009/TNPI2000J01.do",
  "TOHOシネマズ 渋谷": "https://hlo.tohotheater.jp/net/schedule/043/TNPI2000J01.do",
  "TOHOシネマズ 西新井": "https://hlo.tohotheater.jp/net/schedule/040/TNPI2000J01.do",
  "TOHOシネマズ 南大沢": "https://hlo.tohotheater.jp/net/schedule/006/TNPI2000J01.do",
  "TOHOシネマズ 府中": "https://hlo.tohotheater.jp/net/schedule/012/TNPI2000J01.do",
  "TOHOシネマズ 立川立飛": "https://hlo.tohotheater.jp/net/schedule/085/TNPI2000J01.do",
  "TOHOシネマズ 錦糸町（楽天地・オリナス）": "https://hlo.tohotheater.jp/net/schedule/029/TNPI2000J01.do",
  "TOHOシネマズ ららぽーと船橋": "https://hlo.tohotheater.jp/net/schedule/018/TNPI2000J01.do",
  "TOHOシネマズ 市川コルトンプラザ": "https://hlo.tohotheater.jp/net/schedule/003/TNPI2000J01.do",
  "TOHOシネマズ 柏": "https://hlo.tohotheater.jp/net/schedule/077/TNPI2000J01.do",
  "TOHOシネマズ 八千代緑が丘": "https://hlo.tohotheater.jp/net/schedule/028/TNPI2000J01.do",
  "TOHOシネマズ 流山おおたかの森": "https://hlo.tohotheater.jp/net/schedule/035/TNPI2000J01.do",
  "TOHOシネマズ 市原": "https://hlo.tohotheater.jp/net/schedule/071/TNPI2000J01.do",
  "TOHOシネマズ 海老名": "https://hlo.tohotheater.jp/net/schedule/007/TNPI2000J01.do",
  "TOHOシネマズ 小田原": "https://hlo.tohotheater.jp/net/schedule/008/TNPI2000J01.do",
  "TOHOシネマズ 川崎": "https://hlo.tohotheater.jp/net/schedule/010/TNPI2000J01.do",
  "TOHOシネマズ ららぽーと横浜": "https://hlo.tohotheater.jp/net/schedule/036/TNPI2000J01.do",
  "TOHOシネマズ 上大岡": "https://hlo.tohotheater.jp/net/schedule/066/TNPI2000J01.do",
  "TOHOシネマズ ららぽーと富士見": "https://hlo.tohotheater.jp/net/schedule/075/TNPI2000J01.do",
  "TOHOシネマズ 宇都宮": "https://hlo.tohotheater.jp/net/schedule/015/TNPI2000J01.do",
  "TOHOシネマズ ひたちなか": "https://hlo.tohotheater.jp/net/schedule/024/TNPI2000J01.do",
  "TOHOシネマズ 水戸内原": "https://hlo.tohotheater.jp/net/schedule/025/TNPI2000J01.do",
  "TOHOシネマズ 甲府": "https://hlo.tohotheater.jp/net/schedule/067/TNPI2000J01.do",
  "TOHOシネマズ 赤池": "https://hlo.tohotheater.jp/net/schedule/079/TNPI2000J01.do",
  "TOHOシネマズ 津島": "https://hlo.tohotheater.jp/net/schedule/026/TNPI2000J01.do",
  "TOHOシネマズ 東浦": "https://hlo.tohotheater.jp/net/schedule/021/TNPI2000J01.do",
  "TOHOシネマズ 木曽川": "https://hlo.tohotheater.jp/net/schedule/016/TNPI2000J01.do",
  "TOHOシネマズ 浜松": "https://hlo.tohotheater.jp/net/schedule/004/TNPI2000J01.do",
  "TOHOシネマズ サンストリート浜北": "https://hlo.tohotheater.jp/net/schedule/039/TNPI2000J01.do",
  "TOHOシネマズ ららぽーと磐田": "https://hlo.tohotheater.jp/net/schedule/065/TNPI2000J01.do",
  "TOHOシネマズ 岐阜": "https://hlo.tohotheater.jp/net/schedule/020/TNPI2000J01.do",
  "TOHOシネマズ モレラ岐阜": "https://hlo.tohotheater.jp/net/schedule/030/TNPI2000J01.do",
  "TOHOシネマズ ファボーレ富山": "https://hlo.tohotheater.jp/net/schedule/053/TNPI2000J01.do",
  "TOHOシネマズ 高岡": "https://hlo.tohotheater.jp/net/schedule/054/TNPI2000J01.do",
  "TOHOシネマズ 上田": "https://hlo.tohotheater.jp/net/schedule/068/TNPI2000J01.do",
  "TOHOシネマズ 梅田": "https://hlo.tohotheater.jp/net/schedule/037/TNPI2000J01.do",
  "TOHOシネマズ なんば（本館・別館）": "https://hlo.tohotheater.jp/net/schedule/032/TNPI2000J01.do",
  "TOHOシネマズ 泉北": "https://hlo.tohotheater.jp/net/schedule/005/TNPI2000J01.do",
  "TOHOシネマズ 鳳": "https://hlo.tohotheater.jp/net/schedule/045/TNPI2000J01.do",
  "TOHOシネマズ くずはモール": "https://hlo.tohotheater.jp/net/schedule/072/TNPI2000J01.do",
  "TOHOシネマズ セブンパーク天美": "https://hlo.tohotheater.jp/net/schedule/086/TNPI2000J01.do",
  "TOHOシネマズ ららぽーと門真": "https://hlo.tohotheater.jp/net/schedule/088/TNPI2000J01.do",
  "TOHOシネマズ 二条": "https://hlo.tohotheater.jp/net/schedule/023/TNPI2000J01.do",
  "TOHOシネマズ 西宮OS": "https://hlo.tohotheater.jp/net/schedule/064/TNPI2000J01.do",
  "TOHOシネマズ 伊丹": "https://hlo.tohotheater.jp/net/schedule/038/TNPI2000J01.do",
  "TOHOシネマズ 橿原": "https://hlo.tohotheater.jp/net/schedule/013/TNPI2000J01.do",
  "TOHOシネマズ 岡南": "https://hlo.tohotheater.jp/net/schedule/031/TNPI2000J01.do",
  "TOHOシネマズ 緑井": "https://hlo.tohotheater.jp/net/schedule/019/TNPI2000J01.do",
  "TOHOシネマズ 高知": "https://hlo.tohotheater.jp/net/schedule/017/TNPI2000J01.do",
  "TOHOシネマズ 新居浜": "https://hlo.tohotheater.jp/net/schedule/048/TNPI2000J01.do",
  "TOHOシネマズ ららぽーと福岡": "https://hlo.tohotheater.jp/net/schedule/087/TNPI2000J01.do",
  "TOHOシネマズ 天神・ソラリア館": "https://hlo.tohotheater.jp/net/schedule/056/TNPI2000J01.do",
  "TOHOシネマズ 福津": "https://hlo.tohotheater.jp/net/schedule/069/TNPI2000J01.do",
  "TOHOシネマズ 直方": "https://hlo.tohotheater.jp/net/schedule/022/TNPI2000J01.do",
  "TOHOシネマズ 長崎": "https://hlo.tohotheater.jp/net/schedule/046/TNPI2000J01.do",
  "TOHOシネマズ 熊本サクラマチ": "https://hlo.tohotheater.jp/net/schedule/083/TNPI2000J01.do",
  "TOHOシネマズ 光の森": "https://hlo.tohotheater.jp/net/schedule/014/TNPI2000J01.do",
  "TOHOシネマズ はません": "https://hlo.tohotheater.jp/net/schedule/027/TNPI2000J01.do",
  "TOHOシネマズ 宇城": "https://hlo.tohotheater.jp/net/schedule/057/TNPI2000J01.do",
  "TOHOシネマズ 大分わさだ": "https://hlo.tohotheater.jp/net/schedule/055/TNPI2000J01.do",
  "TOHOシネマズ アミュプラザおおいた": "https://hlo.tohotheater.jp/net/schedule/074/TNPI2000J01.do",
  "TOHOシネマズ 与次郎": "https://hlo.tohotheater.jp/net/schedule/033/TNPI2000J01.do",
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

#TOHOのデータ取得・保存
def toho_fetch_and_store_movie_schedules():
    """映画スケジュールを取得し、データベースに保存"""
    service = ChoromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(1)

    # 古いデータ（1週間より前のデータ）を削除
    threshold_date = datetime.today().date() - timedelta(days=7)
    Movie.objects.filter(date__lt=threshold_date).delete()

    for theater_name, url in URLS.items():
        print(f"アクセスするURL: {url}")
        match = re.search(r'\/(\d+)\/', url)
        if not match:
            print(f"【エラー】劇場IDがURLから取得できません: {url}")
            continue
        theater_id = match.group(1)
        theater, _ = Theater.objects.update_or_create(id_number=theater_id, name=theater_name)

        driver.get(url)
        time.sleep(2)

        for day_offset in range(7 + 1):  # 今日を含む7日間
            base_date = datetime.today().date() + timedelta(days=day_offset)

            if day_offset != 0:
                # ▼▼ 日付変更のブラウザ操作コード ▼▼
                target_date_id = base_date.strftime("%Y%m%d")
                try:
                    tab = driver.find_element(By.ID, target_date_id)
                    driver.execute_script("arguments[0].click();", tab)
                    time.sleep(2)  # ページ切り替えの待機
                except Exception as e:
                    print(f"【スキップ】日付 {target_date_id} のタブが見つかりません: {e}")
                    continue

            soup = BeautifulSoup(driver.page_source, 'html.parser')
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
                                date=start_datetime.date(),
                                start_time=start_datetime.time(),
                                end_time=end_datetime.time(),
                            )
                        else:
                            print(f"【スキップ】不正な時刻データ: {start_text}, {end_text}")

    driver.quit()


#109のデータを取得・保存
def loq_fetch_and_store_movie_scadules():
    options = Options()
    options.headless = False
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    driver.get('https://109cinemas.net/kawasaki/')
    driver.implicitly_wait(10)

    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
    iframe = driver.find_element(By.TAG_NAME, 'iframe')
    driver.switch_to.frame(iframe)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    today = datetime.today().date()

    theater, _ = Theater.objects.update_or_create(name="109シネマズ川崎")

    for article in soup.find_all('article'):
        title_element = article.find('h2')
        if not title_element:
            continue
        movie_title = title_element.text.strip()

        # 開始時刻と終了時刻を空リストで初期化
        start_times = []
        end_times = []

        # 開始時刻と終了時刻を取得
        start_times = [start_time.text.strip() for start_time in article.find_all('time', class_='start')]
        end_times = [end_time.text.strip() for end_time in article.find_all('time', class_='end')]

        # 開始時刻または終了時刻が空の場合はスキップ
        if not start_times or not end_times:
            print(f"【スキップ】開始時刻または終了時刻が見つかりませんでした: {movie_title}")
            continue

        # start_times と end_times を結びつけて、映画スケジュールをデータベースに保存
        for start_text, end_text in zip(start_times, end_times):
            start_datetime = convert_time(start_text, today)
            end_datetime = convert_time(end_text, today)

            if start_datetime and end_datetime:
                Movie.objects.get_or_create(
                    title=movie_title,
                    theater=theater,
                    date=start_datetime.date(),
                    start_time=start_datetime.time(),
                    end_time=end_datetime.time(),
                )
            else:
                print(f"【スキップ】不正な時刻データ: {start_text}, {end_text}")

    driver.quit()

#入力を受け取り、結果を返す
@csrf_exempt
def get_movie_schedule(request):
    if request.method == "POST":
        data = json.loads(request.body)
        movie_title = data.get("title", "").strip()
        date_str = data.get("date","").strip()

        if not movie_title:
            return JsonResponse({"error": "映画タイトルを入力してください"}, status=400)
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "日付の形式が不正です。"}, status=400)
        
        schedule = {}
        theaters = Theater.objects.all()

        for theater in theaters:
            movies = Movie.objects.filter(
                title__icontains=movie_title,
                theater=theater,
                date = selected_date,
                )

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
loq_fetch_and_store_movie_scadules()

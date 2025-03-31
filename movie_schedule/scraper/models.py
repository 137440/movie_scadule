from django.db import models

# Create your models here.
class Theater(models.Model):
    id_number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name} ({self.id_number})"
    
class Movie(models.Model):
    title = models.CharField(max_length=255)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    date = models.DateField()  # 日付
    start_time = models.TimeField()  # 開始時刻
    end_time = models.TimeField()  # 終了時刻

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = self.start_time.date()  # start_time から date を自動設定
        super().save(*args, **kwargs)

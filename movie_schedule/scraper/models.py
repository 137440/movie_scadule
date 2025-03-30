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
    start_time = models.TimeField() 
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.title} ({self.theater.name}) - {self.start_time} ～ {self.end_time}"
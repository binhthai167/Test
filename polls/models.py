from django.db import models
import datetime
from django.utils import timezone
from django.contrib import admin
# Create your models here.
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    def __str__(self):
        return self.question_text

class Choice(models.Model):
    CHOICE_LABELS = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    label = models.CharField(max_length=1, choices=CHOICE_LABELS, default='A')
    is_correct = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        # Nếu is_correct=True, thì reset tất cả các Choice khác của cùng câu hỏi về False
        if self.is_correct:
            Choice.objects.filter(question=self.question, is_correct=True).update(is_correct=False)
        super().save(*args, **kwargs)
    def __str__(self):
         return f"{self.label}. {self.choice_text}"
class ExamResult(models.Model):
    username = models.CharField(max_length=100)
    score = models.IntegerField()
    submit_time = models.DateTimeField(auto_now_add=True)
    passed = models.BooleanField(default=False)  # Thêm trường này

    def __str__(self):
        return f"{self.username}: {self.score} ({self.submit_time}) ({'O' if self.passed else 'X'})"
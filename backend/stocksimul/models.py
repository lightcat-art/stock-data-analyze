from django.db import models
from django.conf import settings
from django.utils import timezone


# Model을 정의함으로써 장고는 Post메소드가 데이터베이스에 저장되어야 한다고 알게됨.
class StockSimulParam(models.Model):
    # 글자수가 제한된 텍스트 정의 ( 글 제목같은 짧은 문자열)
    event_name = models.CharField(max_length=200)
    # 시뮬레이션 기간
    days = models.IntegerField(default=1)
    # 날짜와 시간 정의
    start_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.event_name
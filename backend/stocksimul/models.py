from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint
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


class StockSimulResult(models.Model):
    stock_simul_param_id = models.ForeignKey("StockSimulParam", on_delete=models.CASCADE)
    event_code = models.CharField(max_length=10)
    event_name = models.CharField(max_length=200)
    max_rate = models.FloatField(default=0)
    max_days_taken = models.IntegerField(default=0)
    min_rate = models.FloatField(default=0)
    min_days_taken = models.IntegerField(default=0)


class StockPrice(models.Model):
    # 기본적으로 django가 auto-increment id를 생성하기 때문에, 명시적으로 생성할 pk에는 primary_key 옵션을 넣어주어야 한다.
    stock_price_id = models.BigAutoField(primary_key=True)
    event_code = models.CharField(max_length=10)
    date = models.DateField()
    open = models.IntegerField(default=-1)
    close = models.IntegerField(default=-1)
    high = models.IntegerField(default=-1)
    low = models.IntegerField(default=-1)
    volume = models.IntegerField(default=-1)

    objects = models.Manager()
    class Meta:
        index_together = [("event_code", "date"),]

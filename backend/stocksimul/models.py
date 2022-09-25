from django.db import models
from django.conf import settings
from django.db.models import UniqueConstraint
from django.utils import timezone


# Model을 정의함으로써 장고는 Post메소드가 데이터베이스에 저장되어야 한다고 알게됨.
class StockSimulParam(models.Model):
    # event_choices = (('삼성전자','삼성전자'),('삼성생명','삼성생명'))
    # event_name = models.CharField(max_length=200, choices=event_choices)
    # 글자수가 제한된 텍스트 정의 ( 글 제목같은 짧은 문자열)
    event_name = models.CharField(max_length=200)
    # 시뮬레이션 기간
    days = models.IntegerField(default=1)
    # 날짜와 시간 정의
    start_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.event_name


class StockEvent(models.Model):
    stock_event_id = models.BigAutoField(primary_key=True)
    event_code = models.CharField(max_length=10)
    event_name = models.CharField(max_length=200)

    objects = models.Manager()


class StockSimulResult(models.Model):
    stock_simul_param = models.ForeignKey("StockSimulParam", on_delete=models.CASCADE)
    stock_event = models.ForeignKey("StockEvent", on_delete=models.CASCADE)
    max_rate = models.FloatField(default=0)
    max_days_taken = models.IntegerField(default=0)
    min_rate = models.FloatField(default=0)
    min_days_taken = models.IntegerField(default=0)


class StockPrice(models.Model):
    # 기본적으로 django가 auto-increment id를 생성하기 때문에, 명시적으로 생성할 pk에는 primary_key 옵션을 넣어주어야 한다.
    stock_price_id = models.BigAutoField(primary_key=True)
    stock_event = models.ForeignKey("StockEvent", on_delete=models.CASCADE)
    date = models.DateField()
    open = models.IntegerField(default=-1, null=True)
    close = models.IntegerField(default=-1, null=True)
    high = models.IntegerField(default=-1, null=True)
    low = models.IntegerField(default=-1, null=True)
    volume = models.IntegerField(default=-1, null=True)

    objects = models.Manager()

    class Meta:
        index_together = [("stock_event_id", "date"), ]


class StockInfoUpdateStatus(models.Model):
    stock_info_update_status_id = models.AutoField(primary_key=True)
    table_type = models.CharField(max_length=1)  # 'P' : 주가테이블, 'E' : 종목코드테이블
    detail_info_1 = models.BigIntegerField(null=True)  # 각 테이블 filtering에 필요한 big integer 정보 입력
    detail_info_2 = models.CharField(max_length=200, null=True)  # 각 테이블 filtering에 필요한 char 정보 입력
    mod_dt = models.DateField(default=timezone.now)
    reg_dt = models.DateField()

    objects = models.Manager()

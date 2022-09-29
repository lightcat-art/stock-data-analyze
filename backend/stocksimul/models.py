from django.db import models
from django.utils import timezone


# Model을 정의함으로써 장고는 Post메소드가 데이터베이스에 저장되어야 한다고 알게됨.
class StockSimulParam(models.Model):
    # event_choices = (('삼성전자','삼성전자'),('삼성생명','삼성생명'))
    # event_name = models.CharField(max_length=200, choices=event_choices)
    # 글자수가 제한된 텍스트 정의 ( 글 제목같은 짧은 문자열)
    event_name = models.CharField(max_length=200, help_text="종목명을 입력하세요")
    # 시뮬레이션 기간
    days = models.PositiveIntegerField(help_text="시작날짜로부터 조회할 기간을 선택하세요")
    # 날짜와 시간 정의
    start_date = models.DateField(help_text="시작날짜를 선택하세요")

    def __str__(self):
        return self.event_name


class StockEvent(models.Model):
    stock_event_id = models.BigAutoField(primary_key=True)
    event_code = models.CharField(max_length=10)
    event_name = models.CharField(max_length=200)

    # def __str__(self):
    #     return self.event_name

    # class Meta:
    #     db_table = "stocksimul_stockevent"

    objects = models.Manager()


class StockSimulResult(models.Model):
    # 데이터 누락을 방지하기 위해 fk 설정
    stock_simul_param = models.ForeignKey("StockSimulParam", on_delete=models.CASCADE)
    stock_event = models.ForeignKey("StockEvent", on_delete=models.CASCADE)
    max_rate = models.FloatField(default=0)
    max_days_taken = models.IntegerField(default=0)
    min_rate = models.FloatField(default=0)
    min_days_taken = models.IntegerField(default=0)


class StockPrice(models.Model):
    # 기본적으로 django가 auto-increment id를 생성하기 때문에, 명시적으로 생성할 pk에는 primary_key 옵션을 넣어주어야 한다.
    stock_price_id = models.BigAutoField(primary_key=True)
    # 데이터 누락을 방지하기 위해 fk 설정
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
    stock_event = models.ForeignKey("StockEvent", on_delete=models.CASCADE, null=True)
    mod_dt = models.DateField(default=timezone.now)
    reg_dt = models.DateField()

    objects = models.Manager()

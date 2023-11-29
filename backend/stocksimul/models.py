from django.db import models
from django.utils import timezone


# Model을 정의함으로써 장고는 Post메소드가 데이터베이스에 저장되어야 한다고 알게됨.
class SimulParam(models.Model):
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


class EventInfo(models.Model):
    stock_event_id = models.BigAutoField(primary_key=True)
    event_code = models.CharField(max_length=10)
    event_name = models.CharField(max_length=200)

    # def __str__(self):
    #     return self.event_name

    # class Meta:
    #     db_table = "stocksimul_stockevent"

    objects = models.Manager()


class SimulResult(models.Model):
    # 데이터 누락을 방지하기 위해 fk 설정
    stock_simul_param_id = models.IntegerField(default=-1)
    stock_event_id = models.IntegerField(default=-1)
    max_rate = models.FloatField(default=0)
    max_days_taken = models.IntegerField(default=0)
    min_rate = models.FloatField(default=0)
    min_days_taken = models.IntegerField(default=0)


class PriceInfo(models.Model):
    # 기본적으로 django가 auto-increment id를 생성하기 때문에, 명시적으로 생성할 pk에는 primary_key 옵션을 넣어주어야 한다.
    stock_price_id = models.BigAutoField(primary_key=True)
    stock_event_id = models.IntegerField(null=True)
    date = models.DateField()
    open = models.IntegerField(null=True)
    close = models.IntegerField(null=True)
    high = models.IntegerField(null=True)
    low = models.IntegerField(null=True)
    volume = models.IntegerField(null=True)
    value = models.BigIntegerField(null=True)
    up_down_rate = models.FloatField(null=True)

    objects = models.Manager()

    class Meta:
        # index_together = [("stock_event_id", "date"), ]
        indexes = [models.Index(fields=['stock_event_id'], name='idx_priceinfo_1')]


class NotAdjPriceInfo(models.Model):
    not_adj_price_id = models.BigAutoField(primary_key=True)
    stock_event_id = models.IntegerField(null=True)
    date = models.DateField()
    open = models.IntegerField(null=True)
    close = models.IntegerField(null=True)
    high = models.IntegerField(null=True)
    low = models.IntegerField(null=True)
    volume = models.IntegerField(null=True)
    value = models.BigIntegerField(null=True)
    up_down_rate = models.FloatField(null=True)
    market_cap = models.BigIntegerField(null=True)
    listed_shares = models.BigIntegerField(null=True)

    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['stock_event_id'], name='idx_notadj_priceinfo_1'),
            models.Index(fields=['stock_event_id', 'date'], name='idx_notadj_priceinfo_2'),
        ]


class InfoUpdateStatus(models.Model):
    stock_info_update_status_id = models.AutoField(primary_key=True)
    table_type = models.CharField(max_length=1)  # 'P' : 주가테이블, 'E' : 종목코드테이블, 'N' : KRX-API에서 가져온 미수정종가
    stock_event_id = models.IntegerField(null=True)

    update_type = models.CharField(max_length=1, default='N')  # N : 업데이트안됨, U : 업데이트완료
    mod_dt = models.DateField()
    reg_dt = models.DateField()

    objects = models.Manager()


class FundamentalInfo(models.Model):
    fm_info_id = models.AutoField(primary_key=True)
    stock_event_id = models.IntegerField(null=True)
    quarter = models.CharField(max_length=6, null=True)  # 분기명
    stock_tot_co = models.BigIntegerField(null=True)  # 총 발행 주식수
    cap = models.BigIntegerField(null=True)  # 시가총액
    eps = models.IntegerField(null=True)  # 주당순이익
    bps = models.IntegerField(blank=True, null=True)  # 주당순자산가치
    per = models.FloatField(null=True)
    pbr = models.FloatField(null=True)
    roe = models.FloatField(null=True)
    profit_loss = models.BigIntegerField(default=0)  # 당기순이익(손실)
    profit_loss_control = models.BigIntegerField(default=0)  # 당기순이익(손실지배)
    profit_loss_non_control = models.BigIntegerField(default=0)  # 당기순이익(손실비지배)
    profit_loss_before_tax = models.BigIntegerField(default=0)  # 세전계속사업이익
    assets = models.BigIntegerField(default=0)  # 자산총계
    current_assets = models.BigIntegerField(default=0)  # 유동자산
    non_current_assets = models.BigIntegerField(default=0)  # 비유동자산
    liabilities = models.BigIntegerField(default=0)  # 부채총계
    current_liabilities = models.BigIntegerField(default=0)  # 유동부채
    non_current_liabilities = models.BigIntegerField(default=0)  # 비유동부채
    equity = models.BigIntegerField(default=0)  # 자본총계
    equity_control = models.BigIntegerField(default=0)  # 지배자본
    equity_non_control = models.BigIntegerField(default=0)  # 비지배자본
    revenue = models.BigIntegerField(default=0)  # 수익(매출액)
    cost_of_sales = models.BigIntegerField(default=0)  # 매출원가 /영업비용(판관비 포함)
    gross_profit = models.BigIntegerField(default=0)  # 매출총이익
    operating_income_loss = models.BigIntegerField(default=0)  # 영업이익
    investing_cash_flow = models.BigIntegerField(default=0)  # 투자활동현금흐름
    operating_cash_flow = models.BigIntegerField(default=0)  # 영업활동현금흐름
    financing_cash_flow = models.BigIntegerField(default=0)  # 재무활동현금흐름

    objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['stock_event_id'], name='idx_fundinfo_1'),
            models.Index(fields=['stock_event_id', 'quarter'], name='idx_fundinfo_2'),
        ]

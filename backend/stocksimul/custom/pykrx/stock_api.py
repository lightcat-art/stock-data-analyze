from pykrx.website import krx, naver
import datetime
from pandas import DataFrame
import re
from pykrx.stock.stock_api import get_market_ticker_name, resample_ohlcv, market_valid_check, \
    get_nearest_business_day_in_a_week
from . import wrap


# 기본적으로 krx로 요청하는 변형함수
def get_market_ohlcv_by_date(
        fromdate: str, todate: str, ticker: str, freq: str = 'd',
        name_display: bool = False) -> DataFrame:
    """특정 종목의 일자별로 정렬된 OHLCV

    Args:
        fromdate     (str           ): 조회 시작 일자 (YYYYMMDD)
        todate       (str           ): 조회 종료 일자 (YYYYMMDD)
        ticker       (str           ): 조회할 종목의 티커
        freq         (str,  optional): d - 일 / m - 월 / y - 년
        adjusted     (bool, optional): 수정 종가 여부 (True/False)
        name_display (bool, optional): columns의 이름 출력 여부 (True/False)

    Returns:
        DataFrame:

            >> get_market_ohlcv_by_date("20210118", "20210126", "005930")

                         시가   고가   저가   종가    거래량
            날짜
            2021-01-18  86600  87300  84100  85000  43227951
            2021-01-19  84500  88000  83600  87000  39895044
            2021-01-20  89000  89000  86500  87200  25211127
            2021-01-21  87500  88600  86500  88100  25318011
            2021-01-22  89000  89700  86800  86800  30861661
    """

    if isinstance(fromdate, datetime.datetime):
        fromdate = krx.datetime2string(fromdate)

    if isinstance(todate, datetime.datetime):
        todate = krx.datetime2string(todate)

    fromdate = fromdate.replace("-", "")
    todate = todate.replace("-", "")

    df = wrap.get_market_ohlcv_by_date_all(fromdate, todate, ticker, False)

    if name_display:
        df.columns.name = get_market_ticker_name(ticker)

    how = {
        '시가': 'first',
        '고가': 'max',
        '저가': 'min',
        '종가': 'last',
        '거래량': 'sum'
    }

    return resample_ohlcv(df, freq, how)


@market_valid_check()
def get_market_ohlcv_by_ticker(
        date, market: str = "KOSPI", alternative: bool = False) -> DataFrame:
    """티커별로 정리된 전종목 OHLCV

    Args:
        date        (str           ): 조회 일자 (YYYYMMDD)
        market      (str           ): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL)
        alternative (bool, optional): 휴일일 경우 이전 영업일 선택 여부

    Returns:
        DataFrame:

            >> get_market_ohlcv_by_ticker("20210122")

                      시가    고가    저가    종가   거래량     거래대금     등락률   시가총액    상장주식수  시장
            티커
            095570    4190    4245    4160    4210   216835    910274405   0.839844
            006840   25750   29550   25600   29100   727088  20462325950  12.570312
            027410    5020    5250    4955    5220  1547629   7990770515   4.191406
            282330  156500  156500  151500  152000    62510   9555364000  -2.560547

            >> get_market_ohlcv_by_ticker("20210122", "KOSDAQ")

                      시가    고가    저가    종가   거래량     거래대금    등락률    시가총액    상장주식수  시장
            티커
            060310    2265    2290    2225    2255   275425    619653305 -0.219971 
            054620    7210    7250    7030    7120   124636    883893780 -1.110352
            265520   25850   25850   25200   25400   196384   4994644750 -0.779785
            211270   10250   10950   10050   10350  1664154  17351956900  1.469727
            035760  165200  166900  162600  163800   179018  29574003100  0.429932

        NOTE: 거래정지 종목은 종가만 존재하며 나머지는 0으로 채워진다.
    """  # pylint: disable=line-too-long # noqa: E501

    if isinstance(date, datetime.datetime):
        date = krx.datetime2string(date)

    date = date.replace("-", "")

    df = wrap.get_market_ohlcv_by_ticker_all(date, market)
    holiday = (df[['시가', '고가', '저가', '종가']] == 0).all(axis=None)
    if holiday and alternative:
        target_date = get_nearest_business_day_in_a_week(date=date, prev=True)
        df = wrap.get_market_ohlcv_by_ticker_all(target_date, market)
    return df

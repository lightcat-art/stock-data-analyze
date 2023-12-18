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

                      시가    고가    저가    종가   거래량     거래대금     등락률   시가총액    상장주식수  시장 등락유형 등락폭
            티커
            095570    4190    4245    4160    4210   216835    910274405   0.839844
            006840   25750   29550   25600   29100   727088  20462325950  12.570312
            027410    5020    5250    4955    5220  1547629   7990770515   4.191406
            282330  156500  156500  151500  152000    62510   9555364000  -2.560547

            >> get_market_ohlcv_by_ticker("20210122", "KOSDAQ")

                      시가    고가    저가    종가   거래량     거래대금    등락률    시가총액    상장주식수  시장 등락유형 등락폭
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


@market_valid_check()
def get_exhaustion_rates_of_foreign_investment_by_ticker(
    date: str, market: str = "KOSPI", balance_limit: bool = False) \
        -> DataFrame:
    """특정 시장에서 티커로 정렬된 외국인 보유량 조회

    Args:
        date          (str ): 조회 시작 일자 (YYYYMMDD)
        market        (str ): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL)
        balance_limit (bool): 외국인보유제한종목
            - False : check X
            - True  : check O

    Returns:
        DataFrame:
                   상장주식수   보유수량     지분율   한도수량 한도소진율
            티커
            003490   94844634   12350096  13.023438   47412833  26.046875
            003495    1110794      29061   2.619141     555286   5.230469
            015760  641964077  127919592  19.937500  256785631  49.812500
            017670   80745711   28962369  35.875000   39565398  73.187500
            020560  223235294   13871465   6.210938  111595323  12.429688
    """

    if isinstance(date, datetime.datetime):
        date = wrap.datetime2string(date)

    date = date.replace("-", "")

    return wrap.get_exhaustion_rates_of_foreign_investment_by_ticker(
        date, market, balance_limit)


def get_index_ohlcv_by_ticker(
        date, market: str = "KOSPI", alternative: bool = False):
    """티커별로 정리된 전종목 OHLCV

    Args:
        date   (str): 조회 일자 (YYYYMMDD)
        market (str): 조회 시장 (KOSPI/KOSDAQ/KRX/테마/ALL)
        alternative (bool, optional): 휴일일 경우 이전 영업일 선택 여부

    Returns:
        DataFrame:

            >> get_index_ohlcv_by_ticker("20210122")

                                    시가      고가       저가     종가      거래량        거래대금  상장시가총액  
                                                                                                    등락유형 등락폭 등락률
            지수명
            코스피외국주포함        0.00      0.00      0.00      0.00  1111222984  24305355507985
            코스피               3163.83   3185.26   3140.60   3140.63  1110004515  24300291238350
            코스피200             430.73    433.84    427.13    427.13   269257473  19087641760593
            코스피100            3295.34   3318.12   3266.10   3266.10   164218193  15401724965613
            코스피50             3034.99   3055.71   3008.02   3008.02   110775949  13083864634083

            >> get_index_ohlcv_by_ticker("20210122", "KOSDAQ")

                                    시가      고가      저가       종가      거래량        거래대금  상장시가총액  
                                                                                                    등락유형 등락폭 등락률
            지수명
            코스닥외국주포함         0.00      0.00      0.00      0.00  2288183346  15030875451228
            코스닥지수             982.20    984.67    975.05    979.98  2228382472  14929462086998
            코스닥150             1495.47   1501.68   1482.26   1492.01   104675565   3789026943821
            코스닥150정보기술      868.99    873.55    852.24    852.71    37578587    998283997365
            코스닥150헬스케어     4928.03   4974.17   4855.87   4949.63    21481119   1364482054586

        NOTE: 거래정지 종목은 종가만 존재하며 나머지는 0으로 채워진다.
    """  # pylint: disable=line-too-long # noqa: E501

    if isinstance(date, datetime.datetime):
        date = krx.datetime2string(date)

    date = date.replace("-", "")

    df = krx.get_index_ohlcv_by_ticker(date, market)
    holiday = (df[['시가', '고가', '저가', '종가']] == 0).all(axis=None)
    if holiday and alternative:
        target_date = get_nearest_business_day_in_a_week(date=date, prev=True)
        df = krx.get_index_ohlcv_by_ticker(target_date, market)
    return df
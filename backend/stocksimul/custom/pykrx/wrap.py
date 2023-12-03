from pykrx.website.comm import dataframe_empty_handler
from pykrx.website.krx.market.ticker import get_stock_ticker_isin
from pykrx.website.krx.market.core import (
    개별종목시세, 전종목등락률, PER_PBR_배당수익률_전종목,
    PER_PBR_배당수익률_개별, 전종목시세, 외국인보유량_개별추이,
    외국인보유량_전종목, 투자자별_순매수상위종목,
    투자자별_거래실적_개별종목_기간합계,
    투자자별_거래실적_개별종목_일별추이_일반,
    투자자별_거래실적_개별종목_일별추이_상세,
    투자자별_거래실적_전체시장_기간합계, 업종분류현황,
    투자자별_거래실적_전체시장_일별추이_일반, 개별종목_공매도_거래_전종목,
    투자자별_거래실적_전체시장_일별추이_상세, 개별종목_공매도_종합정보,
    개별종목_공매도_거래_개별추이, 투자자별_공매도_거래, 전종목_공매도_잔고,
    개별종목_공매도_잔고, 공매도_거래상위_50종목, 공매도_잔고상위_50종목,
    전체지수기본정보, 개별지수시세, 전체지수등락률, 전체지수시세, 지수구성종목,
    PER_PBR_배당수익률_전지수, PER_PBR_배당수익률_개별지수, 기업주요변동사항
)

import numpy as np
import pandas as pd
from pandas import Series, DataFrame


@dataframe_empty_handler
def get_market_ohlcv_by_date_all(fromdate: str, todate: str, ticker: str,
                             adjusted: bool = True) -> DataFrame:
    """일자별로 정렬된 특정 종목의 OHLCV

    Args:
        fromdate    (str): 조회 시작 일자 (YYYYMMDD)
        todate      (str): 조회 종료 일자 (YYYYMMDD)
        ticker      (str): 조회 종목의 ticker
        adjusted    (bool, optional): 수정 종가 여부 (True/False)

    Returns:
        DataFrame:

        >> get_market_ohlcv_by_date("20150720", "20150810", "005930")

                           시가     고가     저가     종가  거래량      거래대금    등락률
            날짜
            2015-07-20  1291000  1304000  1273000  1275000  128928  165366199000 -2.300781
            2015-07-21  1275000  1277000  1247000  1263000  194055  244129106000 -0.939941
            2015-07-22  1244000  1260000  1235000  1253000  268323  333813094000 -0.790039
            2015-07-23  1244000  1253000  1234000  1234000  208965  259446564000 -1.519531
    """  # pylint: disable=line-too-long # noqa: E501

    isin = get_stock_ticker_isin(ticker)
    adjusted = 2 if adjusted else 1
    df = 개별종목시세().fetch(fromdate, todate, isin, adjusted)
    # FLUC_TP_CD : (1: up / 2:down / 3:same)
    df = df[['TRD_DD', 'TDD_OPNPRC', 'TDD_HGPRC', 'TDD_LWPRC', 'TDD_CLSPRC',
             'ACC_TRDVOL', 'ACC_TRDVAL', 'FLUC_RT', 'MKTCAP', 'LIST_SHRS']]
    df.columns = ['날짜', '시가', '고가', '저가', '종가', '거래량', '거래대금',
                  '등락률', '시가총액', '상장주식수']
    df = df.set_index('날짜')
    df.index = pd.to_datetime(df.index, format='%Y/%m/%d')
    df = df.replace(r'[^-\w\.]', '', regex=True)
    df = df.replace(r'\-$', '0', regex=True)
    df = df.replace('', '0')
    df = df.astype({"시가": np.int32, "고가": np.int32, "저가": np.int32,
                    "종가": np.int32, "거래량": np.int32, "거래대금": np.int64,
                    "등락률": np.float32})
    return df.sort_index()


@dataframe_empty_handler
def get_market_ohlcv_by_ticker_all(date: str, market: str = "KOSPI") -> DataFrame:
    """티커별로 정리된 전종목 OHLCV

    Args:
        date   (str): 조회 일자 (YYYYMMDD)
        market (str): 조회 시장 (KOSPI/KOSDAQ/KONEX/ALL)

    Returns:
        DataFrame:
                     시가   고가   저가   종가  거래량    거래대금
            티커
            060310   2150   2390   2150   2190  981348  2209370985
            095570   3135   3200   3100   3130   89871   282007385
            006840  17050  17200  16500  16500   30567   512403000
            054620   8550   8740   8400   8650  647596  5525789290
            265520  22150  23100  22050  22400  255846  5798313650
    """

    market2mktid = {
        "ALL": "ALL",
        "KOSPI": "STK",
        "KOSDAQ": "KSQ",
        "KONEX": "KNX"
    }

    df = 전종목시세().fetch(date, market2mktid[market])
    df = df[['ISU_SRT_CD', 'TDD_OPNPRC', 'TDD_HGPRC', 'TDD_LWPRC',
             'TDD_CLSPRC', 'ACC_TRDVOL', 'ACC_TRDVAL', 'FLUC_RT', 'MKTCAP', 'LIST_SHRS', 'MKT_NM']]
    df.columns = ['티커', '시가', '고가', '저가', '종가', '거래량', '거래대금',
                  '등락률', '시가총액', '상장주식수', '시장']
    df = df.replace(r'[^-\w\.]', '', regex=True)
    df = df.replace(r'\-$', '0', regex=True)
    df = df.replace('', '0')
    df = df.set_index('티커')
    df = df.astype({
        "시가": np.int32,
        "고가": np.int32,
        "저가": np.int32,
        "종가": np.int32,
        "거래량": np.int32,
        "거래대금": np.int64,
        "등락률": np.float32
    })
    return df

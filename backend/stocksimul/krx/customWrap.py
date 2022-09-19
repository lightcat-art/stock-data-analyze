from pykrx.website.comm import dataframe_empty_handler
from pykrx.website.krx.market.ticker import get_stock_ticker_isin, get_stock_ticekr_market
from pykrx.website.krx.market.core import (개별종목시세, 전종목등락률, PER_PBR_배당수익률_전종목,
                                           PER_PBR_배당수익률_개별, 전종목시세, 외국인보유량_개별추이,
                                           외국인보유량_전종목, 투자자별_순매수상위종목,
                                           투자자별_거래실적_개별종목_기간합계, 투자자별_거래실적_개별종목_일별추이_일반,
                                           투자자별_거래실적_개별종목_일별추이_상세, 투자자별_거래실적_전체시장_기간합계,
                                           투자자별_거래실적_전체시장_일별추이_일반, 투자자별_거래실적_전체시장_일별추이_상세)
from pykrx.website.krx.market.core import (개별종목_공매도_종합정보, 개별종목_공매도_거래_전종목, 개별종목_공매도_거래_개별추이,
                                           투자자별_공매도_거래, 전종목_공매도_잔고, 개별종목_공매도_잔고,
                                           공매도_거래상위_50종목, 공매도_잔고상위_50종목)
from pykrx.website.krx.market.core import (전체지수기본정보, 개별지수시세, 전체지수등락률, 지수구성종목)
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import datetime
from backend.stocksimul.util.typeUtil import *

@dataframe_empty_handler
def getMarketOhlcvByTicker(date, market: str="KOSPI") -> DataFrame:
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
    if isinstance(date, datetime.datetime):
        date = datetime2string(date)

    market = {"ALL": "ALL", "KOSPI": "STK", "KOSDAQ": "KSQ", "KONEX": "KNX"}[market]
    df = 전종목시세().fetch(date, market)
    df = df[['ISU_SRT_CD', 'ISU_ABBRV', 'TDD_OPNPRC', 'TDD_HGPRC', 'TDD_LWPRC', 'TDD_CLSPRC', 'ACC_TRDVOL', 'ACC_TRDVAL', 'FLUC_RT', 'MKTCAP']]
    df.columns = ['티커', '종목명', '시가', '고가', '저가', '종가', '거래량', '거래대금', '등락률', '시가총액']
    df = df.replace('[^-\w\.]', '', regex=True)
    df = df.replace('\-$', '0', regex=True)
    df = df.replace('', '0')
    df = df.set_index('티커')
    df = df.astype({
        "시가":np.int32, "고가":np.int32, "저가":np.int32, "종가":np.int32,
        "거래량":np.int32, "거래대금":np.int64, "등락률":np.float32 } )
    return df



if __name__ == "__main__":
    df = getMarketOhlcvByTicker("20210507",market="KOSPI")
    print(df)
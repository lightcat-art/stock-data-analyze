from pykrx.website import krx
from pykrx import stock
from datetime import timedelta, datetime


def get_market_ohlcv_by_date(fromdate, todate, ticker):
    price_info_df = stock.get_market_ohlcv_by_date(fromdate=fromdate, todate=todate,
                                               ticker=ticker)
    return price_info_df


if __name__ == "__main__":
    # df = get_market_ohlcv_by_date("20010101", "20190820", "005930")
    # df = get_market_ohlcv_by_date("20191220", "20200227", "000020")
    # df = get_market_ohlcv_by_date("19991220", "20191231", "008480")
    df = get_market_ohlcv_by_date("20230701", "20230702", "005930")
    print(len(df))
    # df = get_market_ohlcv_by_date("20211221", "20211222", "005930")
    # df = get_market_ohlcv_by_date("20200121", "20200222", "005930")
    print(df)
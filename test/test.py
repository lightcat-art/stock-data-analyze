from pykrx.website import krx
from pykrx import stock
import datetime
from backend.stocksimul.custom.opendartreader.dart import OpenDartReader


def get_market_ohlcv_by_date(fromdate, todate, ticker, adjusted):
    price_info_df = stock.get_market_ohlcv_by_date(fromdate=fromdate, todate=todate,
                                                   ticker=ticker, adjusted=adjusted)
    return price_info_df


def get_market_cap_by_date(fromdate, todate, ticker):
    print(stock.get_market_cap_by_date(fromdate, todate, ticker));


def test_datetime():
    today_org = datetime.datetime.now()
    print(today_org)
    reset_today = datetime.datetime.combine(datetime.date(today_org.year, today_org.month, today_org.day),
                                            datetime.time(12, 00, 00))
    print(reset_today)


def test_dict():
    dictionary = {'005930': '삼성전자', '000000': 'xxxxxx'}
    if '005930' in dictionary:
        print('ok')
        print(dictionary['005930'])


def dart_report():
    dart = OpenDartReader('69500f38022cc6f7d33956e4690d43499fa10423')
    report = dart.report('005930', '배당', 2023, reprt_code='11013')

    print(report)


def dart_finstate():
    dart = OpenDartReader('69500f38022cc6f7d33956e4690d43499fa10423')
    finstate = dart.finstate('삼성전자', 2023, reprt_code='11013')
    print(finstate)


def dart_finstate_all():
    dart = OpenDartReader('69500f38022cc6f7d33956e4690d43499fa10423')
    # finstate = dart.finstate_all('삼성전자', 2023, reprt_code='11013')
    finstate = dart.finstate_all('삼성전자', 2022, reprt_code='11014')
    print(finstate)


if __name__ == "__main__":
    # df = get_market_ohlcv_by_date("20010101", "20190820", "005930")
    # df = get_market_ohlcv_by_date("20191220", "20200227", "000020")
    # df = get_market_ohlcv_by_date("19991220", "20191231", "008480")
    # df = get_market_ohlcv_by_date("20230701", "20230702", "005930")
    # print(len(df))
    # df = get_market_ohlcv_by_date("20211221", "20211222", "005930")
    # df = get_market_ohlcv_by_date("19970101", "20230923", "005930", True)
    # print(df)

    get_market_cap_by_date('20221229','20221229','005930')
    # get_market_cap_by_date('20140101','20170101','018260')
    # dart_report()
    # dart_finstate()
    # dart_finstate_all()
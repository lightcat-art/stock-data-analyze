from ..custom.opendartreader.dart import OpenDartReader
from ..config import stockConfig
from pykrx import stock
from pykrx.website.krx.market import wrap
import pandas


class Core:
    def __init__(self):
        # self.dart = OpenDartReader(stockConfig.OPEN_DART_API_KEY)
        pass

    def stock_table(self, event_name, start_date, end_date):
        test_table = pandas.DataFrame({'data': [1, 2, 3, 4, 5], 'status': ['ok', 'ok', 'ok', 'ok', 'ok']})
        return test_table

    def stock_graph(self, event_code, start_date, end_date):

        codeDF = stock.get_market_ohlcv_by_date(start_date, end_date, event_code)

        return codeDF
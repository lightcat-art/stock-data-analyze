from datetime import datetime, timedelta
# from backend.stocksimul.opendart.dart import OpenDartReader
from pykrx import stock

class Core:
    def __init__(self):
        # dart = OpenDartReader(settings.OPEN_DART_API_KEY)
        pass

    def analyze(self, event_code, start_date, end_date):
        
        codeDF = stock.get_market_ohlcv_by_date(start_date, end_date, event_code)
        print(codeDF)


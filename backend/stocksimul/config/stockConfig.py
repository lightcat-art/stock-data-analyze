"""
used in analyzing
"""
FIELD_SCAN_PERIOD = 7
STOCK_SCAN_PERIOD = 50
USE_MONEY_PERCENT = 0.5
NAVER_COLUMN_SEPARATOR = '!@#'

# 과거의 데이터로 시뮬레이션
TEST_YN = False
TEST_FIELD_SCAN_PERIOD = 7  # 기준날짜 이전 몇일까지 코스피하락한 날짜를 뽑아낼지
TEST_SIMULATION_PERIOD = 70  # 기준날짜로부터 이후 시뮬레이션할 기간
TEST_START_DATE = '20180701'  # 기준날짜

# open dart api key
OPEN_DART_API_KEY = 'c7b16eb1d1497ef4219a393248a46fb44b61da6e'
# 종목정보 업데이트 날짜주기
EVENT_INFO_UPDATE_PERIOD = 9999
# 종목별 주가정보 업데이트 날짜주기
PRICE_INFO_UPDATE_PERIOD = 1

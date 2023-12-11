from datetime import timedelta, datetime

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
# 종목 업데이트 배치 실행 시간
BATCH_HOUR = 16
BATCH_MIN = 00
BATCH_SEC = 00

ETC_BATCH_HOUR = 16
ETC_BATCH_MIN = 1
ETC_BATCH_SEC = 00

INDIC_BATCH_HOUR = 16
INDIC_BATCH_MIN = 2
INDIC_BATCH_SEC = 00

# 운영
# BATCH_TEST = False  # 배치 테스트 여부 - True라면 init_batch와 daily_batch가 앱이 실행된 거의 직후 실행되도록 함.
# SKIP_MANAGE_EVENT_INIT = False  # 첫 insert 스킵 여부.
# BATCH_TEST_CODE_YN = False  # 테스트시 특정 코드만 진행 여부
# BATCH_TEST_CODE_LIST = ['005930','005935']  # 특정 종목 테스트 시 종목코드 지정
# ETC_FIRST_BATCH_TODATE = '20231122'  # ETC 배치 작업 시 첫 INSERT의 todate 조회날짜를 일괄적으로 맞추기 위해 최근날짜를 수기로 지정.
# FUND_RETRY = True  # 재무정보 배치 실행 시 계속 일정간격마다 실행하도록 수정.
# FUND_API_REQUEST_TERM = 0.5

# 개발
BATCH_TEST = False  # 배치 테스트 여부 - True라면 init_batch와 daily_batch가 앱이 실행된 거의 직후 실행되도록 함.
ETC_BATCH_IMMEDIATE = True  # krx-api 배치 테스트 여부 - True라면 init_batch와 daily_batch가 앱이 실행된 거의 직후 실행되도록 함.
SKIP_MANAGE_EVENT_INIT = False  # 추가할 종목이 있더라도 현재 DB에 등록된 종목만 사용하도록 INSERT 스킵여부 설부
BATCH_TEST_CODE_YN = False  # 테스트시 특정 코드만 진행 여부
BATCH_TEST_CODE_LIST = ['001260']  # 특정 종목 테스트 시 종목코드 지정
FIRST_BATCH_TODATE = '20231126'  # ETC 배치 작업 시 첫 INSERT의 todate 조회날짜를 일괄적으로 맞추기 위해 최근날짜를 수기로 지정.
FUND_SKIP_FINSTATE = False  # 재무제표 스킵여부
FUND_SKIP_CO = True  # 주식수 스킵여부
FUND_API_REQUEST_TERM = 0.5

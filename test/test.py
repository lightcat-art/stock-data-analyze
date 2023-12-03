from pykrx.website import krx
from pykrx import stock
import datetime
import OpenDartReader
from backend.stocksimul.custom.opendartreader.dart_manager import DartManager
from backend.stocksimul.custom.opendartreader.dart_config import DartFinstateConfig
from backend.stocksimul.custom import pykrx as stock_custom
import logging

logger = logging.getLogger('test')


def get_market_ohlcv_by_date(fromdate, todate, ticker, adjusted):
    start_time = datetime.datetime.now().timestamp()
    price_info_df = stock.get_market_ohlcv_by_date(fromdate=fromdate, todate=todate,
                                                   ticker=ticker, adjusted=adjusted)
    print('price_info = {}'.format(price_info_df))
    end_time = datetime.datetime.now().timestamp()
    time_taken = end_time - start_time
    print('time_taken : {}'.format(time_taken))
    return price_info_df


def get_market_cap_by_date(fromdate, todate, ticker):
    print(stock.get_market_cap_by_date(fromdate, todate, ticker));


def get_market_ticker():
    cur_date_str = datetime.datetime.now().strftime('%Y%m%d')
    market_event_info = krx.get_market_ticker_and_name(date=cur_date_str, market='ALL')
    return market_event_info


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


def calcQuarterCodeFromNumber(quarter: int = None):
    if quarter == '1':
        return '11013'
    elif quarter == '2':
        return '11012'
    elif quarter == '3':
        return '11014'
    elif quarter == '4':
        return '11011'


def dart_finstate_all(event_name: str = None, year: int = None, qt: str = None):
    reprt_code = calcQuarterCodeFromNumber(qt)
    finstate = None
    try:
        finstate = DartManager.instance().get_dart().finstate_all(event_name, year, reprt_code=reprt_code)
    except Exception as e:
        logger.exception('get finstate request over-limited')
    print(finstate)
    if finstate is not None:
        assets = int(
            finstate.loc[DartFinstateConfig().assets_condition(finstate)].iloc[0][DartFinstateConfig().column_amount])
        current_assets = int(
            finstate.loc[DartFinstateConfig().current_assets_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        non_current_assets = int(
            finstate.loc[DartFinstateConfig().non_current_assets_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        liabilities = int(
            finstate.loc[DartFinstateConfig().liabilities_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        current_liabilities = int(
            finstate.loc[DartFinstateConfig().current_liabilities_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        non_current_liabilities = int(
            finstate.loc[DartFinstateConfig().non_current_liabilities_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        equity = int(
            finstate.loc[DartFinstateConfig().equity_condition(finstate)].iloc[0][DartFinstateConfig().column_amount])
        equity_control = int(
            finstate.loc[DartFinstateConfig().equity_control_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        equity_non_control_org = \
            finstate.loc[DartFinstateConfig().equity_non_control_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount]
        equity_non_control = None if equity_non_control_org == '' else int(equity_non_control_org)
        revenue = int(
            finstate.loc[DartFinstateConfig().revenue_condition(finstate)].iloc[0][DartFinstateConfig().column_amount])
        cost_of_sales = int(
            finstate.loc[DartFinstateConfig().cost_of_sales_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        gross_profit = int(
            finstate.loc[DartFinstateConfig().gross_profit_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        operating_income_loss = int(
            finstate.loc[DartFinstateConfig().operating_income_loss_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        profit_loss = int(
            finstate.loc[DartFinstateConfig().profit_loss_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        profit_loss_control = int(
            finstate.loc[DartFinstateConfig().profit_loss_control_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        profit_loss_non_control = int(
            finstate.loc[DartFinstateConfig().profit_loss_non_control_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        profit_loss_before_tax = int(
            finstate.loc[DartFinstateConfig().profit_loss_before_tax_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        # eps = int(
        #     finstate.loc[DartFinstateConfig().eps_condition(finstate)].iloc[0][DartFinstateConfig().column_amount])
        investing_cash_flow = int(
            finstate.loc[DartFinstateConfig().investing_cash_flow_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        operating_cash_flow = int(
            finstate.loc[DartFinstateConfig().operating_cash_flow_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])
        financing_cash_flow = int(
            finstate.loc[DartFinstateConfig().financing_cash_flow_condition(finstate)].iloc[0][
                DartFinstateConfig().column_amount])

        print(
            'assets={}\n'
            'liabilities={}\n'
            'equity={}\n'
            'revenue={}\n'
            'profit_loss={}\n'
            'operating_income_loss={}\n'
            'profit_loss_control={}\n'
            'profit_loss_non_control={}\n'
            'profit_loss_before_tax={}\n'
            'investing_cash_flow={}\n'
            'operating_cash_flow={}\n'
            'financing_cash_flow={}\n'.format(assets, liabilities, equity, revenue, profit_loss, operating_income_loss,
                                              profit_loss_control, profit_loss_non_control, profit_loss_before_tax,
                                              investing_cash_flow, operating_cash_flow, financing_cash_flow
                                              ))


def get_stock_tot_qy_state(event_name: str = None, year: int = None, qt: str = None):
    reprt_code = calcQuarterCodeFromNumber(qt)
    stocktotco_state = None
    try:
        stocktotco_state = DartManager.instance().get_dart().report(event_name,
                                                                    '주식총수',
                                                                    year, reprt_code)
    except Exception as e:
        logger.exception('get finstate request over-limited')
    if stocktotco_state is not None:
        print(stocktotco_state)
        

def test_custom_krx_api():
    print(stock_custom.get_market_ohlcv_by_ticker(date='231122', market="ALL"))


def date_comparison():
    cur_date = datetime.datetime.now()
    before_date = datetime.datetime.now() - datetime.timedelta(hours=1)

    if cur_date.date() == before_date.date():
        print('same date')
    else:
        print('dif date')


def datetime_obj_check():
    print(type(datetime.datetime.now()))  # datetime.datetime object


def calFirstQuarterOfNextYear(qt: str):
    qt_origin = datetime.datetime.strptime(qt, '%Y%m')
    # 해당년도 1분기가 DB에 등록되어있는지 조회
    qt_1 = datetime.date(qt_origin.year + 1, 3, 1)
    return qt_1.strftime('%Y%m')


def strComparison(qt1, qt2):
    if qt1 <= qt2:
        print('{} is lower or same'.format(qt1))
    else:
        print('{} is lower'.format(qt2))


if __name__ == "__main__":
    get_stock_tot_qy_state('KG모빌리티', 2021, '1')
    """
    # assets 관련
    # dart_finstate_all('KG모빌리티', 2021, '1')
    """

    # equity / 매출 관련
    # 149까지
    # dart_finstate_all('AJ네트웍스', 2016, '1')  # 매출 총이익 누락 - 영업비용에 판관비 포함 (완료)
    # dart_finstate_all('CJ CGV', 2023, '3') # 매출액 매출원가 매출총이익 누락(완료)
    # dart_finstate_all('BGF에코머티리얼즈', 2018, '1') # 지배/비지배 누락(완료  -속성이 없음)
    # dart_finstate_all('CG인바이츠', 2016, '1')  # 자본 /비지배 /지배 간 계산이 맞지 않음 (완료 - dart_ContributedEquity 삭제)
    # dart_finstate_all('CJ 바이오사이언스', 2020, '4')  # 지배/비지배 누락(완료  -속성이 없음)
    # dart_finstate_all('CMG제약', 2016, '1')  # 지배/비지배 누락(완료) , 매출원가 매출총이익 누락(완료)
    # dart_finstate_all('CNH', 2016, '1')  # 매출총이익 누락 (완료 - 영업비용에 판관비 포함)
    # dart_finstate_all('DB하이텍', 2018, '2')  # 지배/비지배 누락(완료  -속성이 없음)
    # dart_finstate_all('DL이앤씨', 2021, '3')  # 지배 누락(완료 - 지배만 표준코드가 없음 - 직접 계산 필요)
    # dart_finstate_all('DRB동일', 2016, '1')  # 자본 /비지배 /지배 간 계산이 맞지 않음. (완료 - dart_ContributedEquity 삭제)
    # dart_finstate_all('DSEN', 2016, '1')  # 자본 /비지배 /지배 간 계산이 맞지 않음. (완료 - dart_ContributedEquity 삭제)
    # dart_finstate_all('DXVX', 2019, '3')  # 지배/비지배 누락 (완료  -속성이 없음)
    # dart_finstate_all('DMS', 2017, '2')  # 매출관련 모두 누락 (완료 - name 속성 추가)
    # dart_finstate_all('FSN', 2018, '1')  # 매출총이익 누락 (완료 - 영업비용에 판관비 포함)
    # dart_finstate_all('GRT', 2018, '4')  # 지배/비지배 누락 (완료 - 속성이 없음)
    # dart_finstate_all('GS건설', 2016, '1')  # 지배 누락 (완료 - 속성값이 불안정함(dart_ElementsOfOtherStockholdersEquity) - 직접 계산 필요)
    # dart_finstate_all('HB솔루션', 2021, '1')  # 지배/비지배 누락 (완료 -속성이 없음)
    # dart_finstate_all('HDC현대산업개발', 2019, '3')  # 지배/비지배 누락 (완료 -속성이 없음)
    # dart_finstate_all('HD현대중공업', 2022, '1')  # 지배/비지배 누락 (완료 -속성이 없음)
    # dart_finstate_all('HD한국조선해양', 2020, '1')  # 영업이익 누락 (완료 - name 속성 추가)
    # dart_finstate_all('HLB생명과학', 2016, '1')  # 자본 /비지배 /지배 간 계산이 맞지 않음. (완료 - dart_ContributedEquity 삭제)
    # dart_finstate_all('HLB생명과학', 2017, '4')  # 지배/비지배 누락( 완료 -속성이 없음)
    # dart_finstate_all('HLB이노베이션', 2016, '1')  # 비지배 누락 ( 지배속성이 잘못된것으로 확인 - dart_Contributed..삭제)
    # dart_finstate_all('HLB테라퓨틱스', 2016, '1')  # 자본 /비지배 /지배 간 계산이 맞지 않음. ( 지배계산이 잘못된것으로 확인 - dart_Contributed..삭제)
    # dart_finstate_all('HLB바이오스텝', 2020, '1')  # 매출원가 매출총이익 누락 (완료 - dart_OperatingExpenses 추가, 영업비용에 판관비 포함)
    # dart_finstate_all('HL만도', 2016, '1')  # 지배 누락 (완료  - 속성 없음)
    # dart_finstate_all('HL홀딩스', 2016, '1')  # 지배 누락 (완료  - 속성 없음)
    # dart_finstate_all('JW생명과학', 2017, '1')  # 지배/비지배 누락 , 매출관련 모두 누락 (완료 - 속성있는것들 추가)
    # dart_finstate_all('JW신약', 2017, '1')  # 자본 누락 ( name 속성 추가)
    # dart_finstate_all('JW중외제약', 2017, '1')  # 비지배 누락 ( 지배속성이 잘못된것으로 확인 - dart_Contributed..삭제)
    # dart_finstate_all('JW중외제약', 2017, '3')  # 지배/비지배 누락 ( 속성 없음)
    # dart_finstate_all('JW중외제약', 2021, '2')  # 지배 누락 ( 속성없음 계산필요)
    # dart_finstate_all('JW홀딩스', 2016, '1')  # 지배 누락(속성없음) , 매출액 /매출원가 /영업이익 누락(name 속성추가)
    # dart_finstate_all('KBI메탈', 2017, '1')  # 자본 누락(name 속성추가)
    # dart_finstate_all('KB오토시스', 2017, '1')  # 비지배누락( 지배속성이 잘못된것으로 확인 - dart_Contributed..삭제)
    # dart_finstate_all('KC그린홀딩스', 2017, '2')  # 지배누락(속성없음)
    # dart_finstate_all('KC그린홀딩스', 2017, '3')  # 매출액 매출원가 매출총이익 누락 (name 속성 추가, 영업비용으로 계산)
    # dart_finstate_all('KC코트렐', 2016, '1')  # 지배누락(속성없음), 매출액 매출원가 누락 (완료)
    # dart_finstate_all('KD', 2019, '1')  # 자본 지배누락 (자본 name 추가, 지배 속성없음)
    # dart_finstate_all('KG모빌리티', 2019, '1')  # 자본 비지배누락 (비지배는 계산산 0, 자본 name 속성 추가)
    # dart_finstate_all('웹스', 2022, '1')  # 지배 비지배 누락 (속성 없음)

    """
        # 149 KG케미칼 까지 당기순이익 관련 체크
    # dart_finstate_all('AJ네트웍스', 2021, '1')
    # dart_finstate_all('AJ네트웍스', 2021, '2')
    # dart_finstate_all('AK홀딩스', 2018, '1')
    # dart_finstate_all('BGF에코머티리얼즈', 2016, '1')
    # dart_finstate_all('BGF에코머티리얼즈', 2021, '1')
    # dart_finstate_all('CBI', 2022, '1')
    # dart_finstate_all('CG인바이츠', 2018, '1')
    # dart_finstate_all('CJ제일제당', 2018, '1')
    # dart_finstate_all('CJ프레시웨이', 2016, '1')
    # dart_finstate_all('CMG제약', 2018, '1')
    # dart_finstate_all('CNH', 2018, '1')
    # dart_finstate_all('CNT85', 2019, '1')
    # dart_finstate_all('CS', 2018, '1')
    # dart_finstate_all('CS홀딩스', 2016, '4')
    # dart_finstate_all('DB', 2018, '1')
    # dart_finstate_all('DGP', 2022, '3')
    # dart_finstate_all('DMS', 2017, '1')
    # dart_finstate_all('DRB동일', 2017, '1')
    # dart_finstate_all('DRB동일', 2017, '2')
    # dart_finstate_all('DSEN', 2022, '3')
    # dart_finstate_all('DXVX', 2019, '1')
    # dart_finstate_all('ES큐브', 2018, '1')
    # dart_finstate_all('GS건설', 2018, '2')
    # dart_finstate_all('GS글로벌', 2017, '2')
    # dart_finstate_all('GS리테일', 2019, '1')
    # dart_finstate_all('HB솔루션', 2022, '2')
    # dart_finstate_all('HDC', 2017, '1')
    # dart_finstate_all('HD한국조선해양', 2020, '1')
    # dart_finstate_all('HD현대에너지솔루션', 2020, '1')
    # dart_finstate_all('HD현대인프라코어', 2017, '1')
    # dart_finstate_all('HD현대중공업', 2022, '1')
    # dart_finstate_all('HJ중공업', 2023, '1')
    # dart_finstate_all('HK이노엔', 2022, '1')
    # dart_finstate_all('HLB생명과학', 2017, '1')
    # dart_finstate_all('HLB제약', 2019, '1')
    # dart_finstate_all('HL만도', 2021, '3')
    # dart_finstate_all('HRS', 2017, '1')
    # dart_finstate_all('HSD엔진', 2017, '1')
    # dart_finstate_all('JTC', 2019, '1')
    # dart_finstate_all('JW생명과학', 2023, '3')
    # dart_finstate_all('JW신약', 2017, '1')
    # dart_finstate_all('JW중외제약', 2017, '1')
    # dart_finstate_all('JW홀딩스', 2017, '1')
    # dart_finstate_all('JYP Ent.', 2017, '3')
    # dart_finstate_all('KBI메탈', 2017, '3')
    # dart_finstate_all('KD', 2022, '1')
    # dart_finstate_all('KG ETS', 2019, '1')
    # dart_finstate_all('KG모빌리언스', 2017, '1')
    # dart_finstate_all('KG모빌리티', 2018, '1')
    # dart_finstate_all('KG스틸', 2017, '1')
    """

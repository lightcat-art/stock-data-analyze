from pykrx.website import krx
from pykrx import stock
import datetime
import OpenDartReader
from backend.stocksimul.custom.opendartreader.dart_manager import DartManager
from backend.stocksimul.custom.opendartreader.dart_config import DartFinstateConfig, DartStockSharesConfig
from backend.stocksimul.custom import pykrx as stock_custom
import logging
import xml.etree.ElementTree as ET

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


def dart_finstate(event_name: str = None, year: int = None, qt: str = None):
    reprt_code = calcQuarterCodeFromNumber(qt)
    finstate = None
    try:
        finstate = DartManager.instance().get_dart().finstate(event_name, year, reprt_code=reprt_code)
    except Exception as e:
        logger.exception('get finstate request over-limited')
    print(finstate)
    if finstate is not None:
        pass


def get_stock_tot_qy_state(event_name: str = None, year: int = None, qt: str = None):
    reprt_code = calcQuarterCodeFromNumber(qt)
    shares = None
    try:
        shares = DartManager.instance().get_dart().report(event_name,
                                                          '주식총수',
                                                          year, reprt_code)
    except Exception as e:
        logger.exception('get finstate request over-limited')
    if shares is not None:
        try:
            stock_tot_co = 0  # 총 발행 주식수
            stock_normal_co = 0  # 보통주 발행 주식수
            stock_prior_co = 0  # 우선주 발행 주식수
            distb_stock_tot_co = 0  # 총 유통 주식수
            distb_stock_normal_co = 0  # 보통주 유통 주식수
            distb_stock_prior_co = 0  # 우선주 유통 주식수
            tes_stock_tot_co = 0  # 총 자기 주식수
            tes_stock_normal_co = 0  # 보통주 자기 주식수
            tes_stock_prior_co = 0  # 우선주 자기 주식수

            stock_tot_co_str = shares.loc[DartStockSharesConfig().tot_condition(shares)].iloc[0][
                DartStockSharesConfig().column_pub_stock]
            stock_normal_co = shares.loc[DartStockSharesConfig().normal_condition(shares)].iloc[0][
                DartStockSharesConfig().column_pub_stock]
            stock_prior_co = shares.loc[DartStockSharesConfig().prior_condition(shares)].iloc[0][
                DartStockSharesConfig().column_pub_stock]
            distb_stock_tot_co = shares.loc[DartStockSharesConfig().tot_condition(shares)].iloc[0][
                DartStockSharesConfig().column_dist_stock]
            distb_stock_normal_co = shares.loc[DartStockSharesConfig().normal_condition(shares)].iloc[0][
                DartStockSharesConfig().column_dist_stock]
            distb_stock_prior_co = shares.loc[DartStockSharesConfig().prior_condition(shares)].iloc[0][
                DartStockSharesConfig().column_dist_stock]
            tes_stock_tot_co = shares.loc[DartStockSharesConfig().tot_condition(shares)].iloc[0][
                DartStockSharesConfig().column_own_stock]
            tes_stock_normal_co = shares.loc[DartStockSharesConfig().normal_condition(shares)].iloc[0][
                DartStockSharesConfig().column_own_stock]
            tes_stock_prior_co = shares.loc[DartStockSharesConfig().prior_condition(shares)].iloc[0][
                DartStockSharesConfig().column_own_stock]
        except Exception as e:
            logger.exception('error occured')
            pass


def get_market_sector_classifications_test(date: str, market: str):
    print(stock.get_market_sector_classifications(date, market))


def get_market_price_change_by_ticker_test():
    stock.get_market_price_change_by_ticker(fromdate='20231201', todate='20231201', market="KOSPI")


def test_custom_krx_api_by_ticker():
    df = stock_custom.get_market_ohlcv_by_ticker(date='20231211', market="ALL")
    for k, v in df.to_dict('index').items():
        if k == '005930':
            print(v)
        elif k == '404950':
            print(v)

        # print('key = {}'.format(k))
        # print('value = {}, valueType = {}'.format(v, type(v)))
        #
        # v.pop('시장')
        # print('change value = {}'.format(v))


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


def flagComparison(code):
    ERROR = 2 ** 10
    EXECUTED = 2 ** 11
    print(code & (EXECUTED | ERROR))
    # if (code & (EXECUTED | ERROR)) != 0:
    #     print('')


def raiseExceptionTest():
    try:

        raise ValueError('value error')
    except ET.ParseError as e:
        pass
    result = 'result1'

    return result


def dartCorplist(corp_name):
    corp_code = DartManager.instance().get_dart().corp_codes
    print(type(corp_code))
    print(corp_code)
    # corp_code.set_index('corp_name')
    for k, v in corp_code.to_dict('index').items():
        if corp_name in v['corp_name']:
            print(v)


def digitTest(corp):  # type 자체가 int로들어가야하는것이 아닌 string에서 숫자만 들어가는지 아닌지 인식하는 메소드
    if corp.isdigit():
        print('digit')
    else:
        print('not digit')


def dicKeyTest():
    dic = {'status': 100, 'code': 124}
    if 'status' in dic:
        print('ok')


def mainIndicatorTest():
    indic_info_df = stock.get_market_fundamental_by_ticker(date='20231205', market='ALL')
    print(indic_info_df)


# 외국인 보유량 관련 체크
# balance_limit이 False라면 외국인 보유제한종목만 보여지게됨.
def get_exhaustion_rates_of_foreign_investment_by_ticker(date, market, balance_limit):
    df = None
    try:
        df = stock.get_exhaustion_rates_of_foreign_investment_by_ticker(date, market, balance_limit)
        print(len(df))
        df = df.reset_index()
        if (df['티커'] == '003495').any():
            print(df[df['티커'] == '003495'])
    except Exception as e:
        print(e)
    # print(df)


# 매수 매도량 조회
def get_market_net_purchases_of_equities(fromdate, todate, market, investor):
    stock.get_market_net_purchases_of_equities(fromdate, todate, market, investor)


def get_index_info(date, market):
    index_list = stock.get_index_ticker_list(date, market)
    for ticker in index_list:
        name = stock.get_index_ticker_name(ticker)
        event_list = stock.get_index_portfolio_deposit_file(date=date, ticker=ticker)
        print('ticker={}, name={}, event_list={}'.format(ticker, name, event_list))


def get_index_ohlc(date, market):
    print(stock.get_index_ohlcv_by_ticker(date=date, market=market))


if __name__ == "__main__":
    # get_market_sector_classifications_test("20231201", "KOSPI")
    # test_custom_krx_api_by_ticker()
    # get_exhaustion_rates_of_foreign_investment_by_ticker('20231214', 'ALL', True)
    # get_exhaustion_rates_of_foreign_investment_by_ticker('20231003', 'ALL', False)
    # get_index_info('20231214', 'KOSPI')
    # get_index_info('20231214', 'KOSDAQ')
    # get_index_info('20231214', 'KONEX')
    # get_index_info('20231214', '테마')

    get_index_ohlc('20231216', 'KOSPI')
    # get_index_ohlc('20231214', 'KOSDAQ')
    # get_index_ohlc('20231214', '테마')
    # get_index_ohlc('20231214', 'KRX')

    # flagComparison(2**11)
    # get_stock_tot_qy_state('삼성전자우', 2022, '1')
    # print(raiseExceptionTest())
    # dart_finstate('F&F홀딩스',2022,'3')
    # dartCorplist('BNK')
    # digitTest()
    # dart_finstate_all('138930', 2022, '1')  # 매출 총이익 누락 - 영업비용에 판관비 포함 (완료)'
    # dicKeyTest()
    # mainIndicatorTest()
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

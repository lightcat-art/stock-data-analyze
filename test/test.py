from pykrx.website import krx
from pykrx import stock
import datetime
from backend.stocksimul.custom.opendartreader.dart import OpenDartReader
from backend.stocksimul.custom.opendartreader.dart_manager import DartManager
from backend.stocksimul.custom.opendartreader.dart_config import DartConfig
from backend.stocksimul.custom import pykrx as stock_custom


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


def dart_finstate_all():
    finstate = DartManager.instance().get_dart().finstate_all('삼성전자', 2016, reprt_code='11012')
    print(finstate)
    if finstate is not None:
        assets = int(finstate.loc[DartConfig().assets_condition(finstate)].iloc[0][DartConfig().column_amount])
        liabilities = int(
            finstate.loc[DartConfig().liabilities_condition(finstate)].iloc[0][DartConfig().column_amount])
        equity = int(finstate.loc[DartConfig().equity_condition(finstate)].iloc[0][DartConfig().column_amount])
        revenue = int(finstate.loc[DartConfig().revenue_condition(finstate)].iloc[0][DartConfig().column_amount])
        profit_loss = int(
            finstate.loc[DartConfig().profit_loss_condition(finstate)].iloc[0][DartConfig().column_amount])
        operating_income_loss = int(finstate.loc[DartConfig().operating_income_loss_condition(finstate)].iloc[0][
                                        DartConfig().column_amount])
        profit_loss_control = int(finstate.loc[DartConfig().profit_loss_control_condition(finstate)].iloc[0][
                                      DartConfig().column_amount])
        profit_loss_non_control = int(finstate.loc[DartConfig().profit_loss_non_control_condition(finstate)].iloc[0][
                                          DartConfig().column_amount])
        profit_loss_before_tax = int(finstate.loc[DartConfig().profit_loss_before_tax_condition(finstate)].iloc[0][
                                         DartConfig().column_amount])
        eps = int(finstate.loc[DartConfig().eps_condition(finstate)].iloc[0][DartConfig().column_amount])
        investing_cash_flow = int(finstate.loc[DartConfig().investing_cash_flow_condition(finstate)].iloc[0][
                                      DartConfig().column_amount])
        operating_cash_flow = int(finstate.loc[DartConfig().operating_cash_flow_condition(finstate)].iloc[0][
                                      DartConfig().column_amount])
        financing_cash_flow = int(finstate.loc[DartConfig().financing_cash_flow_condition(finstate)].iloc[0][
                                      DartConfig().column_amount])

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
            'eps={}\n'
            'investing_cash_flow={}\n'
            'operating_cash_flow={}\n'
            'financing_cash_flow={}\n'.format(assets, liabilities, equity, revenue, profit_loss, operating_income_loss,
                                              profit_loss_control, profit_loss_non_control, profit_loss_before_tax, eps,
                                              investing_cash_flow, operating_cash_flow, financing_cash_flow
                                              ))


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
    print(type(datetime.datetime.now())) # datetime.datetime object


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
    # df = get_market_ohlcv_by_date("20211221", "20211222", "005930")
    # get_market_ohlcv_by_date("19900101", "19960101", "060310", False)

    # df = krx.get_market_ohlcv_by_ticker(date='20231119', market='ALL')
    # print(df)

    # date_comparison()
    # test_custom_krx_api()
    # datetime_obj_check()
    # print(calFirstQuarterOfNextYear('202311'))
    strComparison('202312','202409')
    strComparison('202312','202312')
    strComparison('202312','202303')

    # print(stock.get_market_ohlcv_by_ticker(date='20231119', market='ALL'))

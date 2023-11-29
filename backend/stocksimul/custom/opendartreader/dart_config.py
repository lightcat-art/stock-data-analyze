import enum


class DartConfig:
    column_amount = 'thstrm_amount'  # 금액 컬럼명
    column_standard_code = 'account_id'  # 표준계정코드 컬럼명
    column_account_nm = 'account_nm'  # 재무항목명

    column_table_type = 'sj_div'  # 표 종류 컬럼명
    table_type_bs = 'BS'  # 재무상태표
    table_type_is = 'IS'  # 손익계산서
    table_type_cis = 'CIS'  # 포괄손익계산서
    table_type_cf = 'CF'  # 현금흐름표

    assets_id_list = ['ifrs-full_Assets', 'ifrs_Assets']  # 자산총계
    assets_nm_list = ['자산총계']
    current_assets_id_list = ['ifrs-full_CurrentAssets', 'ifrs_CurrentAssets']  # 유동자산
    non_current_assets_id_list = ['ifrs-full_NoncurrentAssets', 'ifrs_NoncurrentAssets']  # 비유동자산

    liabilities_id_list = ['ifrs-full_Liabilities', 'ifrs_Liabilities']  # 부채총계
    current_liabilities_id_list = ['ifrs-full_CurrentLiabilities', 'ifrs_CurrentLiabilities']  # 유동부채
    non_current_liabilities_id_list = ['ifrs-full_NoncurrentLiabilities', 'ifrs_NoncurrentLiabilities']  # 비유동부채

    equity_id_list = ['ifrs-full_Equity', 'ifrs_Equity']  # 자본총계
    equity_nm_list = ['자본총계']
    equity_control_id_list = ['ifrs-full_EquityAttributableToOwnersOfParent',
                              'ifrs_EquityAttributableToOwnersOfParent']  # 지배기업 소유주지분
    equity_non_control_id_list = ['ifrs-full_NoncontrollingInterests', 'ifrs_NoncontrollingInterests']  # 비지배지분

    revenue_id_list = ['ifrs-full_Revenue', 'ifrs_Revenue']  # 수익(매출액)
    revenue_nm_list = ['영업수익', '매출액', 'I.매출액']

    cost_of_sales_id_list = ['ifrs-full_CostOfSales', 'ifrs_CostOfSales', 'dart_OperatingExpenses']  # 매출원가 / 영업비용(판관비포함)
    cost_of_sales_nm_list = ['영업비용', '매출원가', 'II.매출원가']

    gross_profit_id_list = ['ifrs-full_GrossProfit', 'ifrs_GrossProfit']  # 매출총이익
    gross_profit_nm_list = ['매출총이익', 'III.매출총이익', '매출 총이익']

    # total_sell_admin_expenses_id_list = ['dart_TotalSellingGeneralAdministrativeExpenses']  # 판매비와 관리비
    operating_income_loss_id_list = ['dart_OperatingIncomeLoss']  # 영업이익
    operating_income_loss_nm_list = ['IV.영업이익(손실)', '영업이익', '영업이익(손실)']

    profit_loss_id_list = ['ifrs-full_ProfitLoss', 'ifrs_ProfitLoss',
                           'ifrs_ProfitLossFromContinuingOperations',
                           'ifrs-full_ProfitLossFromContinuingOperations']  # 당기순이익
    profit_loss_nm_list = ['당기순이익', 'VI. 당기순이익(손실)', '반기순이익', '반기순이익(손실)', '분기순이익', '분기순이익(손실)']

    profit_loss_control_id_list = ['ifrs-full_ProfitLossAttributableToOwnersOfParent',
                                   'ifrs_ProfitLossAttributableToOwnersOfParent']  # 당기순이익(지배)
    profit_loss_control_nm_list = ['지배기업지분순이익(손실)', '지배기업지분순이익', '지배주주지분 당기순이익',
                                   '지배주주지분 반기순이익', '지배기업의 소유주 귀속 당기순이익',
                                   '지배기업의 소유주 귀속 반기순이익', '지배기업의 소유주에 귀속될 당기순이익',
                                   '지배기업의 소유주에게 귀속되는 당기순이익(손실)', '지배기업소유주지분순이익',
                                   '지배회사지분순이익']

    profit_loss_non_control_id_list = ['ifrs-full_ProfitLossAttributableToNoncontrollingInterests',
                                       'ifrs_ProfitLossAttributableToNoncontrollingInterests']  # 당기순이익(비지배)
    profit_loss_non_control_nm_list = ['비지배지분순이익(손실)', '비지배지분순이익', '비지배주주지분 당기순이익',
                                       '비지배주주지분 반기순이익', '비지배지분 귀속 당기순이익',
                                       '비지배지분 귀속 반기순이익', '비지배지분에 귀속될 당기순이익',
                                       '비지배지분에 귀속되는 당기순이익(손실)', '소수주주지분순이익(손실)']

    profit_loss_before_tax_id_list = ['ifrs-full_ProfitLossBeforeTax',
                                      'ifrs_ProfitLossBeforeTax']  # 세전계속사업이익(법인세비용차감전순이익)
    eps_id_list = ['ifrs-full_BasicEarningsLossPerShare', 'ifrs_BasicEarningsLossPerShare']  # 주당순이익
    investing_cash_flow_id_list = ['ifrs-full_CashFlowsFromUsedInInvestingActivities',
                                   'ifrs_CashFlowsFromUsedInInvestingActivities']  # 투자활동현금흐름
    operating_cash_flow_id_list = ['ifrs-full_CashFlowsFromUsedInOperatingActivities',
                                   'ifrs_CashFlowsFromUsedInOperatingActivities']  # 영업활동현금흐름
    financing_cash_flow_id_list = ['ifrs-full_CashFlowsFromUsedInFinancingActivities',
                                   'ifrs_CashFlowsFromUsedInFinancingActivities']  # 재무활동현금흐름

    def assets_condition(self, df):
        assets_id_condition = None
        for i, item in enumerate(self.assets_id_list):
            if assets_id_condition is not None:
                assets_id_condition = assets_id_condition | (df[self.column_standard_code] == item)
            else:
                assets_id_condition = df[self.column_standard_code] == item
        for i, item in enumerate(self.assets_nm_list):
            assets_id_condition = assets_id_condition | (df[self.column_account_nm] == item)
        return assets_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def current_assets_condition(self, df):
        current_assets_id_condition = None
        for i, item in enumerate(self.current_assets_id_list):
            if current_assets_id_condition is not None:
                current_assets_id_condition = current_assets_id_condition | (df[self.column_standard_code] == item)
            else:
                current_assets_id_condition = df[self.column_standard_code] == item
        return current_assets_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def non_current_assets_condition(self, df):
        non_current_assets_id_condition = None
        for i, item in enumerate(self.non_current_assets_id_list):
            if non_current_assets_id_condition is not None:
                non_current_assets_id_condition = non_current_assets_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                non_current_assets_id_condition = df[self.column_standard_code] == item
        return non_current_assets_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def liabilities_condition(self, df):
        liabilities_id_condition = None
        for i, item in enumerate(self.liabilities_id_list):
            if liabilities_id_condition is not None:
                liabilities_id_condition = liabilities_id_condition | (df[self.column_standard_code] == item)
            else:
                liabilities_id_condition = df[self.column_standard_code] == item
        return liabilities_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def current_liabilities_condition(self, df):
        current_liabilities_id_condition = None
        for i, item in enumerate(self.current_liabilities_id_list):
            if current_liabilities_id_condition is not None:
                current_liabilities_id_condition = current_liabilities_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                current_liabilities_id_condition = df[self.column_standard_code] == item
        return current_liabilities_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def non_current_liabilities_condition(self, df):
        non_current_liabilities_id_condition = None
        for i, item in enumerate(self.non_current_liabilities_id_list):
            if non_current_liabilities_id_condition is not None:
                non_current_liabilities_id_condition = non_current_liabilities_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                non_current_liabilities_id_condition = df[self.column_standard_code] == item
        return non_current_liabilities_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def equity_condition(self, df):
        equity_id_condition = None
        for i, item in enumerate(self.equity_id_list):
            if equity_id_condition is not None:
                equity_id_condition = equity_id_condition | (df[self.column_standard_code] == item)
            else:
                equity_id_condition = df[self.column_standard_code] == item
        for i, item in enumerate(self.equity_nm_list):
            equity_id_condition = equity_id_condition | (df[self.column_account_nm] == item)
        return equity_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def equity_control_condition(self, df):
        equity_control_id_condition = None
        for i, item in enumerate(self.equity_control_id_list):
            if equity_control_id_condition is not None:
                equity_control_id_condition = equity_control_id_condition | (df[self.column_standard_code] == item)
            else:
                equity_control_id_condition = df[self.column_standard_code] == item
        return equity_control_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def equity_non_control_condition(self, df):
        equity_non_control_id_condition = None
        for i, item in enumerate(self.equity_non_control_id_list):
            if equity_non_control_id_condition is not None:
                equity_non_control_id_condition = equity_non_control_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                equity_non_control_id_condition = df[self.column_standard_code] == item
        return equity_non_control_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def revenue_condition(self, df):
        revenue_id_condition = None
        for i, item in enumerate(self.revenue_id_list):
            if revenue_id_condition is not None:
                revenue_id_condition = revenue_id_condition | (df[self.column_standard_code] == item)
            else:
                revenue_id_condition = df[self.column_standard_code] == item
        for i, item in enumerate(self.revenue_nm_list):
            revenue_id_condition = revenue_id_condition | (df[self.column_account_nm] == item)
        return revenue_id_condition & ((df[self.column_table_type] == self.table_type_is) |
                                       (df[self.column_table_type] == self.table_type_cis))

    def cost_of_sales_condition(self, df):
        cost_of_sales_id_condition = None
        for i, item in enumerate(self.cost_of_sales_id_list):
            if cost_of_sales_id_condition is not None:
                cost_of_sales_id_condition = cost_of_sales_id_condition | (df[self.column_standard_code] == item)
            else:
                cost_of_sales_id_condition = df[self.column_standard_code] == item
        for i, item in enumerate(self.cost_of_sales_nm_list):
            cost_of_sales_id_condition = cost_of_sales_id_condition | (df[self.column_account_nm] == item)
        return cost_of_sales_id_condition & ((df[self.column_table_type] == self.table_type_is) |
                                             (df[self.column_table_type] == self.table_type_cis))

    def gross_profit_condition(self, df):
        gross_profit_id_condition = None
        for i, item in enumerate(self.gross_profit_id_list):
            if gross_profit_id_condition is not None:
                gross_profit_id_condition = gross_profit_id_condition | (df[self.column_standard_code] == item)
            else:
                gross_profit_id_condition = df[self.column_standard_code] == item
        for i, item in enumerate(self.gross_profit_nm_list):
            gross_profit_id_condition = gross_profit_id_condition | (df[self.column_account_nm] == item)
        return gross_profit_id_condition & ((df[self.column_table_type] == self.table_type_is) |
                                            (df[self.column_table_type] == self.table_type_cis))

    # def total_sell_admin_expenses_condition(self, df):
    #     total_sell_admin_expenses_id_condition = None
    #     for i, item in enumerate(self.total_sell_admin_expenses_id_list):
    #         if total_sell_admin_expenses_id_condition is not None:
    #             total_sell_admin_expenses_id_condition = total_sell_admin_expenses_id_condition | (
    #                         df[self.column_standard_code] == item)
    #         else:
    #             total_sell_admin_expenses_id_condition = df[self.column_standard_code] == item
    #     return total_sell_admin_expenses_id_condition & ((df[self.column_table_type] == self.table_type_is) |
    #                                                      (df[self.column_table_type] == self.table_type_cis))

    def operating_income_loss_condition(self, df):
        operating_income_loss_id_condition = None
        for i, item in enumerate(self.operating_income_loss_id_list):
            if operating_income_loss_id_condition is not None:
                operating_income_loss_id_condition = operating_income_loss_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                operating_income_loss_id_condition = df[self.column_standard_code] == item
        for i, item in enumerate(self.operating_income_loss_nm_list):
            operating_income_loss_id_condition = operating_income_loss_id_condition | (
                    df[self.column_account_nm] == item)
        return operating_income_loss_id_condition & ((df[self.column_table_type] == self.table_type_is) |
                                                     (df[self.column_table_type] == self.table_type_cis))

    def profit_loss_condition(self, df):
        profit_loss_id_condition = None
        for i, item in enumerate(self.profit_loss_id_list):
            if profit_loss_id_condition is not None:
                profit_loss_id_condition = profit_loss_id_condition | (df[self.column_standard_code] == item)
            else:
                profit_loss_id_condition = df[self.column_standard_code] == item
        for i, item in enumerate(self.profit_loss_nm_list):
            profit_loss_id_condition = profit_loss_id_condition | (df[self.column_account_nm] == item)
        return profit_loss_id_condition & ((df[self.column_table_type] == self.table_type_is) |
                                           (df[self.column_table_type] == self.table_type_cis))

    def profit_loss_before_tax_condition(self, df):
        profit_loss_before_tax_id_condition = None
        for i, item in enumerate(self.profit_loss_before_tax_id_list):
            if profit_loss_before_tax_id_condition is not None:
                profit_loss_before_tax_id_condition = profit_loss_before_tax_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                profit_loss_before_tax_id_condition = df[self.column_standard_code] == item
        return profit_loss_before_tax_id_condition & ((df[self.column_table_type] == self.table_type_is) |
                                                      (df[self.column_table_type] == self.table_type_cis))

    def profit_loss_control_condition(self, df):
        profit_loss_control_id_condition = None
        for i, item in enumerate(self.profit_loss_control_id_list):
            if profit_loss_control_id_condition is not None:
                profit_loss_control_id_condition = profit_loss_control_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                profit_loss_control_id_condition = df[self.column_standard_code] == item
        for i, item in enumerate(self.profit_loss_control_nm_list):
            profit_loss_control_id_condition = profit_loss_control_id_condition | (df[self.column_account_nm] == item)
        return profit_loss_control_id_condition & ((df[self.column_table_type] == self.table_type_is) |
                                                   (df[self.column_table_type] == self.table_type_cis))

    def profit_loss_non_control_condition(self, df):
        profit_loss_non_control_id_condition = None
        for i, item in enumerate(self.profit_loss_non_control_id_list):
            if profit_loss_non_control_id_condition is not None:
                profit_loss_non_control_id_condition = profit_loss_non_control_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                profit_loss_non_control_id_condition = df[self.column_standard_code] == item
        for i, item in enumerate(self.profit_loss_non_control_nm_list):
            profit_loss_non_control_id_condition = profit_loss_non_control_id_condition | (
                    df[self.column_account_nm] == item)
        return profit_loss_non_control_id_condition & ((df[self.column_table_type] == self.table_type_is) |
                                                       (df[self.column_table_type] == self.table_type_cis))

    def eps_condition(self, df):
        eps_id_condition = None
        for i, item in enumerate(self.eps_id_list):
            if eps_id_condition is not None:
                eps_id_condition = eps_id_condition | (df[self.column_standard_code] == item)
            else:
                eps_id_condition = df[self.column_standard_code] == item
        return eps_id_condition & ((df[self.column_table_type] == self.table_type_is) |
                                   (df[self.column_table_type] == self.table_type_cis))

    def investing_cash_flow_condition(self, df):
        investing_cash_flow_id_condition = None
        for i, item in enumerate(self.investing_cash_flow_id_list):
            if investing_cash_flow_id_condition is not None:
                investing_cash_flow_id_condition = investing_cash_flow_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                investing_cash_flow_id_condition = df[self.column_standard_code] == item
        return investing_cash_flow_id_condition & (df[self.column_table_type] == self.table_type_cf)

    def operating_cash_flow_condition(self, df):
        operating_cash_flow_id_condition = None
        for i, item in enumerate(self.operating_cash_flow_id_list):
            if operating_cash_flow_id_condition is not None:
                operating_cash_flow_id_condition = operating_cash_flow_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                operating_cash_flow_id_condition = df[self.column_standard_code] == item
        return operating_cash_flow_id_condition & (df[self.column_table_type] == self.table_type_cf)

    def financing_cash_flow_condition(self, df):
        financing_cash_flow_id_condition = None
        for i, item in enumerate(self.financing_cash_flow_id_list):
            if financing_cash_flow_id_condition is not None:
                financing_cash_flow_id_condition = financing_cash_flow_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                financing_cash_flow_id_condition = df[self.column_standard_code] == item
        return financing_cash_flow_id_condition & (df[self.column_table_type] == self.table_type_cf)

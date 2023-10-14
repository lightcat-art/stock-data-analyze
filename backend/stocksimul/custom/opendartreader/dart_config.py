import enum


class DartConfig:
    column_amount = 'thstrm_amount'  # 금액 컬럼명
    column_standard_code = 'account_id'  # 표준계정코드 컬럼명

    column_table_type = 'sj_div'  # 표 종류 컬럼명
    table_type_bs = 'BS'  # 재무상태표
    table_type_is = 'IS'  # 손익계산서
    table_type_cis = 'CIS'  # 포괄손익계산서
    table_type_cf = 'CF'  # 현금흐름표

    assets_id_list = ['ifrs-full_Assets', 'ifrs_Assets']  # 자산총계
    liabilities_id_list = ['ifrs-full_Liabilities', 'ifrs_Liabilities']  # 부채총계
    equity_id_list = ['ifrs-full_Equity', 'ifrs_Equity']  # 자본총계
    revenue_id_list = ['ifrs-full_Revenue', 'ifrs_Revenue']  # 수익(매출액)
    operating_income_loss_id_list = ['dart_OperatingIncomeLoss']  # 영업이익
    profit_loss_id_list = ['ifrs-full_ProfitLoss', 'ifrs_ProfitLoss']  # 당기순이익
    profit_loss_control_id_list = ['ifrs-full_ProfitLossAttributableToOwnersOfParent',
                                   'ifrs_ProfitLossAttributableToOwnersOfParent']  # 당기순이익(지배)
    profit_loss_non_control_id_list = ['ifrs-full_ProfitLossAttributableToNoncontrollingInterests',
                                       'ifrs_ProfitLossAttributableToNoncontrollingInterests']  # 당기순이익(비지배)
    profit_loss_before_tax_id_list = ['ifrs-full_ProfitLossBeforeTax', 'ifrs_ProfitLossBeforeTax']  # 세전계속사업이익
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
        return assets_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def liabilities_condition(self, df):
        liabilities_id_condition = None
        for i, item in enumerate(self.liabilities_id_list):
            if liabilities_id_condition is not None:
                liabilities_id_condition = liabilities_id_condition | (df[self.column_standard_code] == item)
            else:
                liabilities_id_condition = df[self.column_standard_code] == item
        return liabilities_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def equity_condition(self, df):
        equity_id_condition = None
        for i, item in enumerate(self.equity_id_list):
            if equity_id_condition is not None:
                equity_id_condition = equity_id_condition | (df[self.column_standard_code] == item)
            else:
                equity_id_condition = df[self.column_standard_code] == item
        return equity_id_condition & (df[self.column_table_type] == self.table_type_bs)

    def revenue_condition(self, df):
        revenue_id_condition = None
        for i, item in enumerate(self.revenue_id_list):
            if revenue_id_condition is not None:
                revenue_id_condition = revenue_id_condition | (df[self.column_standard_code] == item)
            else:
                revenue_id_condition = df[self.column_standard_code] == item
        return revenue_id_condition & (df[self.column_table_type] == self.table_type_is)

    def operating_income_loss_condition(self, df):
        operating_income_loss_id_condition = None
        for i, item in enumerate(self.operating_income_loss_id_list):
            if operating_income_loss_id_condition is not None:
                operating_income_loss_id_condition = operating_income_loss_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                operating_income_loss_id_condition = df[self.column_standard_code] == item
        return operating_income_loss_id_condition & (df[self.column_table_type] == self.table_type_is)

    def profit_loss_condition(self, df):
        profit_loss_id_condition = None
        for i, item in enumerate(self.profit_loss_id_list):
            if profit_loss_id_condition is not None:
                profit_loss_id_condition = profit_loss_id_condition | (df[self.column_standard_code] == item)
            else:
                profit_loss_id_condition = df[self.column_standard_code] == item
        return profit_loss_id_condition & (df[self.column_table_type] == self.table_type_is)

    def profit_loss_before_tax_condition(self, df):
        profit_loss_before_tax_id_condition = None
        for i, item in enumerate(self.profit_loss_before_tax_id_list):
            if profit_loss_before_tax_id_condition is not None:
                profit_loss_before_tax_id_condition = profit_loss_before_tax_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                profit_loss_before_tax_id_condition = df[self.column_standard_code] == item
        return profit_loss_before_tax_id_condition & (df[self.column_table_type] == self.table_type_is)

    def profit_loss_control_condition(self, df):
        profit_loss_control_id_condition = None
        for i, item in enumerate(self.profit_loss_control_id_list):
            if profit_loss_control_id_condition is not None:
                profit_loss_control_id_condition = profit_loss_control_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                profit_loss_control_id_condition = df[self.column_standard_code] == item
        return profit_loss_control_id_condition & (df[self.column_table_type] == self.table_type_is)

    def profit_loss_non_control_condition(self, df):
        profit_loss_non_control_id_condition = None
        for i, item in enumerate(self.profit_loss_non_control_id_list):
            if profit_loss_non_control_id_condition is not None:
                profit_loss_non_control_id_condition = profit_loss_non_control_id_condition | (
                        df[self.column_standard_code] == item)
            else:
                profit_loss_non_control_id_condition = df[self.column_standard_code] == item
        return profit_loss_non_control_id_condition & (df[self.column_table_type] == self.table_type_is)

    def eps_condition(self, df):
        eps_id_condition = None
        for i, item in enumerate(self.eps_id_list):
            if eps_id_condition is not None:
                eps_id_condition = eps_id_condition | (df[self.column_standard_code] == item)
            else:
                eps_id_condition = df[self.column_standard_code] == item
        return eps_id_condition & (df[self.column_table_type] == self.table_type_is)

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

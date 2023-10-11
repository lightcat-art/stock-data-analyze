import enum


class DartConfig:
    column_amount = 'thstrm_amount'  # 금액 컬럼명
    column_standard_code = 'account_id'  # 표준계정코드 컬럼명

    column_table_type = 'sj_div'  # 표 종류 컬럼명
    table_type_bs = 'BS'  # 재무상태표
    table_type_is = 'IS'  # 손익계산서
    table_type_cis = 'CIS'  # 포괄손익계산서
    table_type_cf = 'CF'  # 현금흐름표

    assets_id = 'ifrs-full_CurrentAssets'  # 자산총계
    liabilities_id = 'ifrs-full_Liabilities'  # 부채총계
    equity_id = 'ifrs-full_Equity'  # 자본총계
    revenue_id = 'ifrs-full_Revenue'  # 수익(매출액)
    operating_income_loss_id = 'dart_OperatingIncomeLoss'  # 영업이익
    profit_loss_id = 'ifrs-full_ProfitLoss'  # 당기순이익
    profit_loss_control_id = 'ifrs-full_ProfitLossAttributableToOwnersOfParent'  # 당기순이익(지배)
    profit_loss_non_control_id = 'ifrs-full_ProfitLossAttributableToNoncontrollingInterests'  # 당기순이익(비지배)
    profit_loss_before_tax_id = 'ifrs-full_ProfitLossBeforeTax'  # 세전계속사업이익
    eps_id = 'ifrs-full_BasicEarningsLossPerShare'  # 주당순이익
    investing_cash_flow_id = 'ifrs-full_CashFlowsFromUsedInInvestingActivities'  # 투자활동현금흐름
    operating_cash_flow_id = 'ifrs-full_CashFlowsFromUsedInOperatingActivities'  # 영업활동현금흐름
    financing_cash_flow_id = 'ifrs-full_CashFlowsFromUsedInFinancingActivities'  # 재무활동현금흐름

    def assets_condition(self, df):
        return (df[self.column_standard_code] == self.assets_id) & (df[self.column_table_type] == self.table_type_bs)

    def liabilities_condition(self, df):
        return (df[self.column_standard_code] == self.liabilities_id) & (
                df[self.column_table_type] == self.table_type_bs)

    def equity_condition(self, df):
        return (df[self.column_standard_code] == self.equity_id) & (df[self.column_table_type] == self.table_type_bs)

    def revenue_condition(self, df):
        return (df[self.column_standard_code] == self.revenue_id) & (df[self.column_table_type] == self.table_type_is)

    def operating_income_loss_condition(self, df):
        return (df[self.column_standard_code] == self.operating_income_loss_id) & (
                df[self.column_table_type] == self.table_type_is)

    def profit_loss_condition(self, df):
        return (df[self.column_standard_code] == self.profit_loss_id) & (
                df[self.column_table_type] == self.table_type_is)

    def profit_loss_before_tax_condition(self, df):
        return (df[self.column_standard_code] == self.profit_loss_before_tax_id) & (
                df[self.column_table_type] == self.table_type_is)

    def profit_loss_control_condition(self, df):
        return (df[self.column_standard_code] == self.profit_loss_control_id) & (
                    df[self.column_table_type] == self.table_type_is)

    def profit_loss_non_control_condition(self, df):
        return (df[self.column_standard_code] == self.profit_loss_non_control_id) & (
                    df[self.column_table_type] == self.table_type_is)

    def eps_condition(self, df):
        return (df[self.column_standard_code] == self.eps_id) & (df[self.column_table_type] == self.table_type_is)

    def investing_cash_flow_condition(self, df):
        return (df[self.column_standard_code] == self.investing_cash_flow_id) & (
                    df[self.column_table_type] == self.table_type_cf)

    def operating_cash_flow_condition(self, df):
        return (df[self.column_standard_code] == self.operating_cash_flow_id) & (
                df[self.column_table_type] == self.table_type_cf)

    def financing_cash_flow_condition(self, df):
        return (df[self.column_standard_code] == self.financing_cash_flow_id) & (
                df[self.column_table_type] == self.table_type_cf)

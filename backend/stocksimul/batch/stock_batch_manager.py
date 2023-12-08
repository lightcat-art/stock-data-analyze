from ..common.singleton import SingletonInstance


class StockBatchManager(SingletonInstance):
    def __init__(self):
        self.RETRY_FUND = False
        self.RETRY_SHARES = False

    def is_retry_fund(self):
        return self.RETRY_FUND

    def set_retry_fund(self, retryTF: bool):
        self.RETRY_FUND = retryTF

    def is_retry_shares(self):
        return self.RETRY_SHARES

    def set_retry_shares(self, retryTF: bool):
        self.RETRY_SHARES = retryTF

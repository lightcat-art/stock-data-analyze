from ..common.singleton import SingletonInstance


class StockBatchManager(SingletonInstance):
    def __init__(self):
        self.RETRY_FUND = False

    def is_retry_fund(self):
        return self.RETRY_FUND

    def set_retry_fund(self, retryTF: bool):
        self.RETRY_FUND = retryTF

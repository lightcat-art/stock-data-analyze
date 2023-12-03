from ..common.singleton import SingletonInstance


class StockBatchManager(SingletonInstance):
    def __init__(self):
        self.STOP_FUNDAMENTAL_BATCH_REQUEST = False

    def is_fundamental_batch_stop_request(self):
        return self.STOP_FUNDAMENTAL_BATCH_REQUEST

    def set_fundamental_batch_stop_request(self, stopTF: bool):
        self.STOP_FUNDAMENTAL_BATCH_REQUEST = stopTF

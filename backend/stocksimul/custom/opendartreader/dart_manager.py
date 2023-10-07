from backend.stocksimul.custom.opendartreader.dart import OpenDartReader
from backend.stocksimul.common.singleton import SingletonInstance


class DartManager(SingletonInstance):
    def __init__(self):
        self.dart = OpenDartReader('69500f38022cc6f7d33956e4690d43499fa10423')

    def get_dart(self):
        return self.dart





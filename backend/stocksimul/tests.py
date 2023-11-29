from django.test import TestCase
from .models import PriceInfo
import datetime


# Create your tests here.
class NullTestCase(TestCase):
    def setUp(self):
        PriceInfo.objects.create(stock_event_id=1, stock_price_id=1, date=datetime.datetime.now())

    def one(self):
        info = PriceInfo.objects.filter(stock_price_id=1)
        print(info)
        self.assertEqual(info.first().value, None)

    def two(self):
        info = PriceInfo.objects.filter(stock_price_id=1)
        print(info)
        self.assertEqual(info.first().value, 1)

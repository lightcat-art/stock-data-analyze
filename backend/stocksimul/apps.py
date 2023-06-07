from django.apps import AppConfig
from django.conf import settings


class StocksimulConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stocksimul'

    def ready(self):
        if settings.SCHEDULER_DEFAULT:
            from .batch import operator
            operator.start()

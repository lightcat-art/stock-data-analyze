from django.apps import AppConfig
from django.conf import settings
import os


class StocksimulConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stocksimul'

    def ready(self):
        super().ready()
        # 한번 불려야 하는데 두번 불림.
        # 두번 불리는 이유: https://stackoverflow.com/questions/33814615/how-to-avoid-appconfig-ready-method-running-twice-in-django
        #  Reload와 main 두가지 프로세스가 뜬다고 함.
        if os.environ.get('RUN_MAIN', None) != 'true':  # 또는 python manage.py runserver --noreload  로 실행하면 됨.
            if settings.SCHEDULER_DEFAULT:
                from .batch import operator
                # 처음 서버 실행시에 이전 잡들 모두 제거
                # operator.operator().remove()
                operator.operator().start()


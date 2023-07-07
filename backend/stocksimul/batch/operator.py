from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from .stock_data_manage import stock_batch
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import traceback


class operator:
    def __init__(self):
        print('init operator')
        self.job = None
        self.scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        self.scheduler.add_jobstore(DjangoJobStore())
    def start(self):
        print('register job start')
        # jobstores = {
        #     'default': DjangoJobStore()
        # }
        # executors = {
        #     'default': ThreadPoolExecutor(20),
        #     'processpool': ProcessPoolExecutor(5)
        # }
        # job_defaults = {
        #     'coalesce': False,
        #     'max_instances': 1
        # }
        # scheduler = BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults, executors=executors, timezone=settings.TIME_ZONE)
        try:
            self.job = self.scheduler.add_job(stock_batch, 'cron', hour=11, minute=47, id='stock_batch', replace_existing=True)

            self.scheduler.start()
        except Exception as e:
            traceback.print_exc()
        print('register job end')

    def remove(self):
        print('remove before job start')
        # 현재 실행중인 job을 기반으로 검색함. 등록만 되어있고 실행되지 않으면 검색되지 않음.
        if self.scheduler.get_job('stock_batch') is not None:
            self.scheduler.remove_job(job_id='stock_batch')
        print('remove before job end')


from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from .stock_data_manage import manage_event_init, manage_event_daily
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import traceback
from datetime import timedelta, datetime


class operator:
    def __init__(self):
        print('init operator')
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
            today_org = datetime.now()
            # The 'date' trigger and datetime.now() as run_date are implicit
            self.scheduler.add_job(manage_event_init, 'date', run_date=today_org+timedelta(seconds=10),
                                              id='manage_event_init', replace_existing=True)

            self.scheduler.add_job(manage_event_daily, 'cron', hour=(today_org+timedelta(minutes=2)).hour,
                                              minute=(today_org+timedelta(minutes=2)).minute, id='manage_event_daily',
                                              replace_existing=True)

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


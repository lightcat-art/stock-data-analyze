from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from .stock_data_manage import manage_event_init, manage_event_daily
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import traceback
import datetime
from ..config.stockConfig import BATCH_HOUR, BATCH_MIN, BATCH_SEC, BATCH_TEST
import logging

logger = logging.getLogger('batch')


class operator:
    def __init__(self):
        logger.info('[operator] init operator')
        self.scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        self.scheduler.add_jobstore(DjangoJobStore())

    def start(self):
        logger.info('[operator] register job start')
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
            today_org = datetime.datetime.now()
            # The 'date' trigger and datetime.now() as run_date are implicit
            self.scheduler.add_job(manage_event_init, 'date', run_date=today_org + datetime.timedelta(seconds=10),
                                   id='manage_event_init', replace_existing=True)

            daily_batch_time = None
            if BATCH_TEST:
                daily_batch_time = today_org + datetime.timedelta(seconds=30)
            else:
                daily_batch_time = datetime.datetime.combine(
                    datetime.date(today_org.year, today_org.month, today_org.day),
                    datetime.time(BATCH_HOUR, BATCH_MIN, BATCH_SEC))

            self.scheduler.add_job(manage_event_daily, 'cron', hour=daily_batch_time.hour,
                                   minute=daily_batch_time.minute,
                                   second=daily_batch_time.second,
                                   id='manage_event_daily',
                                   replace_existing=True)

            self.scheduler.start()
        except Exception as e:
            logger.error('[operator] error occured when register batch job')
        logger.info('[operator] register job end')

    def remove(self):
        logger.info('[operator] remove before job start')
        # 현재 실행중인 job을 기반으로 검색함. 등록만 되어있고 실행되지 않으면 검색되지 않음.
        if self.scheduler.get_job('stock_batch') is not None:
            self.scheduler.remove_job(job_id='stock_batch')
        logger.info('[operator] remove before job end')

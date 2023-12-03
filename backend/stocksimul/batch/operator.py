from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from .stock_batch import manage_event_init, manage_event_daily, validate_connection, manage_fundamental_daily, \
    manage_event_init_etc, manage_event_daily_etc
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import traceback
import datetime
from ..config.stockConfig import BATCH_HOUR, BATCH_MIN, BATCH_SEC, BATCH_TEST, \
    ETC_BATCH_HOUR, ETC_BATCH_MIN, ETC_BATCH_SEC, \
    FUND_BATCH_HOUR, FUND_BATCH_MIN, FUND_BATCH_SEC, FUND_RETRY
import logging

logger = logging.getLogger('batch')


class operator:
    def __init__(self):
        logger.info('[operator] init operator')
        # jobstores = {
        #     'default': DjangoJobStore()
        # }
        # executors = {
        #     # job 개수 통제 ( job 각각으로서는 설정하지 않아도 기본적으로 이전작업이 끝나지 않으면 다음작업 실행안됨)
        #     'default': ThreadPoolExecutor(3),
        #
        #     # job을 별도의 프로세스에서 실행하도록 설정 (job개수를 통제할수 없음)
        #     'processpool': ProcessPoolExecutor(2)
        # }
        # job_defaults = {
        #     'coalesce': False,
        #     'max_instances': 1
        # }
        self.scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        self.scheduler.add_jobstore(DjangoJobStore())

    def start(self):
        logger.info('[operator] register job start')
        try:
            today_org = datetime.datetime.now()
            # The 'date' trigger and datetime.now() as run_date are implicit
            self.scheduler.add_job(manage_event_init, 'date', run_date=today_org + datetime.timedelta(seconds=10),
                                   id='manage_event_init', replace_existing=True)
            #
            # daily_batch_time = None
            # if BATCH_TEST:
            #     daily_batch_time = today_org + datetime.timedelta(seconds=20)
            # else:
            #     daily_batch_time = datetime.datetime.combine(
            #         datetime.date(today_org.year, today_org.month, today_org.day),
            #         datetime.time(BATCH_HOUR, BATCH_MIN, BATCH_SEC))
            #
            # self.scheduler.add_job(manage_event_daily, 'cron', hour=daily_batch_time.hour,
            #                        minute=daily_batch_time.minute,
            #                        second=daily_batch_time.second,
            #                        id='manage_event_daily',
            #                        replace_existing=True)
            #
            # # The 'date' trigger and datetime.now() as run_date are implicit
            # self.scheduler.add_job(manage_event_init_etc, 'date', run_date=today_org + datetime.timedelta(seconds=30),
            #                        id='manage_event_init_etc', replace_existing=True)
            #
            # etc_daily_batch_time = None
            # if BATCH_TEST:
            #     etc_daily_batch_time = today_org + datetime.timedelta(seconds=40)
            # else:
            #     etc_daily_batch_time = datetime.datetime.combine(
            #         datetime.date(today_org.year, today_org.month, today_org.day),
            #         datetime.time(ETC_BATCH_HOUR, ETC_BATCH_MIN, ETC_BATCH_SEC))
            #
            # self.scheduler.add_job(manage_event_daily_etc, 'cron', hour=etc_daily_batch_time.hour,
            #                        minute=etc_daily_batch_time.minute,
            #                        second=etc_daily_batch_time.second,
            #                        id='manage_event_daily_etc',
            #                        replace_existing=True)

            fund_daily_batch_time = None
            if BATCH_TEST:
                fund_daily_batch_time = today_org + datetime.timedelta(seconds=40)
            else:
                fund_daily_batch_time = datetime.datetime.combine(
                    datetime.date(today_org.year, today_org.month, today_org.day),
                    datetime.time(FUND_BATCH_HOUR, FUND_BATCH_MIN, FUND_BATCH_SEC))

            if FUND_RETRY:
                # 추후 횟수제한이 필요하다면 FUND_RETRY를 이용하여 RETRY_Manager를 생성하여 횟수 제어
                self.scheduler.add_job(manage_fundamental_daily, 'interval', seconds=30, id='manage_fundamental_daily',
                                       replace_existing=True)
            else:
                self.scheduler.add_job(manage_fundamental_daily, 'cron', hour=fund_daily_batch_time.hour,
                                       minute=fund_daily_batch_time.minute,
                                       second=fund_daily_batch_time.second,
                                       id='manage_fundamental_daily',
                                       replace_existing=True)

            self.scheduler.add_job(validate_connection, 'interval', hours=2, id='validate_connection',
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

from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from .stock_batch import manage_event_init, manage_event_daily, validate_connection, \
    manage_event_daily_etc, manage_financial_indicator_daily, manage_event_init_etc
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import traceback
import datetime
from ..config.stockConfig import BATCH_HOUR, BATCH_MIN, BATCH_SEC, BATCH_TEST, \
    ETC_BATCH_HOUR, ETC_BATCH_MIN, ETC_BATCH_SEC, ETC_BATCH_IMMEDIATE, \
    INDIC_BATCH_HOUR, INDIC_BATCH_MIN, INDIC_BATCH_SEC
import logging
from .stock_batch_manager import StockBatchManager
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

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
        self.fund_batch_time = None

    def start(self):
        logger.info('[operator] register job start')
        try:
            today_org = datetime.datetime.now()

            self.scheduler.add_job(manage_event_init, 'date', run_date=today_org + datetime.timedelta(seconds=10),
                                   id='manage_event_init', replace_existing=True)

            daily_batch_time = None
            if BATCH_TEST:
                daily_batch_time = today_org + datetime.timedelta(seconds=20)
            else:
                daily_batch_time = datetime.datetime.combine(
                    datetime.date(today_org.year, today_org.month, today_org.day),
                    datetime.time(BATCH_HOUR, BATCH_MIN, BATCH_SEC))

            self.scheduler.add_job(manage_event_daily, 'cron', hour=daily_batch_time.hour,
                                   minute=daily_batch_time.minute,
                                   second=daily_batch_time.second,
                                   id='manage_event_daily',
                                   replace_existing=True)

            # 23-12-05 당분간 사용하지 않기. 일별 가격정보 받아오는게 안정화되면 고려.
            # self.scheduler.add_job(manage_event_init_etc, 'date', run_date=today_org + datetime.timedelta(seconds=30),
            #                        id='manage_event_init_etc', replace_existing=True)

            etc_daily_batch_time = None
            if ETC_BATCH_IMMEDIATE:
                etc_daily_batch_time = today_org + datetime.timedelta(seconds=40)
            else:
                etc_daily_batch_time = datetime.datetime.combine(
                    datetime.date(today_org.year, today_org.month, today_org.day),
                    datetime.time(ETC_BATCH_HOUR, ETC_BATCH_MIN, ETC_BATCH_SEC))

            self.scheduler.add_job(manage_event_daily_etc, 'cron', hour=etc_daily_batch_time.hour,
                                   minute=etc_daily_batch_time.minute,
                                   second=etc_daily_batch_time.second,
                                   id='manage_event_daily_etc',
                                   replace_existing=True)

            indic_daily_batch_time = None
            if BATCH_TEST:
                indic_daily_batch_time = today_org + datetime.timedelta(seconds=40)
            else:
                indic_daily_batch_time = datetime.datetime.combine(
                    datetime.date(today_org.year, today_org.month, today_org.day),
                    datetime.time(INDIC_BATCH_HOUR, INDIC_BATCH_MIN, INDIC_BATCH_SEC))

            self.scheduler.add_job(manage_financial_indicator_daily, 'cron', hour=indic_daily_batch_time.hour,
                                   minute=indic_daily_batch_time.minute,
                                   second=indic_daily_batch_time.second,
                                   id='manage_financial_indicator_daily',
                                   replace_existing=True)

            # if BATCH_TEST:
            #     self.fund_batch_time = today_org + datetime.timedelta(seconds=40)
            # else:
            #     self.fund_batch_time = datetime.datetime.combine(
            #         datetime.date(today_org.year, today_org.month, today_org.day),
            #         datetime.time(FUND_BATCH_HOUR, FUND_BATCH_MIN, FUND_BATCH_SEC))

            # self.scheduler.add_job(manage_fundamental, 'cron', hour=self.fund_batch_time.hour,
            #                        minute=self.fund_batch_time.minute,
            #                        second=self.fund_batch_time.second,
            #                        id='manage_fundamental',
            #                        replace_existing=True)

            self.scheduler.add_job(validate_connection, 'interval', hours=2, id='validate_connection',
                                   replace_existing=True)

            # self.scheduler.add_listener(self.check_fund_retry, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

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

    # def check_fund_retry(self, event):
    #     if event.job_id == 'manage_fundamental':
    #         if (event.code & EVENT_JOB_ERROR) != 0 or (
    #                 ((event.code & EVENT_JOB_EXECUTED) != 0) and StockBatchManager.instance().is_retry_fund()):
    #             logger.info('transfrom manage_fundamental to interval because of retry request')
    #             self.scheduler.add_job(manage_fundamental, 'interval', seconds=30, id='manage_fundamental',
    #                                    replace_existing=True)
    #             pass
    #         elif ((event.code & EVENT_JOB_EXECUTED) != 0) and not StockBatchManager.instance().is_retry_fund():
    #             logger.info('recover manage_fundamental to origin cron batch.')
    #             self.scheduler.add_job(manage_fundamental, 'cron', hour=self.fund_batch_time.hour,
    #                                    minute=self.fund_batch_time.minute,
    #                                    second=self.fund_batch_time.second,
    #                                    id='manage_fundamental',
    #                                    replace_existing=True)

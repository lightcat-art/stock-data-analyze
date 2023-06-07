from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from .stock_data_manage import stock_batch


def start():
    # def handle(self, *args, **options):

    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE) # 왜 여러번 돌지?
    scheduler.add_jobstore(DjangoJobStore(), "default")
    # scheduler.add_job(
    #     stock_batch, 'interval', seconds=60
    # )

    scheduler.add_job(
        stock_batch,
        trigger=CronTrigger(second="59"),  # 60초마다 작동합니다.
        id="my_job",  # id는 고유해야합니다.
        max_instances=1,
        replace_existing=True,
    )
    scheduler.start()
    # try:
    #     scheduler.start()
    # except KeyboardInterrupt:
    #     scheduler.shutdown()

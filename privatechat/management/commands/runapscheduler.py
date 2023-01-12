import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime, timedelta

from ...models import *
# from Utube.utube_app.models import CustomUser
User = get_user_model()


logger = logging.getLogger(__name__)


def filter_by_id(queryset, id):
    return queryset.filter(recepient=id)

def my_job():
    # уведомления о сообщениях старше 24 часов, но не старше 1 недели
    unread_private_msg_list_week = PrivateMessage.objects.filter(time_creation__range=[datetime.now()-timedelta(days=7),
                                                                                       datetime.now()-timedelta(days=1)],
                                                                 isRead=False)
    for user in User.objects.all():
        msg_list = filter_by_id(unread_private_msg_list_week, user.id)
        html_content = render_to_string(
            'daily.html',
            {
                'msg_list': msg_list,
                'username': user.username,
            }
        )
        msg = EmailMultiAlternatives(
            subject='Daily Update on Unread Messages',
            body='',
            from_email='arahna.aurum@yandex.ru',
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # еженедельная рассылка писем
        scheduler.add_job(
            my_job,
            # ежедневная рассылка
            # trigger=CronTrigger(day_of_week="*", hour="00", minute="00"),
            # для проверки работы рассылки - частота раз в 30 секунд.
            trigger=CronTrigger(second="*/30"),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
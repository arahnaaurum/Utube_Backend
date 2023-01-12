from django.apps import AppConfig


class UtubeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utube_app'

    def ready(self):
        import utube_app.signals
from django.apps import AppConfig


class CorecodeConfig(AppConfig):
    name = "apps.corecode"
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        import apps.corecode.signals
        # Make sure templatetags are loaded
        import apps.corecode.templatetags.breadcrumb_tags

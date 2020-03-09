from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class PluginApp(AppConfig):
    name = 'pretix_reluctant_stripe'
    verbose_name = 'Stripe plugin (reluctant to work)'

    class PretixPluginMeta:
        name = gettext_lazy('Stripe plugin (reluctant to work)')
        author = 'Team MRMCD'
        description = gettext_lazy('Short description')
        visible = True
        version = '1.0.0'

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_reluctant_stripe.PluginApp'

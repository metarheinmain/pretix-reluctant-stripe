from django.apps import AppConfig
from django.utils.translation import gettext_lazy
from . import __version__


class PluginApp(AppConfig):
    name = 'pretix_reluctant_stripe'
    verbose_name = 'Stripe plugin (reluctant to work)'

    class PretixPluginMeta:
        name = gettext_lazy('Stripe plugin (reluctant to work)')
        author = 'Team MRMCD'
        description = gettext_lazy('Short description')
        visible = True
        version = __version__
        compatibility = "pretix>=2023.7.0.dev0"

    def ready(self):
        from . import signals  # NOQA



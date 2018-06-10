import logging
from collections import OrderedDict

from django import forms
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from pretix.plugins.stripe.payment import StripeCC

logger = logging.getLogger(__name__)


class ReluctantStripeCC(StripeCC):
    method = 'cc_reluctant'
    identifier = 'stripe_cc_reluctant'
    verbose_name = _('Stripe Credit Card (reluctant)')

    @property
    def settings_form_fields(self):
        return OrderedDict([
            ('_reluctant_enabled',
             forms.BooleanField(
                 label=_('Enable payment method'),
                 required=False,
             )),
        ])

    @property
    def is_enabled(self) -> bool:
        return self.settings.get('_reluctant_enabled', as_type=bool)

    def payment_form_render(self, request) -> str:
        ui = self.settings.get('ui', default='pretix')
        template = get_template('pretix_reluctant_stripe/checkout_payment_form.html')
        ctx = {
            'request': request,
            'event': self.event,
            'settings': self.settings,
        }
        return template.render(ctx)

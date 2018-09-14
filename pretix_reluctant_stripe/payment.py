from decimal import Decimal

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
    def payment_form_fields(self):
        return OrderedDict([
            ('pay_fees',
             forms.ChoiceField(
                 label=_('Pay fees yourself'),
                 choices=(
                     ('yes', 'Yes, that\'s alright. Just add it to the bill!'),
                     ('no', _('I\'d rather not, please pay the fees for me.'))
                 ),
                 required=False,
                 widget=forms.RadioSelect
             )),
        ])

    @property
    def is_enabled(self) -> bool:
        return self.settings.get('_reluctant_enabled', as_type=bool)

    def payment_form_render(self, request, total) -> str:
        template = get_template('pretix_reluctant_stripe/checkout_payment_form.html')
        max_stripe_fee = Decimal('0.25') + Decimal('.029') * total
        form = self.payment_form(request)
        ctx = {
            'request': request,
            'event': self.event,
            'form': form,
            'settings': self.settings,
            'fee': max_stripe_fee
        }
        return template.render(ctx)

    def checkout_prepare(self, request, cart):
        form = self.payment_form(request)
        if form.is_valid():
            for k, v in form.cleaned_data.items():
                request.session['payment_%s_%s' % (self.identifier, k)] = v
            return super().checkout_prepare(request, cart)
        else:
            return False

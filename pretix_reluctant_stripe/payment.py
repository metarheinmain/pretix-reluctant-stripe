from decimal import Decimal

import logging
from collections import OrderedDict

from django import forms
from django.db.models import Sum
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _

from pretix.base.models import OrderFee, InvoiceAddress
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
                     ('yes', _('Yes, that\'s alright. Just add it to the bill!')),
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

    def payment_prepare(self, request, payment):
        from .signals import get_fee

        payment.order.fees.filter(fee_type=OrderFee.FEE_TYPE_PAYMENT).delete()
        if request.POST.get('payment_stripe_cc_reluctant-pay_fees', 'no') == 'yes':
            try:
                fee = get_fee(self.event, payment.order.total, payment.order.invoice_address)
            except InvoiceAddress.DoesNotExist:
                fee = get_fee(self.event, payment.order.total, None)

            fee.order = payment.order
            fee._calculate_tax()
            if fee.tax_rule and not fee.tax_rule.pk:
                fee.tax_rule = None
            fee.save()
        payment.order.total = (
            (payment.order.positions.aggregate(sum=Sum('price'))['sum'] or 0) +
            (payment.order.fees.aggregate(sum=Sum('value'))['sum'] or 0)
        )
        payment.amount = payment.order.pending_sum
        payment.save(update_fields=['amount'])
        return self.checkout_prepare(request, None)

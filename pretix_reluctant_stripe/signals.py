from decimal import Decimal

from django.dispatch import receiver
from django.http import HttpRequest
from django.template.loader import get_template
from django.urls import resolve

from pretix.base.decimal import round_decimal
from pretix.base.models import Event, TaxRule, OrderFee
from pretix.base.services.cart import get_fees
from pretix.base.signals import register_payment_providers, order_fee_calculation
from pretix.presale.signals import html_head, fee_calculation_for_cart, order_meta_from_request
from pretix.presale.views.cart import cart_session
from .payment import ReluctantStripeCC


@receiver(register_payment_providers, dispatch_uid="payment_stripe_reluctant")
def register_payment_provider(sender, **kwargs):
    return ReluctantStripeCC


@receiver(html_head, dispatch_uid="payment_stripe_reluctant_html_head")
def html_head_presale(sender, request=None, **kwargs):
    provider = ReluctantStripeCC(sender)
    url = resolve(request.path_info)
    if provider.is_enabled and ("checkout" in url.url_name or "order.pay" in url.url_name):
        template = get_template('pretix_reluctant_stripe/presale_head.html')
        ctx = {'event': sender, 'settings': provider.settings}
        return template.render(ctx)
    else:
        return ""


def get_fee(event, total, invoice_address):
    payment_fee = round_decimal(Decimal('0.25') + Decimal('0.029') * total)
    payment_fee_tax_rule = event.settings.tax_rate_default or TaxRule.zero()
    if payment_fee_tax_rule.tax_applicable(invoice_address):
        payment_fee_tax = payment_fee_tax_rule.tax(payment_fee, base_price_is='gross')
        return OrderFee(
            fee_type=OrderFee.FEE_TYPE_PAYMENT,
            value=payment_fee,
            tax_rate=payment_fee_tax.rate,
            tax_value=payment_fee_tax.tax,
            tax_rule=payment_fee_tax_rule
        )
    else:
        return OrderFee(
            fee_type=OrderFee.FEE_TYPE_PAYMENT,
            value=payment_fee,
            tax_rate=Decimal('0.00'),
            tax_value=Decimal('0.00'),
            tax_rule=payment_fee_tax_rule
        )



@receiver(fee_calculation_for_cart, dispatch_uid="payment_stripe_reluctant_fee_calc_cart")
def cart_fee(sender: Event, request: HttpRequest, total: Decimal, invoice_address, **kwargs):
    cs = cart_session(request)
    if cs.get('payment') == 'stripe_cc_reluctant' and total > 0:
        if request.session.get('payment_%s_%s' % ('stripe_cc_reluctant', 'pay_fees')) == 'yes':
            return [get_fee(sender, total, invoice_address)]
    return []


@receiver(order_meta_from_request, dispatch_uid="pretix_stripe_reluctant_fee_order_meta")
def order_meta_signal(sender: Event, request: HttpRequest, **kwargs):
    return {
        'pretix_stripe_reluctant_pay_fee': request.session.get('payment_%s_%s' % ('stripe_cc_reluctant', 'pay_fees')) == 'yes'
    }


@receiver(order_fee_calculation, dispatch_uid="pretix_stripe_reluctant_fee_calc_order")
def order_fee(sender: Event, invoice_address, meta_info: dict, total: Decimal, **kwargs):
    if meta_info.get('pretix_stripe_reluctant_pay_fee'):
        return [get_fee(sender, total, invoice_address)]
    return []

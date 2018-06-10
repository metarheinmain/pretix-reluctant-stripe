from django.dispatch import receiver
from django.template.loader import get_template
from django.urls import resolve

from pretix.base.signals import register_payment_providers
from pretix.presale.signals import html_head
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

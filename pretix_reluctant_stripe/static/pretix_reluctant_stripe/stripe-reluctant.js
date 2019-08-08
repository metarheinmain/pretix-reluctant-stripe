$(function () {
    if (!$(".stripe-container, #stripe-checkout").length) // Not on the checkout page
        return;

    if ($("input[name=payment][value=stripe_cc_reluctant]").is(':checked') || $(".payment-redo-form").length) {
        pretixstripe.load();
    } else {
        $("input[name=payment]").change(function () {
            if ($(this).val() === 'stripe_cc_reluctant') {
                pretixstripe.load();
            }
        })
    }
    $('.stripe-container').closest("form").submit(
        function () {
          if ($("input[name=card_new]").length && !$("input[name=card_new]").prop('checked')) {
            return null;
          }
            if (($("input[name=payment][value=stripe_cc_reluctant]").prop('checked') || $("input[name=payment][type=radio]").length === 0)
                && $("#stripe_payment_method_id").val() == "") {
                pretixstripe.cc_request();
                return false;
            }
        }
    );
    $(".stripe-reluctant-ignore").click(function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(".stripe-reluctant-body").slideDown();
        $(".stripe-reluctant-warning").slideUp();
        return true;
    });
    $(".stripe-reluctant-okay").click(function (e) {
        e.preventDefault();
        e.stopPropagation();
        $("input[name=payment][value=stripe_cc_reluctant]").prop("checked", false);
        $("input[name=payment][value=banktransfer]").prop("checked", true).trigger('change');
        $('.stripe-container').closest("form").find(".checkout-button-row .btn-primary").prop("disabled", false);
        return true;
    });
    $(".stripe-reluctant-choice input").change(function (e) {
        $(".stripe-reluctant-ignore").prop("disabled", false);
    });

    $(".stripe-reluctant-body").hide();
});

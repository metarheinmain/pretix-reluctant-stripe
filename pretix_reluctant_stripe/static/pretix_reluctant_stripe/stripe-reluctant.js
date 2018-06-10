$(function () {
    if (!$(".stripe-container, #stripe-checkout").length) // Not on the checkout page
        return;

    if ($("input[name=payment][value=stripe_cc_reluctant]").is(':checked') || $(".payment-redo-form").length) {
        if ($("#stripe-checkout").length) {
            pretixstripe.load_checkout();
        } else {
            pretixstripe.load();
        }
    } else {
        $("input[name=payment]").change(function () {
            if ($(this).val() === 'stripe_cc_reluctant') {
                if ($("#stripe-checkout").length) {
                    pretixstripe.load_checkout();
                } else {
                    pretixstripe.load();
                }
            }
        })
    }
    $('.stripe-container').closest("form").submit(
        function () {
            if (($("input[name=payment][value=stripe_cc_reluctant]").prop('checked') || $("input[name=payment][type=radio]").length === 0)
                && $("#stripe_token").val() == "") {
                if ($("#stripe-checkout").length) {
                    pretixstripe.show_checkout();
                } else {
                    pretixstripe.cc_request();
                }
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
        return true;
    });

    $(".stripe-reluctant-body").hide();
});

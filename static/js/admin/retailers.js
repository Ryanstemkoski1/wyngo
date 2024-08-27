$(document).ready(function () {
    django.jQuery('.field-name a').css('text-decoration', 'underline');
    django.jQuery('.field-user').hide();

    function toggleMerchantField() {
        if (django.jQuery('#id_origin').val() === 'SQUARE') {
            django.jQuery('.form-row.field-merchant_id').hide();
            // django.jQuery('#id_merchant_id').val('');
        } else {
            django.jQuery('.form-row.field-merchant_id').show();
        }
    }

    toggleMerchantField();

    django.jQuery('#id_origin').on('change', toggleMerchantField);

});
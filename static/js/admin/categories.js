$(document).ready(function () {


    let $selectElement = django.jQuery('#id_icon');
    let $container = django.jQuery('.field-icon .flex-container');


    $selectElement.on('change', function () {
        $container.find('.material-symbols-outlined').remove();

        let $newSpan = django.jQuery('<span/>', {
            'class': 'material-symbols-outlined', 'style': 'margin-left: 20px;'
        });

        $newSpan.text(django.jQuery(this).val());

        $container.append($newSpan);
    });

    setTimeout(django.jQuery('#id_icon').trigger('change'), 3000);

});
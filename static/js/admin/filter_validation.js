document.addEventListener("DOMContentLoaded", function () {
    const currentDate = new Date();
    const submitButton = document.querySelector('#created-date-form .button[type="submit"]');

    function updateSubmitButtonStatus() {
        let startDateElement = document.getElementById('id_order_time__range__gte');
        let endDateElement = document.getElementById('id_order_time__range__lte');

        if (startDateElement.value && endDateElement.value) {
            submitButton.removeAttribute('disabled');
        } else {
            submitButton.setAttribute('disabled', 'disabled');
        }
    }

    document.getElementById('id_order_time__range__gte').addEventListener('blur', updateSubmitButtonStatus);
    document.getElementById('id_order_time__range__lte').addEventListener('blur', updateSubmitButtonStatus);

    updateSubmitButtonStatus();

    function showError(element, message) {
        let errorSpan = document.createElement("span");
        errorSpan.textContent = message;
        errorSpan.style.color = "red";
        errorSpan.className = "custom-error";
        errorSpan.style.display = "block";
        errorSpan.style.marginBottom = "20px";
        errorSpan.style.lineHeight = "14px";

        let dateParent = element.closest('.date');

        dateParent.insertBefore(errorSpan, dateParent.firstChild);

        setTimeout(function () {
            errorSpan.remove();
        }, 5000);
    }

    document.addEventListener('blur', function (event) {
        let existingError = event.target.closest('.date').querySelector('.custom-error');
        if (existingError) existingError.remove();

        if (event.target.id === 'id_order_time__range__gte') {
            let dateValue = new Date(event.target.value);
            if (dateValue > currentDate) {
                showError(event.target, 'The start date cannot be in the future.');
                event.target.value = '';
            }
        }
    }, true);
});

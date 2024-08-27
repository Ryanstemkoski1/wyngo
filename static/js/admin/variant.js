document.addEventListener("DOMContentLoaded", function () {
    updateTableTitle();
    document.querySelectorAll(".delete-image").forEach(function (element) {
        element.addEventListener("click", function (event) {
            event.preventDefault();

            const imageId = event.target.getAttribute('data-image-id');
            const rowElement = event.target.closest("tr");

            fetch(`/inventory/delete_image/${imageId}/`, {
                method: 'DELETE',
            }).then(response => {
                if (response.ok) {
                    const deleteButton = event.target.closest(".delete-image");

                    const previousImageLink = deleteButton.previousElementSibling;
                    if (previousImageLink && previousImageLink.tagName === 'A' && previousImageLink.target === "_blank") {
                        previousImageLink.remove();
                    }

                    const nextBreak = deleteButton && deleteButton.nextElementSibling;
                    if (nextBreak && nextBreak.tagName === 'BR') {
                        nextBreak.remove();
                    }
                    if (deleteButton) {
                        deleteButton.remove();
                    }

                    updateImageNames(rowElement);
                    updateTableTitle();
                } else {
                    alert("Error al borrar la imagen.");
                }
            });
        });
    });

    let mainNameField = document.getElementById("id_name");
    let variantNameField = document.getElementById("id_variants-0-name");
    let tbody = document.querySelector("fieldset tbody");

    function hasSingleRow() {
        return tbody.childElementCount === 2;
    }

    mainNameField.addEventListener("input", function () {
        if (hasSingleRow()) {
            variantNameField.value = mainNameField.value;
        }
    });

    variantNameField.addEventListener("input", function () {
        if (hasSingleRow()) {
            mainNameField.value = variantNameField.value;
        }
    });

});

function updateTableTitle() {
    let rowCount = document.querySelector("fieldset tbody").childElementCount;

    if (rowCount <= 1) {
        document.querySelector("fieldset h2").textContent = "Product Detail";
    } else {
        document.querySelector("fieldset h2").textContent = "Variations";
    }
}

function updateImageNames(rowElement) {
    const imageLinks = rowElement.querySelectorAll('a[target="_blank"]:not(.delete-image)');
    imageLinks.forEach((element, index) => {
        element.textContent = `View image #${index + 1}`;
    });
}



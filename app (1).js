document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll("form");

    forms.forEach((form) => {
        form.addEventListener("submit", () => {
            const button = form.querySelector(
                'button[type="submit"]'
            );

            if (button) {
                button.disabled = true;
                button.dataset.originalText =
                    button.textContent;

                button.textContent = "Generating...";
            }
        });
    });

    const imageInput = document.querySelector(
        "#outfit_image"
    );

    const preview = document.querySelector(
        "#image-preview"
    );

    if (imageInput && preview) {
        imageInput.addEventListener(
            "change",
            () => {
                const file = imageInput.files[0];

                if (!file) {
                    preview.innerHTML = "";
                    return;
                }

                if (!file.type.startsWith("image/")) {
                    preview.innerHTML =
                        "<p>Please select an image file.</p>";
                    return;
                }

                const reader = new FileReader();

                reader.onload = (event) => {
                    preview.innerHTML = `
                        <img
                            src="${event.target.result}"
                            alt="Outfit preview"
                            class="image-preview"
                        />
                    `;
                };

                reader.readAsDataURL(file);
            }
        );
    }
});
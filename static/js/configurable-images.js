(() => {
  "use strict";

  const initializeFallbackImages = () => {
    document
      .querySelectorAll(".js-image-fallback")
      .forEach((image) => {
        image.addEventListener(
          "error",
          () => {
            const fallback = image.dataset.fallback;

            if (!fallback) {
              return;
            }

            image.src = fallback;
          },
          { once: true },
        );
      });

    document
      .querySelectorAll(".js-option-image")
      .forEach((image) => {
        image.addEventListener(
          "error",
          () => {
            const container = image.closest(
              ".option-card__image, .vote-option__visual",
            );

            if (container) {
              container.remove();
            }
          },
          { once: true },
        );
      });

    document
      .querySelectorAll(".js-admin-image")
      .forEach((image) => {
        image.addEventListener(
          "error",
          () => {
            const preview = image.closest(".media-preview");

            if (preview) {
              preview.remove();
            }
          },
          { once: true },
        );
      });
  };

  const initializeLocalPreviews = () => {
    document
      .querySelectorAll(".js-image-input")
      .forEach((input) => {
        const scope =
          input.closest(".option-row") ||
          input.closest(".form-card");

        if (!scope) {
          return;
        }

        const preview = scope.querySelector(
          ".media-preview--pending",
        );
        const image = preview?.querySelector(
          ".js-selected-preview",
        );
        const currentPreview = scope.querySelector(
          ".media-preview:not(.media-preview--pending)",
        );
        const status = scope.querySelector(
          ".js-image-status",
        );
        const clearInput = scope.querySelector(
          `input[type="checkbox"][name="${input.name}-clear"]`,
        );

        const hasCurrentImage = Boolean(currentPreview);
        let temporaryUrl = null;

        const clearTemporaryUrl = () => {
          if (temporaryUrl) {
            URL.revokeObjectURL(temporaryUrl);
            temporaryUrl = null;
          }
        };

        const hidePendingPreview = () => {
          clearTemporaryUrl();

          if (preview) {
            preview.hidden = true;
          }

          if (image) {
            image.removeAttribute("src");
            image.alt = "";
          }
        };

        const setDefaultStatus = () => {
          if (!status) {
            return;
          }

          status.textContent = hasCurrentImage
            ? "La imagen actual se conservará."
            : "No hay una imagen configurada.";
        };

        input.addEventListener("change", () => {
          const file = input.files?.[0];

          if (!file || !file.type.startsWith("image/")) {
            hidePendingPreview();

            if (!clearInput?.checked) {
              setDefaultStatus();
            }

            return;
          }

          if (clearInput) {
            clearInput.checked = false;
          }

          currentPreview?.classList.remove(
            "is-pending-removal",
          );

          clearTemporaryUrl();
          temporaryUrl = URL.createObjectURL(file);

          if (image && preview) {
            image.src = temporaryUrl;
            image.alt = `Vista previa de ${file.name}`;
            preview.hidden = false;
          }

          if (status) {
            status.textContent = hasCurrentImage
              ? "La imagen nueva reemplazará la actual al guardar."
              : "La imagen seleccionada se guardará con el registro.";
          }
        });

        clearInput?.addEventListener("change", () => {
          if (clearInput.checked) {
            input.value = "";
            hidePendingPreview();
            currentPreview?.classList.add(
              "is-pending-removal",
            );

            if (status) {
              status.textContent =
                "La imagen actual se retirará al guardar.";
            }
          } else {
            currentPreview?.classList.remove(
              "is-pending-removal",
            );
            setDefaultStatus();
          }
        });

        window.addEventListener(
          "beforeunload",
          clearTemporaryUrl,
          { once: true },
        );
      });
  };

  initializeFallbackImages();
  initializeLocalPreviews();
})();

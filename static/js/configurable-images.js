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
              ".option-card__image",
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
            const preview = image.closest(
              ".media-preview",
            );

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
        input.addEventListener("change", () => {
          const file = input.files?.[0];
          const scope =
            input.closest(".option-row") ||
            input.closest(".form-card");

          const preview = scope?.querySelector(
            ".media-preview--pending",
          );

          const image = preview?.querySelector(
            ".js-selected-preview",
          );

          if (!preview || !image) {
            return;
          }

          if (!file || !file.type.startsWith("image/")) {
            preview.hidden = true;
            image.removeAttribute("src");
            return;
          }

          const temporaryUrl = URL.createObjectURL(file);

          image.src = temporaryUrl;
          image.alt = `Vista previa de ${file.name}`;
          preview.hidden = false;

          image.addEventListener(
            "load",
            () => URL.revokeObjectURL(temporaryUrl),
            { once: true },
          );
        });
      });
  };

  initializeFallbackImages();
  initializeLocalPreviews();
})();

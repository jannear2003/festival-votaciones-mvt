# Laboratorio de Estela Musical

Prototipo navegable de una página cultural vallenata. Su dirección visual usa una paleta de amanecer —`#FBC867`, `#FCA` (`#FFCCAA`), `#250806`, `#C25061` y `#ED7608`)— con fondos muy difuminados y paneles translúcidos tipo cristal esmerilado. El arte del paisaje y el acordeón está hecho en CSS: no requiere imágenes, audio ni recursos externos.

## Abrir

Abre `index.html` en un navegador moderno. El botón **Ver los efectos** lleva al escenario y dispara una muestra de notas. En el escenario, mueve el cursor o pulsa para crear partículas. Usa los controles para activar efectos, cambiar intensidad y color, o limpiar.

## Ajustes rápidos

- **Paleta y cristal:** las variables principales están al inicio de `styles.css`; las superficies y el fondo difuminado están en el bloque `Identidad cromática + vidrio esmerilado` al final.
- **Cantidad:** cambia el valor de `count` dentro de `burstAt` en `script.js`; `limits` limita las partículas simultáneas.
- **Velocidad:** modifica los rangos `duration` en `script.js` (menos milisegundos produce animaciones más rápidas).
- **Densidad:** el arreglo `distances` define la distancia mínima entre notas de la estela.

## Estructura

- `index.html`: navegación, contenido editorial, escenario y controles.
- `styles.css`: identidad visual, diseño adaptable, ilustraciones y animaciones.
- `script.js`: eventos de puntero y teclado, ajustes, límites y limpieza.

La función `addParticle` y `burstAt` concentran la lógica reutilizable para generar efectos y se pueden trasladar a otro contenedor en una futura integración.

## Acabado visual

La superficie usa capas transparentes con desenfoque, reflejos de borde y brillos interiores para aproximar el lenguaje **Liquid Glass**. El fondo conserva el amanecer cálido y difuminado; las transparencias se reducen automáticamente cuando el sistema solicita menos transparencia.

La fotografía de amanecer marino compartida como referencia está guardada en `assets/amanecer-mar.png` y se usa localmente como fondo difuminado. Mantén esa carpeta junto a `index.html` para conservar el fondo sin conexión.

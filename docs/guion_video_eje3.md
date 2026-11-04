# Guion del video de sustentación del Eje 3

## 1. Propósito

Este guion organiza una demostración técnica y funcional de máximo ocho minutos. El video debe demostrar los requisitos del Eje 3 sin intentar reproducir toda la suite ni leer el código completo.

## 2. Duración objetivo

- Duración máxima permitida: 8:00.
- Duración objetivo de edición: 7:20 a 7:40.
- Margen de seguridad: 20 a 40 segundos.
- Resolución recomendada: 1920 × 1080 o 1366 × 768.
- Navegador: una ventana normal para la cuenta autenticada y una ventana privada para CP-04.

## 3. Preparación antes de grabar

1. Usar la rama `develop`.
2. Confirmar que MySQL 8.4 está `healthy`.
3. Aplicar migraciones y verificar que no existan operaciones pendientes.
4. Ejecutar previamente las 108 pruebas.
5. Preparar una categoría con dos votaciones o subeventos para CP-02.
6. Preparar una segunda categoría habilitada para CP-03.
7. Preparar una categoría inactiva o no visible para CP-05.
8. Tener listas una cuenta pública A, una cuenta pública B y una cuenta administrativa.
9. No mostrar contraseñas durante la grabación.
10. Abrir previamente las pestañas necesarias y cerrar información irrelevante.
11. Configurar el puerto 8000 según la visibilidad requerida para la evaluación.
12. Probar micrófono, resolución y tamaño de fuente de terminal.

## 4. Datos de demostración

| Elemento | Valor de demostración |
|---|---|
| Edición | Festival de la Leyenda Vallenata 2027 |
| Categoría A | **PENDIENTE: categoría con dos subeventos** |
| Votación A1 | **PENDIENTE** |
| Votación A2 | **PENDIENTE** |
| Categoría B | **PENDIENTE: categoría diferente** |
| Votación B1 | **PENDIENTE** |
| Categoría no habilitada | **PENDIENTE** |
| Usuario público A | **PENDIENTE** |
| Usuario público B | **PENDIENTE** |
| Usuario administrativo | **PENDIENTE** |

Las cuentas deben ser ficticias y creadas exclusivamente para la demostración.

## 5. Estructura temporal

| Tiempo | Bloque | Casos principales |
|---:|---|---|
| 0:00-0:30 | Presentación y alcance | Contexto |
| 0:30-1:00 | Arquitectura y ambiente | MySQL, Django, ramas |
| 1:00-2:05 | Voto válido | CP-01 |
| 2:05-2:55 | Unicidad y otra categoría | CP-02, CP-03 |
| 2:55-3:35 | Autenticación y disponibilidad | CP-04, CP-05 |
| 3:35-4:05 | Opción ajena | CP-06 |
| 4:05-4:50 | Historial y administración | CP-07, CP-08 |
| 4:50-5:35 | Concurrencia | CP-09 |
| 5:35-6:20 | API | CP-10 |
| 6:20-7:10 | Pruebas y repositorio | 108 pruebas |
| 7:10-7:35 | Conclusiones | Cierre |

Duración objetivo: 7:35.

## 6. Guion detallado

### 0:00-0:30. Presentación

**Pantalla:** portada breve o página principal.

**Guion:**

> Buenas tardes. Presentamos el tercer eje del Sistema Web de Votaciones para el Festival de la Leyenda Vallenata. En esta entrega consolidamos el registro autenticado de votos, la unicidad por usuario, edición y categoría, la consulta de participaciones, la persistencia en MySQL, el control de concurrencia y una API pública de categorías. La demostración se ejecuta sobre Django 6.0.5 y MySQL 8.4.

**Mensaje clave:** el Eje 3 implementa el flujo real de participación y su protección técnica.

### 0:30-1:00. Ambiente y control de versiones

**Pantalla:** terminal con comandos previamente preparados.

**Mostrar:**

```bash
git branch --show-current
docker compose --env-file .env.mysql -f compose.mysql.yml ps
python manage.py shell -c "from django.db import connection; print(connection.vendor, connection.settings_dict['NAME'])"
```

**Guion:**

> La versión funcional está integrada en la rama develop mediante los Pull Requests 13 y 14. La rama main conserva la versión académica anterior. El contenedor MySQL 8.4 se encuentra saludable y Django confirma la conexión con la base festival_votaciones.

### 1:00-2:05. CP-01, voto válido

**Pantalla:** portal con Usuario A autenticado.

**Acciones:**

1. Abrir Votación A1.
2. Seleccionar una opción de demostración.
3. Abrir la revisión.
4. Confirmar.
5. Mostrar el comprobante.

**Guion:**

> Para CP-01, una cuenta autenticada consulta las opciones activas de una votación habilitada. El sistema presenta una etapa de revisión antes de confirmar. Al confirmar, Django crea dentro de una transacción la participación y el voto. El comprobante identifica la participación, pero no revela públicamente la opción seleccionada.

**Evitar:** leer todos los textos de la pantalla o escribir contraseñas durante la grabación.

### 2:05-2:55. CP-02 y CP-03

**Pantalla:** Votación A2 y posteriormente Votación B1.

**Acciones:**

1. Intentar participar en Votación A2 de la misma Categoría A.
2. Mostrar el rechazo.
3. Abrir Votación B1 de Categoría B.
4. Confirmar que el usuario sí puede participar.

**Guion:**

> En CP-02 intentamos votar en otro subevento de la misma categoría y edición. El sistema detecta la participación previa y rechaza el segundo intento. La regla no se limita a una votación: utiliza usuario, edición y categoría. En CP-03 accedemos a una categoría diferente y la participación sí se permite, porque la categoría cambia.

### 2:55-3:35. CP-04 y CP-05

**Pantalla:** ventana privada y categoría no habilitada.

**Acciones:**

1. Desde la ventana privada, abrir el detalle público.
2. Intentar participar y mostrar la redirección al login.
3. En la sesión autenticada, abrir directamente una votación no habilitada.
4. Mostrar respuesta controlada.

**Guion:**

> CP-04 demuestra que un visitante puede consultar la información pública, pero debe iniciar sesión antes de votar. La aplicación redirige al login y conserva la ruta de retorno. Para CP-05, una categoría inactiva, no visible o no publicada genera una respuesta controlada y no crea participaciones ni votos.

### 3:35-4:05. CP-06, opción ajena

**Pantalla:** terminal con la prueba aislada o evidencia preparada.

**Comando:**

```bash
python manage.py test elecciones.test_eje3_votacion_categoria.CasosPruebaEje3Tests.test_cp06_opcion_de_otra_categoria_es_rechazada -v 2
```

**Guion:**

> CP-06 manipula el identificador enviado al servidor para utilizar una opción de otra categoría. El formulario limita las opciones al conjunto activo de la votación y la vista valida nuevamente la relación. La solicitud se rechaza y los conteos de participación y voto permanecen en cero.

**Motivo para usar prueba:** permite demostrar la manipulación sin alterar datos reales desde las herramientas del navegador.

### 4:05-4:50. CP-07 y CP-08

**Pantalla:** Mis participaciones y administración.

**Acciones:**

1. Abrir `/cuenta/participaciones/`.
2. Mostrar las dos categorías votadas.
3. Abrir administración con cuenta autorizada.
4. Mostrar la participación y su relación con edición, categoría y votación.

**Guion:**

> En CP-07, Mis participaciones muestra únicamente los registros confirmados de la cuenta autenticada. No presenta participaciones ajenas ni revela la opción seleccionada. En CP-08 consultamos administrativamente la participación persistida y verificamos su relación con usuario, edición, categoría y votación en MySQL.

### 4:50-5:35. CP-09, concurrencia

**Pantalla:** terminal.

**Comando:**

```bash
python manage.py test elecciones.test_eje3_concurrencia -v 2
```

**Guion:**

> CP-09 utiliza TransactionTestCase, dos hilos, conexiones independientes y una barrera para intentar dos registros simultáneos. Uno de los intentos se registra y el otro es rechazado. La restricción única de MySQL garantiza que al final exista una sola participación y un solo voto para el usuario, la edición y la categoría.

**Mostrar:** nombre de la prueba, estado `ok` y resultado `OK`.

### 5:35-6:20. CP-10, API pública

**Pantalla:** navegador en `/api/categorias/`, preferiblemente con JSON indentado.

**Acciones:**

1. Mostrar la URL.
2. Señalar la edición activa.
3. Señalar una categoría, una votación y sus opciones.
4. Explicar los filtros y la ausencia de datos sensibles.

**Guion:**

> CP-10 corresponde al endpoint GET /api/categorias/. La respuesta se construye con datos reales de MySQL e incluye la edición activa, categorías activas y visibles, votaciones publicadas no canceladas y opciones activas. La API no expone usuarios, correos, participaciones o votos individuales, y rechaza métodos diferentes de GET con HTTP 405.

### 6:20-7:10. Suite y repositorio

**Pantalla:** salida final de pruebas y repositorio.

**Mostrar:**

```text
Found 108 test(s).
Ran 108 tests
OK
```

Luego mostrar brevemente:

- `README.md`.
- Migración `0006`.
- Archivos `test_eje3_*`.
- Carpeta `docs/`.

**Guion:**

> La suite completa ejecuta 108 pruebas sobre una base temporal MySQL y finaliza sin fallos ni errores. El repositorio público contiene las instrucciones de instalación, la migración de unicidad, las pruebas CP-01 a CP-10 y la documentación de evidencias. La rama main permanece separada hasta el cierre formal de la entrega.

### 7:10-7:35. Cierre

**Pantalla:** portal o diapositiva final.

**Guion:**

> En conclusión, el Eje 3 implementa un flujo de voto autenticado y verificable, garantiza un voto por usuario, edición y categoría incluso bajo concurrencia, permite consultar las participaciones y expone información pública mediante una API de solo lectura. La solución queda respaldada por MySQL 8.4, control de versiones y 108 pruebas automatizadas. Muchas gracias.

## 7. Relación CP-minuto

Completar únicamente después de exportar el video final.

| Caso | Inicio propuesto | Fin propuesto | Minuto definitivo |
|---|---:|---:|---:|
| CP-01 | 1:00 | 2:05 | **PENDIENTE** |
| CP-02 | 2:05 | 2:35 | **PENDIENTE** |
| CP-03 | 2:35 | 2:55 | **PENDIENTE** |
| CP-04 | 2:55 | 3:15 | **PENDIENTE** |
| CP-05 | 3:15 | 3:35 | **PENDIENTE** |
| CP-06 | 3:35 | 4:05 | **PENDIENTE** |
| CP-07 | 4:05 | 4:30 | **PENDIENTE** |
| CP-08 | 4:30 | 4:50 | **PENDIENTE** |
| CP-09 | 4:50 | 5:35 | **PENDIENTE** |
| CP-10 | 5:35 | 6:20 | **PENDIENTE** |

## 8. Comandos preparados para grabación

Guardar las salidas previamente y ejecutar solo los comandos necesarios durante el video.

```bash
# Ambiente
git branch --show-current
docker compose --env-file .env.mysql -f compose.mysql.yml ps

# CP-06
python manage.py test elecciones.test_eje3_votacion_categoria.CasosPruebaEje3Tests.test_cp06_opcion_de_otra_categoria_es_rechazada -v 2

# CP-09
python manage.py test elecciones.test_eje3_concurrencia -v 2

# CP-10
python manage.py test elecciones.test_eje3_api_categorias -v 2

# Suite completa
python manage.py test -v 2
```

No es necesario ejecutar la suite completa durante la grabación si su duración afecta el límite. Puede mostrarse la salida completa previamente guardada, indicando con transparencia que corresponde a la ejecución final de validación.

## 9. Recomendaciones de grabación

1. Grabar en una sola resolución, sin cambiar escalado a mitad del video.
2. Aumentar el tamaño de fuente de terminal a un mínimo visual equivalente a 16 px.
3. Ocultar marcadores, extensiones o pestañas que contengan información personal.
4. Mantener el cursor fuera del texto importante.
5. Evitar tiempos muertos de carga mediante pestañas preabiertas.
6. No acelerar tanto el video que resulte ilegible.
7. Usar transiciones simples o cortes directos.
8. No añadir música que interfiera con la voz.
9. Exportar en MP4 con códec H.264 y audio AAC si la plataforma lo admite.
10. Revisar el video completo después de exportar.

## 10. Lista de verificación final

- [ ] El video dura 8:00 o menos.
- [ ] Se menciona MySQL 8.4.
- [ ] Se identifica la regla usuario, edición y categoría.
- [ ] CP-01 a CP-10 tienen evidencia o explicación verificable.
- [ ] CP-09 muestra la prueba concurrente en `ok`.
- [ ] CP-10 muestra la URL y el JSON de la API.
- [ ] La suite de 108 pruebas aparece claramente.
- [ ] No se muestran contraseñas, tokens, cookies o archivos `.env`.
- [ ] No se revelan opciones de usuarios reales.
- [ ] Los minutos definitivos se registraron en matriz, ficha y PDF.
- [ ] El enlace abre en una ventana privada.
- [ ] La versión final es la misma referenciada en el PDF.

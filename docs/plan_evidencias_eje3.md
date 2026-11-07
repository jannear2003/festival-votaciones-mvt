# Plan de evidencias del Eje 3

## 1. Propósito

Este plan define las evidencias funcionales, técnicas y documentales necesarias para demostrar el cumplimiento de la tercera entrega del sistema de votaciones. Cada evidencia debe relacionarse con un requisito, un caso de prueba CP-01 a CP-10 o una condición de reproducibilidad del proyecto.

## 2. Criterios generales de captura

1. Utilizar la rama `develop`, que contiene los Pull Requests 13 y 14 del Eje 3.
2. Ejecutar las evidencias oficiales con MySQL 8.4, no con SQLite.
3. Mantener visible únicamente la información necesaria para demostrar el requisito.
4. No mostrar contraseñas, archivos `.env`, tokens, cookies, claves de sesión o secretos.
5. No utilizar correos, nombres completos u otros datos personales reales.
6. No revelar la opción elegida por una persona real. Utilizar cuentas y datos de demostración.
7. Recortar espacios irrelevantes, pero conservar la barra de dirección, el nombre de la ruta o el comando cuando sean necesarios para interpretar la evidencia.
8. Usar formato PNG. Evitar JPEG para terminales y texto, porque introduce pérdida de nitidez.
9. Mantener una resolución mínima recomendada de 1366 × 768 para capturas completas.
10. Si una evidencia requiere más de una captura, usar sufijos `-a`, `-b` y `-c`.
11. Conservar también salidas de terminal en formato `.txt` cuando la legibilidad en el PDF pueda verse afectada.
12. Registrar el minuto definitivo del video después de la edición final.

## 3. Organización de archivos

Las evidencias se almacenarán en:

```text
evidencias/eje3/
```

Convención de nombres:

```text
figura-NN-descripcion-breve.png
figura-NN-descripcion-breve.txt
```

Los nombres deben escribirse en minúsculas, sin espacios y sin tildes.

## 4. Inventario maestro

| Figura | Evidencia | Relación | Formato | Estado |
|---|---|---|---|---|
| 01 | Estado de ramas y protección de `main` | Control de versiones | PNG/TXT | Pendiente |
| 02 | MySQL 8.4 saludable y Django conectado | Ambiente | PNG/TXT | Pendiente |
| 03 | Migración `0006` y restricción única | Regla central | PNG/TXT | Pendiente |
| 04 | Flujo de voto válido | CP-01 | PNG | Pendiente |
| 05 | Rechazo de segundo voto en la misma categoría | CP-02 | PNG | Pendiente |
| 06 | Voto permitido en otra categoría | CP-03 | PNG | Pendiente |
| 07 | Autenticación obligatoria | CP-04 | PNG | Pendiente |
| 08 | Categoría no habilitada | CP-05 | PNG | Pendiente |
| 09 | Opción ajena rechazada | CP-06 | PNG/TXT | Pendiente |
| 10 | Mis participaciones | CP-07 | PNG | Pendiente |
| 11 | Consulta administrativa y persistencia | CP-08 | PNG | Pendiente |
| 12 | Prueba de concurrencia | CP-09 | PNG/TXT | Pendiente |
| 13 | API de categorías | CP-10 | PNG | Pendiente |
| 14 | Suite completa de 114 pruebas | Calidad | PNG/TXT | Pendiente |
| 15 | Repositorio público y README | Reproducibilidad | PNG | Pendiente |

## 5. Detalle de evidencias

### Figura 01. Estado de ramas y protección de `main`

**Archivo:** `figura-01-estado-ramas.png` y `figura-01-estado-ramas.txt`.

**Objetivo:** demostrar que el Eje 3 está integrado en `develop` y que `main` conserva la versión académica anterior.

**Comandos sugeridos:**

```bash
git log -3 --oneline --decorate
git log -1 --oneline --decorate origin/main
git merge-base --is-ancestor 468c2df origin/develop; echo $?
git merge-base --is-ancestor 468c2df origin/main; echo $?
```

**Debe mostrar:**

- `develop` en el merge del Pull Request 14.
- Commit `468c2df` contenido en `develop`.
- Código de salida `1` al comprobar el mismo commit en `main`.

**Ocultar:** nombres de usuario del sistema operativo si no son necesarios.

**Pie sugerido:** Estado del control de versiones: el Eje 3 está integrado en `develop`, mientras `main` permanece en la versión académica anterior.

### Figura 02. MySQL saludable y conexión de Django

**Archivo:** `figura-02-mysql-conexion.png` y `figura-02-mysql-conexion.txt`.

**Objetivo:** demostrar que las evidencias se producen sobre MySQL 8.4.

**Comandos sugeridos:**

```bash
docker compose --env-file .env.mysql -f compose.mysql.yml ps
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Motor:', connection.vendor); print('Base:', connection.settings_dict['NAME']); print('Host:', connection.settings_dict['HOST'])"
```

**Debe mostrar:** contenedor `festival-mysql` en estado `healthy`, motor `mysql` y base `festival_votaciones`.

**Ocultar:** contraseñas y contenido de `.env.mysql`.

**Pie sugerido:** Contenedor MySQL 8.4 saludable y conexión real de Django con la base `festival_votaciones`.

### Figura 03. Migración y restricción única

**Archivo:** `figura-03-restriccion-unica-mysql.png` y `figura-03-restriccion-unica-mysql.txt`.

**Objetivo:** evidenciar la protección física de la regla usuario, edición y categoría.

**Comandos sugeridos:**

```bash
python manage.py showmigrations elecciones
python manage.py shell -c "from django.db import connection; r=connection.introspection.get_constraints(connection.cursor(), 'elecciones_participacion'); d=r['una_participacion_por_usuario_edicion_categoria']; print('Columnas:', d['columns']); print('Unica:', d['unique'])"
```

**Debe mostrar:** migración `0006` aplicada, columnas `usuario_id`, `edicion_id`, `categoria_id` y valor `Unica: True`.

**Pie sugerido:** Restricción única de MySQL que impide más de una participación por usuario, edición y categoría.

### Figura 04. CP-01, voto válido

**Archivo:** `figura-04-cp01-voto-valido.png`.

**Objetivo:** demostrar el flujo selección, revisión, confirmación y comprobante.

**Capturas recomendadas:**

- `figura-04a-cp01-seleccion.png`.
- `figura-04b-cp01-revision.png`.
- `figura-04c-cp01-comprobante.png`.

**Debe mostrar:** usuario autenticado, opción de demostración, pantalla de revisión y comprobante con referencia.

**Ocultar:** contraseña y cualquier opción de una persona real. El comprobante no debe revelar públicamente la opción elegida.

**Pie sugerido:** Flujo válido de participación autenticada, desde la selección hasta la generación del comprobante.

### Figura 05. CP-02, segundo voto rechazado

**Archivo:** `figura-05-cp02-voto-duplicado.png`.

**Objetivo:** demostrar que un segundo subevento de la misma categoría no permite otro voto.

**Preparación:** crear dos votaciones de demostración dentro de la misma categoría y edición. Confirmar previamente un voto en la primera.

**Debe mostrar:** mensaje de participación ya registrada para la categoría y ausencia de un segundo voto.

**Evidencia complementaria:** consulta ORM que muestre un total de una participación y un voto para la combinación.

**Pie sugerido:** Rechazo del segundo intento en otro subevento de la misma categoría y edición.

### Figura 06. CP-03, voto en categoría diferente

**Archivo:** `figura-06-cp03-otra-categoria.png`.

**Objetivo:** demostrar que el mismo usuario sí puede votar en una categoría distinta.

**Debe mostrar:** comprobante de la segunda categoría o historial con dos categorías diferentes.

**Pie sugerido:** La unicidad se aplica por categoría; el usuario puede participar válidamente en una categoría diferente.

### Figura 07. CP-04, autenticación obligatoria

**Archivo:** `figura-07-cp04-autenticacion-obligatoria.png`.

**Objetivo:** demostrar que un visitante puede consultar información pública, pero debe iniciar sesión para votar.

**Debe mostrar:** invitación para registrarse o iniciar sesión y redirección a `/cuentas/login/` con parámetro `next` cuando se intenta participar.

**Pie sugerido:** El portal permite consulta pública, pero exige autenticación antes de acceder al flujo de votación.

### Figura 08. CP-05, categoría no habilitada

**Archivo:** `figura-08-cp05-categoria-no-habilitada.png`.

**Objetivo:** demostrar el rechazo de una categoría inactiva, no visible o no publicada.

**Debe mostrar:** pantalla controlada de votación no disponible o respuesta HTTP 403.

**Evidencia complementaria:** salida de la prueba `test_cp05_categoria_no_habilitada_rechaza_operacion`.

**Pie sugerido:** El servidor rechaza la participación cuando la categoría o la votación no están habilitadas.

### Figura 09. CP-06, opción ajena rechazada

**Archivo:** `figura-09-cp06-opcion-ajena.png` y `figura-09-cp06-opcion-ajena.txt`.

**Objetivo:** demostrar la validación del servidor frente a un identificador de opción manipulado.

**Método recomendado:** usar la prueba automatizada o una solicitud controlada mediante Django Test Client. No manipular datos reales desde el navegador.

**Debe mostrar:** opción inválida rechazada, cero participaciones nuevas y cero votos nuevos.

**Pie sugerido:** Una opción perteneciente a otra votación o categoría es rechazada por la validación del servidor.

### Figura 10. CP-07, Mis participaciones

**Archivo:** `figura-10-cp07-mis-participaciones.png`.

**Objetivo:** demostrar la consulta privada del historial del usuario autenticado.

**Debe mostrar:** edición, categoría, votación, referencia y fecha de las participaciones confirmadas.

**Ocultar:** datos de otros usuarios y opción seleccionada.

**Pie sugerido:** Historial privado con las participaciones confirmadas del usuario autenticado.

### Figura 11. CP-08, consulta administrativa

**Archivo:** `figura-11-cp08-consulta-administrativa.png`.

**Objetivo:** demostrar que la participación y el voto son consultables administrativamente y persisten en MySQL.

**Debe mostrar:** registro de participación con usuario de demostración, edición, categoría, votación, estado y referencia. Puede complementarse con el voto relacionado.

**Ocultar:** contraseñas, correos reales e información innecesaria sobre la selección.

**Pie sugerido:** Registro persistido y consultable desde la administración, relacionado con la edición, categoría y votación correspondientes.

### Figura 12. CP-09, concurrencia

**Archivo:** `figura-12-cp09-concurrencia.png` y `figura-12-cp09-concurrencia.txt`.

**Objetivo:** demostrar que dos intentos simultáneos no generan dos votos.

**Comando:**

```bash
python manage.py test elecciones.test_eje3_concurrencia -v 2
```

**Debe mostrar:** prueba `test_cp09_dos_intentos_simultaneos_registran_un_voto` finalizada en `ok` y resultado global `OK`.

**Evidencia técnica complementaria:** fragmento de `TransactionTestCase`, `ThreadPoolExecutor`, `Barrier`, `transaction.atomic()` y la restricción única.

**Pie sugerido:** Prueba concurrente sobre MySQL: dos intentos simultáneos conservan una sola participación y un solo voto.

### Figura 13. CP-10, API de categorías

**Archivo:** `figura-13-cp10-api-categorias.png`.

**Objetivo:** demostrar el endpoint público con datos reales.

**Ruta:** `/api/categorias/`.

**Debe mostrar:** barra de dirección, edición activa, categorías, votaciones y opciones. Activar la presentación con sangría del visor JSON si está disponible.

**Ocultar:** nada adicional si la API conserva el contrato actual, porque no expone información personal.

**Pie sugerido:** Respuesta JSON del endpoint GET `/api/categorias/`, construida con categorías, votaciones y opciones activas consultadas desde MySQL.

### Figura 14. Suite completa

**Archivo:** `figura-14-suite-108-pruebas.png` y `figura-14-suite-108-pruebas.txt`.

**Objetivo:** demostrar ausencia de regresiones y cobertura automatizada.

**Comando:**

```bash
python manage.py test -v 2
```

**Debe mostrar:** `Found 108 test(s)`, `Ran 114 tests` y `OK`.

**Pie sugerido:** Suite completa ejecutada sobre MySQL: 114 pruebas aprobadas, sin fallos ni errores.

### Figura 15. Repositorio y documentación

**Archivo:** `figura-15-repositorio-readme.png`.

**Objetivo:** demostrar disponibilidad y reproducibilidad de la entrega.

**Debe mostrar:** repositorio público, rama `develop`, migración `0006`, archivos de pruebas del Eje 3 y README actualizado.

**Verificación adicional:** abrir el enlace en una ventana privada para confirmar acceso sin sesión institucional.

**Pie sugerido:** Repositorio público con código, migraciones, pruebas y documentación de reproducción del Eje 3.

## 6. Evidencias en texto

Además de las capturas, guardar las salidas completas de terminal:

```text
evidencias/eje3/figura-01-estado-ramas.txt
evidencias/eje3/figura-02-mysql-conexion.txt
evidencias/eje3/figura-03-restriccion-unica-mysql.txt
evidencias/eje3/figura-09-cp06-opcion-ajena.txt
evidencias/eje3/figura-12-cp09-concurrencia.txt
evidencias/eje3/figura-14-suite-108-pruebas.txt
```

Una forma segura de capturar salida es:

```bash
comando 2>&1 | tee evidencias/eje3/nombre-evidencia.txt
```

Antes de confirmar el archivo en Git, revisar que no contenga secretos o datos personales.

## 7. Lista de control antes del PDF

- [ ] Todas las figuras tienen numeración y título coherentes.
- [ ] Cada CP tiene al menos una evidencia funcional o técnica.
- [ ] Las capturas corresponden a `develop`.
- [ ] MySQL 8.4 está identificado en las evidencias técnicas.
- [ ] No aparecen contraseñas, tokens, archivos `.env` o cookies.
- [ ] No se revelan opciones seleccionadas por usuarios reales.
- [ ] Las imágenes son legibles al insertarlas en el PDF.
- [ ] Los archivos PNG y TXT están en `evidencias/eje3/`.
- [ ] Los pies de figura explican qué se demuestra, no solo qué se ve.
- [ ] Los minutos del video se completaron después de la edición final.
- [ ] Los enlaces del repositorio y del video se validaron en ventana privada.
- [ ] La suite final muestra 114 pruebas aprobadas.

## 8. Registro de minutos del video

| Evidencia | Caso | Minuto inicial | Minuto final | Estado |
|---|---|---:|---:|---|
| Flujo de voto válido | CP-01 | Pendiente | Pendiente | Pendiente |
| Segundo voto rechazado | CP-02 | Pendiente | Pendiente | Pendiente |
| Otra categoría permitida | CP-03 | Pendiente | Pendiente | Pendiente |
| Autenticación obligatoria | CP-04 | Pendiente | Pendiente | Pendiente |
| Categoría no habilitada | CP-05 | Pendiente | Pendiente | Pendiente |
| Opción ajena rechazada | CP-06 | Pendiente | Pendiente | Pendiente |
| Mis participaciones | CP-07 | Pendiente | Pendiente | Pendiente |
| Consulta administrativa | CP-08 | Pendiente | Pendiente | Pendiente |
| Concurrencia | CP-09 | Pendiente | Pendiente | Pendiente |
| API de categorías | CP-10 | Pendiente | Pendiente | Pendiente |

Los minutos se registrarán únicamente después de exportar y revisar el video definitivo, cuya duración máxima permitida es de ocho minutos.

# Matriz de casos de prueba del Eje 3

## 1. Propósito

Esta matriz relaciona los diez casos de prueba obligatorios del Eje 3 con las reglas de negocio, la evidencia funcional, la persistencia en MySQL 8.4 y las pruebas automatizadas del proyecto.

## 2. Ambiente de validación

- Rama funcional validada: `develop`.
- Motor de base de datos: MySQL 8.4.
- Base principal: `festival_votaciones`.
- Base temporal de pruebas: `test_festival_votaciones`.
- Python: 3.12.
- Django: 6.0.5.
- Suite de referencia: 108 pruebas aprobadas, 0 fallos y 0 errores.
- Migración principal del Eje 3: `0006_unicidad_usuario_edicion_categoria`.
- Restricción de base de datos: `una_participacion_por_usuario_edicion_categoria`.

## 3. Convenciones

- **Usuario A:** cuenta pública autenticada para ejecutar el flujo principal.
- **Usuario B:** segunda cuenta pública para validar separación entre usuarios.
- **Categoría A:** categoría activa y visible con al menos dos votaciones o subeventos.
- **Categoría B:** categoría activa y visible diferente de la Categoría A.
- **Votación A1 y A2:** votaciones diferentes vinculadas con la Categoría A.
- **Votación B1:** votación vinculada con la Categoría B.
- **Opción válida:** opción activa perteneciente a la votación probada.

No deben utilizarse datos personales reales ni revelarse contraseñas, archivos `.env`, claves de sesión u opciones seleccionadas por usuarios reales.

## 4. Resumen de cobertura

| Caso | Requisito validado | Prueba automatizada | Estado técnico |
|---|---|---|---|
| CP-01 | Registro de un voto válido | `test_cp01_voto_valido_se_registra_en_mysql` | Aprobado |
| CP-02 | Unicidad por usuario, edición y categoría | `test_cp02_no_permite_segundo_voto_en_misma_categoria` y `test_cp02_mysql_rechaza_duplicado_en_otro_subevento` | Aprobado |
| CP-03 | Voto permitido en categoría diferente | `test_cp03_permite_votar_en_categoria_diferente` | Aprobado |
| CP-04 | Autenticación obligatoria | `test_cp04_visitante_no_puede_ingresar_al_flujo` | Aprobado |
| CP-05 | Rechazo de categoría no habilitada | `test_cp05_categoria_no_habilitada_rechaza_operacion` | Aprobado |
| CP-06 | Rechazo de opción ajena | `test_cp06_opcion_de_otra_categoria_es_rechazada` | Aprobado |
| CP-07 | Consulta privada de participaciones | `test_cp07_historial_muestra_las_categorias_votadas` | Aprobado |
| CP-08 | Persistencia y consulta administrativa | `test_cp08_registro_persistido_es_consultable` | Aprobado |
| CP-09 | Control de concurrencia | `test_cp09_dos_intentos_simultaneos_registran_un_voto` | Aprobado |
| CP-10 | API GET de categorías | Siete pruebas en `test_eje3_api_categorias.py` | Aprobado |

## 5. Detalle de los casos

### CP-01. Registrar un voto válido

**Objetivo:** comprobar que un usuario autenticado puede seleccionar, revisar y confirmar una opción válida, y que la participación y el voto quedan almacenados en MySQL.

**Precondiciones:**

1. Usuario A registrado y autenticado.
2. Edición activa.
3. Categoría A activa y visible.
4. Votación A1 publicada, abierta y dentro de sus fechas.
5. Opción válida activa.
6. Usuario A sin participación confirmada previa en Categoría A para dicha edición.

**Procedimiento manual:**

1. Iniciar sesión como Usuario A.
2. Abrir Votación A1.
3. Seleccionar una opción activa.
4. Pulsar la acción de revisión.
5. Verificar la selección presentada.
6. Confirmar el voto.
7. Abrir el comprobante y “Mis participaciones”.
8. Consultar la participación desde administración o MySQL.

**Resultado esperado:**

- Se crea una participación confirmada asociada con Usuario A, la edición, Categoría A y Votación A1.
- Se crea un único voto relacionado con la opción válida.
- Se presenta un comprobante sin revelar públicamente la opción seleccionada.
- “Mis participaciones” incluye la categoría y la edición.

**Prueba automatizada:** `elecciones.test_eje3_votacion_categoria.CasosPruebaEje3Tests.test_cp01_voto_valido_se_registra_en_mysql`.

**Evidencia sugerida:** `evidencias/eje3/figura-04-cp01-voto-valido.png`.

**Minuto del video:** por completar después de la grabación.

### CP-02. Rechazar un segundo voto en la misma categoría y edición

**Objetivo:** verificar que el mismo usuario no pueda votar dos veces en una categoría y edición, aunque use otra votación o subevento.

**Precondiciones:**

1. Categoría A contiene Votación A1 y Votación A2.
2. Usuario A ya confirmó un voto en Votación A1.
3. Votación A2 está publicada y habilitada.

**Procedimiento manual:**

1. Mantener autenticado al Usuario A.
2. Abrir Votación A2, perteneciente a la misma Categoría A.
3. Intentar iniciar o confirmar una nueva participación.
4. Consultar el total de participaciones y votos del usuario en Categoría A.

**Resultado esperado:**

- El sistema informa que la cuenta ya registró una participación en esa categoría para la edición.
- No se crea una segunda participación confirmada.
- No se crea un segundo voto.
- MySQL conserva un único registro para la combinación usuario, edición y categoría.

**Pruebas automatizadas:**

- `test_cp02_no_permite_segundo_voto_en_misma_categoria`.
- `test_cp02_mysql_rechaza_duplicado_en_otro_subevento`.

**Evidencia sugerida:** `evidencias/eje3/figura-05-cp02-voto-duplicado.png`.

**Minuto del video:** por completar después de la grabación.

### CP-03. Permitir un voto en una categoría diferente

**Objetivo:** demostrar que la regla de unicidad no impide participar en categorías diferentes de la misma edición.

**Precondiciones:**

1. Usuario A ya votó en Categoría A.
2. Categoría B está activa y visible.
3. Votación B1 está publicada y habilitada.
4. Usuario A no ha votado en Categoría B.

**Procedimiento manual:**

1. Abrir Votación B1 con Usuario A autenticado.
2. Seleccionar una opción válida.
3. Revisar y confirmar.
4. Abrir “Mis participaciones”.

**Resultado esperado:**

- Se permite la participación en Categoría B.
- El usuario conserva una participación confirmada en Categoría A y otra en Categoría B.
- No se viola la restricción única, porque la categoría es diferente.

**Prueba automatizada:** `test_cp03_permite_votar_en_categoria_diferente`.

**Evidencia sugerida:** `evidencias/eje3/figura-06-cp03-otra-categoria.png`.

**Minuto del video:** por completar después de la grabación.

### CP-04. Impedir el voto de un visitante no autenticado

**Objetivo:** confirmar que el flujo de votación exige autenticación.

**Precondiciones:** votación publicada y habilitada; navegador sin sesión iniciada.

**Procedimiento manual:**

1. Cerrar sesión o abrir una ventana privada.
2. Consultar el detalle público de una votación.
3. Intentar acceder a la ruta de participación.

**Resultado esperado:**

- El visitante puede consultar la información pública y las opciones.
- El formulario de voto no se habilita para el visitante.
- El acceso al flujo de participación redirige al inicio de sesión y conserva el parámetro `next`.

**Prueba automatizada:** `test_cp04_visitante_no_puede_ingresar_al_flujo`.

**Evidencia sugerida:** `evidencias/eje3/figura-07-cp04-autenticacion-obligatoria.png`.

**Minuto del video:** por completar después de la grabación.

### CP-05. Rechazar una categoría no habilitada

**Objetivo:** validar que una categoría inactiva, no visible o con votación no disponible no admita participaciones.

**Precondiciones:** categoría inactiva o no visible; votación asociada no publicada o no habilitada.

**Procedimiento manual:**

1. Configurar una categoría como inactiva o no visible.
2. Intentar acceder directamente a la ruta de participación de su votación.
3. Verificar los registros de participación y voto.

**Resultado esperado:**

- La respuesta es controlada y rechaza la operación, con estado HTTP 403 en el flujo implementado.
- No se crean participaciones ni votos.

**Prueba automatizada:** `test_cp05_categoria_no_habilitada_rechaza_operacion`.

**Evidencia sugerida:** `evidencias/eje3/figura-08-cp05-categoria-no-habilitada.png`.

**Minuto del video:** por completar después de la grabación.

### CP-06. Rechazar una opción perteneciente a otra categoría

**Objetivo:** comprobar que el servidor no confía únicamente en las opciones visibles del formulario y rechaza un identificador manipulado.

**Precondiciones:** Usuario A autenticado; Votación A1 habilitada; opción activa perteneciente a Categoría B.

**Procedimiento técnico:**

1. Enviar un `POST` a la ruta de participación de Votación A1.
2. Utilizar como valor de `opcion` el identificador de una opción de Categoría B.
3. Consultar participaciones y votos.

**Resultado esperado:**

- El formulario rechaza la opción por no pertenecer al conjunto permitido.
- No se crea participación.
- No se crea voto.

**Prueba automatizada:** `test_cp06_opcion_de_otra_categoria_es_rechazada`.

**Evidencia sugerida:** `evidencias/eje3/figura-09-cp06-opcion-ajena.png`.

**Minuto del video:** por completar después de la grabación.

### CP-07. Consultar las categorías votadas por el usuario

**Objetivo:** verificar que “Mis participaciones” muestre únicamente las participaciones confirmadas del usuario autenticado.

**Precondiciones:** Usuario A con votos confirmados en Categoría A y Categoría B; Usuario B con una participación diferente.

**Procedimiento manual:**

1. Iniciar sesión como Usuario A.
2. Abrir `/cuenta/participaciones/`.
3. Revisar las categorías, ediciones, votaciones, referencias y fechas mostradas.
4. Confirmar que no se muestren participaciones de Usuario B.

**Resultado esperado:**

- Se presentan las categorías votadas por Usuario A.
- Solo se incluyen participaciones confirmadas.
- No se revelan datos de otros usuarios ni la opción seleccionada.

**Prueba automatizada:** `test_cp07_historial_muestra_las_categorias_votadas`.

**Evidencia sugerida:** `evidencias/eje3/figura-10-cp07-mis-participaciones.png`.

**Minuto del video:** por completar después de la grabación.

### CP-08. Consultar el registro persistido

**Objetivo:** confirmar que el voto y su participación pueden consultarse desde la administración y que coinciden con los datos persistidos en MySQL.

**Precondiciones:** voto válido confirmado; cuenta administrativa autorizada.

**Procedimiento manual:**

1. Ingresar al panel administrativo o Django Admin.
2. Consultar la participación confirmada.
3. Consultar el voto relacionado.
4. Verificar edición, categoría, votación, usuario, referencia y fecha.
5. Contrastar el registro mediante ORM o consulta de MySQL sin exponer la opción en evidencia pública innecesaria.

**Resultado esperado:**

- La participación y el voto existen y están relacionados.
- La participación corresponde al usuario, edición y categoría esperados.
- El voto corresponde a la votación y opción válidas.

**Prueba automatizada:** `test_cp08_registro_persistido_es_consultable`.

**Evidencia sugerida:** `evidencias/eje3/figura-11-cp08-consulta-administrativa.png`.

**Minuto del video:** por completar después de la grabación.

### CP-09. Controlar dos intentos concurrentes

**Objetivo:** demostrar que dos intentos simultáneos del mismo usuario sobre la misma categoría y edición no generan dos votos.

**Precondiciones:** MySQL 8.4; misma cuenta, edición y categoría; dos votaciones diferentes en la misma categoría.

**Procedimiento automatizado:**

1. Crear dos conexiones independientes.
2. Sincronizar dos hilos con una barrera.
3. Intentar registrar simultáneamente dos participaciones y dos votos.
4. Consultar los registros finales.

**Resultado esperado:**

- Un intento se registra.
- El segundo intento es rechazado por integridad o por control operacional de MySQL.
- La base conserva una participación confirmada y un voto.

**Prueba automatizada:** `elecciones.test_eje3_concurrencia.ConcurrenciaEje3Tests.test_cp09_dos_intentos_simultaneos_registran_un_voto`.

**Evidencia sugerida:** `evidencias/eje3/figura-12-cp09-concurrencia.png`.

**Minuto del video:** por completar después de la grabación.

### CP-10. Consultar la API de categorías

**Objetivo:** comprobar que `GET /api/categorias/` devuelve JSON válido con información real de MySQL.

**Precondiciones:** edición activa; categorías activas y visibles; votaciones publicadas; opciones activas.

**Procedimiento manual:**

1. Abrir `/api/categorias/` en el navegador o Postman.
2. Confirmar el estado HTTP 200 y el tipo `application/json`.
3. Revisar la edición, categorías, votaciones y opciones.
4. Enviar un método `POST` para validar el rechazo HTTP 405.

**Resultado esperado:**

- La respuesta incluye la edición activa.
- Incluye únicamente categorías activas y visibles.
- Incluye votaciones publicadas no canceladas y opciones activas.
- No expone usuarios, correos, sesiones, referencias o votos individuales.
- Los métodos diferentes de GET reciben HTTP 405.

**Pruebas automatizadas:** siete pruebas en `elecciones/test_eje3_api_categorias.py`.

**Evidencia sugerida:** `evidencias/eje3/figura-13-cp10-api-categorias.png`.

**Minuto del video:** por completar después de la grabación.

## 6. Ejecución automatizada

Casos CP-01 a CP-08:

```bash
python manage.py test elecciones.test_eje3_votacion_categoria -v 2
```

Caso CP-09:

```bash
python manage.py test elecciones.test_eje3_concurrencia -v 2
```

Caso CP-10:

```bash
python manage.py test elecciones.test_eje3_api_categorias -v 2
```

Suite completa:

```bash
python manage.py test -v 2
```

Resultado de referencia:

```text
Found 108 test(s).
Ran 108 tests
OK
```

## 7. Criterio de cierre

Un caso se considera aprobado cuando:

1. El resultado observado coincide con el esperado.
2. No se crean registros no autorizados.
3. La evidencia no revela datos sensibles.
4. La prueba automatizada correspondiente finaliza en `ok`.
5. El resultado queda registrado en la tabla final del PDF.
6. El minuto del video se actualiza después de la grabación definitiva.

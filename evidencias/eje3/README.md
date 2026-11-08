# Evidencias del Eje 3

## 1. Propósito

Esta carpeta reúne las evidencias funcionales, técnicas y documentales de la tercera entrega del Sistema Web de Votaciones para el Festival de la Leyenda Vallenata.

Las evidencias deben demostrar:

- Ejecución sobre MySQL 8.4.
- Integración del Eje 3 en la rama `develop`.
- Conservación de `main` como versión académica anterior mientras se cierra la entrega.
- Regla de un voto por usuario, edición y categoría.
- Persistencia de participaciones y votos.
- Validaciones CP-01 a CP-10.
- Control de concurrencia.
- Funcionamiento de `GET /api/categorias/`.
- Ejecución satisfactoria de 114 pruebas automatizadas.

El detalle de cada captura se encuentra en:

```text
docs/plan_evidencias_eje3.md
```

La trazabilidad de los casos está documentada en:

```text
docs/matriz_casos_prueba_eje3.md
```

## 2. Ubicación

Todos los archivos deben almacenarse en:

```text
evidencias/eje3/
```

No deben mezclarse con `evidencias/eje2/`, porque cada carpeta corresponde a una entrega académica diferente.

## 3. Convención de nombres

Utilizar nombres en minúsculas, sin espacios y sin tildes:

```text
figura-NN-descripcion-breve.png
figura-NN-descripcion-breve.txt
```

Cuando una evidencia requiera varias capturas:

```text
figura-04a-cp01-seleccion.png
figura-04b-cp01-revision.png
figura-04c-cp01-comprobante.png
```

No usar nombres genéricos como:

```text
captura1.png
imagen-final.png
prueba-nueva.png
```

## 4. Inventario previsto

| Figura | Archivo principal | Contenido |
|---:|---|---|
| 01 | `figura-01-estado-ramas.png` | Eje 3 en `develop` y ausencia en `main` |
| 02 | `figura-02-mysql-conexion.png` | MySQL saludable y Django conectado |
| 03 | `figura-03-restriccion-unica-mysql.png` | Migración `0006` y restricción única |
| 04 | `figura-04-cp01-voto-valido.png` | Selección, revisión, confirmación y comprobante |
| 05 | `figura-05-cp02-voto-duplicado.png` | Segundo voto rechazado en la misma categoría |
| 06 | `figura-06-cp03-otra-categoria.png` | Voto permitido en una categoría diferente |
| 07 | `figura-07-cp04-autenticacion-obligatoria.png` | Redirección del visitante al login |
| 08 | `figura-08-cp05-categoria-no-habilitada.png` | Rechazo de categoría o votación no disponible |
| 09 | `figura-09-cp06-opcion-ajena.png` | Opción ajena rechazada por el servidor |
| 10 | `figura-10-cp07-mis-participaciones.png` | Historial privado del usuario |
| 11 | `figura-11-cp08-consulta-administrativa.png` | Participación y voto persistidos |
| 12 | `figura-12-cp09-concurrencia.png` | Dos intentos simultáneos, un solo voto |
| 13 | `figura-13-cp10-api-categorias.png` | Respuesta JSON de la API |
| 14 | `figura-14-suite-108-pruebas.png` | Suite completa aprobada |
| 15 | `figura-15-repositorio-readme.png` | Repositorio público y documentación |

## 5. Archivos de texto recomendados

Además de las capturas, conservar las salidas completas de terminal:

```text
figura-01-estado-ramas.txt
figura-02-mysql-conexion.txt
figura-03-restriccion-unica-mysql.txt
figura-09-cp06-opcion-ajena.txt
figura-12-cp09-concurrencia.txt
figura-14-suite-108-pruebas.txt
```

Ejemplo de captura de salida:

```bash
python manage.py test elecciones.test_eje3_concurrencia -v 2 \
  2>&1 | tee evidencias/eje3/figura-12-cp09-concurrencia.txt
```

Antes de confirmar un archivo `.txt`, revisar que no contenga secretos, contraseñas, tokens, cookies o información personal.

## 6. Requisitos de calidad visual

- Formato preferido: PNG.
- Resolución recomendada: 1366 × 768 o superior.
- El texto debe ser legible al insertarse en el PDF.
- La terminal debe usar una fuente equivalente a 16 px o mayor.
- La barra de dirección debe permanecer visible cuando la ruta sea parte de la evidencia.
- Evitar áreas vacías, pestañas innecesarias y notificaciones del sistema.
- No deformar las imágenes al insertarlas en el documento.
- Mantener una relación de aspecto consistente.
- Si una captura es demasiado extensa, dividirla en partes identificadas con sufijos.

## 7. Protección de información

No almacenar en esta carpeta:

- Archivos `.env` o `.env.mysql`.
- Contraseñas.
- Tokens de GitHub, Azure u otros servicios.
- Cookies o identificadores de sesión.
- Claves de sesión de participaciones.
- Correos o datos personales reales.
- Opciones seleccionadas por usuarios reales.
- Copias de bases de datos con información sensible.
- Capturas de administradores de contraseñas.

Utilizar exclusivamente cuentas y datos de demostración.

## 8. Relación con CP-01 a CP-10

| Caso | Evidencia mínima |
|---|---|
| CP-01 | Flujo válido y comprobante |
| CP-02 | Rechazo del segundo voto y conteo final igual a uno |
| CP-03 | Participación válida en otra categoría |
| CP-04 | Redirección al inicio de sesión |
| CP-05 | Respuesta controlada para categoría no habilitada |
| CP-06 | Prueba de opción ajena sin registros nuevos |
| CP-07 | Historial privado con categorías votadas |
| CP-08 | Consulta administrativa de participación y voto |
| CP-09 | Prueba concurrente finalizada en `ok` |
| CP-10 | JSON válido de `/api/categorias/` |

## 9. Pies de figura

Cada captura debe incluir en el PDF un pie que explique qué requisito demuestra. Evitar pies genéricos como “Pantalla del sistema”.

Ejemplo adecuado:

> **Figura 12. Prueba concurrente sobre MySQL.** Dos intentos simultáneos del mismo usuario para la misma edición y categoría conservan una sola participación y un solo voto.

Ejemplo inadecuado:

> **Figura 12. Terminal.**

## 10. Comandos de verificación

### Estado de ramas

```bash
git fetch --all --prune
git log -1 --oneline --decorate origin/main
git log -1 --oneline --decorate origin/develop
git merge-base --is-ancestor 468c2df origin/develop; echo $?
git merge-base --is-ancestor 468c2df origin/main; echo $?
```

### Conexión MySQL

```bash
docker compose --env-file .env.mysql -f compose.mysql.yml ps
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Motor:', connection.vendor); print('Base:', connection.settings_dict['NAME'])"
```

### Migración y restricción

```bash
python manage.py showmigrations elecciones
python manage.py shell -c "from django.db import connection; r=connection.introspection.get_constraints(connection.cursor(), 'elecciones_participacion'); d=r['una_participacion_por_usuario_edicion_categoria']; print('Columnas:', d['columns']); print('Unica:', d['unique'])"
```

### Casos específicos

```bash
python manage.py test elecciones.test_eje3_votacion_categoria -v 2
python manage.py test elecciones.test_eje3_concurrencia -v 2
python manage.py test elecciones.test_eje3_api_categorias -v 2
```

### Suite completa

```bash
python manage.py test -v 2
```

Resultado de referencia:

```text
Found 114 test(s).
Ran 114 tests
OK
```

## 11. Proceso de incorporación

1. Crear la captura o salida `.txt`.
2. Aplicar la convención de nombre.
3. Revisar que no contenga información sensible.
4. Guardarla en `evidencias/eje3/`.
5. Relacionarla en `docs/matriz_casos_prueba_eje3.md`.
6. Insertarla en el documento académico con su pie de figura.
7. Registrar el minuto definitivo del video.
8. Verificar legibilidad en el PDF exportado.
9. Confirmar el archivo en Git únicamente después de la revisión.

## 12. Lista de control

- [ ] Existen evidencias para CP-01 a CP-10.
- [ ] MySQL 8.4 aparece en las evidencias técnicas.
- [ ] La migración `0006` aparece aplicada.
- [ ] La restricción única muestra sus tres columnas.
- [ ] CP-09 muestra el resultado `ok`.
- [ ] CP-10 muestra la URL y un JSON legible.
- [ ] La suite completa muestra 114 pruebas y `OK`.
- [ ] Todas las capturas son PNG y legibles.
- [ ] Las salidas importantes también se conservaron en TXT.
- [ ] No existen secretos ni datos personales.
- [ ] Los pies de figura explican el requisito demostrado.
- [ ] Los minutos del video fueron actualizados después de la edición final.
- [ ] El repositorio y el video fueron probados en ventana privada.

## 13. Estado de elaboración

Actualizar esta tabla durante el cierre:

| Evidencia | Capturada | Revisada | Incluida en PDF | Minuto registrado |
|---|---|---|---|---|
| Figura 01 | Sí | Sí | No | No aplica |
| Figura 02 | Sí | Sí | No | No aplica |
| Figura 03 | Sí | Sí | No | No aplica |
| Figura 04A | Sí | Sí | No | No |
| Figura 04B | Sí | Sí | No | No |
| Figura 05 | Sí | Sí | No | No |
| Figura 06 | Sí | Sí | No | No |
| Figura 07 | Si | Si | No | No |
| Figura 08 | Si | Si | No | No |
| Figura 09 | Si | Si | No | No |
| Figura 10 | No | No | No | No |
| Figura 11 | Sí | Sí | No | No |
| Figura 12 | Si | Si | No | No |
| Figura 13 | Si | Si | No | No |
| Figura 14 | Si | Si | No | No aplica |
| Figura 15 | No | No | No | No aplica |

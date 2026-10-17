# Matriz de trazabilidad - Actividad evaluativa Eje 2

## Convenciones

- **Cumple:** implementado, probado y listo para evidenciar.
- **Cumple con ajuste:** implementado, pero requiere captura o explicación final.
- **Pendiente:** falta producir o completar.
- **Adicional:** supera el mínimo de la actividad.

## Criterio 1. Django, MySQL y modelo de datos

| ID | Requisito | Estado | Implementación | Prueba o evidencia | Extracto previsto | Responsable |
|---|---|---|---|---|---|---|
| C1.1 | Proyecto Django ejecutable | Cumple | `manage.py`, `config/` | `manage.py check` | Configuración básica | Pendiente |
| C1.2 | Patrón MVT | Cumple | `elecciones/`, `templates/` | Portal y administración | Modelo, vista y plantilla | Pendiente |
| C1.3 | Conexión MySQL | Cumple | `config/settings.py` | `vendor=mysql`, MySQL 8.4 | Bloque `DATABASES` | Pendiente |
| C1.4 | Servicio reproducible | Cumple | `compose.mysql.yml` | Contenedor `healthy` | Servicio y healthcheck | Pendiente |
| C1.5 | Edición a Categoría | Cumple | `elecciones/models.py` | Relación persistida | Clave foránea | Pendiente |
| C1.6 | Categoría a Votación | Cumple | `elecciones/models.py` | Relación persistida | Clave foránea | Pendiente |
| C1.7 | Votación a Opción | Cumple | `elecciones/models.py` | Relación persistida | Clave foránea | Pendiente |
| C1.8 | Migraciones en MySQL | Cumple | `elecciones/migrations/` | Migraciones aplicadas | Operación representativa | Pendiente |
| C1.9 | Persistencia real | Cumple con ajuste | MySQL `festival_votaciones` | Captura pendiente | Consulta ORM | Pendiente |

## Criterio 2. Autenticación y administración

| ID | Requisito | Estado | Implementación | Prueba o evidencia | Extracto previsto | Responsable |
|---|---|---|---|---|---|---|
| C2.1 | Registro | Cumple | `RegistroUsuarioForm`, `registrar_usuario` | Pruebas de registro | Formulario y vista | Pendiente |
| C2.2 | Login | Cumple | `LoginPorRolView` | Redirección por rol | Vista de login | Pendiente |
| C2.3 | Logout | Cumple | URLs auth de Django | Logout mediante POST | Formulario de navegación | Pendiente |
| C2.4 | Contraseñas seguras | Cumple | Auth de Django | `check_password`, hash | Prueba automatizada | Pendiente |
| C2.5 | Ediciones | Cumple con ajuste | Django Admin | Captura pendiente | `EdicionAdmin` | Pendiente |
| C2.6 | Categorías | Cumple | Admin e interfaz propia | Pruebas existentes | Formulario/Admin | Pendiente |
| C2.7 | Votaciones | Cumple | Admin e interfaz propia | Pruebas existentes | Formulario y formset | Pendiente |
| C2.8 | Opciones | Cumple | Inline y formset | Pruebas existentes | `OpcionFormSet` | Pendiente |
| C2.9 | Autorización | Adicional | Middleware, grupos y permisos | Cuenta pública recibe 403 | Middleware | Pendiente |

## Criterio 3. Interfaces y entregables

| ID | Requisito | Estado | Implementación | Evidencia pendiente | Responsable |
|---|---|---|---|---|---|
| C3.1 | Portal dinámico | Cumple | `inicio`, plantillas | Captura con datos MySQL | Pendiente |
| C3.2 | Datos no codificados | Cumple | ORM y bucles de plantilla | Antes y después en Admin | Pendiente |
| C3.3 | Pruebas | Cumple | 26 pruebas sobre MySQL | Captura de salida final | Pendiente |
| C3.4 | Código relevante | Cumple con ajuste | Archivos identificados | Incorporar 10 a 14 extractos | Pendiente |
| C3.5 | PDF único | Pendiente | Documento final | Generar y validar enlaces | Pendiente |
| C3.6 | Repositorio | Cumple con ajuste | Rama `actividad-eje2-mysql` | Verificar acceso anónimo | Pendiente |
| C3.7 | Video | Pendiente | Por producir | Enlace y participación del equipo | Pendiente |

## Criterio 4. Trabajo colaborativo

| ID | Requisito | Estado | Evidencia necesaria | Responsable |
|---|---|---|---|---|
| C4.1 | Cuatro integrantes | Pendiente | Portada y equipo definitivo | Pendiente |
| C4.2 | Contribuciones reales | Pendiente | Commits, ramas o pull requests | Pendiente |
| C4.3 | Participación en video | Pendiente | Intervención de cuatro integrantes | Pendiente |
| C4.4 | Distribución del trabajo | Pendiente | Tabla en PDF | Pendiente |

## Extractos de código previstos

1. Configuración MySQL.
2. Modelo Edición.
3. Relación Categoría-Edición.
4. Relación Votación-Categoría.
5. Relación Opción-Votación.
6. `RegistroUsuarioForm`.
7. Vista `registrar_usuario`.
8. `LoginPorRolView`.
9. Middleware de autorización.
10. Django Admin.
11. Consulta pública.
12. Plantilla dinámica.
13. Prueba de registro y hash.
14. Prueba de autorización.

## Evidencias visuales pendientes

1. Estructura del proyecto.
2. MySQL 8.4 y tablas.
3. Migraciones aplicadas.
4. Django Admin.
5. Ediciones y categorías.
6. Votación con opciones.
7. Registro.
8. Login y logout.
9. Portal dinámico.
10. Suite de 26 pruebas.
11. Historial colaborativo.

# Plan de evidencias visuales - Actividad evaluativa Eje 2

## Propósito

Este documento controla las capturas y evidencias que se incorporarán al PDF académico. Cada figura se vincula con un requisito de la rúbrica, un extracto de código y una prueba o validación técnica.

## Reglas generales

- Utilizar datos académicos ficticios y coherentes.
- No mostrar contraseñas, tokens, cookies, cadenas de conexión ni archivos `.env`.
- Mantener una resolución uniforme y texto legible.
- Cerrar notificaciones personales y pestañas no relacionadas.
- Evitar capturas con errores, cursores sobre información sensible o formularios incompletos.
- Conservar la misma edición, categorías y votaciones en todas las figuras.
- Numerar las figuras según el orden definitivo del PDF.
- Incluir un pie de figura descriptivo y una explicación posterior.
- Tomar las capturas definitivas únicamente cuando la interfaz esté estable.

## Datos de demostración propuestos

Para mantener consistencia visual se utilizarán datos del Festival de la Leyenda Vallenata, sin información personal real:

- Festival: Festival de la Leyenda Vallenata.
- Edición: Edición 2027.
- Categorías: Acordeón profesional, Canción vallenata inédita y Piqueria.
- Votaciones: las configuradas en el fixture académico.
- Cuenta pública para evidencias: una cuenta ficticia sin privilegios.
- Cuenta administrativa: superusuario académico o cuenta de demostración con rol autorizado.

## Figura 1. Estructura del proyecto Django

- **Pantalla:** explorador de archivos de Codespaces.
- **Debe mostrar:** `config/`, `elecciones/`, `templates/`, `static/`, `docs/`, `manage.py`, `compose.mysql.yml` y `requirements.txt`.
- **No debe mostrar:** contenido de `.env`, `.env.mysql`, claves o archivos temporales.
- **Requisito:** C1.1 Proyecto Django y C1.2 patrón MVT.
- **Código asociado:** visión general; no requiere fragmento específico.
- **Prueba asociada:** `python manage.py check`.
- **Pie propuesto:** *Figura 1. Organización del proyecto Django conforme al patrón MVT y separación de configuración, lógica, plantillas y recursos estáticos.*
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 2. MySQL 8.4 operativo

- **Pantalla:** terminal con `docker compose ... ps`.
- **Debe mostrar:** contenedor `festival-mysql`, imagen `mysql:8.4`, estado `healthy` y puerto local `127.0.0.1:3306`.
- **Requisito:** C1.3 conexión MySQL y C1.4 servicio reproducible.
- **Código asociado:** Código 1 y `compose.mysql.yml`.
- **Prueba asociada:** estado saludable del contenedor.
- **Pie propuesto:** *Figura 2. Servicio MySQL 8.4 ejecutado en un contenedor aislado y accesible únicamente desde el entorno local de desarrollo.*
- **Precaución:** ocultar otras terminales y no mostrar `.env.mysql`.
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 3. Conexión efectiva entre Django y MySQL

- **Pantalla:** terminal con diagnóstico no sensible.
- **Debe mostrar:** proveedor `mysql`, versión 8.4 y base `festival_votaciones`.
- **Requisito:** C1.3 conexión MySQL.
- **Código asociado:** Código 1.
- **Prueba asociada:** apertura satisfactoria de la conexión mediante Django.
- **Pie propuesto:** *Figura 3. Verificación de la conexión de Django con la base de datos MySQL utilizada por la aplicación.*
- **Precaución:** no mostrar usuario, contraseña ni cadena completa.
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 4. Tablas de la aplicación en MySQL

- **Pantalla:** cliente MySQL dentro del contenedor.
- **Debe mostrar:** `django_migrations`, `auth_user`, `elecciones_edicion`, `elecciones_categoria`, `elecciones_votacion` y `elecciones_opcion`.
- **Requisito:** C1.5 a C1.9, modelos, migraciones y persistencia.
- **Código asociado:** Códigos 2 a 5.
- **Prueba asociada:** migraciones aplicadas.
- **Pie propuesto:** *Figura 4. Tablas generadas en MySQL a partir de los modelos y migraciones de Django.*
- **Precaución:** no mostrar datos de usuarios ni credenciales.
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 5. Administración de la edición y sus categorías

- **Pantalla:** Django Admin, formulario o listado de una edición.
- **Debe mostrar:** Edición 2027 y las categorías asociadas, con estado y visibilidad.
- **Requisito:** C1.5 y C2.5-C2.6.
- **Código asociado:** Códigos 2 y 3.
- **Prueba asociada:** relaciones persistidas y administración de categorías.
- **Pie propuesto:** *Figura 5. Administración de una edición anual y de las categorías relacionadas mediante Django Admin.*
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 6. Votación con opciones administrables

- **Pantalla:** formulario de votación en Django Admin o interfaz propia.
- **Debe mostrar:** categoría, tipo, fechas, estado, publicación y al menos dos opciones.
- **Requisito:** C1.6-C1.7 y C2.7-C2.8.
- **Código asociado:** Códigos 4, 5 y 10.
- **Prueba asociada:** creación y consulta de votaciones y opciones.
- **Pie propuesto:** *Figura 6. Configuración de una votación y de sus opciones participantes vinculadas con una categoría.*
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 7. Formulario de registro

- **Pantalla:** `/cuentas/registro/`.
- **Debe mostrar:** usuario, nombres, apellidos, correo, contraseña y confirmación, sin valores sensibles visibles.
- **Requisito:** C2.1 registro.
- **Código asociado:** Códigos 6 y 7.
- **Prueba asociada:** formulario disponible y registro válido.
- **Pie propuesto:** *Figura 7. Formulario de registro basado en los mecanismos de creación segura de usuarios de Django.*
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 8. Validación de registro

- **Pantalla:** formulario con un error controlado, por ejemplo correo duplicado o contraseñas diferentes.
- **Debe mostrar:** mensaje legible junto al campo correspondiente.
- **Requisito:** C2.1 y C2.4.
- **Código asociado:** Código 6.
- **Prueba asociada:** pruebas de correo duplicado y contraseñas diferentes.
- **Pie propuesto:** *Figura 8. Validación del registro ante datos duplicados o inconsistentes antes de almacenar la cuenta.*
- **Precaución:** no utilizar contraseñas reales.
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 9. Inicio de sesión

- **Pantalla:** `/cuentas/login/`.
- **Debe mostrar:** formulario de acceso y enlace de registro.
- **Requisito:** C2.2 login.
- **Código asociado:** Código 8.
- **Prueba asociada:** login de cuenta pública y administrativa.
- **Pie propuesto:** *Figura 9. Interfaz de inicio de sesión integrada con el sistema de autenticación de Django.*
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 10. Cuenta pública autenticada

- **Pantalla:** portal público después del login de una cuenta sin grupos.
- **Debe mostrar:** botón `Salir`; no debe mostrar `Panel` ni `Django Admin`.
- **Requisito:** C2.2 y autorización adicional C2.9.
- **Código asociado:** Códigos 8 y 9.
- **Prueba asociada:** usuario público sin enlaces administrativos.
- **Pie propuesto:** *Figura 10. Navegación de una cuenta pública autenticada sin privilegios administrativos.*
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 11. Acceso administrativo denegado

- **Pantalla:** `/administracion/` abierta manualmente con una cuenta pública.
- **Debe mostrar:** título `Acceso denegado`, explicación y enlace al portal.
- **Requisito:** autorización adicional C2.9.
- **Código asociado:** Código 9.
- **Prueba asociada:** respuesta HTTP 403 para cuenta pública.
- **Pie propuesto:** *Figura 11. Respuesta controlada ante un intento de acceso administrativo realizado por una cuenta sin rol autorizado.*
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 12. Panel de una cuenta administrativa

- **Pantalla:** `/administracion/` con superusuario o rol administrativo.
- **Debe mostrar:** indicadores de ediciones, categorías y votaciones, además de enlaces autorizados.
- **Requisito:** C2.5-C2.8.
- **Código asociado:** Código 9 y vistas administrativas.
- **Prueba asociada:** superusuario con acceso al panel.
- **Pie propuesto:** *Figura 12. Panel de configuración disponible para una cuenta con privilegios administrativos.*
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 13. Portal público dinámico

- **Pantalla:** página principal.
- **Debe mostrar:** edición activa y votaciones publicadas recuperadas desde MySQL.
- **Requisito:** C3.1 y C3.2.
- **Código asociado:** Códigos 11 y 12.
- **Prueba asociada:** consulta ORM y renderizado de datos almacenados.
- **Pie propuesto:** *Figura 13. Portal público construido dinámicamente con información persistida en MySQL.*
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 14. Suite automatizada sobre MySQL

- **Pantalla:** terminal al finalizar `python manage.py test`.
- **Debe mostrar:** `Found 26 test(s)`, `Ran 26 tests` y `OK`.
- **Requisito:** C3.3 pruebas y resultados.
- **Código asociado:** Códigos 13 y 14.
- **Prueba asociada:** suite completa.
- **Pie propuesto:** *Figura 14. Resultado satisfactorio de las 26 pruebas automatizadas ejecutadas sobre una base temporal MySQL.*
- **Precaución:** recortar salidas repetitivas de configuración de roles si afectan la legibilidad, sin alterar el resultado.
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Figura 15. Historial colaborativo

- **Pantalla:** historial de commits, contribuciones o pull requests de GitHub.
- **Debe mostrar:** aportes verificables de los cuatro integrantes.
- **Requisito:** C4.1-C4.4 trabajo colaborativo.
- **Código asociado:** no aplica.
- **Prueba asociada:** historial Git.
- **Pie propuesto:** *Figura 15. Evidencia de participación y contribuciones técnicas de los integrantes del equipo.*
- **Estado:** Pendiente.
- **Responsable:** Pendiente.

## Registro de capturas

| Figura | Archivo de imagen | Fecha | Revisada | Incorporada al PDF | Observaciones |
|---|---|---|---|---|---|
| 1 | Pendiente | Pendiente | No | No | |
| 2 | Pendiente | Pendiente | No | No | |
| 3 | Pendiente | Pendiente | No | No | |
| 4 | Pendiente | Pendiente | No | No | |
| 5 | Pendiente | Pendiente | No | No | |
| 6 | Pendiente | Pendiente | No | No | |
| 7 | Pendiente | Pendiente | No | No | |
| 8 | Pendiente | Pendiente | No | No | |
| 9 | Pendiente | Pendiente | No | No | |
| 10 | Pendiente | Pendiente | No | No | |
| 11 | Pendiente | Pendiente | No | No | |
| 12 | Pendiente | Pendiente | No | No | |
| 13 | Pendiente | Pendiente | No | No | |
| 14 | Pendiente | Pendiente | No | No | |
| 15 | Pendiente | Pendiente | No | No | |

## Criterio de aprobación de una figura

Una figura se considera lista cuando:

1. Presenta únicamente la información necesaria.
2. El texto es legible al insertarse en el PDF.
3. No contiene datos sensibles.
4. Coincide con el estado final del código.
5. Tiene requisito, extracto y prueba asociados.
6. Cuenta con pie de figura y explicación posterior.
7. Fue revisada por al menos otro integrante.

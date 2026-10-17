# Registro de pruebas - Actividad evaluativa Eje 2

## Entorno

```text
Python: 3.12
Django: 6.0.5
Base de datos: MySQL 8.4
Controlador: mysqlclient
Contenedores: Docker y Docker Compose
Rama: actividad-eje2-mysql
```

## Bases utilizadas

- Principal: `festival_votaciones`.
- Temporal de pruebas: `test_festival_votaciones`.

Django crea la base temporal, aplica las migraciones, ejecuta la suite y elimina la base al finalizar.

## Comandos de validación

```bash
python manage.py check
python manage.py test
```

## Resultado consolidado

```text
Pruebas encontradas: 26
Pruebas aprobadas: 26
Fallos: 0
Errores: 0
Resultado: OK
```

## Áreas cubiertas

### Configuración y modelos

- Migraciones compatibles con MySQL.
- Relaciones del modelo.
- Datos configurables por edición.

### Roles y permisos

- Administrador general.
- Configurador.
- Operador.
- Publicador.
- Auditor.

### Registro y autenticación

- Formulario visible.
- Registro válido.
- Hash de contraseña.
- Usuario duplicado rechazado.
- Correo duplicado rechazado.
- Contraseñas diferentes rechazadas.
- Login y logout.

### Autorización

- Cuenta pública sin acceso al panel.
- Cuenta pública sin enlaces administrativos.
- Cuenta pública sin acceso a Django Admin.
- Superusuario con acceso administrativo.
- Redirección posterior al login según rol.
- Parámetro `next` conservado.

## Evidencia para el PDF

La captura definitiva debe mostrar únicamente el resumen de la ejecución completa, incluyendo:

```text
Found 26 test(s).
Ran 26 tests in ...
OK
```

No debe mostrar contraseñas, tokens, archivos `.env` ni cadenas de conexión.

## Interpretación académica

Las pruebas demuestran que la aplicación opera sobre MySQL, que las cuentas se registran mediante los mecanismos de Django y que la autenticación no implica automáticamente autorización administrativa.

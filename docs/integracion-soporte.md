# Integración de soporte TG Technology → TG Management

La integración usa HTTP POST servidor-a-servidor, sin compartir bases de datos ni ejecutar procesos de otro proyecto.

## Configuración local

1. En ambos procesos definir la **misma** variable `TG_SUPPORT_API_TOKEN` con un secreto aleatorio largo (no subirlo a GitHub).
2. En TG Technology definir `TG_SUPPORT_API_URL=http://127.0.0.1:8001/soporte/api/tickets/`.
3. Iniciar TG Management: `python manage.py runserver 127.0.0.1:8001`.
4. Iniciar TG Technology en otro puerto: `python manage.py runserver 127.0.0.1:8000`.
5. Crear en TG Management una empresa activa de tipo Cliente y un contacto activo con el correo de prueba.
6. Enviar desde `http://127.0.0.1:8000/soporte/` y verificar el ticket en `http://127.0.0.1:8001/soporte/tickets/`.

Generar un secreto: `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

## Producción

- Publicar TG Management en un endpoint HTTPS privado/protegido; configurar `TG_SUPPORT_API_URL=https://.../soporte/api/tickets/` solo en TG Technology.
- Definir el token en el gestor de secretos/variables de entorno de ambos servicios; no incluirlo en repositorio, plantillas ni JavaScript.
- Implementar controles perimetrales (limitación de solicitudes, monitoreo y restricciones de red) antes de abrir el endpoint a internet.
- La referencia UUID mantiene idempotencia en reintentos con el mismo identificador. Si la conexión falla, el formulario muestra un error y conserva la referencia.
- Ejecutar pruebas: `python manage.py test soporte.test_api` en Management y `python manage.py test core.test_support_api` en Technology.
- La API rechaza correos sin coincidencia única con cliente activo; no crea clientes automáticamente.
- Revisar `DEBUG`, `ALLOWED_HOSTS`, claves de Django, HTTPS, almacenamiento y respaldos antes del despliegue. La configuración actual de desarrollo NO es apta para producción.

## Notificaciones por correo

TG Management envía dos mensajes únicamente después de guardar un ticket nuevo:
- Confirmación HTML + texto al correo del reportante con el código del ticket.
- Aviso de texto a la casilla interna de soporte.

Los reintentos con el mismo UUID no vuelven a enviar correos. Un fallo SMTP se registra en logs y no anula el ticket.

**Desactivadas por defecto:** configurar estas variables en el servidor de TG Management (no en TG Technology):
- `TG_SUPPORT_EMAIL_ENABLED=true`
- `TG_SUPPORT_NOTIFICATION_EMAIL=<correo-interno>`
- `DEFAULT_FROM_EMAIL=<remitente-verificado>`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` (o `EMAIL_USE_SSL`)

Para pruebas sin correos reales, utilizar `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` o el backend de memoria en pruebas automatizadas.

Antes de habilitar SMTP real, verificar la identidad del dominio remitente y su configuración SPF/DKIM/DMARC. Para producción con alto volumen conviene usar una cola persistente y reintentos supervisados; la implementación actual es síncrona y registra errores, pero no reintenta automáticamente.

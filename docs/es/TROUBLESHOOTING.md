# Guía de Solución de Problemas

> 🌍 **Idiomas Disponibles**: [English](../en/TROUBLESHOOTING.md) | **Español** (Actual)

Esta guía proporciona soluciones para problemas comunes que puedes encontrar al usar los scripts de aprendizaje de AWS IoT Core.

## Tabla de Contenidos

- [Problemas de Configuración](#problemas-de-configuración)
- [Errores de Credenciales AWS](#errores-de-credenciales-aws)
- [Problemas de Conexión MQTT](#problemas-de-conexión-mqtt)
- [Errores de Certificados](#errores-de-certificados)
- [Problemas del Motor de Reglas IoT](#problemas-del-motor-de-reglas-iot)
- [Errores de Permisos](#errores-de-permisos)
- [Problemas de Limpieza](#problemas-de-limpieza)

## Problemas de Configuración

### Error: "ModuleNotFoundError: No module named 'boto3'"

**Síntoma:**
```
ModuleNotFoundError: No module named 'boto3'
```

**Solución:**
```bash
# Asegúrate de que el entorno virtual esté activado
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Error: "python: command not found"

**Síntoma:**
```
python: command not found
```

**Solución:**
```bash
# Usar python3 en su lugar
python3 scripts/setup_sample_data.py

# O crear un alias
alias python=python3
```

### Error: Versión de Python Incorrecta

**Síntoma:**
```
SyntaxError: invalid syntax (f-strings require Python 3.6+)
```

**Solución:**
```bash
# Verificar versión de Python
python --version

# Debe ser 3.7 o superior
# Si no, instalar Python más reciente o usar python3
python3 --version
```

## Errores de Credenciales AWS

### Error: "NoCredentialsError"

**Síntoma:**
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**Solución:**
```bash
# Opción 1: Variables de entorno
export AWS_ACCESS_KEY_ID=<tu-clave>
export AWS_SECRET_ACCESS_KEY=<tu-clave-secreta>
export AWS_DEFAULT_REGION=us-east-1

# Opción 2: AWS CLI
aws configure

# Opción 3: Verificar credenciales existentes
aws sts get-caller-identity
```

### Error: "AccessDenied" o "UnauthorizedOperation"

**Síntoma:**
```
ClientError: An error occurred (AccessDenied) when calling the ListThings operation
```

**Solución:**
1. **Verificar permisos AWS IAM** - Tu usuario/rol necesita permisos de AWS IoT
2. **Política AWS IAM mínima requerida:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:*",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:CreatePolicy",
                "iam:GetRole",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
```

### Error: Región Incorrecta

**Síntoma:**
```
EndpointConnectionError: Could not connect to the endpoint URL
```

**Solución:**
```bash
# Verificar región actual
aws configure get region

# Establecer región correcta
export AWS_DEFAULT_REGION=us-east-1

# O usar aws configure
aws configure set region us-east-1
```

## Problemas de Conexión MQTT

### Error: "Connection refused" o "Timeout"

**Síntoma:**
```
Connection failed: Connection refused
```

**Soluciones:**
1. **Verificar endpoint IoT:**
```bash
aws iot describe-endpoint --endpoint-type iot:Data-ATS
```

2. **Verificar certificados:**
```bash
ls -la certificates/
# Debe mostrar archivos .crt, .key, .pub
```

3. **Verificar política adjunta:**
```bash
aws iot list-attached-policies --target <certificate-arn>
```

### Error: "SSL/TLS handshake failed"

**Síntoma:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Soluciones:**
1. **Verificar archivos de certificado:**
```bash
# El certificado debe ser válido
openssl x509 -in certificates/thing-name/cert.crt -text -noout
```

2. **Verificar permisos de archivos:**
```bash
chmod 600 certificates/*/private.key
chmod 644 certificates/*/certificate.crt
```

3. **Regenerar certificados si es necesario:**
```bash
python scripts/certificate_manager.py
# Seleccionar opción 1 para crear nuevo certificado
```

### Error: "MQTT connection lost"

**Síntoma:**
```
Connection lost: The connection was lost
```

**Soluciones:**
1. **Verificar conectividad de red**
2. **Verificar que el certificado esté activo:**
```bash
aws iot describe-certificate --certificate-id <cert-id>
```

3. **Verificar límites de conexión** - AWS IoT tiene límites de conexiones concurrentes

## Errores de Certificados

### Error: "Certificate not found"

**Síntoma:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'certificates/...'
```

**Solución:**
```bash
# Ejecutar el gestor de certificados primero
python scripts/certificate_manager.py

# Seleccionar opción 1 para crear certificado
```

### Error: "Invalid certificate format"

**Síntoma:**
```
SSL: PEM lib error
```

**Soluciones:**
1. **Verificar formato del certificado:**
```bash
head -1 certificates/*/certificate.crt
# Debe comenzar con -----BEGIN CERTIFICATE-----
```

2. **Regenerar certificado si está corrupto:**
```bash
rm -rf certificates/thing-name/
python scripts/certificate_manager.py
```

### Error: "Certificate already exists"

**Síntoma:**
```
ResourceAlreadyExistsException: Certificate already exists
```

**Solución:**
- Esto es normal - el script continuará con el certificado existente
- O eliminar certificados existentes y crear nuevos

## Problemas del Motor de Reglas IoT

### Error: "Invalid SQL syntax"

**Síntoma:**
```
InvalidRequestException: Invalid SQL
```

**Soluciones:**
1. **Verificar sintaxis SQL:**
```sql
-- Correcto
SELECT * FROM 'topic/+/temperature' WHERE temperature > 25

-- Incorrecto (comillas faltantes en el tópico)
SELECT * FROM topic/+/temperature WHERE temperature > 25
```

2. **Usar el modo debug para ver SQL generado:**
```bash
python scripts/iot_rules_explorer.py --debug
```

### Error: "Role does not exist"

**Síntoma:**
```
InvalidRequestException: The role does not exist
```

**Solución:**
- El script debería crear el rol automáticamente
- Si falla, verificar permisos AWS IAM para crear roles
- Esperar unos segundos para propagación de AWS IAM

### Error: "Rule already exists"

**Síntoma:**
```
ResourceAlreadyExistsException: Rule already exists
```

**Solución:**
```bash
# Listar reglas existentes
aws iot list-topic-rules

# Eliminar regla existente si es necesario
aws iot delete-topic-rule --rule-name <rule-name>
```

## Errores de Permisos

### Error: "Access denied to IoT service"

**Síntoma:**
```
AccessDenied: User is not authorized to perform iot:CreateThing
```

**Solución:**
Agregar política AWS IAM con permisos IoT:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:CreateThing",
                "iot:ListThings",
                "iot:DescribeThing",
                "iot:CreateThingType",
                "iot:CreateThingGroup",
                "iot:CreateKeysAndCertificate",
                "iot:AttachThingPrincipal",
                "iot:CreatePolicy",
                "iot:AttachPrincipalPolicy"
            ],
            "Resource": "*"
        }
    ]
}
```

### Error: "Cannot create IAM role"

**Síntoma:**
```
AccessDenied: User is not authorized to perform iam:CreateRole
```

**Solución:**
Agregar permisos AWS IAM:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:CreatePolicy",
                "iam:GetRole",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
```

## Problemas de Limpieza

### Error: "Cannot delete Thing with attached certificates"

**Síntoma:**
```
InvalidRequestException: Cannot delete thing with attached certificates
```

**Solución:**
```bash
# El script de limpieza maneja esto automáticamente
python scripts/cleanup_sample_data.py

# O manualmente:
# 1. Desadjuntar certificados
aws iot detach-thing-principal --thing-name <thing-name> --principal <cert-arn>

# 2. Eliminar Thing
aws iot delete-thing --thing-name <thing-name>
```

### Error: "Thing Type in use"

**Síntoma:**
```
InvalidRequestException: Cannot delete thing type while things of this type exist
```

**Solución:**
1. **Eliminar todos los Things de ese tipo primero**
2. **Deprecar el Thing Type:**
```bash
aws iot deprecate-thing-type --thing-type-name <type-name>
```
3. **Esperar 5 minutos, luego eliminar:**
```bash
aws iot delete-thing-type --thing-type-name <type-name>
```

## Comandos de Diagnóstico Útiles

### Verificar Estado General
```bash
# Verificar credenciales
aws sts get-caller-identity

# Verificar región
aws configure get region

# Verificar endpoint IoT
aws iot describe-endpoint --endpoint-type iot:Data-ATS

# Listar recursos IoT
aws iot list-things
aws iot list-certificates
aws iot list-thing-types
aws iot list-thing-groups
```

### Verificar Conectividad
```bash
# Probar conectividad a endpoint IoT
curl -I https://$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text)

# Verificar puertos (MQTT usa 8883, WebSocket usa 443)
telnet $(aws iot describe-endpoint --endpoint-type iot:Data-ATS --query endpointAddress --output text) 8883
```

### Logs de Debug
```bash
# Ejecutar cualquier script con modo debug
python scripts/setup_sample_data.py --debug
python scripts/iot_registry_explorer.py --debug
python scripts/certificate_manager.py --debug
python scripts/mqtt_client_explorer.py --debug
```

## Obtener Ayuda Adicional

Si los problemas persisten:

1. **Verificar logs de AWS CloudTrail** para errores de API
2. **Consultar documentación de AWS IoT**: https://docs.aws.amazon.com/iot/
3. **Foros de AWS**: https://forums.aws.amazon.com/forum.jspa?forumID=210
4. **Crear issue en GitHub**: Incluir logs de debug y pasos para reproducir

## Información de Contacto de Soporte

- **GitHub Issues**: [Reportar problemas](https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics/issues)
- **Documentación AWS**: [Guía del Desarrollador de AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/)
- **Soporte AWS**: [Centro de Soporte AWS](https://console.aws.amazon.com/support/)
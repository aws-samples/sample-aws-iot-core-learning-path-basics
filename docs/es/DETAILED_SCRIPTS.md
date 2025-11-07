# Documentación Detallada de Scripts

> 🌍 **Idiomas Disponibles**: [English](../en/DETAILED_SCRIPTS.md) | **Español** (Actual)

Este documento proporciona documentación completa para todos los scripts de aprendizaje en el proyecto AWS IoT Core - Conceptos Básicos.

## Tabla de Contenidos

- [Explorador de API del Registro IoT](#explorador-de-api-del-registro-iot)
- [Gestor de Certificados y Políticas](#gestor-de-certificados-y-políticas)
- [Comunicación MQTT](#comunicación-mqtt)
- [Explorador de AWS IoT Device Shadow service](#explorador-de-device-shadow)
- [Explorador del Motor de Reglas IoT](#explorador-del-motor-de-reglas-iot)

## Explorador de API del Registro IoT

### Propósito
Herramienta interactiva para aprender las APIs del Registro de AWS IoT a través de llamadas reales de API con explicaciones detalladas. Este script te enseña las operaciones del Plano de Control utilizadas para gestionar dispositivos IoT, certificados y políticas.

**Nota**: AWS IoT Core proporciona muchas APIs a través de la gestión de dispositivos y seguridad. Este explorador se enfoca en 8 APIs centrales del Registro que son esenciales para entender la gestión del ciclo de vida de dispositivos IoT.

### Cómo Ejecutar

**Uso Básico:**
```bash
python scripts/iot_registry_explorer.py
```

**Con Modo Debug (detalles mejorados de API):**
```bash
python scripts/iot_registry_explorer.py --debug
```

### Sistema de Menú Interactivo

Cuando ejecutes el script, verás:
```
📋 Operaciones Disponibles:
1. Listar Things
2. Listar Certificados
3. Listar Thing Groups
4. Listar Thing Types
5. Describir Thing
6. Describir Thing Group
7. Describir Thing Type
8. Describir Endpoint
9. Salir

Seleccionar operación (1-9):
```

### APIs Soportadas con Detalles de Aprendizaje

#### 1. Listar Things
- **Propósito**: Recuperar todos los dispositivos IoT (Things) en tu cuenta
- **HTTP**: `GET /things`
- **Aprender**: Descubrimiento de dispositivos con opciones de paginación y filtrado
- **Opciones Disponibles**:
  - **Listado básico**: Muestra todos los Things
  - **Paginación**: Recuperar Things en lotes más pequeños
  - **Filtrar por Thing Type**: Encontrar vehículos de categorías específicas
  - **Filtrar por Atributo**: Encontrar vehículos con atributos específicos
- **Salida**: Array de objetos Thing con nombres, tipos, atributos

#### 2. Listar Certificados
- **Propósito**: Ver todos los certificados X.509 para autenticación de dispositivos
- **HTTP**: `GET /certificates`
- **Aprender**: Ciclo de vida de certificados, gestión de estado
- **Salida**: IDs de certificados, ARNs, fechas de creación, estado

#### 3. Listar Thing Groups
- **Propósito**: Ver organización de dispositivos y jerarquías
- **HTTP**: `GET /thing-groups`
- **Aprender**: Estrategias de agrupación de dispositivos, gestión a escala
- **Salida**: Nombres de grupos, ARNs, propiedades básicas

#### 4. Listar Thing Types
- **Propósito**: Ver plantillas de dispositivos y categorías
- **HTTP**: `GET /thing-types`
- **Aprender**: Clasificación de dispositivos, esquemas de atributos
- **Salida**: Nombres de tipos, descripciones, atributos buscables

#### 5. Describir Thing
- **Propósito**: Obtener información detallada sobre un dispositivo específico
- **HTTP**: `GET /things/{thingName}`
- **Entrada Requerida**: Nombre del Thing (ej. "Vehicle-VIN-001")
- **Aprender**: Metadatos de dispositivos, atributos, relaciones
- **Salida**: Detalles completos del Thing, versión, ARN

#### 6. Describir Thing Group
- **Propósito**: Ver detalles y propiedades del grupo
- **HTTP**: `GET /thing-groups/{thingGroupName}`
- **Entrada Requerida**: Nombre del grupo (ej. "CustomerFleet")
- **Aprender**: Jerarquías de grupos, políticas, atributos
- **Salida**: Propiedades del grupo, relaciones padre/hijo

#### 7. Describir Thing Type
- **Propósito**: Ver especificaciones y plantillas de tipos
- **HTTP**: `GET /thing-types/{thingTypeName}`
- **Entrada Requerida**: Nombre del tipo (ej. "SedanVehicle")
- **Aprender**: Definiciones de tipos, atributos buscables
- **Salida**: Propiedades del tipo, metadatos de creación

#### 8. Describir Endpoint
- **Propósito**: Obtener URLs de endpoint IoT para tu cuenta
- **HTTP**: `GET /endpoint`
- **Opciones de Entrada**: Tipo de endpoint (iot:Data-ATS, iot:CredentialProvider, iot:Jobs)
- **Aprender**: Diferentes tipos de endpoint y sus propósitos (iot:Jobs es para AWS IoT Jobs service)
- **Salida**: URL de endpoint HTTPS para conexiones de dispositivos
- **Salida**: URL de endpoint HTTPS para conexiones de dispositivos

### Características de Aprendizaje

**Para cada llamada de API, verás:**
- 🔄 **Nombre de llamada API** y descripción
- 🌐 **Solicitud HTTP** método y ruta completa
- ℹ️ **Explicación de operación** - qué hace y por qué
- 📥 **Parámetros de entrada** - qué datos estás enviando
- 💡 **Explicación de respuesta** - qué significa la salida
- 📤 **Payload de respuesta** - datos JSON reales devueltos

## Gestor de Certificados y Políticas

### Propósito
Aprender conceptos de seguridad de AWS IoT a través de gestión práctica de certificados y políticas. Este script enseña el modelo de seguridad completo: identidad de dispositivo (certificados) y autorización (políticas).

### Cómo Ejecutar

**Uso Básico:**
```bash
python scripts/certificate_manager.py
```

**Con Modo Debug (logging detallado de API):**
```bash
python scripts/certificate_manager.py --debug
```

### Menú Principal Interactivo

Cuando ejecutes el script, verás:
```
🔐 Gestor de Certificados y Políticas de AWS IoT
==================================================
Este script te enseña conceptos de seguridad de AWS IoT:
• Certificados X.509 para autenticación de dispositivos
• Adjuntar certificado a Thing
• Políticas IoT para autorización
• Adjuntar y desadjuntar políticas
• Registro de certificados externos
• Detalles completos de API para cada operación
==================================================

📋 Menú Principal:
1. Crear Certificado AWS IoT y Adjuntar a Thing (+ Política Opcional)
2. Registrar Certificado Externo y Adjuntar a Thing (+ Política Opcional)
3. Adjuntar Política a Certificado Existente
4. Desadjuntar Política de Certificado
5. Habilitar/Deshabilitar Certificado
6. Salir

Seleccionar opción (1-6):
```

### Áreas Clave de Aprendizaje

**Gestión de Certificados:**
- Creación y ciclo de vida de certificados X.509
- Adjuntar certificado-Thing para identidad de dispositivo
- Almacenamiento y organización de archivos locales
- Mejores prácticas de seguridad

**Gestión de Políticas:**
- Creación de políticas IoT con plantillas
- Adjuntar políticas a certificados
- Conceptos de control de permisos
- Consideraciones de seguridad de producción

**⚠️ Nota de Seguridad de Producción**: Las plantillas de políticas usan `"Resource": "*"` para propósitos de demostración. En producción, usa ARNs de recursos específicos y variables de política como `${iot:Connection.Thing.ThingName}` para restringir el acceso de dispositivos solo a sus recursos específicos.

## Comunicación MQTT

### Propósito
Experimentar comunicación IoT en tiempo real usando el protocolo MQTT. Aprender cómo los dispositivos se conectan a AWS IoT Core e intercambian mensajes de forma segura.

### Dos Opciones MQTT Disponibles

#### Opción A: MQTT Basado en Certificados (Recomendado para Aprendizaje)
**Archivo**: `scripts/mqtt_client_explorer.py`
**Autenticación**: Certificados X.509 (TLS mutuo)
**Mejor para**: Entender seguridad IoT de producción

#### Opción B: MQTT WebSocket (Método Alternativo)
**Archivo**: `scripts/mqtt_websocket_explorer.py`
**Autenticación**: Credenciales AWS IAM (SigV4)
**Mejor para**: Aplicaciones web y conexiones amigables con firewall

### Cliente MQTT Basado en Certificados

#### Cómo Ejecutar

**Uso Básico:**
```bash
python scripts/mqtt_client_explorer.py
```

**Con Modo Debug (diagnósticos de conexión):**
```bash
python scripts/mqtt_client_explorer.py --debug
```

#### Prerrequisitos
- **Los certificados deben existir** - Ejecutar `certificate_manager.py` primero
- **Política adjunta** - El certificado necesita permisos IoT
- **Asociación Thing** - El certificado debe estar adjunto a un Thing

#### Comandos Interactivos

Una vez conectado, usa estos comandos:

```bash
# Suscripción a Tópicos
📡 MQTT> sub device/+/temperature                  # Suscribirse con QoS 0
📡 MQTT> sub1 device/alerts/#                      # Suscribirse con QoS 1
📡 MQTT> unsub device/+/temperature               # Desuscribirse del tópico

# Publicación de Mensajes
📡 MQTT> pub device/sensor/temperature 23.5        # Publicar con QoS 0
📡 MQTT> pub1 device/alert "High temp!"            # Publicar con QoS 1
📡 MQTT> json device/data temp=23.5 humidity=65    # Publicar objeto JSON

# Comandos de Utilidad
📡 MQTT> test                                      # Enviar mensaje de prueba
📡 MQTT> status                                    # Mostrar info de conexión
📡 MQTT> messages                                  # Mostrar historial de mensajes
📡 MQTT> debug                                     # Diagnósticos de conexión
📡 MQTT> help                                      # Mostrar todos los comandos
📡 MQTT> quit                                      # Salir del cliente
```

## Explorador de AWS IoT Device Shadow service

### Propósito
Aprender el servicio AWS IoT Device Shadow a través de exploración práctica de sincronización de estado de dispositivos. Este script enseña el ciclo de vida completo del shadow: estado deseado, estado reportado y procesamiento delta.

### Cómo Ejecutar

**Uso Básico:**
```bash
python scripts/device_shadow_explorer.py
```

**Con Modo Debug (análisis detallado de mensajes shadow):**
```bash
python scripts/device_shadow_explorer.py --debug
```

### Prerrequisitos
- **Los certificados deben existir** - Ejecutar `certificate_manager.py` primero
- **Política con permisos shadow** - El certificado necesita permisos IoT shadow
- **Asociación Thing** - El certificado debe estar adjunto a un Thing

### Características Clave de Aprendizaje

#### Estructura del Documento Shadow
```json
{
  "state": {
    "desired": {
      "temperature": 25.0,
      "status": "active"
    },
    "reported": {
      "temperature": 22.5,
      "status": "online",
      "firmware_version": "1.0.0"
    },
    "delta": {
      "temperature": 25.0,
      "status": "active"
    }
  },
  "metadata": {
    "desired": {
      "temperature": {
        "timestamp": 1642248600
      }
    },
    "reported": {
      "temperature": {
        "timestamp": 1642248500
      }
    }
  },
  "version": 15,
  "timestamp": 1642248600
}
```

#### Comandos Interactivos

Una vez conectado, usa estos comandos:

```bash
# Operaciones Shadow
🌟 Shadow> get                                    # Solicitar documento shadow actual
🌟 Shadow> report                                 # Reportar estado local al shadow
🌟 Shadow> desire temperature=25.0 status=active # Establecer estado deseado

# Gestión de Dispositivo Local
🌟 Shadow> local                                  # Mostrar estado actual del dispositivo local
🌟 Shadow> edit                                   # Editar estado del dispositivo local interactivamente

# Comandos de Utilidad
🌟 Shadow> status                                 # Mostrar estado de conexión y shadow
🌟 Shadow> messages                               # Mostrar historial de mensajes shadow
🌟 Shadow> debug                                  # Diagnósticos de conexión
🌟 Shadow> help                                   # Mostrar todos los comandos
🌟 Shadow> quit                                   # Salir del explorador
```

## Explorador del Motor de Reglas IoT

### Propósito
Aprender el Motor de Reglas de AWS IoT a través de creación y gestión práctica de reglas. Este script enseña enrutamiento de mensajes, filtrado basado en SQL y configuración de acciones con configuración automática de roles AWS IAM.

### Cómo Ejecutar

**Uso Básico:**
```bash
python scripts/iot_rules_explorer.py
```

**Con Modo Debug (operaciones detalladas de API e AWS IAM):**
```bash
python scripts/iot_rules_explorer.py --debug
```

### Prerrequisitos
- **Credenciales AWS** - Permisos AWS IAM para Reglas IoT y gestión de roles AWS IAM
- **No se necesitan certificados** - El Motor de Reglas opera a nivel de servicio

### Características Clave de Aprendizaje

#### Flujo de Trabajo de Creación de Reglas
**Creación Guiada Paso a Paso:**
1. **Nomenclatura de Reglas** - Aprender convenciones de nomenclatura y requisitos de unicidad
2. **Selección de Tipo de Evento** - Elegir entre tipos de eventos IoT comunes o personalizados
3. **Construcción de Declaración SQL** - Construcción interactiva de cláusulas SELECT, FROM, WHERE
4. **Configuración de Acciones** - Configurar objetivos de republicación con roles AWS IAM apropiados
5. **Configuración Automática de AWS IAM** - El script crea y configura permisos necesarios

#### Ejemplos Completos de SQL
**Monitoreo de Temperatura:**
```sql
SELECT deviceId, timestamp, value 
FROM 'testRulesEngineTopic/+/temperature' 
WHERE value > 30
```

**Alertas de Batería:**
```sql
SELECT deviceId, battery, status 
FROM 'testRulesEngineTopic/+/battery' 
WHERE battery < 15
```

**Detección de Movimiento:**
```sql
SELECT * 
FROM 'testRulesEngineTopic/+/motion' 
WHERE value = 'detected'
```

### Configuración Automática de AWS IAM

#### Creación de Rol AWS IAM
**Configuración Automática:**
- Crea `IoTRulesEngineRole` si no existe
- Configura política de confianza para `iot.amazonaws.com`
- Adjunta permisos necesarios para acciones de republicación
- Maneja retrasos de consistencia eventual de AWS IAM

**📚 Aprender Más**: [Motor de Reglas de AWS IoT](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rules.html) | [Referencia SQL del Motor de Reglas](https://docs.aws.amazon.com/iot/latest/developerguide/iot-sql-reference.html)
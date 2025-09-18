# AWS IoT Core - Ruta de Aprendizaje - Conceptos Básicos

> 🌍 **Idiomas Disponibles** | **Available Languages** | **利用可能な言語** | **可用语言**
> 
> - [English](README.md) | **Español** (Actual) | [中文](README.zh-CN.md) | [日本語](README.ja.md) | [Português](README.pt-BR.md)
> - **Documentación**: [English](docs/en/) | [Español](docs/es/) | [中文](docs/zh-CN/) | [日本語](docs/ja/) | [Português](docs/pt-BR/)

Un conjunto completo de herramientas en Python para aprender los conceptos básicos de Amazon Web Services (AWS) IoT Core a través de exploración práctica. Los scripts interactivos demuestran gestión de dispositivos, seguridad, operaciones de API y comunicación MQTT con explicaciones detalladas.

## 🚀 Resumen Rápido - Ruta de Aprendizaje Completa

```bash
# 1. Clonar y configurar
git clone https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics.git
cd sample-aws-iot-core-learning-path-basics

# 2. Configurar entorno
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar credenciales de AWS
export AWS_ACCESS_KEY_ID=<tu-clave>
export AWS_SECRET_ACCESS_KEY=<tu-clave-secreta>
export AWS_DEFAULT_REGION=<tu-region (ej. us-east-1)>

# 4. Opcional: Configurar preferencia de idioma
export AWS_IOT_LANG=es  # 'en' para inglés, 'ja' para japonés, 'zh-CN' para chino

# 5. Secuencia completa de aprendizaje
python scripts/setup_sample_data.py          # Crear recursos IoT de ejemplo
python scripts/iot_registry_explorer.py      # Explorar APIs de AWS IoT
python scripts/certificate_manager.py        # Aprender seguridad IoT
python scripts/mqtt_client_explorer.py       # Comunicación MQTT en tiempo real
python scripts/device_shadow_explorer.py     # Sincronización de estado de dispositivos
python scripts/iot_rules_explorer.py         # Enrutamiento y procesamiento de mensajes
python scripts/cleanup_sample_data.py        # Limpiar recursos (¡IMPORTANTE!)
```

**⚠️ Advertencia de Costos**: Esto crea recursos reales de AWS (~$0.17 total). ¡Ejecuta la limpieza cuando termines!

## Audiencia Objetivo

**Audiencia Principal:** Desarrolladores cloud, arquitectos de soluciones, ingenieros DevOps nuevos en AWS IoT Core

**Prerrequisitos:** Conocimiento básico de AWS, fundamentos de Python, uso de línea de comandos

**Nivel de Aprendizaje:** Nivel asociado con enfoque práctico

## 🔧 Construido con SDKs de AWS

Este proyecto aprovecha los SDKs oficiales de AWS para proporcionar experiencias auténticas de AWS IoT Core:

### **Boto3 - SDK de AWS para Python**
- **Propósito**: Potencia todas las operaciones del Registro de AWS IoT, gestión de certificados e interacciones del Motor de Reglas
- **Versión**: `>=1.26.0`
- **Documentación**: [Documentación de Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- **APIs de IoT Core**: [Cliente IoT de Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot.html)

### **SDK de Dispositivos AWS IoT para Python**
- **Propósito**: Permite comunicación MQTT auténtica con AWS IoT Core usando certificados X.509
- **Versión**: `>=1.11.0`
- **Documentación**: [SDK de Dispositivos AWS IoT para Python v2](https://aws.github.io/aws-iot-device-sdk-python-v2/)
- **GitHub**: [aws-iot-device-sdk-python-v2](https://github.com/aws/aws-iot-device-sdk-python-v2)

**Por Qué Importan Estos SDKs:**
- **Listos para Producción**: Los mismos SDKs utilizados en aplicaciones IoT reales
- **Seguridad**: Soporte integrado para las mejores prácticas de seguridad de AWS IoT
- **Confiabilidad**: Bibliotecas oficiales mantenidas por AWS con manejo integral de errores
- **Valor de Aprendizaje**: Experimenta patrones auténticos de desarrollo de AWS IoT

## Tabla de Contenidos

- 🚀 [Inicio Rápido](#-resumen-rápido---ruta-de-aprendizaje-completa)
- ⚙️ [Instalación y Configuración](#️-instalación-y-configuración)
- 📚 [Scripts de Aprendizaje](#-scripts-de-aprendizaje)
- 🧹 [Limpieza de Recursos](#limpieza-de-recursos)
- 🛠️ [Solución de Problemas](#solución-de-problemas)
- 📖 [Documentación Avanzada](#-documentación-avanzada)

## ⚙️ Instalación y Configuración

### Prerrequisitos
- Python 3.10+
- Cuenta de AWS con permisos de IoT
- Acceso a terminal/línea de comandos
- OpenSSL (para funciones de certificados)

<details>
<summary>💰 <strong>Detalles de Costos de AWS</strong></summary>

**Este proyecto crea recursos reales de AWS que incurrirán en cargos (~$0.17 total).**

| Servicio | Uso | Costo Estimado (USD) |
|---------|-------|---------------------|
| **AWS IoT Core** | ~100 mensajes, 20 dispositivos | $0.10 |
| **IoT Device Shadow** | ~30 operaciones shadow | $0.04 |
| **IoT Rules Engine** | ~50 ejecuciones de reglas | $0.01 |
| **Almacenamiento de Certificados** | 20 certificados por 1 día | $0.01 |
| **Amazon CloudWatch Logs** | Logging básico | $0.01 |
| **Total Estimado** | **Sesión completa de aprendizaje** | **~$0.17** |

**Gestión de Costos:**
- ✅ Script de limpieza automática proporcionado
- ✅ Creación mínima de recursos
- ✅ Recursos de corta duración (sesión única)
- ⚠️ **Tu responsabilidad** ejecutar script de limpieza

**📊 Monitorear costos:** [Panel de Facturación de AWS](https://console.aws.amazon.com/billing/)

</details>



<details>
<summary>🔧 <strong>Pasos de Instalación Detallados</strong></summary>

**1. Clonar el Repositorio:**
```bash
git clone https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics.git
cd sample-aws-iot-core-learning-path-basics
```

**2. Instalar OpenSSL:**
- **macOS:** `brew install openssl`
- **Ubuntu/Debian:** `sudo apt-get install openssl`
- **Windows:** Descargar desde [Win32/Win64 OpenSSL](https://slproweb.com/products/Win32OpenSSL.html)

**3. Entorno Virtual (Recomendado):**
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

**4. Credenciales de AWS:**
```bash
export AWS_ACCESS_KEY_ID=<tu-clave-de-acceso>
export AWS_SECRET_ACCESS_KEY=<tu-clave-secreta>
export AWS_SESSION_TOKEN=<tu-token-de-sesion>  # Opcional
export AWS_DEFAULT_REGION=us-east-1
```

**5. Configuración de Idioma (Opcional):**
```bash
# Configurar preferencia de idioma para todos los scripts
export AWS_IOT_LANG=es     # Español (recomendado)
export AWS_IOT_LANG=en     # Inglés
export AWS_IOT_LANG=ja     # Japonés
export AWS_IOT_LANG=zh-CN  # Chino

# Alternativa: Los scripts preguntarán por el idioma si no está configurado
```

**Idiomas Soportados:**
- **Español** (`es`, `spanish`, `español`) - Traducción completa disponible
- **Inglés** (`en`, `english`) - Idioma por defecto
- **Japonés** (`ja`, `japanese`, `日本語`, `jp`) - Traducción completa disponible
- **Chino** (`zh-CN`, `chinese`, `中文`, `zh`) - Traducción completa disponible

## 🌍 Soporte Multi-Idioma

Todos los scripts de aprendizaje soportan interfaces en inglés, español, japonés y chino. El idioma afecta:

**✅ Lo que se Traduce:**
- Mensajes de bienvenida y contenido educativo
- Opciones de menú y prompts de usuario
- Momentos de aprendizaje y explicaciones
- Mensajes de error y confirmaciones
- Indicadores de progreso y mensajes de estado

**❌ Lo que Permanece en Idioma Original:**
- Respuestas de API de AWS (datos JSON)
- Nombres y valores de parámetros técnicos
- Métodos HTTP y endpoints
- Información de debug y logs
- Nombres de recursos de AWS e identificadores

**Opciones de Uso:**

**Opción 1: Variable de Entorno (Recomendada)**
```bash
# Configurar preferencia de idioma para todos los scripts
export AWS_IOT_LANG=es     # Español
export AWS_IOT_LANG=en     # Inglés
export AWS_IOT_LANG=ja     # Japonés
export AWS_IOT_LANG=zh-CN  # Chino

# Ejecutar cualquier script - el idioma se aplicará automáticamente
python scripts/iot_registry_explorer.py
```

**Opción 2: Selección Interactiva**
```bash
# Ejecutar sin variable de entorno - el script preguntará por el idioma
python scripts/setup_sample_data.py

# Ejemplo de salida:
# 🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择
# 1. English
# 2. Español (Spanish)
# 3. 日本語 (Japanese)
# 4. 中文 (Chinese)
# Seleccionar idioma (1-4): 2
```

**Scripts Soportados:**
- ✅ `setup_sample_data.py` - Creación de datos de ejemplo
- ✅ `iot_registry_explorer.py` - Exploración de API
- ✅ `certificate_manager.py` - Gestión de certificados
- ✅ `mqtt_client_explorer.py` - Comunicación MQTT
- ✅ `mqtt_websocket_explorer.py` - MQTT WebSocket
- ✅ `device_shadow_explorer.py` - Operaciones Device Shadow
- ✅ `iot_rules_explorer.py` - Exploración Rules Engine
- ✅ `cleanup_sample_data.py` - Limpieza de recursos

**Alternativa:** Usar configuración de AWS CLI o roles de AWS Identity and Access Management (IAM).

</details>

## 📚 Scripts de Aprendizaje

**Ruta de Aprendizaje Recomendada:**
1. `scripts/setup_sample_data.py` - Crear recursos IoT de ejemplo
2. `scripts/iot_registry_explorer.py` - Explorar APIs de AWS IoT
3. `scripts/certificate_manager.py` - Aprender seguridad IoT
4. `scripts/mqtt_client_explorer.py` - Comunicación MQTT en tiempo real
5. `scripts/device_shadow_explorer.py` - Sincronización de estado de dispositivos
6. `scripts/iot_rules_explorer.py` - Enrutamiento y procesamiento de mensajes
7. `scripts/cleanup_sample_data.py` - Limpiar recursos

**Lo que Aprenderás:**
- **Gestión de Dispositivos**: Things, Thing Types, Thing Groups
- **Seguridad**: Certificados X.509, políticas IoT, autenticación
- **APIs**: Detalles completos de solicitud/respuesta HTTP
- **MQTT**: Mensajería en tiempo real con certificados y WebSockets
- **Mejores Prácticas**: Gestión del ciclo de vida de recursos

**📚 Referencia**: [Guía del Desarrollador de AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/)

## Limpieza de Recursos

### Propósito
Limpiar adecuadamente los recursos de AWS para evitar cargos y mantener una cuenta ordenada. El script de limpieza solo elimina recursos creados por este proyecto de aprendizaje.

### Cómo Ejecutar

**Uso Básico:**
```bash
python scripts/cleanup_sample_data.py
```

**Con Modo Debug (ver operaciones detalladas de API):**
```bash
python scripts/cleanup_sample_data.py --debug
```

## 🛠️ Solución de Problemas

**Soluciones Rápidas:**
- **Credenciales**: `aws sts get-caller-identity`
- **Región**: `export AWS_DEFAULT_REGION=us-east-1`
- **Dependencias**: `pip install --upgrade -r requirements.txt`
- **Modo debug**: Agregar bandera `--debug` a cualquier script

**📋 Guía Completa de Solución de Problemas**: Ver [Documentación de Solución de Problemas](docs/es/TROUBLESHOOTING.md) para soluciones detalladas a problemas comunes, problemas de conexión MQTT, errores de certificados y más.

## 📖 Documentación Avanzada

### Documentación Detallada

- **[📚 Documentación Detallada de Scripts](docs/es/DETAILED_SCRIPTS.md)** - Guías completas para cada script de aprendizaje
- **[🛠️ Guía de Solución de Problemas](docs/es/TROUBLESHOOTING.md)** - Soluciones para problemas y errores comunes
- **[📋 Ejemplos de Uso](docs/es/EXAMPLES.md)** - Flujos de trabajo completos y ejemplos interactivos


### Estructura del Proyecto

```
├── scripts/
│   ├── setup_sample_data.py          # Crea recursos IoT de ejemplo
│   ├── iot_registry_explorer.py      # Explorador interactivo de API
│   ├── certificate_manager.py        # Gestión de certificados y políticas
│   ├── mqtt_client_explorer.py       # Cliente MQTT basado en certificados
│   ├── mqtt_websocket_explorer.py    # Cliente MQTT WebSocket
│   ├── device_shadow_explorer.py     # Herramienta de aprendizaje Device Shadow
│   ├── iot_rules_explorer.py         # Herramienta de aprendizaje IoT Rules Engine
│   └── cleanup_sample_data.py        # Limpieza segura de recursos de ejemplo
├── docs/
│   ├── es/                           # Documentación en español
│   └── en/                           # Documentación en inglés
├── requirements.txt                   # Dependencias de Python
├── certificates/                      # Almacenamiento local de certificados (auto-creado)
└── README.md                         # Documentación principal del proyecto
```

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor lee nuestras [pautas de contribución](CONTRIBUTING.md) antes de enviar pull requests.

### Recursos de Aprendizaje

#### Documentación de AWS IoT Core
- **[Guía del Desarrollador de AWS IoT Core](https://docs.aws.amazon.com/iot/latest/developerguide/)** - Guía completa del desarrollador
- **[Referencia de API de AWS IoT Core](https://docs.aws.amazon.com/iot/latest/apireference/)** - Documentación de API

#### SDKs de AWS Utilizados en Este Proyecto
- **[Documentación de Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)** - Documentación completa del SDK de Python
- **[Referencia del Cliente IoT de Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iot.html)** - Métodos de API específicos de IoT
- **[SDK de Dispositivos AWS IoT para Python v2](https://aws.github.io/aws-iot-device-sdk-python-v2/)** - Documentación del cliente MQTT
- **[GitHub del SDK de Dispositivos AWS IoT](https://github.com/aws/aws-iot-device-sdk-python-v2)** - Código fuente y ejemplos

#### Protocolos y Estándares
- **[Especificación del Protocolo MQTT](https://mqtt.org/)** - Documentación oficial de MQTT
- **[Estándar de Certificados X.509](https://tools.ietf.org/html/rfc5280)** - Especificación del formato de certificados

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT-0. Ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

- **Problemas**: [GitHub Issues](https://github.com/aws-samples/sample-aws-iot-core-learning-path-basics/issues)
- **Documentación**: [AWS IoT Core Developer Guide](https://docs.aws.amazon.com/iot/latest/developerguide/)
- **Foros de AWS**: [AWS IoT Forum](https://forums.aws.amazon.com/forum.jspa?forumID=210)
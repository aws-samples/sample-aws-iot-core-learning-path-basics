#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT MQTT over WebSocket Explorer
Educational MQTT client using WebSocket connection with SigV4 authentication.
"""
import json
import os
import sys
import threading
import time
import traceback
import uuid
from datetime import datetime

import boto3
from awscrt import auth, mqtt
from awsiot import mqtt_connection_builder

# Simple translation system for learning content
MESSAGES = {
    "en": {
        "title": "📡 AWS IoT MQTT over WebSocket Explorer",
        "separator": "=" * 60,
        "description_intro": "Educational MQTT client using WebSocket connection with SigV4 authentication.",
        "debug_enabled": "🔍 DEBUG MODE ENABLED",
        "debug_features": [
            "• Enhanced API request/response logging",
            "• Full error details and tracebacks",
            "• Extended educational information",
        ],
        "tip": "💡 Tip: Use --debug or -d flag for enhanced API logging",
        "websocket_endpoint_discovery": "🌐 AWS IoT WebSocket Endpoint Discovery",
        "endpoint_type": "Endpoint Type: iot:Data-ATS (recommended)",
        "endpoint_url": "Endpoint URL",
        "port": "Port: 443 (HTTPS/WebSocket)",
        "protocol": "Protocol: MQTT over WebSocket with SigV4",
        "error_getting_endpoint": "❌ Error getting IoT endpoint:",
        "no_aws_credentials": "❌ No AWS credentials found",
        "credentials_help": "💡 Set credentials using one of these methods:",
        "credentials_methods": [
            "• AWS CLI: aws configure",
            "• Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY",
            "• IAM roles (if running on EC2)",
        ],
        "aws_credentials_sigv4": "🔐 AWS Credentials for SigV4 Authentication",
        "access_key": "Access Key",
        "region": "Region",
        "session_token": "Session Token",
        "present": "Present",
        "not_present": "Not present",
        "error_getting_credentials": "❌ Error getting AWS credentials:",
        "connection_interrupted": "CONNECTION INTERRUPTED",
        "error": "Error",
        "timestamp": "Timestamp",
        "auto_reconnect": "Auto Reconnect: AWS IoT SDK will attempt to reconnect automatically",
        "connection_resumed": "CONNECTION RESUMED",
        "return_code": "Return Code",
        "session_present": "Session Present",
        "status": "Status: Connection restored successfully",
        "resubscribing_topics": "🔄 Re-subscribing to {} topics after reconnection...",
        "resubscribed_success": "✅ Re-subscribed to {} (QoS {})",
        "resubscribe_failed": "❌ Failed to re-subscribe to {}: {}",
        "incoming_message": "🔔 INCOMING MESSAGE #{} [{}]",
        "topic": "📥 Topic",
        "qos": "🏷️  QoS",
        "qos_descriptions": {0: "At most once", 1: "At least once", 2: "Exactly once"},
        "payload_size": "📊 Payload Size",
        "transport": "🌐 Transport: WebSocket with SigV4",
        "flags": "🚩 Flags",
        "duplicate_flag": "🔄 DUPLICATE (retransmitted)",
        "retain_flag": "📌 RETAIN (stored by broker)",
        "mqtt5_properties": "🔧 MQTT5 Properties:",
        "content_type": "📄 Content-Type",
        "correlation_data": "🔗 Correlation-Data",
        "message_expiry": "⏰ Message-Expiry",
        "response_topic": "↩️  Response-Topic",
        "payload_format": "📝 Payload-Format",
        "user_properties": "🏷️  User-Properties",
        "message_payload": "💬 Message Payload:",
        "json_format": "📋 JSON Format:",
        "text_format": "📝 Text:",
        "message_encoding_error": "❌ Message encoding error:",
        "json_parsing_error": "❌ JSON parsing error in message:",
        "message_attribute_error": "❌ Message attribute error:",
        "unexpected_message_error": "❌ Unexpected error processing received message:",
        "establishing_connection": "Establishing MQTT over WebSocket Connection",
        "websocket_connection_params": "🔗 WebSocket Connection Parameters:",
        "client_id": "Client ID",
        "endpoint": "Endpoint",
        "port_443": "Port: 443",
        "protocol_mqtt311": "Protocol: MQTT 3.1.1 over WebSocket",
        "authentication": "Authentication: AWS SigV4",
        "connecting_websocket": "🔄 Connecting to AWS IoT Core via WebSocket...",
        "websocket_connection_established": "WEBSOCKET CONNECTION ESTABLISHED",
        "connection_status": "Status: Successfully connected to AWS IoT Core",
        "transport_websocket": "Transport: WebSocket over HTTPS (port 443)",
        "clean_session": "Clean Session: True",
        "keep_alive": "Keep Alive: 30 seconds",
        "tls_version": "TLS Version: 1.2",
        "websocket_connection_failed": "❌ WebSocket connection failed:",
        "not_connected": "❌ Not connected to AWS IoT Core",
        "subscribing_topic_websocket": "📥 Subscribing to Topic (WebSocket)",
        "websocket_subscription_established": "WEBSOCKET SUBSCRIPTION ESTABLISHED",
        "qos_requested": "QoS Requested",
        "qos_granted": "QoS Granted",
        "packet_id": "Packet ID",
        "wildcard_support": "Wildcard Support: AWS IoT supports + (single level) and # (multi level)",
        "websocket_subscription_failed": "❌ WebSocket subscription failed:",
        "detailed_error_info": "🔍 Detailed Error Information:",
        "error_type": "Error Type",
        "error_message": "Error Message",
        "troubleshooting_timeout": "💡 Troubleshooting: WebSocket subscription timeout",
        "timeout_causes": [
            "• WebSocket connection may be unstable",
            "• Network connectivity issues",
            "• AWS IoT endpoint may be unreachable",
        ],
        "troubleshooting_auth": "💡 Troubleshooting: Authorization failed",
        "auth_causes": [
            "• AWS credentials may be invalid or expired",
            "• IAM policy may not allow 'iot:Subscribe' action",
            "• Check IAM user/role permissions",
        ],
        "troubleshooting_invalid_topic": "💡 Troubleshooting: Invalid topic format",
        "invalid_topic_causes": [
            "• Topics cannot start with '/' or '$' (unless AWS reserved)",
            "• Use alphanumeric characters, hyphens, and forward slashes",
            "• Maximum topic length is 256 characters",
        ],
        "troubleshooting_connection": "💡 Troubleshooting: Connection issue",
        "connection_causes": [
            "• WebSocket connection may have been lost",
            "• AWS credentials may be invalid",
            "• Endpoint URL may be incorrect",
        ],
        "troubleshooting_unknown": "💡 Troubleshooting: Unknown subscription failure",
        "unknown_causes": [
            "• Run 'debug {}' command for detailed diagnostics",
            "• Check AWS IoT logs in CloudWatch if enabled",
        ],
        "publishing_message_websocket": "📤 Publishing Message (WebSocket)",
        "published_websocket": "✅ [{}] PUBLISHED via WebSocket",
        "delivery_ack_required": "🔄 Delivery: Acknowledgment required (QoS {})",
        "delivery_fire_forget": "🚀 Delivery: Fire-and-forget (QoS 0)",
        "websocket_publish_failed": "❌ WebSocket publish failed:",
        "troubleshooting_publish_timeout": "💡 Troubleshooting: WebSocket publish timeout",
        "troubleshooting_payload_large": "💡 Troubleshooting: Payload size limit exceeded",
        "payload_limit_info": ["• AWS IoT message size limit is 128 KB", "• Current payload size: {} bytes"],
        "interactive_messaging": "Interactive MQTT over WebSocket Messaging",
        "mqtt_topic_guidelines": "💡 MQTT Topic Guidelines:",
        "topic_guidelines": [
            "• Use forward slashes for hierarchy: device/sensor/temperature",
            "• Avoid leading slashes: ❌ /device/data ✅ device/data",
            "• Keep topics descriptive and organized",
            "• AWS IoT reserved topics start with $aws/",
        ],
        "enter_subscribe_topic": "📥 Enter topic to subscribe to (or 'skip'): ",
        "qos_level_prompt": "QoS level (0=At most once, 1=At least once) [0]: ",
        "invalid_qos": "❌ Please enter 0 or 1",
        "subscription_failed_retry": "❌ Subscription failed, try again",
        "run_diagnostics": "Would you like to run connection diagnostics? (y/N): ",
        "topic_cannot_be_empty": "❌ Topic cannot be empty",
        "interactive_websocket_mode": "🎮 Interactive WebSocket MQTT Messaging Mode",
        "messages_appear_immediately": "💡 Messages will appear immediately when received on subscribed topics!",
        "commands": "Commands:",
        "command_list": [
            "• 'sub <topic>' - Subscribe to topic (QoS 0)",
            "• 'sub1 <topic>' - Subscribe to topic (QoS 1)",
            "• 'unsub <topic>' - Unsubscribe from topic",
            "• 'pub <topic> <message>' - Publish message (QoS 0)",
            "• 'pub1 <topic> <message>' - Publish with QoS 1",
            "• 'json <topic> <key=value> [key=value...]' - Publish JSON",
            "• 'props <topic> <message> [prop=value...]' - Publish with MQTT5 properties",
            "• 'test' - Send test message to subscribed topics",
            "• 'status' - Show connection and subscription status",
            "• 'messages' - Show message history",
            "• 'debug [topic]' - Show connection diagnostics and troubleshooting",
            "• 'clear' - Clear screen",
            "• 'help' - Show this help",
            "• 'quit' - Exit",
        ],
        "mqtt_ws_prompt": "📡 MQTT-WS> ",
        "invalid_command": "❌ Invalid command. Type 'help' for available commands.",
        "goodbye": "👋 Goodbye!",
        "connection_diagnostics": "🔍 Connection Diagnostics",
        "connection_status_label": "Connection Status",
        "connected": "Connected",
        "disconnected": "Disconnected",
        "subscriptions_count": "Active Subscriptions: {}",
        "no_subscriptions": "No active subscriptions",
        "subscription_details": "📋 Subscription Details:",
        "granted_qos": "Granted QoS",
        "subscribed_at": "Subscribed At",
        "message_history": "📊 Message History",
        "received_messages": "Received Messages: {}",
        "sent_messages": "Sent Messages: {}",
        "no_messages": "No messages yet",
        "recent_received": "📥 Recent Received Messages:",
        "recent_sent": "📤 Recent Sent Messages:",
        "direction": "Direction",
        "size": "Size",
        "clear_screen": "🧹 Screen cleared",
        "test_message_sent": "🧪 Test message sent to {} subscribed topic(s)",
        "no_subscribed_topics": "❌ No subscribed topics for test message",
        "unsubscribing_from": "📤 Unsubscribing from: {}",
        "unsubscribed_success": "✅ Unsubscribed from: {}",
        "unsubscribe_failed": "❌ Unsubscribe failed: {}",
        "not_subscribed_to": "❌ Not subscribed to: {}",
        "json_publish_format": "📋 JSON Publish Format: json <topic> key1=value1 key2=value2 ...",
        "json_publish_example": "Example: json sensors/temp temperature=25.5 humidity=60 location=room1",
        "invalid_json_format": "❌ Invalid JSON format. Use: key=value pairs",
        "props_publish_format": "🔧 MQTT5 Properties Format: props <topic> <message> [prop=value...]",
        "props_publish_example": "Example: props alerts/fire 'Fire detected!' content-type=text/plain expiry=300",
        "available_properties": "Available properties: content-type, correlation-data, expiry, response-topic",
        "invalid_props_format": "❌ Invalid properties format. Use: prop=value pairs",
        "unknown_mqtt5_property": "⚠️  Unknown MQTT5 property: {}",
        "bytes": "bytes",
        "client_id_prompt": "Enter custom Client ID (or press Enter for auto-generated): ",
        "client_id_auto_generated": "Auto-generated Client ID",
        "client_id_custom": "Custom Client ID",
        "client_id_invalid": "❌ Invalid Client ID. Must be 1-128 characters, alphanumeric, hyphens, underscores only.",
        "client_id_guidelines": "💡 Client ID Guidelines:",
        "client_id_rules": [
            "• Must be unique per connection",
            "• 1-128 characters allowed",
            "• Use alphanumeric, hyphens (-), and underscores (_)",
            "• Avoid spaces and special characters",
            "• Example: my-device-001, sensor_temp_01",
        ],
    },
    "es": {
        "title": "📡 Explorador AWS IoT MQTT sobre WebSocket",
        "separator": "=" * 60,
        "description_intro": "Cliente MQTT educativo usando conexión WebSocket con autenticación SigV4.",
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Registro mejorado de solicitudes/respuestas de API",
            "• Detalles completos de errores y trazas",
            "• Información educativa extendida",
        ],
        "tip": "💡 Consejo: Usa la bandera --debug o -d para registro mejorado de API",
        "websocket_endpoint_discovery": "🌐 Descubrimiento de Endpoint WebSocket de AWS IoT",
        "endpoint_type": "Tipo de Endpoint: iot:Data-ATS (recomendado)",
        "endpoint_url": "URL del Endpoint",
        "port": "Puerto: 443 (HTTPS/WebSocket)",
        "protocol": "Protocolo: MQTT sobre WebSocket con SigV4",
        "error_getting_endpoint": "❌ Error obteniendo endpoint de IoT:",
        "no_aws_credentials": "❌ No se encontraron credenciales de AWS",
        "credentials_help": "💡 Configura credenciales usando uno de estos métodos:",
        "credentials_methods": [
            "• AWS CLI: aws configure",
            "• Variables de entorno: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY",
            "• Roles IAM (si se ejecuta en EC2)",
        ],
        "aws_credentials_sigv4": "🔐 Credenciales de AWS para Autenticación SigV4",
        "access_key": "Clave de Acceso",
        "region": "Región",
        "session_token": "Token de Sesión",
        "present": "Presente",
        "not_present": "No presente",
        "error_getting_credentials": "❌ Error obteniendo credenciales de AWS:",
        "connection_interrupted": "CONEXIÓN INTERRUMPIDA",
        "error": "Error",
        "timestamp": "Marca de Tiempo",
        "auto_reconnect": "Reconexión Automática: El SDK de AWS IoT intentará reconectarse automáticamente",
        "connection_resumed": "CONEXIÓN RESTABLECIDA",
        "return_code": "Código de Retorno",
        "session_present": "Sesión Presente",
        "status": "Estado: Conexión restaurada exitosamente",
        "resubscribing_topics": "🔄 Re-suscribiendo a {} temas después de la reconexión...",
        "resubscribed_success": "✅ Re-suscrito a {} (QoS {})",
        "resubscribe_failed": "❌ Falló la re-suscripción a {}: {}",
        "incoming_message": "🔔 MENSAJE ENTRANTE #{} [{}]",
        "topic": "📥 Tema",
        "qos": "🏷️  QoS",
        "qos_descriptions": {0: "A lo sumo una vez", 1: "Al menos una vez", 2: "Exactamente una vez"},
        "payload_size": "📊 Tamaño del Payload",
        "transport": "🌐 Transporte: WebSocket con SigV4",
        "flags": "🚩 Banderas",
        "duplicate_flag": "🔄 DUPLICADO (retransmitido)",
        "retain_flag": "📌 RETENER (almacenado por el broker)",
        "mqtt5_properties": "🔧 Propiedades MQTT5:",
        "content_type": "📄 Tipo-de-Contenido",
        "correlation_data": "🔗 Datos-de-Correlación",
        "message_expiry": "⏰ Expiración-de-Mensaje",
        "response_topic": "↩️  Tema-de-Respuesta",
        "payload_format": "📝 Formato-de-Payload",
        "user_properties": "🏷️  Propiedades-de-Usuario",
        "message_payload": "💬 Payload del Mensaje:",
        "json_format": "📋 Formato JSON:",
        "text_format": "📝 Texto:",
        "message_encoding_error": "❌ Error de codificación del mensaje:",
        "json_parsing_error": "❌ Error de análisis JSON en el mensaje:",
        "message_attribute_error": "❌ Error de atributo del mensaje:",
        "unexpected_message_error": "❌ Error inesperado procesando mensaje recibido:",
        "establishing_connection": "Estableciendo Conexión MQTT sobre WebSocket",
        "websocket_connection_params": "🔗 Parámetros de Conexión WebSocket:",
        "client_id": "ID del Cliente",
        "endpoint": "Endpoint",
        "port_443": "Puerto: 443",
        "protocol_mqtt311": "Protocolo: MQTT 3.1.1 sobre WebSocket",
        "authentication": "Autenticación: AWS SigV4",
        "connecting_websocket": "🔄 Conectando a AWS IoT Core vía WebSocket...",
        "websocket_connection_established": "CONEXIÓN WEBSOCKET ESTABLECIDA",
        "connection_status": "Estado: Conectado exitosamente a AWS IoT Core",
        "transport_websocket": "Transporte: WebSocket sobre HTTPS (puerto 443)",
        "clean_session": "Sesión Limpia: Verdadero",
        "keep_alive": "Mantener Vivo: 30 segundos",
        "tls_version": "Versión TLS: 1.2",
        "websocket_connection_failed": "❌ Falló la conexión WebSocket:",
        "not_connected": "❌ No conectado a AWS IoT Core",
        "subscribing_topic_websocket": "📥 Suscribiéndose al Tema (WebSocket)",
        "websocket_subscription_established": "SUSCRIPCIÓN WEBSOCKET ESTABLECIDA",
        "qos_requested": "QoS Solicitado",
        "qos_granted": "QoS Otorgado",
        "packet_id": "ID del Paquete",
        "wildcard_support": "Soporte de Comodines: AWS IoT soporta + (nivel único) y # (multi nivel)",
        "websocket_subscription_failed": "❌ Falló la suscripción WebSocket:",
        "detailed_error_info": "🔍 Información Detallada del Error:",
        "error_type": "Tipo de Error",
        "error_message": "Mensaje de Error",
        "troubleshooting_timeout": "💡 Solución de Problemas: Tiempo de espera de suscripción WebSocket",
        "timeout_causes": [
            "• La conexión WebSocket puede estar inestable",
            "• Problemas de conectividad de red",
            "• El endpoint de AWS IoT puede estar inalcanzable",
        ],
        "troubleshooting_auth": "💡 Solución de Problemas: Falló la autorización",
        "auth_causes": [
            "• Las credenciales de AWS pueden ser inválidas o expiradas",
            "• La política IAM puede no permitir la acción 'iot:Subscribe'",
            "• Verifica los permisos del usuario/rol IAM",
        ],
        "troubleshooting_invalid_topic": "💡 Solución de Problemas: Formato de tema inválido",
        "invalid_topic_causes": [
            "• Los temas no pueden empezar con '/' o '$' (a menos que sean reservados de AWS)",
            "• Usa caracteres alfanuméricos, guiones y barras diagonales",
            "• La longitud máxima del tema es 256 caracteres",
        ],
        "troubleshooting_connection": "💡 Solución de Problemas: Problema de conexión",
        "connection_causes": [
            "• La conexión WebSocket puede haberse perdido",
            "• Las credenciales de AWS pueden ser inválidas",
            "• La URL del endpoint puede ser incorrecta",
        ],
        "troubleshooting_unknown": "💡 Solución de Problemas: Fallo de suscripción desconocido",
        "unknown_causes": [
            "• Ejecuta el comando 'debug {}' para diagnósticos detallados",
            "• Verifica los logs de AWS IoT en CloudWatch si están habilitados",
        ],
        "publishing_message_websocket": "📤 Publicando Mensaje (WebSocket)",
        "published_websocket": "✅ [{}] PUBLICADO vía WebSocket",
        "delivery_ack_required": "🔄 Entrega: Confirmación requerida (QoS {})",
        "delivery_fire_forget": "🚀 Entrega: Disparar y olvidar (QoS 0)",
        "websocket_publish_failed": "❌ Falló la publicación WebSocket:",
        "troubleshooting_publish_timeout": "💡 Solución de Problemas: Tiempo de espera de publicación WebSocket",
        "troubleshooting_payload_large": "💡 Solución de Problemas: Límite de tamaño de payload excedido",
        "payload_limit_info": [
            "• El límite de tamaño de mensaje de AWS IoT es 128 KB",
            "• Tamaño actual del payload: {} bytes",
        ],
        "interactive_messaging": "Mensajería Interactiva MQTT sobre WebSocket",
        "mqtt_topic_guidelines": "💡 Guías de Temas MQTT:",
        "topic_guidelines": [
            "• Usa barras diagonales para jerarquía: device/sensor/temperature",
            "• Evita barras iniciales: ❌ /device/data ✅ device/data",
            "• Mantén los temas descriptivos y organizados",
            "• Los temas reservados de AWS IoT empiezan con $aws/",
        ],
        "enter_subscribe_topic": "📥 Ingresa el tema para suscribirse (o 'skip'): ",
        "qos_level_prompt": "Nivel QoS (0=A lo sumo una vez, 1=Al menos una vez) [0]: ",
        "invalid_qos": "❌ Por favor ingresa 0 o 1",
        "subscription_failed_retry": "❌ Falló la suscripción, intenta de nuevo",
        "run_diagnostics": "¿Te gustaría ejecutar diagnósticos de conexión? (y/N): ",
        "topic_cannot_be_empty": "❌ El tema no puede estar vacío",
        "interactive_websocket_mode": "🎮 Modo de Mensajería MQTT WebSocket Interactivo",
        "messages_appear_immediately": "💡 ¡Los mensajes aparecerán inmediatamente cuando se reciban!",
        "commands": "Comandos:",
        "command_list": [
            "• 'sub <tema>' - Suscribirse al tema (QoS 0)",
            "• 'sub1 <tema>' - Suscribirse al tema (QoS 1)",
            "• 'unsub <tema>' - Desuscribirse del tema",
            "• 'pub <tema> <mensaje>' - Publicar mensaje (QoS 0)",
            "• 'pub1 <tema> <mensaje>' - Publicar con QoS 1",
            "• 'json <tema> <clave=valor> [clave=valor...]' - Publicar JSON",
            "• 'props <tema> <mensaje> [prop=valor...]' - Publicar con propiedades MQTT5",
            "• 'test' - Enviar mensaje de prueba a temas suscritos",
            "• 'status' - Mostrar estado de conexión y suscripciones",
            "• 'messages' - Mostrar historial de mensajes",
            "• 'debug [tema]' - Mostrar diagnósticos de conexión y solución de problemas",
            "• 'clear' - Limpiar pantalla",
            "• 'help' - Mostrar esta ayuda",
            "• 'quit' - Salir",
        ],
        "mqtt_ws_prompt": "📡 MQTT-WS> ",
        "invalid_command": "❌ Comando inválido. Escribe 'help' para comandos disponibles.",
        "goodbye": "👋 ¡Adiós!",
        "connection_diagnostics": "🔍 Diagnósticos de Conexión",
        "connection_status_label": "Estado de Conexión",
        "connected": "Conectado",
        "disconnected": "Desconectado",
        "subscriptions_count": "Suscripciones Activas: {}",
        "no_subscriptions": "Sin suscripciones activas",
        "subscription_details": "📋 Detalles de Suscripción:",
        "granted_qos": "QoS Otorgado",
        "subscribed_at": "Suscrito En",
        "message_history": "📊 Historial de Mensajes",
        "received_messages": "Mensajes Recibidos: {}",
        "sent_messages": "Mensajes Enviados: {}",
        "no_messages": "Aún no hay mensajes",
        "recent_received": "📥 Mensajes Recibidos Recientes:",
        "recent_sent": "📤 Mensajes Enviados Recientes:",
        "direction": "Dirección",
        "size": "Tamaño",
        "clear_screen": "🧹 Pantalla limpiada",
        "test_message_sent": "🧪 Mensaje de prueba enviado a {} tema(s) suscrito(s)",
        "no_subscribed_topics": "❌ No hay temas suscritos para mensaje de prueba",
        "unsubscribing_from": "📤 Desuscribiéndose de: {}",
        "unsubscribed_success": "✅ Desuscrito de: {}",
        "unsubscribe_failed": "❌ Falló la desuscripción: {}",
        "not_subscribed_to": "❌ No suscrito a: {}",
        "json_publish_format": "📋 Formato de Publicación JSON: json <tema> clave1=valor1 clave2=valor2 ...",
        "json_publish_example": "Ejemplo: json sensors/temp temperature=25.5 humidity=60 location=room1",
        "invalid_json_format": "❌ Formato JSON inválido. Usa: pares clave=valor",
        "props_publish_format": "🔧 Formato de Propiedades MQTT5: props <tema> <mensaje> [prop=valor...]",
        "props_publish_example": "Ejemplo: props alerts/fire '¡Fuego detectado!' content-type=text/plain expiry=300",
        "available_properties": "Propiedades disponibles: content-type, correlation-data, expiry, response-topic",
        "invalid_props_format": "❌ Formato de propiedades inválido. Usa: pares prop=valor",
        "unknown_mqtt5_property": "⚠️  Propiedad MQTT5 desconocida: {}",
        "bytes": "bytes",
        "client_id_prompt": "Ingresa ID de Cliente personalizado (o presiona Enter para auto-generar): ",
        "client_id_auto_generated": "ID de Cliente Auto-generado",
        "client_id_custom": "ID de Cliente Personalizado",
        "client_id_invalid": "❌ ID de Cliente inválido. 1-128 caracteres, alfanuméricos, guiones y guiones bajos.",
        "client_id_guidelines": "💡 Guías de ID de Cliente:",
        "client_id_rules": [
            "• Debe ser único por conexión",
            "• Se permiten 1-128 caracteres",
            "• Usa alfanuméricos, guiones (-) y guiones bajos (_)",
            "• Evita espacios y caracteres especiales",
            "• Ejemplo: mi-dispositivo-001, sensor_temp_01",
        ],
    },
    "debug_messages": {
        "en": {
            "debug_full_error": "🔍 DEBUG: Full error response:",
            "debug_full_traceback": "🔍 DEBUG: Full traceback:",
            "debug_websocket_setup": "🔍 DEBUG: WebSocket Connection Setup",
            "debug_connection_result": "🔍 DEBUG: Connection result:",
            "debug_testing_stability": "🔍 DEBUG: Testing WebSocket connection stability...",
            "debug_connection_stable": "✅ WebSocket connection appears stable and ready for operations",
            "debug_connection_unstable": "⚠️  Connection established but may be unstable:",
            "debug_mqtt_websocket_subscribe": "🔍 DEBUG: MQTT WebSocket Subscribe Operation",
            "debug_connection_status": "Connection Status",
            "debug_connection_object": "Connection Object",
            "debug_topic_pattern": "Topic Pattern",
            "debug_requested_qos": "Requested QoS",
            "debug_converted_qos": "🔍 DEBUG: Converted QoS:",
            "debug_callback_function": "🔍 DEBUG: Callback function:",
            "debug_subscribe_sent": "🔍 DEBUG: Subscribe request sent, waiting for response...",
            "debug_subscribe_result": "🔍 DEBUG: Subscribe result received:",
            "debug_result": "Result",
            "debug_result_type": "Result type",
            "debug_websocket_publish": "🔍 DEBUG: WebSocket Publish parameters:",
            "debug_payload_length": "Payload length",
        },
        "es": {
            "debug_full_error": "🔍 DEBUG: Respuesta completa de error:",
            "debug_full_traceback": "🔍 DEBUG: Traza completa:",
            "debug_websocket_setup": "🔍 DEBUG: Configuración de Conexión WebSocket",
            "debug_connection_result": "🔍 DEBUG: Resultado de conexión:",
            "debug_testing_stability": "🔍 DEBUG: Probando estabilidad de conexión WebSocket...",
            "debug_connection_stable": "✅ La conexión WebSocket parece estable y lista para operaciones",
            "debug_connection_unstable": "⚠️  Conexión establecida pero puede estar inestable:",
            "debug_mqtt_websocket_subscribe": "🔍 DEBUG: Operación de Suscripción MQTT WebSocket",
            "debug_connection_status": "Estado de Conexión",
            "debug_connection_object": "Objeto de Conexión",
            "debug_topic_pattern": "Patrón de Tema",
            "debug_requested_qos": "QoS Solicitado",
            "debug_converted_qos": "🔍 DEBUG: QoS Convertido:",
            "debug_callback_function": "🔍 DEBUG: Función de callback:",
            "debug_subscribe_sent": "🔍 DEBUG: Solicitud de suscripción enviada, esperando respuesta...",
            "debug_subscribe_result": "🔍 DEBUG: Resultado de suscripción recibido:",
            "debug_result": "Resultado",
            "debug_result_type": "Tipo de resultado",
            "debug_websocket_publish": "🔍 DEBUG: Parámetros de publicación WebSocket:",
            "debug_payload_length": "Longitud del payload",
        },
    },
    "ja": {
        "title": "🌐 AWS IoT MQTT WebSocket エクスプローラー",
        "separator": "=" * 50,
        "aws_config": "📍 AWS設定:",
        "account_id": "アカウントID",
        "region": "リージョン",
        "description": "WebSocket接続を使用したブラウザフレンドリーなMQTT通信の学習。",
        "debug_enabled": "🔍 デバッグモード有効",
        "debug_features": ["• 詳細なWebSocket接続ログ", "• 完全なメッセージペイロード", "• 拡張認証診断"],
        "tip": "💡 ヒント: 詳細なWebSocketログには--debugフラグを使用",
        "client_initialized": "✅ AWS IoTクライアントが初期化されました",
        "invalid_credentials": "❌ 無効なAWS認証情報",
        "no_region_error": "❌ AWSリージョンが設定されていません",
        "region_setup_instructions": [
            "以下のいずれかの方法でAWSリージョンを設定してください:",
            "1. 環境変数を設定: export AWS_DEFAULT_REGION=us-east-1",
            "2. AWS CLIを設定: aws configure",
            "3. AWS認証情報ファイルでリージョンを設定",
        ],
        "aws_context_error": "⚠️ AWSコンテキストを取得できませんでした:",
        "aws_credentials_reminder": "   AWS認証情報が設定されていることを確認してください",
        "websocket_intro_title": "MQTT WebSocket - ブラウザフレンドリー通信",
        "websocket_intro_content": (
            "MQTT over WebSocketsにより、ウェブアプリケーションがAWS IoT Coreと直接通信できます。"
            "X.509証明書の代わりにAWS認証情報を使用し、ブラウザベースのIoTアプリケーションに最適です。"
        ),
        "websocket_intro_next": "WebSocket接続を確立し、ブラウザフレンドリーなメッセージングを探索します",
        "press_enter": "Enterキーを押して続行...",
        "goodbye": "👋 さようなら！",
        "getting_endpoint": "🌐 IoT WebSocketエンドポイントを取得中...",
        "endpoint_retrieved": "✅ エンドポイント: {}",
        "error_getting_endpoint": "❌ エンドポイント取得エラー: {}",
        "creating_credentials": "🔐 AWS認証情報を作成中...",
        "credentials_created": "✅ 認証情報が作成されました",
        "error_creating_credentials": "❌ 認証情報作成エラー: {}",
        "connecting_websocket": "🔌 WebSocket MQTTクライアントに接続中...",
        "websocket_connected": "✅ WebSocket MQTTに接続されました！",
        "websocket_connection_failed": "❌ WebSocket MQTT接続に失敗しました: {}",
        "websocket_disconnected": "🔌 WebSocket MQTTから切断されました",
        "operations_menu": "📋 利用可能な操作:",
        "operations": ["1. トピックを購読", "2. メッセージを公開", "3. 接続状態を表示", "4. 切断して終了"],
        "select_operation": "操作を選択 (1-4): ",
        "invalid_choice": "❌ 無効な選択です。1-4を選択してください。",
        "subscribe_learning_title": "📚 学習ポイント: WebSocket MQTT購読",
        "subscribe_learning_content": (
            "WebSocket経由のMQTT購読により、ウェブアプリケーションがリアルタイムでIoTデータを受信できます。"
            "これは、ライブダッシュボード、リアルタイム監視、インタラクティブなウェブベースのIoTアプリケーションの構築に不可欠です。"
        ),
        "subscribe_learning_next": "WebSocket接続でトピックを購読し、リアルタイムメッセージを受信します",
        "enter_topic_subscribe": "購読するトピックを入力:",
        "subscribing_to_topic": "📡 トピック '{}' を購読中...",
        "subscribed_successfully": "✅ トピック '{}' の購読に成功しました",
        "subscription_failed": "❌ 購読に失敗しました: {}",
        "publish_learning_title": "📚 学習ポイント: WebSocket MQTT公開",
        "publish_learning_content": (
            "WebSocket経由のMQTT公開により、ウェブアプリケーションからIoTデバイスにコマンドやデータを送信できます。"
            "これは、リモート制御、設定更新、ウェブベースのデバイス管理に使用されます。"
        ),
        "publish_learning_next": "WebSocket接続でメッセージを公開し、リアルタイム配信を確認します",
        "enter_topic_publish": "公開するトピックを入力:",
        "enter_message": "メッセージを入力:",
        "publishing_message": "📤 メッセージを公開中...",
        "message_published": "✅ メッセージが公開されました",
        "publish_failed": "❌ 公開に失敗しました: {}",
        "connection_status_title": "🔌 接続状態",
        "connection_status_connected": "✅ 接続済み",
        "connection_status_disconnected": "❌ 切断済み",
        "endpoint_info": "WebSocketエンドポイント: {}",
        "auth_method": "認証方法: AWS認証情報（WebSocket）",
        "active_subscriptions": "アクティブな購読:",
        "no_active_subscriptions": "アクティブな購読なし",
        "disconnecting": "🔌 切断中...",
        "disconnected_successfully": "✅ 正常に切断されました",
        "message_received_title": "📨 メッセージ受信",
        "topic_label": "トピック:",
        "message_label": "メッセージ:",
        "timestamp_label": "タイムスタンプ:",
        "debug_full_error": "🔍 デバッグ: 完全なエラーレスポンス:",
        "debug_full_traceback": "🔍 デバッグ: 完全なトレースバック:",
        "api_error": "❌ APIエラー:",
        "websocket_error": "❌ WebSocketエラー:",
        "error": "❌ エラー:",
        "learning_moments": {
            "websocket_vs_certificate": {
                "title": "📚 学習ポイント: WebSocket vs 証明書認証",
                "content": (
                    "WebSocket MQTTはAWS認証情報を使用し、ブラウザアプリケーションに適しています。"
                    "証明書ベースのMQTTはデバイス認証により適しています。"
                ),
                "next": "WebSocket接続の利点を体験します",
            },
            "browser_compatibility": {
                "title": "📚 学習ポイント: ブラウザ互換性",
                "content": (
                    "WebSocket MQTTにより、標準的なウェブブラウザがIoTデバイスと直接通信できます。"
                    "これにより、リアルタイムダッシュボード、監視アプリケーション、インタラクティブなIoT制御パネルの構築が可能になります。"
                ),
                "next": "ブラウザフレンドリーなメッセージングを探索します",
            },
            "debug_connection_details": "🔍 デバッグ: 接続詳細: {}",
            "debug_message_details": "🔍 デバッグ: メッセージ詳細: {}",
            "debug_payload_length": "ペイロード長",
        },
        "bytes": "バイト",
        "client_id_prompt": "カスタムクライアントIDを入力 (または自動生成するにはEnterを押す): ",
        "client_id_auto_generated": "自動生成されたクライアントID",
        "client_id_custom": "カスタムクライアントID",
        "client_id_invalid": "❌ 無効なクライアントIDです。1-128文字、英数字、ハイフン、アンダースコアのみ使用可能です。",
        "client_id_guidelines": "💡 クライアントIDガイドライン:",
        "client_id_rules": [
            "• 接続ごとに一意である必要があります",
            "• 1-128文字が許可されています",
            "• 英数字、ハイフン(-)、アンダースコア(_)を使用",
            "• スペースと特殊文字を避ける",
            "• 例: my-device-001, sensor_temp_01",
        ],
    },
    "zh-CN": {
        "title": "📡 AWS IoT MQTT WebSocket 探索器",
        "separator": "=" * 60,
        "description_intro": "使用 SigV4 认证的 WebSocket 连接的教育性 MQTT 客户端。",
        "debug_enabled": "🔍 调试模式已启用",
        "debug_features": [
            "• 增强的 API 请求/响应日志记录",
            "• 完整的错误详细信息和回溯",
            "• 扩展的教育信息",
        ],
        "tip": "💡 提示：使用 --debug 或 -d 标志进行增强的 API 日志记录",
        "websocket_endpoint_discovery": "🌐 AWS IoT WebSocket 端点发现",
        "endpoint_type": "端点类型：iot:Data-ATS（推荐）",
        "endpoint_url": "端点 URL",
        "port": "端口：443（HTTPS/WebSocket）",
        "protocol": "协议：使用 SigV4 的 WebSocket 上的 MQTT",
        "error_getting_endpoint": "❌ 获取 IoT 端点时出错：",
        "no_aws_credentials": "❌ 未找到 AWS 凭证",
        "credentials_help": "💡 使用以下方法之一设置凭证：",
        "credentials_methods": [
            "• AWS CLI：aws configure",
            "• 环境变量：AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY",
            "• IAM 角色（如果在 EC2 上运行）",
        ],
        "aws_credentials_sigv4": "🔐 用于 SigV4 认证的 AWS 凭证",
        "access_key": "访问密钥",
        "region": "区域",
        "session_token": "会话令牌",
        "present": "存在",
        "not_present": "不存在",
        "error_getting_credentials": "❌ 获取 AWS 凭证时出错：",
        "connection_interrupted": "连接中断",
        "error": "错误",
        "timestamp": "时间戳",
        "auto_reconnect": "自动重连：AWS IoT SDK 将自动尝试重新连接",
        "connection_resumed": "连接已恢复",
        "return_code": "返回代码",
        "session_present": "会话存在",
        "status": "状态：连接已成功恢复",
        "incoming_message": "🔔 传入消息 #{} [{}]",
        "topic": "📥 主题",
        "qos": "🏷️  QoS",
        "qos_descriptions": {0: "最多一次", 1: "至少一次", 2: "恰好一次"},
        "payload_size": "📊 负载大小",
        "transport": "🌐 传输：使用 SigV4 的 WebSocket",
        "message_payload": "💬 消息负载：",
        "json_format": "📋 JSON 格式：",
        "text_format": "📝 文本：",
        "establishing_connection": "建立 WebSocket 上的 MQTT 连接",
        "websocket_connection_params": "🔗 WebSocket 连接参数：",
        "client_id": "客户端 ID",
        "endpoint": "端点",
        "port_443": "端口：443",
        "protocol_mqtt311": "协议：WebSocket 上的 MQTT 3.1.1",
        "authentication": "认证：AWS SigV4",
        "connecting_websocket": "🔄 通过 WebSocket 连接到 AWS IoT Core...",
        "websocket_connection_established": "WEBSOCKET 连接已建立",
        "connection_status": "状态：已成功连接到 AWS IoT Core",
        "websocket_connection_failed": "❌ WebSocket 连接失败：",
        "not_connected": "❌ 未连接到 AWS IoT Core",
        "subscribing_topic_websocket": "📥 订阅主题（WebSocket）",
        "websocket_subscription_established": "WEBSOCKET 订阅已建立",
        "websocket_subscription_failed": "❌ WebSocket 订阅失败：",
        "publishing_message_websocket": "📤 发布消息（WebSocket）",
        "published_websocket": "✅ [{}] 通过 WebSocket 发布",
        "websocket_publish_failed": "❌ WebSocket 发布失败：",
        "interactive_messaging": "WebSocket 上的交互式 MQTT 消息传递",
        "mqtt_topic_guidelines": "💡 MQTT 主题指南：",
        "topic_guidelines": [
            "• 使用斜杠表示层次结构：device/sensor/temperature",
            "• 避免前导斜杠：❌ /device/data ✅ device/data",
            "• 保持主题描述性和有组织",
            "• AWS IoT 保留主题以 $aws/ 开头",
        ],
        "enter_subscribe_topic": "📥 输入要订阅的主题（或 'skip'）：",
        "qos_level_prompt": "QoS 级别（0=最多一次，1=至少一次）[0]：",
        "invalid_qos": "❌ 请输入 0 或 1",
        "subscription_failed_retry": "❌ 订阅失败，请重试",
        "run_diagnostics": "您想运行连接诊断吗？(y/N)：",
        "topic_cannot_be_empty": "❌ 主题不能为空",
        "interactive_websocket_mode": "🎮 交互式 WebSocket MQTT 消息传递模式",
        "messages_appear_immediately": "💡 在订阅的主题上收到消息时会立即显示！",
        "commands": "命令：",
        "command_list": [
            "• 'sub <主题>' - 订阅主题（QoS 0）",
            "• 'sub1 <主题>' - 订阅主题（QoS 1）",
            "• 'unsub <主题>' - 取消订阅主题",
            "• 'pub <主题> <消息>' - 发布消息（QoS 0）",
            "• 'pub1 <主题> <消息>' - 使用 QoS 1 发布",
            "• 'json <主题> <键=值> [键=值...]' - 发布 JSON",
            "• 'test' - 向订阅的主题发送测试消息",
            "• 'status' - 显示连接和订阅状态",
            "• 'messages' - 显示消息历史",
            "• 'debug [主题]' - 显示连接诊断",
            "• 'clear' - 清屏",
            "• 'help' - 显示此帮助",
            "• 'quit' - 退出",
        ],
        "mqtt_ws_prompt": "📡 MQTT-WS> ",
        "invalid_command": "❌ 无效命令。输入 'help' 查看可用命令。",
        "goodbye": "👋 再见！",
        "connection_diagnostics": "🔍 连接诊断",
        "connection_status_label": "连接状态",
        "connected": "已连接",
        "disconnected": "已断开",
        "subscriptions_count": "活动订阅：{}",
        "no_subscriptions": "无活动订阅",
        "message_history": "📊 消息历史",
        "received_messages": "接收的消息：{}",
        "sent_messages": "发送的消息：{}",
        "no_messages": "还没有消息",
        "recent_received": "📥 最近接收的消息：",
        "recent_sent": "📤 最近发送的消息：",
        "size": "大小",
        "clear_screen": "🧹 屏幕已清除",
        "test_message_sent": "🧪 测试消息已发送到 {} 个订阅主题",
        "no_subscribed_topics": "❌ 没有订阅的主题用于测试消息",
        "unsubscribing_from": "📤 正在取消订阅：{}",
        "unsubscribed_success": "✅ 已取消订阅：{}",
        "unsubscribe_failed": "❌ 取消订阅失败：{}",
        "not_subscribed_to": "❌ 未订阅：{}",
        "bytes": "字节",
        "client_id_prompt": "输入自定义客户端 ID（或按 Enter 自动生成）：",
        "client_id_auto_generated": "自动生成的客户端 ID",
        "client_id_custom": "自定义客户端 ID",
        "client_id_invalid": "❌ 无效的客户端 ID。必须是 1-128 个字符，仅限字母数字、连字符和下划线。",
        "client_id_guidelines": "💡 客户端 ID 指南：",
        "client_id_rules": [
            "• 每个连接必须唯一",
            "• 允许 1-128 个字符",
            "• 使用字母数字、连字符 (-) 和下划线 (_)",
            "• 避免空格和特殊字符",
            "• 示例：my-device-001, sensor_temp_01",
        ],
    },
    "pt-BR": {
        "title": "📡 Explorador AWS IoT MQTT sobre WebSocket",
        "separator": "=" * 60,
        "description_intro": "Cliente MQTT educativo usando conexão WebSocket com autenticação SigV4.",
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Log aprimorado de solicitações/respostas de API",
            "• Detalhes completos de erros e rastreamentos",
            "• Informações educativas estendidas",
        ],
        "tip": "💡 Dica: Use a flag --debug ou -d para log aprimorado de API",
        "websocket_endpoint_discovery": "🌐 Descoberta de Endpoint WebSocket AWS IoT",
        "endpoint_type": "Tipo de Endpoint: iot:Data-ATS (recomendado)",
        "endpoint_url": "URL do Endpoint",
        "port": "Porta: 443 (HTTPS/WebSocket)",
        "protocol": "Protocolo: MQTT sobre WebSocket com SigV4",
        "error_getting_endpoint": "❌ Erro obtendo endpoint IoT:",
        "no_aws_credentials": "❌ Nenhuma credencial AWS encontrada",
        "credentials_help": "💡 Configure credenciais usando um destes métodos:",
        "credentials_methods": [
            "• AWS CLI: aws configure",
            "• Variáveis de ambiente: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY",
            "• Funções IAM (se executando no EC2)",
        ],
        "aws_credentials_sigv4": "🔐 Credenciais AWS para Autenticação SigV4",
        "access_key": "Chave de Acesso",
        "region": "Região",
        "session_token": "Token de Sessão",
        "present": "Presente",
        "not_present": "Não presente",
        "error_getting_credentials": "❌ Erro obtendo credenciais AWS:",
        "connection_interrupted": "CONEXÃO INTERROMPIDA",
        "error": "Erro",
        "timestamp": "Timestamp",
        "auto_reconnect": "Reconexão Automática: O SDK AWS IoT tentará reconectar automaticamente",
        "connection_resumed": "CONEXÃO RETOMADA",
        "return_code": "Código de Retorno",
        "session_present": "Sessão Presente",
        "status": "Status: Conexão restaurada com sucesso",
        "incoming_message": "🔔 MENSAGEM RECEBIDA #{} [{}]",
        "topic": "📥 Tópico",
        "qos": "🏷️  QoS",
        "qos_descriptions": {0: "No máximo uma vez", 1: "Pelo menos uma vez", 2: "Exatamente uma vez"},
        "payload_size": "📋 Tamanho do Payload",
        "transport": "🌐 Transporte: WebSocket com SigV4",
        "message_payload": "💬 Payload da Mensagem:",
        "json_format": "📋 Formato JSON:",
        "text_format": "📝 Texto:",
        "establishing_connection": "Estabelecendo Conexão MQTT sobre WebSocket",
        "websocket_connection_params": "🔗 Parâmetros de Conexão WebSocket:",
        "client_id": "ID do Cliente",
        "endpoint": "Endpoint",
        "port_443": "Porta: 443",
        "protocol_mqtt311": "Protocolo: MQTT 3.1.1 sobre WebSocket",
        "authentication": "Autenticação: AWS SigV4",
        "connecting_websocket": "🔄 Conectando ao AWS IoT Core via WebSocket...",
        "websocket_connection_established": "CONEXÃO WEBSOCKET ESTABELECIDA",
        "connection_status": "Status: Conectado com sucesso ao AWS IoT Core",
        "websocket_connection_failed": "❌ Conexão WebSocket falhou:",
        "not_connected": "❌ Não conectado ao AWS IoT Core",
        "subscribing_topic_websocket": "📥 Inscrevendo-se no Tópico (WebSocket)",
        "websocket_subscription_established": "INSCRIÇÃO WEBSOCKET ESTABELECIDA",
        "websocket_subscription_failed": "❌ Inscrição WebSocket falhou:",
        "publishing_message_websocket": "📤 Publicando Mensagem (WebSocket)",
        "published_websocket": "✅ [{}] PUBLICADO via WebSocket",
        "websocket_publish_failed": "❌ Publicação WebSocket falhou:",
        "interactive_messaging": "Mensagens Interativas MQTT sobre WebSocket",
        "mqtt_topic_guidelines": "💡 Diretrizes de Tópicos MQTT:",
        "topic_guidelines": [
            "• Use barras para hierarquia: device/sensor/temperature",
            "• Evite barras iniciais: ❌ /device/data ✅ device/data",
            "• Mantenha tópicos descritivos e organizados",
            "• Tópicos reservados AWS IoT começam com $aws/",
        ],
        "enter_subscribe_topic": "📥 Digite o tópico para se inscrever (ou 'skip'): ",
        "qos_level_prompt": "Nível QoS (0=No máximo uma vez, 1=Pelo menos uma vez) [0]: ",
        "invalid_qos": "❌ Por favor digite 0 ou 1",
        "subscription_failed_retry": "❌ Inscrição falhou, tente novamente",
        "run_diagnostics": "Gostaria de executar diagnósticos de conexão? (s/N): ",
        "topic_cannot_be_empty": "❌ Tópico não pode estar vazio",
        "interactive_websocket_mode": "🎮 Modo de Mensagens MQTT WebSocket Interativo",
        "messages_appear_immediately": "💡 Mensagens aparecerão imediatamente quando recebidas em tópicos inscritos!",
        "commands": "Comandos:",
        "command_list": [
            "• 'sub <tópico>' - Inscrever-se no tópico (QoS 0)",
            "• 'sub1 <tópico>' - Inscrever-se no tópico (QoS 1)",
            "• 'unsub <tópico>' - Cancelar inscrição do tópico",
            "• 'pub <tópico> <mensagem>' - Publicar mensagem (QoS 0)",
            "• 'pub1 <tópico> <mensagem>' - Publicar com QoS 1",
            "• 'json <tópico> <chave=valor> [chave=valor...]' - Publicar JSON",
            "• 'test' - Enviar mensagem de teste para tópicos inscritos",
            "• 'status' - Mostrar status de conexão e inscrições",
            "• 'messages' - Mostrar histórico de mensagens",
            "• 'debug [tópico]' - Mostrar diagnósticos de conexão",
            "• 'clear' - Limpar tela",
            "• 'help' - Mostrar esta ajuda",
            "• 'quit' - Sair",
        ],
        "mqtt_ws_prompt": "📡 MQTT-WS> ",
        "invalid_command": "❌ Comando inválido. Digite 'help' para comandos disponíveis.",
        "goodbye": "👋 Tchau!",
        "connection_diagnostics": "🔍 Diagnósticos de Conexão",
        "connection_status_label": "Status da Conexão",
        "connected": "Conectado",
        "disconnected": "Desconectado",
        "subscriptions_count": "Inscrições Ativas: {}",
        "no_subscriptions": "Nenhuma inscrição ativa",
        "message_history": "📋 Histórico de Mensagens",
        "received_messages": "Mensagens Recebidas: {}",
        "sent_messages": "Mensagens Enviadas: {}",
        "no_messages": "Nenhuma mensagem ainda",
        "recent_received": "📥 Mensagens Recebidas Recentes:",
        "recent_sent": "📤 Mensagens Enviadas Recentes:",
        "size": "Tamanho",
        "clear_screen": "🧹 Tela limpa",
        "test_message_sent": "🧪 Mensagem de teste enviada para {} tópico(s) inscrito(s)",
        "no_subscribed_topics": "❌ Nenhum tópico inscrito para mensagem de teste",
        "unsubscribing_from": "📤 Cancelando inscrição de: {}",
        "unsubscribed_success": "✅ Inscrição cancelada de: {}",
        "unsubscribe_failed": "❌ Cancelamento de inscrição falhou: {}",
        "not_subscribed_to": "❌ Não inscrito em: {}",
        "bytes": "bytes",
        "client_id_prompt": "Digite ID do Cliente personalizado (ou pressione Enter para auto-gerar): ",
        "client_id_auto_generated": "ID do Cliente Auto-gerado",
        "client_id_custom": "ID do Cliente Personalizado",
        "client_id_invalid": "❌ ID do Cliente inválido. 1-128 caracteres, alfanuméricos, hífens e sublinhados.",
        "client_id_guidelines": "💡 Diretrizes do ID do Cliente:",
        "client_id_rules": [
            "• Deve ser único por conexão",
            "• 1-128 caracteres permitidos",
            "• Use alfanuméricos, hífens (-) e sublinhados (_)",
            "• Evite espaços e caracteres especiais",
            "• Exemplo: meu-dispositivo-001, sensor_temp_01",
        ],
    },
    "ko": {
        "title": "📡 AWS IoT MQTT WebSocket 탐색기",
        "separator": "=" * 60,
        "description_intro": "SigV4 인증을 사용한 WebSocket 연결을 통한 교육용 MQTT 클라이언트.",
        "debug_enabled": "🔍 디버그 모드 활성화됨",
        "debug_features": [
            "• 향상된 API 요청/응답 로깅",
            "• 완전한 오류 세부사항 및 추적",
            "• 확장된 교육 정보",
        ],
        "tip": "💡 팁: 향상된 API 로깅을 위해 --debug 또는 -d 플래그를 사용하세요",
        "websocket_endpoint_discovery": "🌐 AWS IoT WebSocket 엔드포인트 검색",
        "endpoint_type": "엔드포인트 유형: iot:Data-ATS (권장)",
        "endpoint_url": "엔드포인트 URL",
        "port": "포트: 443 (HTTPS/WebSocket)",
        "protocol": "프로토콜: SigV4를 사용한 WebSocket 상의 MQTT",
        "error_getting_endpoint": "❌ IoT 엔드포인트 가져오기 오류:",
        "no_aws_credentials": "❌ AWS 자격 증명을 찾을 수 없습니다",
        "credentials_help": "💡 다음 방법 중 하나를 사용하여 자격 증명을 설정하세요:",
        "credentials_methods": [
            "• AWS CLI: aws configure",
            "• 환경 변수: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY",
            "• IAM 역할 (EC2에서 실행하는 경우)",
        ],
        "aws_credentials_sigv4": "🔐 SigV4 인증을 위한 AWS 자격 증명",
        "access_key": "액세스 키",
        "region": "리전",
        "session_token": "세션 토큰",
        "present": "존재함",
        "not_present": "존재하지 않음",
        "error_getting_credentials": "❌ AWS 자격 증명 가져오기 오류:",
        "connection_interrupted": "연결 중단됨",
        "error": "오류",
        "timestamp": "타임스탬프",
        "auto_reconnect": "자동 재연결: AWS IoT SDK가 자동으로 재연결을 시도합니다",
        "connection_resumed": "연결 재개됨",
        "return_code": "반환 코드",
        "session_present": "세션 존재",
        "status": "상태: 연결이 성공적으로 복원되었습니다",
        "incoming_message": "🔔 수신 메시지 #{} [{}]",
        "topic": "📥 토픽",
        "qos": "🏷️  QoS",
        "qos_descriptions": {0: "최대 한 번", 1: "최소 한 번", 2: "정확히 한 번"},
        "payload_size": "📊 페이로드 크기",
        "transport": "🌐 전송: SigV4를 사용한 WebSocket",
        "message_payload": "💬 메시지 페이로드:",
        "json_format": "📋 JSON 형식:",
        "text_format": "📝 텍스트:",
        "establishing_connection": "WebSocket 상의 MQTT 연결 설정",
        "websocket_connection_params": "🔗 WebSocket 연결 매개변수:",
        "client_id": "클라이언트 ID",
        "endpoint": "엔드포인트",
        "port_443": "포트: 443",
        "protocol_mqtt311": "프로토콜: WebSocket 상의 MQTT 3.1.1",
        "authentication": "인증: AWS SigV4",
        "connecting_websocket": "🔄 WebSocket을 통해 AWS IoT Core에 연결 중...",
        "websocket_connection_established": "WEBSOCKET 연결 설정됨",
        "connection_status": "상태: AWS IoT Core에 성공적으로 연결됨",
        "websocket_connection_failed": "❌ WebSocket 연결 실패:",
        "not_connected": "❌ AWS IoT Core에 연결되지 않음",
        "subscribing_topic_websocket": "📥 토픽 구독 (WebSocket)",
        "websocket_subscription_established": "WEBSOCKET 구독 설정됨",
        "websocket_subscription_failed": "❌ WebSocket 구독 실패:",
        "publishing_message_websocket": "📤 메시지 게시 (WebSocket)",
        "published_websocket": "✅ [{}] WebSocket을 통해 게시됨",
        "websocket_publish_failed": "❌ WebSocket 게시 실패:",
        "interactive_messaging": "WebSocket 상의 대화형 MQTT 메시징",
        "mqtt_topic_guidelines": "💡 MQTT 토픽 가이드라인:",
        "topic_guidelines": [
            "• 계층 구조에 슬래시 사용: device/sensor/temperature",
            "• 앞의 슬래시 피하기: ❌ /device/data ✅ device/data",
            "• 토픽을 설명적이고 체계적으로 유지",
            "• AWS IoT 예약 토픽은 $aws/로 시작",
        ],
        "enter_subscribe_topic": "📥 구독할 토픽 입력 (또는 'skip'): ",
        "qos_level_prompt": "QoS 레벨 (0=최대 한 번, 1=최소 한 번) [0]: ",
        "invalid_qos": "❌ 0 또는 1을 입력하세요",
        "subscription_failed_retry": "❌ 구독 실패, 다시 시도하세요",
        "run_diagnostics": "연결 진단을 실행하시겠습니까? (y/N): ",
        "topic_cannot_be_empty": "❌ 토픽은 비어있을 수 없습니다",
        "interactive_websocket_mode": "🎮 대화형 WebSocket MQTT 메시징 모드",
        "messages_appear_immediately": "💡 구독된 토픽에서 메시지를 받으면 즉시 나타납니다!",
        "commands": "명령어:",
        "command_list": [
            "• 'sub <토픽>' - 토픽 구독 (QoS 0)",
            "• 'sub1 <토픽>' - 토픽 구독 (QoS 1)",
            "• 'unsub <토픽>' - 토픽 구독 해제",
            "• 'pub <토픽> <메시지>' - 메시지 게시 (QoS 0)",
            "• 'pub1 <토픽> <메시지>' - QoS 1로 게시",
            "• 'json <토픽> <키=값> [키=값...]' - JSON 게시",
            "• 'test' - 구독된 토픽에 테스트 메시지 전송",
            "• 'status' - 연결 및 구독 상태 표시",
            "• 'messages' - 메시지 기록 표시",
            "• 'debug [토픽]' - 연결 진단 표시",
            "• 'clear' - 화면 지우기",
            "• 'help' - 이 도움말 표시",
            "• 'quit' - 종료",
        ],
        "mqtt_ws_prompt": "📡 MQTT-WS> ",
        "invalid_command": "❌ 잘못된 명령어입니다. 사용 가능한 명령어를 보려면 'help'를 입력하세요.",
        "goodbye": "👋 안녕히 가세요!",
        "connection_diagnostics": "🔍 연결 진단",
        "connection_status_label": "연결 상태",
        "connected": "연결됨",
        "disconnected": "연결 해제됨",
        "subscriptions_count": "활성 구독: {}",
        "no_subscriptions": "활성 구독 없음",
        "message_history": "📊 메시지 기록",
        "received_messages": "수신된 메시지: {}",
        "sent_messages": "전송된 메시지: {}",
        "no_messages": "아직 메시지 없음",
        "recent_received": "📥 최근 수신된 메시지:",
        "recent_sent": "📤 최근 전송된 메시지:",
        "size": "크기",
        "clear_screen": "🧹 화면이 지워졌습니다",
        "test_message_sent": "🧪 {}개의 구독된 토픽에 테스트 메시지가 전송되었습니다",
        "no_subscribed_topics": "❌ 테스트 메시지를 위한 구독된 토픽이 없습니다",
        "unsubscribing_from": "📤 구독 해제 중: {}",
        "unsubscribed_success": "✅ 구독 해제됨: {}",
        "unsubscribe_failed": "❌ 구독 해제 실패: {}",
        "not_subscribed_to": "❌ 구독되지 않음: {}",
        "bytes": "바이트",
        "client_id_prompt": "사용자 정의 클라이언트 ID 입력 (또는 자동 생성하려면 Enter 누름): ",
        "client_id_auto_generated": "자동 생성된 클라이언트 ID",
        "client_id_custom": "사용자 정의 클라이언트 ID",
        "client_id_invalid": "❌ 잘못된 클라이언트 ID입니다. 1-128자, 영숫자, 하이픈, 언더스코어만 사용 가능합니다.",
        "client_id_guidelines": "💡 클라이언트 ID 가이드라인:",
        "client_id_rules": [
            "• 연결마다 고유해야 합니다",
            "• 1-128자가 허용됩니다",
            "• 영숫자, 하이픈(-), 언더스코어(_) 사용",
            "• 공백과 특수 문자 피하기",
            "• 예시: my-device-001, sensor_temp_01",
        ],
    },
}

# Global variable for user's language preference
USER_LANG = "en"

# Global debug mode flag
DEBUG_MODE = False


def get_language():
    """Get user's preferred language"""
    # Check environment variable first
    env_lang = os.getenv("AWS_IOT_LANG", "").lower()
    if env_lang in ["es", "spanish", "español"]:
        return "es"
    elif env_lang in ["en", "english"]:
        return "en"
    elif env_lang in ["ja", "japanese", "日本語", "jp"]:
        return "ja"
    elif env_lang in ["zh-cn", "chinese", "中文", "zh"]:
        return "zh-CN"
    elif env_lang in ["pt-br", "portuguese", "português", "pt"]:
        return "pt-BR"
    elif env_lang in ["ko", "korean", "한국어", "kr"]:
        return "ko"

    # If no environment variable, ask user
    print("🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma")
    print("=" * 80)
    print("1. English")
    print("2. Español (Spanish)")
    print("3. 日本語 (Japanese)")
    print("4. 中文 (Chinese)")
    print("5. Português (Portuguese)")
    print("6. 한국어 (Korean)")

    while True:
        try:
            choice = input(
                "Select language / Seleccionar idioma / 言語を選択 / 选择语言 / Selecionar idioma / 언어 선택 (1-6): "
            ).strip()
            if choice == "1":
                return "en"
            elif choice == "2":
                return "es"
            elif choice == "3":
                return "ja"
            elif choice == "4":
                return "zh-CN"
            elif choice == "5":
                return "pt-BR"
            elif choice == "6":
                return "ko"
            else:
                print("Invalid choice. Please select 1-6.")
                print("Selección inválida. Por favor selecciona 1-5.")
                print("無効な選択です。1-5を選択してください。")
                print("无效选择。请选择 1-5。")
                print("Escolha inválida. Por favor selecione 1-5.")
        except KeyboardInterrupt:
            print("Goodbye! / ¡Adiós! / さようなら！ / 再见！ / Tchau!")
            sys.exit(0)


def get_message(key, lang="en", *args):
    """Get localized message"""
    # Check debug messages first
    debug_msg = MESSAGES.get("debug_messages", {}).get(lang, {}).get(key)
    if debug_msg:
        return debug_msg

    # Get regular message
    message = MESSAGES.get(lang, MESSAGES["en"]).get(key, key)

    # Handle formatting with arguments
    if args:
        try:
            return message.format(*args)
        except (IndexError, KeyError):
            return message

    return message


class MQTTWebSocketExplorer:
    def __init__(self):
        self.connection = None
        self.connected = False
        self.received_messages = []
        self.sent_messages = []
        self.subscriptions = {}
        self.message_lock = threading.Lock()
        self.message_count = 0
        self.debug_mode = False

    def print_header(self, title):
        """Print formatted header"""
        print(f"\n📡 {title}")
        print(get_message("separator", USER_LANG))

    def print_step(self, step, description):
        """Print step with formatting"""
        print(f"\n🔧 Step {step}: {description}")
        print("-" * 50)

    def print_mqtt_details(self, message_type, details):
        """Print detailed MQTT protocol information"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n📊 MQTT {message_type} Details [{timestamp}]")
        print("-" * 40)

        for key, value in details.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"      {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")

    def validate_client_id(self, client_id):
        """Validate MQTT Client ID according to AWS IoT requirements"""
        if not client_id:
            return False

        # Length check: 1-128 characters
        if len(client_id) < 1 or len(client_id) > 128:
            return False

        # Character check: alphanumeric, hyphens, and underscores only
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", client_id):
            return False

        return True

    def get_client_id(self):
        """Get client ID from user input or generate automatically"""
        print(f"\n{get_message('client_id_guidelines', USER_LANG)}")
        for rule in get_message("client_id_rules", USER_LANG):
            print(f"   {rule}")

        while True:
            try:
                custom_id = input(f"\n{get_message('client_id_prompt', USER_LANG)}").strip()

                if not custom_id:
                    # Auto-generate client ID
                    client_id = f"websocket-client-{uuid.uuid4().hex[:8]}"
                    print(f"   {get_message('client_id_auto_generated', USER_LANG)}: {client_id}")
                    return client_id
                else:
                    # Validate custom client ID
                    if self.validate_client_id(custom_id):
                        print(f"   {get_message('client_id_custom', USER_LANG)}: {custom_id}")
                        return custom_id
                    else:
                        print(f"   {get_message('client_id_invalid', USER_LANG)}")
                        continue

            except KeyboardInterrupt:
                print(f"\n{get_message('operation_cancelled', USER_LANG)}")
                return None

    def get_iot_endpoint(self, debug=False):
        """Get AWS IoT endpoint for WebSocket connections"""
        try:
            iot = boto3.client("iot")

            if debug:
                print("🔍 DEBUG: Calling describe_endpoint API for WebSocket")
                print("📥 Input Parameters: {'endpointType': 'iot:Data-ATS'}")

            response = iot.describe_endpoint(endpointType="iot:Data-ATS")
            endpoint = response["endpointAddress"]

            if debug:
                print(f"📤 API Response: {json.dumps(response, indent=2, default=str)}")

            print(get_message("websocket_endpoint_discovery", USER_LANG))
            print(f"   {get_message('endpoint_type', USER_LANG)}")
            print(f"   {get_message('endpoint_url', USER_LANG)}: {endpoint}")
            print(f"   {get_message('port', USER_LANG)}")
            print(f"   {get_message('protocol', USER_LANG)}")

            return endpoint
        except Exception as e:
            print(f"{get_message('error_getting_endpoint', USER_LANG)} {str(e)}")
            if debug:
                print(get_message("debug_full_traceback", USER_LANG))
                traceback.print_exc()
            return None

    def get_aws_credentials(self, debug=False):
        """Get AWS credentials for SigV4 authentication"""
        try:
            # Try to get credentials from boto3 session
            session = boto3.Session()
            credentials = session.get_credentials()

            if not credentials:
                print(get_message("no_aws_credentials", USER_LANG))
                print(get_message("credentials_help", USER_LANG))
                for method in get_message("credentials_methods", USER_LANG):
                    print(f"   {method}")
                return None, None, None, None

            access_key = credentials.access_key
            secret_key = credentials.secret_key
            session_token = credentials.token
            region = session.region_name or os.getenv("AWS_DEFAULT_REGION", "us-east-1")

            if debug:
                print("🔍 DEBUG: AWS Credentials Retrieved")
                print(f"   Access Key: {access_key[:10]}..." if access_key else "   Access Key: None")
                print(f"   Secret Key: {'*' * 20}" if secret_key else "   Secret Key: None")
                print(f"   Session Token: {'Present' if session_token else 'None'}")
                print(f"   Region: {region}")

            print(get_message("aws_credentials_sigv4", USER_LANG))
            print(
                f"   {get_message('access_key', USER_LANG)}: {access_key[:10]}..."
                if access_key
                else f"   {get_message('access_key', USER_LANG)}: None"
            )
            print(f"   {get_message('region', USER_LANG)}: {region}")
            print(
                f"   {get_message('session_token', USER_LANG)}: "
                f"{get_message('present', USER_LANG) if session_token else get_message('not_present', USER_LANG)}"
            )

            return access_key, secret_key, session_token, region

        except Exception as e:
            print(f"{get_message('error_getting_credentials', USER_LANG)} {str(e)}")
            if debug:
                print(get_message("debug_full_traceback", USER_LANG))
                traceback.print_exc()
            return None, None, None, None

    def on_connection_interrupted(self, connection, error, **kwargs):
        """Callback for connection interruption"""
        self.print_mqtt_details(
            get_message("connection_interrupted", USER_LANG),
            {
                get_message("error", USER_LANG): str(error),
                get_message("timestamp", USER_LANG): datetime.now().isoformat(),
                get_message("auto_reconnect", USER_LANG): get_message("auto_reconnect", USER_LANG),
            },
        )
        self.connected = False

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """Callback for connection resumption"""
        self.print_mqtt_details(
            get_message("connection_resumed", USER_LANG),
            {
                get_message("return_code", USER_LANG): return_code,
                get_message("session_present", USER_LANG): session_present,
                get_message("timestamp", USER_LANG): datetime.now().isoformat(),
                get_message("status", USER_LANG): get_message("status", USER_LANG),
            },
        )
        self.connected = True

        # Re-subscribe to all topics if session not present
        if not session_present and self.subscriptions:
            print(f"\n{get_message('resubscribing_topics', USER_LANG, len(self.subscriptions))}")
            topics_to_resubscribe = list(self.subscriptions.items())
            for topic, subscription_info in topics_to_resubscribe:
                try:
                    qos = subscription_info.get("qos", 0) if isinstance(subscription_info, dict) else subscription_info
                    subscribe_future, _ = self.connection.subscribe(
                        topic=topic, qos=mqtt.QoS(qos), callback=self.on_message_received
                    )
                    subscribe_future.result()
                    print(f"   {get_message('resubscribed_success', USER_LANG, topic, qos)}")
                except Exception as e:
                    print(f"   {get_message('resubscribe_failed', USER_LANG, topic, str(e))}")
                    # Remove failed subscription from tracking
                    self.subscriptions.pop(topic, None)

    def on_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """Callback for received messages with comprehensive MQTT metadata"""
        try:
            # Try to parse as JSON, fallback to string
            try:
                message_data = json.loads(payload.decode("utf-8"))
                payload_display = json.dumps(message_data, indent=2)
                is_json = True
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload_display = payload.decode("utf-8")
                is_json = False

            # Extract additional MQTT properties from kwargs
            user_properties = kwargs.get("user_properties", [])
            content_type = kwargs.get("content_type", None)
            correlation_data = kwargs.get("correlation_data", None)
            message_expiry_interval = kwargs.get("message_expiry_interval", None)
            response_topic = kwargs.get("response_topic", None)
            payload_format_indicator = kwargs.get("payload_format_indicator", None)

            message_info = {
                "Direction": "RECEIVED",
                "Topic": topic,
                "QoS": qos,
                "Duplicate": dup,
                "Retain": retain,
                "Payload Size": f"{len(payload)} bytes",
                "Timestamp": datetime.now().isoformat(),
                "Payload": payload_display,
                "User Properties": user_properties,
                "Content Type": content_type,
                "Correlation Data": correlation_data,
                "Message Expiry": message_expiry_interval,
                "Response Topic": response_topic,
                "Payload Format": payload_format_indicator,
            }

            with self.message_lock:
                self.received_messages.append(message_info)
                self.message_count += 1

            # Immediate visual notification with enhanced formatting
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print("\n" + "=" * 70)
            print(f"{get_message('incoming_message', USER_LANG, self.message_count, timestamp)}")
            print("=" * 70)

            # Core MQTT Properties
            print(f"{get_message('topic', USER_LANG)}: {topic}")
            qos_desc = get_message("qos_descriptions", USER_LANG).get(qos, f"QoS {qos}")
            print(f"{get_message('qos', USER_LANG)}: {qos} ({qos_desc})")
            print(f"{get_message('payload_size', USER_LANG)}: {len(payload)} {get_message('bytes', USER_LANG)}")
            print(get_message("transport", USER_LANG))

            # MQTT Flags
            flags = []
            if dup:
                flags.append(get_message("duplicate_flag", USER_LANG))
            if retain:
                flags.append(get_message("retain_flag", USER_LANG))
            if flags:
                print(f"{get_message('flags', USER_LANG)}: {', '.join(flags)}")

            # MQTT5 Properties (if available)
            mqtt5_props = []
            if content_type:
                mqtt5_props.append(f"{get_message('content_type', USER_LANG)}: {content_type}")
            if correlation_data:
                mqtt5_props.append(f"{get_message('correlation_data', USER_LANG)}: {correlation_data}")
            if message_expiry_interval:
                mqtt5_props.append(f"{get_message('message_expiry', USER_LANG)}: {message_expiry_interval}s")
            if response_topic:
                mqtt5_props.append(f"{get_message('response_topic', USER_LANG)}: {response_topic}")
            if payload_format_indicator is not None:
                format_desc = "UTF-8 String" if payload_format_indicator == 1 else "Bytes"
                mqtt5_props.append(f"{get_message('payload_format', USER_LANG)}: {format_desc}")
            if user_properties:
                mqtt5_props.append(f"{get_message('user_properties', USER_LANG)}: {len(user_properties)} properties")
                for prop in user_properties:
                    mqtt5_props.append(f"   • {prop[0]}: {prop[1]}")

            if mqtt5_props:
                print(get_message("mqtt5_properties", USER_LANG))
                for prop in mqtt5_props:
                    print(f"   {prop}")

            # Payload Display
            print(get_message("message_payload", USER_LANG))
            if is_json:
                print(f"   {get_message('json_format', USER_LANG)}")
                for line in payload_display.split("\n"):
                    print(f"   {line}")
            else:
                print(f"   {get_message('text_format', USER_LANG)} {payload_display}")

            print("=" * 70)
            print(get_message("mqtt_ws_prompt", USER_LANG), end="", flush=True)  # Restore prompt

        except UnicodeDecodeError as e:
            print(f"\n{get_message('message_encoding_error', USER_LANG)} {str(e)}")
            print(get_message("mqtt_ws_prompt", USER_LANG), end="", flush=True)
        except json.JSONDecodeError as e:
            print(f"\n{get_message('json_parsing_error', USER_LANG)} {str(e)}")
            print(get_message("mqtt_ws_prompt", USER_LANG), end="", flush=True)
        except AttributeError as e:
            print(f"\n{get_message('message_attribute_error', USER_LANG)} {str(e)}")
            print(get_message("mqtt_ws_prompt", USER_LANG), end="", flush=True)
        except Exception as e:
            print(f"\n{get_message('unexpected_message_error', USER_LANG)} {str(e)}")
            print(get_message("mqtt_ws_prompt", USER_LANG), end="", flush=True)

    def connect_to_aws_iot_websocket(self, client_id, access_key, secret_key, session_token, region, endpoint, debug=False):
        """Establish MQTT over WebSocket connection to AWS IoT Core using SigV4"""
        self.print_step(1, get_message("establishing_connection", USER_LANG))

        if debug:
            print(get_message("debug_websocket_setup", USER_LANG))
            print(f"   {get_message('client_id', USER_LANG)}: {client_id}")
            print(f"   {get_message('endpoint', USER_LANG)}: {endpoint}")
            print(f"   {get_message('region', USER_LANG)}: {region}")
            print(f"   {get_message('access_key', USER_LANG)}: {access_key[:10]}..." if access_key else "None")

        try:
            print(get_message("websocket_connection_params", USER_LANG))
            print(f"   {get_message('client_id', USER_LANG)}: {client_id}")
            print(f"   {get_message('endpoint', USER_LANG)}: {endpoint}")
            print(f"   {get_message('port_443', USER_LANG)}")
            print(f"   {get_message('protocol_mqtt311', USER_LANG)}")
            print(f"   {get_message('authentication', USER_LANG)}")
            print(f"   {get_message('region', USER_LANG)}: {region}")

            # Create credentials provider
            credentials_provider = auth.AwsCredentialsProvider.new_static(
                access_key_id=access_key, secret_access_key=secret_key, session_token=session_token
            )

            # Build MQTT connection over WebSocket
            self.connection = mqtt_connection_builder.websockets_with_default_aws_signing(
                endpoint=endpoint,
                region=region,
                credentials_provider=credentials_provider,
                client_id=client_id,
                clean_session=True,
                keep_alive_secs=30,
                on_connection_interrupted=self.on_connection_interrupted,
                on_connection_resumed=self.on_connection_resumed,
            )

            print(f"\n{get_message('connecting_websocket', USER_LANG)}")
            connect_future = self.connection.connect()
            connection_result = connect_future.result()  # Wait for connection

            if debug:
                print(f"{get_message('debug_connection_result', USER_LANG)} {connection_result}")

            self.connected = True

            self.print_mqtt_details(
                get_message("websocket_connection_established", USER_LANG),
                {
                    get_message("status", USER_LANG): get_message("connection_status", USER_LANG),
                    get_message("client_id", USER_LANG): client_id,
                    get_message("endpoint", USER_LANG): endpoint,
                    get_message("transport", USER_LANG): get_message("transport_websocket", USER_LANG),
                    get_message("authentication", USER_LANG): "AWS SigV4",
                    get_message("region", USER_LANG): region,
                    get_message("clean_session", USER_LANG): get_message("clean_session", USER_LANG),
                    get_message("keep_alive", USER_LANG): get_message("keep_alive", USER_LANG),
                    get_message("tls_version", USER_LANG): get_message("tls_version", USER_LANG),
                },
            )

            # Test basic connectivity
            if debug:
                print(get_message("debug_testing_stability", USER_LANG))
                try:
                    time.sleep(1)  # nosemgrep: arbitrary-sleep
                    print(get_message("debug_connection_stable", USER_LANG))
                except Exception as test_e:
                    print(f"{get_message('debug_connection_unstable', USER_LANG)} {str(test_e)}")

            return True

        except Exception as e:
            print(f"{get_message('websocket_connection_failed', USER_LANG)} {str(e)}")
            if debug:
                print(get_message("debug_full_traceback", USER_LANG))
                traceback.print_exc()
            return False

    def subscribe_to_topic(self, topic, qos=0, debug=False):
        """Subscribe to an MQTT topic over WebSocket"""
        if not self.connected:
            print(get_message("not_connected", USER_LANG))
            return False

        try:
            print(f"\n{get_message('subscribing_topic_websocket', USER_LANG)}")
            print(f"   {get_message('topic', USER_LANG)}: {topic}")
            qos_desc = get_message("qos_descriptions", USER_LANG).get(qos, f"QoS {qos}")
            print(f"   QoS: {qos} ({qos_desc})")
            print(f"   {get_message('transport', USER_LANG)}")

            if debug:
                print(get_message("debug_mqtt_websocket_subscribe", USER_LANG))
                print(f"   {get_message('debug_connection_status', USER_LANG)}: {self.connected}")
                print(f"   {get_message('debug_connection_object', USER_LANG)}: {self.connection}")
                print(f"   {get_message('debug_topic_pattern', USER_LANG)}: {topic}")
                print(f"   {get_message('debug_requested_qos', USER_LANG)}: {qos}")

            # Convert QoS to proper enum
            mqtt_qos = mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE

            if debug:
                print(f"{get_message('debug_converted_qos', USER_LANG)} {mqtt_qos}")
                print(f"{get_message('debug_callback_function', USER_LANG)} {self.on_message_received}")

            subscribe_future, packet_id = self.connection.subscribe(
                topic=topic, qos=mqtt_qos, callback=self.on_message_received
            )

            if debug:
                print(get_message("debug_subscribe_sent", USER_LANG))
                print(f"   {get_message('packet_id', USER_LANG)}: {packet_id}")

            # Wait for subscription result
            subscribe_result = subscribe_future.result()

            if debug:
                print(get_message("debug_subscribe_result", USER_LANG))
                print(f"   {get_message('debug_result', USER_LANG)}: {subscribe_result}")
                print(f"   {get_message('debug_result_type', USER_LANG)}: {type(subscribe_result)}")

            # Extract QoS from result - the result format may vary
            granted_qos = qos  # Default fallback
            if hasattr(subscribe_result, "qos"):
                granted_qos = subscribe_result.qos
            elif isinstance(subscribe_result, dict) and "qos" in subscribe_result:
                granted_qos = subscribe_result["qos"]

            self.subscriptions[topic] = {
                "qos": qos,
                "granted_qos": granted_qos,
                "packet_id": packet_id,
                "subscribed_at": datetime.now().isoformat(),
                "transport": "WebSocket",
            }

            self.print_mqtt_details(
                get_message("websocket_subscription_established", USER_LANG),
                {
                    get_message("topic", USER_LANG): topic,
                    get_message("qos_requested", USER_LANG): qos,
                    get_message("qos_granted", USER_LANG): granted_qos,
                    get_message("packet_id", USER_LANG): packet_id,
                    get_message("transport", USER_LANG): "WebSocket with SigV4",
                    get_message("status", USER_LANG): "Successfully subscribed",
                    get_message("wildcard_support", USER_LANG): get_message("wildcard_support", USER_LANG),
                },
            )

            return True

        except Exception as e:
            print(f"{get_message('websocket_subscription_failed', USER_LANG)} {str(e)}")
            print(get_message("detailed_error_info", USER_LANG))
            print(f"   {get_message('error_type', USER_LANG)}: {type(e).__name__}")
            print(f"   {get_message('error_message', USER_LANG)}: {str(e)}")

            # Check for common issues
            error_str = str(e).lower()
            if "timeout" in error_str:
                print(get_message("troubleshooting_timeout", USER_LANG))
                for cause in get_message("timeout_causes", USER_LANG):
                    print(f"   {cause}")
            elif "not authorized" in error_str or "forbidden" in error_str or "access denied" in error_str:
                print(get_message("troubleshooting_auth", USER_LANG))
                for cause in get_message("auth_causes", USER_LANG):
                    print(f"   {cause}")
            elif "invalid topic" in error_str or "malformed" in error_str:
                print(get_message("troubleshooting_invalid_topic", USER_LANG))
                for cause in get_message("invalid_topic_causes", USER_LANG):
                    print(f"   {cause}")
            elif "connection" in error_str or "disconnected" in error_str:
                print(get_message("troubleshooting_connection", USER_LANG))
                for cause in get_message("connection_causes", USER_LANG):
                    print(f"   {cause}")
            else:
                print(get_message("troubleshooting_unknown", USER_LANG))
                for cause in get_message("unknown_causes", USER_LANG):
                    print(f"   {cause.format(topic)}")

            if debug:
                print(get_message("debug_full_traceback", USER_LANG))
                traceback.print_exc()

            return False

    def publish_message(self, topic, message, qos=0, **mqtt_properties):
        """Publish a message to an MQTT topic over WebSocket"""
        if not self.connected:
            print("❌ Not connected to AWS IoT Core")
            return False

        try:
            # Prepare payload
            if isinstance(message, dict):
                payload = json.dumps(message)
                content_type = "application/json"
            else:
                payload = str(message)
                content_type = "text/plain"

            # Extract MQTT5 properties
            user_properties = mqtt_properties.get("user_properties", [])
            correlation_data = mqtt_properties.get("correlation_data", None)
            message_expiry_interval = mqtt_properties.get("message_expiry_interval", None)
            response_topic = mqtt_properties.get("response_topic", None)

            print(f"\n{get_message('publishing_message_websocket', USER_LANG)}")
            print(f"   {get_message('topic', USER_LANG)}: {topic}")
            qos_desc = get_message("qos_descriptions", USER_LANG).get(qos, f"QoS {qos}")
            print(f"   QoS: {qos} ({qos_desc})")
            print(f"   {get_message('payload_size', USER_LANG)}: {len(payload)} {get_message('bytes', USER_LANG)}")
            print(f"   {get_message('content_type', USER_LANG)}: {content_type}")
            print(f"   {get_message('transport', USER_LANG)}")

            # Show MQTT5 properties if any
            if user_properties or correlation_data or message_expiry_interval or response_topic:
                print(f"   {get_message('mqtt5_properties', USER_LANG)}")
                if correlation_data:
                    print(f"      {get_message('correlation_data', USER_LANG)}: {correlation_data}")
                if message_expiry_interval:
                    print(f"      {get_message('message_expiry', USER_LANG)}: {message_expiry_interval}s")
                if response_topic:
                    print(f"      {get_message('response_topic', USER_LANG)}: {response_topic}")
                if user_properties:
                    print(f"      {get_message('user_properties', USER_LANG)}:")
                    for prop in user_properties:
                        print(f"         • {prop[0]}: {prop[1]}")

            # Prepare publish parameters
            publish_params = {
                "topic": topic,
                "payload": payload,
                "qos": mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE,
            }

            # Debug publish parameters
            if self.debug_mode:
                print(get_message("debug_websocket_publish", USER_LANG))
                print(f"   {get_message('topic', USER_LANG)}: {publish_params['topic']}")
                print(f"   QoS: {publish_params['qos']}")
                print(f"   {get_message('debug_payload_length', USER_LANG)}: {len(publish_params['payload'])}")

            publish_future, packet_id = self.connection.publish(**publish_params)

            # Wait for publish to complete
            publish_future.result()

            message_info = {
                "Direction": "SENT",
                "Topic": topic,
                "QoS": qos,
                "Packet ID": packet_id,
                "Payload Size": f"{len(payload)} bytes",
                "Timestamp": datetime.now().isoformat(),
                "Payload": payload,
                "Content Type": content_type,
                "Transport": "WebSocket",
                "User Properties": user_properties,
                "Correlation Data": correlation_data,
                "Message Expiry": message_expiry_interval,
                "Response Topic": response_topic,
            }

            with self.message_lock:
                self.sent_messages.append(message_info)

            # Enhanced publish confirmation with protocol details
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{get_message('published_websocket', USER_LANG, timestamp)}")
            print(f"   📤 {get_message('topic', USER_LANG)}: {topic}")
            print(f"   🏷️  QoS: {qos} | {get_message('packet_id', USER_LANG)}: {packet_id}")
            print(
                f"   📊 {get_message('size', USER_LANG)}: {len(payload)} "
                f"{get_message('bytes', USER_LANG)} | Type: {content_type}"
            )
            print(f"   {get_message('transport', USER_LANG)}")
            if qos > 0:
                print(f"   {get_message('delivery_ack_required', USER_LANG, qos)}")
            else:
                print(f"   {get_message('delivery_fire_forget', USER_LANG)}")

            return True

        except Exception as e:
            print(f"{get_message('websocket_publish_failed', USER_LANG)} {str(e)}")
            print(get_message("detailed_error_info", USER_LANG))
            print(f"   {get_message('error_type', USER_LANG)}: {type(e).__name__}")
            print(f"   {get_message('error_message', USER_LANG)}: {str(e)}")

            # Check for common issues
            error_str = str(e).lower()
            if "timeout" in error_str:
                print(get_message("troubleshooting_publish_timeout", USER_LANG))
                for cause in get_message("timeout_causes", USER_LANG):
                    print(f"   {cause}")
            elif "not authorized" in error_str or "forbidden" in error_str or "access denied" in error_str:
                print(get_message("troubleshooting_auth", USER_LANG))
                for cause in get_message("auth_causes", USER_LANG):
                    print(f"   {cause}")
            elif "invalid topic" in error_str or "malformed" in error_str:
                print(get_message("troubleshooting_invalid_topic", USER_LANG))
                for cause in get_message("invalid_topic_causes", USER_LANG):
                    print(f"   {cause}")
            elif "payload too large" in error_str:
                print(get_message("troubleshooting_payload_large", USER_LANG))
                for info in get_message("payload_limit_info", USER_LANG):
                    print(f"   {info.format(len(payload))}")
            elif "connection" in error_str or "disconnected" in error_str:
                print(get_message("troubleshooting_connection", USER_LANG))
                for cause in get_message("connection_causes", USER_LANG):
                    print(f"   {cause}")
            else:
                print(get_message("troubleshooting_unknown", USER_LANG))
                for cause in get_message("unknown_causes", USER_LANG):
                    print(f"   {cause.format(topic)}")

            return False

    def interactive_messaging(self):
        """Interactive messaging interface for WebSocket MQTT"""
        self.print_step(2, get_message("interactive_messaging", USER_LANG))

        print(get_message("mqtt_topic_guidelines", USER_LANG))
        for guideline in get_message("topic_guidelines", USER_LANG):
            print(f"   {guideline}")

        # Get subscription topic
        while True:
            sub_topic = input(f"\n{get_message('enter_subscribe_topic', USER_LANG)}").strip()
            if sub_topic.lower() == "skip":
                sub_topic = None
                break
            elif sub_topic:
                # Ask for QoS
                while True:
                    qos_choice = input(f"   {get_message('qos_level_prompt', USER_LANG)}").strip()
                    if qos_choice == "" or qos_choice == "0":
                        sub_qos = 0
                        break
                    elif qos_choice == "1":
                        sub_qos = 1
                        break
                    else:
                        print(f"   {get_message('invalid_qos', USER_LANG)}")

                # Check if debug mode is available
                debug_mode = getattr(self, "debug_mode", False)
                if self.subscribe_to_topic(sub_topic, sub_qos, debug=debug_mode):
                    break
                else:
                    print(f"   {get_message('subscription_failed_retry', USER_LANG)}")

                    # Offer connection diagnostics
                    check_debug = input(f"   {get_message('run_diagnostics', USER_LANG)}").strip().lower()
                    if check_debug == "y":
                        self.check_connection_details(sub_topic)
            else:
                print(f"   {get_message('topic_cannot_be_empty', USER_LANG)}")

        # Interactive messaging loop
        print(f"\n{get_message('interactive_websocket_mode', USER_LANG)}")
        print(get_message("messages_appear_immediately", USER_LANG))

        print(f"\n{get_message('commands', USER_LANG)}")
        for command in get_message("command_list", USER_LANG):
            print(f"   {command}")
        print("\n" + "=" * 60)

        while True:
            try:
                command = input(f"\n{get_message('mqtt_ws_prompt', USER_LANG)}").strip()

                if not command:
                    continue

                parts = command.split(" ", 2)
                cmd = parts[0].lower()

                if cmd == "quit":
                    break

                elif cmd == "help":
                    print("\n📖 Available Commands:")
                    for command_help in get_message("command_list", USER_LANG):
                        print(f"   {command_help}")
                    print("\n💡 MQTT5 Properties (props command):")
                    print("   correlation=<data>        - Correlation data for request/response")
                    print("   expiry=<seconds>          - Message expiry interval")
                    print("   response=<topic>          - Response topic for replies")
                    print("   user.<key>=<value>        - User-defined properties")

                elif cmd == "status":
                    print("\n📊 WebSocket Connection Status:")
                    print(f"   Connected: {'✅ Yes' if self.connected else '❌ No'}")
                    print("   Transport: WebSocket with SigV4")
                    print(f"   Subscriptions: {len(self.subscriptions)}")
                    for topic, info in self.subscriptions.items():
                        transport = info.get("transport", "Unknown")
                        print(f"      • {topic} (QoS {info['qos']}) - {transport}")
                    print(f"   Messages Sent: {len(self.sent_messages)}")
                    print(f"   Messages Received: {len(self.received_messages)}")

                elif cmd == "messages":
                    print(f"\n{get_message('message_history', USER_LANG)}")
                    with self.message_lock:
                        if not self.sent_messages and not self.received_messages:
                            print(f"   {get_message('no_messages', USER_LANG)}")
                        else:
                            print(f"   {get_message('received_messages', USER_LANG, len(self.received_messages))}")
                            print(f"   {get_message('sent_messages', USER_LANG, len(self.sent_messages))}")

                            all_messages = self.sent_messages + self.received_messages
                            all_messages.sort(key=lambda x: x["Timestamp"])

                            if all_messages:
                                recent_msg = (
                                    get_message("recent_received", USER_LANG)
                                    if len(self.received_messages) > 0
                                    else get_message("recent_sent", USER_LANG)
                                )
                                print(f"\n   {recent_msg}")
                                for msg in all_messages[-10:]:  # Show last 10 messages
                                    direction = "📤" if msg["Direction"] == "SENT" else "📥"
                                    timestamp = msg["Timestamp"].split("T")[1][:8]
                                    transport = msg.get("Transport", "Unknown")
                                    topic_qos = f"{msg['Topic']} (QoS {msg['QoS']}) - {transport}"
                                    print(f"   {direction} [{timestamp}] {topic_qos}")
                                    if len(str(msg["Payload"])) > 50:
                                        print(f"      {str(msg['Payload'])[:50]}...")
                                    else:
                                        print(f"      {msg['Payload']}")

                elif cmd in ["sub", "sub1"]:
                    if len(parts) < 2:
                        print("   ❌ Usage: sub <topic>")
                        continue

                    topic = parts[1]
                    qos = 1 if cmd == "sub1" else 0

                    debug_mode = getattr(self, "debug_mode", False)
                    if self.subscribe_to_topic(topic, qos, debug=debug_mode):
                        print(f"   ✅ Successfully subscribed to {topic} with QoS {qos}")
                    else:
                        print(f"   ❌ Failed to subscribe to {topic}")

                elif cmd == "unsub":
                    if len(parts) < 2:
                        print("   ❌ Usage: unsub <topic>")
                        continue

                    topic = parts[1]
                    if topic not in self.subscriptions:
                        print(f"   {get_message('not_subscribed_to', USER_LANG, topic)}")
                        continue

                    try:
                        print(f"   {get_message('unsubscribing_from', USER_LANG, topic)}")
                        unsubscribe_future, packet_id = self.connection.unsubscribe(topic)
                        unsubscribe_future.result()
                        del self.subscriptions[topic]
                        print(f"   {get_message('unsubscribed_success', USER_LANG, topic)}")
                    except Exception as e:
                        print(f"   {get_message('unsubscribe_failed', USER_LANG, str(e))}")

                elif cmd in ["pub", "pub1"]:
                    if len(parts) < 3:
                        print("   ❌ Usage: pub <topic> <message>")
                        continue

                    topic = parts[1]
                    message = parts[2]
                    qos = 1 if cmd == "pub1" else 0

                    self.publish_message(topic, message, qos)

                elif cmd == "json":
                    if len(parts) < 3:
                        print(f"   {get_message('json_publish_format', USER_LANG)}")
                        print(f"   {get_message('json_publish_example', USER_LANG)}")
                        continue

                    topic = parts[1]
                    json_parts = parts[2].split()

                    json_obj = {}
                    for part in json_parts:
                        if "=" in part:
                            key, value = part.split("=", 1)
                            # Try to convert to appropriate type
                            try:
                                if value.lower() in ["true", "false"]:
                                    json_obj[key] = value.lower() == "true"
                                elif value.isdigit():
                                    json_obj[key] = int(value)
                                elif "." in value and value.replace(".", "").isdigit():
                                    json_obj[key] = float(value)
                                else:
                                    json_obj[key] = value
                            except (ValueError, TypeError):
                                json_obj[key] = value

                    if json_obj:
                        # Add timestamp
                        json_obj["timestamp"] = datetime.now().isoformat()
                        json_obj["transport"] = "websocket"
                        self.publish_message(topic, json_obj)
                    else:
                        print(f"   {get_message('invalid_json_format', USER_LANG)}")

                elif cmd == "props":
                    if len(parts) < 3:
                        print(f"   {get_message('props_publish_format', USER_LANG)}")
                        print(f"   {get_message('props_publish_example', USER_LANG)}")
                        print(f"   {get_message('available_properties', USER_LANG)}")
                        continue

                    topic = parts[1]
                    message_parts = parts[2].split()
                    message = message_parts[0] if message_parts else ""

                    # Parse MQTT5 properties
                    mqtt_props = {
                        "user_properties": [],
                        "correlation_data": None,
                        "message_expiry_interval": None,
                        "response_topic": None,
                    }

                    for part in message_parts[1:]:
                        if "=" in part:
                            key, value = part.split("=", 1)
                            if key == "correlation" or key == "correlation-data":
                                mqtt_props["correlation_data"] = value
                            elif key == "expiry":
                                try:
                                    mqtt_props["message_expiry_interval"] = int(value)
                                except ValueError:
                                    print(f"   ⚠️  Invalid expiry value: {value}")
                            elif key == "response" or key == "response-topic":
                                mqtt_props["response_topic"] = value
                            elif key.startswith("user."):
                                user_key = key[5:]  # Remove 'user.' prefix
                                mqtt_props["user_properties"].append((user_key, value))
                            else:
                                print(f"   {get_message('unknown_mqtt5_property', USER_LANG, key)}")
                        else:
                            print(f"   {get_message('invalid_props_format', USER_LANG)}")

                    # Clean up None values
                    mqtt_props = {k: v for k, v in mqtt_props.items() if v is not None and v != []}

                    self.publish_message(topic, message, qos=0, **mqtt_props)

                elif cmd == "test":
                    if not self.subscriptions:
                        print(f"   {get_message('no_subscribed_topics', USER_LANG)}")
                    else:
                        test_message = {
                            "message": "Test message from WebSocket MQTT Explorer",
                            "timestamp": datetime.now().isoformat(),
                            "test_id": uuid.uuid4().hex[:8],
                            "transport": "websocket",
                        }

                        print(f"   {get_message('test_message_sent', USER_LANG, len(self.subscriptions))}")
                        for topic in self.subscriptions.keys():
                            print(f"      📤 {topic}")
                            self.publish_message(topic, test_message)

                elif cmd == "debug":
                    topic = parts[1] if len(parts) > 1 else None
                    self.check_connection_details(topic)

                elif cmd == "clear":
                    # Safe screen clearing without os.system
                    print("\n" * 50)
                    print(get_message("clear_screen", USER_LANG))
                    conn_status = "✅" if self.connected else "❌"
                    subs_count = len(self.subscriptions)
                    msg_count = self.message_count
                    print(f"Connected: {conn_status} | Subscriptions: {subs_count} | Messages: {msg_count}")

                else:
                    print(f"   {get_message('invalid_command', USER_LANG)}")

            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user" if USER_LANG == "en" else "\n\n🛑 Interrumpido por el usuario")
                break
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

    def check_connection_details(self, topic=None):
        """Check and display detailed WebSocket connection information"""
        print(f"\n{get_message('connection_diagnostics', USER_LANG)}")
        print("=" * 60)

        print(f"{get_message('connection_status_label', USER_LANG)}:")
        status_text = get_message("connected", USER_LANG) if self.connected else get_message("disconnected", USER_LANG)
        print(f"   • Connected: {'✅' if self.connected else '❌'} {status_text}")
        print("   • Transport: WebSocket with SigV4 Authentication")
        print(f"   • {get_message('subscriptions_count', USER_LANG, len(self.subscriptions))}")
        print(f"   • {get_message('sent_messages', USER_LANG, len(self.sent_messages))}")
        print(f"   • {get_message('received_messages', USER_LANG, len(self.received_messages))}")

        if hasattr(self, "connection") and self.connection:
            try:
                print("\n🔗 WebSocket Connection Details:")
                print("   • Protocol: MQTT 3.1.1 over WebSocket")
                print("   • Port: 443 (HTTPS)")
                print("   • Authentication: AWS SigV4")
                print("   • Keep Alive: 30 seconds")
                print("   • Clean Session: True")
                print("   • TLS Version: 1.2")
            except Exception:
                print("   • Connection object exists but details unavailable")

        if topic:
            print(f"\n📝 Topic Analysis: {topic}")
            print(f"   • Length: {len(topic)} characters (max: 256)")
            print(f"   • Valid characters: {'✅' if all(c.isalnum() or c in '/-_' for c in topic) else '❌'}")
            print(f"   • Starts with '/': {'❌ Invalid' if topic.startswith('/') else '✅ Valid'}")
            print(f"   • Contains '$': {'⚠️  Reserved' if '$' in topic else '✅ Valid'}")

        print("\n🔧 Troubleshooting Steps:")
        if USER_LANG == "es":
            print("1. Verificar que las credenciales de AWS sean válidas y no hayan expirado")
            print("2. Verificar que la política IAM permita acciones IoT (iot:Connect, iot:Publish, iot:Subscribe)")
            print("3. Confirmar que se esté usando la región correcta de AWS")
            print("4. Verificar los logs de AWS IoT en CloudWatch (si están habilitados)")

            print("\n💡 Problemas Comunes de WebSocket:")
            print("   • Credenciales de AWS expiradas o inválidas")
            print("   • Política IAM sin permisos requeridos")
            print("   • Firewall de red bloqueando conexiones WebSocket")
            print("   • Configuración incorrecta de región de AWS")
            print("   • Proxy corporativo interfiriendo con WebSocket")
        else:
            print("1. Verify AWS credentials are valid and not expired")
            print("2. Check IAM policy allows IoT actions (iot:Connect, iot:Publish, iot:Subscribe)")
            print("3. Confirm correct AWS region is being used")
            print("4. Check AWS IoT logs in CloudWatch (if enabled)")

            print("\n💡 Common WebSocket Issues:")
            print("   • AWS credentials expired or invalid")
            print("   • IAM policy missing required permissions")
            print("   • Network firewall blocking WebSocket connections")
            print("   • Incorrect AWS region configuration")
            print("   • Corporate proxy interfering with WebSocket")

    def disconnect(self):
        """Disconnect from AWS IoT Core WebSocket"""
        if self.connection and self.connected:
            print(
                "\n🔌 Disconnecting from AWS IoT Core WebSocket..."
                if USER_LANG == "en"
                else "\n🔌 Desconectando de AWS IoT Core WebSocket..."
            )

            # Unsubscribe from all topics
            for topic in list(self.subscriptions.keys()):
                try:
                    unsubscribe_future, packet_id = self.connection.unsubscribe(topic)
                    unsubscribe_future.result()
                    print(f"   {get_message('unsubscribed_success', USER_LANG, topic)}")
                except Exception as e:
                    print(f"   ⚠️  Error unsubscribing from {topic}: {str(e)}")

            # Disconnect
            try:
                disconnect_future = self.connection.disconnect()
                disconnect_future.result()

                self.print_mqtt_details(
                    "WEBSOCKET DISCONNECTION",
                    {
                        get_message("status", USER_LANG): "Successfully disconnected from AWS IoT Core",
                        get_message("transport", USER_LANG): "WebSocket with SigV4",
                        "Total Messages Sent": len(self.sent_messages),
                        "Total Messages Received": len(self.received_messages),
                        "Session Duration": "Connection closed cleanly",
                    },
                )

            except Exception as e:
                print(f"   ❌ Error during disconnect: {str(e)}")

            self.connected = False


def main():
    global USER_LANG, DEBUG_MODE

    try:
        # Get user's preferred language
        USER_LANG = get_language()

        # Check for debug flag
        debug_mode = "--debug" in sys.argv or "-d" in sys.argv
        DEBUG_MODE = debug_mode

        print(get_message("title", USER_LANG))
        print(get_message("separator", USER_LANG))

        # Display AWS context first
        try:
            sts = boto3.client("sts")
            iot = boto3.client("iot")
            identity = sts.get_caller_identity()

            print("📍 AWS Configuration:")
            print(f"   Account ID: {identity['Account']}")
            print(f"   Region: {iot.meta.region_name}")
            print()

        except Exception as e:
            print(f"⚠️ Could not retrieve AWS context: {str(e)}")
            print("   Make sure AWS credentials are configured")
            print()

        print(get_message("description_intro", USER_LANG))
        print("This tool demonstrates:")
        print("• MQTT connection over WebSocket with SigV4 authentication")
        print("• Topic subscription and publishing with QoS options")
        print("• Detailed MQTT protocol information for every operation")
        print("• Interactive messaging with real-time feedback")

        print("\n📚 LEARNING MOMENT: MQTT over WebSocket")
        if USER_LANG == "es":
            long_text = (
                "MQTT sobre WebSocket permite la comunicación IoT a través de navegadores web y conexiones "
                "amigables con firewalls. En lugar de certificados X.509, usa autenticación AWS SigV4 con "
                "credenciales IAM. Este enfoque es ideal para aplicaciones web, aplicaciones móviles y "
                "entornos donde la gestión de certificados es desafiante."
            )
            print(long_text)
            print("\n🔄 SIGUIENTE: Estableceremos una conexión MQTT WebSocket usando credenciales de AWS")
        else:
            long_text = (
                "MQTT over WebSocket enables IoT communication through web browsers and firewall-friendly "
                "connections. Instead of X.509 certificates, it uses AWS SigV4 authentication with IAM "
                "credentials. This approach is ideal for web applications, mobile apps, and environments "
                "where certificate management is challenging."
            )
            print(long_text)
            print("\n🔄 NEXT: We will establish a WebSocket MQTT connection using AWS credentials")

        input("Press Enter to continue..." if USER_LANG == "en" else "Presiona Enter para continuar...")

        if debug_mode:
            print(f"\n{get_message('debug_enabled', USER_LANG)}")
            for feature in get_message("debug_features", USER_LANG):
                print(feature)
        else:
            print(f"\n{get_message('tip', USER_LANG)}")

        print(get_message("separator", USER_LANG))

        client = MQTTWebSocketExplorer()
        client.debug_mode = debug_mode  # Store debug mode in client

        try:
            # Get IoT endpoint
            endpoint = client.get_iot_endpoint(debug=debug_mode)
            if not endpoint:
                return

            # Get AWS credentials
            access_key, secret_key, session_token, region = client.get_aws_credentials(debug=debug_mode)
            if not access_key or not secret_key:
                return

            # Get client ID from user or auto-generate
            client_id = client.get_client_id()
            if not client_id:
                return

            # Connect to AWS IoT via WebSocket
            if not client.connect_to_aws_iot_websocket(
                client_id, access_key, secret_key, session_token, region, endpoint, debug=debug_mode
            ):
                return

            # Interactive messaging
            client.interactive_messaging()

        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user" if USER_LANG == "en" else "\n\n🛑 Interrumpido por el usuario")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}" if USER_LANG == "en" else f"\n❌ Error inesperado: {str(e)}")
            if debug_mode:
                traceback.print_exc()
        finally:
            # Always disconnect cleanly
            client.disconnect()
            print(
                "\n👋 WebSocket MQTT Client Explorer session ended"
                if USER_LANG == "en"
                else "\n👋 Sesión del Explorador Cliente MQTT WebSocket terminada"
            )

    except KeyboardInterrupt:
        print(f"\n\n{get_message('goodbye', USER_LANG)}")


if __name__ == "__main__":
    main()

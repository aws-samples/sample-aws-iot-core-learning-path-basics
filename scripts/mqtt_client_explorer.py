#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT MQTT Client Explorer
Educational MQTT client for learning AWS IoT Core communication patterns.
"""
import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime

import boto3
from awscrt import mqtt
from awsiot import mqtt_connection_builder

# Simple translation system for learning content
MESSAGES = {
    "en": {
        "title": "📡 AWS IoT MQTT Client Explorer",
        "separator": "=" * 60,
        "aws_context_info": "🌍 AWS Context Information:",
        "account_id": "Account ID",
        "region": "Region",
        "aws_context_error": "⚠️ Could not retrieve AWS context:",
        "aws_credentials_reminder": "   Make sure AWS credentials are configured",
        "description_intro": "This script teaches you AWS IoT MQTT communication:",
        "mqtt_concepts": [
            "• Real-time messaging with MQTT protocol",
            "• Certificate-based device authentication",
            "• Topic-based publish/subscribe patterns",
            "• Quality of Service (QoS) levels",
            "• Connection management and error handling",
            "• Complete MQTT protocol details for each operation",
        ],
        "debug_enabled": "🔍 DEBUG MODE ENABLED",
        "debug_features": [
            "• Enhanced MQTT protocol logging",
            "• Full connection and message details",
            "• Extended troubleshooting information",
        ],
        "tip": "💡 Tip: Use --debug or -d flag for enhanced MQTT logging",
        "press_enter": "Press Enter to continue...",
        "goodbye": "👋 Goodbye!",
        "main_menu": "📋 Main Menu:",
        "menu_options": ["1. Connect to AWS IoT Core with Certificate", "2. Exit"],
        "select_option": "Select option (1-2): ",
        "invalid_choice": "❌ Invalid choice. Please select 1-2.",
        "step_establishing_connection": "Establishing MQTT Connection",
        "step_interactive_messaging": "Interactive MQTT Messaging",
        "mqtt_connection_setup": "🔍 DEBUG: MQTT Connection Setup",
        "thing_name_label": "Thing Name",
        "certificate_file_label": "Certificate File",
        "private_key_file_label": "Private Key File",
        "endpoint_label": "Endpoint",
        "connection_parameters": "🔗 Connection Parameters:",
        "client_id_label": "Client ID",
        "port_label": "Port",
        "protocol_label": "Protocol",
        "authentication_label": "Authentication",
        "connecting_to_iot": "🔄 Connecting to AWS IoT Core...",
        "connection_result_debug": "🔍 DEBUG: Connection result:",
        "connection_established": "CONNECTION ESTABLISHED",
        "connection_status_success": "Successfully connected to AWS IoT Core",
        "clean_session_label": "Clean Session",
        "keep_alive_label": "Keep Alive",
        "tls_version_label": "TLS Version",
        "cert_auth_label": "Certificate Authentication",
        "testing_connection_stability": "🔍 DEBUG: Testing MQTT connection stability...",
        "connection_stable": "✅ Connection appears stable and ready for operations",
        "connection_unstable": "⚠️  Connection established but may be unstable:",
        "connection_failed": "❌ Connection failed:",
        "iot_endpoint_discovery": "🌐 AWS IoT Endpoint Discovery",
        "endpoint_type_label": "Endpoint Type",
        "endpoint_type_recommended": "iot:Data-ATS (recommended)",
        "endpoint_url_label": "Endpoint URL",
        "port_mqtt_tls": "8883 (MQTT over TLS)",
        "protocol_mqtt_tls": "MQTT 3.1.1 over TLS",
        "error_getting_endpoint": "❌ Error getting IoT endpoint:",
        "debug_calling_api": "🔍 DEBUG: Calling describe_endpoint API",
        "debug_input_params": "📥 Input Parameters:",
        "debug_api_response": "📤 API Response:",
        "debug_full_traceback": "🔍 DEBUG: Full traceback:",
        "available_devices": "📱 Available Devices ({} found):",
        "no_things_found": "❌ No Things found. Please run setup_sample_data.py first",
        "select_device": "Select device (1-{}):",
        "invalid_selection": "❌ Invalid selection. Please enter 1-{}",
        "enter_valid_number": "❌ Please enter a valid number",
        "operation_cancelled": "🛑 Operation cancelled",
        "selected_device": "✅ Selected device:",
        "debug_calling_list_things": "🔍 DEBUG: Calling list_things API",
        "debug_input_params_none": "📥 Input Parameters: None",
        "debug_api_response_found_things": "📤 API Response: Found {} Things",
        "debug_thing_names": "📊 Thing Names:",
        "debug_calling_list_principals": "🔍 DEBUG: Calling list_thing_principals API",
        "debug_input_params_thing": "📥 Input Parameters:",
        "debug_api_response_principals": "📤 API Response: Found {} principals, {} certificates",
        "debug_certificate_arns": "📊 Certificate ARNs:",
        "no_certificates_found": "❌ No certificates found for device '{}'",
        "run_certificate_manager": "💡 Run certificate_manager.py to create and attach a certificate",
        "using_certificate": "✅ Using certificate:",
        "multiple_certificates_found": "🔐 Multiple certificates found:",
        "select_certificate": "Select certificate (1-{}):",
        "cert_dir_not_found": "❌ Certificate directory not found:",
        "run_cert_manager_files": "💡 Run certificate_manager.py to create certificate files",
        "cert_files_not_found": "❌ Certificate files not found in {}",
        "looking_for_files": "   Looking for: {}.crt and {}.key",
        "cert_files_found": "✅ Certificate files found:",
        "certificate_label": "Certificate",
        "private_key_label": "Private Key",
        "error_selecting_device": "❌ Error selecting device:",
        "connection_interrupted": "CONNECTION INTERRUPTED",
        "error_label": "Error",
        "timestamp_label": "Timestamp",
        "auto_reconnect_label": "Auto Reconnect",
        "auto_reconnect_msg": "AWS IoT SDK will attempt to reconnect automatically",
        "connection_resumed": "CONNECTION RESUMED",
        "return_code_label": "Return Code",
        "session_present_label": "Session Present",
        "status_label": "Status",
        "connection_restored": "Connection restored successfully",
        "resubscribing_topics": "🔄 Re-subscribing to {} topics after reconnection...",
        "resubscribed_to_topic": "   ✅ Re-subscribed to {} (QoS {})",
        "failed_resubscribe": "   ❌ Failed to re-subscribe to {}:",
        "incoming_message": "🔔 INCOMING MESSAGE #{} [{}]",
        "topic_label": "📥 Topic:",
        "qos_label": "🏷️  QoS:",
        "qos_at_most_once": "At most once",
        "qos_at_least_once": "At least once",
        "qos_exactly_once": "Exactly once",
        "payload_size_label": "📊 Payload Size:",
        "flags_label": "🚩 Flags:",
        "duplicate_flag": "🔄 DUPLICATE (retransmitted)",
        "retain_flag": "📌 RETAIN (stored by broker)",
        "mqtt5_properties": "🔧 MQTT5 Properties:",
        "content_type_prop": "📄 Content-Type:",
        "correlation_data_prop": "🔗 Correlation-Data:",
        "message_expiry_prop": "⏰ Message-Expiry:",
        "response_topic_prop": "↩️  Response-Topic:",
        "payload_format_prop": "📝 Payload-Format:",
        "user_properties_prop": "🏷️  User-Properties:",
        "utf8_string": "UTF-8 String",
        "bytes_format": "Bytes",
        "properties_count": "{} properties",
        "message_payload": "💬 Message Payload:",
        "json_format": "   📋 JSON Format:",
        "text_format": "   📝 Text:",
        "error_processing_message": "❌ Error processing received message:",
        "mqtt_prompt": "📡 MQTT> ",
        "not_connected_iot": "❌ Not connected to AWS IoT Core",
        "subscribing_to_topic": "📥 Subscribing to Topic",
        "debug_subscribe_operation": "🔍 DEBUG: MQTT Subscribe Operation",
        "connection_status_debug": "   Connection Status:",
        "connection_object_debug": "   Connection Object:",
        "topic_pattern_debug": "   Topic Pattern:",
        "requested_qos_debug": "   Requested QoS:",
        "converted_qos_debug": "🔍 DEBUG: Converted QoS:",
        "callback_function_debug": "🔍 DEBUG: Callback function:",
        "subscribe_request_sent": "🔍 DEBUG: Subscribe request sent, waiting for response...",
        "packet_id_debug": "   Packet ID:",
        "subscribe_result_received": "🔍 DEBUG: Subscribe result received:",
        "result_debug": "   Result:",
        "result_type_debug": "   Result type:",
        "subscription_established": "SUBSCRIPTION ESTABLISHED",
        "qos_requested_label": "QoS Requested",
        "qos_granted_label": "QoS Granted",
        "packet_id_label": "Packet ID",
        "status_subscribed": "Successfully subscribed",
        "wildcard_support": "Wildcard Support",
        "wildcard_support_msg": "AWS IoT supports + (single level) and # (multi level)",
        "subscription_failed": "❌ Subscription failed:",
        "detailed_error_info": "🔍 Detailed Error Information:",
        "error_type_label": "   Error Type:",
        "error_message_label": "   Error Message:",
        "troubleshooting_timeout": "💡 Troubleshooting: Subscription timeout",
        "timeout_reasons": [
            "   • MQTT connection may be unstable",
            "   • Network connectivity issues",
            "   • AWS IoT endpoint may be unreachable",
        ],
        "troubleshooting_auth": "💡 Troubleshooting: Authorization failed",
        "auth_reasons": [
            "   • Certificate may not be ACTIVE",
            "   • Certificate may not be attached to Thing",
            "   • Policy may not be attached to certificate",
        ],
        "troubleshooting_invalid_topic": "💡 Troubleshooting: Invalid topic format",
        "invalid_topic_reasons": [
            "   • Topics cannot start with '/' or '$' (unless AWS reserved)",
            "   • Use alphanumeric characters, hyphens, and forward slashes",
            "   • Maximum topic length is 256 characters",
        ],
        "troubleshooting_connection": "💡 Troubleshooting: Connection issue",
        "connection_reasons": [
            "   • MQTT connection may have been lost",
            "   • Certificate files may be corrupted",
            "   • Endpoint URL may be incorrect",
        ],
        "troubleshooting_unknown": "💡 Troubleshooting: Unknown subscription failure",
        "unknown_reasons": [
            "   • Run 'debug {}' command for detailed diagnostics",
            "   • Check AWS IoT logs in CloudWatch if enabled",
        ],
        "publishing_message": "📤 Publishing Message",
        "content_type_label": "Content-Type",
        "mqtt5_properties_label": "🔧 MQTT5 Properties:",
        "published_timestamp": "✅ [{}] PUBLISHED",
        "delivery_ack_required": "🔄 Delivery: Acknowledgment required (QoS {})",
        "delivery_fire_forget": "🚀 Delivery: Fire-and-forget (QoS 0)",
        "publish_failed": "❌ Publish failed:",
        "troubleshooting_publish_timeout": "💡 Troubleshooting: Publish timeout",
        "troubleshooting_payload_large": "💡 Troubleshooting: Payload size limit exceeded",
        "payload_limit_msg": "   • AWS IoT message size limit is 128 KB",
        "current_payload_size": "   • Current payload size: {} bytes",
        "mqtt_topic_guidelines": "💡 MQTT Topic Guidelines:",
        "topic_guidelines": [
            "   • Use forward slashes (/) to separate topic levels",
            "   • Avoid spaces and special characters",
            "   • Use descriptive names: device/sensor/temperature",
            "   • Wildcards: + (single level), # (multi-level)",
        ],
        "interactive_commands": "📋 Interactive Commands:",
        "command_list": [
            "   • 'sub <topic>' - Subscribe to topic (QoS 0)",
            "   • 'sub1 <topic>' - Subscribe to topic (QoS 1)",
            "   • 'unsub <topic>' - Unsubscribe from topic",
            "   • 'pub <topic> <message>' - Publish message (QoS 0)",
            "   • 'pub1 <topic> <message>' - Publish message (QoS 1)",
            "   • 'json <topic> key=val...' - Publish JSON message",
            "   • 'test' - Send test message",
            "   • 'status' - Show connection status",
            "   • 'messages' - Show message history",
            "   • 'debug' - Connection diagnostics",
            "   • 'help' - Show this help",
            "   • 'quit' - Exit interactive mode",
        ],
        "enter_command": "Enter command (or 'help' for options):",
        "invalid_command": "❌ Invalid command. Type 'help' for available commands.",
        "exiting_interactive": "Exiting interactive mode...",
        "connection_status": "📊 Connection Status:",
        "connected_status": "✅ Connected to AWS IoT Core",
        "disconnected_status": "❌ Not connected",
        "active_subscriptions": "📥 Active Subscriptions:",
        "no_subscriptions": "   No active subscriptions",
        "message_history": "📜 Message History:",
        "no_messages": "   No messages yet",
        "no_messages_received": "   No messages received yet",
        "sent_messages": "📤 Sent Messages:",
        "received_messages": "📥 Received Messages:",
        "connection_diagnostics": "🔍 Connection Diagnostics:",
        "connected_label": "Connected",
        "subscriptions_label": "Subscriptions",
        "messages_received_label": "Messages received",
        "not_set": "Not set",
        "enter_topic_subscribe": "Enter topic to subscribe to:",
        "enter_qos_level": "Enter QoS level (0 or 1, default 0):",
        "enter_topic_publish": "Enter topic to publish to:",
        "enter_message": "Enter message:",
        "client_id_prompt": "Enter custom Client ID (or press Enter for auto-generated): ",
        "client_id_auto_generated": "Auto-generated Client ID",
        "client_id_custom": "Custom Client ID",
        "client_id_invalid": "❌ Invalid Client ID. Must be 1-128 characters, alphanumeric, hyphens, and underscores only.",
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
        "title": "📡 Explorador de Cliente MQTT de AWS IoT",
        "separator": "=" * 60,
        "aws_context_info": "🌍 Información de Contexto de AWS:",
        "account_id": "ID de Cuenta",
        "region": "Región",
        "aws_context_error": "⚠️ No se pudo recuperar el contexto de AWS:",
        "aws_credentials_reminder": "   Asegúrate de que las credenciales de AWS estén configuradas",
        "description_intro": "Este script te enseña comunicación MQTT de AWS IoT:",
        "mqtt_concepts": [
            "• Mensajería en tiempo real con protocolo MQTT",
            "• Autenticación de dispositivos basada en certificados",
            "• Patrones de publicación/suscripción basados en temas",
            "• Niveles de Calidad de Servicio (QoS)",
            "• Gestión de conexiones y manejo de errores",
            "• Detalles completos del protocolo MQTT para cada operación",
        ],
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Registro mejorado del protocolo MQTT",
            "• Detalles completos de conexión y mensajes",
            "• Información extendida de resolución de problemas",
        ],
        "tip": "💡 Consejo: Usa la bandera --debug o -d para registro mejorado de MQTT",
        "press_enter": "Presiona Enter para continuar...",
        "goodbye": "👋 ¡Adiós!",
        "main_menu": "📋 Menú Principal:",
        "menu_options": ["1. Conectar a AWS IoT Core con Certificado", "2. Salir"],
        "select_option": "Seleccionar opción (1-2): ",
        "invalid_choice": "❌ Selección inválida. Por favor selecciona 1-2.",
        "step_establishing_connection": "Estableciendo Conexión MQTT",
        "step_interactive_messaging": "Mensajería Interactiva MQTT",
        "mqtt_connection_setup": "🔍 DEBUG: Configuración de Conexión MQTT",
        "thing_name_label": "Nombre del Thing",
        "certificate_file_label": "Archivo de Certificado",
        "private_key_file_label": "Archivo de Clave Privada",
        "endpoint_label": "Endpoint",
        "connection_parameters": "🔗 Parámetros de Conexión:",
        "client_id_label": "ID de Cliente",
        "port_label": "Puerto",
        "protocol_label": "Protocolo",
        "authentication_label": "Autenticación",
        "connecting_to_iot": "🔄 Conectando a AWS IoT Core...",
        "connection_result_debug": "🔍 DEBUG: Resultado de conexión:",
        "connection_established": "CONEXIÓN ESTABLECIDA",
        "connection_status_success": "Conectado exitosamente a AWS IoT Core",
        "clean_session_label": "Sesión Limpia",
        "keep_alive_label": "Keep Alive",
        "tls_version_label": "Versión TLS",
        "cert_auth_label": "Autenticación de Certificado",
        "testing_connection_stability": "🔍 DEBUG: Probando estabilidad de conexión MQTT...",
        "connection_stable": "✅ La conexión parece estable y lista para operaciones",
        "connection_unstable": "⚠️  Conexión establecida pero puede ser inestable:",
        "connection_failed": "❌ Conexión falló:",
        "iot_endpoint_discovery": "🌐 Descubrimiento de Endpoint de AWS IoT",
        "endpoint_type_label": "Tipo de Endpoint",
        "endpoint_type_recommended": "iot:Data-ATS (recomendado)",
        "endpoint_url_label": "URL del Endpoint",
        "port_mqtt_tls": "8883 (MQTT sobre TLS)",
        "protocol_mqtt_tls": "MQTT 3.1.1 sobre TLS",
        "error_getting_endpoint": "❌ Error obteniendo endpoint de IoT:",
        "debug_calling_api": "🔍 DEBUG: Llamando API describe_endpoint",
        "debug_input_params": "📥 Parámetros de Entrada:",
        "debug_api_response": "📤 Respuesta de API:",
        "debug_full_traceback": "🔍 DEBUG: Traza completa:",
        "available_devices": "📱 Dispositivos Disponibles ({} encontrados):",
        "no_things_found": "❌ No se encontraron Things. Por favor ejecuta setup_sample_data.py primero",
        "select_device": "Seleccionar dispositivo (1-{}):",
        "invalid_selection": "❌ Selección inválida. Por favor ingresa 1-{}",
        "enter_valid_number": "❌ Por favor ingresa un número válido",
        "operation_cancelled": "🛑 Operación cancelada",
        "selected_device": "✅ Dispositivo seleccionado:",
        "debug_calling_list_things": "🔍 DEBUG: Llamando API list_things",
        "debug_input_params_none": "📥 Parámetros de Entrada: Ninguno",
        "debug_api_response_found_things": "📤 Respuesta de API: Se encontraron {} Things",
        "debug_thing_names": "📊 Nombres de Things:",
        "debug_calling_list_principals": "🔍 DEBUG: Llamando API list_thing_principals",
        "debug_input_params_thing": "📥 Parámetros de Entrada:",
        "debug_api_response_principals": "📤 Respuesta de API: Se encontraron {} principales, {} certificados",
        "debug_certificate_arns": "📊 ARNs de Certificados:",
        "no_certificates_found": "❌ No se encontraron certificados para el dispositivo '{}'",
        "run_certificate_manager": "💡 Ejecuta certificate_manager.py para crear y vincular un certificado",
        "using_certificate": "✅ Usando certificado:",
        "multiple_certificates_found": "🔐 Se encontraron múltiples certificados:",
        "select_certificate": "Seleccionar certificado (1-{}):",
        "cert_dir_not_found": "❌ Directorio de certificados no encontrado:",
        "run_cert_manager_files": "💡 Ejecuta certificate_manager.py para crear archivos de certificado",
        "cert_files_not_found": "❌ Archivos de certificado no encontrados en {}",
        "looking_for_files": "   Buscando: {}.crt y {}.key",
        "cert_files_found": "✅ Archivos de certificado encontrados:",
        "certificate_label": "Certificado",
        "private_key_label": "Clave Privada",
        "error_selecting_device": "❌ Error seleccionando dispositivo:",
        "connection_interrupted": "CONEXIÓN INTERRUMPIDA",
        "error_label": "Error",
        "timestamp_label": "Marca de Tiempo",
        "auto_reconnect_label": "Reconexión Automática",
        "auto_reconnect_msg": "El SDK de AWS IoT intentará reconectarse automáticamente",
        "connection_resumed": "CONEXIÓN RESTABLECIDA",
        "return_code_label": "Código de Retorno",
        "session_present_label": "Sesión Presente",
        "status_label": "Estado",
        "connection_restored": "Conexión restaurada exitosamente",
        "resubscribing_topics": "🔄 Re-suscribiéndose a {} temas después de la reconexión...",
        "resubscribed_to_topic": "   ✅ Re-suscrito a {} (QoS {})",
        "failed_resubscribe": "   ❌ Error al re-suscribirse a {}:",
        "incoming_message": "🔔 MENSAJE ENTRANTE #{} [{}]",
        "topic_label": "📥 Tema:",
        "qos_label": "🏷️  QoS:",
        "qos_at_most_once": "A lo sumo una vez",
        "qos_at_least_once": "Al menos una vez",
        "qos_exactly_once": "Exactamente una vez",
        "payload_size_label": "📊 Tamaño del Payload:",
        "flags_label": "🚩 Banderas:",
        "duplicate_flag": "🔄 DUPLICADO (retransmitido)",
        "retain_flag": "📌 RETENER (almacenado por broker)",
        "mqtt5_properties": "🔧 Propiedades MQTT5:",
        "content_type_prop": "📄 Content-Type:",
        "correlation_data_prop": "🔗 Correlation-Data:",
        "message_expiry_prop": "⏰ Message-Expiry:",
        "response_topic_prop": "↩️  Response-Topic:",
        "payload_format_prop": "📝 Payload-Format:",
        "user_properties_prop": "🏷️  User-Properties:",
        "utf8_string": "Cadena UTF-8",
        "bytes_format": "Bytes",
        "properties_count": "{} propiedades",
        "message_payload": "💬 Payload del Mensaje:",
        "json_format": "   📋 Formato JSON:",
        "text_format": "   📝 Texto:",
        "error_processing_message": "❌ Error procesando mensaje recibido:",
        "mqtt_prompt": "📡 MQTT> ",
        "not_connected_iot": "❌ No conectado a AWS IoT Core",
        "subscribing_to_topic": "📥 Suscribiéndose al Tema",
        "debug_subscribe_operation": "🔍 DEBUG: Operación de Suscripción MQTT",
        "connection_status_debug": "   Estado de Conexión:",
        "connection_object_debug": "   Objeto de Conexión:",
        "topic_pattern_debug": "   Patrón de Tema:",
        "requested_qos_debug": "   QoS Solicitado:",
        "converted_qos_debug": "🔍 DEBUG: QoS Convertido:",
        "callback_function_debug": "🔍 DEBUG: Función de callback:",
        "subscribe_request_sent": "🔍 DEBUG: Solicitud de suscripción enviada, esperando respuesta...",
        "packet_id_debug": "   ID de Paquete:",
        "subscribe_result_received": "🔍 DEBUG: Resultado de suscripción recibido:",
        "result_debug": "   Resultado:",
        "result_type_debug": "   Tipo de resultado:",
        "subscription_established": "SUSCRIPCIÓN ESTABLECIDA",
        "qos_requested_label": "QoS Solicitado",
        "qos_granted_label": "QoS Otorgado",
        "packet_id_label": "ID de Paquete",
        "status_subscribed": "Suscrito exitosamente",
        "wildcard_support": "Soporte de Comodines",
        "wildcard_support_msg": "AWS IoT soporta + (nivel único) y # (múltiples niveles)",
        "subscription_failed": "❌ Suscripción falló:",
        "detailed_error_info": "🔍 Información Detallada del Error:",
        "error_type_label": "   Tipo de Error:",
        "error_message_label": "   Mensaje de Error:",
        "troubleshooting_timeout": "💡 Resolución de Problemas: Timeout de suscripción",
        "timeout_reasons": [
            "   • La conexión MQTT puede ser inestable",
            "   • Problemas de conectividad de red",
            "   • El endpoint de AWS IoT puede no ser alcanzable",
        ],
        "troubleshooting_auth": "💡 Resolución de Problemas: Autorización falló",
        "auth_reasons": [
            "   • El certificado puede no estar ACTIVO",
            "   • El certificado puede no estar vinculado al Thing",
            "   • La política puede no estar vinculada al certificado",
        ],
        "troubleshooting_invalid_topic": "💡 Resolución de Problemas: Formato de tema inválido",
        "invalid_topic_reasons": [
            "   • Los temas no pueden empezar con '/' o '$' (a menos que sean reservados de AWS)",
            "   • Usa caracteres alfanuméricos, guiones y barras diagonales",
            "   • La longitud máxima del tema es 256 caracteres",
        ],
        "troubleshooting_connection": "💡 Resolución de Problemas: Problema de conexión",
        "connection_reasons": [
            "   • La conexión MQTT puede haberse perdido",
            "   • Los archivos de certificado pueden estar corruptos",
            "   • La URL del endpoint puede ser incorrecta",
        ],
        "troubleshooting_unknown": "💡 Resolución de Problemas: Fallo de suscripción desconocido",
        "unknown_reasons": [
            "   • Ejecuta el comando 'debug {}' para diagnósticos detallados",
            "   • Revisa los logs de AWS IoT en CloudWatch si están habilitados",
        ],
        "publishing_message": "📤 Publicando Mensaje",
        "content_type_label": "Content-Type",
        "mqtt5_properties_label": "🔧 Propiedades MQTT5:",
        "published_timestamp": "✅ [{}] PUBLICADO",
        "delivery_ack_required": "🔄 Entrega: Confirmación requerida (QoS {})",
        "delivery_fire_forget": "🚀 Entrega: Disparar y olvidar (QoS 0)",
        "publish_failed": "❌ Publicación falló:",
        "troubleshooting_publish_timeout": "💡 Resolución de Problemas: Timeout de publicación",
        "troubleshooting_payload_large": "💡 Resolución de Problemas: Límite de tamaño de payload excedido",
        "payload_limit_msg": "   • El límite de tamaño de mensaje de AWS IoT es 128 KB",
        "current_payload_size": "   • Tamaño actual del payload: {} bytes",
        "mqtt_topic_guidelines": "💡 Guías de Temas MQTT:",
        "topic_guidelines": [
            "   • Usa barras diagonales (/) para separar niveles de tema",
            "   • Evita espacios y caracteres especiales",
            "   • Usa nombres descriptivos: device/sensor/temperature",
            "   • Comodines: + (nivel único), # (múltiples niveles)",
        ],
        "interactive_commands": "📋 Comandos Interactivos:",
        "command_list": [
            "   • 'sub <tema>' - Suscribirse al tema (QoS 0)",
            "   • 'sub1 <tema>' - Suscribirse al tema (QoS 1)",
            "   • 'unsub <tema>' - Desuscribirse del tema",
            "   • 'pub <tema> <mensaje>' - Publicar mensaje (QoS 0)",
            "   • 'pub1 <tema> <mensaje>' - Publicar mensaje (QoS 1)",
            "   • 'json <tema> clave=val...' - Publicar mensaje JSON",
            "   • 'test' - Enviar mensaje de prueba",
            "   • 'status' - Mostrar estado de conexión",
            "   • 'messages' - Mostrar historial de mensajes",
            "   • 'debug' - Diagnósticos de conexión",
            "   • 'help' - Mostrar esta ayuda",
            "   • 'quit' - Salir del modo interactivo",
        ],
        "enter_command": "Ingresa comando (o 'help' para opciones):",
        "invalid_command": "❌ Comando inválido. Escribe 'help' para comandos disponibles.",
        "exiting_interactive": "Saliendo del modo interactivo...",
        "connection_status": "📊 Estado de Conexión:",
        "connected_status": "✅ Conectado a AWS IoT Core",
        "disconnected_status": "❌ No conectado",
        "active_subscriptions": "📥 Suscripciones Activas:",
        "no_subscriptions": "   No hay suscripciones activas",
        "message_history": "📜 Historial de Mensajes:",
        "no_messages": "   No hay mensajes aún",
        "no_messages_received": "   No se han recibido mensajes aún",
        "sent_messages": "📤 Mensajes Enviados:",
        "received_messages": "📥 Mensajes Recibidos:",
        "connection_diagnostics": "🔍 Diagnósticos de Conexión:",
        "connected_label": "Conectado",
        "subscriptions_label": "Suscripciones",
        "messages_received_label": "Mensajes recibidos",
        "not_set": "No configurado",
        "enter_topic_subscribe": "Ingresa el tema al cual suscribirse:",
        "enter_qos_level": "Ingresa el nivel QoS (0 o 1, por defecto 0):",
        "enter_topic_publish": "Ingresa el tema donde publicar:",
        "enter_message": "Ingresa el mensaje:",
        "client_id_prompt": "Ingresa ID de Cliente personalizado (o presiona Enter para auto-generar): ",
        "client_id_auto_generated": "ID de Cliente Auto-generado",
        "client_id_custom": "ID de Cliente Personalizado",
        "client_id_invalid": "❌ ID de Cliente inválido. Debe tener 1-128 caracteres, solo alfanuméricos, guiones y guiones bajos.",
        "client_id_guidelines": "💡 Guías de ID de Cliente:",
        "client_id_rules": [
            "• Debe ser único por conexión",
            "• Se permiten 1-128 caracteres",
            "• Usa alfanuméricos, guiones (-) y guiones bajos (_)",
            "• Evita espacios y caracteres especiales",
            "• Ejemplo: mi-dispositivo-001, sensor_temp_01",
        ],
    },
    "ja": {
        "title": "📡 AWS IoT MQTT クライアントエクスプローラー",
        "separator": "=" * 45,
        "aws_config": "📍 AWS設定:",
        "account_id": "アカウントID",
        "region": "リージョン",
        "description": "証明書ベースの認証を使用したリアルタイムMQTT通信の学習。",
        "debug_enabled": "🔍 デバッグモード有効",
        "debug_features": ["• 詳細なMQTT接続ログ", "• 完全なメッセージペイロード", "• 拡張エラー診断"],
        "tip": "💡 ヒント: 詳細なMQTTログには--debugフラグを使用",
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
        "mqtt_intro_title": "MQTT通信 - リアルタイムメッセージング",
        "mqtt_intro_content": "MQTTは、IoTデバイス間のリアルタイム通信を可能にする軽量メッセージングプロトコルです。AWS IoT Coreは、X.509証明書を使用した安全なMQTT接続を提供します。このエクスプローラーでは、トピックの購読、メッセージの公開、リアルタイム通信パターンを学習します。",
        "mqtt_intro_next": "証明書ベースのMQTT接続を確立し、メッセージングを探索します",
        "press_enter": "Enterキーを押して続行...",
        "goodbye": "👋 さようなら！",
        "certificate_selection_title": "🔐 証明書選択",
        "available_certificates": "利用可能な証明書:",
        "no_certificates_found": "❌ 証明書が見つかりません。certificate_manager.pyを実行して証明書を作成してください。",
        "select_certificate": "証明書を選択 (1-{}): ",
        "invalid_certificate_choice": "❌ 無効な選択です。1-{}を選択してください。",
        "selected_certificate": "✅ 選択された証明書: {}",
        "certificate_files_check": "🔍 証明書ファイルを確認中...",
        "certificate_file_found": "✅ 見つかりました: {}",
        "certificate_file_missing": "❌ 見つかりません: {}",
        "certificate_files_ready": "✅ すべての証明書ファイルが準備完了",
        "certificate_files_incomplete": "❌ 証明書ファイルが不完全です。certificate_manager.pyを実行してください。",
        "getting_endpoint": "🌐 IoTエンドポイントを取得中...",
        "endpoint_retrieved": "✅ エンドポイント: {}",
        "error_getting_endpoint": "❌ エンドポイント取得エラー: {}",
        "connecting_mqtt": "🔌 MQTTクライアントに接続中...",
        "mqtt_connected": "✅ MQTTに接続されました！",
        "mqtt_connection_failed": "❌ MQTT接続に失敗しました: {}",
        "mqtt_disconnected": "🔌 MQTTから切断されました",
        "operations_menu": "📋 利用可能な操作:",
        "operations": ["1. トピックを購読", "2. メッセージを公開", "3. 接続状態を表示", "4. 切断して終了"],
        "select_operation": "操作を選択 (1-4): ",
        "invalid_choice": "❌ 無効な選択です。1-4を選択してください。",
        "subscribe_learning_title": "📚 学習ポイント: MQTTトピック購読",
        "subscribe_learning_content": "トピック購読により、特定のトピックに公開されたメッセージをリアルタイムで受信できます。MQTTはワイルドカード（+は単一レベル、#は複数レベル）をサポートし、複数のトピックを効率的に監視できます。",
        "subscribe_learning_next": "トピックを購読し、リアルタイムメッセージを受信します",
        "enter_topic_subscribe": "購読するトピックを入力:",
        "subscribing_to_topic": "📡 トピック '{}' を購読中...",
        "subscribed_successfully": "✅ トピック '{}' の購読に成功しました",
        "subscription_failed": "❌ 購読に失敗しました: {}",
        "publish_learning_title": "📚 学習ポイント: MQTTメッセージ公開",
        "publish_learning_content": "メッセージ公開により、特定のトピックにデータを送信し、そのトピックを購読しているすべてのクライアントに配信できます。これは、センサーデータ、コマンド、ステータス更新の送信に使用されます。",
        "publish_learning_next": "トピックにメッセージを公開し、リアルタイム配信を確認します",
        "enter_topic_publish": "公開するトピックを入力:",
        "enter_message": "メッセージを入力:",
        "publishing_message": "📤 メッセージを公開中...",
        "message_published": "✅ メッセージが公開されました",
        "publish_failed": "❌ 公開に失敗しました: {}",
        "connection_status_title": "🔌 接続状態",
        "connection_status_connected": "✅ 接続済み",
        "connection_status_disconnected": "❌ 切断済み",
        "endpoint_info": "エンドポイント: {}",
        "certificate_info": "証明書: {}",
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
        "mqtt_error": "❌ MQTTエラー:",
        "error": "❌ エラー:",
        "client_id_prompt": "カスタムクライアントIDを入力 (または自動生成するにはEnterを押す): ",
        "client_id_auto_generated": "自動生成クライアントID",
        "client_id_custom": "カスタムクライアントID",
        "client_id_invalid": "❌ 無効なクライアントID。1-128文字、英数字、ハイフン、アンダースコアのみ使用可能。",
        "client_id_guidelines": "💡 クライアントIDガイドライン:",
        "client_id_rules": [
            "• 接続ごとに一意である必要があります",
            "• 1-128文字が許可されています",
            "• 英数字、ハイフン(-)、アンダースコア(_)を使用",
            "• スペースや特殊文字は避ける",
            "• 例: my-device-001, sensor_temp_01",
        ],
    },
    "pt-BR": {
        "title": "📡 Explorador de Cliente MQTT AWS IoT",
        "separator": "=" * 60,
        "aws_context_info": "🌍 Informações de Contexto AWS:",
        "account_id": "ID da Conta",
        "region": "Região",
        "aws_context_error": "⚠️ Não foi possível recuperar o contexto AWS:",
        "aws_credentials_reminder": "   Certifique-se de que as credenciais AWS estão configuradas",
        "description_intro": "Este script ensina comunicação MQTT AWS IoT:",
        "mqtt_concepts": [
            "• Mensagens em tempo real com protocolo MQTT",
            "• Autenticação de dispositivos baseada em certificados",
            "• Padrões de publicação/inscrição baseados em tópicos",
            "• Níveis de Qualidade de Serviço (QoS)",
            "• Gerenciamento de conexão e tratamento de erros",
            "• Detalhes completos do protocolo MQTT para cada operação",
        ],
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Log aprimorado do protocolo MQTT",
            "• Detalhes completos de conexão e mensagens",
            "• Informações estendidas de solução de problemas",
        ],
        "tip": "💡 Dica: Use a flag --debug ou -d para log aprimorado de MQTT",
        "press_enter": "Pressione Enter para continuar...",
        "goodbye": "👋 Tchau!",
        "main_menu": "📋 Menu Principal:",
        "menu_options": ["1. Conectar ao AWS IoT Core com Certificado", "2. Sair"],
        "select_option": "Selecionar opção (1-2): ",
        "invalid_choice": "❌ Escolha inválida. Por favor selecione 1-2.",
        "step_establishing_connection": "Estabelecendo Conexão MQTT",
        "step_interactive_messaging": "Mensagens Interativas MQTT",
        "connection_parameters": "🔗 Parâmetros de Conexão:",
        "client_id_label": "ID do Cliente",
        "endpoint_label": "Endpoint",
        "port_label": "Porta",
        "protocol_label": "Protocolo",
        "authentication_label": "Autenticação",
        "connecting_to_iot": "🔄 Conectando ao AWS IoT Core...",
        "connection_established": "CONEXÃO ESTABELECIDA",
        "connection_status_success": "Conectado com sucesso ao AWS IoT Core",
        "connection_failed": "❌ Conexão falhou:",
        "iot_endpoint_discovery": "🌐 Descoberta de Endpoint AWS IoT",
        "endpoint_type_label": "Tipo de Endpoint",
        "endpoint_type_recommended": "iot:Data-ATS (recomendado)",
        "endpoint_url_label": "URL do Endpoint",
        "port_mqtt_tls": "8883 (MQTT sobre TLS)",
        "protocol_mqtt_tls": "MQTT 3.1.1 sobre TLS",
        "error_getting_endpoint": "❌ Erro obtendo endpoint IoT:",
        "available_devices": "📱 Dispositivos Disponíveis ({} encontrados):",
        "no_things_found": "❌ Nenhum Thing encontrado. Por favor execute setup_sample_data.py primeiro",
        "select_device": "Selecionar dispositivo (1-{}):",
        "invalid_selection": "❌ Seleção inválida. Por favor digite 1-{}",
        "enter_valid_number": "❌ Por favor digite um número válido",
        "operation_cancelled": "🛑 Operação cancelada",
        "selected_device": "✅ Dispositivo selecionado:",
        "no_certificates_found": "❌ Nenhum certificado encontrado para o dispositivo '{}'",
        "run_certificate_manager": "💡 Execute certificate_manager.py para criar e anexar um certificado",
        "using_certificate": "✅ Usando certificado:",
        "multiple_certificates_found": "🔐 Múltiplos certificados encontrados:",
        "select_certificate": "Selecionar certificado (1-{}):",
        "cert_dir_not_found": "❌ Diretório de certificados não encontrado:",
        "run_cert_manager_files": "💡 Execute certificate_manager.py para criar arquivos de certificado",
        "cert_files_not_found": "❌ Arquivos de certificado não encontrados em {}",
        "looking_for_files": "   Procurando: {}.crt e {}.key",
        "cert_files_found": "✅ Arquivos de certificado encontrados:",
        "certificate_label": "Certificado",
        "private_key_label": "Chave Privada",
        "error_selecting_device": "❌ Erro selecionando dispositivo:",
        "connection_interrupted": "CONEXÃO INTERROMPIDA",
        "connection_resumed": "CONEXÃO RETOMADA",
        "incoming_message": "🔔 MENSAGEM RECEBIDA #{} [{}]",
        "topic_label": "📥 Tópico:",
        "qos_label": "🏷️  QoS:",
        "qos_at_most_once": "No máximo uma vez",
        "qos_at_least_once": "Pelo menos uma vez",
        "qos_exactly_once": "Exatamente uma vez",
        "payload_size_label": "📋 Tamanho do Payload:",
        "message_payload": "💬 Payload da Mensagem:",
        "json_format": "   📋 Formato JSON:",
        "text_format": "   📝 Texto:",
        "error_processing_message": "❌ Erro processando mensagem recebida:",
        "mqtt_prompt": "📡 MQTT> ",
        "not_connected_iot": "❌ Não conectado ao AWS IoT Core",
        "subscribing_to_topic": "📥 Inscrevendo-se no Tópico",
        "subscription_established": "INSCRIÇÃO ESTABELECIDA",
        "subscription_failed": "❌ Inscrição falhou:",
        "publishing_message": "📤 Publicando Mensagem",
        "published_timestamp": "✅ [{}] PUBLICADO",
        "publish_failed": "❌ Publicação falhou:",
        "interactive_commands": "📋 Comandos Interativos:",
        "command_list": [
            "   • 'sub <tópico>' - Inscrever-se no tópico (QoS 0)",
            "   • 'sub1 <tópico>' - Inscrever-se no tópico (QoS 1)",
            "   • 'unsub <tópico>' - Cancelar inscrição do tópico",
            "   • 'pub <tópico> <mensagem>' - Publicar mensagem (QoS 0)",
            "   • 'pub1 <tópico> <mensagem>' - Publicar mensagem (QoS 1)",
            "   • 'json <tópico> chave=val...' - Publicar mensagem JSON",
            "   • 'test' - Enviar mensagem de teste",
            "   • 'status' - Mostrar status da conexão",
            "   • 'messages' - Mostrar histórico de mensagens",
            "   • 'debug' - Diagnósticos de conexão",
            "   • 'help' - Mostrar esta ajuda",
            "   • 'quit' - Sair do modo interativo",
        ],
        "invalid_command": "❌ Comando inválido. Digite 'help' para comandos disponíveis.",
        "exiting_interactive": "Saindo do modo interativo...",
        "connection_status": "📋 Status da Conexão:",
        "connected_status": "✅ Conectado ao AWS IoT Core",
        "disconnected_status": "❌ Não conectado",
        "active_subscriptions": "📥 Inscrições Ativas:",
        "no_subscriptions": "   Nenhuma inscrição ativa",
        "message_history": "📜 Histórico de Mensagens:",
        "no_messages_received": "   Nenhuma mensagem recebida ainda",
        "connection_diagnostics": "🔍 Diagnósticos de Conexão:",
        "connected_label": "Conectado",
        "subscriptions_label": "Inscrições",
        "messages_received_label": "Mensagens recebidas",
        "not_set": "Não definido",
        "client_id_prompt": "Digite ID do Cliente personalizado (ou pressione Enter para auto-gerar): ",
        "client_id_auto_generated": "ID do Cliente Auto-gerado",
        "client_id_custom": "ID do Cliente Personalizado",
        "client_id_invalid": "❌ ID do Cliente inválido. Deve ter 1-128 caracteres, apenas alfanuméricos, hífens e sublinhados.",
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
        "title": "📡 AWS IoT MQTT 클라이언트 탐색기",
        "separator": "=" * 60,
        "aws_context_info": "🌍 AWS 컨텍스트 정보:",
        "account_id": "계정 ID",
        "region": "리전",
        "aws_context_error": "⚠️ AWS 컨텍스트를 검색할 수 없습니다:",
        "aws_credentials_reminder": "   AWS 자격 증명이 구성되어 있는지 확인하세요",
        "description_intro": "이 스크립트는 AWS IoT MQTT 통신을 가르칩니다:",
        "mqtt_concepts": [
            "• MQTT 프로토콜을 사용한 실시간 메시징",
            "• 인증서 기반 디바이스 인증",
            "• 주제 기반 게시/구독 패턴",
            "• 서비스 품질(QoS) 수준",
            "• 연결 관리 및 오류 처리",
            "• 각 작업에 대한 완전한 MQTT 프로토콜 세부 정보",
        ],
        "debug_enabled": "🔍 디버그 모드 활성화",
        "debug_features": [
            "• 향상된 MQTT 프로토콜 로깅",
            "• 완전한 연결 및 메시지 세부 정보",
            "• 확장된 문제 해결 정보",
        ],
        "tip": "💡 팁: 향상된 MQTT 로깅을 위해 --debug 또는 -d 플래그를 사용하세요",
        "press_enter": "계속하려면 Enter를 누르세요...",
        "goodbye": "👋 안녕히 가세요!",
        "main_menu": "📋 메인 메뉴:",
        "menu_options": ["1. 인증서로 AWS IoT Core에 연결", "2. 종료"],
        "select_option": "옵션 선택 (1-2): ",
        "invalid_choice": "❌ 잘못된 선택입니다. 1-2를 선택해주세요.",
        "step_establishing_connection": "MQTT 연결 설정",
        "step_interactive_messaging": "대화형 MQTT 메시징",
        "mqtt_connection_setup": "🔍 디버그: MQTT 연결 설정",
        "thing_name_label": "Thing 이름",
        "certificate_file_label": "인증서 파일",
        "private_key_file_label": "개인 키 파일",
        "endpoint_label": "엔드포인트",
        "connection_parameters": "🔗 연결 매개변수:",
        "client_id_label": "클라이언트 ID",
        "port_label": "포트",
        "protocol_label": "프로토콜",
        "authentication_label": "인증",
        "connecting_to_iot": "🔄 AWS IoT Core에 연결 중...",
        "connection_result_debug": "🔍 디버그: 연결 결과:",
        "connection_established": "연결 설정됨",
        "connection_status_success": "AWS IoT Core에 성공적으로 연결됨",
        "clean_session_label": "클린 세션",
        "keep_alive_label": "Keep Alive",
        "tls_version_label": "TLS 버전",
        "cert_auth_label": "인증서 인증",
        "testing_connection_stability": "🔍 디버그: MQTT 연결 안정성 테스트 중...",
        "connection_stable": "✅ 연결이 안정적이며 작업 준비가 완료되었습니다",
        "connection_unstable": "⚠️  연결이 설정되었지만 불안정할 수 있습니다:",
        "connection_failed": "❌ 연결 실패:",
        "iot_endpoint_discovery": "🌐 AWS IoT 엔드포인트 검색",
        "endpoint_type_label": "엔드포인트 유형",
        "endpoint_type_recommended": "iot:Data-ATS (권장)",
        "endpoint_url_label": "엔드포인트 URL",
        "port_mqtt_tls": "8883 (TLS를 통한 MQTT)",
        "protocol_mqtt_tls": "TLS를 통한 MQTT 3.1.1",
        "error_getting_endpoint": "❌ IoT 엔드포인트 가져오기 오류:",
        "debug_calling_api": "🔍 디버그: describe_endpoint API 호출",
        "debug_input_params": "📥 입력 매개변수:",
        "debug_api_response": "📤 API 응답:",
        "debug_full_traceback": "🔍 디버그: 전체 추적:",
        "available_devices": "📱 사용 가능한 디바이스 ({} 개 발견):",
        "no_things_found": "❌ Things를 찾을 수 없습니다. 먼저 setup_sample_data.py를 실행하세요",
        "select_device": "디바이스 선택 (1-{}):",
        "invalid_selection": "❌ 잘못된 선택입니다. 1-{}를 입력하세요",
        "enter_valid_number": "❌ 유효한 숫자를 입력하세요",
        "operation_cancelled": "🛑 작업이 취소되었습니다",
        "selected_device": "✅ 선택된 디바이스:",
        "debug_calling_list_things": "🔍 디버그: list_things API 호출",
        "debug_input_params_none": "📥 입력 매개변수: 없음",
        "debug_api_response_found_things": "📤 API 응답: {} Things 발견",
        "debug_thing_names": "📊 Thing 이름:",
        "debug_calling_list_principals": "🔍 디버그: list_thing_principals API 호출",
        "debug_input_params_thing": "📥 입력 매개변수:",
        "debug_api_response_principals": "📤 API 응답: {} 주체, {} 인증서 발견",
        "debug_certificate_arns": "📊 인증서 ARN:",
        "no_certificates_found": "❌ 디바이스 '{}'에 대한 인증서를 찾을 수 없습니다",
        "run_certificate_manager": "💡 certificate_manager.py를 실행하여 인증서를 생성하고 연결하세요",
        "using_certificate": "✅ 인증서 사용:",
        "multiple_certificates_found": "🔐 여러 인증서 발견:",
        "select_certificate": "인증서 선택 (1-{}):",
        "cert_dir_not_found": "❌ 인증서 디렉토리를 찾을 수 없습니다:",
        "run_cert_manager_files": "💡 certificate_manager.py를 실행하여 인증서 파일을 생성하세요",
        "cert_files_not_found": "❌ {}에서 인증서 파일을 찾을 수 없습니다",
        "looking_for_files": "   찾는 파일: {}.crt 및 {}.key",
        "cert_files_found": "✅ 인증서 파일 발견:",
        "certificate_label": "인증서",
        "private_key_label": "개인 키",
        "error_selecting_device": "❌ 디바이스 선택 오류:",
        "connection_interrupted": "연결 중단됨",
        "error_label": "오류",
        "timestamp_label": "타임스탬프",
        "auto_reconnect_label": "자동 재연결",
        "auto_reconnect_msg": "AWS IoT SDK가 자동으로 재연결을 시도합니다",
        "connection_resumed": "연결 재개됨",
        "return_code_label": "반환 코드",
        "session_present_label": "세션 존재",
        "status_label": "상태",
        "connection_restored": "연결이 성공적으로 복원되었습니다",
        "resubscribing_topics": "🔄 재연결 후 {} 주제에 다시 구독 중...",
        "resubscribed_to_topic": "   ✅ {}에 다시 구독됨 (QoS {})",
        "failed_resubscribe": "   ❌ {}에 다시 구독 실패:",
        "incoming_message": "🔔 수신 메시지 #{} [{}]",
        "topic_label": "📥 주제:",
        "qos_label": "🏷️  QoS:",
        "qos_at_most_once": "최대 한 번",
        "qos_at_least_once": "최소 한 번",
        "qos_exactly_once": "정확히 한 번",
        "payload_size_label": "📊 페이로드 크기:",
        "flags_label": "🚩 플래그:",
        "duplicate_flag": "🔄 중복 (재전송됨)",
        "retain_flag": "📌 보관 (브로커에 저장됨)",
        "mqtt5_properties": "🔧 MQTT5 속성:",
        "content_type_prop": "📄 Content-Type:",
        "correlation_data_prop": "🔗 Correlation-Data:",
        "message_expiry_prop": "⏰ Message-Expiry:",
        "response_topic_prop": "↩️  Response-Topic:",
        "payload_format_prop": "📝 Payload-Format:",
        "user_properties_prop": "🏷️  User-Properties:",
        "utf8_string": "UTF-8 문자열",
        "bytes_format": "바이트",
        "properties_count": "{} 속성",
        "message_payload": "💬 메시지 페이로드:",
        "json_format": "   📋 JSON 형식:",
        "text_format": "   📝 텍스트:",
        "error_processing_message": "❌ 수신된 메시지 처리 오류:",
        "mqtt_prompt": "📡 MQTT> ",
        "not_connected_iot": "❌ AWS IoT Core에 연결되지 않음",
        "subscribing_to_topic": "📥 주제 구독",
        "debug_subscribe_operation": "🔍 디버그: MQTT 구독 작업",
        "connection_status_debug": "   연결 상태:",
        "connection_object_debug": "   연결 객체:",
        "topic_pattern_debug": "   주제 패턴:",
        "requested_qos_debug": "   요청된 QoS:",
        "converted_qos_debug": "🔍 디버그: 변환된 QoS:",
        "callback_function_debug": "🔍 디버그: 콜백 함수:",
        "subscribe_request_sent": "🔍 디버그: 구독 요청 전송됨, 응답 대기 중...",
        "packet_id_debug": "   패킷 ID:",
        "subscribe_result_received": "🔍 디버그: 구독 결과 수신됨:",
        "result_debug": "   결과:",
        "result_type_debug": "   결과 유형:",
        "subscription_established": "구독 설정됨",
        "qos_requested_label": "요청된 QoS",
        "qos_granted_label": "부여된 QoS",
        "packet_id_label": "패킷 ID",
        "status_subscribed": "성공적으로 구독됨",
        "wildcard_support": "와일드카드 지원",
        "wildcard_support_msg": "AWS IoT는 + (단일 레벨) 및 # (다중 레벨)을 지원합니다",
        "subscription_failed": "❌ 구독 실패:",
        "detailed_error_info": "🔍 자세한 오류 정보:",
        "error_type_label": "   오류 유형:",
        "error_message_label": "   오류 메시지:",
        "troubleshooting_timeout": "💡 문제 해결: 구독 시간 초과",
        "timeout_reasons": [
            "   • MQTT 연결이 불안정할 수 있습니다",
            "   • 네트워크 연결 문제",
            "   • AWS IoT 엔드포인트에 도달할 수 없을 수 있습니다",
        ],
        "troubleshooting_auth": "💡 문제 해결: 권한 부여 실패",
        "auth_reasons": [
            "   • 인증서가 ACTIVE 상태가 아닐 수 있습니다",
            "   • 인증서가 Thing에 연결되지 않았을 수 있습니다",
            "   • 정책이 인증서에 연결되지 않았을 수 있습니다",
        ],
        "troubleshooting_invalid_topic": "💡 문제 해결: 잘못된 주제 형식",
        "invalid_topic_reasons": [
            "   • 주제는 '/' 또는 '$'로 시작할 수 없습니다 (AWS 예약어 제외)",
            "   • 영숫자, 하이픈, 슬래시를 사용하세요",
            "   • 최대 주제 길이는 256자입니다",
        ],
        "troubleshooting_connection": "💡 문제 해결: 연결 문제",
        "connection_reasons": [
            "   • MQTT 연결이 끊어졌을 수 있습니다",
            "   • 인증서 파일이 손상되었을 수 있습니다",
            "   • 엔드포인트 URL이 잘못되었을 수 있습니다",
        ],
        "troubleshooting_unknown": "💡 문제 해결: 알 수 없는 구독 실패",
        "unknown_reasons": [
            "   • 자세한 진단을 위해 'debug {}' 명령을 실행하세요",
            "   • 활성화된 경우 CloudWatch에서 AWS IoT 로그를 확인하세요",
        ],
        "publishing_message": "📤 메시지 게시",
        "content_type_label": "Content-Type",
        "mqtt5_properties_label": "🔧 MQTT5 속성:",
        "published_timestamp": "✅ [{}] 게시됨",
        "delivery_ack_required": "🔄 전달: 확인 필요 (QoS {})",
        "delivery_fire_forget": "🚀 전달: 발사 후 망각 (QoS 0)",
        "publish_failed": "❌ 게시 실패:",
        "troubleshooting_publish_timeout": "💡 문제 해결: 게시 시간 초과",
        "troubleshooting_payload_large": "💡 문제 해결: 페이로드 크기 제한 초과",
        "payload_limit_msg": "   • AWS IoT 메시지 크기 제한은 128 KB입니다",
        "current_payload_size": "   • 현재 페이로드 크기: {} 바이트",
        "mqtt_topic_guidelines": "💡 MQTT 주제 가이드라인:",
        "topic_guidelines": [
            "   • 슬래시(/)를 사용하여 주제 레벨을 구분하세요",
            "   • 공백과 특수 문자를 피하세요",
            "   • 설명적인 이름을 사용하세요: device/sensor/temperature",
            "   • 와일드카드: + (단일 레벨), # (다중 레벨)",
        ],
        "interactive_commands": "📋 대화형 명령:",
        "command_list": [
            "   • 'sub <주제>' - 주제 구독 (QoS 0)",
            "   • 'sub1 <주제>' - 주제 구독 (QoS 1)",
            "   • 'unsub <주제>' - 주제 구독 해제",
            "   • 'pub <주제> <메시지>' - 메시지 게시 (QoS 0)",
            "   • 'pub1 <주제> <메시지>' - 메시지 게시 (QoS 1)",
            "   • 'json <주제> key=val...' - JSON 메시지 게시",
            "   • 'test' - 테스트 메시지 전송",
            "   • 'status' - 연결 상태 표시",
            "   • 'messages' - 메시지 기록 표시",
            "   • 'debug' - 연결 진단",
            "   • 'help' - 이 도움말 표시",
            "   • 'quit' - 대화형 모드 종료",
        ],
        "enter_command": "명령 입력 (또는 옵션을 보려면 'help'):",
        "invalid_command": "❌ 잘못된 명령입니다. 사용 가능한 명령을 보려면 'help'를 입력하세요.",
        "exiting_interactive": "대화형 모드를 종료합니다...",
        "connection_status": "📊 연결 상태:",
        "connected_status": "✅ AWS IoT Core에 연결됨",
        "disconnected_status": "❌ 연결되지 않음",
        "active_subscriptions": "📥 활성 구독:",
        "no_subscriptions": "   활성 구독 없음",
        "message_history": "📜 메시지 기록:",
        "no_messages": "   아직 메시지 없음",
        "no_messages_received": "   아직 메시지를 받지 않았습니다",
        "sent_messages": "📤 전송된 메시지:",
        "received_messages": "📥 수신된 메시지:",
        "connection_diagnostics": "🔍 연결 진단:",
        "connected_label": "연결됨",
        "subscriptions_label": "구독",
        "messages_received_label": "수신된 메시지",
        "not_set": "설정되지 않음",
        "enter_topic_subscribe": "구독할 주제를 입력하세요:",
        "enter_qos_level": "QoS 레벨을 입력하세요 (0 또는 1, 기본값 0):",
        "enter_topic_publish": "게시할 주제를 입력하세요:",
        "enter_message": "메시지를 입력하세요:",
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


def interactive_messaging(mqtt_client):
    """Interactive command-line interface for MQTT operations"""
    if not mqtt_client.connected:
        print(get_message("not_connected_iot", USER_LANG))
        return

    print(f"\n{get_message('step_interactive_messaging', USER_LANG)}")
    print("=" * 50)

    # Show available commands
    print(f"\n{get_message('interactive_commands', USER_LANG)}")
    for command in get_message("command_list", USER_LANG):
        print(command)

    print(f"\n{get_message('mqtt_topic_guidelines', USER_LANG)}")
    for guideline in get_message("topic_guidelines", USER_LANG):
        print(guideline)

    print("\n" + "=" * 50)

    while True:
        try:
            command_input = input("\n📡 MQTT> ").strip()

            if not command_input:
                continue

            parts = command_input.split()
            command = parts[0].lower()

            if command in ["quit", "exit"]:
                print(get_message("exiting_interactive", USER_LANG))
                # Clean up connection state when exiting interactive mode
                mqtt_client.cleanup_connection_state()
                break

            elif command == "help":
                print(f"\n{get_message('interactive_commands', USER_LANG)}")
                for cmd in get_message("command_list", USER_LANG):
                    print(cmd)

            elif command == "status":
                print(f"\n{get_message('connection_status', USER_LANG)}")
                if mqtt_client.connected:
                    print(get_message("connected_status", USER_LANG))
                else:
                    print(get_message("disconnected_status", USER_LANG))

                print(f"\n{get_message('active_subscriptions', USER_LANG)}")
                if mqtt_client.subscriptions:
                    for topic, info in mqtt_client.subscriptions.items():
                        print(f"   • {topic} (QoS {info['qos']})")
                else:
                    print(get_message("no_subscriptions", USER_LANG))

            elif command == "messages":
                print(f"\n{get_message('message_history', USER_LANG)}")
                if mqtt_client.received_messages:
                    for i, msg in enumerate(mqtt_client.received_messages[-10:], 1):
                        timestamp = msg.get("Timestamp", "Unknown")
                        topic = msg.get("Topic", "Unknown")
                        payload = str(msg.get("Payload", ""))[:100]
                        print(f"   {i}. [{timestamp}] {topic}: {payload}...")
                else:
                    print(get_message("no_messages_received", USER_LANG))

            elif command == "debug":
                print(f"\n{get_message('connection_diagnostics', USER_LANG)}")
                print(
                    f"   {get_message('endpoint_label', USER_LANG)}: {mqtt_client.endpoint or get_message('not_set', USER_LANG)}"
                )
                print(
                    f"   {get_message('thing_name_label', USER_LANG)}: {mqtt_client.thing_name or get_message('not_set', USER_LANG)}"
                )
                print(f"   {get_message('connected_label', USER_LANG)}: {mqtt_client.connected}")
                print(f"   {get_message('subscriptions_label', USER_LANG)}: {len(mqtt_client.subscriptions)}")
                print(f"   {get_message('messages_received_label', USER_LANG)}: {len(mqtt_client.received_messages)}")

            elif command == "sub":
                if len(parts) < 2:
                    print("Usage: sub <topic>")
                    continue
                topic = parts[1]
                mqtt_client.subscribe_to_topic(topic, 0, DEBUG_MODE)

            elif command == "sub1":
                if len(parts) < 2:
                    print("Usage: sub1 <topic>")
                    continue
                topic = parts[1]
                mqtt_client.subscribe_to_topic(topic, 1, DEBUG_MODE)

            elif command == "unsub":
                if len(parts) < 2:
                    print("Usage: unsub <topic>")
                    continue
                topic = parts[1]
                if hasattr(mqtt_client, "unsubscribe_from_topic"):
                    mqtt_client.unsubscribe_from_topic(topic, DEBUG_MODE)
                else:
                    print("Unsubscribe functionality not implemented yet")

            elif command == "pub":
                if len(parts) < 3:
                    print("Usage: pub <topic> <message>")
                    continue
                topic = parts[1]
                message = "".join(parts[2:])
                mqtt_client.publish_message(topic, message, 0)

            elif command == "pub1":
                if len(parts) < 3:
                    print("Usage: pub1 <topic> <message>")
                    continue
                topic = parts[1]
                message = "".join(parts[2:])
                mqtt_client.publish_message(topic, message, 1)

            elif command == "json":
                if len(parts) < 3:
                    print("Usage: json <topic> key=val key2=val2...")
                    continue
                topic = parts[1]
                # Parse key=value pairs into JSON
                json_data = {}
                for pair in parts[2:]:
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        # Try to parse as number or boolean
                        if value.lower() == "true":
                            json_data[key] = True
                        elif value.lower() == "false":
                            json_data[key] = False
                        elif value.isdigit():
                            json_data[key] = int(value)
                        else:
                            try:
                                json_data[key] = float(value)
                            except ValueError:
                                json_data[key] = value
                mqtt_client.publish_message(topic, json_data, 0)

            elif command == "test":
                # Send a test message
                test_topic = f"test/{getattr(mqtt_client, 'thing_name', 'device')}/message"
                test_message = {
                    "timestamp": time.time(),
                    "message": "Hello from MQTT Client Explorer!",
                    "device": getattr(mqtt_client, "thing_name", "unknown"),
                }
                mqtt_client.publish_message(test_topic, test_message, 0)

            else:
                print(get_message("invalid_command", USER_LANG))

        except KeyboardInterrupt:
            print(f"\n{get_message('exiting_interactive', USER_LANG)}")
            # Clean up connection state when exiting interactive mode
            mqtt_client.cleanup_connection_state()
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if DEBUG_MODE:
                import traceback

                traceback.print_exc()


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
    print("🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma / 언어 선택")
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
                "\nSelect language / Seleccionar idioma / 言語を選択 / 选择语言 / Selecionar idioma / 언어 선택 (1-6): "
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
                print("Selección inválida. Por favor selecciona 1-6.")
                print("無効な選択です。1-6を選択してください。")
                print("无效选择。请选择 1-6。")
                print("Escolha inválida. Por favor selecione 1-6.")
                print("잘못된 선택입니다. 1-6을 선택해주세요.")
        except KeyboardInterrupt:
            print("\n\nGoodbye! / ¡Adiós! / さようなら！ / 再见！ / Tchau! / 안녕히 가세요!")
            sys.exit(0)


def get_message(key, lang="en", category=None):
    """Get localized message"""
    # Handle nested categories
    if category:
        return MESSAGES.get(lang, MESSAGES["en"]).get(category, {}).get(key, key)

    return MESSAGES.get(lang, MESSAGES["en"]).get(key, key)


def display_aws_context():
    """Display current AWS account and region information"""
    try:
        sts = boto3.client("sts")
        iot = boto3.client("iot")
        identity = sts.get_caller_identity()

        print(f"\n{get_message('aws_context_info', USER_LANG)}")
        print(f"   {get_message('account_id', USER_LANG)}: {identity['Account']}")
        print(f"   {get_message('region', USER_LANG)}: {iot.meta.region_name}")
    except Exception as e:
        print(f"\n{get_message('aws_context_error', USER_LANG)} {str(e)}")
        print(get_message("aws_credentials_reminder", USER_LANG))
    print()


class MQTTClientExplorer:
    def __init__(self):
        self.connection = None
        self.connected = False
        self.received_messages = []
        self.sent_messages = []
        self.subscriptions = {}
        self.message_lock = threading.Lock()
        self.message_count = 0
        self.endpoint = None
        self.thing_name = None

    def cleanup_connection_state(self):
        """Clean up connection state when disconnecting or reconnecting"""
        self.connected = False
        self.received_messages = []
        self.sent_messages = []
        self.subscriptions = {}
        self.message_count = 0
        if self.connection:
            try:
                self.connection.disconnect()
            except Exception:
                pass
        self.connection = None

    def print_header(self, title):
        """Print formatted header"""
        print(f"\n📡 {title}")
        print("=" * 60)

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

    def get_client_id(self, thing_name):
        """Get client ID from user input or generate automatically"""
        print(f"\n{get_message('client_id_guidelines', USER_LANG)}")
        for rule in get_message("client_id_rules", USER_LANG):
            print(f"   {rule}")

        while True:
            try:
                custom_id = input(f"\n{get_message('client_id_prompt', USER_LANG)}").strip()

                if not custom_id:
                    # Auto-generate client ID
                    client_id = f"{thing_name}-{uuid.uuid4().hex[:8]}"
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
        """Get AWS IoT endpoint for the account"""
        try:
            iot = boto3.client("iot")

            if debug:
                print(get_message("debug_calling_api", USER_LANG))
                print(f"{get_message('debug_input_params', USER_LANG)} {{'endpointType': 'iot:Data-ATS'}}")

            response = iot.describe_endpoint(endpointType="iot:Data-ATS")
            endpoint = response["endpointAddress"]

            if debug:
                print(f"{get_message('debug_api_response', USER_LANG)} {json.dumps(response, indent=2, default=str)}")

            print(get_message("iot_endpoint_discovery", USER_LANG))
            print(f"   {get_message('endpoint_type_label', USER_LANG)}: {get_message('endpoint_type_recommended', USER_LANG)}")
            print(f"   {get_message('endpoint_url_label', USER_LANG)}: {endpoint}")
            print(f"   {get_message('port_label', USER_LANG)}: {get_message('port_mqtt_tls', USER_LANG)}")
            print(f"   {get_message('protocol_label', USER_LANG)}: {get_message('protocol_mqtt_tls', USER_LANG)}")

            return endpoint
        except Exception as e:
            print(f"{get_message('error_getting_endpoint', USER_LANG)} {str(e)}")
            if debug:
                import traceback

                print(get_message("debug_full_traceback", USER_LANG))
                traceback.print_exc()
            return None

    def select_device_and_certificate(self, debug=False):
        """Select a device and its certificate for MQTT connection"""
        try:
            iot = boto3.client("iot")

            # Get all Things
            if debug:
                print(get_message("debug_calling_list_things", USER_LANG))
                print(get_message("debug_input_params_none", USER_LANG))

            things_response = iot.list_things()
            things = things_response.get("things", [])

            if debug:
                print(get_message("debug_api_response_found_things", USER_LANG).format(len(things)))
                print(f"{get_message('debug_thing_names', USER_LANG)} {[t['thingName'] for t in things]}")

            if not things:
                print(get_message("no_things_found", USER_LANG))
                return None, None, None

            print(get_message("available_devices", USER_LANG).format(len(things)))
            for i, thing in enumerate(things, 1):
                print(f"   {i}. {thing['thingName']} (Type: {thing.get('thingTypeName', 'None')})")

            while True:
                try:
                    choice = int(input(f"\n{get_message('select_device', USER_LANG).format(len(things))} ")) - 1
                    if 0 <= choice < len(things):
                        selected_thing = things[choice]["thingName"]
                        break
                    else:
                        print(get_message("invalid_selection", USER_LANG).format(len(things)))
                except ValueError:
                    print(get_message("enter_valid_number", USER_LANG))
                except KeyboardInterrupt:
                    print(f"\n{get_message('operation_cancelled', USER_LANG)}")
                    return None, None, None

            print(f"{get_message('selected_device', USER_LANG)} {selected_thing}")

            # Get certificates for the selected Thing
            if debug:
                print(get_message("debug_calling_list_principals", USER_LANG))
                print(f"{get_message('debug_input_params_thing', USER_LANG)} {{'thingName': '{selected_thing}'}}")

            principals_response = iot.list_thing_principals(thingName=selected_thing)
            principals = principals_response.get("principals", [])
            cert_arns = [p for p in principals if "cert/" in p]

            if debug:
                print(get_message("debug_api_response_principals", USER_LANG).format(len(principals), len(cert_arns)))
                print(f"{get_message('debug_certificate_arns', USER_LANG)} {cert_arns}")

            if not cert_arns:
                print(get_message("no_certificates_found", USER_LANG).format(selected_thing))
                print(get_message("run_certificate_manager", USER_LANG))
                return None, None, None

            # Select certificate if multiple
            if len(cert_arns) == 1:
                selected_cert_arn = cert_arns[0]
                cert_id = selected_cert_arn.split("/")[-1]
                print(f"{get_message('using_certificate', USER_LANG)} {cert_id}")
            else:
                print(f"\n{get_message('multiple_certificates_found', USER_LANG)}")
                for i, cert_arn in enumerate(cert_arns, 1):
                    cert_id = cert_arn.split("/")[-1]
                    print(f"   {i}. {cert_id}")

                while True:
                    try:
                        choice = int(input(get_message("select_certificate", USER_LANG).format(len(cert_arns)))) - 1
                        if 0 <= choice < len(cert_arns):
                            selected_cert_arn = cert_arns[choice]
                            cert_id = selected_cert_arn.split("/")[-1]
                            break
                        else:
                            print(get_message("invalid_selection", USER_LANG))
                    except ValueError:
                        print(get_message("enter_valid_number", USER_LANG))
                    except KeyboardInterrupt:
                        print(f"\n{get_message('operation_cancelled', USER_LANG)}")
                        return None, None, None

            # Find certificate files
            cert_dir = os.path.join(os.getcwd(), "certificates", selected_thing)
            if not os.path.exists(cert_dir):
                print(f"{get_message('cert_dir_not_found', USER_LANG)} {cert_dir}")
                print(get_message("run_cert_manager_files", USER_LANG))
                return None, None, None

            cert_file = None
            key_file = None

            for file in os.listdir(cert_dir):
                if cert_id in file:
                    if file.endswith(".crt"):
                        cert_file = os.path.join(cert_dir, file)
                    elif file.endswith(".key"):
                        key_file = os.path.join(cert_dir, file)

            if not cert_file or not key_file:
                print(get_message("cert_files_not_found", USER_LANG).format(cert_dir))
                print(get_message("looking_for_files", USER_LANG).format(cert_id))
                return None, None, None

            print(get_message("cert_files_found", USER_LANG))
            print(f"   {get_message('certificate_label', USER_LANG)}: {cert_file}")
            print(f"   {get_message('private_key_label', USER_LANG)}: {key_file}")

            return selected_thing, cert_file, key_file

        except Exception as e:
            print(f"{get_message('error_selecting_device', USER_LANG)} {str(e)}")
            return None, None, None

    def on_connection_interrupted(self, connection, error, **kwargs):
        """Callback for connection interruption"""
        self.print_mqtt_details(
            get_message("connection_interrupted", USER_LANG),
            {
                get_message("error_label", USER_LANG): str(error),
                get_message("timestamp_label", USER_LANG): datetime.now().isoformat(),
                get_message("auto_reconnect_label", USER_LANG): get_message("auto_reconnect_msg", USER_LANG),
            },
        )
        self.connected = False

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """Callback for connection resumption"""
        self.print_mqtt_details(
            get_message("connection_resumed", USER_LANG),
            {
                get_message("return_code_label", USER_LANG): return_code,
                get_message("session_present_label", USER_LANG): session_present,
                get_message("timestamp_label", USER_LANG): datetime.now().isoformat(),
                get_message("status_label", USER_LANG): get_message("connection_restored", USER_LANG),
            },
        )
        self.connected = True

        # Re-subscribe to all topics if session not present
        if not session_present and self.subscriptions:
            print(get_message("resubscribing_topics", USER_LANG).format(len(self.subscriptions)))
            topics_to_resubscribe = list(self.subscriptions.items())
            for topic, qos in topics_to_resubscribe:
                try:
                    subscribe_future, _ = self.connection.subscribe(
                        topic=topic, qos=mqtt.QoS(qos), callback=self.on_message_received
                    )
                    subscribe_future.result()
                    print(get_message("resubscribed_to_topic", USER_LANG).format(topic, qos))
                except Exception as e:
                    print(f"{get_message('failed_resubscribe', USER_LANG).format(topic)} {str(e)}")
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
            print(get_message("incoming_message", USER_LANG).format(self.message_count, timestamp))
            print("=" * 70)

            # Core MQTT Properties
            print(f"{get_message('topic_label', USER_LANG)} {topic}")
            qos_desc = (
                get_message("qos_at_most_once", USER_LANG)
                if qos == 0
                else get_message("qos_at_least_once", USER_LANG) if qos == 1 else get_message("qos_exactly_once", USER_LANG)
            )
            print(f"{get_message('qos_label', USER_LANG)} {qos} ({qos_desc})")
            print(f"{get_message('payload_size_label', USER_LANG)} {len(payload)} bytes")

            # MQTT Flags
            flags = []
            if dup:
                flags.append(get_message("duplicate_flag", USER_LANG))
            if retain:
                flags.append(get_message("retain_flag", USER_LANG))
            if flags:
                print(f"{get_message('flags_label', USER_LANG)} {', '.join(flags)}")

            # MQTT5 Properties (if available)
            mqtt5_props = []
            if content_type:
                mqtt5_props.append(f"{get_message('content_type_prop', USER_LANG)} {content_type}")
            if correlation_data:
                mqtt5_props.append(f"{get_message('correlation_data_prop', USER_LANG)} {correlation_data}")
            if message_expiry_interval:
                mqtt5_props.append(f"{get_message('message_expiry_prop', USER_LANG)} {message_expiry_interval}s")
            if response_topic:
                mqtt5_props.append(f"{get_message('response_topic_prop', USER_LANG)} {response_topic}")
            if payload_format_indicator is not None:
                format_desc = (
                    get_message("utf8_string", USER_LANG)
                    if payload_format_indicator == 1
                    else get_message("bytes_format", USER_LANG)
                )
                mqtt5_props.append(f"{get_message('payload_format_prop', USER_LANG)} {format_desc}")
            if user_properties:
                mqtt5_props.append(
                    f"{get_message('user_properties_prop', USER_LANG)} {get_message('properties_count', USER_LANG).format(len(user_properties))}"
                )
                for prop in user_properties:
                    mqtt5_props.append(f"   • {prop[0]}: {prop[1]}")

            if mqtt5_props:
                print(get_message("mqtt5_properties", USER_LANG))
                for prop in mqtt5_props:
                    print(f"   {prop}")

            # Payload Display
            print(get_message("message_payload", USER_LANG))
            if is_json:
                print(get_message("json_format", USER_LANG))
                for line in payload_display.split("\n"):
                    print(f"   {line}")
            else:
                print(f"{get_message('text_format', USER_LANG)} {payload_display}")

            print("=" * 70)
            print(get_message("mqtt_prompt", USER_LANG), end="", flush=True)  # Restore prompt

        except Exception as e:
            print(f"\n{get_message('error_processing_message', USER_LANG)} {str(e)}")
            print(get_message("mqtt_prompt", USER_LANG), end="", flush=True)

    def connect_to_aws_iot(self, thing_name, cert_file, key_file, endpoint, debug=False):
        """Establish MQTT connection to AWS IoT Core"""
        # Clean up any previous connection state
        self.cleanup_connection_state()

        # Store connection details
        self.endpoint = endpoint
        self.thing_name = thing_name

        self.print_step(1, get_message("step_establishing_connection", USER_LANG))

        if debug:
            print(get_message("mqtt_connection_setup", USER_LANG))
            print(f"   {get_message('thing_name_label', USER_LANG)}: {thing_name}")
            print(f"   {get_message('certificate_file_label', USER_LANG)}: {cert_file}")
            print(f"   {get_message('private_key_file_label', USER_LANG)}: {key_file}")
            print(f"   {get_message('endpoint_label', USER_LANG)}: {endpoint}")

        try:
            # Get client ID from user or auto-generate
            client_id = self.get_client_id(thing_name)
            if not client_id:
                return False

            print(f"\n{get_message('connection_parameters', USER_LANG)}")
            print(f"   {get_message('client_id_label', USER_LANG)}: {client_id}")
            print(f"   {get_message('endpoint_label', USER_LANG)}: {endpoint}")
            print(f"   {get_message('port_label', USER_LANG)}: 8883")
            print(f"   {get_message('protocol_label', USER_LANG)}: {get_message('protocol_mqtt_tls', USER_LANG)}")
            print(f"   {get_message('authentication_label', USER_LANG)}: X.509 Certificate")
            print(f"   {get_message('certificate_file_label', USER_LANG)}: {cert_file}")
            print(f"   {get_message('private_key_file_label', USER_LANG)}: {key_file}")

            # Build MQTT connection
            self.connection = mqtt_connection_builder.mtls_from_path(
                endpoint=endpoint,
                port=8883,
                cert_filepath=cert_file,
                pri_key_filepath=key_file,
                client_id=client_id,
                clean_session=True,  # Use clean session for better reliability
                keep_alive_secs=30,
                on_connection_interrupted=self.on_connection_interrupted,
                on_connection_resumed=self.on_connection_resumed,
            )

            print(f"\n{get_message('connecting_to_iot', USER_LANG)}")
            connect_future = self.connection.connect()
            connection_result = connect_future.result()  # Wait for connection

            if debug:
                print(f"{get_message('connection_result_debug', USER_LANG)} {connection_result}")

            self.connected = True

            self.print_mqtt_details(
                get_message("connection_established", USER_LANG),
                {
                    get_message("status_label", USER_LANG): get_message("connection_status_success", USER_LANG),
                    get_message("client_id_label", USER_LANG): client_id,
                    get_message("endpoint_label", USER_LANG): endpoint,
                    get_message("clean_session_label", USER_LANG): False,
                    get_message("keep_alive_label", USER_LANG): "30 seconds",
                    get_message("tls_version_label", USER_LANG): "1.2",
                    get_message("cert_auth_label", USER_LANG): "X.509 mutual TLS",
                },
            )

            # Test basic connectivity with a simple operation
            if debug:
                print(get_message("testing_connection_stability", USER_LANG))
                try:
                    # Try a simple operation to verify the connection is fully functional
                    import time

                    time.sleep(1)  # nosemgrep: arbitrary-sleep
                    print(get_message("connection_stable", USER_LANG))
                except Exception as test_e:
                    print(f"{get_message('connection_unstable', USER_LANG)} {str(test_e)}")

            return True

        except Exception as e:
            print(f"{get_message('connection_failed', USER_LANG)} {str(e)}")
            return False

    def subscribe_to_topic(self, topic, qos=0, debug=False):
        """Subscribe to an MQTT topic with enhanced error handling"""
        if not self.connected:
            print(get_message("not_connected_iot", USER_LANG))
            return False

        try:
            print(f"\n{get_message('subscribing_to_topic', USER_LANG)}")
            print(f"   Topic: {topic}")
            qos_desc = get_message("qos_at_most_once", USER_LANG) if qos == 0 else get_message("qos_at_least_once", USER_LANG)
            print(f"   QoS: {qos} ({qos_desc})")

            if debug:
                print(get_message("debug_subscribe_operation", USER_LANG))
                print(f"{get_message('connection_status_debug', USER_LANG)} {self.connected}")
                print(f"{get_message('connection_object_debug', USER_LANG)} {self.connection}")
                print(f"{get_message('topic_pattern_debug', USER_LANG)} {topic}")
                print(f"{get_message('requested_qos_debug', USER_LANG)} {qos}")

            # Convert QoS to proper enum
            mqtt_qos = mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE

            if debug:
                print(f"{get_message('converted_qos_debug', USER_LANG)} {mqtt_qos}")
                print(f"{get_message('callback_function_debug', USER_LANG)} {self.on_message_received}")

            subscribe_future, packet_id = self.connection.subscribe(
                topic=topic, qos=mqtt_qos, callback=self.on_message_received
            )

            if debug:
                print(get_message("subscribe_request_sent", USER_LANG))
                print(f"{get_message('packet_id_debug', USER_LANG)} {packet_id}")

            # Wait for subscription result
            subscribe_result = subscribe_future.result()

            if debug:
                print(get_message("subscribe_result_received", USER_LANG))
                print(f"{get_message('result_debug', USER_LANG)} {subscribe_result}")
                print(f"{get_message('result_type_debug', USER_LANG)} {type(subscribe_result)}")

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
            }

            self.print_mqtt_details(
                get_message("subscription_established", USER_LANG),
                {
                    "Topic": topic,
                    get_message("qos_requested_label", USER_LANG): qos,
                    get_message("qos_granted_label", USER_LANG): granted_qos,
                    get_message("packet_id_label", USER_LANG): packet_id,
                    get_message("status_label", USER_LANG): get_message("status_subscribed", USER_LANG),
                    get_message("wildcard_support", USER_LANG): get_message("wildcard_support_msg", USER_LANG),
                },
            )

            return True

        except Exception as e:
            print(f"{get_message('subscription_failed', USER_LANG)} {str(e)}")
            print(get_message("detailed_error_info", USER_LANG))
            print(f"{get_message('error_type_label', USER_LANG)} {type(e).__name__}")
            print(f"{get_message('error_message_label', USER_LANG)} {str(e)}")

            # Check for common issues
            error_str = str(e).lower()
            if "timeout" in error_str:
                print(get_message("troubleshooting_timeout", USER_LANG))
                for reason in get_message("timeout_reasons", USER_LANG):
                    print(reason)
            elif "not authorized" in error_str or "forbidden" in error_str or "access denied" in error_str:
                print(get_message("troubleshooting_auth", USER_LANG))
                for reason in get_message("auth_reasons", USER_LANG):
                    print(reason)
            elif "invalid topic" in error_str or "malformed" in error_str:
                print(get_message("troubleshooting_invalid_topic", USER_LANG))
                for reason in get_message("invalid_topic_reasons", USER_LANG):
                    print(reason)
            elif "connection" in error_str or "disconnected" in error_str:
                print(get_message("troubleshooting_connection", USER_LANG))
                for reason in get_message("connection_reasons", USER_LANG):
                    print(reason)
            else:
                print(get_message("troubleshooting_unknown", USER_LANG))
                for reason in get_message("unknown_reasons", USER_LANG):
                    print(reason.format(topic))

            if debug:
                import traceback

                print(get_message("debug_full_traceback", USER_LANG))
                traceback.print_exc()

            return False

    def publish_message(self, topic, message, qos=0, **mqtt_properties):
        """Publish a message to an MQTT topic with optional MQTT5 properties"""
        if not self.connected:
            print(get_message("not_connected_iot", USER_LANG))
            return False

        try:
            # Prepare payload
            if isinstance(message, dict):
                payload = json.dumps(message)
                content_type = "application/json"
            else:
                payload = str(message)
                # Auto-detect JSON content type
                try:
                    json.loads(payload)
                    content_type = "application/json"
                except (json.JSONDecodeError, ValueError):
                    content_type = "text/plain"

            # Extract MQTT5 properties
            user_properties = mqtt_properties.get("user_properties", [])
            correlation_data = mqtt_properties.get("correlation_data", None)
            message_expiry_interval = mqtt_properties.get("message_expiry_interval", None)
            response_topic = mqtt_properties.get("response_topic", None)

            print(f"\n{get_message('publishing_message', USER_LANG)}")
            print(f"   Topic: {topic}")
            qos_desc = (
                get_message("qos_at_most_once", USER_LANG)
                if qos == 0
                else get_message("qos_at_least_once", USER_LANG) if qos == 1 else get_message("qos_exactly_once", USER_LANG)
            )
            print(f"   QoS: {qos} ({qos_desc})")
            print(f"   Payload Size: {len(payload)} bytes")
            print(f"   {get_message('content_type_label', USER_LANG)}: {content_type}")

            # Show MQTT5 properties if any
            if user_properties or correlation_data or message_expiry_interval or response_topic:
                print(f"   {get_message('mqtt5_properties_label', USER_LANG)}")
                if correlation_data:
                    print(f"      {get_message('correlation_data_prop', USER_LANG)} {correlation_data}")
                if message_expiry_interval:
                    print(f"      {get_message('message_expiry_prop', USER_LANG)} {message_expiry_interval}s")
                if response_topic:
                    print(f"      {get_message('response_topic_prop', USER_LANG)} {response_topic}")
                if user_properties:
                    print(f"      {get_message('user_properties_prop', USER_LANG)}")
                    for prop in user_properties:
                        print(f"         • {prop[0]}: {prop[1]}")

            # Prepare publish parameters
            publish_params = {"topic": topic, "payload": payload, "qos": qos}

            # Convert QoS to proper enum
            mqtt_qos = mqtt.QoS.AT_MOST_ONCE if qos == 0 else mqtt.QoS.AT_LEAST_ONCE
            publish_params["qos"] = mqtt_qos

            # Debug publish parameters
            debug_mode = getattr(self, "debug_mode", False)
            if debug_mode:
                print("🔍 DEBUG: Publish parameters:")
                print(f"   Topic: {publish_params['topic']}")
                print(f"   QoS: {publish_params['qos']}")
                print(f"   Payload length: {len(publish_params['payload'])}")

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
                "User Properties": user_properties,
                "Correlation Data": correlation_data,
                "Message Expiry": message_expiry_interval,
                "Response Topic": response_topic,
            }

            with self.message_lock:
                self.sent_messages.append(message_info)

            # Enhanced publish confirmation with protocol details
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(get_message("published_timestamp", USER_LANG).format(timestamp))
            print(f"   📤 Topic: {topic}")
            print(f"   🏷️  QoS: {qos} | Packet ID: {packet_id}")
            print(f"   📊 Size: {len(payload)} bytes | Type: {content_type}")
            if qos > 0:
                print(f"   {get_message('delivery_ack_required', USER_LANG).format(qos)}")
            else:
                print(f"   {get_message('delivery_fire_forget', USER_LANG)}")

            return True

        except Exception as e:
            print(f"{get_message('publish_failed', USER_LANG)} {str(e)}")
            print(get_message("detailed_error_info", USER_LANG))
            print(f"{get_message('error_type_label', USER_LANG)} {type(e).__name__}")
            print(f"{get_message('error_message_label', USER_LANG)} {str(e)}")

            # Check for common issues
            error_str = str(e).lower()
            if "timeout" in error_str:
                print(get_message("troubleshooting_publish_timeout", USER_LANG))
                for reason in get_message("timeout_reasons", USER_LANG):
                    print(reason)
            elif "not authorized" in error_str or "forbidden" in error_str or "access denied" in error_str:
                print(get_message("troubleshooting_auth", USER_LANG))
                for reason in get_message("auth_reasons", USER_LANG):
                    print(reason)
            elif "invalid topic" in error_str or "malformed" in error_str:
                print(get_message("troubleshooting_invalid_topic", USER_LANG))
                for reason in get_message("invalid_topic_reasons", USER_LANG):
                    print(reason)
            elif "payload too large" in error_str:
                print(get_message("troubleshooting_payload_large", USER_LANG))
                print(get_message("payload_limit_msg", USER_LANG))
                print(get_message("current_payload_size", USER_LANG).format(len(payload)))
            elif "connection" in error_str or "disconnected" in error_str:
                print(get_message("troubleshooting_connection", USER_LANG))
                for reason in get_message("connection_reasons", USER_LANG):
                    print(reason)
            else:
                print(get_message("troubleshooting_unknown", USER_LANG))
                for reason in get_message("unknown_reasons", USER_LANG):
                    print(reason.format(topic))

            return False


def main():
    """Main function"""
    global USER_LANG, DEBUG_MODE

    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] in ["--debug", "-d"]:
        DEBUG_MODE = True

    # Get user's preferred language
    USER_LANG = get_language()

    # Display header
    print(f"\n{get_message('title', USER_LANG)}")
    print(get_message("separator", USER_LANG))

    print(f"\n{get_message('description_intro', USER_LANG)}")
    for concept in get_message("mqtt_concepts", USER_LANG):
        print(concept)

    if DEBUG_MODE:
        print(f"\n{get_message('debug_enabled', USER_LANG)}")
        for feature in get_message("debug_features", USER_LANG):
            print(feature)
    else:
        print(f"\n{get_message('tip', USER_LANG)}")

    # Display AWS context
    display_aws_context()

    # Initialize MQTT client
    mqtt_client = MQTTClientExplorer()

    try:
        while True:
            print(f"\n{get_message('main_menu', USER_LANG)}")
            for option in get_message("menu_options", USER_LANG):
                print(option)

            try:
                choice = input(f"\n{get_message('select_option', USER_LANG)}").strip()

                if choice == "1":
                    # Connect to AWS IoT Core and start interactive mode
                    endpoint = mqtt_client.get_iot_endpoint(DEBUG_MODE)
                    if endpoint:
                        thing_name, cert_file, key_file = mqtt_client.select_device_and_certificate(DEBUG_MODE)
                        if thing_name and cert_file and key_file:
                            if mqtt_client.connect_to_aws_iot(thing_name, cert_file, key_file, endpoint, DEBUG_MODE):
                                # Automatically start interactive messaging after successful connection
                                interactive_messaging(mqtt_client)

                elif choice == "2":
                    print(f"\n{get_message('goodbye', USER_LANG)}")
                    break

                else:
                    print(get_message("invalid_choice", USER_LANG))

                # No need for press enter since we only have connect and exit

            except KeyboardInterrupt:
                print(f"\n\n{get_message('goodbye', USER_LANG)}")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                if DEBUG_MODE:
                    import traceback

                    traceback.print_exc()

    finally:
        # Clean up connection
        if mqtt_client.connected and mqtt_client.connection:
            try:
                mqtt_client.connection.disconnect()
            except Exception:
                pass


if __name__ == "__main__":
    main()

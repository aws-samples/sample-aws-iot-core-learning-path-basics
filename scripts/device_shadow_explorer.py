#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT Device Shadow Explorer
Educational tool for learning AWS IoT Device Shadow service through hands-on exploration.
"""
import json
import os
import re
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
        "title": "🌟 AWS IoT Device Shadow Explorer",
        "separator": "=" * 60,
        "aws_context_info": "🌍 AWS Context Information:",
        "account_id": "Account ID",
        "region": "Region",
        "aws_context_error": "⚠️ Could not retrieve AWS context:",
        "aws_credentials_reminder": "   Make sure AWS credentials are configured",
        "description_intro": "This script teaches you AWS IoT Device Shadow concepts:",
        "shadow_concepts": [
            "• Device Shadow service for state synchronization",
            "• Shadow document structure (desired vs reported)",
            "• MQTT topics for shadow operations",
            "• Delta messages for state differences",
            "• Real-time shadow updates and notifications",
            "• Complete API details for each operation",
        ],
        "debug_enabled": "🔍 DEBUG MODE ENABLED",
        "debug_features": [
            "• Enhanced MQTT message logging",
            "• Full shadow document analysis",
            "• Extended educational information",
        ],
        "tip": "💡 Tip: Use --debug or -d flag for enhanced shadow logging",
        "press_enter": "Press Enter to continue...",
        "goodbye": "👋 Goodbye!",
        "main_menu": "📋 Device Shadow Operations:",
        "menu_options": [
            "1. Connect to Device & Subscribe to Shadow Topics",
            "2. Get Current Shadow Document",
            "3. Update Shadow Reported State (Device → Cloud)",
            "4. Update Shadow Desired State (Cloud → Device)",
            "5. Simulate Device State Changes",
            "6. View Shadow Message History",
            "7. Disconnect and Exit",
        ],
        "select_option": "Select option (1-7): ",
        "invalid_choice": "❌ Invalid choice. Please select 1-7.",
        "learning_moments": {
            "shadow_foundation": {
                "title": "📚 LEARNING MOMENT: Device Shadow Foundation",
                "content": "AWS IoT Device Shadow is a JSON document that stores and retrieves current state information for a device. The shadow acts as an intermediary between devices and applications, enabling reliable communication even when devices are offline. Understanding shadow concepts is essential for building robust IoT applications.",
                "next": "We will explore shadow operations and MQTT communication",
            },
            "shadow_connection": {
                "title": "📚 LEARNING MOMENT: Shadow MQTT Connection",
                "content": "Device Shadows use MQTT topics for communication. Each shadow operation (get, update, delete) has corresponding accepted/rejected response topics. Delta topics notify when desired state differs from reported state. This pub/sub model enables real-time, bidirectional communication between devices and applications.",
                "next": "We will establish MQTT connection and subscribe to shadow topics",
            },
            "shadow_document": {
                "title": "📚 LEARNING MOMENT: Shadow Document Structure",
                "content": "A shadow document contains 'desired' and 'reported' states. Desired state represents what the device should be, typically set by applications. Reported state represents the device's current state. When these differ, AWS IoT generates delta messages to notify the device of required changes.",
                "next": "We will retrieve and analyze the current shadow document",
            },
            "reported_state": {
                "title": "📚 LEARNING MOMENT: Reported State Updates",
                "content": "Devices update their reported state to inform the cloud of their current status. This is typically done after the device changes its physical state (temperature, status, etc.). Reported state updates help keep the shadow synchronized with the actual device state.",
                "next": "We will update the shadow's reported state from device",
            },
            "desired_state": {
                "title": "📚 LEARNING MOMENT: Desired State Updates",
                "content": "Applications set the desired state to request device changes. When desired state differs from reported state, AWS IoT sends delta messages to the device. This mechanism enables remote device control and configuration management through the cloud.",
                "next": "We will update the shadow's desired state from cloud",
            },
            "state_simulation": {
                "title": "📚 LEARNING MOMENT: Device State Simulation",
                "content": "Simulating device state changes helps understand the complete shadow workflow. We'll modify local device state and see how it propagates through the shadow service. This demonstrates the bidirectional nature of shadow communication and state synchronization.",
                "next": "We will simulate realistic device state changes",
            },
        },
        "workflow_titles": {
            "shadow_connection": "🔗 Shadow Connection Workflow",
            "shadow_retrieval": "📥 Shadow Document Retrieval",
            "reported_update": "📡 Reported State Update",
            "desired_update": "🎯 Desired State Update",
            "state_simulation": "🔄 Device State Simulation",
            "message_history": "📜 Shadow Message History",
        },
        "step_establishing_connection": "Establishing MQTT Connection for Shadow Operations",
        "step_subscribing_topics": "Subscribing to Shadow Topics",
        "step_requesting_shadow": "Requesting Shadow Document",
        "step_updating_reported": "Updating Reported State",
        "step_updating_desired": "Updating Desired State",
        "step_simulating_changes": "Simulating Device Changes",
        "shadow_connection_params": "🔗 Shadow Connection Parameters:",
        "client_id": "Client ID",
        "thing_name": "Thing Name",
        "endpoint": "Endpoint",
        "port": "Port",
        "protocol": "Protocol",
        "authentication": "Authentication",
        "shadow_type": "Shadow Type",
        "connecting_to_iot": "🔄 Connecting to AWS IoT Core...",
        "connection_established": "SHADOW CONNECTION ESTABLISHED",
        "connection_status": "Successfully connected to AWS IoT Core",
        "clean_session": "Clean Session",
        "keep_alive": "Keep Alive",
        "tls_version": "TLS Version",
        "certificate_auth": "Certificate Authentication",
        "shadow_connection_failed": "❌ Shadow connection failed:",
        "not_connected": "❌ Not connected to AWS IoT Core",
        "shadow_topics_for_thing": "🌟 Shadow Topics for Thing:",
        "classic_shadow_topics": "📋 Classic Shadow Topics:",
        "subscription_successful": "✅ Successfully subscribed to all {} shadow topics",
        "subscription_partial": "⚠️  Only {}/{} subscriptions successful",
        "shadow_topic_explanations": "📖 Shadow Topic Explanations:",
        "topic_get_accepted": "• get/accepted - Shadow document retrieval success",
        "topic_get_rejected": "• get/rejected - Shadow document retrieval failure",
        "topic_update_accepted": "• update/accepted - Shadow update success",
        "topic_update_rejected": "• update/rejected - Shadow update failure",
        "topic_update_delta": "• update/delta - Desired ≠ Reported (action needed)",
        "requesting_shadow_document": "📥 Requesting Shadow Document",
        "topic": "Topic",
        "thing": "Thing",
        "shadow_type_classic": "Classic",
        "shadow_get_request_sent": "✅ Shadow GET request sent",
        "qos": "QoS",
        "packet_id": "Packet ID",
        "waiting_for_response": "⏳ Waiting for response on get/accepted or get/rejected...",
        "failed_request_shadow": "❌ Failed to request shadow document:",
        "shadow_message_received": "🌟 SHADOW MESSAGE RECEIVED",
        "direction": "Direction",
        "received": "RECEIVED",
        "payload_size": "Payload Size",
        "timestamp": "Timestamp",
        "shadow_data": "Shadow Data",
        "error_processing_message": "❌ Error processing shadow message:",
        "shadow_get_accepted": "✅ SHADOW GET ACCEPTED",
        "shadow_document_retrieved": "📋 Shadow Document Retrieved:",
        "version": "Version",
        "desired_state": "Desired State",
        "reported_state": "Reported State",
        "none": "None",
        "shadow_get_rejected": "❌ SHADOW GET REJECTED",
        "error_code": "Error Code",
        "message": "Message",
        "shadow_doesnt_exist": "Shadow doesn't exist yet - will create one on next update",
        "checking_shadow_exists": "Checking if shadow exists for {}...",
        "shadow_creation_normal": "This is normal for new devices - we'll create the shadow by reporting initial state",
        "creating_initial_shadow": "Shadow doesn't exist yet. Creating initial shadow...",
        "initial_shadow_created": "Initial shadow created successfully!",
        "retrieving_new_shadow": "Retrieving newly created shadow...",
        "shadow_already_exists": "Shadow already exists",
        "shadow_update_accepted": "✅ SHADOW UPDATE ACCEPTED",
        "new_version": "New Version",
        "updated_desired": "Updated Desired",
        "updated_reported": "Updated Reported",
        "shadow_update_rejected": "❌ SHADOW UPDATE REJECTED",
        "shadow_delta_received": "🔄 SHADOW DELTA RECEIVED",
        "description": "Description",
        "desired_differs_reported": "Desired state differs from reported state",
        "changes_needed": "Changes Needed",
        "state_comparison": "🔍 State Comparison:",
        "local_state": "Local State",
        "delta": "Delta",
        "desired": "Desired",
        "differences_found": "⚠️  Differences Found:",
        "apply_changes_prompt": "Apply these changes to local device? (y/N): ",
        "local_state_updated": "✅ Local state updated successfully",
        "failed_update_local": "❌ Failed to update local state",
        "changes_not_applied": "⏭️  Changes not applied to local device",
        "local_matches_desired": "✅ Local state matches desired state - no changes needed",
        "automatically_reporting": "📡 Automatically reporting updated state to shadow...",
        "local_state_saved": "💾 Local state saved to:",
        "created_default_state": "📄 Created default local state file:",
        "default_state": "📊 Default state:",
        "using_existing_state": "📄 Using existing local state file:",
        "current_local_state": "📊 Current local state:",
        "local_state_not_found": "❌ Local state file not found:",
        "invalid_json_state": "❌ Invalid JSON in state file:",
        "permission_denied_state": "❌ Permission denied accessing state file:",
        "unexpected_error_loading": "❌ Unexpected error loading local state:",
        "permission_denied_writing": "❌ Permission denied writing to state file:",
        "filesystem_error_saving": "❌ File system error saving state:",
        "invalid_state_data": "❌ Invalid state data type:",
        "unexpected_error_saving": "❌ Unexpected error saving local state:",
        "connection_interrupted": "CONNECTION INTERRUPTED",
        "error": "Error",
        "auto_reconnect": "Auto Reconnect",
        "sdk_will_reconnect": "AWS IoT SDK will attempt to reconnect automatically",
        "connection_resumed": "CONNECTION RESUMED",
        "return_code": "Return Code",
        "session_present": "Session Present",
        "status": "Status",
        "connection_restored": "Connection restored successfully",
        "iot_endpoint_discovery": "🌐 AWS IoT Endpoint Discovery",
        "endpoint_type": "Endpoint Type",
        "endpoint_type_ats": "iot:Data-ATS (recommended)",
        "endpoint_url": "Endpoint URL",
        "port_mqtt_tls": "Port: 8883 (MQTT over TLS)",
        "protocol_mqtt": "Protocol: MQTT 3.1.1 over TLS",
        "error_getting_endpoint": "❌ Error getting IoT endpoint:",
        "available_devices": "📱 Available Devices ({} found):",
        "type": "Type",
        "selected_device": "✅ Selected device:",
        "invalid_selection": "❌ Invalid selection. Please enter 1-{}",
        "enter_valid_number": "❌ Please enter a valid number",
        "operation_cancelled": "🛑 Operation cancelled",
        "no_things_found": "❌ No Things found. Please run setup_sample_data.py first",
        "error_selecting_device": "❌ Error selecting device:",
        "no_certificates_found": "❌ No certificates found for device '{}'",
        "run_certificate_manager": "💡 Run certificate_manager.py to create and attach a certificate",
        "using_certificate": "✅ Using certificate:",
        "multiple_certificates_found": "🔐 Multiple certificates found:",
        "select_certificate": "Select certificate (1-{}): ",
        "invalid_selection_cert": "❌ Invalid selection",
        "certificate_files_found": "✅ Certificate files found:",
        "certificate": "Certificate",
        "private_key": "Private Key",
        "cert_dir_not_found": "❌ Certificate directory not found:",
        "run_cert_manager_files": "💡 Run certificate_manager.py to create certificate files",
        "cert_files_not_found": "❌ Certificate files not found in {}",
        "looking_for_files": "Looking for: {}.crt and {}.key",
        "invalid_thing_name": "⚠️ Invalid thing name:",
        "unsafe_path_detected": "⚠️ Unsafe path detected:",
        "updating_shadow_reported": "📡 Updating Shadow Reported State",
        "reported_state_update": "📊 Reported State Update:",
        "current_local_state_label": "Current Local State",
        "shadow_update_payload": "Shadow Update Payload",
        "shadow_update_sent": "✅ Shadow UPDATE (reported) sent",
        "failed_update_reported": "❌ Failed to update reported state:",
        "updating_shadow_desired": "🎯 Updating Shadow Desired State",
        "desired_state_update": "📊 Desired State Update:",
        "enter_property_name": "Enter property name: ",
        "property_name_required": "❌ Property name is required",
        "enter_property_value": "Enter property value: ",
        "property_value_required": "❌ Property value is required",
        "desired_state_to_set": "Desired State to Set",
        "property": "Property",
        "value": "Value",
        "shadow_update_desired_sent": "✅ Shadow UPDATE (desired) sent",
        "failed_update_desired": "❌ Failed to update desired state:",
        "simulating_device_changes": "🔄 Simulating Device State Changes",
        "simulation_options": "📋 Simulation Options:",
        "temperature_change": "1. Temperature change (±5°C)",
        "humidity_change": "2. Humidity change (±10%)",
        "status_toggle": "3. Status toggle (online/offline)",
        "firmware_update": "4. Firmware version update",
        "custom_property": "5. Custom property change",
        "select_simulation": "Select simulation (1-5): ",
        "invalid_simulation": "❌ Invalid selection. Please select 1-5.",
        "temperature_changed": "🌡️  Temperature changed: {} → {}°C",
        "humidity_changed": "💧 Humidity changed: {} → {}%",
        "status_changed": "🔄 Status changed: {} → {}",
        "firmware_updated": "🔧 Firmware updated: {} → {}",
        "custom_property_changed": "🔧 Custom property '{}' changed: {} → {}",
        "state_change_summary": "📊 State Change Summary:",
        "previous_value": "Previous Value",
        "new_value": "New Value",
        "local_state_updated_sim": "💾 Local state updated and saved",
        "reporting_to_shadow": "📡 Reporting change to shadow...",
        "simulation_complete": "✅ Simulation complete",
        "viewing_message_history": "📜 Viewing Shadow Message History",
        "message_history": "📊 Shadow Message History ({} messages):",
        "no_messages_received": "📭 No shadow messages received yet",
        "try_other_operations": "💡 Try other operations first to generate shadow messages",
        "message_details": "Message Details:",
        "clear_history_prompt": "Clear message history? (y/N): ",
        "history_cleared": "🗑️  Message history cleared",
        "history_not_cleared": "📜 Message history preserved",
        "disconnecting_from_iot": "🔌 Disconnecting from AWS IoT Core...",
        "disconnection_complete": "✅ Disconnection complete",
        "session_summary": "📊 Session Summary:",
        "total_messages": "Total Messages Received",
        "connection_duration": "Connection Duration",
        "shadow_operations": "Shadow Operations Performed",
        "thank_you_message": "Thank you for exploring AWS IoT Device Shadows!",
        "next_steps_suggestions": "🔍 Next Steps:",
        "explore_iot_rules": "• Explore iot_rules_explorer.py for message processing",
        "try_mqtt_client": "• Try mqtt_client_explorer.py for direct MQTT communication",
        "check_registry": "• Use iot_registry_explorer.py to view device details",
        "edit_local_state_title": "📝 Local State Editor",
        "current_state": "Current state:",
        "options": "Options:",
        "edit_individual_values": "1. Edit individual values",
        "replace_entire_state": "2. Replace entire state with JSON",
        "cancel": "3. Cancel",
        "select_option_1_3": "Select option (1-3): ",
        "current_values": "Current values:",
        "add_new_key": "Add new key",
        "done_editing": "Done editing",
        "select_item_to_edit": "Select item to edit (1-{}): ",
        "editing_key": "Editing '{}' (current: {})",
        "new_value_prompt": "New value (or press Enter to keep current): ",
        "updated_key": "✅ Updated {} = {}",
        "new_key_name": "New key name: ",
        "value_for_key": "Value for '{}': ",
        "added_new_key": "✅ Added new key: {} = {}",
        "enter_json_prompt": "Enter your JSON state (press Enter twice when done):",
        "invalid_json": "❌ Invalid JSON: {}",
        "state_updated_from_json": "✅ State updated from JSON",
        "report_updated_state": "Report updated state to shadow? (y/N): ",
        "shadow_command_prompt": "🌟 Shadow> ",
        "available_commands": "📖 Available Commands:",
        "get_command": "   get                       - Request shadow document",
        "local_command": "   local                     - Show local device state",
        "edit_command": "   edit                      - Edit local device state",
        "report_command": "   report                    - Report local state to shadow",
        "desire_command": "   desire key=val [key=val]  - Set desired state",
        "status_command": "   status                    - Connection status",
        "messages_command": "   messages                  - Shadow message history",
        "debug_command": "   debug                     - Connection diagnostics",
        "quit_command": "   quit                      - Exit",
        "example_desire": "💡 Example: desire temperature=25.0 status=active",
        "current_local_device_state": "📱 Current Local Device State:",
        "usage_desire": "❌ Usage: desire key=value [key=value...]",
        "example_desire_usage": "💡 Example: desire temperature=25.0 status=active",
        "setting_desired_state": "🎯 Setting desired state: {}",
        "no_valid_pairs": "❌ No valid key=value pairs found",
        "shadow_connection_status": "📊 Shadow Connection Status:",
        "connected": "Connected",
        "yes": "✅ Yes",
        "no": "❌ No",
        "shadow_message_history": "📨 Shadow Message History:",
        "unknown_command": "❌ Unknown command: {}. Type 'help' for available commands.",
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
        "title": "🌟 Explorador de Device Shadow de AWS IoT",
        "separator": "=" * 60,
        "aws_context_info": "🌍 Información de Contexto de AWS:",
        "account_id": "ID de Cuenta",
        "region": "Región",
        "aws_context_error": "⚠️ No se pudo recuperar el contexto de AWS:",
        "aws_credentials_reminder": "   Asegúrate de que las credenciales de AWS estén configuradas",
        "description_intro": "Este script te enseña conceptos de AWS IoT Device Shadow:",
        "shadow_concepts": [
            "• Servicio Device Shadow para sincronización de estado",
            "• Estructura del documento Shadow (deseado vs reportado)",
            "• Tópicos MQTT para operaciones de shadow",
            "• Mensajes delta para diferencias de estado",
            "• Actualizaciones de shadow en tiempo real y notificaciones",
            "• Detalles completos de API para cada operación",
        ],
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Registro mejorado de mensajes MQTT",
            "• Análisis completo de documentos shadow",
            "• Información educativa extendida",
        ],
        "tip": "💡 Consejo: Usa la bandera --debug o -d para registro mejorado de shadow",
        "press_enter": "Presiona Enter para continuar...",
        "goodbye": "👋 ¡Adiós!",
        "main_menu": "📋 Operaciones de Device Shadow:",
        "menu_options": [
            "1. Conectar a Dispositivo y Suscribirse a Tópicos Shadow",
            "2. Obtener Documento Shadow Actual",
            "3. Actualizar Estado Reportado del Shadow (Dispositivo → Nube)",
            "4. Actualizar Estado Deseado del Shadow (Nube → Dispositivo)",
            "5. Simular Cambios de Estado del Dispositivo",
            "6. Ver Historial de Mensajes Shadow",
            "7. Desconectar y Salir",
        ],
        "select_option": "Seleccionar opción (1-7): ",
        "invalid_choice": "❌ Selección inválida. Por favor selecciona 1-7.",
        "learning_moments": {
            "shadow_foundation": {
                "title": "📚 LEARNING MOMENT: Fundamentos de Device Shadow",
                "content": "AWS IoT Device Shadow es un documento JSON que almacena y recupera información del estado actual de un dispositivo. El shadow actúa como intermediario entre dispositivos y aplicaciones, permitiendo comunicación confiable incluso cuando los dispositivos están desconectados. Entender los conceptos de shadow es esencial para construir aplicaciones IoT robustas.",
                "next": "Exploraremos operaciones de shadow y comunicación MQTT",
            },
            "shadow_connection": {
                "title": "📚 LEARNING MOMENT: Conexión MQTT de Shadow",
                "content": "Los Device Shadows usan tópicos MQTT para comunicación. Cada operación de shadow (get, update, delete) tiene tópicos de respuesta correspondientes accepted/rejected. Los tópicos delta notifican cuando el estado deseado difiere del reportado. Este modelo pub/sub permite comunicación bidireccional en tiempo real entre dispositivos y aplicaciones.",
                "next": "Estableceremos conexión MQTT y nos suscribiremos a tópicos shadow",
            },
            "shadow_document": {
                "title": "📚 LEARNING MOMENT: Estructura del Documento Shadow",
                "content": "Un documento shadow contiene estados 'desired' y 'reported'. El estado deseado representa lo que el dispositivo debería ser, típicamente establecido por aplicaciones. El estado reportado representa el estado actual del dispositivo. Cuando estos difieren, AWS IoT genera mensajes delta para notificar al dispositivo de los cambios requeridos.",
                "next": "Recuperaremos y analizaremos el documento shadow actual",
            },
            "reported_state": {
                "title": "📚 LEARNING MOMENT: Actualizaciones de Estado Reportado",
                "content": "Los dispositivos actualizan su estado reportado para informar a la nube de su estado actual. Esto se hace típicamente después de que el dispositivo cambia su estado físico (temperatura, estado, etc.). Las actualizaciones de estado reportado ayudan a mantener el shadow sincronizado con el estado real del dispositivo.",
                "next": "Actualizaremos el estado reportado del shadow desde el dispositivo",
            },
            "desired_state": {
                "title": "📚 LEARNING MOMENT: Actualizaciones de Estado Deseado",
                "content": "Las aplicaciones establecen el estado deseado para solicitar cambios en el dispositivo. Cuando el estado deseado difiere del reportado, AWS IoT envía mensajes delta al dispositivo. Este mecanismo permite control remoto de dispositivos y gestión de configuración a través de la nube.",
                "next": "Actualizaremos el estado deseado del shadow desde la nube",
            },
            "state_simulation": {
                "title": "📚 LEARNING MOMENT: Simulación de Estado del Dispositivo",
                "content": "Simular cambios de estado del dispositivo ayuda a entender el flujo completo del shadow. Modificaremos el estado local del dispositivo y veremos cómo se propaga a través del servicio shadow. Esto demuestra la naturaleza bidireccional de la comunicación shadow y sincronización de estado.",
                "next": "Simularemos cambios realistas de estado del dispositivo",
            },
        },
        "workflow_titles": {
            "shadow_connection": "🔗 Flujo de Conexión Shadow",
            "shadow_retrieval": "📥 Recuperación de Documento Shadow",
            "reported_update": "📡 Actualización de Estado Reportado",
            "desired_update": "🎯 Actualización de Estado Deseado",
            "state_simulation": "🔄 Simulación de Estado del Dispositivo",
            "message_history": "📜 Historial de Mensajes Shadow",
        },
        "step_establishing_connection": "Estableciendo Conexión MQTT para Operaciones Shadow",
        "step_subscribing_topics": "Suscribiéndose a Tópicos Shadow",
        "step_requesting_shadow": "Solicitando Documento Shadow",
        "step_updating_reported": "Actualizando Estado Reportado",
        "step_updating_desired": "Actualizando Estado Deseado",
        "step_simulating_changes": "Simulando Cambios del Dispositivo",
        "shadow_connection_params": "🔗 Parámetros de Conexión Shadow:",
        "client_id": "ID de Cliente",
        "thing_name": "Nombre del Thing",
        "endpoint": "Endpoint",
        "port": "Puerto",
        "protocol": "Protocolo",
        "authentication": "Autenticación",
        "shadow_type": "Tipo de Shadow",
        "connecting_to_iot": "🔄 Conectando a AWS IoT Core...",
        "connection_established": "CONEXIÓN SHADOW ESTABLECIDA",
        "connection_status": "Conectado exitosamente a AWS IoT Core",
        "clean_session": "Sesión Limpia",
        "keep_alive": "Keep Alive",
        "tls_version": "Versión TLS",
        "certificate_auth": "Autenticación por Certificado",
        "shadow_connection_failed": "❌ Falló la conexión shadow:",
        "not_connected": "❌ No conectado a AWS IoT Core",
        "shadow_topics_for_thing": "🌟 Tópicos Shadow para Thing:",
        "classic_shadow_topics": "📋 Tópicos Shadow Clásicos:",
        "subscription_successful": "✅ Suscrito exitosamente a todos los {} tópicos shadow",
        "subscription_partial": "⚠️  Solo {}/{} suscripciones exitosas",
        "shadow_topic_explanations": "📖 Explicaciones de Tópicos Shadow:",
        "topic_get_accepted": "• get/accepted - Recuperación exitosa de documento shadow",
        "topic_get_rejected": "• get/rejected - Fallo en recuperación de documento shadow",
        "topic_update_accepted": "• update/accepted - Actualización exitosa de shadow",
        "topic_update_rejected": "• update/rejected - Fallo en actualización de shadow",
        "topic_update_delta": "• update/delta - Deseado ≠ Reportado (acción necesaria)",
        "requesting_shadow_document": "📥 Solicitando Documento Shadow",
        "topic": "Tópico",
        "thing": "Thing",
        "shadow_type_classic": "Clásico",
        "shadow_get_request_sent": "✅ Solicitud GET de shadow enviada",
        "qos": "QoS",
        "packet_id": "ID de Paquete",
        "waiting_for_response": "⏳ Esperando respuesta en get/accepted o get/rejected...",
        "failed_request_shadow": "❌ Falló la solicitud de documento shadow:",
        "shadow_message_received": "🌟 MENSAJE SHADOW RECIBIDO",
        "direction": "Dirección",
        "received": "RECIBIDO",
        "payload_size": "Tamaño de Payload",
        "timestamp": "Marca de Tiempo",
        "shadow_data": "Datos Shadow",
        "error_processing_message": "❌ Error procesando mensaje shadow:",
        "shadow_get_accepted": "✅ SHADOW GET ACEPTADO",
        "shadow_document_retrieved": "📋 Documento Shadow Recuperado:",
        "version": "Versión",
        "desired_state": "Estado Deseado",
        "reported_state": "Estado Reportado",
        "none": "Ninguno",
        "shadow_get_rejected": "❌ SHADOW GET RECHAZADO",
        "error_code": "Código de Error",
        "message": "Mensaje",
        "shadow_doesnt_exist": "El shadow no existe aún - se creará uno en la próxima actualización",
        "checking_shadow_exists": "Verificando si existe shadow para {}...",
        "shadow_creation_normal": "Esto es normal para dispositivos nuevos - crearemos el shadow reportando el estado inicial",
        "creating_initial_shadow": "El shadow no existe aún. Creando shadow inicial...",
        "initial_shadow_created": "¡Shadow inicial creado exitosamente!",
        "retrieving_new_shadow": "Recuperando shadow recién creado...",
        "shadow_already_exists": "El shadow ya existe",
        "shadow_update_accepted": "✅ ACTUALIZACIÓN SHADOW ACEPTADA",
        "new_version": "Nueva Versión",
        "updated_desired": "Deseado Actualizado",
        "updated_reported": "Reportado Actualizado",
        "shadow_update_rejected": "❌ ACTUALIZACIÓN SHADOW RECHAZADA",
        "shadow_delta_received": "🔄 DELTA SHADOW RECIBIDO",
        "description": "Descripción",
        "desired_differs_reported": "El estado deseado difiere del estado reportado",
        "changes_needed": "Cambios Necesarios",
        "state_comparison": "🔍 Comparación de Estado:",
        "local_state": "Estado Local",
        "delta": "Delta",
        "desired": "Deseado",
        "differences_found": "⚠️  Diferencias Encontradas:",
        "apply_changes_prompt": "¿Aplicar estos cambios al dispositivo local? (y/N): ",
        "local_state_updated": "✅ Estado local actualizado exitosamente",
        "failed_update_local": "❌ Falló la actualización del estado local",
        "changes_not_applied": "⏭️  Cambios no aplicados al dispositivo local",
        "local_matches_desired": "✅ El estado local coincide con el estado deseado - no se necesitan cambios",
        "automatically_reporting": "📡 Reportando automáticamente estado actualizado al shadow...",
        "local_state_saved": "💾 Estado local guardado en:",
        "created_default_state": "📄 Archivo de estado local por defecto creado:",
        "default_state": "📊 Estado por defecto:",
        "using_existing_state": "📄 Usando archivo de estado local existente:",
        "current_local_state": "📊 Estado local actual:",
        "local_state_not_found": "❌ Archivo de estado local no encontrado:",
        "invalid_json_state": "❌ JSON inválido en archivo de estado:",
        "permission_denied_state": "❌ Permiso denegado accediendo archivo de estado:",
        "unexpected_error_loading": "❌ Error inesperado cargando estado local:",
        "permission_denied_writing": "❌ Permiso denegado escribiendo archivo de estado:",
        "filesystem_error_saving": "❌ Error del sistema de archivos guardando estado:",
        "invalid_state_data": "❌ Tipo de datos de estado inválido:",
        "unexpected_error_saving": "❌ Error inesperado guardando estado local:",
        "connection_interrupted": "CONEXIÓN INTERRUMPIDA",
        "error": "Error",
        "auto_reconnect": "Reconexión Automática",
        "sdk_will_reconnect": "El SDK de AWS IoT intentará reconectar automáticamente",
        "connection_resumed": "CONEXIÓN RESTABLECIDA",
        "return_code": "Código de Retorno",
        "session_present": "Sesión Presente",
        "status": "Estado",
        "connection_restored": "Conexión restaurada exitosamente",
        "iot_endpoint_discovery": "🌐 Descubrimiento de Endpoint de AWS IoT",
        "endpoint_type": "Tipo de Endpoint",
        "endpoint_type_ats": "iot:Data-ATS (recomendado)",
        "endpoint_url": "URL del Endpoint",
        "port_mqtt_tls": "Puerto: 8883 (MQTT sobre TLS)",
        "protocol_mqtt": "Protocolo: MQTT 3.1.1 sobre TLS",
        "error_getting_endpoint": "❌ Error obteniendo endpoint IoT:",
        "available_devices": "📱 Dispositivos Disponibles ({} encontrados):",
        "type": "Tipo",
        "selected_device": "✅ Dispositivo seleccionado:",
        "invalid_selection": "❌ Selección inválida. Por favor ingresa 1-{}",
        "enter_valid_number": "❌ Por favor ingresa un número válido",
        "operation_cancelled": "🛑 Operación cancelada",
        "no_things_found": "❌ No se encontraron Things. Por favor ejecuta setup_sample_data.py primero",
        "error_selecting_device": "❌ Error seleccionando dispositivo:",
        "no_certificates_found": "❌ No se encontraron certificados para el dispositivo '{}'",
        "run_certificate_manager": "💡 Ejecuta certificate_manager.py para crear y vincular un certificado",
        "using_certificate": "✅ Usando certificado:",
        "multiple_certificates_found": "🔐 Múltiples certificados encontrados:",
        "select_certificate": "Seleccionar certificado (1-{}): ",
        "invalid_selection_cert": "❌ Selección inválida",
        "certificate_files_found": "✅ Archivos de certificado encontrados:",
        "certificate": "Certificado",
        "private_key": "Clave Privada",
        "cert_dir_not_found": "❌ Directorio de certificados no encontrado:",
        "run_cert_manager_files": "💡 Ejecuta certificate_manager.py para crear archivos de certificado",
        "cert_files_not_found": "❌ Archivos de certificado no encontrados en {}",
        "looking_for_files": "Buscando: {}.crt y {}.key",
        "invalid_thing_name": "⚠️ Nombre de thing inválido:",
        "unsafe_path_detected": "⚠️ Ruta insegura detectada:",
        "updating_shadow_reported": "📡 Actualizando Estado Reportado del Shadow",
        "reported_state_update": "📊 Actualización de Estado Reportado:",
        "current_local_state_label": "Estado Local Actual",
        "shadow_update_payload": "Payload de Actualización Shadow",
        "shadow_update_sent": "✅ UPDATE de shadow (reportado) enviado",
        "failed_update_reported": "❌ Falló la actualización del estado reportado:",
        "updating_shadow_desired": "🎯 Actualizando Estado Deseado del Shadow",
        "desired_state_update": "📊 Actualización de Estado Deseado:",
        "enter_property_name": "Ingresa nombre de propiedad: ",
        "property_name_required": "❌ El nombre de propiedad es requerido",
        "enter_property_value": "Ingresa valor de propiedad: ",
        "property_value_required": "❌ El valor de propiedad es requerido",
        "desired_state_to_set": "Estado Deseado a Establecer",
        "property": "Propiedad",
        "value": "Valor",
        "shadow_update_desired_sent": "✅ UPDATE de shadow (deseado) enviado",
        "failed_update_desired": "❌ Falló la actualización del estado deseado:",
        "simulating_device_changes": "🔄 Simulando Cambios de Estado del Dispositivo",
        "simulation_options": "📋 Opciones de Simulación:",
        "temperature_change": "1. Cambio de temperatura (±5°C)",
        "humidity_change": "2. Cambio de humedad (±10%)",
        "status_toggle": "3. Alternar estado (online/offline)",
        "firmware_update": "4. Actualización de versión de firmware",
        "custom_property": "5. Cambio de propiedad personalizada",
        "select_simulation": "Seleccionar simulación (1-5): ",
        "invalid_simulation": "❌ Selección inválida. Por favor selecciona 1-5.",
        "temperature_changed": "🌡️  Temperatura cambiada: {} → {}°C",
        "humidity_changed": "💧 Humedad cambiada: {} → {}%",
        "status_changed": "🔄 Estado cambiado: {} → {}",
        "firmware_updated": "🔧 Firmware actualizado: {} → {}",
        "custom_property_changed": "🔧 Propiedad personalizada '{}' cambiada: {} → {}",
        "state_change_summary": "📊 Resumen de Cambio de Estado:",
        "previous_value": "Valor Anterior",
        "new_value": "Nuevo Valor",
        "local_state_updated_sim": "💾 Estado local actualizado y guardado",
        "reporting_to_shadow": "📡 Reportando cambio al shadow...",
        "simulation_complete": "✅ Simulación completa",
        "viewing_message_history": "📜 Viendo Historial de Mensajes Shadow",
        "message_history": "📊 Historial de Mensajes Shadow ({} mensajes):",
        "no_messages_received": "📭 No se han recibido mensajes shadow aún",
        "try_other_operations": "💡 Prueba otras operaciones primero para generar mensajes shadow",
        "message_details": "Detalles del Mensaje:",
        "clear_history_prompt": "¿Limpiar historial de mensajes? (y/N): ",
        "history_cleared": "🗑️  Historial de mensajes limpiado",
        "history_not_cleared": "📜 Historial de mensajes preservado",
        "disconnecting_from_iot": "🔌 Desconectando de AWS IoT Core...",
        "disconnection_complete": "✅ Desconexión completa",
        "session_summary": "📊 Resumen de Sesión:",
        "total_messages": "Total de Mensajes Recibidos",
        "connection_duration": "Duración de Conexión",
        "shadow_operations": "Operaciones Shadow Realizadas",
        "thank_you_message": "¡Gracias por explorar AWS IoT Device Shadows!",
        "next_steps_suggestions": "🔍 Próximos Pasos:",
        "explore_iot_rules": "• Explora iot_rules_explorer.py para procesamiento de mensajes",
        "try_mqtt_client": "• Prueba mqtt_client_explorer.py para comunicación MQTT directa",
        "check_registry": "• Usa iot_registry_explorer.py para ver detalles del dispositivo",
        "edit_local_state_title": "📝 Editor de Estado Local",
        "current_state": "Estado actual:",
        "options": "Opciones:",
        "edit_individual_values": "1. Editar valores individuales",
        "replace_entire_state": "2. Reemplazar todo el estado con JSON",
        "cancel": "3. Cancelar",
        "select_option_1_3": "Seleccionar opción (1-3): ",
        "current_values": "Valores actuales:",
        "add_new_key": "Agregar nueva clave",
        "done_editing": "Terminar edición",
        "select_item_to_edit": "Seleccionar elemento a editar (1-{}): ",
        "editing_key": "Editando '{}' (actual: {})",
        "new_value_prompt": "Nuevo valor (o presiona Enter para mantener actual): ",
        "updated_key": "✅ Actualizado {} = {}",
        "new_key_name": "Nombre de nueva clave: ",
        "value_for_key": "Valor para '{}': ",
        "added_new_key": "✅ Agregada nueva clave: {} = {}",
        "enter_json_prompt": "Ingresa tu estado JSON (presiona Enter dos veces cuando termines):",
        "invalid_json": "❌ JSON inválido: {}",
        "state_updated_from_json": "✅ Estado actualizado desde JSON",
        "report_updated_state": "¿Reportar estado actualizado al shadow? (y/N): ",
        "shadow_command_prompt": "🌟 Shadow> ",
        "available_commands": "📖 Comandos Disponibles:",
        "get_command": "   get                       - Solicitar documento shadow",
        "local_command": "   local                     - Mostrar estado local del dispositivo",
        "edit_command": "   edit                      - Editar estado local del dispositivo",
        "report_command": "   report                    - Reportar estado local al shadow",
        "desire_command": "   desire key=val [key=val]  - Establecer estado deseado",
        "status_command": "   status                    - Estado de conexión",
        "messages_command": "   messages                  - Historial de mensajes shadow",
        "debug_command": "   debug                     - Diagnósticos de conexión",
        "quit_command": "   quit                      - Salir",
        "example_desire": "💡 Ejemplo: desire temperature=25.0 status=active",
        "current_local_device_state": "📱 Estado Actual del Dispositivo Local:",
        "usage_desire": "❌ Uso: desire key=value [key=value...]",
        "example_desire_usage": "💡 Ejemplo: desire temperature=25.0 status=active",
        "setting_desired_state": "🎯 Estableciendo estado deseado: {}",
        "no_valid_pairs": "❌ No se encontraron pares key=value válidos",
        "shadow_connection_status": "📊 Estado de Conexión Shadow:",
        "connected": "Conectado",
        "yes": "✅ Sí",
        "no": "❌ No",
        "shadow_message_history": "📨 Historial de Mensajes Shadow:",
        "unknown_command": "❌ Comando desconocido: {}. Escribe 'help' para comandos disponibles.",
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
    "zh-CN": {
        "title": "🌟 AWS IoT 设备影子探索器",
        "separator": "=" * 60,
        "aws_context_info": "🌍 AWS 上下文信息：",
        "account_id": "账户 ID",
        "region": "区域",
        "aws_context_error": "⚠️ 无法检索 AWS 上下文：",
        "aws_credentials_reminder": "   请确保已配置 AWS 凭证",
        "description_intro": "此脚本教您 AWS IoT 设备影子概念：",
        "shadow_concepts": [
            "• 用于状态同步的设备影子服务",
            "• 影子文档结构（期望状态 vs 报告状态）",
            "• 影子操作的 MQTT 主题",
            "• 状态差异的增量消息",
            "• 实时影子更新和通知",
            "• 每个操作的完整 API 详细信息",
        ],
        "debug_enabled": "🔍 调试模式已启用",
        "debug_features": [
            "• 增强的 MQTT 消息日志记录",
            "• 完整的影子文档分析",
            "• 扩展的教育信息",
        ],
        "tip": "💡 提示：使用 --debug 或 -d 标志进行增强的影子日志记录",
        "press_enter": "按 Enter 键继续...",
        "goodbye": "👋 再见！",
        "main_menu": "📋 设备影子操作：",
        "menu_options": [
            "1. 连接到设备并订阅影子主题",
            "2. 获取当前影子文档",
            "3. 更新影子报告状态（设备 → 云端）",
            "4. 更新影子期望状态（云端 → 设备）",
            "5. 模拟设备状态变化",
            "6. 查看影子消息历史",
            "7. 断开连接并退出",
        ],
        "select_option": "选择选项 (1-7)：",
        "invalid_choice": "❌ 无效选择。请选择 1-7。",
        "learning_moments": {
            "shadow_foundation": {
                "title": "📚 学习要点：设备影子基础",
                "content": "AWS IoT 设备影子是一个 JSON 文档，用于存储和检索设备的当前状态信息。影子充当设备和应用程序之间的中介，即使在设备离线时也能实现可靠的通信。理解影子概念对于构建强大的 IoT 应用程序至关重要。",
                "next": "我们将探索影子操作和 MQTT 通信",
            },
            "shadow_connection": {
                "title": "📚 学习要点：影子 MQTT 连接",
                "content": "设备影子使用 MQTT 主题进行通信。每个影子操作（get、update、delete）都有相应的 accepted/rejected 响应主题。当期望状态与报告状态不同时，增量主题会发出通知。这种发布/订阅模型实现了设备和应用程序之间的实时双向通信。",
                "next": "我们将建立 MQTT 连接并订阅影子主题",
            },
            "shadow_document": {
                "title": "📚 学习要点：影子文档结构",
                "content": "影子文档包含'desired'（期望）和'reported'（报告）状态。期望状态表示设备应该处于的状态，通常由应用程序设置。报告状态表示设备的当前状态。当这两者不同时，AWS IoT 会生成增量消息来通知设备所需的更改。",
                "next": "我们将检索并分析当前的影子文档",
            },
            "reported_state": {
                "title": "📚 学习要点：报告状态更新",
                "content": "设备更新其报告状态以告知云端其当前状态。这通常在设备更改其物理状态（温度、状态等）后进行。报告状态更新有助于保持影子与实际设备状态同步。",
                "next": "我们将从设备更新影子的报告状态",
            },
            "desired_state": {
                "title": "📚 学习要点：期望状态更新",
                "content": "应用程序设置期望状态以请求设备更改。当期望状态与报告状态不同时，AWS IoT 会向设备发送增量消息。这种机制通过云端实现远程设备控制和配置管理。",
                "next": "我们将从云端更新影子的期望状态",
            },
            "state_simulation": {
                "title": "📚 学习要点：设备状态模拟",
                "content": "模拟设备状态变化有助于理解完整的影子工作流程。我们将修改本地设备状态并观察它如何通过影子服务传播。这展示了影子通信和状态同步的双向性质。",
                "next": "我们将模拟真实的设备状态变化",
            },
        },
        "workflow_titles": {
            "shadow_connection": "🔗 影子连接工作流",
            "shadow_retrieval": "📥 影子文档检索",
            "reported_update": "📡 报告状态更新",
            "desired_update": "🎯 期望状态更新",
            "state_simulation": "🔄 设备状态模拟",
            "message_history": "📜 影子消息历史",
        },
        "step_establishing_connection": "建立影子操作的 MQTT 连接",
        "step_subscribing_topics": "订阅影子主题",
        "step_requesting_shadow": "请求影子文档",
        "step_updating_reported": "更新报告状态",
        "step_updating_desired": "更新期望状态",
        "step_simulating_changes": "模拟设备变化",
        "shadow_connection_params": "🔗 影子连接参数：",
        "client_id": "客户端 ID",
        "thing_name": "物品名称",
        "endpoint": "端点",
        "port": "端口",
        "protocol": "协议",
        "authentication": "身份验证",
        "shadow_type": "影子类型",
        "connecting_to_iot": "🔄 正在连接到 AWS IoT Core...",
        "connection_established": "影子连接已建立",
        "connection_status": "成功连接到 AWS IoT Core",
        "clean_session": "清洁会话",
        "keep_alive": "保持活动",
        "tls_version": "TLS 版本",
        "certificate_auth": "证书身份验证",
        "shadow_connection_failed": "❌ 影子连接失败：",
        "not_connected": "❌ 未连接到 AWS IoT Core",
        "shadow_topics_for_thing": "🌟 物品的影子主题：",
        "classic_shadow_topics": "📋 经典影子主题：",
        "subscription_successful": "✅ 成功订阅所有 {} 个影子主题",
        "subscription_partial": "⚠️  只有 {}/{} 个订阅成功",
        "shadow_topic_explanations": "📖 影子主题说明：",
        "topic_get_accepted": "• get/accepted - 影子文档检索成功",
        "topic_get_rejected": "• get/rejected - 影子文档检索失败",
        "topic_update_accepted": "• update/accepted - 影子更新成功",
        "topic_update_rejected": "• update/rejected - 影子更新失败",
        "topic_update_delta": "• update/delta - 期望 ≠ 报告（需要操作）",
        "requesting_shadow_document": "📥 请求影子文档",
        "topic": "主题",
        "thing": "物品",
        "shadow_type_classic": "经典",
        "shadow_get_request_sent": "✅ 影子 GET 请求已发送",
        "qos": "QoS",
        "packet_id": "数据包 ID",
        "waiting_for_response": "⏳ 等待 get/accepted 或 get/rejected 的响应...",
        "failed_request_shadow": "❌ 请求影子文档失败：",
        "shadow_message_received": "🌟 收到影子消息",
        "direction": "方向",
        "received": "已接收",
        "payload_size": "负载大小",
        "timestamp": "时间戳",
        "shadow_data": "影子数据",
        "error_processing_message": "❌ 处理影子消息时出错：",
        "shadow_get_accepted": "✅ 影子 GET 已接受",
        "shadow_document_retrieved": "📋 已检索影子文档：",
        "version": "版本",
        "desired_state": "期望状态",
        "reported_state": "报告状态",
        "none": "无",
        "shadow_get_rejected": "❌ 影子 GET 被拒绝",
        "error_code": "错误代码",
        "message": "消息",
        "shadow_doesnt_exist": "影子尚不存在 - 将在下次更新时创建",
        "checking_shadow_exists": "检查 {} 的影子是否存在...",
        "shadow_creation_normal": "这对于新设备是正常的 - 我们将通过报告初始状态来创建影子",
        "creating_initial_shadow": "影子尚不存在。正在创建初始影子...",
        "initial_shadow_created": "初始影子创建成功！",
        "retrieving_new_shadow": "检索新创建的影子...",
        "shadow_already_exists": "影子已存在",
        "shadow_update_accepted": "✅ 影子更新已接受",
        "new_version": "新版本",
        "updated_desired": "已更新期望",
        "updated_reported": "已更新报告",
        "shadow_update_rejected": "❌ 影子更新被拒绝",
        "shadow_delta_received": "🔄 收到影子增量",
        "description": "描述",
        "desired_differs_reported": "期望状态与报告状态不同",
        "changes_needed": "需要的更改",
        "state_comparison": "🔍 状态比较：",
        "local_state": "本地状态",
        "delta": "增量",
        "desired": "期望",
        "differences_found": "⚠️  发现差异：",
        "apply_changes_prompt": "将这些更改应用到本地设备？(y/N)：",
        "local_state_updated": "✅ 本地状态更新成功",
        "failed_update_local": "❌ 更新本地状态失败",
        "changes_not_applied": "⏭️  更改未应用到本地设备",
        "local_matches_desired": "✅ 本地状态与期望状态匹配 - 无需更改",
        "automatically_reporting": "📡 自动向影子报告更新状态...",
        "local_state_saved": "💾 本地状态已保存到：",
        "created_default_state": "📄 已创建默认本地状态文件：",
        "default_state": "📊 默认状态：",
        "using_existing_state": "📄 使用现有本地状态文件：",
        "current_local_state": "📊 当前本地状态：",
        "local_state_not_found": "❌ 未找到本地状态文件：",
        "invalid_json_state": "❌ 状态文件中的 JSON 无效：",
        "permission_denied_state": "❌ 访问状态文件权限被拒绝：",
        "unexpected_error_loading": "❌ 加载本地状态时出现意外错误：",
        "permission_denied_writing": "❌ 写入状态文件权限被拒绝：",
        "filesystem_error_saving": "❌ 保存状态时文件系统错误：",
        "invalid_state_data": "❌ 无效的状态数据类型：",
        "unexpected_error_saving": "❌ 保存本地状态时出现意外错误：",
        "connection_interrupted": "连接中断",
        "error": "错误",
        "auto_reconnect": "自动重连",
        "sdk_will_reconnect": "AWS IoT SDK 将尝试自动重新连接",
        "connection_resumed": "连接已恢复",
        "return_code": "返回代码",
        "session_present": "会话存在",
        "status": "状态",
        "connection_restored": "连接成功恢复",
        "iot_endpoint_discovery": "🌐 AWS IoT 端点发现",
        "endpoint_type": "端点类型",
        "endpoint_type_ats": "iot:Data-ATS（推荐）",
        "endpoint_url": "端点 URL",
        "port_mqtt_tls": "端口：8883（MQTT over TLS）",
        "protocol_mqtt": "协议：MQTT 3.1.1 over TLS",
        "error_getting_endpoint": "❌ 获取 IoT 端点时出错：",
        "available_devices": "📱 可用设备（找到 {} 个）：",
        "type": "类型",
        "selected_device": "✅ 已选择设备：",
        "invalid_selection": "❌ 无效选择。请输入 1-{}",
        "enter_valid_number": "❌ 请输入有效数字",
        "operation_cancelled": "🛑 操作已取消",
        "no_things_found": "❌ 未找到物品。请先运行 setup_sample_data.py",
        "error_selecting_device": "❌ 选择设备时出错：",
        "no_certificates_found": "❌ 未找到设备 '{}' 的证书",
        "run_certificate_manager": "💡 运行 certificate_manager.py 创建并附加证书",
        "using_certificate": "✅ 使用证书：",
        "multiple_certificates_found": "🔐 找到多个证书：",
        "select_certificate": "选择证书 (1-{})：",
        "invalid_selection_cert": "❌ 无效选择",
        "certificate_files_found": "✅ 找到证书文件：",
        "certificate": "证书",
        "private_key": "私钥",
        "cert_dir_not_found": "❌ 未找到证书目录：",
        "run_cert_manager_files": "💡 运行 certificate_manager.py 创建证书文件",
        "cert_files_not_found": "❌ 在 {} 中未找到证书文件",
        "looking_for_files": "查找：{}.crt 和 {}.key",
        "invalid_thing_name": "⚠️ 无效的物品名称：",
        "unsafe_path_detected": "⚠️ 检测到不安全路径：",
        "updating_shadow_reported": "📡 更新影子报告状态",
        "reported_state_update": "📊 报告状态更新：",
        "current_local_state_label": "当前本地状态",
        "shadow_update_payload": "影子更新负载",
        "shadow_update_sent": "✅ 影子 UPDATE（报告）已发送",
        "failed_update_reported": "❌ 更新报告状态失败：",
        "updating_shadow_desired": "🎯 更新影子期望状态",
        "desired_state_update": "📊 期望状态更新：",
        "enter_property_name": "输入属性名称：",
        "property_name_required": "❌ 属性名称是必需的",
        "enter_property_value": "输入属性值：",
        "property_value_required": "❌ 属性值是必需的",
        "desired_state_to_set": "要设置的期望状态",
        "property": "属性",
        "value": "值",
        "shadow_update_desired_sent": "✅ 影子 UPDATE（期望）已发送",
        "failed_update_desired": "❌ 更新期望状态失败：",
        "simulating_device_changes": "🔄 模拟设备状态变化",
        "simulation_options": "📋 模拟选项：",
        "temperature_change": "1. 温度变化（±5°C）",
        "humidity_change": "2. 湿度变化（±10%）",
        "status_toggle": "3. 状态切换（在线/离线）",
        "firmware_update": "4. 固件版本更新",
        "custom_property": "5. 自定义属性变化",
        "select_simulation": "选择模拟 (1-5)：",
        "invalid_simulation": "❌ 无效选择。请选择 1-5。",
        "temperature_changed": "🌡️  温度已变化：{} → {}°C",
        "humidity_changed": "💧 湿度已变化：{} → {}%",
        "status_changed": "🔄 状态已变化：{} → {}",
        "firmware_updated": "🔧 固件已更新：{} → {}",
        "custom_property_changed": "🔧 自定义属性 '{}' 已变化：{} → {}",
        "state_change_summary": "📊 状态变化摘要：",
        "previous_value": "先前值",
        "new_value": "新值",
        "local_state_updated_sim": "💾 本地状态已更新并保存",
        "reporting_to_shadow": "📡 向影子报告变化...",
        "simulation_complete": "✅ 模拟完成",
        "viewing_message_history": "📜 查看影子消息历史",
        "message_history": "📊 影子消息历史（{} 条消息）：",
        "no_messages_received": "📭 尚未收到影子消息",
        "try_other_operations": "💡 请先尝试其他操作以生成影子消息",
        "message_details": "消息详细信息：",
        "clear_history_prompt": "清除消息历史？(y/N)：",
        "history_cleared": "🗑️  消息历史已清除",
        "history_not_cleared": "📜 消息历史已保留",
        "disconnecting_from_iot": "🔌 正在断开与 AWS IoT Core 的连接...",
        "disconnection_complete": "✅ 断开连接完成",
        "session_summary": "📊 会话摘要：",
        "total_messages": "收到的消息总数",
        "connection_duration": "连接持续时间",
        "shadow_operations": "执行的影子操作",
        "thank_you_message": "感谢您探索 AWS IoT 设备影子！",
        "next_steps_suggestions": "🔍 下一步：",
        "explore_iot_rules": "• 探索 iot_rules_explorer.py 进行消息处理",
        "try_mqtt_client": "• 尝试 mqtt_client_explorer.py 进行直接 MQTT 通信",
        "check_registry": "• 使用 iot_registry_explorer.py 查看设备详细信息",
        "edit_local_state_title": "📝 本地状态编辑器",
        "current_state": "当前状态：",
        "options": "选项：",
        "edit_individual_values": "1. 编辑单个值",
        "replace_entire_state": "2. 用 JSON 替换整个状态",
        "cancel": "3. 取消",
        "select_option_1_3": "选择选项 (1-3)：",
        "current_values": "当前值：",
        "add_new_key": "添加新键",
        "done_editing": "完成编辑",
        "select_item_to_edit": "选择要编辑的项目 (1-{})：",
        "editing_key": "编辑 '{}'（当前：{}）",
        "new_value_prompt": "新值（或按 Enter 保持当前值）：",
        "updated_key": "✅ 已更新 {} = {}",
        "new_key_name": "新键名称：",
        "value_for_key": "'{}' 的值：",
        "added_new_key": "✅ 已添加新键：{} = {}",
        "enter_json_prompt": "输入您的 JSON 状态（完成后按两次 Enter）：",
        "invalid_json": "❌ 无效的 JSON：{}",
        "state_updated_from_json": "✅ 状态已从 JSON 更新",
        "report_updated_state": "向影子报告更新状态？(y/N)：",
        "shadow_command_prompt": "🌟 影子> ",
        "available_commands": "📖 可用命令：",
        "get_command": "   get                       - 请求影子文档",
        "local_command": "   local                     - 显示本地设备状态",
        "edit_command": "   edit                      - 编辑本地设备状态",
        "report_command": "   report                    - 向影子报告本地状态",
        "desire_command": "   desire key=val [key=val]  - 设置期望状态",
        "status_command": "   status                    - 连接状态",
        "messages_command": "   messages                  - 影子消息历史",
        "debug_command": "   debug                     - 连接诊断",
        "quit_command": "   quit                      - 退出",
        "example_desire": "💡 示例：desire temperature=25.0 status=active",
        "current_local_device_state": "📱 当前本地设备状态：",
        "usage_desire": "❌ 用法：desire key=value [key=value...]",
        "example_desire_usage": "💡 示例：desire temperature=25.0 status=active",
        "setting_desired_state": "🎯 设置期望状态：{}",
        "no_valid_pairs": "❌ 未找到有效的 key=value 对",
        "shadow_connection_status": "📊 影子连接状态：",
        "connected": "已连接",
        "yes": "✅ 是",
        "no": "❌ 否",
        "shadow_message_history": "📨 影子消息历史：",
        "unknown_command": "❌ 未知命令：{}。输入 'help' 查看可用命令。",
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
    "debug_messages": {
        "en": {
            "debug_raw_topic": "🔍 DEBUG: Raw topic:",
            "debug_qos_duplicate": "🔍 DEBUG: QoS: {}, Duplicate: {}, Retain: {}",
            "debug_payload_size": "🔍 DEBUG: Payload size: {} bytes",
            "debug_message_count": "🔍 DEBUG: Message count: {}",
            "debug_unrecognized_topic": "🔍 DEBUG: Unrecognized shadow topic pattern",
            "debug_comparing_desired": "🔍 DEBUG: Comparing desired state with local state",
            "debug_desired_keys": "🔍 DEBUG: Desired keys: {}",
            "debug_no_desired_state": "🔍 DEBUG: No desired state in shadow document",
            "debug_normal_for_new": "🔍 DEBUG: This is normal for new devices - shadow created on first update",
            "debug_error_code_indicates": "🔍 DEBUG: Error code {} indicates: {}",
            "debug_processing_delta": "🔍 DEBUG: Processing delta with {} changed properties",
            "debug_delta_keys": "🔍 DEBUG: Delta keys: {}",
            "debug_loaded_local_state": "🔍 DEBUG: Loaded local state with {} properties",
            "debug_comparing_properties": "🔍 DEBUG: Comparing {} desired properties",
            "debug_differences_found": "🔍 DEBUG: Found {} differences out of {} desired properties",
            "debug_type_change": "🔍 DEBUG: Type change: {} → {}",
            "debug_updated_properties": "🔍 DEBUG: Updated {} properties in local state",
            "debug_new_state_size": "🔍 DEBUG: New local state size: {} properties",
            "debug_all_match": "🔍 DEBUG: All {} desired properties match local state",
            "debug_setting_up_state": "🔍 DEBUG: Setting up local state file: {}",
            "debug_cert_directory": "🔍 DEBUG: Certificate directory: {}",
            "debug_file_exists": "🔍 DEBUG: File exists: {}",
            "debug_created_new_state": "🔍 DEBUG: Created new state file with {} properties",
            "debug_loaded_existing_state": "🔍 DEBUG: Loaded existing state file with {} properties",
            "debug_file_size": "🔍 DEBUG: File size: {} bytes",
            "debug_calling_describe_endpoint": "🔍 DEBUG: Calling describe_endpoint API",
            "debug_input_parameters": "📥 Input Parameters: {'endpointType': 'iot:Data-ATS'}",
            "debug_api_response": "📤 API Response: {}",
            "debug_full_traceback": "🔍 DEBUG: Full traceback:",
            "debug_calling_list_things": "🔍 DEBUG: Calling list_things API",
            "debug_input_params_none": "📥 Input Parameters: None",
            "debug_found_things": "📤 API Response: Found {} Things",
            "debug_thing_names": "📊 Thing Names: {}",
            "debug_calling_list_principals": "🔍 DEBUG: Calling list_thing_principals API",
            "debug_input_thing_name": "📥 Input Parameters: {'thingName': '{}'}",
            "debug_found_principals": "📤 API Response: Found {} principals, {} certificates",
            "debug_cert_arns": "📊 Certificate ARNs: {}",
            "debug_shadow_connection_setup": "🔍 DEBUG: Shadow MQTT Connection Setup",
            "debug_thing_name": "   Thing Name: {}",
            "debug_cert_file": "   Certificate File: {}",
            "debug_private_key_file": "   Private Key File: {}",
            "debug_endpoint": "   Endpoint: {}",
            "debug_connection_result": "🔍 DEBUG: Connection result: {}",
            "debug_subscribing_topic": "🔍 DEBUG: Subscribing to shadow topic: {}",
            "debug_subscription_successful": "🔍 DEBUG: Subscription successful, packet ID: {}",
            "debug_publishing_shadow_get": "🔍 DEBUG: Publishing shadow get request",
            "debug_topic": "   Topic: {}",
            "debug_payload_empty": "   Payload: Empty (shadow get requests have no payload)",
            "debug_publishing_shadow_update": "🔍 DEBUG: Publishing shadow update request",
            "debug_payload_json": "   Payload: {}",
            "debug_update_type": "   Update Type: {}",
            "debug_simulation_type": "🔍 DEBUG: Simulation type: {}",
            "debug_property_change": "🔍 DEBUG: Property '{}' changed from {} to {}",
            "debug_state_before": "🔍 DEBUG: State before: {}",
            "debug_state_after": "🔍 DEBUG: State after: {}",
        },
        "es": {
            "debug_raw_topic": "🔍 DEBUG: Tópico crudo:",
            "debug_qos_duplicate": "🔍 DEBUG: QoS: {}, Duplicado: {}, Retener: {}",
            "debug_payload_size": "🔍 DEBUG: Tamaño de payload: {} bytes",
            "debug_message_count": "🔍 DEBUG: Conteo de mensajes: {}",
            "debug_unrecognized_topic": "🔍 DEBUG: Patrón de tópico shadow no reconocido",
            "debug_comparing_desired": "🔍 DEBUG: Comparando estado deseado con estado local",
            "debug_desired_keys": "🔍 DEBUG: Claves deseadas: {}",
            "debug_no_desired_state": "🔍 DEBUG: No hay estado deseado en documento shadow",
            "debug_normal_for_new": "🔍 DEBUG: Esto es normal para dispositivos nuevos - shadow creado en primera actualización",
            "debug_error_code_indicates": "🔍 DEBUG: Código de error {} indica: {}",
            "debug_processing_delta": "🔍 DEBUG: Procesando delta con {} propiedades cambiadas",
            "debug_delta_keys": "🔍 DEBUG: Claves delta: {}",
            "debug_loaded_local_state": "🔍 DEBUG: Estado local cargado con {} propiedades",
            "debug_comparing_properties": "🔍 DEBUG: Comparando {} propiedades deseadas",
            "debug_differences_found": "🔍 DEBUG: Encontradas {} diferencias de {} propiedades deseadas",
            "debug_type_change": "🔍 DEBUG: Cambio de tipo: {} → {}",
            "debug_updated_properties": "🔍 DEBUG: Actualizadas {} propiedades en estado local",
            "debug_new_state_size": "🔍 DEBUG: Nuevo tamaño de estado local: {} propiedades",
            "debug_all_match": "🔍 DEBUG: Todas las {} propiedades deseadas coinciden con estado local",
            "debug_setting_up_state": "🔍 DEBUG: Configurando archivo de estado local: {}",
            "debug_cert_directory": "🔍 DEBUG: Directorio de certificados: {}",
            "debug_file_exists": "🔍 DEBUG: Archivo existe: {}",
            "debug_created_new_state": "🔍 DEBUG: Creado nuevo archivo de estado con {} propiedades",
            "debug_loaded_existing_state": "🔍 DEBUG: Cargado archivo de estado existente con {} propiedades",
            "debug_file_size": "🔍 DEBUG: Tamaño de archivo: {} bytes",
            "debug_calling_describe_endpoint": "🔍 DEBUG: Llamando API describe_endpoint",
            "debug_input_parameters": "📥 Parámetros de Entrada: {'endpointType': 'iot:Data-ATS'}",
            "debug_api_response": "📤 Respuesta de API: {}",
            "debug_full_traceback": "🔍 DEBUG: Traza completa:",
            "debug_calling_list_things": "🔍 DEBUG: Llamando API list_things",
            "debug_input_params_none": "📥 Parámetros de Entrada: Ninguno",
            "debug_found_things": "📤 Respuesta de API: Encontrados {} Things",
            "debug_thing_names": "📊 Nombres de Things: {}",
            "debug_calling_list_principals": "🔍 DEBUG: Llamando API list_thing_principals",
            "debug_input_thing_name": "📥 Parámetros de Entrada: {'thingName': '{}'}",
            "debug_found_principals": "📤 Respuesta de API: Encontrados {} principales, {} certificados",
            "debug_cert_arns": "📊 ARNs de Certificados: {}",
            "debug_shadow_connection_setup": "🔍 DEBUG: Configuración de Conexión MQTT Shadow",
            "debug_thing_name": "   Nombre del Thing: {}",
            "debug_cert_file": "   Archivo de Certificado: {}",
            "debug_private_key_file": "   Archivo de Clave Privada: {}",
            "debug_endpoint": "   Endpoint: {}",
            "debug_connection_result": "🔍 DEBUG: Resultado de conexión: {}",
            "debug_subscribing_topic": "🔍 DEBUG: Suscribiéndose a tópico shadow: {}",
            "debug_subscription_successful": "🔍 DEBUG: Suscripción exitosa, ID de paquete: {}",
            "debug_publishing_shadow_get": "🔍 DEBUG: Publicando solicitud shadow get",
            "debug_topic": "   Tópico: {}",
            "debug_payload_empty": "   Payload: Vacío (solicitudes shadow get no tienen payload)",
            "debug_publishing_shadow_update": "🔍 DEBUG: Publicando solicitud shadow update",
            "debug_payload_json": "   Payload: {}",
            "debug_update_type": "   Tipo de Actualización: {}",
            "debug_simulation_type": "🔍 DEBUG: Tipo de simulación: {}",
            "debug_property_change": "🔍 DEBUG: Propiedad '{}' cambiada de {} a {}",
            "debug_state_before": "🔍 DEBUG: Estado antes: {}",
            "debug_state_after": "🔍 DEBUG: Estado después: {}",
        },
        "pt-BR": {
            "debug_raw_topic": "🔍 DEBUG: Tópico bruto:",
            "debug_qos_duplicate": "🔍 DEBUG: QoS: {}, Duplicado: {}, Reter: {}",
            "debug_payload_size": "🔍 DEBUG: Tamanho do payload: {} bytes",
            "debug_message_count": "🔍 DEBUG: Contagem de mensagens: {}",
            "debug_unrecognized_topic": "🔍 DEBUG: Padrão de tópico shadow não reconhecido",
            "debug_comparing_desired": "🔍 DEBUG: Comparando estado desejado com estado local",
            "debug_desired_keys": "🔍 DEBUG: Chaves desejadas: {}",
            "debug_no_desired_state": "🔍 DEBUG: Nenhum estado desejado no documento shadow",
            "debug_normal_for_new": "🔍 DEBUG: Isso é normal para novos dispositivos - shadow criado na primeira atualização",
            "debug_error_code_indicates": "🔍 DEBUG: Código de erro {} indica: {}",
            "debug_processing_delta": "🔍 DEBUG: Processando delta com {} propriedades alteradas",
            "debug_delta_keys": "🔍 DEBUG: Chaves delta: {}",
            "debug_loaded_local_state": "🔍 DEBUG: Estado local carregado com {} propriedades",
            "debug_comparing_properties": "🔍 DEBUG: Comparando {} propriedades desejadas",
            "debug_differences_found": "🔍 DEBUG: Encontradas {} diferenças de {} propriedades desejadas",
            "debug_type_change": "🔍 DEBUG: Mudança de tipo: {} → {}",
            "debug_updated_properties": "🔍 DEBUG: Atualizadas {} propriedades no estado local",
            "debug_new_state_size": "🔍 DEBUG: Novo tamanho do estado local: {} propriedades",
            "debug_all_match": "🔍 DEBUG: Todas as {} propriedades desejadas coincidem com o estado local",
            "debug_setting_up_state": "🔍 DEBUG: Configurando arquivo de estado local: {}",
            "debug_cert_directory": "🔍 DEBUG: Diretório de certificados: {}",
            "debug_file_exists": "🔍 DEBUG: Arquivo existe: {}",
            "debug_created_new_state": "🔍 DEBUG: Criado novo arquivo de estado com {} propriedades",
            "debug_loaded_existing_state": "🔍 DEBUG: Carregado arquivo de estado existente com {} propriedades",
            "debug_file_size": "🔍 DEBUG: Tamanho do arquivo: {} bytes",
            "debug_calling_describe_endpoint": "🔍 DEBUG: Chamando API describe_endpoint",
            "debug_input_parameters": "📥 Parâmetros de Entrada: {'endpointType': 'iot:Data-ATS'}",
            "debug_api_response": "📤 Resposta da API: {}",
            "debug_full_traceback": "🔍 DEBUG: Rastreamento completo:",
            "debug_calling_list_things": "🔍 DEBUG: Chamando API list_things",
            "debug_input_params_none": "📥 Parâmetros de Entrada: Nenhum",
            "debug_found_things": "📤 Resposta da API: Encontrados {} Things",
            "debug_thing_names": "📊 Nomes dos Things: {}",
            "debug_calling_list_principals": "🔍 DEBUG: Chamando API list_thing_principals",
            "debug_input_thing_name": "📥 Parâmetros de Entrada: {'thingName': '{}'}",
            "debug_found_principals": "📤 Resposta da API: Encontrados {} principais, {} certificados",
            "debug_cert_arns": "📊 ARNs dos Certificados: {}",
            "debug_shadow_connection_setup": "🔍 DEBUG: Configuração da Conexão MQTT Shadow",
            "debug_thing_name": "   Nome do Thing: {}",
            "debug_cert_file": "   Arquivo de Certificado: {}",
            "debug_private_key_file": "   Arquivo de Chave Privada: {}",
            "debug_endpoint": "   Endpoint: {}",
            "debug_connection_result": "🔍 DEBUG: Resultado da conexão: {}",
            "debug_subscribing_topic": "🔍 DEBUG: Inscrevendo-se no tópico shadow: {}",
            "debug_subscription_successful": "🔍 DEBUG: Inscrição bem-sucedida, ID do pacote: {}",
            "debug_publishing_shadow_get": "🔍 DEBUG: Publicando solicitação shadow get",
            "debug_topic": "   Tópico: {}",
            "debug_payload_empty": "   Payload: Vazio (solicitações shadow get não têm payload)",
            "debug_publishing_shadow_update": "🔍 DEBUG: Publicando solicitação shadow update",
            "debug_payload_json": "   Payload: {}",
            "debug_update_type": "   Tipo de Atualização: {}",
            "debug_simulation_type": "🔍 DEBUG: Tipo de simulação: {}",
            "debug_property_change": "🔍 DEBUG: Propriedade '{}' alterada de {} para {}",
            "debug_state_before": "🔍 DEBUG: Estado antes: {}",
            "debug_state_after": "🔍 DEBUG: Estado depois: {}",
        },
        "ja": {
            "debug_raw_topic": "🔍 DEBUG: 生トピック:",
            "debug_qos_duplicate": "🔍 DEBUG: QoS: {}, 重複: {}, 保持: {}",
            "debug_payload_size": "🔍 DEBUG: ペイロードサイズ: {} バイト",
            "debug_message_count": "🔍 DEBUG: メッセージ数: {}",
            "debug_unrecognized_topic": "🔍 DEBUG: 認識されないシャドウトピックパターン",
            "debug_comparing_desired": "🔍 DEBUG: 希望状態とローカル状態を比較中",
            "debug_desired_keys": "🔍 DEBUG: 希望キー: {}",
            "debug_no_desired_state": "🔍 DEBUG: シャドウドキュメントに希望状態がありません",
            "debug_normal_for_new": "🔍 DEBUG: これは新しいデバイスでは正常です - 最初の更新でシャドウが作成されます",
            "debug_error_code_indicates": "🔍 DEBUG: エラーコード {} は次を示します: {}",
            "debug_processing_delta": "🔍 DEBUG: {} 個の変更されたプロパティでデルタを処理中",
            "debug_delta_keys": "🔍 DEBUG: デルタキー: {}",
            "debug_loaded_local_state": "🔍 DEBUG: {} 個のプロパティでローカル状態をロード",
            "debug_comparing_properties": "🔍 DEBUG: {} 個の希望プロパティを比較中",
            "debug_differences_found": "🔍 DEBUG: {} 個の希望プロパティのうち {} 個の違いを発見",
            "debug_type_change": "🔍 DEBUG: タイプ変更: {} → {}",
            "debug_updated_properties": "🔍 DEBUG: ローカル状態で {} 個のプロパティを更新",
            "debug_new_state_size": "🔍 DEBUG: 新しいローカル状態サイズ: {} 個のプロパティ",
            "debug_all_match": "🔍 DEBUG: すべての {} 個の希望プロパティがローカル状態と一致",
            "debug_setting_up_state": "🔍 DEBUG: ローカル状態ファイルを設定中: {}",
            "debug_cert_directory": "🔍 DEBUG: 証明書ディレクトリ: {}",
            "debug_file_exists": "🔍 DEBUG: ファイル存在: {}",
            "debug_created_new_state": "🔍 DEBUG: {} 個のプロパティで新しい状態ファイルを作成",
            "debug_loaded_existing_state": "🔍 DEBUG: {} 個のプロパティで既存の状態ファイルをロード",
            "debug_file_size": "🔍 DEBUG: ファイルサイズ: {} バイト",
            "debug_calling_describe_endpoint": "🔍 DEBUG: describe_endpoint API を呼び出し中",
            "debug_input_parameters": "📥 入力パラメータ: {'endpointType': 'iot:Data-ATS'}",
            "debug_api_response": "📤 API レスポンス: {}",
            "debug_full_traceback": "🔍 DEBUG: 完全なトレースバック:",
            "debug_calling_list_things": "🔍 DEBUG: list_things API を呼び出し中",
            "debug_input_params_none": "📥 入力パラメータ: なし",
            "debug_found_things": "📤 API レスポンス: {} 個の Thing を発見",
            "debug_thing_names": "📊 Thing 名: {}",
            "debug_calling_list_principals": "🔍 DEBUG: list_thing_principals API を呼び出し中",
            "debug_input_thing_name": "📥 入力パラメータ: {'thingName': '{}'}",
            "debug_found_principals": "📤 API レスポンス: {} 個のプリンシパル、{} 個の証明書を発見",
            "debug_cert_arns": "📊 証明書 ARN: {}",
            "debug_shadow_connection_setup": "🔍 DEBUG: シャドウ MQTT 接続設定",
            "debug_thing_name": "   Thing 名: {}",
            "debug_cert_file": "   証明書ファイル: {}",
            "debug_private_key_file": "   秘密鍵ファイル: {}",
            "debug_endpoint": "   エンドポイント: {}",
            "debug_connection_result": "🔍 DEBUG: 接続結果: {}",
            "debug_subscribing_topic": "🔍 DEBUG: シャドウトピックを購読中: {}",
            "debug_subscription_successful": "🔍 DEBUG: 購読成功、パケット ID: {}",
            "debug_publishing_shadow_get": "🔍 DEBUG: シャドウ get リクエストを公開中",
            "debug_topic": "   トピック: {}",
            "debug_payload_empty": "   ペイロード: 空（シャドウ get リクエストにはペイロードがありません）",
            "debug_publishing_shadow_update": "🔍 DEBUG: シャドウ update リクエストを公開中",
            "debug_payload_json": "   ペイロード: {}",
            "debug_update_type": "   更新タイプ: {}",
            "debug_simulation_type": "🔍 DEBUG: シミュレーションタイプ: {}",
            "debug_property_change": "🔍 DEBUG: プロパティ '{}' が {} から {} に変更",
            "debug_state_before": "🔍 DEBUG: 変更前の状態: {}",
            "debug_state_after": "🔍 DEBUG: 変更後の状態: {}",
        },
        "zh-CN": {
            "debug_raw_topic": "🔍 DEBUG: 原始主题:",
            "debug_qos_duplicate": "🔍 DEBUG: QoS: {}, 重复: {}, 保留: {}",
            "debug_payload_size": "🔍 DEBUG: 负载大小: {} 字节",
            "debug_message_count": "🔍 DEBUG: 消息计数: {}",
            "debug_unrecognized_topic": "🔍 DEBUG: 无法识别的影子主题模式",
            "debug_comparing_desired": "🔍 DEBUG: 正在比较期望状态与本地状态",
            "debug_desired_keys": "🔍 DEBUG: 期望键: {}",
            "debug_no_desired_state": "🔍 DEBUG: 影子文档中没有期望状态",
            "debug_normal_for_new": "🔍 DEBUG: 这对新设备是正常的 - 影子在首次更新时创建",
            "debug_error_code_indicates": "🔍 DEBUG: 错误代码 {} 表示: {}",
            "debug_processing_delta": "🔍 DEBUG: 正在处理包含 {} 个更改属性的增量",
            "debug_delta_keys": "🔍 DEBUG: 增量键: {}",
            "debug_loaded_local_state": "🔍 DEBUG: 已加载包含 {} 个属性的本地状态",
            "debug_comparing_properties": "🔍 DEBUG: 正在比较 {} 个期望属性",
            "debug_differences_found": "🔍 DEBUG: 在 {} 个期望属性中发现 {} 个差异",
            "debug_type_change": "🔍 DEBUG: 类型更改: {} → {}",
            "debug_updated_properties": "🔍 DEBUG: 在本地状态中更新了 {} 个属性",
            "debug_new_state_size": "🔍 DEBUG: 新本地状态大小: {} 个属性",
            "debug_all_match": "🔍 DEBUG: 所有 {} 个期望属性都与本地状态匹配",
            "debug_setting_up_state": "🔍 DEBUG: 正在设置本地状态文件: {}",
            "debug_cert_directory": "🔍 DEBUG: 证书目录: {}",
            "debug_file_exists": "🔍 DEBUG: 文件存在: {}",
            "debug_created_new_state": "🔍 DEBUG: 创建了包含 {} 个属性的新状态文件",
            "debug_loaded_existing_state": "🔍 DEBUG: 加载了包含 {} 个属性的现有状态文件",
            "debug_file_size": "🔍 DEBUG: 文件大小: {} 字节",
            "debug_calling_describe_endpoint": "🔍 DEBUG: 正在调用 describe_endpoint API",
            "debug_input_parameters": "📥 输入参数: {'endpointType': 'iot:Data-ATS'}",
            "debug_api_response": "📤 API 响应: {}",
            "debug_full_traceback": "🔍 DEBUG: 完整回溯:",
            "debug_calling_list_things": "🔍 DEBUG: 正在调用 list_things API",
            "debug_input_params_none": "📥 输入参数: 无",
            "debug_found_things": "📤 API 响应: 找到 {} 个 Thing",
            "debug_thing_names": "📊 Thing 名称: {}",
            "debug_calling_list_principals": "🔍 DEBUG: 正在调用 list_thing_principals API",
            "debug_input_thing_name": "📥 输入参数: {'thingName': '{}'}",
            "debug_found_principals": "📤 API 响应: 找到 {} 个主体，{} 个证书",
            "debug_cert_arns": "📊 证书 ARN: {}",
            "debug_shadow_connection_setup": "🔍 DEBUG: 影子 MQTT 连接设置",
            "debug_thing_name": "   Thing 名称: {}",
            "debug_cert_file": "   证书文件: {}",
            "debug_private_key_file": "   私钥文件: {}",
            "debug_endpoint": "   端点: {}",
            "debug_connection_result": "🔍 DEBUG: 连接结果: {}",
            "debug_subscribing_topic": "🔍 DEBUG: 正在订阅影子主题: {}",
            "debug_subscription_successful": "🔍 DEBUG: 订阅成功，数据包 ID: {}",
            "debug_publishing_shadow_get": "🔍 DEBUG: 正在发布影子 get 请求",
            "debug_topic": "   主题: {}",
            "debug_payload_empty": "   负载: 空（影子 get 请求没有负载）",
            "debug_publishing_shadow_update": "🔍 DEBUG: 正在发布影子 update 请求",
            "debug_payload_json": "   负载: {}",
            "debug_update_type": "   更新类型: {}",
            "debug_simulation_type": "🔍 DEBUG: 模拟类型: {}",
            "debug_property_change": "🔍 DEBUG: 属性 '{}' 从 {} 更改为 {}",
            "debug_state_before": "🔍 DEBUG: 更改前状态: {}",
            "debug_state_after": "🔍 DEBUG: 更改后状态: {}",
        },
        "ko": {
            "debug_raw_topic": "🔍 DEBUG: 원시 토픽:",
            "debug_qos_duplicate": "🔍 DEBUG: QoS: {}, 중복: {}, 보유: {}",
            "debug_payload_size": "🔍 DEBUG: 페이로드 크기: {} 바이트",
            "debug_message_count": "🔍 DEBUG: 메시지 수: {}",
            "debug_unrecognized_topic": "🔍 DEBUG: 인식되지 않는 섀도우 토픽 패턴",
            "debug_comparing_desired": "🔍 DEBUG: 원하는 상태와 로컬 상태 비교 중",
            "debug_desired_keys": "🔍 DEBUG: 원하는 키: {}",
            "debug_no_desired_state": "🔍 DEBUG: 섀도우 문서에 원하는 상태가 없음",
            "debug_normal_for_new": "🔍 DEBUG: 새 장치에서는 정상입니다 - 첫 번째 업데이트에서 섀도우가 생성됨",
            "debug_error_code_indicates": "🔍 DEBUG: 오류 코드 {}는 다음을 나타냅니다: {}",
            "debug_processing_delta": "🔍 DEBUG: {} 개의 변경된 속성으로 델타 처리 중",
            "debug_delta_keys": "🔍 DEBUG: 델타 키: {}",
            "debug_loaded_local_state": "🔍 DEBUG: {} 개의 속성으로 로컬 상태 로드됨",
            "debug_comparing_properties": "🔍 DEBUG: {} 개의 원하는 속성 비교 중",
            "debug_differences_found": "🔍 DEBUG: {} 개의 원하는 속성 중 {} 개의 차이점 발견",
            "debug_type_change": "🔍 DEBUG: 타입 변경: {} → {}",
            "debug_updated_properties": "🔍 DEBUG: 로컬 상태에서 {} 개의 속성 업데이트됨",
            "debug_new_state_size": "🔍 DEBUG: 새 로컬 상태 크기: {} 개의 속성",
            "debug_all_match": "🔍 DEBUG: 모든 {} 개의 원하는 속성이 로컬 상태와 일치",
            "debug_setting_up_state": "🔍 DEBUG: 로컬 상태 파일 설정 중: {}",
            "debug_cert_directory": "🔍 DEBUG: 인증서 디렉토리: {}",
            "debug_file_exists": "🔍 DEBUG: 파일 존재: {}",
            "debug_created_new_state": "🔍 DEBUG: {} 개의 속성으로 새 상태 파일 생성됨",
            "debug_loaded_existing_state": "🔍 DEBUG: {} 개의 속성으로 기존 상태 파일 로드됨",
            "debug_file_size": "🔍 DEBUG: 파일 크기: {} 바이트",
            "debug_calling_describe_endpoint": "🔍 DEBUG: describe_endpoint API 호출 중",
            "debug_input_parameters": "📥 입력 매개변수: {'endpointType': 'iot:Data-ATS'}",
            "debug_api_response": "📤 API 응답: {}",
            "debug_full_traceback": "🔍 DEBUG: 전체 추적:",
            "debug_calling_list_things": "🔍 DEBUG: list_things API 호출 중",
            "debug_input_params_none": "📥 입력 매개변수: 없음",
            "debug_found_things": "📤 API 응답: {} 개의 Thing 발견",
            "debug_thing_names": "📊 Thing 이름: {}",
            "debug_calling_list_principals": "🔍 DEBUG: list_thing_principals API 호출 중",
            "debug_input_thing_name": "📥 입력 매개변수: {'thingName': '{}'}",
            "debug_found_principals": "📤 API 응답: {} 개의 주체, {} 개의 인증서 발견",
            "debug_cert_arns": "📊 인증서 ARN: {}",
            "debug_shadow_connection_setup": "🔍 DEBUG: 섀도우 MQTT 연결 설정",
            "debug_thing_name": "   Thing 이름: {}",
            "debug_cert_file": "   인증서 파일: {}",
            "debug_private_key_file": "   개인 키 파일: {}",
            "debug_endpoint": "   엔드포인트: {}",
            "debug_connection_result": "🔍 DEBUG: 연결 결과: {}",
            "debug_subscribing_topic": "🔍 DEBUG: 섀도우 토픽 구독 중: {}",
            "debug_subscription_successful": "🔍 DEBUG: 구독 성공, 패킷 ID: {}",
            "debug_publishing_shadow_get": "🔍 DEBUG: 섀도우 get 요청 게시 중",
            "debug_topic": "   토픽: {}",
            "debug_payload_empty": "   페이로드: 비어있음 (섀도우 get 요청에는 페이로드가 없음)",
            "debug_publishing_shadow_update": "🔍 DEBUG: 섀도우 update 요청 게시 중",
            "debug_payload_json": "   페이로드: {}",
            "debug_update_type": "   업데이트 타입: {}",
            "debug_simulation_type": "🔍 DEBUG: 시뮬레이션 타입: {}",
            "debug_property_change": "🔍 DEBUG: 속성 '{}'이 {}에서 {}로 변경됨",
            "debug_state_before": "🔍 DEBUG: 변경 전 상태: {}",
            "debug_state_after": "🔍 DEBUG: 변경 후 상태: {}",
        },
    },
    "ja": {
        "title": "🌟 AWS IoT Device Shadow エクスプローラー",
        "separator": "=" * 45,
        "aws_config": "📍 AWS設定:",
        "account_id": "アカウントID",
        "region": "リージョン",
        "description": "Device Shadowを使用したデバイス状態同期の学習。",
        "debug_enabled": "🔍 デバッグモード有効",
        "debug_features": ["• 詳細なShadow操作ログ", "• 完全な状態変更追跡", "• 拡張エラー診断"],
        "tip": "💡 ヒント: 詳細なShadowログには--debugフラグを使用",
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
        "shadow_intro_title": "Device Shadow - デバイス状態同期",
        "shadow_intro_content": "AWS IoT Device Shadowは、デバイスの現在の状態と希望する状態を同期するサービスです。デバイスがオフラインでも状態を保持し、再接続時に同期を行います。これにより、信頼性の高いIoTアプリケーションの構築が可能になります。",
        "shadow_intro_next": "Device Shadowの操作を探索し、状態管理を学習します",
        "press_enter": "Enterキーを押して続行...",
        "goodbye": "👋 さようなら！",
        "thing_selection_title": "📱 Thing選択",
        "available_things": "利用可能なThings:",
        "no_things_found": "❌ Thingsが見つかりません。setup_sample_data.pyを実行してサンプルデータを作成してください。",
        "select_thing": "Thingを選択 (1-{}): ",
        "invalid_thing_choice": "❌ 無効な選択です。1-{}を選択してください。",
        "selected_thing": "✅ 選択されたThing: {}",
        "operations_menu": "📋 利用可能な操作:",
        "operations": [
            "1. Shadowを取得",
            "2. 希望する状態を更新",
            "3. 報告された状態を更新",
            "4. Shadowを削除",
            "5. 別のThingを選択",
            "6. 終了",
        ],
        "select_operation": "操作を選択 (1-6): ",
        "invalid_choice": "❌ 無効な選択です。1-6を選択してください。",
        "get_shadow_learning_title": "📚 学習ポイント: Shadow取得",
        "get_shadow_learning_content": "Shadow取得により、デバイスの現在の状態、希望する状態、および差分（delta）を確認できます。これは、デバイスの現在の設定を理解し、同期が必要な変更を特定するために重要です。",
        "get_shadow_learning_next": "Shadowドキュメントを取得し、その構造を調査します",
        "getting_shadow": "🔍 Thing '{}'のShadowを取得中...",
        "shadow_retrieved": "✅ Shadow取得成功",
        "shadow_not_found": "📭 Shadowが見つかりません（まだ作成されていません）",
        "shadow_get_failed": "❌ Shadow取得に失敗しました: {}",
        "shadow_structure_title": "📊 Shadow構造:",
        "shadow_state_title": "状態:",
        "shadow_desired_title": "希望する状態:",
        "shadow_reported_title": "報告された状態:",
        "shadow_delta_title": "差分（Delta）:",
        "shadow_metadata_title": "メタデータ:",
        "shadow_version_title": "バージョン:",
        "shadow_timestamp_title": "タイムスタンプ:",
        "no_desired_state": "希望する状態なし",
        "no_reported_state": "報告された状態なし",
        "no_delta": "差分なし",
        "update_desired_learning_title": "📚 学習ポイント: 希望する状態の更新",
        "update_desired_learning_content": "希望する状態の更新により、デバイスが達成すべき目標設定を定義できます。デバイスは、この希望する状態と現在の報告された状態の差分を受信し、必要な変更を適用します。",
        "update_desired_learning_next": "希望する状態を更新し、デバイス同期を開始します",
        "enter_desired_state": "希望する状態をJSON形式で入力:",
        "example_desired_state": '例: {"temperature": 22, "humidity": 45}',
        "updating_desired_state": "🔄 希望する状態を更新中...",
        "desired_state_updated": "✅ 希望する状態が更新されました",
        "desired_update_failed": "❌ 希望する状態の更新に失敗しました: {}",
        "invalid_json": "❌ 無効なJSON形式です。もう一度試してください。",
        "update_reported_learning_title": "📚 学習ポイント: 報告された状態の更新",
        "update_reported_learning_content": "報告された状態の更新により、デバイスの現在の実際の状態を記録できます。これは通常、デバイス自体が行いますが、テスト目的でシミュレートできます。",
        "update_reported_learning_next": "報告された状態を更新し、デバイスの現在の状態を記録します",
        "enter_reported_state": "報告された状態をJSON形式で入力:",
        "example_reported_state": '例: {"temperature": 21, "humidity": 43}',
        "updating_reported_state": "🔄 報告された状態を更新中...",
        "reported_state_updated": "✅ 報告された状態が更新されました",
        "reported_update_failed": "❌ 報告された状態の更新に失敗しました: {}",
        "delete_shadow_learning_title": "📚 学習ポイント: Shadow削除",
        "delete_shadow_learning_content": "Shadow削除により、デバイスのすべての状態情報を完全に削除できます。これは、デバイスのリセットや再初期化に使用されます。削除後、新しいShadowドキュメントを作成できます。",
        "delete_shadow_learning_next": "Shadowドキュメントを削除し、状態をリセットします",
        "confirm_delete": "本当にThing '{}'のShadowを削除しますか？ (y/N): ",
        "delete_cancelled": "削除がキャンセルされました",
        "deleting_shadow": "🗑️ Shadowを削除中...",
        "shadow_deleted": "✅ Shadowが削除されました",
        "shadow_delete_failed": "❌ Shadow削除に失敗しました: {}",
        "debug_full_error": "🔍 デバッグ: 完全なエラーレスポンス:",
        "debug_full_traceback": "🔍 デバッグ: 完全なトレースバック:",
        "api_error": "❌ APIエラー:",
        "error": "❌ エラー:",
        "learning_moments": {
            "shadow_concepts": {
                "title": "📚 学習ポイント: Device Shadow概念",
                "content": "Device Shadowは、デバイスの状態を表すJSONドキュメントです。'desired'（希望する状態）、'reported'（報告された状態）、'delta'（差分）の3つの主要セクションがあります。これにより、デバイスがオフラインでも状態管理が可能になります。",
                "next": "Shadow操作を通じてこれらの概念を探索します",
            },
            "state_synchronization": {
                "title": "📚 学習ポイント: 状態同期",
                "content": "状態同期は、希望する状態と報告された状態の差分を通じて行われます。デバイスは差分を受信し、必要な変更を適用してから、新しい報告された状態を送信します。これにより、確実な状態管理が実現されます。",
                "next": "状態更新を通じて同期プロセスを体験します",
            },
            "version_control": {
                "title": "📚 学習ポイント: バージョン制御",
                "content": "各Shadow更新はバージョン番号を増加させます。これにより、競合状態を防ぎ、更新の順序を保証します。バージョン制御は、複数のアプリケーションが同じデバイスを管理する場合に重要です。",
                "next": "バージョン変更を観察しながら更新を実行します",
            },
            "debug_state_before": "🔍 デバッグ: 更新前の状態: {}",
            "debug_state_after": "🔍 デバッグ: 更新後の状態: {}",
        },
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
        "title": "🌟 Explorador de Device Shadow AWS IoT",
        "separator": "=" * 60,
        "aws_context_info": "🌍 Informações de Contexto AWS:",
        "account_id": "ID da Conta",
        "region": "Região",
        "aws_context_error": "⚠️ Não foi possível recuperar o contexto AWS:",
        "aws_credentials_reminder": "   Certifique-se de que as credenciais AWS estão configuradas",
        "description_intro": "Este script ensina conceitos de AWS IoT Device Shadow:",
        "shadow_concepts": [
            "• Serviço Device Shadow para sincronização de estado",
            "• Estrutura do documento Shadow (desejado vs reportado)",
            "• Tópicos MQTT para operações de shadow",
            "• Mensagens delta para diferenças de estado",
            "• Atualizações de shadow em tempo real e notificações",
            "• Detalhes completos da API para cada operação",
        ],
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Log aprimorado de mensagens MQTT",
            "• Análise completa de documentos shadow",
            "• Informações educacionais estendidas",
        ],
        "tip": "💡 Dica: Use a flag --debug ou -d para log aprimorado de shadow",
        "press_enter": "Pressione Enter para continuar...",
        "goodbye": "👋 Tchau!",
        "main_menu": "📋 Operações de Device Shadow:",
        "menu_options": [
            "1. Conectar ao Dispositivo e Inscrever-se nos Tópicos Shadow",
            "2. Obter Documento Shadow Atual",
            "3. Atualizar Estado Reportado do Shadow (Dispositivo → Nuvem)",
            "4. Atualizar Estado Desejado do Shadow (Nuvem → Dispositivo)",
            "5. Simular Mudanças de Estado do Dispositivo",
            "6. Ver Histórico de Mensagens Shadow",
            "7. Desconectar e Sair",
        ],
        "select_option": "Selecionar opção (1-7): ",
        "invalid_choice": "❌ Escolha inválida. Por favor selecione 1-7.",
        "learning_moments": {
            "shadow_foundation": {
                "title": "📚 MOMENTO DE APRENDIZADO: Fundamentos do Device Shadow",
                "content": "AWS IoT Device Shadow é um documento JSON que armazena e recupera informações do estado atual de um dispositivo. O shadow atua como intermediário entre dispositivos e aplicações, permitindo comunicação confiável mesmo quando dispositivos estão offline. Compreender conceitos de shadow é essencial para construir aplicações IoT robustas.",
                "next": "Exploraremos operações de shadow e comunicação MQTT",
            },
            "shadow_connection": {
                "title": "📚 MOMENTO DE APRENDIZADO: Conexão MQTT do Shadow",
                "content": "Device Shadows usam tópicos MQTT para comunicação. Cada operação de shadow (get, update, delete) tem tópicos de resposta correspondentes accepted/rejected. Tópicos delta notificam quando o estado desejado difere do reportado. Este modelo pub/sub permite comunicação bidirecional em tempo real entre dispositivos e aplicações.",
                "next": "Estabeleceremos conexão MQTT e nos inscreveremos nos tópicos shadow",
            },
        },
        "not_connected": "❌ Não conectado ao AWS IoT Core",
        "connection_established": "CONEXÃO SHADOW ESTABELECIDA",
        "shadow_get_accepted": "✅ SHADOW GET ACEITO",
        "shadow_get_rejected": "❌ SHADOW GET REJEITADO",
        "shadow_update_accepted": "✅ ATUALIZAÇÃO SHADOW ACEITA",
        "shadow_update_rejected": "❌ ATUALIZAÇÃO SHADOW REJEITADA",
        "shadow_delta_received": "🔄 DELTA SHADOW RECEBIDO",
        "operation_cancelled": "🛑 Operação cancelada",
        "no_things_found": "❌ Nenhum Thing encontrado. Por favor execute setup_sample_data.py primeiro",
        "available_devices": "📱 Dispositivos Disponíveis ({} encontrados):",
        "selected_device": "✅ Dispositivo selecionado:",
        "using_certificate": "✅ Usando certificado:",
        "certificate_files_found": "✅ Arquivos de certificado encontrados:",
        "certificate": "Certificado",
        "private_key": "Chave Privada",
        "connecting_to_iot": "🔄 Conectando ao AWS IoT Core...",
        "shadow_connection_params": "🔗 Parâmetros de Conexão Shadow:",
        "client_id": "ID do Cliente",
        "thing_name": "Nome do Thing",
        "endpoint": "Endpoint",
        "port": "Porta",
        "protocol": "Protocolo",
        "authentication": "Autenticação",
        "shadow_type": "Tipo de Shadow",
        "shadow_type_classic": "Clássico",
        "requesting_shadow_document": "📥 Solicitando Documento Shadow",
        "topic": "Tópico",
        "thing": "Thing",
        "shadow_get_request_sent": "✅ Solicitação GET do shadow enviada",
        "qos": "QoS",
        "packet_id": "ID do Pacote",
        "waiting_for_response": "⏳ Aguardando resposta em get/accepted ou get/rejected...",
        "shadow_message_received": "🌟 MENSAGEM SHADOW RECEBIDA",
        "direction": "Direção",
        "received": "RECEBIDO",
        "payload_size": "Tamanho do Payload",
        "timestamp": "Timestamp",
        "shadow_data": "Dados Shadow",
        "shadow_document_retrieved": "📋 Documento Shadow Recuperado:",
        "version": "Versão",
        "desired_state": "Estado Desejado",
        "reported_state": "Estado Reportado",
        "none": "Nenhum",
        "error_code": "Código de Erro",
        "message": "Mensagem",
        "shadow_doesnt_exist": "Shadow não existe ainda - será criado na próxima atualização",
        "new_version": "Nova Versão",
        "updated_desired": "Desejado Atualizado",
        "updated_reported": "Reportado Atualizado",
        "description": "Descrição",
        "desired_differs_reported": "Estado desejado difere do estado reportado",
        "changes_needed": "Mudanças Necessárias",
        "state_comparison": "🔍 Comparação de Estado:",
        "local_state": "Estado Local",
        "delta": "Delta",
        "desired": "Desejado",
        "differences_found": "⚠️  Diferenças Encontradas:",
        "apply_changes_prompt": "Aplicar essas mudanças ao dispositivo local? (s/N): ",
        "local_state_updated": "✅ Estado local atualizado com sucesso",
        "failed_update_local": "❌ Falha ao atualizar estado local",
        "changes_not_applied": "⏭️  Mudanças não aplicadas ao dispositivo local",
        "local_matches_desired": "✅ Estado local corresponde ao estado desejado - nenhuma mudança necessária",
        "automatically_reporting": "📡 Reportando automaticamente estado atualizado ao shadow...",
        "local_state_saved": "💾 Estado local salvo em:",
        "created_default_state": "📄 Arquivo de estado local padrão criado:",
        "default_state": "📋 Estado padrão:",
        "using_existing_state": "📄 Usando arquivo de estado local existente:",
        "current_local_state": "📋 Estado local atual:",
        "thank_you_message": "Obrigado por explorar AWS IoT Device Shadows!",
        "shadow_command_prompt": "🌟 Shadow> ",
        "unknown_command": "❌ Comando desconhecido: {}. Digite 'help' para comandos disponíveis.",
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
        "title": "🌟 AWS IoT Device Shadow 탐색기",
        "separator": "=" * 60,
        "aws_context_info": "🌍 AWS 컨텍스트 정보:",
        "account_id": "계정 ID",
        "region": "리전",
        "aws_context_error": "⚠️ AWS 컨텍스트를 검색할 수 없습니다:",
        "aws_credentials_reminder": "   AWS 자격 증명이 구성되어 있는지 확인하세요",
        "description_intro": "이 스크립트는 AWS IoT Device Shadow 개념을 가르칩니다:",
        "shadow_concepts": [
            "• 상태 동기화를 위한 Device Shadow 서비스",
            "• Shadow 문서 구조 (원하는 상태 vs 보고된 상태)",
            "• Shadow 작업을 위한 MQTT 주제",
            "• 상태 차이를 위한 델타 메시지",
            "• 실시간 Shadow 업데이트 및 알림",
            "• 각 작업에 대한 완전한 API 세부 정보",
        ],
        "debug_enabled": "🔍 디버그 모드 활성화",
        "debug_features": [
            "• 향상된 MQTT 메시지 로깅",
            "• 완전한 Shadow 문서 분석",
            "• 확장된 교육 정보",
        ],
        "tip": "💡 팁: 향상된 Shadow 로깅을 위해 --debug 또는 -d 플래그를 사용하세요",
        "press_enter": "계속하려면 Enter를 누르세요...",
        "goodbye": "👋 안녕히 가세요!",
        "main_menu": "📋 Device Shadow 작업:",
        "menu_options": [
            "1. 디바이스에 연결 및 Shadow 주제 구독",
            "2. 현재 Shadow 문서 가져오기",
            "3. Shadow 보고된 상태 업데이트 (디바이스 → 클라우드)",
            "4. Shadow 원하는 상태 업데이트 (클라우드 → 디바이스)",
            "5. 디바이스 상태 변경 시뮬레이션",
            "6. Shadow 메시지 기록 보기",
            "7. 연결 해제 및 종료",
        ],
        "select_option": "옵션 선택 (1-7): ",
        "invalid_choice": "❌ 잘못된 선택입니다. 1-7을 선택해주세요.",
        "not_connected": "❌ AWS IoT Core에 연결되지 않음",
        "connection_established": "SHADOW 연결 설정됨",
        "shadow_get_accepted": "✅ SHADOW GET 승인됨",
        "shadow_get_rejected": "❌ SHADOW GET 거부됨",
        "shadow_update_accepted": "✅ SHADOW 업데이트 승인됨",
        "shadow_update_rejected": "❌ SHADOW 업데이트 거부됨",
        "shadow_delta_received": "🔄 SHADOW 델타 수신됨",
        "operation_cancelled": "🛑 작업이 취소되었습니다",
        "no_things_found": "❌ Things를 찾을 수 없습니다. 먼저 setup_sample_data.py를 실행하세요",
        "available_devices": "📱 사용 가능한 디바이스 ({} 개 발견):",
        "selected_device": "✅ 선택된 디바이스:",
        "using_certificate": "✅ 인증서 사용:",
        "certificate_files_found": "✅ 인증서 파일 발견:",
        "certificate": "인증서",
        "private_key": "개인 키",
        "connecting_to_iot": "🔄 AWS IoT Core에 연결 중...",
        "shadow_connection_params": "🔗 Shadow 연결 매개변수:",
        "client_id": "클라이언트 ID",
        "thing_name": "Thing 이름",
        "endpoint": "엔드포인트",
        "port": "포트",
        "protocol": "프로토콜",
        "authentication": "인증",
        "shadow_type": "Shadow 유형",
        "shadow_type_classic": "클래식",
        "requesting_shadow_document": "📥 Shadow 문서 요청",
        "topic": "주제",
        "thing": "Thing",
        "shadow_get_request_sent": "✅ Shadow GET 요청 전송됨",
        "qos": "QoS",
        "packet_id": "패킷 ID",
        "waiting_for_response": "⏳ get/accepted 또는 get/rejected에서 응답 대기 중...",
        "shadow_message_received": "🌟 SHADOW 메시지 수신됨",
        "direction": "방향",
        "received": "수신됨",
        "payload_size": "페이로드 크기",
        "timestamp": "타임스탬프",
        "shadow_data": "Shadow 데이터",
        "shadow_document_retrieved": "📋 Shadow 문서 검색됨:",
        "version": "버전",
        "desired_state": "원하는 상태",
        "reported_state": "보고된 상태",
        "none": "없음",
        "error_code": "오류 코드",
        "message": "메시지",
        "shadow_doesnt_exist": "Shadow가 아직 존재하지 않습니다 - 다음 업데이트에서 생성됩니다",
        "new_version": "새 버전",
        "updated_desired": "업데이트된 원하는 상태",
        "updated_reported": "업데이트된 보고된 상태",
        "description": "설명",
        "desired_differs_reported": "원하는 상태가 보고된 상태와 다릅니다",
        "changes_needed": "필요한 변경사항",
        "state_comparison": "🔍 상태 비교:",
        "local_state": "로컬 상태",
        "delta": "델타",
        "desired": "원하는 상태",
        "differences_found": "⚠️  차이점 발견:",
        "apply_changes_prompt": "이러한 변경사항을 로컬 디바이스에 적용하시겠습니까? (y/N): ",
        "local_state_updated": "✅ 로컬 상태가 성공적으로 업데이트되었습니다",
        "failed_update_local": "❌ 로컬 상태 업데이트 실패",
        "changes_not_applied": "⏭️  변경사항이 로컬 디바이스에 적용되지 않았습니다",
        "local_matches_desired": "✅ 로컬 상태가 원하는 상태와 일치합니다 - 변경이 필요하지 않습니다",
        "automatically_reporting": "📡 업데이트된 상태를 Shadow에 자동으로 보고 중...",
        "local_state_saved": "💾 로컬 상태 저장됨:",
        "created_default_state": "📄 기본 로컬 상태 파일 생성됨:",
        "default_state": "📊 기본 상태:",
        "using_existing_state": "📄 기존 로컬 상태 파일 사용:",
        "current_local_state": "📊 현재 로컬 상태:",
        "thank_you_message": "AWS IoT Device Shadows를 탐색해 주셔서 감사합니다!",
        "shadow_command_prompt": "🌟 Shadow> ",
        "unknown_command": "❌ 알 수 없는 명령: {}. 사용 가능한 명령을 보려면 'help'를 입력하세요.",
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
                print("Selección inválida. Por favor selecciona 1-6.")
                print("無効な選択です。1-6を選択してください。")
                print("无效选择。请选择 1-6。")
                print("Escolha inválida. Por favor selecione 1-6.")
                print("잘못된 선택입니다. 1-6을 선택해주세요.")
        except KeyboardInterrupt:
            print("Goodbye! / ¡Adiós! / さようなら！ / 再见！ / Tchau! / 안녕히 가세요!")
            sys.exit(0)


def get_message(key, lang="en", category=None):
    """Get localized message"""
    # Check debug messages first
    debug_msg = MESSAGES.get("debug_messages", {}).get(lang, {}).get(key)
    if debug_msg:
        return debug_msg

    # Handle nested categories like workflow_titles
    if category:
        return MESSAGES.get(lang, MESSAGES["en"]).get(category, {}).get(key, key)

    return MESSAGES.get(lang, MESSAGES["en"]).get(key, key)


def get_learning_moment(moment_key, lang="en"):
    """Get localized learning moment"""
    return MESSAGES.get(lang, MESSAGES["en"]).get("learning_moments", {}).get(moment_key, {})


def print_learning_moment(moment_key, lang="en"):
    """Print a formatted learning moment"""
    moment = get_learning_moment(moment_key, lang)
    if moment:
        print(f"\n{moment.get('title', '')}")
        print(moment.get("content", ""))
        print(f"\n🔄 NEXT: {moment.get('next', '')}")
        print(f"\n{get_message('press_enter', lang)}")
        try:
            input()
        except KeyboardInterrupt:
            print(f"\n{get_message('goodbye', lang)}")
            sys.exit(0)


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


class DeviceShadowExplorer:
    def __init__(self):
        self.connection = None
        self.connected = False
        self.thing_name = None
        self.shadow_name = None  # Classic shadow uses None
        self.local_state_file = None
        self.received_messages = []
        self.message_lock = threading.Lock()
        self.debug_mode = DEBUG_MODE
        self.last_shadow_response = None

    def print_header(self, title):
        """Print formatted header"""
        print(f"\n🌟 {title}")
        print("=" * 60)

    def print_step(self, step, description):
        """Print step with formatting"""
        print(f"\n🔧 Step {step}: {description}")
        print("-" * 50)

    def print_shadow_details(self, message_type, details):
        """Print detailed Shadow protocol information"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n📊 Shadow {message_type} [{timestamp}]")
        print("-" * 40)

        for key, value in details.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"      {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")

    def get_iot_endpoint(self, debug=False):
        """Get AWS IoT endpoint for the account"""
        try:
            iot = boto3.client("iot")

            if debug:
                print(get_message("debug_calling_describe_endpoint", USER_LANG))
                print(get_message("debug_input_parameters", USER_LANG))

            response = iot.describe_endpoint(endpointType="iot:Data-ATS")
            endpoint = response["endpointAddress"]

            if debug:
                print(get_message("debug_api_response", USER_LANG).format(json.dumps(response, indent=2, default=str)))

            print(get_message("iot_endpoint_discovery", USER_LANG))
            print(f"   {get_message('endpoint_type', USER_LANG)}: {get_message('endpoint_type_ats', USER_LANG)}")
            print(f"   {get_message('endpoint_url', USER_LANG)}: {endpoint}")
            print(f"   {get_message('port_mqtt_tls', USER_LANG)}")
            print(f"   {get_message('protocol_mqtt', USER_LANG)}")

            return endpoint
        except Exception as e:
            print(f"{get_message('error_getting_endpoint', USER_LANG)} {str(e)}")
            if debug:
                import traceback

                print(get_message("debug_full_traceback", USER_LANG))
                traceback.print_exc()
            return None

    def select_device_and_certificate(self, debug=False):
        """Select a device and its certificate for Shadow operations"""
        try:
            iot = boto3.client("iot")

            # Get all Things
            if debug:
                print(get_message("debug_calling_list_things", USER_LANG))
                print(get_message("debug_input_params_none", USER_LANG))

            things_response = iot.list_things()
            things = things_response.get("things", [])

            if debug:
                print(get_message("debug_found_things", USER_LANG).format(len(things)))
                print(get_message("debug_thing_names", USER_LANG).format([t["thingName"] for t in things]))

            if not things:
                print(get_message("no_things_found", USER_LANG))
                return None, None, None

            print(f"\n{get_message('available_devices', USER_LANG).format(len(things))}")
            for i, thing in enumerate(things, 1):
                print(
                    f"   {i}. {thing['thingName']} ({get_message('type', USER_LANG)}: {thing.get('thingTypeName', get_message('none', USER_LANG))})"
                )

            while True:
                try:
                    choice = (
                        int(input(f"\n{get_message('select_option', USER_LANG).replace('(1-6)', f'(1-{len(things)})')}: ")) - 1
                    )
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
                print(get_message("debug_input_thing_name", USER_LANG).format(selected_thing))

            principals_response = iot.list_thing_principals(thingName=selected_thing)
            principals = principals_response.get("principals", [])
            cert_arns = [p for p in principals if "cert/" in p]

            if debug:
                print(get_message("debug_found_principals", USER_LANG).format(len(principals), len(cert_arns)))
                print(get_message("debug_cert_arns", USER_LANG).format(cert_arns))

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
                            print(get_message("invalid_selection_cert", USER_LANG))
                    except ValueError:
                        print(get_message("enter_valid_number", USER_LANG))

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
                print(f"   {get_message('looking_for_files', USER_LANG).format(cert_id)}")
                return None, None, None

            print(get_message("certificate_files_found", USER_LANG))
            print(f"   {get_message('certificate', USER_LANG)}: {cert_file}")
            print(f"   {get_message('private_key', USER_LANG)}: {key_file}")

            return selected_thing, cert_file, key_file

        except Exception as e:
            print(f"{get_message('error_selecting_device', USER_LANG)} {str(e)}")
            return None, None, None

    def setup_local_state_file(self, thing_name, debug=False):
        """Setup local state file for device shadow simulation"""
        # Validate thing_name to prevent path traversal
        if not re.match(r"^[a-zA-Z0-9_-]+$", thing_name):
            print(f"{get_message('invalid_thing_name', USER_LANG)} {thing_name}")
            return None

        cert_dir = os.path.join(os.getcwd(), "certificates", thing_name)
        # Validate the constructed path stays within certificates directory
        if not os.path.abspath(cert_dir).startswith(os.path.abspath(os.path.join(os.getcwd(), "certificates"))):
            print(f"{get_message('unsafe_path_detected', USER_LANG)} {thing_name}")
            return None

        state_file = os.path.join(cert_dir, "device_state.json")

        if debug:
            print(get_message("debug_setting_up_state", USER_LANG).format(state_file))
            print(get_message("debug_cert_directory", USER_LANG).format(cert_dir))
            print(get_message("debug_file_exists", USER_LANG).format(os.path.exists(state_file)))

        # Create default state if file doesn't exist
        if not os.path.exists(state_file):
            default_state = {
                "temperature": 22.5,
                "humidity": 45.0,
                "status": "online",
                "firmware_version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
            }

            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(default_state, f, indent=2)

            print(f"{get_message('created_default_state', USER_LANG)} {state_file}")
            print(f"{get_message('default_state', USER_LANG)} {json.dumps(default_state, indent=2)}")
            if debug:
                print(get_message("debug_created_new_state", USER_LANG).format(len(default_state)))
        else:
            print(f"{get_message('using_existing_state', USER_LANG)} {state_file}")
            with open(state_file, "r", encoding="utf-8") as f:
                current_state = json.load(f)
            print(f"{get_message('current_local_state', USER_LANG)} {json.dumps(current_state, indent=2)}")
            if debug:
                print(get_message("debug_loaded_existing_state", USER_LANG).format(len(current_state)))
                print(get_message("debug_file_size", USER_LANG).format(os.path.getsize(state_file)))

        self.local_state_file = state_file
        return state_file

    def load_local_state(self):
        """Load current local device state"""
        try:
            with open(self.local_state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{get_message('local_state_not_found', USER_LANG)} {self.local_state_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"{get_message('invalid_json_state', USER_LANG)} {str(e)}")
            return {}
        except PermissionError:
            print(f"{get_message('permission_denied_state', USER_LANG)} {self.local_state_file}")
            return {}
        except Exception as e:
            print(f"{get_message('unexpected_error_loading', USER_LANG)} {str(e)}")
            return {}

    def save_local_state(self, state):
        """Save device state to local file"""
        try:
            state["last_updated"] = datetime.now().isoformat()
            with open(self.local_state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            print(f"{get_message('local_state_saved', USER_LANG)} {self.local_state_file}")
            return True
        except PermissionError:
            print(f"{get_message('permission_denied_writing', USER_LANG)} {self.local_state_file}")
            return False
        except OSError as e:
            print(f"{get_message('filesystem_error_saving', USER_LANG)} {str(e)}")
            return False
        except TypeError as e:
            print(f"{get_message('invalid_state_data', USER_LANG)} {str(e)}")
            return False
        except Exception as e:
            print(f"{get_message('unexpected_error_saving', USER_LANG)} {str(e)}")
            return False

    def on_connection_interrupted(self, connection, error, **kwargs):
        """Callback for connection interruption"""
        self.print_shadow_details(
            get_message("connection_interrupted", USER_LANG),
            {
                get_message("error", USER_LANG): str(error),
                get_message("timestamp", USER_LANG): datetime.now().isoformat(),
                get_message("auto_reconnect", USER_LANG): get_message("sdk_will_reconnect", USER_LANG),
            },
        )
        self.connected = False

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        """Callback for connection resumption"""
        self.print_shadow_details(
            get_message("connection_resumed", USER_LANG),
            {
                get_message("return_code", USER_LANG): return_code,
                get_message("session_present", USER_LANG): session_present,
                get_message("timestamp", USER_LANG): datetime.now().isoformat(),
                get_message("status", USER_LANG): get_message("connection_restored", USER_LANG),
            },
        )
        self.connected = True

    def on_shadow_message_received(self, topic, payload, dup, qos, retain, **kwargs):
        """Callback for Shadow messages with comprehensive analysis"""
        try:
            # Parse shadow message
            try:
                shadow_data = json.loads(payload.decode("utf-8"))
                payload_display = json.dumps(shadow_data, indent=2)
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload_display = payload.decode("utf-8")
                shadow_data = {}

            message_info = {
                get_message("direction", USER_LANG): get_message("received", USER_LANG),
                get_message("topic", USER_LANG): topic,
                get_message("qos", USER_LANG): qos,
                get_message("payload_size", USER_LANG): f"{len(payload)} bytes",
                get_message("timestamp", USER_LANG): datetime.now().isoformat(),
                get_message("shadow_data", USER_LANG): shadow_data,
            }

            with self.message_lock:
                self.received_messages.append(message_info)
                # Store last response for shadow existence checking
                self.last_shadow_response = shadow_data

            # Immediate visual notification
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print("\n" + "=" * 70)
            print(f"{get_message('shadow_message_received', USER_LANG)} [{timestamp}]")
            print("=" * 70)

            if self.debug_mode:
                print(get_message("debug_raw_topic", USER_LANG).format(topic))
                print(get_message("debug_qos_duplicate", USER_LANG).format(qos, dup, retain))
                print(get_message("debug_payload_size", USER_LANG).format(len(payload)))
                print(get_message("debug_message_count", USER_LANG).format(len(self.received_messages)))

            # Analyze topic to determine message type
            if "get" in topic and "accepted" in topic:
                self.handle_shadow_get_accepted(shadow_data)
            elif "get" in topic and "rejected" in topic:
                self.handle_shadow_get_rejected(shadow_data)
            elif "update" in topic and "accepted" in topic:
                self.handle_shadow_update_accepted(shadow_data)
            elif "update" in topic and "rejected" in topic:
                self.handle_shadow_update_rejected(shadow_data)
            elif "update" in topic and "delta" in topic:
                self.handle_shadow_delta(shadow_data)
            else:
                print(f"📥 {get_message('topic', USER_LANG)}: {topic}")
                print(f"🏷️  {get_message('qos', USER_LANG)}: {qos}")
                print(f"📊 Payload: {payload_display}")
                if self.debug_mode:
                    print(get_message("debug_unrecognized_topic", USER_LANG))

            print("=" * 70)

        except Exception as e:
            print(f"\n{get_message('error_processing_message', USER_LANG)} {str(e)}")

    def handle_shadow_get_accepted(self, shadow_data):
        """Handle shadow get accepted response"""
        print(get_message("shadow_get_accepted", USER_LANG))
        if self.debug_mode:
            print(f"   📝 {get_message('topic', USER_LANG)}: $aws/things/{self.thing_name}/shadow/get/accepted")
        print(get_message("shadow_document_retrieved", USER_LANG))

        state = shadow_data.get("state", {})
        desired = state.get("desired", {})
        reported = state.get("reported", {})
        version = shadow_data.get("version", "Unknown")

        print(f"   📊 {get_message('version', USER_LANG)}: {version}")
        print(
            f"   🎯 {get_message('desired_state', USER_LANG)}: {json.dumps(desired, indent=6) if desired else get_message('none', USER_LANG)}"
        )
        print(
            f"   📡 {get_message('reported_state', USER_LANG)}: {json.dumps(reported, indent=6) if reported else get_message('none', USER_LANG)}"
        )

        # Compare with local state
        if desired:
            if self.debug_mode:
                print(get_message("debug_comparing_desired", USER_LANG))
                print(get_message("debug_desired_keys", USER_LANG).format(list(desired.keys())))
            self.compare_and_prompt_update(desired)
        elif self.debug_mode:
            print(get_message("debug_no_desired_state", USER_LANG))

    def handle_shadow_get_rejected(self, shadow_data):
        """Handle shadow get rejected response"""
        print(get_message("shadow_get_rejected", USER_LANG))
        if self.debug_mode:
            print(f"   📝 {get_message('topic', USER_LANG)}: $aws/things/{self.thing_name}/shadow/get/rejected")
        error_code = shadow_data.get("code", "Unknown")
        error_message = shadow_data.get("message", "No message")
        print(f"   🚫 {get_message('error_code', USER_LANG)}: {error_code}")
        print(f"   📝 {get_message('message', USER_LANG)}: {error_message}")

        # Store error code for shadow existence checking
        with self.message_lock:
            self.last_shadow_response = {"error_code": error_code, "error_message": error_message}

        if error_code == 404:
            print(f"   💡 {get_message('shadow_doesnt_exist', USER_LANG)}")
            if self.debug_mode:
                print(get_message("debug_normal_for_new", USER_LANG))
        elif self.debug_mode:
            print(get_message("debug_error_code_indicates", USER_LANG).format(error_code, error_message))

    def handle_shadow_update_accepted(self, shadow_data):
        """Handle shadow update accepted response"""
        print(get_message("shadow_update_accepted", USER_LANG))
        if self.debug_mode:
            print(f"   📝 {get_message('topic', USER_LANG)}: $aws/things/{self.thing_name}/shadow/update/accepted")
        state = shadow_data.get("state", {})
        version = shadow_data.get("version", "Unknown")
        timestamp = shadow_data.get("timestamp", "Unknown")

        print(f"   📊 {get_message('new_version', USER_LANG)}: {version}")
        print(f"   ⏰ {get_message('timestamp', USER_LANG)}: {timestamp}")
        if "desired" in state:
            print(f"   🎯 {get_message('updated_desired', USER_LANG)}: {json.dumps(state['desired'], indent=6)}")
        if "reported" in state:
            print(f"   📡 {get_message('updated_reported', USER_LANG)}: {json.dumps(state['reported'], indent=6)}")

    def handle_shadow_update_rejected(self, shadow_data):
        """Handle shadow update rejected response"""
        print(get_message("shadow_update_rejected", USER_LANG))
        if self.debug_mode:
            print(f"   📝 {get_message('topic', USER_LANG)}: $aws/things/{self.thing_name}/shadow/update/rejected")
        error_code = shadow_data.get("code", "Unknown")
        error_message = shadow_data.get("message", "No message")
        print(f"   🚫 {get_message('error_code', USER_LANG)}: {error_code}")
        print(f"   📝 {get_message('message', USER_LANG)}: {error_message}")

    def handle_shadow_delta(self, shadow_data):
        """Handle shadow delta message (desired != reported)"""
        print(get_message("shadow_delta_received", USER_LANG))
        if self.debug_mode:
            print(f"   📝 {get_message('topic', USER_LANG)}: $aws/things/{self.thing_name}/shadow/update/delta")
        print(f"   📝 {get_message('description', USER_LANG)}: {get_message('desired_differs_reported', USER_LANG)}")

        state = shadow_data.get("state", {})
        version = shadow_data.get("version", "Unknown")
        timestamp = shadow_data.get("timestamp", "Unknown")

        print(f"   📊 {get_message('version', USER_LANG)}: {version}")
        print(f"   ⏰ {get_message('timestamp', USER_LANG)}: {timestamp}")
        print(f"   🔄 {get_message('changes_needed', USER_LANG)}: {json.dumps(state, indent=6)}")

        # Prompt user to apply changes
        if self.debug_mode:
            print(get_message("debug_processing_delta", USER_LANG).format(len(state)))
            print(get_message("debug_delta_keys", USER_LANG).format(list(state.keys())))
        self.compare_and_prompt_update(state, is_delta=True)

    def compare_and_prompt_update(self, desired_state, is_delta=False):
        """Compare desired state with local state and prompt for updates"""
        local_state = self.load_local_state()

        if self.debug_mode:
            print(get_message("debug_loaded_local_state", USER_LANG).format(len(local_state)))
            print(get_message("debug_comparing_properties", USER_LANG).format(len(desired_state)))

        print(f"\n{get_message('state_comparison', USER_LANG)}")
        print(f"   📱 {get_message('local_state', USER_LANG)}: {json.dumps(local_state, indent=6)}")
        print(
            f"   {get_message('delta', USER_LANG) if is_delta else get_message('desired', USER_LANG)}: {json.dumps(desired_state, indent=6)}"
        )

        # Find differences
        differences = {}
        for key, desired_value in desired_state.items():
            local_value = local_state.get(key)
            if local_value != desired_value:
                differences[key] = {"local": local_value, "desired": desired_value}

        if differences:
            if self.debug_mode:
                print(get_message("debug_differences_found", USER_LANG).format(len(differences), len(desired_state)))
            print(f"\n{get_message('differences_found', USER_LANG)}")
            for key, diff in differences.items():
                print(f"   • {key}: {diff['local']} → {diff['desired']}")
                if self.debug_mode:
                    print(
                        get_message("debug_type_change", USER_LANG).format(
                            type(diff["local"]).__name__, type(diff["desired"]).__name__
                        )
                    )

            apply_changes = input(f"\n{get_message('apply_changes_prompt', USER_LANG)}").strip().lower()
            if apply_changes == "y":
                time.sleep(0.1)  # nosemgrep: arbitrary-sleep
                # Update local state
                for key, desired_value in desired_state.items():
                    local_state[key] = desired_value

                if self.save_local_state(local_state):
                    if self.debug_mode:
                        print(get_message("debug_updated_properties", USER_LANG).format(len(desired_state)))
                        print(get_message("debug_new_state_size", USER_LANG).format(len(local_state)))
                    print(get_message("local_state_updated", USER_LANG))

                    # Automatically report back to shadow (required for proper synchronization)
                    print(get_message("automatically_reporting", USER_LANG))
                    self.update_shadow_reported(local_state)
                    time.sleep(1.5)  # nosemgrep: arbitrary-sleep
                else:
                    print(get_message("failed_update_local", USER_LANG))
            else:
                print(get_message("changes_not_applied", USER_LANG))
        else:
            if self.debug_mode:
                print(get_message("debug_all_match", USER_LANG).format(len(desired_state)))
            print(get_message("local_matches_desired", USER_LANG))

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
                    client_id = f"{thing_name}-shadow-{uuid.uuid4().hex[:8]}"
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

    def connect_to_aws_iot(self, thing_name, cert_file, key_file, endpoint, debug=False):
        """Establish MQTT connection to AWS IoT Core for Shadow operations"""
        self.print_step(1, get_message("step_establishing_connection", USER_LANG))

        if debug:
            print(get_message("debug_shadow_connection_setup", USER_LANG))
            print(get_message("debug_thing_name", USER_LANG).format(thing_name))
            print(get_message("debug_cert_file", USER_LANG).format(cert_file))
            print(get_message("debug_private_key_file", USER_LANG).format(key_file))
            print(get_message("debug_endpoint", USER_LANG).format(endpoint))

        try:
            # Get client ID from user or auto-generate
            client_id = self.get_client_id(thing_name)
            if not client_id:
                return False

            print(get_message("shadow_connection_params", USER_LANG))
            print(f"   {get_message('client_id', USER_LANG)}: {client_id}")
            print(f"   {get_message('thing_name', USER_LANG)}: {thing_name}")
            print(f"   {get_message('endpoint', USER_LANG)}: {endpoint}")
            print(f"   {get_message('port', USER_LANG)}: 8883")
            print(f"   {get_message('protocol', USER_LANG)}: MQTT 3.1.1 over TLS")
            print(f"   {get_message('authentication', USER_LANG)}: X.509 Certificate")
            print(f"   {get_message('shadow_type', USER_LANG)}: {get_message('shadow_type_classic', USER_LANG)}")

            # Build MQTT connection
            self.connection = mqtt_connection_builder.mtls_from_path(
                endpoint=endpoint,
                port=8883,
                cert_filepath=cert_file,
                pri_key_filepath=key_file,
                client_id=client_id,
                clean_session=True,
                keep_alive_secs=30,
                on_connection_interrupted=self.on_connection_interrupted,
                on_connection_resumed=self.on_connection_resumed,
            )

            print(f"\n{get_message('connecting_to_iot', USER_LANG)}")
            connect_future = self.connection.connect()
            connection_result = connect_future.result()

            if debug:
                print(get_message("debug_connection_result", USER_LANG).format(connection_result))

            self.connected = True
            self.thing_name = thing_name

            self.print_shadow_details(
                get_message("connection_established", USER_LANG),
                {
                    get_message("status", USER_LANG): get_message("connection_status", USER_LANG),
                    get_message("client_id", USER_LANG): client_id,
                    get_message("thing_name", USER_LANG): thing_name,
                    get_message("endpoint", USER_LANG): endpoint,
                    get_message("shadow_type", USER_LANG): get_message("shadow_type_classic", USER_LANG),
                    get_message("clean_session", USER_LANG): True,
                    get_message("keep_alive", USER_LANG): "30 seconds",
                    get_message("tls_version", USER_LANG): "1.2",
                    get_message("certificate_auth", USER_LANG): "X.509 mutual TLS",
                },
            )

            return True

        except Exception as e:
            print(f"{get_message('shadow_connection_failed', USER_LANG)} {str(e)}")
            return False

    def subscribe_to_shadow_topics(self, debug=False):
        """Subscribe to all relevant shadow topics"""
        self.print_step(2, get_message("step_subscribing_topics", USER_LANG))

        if not self.connected:
            print(get_message("not_connected", USER_LANG))
            return False

        # Shadow topic patterns for classic shadow
        shadow_topics = [
            f"$aws/things/{self.thing_name}/shadow/get/accepted",
            f"$aws/things/{self.thing_name}/shadow/get/rejected",
            f"$aws/things/{self.thing_name}/shadow/update/accepted",
            f"$aws/things/{self.thing_name}/shadow/update/rejected",
            f"$aws/things/{self.thing_name}/shadow/update/delta",
        ]

        print(f"{get_message('shadow_topics_for_thing', USER_LANG)} {self.thing_name}")
        print(get_message("classic_shadow_topics", USER_LANG))

        success_count = 0
        for topic in shadow_topics:
            try:
                if debug:
                    print(get_message("debug_subscribing_topic", USER_LANG).format(topic))

                subscribe_future, packet_id = self.connection.subscribe(
                    topic=topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=self.on_shadow_message_received
                )

                subscribe_future.result()

                print(f"   ✅ {topic}")
                success_count += 1

                if debug:
                    print(get_message("debug_subscription_successful", USER_LANG).format(packet_id))

            except Exception as e:
                print(f"   ❌ {topic} - Error: {str(e)}")

        if success_count == len(shadow_topics):
            print(f"\n{get_message('subscription_successful', USER_LANG).format(success_count)}")

            print(f"\n{get_message('shadow_topic_explanations', USER_LANG)}")
            print(f"   {get_message('topic_get_accepted', USER_LANG)}")
            print(f"   {get_message('topic_get_rejected', USER_LANG)}")
            print(f"   {get_message('topic_update_accepted', USER_LANG)}")
            print(f"   {get_message('topic_update_rejected', USER_LANG)}")
            print(f"   {get_message('topic_update_delta', USER_LANG)}")

            return True
        else:
            print(get_message("subscription_partial", USER_LANG).format(success_count, len(shadow_topics)))
            return False

    def get_shadow_document(self, debug=False, wait_for_response=False):
        """Request the current shadow document"""
        if not self.connected:
            print(get_message("not_connected", USER_LANG))
            return False

        try:
            get_topic = f"$aws/things/{self.thing_name}/shadow/get"

            print(f"\n{get_message('requesting_shadow_document', USER_LANG)}")
            print(f"   {get_message('topic', USER_LANG)}: {get_topic}")
            print(f"   {get_message('thing', USER_LANG)}: {self.thing_name}")
            print(f"   {get_message('shadow_type', USER_LANG)}: {get_message('shadow_type_classic', USER_LANG)}")

            if debug:
                print(get_message("debug_publishing_shadow_get", USER_LANG))
                print(get_message("debug_topic", USER_LANG).format(get_topic))
                print(get_message("debug_payload_empty", USER_LANG))

            # Shadow get requests have empty payload
            publish_future, packet_id = self.connection.publish(topic=get_topic, payload="", qos=mqtt.QoS.AT_LEAST_ONCE)

            # Non-blocking publish - don't wait for result
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{get_message('shadow_get_request_sent', USER_LANG)} [{timestamp}]")
            print(f"   📤 {get_message('topic', USER_LANG)}: {get_topic}")
            print(f"   🏷️  {get_message('qos', USER_LANG)}: 1 | {get_message('packet_id', USER_LANG)}: {packet_id}")
            print(f"   {get_message('waiting_for_response', USER_LANG)}")

            return True

        except Exception as e:
            print(f"{get_message('failed_request_shadow', USER_LANG)} {str(e)}")
            return False

    def update_shadow_reported(self, reported_state, debug=False):
        """Update the reported state in the shadow"""
        if not self.connected:
            print(get_message("not_connected", USER_LANG))
            return False

        try:
            update_topic = f"$aws/things/{self.thing_name}/shadow/update"

            print(f"\n{get_message('updating_shadow_reported', USER_LANG)}")
            print(f"\n{get_message('reported_state_update', USER_LANG)}")
            print(f"   {get_message('current_local_state_label', USER_LANG)}: {json.dumps(reported_state, indent=2)}")

            # Create shadow update payload
            shadow_update = {"state": {"reported": reported_state}}

            print(f"   {get_message('shadow_update_payload', USER_LANG)}: {json.dumps(shadow_update, indent=2)}")

            payload = json.dumps(shadow_update)

            if debug:
                print(get_message("debug_publishing_shadow_update", USER_LANG))
                print(get_message("debug_topic", USER_LANG).format(update_topic))
                print(get_message("debug_payload_json", USER_LANG).format(json.dumps(shadow_update, indent=2)))
                print(get_message("debug_update_type", USER_LANG).format("reported"))

            publish_future, packet_id = self.connection.publish(
                topic=update_topic, payload=payload, qos=mqtt.QoS.AT_LEAST_ONCE
            )

            # Non-blocking publish - don't wait for result
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{get_message('shadow_update_sent', USER_LANG)} [{timestamp}]")
            print(f"   📤 {get_message('topic', USER_LANG)}: {update_topic}")
            print(f"   🏷️  {get_message('qos', USER_LANG)}: 1 | {get_message('packet_id', USER_LANG)}: {packet_id}")
            print(f"   {get_message('waiting_for_response', USER_LANG)}")

            return True

        except Exception as e:
            print(f"{get_message('failed_update_reported', USER_LANG)} {str(e)}")
            return False

    def update_shadow_desired(self, desired_state, debug=False):
        """Update the desired state in the shadow (simulates cloud/app request)"""
        if not self.connected:
            print(get_message("not_connected", USER_LANG))
            return False

        try:
            update_topic = f"$aws/things/{self.thing_name}/shadow/update"

            print(f"\n{get_message('updating_shadow_desired', USER_LANG)}")
            print(f"\n{get_message('desired_state_update', USER_LANG)}")
            print(f"   {get_message('desired_state_to_set', USER_LANG)}: {json.dumps(desired_state, indent=2)}")

            # Create shadow update payload
            shadow_update = {"state": {"desired": desired_state}}

            payload = json.dumps(shadow_update)

            print(f"   {get_message('shadow_update_payload', USER_LANG)}: {json.dumps(shadow_update, indent=2)}")
            print(f"   {get_message('topic', USER_LANG)}: {update_topic}")
            print(f"   {get_message('thing', USER_LANG)}: {self.thing_name}")
            if debug:
                print(get_message("debug_publishing_shadow_update", USER_LANG))
                print(get_message("debug_topic", USER_LANG).format(update_topic))
                print(get_message("debug_payload_json", USER_LANG).format(json.dumps(shadow_update, indent=2)))
                print(get_message("debug_update_type", USER_LANG).format("desired"))

            publish_future, packet_id = self.connection.publish(
                topic=update_topic, payload=payload, qos=mqtt.QoS.AT_LEAST_ONCE
            )

            # Non-blocking publish - don't wait for result
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"{get_message('shadow_update_desired_sent', USER_LANG)} [{timestamp}]")
            print(f"   📤 {get_message('topic', USER_LANG)}: {update_topic}")
            print(f"   🏷️  {get_message('qos', USER_LANG)}: 1 | {get_message('packet_id', USER_LANG)}: {packet_id}")
            print(f"   {get_message('waiting_for_response', USER_LANG)}")

            return True

        except Exception as e:
            print(f"{get_message('failed_update_desired', USER_LANG)} {str(e)}")
            return False

    def run_interactive_menu(self):
        """Run the interactive menu system"""
        connected = False
        start_time = time.time()

        while True:
            try:
                print(f"\n{get_message('main_menu', USER_LANG)}")
                for option in get_message("menu_options", USER_LANG):
                    print(f"   {option}")

                choice = input(f"\n{get_message('select_option', USER_LANG)}")

                if choice == "1":
                    if not connected:
                        print_learning_moment("shadow_connection", USER_LANG)

                        # Get IoT endpoint
                        endpoint = self.get_iot_endpoint(debug=self.debug_mode)
                        if not endpoint:
                            continue

                        # Select device and certificate
                        thing_name, cert_file, key_file = self.select_device_and_certificate(debug=self.debug_mode)
                        if not thing_name:
                            continue

                        # Setup local state file
                        self.setup_local_state_file(thing_name, debug=self.debug_mode)

                        # Connect to AWS IoT
                        if self.connect_to_aws_iot(thing_name, cert_file, key_file, endpoint, debug=self.debug_mode):
                            # Subscribe to shadow topics
                            if self.subscribe_to_shadow_topics(debug=self.debug_mode):
                                connected = True
                                start_time = time.time()
                                print(f"\n✅ {get_message('connection_established', USER_LANG)}")
                            else:
                                print("\n❌ Failed to subscribe to shadow topics")
                        else:
                            print("\n❌ Failed to connect to AWS IoT")
                    else:
                        print("\n✅ Already connected to AWS IoT Core")

                elif choice == "2":
                    if not connected:
                        print(f"\n❌ {get_message('not_connected', USER_LANG)}")
                        print("💡 Please connect first (option 1)")
                        continue

                    print_learning_moment("shadow_document", USER_LANG)
                    self.get_shadow_document(debug=self.debug_mode)

                elif choice == "3":
                    if not connected:
                        print(f"\n❌ {get_message('not_connected', USER_LANG)}")
                        print("💡 Please connect first (option 1)")
                        continue

                    print_learning_moment("reported_state", USER_LANG)
                    local_state = self.load_local_state()
                    self.update_shadow_reported(local_state, debug=self.debug_mode)

                elif choice == "4":
                    if not connected:
                        print(f"\n❌ {get_message('not_connected', USER_LANG)}")
                        print("💡 Please connect first (option 1)")
                        continue

                    print_learning_moment("desired_state", USER_LANG)
                    self.update_shadow_desired_interactive()

                elif choice == "5":
                    if not connected:
                        print(f"\n❌ {get_message('not_connected', USER_LANG)}")
                        print("💡 Please connect first (option 1)")
                        continue

                    print_learning_moment("state_simulation", USER_LANG)
                    self.simulate_device_state_changes()

                elif choice == "6":
                    if not connected:
                        print(f"\n❌ {get_message('not_connected', USER_LANG)}")
                        print("💡 Please connect first (option 1)")
                        continue

                    self.view_shadow_message_history()

                elif choice == "7":
                    if connected:
                        self.disconnect_and_summarize(start_time)
                    print(f"\n{get_message('goodbye', USER_LANG)}")
                    break

                else:
                    print(get_message("invalid_choice", USER_LANG))

            except KeyboardInterrupt:
                print(f"\n\n{get_message('operation_cancelled', USER_LANG)}")
                if connected:
                    self.disconnect_and_summarize(start_time)
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                if self.debug_mode:
                    import traceback

                    traceback.print_exc()

    def run_auto_connect_and_interactive(self):
        """Auto-connect and run interactive shadow management"""
        print_learning_moment("shadow_connection", USER_LANG)

        # Get IoT endpoint
        endpoint = self.get_iot_endpoint(debug=self.debug_mode)
        if not endpoint:
            print("❌ Failed to get IoT endpoint")
            return

        # Select device and certificate
        thing_name, cert_file, key_file = self.select_device_and_certificate(debug=self.debug_mode)
        if not thing_name:
            print("❌ Failed to select device and certificate")
            return

        # Setup local state file
        self.setup_local_state_file(thing_name, debug=self.debug_mode)

        # Connect to AWS IoT
        if not self.connect_to_aws_iot(thing_name, cert_file, key_file, endpoint, debug=self.debug_mode):
            print("❌ Failed to connect to AWS IoT")
            return

        # Subscribe to shadow topics
        if not self.subscribe_to_shadow_topics(debug=self.debug_mode):
            print("❌ Failed to subscribe to shadow topics")
            return

        print(f"\n✅ {get_message('connection_established', USER_LANG)}")

        # Check if shadow exists, create if it doesn't
        self.ensure_shadow_exists()

        # Go directly into interactive shadow management
        self.interactive_shadow_management()

    def ensure_shadow_exists(self):
        """Ensure shadow exists by creating it if necessary"""
        print(f"\n🔍 {get_message('checking_shadow_exists', USER_LANG).format(self.thing_name)}")

        # Try to get the shadow first
        shadow_exists = False

        try:
            # Send get request and wait for response
            self.get_shadow_document(debug=self.debug_mode, wait_for_response=True)

            # Wait a moment for the response
            time.sleep(2)  # nosemgrep: arbitrary-sleep

            # Check if we got a successful response
            if hasattr(self, "last_shadow_response") and self.last_shadow_response:
                if "error_code" not in self.last_shadow_response or self.last_shadow_response.get("error_code") != 404:
                    shadow_exists = True

        except Exception as e:
            print(f"⚠️ Error checking shadow existence: {str(e)}")

        if not shadow_exists:
            print(f"📝 {get_message('creating_initial_shadow', USER_LANG)}")
            print(f"💡 {get_message('shadow_creation_normal', USER_LANG)}")

            # Report current local state to create the shadow
            try:
                # Load local state and report it to create the shadow
                local_state = self.load_local_state()
                if local_state:
                    self.update_shadow_reported(local_state, debug=self.debug_mode)
                else:
                    # Create a basic initial state if no local state exists
                    initial_state = {"temperature": 22.5, "humidity": 45.0, "status": "online", "firmware_version": "1.0.0"}
                    self.update_shadow_reported(initial_state, debug=self.debug_mode)
                print(f"✅ {get_message('initial_shadow_created', USER_LANG)}")

                # Wait a moment for the shadow to be created
                time.sleep(3)  # nosemgrep: arbitrary-sleep

                # Now get the shadow to confirm it exists
                print(f"🔄 {get_message('retrieving_new_shadow', USER_LANG)}")
                self.get_shadow_document(debug=self.debug_mode)

            except Exception as e:
                print(f"❌ Error creating initial shadow: {str(e)}")
        else:
            print(f"✅ {get_message('shadow_already_exists', USER_LANG)}")

    def update_shadow_desired_interactive(self):
        """Interactive desired state update"""
        print(f"\n{get_message('updating_shadow_desired', USER_LANG)}")

        property_name = input(get_message("enter_property_name", USER_LANG)).strip()
        if not property_name:
            print(get_message("property_name_required", USER_LANG))
            return

        property_value = input(get_message("enter_property_value", USER_LANG)).strip()
        if not property_value:
            print(get_message("property_value_required", USER_LANG))
            return

        # Try to convert to appropriate type
        try:
            if property_value.lower() in ["true", "false"]:
                property_value = property_value.lower() == "true"
            elif property_value.isdigit():
                property_value = int(property_value)
            elif "." in property_value and property_value.replace(".", "").isdigit():
                property_value = float(property_value)
        except (ValueError, TypeError):
            pass  # Keep as string

        desired_state = {property_name: property_value}

        print(f"\n{get_message('desired_state_to_set', USER_LANG)}:")
        print(f"   {get_message('property', USER_LANG)}: {property_name}")
        print(f"   {get_message('value', USER_LANG)}: {property_value}")

        self.update_shadow_desired(desired_state, debug=self.debug_mode)

    def simulate_device_state_changes(self):
        """Simulate device state changes"""
        print(f"\n{get_message('simulating_device_changes', USER_LANG)}")
        print(f"\n{get_message('simulation_options', USER_LANG)}")

        options = [
            get_message("temperature_change", USER_LANG),
            get_message("humidity_change", USER_LANG),
            get_message("status_toggle", USER_LANG),
            get_message("firmware_update", USER_LANG),
            get_message("custom_property", USER_LANG),
        ]

        for option in options:
            print(f"   {option}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_simulation', USER_LANG)}"))
                if 1 <= choice <= 5:
                    break
                else:
                    print(get_message("invalid_simulation", USER_LANG))
            except ValueError:
                print(get_message("enter_valid_number", USER_LANG))
            except KeyboardInterrupt:
                print(f"\n{get_message('operation_cancelled', USER_LANG)}")
                return

        local_state = self.load_local_state()
        old_state = local_state.copy()

        if choice == 1:  # Temperature change
            import random

            old_temp = local_state.get("temperature", 22.5)
            new_temp = round(old_temp + random.uniform(-5, 5), 1)
            local_state["temperature"] = new_temp
            print(get_message("temperature_changed", USER_LANG).format(old_temp, new_temp))

        elif choice == 2:  # Humidity change
            import random

            old_humidity = local_state.get("humidity", 45.0)
            new_humidity = round(max(0, min(100, old_humidity + random.uniform(-10, 10))), 1)
            local_state["humidity"] = new_humidity
            print(get_message("humidity_changed", USER_LANG).format(old_humidity, new_humidity))

        elif choice == 3:  # Status toggle
            old_status = local_state.get("status", "online")
            new_status = "offline" if old_status == "online" else "online"
            local_state["status"] = new_status
            print(get_message("status_changed", USER_LANG).format(old_status, new_status))

        elif choice == 4:  # Firmware update
            old_version = local_state.get("firmware_version", "1.0.0")
            version_parts = old_version.split(".")
            if len(version_parts) >= 3:
                patch = int(version_parts[2]) + 1
                new_version = f"{version_parts[0]}.{version_parts[1]}.{patch}"
            else:
                new_version = "1.0.1"
            local_state["firmware_version"] = new_version
            print(get_message("firmware_updated", USER_LANG).format(old_version, new_version))

        elif choice == 5:  # Custom property
            prop_name = input(get_message("enter_property_name", USER_LANG)).strip()
            if not prop_name:
                print(get_message("property_name_required", USER_LANG))
                return

            prop_value = input(get_message("enter_property_value", USER_LANG)).strip()
            if not prop_value:
                print(get_message("property_value_required", USER_LANG))
                return

            old_value = local_state.get(prop_name, "None")
            local_state[prop_name] = prop_value
            print(get_message("custom_property_changed", USER_LANG).format(prop_name, old_value, prop_value))

        # Show summary
        print(f"\n{get_message('state_change_summary', USER_LANG)}")
        for key in local_state:
            if key in old_state and old_state[key] != local_state[key]:
                print(f"   • {key}: {old_state[key]} → {local_state[key]}")

        # Save and report
        if self.save_local_state(local_state):
            print(get_message("local_state_updated_sim", USER_LANG))
            print(get_message("reporting_to_shadow", USER_LANG))
            self.update_shadow_reported(local_state, debug=self.debug_mode)
            print(get_message("simulation_complete", USER_LANG))

    def view_shadow_message_history(self):
        """View shadow message history"""
        print(f"\n{get_message('viewing_message_history', USER_LANG)}")

        with self.message_lock:
            if not self.received_messages:
                print(get_message("no_messages_received", USER_LANG))
                print(get_message("try_other_operations", USER_LANG))
                return

            print(f"\n{get_message('message_history', USER_LANG).format(len(self.received_messages))}")

            for i, msg in enumerate(self.received_messages[-10:], 1):  # Show last 10
                timestamp = msg.get("Timestamp", "").split("T")[1][:8] if "T" in msg.get("Timestamp", "") else "Unknown"
                topic = msg.get("Topic", "Unknown")
                topic_type = topic.split("/")[-1] if "/" in topic else topic

                print(f"\n   {i}. [{timestamp}] {topic_type}")
                print(f"      {get_message('topic', USER_LANG)}: {topic}")
                print(f"      {get_message('direction', USER_LANG)}: {msg.get('Direction', 'Unknown')}")

                if msg.get("Shadow Data"):
                    shadow_data = str(msg["Shadow Data"])
                    if len(shadow_data) > 100:
                        shadow_data = shadow_data[:100] + "..."
                    print(f"      {get_message('shadow_data', USER_LANG)}: {shadow_data}")

        # Ask if user wants to clear history
        clear_choice = input(f"\n{get_message('clear_history_prompt', USER_LANG)}").strip().lower()
        if clear_choice == "y":
            with self.message_lock:
                self.received_messages.clear()
            print(get_message("history_cleared", USER_LANG))
        else:
            print(get_message("history_not_cleared", USER_LANG))

    def disconnect_and_summarize(self, start_time):
        """Disconnect and show session summary"""
        print(f"\n{get_message('disconnecting_from_iot', USER_LANG)}")

        if self.connection and self.connected:
            try:
                disconnect_future = self.connection.disconnect()
                disconnect_future.result()
                self.connected = False
            except Exception as e:
                print(f"❌ Error during disconnect: {str(e)}")

        print(get_message("disconnection_complete", USER_LANG))

        # Show session summary
        duration = int(time.time() - start_time)
        minutes = duration // 60
        seconds = duration % 60

        print(f"\n{get_message('session_summary', USER_LANG)}")
        print(f"   {get_message('total_messages', USER_LANG)}: {len(self.received_messages)}")
        print(f"   {get_message('connection_duration', USER_LANG)}: {minutes}m {seconds}s")
        print(f"   {get_message('shadow_operations', USER_LANG)}: Multiple")

        print(f"\n{get_message('thank_you_message', USER_LANG)}")
        print(f"\n{get_message('next_steps_suggestions', USER_LANG)}")
        for suggestion in [
            get_message("explore_iot_rules", USER_LANG),
            get_message("try_mqtt_client", USER_LANG),
            get_message("check_registry", USER_LANG),
        ]:
            print(f"   {suggestion}")

    def interactive_shadow_management(self):
        """Interactive shadow management interface"""
        self.print_step(3, get_message("step_simulating_changes", USER_LANG))

        print(f"💡 {get_message('shadow_concepts', USER_LANG)[0].replace('•', '').strip()}:")
        print(f"   • {get_message('desired_state', USER_LANG)} represents what the device should be")
        print(f"   • {get_message('reported_state', USER_LANG)} represents what the device currently is")
        print(
            f"   • {get_message('topic_update_delta', USER_LANG).replace('• update/delta - ', '').replace(' (action needed)', '')} occur when desired ≠ reported"
        )
        print("   • Local file simulates actual device state")

        # Initial shadow get
        print("\n🔄 Getting initial shadow state...")
        self.get_shadow_document(debug=self.debug_mode)

        # Interactive loop
        print("\n🎮 Interactive Shadow Management Mode")
        print("💡 Shadow messages will appear immediately when received!")

        print("\nCommands:")
        print("   • 'get' - Request current shadow document")
        print("   • 'local' - Show current local device state")
        print("   • 'edit' - Edit local device state")
        print("   • 'report' - Report current local state to shadow")
        print("   • 'desire <key=value> [key=value...]' - Set desired state (simulate cloud)")
        print("   • 'status' - Show connection and shadow status")
        print("   • 'messages' - Show shadow message history")
        print("   • 'debug' - Show connection diagnostics")
        print("   • 'help' - Show this help")
        print("   • 'quit' - Exit")
        print("\n" + "=" * 60)

        while True:
            try:
                command = input(f"\n{get_message('shadow_command_prompt', USER_LANG)}").strip()

                if not command:
                    continue

                parts = command.split(" ", 1)
                cmd = parts[0].lower()

                if cmd == "quit":
                    break

                elif cmd == "help":
                    print(f"\n{get_message('available_commands', USER_LANG)}")
                    print(get_message("get_command", USER_LANG))
                    print(get_message("local_command", USER_LANG))
                    print(get_message("edit_command", USER_LANG))
                    print(get_message("report_command", USER_LANG))
                    print(get_message("desire_command", USER_LANG))
                    print(get_message("status_command", USER_LANG))
                    print(get_message("messages_command", USER_LANG))
                    print(get_message("debug_command", USER_LANG))
                    print(get_message("quit_command", USER_LANG))
                    print(f"\n{get_message('example_desire', USER_LANG)}")

                elif cmd == "get":
                    print("\n📚 LEARNING MOMENT: Shadow Document Retrieval")
                    print(
                        "Getting the shadow document retrieves the complete JSON state including desired, reported, and metadata. This shows the current synchronization status between your application's intentions (desired) and the device's actual state (reported). The version number helps track changes."
                    )
                    print("\n🔄 NEXT: Retrieving the current shadow document...")
                    time.sleep(1)  # Brief pause instead of blocking input  # nosemgrep: arbitrary-sleep

                    self.get_shadow_document(debug=self.debug_mode)
                    time.sleep(0.5)  # nosemgrep: arbitrary-sleep

                elif cmd == "local":
                    local_state = self.load_local_state()
                    print(f"\n{get_message('current_local_device_state', USER_LANG)}")
                    print(f"{json.dumps(local_state, indent=2)}")

                elif cmd == "edit":
                    self.edit_local_state()

                elif cmd == "report":
                    print("\n📚 LEARNING MOMENT: Device State Reporting")
                    print(
                        "Reporting state updates the shadow's 'reported' section with the device's current status. This is how devices communicate their actual state to applications. The shadow service automatically calculates deltas when reported state differs from desired state."
                    )
                    print("\n🔄 NEXT: Reporting local device state to the shadow...")
                    time.sleep(1)  # Brief pause instead of blocking input  # nosemgrep: arbitrary-sleep

                    local_state = self.load_local_state()
                    print("\n📡 Reporting local state to shadow...")
                    self.update_shadow_reported(local_state, debug=self.debug_mode)
                    time.sleep(0.5)  # nosemgrep: arbitrary-sleep

                elif cmd == "desire":
                    if len(parts) < 2:
                        print(f"   {get_message('usage_desire', USER_LANG)}")
                        print(f"   {get_message('example_desire_usage', USER_LANG)}")
                    else:
                        print("\n📚 LEARNING MOMENT: Desired State Management")
                        print(
                            "Setting desired state simulates how applications or cloud services request changes to device configuration. The shadow service stores these requests and notifies devices through delta messages when desired state differs from reported state. This enables remote device control."
                        )
                        print("\n🔄 NEXT: Setting desired state to trigger device changes...")
                        time.sleep(1)  # Brief pause instead of blocking input  # nosemgrep: arbitrary-sleep

                    # Parse key=value pairs
                    desired_updates = {}
                    for pair in parts[1].split():
                        if "=" in pair:
                            key, value = pair.split("=", 1)
                            # Try to convert to appropriate type
                            try:
                                if value.lower() in ["true", "false"]:
                                    desired_updates[key] = value.lower() == "true"
                                elif value.isdigit():
                                    desired_updates[key] = int(value)
                                elif "." in value and value.replace(".", "").isdigit():
                                    desired_updates[key] = float(value)
                                else:
                                    desired_updates[key] = value
                            except (ValueError, TypeError):
                                desired_updates[key] = value

                    if desired_updates:
                        print(get_message("setting_desired_state", USER_LANG).format(json.dumps(desired_updates, indent=2)))
                        self.update_shadow_desired(desired_updates, debug=self.debug_mode)
                        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
                    else:
                        print(f"   {get_message('no_valid_pairs', USER_LANG)}")

                elif cmd == "status":
                    print(f"\n{get_message('shadow_connection_status', USER_LANG)}")
                    print(
                        f"   {get_message('connected', USER_LANG)}: {get_message('yes', USER_LANG) if self.connected else get_message('no', USER_LANG)}"
                    )
                    print(f"   {get_message('thing_name', USER_LANG)}: {self.thing_name}")
                    print(f"   {get_message('shadow_type', USER_LANG)}: {get_message('shadow_type_classic', USER_LANG)}")
                    print(f"   Local State File: {self.local_state_file}")
                    print(f"   Messages Received: {len(self.received_messages)}")

                elif cmd == "messages":
                    print(f"\n{get_message('shadow_message_history', USER_LANG)}")
                    with self.message_lock:
                        for msg in self.received_messages[-10:]:  # Show last 10 messages
                            timestamp = msg["Timestamp"].split("T")[1][:8]
                            topic_type = msg["Topic"].split("/")[-1]
                            print(f"   📥 [{timestamp}] {topic_type}")
                            if msg.get("Shadow Data"):
                                shadow_summary = str(msg["Shadow Data"])[:100]
                                print(f"      {shadow_summary}{'...' if len(str(msg['Shadow Data'])) > 100 else ''}")

                elif cmd == "debug":
                    self.show_shadow_diagnostics()

                else:
                    print(get_message("unknown_command", USER_LANG).format(cmd))

            except KeyboardInterrupt:
                print("\n\n🛑 Interrupted by user")
                break
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

    def edit_local_state(self):
        """Interactive local state editor"""
        local_state = self.load_local_state()

        print(f"\n{get_message('edit_local_state_title', USER_LANG)}")
        print(f"{get_message('current_state', USER_LANG)} {json.dumps(local_state, indent=2)}")
        print(f"\n{get_message('options', USER_LANG)}")
        print(get_message("edit_individual_values", USER_LANG))
        print(get_message("replace_entire_state", USER_LANG))
        print(get_message("cancel", USER_LANG))

        while True:
            choice = input(f"\n{get_message('select_option_1_3', USER_LANG)}").strip()

            if choice == "1":
                # Edit individual values
                print(f"\n{get_message('current_values', USER_LANG)}")
                keys = list(local_state.keys())
                for i, key in enumerate(keys, 1):
                    print(f"   {i}. {key}: {local_state[key]}")

                print(f"   {len(keys) + 1}. {get_message('add_new_key', USER_LANG)}")
                print(f"   {len(keys) + 2}. {get_message('done_editing', USER_LANG)}")

                while True:
                    try:
                        edit_choice = int(input(f"\n{get_message('select_item_to_edit', USER_LANG).format(len(keys) + 2)}"))

                        if 1 <= edit_choice <= len(keys):
                            # Edit existing key
                            key = keys[edit_choice - 1]
                            current_value = local_state[key]
                            print(f"\n{get_message('editing_key', USER_LANG).format(key, current_value)}")
                            new_value = input(get_message("new_value_prompt", USER_LANG)).strip()

                            if new_value:
                                # Try to convert to appropriate type
                                try:
                                    if new_value.lower() in ["true", "false"]:
                                        local_state[key] = new_value.lower() == "true"
                                    elif new_value.isdigit():
                                        local_state[key] = int(new_value)
                                    elif "." in new_value and new_value.replace(".", "").isdigit():
                                        local_state[key] = float(new_value)
                                    else:
                                        local_state[key] = new_value
                                    print(get_message("updated_key", USER_LANG).format(key, local_state[key]))
                                except (ValueError, TypeError):
                                    local_state[key] = new_value
                                    print(get_message("updated_key", USER_LANG).format(key, local_state[key]))

                        elif edit_choice == len(keys) + 1:
                            # Add new key
                            new_key = input(get_message("new_key_name", USER_LANG)).strip()
                            if new_key:
                                new_value = input(get_message("value_for_key", USER_LANG).format(new_key)).strip()
                                # Try to convert to appropriate type
                                try:
                                    if new_value.lower() in ["true", "false"]:
                                        local_state[new_key] = new_value.lower() == "true"
                                    elif new_value.isdigit():
                                        local_state[new_key] = int(new_value)
                                    elif "." in new_value and new_value.replace(".", "").isdigit():
                                        local_state[new_key] = float(new_value)
                                    else:
                                        local_state[new_key] = new_value
                                    print(get_message("added_new_key", USER_LANG).format(new_key, local_state[new_key]))
                                    keys.append(new_key)  # Update keys list
                                except (ValueError, TypeError):
                                    local_state[new_key] = new_value
                                    print(get_message("added_new_key", USER_LANG).format(new_key, local_state[new_key]))
                                    keys.append(new_key)

                        elif edit_choice == len(keys) + 2:
                            # Done editing
                            break

                        else:
                            print(get_message("invalid_selection_cert", USER_LANG))

                    except ValueError:
                        print(get_message("enter_valid_number", USER_LANG))

                break

            elif choice == "2":
                # Replace with JSON
                print(f"\n{get_message('enter_json_prompt', USER_LANG)}")
                json_lines = []
                while True:
                    line = input()
                    if line == "" and json_lines and json_lines[-1] == "":
                        break
                    json_lines.append(line)

                try:
                    json_text = "\n".join(json_lines[:-1])  # Remove last empty line
                    new_state = json.loads(json_text)
                    local_state = new_state
                    print(get_message("state_updated_from_json", USER_LANG))
                    break
                except json.JSONDecodeError as e:
                    print(get_message("invalid_json", USER_LANG).format(str(e)))
                    continue

            elif choice == "3":
                print(f"❌ {get_message('operation_cancelled', USER_LANG)}")
                return

            else:
                print(get_message("invalid_choice", USER_LANG))

        # Save updated state
        if self.save_local_state(local_state):
            print(f"\n{get_message('local_state_updated_sim', USER_LANG)}")
            print(f"📊 {get_message('current_state', USER_LANG)} {json.dumps(local_state, indent=2)}")

            # Ask if user wants to report to shadow
            report = input(f"\n{get_message('report_updated_state', USER_LANG)}").strip().lower()
            if report == "y":
                self.update_shadow_reported(local_state, debug=self.debug_mode)
        else:
            print(get_message("failed_update_local", USER_LANG))

    def show_shadow_diagnostics(self):
        """Show detailed shadow connection and state diagnostics"""
        print("\n🔍 Shadow Connection Diagnostics")
        print("=" * 60)

        print("📡 Connection Status:")
        print(f"   • Connected: {'✅ Yes' if self.connected else '❌ No'}")
        print(f"   • Thing Name: {self.thing_name}")
        print("   • Shadow Type: Classic Shadow")
        print(f"   • Messages Received: {len(self.received_messages)}")

        if self.local_state_file:
            print("\n📱 Local Device State:")
            print(f"   • State File: {self.local_state_file}")
            print(f"   • File Exists: {'✅ Yes' if os.path.exists(self.local_state_file) else '❌ No'}")

            if os.path.exists(self.local_state_file):
                try:
                    local_state = self.load_local_state()
                    print(f"   • Current State: {json.dumps(local_state, indent=6)}")
                except Exception as e:
                    print(f"   • Error reading state: {str(e)}")

        print("\n🌟 Shadow Topics:")
        shadow_topics = [
            f"$aws/things/{self.thing_name}/shadow/get",
            f"$aws/things/{self.thing_name}/shadow/get/accepted",
            f"$aws/things/{self.thing_name}/shadow/get/rejected",
            f"$aws/things/{self.thing_name}/shadow/update",
            f"$aws/things/{self.thing_name}/shadow/update/accepted",
            f"$aws/things/{self.thing_name}/shadow/update/rejected",
            f"$aws/things/{self.thing_name}/shadow/update/delta",
        ]

        for topic in shadow_topics:
            if "get" in topic and topic.endswith("/get"):
                print(f"   📤 {topic} (publish to request shadow)")
            elif "update" in topic and topic.endswith("/update"):
                print(f"   📤 {topic} (publish to update shadow)")
            else:
                print(f"   📥 {topic} (subscribed)")

        print("\n🔧 Troubleshooting:")
        print("1. Verify certificate is ACTIVE and attached to Thing")
        print("2. Check policy allows shadow operations (iot:GetThingShadow, iot:UpdateThingShadow)")
        print("3. Ensure Thing name matches exactly")
        print("4. Check AWS IoT logs in CloudWatch (if enabled)")

    def disconnect(self):
        """Disconnect from AWS IoT Core"""
        if self.connection and self.connected:
            print(f"\n{get_message('disconnecting_from_iot', USER_LANG)}")

            try:
                disconnect_future = self.connection.disconnect()
                disconnect_future.result()

                self.print_shadow_details(
                    "SHADOW DISCONNECTION",
                    {
                        get_message("status", USER_LANG): get_message("disconnection_complete", USER_LANG),
                        get_message("thing_name", USER_LANG): self.thing_name,
                        get_message("total_messages", USER_LANG): len(self.received_messages),
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
        display_aws_context()

        print(get_message("description_intro", USER_LANG))
        for concept in get_message("shadow_concepts", USER_LANG):
            print(concept)

        # Show learning moment
        print_learning_moment("shadow_foundation", USER_LANG)

        if debug_mode:
            print(f"\n{get_message('debug_enabled', USER_LANG)}")
            for feature in get_message("debug_features", USER_LANG):
                print(feature)
        else:
            print(f"\n{get_message('tip', USER_LANG)}")

        print(get_message("separator", USER_LANG))

        explorer = DeviceShadowExplorer()
        explorer.debug_mode = debug_mode

        try:
            # Auto-connect and go into interactive mode
            explorer.run_auto_connect_and_interactive()

        except KeyboardInterrupt:
            print(f"\n\n{get_message('operation_cancelled', USER_LANG)}")
        except (ConnectionError, TimeoutError) as e:
            print(f"\n❌ Connection error: {str(e)}")
            if debug_mode:
                import traceback

                traceback.print_exc()
        except (FileNotFoundError, PermissionError) as e:
            print(f"\n❌ File access error: {str(e)}")
            if debug_mode:
                import traceback

                traceback.print_exc()
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"\n❌ Data format error: {str(e)}")
            if debug_mode:
                import traceback

                traceback.print_exc()
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            if debug_mode:
                import traceback

                traceback.print_exc()
        finally:
            # Always disconnect cleanly
            explorer.disconnect()
            print(f"\n{get_message('thank_you_message', USER_LANG)}")

    except KeyboardInterrupt:
        print(f"\n\n{get_message('operation_cancelled', USER_LANG)}")
        print(get_message("goodbye", USER_LANG))


if __name__ == "__main__":
    main()

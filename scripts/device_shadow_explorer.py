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

    # If no environment variable, ask user
    print("🌍 Language Selection / Selección de Idioma / 言語選択 / 语言选择 / Seleção de Idioma")
    print("=" * 80)
    print("1. English")
    print("2. Español (Spanish)")
    print("3. 日本語 (Japanese)")
    print("4. 中文 (Chinese)")
    print("5. Português (Portuguese)")

    while True:
        try:
            choice = input("Select language / Seleccionar idioma / 言語を選択 / 选择语言 / Selecionar idioma (1-5): ").strip()
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
            else:
                print("Invalid choice. Please select 1-5.")
                print("Selección inválida. Por favor selecciona 1-5.")
                print("無効な選択です。1-5を選択してください。")
                print("无效选择。请选择 1-5。")
                print("Escolha inválida. Por favor selecione 1-5.")
        except KeyboardInterrupt:
            print("Goodbye! / ¡Adiós! / さようなら！ / 再见！ / Tchau!")
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
            # Create client ID
            client_id = f"{thing_name}-shadow-{uuid.uuid4().hex[:8]}"

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

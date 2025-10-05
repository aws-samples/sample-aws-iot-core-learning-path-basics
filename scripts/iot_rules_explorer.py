#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""
AWS IoT Rules Engine Explorer
Educational tool for learning AWS IoT Rules Engine through hands-on rule creation and management.
"""
import json
import os
import sys
import time
from datetime import datetime

import boto3
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
from botocore.exceptions import ClientError

# Internationalization support
MESSAGES = {
    "en": {
        # AWS Context
        "aws_context_info": "🌍 AWS Context Information:",
        "account_id": "Account ID",
        "region": "Region",
        "aws_context_error": "⚠️ Could not retrieve AWS context: {error}",
        "aws_credentials_check": "Make sure AWS credentials are configured",
        # Headers and formatting
        "header_separator": "=" * 60,
        "step_separator": "-" * 50,
        "rule_separator": "-" * 40,
        # Main menu
        "main_title": "⚙️ AWS IoT Rules Engine Explorer",
        "aws_config_title": "📍 AWS Configuration:",
        "main_description": "Learn AWS IoT Rules Engine through hands-on rule creation and management.",
        "main_features": "This tool demonstrates:",
        "feature_sql_syntax": "• IoT Rules Engine SQL syntax and message routing",
        "feature_topic_filtering": "• Topic filtering with SELECT, FROM, and WHERE clauses",
        "feature_republish_actions": "• Republish actions and IAM role configuration",
        "feature_lifecycle": "• Rule lifecycle management (create, enable, disable, delete)",
        "learning_moment_title": "📚 LEARNING MOMENT: IoT Rules Engine",
        "learning_moment_description": "The AWS IoT Rules Engine processes and routes messages from your devices using SQL-like queries. Rules can filter, transform, and route messages to various AWS services like Lambda, DynamoDB, or S3. This enables real-time data processing, alerting, and integration with your broader AWS architecture without requiring device-side logic changes.",
        "next_action": "🔄 NEXT: We will create and manage IoT rules for message processing",
        "press_enter_continue": "Press Enter to continue...",
        "debug_mode_enabled": "🔍 DEBUG MODE ENABLED",
        "debug_features": "• Enhanced AWS IoT API logging",
        "debug_features_2": "• Detailed rule payload and IAM operations",
        "debug_features_3": "• Extended error diagnostics",
        "debug_tip": "💡 Tip: Use --debug or -d flag for enhanced logging",
        # Menu options
        "menu_title": "📋 IoT Rules Engine Menu:",
        "menu_option_1": "1. List all IoT Rules",
        "menu_option_2": "2. Describe specific IoT Rule",
        "menu_option_3": "3. Create new IoT Rule",
        "menu_option_4": "4. Test IoT Rule with sample messages",
        "menu_option_5": "5. Manage IoT Rule (enable/disable/delete)",
        "menu_option_6": "6. Exit",
        "select_option": "Select option (1-6): ",
        "invalid_choice": "❌ Invalid choice. Please select 1-6.",
        "press_enter_menu": "Press Enter to continue...",
        # Learning moments for each option
        "learning_moment_inventory": "📚 LEARNING MOMENT: Rules Inventory & Management",
        "learning_moment_inventory_desc": "Listing IoT rules shows you all the message processing logic currently active in your account. Each rule has a name, SQL statement, and actions. This inventory helps you understand your data flow, identify unused rules, and manage your IoT message processing pipeline effectively.",
        "next_list_rules": "🔄 NEXT: We will list all IoT rules in your account",
        "learning_moment_analysis": "📚 LEARNING MOMENT: Rule Analysis & Troubleshooting",
        "learning_moment_analysis_desc": "Describing a rule reveals its complete configuration including SQL query, actions, and metadata. This detailed view is essential for troubleshooting message routing issues, understanding rule logic, and verifying that rules are configured correctly for your use case.",
        "next_examine_rule": "🔄 NEXT: We will examine a specific rule's configuration",
        "learning_moment_creation": "📚 LEARNING MOMENT: Rule Creation & Message Routing",
        "learning_moment_creation_desc": "Creating IoT rules defines how messages from your devices are processed and routed. Rules use SQL-like syntax to filter and transform messages, then trigger actions like storing data, invoking functions, or sending notifications. This enables real-time data processing without device-side changes.",
        "next_create_rule": "🔄 NEXT: We will create a new IoT rule with SQL and actions",
        "learning_moment_testing": "📚 LEARNING MOMENT: Rule Testing & Validation",
        "learning_moment_testing_desc": "Testing rules with sample messages validates your SQL logic and ensures rules behave as expected before deploying to production. This helps catch filtering errors, syntax issues, and logic problems that could cause message processing failures or unexpected behavior.",
        "next_test_rule": "🔄 NEXT: We will test a rule with sample MQTT messages",
        "learning_moment_lifecycle": "📚 LEARNING MOMENT: Rule Lifecycle Operations",
        "learning_moment_lifecycle_desc": "Managing rules includes enabling, disabling, and deleting them. Disabling rules stops message processing without losing configuration, while deleting removes them permanently. This lifecycle management is crucial for maintaining, updating, and troubleshooting your IoT data processing pipeline.",
        "next_manage_rule": "🔄 NEXT: We will manage rule status and lifecycle",
        # Debug messages
        "debug_operation": "🔍 DEBUG: {operation}",
        "debug_input": "📥 Input: {input}",
        "debug_completed": "✅ {operation} completed",
        "debug_output": "📤 Output: {output}",
        "debug_error_code": "🔍 DEBUG: Error code: {code}",
        # List rules
        "list_rules_title": "List IoT Rules",
        "no_rules_found": "📋 No IoT Rules found in your account",
        "create_first_rule": "💡 Create your first rule using option 2",
        "found_rules": "📋 Found {count} IoT Rules:",
        "rule_status_disabled": "🔴 DISABLED",
        "rule_status_enabled": "🟢 ENABLED",
        "created_label": "📅 Created: {date}",
        "debug_rule_arn": "🔍 DEBUG: Rule ARN: {arn}",
        "sql_label": "📝 SQL: {sql}",
        "actions_count": "🎯 Actions: {count} configured",
        "action_republish": "Republish to: {topic}",
        "action_s3": "S3 to bucket: {bucket}",
        "action_lambda": "Lambda: {function}",
        # Describe rule
        "describe_rule_title": "Describe IoT Rule",
        "list_rules_for_selection": "List IoT Rules for selection",
        "available_rules": "📋 Available Rules:",
        "select_rule_describe": "Select rule to describe (1-{count}): ",
        "invalid_selection_range": "❌ Invalid selection. Please enter 1-{count}",
        "enter_valid_number": "❌ Please enter a valid number",
        "rule_details_title": "📋 Rule Details: {name}",
        "sql_statement_label": "📝 SQL Statement:",
        "sql_breakdown_label": "📖 SQL Breakdown:",
        "select_clause": "🔍 SELECT: {clause}",
        "from_clause": "📥 FROM: {clause}",
        "where_clause": "🔍 WHERE: {clause}",
        "actions_title": "🎯 Actions ({count}):",
        "action_type": "Action Type: {type}",
        "target_topic": "📤 Target Topic: {topic}",
        "role_arn": "🔑 Role ARN: {arn}",
        "qos_label": "🏷️  QoS: {qos}",
        "bucket_label": "🪣 Bucket: {bucket}",
        "key_label": "📁 Key: {key}",
        "function_arn": "⚡ Function ARN: {arn}",
        "error_action_title": "❌ Error Action:",
        "error_action_type": "Type: {type}",
        "error_action_topic": "Topic: {topic}",
        "rule_metadata_title": "📊 Rule Metadata:",
        "rule_status": "🔄 Status: {status}",
        "rule_created": "📅 Created: {date}",
        "debug_complete_payload": "🔍 DEBUG: Complete Rule Payload:",
        # Create rule
        "create_rule_title": "Create IoT Rule",
        "create_learning_objectives": "🎓 Learning Objectives:",
        "objective_sql_syntax": "• Understand IoT Rules Engine SQL syntax",
        "objective_topic_filtering": "• Learn topic filtering and message routing",
        "objective_sql_clauses": "• Practice SELECT, FROM, and WHERE clauses",
        "objective_republish_actions": "• Configure republish actions with proper IAM roles",
        "enter_rule_name": "📝 Enter rule name (alphanumeric and underscores only): ",
        "invalid_rule_name": "❌ Rule name must contain only alphanumeric characters and underscores",
        "rule_name_confirmed": "✅ Rule name: {name}",
        "enter_rule_description": "📖 Enter rule description (optional): ",
        "default_rule_description": "Learning rule for processing IoT messages",
        "rule_description_confirmed": "✅ Rule description: {description}",
        "building_sql_title": "📖 Building SQL Statement for IoT Rules Engine",
        "sql_template": "💡 Template: SELECT <attributes> FROM 'testRulesEngineTopic/<deviceId>/<eventType>' WHERE <condition>",
        "available_event_types": "🎯 Available Event Types:",
        "custom_event_type": "Custom event type",
        "select_event_type": "Select event type (1-{count}): ",
        "enter_custom_event_type": "Enter custom event type: ",
        "event_type_empty": "❌ Event type cannot be empty",
        "invalid_event_selection": "❌ Invalid selection",
        "topic_pattern_confirmed": "✅ Topic pattern: {pattern}",
        "select_clause_title": "🔍 SELECT Clause - Attributes for {event_type} events:",
        "custom_selection": "Custom selection",
        "select_attributes": "Select attributes (1-{count}): ",
        "enter_custom_select": "Enter custom SELECT clause: ",
        "select_clause_empty": "❌ SELECT clause cannot be empty",
        "select_clause_confirmed": "✅ SELECT: {clause}",
        "where_clause_title": "🔍 WHERE Clause (Optional) - Filter {event_type} messages:",
        "where_examples_title": "💡 Examples for {event_type}:",
        "add_where_condition": "Add WHERE condition? (y/N): ",
        "enter_where_condition": "Enter WHERE condition: ",
        "where_clause_confirmed": "✅ WHERE: {clause}",
        "empty_where_warning": "⚠️ Empty WHERE clause, proceeding without filter",
        "complete_sql_title": "📝 Complete SQL Statement:",
        "input_validation_error": "❌ Input validation error: {error}",
        "validation_tip": "💡 Please use only alphanumeric characters, spaces, and basic operators",
        "republish_config_title": "📤 Republish Action Configuration",
        "enter_target_topic": "Enter target topic for republishing (e.g., 'processed/temperature'): ",
        "default_target_topic": "✅ Using default target topic: {topic}",
        "iam_role_setup": "🔑 Setting up IAM Role for Rule Actions",
        "iam_role_failed": "❌ Failed to create/verify IAM role. Cannot create rule.",
        "creating_rule": "🔧 Creating IoT Rule...",
        "debug_rule_payload": "🔍 DEBUG: Rule payload:",
        "create_rule_attempt": "Create IoT Rule '{name}' (attempt {attempt}/{max_attempts})",
        "iam_propagation_wait": "⏳ IAM role may still be propagating. Waiting 10 seconds before retry...",
        "create_rule_failed": "❌ Failed to create rule after {attempts} attempts",
        "rule_created_success": "🎉 Rule '{name}' created successfully!",
        "rule_summary_title": "📋 Rule Summary:",
        "summary_name": "📝 Name: {name}",
        "summary_source_topic": "📥 Source Topic: {topic}",
        "summary_target_topic": "📤 Target Topic: {topic}",
        "summary_sql": "🔍 SQL: {sql}",
        "summary_role": "🔑 Role: {role}",
        "testing_rule_title": "💡 Testing Your Rule:",
        "testing_step_1": "1. Publish a message to: testRulesEngineTopic/device123/{event_type}",
        "testing_step_2": "2. Subscribe to: {topic}",
        "testing_step_3": "3. Check if the message is routed correctly",
        "example_test_message": "📖 Example test message:",
        # IAM role management
        "debug_existing_role": "🔍 DEBUG: Using existing IAM role: {arn}",
        "using_existing_role": "✅ Using existing IAM role: {name}",
        "creating_iam_role": "🔧 Creating IAM role: {name}",
        "error_checking_role": "❌ Error checking IAM role: {error}",
        "create_iam_role_operation": "Create IAM role '{name}'",
        "create_iam_policy_operation": "Create IAM policy '{name}'",
        "attach_policy_operation": "Attach policy to role",
        "iam_role_created_success": "✅ IAM role and policy created successfully",
        "iam_role_propagation": "⏳ Waiting for IAM role propagation (10 seconds)...",
        # Manage rule
        "manage_rule_title": "Manage IoT Rules",
        "list_rules_for_management": "List IoT Rules for management",
        "select_rule_manage": "Select rule to manage (1-{count}): ",
        "managing_rule": "🔧 Managing Rule: {name}",
        "current_status": "📊 Current Status: {status}",
        "management_options": "📋 Management Options:",
        "enable_rule": "1. 🟢 Enable rule",
        "disable_rule": "1. 🔴 Disable rule",
        "delete_rule": "2. 🗑️ Delete rule",
        "cancel_management": "3. ↩️ Cancel",
        "select_action": "Select action (1-3): ",
        "invalid_action_selection": "❌ Invalid selection. Please enter 1-3",
        "get_current_rule_settings": "Get current rule settings",
        "enable_rule_operation": "Enable rule '{name}'",
        "disable_rule_operation": "Disable rule '{name}'",
        "rule_status_updated": "✅ Rule '{name}' is now {status}",
        "failed_get_rule_settings": "❌ Failed to get current rule settings for '{name}'",
        "confirm_delete_rule": "⚠️ Are you sure you want to delete rule '{name}'? (y/N): ",
        "delete_rule_operation": "Delete rule '{name}'",
        "rule_deleted_success": "✅ Rule '{name}' deleted successfully",
        "rule_deletion_cancelled": "❌ Rule deletion cancelled",
        "management_cancelled": "↩️ Management cancelled",
        # Test rule
        "test_rule_title": "Test IoT Rule",
        "test_learning_objectives": "🎓 Learning Objectives:",
        "test_objective_1": "• Test rule topic matching and WHERE conditions",
        "test_objective_2": "• Understand message routing behavior",
        "test_objective_3": "• Practice with matching and non-matching messages",
        "test_objective_4": "• Observe real-time rule processing",
        "list_rules_for_testing": "List IoT Rules for testing",
        "no_rules_for_testing": "📋 No IoT Rules found",
        "create_rule_first": "💡 Create a rule first using option 3",
        "select_rule_test": "Select rule to test (1-{count}): ",
        "get_rule_details_testing": "Get rule details for testing",
        "testing_rule": "📋 Testing Rule: {name}",
        "sql_display": "📝 SQL: {sql}",
        "source_topic_pattern": "📥 Source Topic Pattern: {pattern}",
        "where_condition_display": "🔍 WHERE Condition: {condition}",
        "target_topics_display": "📤 Target Topics: {topics}",
        "finding_devices_certificates": "🔍 Finding devices with certificates...",
        "no_certificates_directory": "❌ No certificates directory found.",
        "run_certificate_manager": "💡 Run certificate_manager.py first to create certificates",
        "no_devices_certificates": "❌ No devices with certificates found.",
        "found_devices_certificates": "📋 Found {count} device(s) with certificates:",
        "using_device": "✅ Using device: {name}",
        "selected_device": "✅ Selected device: {name}",
        "select_device": "Select device (1-{count}): ",
        "invalid_device_selection": "❌ Invalid selection",
        "get_iot_endpoint": "Get IoT endpoint",
        "cannot_get_endpoint": "❌ Cannot get IoT endpoint. Testing requires MQTT connection.",
        # Interactive rule testing
        "interactive_testing_title": "🧪 Interactive Rule Testing",
        "connecting_to_endpoint": "📡 Connecting to: {endpoint}",
        "using_device_info": "📱 Using device: {device}",
        "connecting_aws_iot": "🔌 Connecting to AWS IoT...",
        "connected_aws_iot": "✅ Connected to AWS IoT",
        "subscribed_target_topic": "📡 Subscribed to target topic: {topic}",
        "rule_testing_instructions": "🎯 Rule Testing Instructions:",
        "instruction_1": "• You'll be asked if each message should match the rule",
        "instruction_2": "• Topic matching: Does the topic fit the pattern?",
        "instruction_3": "• WHERE condition: Does the message content match the filter?",
        "instruction_4": "• Watch for rule output messages on target topics",
        "instruction_5": "• Type 'quit' to exit testing",
        "test_message_header": "🧪 Test Message #{count}",
        "topic_pattern_display": "📥 Topic Pattern: {pattern}",
        "no_specific_pattern": "No specific pattern",
        "should_match_topic": "Should this message MATCH the topic pattern? (y/N/quit): ",
        "generated_topic": "📡 Generated Topic: {topic}",
        "where_condition_label": "🔍 WHERE Condition: {condition}",
        "should_match_where": "Should this message MATCH the WHERE condition? (y/n): ",
        "test_message_display": "📝 Test Message:",
        "topic_label": "📡 Topic: {topic}",
        "payload_label": "💬 Payload: {payload}",
        "prediction_should_trigger": "🔮 Prediction: Rule SHOULD trigger",
        "prediction_should_not_trigger": "🔮 Prediction: Rule should NOT trigger",
        "publishing_test_message": "📤 Publishing test message...",
        "waiting_rule_processing": "⏳ Waiting 3 seconds for rule processing...",
        "expected_trigger_no_output": "⚠️ Expected rule to trigger but no output received",
        "unexpected_trigger": "⚠️ Rule triggered unexpectedly",
        "rule_triggered_expected": "✅ Rule triggered as expected!",
        "rule_correctly_not_triggered": "✅ Rule correctly did not trigger",
        "press_enter_next_test": "Press Enter to continue to next test...",
        "testing_error": "❌ Testing error: {error}",
        "disconnecting_aws_iot": "🔌 Disconnecting from AWS IoT...",
        "disconnected_aws_iot": "✅ Disconnected from AWS IoT",
        # MQTT message handling
        "rule_output_received": "🔔 RULE OUTPUT RECEIVED [{timestamp}]",
        "message_topic": "📤 Topic: {topic}",
        "message_content": "💬 Message: {message}",
        "rule_processed_forwarded": "✅ Rule '{name}' processed and forwarded the message!",
        "connection_interrupted": "⚠️ Connection interrupted: {error}",
        "connection_resumed": "✅ Connection resumed",
        # Error messages
        "operation_failed": "❌ {operation} failed: {error}",
        "unexpected_error": "❌ Unexpected error: {error}",
        "interrupted_by_user": "🛑 Interrupted by user",
        "goodbye": "👋 Goodbye!",
        # Validation messages
        "invalid_characters_clause": "Invalid characters in {clause_type} clause. Only alphanumeric characters, spaces, and basic operators are allowed.",
        "dangerous_pattern_detected": "Potentially dangerous pattern '{pattern}' detected in {clause_type} clause.",
        "invalid_characters_topic": "Invalid characters in topic pattern. Only alphanumeric characters, hyphens, underscores, forward slashes, and + wildcards are allowed.",
        # Language selection messages
        "language_selection_title": "🌍 Language Selection",
        "language_option_english": "1. English",
        "language_option_spanish": "2. Español (Spanish)",
        "select_language_prompt": "Select language (1-2): ",
        "invalid_language_choice": "Invalid choice. Please select 1 or 2.",
    },
    "es": {
        # AWS Context
        "aws_context_info": "🌍 Información de Contexto AWS:",
        "account_id": "ID de Cuenta",
        "region": "Región",
        "aws_context_error": "⚠️ No se pudo obtener el contexto AWS: {error}",
        "aws_credentials_check": "Asegúrate de que las credenciales AWS estén configuradas",
        # Headers and formatting
        "header_separator": "=" * 60,
        "step_separator": "-" * 50,
        "rule_separator": "-" * 40,
        # Main menu
        "main_title": "⚙️ Explorador del Motor de Reglas AWS IoT",
        "aws_config_title": "📍 Configuración AWS:",
        "main_description": "Aprende el Motor de Reglas AWS IoT a través de la creación y gestión práctica de reglas.",
        "main_features": "Esta herramienta demuestra:",
        "feature_sql_syntax": "• Sintaxis SQL del Motor de Reglas IoT y enrutamiento de mensajes",
        "feature_topic_filtering": "• Filtrado de temas con cláusulas SELECT, FROM y WHERE",
        "feature_republish_actions": "• Acciones de republicación y configuración de roles IAM",
        "feature_lifecycle": "• Gestión del ciclo de vida de reglas (crear, habilitar, deshabilitar, eliminar)",
        "learning_moment_title": "📚 MOMENTO DE APRENDIZAJE: Motor de Reglas IoT",
        "learning_moment_description": "El Motor de Reglas AWS IoT procesa y enruta mensajes de tus dispositivos usando consultas similares a SQL. Las reglas pueden filtrar, transformar y enrutar mensajes a varios servicios AWS como Lambda, DynamoDB o S3. Esto permite procesamiento de datos en tiempo real, alertas e integración con tu arquitectura AWS más amplia sin requerir cambios en la lógica del dispositivo.",
        "next_action": "🔄 SIGUIENTE: Crearemos y gestionaremos reglas IoT para procesamiento de mensajes",
        "press_enter_continue": "Presiona Enter para continuar...",
        "debug_mode_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": "• Registro mejorado de API AWS IoT",
        "debug_features_2": "• Operaciones detalladas de carga de reglas e IAM",
        "debug_features_3": "• Diagnósticos de errores extendidos",
        "debug_tip": "💡 Consejo: Usa la bandera --debug o -d para registro mejorado",
        # Menu options
        "menu_title": "📋 Menú del Motor de Reglas IoT:",
        "menu_option_1": "1. Listar todas las Reglas IoT",
        "menu_option_2": "2. Describir Regla IoT específica",
        "menu_option_3": "3. Crear nueva Regla IoT",
        "menu_option_4": "4. Probar Regla IoT con mensajes de muestra",
        "menu_option_5": "5. Gestionar Regla IoT (habilitar/deshabilitar/eliminar)",
        "menu_option_6": "6. Salir",
        "select_option": "Selecciona opción (1-6): ",
        "invalid_choice": "❌ Opción inválida. Por favor selecciona 1-6.",
        "press_enter_menu": "Presiona Enter para continuar...",
        # Learning moments for each option
        "learning_moment_inventory": "📚 MOMENTO DE APRENDIZAJE: Inventario y Gestión de Reglas",
        "learning_moment_inventory_desc": "Listar reglas IoT te muestra toda la lógica de procesamiento de mensajes actualmente activa en tu cuenta. Cada regla tiene un nombre, declaración SQL y acciones. Este inventario te ayuda a entender tu flujo de datos, identificar reglas no utilizadas y gestionar tu pipeline de procesamiento de mensajes IoT de manera efectiva.",
        "next_list_rules": "🔄 SIGUIENTE: Listaremos todas las reglas IoT en tu cuenta",
        "learning_moment_analysis": "📚 MOMENTO DE APRENDIZAJE: Análisis y Solución de Problemas de Reglas",
        "learning_moment_analysis_desc": "Describir una regla revela su configuración completa incluyendo consulta SQL, acciones y metadatos. Esta vista detallada es esencial para solucionar problemas de enrutamiento de mensajes, entender la lógica de reglas y verificar que las reglas estén configuradas correctamente para tu caso de uso.",
        "next_examine_rule": "🔄 SIGUIENTE: Examinaremos la configuración de una regla específica",
        "learning_moment_creation": "📚 MOMENTO DE APRENDIZAJE: Creación de Reglas y Enrutamiento de Mensajes",
        "learning_moment_creation_desc": "Crear reglas IoT define cómo se procesan y enrutan los mensajes de tus dispositivos. Las reglas usan sintaxis similar a SQL para filtrar y transformar mensajes, luego activan acciones como almacenar datos, invocar funciones o enviar notificaciones. Esto permite procesamiento de datos en tiempo real sin cambios en el dispositivo.",
        "next_create_rule": "🔄 SIGUIENTE: Crearemos una nueva regla IoT con SQL y acciones",
        "learning_moment_testing": "📚 MOMENTO DE APRENDIZAJE: Prueba y Validación de Reglas",
        "learning_moment_testing_desc": "Probar reglas con mensajes de muestra valida tu lógica SQL y asegura que las reglas se comporten como se espera antes de desplegar a producción. Esto ayuda a detectar errores de filtrado, problemas de sintaxis y problemas de lógica que podrían causar fallas en el procesamiento de mensajes o comportamiento inesperado.",
        "next_test_rule": "🔄 SIGUIENTE: Probaremos una regla con mensajes MQTT de muestra",
        "learning_moment_lifecycle": "📚 MOMENTO DE APRENDIZAJE: Operaciones del Ciclo de Vida de Reglas",
        "learning_moment_lifecycle_desc": "Gestionar reglas incluye habilitarlas, deshabilitarlas y eliminarlas. Deshabilitar reglas detiene el procesamiento de mensajes sin perder la configuración, mientras que eliminarlas las remueve permanentemente. Esta gestión del ciclo de vida es crucial para mantener, actualizar y solucionar problemas en tu pipeline de procesamiento de datos IoT.",
        "next_manage_rule": "🔄 SIGUIENTE: Gestionaremos el estado y ciclo de vida de reglas",
        # Debug messages
        "debug_operation": "🔍 DEBUG: {operation}",
        "debug_input": "📥 Entrada: {input}",
        "debug_completed": "✅ {operation} completado",
        "debug_output": "📤 Salida: {output}",
        "debug_error_code": "🔍 DEBUG: Código de error: {code}",
        # List rules
        "list_rules_title": "Listar Reglas IoT",
        "no_rules_found": "📋 No se encontraron Reglas IoT en tu cuenta",
        "create_first_rule": "💡 Crea tu primera regla usando la opción 2",
        "found_rules": "📋 Se encontraron {count} Reglas IoT:",
        "rule_status_disabled": "🔴 DESHABILITADA",
        "rule_status_enabled": "🟢 HABILITADA",
        "created_label": "📅 Creada: {date}",
        "debug_rule_arn": "🔍 DEBUG: ARN de Regla: {arn}",
        "sql_label": "📝 SQL: {sql}",
        "actions_count": "🎯 Acciones: {count} configuradas",
        "action_republish": "Republicar a: {topic}",
        "action_s3": "S3 al bucket: {bucket}",
        "action_lambda": "Lambda: {function}",
        # Describe rule
        "describe_rule_title": "Describir Regla IoT",
        "list_rules_for_selection": "Listar Reglas IoT para selección",
        "available_rules": "📋 Reglas Disponibles:",
        "select_rule_describe": "Selecciona regla para describir (1-{count}): ",
        "invalid_selection_range": "❌ Selección inválida. Por favor ingresa 1-{count}",
        "enter_valid_number": "❌ Por favor ingresa un número válido",
        "rule_details_title": "📋 Detalles de Regla: {name}",
        "sql_statement_label": "📝 Declaración SQL:",
        "sql_breakdown_label": "📖 Desglose SQL:",
        "select_clause": "🔍 SELECT: {clause}",
        "from_clause": "📥 FROM: {clause}",
        "where_clause": "🔍 WHERE: {clause}",
        "actions_title": "🎯 Acciones ({count}):",
        "action_type": "Tipo de Acción: {type}",
        "target_topic": "📤 Tema Destino: {topic}",
        "role_arn": "🔑 ARN del Rol: {arn}",
        "qos_label": "🏷️  QoS: {qos}",
        "bucket_label": "🪣 Bucket: {bucket}",
        "key_label": "📁 Clave: {key}",
        "function_arn": "⚡ ARN de Función: {arn}",
        "error_action_title": "❌ Acción de Error:",
        "error_action_type": "Tipo: {type}",
        "error_action_topic": "Tema: {topic}",
        "rule_metadata_title": "📊 Metadatos de Regla:",
        "rule_status": "🔄 Estado: {status}",
        "rule_created": "📅 Creada: {date}",
        "debug_complete_payload": "🔍 DEBUG: Carga Completa de Regla:",
        # Create rule
        "create_rule_title": "Crear Regla IoT",
        "create_learning_objectives": "🎓 Objetivos de Aprendizaje:",
        "objective_sql_syntax": "• Entender la sintaxis SQL del Motor de Reglas IoT",
        "objective_topic_filtering": "• Aprender filtrado de temas y enrutamiento de mensajes",
        "objective_sql_clauses": "• Practicar cláusulas SELECT, FROM y WHERE",
        "objective_republish_actions": "• Configurar acciones de republicación con roles IAM apropiados",
        "enter_rule_name": "📝 Ingresa nombre de regla (solo alfanuméricos y guiones bajos): ",
        "invalid_rule_name": "❌ El nombre de regla debe contener solo caracteres alfanuméricos y guiones bajos",
        "rule_name_confirmed": "✅ Nombre de regla: {name}",
        "enter_rule_description": "📖 Ingresa descripción de regla (opcional): ",
        "default_rule_description": "Regla de aprendizaje para procesar mensajes IoT",
        "rule_description_confirmed": "✅ Descripción de regla: {description}",
        "building_sql_title": "📖 Construyendo Declaración SQL para Motor de Reglas IoT",
        "sql_template": "💡 Plantilla: SELECT <atributos> FROM 'testRulesEngineTopic/<deviceId>/<eventType>' WHERE <condición>",
        "available_event_types": "🎯 Tipos de Eventos Disponibles:",
        "custom_event_type": "Tipo de evento personalizado",
        "select_event_type": "Selecciona tipo de evento (1-{count}): ",
        "enter_custom_event_type": "Ingresa tipo de evento personalizado: ",
        "event_type_empty": "❌ El tipo de evento no puede estar vacío",
        "invalid_event_selection": "❌ Selección inválida",
        "topic_pattern_confirmed": "✅ Patrón de tema: {pattern}",
        "select_clause_title": "🔍 Cláusula SELECT - Atributos para eventos {event_type}:",
        "custom_selection": "Selección personalizada",
        "select_attributes": "Selecciona atributos (1-{count}): ",
        "enter_custom_select": "Ingresa cláusula SELECT personalizada: ",
        "select_clause_empty": "❌ La cláusula SELECT no puede estar vacía",
        "select_clause_confirmed": "✅ SELECT: {clause}",
        "where_clause_title": "🔍 Cláusula WHERE (Opcional) - Filtrar mensajes {event_type}:",
        "where_examples_title": "💡 Ejemplos para {event_type}:",
        "add_where_condition": "¿Agregar condición WHERE? (y/N): ",
        "enter_where_condition": "Ingresa condición WHERE: ",
        "where_clause_confirmed": "✅ WHERE: {clause}",
        "empty_where_warning": "⚠️ Cláusula WHERE vacía, procediendo sin filtro",
        "complete_sql_title": "📝 Declaración SQL Completa:",
        "input_validation_error": "❌ Error de validación de entrada: {error}",
        "validation_tip": "💡 Por favor usa solo caracteres alfanuméricos, espacios y operadores básicos",
        "republish_config_title": "📤 Configuración de Acción de Republicación",
        "enter_target_topic": "Ingresa tema destino para republicación (ej., 'processed/temperature'): ",
        "default_target_topic": "✅ Usando tema destino por defecto: {topic}",
        "iam_role_setup": "🔑 Configurando Rol IAM para Acciones de Regla",
        "iam_role_failed": "❌ Falló crear/verificar rol IAM. No se puede crear regla.",
        "creating_rule": "🔧 Creando Regla IoT...",
        "debug_rule_payload": "🔍 DEBUG: Carga de regla:",
        "create_rule_attempt": "Crear Regla IoT '{name}' (intento {attempt}/{max_attempts})",
        "iam_propagation_wait": "⏳ El rol IAM puede estar aún propagándose. Esperando 10 segundos antes de reintentar...",
        "create_rule_failed": "❌ Falló crear regla después de {attempts} intentos",
        "rule_created_success": "🎉 ¡Regla '{name}' creada exitosamente!",
        "rule_summary_title": "📋 Resumen de Regla:",
        "summary_name": "📝 Nombre: {name}",
        "summary_source_topic": "📥 Tema Fuente: {topic}",
        "summary_target_topic": "📤 Tema Destino: {topic}",
        "summary_sql": "🔍 SQL: {sql}",
        "summary_role": "🔑 Rol: {role}",
        "testing_rule_title": "💡 Probando Tu Regla:",
        "testing_step_1": "1. Publica un mensaje a: testRulesEngineTopic/device123/{event_type}",
        "testing_step_2": "2. Suscríbete a: {topic}",
        "testing_step_3": "3. Verifica si el mensaje se enruta correctamente",
        "example_test_message": "📖 Mensaje de prueba de ejemplo:",
        # IAM role management
        "debug_existing_role": "🔍 DEBUG: Usando rol IAM existente: {arn}",
        "using_existing_role": "✅ Usando rol IAM existente: {name}",
        "creating_iam_role": "🔧 Creando rol IAM: {name}",
        "error_checking_role": "❌ Error verificando rol IAM: {error}",
        "create_iam_role_operation": "Crear rol IAM '{name}'",
        "create_iam_policy_operation": "Crear política IAM '{name}'",
        "attach_policy_operation": "Adjuntar política al rol",
        "iam_role_created_success": "✅ Rol IAM y política creados exitosamente",
        "iam_role_propagation": "⏳ Esperando propagación del rol IAM (10 segundos)...",
        # Manage rule
        "manage_rule_title": "Gestionar Reglas IoT",
        "list_rules_for_management": "Listar Reglas IoT para gestión",
        "select_rule_manage": "Selecciona regla para gestionar (1-{count}): ",
        "managing_rule": "🔧 Gestionando Regla: {name}",
        "current_status": "📊 Estado Actual: {status}",
        "management_options": "📋 Opciones de Gestión:",
        "enable_rule": "1. 🟢 Habilitar regla",
        "disable_rule": "1. 🔴 Deshabilitar regla",
        "delete_rule": "2. 🗑️ Eliminar regla",
        "cancel_management": "3. ↩️ Cancelar",
        "select_action": "Selecciona acción (1-3): ",
        "invalid_action_selection": "❌ Selección inválida. Por favor ingresa 1-3",
        "get_current_rule_settings": "Obtener configuración actual de regla",
        "enable_rule_operation": "Habilitar regla '{name}'",
        "disable_rule_operation": "Deshabilitar regla '{name}'",
        "rule_status_updated": "✅ Regla '{name}' ahora está {status}",
        "failed_get_rule_settings": "❌ Falló obtener configuración actual de regla para '{name}'",
        "confirm_delete_rule": "⚠️ ¿Estás seguro de que quieres eliminar la regla '{name}'? (y/N): ",
        "delete_rule_operation": "Eliminar regla '{name}'",
        "rule_deleted_success": "✅ Regla '{name}' eliminada exitosamente",
        "rule_deletion_cancelled": "❌ Eliminación de regla cancelada",
        "management_cancelled": "↩️ Gestión cancelada",
        # Test rule
        "test_rule_title": "Probar Regla IoT",
        "test_learning_objectives": "🎓 Objetivos de Aprendizaje:",
        "test_objective_1": "• Probar coincidencia de temas de regla y condiciones WHERE",
        "test_objective_2": "• Entender comportamiento de enrutamiento de mensajes",
        "test_objective_3": "• Practicar con mensajes que coinciden y no coinciden",
        "test_objective_4": "• Observar procesamiento de reglas en tiempo real",
        "list_rules_for_testing": "Listar Reglas IoT para prueba",
        "no_rules_for_testing": "📋 No se encontraron Reglas IoT",
        "create_rule_first": "💡 Crea una regla primero usando la opción 3",
        "select_rule_test": "Selecciona regla para probar (1-{count}): ",
        "get_rule_details_testing": "Obtener detalles de regla para prueba",
        "testing_rule": "📋 Probando Regla: {name}",
        "sql_display": "📝 SQL: {sql}",
        "source_topic_pattern": "📥 Patrón de Tema Fuente: {pattern}",
        "where_condition_display": "🔍 Condición WHERE: {condition}",
        "target_topics_display": "📤 Temas Destino: {topics}",
        "finding_devices_certificates": "🔍 Buscando dispositivos con certificados...",
        "no_certificates_directory": "❌ No se encontró directorio de certificados.",
        "run_certificate_manager": "💡 Ejecuta certificate_manager.py primero para crear certificados",
        "no_devices_certificates": "❌ No se encontraron dispositivos con certificados.",
        "found_devices_certificates": "📋 Se encontraron {count} dispositivo(s) con certificados:",
        "using_device": "✅ Usando dispositivo: {name}",
        "selected_device": "✅ Dispositivo seleccionado: {name}",
        "select_device": "Selecciona dispositivo (1-{count}): ",
        "invalid_device_selection": "❌ Selección inválida",
        "get_iot_endpoint": "Obtener endpoint IoT",
        "cannot_get_endpoint": "❌ No se puede obtener endpoint IoT. La prueba requiere conexión MQTT.",
        # Interactive rule testing
        "interactive_testing_title": "🧪 Prueba Interactiva de Reglas",
        "connecting_to_endpoint": "📡 Conectando a: {endpoint}",
        "using_device_info": "📱 Usando dispositivo: {device}",
        "connecting_aws_iot": "🔌 Conectando a AWS IoT...",
        "connected_aws_iot": "✅ Conectado a AWS IoT",
        "subscribed_target_topic": "📡 Suscrito al tema destino: {topic}",
        "rule_testing_instructions": "🎯 Instrucciones de Prueba de Reglas:",
        "instruction_1": "• Se te preguntará si cada mensaje debe coincidir con la regla",
        "instruction_2": "• Coincidencia de tema: ¿El tema encaja con el patrón?",
        "instruction_3": "• Condición WHERE: ¿El contenido del mensaje coincide con el filtro?",
        "instruction_4": "• Observa mensajes de salida de regla en temas destino",
        "instruction_5": "• Escribe 'quit' para salir de la prueba",
        "test_message_header": "🧪 Mensaje de Prueba #{count}",
        "topic_pattern_display": "📥 Patrón de Tema: {pattern}",
        "no_specific_pattern": "Sin patrón específico",
        "should_match_topic": "¿Debe este mensaje COINCIDIR con el patrón de tema? (y/N/quit): ",
        "generated_topic": "📡 Tema Generado: {topic}",
        "where_condition_label": "🔍 Condición WHERE: {condition}",
        "should_match_where": "¿Debe este mensaje COINCIDIR con la condición WHERE? (y/n): ",
        "test_message_display": "📝 Mensaje de Prueba:",
        "topic_label": "📡 Tema: {topic}",
        "payload_label": "💬 Carga: {payload}",
        "prediction_should_trigger": "🔮 Predicción: La regla DEBERÍA activarse",
        "prediction_should_not_trigger": "🔮 Predicción: La regla NO debería activarse",
        "publishing_test_message": "📤 Publicando mensaje de prueba...",
        "waiting_rule_processing": "⏳ Esperando 3 segundos para procesamiento de regla...",
        "expected_trigger_no_output": "⚠️ Se esperaba que la regla se activara pero no se recibió salida",
        "unexpected_trigger": "⚠️ La regla se activó inesperadamente",
        "rule_triggered_expected": "✅ ¡La regla se activó como se esperaba!",
        "rule_correctly_not_triggered": "✅ La regla correctamente no se activó",
        "press_enter_next_test": "Presiona Enter para continuar a la siguiente prueba...",
        "testing_error": "❌ Error de prueba: {error}",
        "disconnecting_aws_iot": "🔌 Desconectando de AWS IoT...",
        "disconnected_aws_iot": "✅ Desconectado de AWS IoT",
        # MQTT message handling
        "rule_output_received": "🔔 SALIDA DE REGLA RECIBIDA [{timestamp}]",
        "message_topic": "📤 Tema: {topic}",
        "message_content": "💬 Mensaje: {message}",
        "rule_processed_forwarded": "✅ ¡La regla '{name}' procesó y reenvió el mensaje!",
        "connection_interrupted": "⚠️ Conexión interrumpida: {error}",
        "connection_resumed": "✅ Conexión reanudada",
        # Error messages
        "operation_failed": "❌ {operation} falló: {error}",
        "unexpected_error": "❌ Error inesperado: {error}",
        "interrupted_by_user": "🛑 Interrumpido por el usuario",
        "goodbye": "👋 ¡Adiós!",
        # Validation messages
        "invalid_characters_clause": "Caracteres inválidos en cláusula {clause_type}. Solo se permiten caracteres alfanuméricos, espacios y operadores básicos.",
        "dangerous_pattern_detected": "Patrón potencialmente peligroso '{pattern}' detectado en cláusula {clause_type}.",
        "invalid_characters_topic": "Caracteres inválidos en patrón de tema. Solo se permiten caracteres alfanuméricos, guiones, guiones bajos, barras diagonales y comodines +.",
        # Language selection messages
        "language_selection_title": "🌍 Selección de Idioma",
        "language_option_english": "1. English",
        "language_option_spanish": "2. Español (Spanish)",
        "select_language_prompt": "Seleccionar idioma (1-2): ",
        "invalid_language_choice": "Selección inválida. Por favor selecciona 1 o 2.",
    },
    "ja": {
        "title": "⚙️ AWS IoT Rules Engine エクスプローラー",
        "separator": "=" * 45,
        "aws_config": "📍 AWS設定:",
        "account_id": "アカウントID",
        "region": "リージョン",
        "description": "IoT Rules Engineを使用したメッセージルーティングと処理の学習。",
        "debug_enabled": "🔍 デバッグモード有効",
        "debug_features": ["• 詳細なルール作成ログ", "• 完全なSQL構文分析", "• 拡張IAM診断"],
        "tip": "💡 ヒント: 詳細なルールログには--debugフラグを使用",
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
        "rules_intro_title": "IoT Rules Engine - メッセージルーティング",
        "rules_intro_content": "AWS IoT Rules Engineは、IoTメッセージを他のAWSサービスにルーティングし、リアルタイムで処理するサービスです。SQLライクな構文を使用してメッセージをフィルタリング、変換し、Lambda、DynamoDB、S3などに送信できます。これにより、スケーラブルなIoTデータ処理パイプラインを構築できます。",
        "rules_intro_next": "IoTルールを作成し、メッセージルーティングを探索します",
        "press_enter": "Enterキーを押して続行...",
        "goodbye": "👋 さようなら！",
        "operations_menu": "📋 利用可能な操作:",
        "operations": [
            "1. 既存のルールをリスト",
            "2. 新しいルールを作成",
            "3. ルールの詳細を表示",
            "4. ルールを削除",
            "5. 終了",
        ],
        "select_operation": "操作を選択 (1-5): ",
        "invalid_choice": "❌ 無効な選択です。1-5を選択してください。",
        "list_rules_learning_title": "📚 学習ポイント: IoTルール一覧",
        "list_rules_learning_content": "IoTルールは、メッセージルーティングとアクションの実行を定義します。各ルールには、SQL文（メッセージフィルタリング用）とアクション（処理されたメッセージの送信先）があります。ルールの一覧表示により、現在のメッセージ処理パイプラインを理解できます。",
        "list_rules_learning_next": "既存のIoTルールを調査し、その構造を理解します",
        "listing_rules": "📋 IoTルールをリスト中...",
        "rules_found": "📊 {}個のルールが見つかりました",
        "no_rules_found": "📭 ルールが見つかりません",
        "rule_name": "ルール名:",
        "rule_description": "説明:",
        "rule_sql": "SQL:",
        "rule_created": "作成日:",
        "rule_actions": "アクション数:",
        "create_rule_learning_title": "📚 学習ポイント: IoTルール作成",
        "create_rule_learning_content": "IoTルール作成には、SQL文（メッセージフィルタリング用）とアクション（処理されたデータの送信先）の定義が含まれます。SQLを使用してトピック、ペイロード、メタデータに基づいてメッセージを選択し、変換できます。",
        "create_rule_learning_next": "新しいIoTルールを作成し、メッセージルーティングを設定します",
        "enter_rule_name": "ルール名を入力:",
        "enter_rule_description": "ルールの説明を入力:",
        "enter_rule_sql": "ルールのSQL文を入力:",
        "example_sql": "例: SELECT * FROM 'topic/+' WHERE temperature > 25",
        "creating_rule": "⚙️ ルール '{}'を作成中...",
        "rule_created_success": "✅ ルールが正常に作成されました",
        "rule_creation_failed": "❌ ルール作成に失敗しました: {}",
        "describe_rule_learning_title": "📚 学習ポイント: ルール詳細",
        "describe_rule_learning_content": "ルール詳細表示により、SQL文、アクション、IAMロール、作成日などの完全な設定を確認できます。これは、ルールのトラブルシューティング、パフォーマンス分析、設定の確認に重要です。",
        "describe_rule_learning_next": "特定のルールの詳細設定を調査します",
        "select_rule_to_describe": "詳細表示するルールを選択 (1-{}): ",
        "invalid_rule_choice": "❌ 無効な選択です。1-{}を選択してください。",
        "describing_rule": "🔍 ルール '{}'の詳細を取得中...",
        "rule_details_title": "📊 ルール詳細:",
        "rule_arn": "ARN:",
        "rule_status": "ステータス:",
        "rule_error_action": "エラーアクション:",
        "rule_actions_title": "アクション:",
        "no_actions": "アクションなし",
        "delete_rule_learning_title": "📚 学習ポイント: ルール削除",
        "delete_rule_learning_content": "ルール削除により、メッセージルーティングを停止し、関連するリソースをクリーンアップできます。削除は永続的であり、ルールによって処理されていたメッセージは他のルールまたはデフォルトアクションにフォールバックします。",
        "delete_rule_learning_next": "ルールを安全に削除し、メッセージルーティングを停止します",
        "select_rule_to_delete": "削除するルールを選択 (1-{}): ",
        "confirm_delete_rule": "本当にルール '{}'を削除しますか？ (y/N): ",
        "delete_cancelled": "削除がキャンセルされました",
        "deleting_rule": "🗑️ ルール '{}'を削除中...",
        "rule_deleted_success": "✅ ルールが正常に削除されました",
        "rule_deletion_failed": "❌ ルール削除に失敗しました: {}",
        "debug_full_error": "🔍 デバッグ: 完全なエラーレスポンス:",
        "debug_full_traceback": "🔍 デバッグ: 完全なトレースバック:",
        "api_error": "❌ APIエラー:",
        "error": "❌ エラー:",
        "learning_moments": {
            "sql_syntax": {
                "title": "📚 学習ポイント: IoT SQL構文",
                "content": "IoT SQLは、標準SQLに似た構文を使用してMQTTメッセージをクエリします。SELECT文でフィールドを選択し、FROM句でトピックを指定し、WHERE句で条件をフィルタリングできます。関数、演算子、ネストされたオブジェクトもサポートされています。",
                "next": "SQL文を使用してメッセージフィルタリングを体験します",
            },
            "rule_actions": {
                "title": "📚 学習ポイント: ルールアクション",
                "content": "ルールアクションは、フィルタリングされたメッセージの送信先を定義します。Lambda関数の呼び出し、DynamoDBへの書き込み、S3への保存、SNS通知の送信などが可能です。各アクションには適切なIAM権限が必要です。",
                "next": "異なるアクションタイプとその使用例を探索します",
            },
            "error_handling": {
                "title": "📚 学習ポイント: エラーハンドリング",
                "content": "IoTルールは、アクション実行の失敗を処理するためのエラーアクションをサポートします。これにより、失敗したメッセージを別のトピック、DLQ、またはログサービスにルーティングして、データ損失を防ぐことができます。",
                "next": "エラーハンドリング戦略とベストプラクティスを学習します",
            },
        },
        "language_selection_title": "🌍 言語選択",
        "language_options": ["1. English", "2. Español (Spanish)", "3. 日本語 (Japanese)"],
        "select_language_prompt": "言語を選択 (1-3): ",
        "invalid_language_choice": "無効な選択です。1-3を選択してください。",
    },
    "zh-CN": {
        "title": "⚙️ AWS IoT Rules Engine 探索器",
        "separator": "=" * 45,
        "aws_config": "📍 AWS 配置:",
        "account_id": "账户 ID",
        "region": "区域",
        "description": "通过详细说明学习 AWS IoT Rules Engine 概念。",
        "debug_enabled": "🔍 调试模式已启用",
        "debug_features": ["• 完整的 API 请求/响应详细信息", "• 增强的错误诊断", "• 详细的规则执行跟踪"],
        "tip": "💡 提示: 使用 --debug 或 -d 标志获取详细信息",
        "client_initialized": "✅ AWS IoT 客户端初始化成功",
        "invalid_credentials": "❌ 无效的 AWS 凭证",
        "learning_intro_title": "AWS IoT Rules Engine - 消息路由和处理",
        "learning_intro_content": "AWS IoT Rules Engine 允许您根据 MQTT 消息内容路由和处理消息。规则使用类似 SQL 的语法来过滤消息，并可以触发操作，如将数据发送到其他 AWS 服务。这对于构建响应式 IoT 应用程序和自动化工作流程至关重要。",
        "learning_intro_next": "我们将探索规则创建、测试和管理",
        "press_enter": "按 Enter 继续...",
        "goodbye": "👋 再见！",
        "operations_menu": "⚙️ IoT Rules Engine 选项:",
        "operations": ["1. 创建新规则", "2. 列出现有规则", "3. 查看规则详细信息", "4. 测试规则 SQL", "5. 删除规则", "6. 退出"],
        "select_operation": "选择选项 (1-6):",
        "invalid_choice": "❌ 无效选择。请选择 1-6。",
        "create_rule_title": "📝 创建新规则",
        "rule_name_prompt": "输入规则名称:",
        "rule_description_prompt": "输入规则描述:",
        "sql_statement_prompt": "输入 SQL 语句（例如: SELECT * FROM 'topic/+' WHERE temperature > 25）:",
        "sql_valid": "✅ SQL 语句有效！",
        "sql_invalid": "❌ 无效的 SQL 语句:",
        "action_config_title": "⚙️ 规则操作配置:",
        "available_actions": ["1. CloudWatch 日志", "2. SNS 通知", "3. SQS 队列", "4. Lambda 函数"],
        "select_action": "选择操作 (1-4):",
        "cloudwatch_config_title": "📝 CloudWatch 日志配置:",
        "log_group_name_prompt": "日志组名称:",
        "iam_role_prompt": "IAM 角色:",
        "creating_iam_role": "🔄 创建 IAM 角色...",
        "iam_role_created": "✅ IAM 角色创建成功！",
        "attaching_policy": "🔄 将策略附加到角色...",
        "policy_attached": "✅ 策略附加成功！",
        "creating_rule": "🔄 创建 IoT 规则...",
        "rule_created": "✅ 规则创建成功！",
        "rule_creation_failed": "❌ 规则创建失败:",
        "list_rules_title": "📋 现有规则",
        "no_rules_found": "未找到规则",
        "found_rules": "找到 {} 个规则:",
        "rule_details_title": "🔍 规则详细信息",
        "select_rule_prompt": "选择要查看的规则:",
        "rule_name_label": "规则名称:",
        "rule_description_label": "描述:",
        "sql_statement_label": "SQL 语句:",
        "rule_actions_label": "操作:",
        "rule_status_label": "状态:",
        "rule_created_date_label": "创建日期:",
        "test_sql_title": "🧪 测试规则 SQL",
        "test_sql_prompt": "输入要测试的 SQL 语句:",
        "test_topic_prompt": "输入测试主题:",
        "test_message_prompt": "输入测试消息（JSON 格式）:",
        "sql_test_match": "✅ SQL 匹配成功！",
        "sql_test_no_match": "❌ SQL 不匹配",
        "sql_output_label": "SQL 输出:",
        "delete_rule_title": "🗑️ 删除规则",
        "select_rule_delete_prompt": "选择要删除的规则:",
        "confirm_delete_prompt": "确认删除规则 '{}'？ (yes/no):",
        "rule_deleted": "✅ 规则删除成功！",
        "rule_deletion_failed": "❌ 规则删除失败:",
        "deletion_cancelled": "删除已取消",
        "learning_moments": {
            "rules_engine_intro": {
                "title": "Rules Engine - 消息路由",
                "content": "IoT Rules Engine 允许您根据消息内容自动路由和处理 MQTT 消息。规则使用类似 SQL 的语法来过滤消息，并可以触发操作将数据发送到其他 AWS 服务。这对于构建响应式 IoT 应用程序至关重要。",
                "next": "我们将创建和测试 IoT 规则",
            },
            "sql_syntax": {
                "title": "SQL 语法 - 消息过滤",
                "content": "IoT Rules 使用类似 SQL 的语法来过滤和转换消息。您可以使用 SELECT 选择字段，FROM 指定主题模式，WHERE 应用过滤条件。支持函数如 topic()、timestamp() 和数学运算。",
                "next": "我们将测试不同的 SQL 模式",
            },
            "rule_actions": {
                "title": "规则操作 - 数据路由",
                "content": "规则操作定义匹配消息的处理方式。您可以将数据发送到 CloudWatch、SNS、SQS、Lambda、DynamoDB 等。每个操作都需要适当的 IAM 权限才能访问目标服务。",
                "next": "我们将配置规则操作",
            },
        },
        "api_error": "❌ API 错误:",
        "error": "❌ 错误:",
        "no_region_error": "❌ 未配置 AWS 区域",
        "region_setup_instructions": [
            "请使用以下方法之一配置您的 AWS 区域:",
            "1. 设置环境变量: export AWS_DEFAULT_REGION=us-east-1",
            "2. 配置 AWS CLI: aws configure",
            "3. 在 AWS 凭证文件中设置区域",
        ],
        "aws_context_error": "⚠️ 无法检索 AWS 上下文:",
        "aws_credentials_reminder": "   确保已配置 AWS 凭证",
        "debug_full_error": "🔍 调试: 完整错误响应:",
        "debug_full_traceback": "🔍 调试: 完整堆栈跟踪:",
        "invalid_characters_topic": "主题模式中的字符无效。只允许字母数字字符、连字符、下划线、正斜杠和 + 通配符。",
        "language_selection_title": "🌍 语言选择",
        "language_options": ["1. English", "2. Español (Spanish)", "3. 日本語 (Japanese)", "4. 中文 (Chinese)"],
        "select_language_prompt": "选择语言 (1-4): ",
        "invalid_language_choice": "无效选择。请选择 1-4。",
    },
    "ko": {
        "main_title": "⚙️ AWS IoT 규칙 엔진 탐색기",
        "aws_config_title": "📍 AWS 구성:",
        "account_id": "계정 ID",
        "region": "리전",
        "main_description": "실습을 통해 AWS IoT 규칙 엔진을 학습합니다.",
        "main_features": "이 도구는 다음을 시연합니다:",
        "feature_sql_syntax": "• IoT 규칙 엔진 SQL 구문 및 메시지 라우팅",
        "feature_topic_filtering": "• SELECT, FROM, WHERE 절을 사용한 토픽 필터링",
        "feature_republish_actions": "• 재게시 작업 및 IAM 역할 구성",
        "feature_lifecycle": "• 규칙 생명주기 관리 (생성, 활성화, 비활성화, 삭제)",
        "learning_moment_title": "📚 학습 포인트: IoT 규칙 엔진",
        "learning_moment_description": "AWS IoT 규칙 엔진은 SQL과 유사한 쿼리를 사용하여 디바이스의 메시지를 처리하고 라우팅합니다. 규칙은 Lambda, DynamoDB, S3와 같은 다양한 AWS 서비스로 메시지를 필터링, 변환 및 라우팅할 수 있습니다.",
        "next_action": "🔄 다음: 메시지 처리를 위한 IoT 규칙을 생성하고 관리합니다",
        "press_enter_continue": "계속하려면 Enter를 누르세요...",
        "debug_mode_enabled": "🔍 디버그 모드 활성화됨",
        "debug_tip": "💡 팁: 향상된 로깅을 위해 --debug 또는 -d 플래그를 사용하세요",
        "menu_title": "📋 IoT 규칙 엔진 메뉴:",
        "menu_option_1": "1. 모든 IoT 규칙 나열",
        "menu_option_2": "2. 특정 IoT 규칙 설명",
        "menu_option_3": "3. 새 IoT 규칙 생성",
        "menu_option_4": "4. 샘플 메시지로 IoT 규칙 테스트",
        "menu_option_5": "5. IoT 규칙 관리 (활성화/비활성화/삭제)",
        "menu_option_6": "6. 종료",
        "select_option": "옵션 선택 (1-6): ",
        "invalid_choice": "❌ 잘못된 선택입니다. 1-6을 선택하세요.",
        "press_enter_menu": "계속하려면 Enter를 누르세요...",
        "goodbye": "👋 안녕히 가세요!",
        "operation_failed": "❌ {operation} 실패: {error}",
        "unexpected_error": "❌ 예상치 못한 오류: {error}",
        "interrupted_by_user": "🛑 사용자에 의해 중단됨",
        "aws_context_error": "⚠️ AWS 컨텍스트를 가져올 수 없습니다: {error}",
        "aws_credentials_check": "AWS 자격 증명이 구성되어 있는지 확인하세요",
        "header_separator": "=" * 60,
        "step_separator": "-" * 50,
        "rule_separator": "-" * 40,
    },
}

# Global variable for user's preferred language
USER_LANG = "en"


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


def get_message(key, **kwargs):
    """Get localized message based on user's language preference"""
    # Get message from dictionary
    message = MESSAGES.get(USER_LANG, MESSAGES["en"]).get(key, key)

    # Format message with provided arguments
    if kwargs:
        try:
            return message.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return the unformatted message
            return message

    return message


def display_aws_context():
    """Display current AWS account and region information"""
    try:
        sts = boto3.client("sts")
        iot = boto3.client("iot")
        identity = sts.get_caller_identity()

        print(f"\n{get_message('aws_context_info')}")
        print(f"   {get_message('account_id')}: {identity['Account']}")
        print(f"   {get_message('region')}: {iot.meta.region_name}")
    except Exception as e:
        print(get_message("aws_context_error", error=str(e)))
        print(f"   {get_message('aws_credentials_check')}")
    print()


class IoTRulesExplorer:
    def __init__(self, debug=False):
        self.iot = boto3.client("iot")
        self.iam = boto3.client("iam")
        self.debug_mode = debug
        self.rule_role_name = "IoTRulesEngineRole"

    def print_header(self, title):
        """Print formatted header"""
        print(f"\n⚙️ {title}")
        print(get_message("header_separator"))

    def print_step(self, step, description):
        """Print step with formatting"""
        print(f"\n🔧 Step {step}: {description}")
        print(get_message("step_separator"))

    def validate_sql_clause(self, clause, clause_type):
        """Validate and sanitize SQL clause input"""
        if not clause:
            return ""

        # Remove potentially dangerous characters and patterns
        import re

        # For IoT Rules Engine SQL, allow alphanumeric, spaces, common operators, and IoT-specific functions
        if clause_type == "SELECT":  # nosec B608
            # Allow SELECT clause patterns: *, field names, functions like timestamp()  # nosec B608
            allowed_pattern = r"^[a-zA-Z0-9_\s,.*()=<>!+-]+$"
        elif clause_type == "WHERE":
            # Allow WHERE clause patterns: comparisons, logical operators
            allowed_pattern = r'^[a-zA-Z0-9_\s=<>!()\'".,-]+$'
        else:
            allowed_pattern = r"^[a-zA-Z0-9_\s]+$"

        if not re.match(allowed_pattern, clause):
            raise ValueError(get_message("invalid_characters_clause", clause_type=clause_type))

        # Additional validation for common injection patterns
        dangerous_patterns = ["--", "/*", "*/", ";", "DROP", "DELETE", "INSERT", "UPDATE", "EXEC"]
        clause_upper = clause.upper()
        for pattern in dangerous_patterns:
            if pattern in clause_upper:
                raise ValueError(get_message("dangerous_pattern_detected", pattern=pattern, clause_type=clause_type))

        return clause.strip()

    def validate_topic_pattern(self, topic):
        """Validate IoT topic pattern"""
        if not topic:
            return ""

        import re

        # IoT topics allow alphanumeric, hyphens, underscores, forward slashes, and wildcards
        allowed_pattern = r"^[a-zA-Z0-9_/+-]+$"

        if not re.match(allowed_pattern, topic):
            raise ValueError(get_message("invalid_characters_topic"))

        return topic.strip()

    def safe_operation(self, func, operation_name, **kwargs):
        """Execute operation with error handling and debug info"""
        try:
            if self.debug_mode:
                print(get_message("debug_operation", operation=operation_name))
                print(get_message("debug_input", input=json.dumps(kwargs, indent=2, default=str)))

            response = func(**kwargs)

            if self.debug_mode:
                print(get_message("debug_completed", operation=operation_name))
                if response:
                    output_str = json.dumps(response, indent=2, default=str)
                    truncated_output = output_str[:500] + ("..." if len(output_str) > 500 else "")
                    print(get_message("debug_output", output=truncated_output))

            return response, True
        except ClientError as e:
            print(get_message("operation_failed", operation=operation_name, error=e.response["Error"]["Message"]))
            if self.debug_mode:
                print(get_message("debug_error_code", code=e.response["Error"]["Code"]))
            return None, False
        except Exception as e:
            print(get_message("operation_failed", operation=operation_name, error=str(e)))
            return None, False

    def list_rules(self):
        """List all IoT rules with details"""
        self.print_header(get_message("list_rules_title"))

        response, success = self.safe_operation(self.iot.list_topic_rules, get_message("list_rules_title"))

        if not success:
            return

        rules = response.get("rules", [])

        if not rules:
            print(get_message("no_rules_found"))
            print(get_message("create_first_rule"))
            return

        print(get_message("found_rules", count=len(rules)))
        print()

        for i, rule in enumerate(rules, 1):
            rule_name = rule["ruleName"]
            created_at = rule.get("createdAt", "Unknown")
            rule_disabled = rule.get("ruleDisabled", False)
            status = get_message("rule_status_disabled") if rule_disabled else get_message("rule_status_enabled")

            print(f"{i}. {rule_name} - {status}")
            print(f"   {get_message('created_label', date=created_at)}")

            if self.debug_mode:
                print(f"   {get_message('debug_rule_arn', arn=rule.get('ruleArn', 'N/A'))}")

            # Get rule details
            rule_response, rule_success = self.safe_operation(
                self.iot.get_topic_rule, f"Get rule details for {rule_name}", ruleName=rule_name
            )

            if rule_success and rule_response:
                rule_payload = rule_response.get("rule", {})
                sql = rule_payload.get("sql", "N/A")
                actions = rule_payload.get("actions", [])

                print(f"   {get_message('sql_label', sql=sql)}")
                print(f"   {get_message('actions_count', count=len(actions))}")

                for j, action in enumerate(actions, 1):
                    if "republish" in action:
                        topic = action["republish"].get("topic", "N/A")
                        print(f"      {j}. {get_message('action_republish', topic=topic)}")
                    elif "s3" in action:
                        bucket = action["s3"].get("bucketName", "N/A")
                        print(f"      {j}. {get_message('action_s3', bucket=bucket)}")
                    elif "lambda" in action:
                        function_arn = action["lambda"].get("functionArn", "N/A")
                        function_name = function_arn.split(":")[-1] if ":" in function_arn else function_arn
                        print(f"      {j}. {get_message('action_lambda', function=function_name)}")
                    else:
                        action_type = list(action.keys())[0] if action else "Unknown"
                        print(f"      {j}. {action_type}")

            print()

    def describe_rule(self):
        """Describe a specific IoT rule in detail"""
        self.print_header(get_message("describe_rule_title"))

        # List rules first
        response, success = self.safe_operation(self.iot.list_topic_rules, get_message("list_rules_for_selection"))

        if not success:
            return

        rules = response.get("rules", [])

        if not rules:
            print(get_message("no_rules_found"))
            return

        print(get_message("available_rules"))
        for i, rule in enumerate(rules, 1):
            status = (
                get_message("rule_status_disabled") if rule.get("ruleDisabled", False) else get_message("rule_status_enabled")
            )
            print(f"   {i}. {rule['ruleName']} - {status}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_rule_describe', count=len(rules))}")) - 1
                if 0 <= choice < len(rules):
                    selected_rule = rules[choice]["ruleName"]
                    break
                else:
                    print(get_message("invalid_selection_range", count=len(rules)))
            except ValueError:
                print(get_message("enter_valid_number"))

        # Get detailed rule information
        rule_response, rule_success = self.safe_operation(
            self.iot.get_topic_rule, f"Get detailed rule information for {selected_rule}", ruleName=selected_rule
        )

        if not rule_success:
            return

        rule_payload = rule_response.get("rule", {})

        print(f"\n{get_message('rule_details_title', name=selected_rule)}")
        print(get_message("rule_separator"))

        # Basic information
        print(get_message("sql_statement_label"))
        print(f"   {rule_payload.get('sql', 'N/A')}")

        print(f"\n{get_message('sql_breakdown_label')}")
        sql = rule_payload.get("sql", "")
        if "SELECT" in sql.upper():  # nosec B608
            select_part = sql.split("FROM")[0].replace("SELECT", "").strip()  # nosec B608
            print(f"   {get_message('select_clause', clause=select_part)}")  # nosec B608

        if "FROM" in sql.upper():
            from_part = (
                sql.split("FROM")[1].split("WHERE")[0].strip() if "WHERE" in sql.upper() else sql.split("FROM")[1].strip()
            )
            print(f"   {get_message('from_clause', clause=from_part)}")

        if "WHERE" in sql.upper():
            where_part = sql.split("WHERE")[1].strip()
            print(f"   {get_message('where_clause', clause=where_part)}")

        # Actions
        actions = rule_payload.get("actions", [])
        print(f"\n{get_message('actions_title', count=len(actions))}")

        for i, action in enumerate(actions, 1):
            action_type = list(action.keys())[0] if action else "Unknown"
            print(f"   {i}. {get_message('action_type', type=action_type)}")

            if "republish" in action:
                republish = action["republish"]
                print(f"      {get_message('target_topic', topic=republish.get('topic', 'N/A'))}")
                print(f"      {get_message('role_arn', arn=republish.get('roleArn', 'N/A'))}")
                if "qos" in republish:
                    print(f"      {get_message('qos_label', qos=republish['qos'])}")

            elif "s3" in action:
                s3_action = action["s3"]
                print(f"      {get_message('bucket_label', bucket=s3_action.get('bucketName', 'N/A'))}")
                print(f"      {get_message('key_label', key=s3_action.get('key', 'N/A'))}")
                print(f"      {get_message('role_arn', arn=s3_action.get('roleArn', 'N/A'))}")

            elif "lambda" in action:
                lambda_action = action["lambda"]
                print(f"      {get_message('function_arn', arn=lambda_action.get('functionArn', 'N/A'))}")

        # Error action
        error_action = rule_payload.get("errorAction")
        if error_action:
            print(f"\n{get_message('error_action_title')}")
            error_type = list(error_action.keys())[0] if error_action else "Unknown"
            print(f"   {get_message('error_action_type', type=error_type)}")
            if "republish" in error_action:
                print(f"   {get_message('error_action_topic', topic=error_action['republish'].get('topic', 'N/A'))}")

        # Rule metadata
        print(f"\n{get_message('rule_metadata_title')}")
        status = (
            get_message("rule_status_disabled")
            if rule_payload.get("ruleDisabled", False)
            else get_message("rule_status_enabled")
        )
        print(f"   {get_message('rule_status', status=status)}")
        print(f"   {get_message('rule_created', date=rule_payload.get('createdAt', 'N/A'))}")

        if self.debug_mode:
            print(f"\n{get_message('debug_complete_payload')}")
            print(json.dumps(rule_payload, indent=2, default=str))

    def create_rule(self):
        """Interactive rule creation with guided SQL building"""
        self.print_header(get_message("create_rule_title"))

        print(get_message("create_learning_objectives"))
        print(get_message("objective_sql_syntax"))
        print(get_message("objective_topic_filtering"))
        print(get_message("objective_sql_clauses"))
        print(get_message("objective_republish_actions"))
        print()

        # Step 1: Rule name
        while True:
            rule_name = input(get_message("enter_rule_name")).strip()
            if rule_name and rule_name.replace("_", "").isalnum():
                break
            else:
                print(get_message("invalid_rule_name"))

        print(get_message("rule_name_confirmed", name=rule_name))

        # Step 2: Rule description
        rule_description = input(get_message("enter_rule_description")).strip()
        if not rule_description:
            rule_description = get_message("default_rule_description")

        print(get_message("rule_description_confirmed", description=rule_description))

        # Step 3: Build SQL statement
        print(f"\n{get_message('building_sql_title')}")
        print(get_message("sql_template"))

        # Event type selection
        event_types = ["temperature", "humidity", "pressure", "motion", "door", "alarm", "status", "battery"]

        print(f"\n{get_message('available_event_types')}")
        for i, event_type in enumerate(event_types, 1):
            print(f"   {i}. {event_type}")
        print(f"   {len(event_types) + 1}. {get_message('custom_event_type')}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_event_type', count=len(event_types) + 1)}"))
                if 1 <= choice <= len(event_types):
                    selected_event_type = event_types[choice - 1]
                    break
                elif choice == len(event_types) + 1:
                    selected_event_type = input(get_message("enter_custom_event_type")).strip()
                    if selected_event_type:
                        break
                    else:
                        print(get_message("event_type_empty"))
                else:
                    print(get_message("invalid_event_selection"))
            except ValueError:
                print(get_message("enter_valid_number"))

        # Topic pattern
        topic_pattern = f"testRulesEngineTopic/+/{selected_event_type}"
        print(get_message("topic_pattern_confirmed", pattern=topic_pattern))

        # SELECT clause based on event type
        print(f"\n{get_message('select_clause_title', event_type=selected_event_type)}")  # nosec B608

        # Event-specific attributes
        event_attributes = {  # nosec B608
            "temperature": ["*", "deviceId, timestamp, temperature", "deviceId, temperature, location"],
            "humidity": ["*", "deviceId, timestamp, humidity", "deviceId, humidity, location"],
            "pressure": ["*", "deviceId, timestamp, pressure", "deviceId, pressure, altitude"],
            "motion": ["*", "deviceId, timestamp, detected", "deviceId, detected, location"],
            "door": ["*", "deviceId, timestamp, status", "deviceId, status, location"],
            "alarm": ["*", "deviceId, timestamp, alertType", "deviceId, alertType, severity"],
            "status": ["*", "deviceId, timestamp, status", "deviceId, status, uptime"],
            "battery": ["*", "deviceId, timestamp, level", "deviceId, level, voltage"],
        }

        # Get attributes for selected event type or use generic ones
        available_attributes = event_attributes.get(
            selected_event_type, ["*", "deviceId, timestamp, value", "deviceId, value, status"]
        )
        available_attributes.append(get_message("custom_selection"))

        for i, attr in enumerate(available_attributes, 1):
            print(f"   {i}. {attr}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_attributes', count=len(available_attributes))}"))
                if 1 <= choice <= len(available_attributes) - 1:
                    select_clause = available_attributes[choice - 1]  # nosec B608
                    break
                elif choice == len(available_attributes):
                    select_clause = input(get_message("enter_custom_select")).strip()
                    if select_clause:
                        break
                    else:
                        print(get_message("select_clause_empty"))
                else:
                    print(get_message("invalid_event_selection"))
            except ValueError:
                print(get_message("enter_valid_number"))

        print(get_message("select_clause_confirmed", clause=select_clause))  # nosec B608

        # WHERE clause (optional) with event-specific examples
        print(f"\n{get_message('where_clause_title', event_type=selected_event_type)}")

        # Event-specific WHERE examples
        where_examples = {
            "temperature": ["temperature > 25", "temperature < 0", "location = 'warehouse'"],
            "humidity": ["humidity > 80", "humidity < 30", "location = 'greenhouse'"],
            "pressure": ["pressure > 1013", "pressure < 950", "altitude > 1000"],
            "motion": ["detected = true", "location = 'entrance'", "timestamp > timestamp() - 300000"],
            "door": ["status = 'open'", "status = 'closed'", "location = 'main_entrance'"],
            "alarm": ["alertType = 'fire'", "severity = 'high'", "alertType = 'intrusion'"],
            "status": ["status = 'offline'", "uptime < 3600", "status = 'maintenance'"],
            "battery": ["level < 20", "level < 10", "voltage < 3.0"],
        }

        examples = where_examples.get(
            selected_event_type, ["value > 25", "status = 'active'", "timestamp > timestamp() - 3600000"]
        )
        print(get_message("where_examples_title", event_type=selected_event_type))
        for example in examples:
            print(f"   • {example}")

        add_where = input(f"\n{get_message('add_where_condition')}").strip().lower()
        where_clause = ""

        if add_where == "y":
            where_clause = input(get_message("enter_where_condition")).strip()
            if where_clause:
                print(get_message("where_clause_confirmed", clause=where_clause))
            else:
                print(get_message("empty_where_warning"))

        # Build complete SQL with input validation
        try:
            # Validate and sanitize inputs to prevent injection
            safe_select_clause = self.validate_sql_clause(select_clause, "SELECT")  # nosec B608
            safe_topic_pattern = self.validate_topic_pattern(topic_pattern)
            safe_where_clause = self.validate_sql_clause(where_clause, "WHERE") if where_clause else ""

            sql_statement = "SELECT {} FROM '{}'".format(safe_select_clause, safe_topic_pattern)  # nosec B608
            if safe_where_clause:
                sql_statement += " WHERE {}".format(safe_where_clause)
        except ValueError as e:
            print(get_message("input_validation_error", error=str(e)))
            print(get_message("validation_tip"))
            return

        print(f"\n{get_message('complete_sql_title')}")
        print(f"   {sql_statement}")

        # Step 4: Configure republish action
        print(f"\n{get_message('republish_config_title')}")

        target_topic = input(get_message("enter_target_topic")).strip()
        if not target_topic:
            target_topic = f"processed/{selected_event_type}"
            print(get_message("default_target_topic", topic=target_topic))

        # Step 5: Create/verify IAM role
        print(f"\n{get_message('iam_role_setup')}")
        role_arn = self.ensure_iot_rule_role()

        if not role_arn:
            print(get_message("iam_role_failed"))
            return

        # Step 6: Create the rule
        print(f"\n{get_message('creating_rule')}")

        rule_payload = {
            "sql": sql_statement,
            "description": rule_description,
            "actions": [{"republish": {"topic": target_topic, "roleArn": role_arn, "qos": 1}}],
            "ruleDisabled": False,
        }

        if self.debug_mode:
            print(get_message("debug_rule_payload"))
            print(json.dumps(rule_payload, indent=2))

        # Try creating the rule with retry for IAM propagation
        max_retries = 3
        for attempt in range(max_retries):
            response, success = self.safe_operation(
                self.iot.create_topic_rule,
                get_message("create_rule_attempt", name=rule_name, attempt=attempt + 1, max_attempts=max_retries),
                ruleName=rule_name,
                topicRulePayload=rule_payload,
            )

            if success:
                break
            elif attempt < max_retries - 1:
                # Check if it's an IAM role propagation issue
                print(get_message("iam_propagation_wait"))
                time.sleep(10)  # nosemgrep: arbitrary-sleep
            else:
                print(get_message("create_rule_failed", attempts=max_retries))
                return

        if success:
            print(f"\n{get_message('rule_created_success', name=rule_name)}")
            print(f"\n{get_message('rule_summary_title')}")
            print(f"   {get_message('summary_name', name=rule_name)}")
            print(f"   {get_message('summary_source_topic', topic=topic_pattern)}")
            print(f"   {get_message('summary_target_topic', topic=target_topic)}")
            print(f"   {get_message('summary_sql', sql=sql_statement)}")
            print(f"   {get_message('summary_role', role=role_arn)}")

            print(f"\n{get_message('testing_rule_title')}")
            print(f"   {get_message('testing_step_1', event_type=selected_event_type)}")
            print(f"   {get_message('testing_step_2', topic=target_topic)}")
            print(f"   {get_message('testing_step_3')}")

            print(f"\n{get_message('example_test_message')}")
            example_message = {
                "deviceId": "device123",
                "timestamp": int(time.time() * 1000),
                "value": 25.5 if selected_event_type in ["temperature", "humidity", "pressure"] else "active",
            }
            print(f"   {json.dumps(example_message, indent=2)}")

    def ensure_iot_rule_role(self):
        """Create or verify IAM role for IoT Rules Engine"""
        try:
            # Check if role exists
            response = self.iam.get_role(RoleName=self.rule_role_name)
            role_arn = response["Role"]["Arn"]

            if self.debug_mode:
                print(get_message("debug_existing_role", arn=role_arn))

            print(get_message("using_existing_role", name=self.rule_role_name))
            return role_arn

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                # Role doesn't exist, create it
                print(get_message("creating_iam_role", name=self.rule_role_name))
                return self.create_iot_rule_role()
            else:
                print(get_message("error_checking_role", error=e.response["Error"]["Message"]))
                return None

    def create_iot_rule_role(self):
        """Create IAM role with necessary permissions for IoT Rules"""
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Principal": {"Service": "iot.amazonaws.com"}, "Action": "sts:AssumeRole"}],
        }

        # Create role
        response, success = self.safe_operation(
            self.iam.create_role,
            get_message("create_iam_role_operation", name=self.rule_role_name),
            RoleName=self.rule_role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="IAM role for AWS IoT Rules Engine learning exercises",
        )

        if not success:
            return None

        role_arn = response["Role"]["Arn"]

        # Create and attach policy for IoT actions
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [{"Effect": "Allow", "Action": ["iot:Publish"], "Resource": "*"}],
        }

        policy_name = "IoTRulesEnginePolicy"

        # Create policy
        policy_response, policy_success = self.safe_operation(
            self.iam.create_policy,
            get_message("create_iam_policy_operation", name=policy_name),
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description="Policy for IoT Rules Engine to publish messages",
        )

        if policy_success:
            policy_arn = policy_response["Policy"]["Arn"]

            # Attach policy to role
            attach_response, attach_success = self.safe_operation(
                self.iam.attach_role_policy,
                get_message("attach_policy_operation"),
                RoleName=self.rule_role_name,
                PolicyArn=policy_arn,
            )

            if attach_success:
                print(get_message("iam_role_created_success"))
                print(get_message("iam_role_propagation"))
                # Wait longer for IAM consistency
                time.sleep(10)  # nosemgrep: arbitrary-sleep
                return role_arn

        return None

    def manage_rule(self):
        """Enable, disable, or delete rules"""
        self.print_header(get_message("manage_rule_title"))

        # List rules first
        response, success = self.safe_operation(self.iot.list_topic_rules, get_message("list_rules_for_management"))

        if not success:
            return

        rules = response.get("rules", [])

        if not rules:
            print(get_message("no_rules_found"))
            return

        print(get_message("available_rules"))
        for i, rule in enumerate(rules, 1):
            status = (
                get_message("rule_status_disabled") if rule.get("ruleDisabled", False) else get_message("rule_status_enabled")
            )
            print(f"   {i}. {rule['ruleName']} - {status}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_rule_manage', count=len(rules))}")) - 1
                if 0 <= choice < len(rules):
                    selected_rule = rules[choice]
                    break
                else:
                    print(get_message("invalid_selection_range", count=len(rules)))
            except ValueError:
                print(get_message("enter_valid_number"))

        rule_name = selected_rule["ruleName"]
        is_disabled = selected_rule.get("ruleDisabled", False)

        print(f"\n{get_message('managing_rule', name=rule_name)}")
        current_status = get_message("rule_status_disabled") if is_disabled else get_message("rule_status_enabled")
        print(f"{get_message('current_status', status=current_status)}")

        print(f"\n{get_message('management_options')}")
        if is_disabled:
            print(f"   {get_message('enable_rule')}")
        else:
            print(f"   {get_message('disable_rule')}")
        print(f"   {get_message('delete_rule')}")
        print(f"   {get_message('cancel_management')}")

        while True:
            try:
                action = int(input(f"\n{get_message('select_action')}"))
                if action in [1, 2, 3]:
                    break
                else:
                    print(get_message("invalid_action_selection"))
            except ValueError:
                print(get_message("enter_valid_number"))

        if action == 1:
            # Enable/Disable rule
            new_disabled_status = not is_disabled  # If currently disabled, we want to enable (set ruleDisabled=False)
            action_name = (
                get_message("enable_rule_operation", name=rule_name)
                if is_disabled
                else get_message("disable_rule_operation", name=rule_name)
            )

            # Get current rule to preserve settings
            rule_response, rule_success = self.safe_operation(
                self.iot.get_topic_rule, get_message("get_current_rule_settings"), ruleName=rule_name
            )

            if rule_success:
                current_rule = rule_response["rule"]

                # Create clean payload with only allowed fields
                clean_payload = {
                    "sql": current_rule.get("sql", 'SELECT * FROM "temp"'),
                    "ruleDisabled": new_disabled_status,
                    "actions": current_rule.get("actions", []),
                }

                # Add optional fields if they exist
                if "description" in current_rule:
                    clean_payload["description"] = current_rule["description"]
                if "awsIotSqlVersion" in current_rule:
                    clean_payload["awsIotSqlVersion"] = current_rule["awsIotSqlVersion"]
                if "errorAction" in current_rule:
                    clean_payload["errorAction"] = current_rule["errorAction"]

                response, success = self.safe_operation(
                    self.iot.replace_topic_rule, action_name, ruleName=rule_name, topicRulePayload=clean_payload
                )

                if success:
                    status_text = (
                        get_message("rule_status_enabled") if not new_disabled_status else get_message("rule_status_disabled")
                    )
                    print(get_message("rule_status_updated", name=rule_name, status=status_text))
            else:
                print(get_message("failed_get_rule_settings", name=rule_name))

        elif action == 2:
            # Delete rule
            confirm = input(get_message("confirm_delete_rule", name=rule_name)).strip().lower()

            if confirm == "y":
                response, success = self.safe_operation(
                    self.iot.delete_topic_rule, get_message("delete_rule_operation", name=rule_name), ruleName=rule_name
                )

                if success:
                    print(get_message("rule_deleted_success", name=rule_name))
            else:
                print(get_message("rule_deletion_cancelled"))

        elif action == 3:
            print(get_message("management_cancelled"))

    def test_rule(self):
        """Test IoT rules with sample messages"""
        self.print_header(get_message("test_rule_title"))

        print(get_message("test_learning_objectives"))
        print(get_message("test_objective_1"))
        print(get_message("test_objective_2"))
        print(get_message("test_objective_3"))
        print(get_message("test_objective_4"))
        print()

        # List rules first
        response, success = self.safe_operation(self.iot.list_topic_rules, get_message("list_rules_for_testing"))

        if not success:
            return

        rules = response.get("rules", [])

        if not rules:
            print(get_message("no_rules_for_testing"))
            print(get_message("create_rule_first"))
            return

        print(get_message("available_rules"))
        for i, rule in enumerate(rules, 1):
            status = (
                get_message("rule_status_disabled") if rule.get("ruleDisabled", False) else get_message("rule_status_enabled")
            )
            print(f"   {i}. {rule['ruleName']} - {status}")

        while True:
            try:
                choice = int(input(f"\n{get_message('select_rule_test', count=len(rules))}")) - 1
                if 0 <= choice < len(rules):
                    selected_rule = rules[choice]
                    break
                else:
                    print(get_message("invalid_selection_range", count=len(rules)))
            except ValueError:
                print(get_message("enter_valid_number"))

        rule_name = selected_rule["ruleName"]

        # Get rule details
        rule_response, rule_success = self.safe_operation(
            self.iot.get_topic_rule, get_message("get_rule_details_testing"), ruleName=rule_name
        )

        if not rule_success:
            return

        rule_payload = rule_response.get("rule", {})
        sql_statement = rule_payload.get("sql", "")

        print(f"\n{get_message('testing_rule', name=rule_name)}")
        print(get_message("sql_display", sql=sql_statement))

        # Parse SQL to extract topic pattern
        topic_pattern = self.extract_topic_from_sql(sql_statement)
        where_condition = self.extract_where_from_sql(sql_statement)

        if topic_pattern:
            print(get_message("source_topic_pattern", pattern=topic_pattern))
        if where_condition:
            print(get_message("where_condition_display", condition=where_condition))

        # Get republish target topics
        actions = rule_payload.get("actions", [])
        target_topics = []
        for action in actions:
            if "republish" in action:
                target_topics.append(action["republish"].get("topic", "unknown"))

        if target_topics:
            print(get_message("target_topics_display", topics=", ".join(target_topics)))

        # Get device selection
        selected_device = self.select_device_with_certificates()
        if not selected_device:
            return

        # Get IoT endpoint
        endpoint_response, endpoint_success = self.safe_operation(
            self.iot.describe_endpoint, get_message("get_iot_endpoint"), endpointType="iot:Data-ATS"
        )

        if not endpoint_success:
            print(get_message("cannot_get_endpoint"))
            return

        endpoint = endpoint_response["endpointAddress"]

        # Start interactive testing
        self.run_rule_testing(endpoint, selected_device, rule_name, topic_pattern, where_condition, target_topics)

    def extract_topic_from_sql(self, sql):
        """Extract topic pattern from SQL FROM clause"""
        try:
            if "FROM" in sql.upper():
                from_part = (
                    sql.split("FROM")[1].split("WHERE")[0].strip() if "WHERE" in sql.upper() else sql.split("FROM")[1].strip()
                )
                # Remove quotes
                topic = from_part.strip("'\"")
                return topic
        except (IndexError, AttributeError):
            pass
        return None

    def extract_where_from_sql(self, sql):
        """Extract WHERE condition from SQL"""
        try:
            if "WHERE" in sql.upper():
                where_part = sql.split("WHERE")[1].strip()
                return where_part
        except (IndexError, AttributeError):
            pass
        return None

    def select_device_with_certificates(self):
        """Select device with certificates like other scripts"""
        print(f"\n{get_message('finding_devices_certificates')}")

        cert_dir = "certificates"
        if not os.path.exists(cert_dir):
            print(get_message("no_certificates_directory"))
            print(get_message("run_certificate_manager"))
            return None

        # Find available devices with certificates
        available_devices = []
        for thing_dir in os.listdir(cert_dir):
            thing_path = os.path.join(cert_dir, thing_dir)
            if os.path.isdir(thing_path):
                cert_files = [f for f in os.listdir(thing_path) if f.endswith(".crt")]
                if cert_files:
                    cert_id = cert_files[0].replace(".crt", "")
                    cert_path = os.path.join(thing_path, f"{cert_id}.crt")
                    key_path = os.path.join(thing_path, f"{cert_id}.key")
                    if os.path.exists(key_path):
                        available_devices.append(
                            {"thing_name": thing_dir, "cert_path": cert_path, "key_path": key_path, "cert_id": cert_id}
                        )

        if not available_devices:
            print(get_message("no_devices_certificates"))
            print(get_message("run_certificate_manager"))
            return None

        print(get_message("found_devices_certificates", count=len(available_devices)))
        for i, device in enumerate(available_devices, 1):
            print(f"   {i}. {device['thing_name']}")

        if len(available_devices) == 1:
            selected_device = available_devices[0]
            print(get_message("using_device", name=selected_device["thing_name"]))
        else:
            while True:
                try:
                    choice = int(input(f"\n{get_message('select_device', count=len(available_devices))}")) - 1
                    if 0 <= choice < len(available_devices):
                        selected_device = available_devices[choice]
                        print(get_message("selected_device", name=selected_device["thing_name"]))
                        break
                    else:
                        print(get_message("invalid_device_selection"))
                except ValueError:
                    print(get_message("enter_valid_number"))

        return selected_device

    def run_rule_testing(self, endpoint, device_info, rule_name, topic_pattern, where_condition, target_topics):
        """Run interactive rule testing with AWS IoT SDK"""
        print(f"\n{get_message('interactive_testing_title')}")
        print(get_message("connecting_to_endpoint", endpoint=endpoint))
        print(get_message("using_device_info", device=device_info["thing_name"]))

        # Setup event loop and connection
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        messages_received = []

        def on_message_received(topic, payload, dup, qos, retain, **kwargs):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            message_data = {"timestamp": timestamp, "topic": topic, "payload": payload.decode("utf-8")}
            messages_received.append(message_data)
            print(f"\n{get_message('rule_output_received', timestamp=timestamp)}")
            print(get_message("message_topic", topic=topic))
            print(get_message("message_content", message=payload.decode("utf-8")))
            print(get_message("rule_processed_forwarded", name=rule_name))

        # Create MQTT connection
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=endpoint,
            cert_filepath=device_info["cert_path"],
            pri_key_filepath=device_info["key_path"],
            client_bootstrap=client_bootstrap,
            client_id=f"rule-tester-{device_info['thing_name']}",
            clean_session=False,
            keep_alive_secs=30,
            on_connection_interrupted=lambda connection, error, **kwargs: print(
                get_message("connection_interrupted", error=error)
            ),
            on_connection_resumed=lambda connection, return_code, session_present, **kwargs: print(
                get_message("connection_resumed")
            ),
        )

        try:
            print(get_message("connecting_aws_iot"))
            connect_future = mqtt_connection.connect()
            connect_future.result(timeout=10)
            print(get_message("connected_aws_iot"))

            # Subscribe to target topics
            for topic in target_topics:
                subscribe_future, _ = mqtt_connection.subscribe(
                    topic=topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received
                )
                subscribe_future.result(timeout=10)
                print(get_message("subscribed_target_topic", topic=topic))

            print(f"\n{get_message('rule_testing_instructions')}")
            print(get_message("instruction_1"))
            print(get_message("instruction_2"))
            print(get_message("instruction_3"))
            print(get_message("instruction_4"))
            print(get_message("instruction_5"))

            # Interactive testing loop
            test_count = 0
            while True:
                test_count += 1
                print(f"\n{get_message('header_separator')}")
                print(get_message("test_message_header", count=test_count))
                print(f"{get_message('header_separator')}")

                # Ask about topic matching
                pattern_display = topic_pattern or get_message("no_specific_pattern")
                print(f"\n{get_message('topic_pattern_display', pattern=pattern_display)}")
                topic_should_match = input(get_message("should_match_topic")).strip().lower()

                if topic_should_match == "quit":
                    break

                # Generate test topic
                if topic_should_match == "y":
                    test_topic = self.generate_matching_topic(topic_pattern)
                else:
                    test_topic = self.generate_non_matching_topic(topic_pattern)

                print(get_message("generated_topic", topic=test_topic))

                # Ask about WHERE condition
                where_should_match = "y"  # Default if no WHERE clause
                if where_condition:
                    print(f"\n{get_message('where_condition_label', condition=where_condition)}")
                    where_should_match = input(get_message("should_match_where")).strip().lower()

                # Generate test message
                test_message = self.generate_test_message(where_condition, where_should_match == "y")

                print(f"\n{get_message('test_message_display')}")
                print(get_message("topic_label", topic=test_topic))
                print(get_message("payload_label", payload=json.dumps(test_message, indent=2)))

                # Predict outcome
                should_trigger = (topic_should_match == "y") and (where_should_match == "y")
                prediction_msg = (
                    get_message("prediction_should_trigger")
                    if should_trigger
                    else get_message("prediction_should_not_trigger")
                )
                print(f"\n{prediction_msg}")

                # Publish message
                print(f"\n{get_message('publishing_test_message')}")
                publish_future, _ = mqtt_connection.publish(
                    topic=test_topic, payload=json.dumps(test_message), qos=mqtt.QoS.AT_LEAST_ONCE
                )
                publish_future.result(timeout=10)

                # Wait for potential rule output
                print(get_message("waiting_rule_processing"))
                time.sleep(3)  # nosemgrep: arbitrary-sleep

                # Simple check for recent messages
                recent_count = len([msg for msg in messages_received[-3:]])

                if should_trigger and recent_count == 0:
                    print(get_message("expected_trigger_no_output"))
                elif not should_trigger and recent_count > 0:
                    print(get_message("unexpected_trigger"))
                elif should_trigger:
                    print(get_message("rule_triggered_expected"))
                else:
                    print(get_message("rule_correctly_not_triggered"))

                input(f"\n{get_message('press_enter_next_test')}")

        except Exception as e:
            print(get_message("testing_error", error=str(e)))
        finally:
            print(f"\n{get_message('disconnecting_aws_iot')}")
            disconnect_future = mqtt_connection.disconnect()
            disconnect_future.result(timeout=10)
            print(get_message("disconnected_aws_iot"))

    def generate_matching_topic(self, topic_pattern):
        """Generate a topic that matches the pattern"""
        if not topic_pattern:
            return "testRulesEngineTopic/device123/temperature"

        # Replace + wildcards with actual values
        topic = topic_pattern.replace("+", "device123")
        return topic

    def generate_non_matching_topic(self, topic_pattern):
        """Generate a topic that doesn't match the pattern"""
        if not topic_pattern:
            return "different/topic/structure"

        # Create a different structure
        return "nonmatching/topic/path"

    def generate_test_message(self, where_condition, should_match):
        """Generate test message based on WHERE condition"""
        base_message = {"deviceId": "test-device-123", "timestamp": int(time.time() * 1000)}

        if not where_condition:
            # No WHERE condition, add generic data
            base_message.update({"temperature": 23.5, "humidity": 45.0, "status": "active"})
            return base_message

        # Parse WHERE condition and generate appropriate data
        condition_lower = where_condition.lower()

        if "temperature" in condition_lower:
            if should_match:
                if ">" in condition_lower:
                    # Extract number and make it higher
                    try:
                        threshold = float(condition_lower.split(">")[1].strip())
                        base_message["temperature"] = threshold + 5
                    except (ValueError, IndexError):
                        base_message["temperature"] = 30.0
                elif "<" in condition_lower:
                    try:
                        threshold = float(condition_lower.split("<")[1].strip())
                        base_message["temperature"] = threshold - 5
                    except (ValueError, IndexError):
                        base_message["temperature"] = 15.0
                else:
                    base_message["temperature"] = 25.0
            else:
                if ">" in condition_lower:
                    try:
                        threshold = float(condition_lower.split(">")[1].strip())
                        base_message["temperature"] = threshold - 5
                    except (ValueError, IndexError):
                        base_message["temperature"] = 20.0
                elif "<" in condition_lower:
                    try:
                        threshold = float(condition_lower.split("<")[1].strip())
                        base_message["temperature"] = threshold + 5
                    except (ValueError, IndexError):
                        base_message["temperature"] = 30.0

        elif "humidity" in condition_lower:
            if should_match:
                base_message["humidity"] = 85.0 if ">" in condition_lower else 25.0
            else:
                base_message["humidity"] = 40.0

        elif "status" in condition_lower:
            if should_match:
                if "'active'" in condition_lower or '"active"' in condition_lower:
                    base_message["status"] = "active"
                elif "'offline'" in condition_lower or '"offline"' in condition_lower:
                    base_message["status"] = "offline"
                else:
                    base_message["status"] = "active"
            else:
                base_message["status"] = "inactive"

        elif "level" in condition_lower or "battery" in condition_lower:
            if should_match:
                base_message["level"] = 15 if "<" in condition_lower else 85
            else:
                base_message["level"] = 50

        else:
            # Generic condition, add some data
            base_message.update({"value": 30.0 if should_match else 15.0, "status": "active" if should_match else "inactive"})

        return base_message


def main():
    try:
        # Get user's preferred language
        global USER_LANG
        USER_LANG = get_language()

        # Check for debug flag
        debug_mode = "--debug" in sys.argv or "-d" in sys.argv

        print(get_message("main_title"))
        print(get_message("header_separator"))

        # Display AWS context first
        try:
            sts = boto3.client("sts")
            iot = boto3.client("iot")
            identity = sts.get_caller_identity()

            print(get_message("aws_config_title"))
            print(f"   {get_message('account_id')}: {identity['Account']}")
            print(f"   {get_message('region')}: {iot.meta.region_name}")
            print()

        except Exception as e:
            print(get_message("aws_context_error", error=str(e)))
            print(f"   {get_message('aws_credentials_check')}")
            print()

        print(get_message("main_description"))
        print(get_message("main_features"))
        print(get_message("feature_sql_syntax"))
        print(get_message("feature_topic_filtering"))
        print(get_message("feature_republish_actions"))
        print(get_message("feature_lifecycle"))

        print(f"\n{get_message('learning_moment_title')}")
        print(get_message("learning_moment_description"))
        print(f"\n{get_message('next_action')}")
        input(get_message("press_enter_continue"))

        if debug_mode:
            print(f"\n{get_message('debug_mode_enabled')}")
            print(get_message("debug_features"))
            print(get_message("debug_features_2"))
            print(get_message("debug_features_3"))
        else:
            print(f"\n{get_message('debug_tip')}")

        print(get_message("header_separator"))

        explorer = IoTRulesExplorer(debug=debug_mode)

        try:
            while True:
                print(f"\n{get_message('menu_title')}")
                print(get_message("menu_option_1"))
                print(get_message("menu_option_2"))
                print(get_message("menu_option_3"))
                print(get_message("menu_option_4"))
                print(get_message("menu_option_5"))
                print(get_message("menu_option_6"))

                choice = input(f"\n{get_message('select_option')}").strip()

                if choice == "1":
                    print(f"\n{get_message('learning_moment_inventory')}")
                    print(get_message("learning_moment_inventory_desc"))
                    print(f"\n{get_message('next_list_rules')}")
                    input(get_message("press_enter_continue"))

                    explorer.list_rules()
                    input(f"\n{get_message('press_enter_menu')}")
                elif choice == "2":
                    print(f"\n{get_message('learning_moment_analysis')}")
                    print(get_message("learning_moment_analysis_desc"))
                    print(f"\n{get_message('next_examine_rule')}")
                    input(get_message("press_enter_continue"))

                    explorer.describe_rule()
                    input(f"\n{get_message('press_enter_menu')}")
                elif choice == "3":
                    print(f"\n{get_message('learning_moment_creation')}")
                    print(get_message("learning_moment_creation_desc"))
                    print(f"\n{get_message('next_create_rule')}")
                    input(get_message("press_enter_continue"))

                    explorer.create_rule()
                    input(f"\n{get_message('press_enter_menu')}")
                elif choice == "4":
                    print(f"\n{get_message('learning_moment_testing')}")
                    print(get_message("learning_moment_testing_desc"))
                    print(f"\n{get_message('next_test_rule')}")
                    input(get_message("press_enter_continue"))

                    explorer.test_rule()
                    input(f"\n{get_message('press_enter_menu')}")
                elif choice == "5":
                    print(f"\n{get_message('learning_moment_lifecycle')}")
                    print(get_message("learning_moment_lifecycle_desc"))
                    print(f"\n{get_message('next_manage_rule')}")
                    input(get_message("press_enter_continue"))

                    explorer.manage_rule()
                    input(f"\n{get_message('press_enter_menu')}")
                elif choice == "6":
                    print(get_message("goodbye"))
                    break
                else:
                    print(get_message("invalid_choice"))
                    input(f"\n{get_message('press_enter_menu')}")

        except KeyboardInterrupt:
            print(f"\n\n{get_message('interrupted_by_user')}")
        except Exception as e:
            print(get_message("unexpected_error", error=str(e)))
            if debug_mode:
                import traceback

                traceback.print_exc()

    except KeyboardInterrupt:
        print(f"\n\n{get_message('goodbye')}")


if __name__ == "__main__":
    main()

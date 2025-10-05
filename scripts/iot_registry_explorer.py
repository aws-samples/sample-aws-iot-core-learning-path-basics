#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import sys

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError

# Simple translation system for learning content
MESSAGES = {
    "en": {
        "title": "🚀 AWS IoT Registry API Explorer",
        "separator": "=" * 40,
        "aws_config": "📍 AWS Configuration:",
        "account_id": "Account ID",
        "region": "Region",
        "description": "Interactive exploration of AWS IoT Registry APIs with detailed explanations.",
        "debug_enabled": "🔍 DEBUG MODE ENABLED",
        "debug_features": [
            "• Full API request/response details",
            "• Complete HTTP information",
            "• Enhanced error diagnostics",
        ],
        "tip": "💡 Tip: Use --debug or -d flag for detailed API information",
        "tip_features": ["• Condensed mode shows key metrics only", "• Debug mode shows complete API details"],
        "client_initialized": "✅ AWS IoT client initialized successfully",
        "invalid_credentials": "❌ Invalid AWS credentials",
        "learning_intro_title": "AWS IoT Registry APIs - Device Management",
        "learning_intro_content": "The AWS IoT Registry is the central database that stores information about your IoT devices (Things), their organization (Thing Groups), device templates (Thing Types), and security certificates. These APIs allow you to programmatically manage your entire IoT device fleet. Understanding these operations is fundamental to building scalable IoT solutions.",
        "learning_intro_next": "We will explore 8 core Registry APIs with detailed explanations",
        "press_enter": "Press Enter to continue...",
        "goodbye": "👋 Goodbye!",
        "operations_menu": "📋 Available Operations:",
        "operations": [
            "1. List Things",
            "2. List Certificates",
            "3. List Thing Groups",
            "4. List Thing Types",
            "5. Describe Thing",
            "6. Describe Thing Group",
            "7. Describe Thing Type",
            "8. Describe Endpoint",
            "9. Exit",
        ],
        "select_operation": "Select operation (1-9):",
        "invalid_choice": "❌ Invalid choice. Please select 1-9.",
        "list_things_options": "🔍 List Things Options:",
        "list_things_menu": [
            "   1. List all Things (basic)",
            "   2. List Things with pagination",
            "   3. Filter Things by Thing Type",
            "   4. Filter Things by attribute",
        ],
        "select_option": "Select option (1-4):",
        "max_results_prompt": "Enter maximum results per page (default 5):",
        "thing_type_prompt": "Enter Thing Type name (e.g., SedanVehicle):",
        "attribute_name_prompt": "Enter attribute name (e.g., country):",
        "attribute_value_prompt": "Enter attribute value (e.g., US):",
        "no_thing_type": "❌ No Thing Type specified",
        "attribute_required": "❌ Attribute name and value are required",
        "executing": "🔄 Executing:",
        "completed": "completed",
        "found_things": "📊 Found {} Things",
        "thing_names": "   Thing Names:",
        "found_certificates": "📊 Found {} Certificates",
        "certificate_ids": "   Certificate IDs:",
        "found_thing_groups": "📊 Found {} Thing Groups",
        "group_names": "   Group Names:",
        "found_thing_types": "📊 Found {} Thing Types",
        "type_names": "   Type Names:",
        "return_to_menu": "Press Enter to return to menu...",
        "available_things": "📋 Available Things",
        "available_groups": "📋 Available Thing Groups",
        "available_types": "📋 Available Thing Types",
        "enter_thing_name": "Enter Thing name: ",
        "enter_group_selection": "Enter number or Thing Group name: ",
        "enter_type_selection": "Enter number or Thing Type name: ",
        "no_things_found": "⚠️ No Things found in your account",
        "no_groups_found": "⚠️ No Thing Groups found in your account",
        "no_types_found": "⚠️ No Thing Types found in your account",
        "could_not_list_things": "⚠️ Could not list Things:",
        "could_not_list_groups": "⚠️ Could not list Thing Groups:",
        "could_not_list_types": "⚠️ Could not list Thing Types:",
        "invalid_selection": "❌ Invalid selection. Please choose",
        "endpoint_type_prompt": "Enter endpoint type (iot:Data-ATS, iot:CredentialProvider, iot:Jobs) [default: iot:Data-ATS]: ",
        "pagination_learning_title": "📚 LEARNING MOMENT: Pagination",
        "pagination_learning_content": "Pagination allows you to retrieve large datasets in smaller chunks. This is essential when managing hundreds or thousands of devices to avoid timeouts and memory issues.",
        "pagination_listing": "🔄 Listing Things with pagination (max {} per page)...",
        "page_summary": "📊 Page {} Summary: {} Things retrieved",
        "continue_next_page": "Continue to next page? (y/N): ",
        "pagination_complete": "🏁 Pagination Complete: {} total Things found across {} page(s)",
        "filter_by_type_learning_title": "📚 LEARNING MOMENT: Filtering by Thing Type",
        "filter_by_type_learning_content": "Filtering allows you to find specific categories of devices. Thing Types act as templates that group similar devices together.",
        "filtering_by_type": "🔄 Filtering Things by Thing Type: {}...",
        "filter_type_results": "📊 Filter Results: {} Things found with Thing Type '{}'",
        "filter_by_attribute_learning_title": "📚 LEARNING MOMENT: Filtering by Attributes",
        "filter_by_attribute_learning_content": "Attribute filtering helps you find devices with specific characteristics. This is useful for targeting devices by location, customer, or other metadata.",
        "filtering_by_attribute": "🔄 Filtering Things by attribute {}={}...",
        "filter_attribute_results": "📊 Filter Results: {} Things found with {}='{}'",
        "debug_full_error": "🔍 DEBUG: Full error response:",
        "debug_full_traceback": "🔍 DEBUG: Full traceback:",
        "api_error": "❌ API Error:",
        "error": "❌ Error:",
        "no_region_error": "❌ AWS region not configured",
        "region_setup_instructions": [
            "Please configure your AWS region using one of these methods:",
            "1. Set environment variable: export AWS_DEFAULT_REGION=us-east-1",
            "2. Configure AWS CLI: aws configure",
            "3. Set region in AWS credentials file",
        ],
        "aws_context_error": "⚠️ Could not retrieve AWS context:",
        "aws_credentials_reminder": "   Make sure AWS credentials are configured",
        "learning_moments": {
            "list_things": {
                "title": "List Things - Device Discovery",
                "content": "The list_things API retrieves all IoT devices (Things) in your account. This is essential for device inventory management, monitoring fleet size, and discovering devices by attributes. You can use pagination and filtering to handle device fleets efficiently.",
                "next": "We will call the list_things API with different options",
            },
            "list_certificates": {
                "title": "List Certificates - Security Inventory",
                "content": "X.509 certificates are the foundation of IoT device security. Each certificate uniquely identifies a device and enables secure communication with AWS IoT Core. This API helps you audit your security posture, track certificate lifecycle, and identify devices that need certificate rotation.",
                "next": "We will retrieve all certificates and examine their security properties",
            },
            "list_thing_groups": {
                "title": "List Thing Groups - Device Organization",
                "content": "Thing Groups provide hierarchical organization for your IoT devices, similar to folders for files. They enable bulk operations, policy inheritance, and logical grouping by location, function, or any business criteria. This is crucial for managing large-scale IoT deployments.",
                "next": "We will explore your Thing Groups and their organizational structure",
            },
            "list_thing_types": {
                "title": "List Thing Types - Device Templates",
                "content": "Thing Types are templates that define categories of IoT devices. They act as blueprints specifying common attributes and behaviors for similar devices. For example, a 'SedanVehicle' type might define attributes like engine type and seating capacity. Thing Types help organize your device fleet and enable standardized device management.",
                "next": "We will examine your Thing Types and their attribute schemas",
            },
            "describe_thing": {
                "title": "Describe Thing - Device Details",
                "content": "The describe_thing API provides complete information about a specific IoT device, including its attributes, Thing Type, version, and unique identifiers. This is essential for device troubleshooting, configuration management, and understanding device relationships within your IoT architecture.",
                "next": "We will examine detailed information for a specific Thing",
            },
            "describe_thing_group": {
                "title": "Describe Thing Group - Group Management",
                "content": "Thing Group details reveal the organizational structure of your IoT fleet. You can see group properties, parent-child hierarchies, attached policies, and member devices. This information is vital for understanding access control, policy inheritance, and device organization strategies.",
                "next": "We will examine detailed properties of a specific Thing Group",
            },
            "describe_thing_type": {
                "title": "Describe Thing Type - Template Analysis",
                "content": "Thing Type details show the blueprint definition for device categories. You can examine searchable attributes, property constraints, and metadata that define how devices of this type should be structured. This helps ensure consistent device registration and enables efficient fleet queries.",
                "next": "We will analyze the schema and properties of a specific Thing Type",
            },
            "describe_endpoint": {
                "title": "Describe Endpoint - Connection Discovery",
                "content": "IoT endpoints are the gateway URLs that devices use to connect to AWS IoT Core. Different endpoint types serve different purposes: Data-ATS for device communication, CredentialProvider for authentication, and Jobs for device management. Understanding endpoints is crucial for device connectivity configuration.",
                "next": "We will discover the endpoint URL for device connections",
            },
        },
        "api_desc_list_things_paginated": "Page {} - Retrieves up to {} Things",
        "api_desc_list_things_by_type": "Retrieves Things filtered by Thing Type '{}'",
        "api_desc_list_things_by_attribute": "Retrieves Things filtered by attribute '{}={}'",
        "api_desc_list_things": "Retrieves a paginated list of all IoT Things in your AWS account",
        "api_desc_list_certificates": "Retrieves a list of X.509 certificates registered in your AWS IoT account",
        "api_desc_list_thing_groups": "Retrieves a list of Thing Groups used to organize and manage IoT devices",
        "api_desc_list_thing_types": "Retrieves a list of Thing Types that define device templates and attributes",
        "api_desc_describe_thing": "Retrieves detailed information about a specific IoT Thing",
        "api_desc_describe_thing_group": "Retrieves detailed information about a specific Thing Group",
        "api_desc_describe_thing_type": "Retrieves detailed information about a specific Thing Type",
        "api_desc_describe_endpoint": "Retrieves the IoT endpoint URL for your AWS account and region",
        "api_explain_list_things": "Shows device inventory with names, types, attributes, and creation dates",
        "api_explain_list_certificates": "Shows security certificates with IDs, ARNs, status, and expiration dates",
        "api_explain_list_thing_groups": "Shows device organization structure with group hierarchies and properties",
        "api_explain_list_thing_types": "Shows device templates with searchable attributes and property definitions",
        "api_explain_describe_thing": "Shows complete device profile including attributes, type, and version information",
        "api_explain_describe_thing_group": "Shows group configuration, parent/child relationships, and applied policies",
        "api_explain_describe_thing_type": "Shows template schema, searchable attributes, and property constraints",
        "api_explain_describe_endpoint": "Returns the HTTPS endpoint URL used for device communication and data operations",
        "api_call_label": "API Call",
        "http_request_label": "HTTP Request",
        "description_label": "Description",
        "input_parameters_label": "Input Parameters",
        "no_input_parameters": "None (this API requires no input parameters)",
        "response_explanation_label": "Response Explanation",
        "response_payload_label": "Response Payload",
        "thing_details": "📊 Thing Details:",
        "thing_group_details": "📊 Thing Group Details:",
        "thing_type_details": "📊 Thing Type Details:",
        "name_label": "Name",
        "type_label": "Type",
        "description_simple": "Description",
    },
    "es": {
        "title": "🚀 Explorador de API del Registro de AWS IoT",
        "separator": "=" * 40,
        "aws_config": "📍 Configuración de AWS:",
        "account_id": "ID de Cuenta",
        "region": "Región",
        "description": "Exploración interactiva de las APIs del Registro de AWS IoT con explicaciones detalladas.",
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Detalles completos de solicitud/respuesta de API",
            "• Información HTTP completa",
            "• Diagnósticos de error mejorados",
        ],
        "tip": "💡 Consejo: Usa la bandera --debug o -d para información detallada de API",
        "tip_features": [
            "• El modo condensado muestra solo métricas clave",
            "• El modo debug muestra detalles completos de API",
        ],
        "client_initialized": "✅ Cliente de AWS IoT inicializado exitosamente",
        "invalid_credentials": "❌ Credenciales de AWS inválidas",
        "learning_intro_title": "APIs del Registro de AWS IoT - Gestión de Dispositivos",
        "learning_intro_content": "El Registro de AWS IoT es la base de datos central que almacena información sobre tus dispositivos IoT (Things), su organización (Thing Groups), plantillas de dispositivos (Thing Types) y certificados de seguridad. Estas APIs te permiten gestionar programáticamente toda tu flota de dispositivos IoT. Entender estas operaciones es fundamental para construir soluciones IoT escalables.",
        "learning_intro_next": "Exploraremos 8 APIs centrales del Registro con explicaciones detalladas",
        "press_enter": "Presiona Enter para continuar...",
        "goodbye": "👋 ¡Adiós!",
        "operations_menu": "📋 Operaciones Disponibles:",
        "operations": [
            "1. Listar Things",
            "2. Listar Certificados",
            "3. Listar Thing Groups",
            "4. Listar Thing Types",
            "5. Describir Thing",
            "6. Describir Thing Group",
            "7. Describir Thing Type",
            "8. Describir Endpoint",
            "9. Salir",
        ],
        "select_operation": "Seleccionar operación (1-9):",
        "invalid_choice": "❌ Selección inválida. Por favor selecciona 1-9.",
        "list_things_options": "🔍 Opciones de Listar Things:",
        "list_things_menu": [
            "   1. Listar todos los Things (básico)",
            "   2. Listar Things con paginación",
            "   3. Filtrar Things por Thing Type",
            "   4. Filtrar Things por atributo",
        ],
        "select_option": "Seleccionar opción (1-4):",
        "max_results_prompt": "Ingresa máximo de resultados por página (predeterminado 5):",
        "thing_type_prompt": "Ingresa nombre del Thing Type (ej., SedanVehicle):",
        "attribute_name_prompt": "Ingresa nombre del atributo (ej., country):",
        "attribute_value_prompt": "Ingresa valor del atributo (ej., US):",
        "no_thing_type": "❌ No se especificó Thing Type",
        "attribute_required": "❌ Se requieren nombre y valor del atributo",
        "executing": "🔄 Ejecutando:",
        "completed": "completado",
        "found_things": "📊 Encontrados {} Things",
        "thing_names": "   Nombres de Things:",
        "found_certificates": "📊 Encontrados {} Certificados",
        "certificate_ids": "   IDs de Certificados:",
        "found_thing_groups": "📊 Encontrados {} Thing Groups",
        "group_names": "   Nombres de Grupos:",
        "found_thing_types": "📊 Encontrados {} Thing Types",
        "type_names": "   Nombres de Tipos:",
        "return_to_menu": "Presiona Enter para volver al menú...",
        "available_things": "📋 Things Disponibles",
        "available_groups": "📋 Thing Groups Disponibles",
        "available_types": "📋 Thing Types Disponibles",
        "enter_thing_name": "Ingresa nombre del Thing: ",
        "enter_group_selection": "Ingresa número o nombre del Thing Group: ",
        "enter_type_selection": "Ingresa número o nombre del Thing Type: ",
        "no_things_found": "⚠️ No se encontraron Things en tu cuenta",
        "no_groups_found": "⚠️ No se encontraron Thing Groups en tu cuenta",
        "no_types_found": "⚠️ No se encontraron Thing Types en tu cuenta",
        "could_not_list_things": "⚠️ No se pudieron listar los Things:",
        "could_not_list_groups": "⚠️ No se pudieron listar los Thing Groups:",
        "could_not_list_types": "⚠️ No se pudieron listar los Thing Types:",
        "invalid_selection": "❌ Selección inválida. Por favor elige",
        "endpoint_type_prompt": "Ingresa tipo de endpoint (iot:Data-ATS, iot:CredentialProvider, iot:Jobs) [predeterminado: iot:Data-ATS]: ",
        "pagination_learning_title": "📚 LEARNING MOMENT: Paginación",
        "pagination_learning_content": "La paginación te permite recuperar grandes conjuntos de datos en fragmentos más pequeños. Esto es esencial cuando gestionas cientos o miles de dispositivos para evitar timeouts y problemas de memoria.",
        "pagination_listing": "🔄 Listando Things con paginación (máximo {} por página)...",
        "page_summary": "📊 Página {} Resumen: {} Things recuperados",
        "continue_next_page": "¿Continuar a la siguiente página? (s/N): ",
        "pagination_complete": "🏁 Paginación Completa: {} Things totales encontrados en {} página(s)",
        "filter_by_type_learning_title": "📚 LEARNING MOMENT: Filtrar por Thing Type",
        "filter_by_type_learning_content": "El filtrado te permite encontrar categorías específicas de dispositivos. Los Thing Types actúan como plantillas que agrupan dispositivos similares.",
        "filtering_by_type": "🔄 Filtrando Things por Thing Type: {}...",
        "filter_type_results": "📊 Resultados del Filtro: {} Things encontrados con Thing Type '{}'",
        "filter_by_attribute_learning_title": "📚 LEARNING MOMENT: Filtrar por Atributos",
        "filter_by_attribute_learning_content": "El filtrado por atributos te ayuda a encontrar dispositivos con características específicas. Esto es útil para dirigirse a dispositivos por ubicación, cliente u otros metadatos.",
        "filtering_by_attribute": "🔄 Filtrando Things por atributo {}={}...",
        "filter_attribute_results": "📊 Resultados del Filtro: {} Things encontrados con {}='{}'",
        "debug_full_error": "🔍 DEBUG: Respuesta completa de error:",
        "debug_full_traceback": "🔍 DEBUG: Traza completa:",
        "api_error": "❌ Error de API:",
        "error": "❌ Error:",
        "no_region_error": "❌ Región de AWS no configurada",
        "region_setup_instructions": [
            "Por favor configura tu región de AWS usando uno de estos métodos:",
            "1. Variable de entorno: export AWS_DEFAULT_REGION=us-east-1",
            "2. Configurar AWS CLI: aws configure",
            "3. Establecer región en el archivo de credenciales de AWS",
        ],
        "aws_context_error": "⚠️ No se pudo recuperar el contexto de AWS:",
        "aws_credentials_reminder": "   Asegúrate de que las credenciales de AWS estén configuradas",
        "learning_moments": {
            "list_things": {
                "title": "Listar Things - Descubrimiento de Dispositivos",
                "content": "La API list_things recupera todos los dispositivos IoT (Things) en tu cuenta. Esto es esencial para la gestión de inventario de dispositivos, monitorear el tamaño de la flota y descubrir dispositivos por atributos. Puedes usar paginación y filtrado para manejar flotas de dispositivos eficientemente.",
                "next": "Llamaremos a la API list_things con diferentes opciones",
            },
            "list_certificates": {
                "title": "Listar Certificados - Inventario de Seguridad",
                "content": "Los certificados X.509 son la base de la seguridad de dispositivos IoT. Cada certificado identifica únicamente un dispositivo y permite comunicación segura con AWS IoT Core. Esta API te ayuda a auditar tu postura de seguridad, rastrear el ciclo de vida de certificados e identificar dispositivos que necesitan rotación de certificados.",
                "next": "Recuperaremos todos los certificados y examinaremos sus propiedades de seguridad",
            },
            "list_thing_groups": {
                "title": "Listar Thing Groups - Organización de Dispositivos",
                "content": "Los Thing Groups proporcionan organización jerárquica para tus dispositivos IoT, similar a carpetas para archivos. Permiten operaciones masivas, herencia de políticas y agrupación lógica por ubicación, función o cualquier criterio de negocio. Esto es crucial para gestionar despliegues IoT a gran escala.",
                "next": "Exploraremos tus Thing Groups y su estructura organizacional",
            },
            "list_thing_types": {
                "title": "Listar Thing Types - Plantillas de Dispositivos",
                "content": "Los Thing Types son plantillas que definen categorías de dispositivos IoT. Actúan como planos que especifican atributos y comportamientos comunes para dispositivos similares. Por ejemplo, un tipo 'SedanVehicle' podría definir atributos como tipo de motor y capacidad de asientos. Los Thing Types ayudan a organizar tu flota de dispositivos y permiten gestión estandarizada de dispositivos.",
                "next": "Examinaremos tus Thing Types y sus esquemas de atributos",
            },
            "describe_thing": {
                "title": "Describir Thing - Detalles del Dispositivo",
                "content": "La API describe_thing proporciona información completa sobre un dispositivo IoT específico, incluyendo sus atributos, Thing Type, versión e identificadores únicos. Esto es esencial para solución de problemas de dispositivos, gestión de configuración y entender las relaciones de dispositivos dentro de tu arquitectura IoT.",
                "next": "Examinaremos información detallada para un Thing específico",
            },
            "describe_thing_group": {
                "title": "Describir Thing Group - Gestión de Grupos",
                "content": "Los detalles del Thing Group revelan la estructura organizacional de tu flota IoT. Puedes ver propiedades del grupo, jerarquías padre-hijo, políticas adjuntas y dispositivos miembros. Esta información es vital para entender el control de acceso, herencia de políticas y estrategias de organización de dispositivos.",
                "next": "Examinaremos propiedades detalladas de un Thing Group específico",
            },
            "describe_thing_type": {
                "title": "Describir Thing Type - Análisis de Plantillas",
                "content": "Los detalles del Thing Type muestran la definición del plano para categorías de dispositivos. Puedes examinar atributos buscables, restricciones de propiedades y metadatos que definen cómo deben estructurarse los dispositivos de este tipo. Esto ayuda a asegurar registro consistente de dispositivos y permite consultas eficientes de flota.",
                "next": "Analizaremos el esquema y propiedades de un Thing Type específico",
            },
            "describe_endpoint": {
                "title": "Describir Endpoint - Descubrimiento de Conexión",
                "content": "Los endpoints IoT son las URLs de puerta de enlace que los dispositivos usan para conectarse a AWS IoT Core. Diferentes tipos de endpoint sirven diferentes propósitos: Data-ATS para comunicación de dispositivos, CredentialProvider para autenticación y Jobs para gestión de dispositivos. Entender los endpoints es crucial para la configuración de conectividad de dispositivos.",
                "next": "Descubriremos la URL del endpoint para conexiones de dispositivos",
            },
        },
        "api_desc_list_things_paginated": "Página {} - Obtiene hasta {} Things",
        "api_desc_list_things_by_type": "Obtiene Things filtrados por Thing Type '{}'",
        "api_desc_list_things_by_attribute": "Obtiene Things filtrados por atributo '{}={}'",
        "api_desc_list_things": "Obtiene una lista paginada de todos los Things IoT en tu cuenta de AWS",
        "api_desc_list_certificates": "Obtiene una lista de certificados X.509 registrados en tu cuenta de AWS IoT",
        "api_desc_list_thing_groups": "Obtiene una lista de Thing Groups usados para organizar y gestionar dispositivos IoT",
        "api_desc_list_thing_types": "Obtiene una lista de Thing Types que definen plantillas y atributos de dispositivos",
        "api_desc_describe_thing": "Obtiene información detallada sobre un Thing IoT específico",
        "api_desc_describe_thing_group": "Obtiene información detallada sobre un Thing Group específico",
        "api_desc_describe_thing_type": "Obtiene información detallada sobre un Thing Type específico",
        "api_desc_describe_endpoint": "Obtiene la URL del endpoint IoT para tu cuenta y región de AWS",
        "api_explain_list_things": "Muestra inventario de dispositivos con nombres, tipos, atributos y fechas de creación",
        "api_explain_list_certificates": "Muestra certificados de seguridad con IDs, ARNs, estado y fechas de expiración",
        "api_explain_list_thing_groups": "Muestra estructura de organización de dispositivos con jerarquías de grupos y propiedades",
        "api_explain_list_thing_types": "Muestra plantillas de dispositivos con atributos buscables y definiciones de propiedades",
        "api_explain_describe_thing": "Muestra perfil completo del dispositivo incluyendo atributos, tipo e información de versión",
        "api_explain_describe_thing_group": "Muestra configuración del grupo, relaciones padre/hijo y políticas aplicadas",
        "api_explain_describe_thing_type": "Muestra esquema de plantilla, atributos buscables y restricciones de propiedades",
        "api_explain_describe_endpoint": "Devuelve la URL del endpoint HTTPS usada para comunicación de dispositivos y operaciones de datos",
        "api_call_label": "Llamada API",
        "http_request_label": "Solicitud HTTP",
        "description_label": "Descripción",
        "input_parameters_label": "Parámetros de Entrada",
        "no_input_parameters": "Ninguno (esta API no requiere parámetros de entrada)",
        "response_explanation_label": "Explicación de Respuesta",
        "response_payload_label": "Carga de Respuesta",
        "thing_details": "📊 Detalles del Thing:",
        "thing_group_details": "📊 Detalles del Thing Group:",
        "thing_type_details": "📊 Detalles del Thing Type:",
        "name_label": "Nombre",
        "type_label": "Tipo",
        "description_simple": "Descripción",
    },
    "ja": {
        "title": "🚀 AWS IoT Registry API エクスプローラー",
        "separator": "=" * 40,
        "aws_config": "📍 AWS設定:",
        "account_id": "アカウントID",
        "region": "リージョン",
        "description": "詳細な説明付きのAWS IoT Registry APIのインタラクティブ探索。",
        "debug_enabled": "🔍 デバッグモード有効",
        "debug_features": ["• 完全なAPIリクエスト/レスポンス詳細", "• 完全なHTTP情報", "• 拡張エラー診断"],
        "tip": "💡 ヒント: 詳細なAPI情報には--debugまたは-dフラグを使用",
        "tip_features": ["• 簡潔モードは主要メトリクスのみ表示", "• デバッグモードは完全なAPI詳細を表示"],
        "client_initialized": "✅ AWS IoTクライアントが正常に初期化されました",
        "invalid_credentials": "❌ 無効なAWS認証情報",
        "learning_intro_title": "AWS IoT Registry APIs - デバイス管理",
        "learning_intro_content": "AWS IoT Registryは、IoTデバイス（Things）、その組織（Thing Groups）、デバイステンプレート（Thing Types）、セキュリティ証明書に関する情報を格納する中央データベースです。これらのAPIにより、IoTデバイスフリート全体をプログラムで管理できます。これらの操作を理解することは、スケーラブルなIoTソリューションを構築するための基本です。",
        "learning_intro_next": "詳細な説明付きで8つのコアRegistry APIを探索します",
        "press_enter": "Enterキーを押して続行...",
        "goodbye": "👋 さようなら！",
        "operations_menu": "📋 利用可能な操作:",
        "operations": [
            "1. Thingsをリスト",
            "2. 証明書をリスト",
            "3. Thing Groupsをリスト",
            "4. Thing Typesをリスト",
            "5. Thingを詳細表示",
            "6. Thing Groupを詳細表示",
            "7. Thing Typeを詳細表示",
            "8. エンドポイントを詳細表示",
            "9. 終了",
        ],
        "select_operation": "操作を選択 (1-9):",
        "invalid_choice": "❌ 無効な選択です。1-9を選択してください。",
        "list_things_options": "🔍 List Things オプション:",
        "list_things_menu": [
            "   1. すべてのThingsをリスト（基本）",
            "   2. ページネーション付きでThingsをリスト",
            "   3. Thing TypeでThingsをフィルタ",
            "   4. 属性でThingsをフィルタ",
        ],
        "select_option": "オプションを選択 (1-4):",
        "max_results_prompt": "ページあたりの最大結果数を入力（デフォルト5）:",
        "thing_type_prompt": "Thing Type名を入力（例: SedanVehicle）:",
        "attribute_name_prompt": "属性名を入力（例: country）:",
        "attribute_value_prompt": "属性値を入力（例: US）:",
        "no_thing_type": "❌ Thing Typeが指定されていません",
        "attribute_required": "❌ 属性名と値が必要です",
        "executing": "🔄 実行中:",
        "completed": "完了",
        "found_things": "📊 {}個のThingsが見つかりました",
        "thing_names": "   Thing名:",
        "found_certificates": "📊 {}個の証明書が見つかりました",
        "certificate_ids": "   証明書ID:",
        "found_thing_groups": "📊 {}個のThing Groupsが見つかりました",
        "group_names": "   グループ名:",
        "found_thing_types": "📊 {}個のThing Typesが見つかりました",
        "type_names": "   タイプ名:",
        "return_to_menu": "Enterキーを押してメニューに戻る...",
        "available_things": "📋 利用可能なThings",
        "available_groups": "📋 利用可能なThing Groups",
        "available_types": "📋 利用可能なThing Types",
        "enter_thing_name": "Thing名を入力: ",
        "enter_group_selection": "番号またはThing Group名を入力: ",
        "enter_type_selection": "番号またはThing Type名を入力: ",
        "no_things_found": "⚠️ アカウントにThingsが見つかりません",
        "no_groups_found": "⚠️ アカウントにThing Groupsが見つかりません",
        "no_types_found": "⚠️ アカウントにThing Typesが見つかりません",
        "could_not_list_things": "⚠️ Thingsをリストできませんでした:",
        "could_not_list_groups": "⚠️ Thing Groupsをリストできませんでした:",
        "could_not_list_types": "⚠️ Thing Typesをリストできませんでした:",
        "invalid_selection": "❌ 無効な選択です。選択してください",
        "endpoint_type_prompt": "エンドポイントタイプを入力（iot:Data-ATS, iot:CredentialProvider, iot:Jobs）[デフォルト: iot:Data-ATS]: ",
        "pagination_learning_title": "📚 学習ポイント: ページネーション",
        "pagination_learning_content": "ページネーションにより、大きなデータセットを小さなチャンクで取得できます。これは、タイムアウトやメモリ問題を回避するために、数百または数千のデバイスを管理する際に不可欠です。",
        "pagination_listing": "🔄 ページネーション付きでThingsをリスト中（ページあたり最大{}）...",
        "page_summary": "📊 ページ{}概要: {}個のThingsを取得",
        "continue_next_page": "次のページに続行しますか？ (y/N): ",
        "pagination_complete": "🏁 ページネーション完了: {}ページにわたって合計{}個のThingsが見つかりました",
        "filter_by_type_learning_title": "📚 学習ポイント: Thing Typeによるフィルタリング",
        "filter_by_type_learning_content": "フィルタリングにより、特定のカテゴリのデバイスを見つけることができます。Thing Typesは類似のデバイスをグループ化するテンプレートとして機能します。",
        "filtering_by_type": "🔄 Thing Type: {}でThingsをフィルタリング中...",
        "filter_type_results": "📊 フィルタ結果: Thing Type '{}'で{}個のThingsが見つかりました",
        "filter_by_attribute_learning_title": "📚 学習ポイント: 属性によるフィルタリング",
        "filter_by_attribute_learning_content": "属性フィルタリングは、特定の特性を持つデバイスを見つけるのに役立ちます。これは、場所、顧客、またはその他のメタデータによってデバイスをターゲットにするのに便利です。",
        "filtering_by_attribute": "🔄 属性{}={}でThingsをフィルタリング中...",
        "filter_attribute_results": "📊 フィルタ結果: {}='{}'で{}個のThingsが見つかりました",
        "debug_full_error": "🔍 デバッグ: 完全なエラーレスポンス:",
        "debug_full_traceback": "🔍 デバッグ: 完全なトレースバック:",
        "api_error": "❌ APIエラー:",
        "error": "❌ エラー:",
        "no_region_error": "❌ AWSリージョンが設定されていません",
        "region_setup_instructions": [
            "以下のいずれかの方法でAWSリージョンを設定してください:",
            "1. 環境変数を設定: export AWS_DEFAULT_REGION=us-east-1",
            "2. AWS CLIを設定: aws configure",
            "3. AWS認証情報ファイルでリージョンを設定",
        ],
        "aws_context_error": "⚠️ AWSコンテキストを取得できませんでした:",
        "aws_credentials_reminder": "   AWS認証情報が設定されていることを確認してください",
        "learning_moments": {
            "list_things": {
                "title": "List Things - デバイス発見",
                "content": "list_things APIは、アカウント内のすべてのIoTデバイス（Things）を取得します。これは、デバイスインベントリ管理、フリートサイズの監視、属性によるデバイス発見に不可欠です。ページネーションとフィルタリングを使用して、デバイスフリートを効率的に処理できます。",
                "next": "異なるオプションでlist_things APIを呼び出します",
            },
            "list_certificates": {
                "title": "List Certificates - セキュリティインベントリ",
                "content": "X.509証明書はIoTデバイスセキュリティの基盤です。各証明書はデバイスを一意に識別し、AWS IoT Coreとの安全な通信を可能にします。このAPIは、セキュリティ態勢の監査、証明書ライフサイクルの追跡、証明書ローテーションが必要なデバイスの特定に役立ちます。",
                "next": "すべての証明書を取得し、そのセキュリティプロパティを調査します",
            },
            "list_thing_groups": {
                "title": "List Thing Groups - デバイス組織",
                "content": "Thing Groupsは、ファイル用のフォルダと同様に、IoTデバイスの階層組織を提供します。一括操作、ポリシー継承、場所、機能、またはビジネス基準による論理グループ化を可能にします。これは、大規模なIoTデプロイメントの管理に重要です。",
                "next": "Thing Groupsとその組織構造を探索します",
            },
            "list_thing_types": {
                "title": "List Thing Types - デバイステンプレート",
                "content": "Thing TypesはIoTデバイスのカテゴリを定義するテンプレートです。類似のデバイスの共通属性と動作を指定するブループリントとして機能します。例えば、'SedanVehicle'タイプは、エンジンタイプや座席数などの属性を定義する場合があります。Thing Typesは、デバイスフリートの整理と標準化されたデバイス管理を可能にします。",
                "next": "Thing Typesとその属性スキーマを調査します",
            },
            "describe_thing": {
                "title": "Describe Thing - 詳細なデバイス情報",
                "content": "describe_thing APIは、特定のIoTデバイスの完全な詳細を提供します。これには、属性、Thing Type、Thing Group メンバーシップ、バージョン情報が含まれます。これは、デバイスのトラブルシューティング、設定の確認、デバイス固有の操作の実行に不可欠です。",
                "next": "特定のThingの詳細情報を取得します",
            },
            "describe_thing_group": {
                "title": "Describe Thing Group - グループ詳細",
                "content": "Thing Groupsは、デバイスの組織構造を提供します。このAPIは、グループのプロパティ、親子関係、メンバーデバイス、適用されるポリシーを表示します。これは、グループベースの操作とポリシー管理を理解するために重要です。",
                "next": "Thing Groupの詳細な構造を調査します",
            },
            "describe_thing_type": {
                "title": "Describe Thing Type - タイプ仕様",
                "content": "Thing Typesは、デバイスカテゴリのテンプレートとして機能します。このAPIは、タイプの属性スキーマ、説明、作成日を表示します。これは、デバイス標準化とタイプベースの操作を理解するために重要です。",
                "next": "Thing Typeの詳細な仕様を調査します",
            },
            "describe_endpoint": {
                "title": "Describe Endpoint - 接続情報",
                "content": "IoTエンドポイントは、デバイスがAWS IoT Coreに接続するためのURLです。このAPIは、MQTT、HTTPS、WebSocketsなどの異なるプロトコルのエンドポイントを提供します。これは、デバイス接続の設定とトラブルシューティングに不可欠です。",
                "next": "利用可能なIoTエンドポイントを取得します",
            },
        },
        "api_call_label": "API呼び出し",
        "http_request_label": "HTTPリクエスト",
        "description_label": "説明",
        "input_parameters_label": "入力パラメータ",
        "no_input_parameters": "なし（このAPIは入力パラメータを必要としません）",
        "response_explanation_label": "レスポンス説明",
        "response_payload_label": "レスポンスペイロード",
        "thing_details": "📊 Thing詳細:",
        "thing_group_details": "📊 Thing Group詳細:",
        "thing_type_details": "📊 Thing Type詳細:",
        "name_label": "名前",
        "type_label": "タイプ",
        "description_simple": "説明",
    },
    "zh-CN": {
        "title": "🚀 AWS IoT Registry API 探索器",
        "separator": "=" * 40,
        "aws_config": "📍 AWS 配置:",
        "account_id": "账户 ID",
        "region": "区域",
        "description": "通过详细说明交互式探索 AWS IoT Registry API。",
        "debug_enabled": "🔍 调试模式已启用",
        "debug_features": ["• 完整的 API 请求/响应详细信息", "• 完整的 HTTP 信息", "• 增强的错误诊断"],
        "tip": "💡 提示: 使用 --debug 或 -d 标志获取详细的 API 信息",
        "tip_features": ["• 精简模式仅显示关键指标", "• 调试模式显示完整的 API 详细信息"],
        "client_initialized": "✅ AWS IoT 客户端初始化成功",
        "invalid_credentials": "❌ 无效的 AWS 凭证",
        "learning_intro_title": "AWS IoT Registry API - 设备管理",
        "learning_intro_content": "AWS IoT Registry 是存储 IoT 设备（Things）、其组织（Thing Groups）、设备模板（Thing Types）和安全证书信息的中央数据库。这些 API 允许您以编程方式管理整个 IoT 设备车队。理解这些操作是构建可扩展 IoT 解决方案的基础。",
        "learning_intro_next": "我们将通过详细说明探索 8 个核心 Registry API",
        "press_enter": "按 Enter 继续...",
        "goodbye": "👋 再见！",
        "operations_menu": "📋 可用操作:",
        "operations": [
            "1. 列出 Things",
            "2. 列出证书",
            "3. 列出 Thing Groups",
            "4. 列出 Thing Types",
            "5. 描述 Thing",
            "6. 描述 Thing Group",
            "7. 描述 Thing Type",
            "8. 描述端点",
            "9. 退出",
        ],
        "select_operation": "选择操作 (1-9):",
        "invalid_choice": "❌ 无效选择。请选择 1-9。",
        "list_things_options": "🔍 List Things 选项:",
        "list_things_menu": [
            "   1. 列出所有 Things（基本）",
            "   2. 使用分页列出 Things",
            "   3. 按 Thing Type 过滤 Things",
            "   4. 按属性过滤 Things",
        ],
        "select_option": "选择选项 (1-4):",
        "max_results_prompt": "输入每页最大结果数（默认 5）:",
        "thing_type_prompt": "输入 Thing Type 名称（例如：SedanVehicle）:",
        "attribute_name_prompt": "输入属性名称（例如：country）:",
        "attribute_value_prompt": "输入属性值（例如：US）:",
        "no_thing_type": "❌ 未指定 Thing Type",
        "attribute_required": "❌ 需要属性名称和值",
        "executing": "🔄 执行中:",
        "completed": "已完成",
        "found_things": "📊 找到 {} 个 Things",
        "thing_names": "   Thing 名称:",
        "found_certificates": "📊 找到 {} 个证书",
        "certificate_ids": "   证书 ID:",
        "found_thing_groups": "📊 找到 {} 个 Thing Groups",
        "group_names": "   组名称:",
        "found_thing_types": "📊 找到 {} 个 Thing Types",
        "type_names": "   类型名称:",
        "return_to_menu": "按 Enter 返回菜单...",
        "available_things": "📋 可用的 Things",
        "available_groups": "📋 可用的 Thing Groups",
        "available_types": "📋 可用的 Thing Types",
        "enter_thing_name": "输入 Thing 名称: ",
        "enter_group_selection": "输入编号或 Thing Group 名称: ",
        "enter_type_selection": "输入编号或 Thing Type 名称: ",
        "no_things_found": "⚠️ 在您的账户中未找到 Things",
        "no_groups_found": "⚠️ 在您的账户中未找到 Thing Groups",
        "no_types_found": "⚠️ 在您的账户中未找到 Thing Types",
        "could_not_list_things": "⚠️ 无法列出 Things:",
        "could_not_list_groups": "⚠️ 无法列出 Thing Groups:",
        "could_not_list_types": "⚠️ 无法列出 Thing Types:",
        "invalid_selection": "❌ 无效选择。请选择",
        "endpoint_type_prompt": "输入端点类型（iot:Data-ATS, iot:CredentialProvider, iot:Jobs）[默认: iot:Data-ATS]: ",
        "pagination_learning_title": "📚 学习要点: 分页",
        "pagination_learning_content": "分页允许您以较小的块检索大型数据集。这在管理数百或数千个设备时至关重要，以避免超时和内存问题。",
        "pagination_listing": "🔄 使用分页列出 Things（每页最多 {}）...",
        "page_summary": "📊 第 {} 页摘要: 检索到 {} 个 Things",
        "continue_next_page": "继续到下一页？ (y/N): ",
        "pagination_complete": "🏁 分页完成: 在 {} 页中找到总共 {} 个 Things",
        "filter_by_type_learning_title": "📚 学习要点: 按 Thing Type 过滤",
        "filter_by_type_learning_content": "过滤允许您查找特定类别的设备。Thing Types 充当将相似设备分组在一起的模板。",
        "filtering_by_type": "🔄 按 Thing Type 过滤 Things: {}...",
        "filter_type_results": "📊 过滤结果: 找到 {} 个具有 Thing Type '{}' 的 Things",
        "filter_by_attribute_learning_title": "📚 学习要点: 按属性过滤",
        "filter_by_attribute_learning_content": "属性过滤帮助您查找具有特定特征的设备。这对于按位置、客户或其他元数据定位设备很有用。",
        "filtering_by_attribute": "🔄 按属性 {}={} 过滤 Things...",
        "filter_attribute_results": "📊 过滤结果: 找到 {} 个具有 {}='{}' 的 Things",
        "debug_full_error": "🔍 调试: 完整错误响应:",
        "debug_full_traceback": "🔍 调试: 完整堆栈跟踪:",
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
        "learning_moments": {
            "list_things": {
                "title": "List Things - 设备发现",
                "content": "list_things API 检索您账户中的所有 IoT 设备（Things）。这对于设备库存管理、监控车队规模和按属性发现设备至关重要。您可以使用分页和过滤来高效处理设备车队。",
                "next": "我们将使用不同选项调用 list_things API",
            },
            "list_certificates": {
                "title": "List Certificates - 安全库存",
                "content": "X.509 证书是 IoT 设备安全的基础。每个证书唯一标识一个设备并启用与 AWS IoT Core 的安全通信。此 API 帮助您审核安全态势、跟踪证书生命周期并识别需要证书轮换的设备。",
                "next": "我们将检索所有证书并检查其安全属性",
            },
            "list_thing_groups": {
                "title": "List Thing Groups - 设备组织",
                "content": "Thing Groups 为您的 IoT 设备提供分层组织，类似于文件的文件夹。它们支持批量操作、策略继承以及按位置、功能或任何业务标准进行逻辑分组。这对于管理大规模 IoT 部署至关重要。",
                "next": "我们将探索您的 Thing Groups 及其组织结构",
            },
            "list_thing_types": {
                "title": "List Thing Types - 设备模板",
                "content": "Thing Types 是定义 IoT 设备类别的模板。它们充当蓝图，指定相似设备的通用属性和行为。例如，'SedanVehicle' 类型可能定义引擎类型和座位容量等属性。Thing Types 帮助组织您的设备车队并启用标准化设备管理。",
                "next": "我们将检查您的 Thing Types 及其属性架构",
            },
            "describe_thing": {
                "title": "Describe Thing - 设备详细信息",
                "content": "describe_thing API 提供特定 IoT 设备的完整详细信息，包括其属性、Thing Type 关联和组成员身份。这对于设备故障排除、配置验证和理解设备关系至关重要。",
                "next": "我们将检查特定 Thing 的详细配置",
            },
            "describe_thing_group": {
                "title": "Describe Thing Group - 组详细信息",
                "content": "Thing Groups 可以有属性、策略和层次关系。此 API 显示组配置、成员设备和继承的策略。理解组结构对于有效的设备管理和策略应用至关重要。",
                "next": "我们将探索 Thing Group 配置和层次结构",
            },
            "describe_thing_type": {
                "title": "Describe Thing Type - 类型定义",
                "content": "Thing Types 定义设备类别的属性架构和描述。此 API 显示类型配置、属性定义和使用统计。这对于理解设备标准化和确保一致的设备配置很重要。",
                "next": "我们将检查 Thing Type 定义和属性",
            },
            "describe_endpoint": {
                "title": "Describe Endpoint - 连接信息",
                "content": "IoT 端点是设备用于连接到 AWS IoT Core 的网关 URL。不同的端点类型服务于不同的目的：Data-ATS 用于设备通信，CredentialProvider 用于身份验证，Jobs 用于设备管理。理解端点对于设备连接配置至关重要。",
                "next": "我们将发现设备连接的端点 URL",
            },
        },
        "api_desc_list_things_paginated": "第 {} 页 - 检索最多 {} 个 Things",
        "api_desc_list_things_basic": "检索所有 Things",
        "api_desc_list_things_filtered_type": "按 Thing Type 过滤的 Things",
        "api_desc_list_things_filtered_attribute": "按属性过滤的 Things",
        "api_desc_list_certificates_basic": "检索所有证书",
        "api_desc_list_certificates_filtered": "按状态过滤的证书",
        "api_desc_list_thing_groups_basic": "检索所有 Thing Groups",
        "api_desc_list_thing_groups_recursive": "递归检索 Thing Groups",
        "api_desc_list_thing_types_basic": "检索所有 Thing Types",
        "api_call_label": "API 调用",
        "http_method_label": "HTTP 方法",
        "endpoint_label": "端点",
        "parameters_label": "参数",
        "response_label": "响应",
        "learning_moment_label": "学习要点",
        "found_label": "找到",
        "things_label": "Things",
        "certificates_label": "证书",
        "thing_groups_label": "Thing Groups",
        "thing_types_label": "Thing Types",
        "name_label": "名称",
        "arn_label": "ARN",
        "id_label": "ID",
        "status_label": "状态",
        "creation_date_label": "创建日期",
        "attributes_label": "属性",
        "thing_type_label": "Thing Type",
        "version_label": "版本",
        "group_properties_label": "组属性",
        "parent_group_label": "父组",
        "root_to_parent_groups_label": "根到父组",
        "thing_type_properties_label": "Thing Type 属性",
        "thing_type_metadata_label": "Thing Type 元数据",
        "endpoint_type_label": "端点类型",
        "endpoint_address_label": "端点地址",
        "api_desc_list_things_by_type": "检索按 Thing Type '{}' 过滤的 Things",
        "api_desc_list_things_by_attribute": "检索按属性 '{}={}' 过滤的 Things",
        "api_desc_list_things": "检索 AWS 账户中所有 IoT Things 的分页列表",
        "api_desc_list_certificates": "检索在 AWS IoT 账户中注册的 X.509 证书列表",
        "api_desc_list_thing_groups": "检索用于组织和管理 IoT 设备的 Thing Groups 列表",
        "api_desc_list_thing_types": "检索定义设备模板和属性的 Thing Types 列表",
        "api_desc_describe_thing": "检索特定 IoT Thing 的详细信息",
        "api_desc_describe_thing_group": "检索特定 Thing Group 的详细信息",
        "api_desc_describe_thing_type": "检索特定 Thing Type 的详细信息",
        "api_desc_describe_endpoint": "检索 AWS 账户和区域的 IoT 端点 URL",
        "api_explain_list_things": "显示包含名称、类型、属性和创建日期的设备清单",
        "api_explain_list_certificates": "显示包含 ID、ARN、状态和到期日期的安全证书",
        "api_explain_list_thing_groups": "显示包含组层次结构和属性的设备组织结构",
        "api_explain_list_thing_types": "显示包含可搜索属性和属性定义的设备模板",
        "api_explain_describe_thing": "显示包含属性、类型和版本信息的完整设备配置文件",
        "api_explain_describe_thing_group": "显示组配置、父/子关系和应用的策略",
        "api_explain_describe_thing_type": "显示模板架构、可搜索属性和属性约束",
        "api_explain_describe_endpoint": "返回用于设备通信和数据操作的 HTTPS 端点 URL",
        "api_call_label": "API 调用",
        "http_request_label": "HTTP 请求",
        "description_label": "描述",
        "input_parameters_label": "输入参数",
        "no_input_parameters": "无（此 API 不需要输入参数）",
        "response_explanation_label": "响应说明",
        "response_payload_label": "响应负载",
        "thing_details": "📊 Thing 详细信息:",
        "thing_group_details": "📊 Thing Group 详细信息:",
        "thing_type_details": "📊 Thing Type 详细信息:",
        "name_label": "名称",
        "type_label": "类型",
        "description_simple": "描述",
    },
    "pt-BR": {
        "title": "🚀 Explorador de API do Registro AWS IoT",
        "separator": "=" * 40,
        "aws_config": "📍 Configuração AWS:",
        "account_id": "ID da Conta",
        "region": "Região",
        "description": "Exploração interativa das APIs do Registro AWS IoT com explicações detalhadas.",
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Detalhes completos de solicitação/resposta da API",
            "• Informações HTTP completas",
            "• Diagnósticos de erro aprimorados",
        ],
        "tip": "💡 Dica: Use a flag --debug ou -d para informações detalhadas da API",
        "tip_features": [
            "• Modo condensado mostra apenas métricas principais",
            "• Modo debug mostra detalhes completos da API",
        ],
        "client_initialized": "✅ Cliente AWS IoT inicializado com sucesso",
        "invalid_credentials": "❌ Credenciais AWS inválidas",
        "learning_intro_title": "APIs do Registro AWS IoT - Gerenciamento de Dispositivos",
        "learning_intro_content": "O Registro AWS IoT é o banco de dados central que armazena informações sobre seus dispositivos IoT (Things), sua organização (Thing Groups), modelos de dispositivos (Thing Types) e certificados de segurança. Essas APIs permitem gerenciar programaticamente toda sua frota de dispositivos IoT. Compreender essas operações é fundamental para construir soluções IoT escaláveis.",
        "learning_intro_next": "Exploraremos 8 APIs centrais do Registro com explicações detalhadas",
        "press_enter": "Pressione Enter para continuar...",
        "goodbye": "👋 Tchau!",
        "operations_menu": "📋 Operações Disponíveis:",
        "operations": [
            "1. Listar Things",
            "2. Listar Certificados",
            "3. Listar Thing Groups",
            "4. Listar Thing Types",
            "5. Descrever Thing",
            "6. Descrever Thing Group",
            "7. Descrever Thing Type",
            "8. Descrever Endpoint",
            "9. Sair",
        ],
        "select_operation": "Selecionar operação (1-9):",
        "invalid_choice": "❌ Escolha inválida. Por favor selecione 1-9.",
        "list_things_options": "🔍 Opções de Listar Things:",
        "list_things_menu": [
            "   1. Listar todos os Things (básico)",
            "   2. Listar Things com paginação",
            "   3. Filtrar Things por Thing Type",
            "   4. Filtrar Things por atributo",
        ],
        "select_option": "Selecionar opção (1-4):",
        "max_results_prompt": "Digite máximo de resultados por página (padrão 5):",
        "thing_type_prompt": "Digite nome do Thing Type (ex., SedanVehicle):",
        "attribute_name_prompt": "Digite nome do atributo (ex., country):",
        "attribute_value_prompt": "Digite valor do atributo (ex., US):",
        "no_thing_type": "❌ Nenhum Thing Type especificado",
        "attribute_required": "❌ Nome e valor do atributo são obrigatórios",
        "executing": "🔄 Executando:",
        "completed": "concluído",
        "found_things": "📋 Encontrados {} Things",
        "thing_names": "   Nomes dos Things:",
        "found_certificates": "📋 Encontrados {} Certificados",
        "certificate_ids": "   IDs dos Certificados:",
        "found_thing_groups": "📋 Encontrados {} Thing Groups",
        "group_names": "   Nomes dos Grupos:",
        "found_thing_types": "📋 Encontrados {} Thing Types",
        "type_names": "   Nomes dos Tipos:",
        "return_to_menu": "Pressione Enter para voltar ao menu...",
        "available_things": "📋 Things Disponíveis",
        "available_groups": "📋 Thing Groups Disponíveis",
        "available_types": "📋 Thing Types Disponíveis",
        "enter_thing_name": "Digite nome do Thing: ",
        "enter_group_selection": "Digite número ou nome do Thing Group: ",
        "enter_type_selection": "Digite número ou nome do Thing Type: ",
        "no_things_found": "⚠️ Não foram encontrados Things em sua conta",
        "no_groups_found": "⚠️ Não foram encontrados Thing Groups em sua conta",
        "no_types_found": "⚠️ Não foram encontrados Thing Types em sua conta",
        "could_not_list_things": "⚠️ Não foi possível listar os Things:",
        "could_not_list_groups": "⚠️ Não foi possível listar os Thing Groups:",
        "could_not_list_types": "⚠️ Não foi possível listar os Thing Types:",
        "invalid_selection": "❌ Seleção inválida. Por favor escolha",
        "endpoint_type_prompt": "Digite tipo de endpoint (iot:Data-ATS, iot:CredentialProvider, iot:Jobs) [padrão: iot:Data-ATS]: ",
        "pagination_learning_title": "📚 MOMENTO DE APRENDIZADO: Paginação",
        "pagination_learning_content": "A paginação permite recuperar grandes conjuntos de dados em pedaços menores. Isso é essencial ao gerenciar centenas ou milhares de dispositivos para evitar timeouts e problemas de memória.",
        "pagination_listing": "🔄 Listando Things com paginação (máximo {} por página)...",
        "page_summary": "📋 Página {} Resumo: {} Things recuperados",
        "continue_next_page": "Continuar para próxima página? (s/N): ",
        "pagination_complete": "🏁 Paginação Completa: {} Things totais encontrados em {} página(s)",
        "filter_by_type_learning_title": "📚 MOMENTO DE APRENDIZADO: Filtrar por Thing Type",
        "filter_by_type_learning_content": "A filtragem permite encontrar categorias específicas de dispositivos. Thing Types atuam como modelos que agrupam dispositivos similares.",
        "filtering_by_type": "🔄 Filtrando Things por Thing Type: {}...",
        "filter_type_results": "📋 Resultados do Filtro: {} Things encontrados com Thing Type '{}'",
        "filter_by_attribute_learning_title": "📚 MOMENTO DE APRENDIZADO: Filtrar por Atributos",
        "filter_by_attribute_learning_content": "A filtragem por atributos ajuda a encontrar dispositivos com características específicas. Isso é útil para direcionar dispositivos por localização, cliente ou outros metadados.",
        "filtering_by_attribute": "🔄 Filtrando Things por atributo {}={}...",
        "filter_attribute_results": "📋 Resultados do Filtro: {} Things encontrados com {}='{}'",
        "debug_full_error": "🔍 DEBUG: Resposta completa de erro:",
        "debug_full_traceback": "🔍 DEBUG: Rastreamento completo:",
        "api_error": "❌ Erro da API:",
        "error": "❌ Erro:",
        "no_region_error": "❌ Região AWS não configurada",
        "region_setup_instructions": [
            "Por favor configure sua região AWS usando um destes métodos:",
            "1. Definir variável de ambiente: export AWS_DEFAULT_REGION=us-east-1",
            "2. Configurar AWS CLI: aws configure",
            "3. Definir região no arquivo de credenciais AWS",
        ],
        "aws_context_error": "⚠️ Não foi possível recuperar o contexto AWS:",
        "aws_credentials_reminder": "   Certifique-se de que as credenciais AWS estão configuradas",
        "learning_moments": {
            "list_things": {
                "title": "List Things - Descoberta de Dispositivos",
                "content": "A API list_things recupera todos os dispositivos IoT (Things) em sua conta. Isso é essencial para gerenciamento de inventário de dispositivos, monitoramento do tamanho da frota e descoberta de dispositivos por atributos. Você pode usar paginação e filtragem para lidar com frotas de dispositivos de forma eficiente.",
                "next": "Chamaremos a API list_things com diferentes opções",
            },
            "list_certificates": {
                "title": "List Certificates - Inventário de Segurança",
                "content": "Certificados X.509 são a base da segurança de dispositivos IoT. Cada certificado identifica unicamente um dispositivo e permite comunicação segura com o AWS IoT Core. Esta API ajuda a auditar sua postura de segurança, rastrear o ciclo de vida dos certificados e identificar dispositivos que precisam de rotação de certificados.",
                "next": "Recuperaremos todos os certificados e examinaremos suas propriedades de segurança",
            },
            "list_thing_groups": {
                "title": "List Thing Groups - Organização de Dispositivos",
                "content": "Thing Groups fornecem organização hierárquica para seus dispositivos IoT, similar a pastas para arquivos. Eles permitem operações em lote, herança de políticas e agrupamento lógico por localização, função ou qualquer critério de negócio. Isso é crucial para gerenciar implantações IoT em larga escala.",
                "next": "Exploraremos seus Thing Groups e sua estrutura organizacional",
            },
            "list_thing_types": {
                "title": "List Thing Types - Modelos de Dispositivos",
                "content": "Thing Types são modelos que definem categorias de dispositivos IoT. Eles atuam como plantas que especificam atributos e comportamentos comuns para dispositivos similares. Por exemplo, um tipo 'SedanVehicle' pode definir atributos como tipo de motor e capacidade de assentos. Thing Types ajudam a organizar sua frota de dispositivos e permitem gerenciamento padronizado de dispositivos.",
                "next": "Examinaremos seus Thing Types e seus esquemas de atributos",
            },
            "describe_thing": {
                "title": "Describe Thing - Detalhes do Dispositivo",
                "content": "A API describe_thing fornece informações completas sobre um dispositivo IoT específico, incluindo seus atributos, Thing Type, versão e identificadores únicos. Isso é essencial para solução de problemas de dispositivos, gerenciamento de configuração e compreensão de relacionamentos de dispositivos dentro de sua arquitetura IoT.",
                "next": "Examinaremos informações detalhadas para um Thing específico",
            },
            "describe_thing_group": {
                "title": "Describe Thing Group - Gerenciamento de Grupos",
                "content": "Detalhes do Thing Group revelam a estrutura organizacional de sua frota IoT. Você pode ver propriedades do grupo, hierarquias pai-filho, políticas anexadas e dispositivos membros. Esta informação é vital para entender controle de acesso, herança de políticas e estratégias de organização de dispositivos.",
                "next": "Examinaremos propriedades detalhadas de um Thing Group específico",
            },
            "describe_thing_type": {
                "title": "Describe Thing Type - Análise de Modelos",
                "content": "Detalhes do Thing Type mostram a definição do modelo para categorias de dispositivos. Você pode examinar atributos pesquisáveis, restrições de propriedades e metadados que definem como dispositivos deste tipo devem ser estruturados. Isso ajuda a garantir registro consistente de dispositivos e permite consultas eficientes da frota.",
                "next": "Analisaremos o esquema e propriedades de um Thing Type específico",
            },
            "describe_endpoint": {
                "title": "Describe Endpoint - Descoberta de Conexão",
                "content": "Endpoints IoT são as URLs de gateway que os dispositivos usam para se conectar ao AWS IoT Core. Diferentes tipos de endpoint servem diferentes propósitos: Data-ATS para comunicação de dispositivos, CredentialProvider para autenticação e Jobs para gerenciamento de dispositivos. Compreender endpoints é crucial para configuração de conectividade de dispositivos.",
                "next": "Descobriremos a URL do endpoint para conexões de dispositivos",
            },
        },
        "api_desc_list_things_paginated": "Página {} - Recupera até {} Things",
        "api_desc_list_things_by_type": "Recupera Things filtrados por Thing Type '{}'",
        "api_desc_list_things_by_attribute": "Recupera Things filtrados por atributo '{}={}'",
        "api_desc_list_things": "Recupera uma lista paginada de todos os Things IoT em sua conta AWS",
        "api_desc_list_certificates": "Recupera uma lista de certificados X.509 registrados em sua conta AWS IoT",
        "api_desc_list_thing_groups": "Recupera uma lista de Thing Groups usados para organizar e gerenciar dispositivos IoT",
        "api_desc_list_thing_types": "Recupera uma lista de Thing Types que definem modelos e atributos de dispositivos",
        "api_desc_describe_thing": "Recupera informações detalhadas sobre um Thing IoT específico",
        "api_desc_describe_thing_group": "Recupera informações detalhadas sobre um Thing Group específico",
        "api_desc_describe_thing_type": "Recupera informações detalhadas sobre um Thing Type específico",
        "api_desc_describe_endpoint": "Recupera a URL do endpoint IoT para sua conta e região AWS",
        "api_explain_list_things": "Mostra inventário de dispositivos com nomes, tipos, atributos e datas de criação",
        "api_explain_list_certificates": "Mostra certificados de segurança com IDs, ARNs, status e datas de expiração",
        "api_explain_list_thing_groups": "Mostra estrutura de organização de dispositivos com hierarquias de grupos e propriedades",
        "api_explain_list_thing_types": "Mostra modelos de dispositivos com atributos pesquisáveis e definições de propriedades",
        "api_explain_describe_thing": "Mostra perfil completo do dispositivo incluindo atributos, tipo e informações de versão",
        "api_explain_describe_thing_group": "Mostra configuração do grupo, relacionamentos pai/filho e políticas aplicadas",
        "api_explain_describe_thing_type": "Mostra esquema do modelo, atributos pesquisáveis e restrições de propriedades",
        "api_explain_describe_endpoint": "Retorna a URL do endpoint HTTPS usada para comunicação de dispositivos e operações de dados",
        "api_call_label": "Chamada da API",
        "http_request_label": "Solicitação HTTP",
        "description_label": "Descrição",
        "input_parameters_label": "Parâmetros de Entrada",
        "no_input_parameters": "Nenhum (esta API não requer parâmetros de entrada)",
        "response_explanation_label": "Explicação da Resposta",
        "response_payload_label": "Payload da Resposta",
        "thing_details": "📋 Detalhes do Thing:",
        "thing_group_details": "📋 Detalhes do Thing Group:",
        "thing_type_details": "📋 Detalhes do Thing Type:",
        "name_label": "Nome",
        "type_label": "Tipo",
        "description_simple": "Descrição",
    },
    "ko": {
        "title": "🚀 AWS IoT 레지스트리 API 탐색기",
        "separator": "=" * 40,
        "aws_config": "📍 AWS 구성:",
        "account_id": "계정 ID",
        "region": "리전",
        "description": "상세한 설명과 함께 AWS IoT 레지스트리 API의 대화형 탐색.",
        "debug_enabled": "🔍 디버그 모드 활성화",
        "debug_features": [
            "• 전체 API 요청/응답 세부 정보",
            "• 완전한 HTTP 정보",
            "• 향상된 오류 진단",
        ],
        "tip": "💡 팁: 상세한 API 정보를 보려면 --debug 또는 -d 플래그를 사용하세요",
        "tip_features": ["• 축약 모드는 핵심 메트릭만 표시", "• 디버그 모드는 완전한 API 세부 정보를 표시"],
        "client_initialized": "✅ AWS IoT 클라이언트가 성공적으로 초기화되었습니다",
        "invalid_credentials": "❌ 유효하지 않은 AWS 자격 증명",
        "learning_intro_title": "AWS IoT 레지스트리 API - 디바이스 관리",
        "learning_intro_content": "AWS IoT 레지스트리는 IoT 디바이스(Things), 그 조직(Thing Groups), 디바이스 템플릿(Thing Types) 및 보안 인증서에 대한 정보를 저장하는 중앙 데이터베이스입니다. 이러한 API를 통해 전체 IoT 디바이스 플릿을 프로그래밍 방식으로 관리할 수 있습니다. 이러한 작업을 이해하는 것은 확장 가능한 IoT 솔루션을 구축하는 데 기본적입니다.",
        "learning_intro_next": "상세한 설명과 함께 8개의 핵심 레지스트리 API를 탐색하겠습니다",
        "press_enter": "계속하려면 Enter를 누르세요...",
        "goodbye": "👋 안녕히 가세요!",
        "operations_menu": "📋 사용 가능한 작업:",
        "operations": [
            "1. Things 목록",
            "2. 인증서 목록",
            "3. Thing Groups 목록",
            "4. Thing Types 목록",
            "5. Thing 설명",
            "6. Thing Group 설명",
            "7. Thing Type 설명",
            "8. 엔드포인트 설명",
            "9. 종료",
        ],
        "select_operation": "작업 선택 (1-9):",
        "invalid_choice": "❌ 잘못된 선택입니다. 1-9를 선택해주세요.",
        "list_things_options": "🔍 Things 목록 옵션:",
        "list_things_menu": [
            "   1. 모든 Things 목록 (기본)",
            "   2. 페이지네이션으로 Things 목록",
            "   3. Thing Type으로 Things 필터링",
            "   4. 속성으로 Things 필터링",
        ],
        "select_option": "옵션 선택 (1-4):",
        "max_results_prompt": "페이지당 최대 결과 수 입력 (기본값 5):",
        "thing_type_prompt": "Thing Type 이름 입력 (예: SedanVehicle):",
        "attribute_name_prompt": "속성 이름 입력 (예: country):",
        "attribute_value_prompt": "속성 값 입력 (예: US):",
        "no_thing_type": "❌ Thing Type이 지정되지 않았습니다",
        "attribute_required": "❌ 속성 이름과 값이 필요합니다",
        "executing": "🔄 실행 중:",
        "completed": "완료",
        "found_things": "📊 {} Things를 찾았습니다",
        "thing_names": "   Thing 이름:",
        "found_certificates": "📊 {} 인증서를 찾았습니다",
        "certificate_ids": "   인증서 ID:",
        "found_thing_groups": "📊 {} Thing Groups를 찾았습니다",
        "group_names": "   그룹 이름:",
        "found_thing_types": "📊 {} Thing Types를 찾았습니다",
        "type_names": "   타입 이름:",
        "return_to_menu": "메뉴로 돌아가려면 Enter를 누르세요...",
        "available_things": "📋 사용 가능한 Things",
        "available_groups": "📋 사용 가능한 Thing Groups",
        "available_types": "📋 사용 가능한 Thing Types",
        "enter_thing_name": "Thing 이름 입력: ",
        "enter_group_selection": "번호 또는 Thing Group 이름 입력: ",
        "enter_type_selection": "번호 또는 Thing Type 이름 입력: ",
        "no_things_found": "⚠️ 계정에서 Things를 찾을 수 없습니다",
        "no_groups_found": "⚠️ 계정에서 Thing Groups를 찾을 수 없습니다",
        "no_types_found": "⚠️ 계정에서 Thing Types를 찾을 수 없습니다",
        "could_not_list_things": "⚠️ Things를 나열할 수 없습니다:",
        "could_not_list_groups": "⚠️ Thing Groups를 나열할 수 없습니다:",
        "could_not_list_types": "⚠️ Thing Types를 나열할 수 없습니다:",
        "invalid_selection": "❌ 잘못된 선택입니다. 다음 중에서 선택하세요",
        "endpoint_type_prompt": "엔드포인트 타입 입력 (iot:Data-ATS, iot:CredentialProvider, iot:Jobs) [기본값: iot:Data-ATS]: ",
        "pagination_learning_title": "📚 학습 포인트: 페이지네이션",
        "pagination_learning_content": "페이지네이션을 사용하면 대용량 데이터셋을 작은 단위로 검색할 수 있습니다. 이는 수백 또는 수천 개의 디바이스를 관리할 때 타임아웃과 메모리 문제를 피하기 위해 필수적입니다.",
        "pagination_listing": "🔄 페이지네이션으로 Things 나열 중 (페이지당 최대 {}개)...",
        "page_summary": "📊 페이지 {} 요약: {} Things 검색됨",
        "continue_next_page": "다음 페이지로 계속하시겠습니까? (y/N): ",
        "pagination_complete": "🏁 페이지네이션 완료: {}개 페이지에서 총 {} Things를 찾았습니다",
        "filter_by_type_learning_title": "📚 학습 포인트: Thing Type으로 필터링",
        "filter_by_type_learning_content": "필터링을 사용하면 특정 카테고리의 디바이스를 찾을 수 있습니다. Thing Types는 비슷한 디바이스를 함께 그룹화하는 템플릿 역할을 합니다.",
        "filtering_by_type": "🔄 Thing Type으로 Things 필터링 중: {}...",
        "filter_type_results": "📊 필터 결과: Thing Type '{}'로 {} Things를 찾았습니다",
        "filter_by_attribute_learning_title": "📚 학습 포인트: 속성으로 필터링",
        "filter_by_attribute_learning_content": "속성 필터링은 특정 특성을 가진 디바이스를 찾는 데 도움이 됩니다. 이는 위치, 고객 또는 기타 메타데이터로 디바이스를 대상으로 지정하는 데 유용합니다.",
        "filtering_by_attribute": "🔄 속성 {}={}로 Things 필터링 중...",
        "filter_attribute_results": "📊 필터 결과: {}='{}'로 {} Things를 찾았습니다",
        "debug_full_error": "🔍 디버그: 전체 오류 응답:",
        "debug_full_traceback": "🔍 디버그: 전체 추적:",
        "api_error": "❌ API 오류:",
        "error": "❌ 오류:",
        "no_region_error": "❌ AWS 리전이 구성되지 않았습니다",
        "region_setup_instructions": [
            "다음 방법 중 하나를 사용하여 AWS 리전을 구성하세요:",
            "1. 환경 변수 설정: export AWS_DEFAULT_REGION=us-east-1",
            "2. AWS CLI 구성: aws configure",
            "3. AWS 자격 증명 파일에서 리전 설정",
        ],
        "aws_context_error": "⚠️ AWS 컨텍스트를 검색할 수 없습니다:",
        "aws_credentials_reminder": "   AWS 자격 증명이 구성되어 있는지 확인하세요",
        "learning_moments": {
            "list_things": {
                "title": "Things 목록 - 디바이스 발견",
                "content": "list_things API는 계정의 모든 IoT 디바이스(Things)를 검색합니다. 이는 디바이스 인벤토리 관리, 플릿 크기 모니터링 및 속성으로 디바이스 발견에 필수적입니다. 페이지네이션과 필터링을 사용하여 디바이스 플릿을 효율적으로 처리할 수 있습니다.",
                "next": "다양한 옵션으로 list_things API를 호출하겠습니다",
            },
            "list_certificates": {
                "title": "인증서 목록 - 보안 인벤토리",
                "content": "X.509 인증서는 IoT 디바이스 보안의 기초입니다. 각 인증서는 디바이스를 고유하게 식별하고 AWS IoT Core와의 보안 통신을 가능하게 합니다. 이 API는 보안 상태를 감사하고, 인증서 수명 주기를 추적하며, 인증서 교체가 필요한 디바이스를 식별하는 데 도움이 됩니다.",
                "next": "모든 인증서를 검색하고 보안 속성을 검토하겠습니다",
            },
            "list_thing_groups": {
                "title": "Thing Groups 목록 - 디바이스 조직",
                "content": "Thing Groups는 파일의 폴더와 유사하게 IoT 디바이스에 대한 계층적 조직을 제공합니다. 위치, 기능 또는 비즈니스 기준에 따른 대량 작업, 정책 상속 및 논리적 그룹화를 가능하게 합니다. 이는 대규모 IoT 배포를 관리하는 데 중요합니다.",
                "next": "Thing Groups와 그 조직 구조를 탐색하겠습니다",
            },
            "list_thing_types": {
                "title": "Thing Types 목록 - 디바이스 템플릿",
                "content": "Thing Types는 IoT 디바이스 카테고리를 정의하는 템플릿입니다. 비슷한 디바이스에 대한 공통 속성과 동작을 지정하는 청사진 역할을 합니다. 예를 들어, 'SedanVehicle' 타입은 엔진 타입과 좌석 수와 같은 속성을 정의할 수 있습니다. Thing Types는 디바이스 플릿을 조직하고 표준화된 디바이스 관리를 가능하게 합니다.",
                "next": "Thing Types와 그 속성 스키마를 검토하겠습니다",
            },
            "describe_thing": {
                "title": "Thing 설명 - 디바이스 세부 정보",
                "content": "describe_thing API는 속성, Thing Type, 버전 및 고유 식별자를 포함하여 특정 IoT 디바이스에 대한 완전한 정보를 제공합니다. 이는 디바이스 문제 해결, 구성 관리 및 IoT 아키텍처 내에서 디바이스 관계를 이해하는 데 필수적입니다.",
                "next": "특정 Thing에 대한 상세 정보를 검토하겠습니다",
            },
            "describe_thing_group": {
                "title": "Thing Group 설명 - 그룹 관리",
                "content": "Thing Group 세부 정보는 IoT 플릿의 조직 구조를 보여줍니다. 그룹 속성, 부모-자식 계층, 첨부된 정책 및 멤버 디바이스를 볼 수 있습니다. 이 정보는 액세스 제어, 정책 상속 및 디바이스 조직 전략을 이해하는 데 중요합니다.",
                "next": "특정 Thing Group의 상세한 속성을 검토하겠습니다",
            },
            "describe_thing_type": {
                "title": "Thing Type 설명 - 템플릿 분석",
                "content": "Thing Type 세부 정보는 디바이스 카테고리에 대한 청사진 정의를 보여줍니다. 검색 가능한 속성, 속성 제약 조건 및 이 타입의 디바이스가 어떻게 구조화되어야 하는지를 정의하는 메타데이터를 검토할 수 있습니다. 이는 일관된 디바이스 등록을 보장하고 효율적인 플릿 쿼리를 가능하게 하는 데 도움이 됩니다.",
                "next": "특정 Thing Type의 스키마와 속성을 분석하겠습니다",
            },
            "describe_endpoint": {
                "title": "엔드포인트 설명 - 연결 발견",
                "content": "IoT 엔드포인트는 디바이스가 AWS IoT Core에 연결하는 데 사용하는 게이트웨이 URL입니다. 다른 엔드포인트 타입은 다른 목적을 제공합니다: 디바이스 통신용 Data-ATS, 인증용 CredentialProvider, 디바이스 관리용 Jobs. 엔드포인트를 이해하는 것은 디바이스 연결 구성에 중요합니다.",
                "next": "디바이스 연결을 위한 엔드포인트 URL을 발견하겠습니다",
            },
        },
        "api_desc_list_things_paginated": "페이지 {} - 최대 {} Things 검색",
        "api_desc_list_things_by_type": "Thing Type '{}'로 필터링된 Things 검색",
        "api_desc_list_things_by_attribute": "속성 '{}={}'로 필터링된 Things 검색",
        "api_desc_list_things": "AWS 계정의 모든 IoT Things의 페이지네이션된 목록 검색",
        "api_desc_list_certificates": "AWS IoT 계정에 등록된 X.509 인증서 목록 검색",
        "api_desc_list_thing_groups": "IoT 디바이스를 조직하고 관리하는 데 사용되는 Thing Groups 목록 검색",
        "api_desc_list_thing_types": "디바이스 템플릿과 속성을 정의하는 Thing Types 목록 검색",
        "api_desc_describe_thing": "특정 IoT Thing에 대한 상세 정보 검색",
        "api_desc_describe_thing_group": "특정 Thing Group에 대한 상세 정보 검색",
        "api_desc_describe_thing_type": "특정 Thing Type에 대한 상세 정보 검색",
        "api_desc_describe_endpoint": "AWS 계정과 리전에 대한 IoT 엔드포인트 URL 검색",
        "api_explain_list_things": "이름, 타입, 속성 및 생성 날짜가 포함된 디바이스 인벤토리 표시",
        "api_explain_list_certificates": "ID, ARN, 상태 및 만료 날짜가 포함된 보안 인증서 표시",
        "api_explain_list_thing_groups": "그룹 계층과 속성이 포함된 디바이스 조직 구조 표시",
        "api_explain_list_thing_types": "검색 가능한 속성과 속성 정의가 포함된 디바이스 템플릿 표시",
        "api_explain_describe_thing": "속성, 타입 및 버전 정보를 포함한 완전한 디바이스 프로필 표시",
        "api_explain_describe_thing_group": "그룹 구성, 부모/자식 관계 및 적용된 정책 표시",
        "api_explain_describe_thing_type": "템플릿 스키마, 검색 가능한 속성 및 속성 제약 조건 표시",
        "api_explain_describe_endpoint": "디바이스 통신 및 데이터 작업에 사용되는 HTTPS 엔드포인트 URL 반환",
        "api_call_label": "API 호출",
        "http_request_label": "HTTP 요청",
        "description_label": "설명",
        "input_parameters_label": "입력 매개변수",
        "no_input_parameters": "없음 (이 API는 입력 매개변수가 필요하지 않습니다)",
        "response_explanation_label": "응답 설명",
        "response_payload_label": "응답 페이로드",
        "thing_details": "📊 Thing 세부 정보:",
        "thing_group_details": "📊 Thing Group 세부 정보:",
        "thing_type_details": "📊 Thing Type 세부 정보:",
        "name_label": "이름",
        "type_label": "타입",
        "description_simple": "설명",
    },
}


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
                print(
                    "❌ Invalid selection / Selección inválida / 無効な選択です / 无效选择 / Seleção inválida / 잘못된 선택입니다. Please select 1-6 / Por favor selecciona 1-6 / 1-6を選択してください / 请选择 1-6 / Por favor selecione 1-6 / 1-6을 선택해주세요."
                )
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! / ¡Adiós! / さようなら！ / 再见！ / Tchau! / 안녕히 가세요!")
            sys.exit(0)


def get_message(key, lang="en"):
    """Get localized message"""
    return MESSAGES.get(lang, MESSAGES["en"]).get(key, key)


def get_learning_moment(moment_key, lang="en"):
    """Get localized learning moment"""
    return MESSAGES.get(lang, MESSAGES["en"]).get("learning_moments", {}).get(moment_key, {})


def print_learning_moment(moment_key, lang="en"):
    """Print a formatted learning moment"""
    moment = get_learning_moment(moment_key, lang)
    if not moment:
        return

    print(f"\n📚 LEARNING MOMENT: {moment.get('title', '')}")
    print(moment.get("content", ""))
    print(f"\n🔄 NEXT: {moment.get('next', '')}")


# Global language variable
USER_LANG = "en"


def check_credentials():
    """Validate AWS credentials are available"""
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease export your AWS credentials:")
        print("export AWS_ACCESS_KEY_ID=<your-access-key>")
        print("export AWS_SECRET_ACCESS_KEY=<your-secret-key>")
        print("export AWS_SESSION_TOKEN=<your-session-token>  # Optional for temporary credentials")
        sys.exit(1)


def get_http_info(operation, params=None):
    """Get HTTP method and path for the operation"""
    http_info = {
        "list_things": ("GET", "/things"),
        "list_certificates": ("GET", "/certificates"),
        "list_thing_groups": ("GET", "/thing-groups"),
        "list_thing_types": ("GET", "/thing-types"),
        "describe_thing": ("GET", f"/things/{params.get('thingName', '<thingName>') if params else '<thingName>'}"),
        "describe_thing_group": (
            "GET",
            f"/thing-groups/{params.get('thingGroupName', '<thingGroupName>') if params else '<thingGroupName>'}",
        ),
        "describe_thing_type": (
            "GET",
            f"/thing-types/{params.get('thingTypeName', '<thingTypeName>') if params else '<thingTypeName>'}",
        ),
        "describe_endpoint": ("GET", "/endpoint"),
    }
    return http_info.get(operation, ("GET", "/unknown"))


def print_api_call(operation, params=None, description=""):
    """Display the API call being made with explanation"""
    method, path = get_http_info(operation, params)
    print(f"\n🔄 {get_message('api_call_label', USER_LANG)}: {operation}")
    print(f"🌐 {get_message('http_request_label', USER_LANG)}: {method} https://iot.<region>.amazonaws.com{path}")
    if description:
        print(f"ℹ️  {get_message('description_label', USER_LANG)}: {description}")
    if params:
        print(f"📥 {get_message('input_parameters_label', USER_LANG)}: {json.dumps(params, indent=2)}")
    else:
        print(f"📥 {get_message('input_parameters_label', USER_LANG)}: {get_message('no_input_parameters', USER_LANG)}")


def print_response(response, explanation=""):
    """Display the API response with explanation"""
    if explanation:
        print(f"💡 {get_message('response_explanation_label', USER_LANG)}: {explanation}")
    print(f"📤 {get_message('response_payload_label', USER_LANG)}: {json.dumps(response, indent=2, default=str)}")


def list_things_paginated(iot, max_results, debug=False):
    """List Things with pagination"""
    print(f"\n{get_message('pagination_learning_title', USER_LANG)}")
    print(get_message("pagination_learning_content", USER_LANG))
    print(f"\n{get_message('pagination_listing', USER_LANG).format(max_results)}")

    next_token = None
    page = 1
    total_things = 0

    while True:
        params = {"maxResults": max_results}
        if next_token:
            params["nextToken"] = next_token

        safe_api_call(
            iot.list_things,
            "list_things",
            description=get_message("api_desc_list_things_paginated", USER_LANG).format(page, max_results),
            explanation=get_message("api_explain_list_things", USER_LANG),
            debug=debug,
            **params,
        )

        response = iot.list_things(**params)
        things = response.get("things", [])
        total_things += len(things)

        print(f"\n{get_message('page_summary', USER_LANG).format(page, len(things))}")

        next_token = response.get("nextToken")
        if not next_token or not things:
            break

        page += 1
        continue_paging = input(f"\n{get_message('continue_next_page', USER_LANG)}").strip().lower()
        if continue_paging not in ["y", "s"]:  # Accept both 'y' (yes) and 's' (sí) for Spanish
            break

    print(f"\n{get_message('pagination_complete', USER_LANG).format(total_things, page)}")


def list_things_by_type(iot, thing_type, debug=False):
    """List Things filtered by Thing Type"""
    print(f"\n{get_message('filter_by_type_learning_title', USER_LANG)}")
    print(get_message("filter_by_type_learning_content", USER_LANG))
    print(f"\n{get_message('filtering_by_type', USER_LANG).format(thing_type)}")

    safe_api_call(
        iot.list_things,
        "list_things",
        description=get_message("api_desc_list_things_by_type", USER_LANG).format(thing_type),
        explanation=get_message("api_explain_list_things", USER_LANG),
        debug=debug,
        thingTypeName=thing_type,
    )

    response = iot.list_things(thingTypeName=thing_type)
    things = response.get("things", [])
    print(f"\n{get_message('filter_type_results', USER_LANG).format(len(things), thing_type)}")


def list_things_by_attribute(iot, attr_name, attr_value, debug=False):
    """List Things filtered by attribute"""
    print(f"\n{get_message('filter_by_attribute_learning_title', USER_LANG)}")
    print(get_message("filter_by_attribute_learning_content", USER_LANG))
    print(f"\n{get_message('filtering_by_attribute', USER_LANG).format(attr_name, attr_value)}")

    safe_api_call(
        iot.list_things,
        "list_things",
        description=get_message("api_desc_list_things_by_attribute", USER_LANG).format(attr_name, attr_value),
        explanation=get_message("api_explain_list_things", USER_LANG),
        debug=debug,
        attributeName=attr_name,
        attributeValue=attr_value,
    )

    response = iot.list_things(attributeName=attr_name, attributeValue=attr_value)
    things = response.get("things", [])
    print(f"\n{get_message('filter_attribute_results', USER_LANG).format(len(things), attr_name, attr_value)}")


def safe_api_call(func, operation, description="", explanation="", debug=True, **kwargs):
    """Execute API call with error handling and explanations"""
    try:
        if debug:
            print_api_call(operation, kwargs if kwargs else None, description)
        else:
            print(f"{get_message('executing', USER_LANG)} {operation}")

        response = func(**kwargs)

        if debug:
            print_response(response, explanation)
        else:
            print(f"✅ {operation} {get_message('completed', USER_LANG)}")
            # Show condensed response for non-debug mode
            if response:
                if isinstance(response, dict):
                    # Show key metrics instead of full response
                    if "things" in response:
                        print(get_message("found_things", USER_LANG).format(len(response["things"])))
                        if response["things"]:
                            print(get_message("thing_names", USER_LANG))
                            for thing in response["things"]:
                                thing_type = (
                                    f" ({thing.get('thingTypeName', 'No Type')})" if thing.get("thingTypeName") else ""
                                )
                                print(f"   • {thing['thingName']}{thing_type}")
                    elif "certificates" in response:
                        print(get_message("found_certificates", USER_LANG).format(len(response["certificates"])))
                        if response["certificates"]:
                            print(get_message("certificate_ids", USER_LANG))
                            for cert in response["certificates"]:
                                status = cert.get("status", "Unknown")
                                print(f"   • {cert['certificateId'][:16]}... ({status})")
                    elif "thingGroups" in response:
                        print(get_message("found_thing_groups", USER_LANG).format(len(response["thingGroups"])))
                        if response["thingGroups"]:
                            print(get_message("group_names", USER_LANG))
                            for group in response["thingGroups"]:
                                print(f"   • {group['groupName']}")
                    elif "thingTypes" in response:
                        print(get_message("found_thing_types", USER_LANG).format(len(response["thingTypes"])))
                        if response["thingTypes"]:
                            print(get_message("type_names", USER_LANG))
                            for thing_type in response["thingTypes"]:
                                print(f"   • {thing_type['thingTypeName']}")
                    elif "thingName" in response:
                        # Handle describe_thing response
                        print(get_message("thing_details", USER_LANG))
                        print(f"   {get_message('name_label', USER_LANG)}: {response['thingName']}")
                        if response.get("thingTypeName"):
                            print(f"   {get_message('type_label', USER_LANG)}: {response['thingTypeName']}")
                        if response.get("attributes"):
                            print(f"   Attributes: {len(response['attributes'])} defined")
                            for key, value in list(response["attributes"].items())[:3]:  # Show first 3 attributes
                                print(f"     • {key}: {value}")
                            if len(response["attributes"]) > 3:
                                print(f"     ... and {len(response['attributes']) - 3} more")
                        print(f"   Version: {response.get('version', 'Unknown')}")
                    elif "thingGroupName" in response:
                        # Handle describe_thing_group response
                        print(get_message("thing_group_details", USER_LANG))
                        print(f"   {get_message('name_label', USER_LANG)}: {response['thingGroupName']}")
                        if response.get("thingGroupProperties", {}).get("thingGroupDescription"):
                            print(
                                f"   {get_message('description_simple', USER_LANG)}: {response['thingGroupProperties']['thingGroupDescription']}"
                            )
                        if response.get("thingGroupProperties", {}).get("attributePayload", {}).get("attributes"):
                            attrs = response["thingGroupProperties"]["attributePayload"]["attributes"]
                            print(f"   Attributes: {len(attrs)} defined")
                    elif "thingTypeName" in response:
                        # Handle describe_thing_type response
                        print(get_message("thing_type_details", USER_LANG))
                        print(f"   {get_message('name_label', USER_LANG)}: {response['thingTypeName']}")
                        if response.get("thingTypeProperties", {}).get("description"):
                            print(
                                f"   {get_message('description_simple', USER_LANG)}: {response['thingTypeProperties']['description']}"
                            )
                        if response.get("thingTypeProperties", {}).get("searchableAttributes"):
                            attrs = response["thingTypeProperties"]["searchableAttributes"]
                            print(f"   Searchable Attributes: {', '.join(attrs)}")
                    elif "endpointAddress" in response:
                        # Handle describe_endpoint response
                        print("📊 IoT Endpoint:")
                        print(f"   URL: {response['endpointAddress']}")
                    else:
                        print("📊 Response received")

        return response
    except ClientError as e:
        print(f"{get_message('api_error', USER_LANG)} {e.response['Error']['Code']} - {e.response['Error']['Message']}")
        if debug:
            print(get_message("debug_full_error", USER_LANG))
            print(json.dumps(e.response, indent=2, default=str))
    except Exception as e:
        print(f"{get_message('error', USER_LANG)} {str(e)}")
        if debug:
            import traceback

            print(get_message("debug_full_traceback", USER_LANG))
            traceback.print_exc()


def main():
    try:
        # Get user's preferred language
        global USER_LANG
        USER_LANG = get_language()

        # Check for debug flag
        debug_mode = "--debug" in sys.argv or "-d" in sys.argv

        print(get_message("title", USER_LANG))
        print(get_message("separator", USER_LANG))

        # Display AWS context first
        try:
            sts = boto3.client("sts")
            iot = boto3.client("iot")
            identity = sts.get_caller_identity()

            print(get_message("aws_config", USER_LANG))
            print(f"   {get_message('account_id', USER_LANG)}: {identity['Account']}")
            print(f"   {get_message('region', USER_LANG)}: {iot.meta.region_name}")
            print()

        except Exception as e:
            print(f"{get_message('aws_context_error', USER_LANG)} {str(e)}")
            print(get_message("aws_credentials_reminder", USER_LANG))
            print()

        print(get_message("description", USER_LANG))

        if debug_mode:
            print(f"\n{get_message('debug_enabled', USER_LANG)}")
            for feature in get_message("debug_features", USER_LANG):
                print(feature)
        else:
            print(f"\n{get_message('tip', USER_LANG)}")
            for feature in get_message("tip_features", USER_LANG):
                print(feature)

        print(get_message("separator", USER_LANG))

        check_credentials()

        try:
            iot = boto3.client("iot")
            print(get_message("client_initialized", USER_LANG))

            if debug_mode:
                print("🔍 DEBUG: Client configuration:")
                print(f"   Region: {iot.meta.region_name}")
                print(f"   Service: {iot.meta.service_model.service_name}")
                print(f"   API Version: {iot.meta.service_model.api_version}")
        except NoCredentialsError:
            print(get_message("invalid_credentials", USER_LANG))
            sys.exit(1)
        except NoRegionError:
            print(get_message("no_region_error", USER_LANG))
            for instruction in get_message("region_setup_instructions", USER_LANG):
                print(f"   {instruction}")
            sys.exit(1)

        print(f"\n📚 LEARNING MOMENT: {get_message('learning_intro_title', USER_LANG)}")
        print(get_message("learning_intro_content", USER_LANG))
        print(f"\n🔄 NEXT: {get_message('learning_intro_next', USER_LANG)}")
        try:
            input(get_message("press_enter", USER_LANG))
        except KeyboardInterrupt:
            print(f"\n\n{get_message('goodbye', USER_LANG)}")
            return

        while True:
            try:
                print(f"\n{get_message('operations_menu', USER_LANG)}")
                for operation in get_message("operations", USER_LANG):
                    print(operation)

                choice = input(f"\n{get_message('select_operation', USER_LANG)} ").strip()
            except KeyboardInterrupt:
                print(f"\n\n{get_message('goodbye', USER_LANG)}")
                break

            if choice == "1":
                print_learning_moment("list_things", USER_LANG)
                input(get_message("press_enter", USER_LANG))

                # Ask for listing options
                print(f"\n{get_message('list_things_options', USER_LANG)}")
                for menu_item in get_message("list_things_menu", USER_LANG):
                    print(menu_item)

                option = input(get_message("select_option", USER_LANG)).strip()

                if option == "2":
                    max_results = input(get_message("max_results_prompt", USER_LANG)).strip()
                    max_results = int(max_results) if max_results.isdigit() else 5
                    list_things_paginated(iot, max_results, debug_mode)
                elif option == "3":
                    thing_type = input(get_message("thing_type_prompt", USER_LANG)).strip()
                    if thing_type:
                        list_things_by_type(iot, thing_type, debug_mode)
                    else:
                        print(get_message("no_thing_type", USER_LANG))
                elif option == "4":
                    attr_name = input(get_message("attribute_name_prompt", USER_LANG)).strip()
                    attr_value = input(get_message("attribute_value_prompt", USER_LANG)).strip()
                    if attr_name and attr_value:
                        list_things_by_attribute(iot, attr_name, attr_value, debug_mode)
                    else:
                        print(get_message("attribute_required", USER_LANG))
                else:
                    safe_api_call(
                        iot.list_things,
                        "list_things",
                        description=get_message("api_desc_list_things", USER_LANG),
                        explanation=get_message("api_explain_list_things", USER_LANG),
                        debug=debug_mode,
                    )

                input(f"\n{get_message('return_to_menu', USER_LANG)}")

            elif choice == "2":
                print_learning_moment("list_certificates", USER_LANG)
                input(get_message("press_enter", USER_LANG))

                safe_api_call(
                    iot.list_certificates,
                    "list_certificates",
                    description=get_message("api_desc_list_certificates", USER_LANG),
                    explanation=get_message("api_explain_list_certificates", USER_LANG),
                    debug=debug_mode,
                )
                input(f"\n{get_message('return_to_menu', USER_LANG)}")

            elif choice == "3":
                print_learning_moment("list_thing_groups", USER_LANG)
                input(get_message("press_enter", USER_LANG))

                safe_api_call(
                    iot.list_thing_groups,
                    "list_thing_groups",
                    description=get_message("api_desc_list_thing_groups", USER_LANG),
                    explanation=get_message("api_explain_list_thing_groups", USER_LANG),
                    debug=debug_mode,
                )
                input(f"\n{get_message('return_to_menu', USER_LANG)}")

            elif choice == "4":
                print_learning_moment("list_thing_types", USER_LANG)
                input(get_message("press_enter", USER_LANG))

                safe_api_call(
                    iot.list_thing_types,
                    "list_thing_types",
                    description=get_message("api_desc_list_thing_types", USER_LANG),
                    explanation=get_message("api_explain_list_thing_types", USER_LANG),
                    debug=debug_mode,
                )
                input(f"\n{get_message('return_to_menu', USER_LANG)}")

            elif choice == "5":
                print_learning_moment("describe_thing", USER_LANG)
                input(get_message("press_enter", USER_LANG))

                # Show available Things
                try:
                    things_response = iot.list_things()
                    if things_response.get("things"):
                        print(f"\n{get_message('available_things', USER_LANG)} ({len(things_response['things'])}):")
                        for i, thing in enumerate(things_response["things"][:10], 1):
                            thing_type = f" ({thing.get('thingTypeName', 'No Type')})" if thing.get("thingTypeName") else ""
                            print(f"   {i}. {thing['thingName']}{thing_type}")
                        if len(things_response["things"]) > 10:
                            print(f"   ... and {len(things_response['things']) - 10} more")
                    else:
                        print(f"\n{get_message('no_things_found', USER_LANG)}")
                except Exception as e:
                    print(f"\n{get_message('could_not_list_things', USER_LANG)} {str(e)}")

                thing_name = input(f"\n{get_message('enter_thing_name', USER_LANG)}").strip()
                if thing_name:
                    safe_api_call(
                        iot.describe_thing,
                        "describe_thing",
                        description=get_message("api_desc_describe_thing", USER_LANG),
                        explanation=get_message("api_explain_describe_thing", USER_LANG),
                        debug=debug_mode,
                        thingName=thing_name,
                    )
                    input(f"\n{get_message('return_to_menu', USER_LANG)}")

            elif choice == "6":
                print_learning_moment("describe_thing_group", USER_LANG)
                input(get_message("press_enter", USER_LANG))

                # Show available Thing Groups
                try:
                    groups_response = iot.list_thing_groups()
                    if groups_response.get("thingGroups"):
                        print(f"\n{get_message('available_groups', USER_LANG)} ({len(groups_response['thingGroups'])}):")
                        for i, group in enumerate(groups_response["thingGroups"], 1):
                            print(f"   {i}. {group['groupName']}")

                        selection = input(f"\n{get_message('enter_group_selection', USER_LANG)}").strip()
                        group_name = None

                        # Check if input is a number
                        if selection.isdigit():
                            group_index = int(selection) - 1
                            if 0 <= group_index < len(groups_response["thingGroups"]):
                                group_name = groups_response["thingGroups"][group_index]["groupName"]
                            else:
                                print(f"{get_message('invalid_selection', USER_LANG)} 1-{len(groups_response['thingGroups'])}")
                        else:
                            # Treat as group name
                            group_name = selection

                        if group_name:
                            safe_api_call(
                                iot.describe_thing_group,
                                "describe_thing_group",
                                description=get_message("api_desc_describe_thing_group", USER_LANG),
                                explanation=get_message("api_explain_describe_thing_group", USER_LANG),
                                debug=debug_mode,
                                thingGroupName=group_name,
                            )
                    else:
                        print(f"\n{get_message('no_groups_found', USER_LANG)}")
                except Exception as e:
                    print(f"\n{get_message('could_not_list_groups', USER_LANG)} {str(e)}")

                input(f"\n{get_message('return_to_menu', USER_LANG)}")

            elif choice == "7":
                print_learning_moment("describe_thing_type", USER_LANG)
                input(get_message("press_enter", USER_LANG))

                # Show available Thing Types
                try:
                    types_response = iot.list_thing_types()
                    if types_response.get("thingTypes"):
                        print(f"\n{get_message('available_types', USER_LANG)} ({len(types_response['thingTypes'])}):")
                        for i, thing_type in enumerate(types_response["thingTypes"], 1):
                            print(f"   {i}. {thing_type['thingTypeName']}")

                        selection = input(f"\n{get_message('enter_type_selection', USER_LANG)}").strip()
                        type_name = None

                        # Check if input is a number
                        if selection.isdigit():
                            type_index = int(selection) - 1
                            if 0 <= type_index < len(types_response["thingTypes"]):
                                type_name = types_response["thingTypes"][type_index]["thingTypeName"]
                            else:
                                print(f"{get_message('invalid_selection', USER_LANG)} 1-{len(types_response['thingTypes'])}")
                        else:
                            # Treat as type name
                            type_name = selection

                        if type_name:
                            safe_api_call(
                                iot.describe_thing_type,
                                "describe_thing_type",
                                description=get_message("api_desc_describe_thing_type", USER_LANG),
                                explanation=get_message("api_explain_describe_thing_type", USER_LANG),
                                debug=debug_mode,
                                thingTypeName=type_name,
                            )
                    else:
                        print(f"\n{get_message('no_types_found', USER_LANG)}")
                except Exception as e:
                    print(f"\n{get_message('could_not_list_types', USER_LANG)} {str(e)}")

                input(f"\n{get_message('return_to_menu', USER_LANG)}")

            elif choice == "8":
                print_learning_moment("describe_endpoint", USER_LANG)
                input(get_message("press_enter", USER_LANG))

                endpoint_type = input(get_message("endpoint_type_prompt", USER_LANG)).strip()
                if not endpoint_type:
                    endpoint_type = "iot:Data-ATS"
                safe_api_call(
                    iot.describe_endpoint,
                    "describe_endpoint",
                    description=get_message("api_desc_describe_endpoint", USER_LANG),
                    explanation=get_message("api_explain_describe_endpoint", USER_LANG),
                    debug=debug_mode,
                    endpointType=endpoint_type,
                )
                input(f"\n{get_message('return_to_menu', USER_LANG)}")

            elif choice == "9":
                print(get_message("goodbye", USER_LANG))
                break

            else:
                print(get_message("invalid_choice", USER_LANG))

            # Handle Ctrl+C in continue prompts
            if choice != "9":
                try:
                    pass  # Continue prompts are already handled in individual sections
                except KeyboardInterrupt:
                    print(f"\n\n{get_message('goodbye', USER_LANG)}")
                    break

    except KeyboardInterrupt:
        print(f"\n\n{get_message('goodbye', USER_LANG)}")


if __name__ == "__main__":
    main()

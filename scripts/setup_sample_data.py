#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import random
import sys
import time
import traceback
import uuid
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError

# Simple translation system for learning content
MESSAGES = {
    "en": {
        "title": "🚀 AWS IoT Sample Data Setup",
        "separator": "=" * 32,
        "aws_config": "📍 AWS Configuration:",
        "account_id": "Account ID",
        "region": "Region",
        "aws_context_error": "⚠️ Could not retrieve AWS context:",
        "aws_credentials_reminder": "   Make sure AWS credentials are configured",
        "description_intro": "This script will create sample IoT resources for learning:",
        "thing_types_desc": "Thing Types:",
        "thing_groups_desc": "Thing Groups:",
        "things_desc": "Things with random attributes",
        "debug_enabled": "🔍 DEBUG MODE ENABLED",
        "debug_features": [
            "• Will show detailed API requests and responses",
            "• Slower execution with extended pauses",
            "• Full error details and tracebacks",
        ],
        "tip": "💡 Tip: Use --debug or -d flag to see detailed API calls",
        "continue_prompt": "Continue? (y/N): ",
        "setup_cancelled": "Setup cancelled",
        "client_initialized": "✅ AWS IoT client initialized",
        "client_error": "❌ Error initializing AWS IoT client:",
        "credentials_reminder": "Make sure you have AWS credentials and region configured",
        "no_region_error": "❌ AWS region not configured",
        "region_setup_instructions": [
            "Please configure your AWS region using one of these methods:",
            "1. Set environment variable: export AWS_DEFAULT_REGION=us-east-1",
            "2. Configure AWS CLI: aws configure",
            "3. Set region in AWS credentials file",
        ],
        "invalid_credentials": "❌ Invalid AWS credentials",
        "credentials_check_failed": "❌ Missing required environment variables:",
        "credentials_instructions": [
            "Please export your AWS credentials:",
            "export AWS_ACCESS_KEY_ID=<your-access-key>",
            "export AWS_SECRET_ACCESS_KEY=<your-secret-key>",
            "export AWS_SESSION_TOKEN=<your-session-token>  # Optional for temporary credentials",
        ],
        "step_1_title": "Creating Thing Types",
        "step_2_title": "Creating Thing Groups",
        "step_3_title": "Creating {} Things with attributes",
        "step_4_title": "Adding Things to Thing Groups",
        "step_5_title": "Setup Summary",
        "creating": "Creating",
        "created": "Created",
        "already_exists": "already exists, skipping",
        "deprecated_undeprecating": "is deprecated, undeprecating...",
        "undeprecated": "undeprecated successfully",
        "already_active": "already exists and is active",
        "error_checking": "Error checking",
        "error_creating": "Error creating",
        "creating_thing": "📱 Creating Thing:",
        "customer_id": "Customer ID:",
        "country": "Country:",
        "manufacturing_date": "Manufacturing Date:",
        "thing_type": "Thing Type:",
        "adding_to_group": "Adding {} to group {}",
        "added_to_group": "Added {} to {}",
        "error_adding": "Error adding {} to {}:",
        "resources_created": "📊 Resources Created:",
        "things": "Things:",
        "thing_types": "Thing Types:",
        "thing_groups": "Thing Groups:",
        "sample_thing_names": "🎯 Sample Thing Names:",
        "and_more": "... and {} more",
        "error_summary": "❌ Error getting summary:",
        "setup_complete": "🎉 Setup complete! You can now use iot_registry_explorer.py to explore the data.",
        "debug_session_complete": "🔍 DEBUG: Session completed with detailed API logging",
        "setup_cancelled_user": "👋 Setup cancelled by user. Goodbye!",
        "debug_creating": "🔍 DEBUG: Creating",
        "debug_api_call": "📤 API Call:",
        "debug_input_params": "📥 Input Parameters:",
        "debug_api_response": "📤 API Response:",
        "debug_full_error": "🔍 DEBUG: Full error response:",
        "debug_full_traceback": "🔍 DEBUG: Full traceback:",
        "api_error": "❌ AWS API Error in",
        "missing_param_error": "❌ Missing required parameter in",
        "invalid_value_error": "❌ Invalid value in",
        "unexpected_error": "❌ Unexpected error in",
        "press_enter": "Press Enter to continue...",
        "learning_moments": {
            "hierarchy": {
                "title": "📚 LEARNING MOMENT: AWS IoT Resource Hierarchy",
                "content": "AWS IoT uses a hierarchical structure to organize devices: Thing Types (templates) define device categories, Thing Groups provide organizational structure, and Things represent actual devices. This hierarchy enables scalable device management, bulk operations, and policy inheritance across your IoT fleet.",
                "next": "We will create sample resources to demonstrate this hierarchy",
            },
            "thing_groups": {
                "title": "📚 LEARNING MOMENT: Thing Groups - Device Organization",
                "content": "Thing Groups provide hierarchical organization for your IoT devices, similar to folders for files. They enable bulk operations, policy inheritance, and logical grouping by location, function, or business criteria. Groups can contain other groups, creating flexible organizational structures for large IoT deployments.",
                "next": "We will create Thing Groups for device organization",
            },
            "things": {
                "title": "📚 LEARNING MOMENT: Things - Device Registration",
                "content": "Things represent your actual IoT devices in AWS IoT Core. Each Thing has a unique name, optional attributes (like serial number, location), and can be assigned to a Thing Type for standardization. Things are the foundation for device management, security policies, and shadow state synchronization.",
                "next": "We will create individual Things with realistic attributes",
            },
            "relationships": {
                "title": "📚 LEARNING MOMENT: Thing-Group Relationships",
                "content": "Adding Things to Groups creates organizational relationships that enable bulk operations and policy inheritance. A Thing can belong to multiple groups, and groups can be nested. This hierarchy is essential for managing device fleets at scale, applying policies, and organizing devices by business logic.",
                "next": "We will assign Things to appropriate Groups",
            },
        },
    },
    "es": {
        "title": "🚀 Configuración de Datos de Muestra de AWS IoT",
        "separator": "=" * 32,
        "aws_config": "📍 Configuración de AWS:",
        "account_id": "ID de Cuenta",
        "region": "Región",
        "aws_context_error": "⚠️ No se pudo recuperar el contexto de AWS:",
        "aws_credentials_reminder": "   Asegúrate de que las credenciales de AWS estén configuradas",
        "description_intro": "Este script creará recursos IoT de muestra para aprendizaje:",
        "thing_types_desc": "Thing Types:",
        "thing_groups_desc": "Thing Groups:",
        "things_desc": "Things con atributos aleatorios",
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Mostrará solicitudes y respuestas detalladas de API",
            "• Ejecución más lenta con pausas extendidas",
            "• Detalles completos de errores y trazas",
        ],
        "tip": "💡 Consejo: Usa la bandera --debug o -d para ver llamadas detalladas de API",
        "continue_prompt": "¿Continuar? (s/N): ",
        "setup_cancelled": "Configuración cancelada",
        "client_initialized": "✅ Cliente de AWS IoT inicializado",
        "client_error": "❌ Error inicializando cliente de AWS IoT:",
        "credentials_reminder": "Asegúrate de tener credenciales y región de AWS configuradas",
        "no_region_error": "❌ Región de AWS no configurada",
        "region_setup_instructions": [
            "Por favor configura tu región de AWS usando uno de estos métodos:",
            "1. Variable de entorno: export AWS_DEFAULT_REGION=us-east-1",
            "2. Configurar AWS CLI: aws configure",
            "3. Establecer región en el archivo de credenciales de AWS",
        ],
        "invalid_credentials": "❌ Credenciales de AWS inválidas",
        "credentials_check_failed": "❌ Variables de entorno requeridas faltantes:",
        "credentials_instructions": [
            "Por favor exporta tus credenciales de AWS:",
            "export AWS_ACCESS_KEY_ID=<tu-access-key>",
            "export AWS_SECRET_ACCESS_KEY=<tu-secret-key>",
            "export AWS_SESSION_TOKEN=<tu-session-token>  # Opcional para credenciales temporales",
        ],
        "step_1_title": "Creando Thing Types",
        "step_2_title": "Creando Thing Groups",
        "step_3_title": "Creando {} Things con atributos",
        "step_4_title": "Agregando Things a Thing Groups",
        "step_5_title": "Resumen de Configuración",
        "creating": "Creando",
        "created": "Creado",
        "already_exists": "ya existe, omitiendo",
        "deprecated_undeprecating": "está deprecado, reactivando...",
        "undeprecated": "reactivado exitosamente",
        "already_active": "ya existe y está activo",
        "error_checking": "Error verificando",
        "error_creating": "Error creando",
        "creating_thing": "📱 Creando Thing:",
        "customer_id": "ID de Cliente:",
        "country": "País:",
        "manufacturing_date": "Fecha de Fabricación:",
        "thing_type": "Thing Type:",
        "adding_to_group": "Agregando {} al grupo {}",
        "added_to_group": "Agregado {} a {}",
        "error_adding": "Error agregando {} a {}:",
        "resources_created": "📊 Recursos Creados:",
        "things": "Things:",
        "thing_types": "Thing Types:",
        "thing_groups": "Thing Groups:",
        "sample_thing_names": "🎯 Nombres de Things de Muestra:",
        "and_more": "... y {} más",
        "error_summary": "❌ Error obteniendo resumen:",
        "setup_complete": "🎉 ¡Configuración completa! Ahora puedes usar iot_registry_explorer.py para explorar los datos.",
        "debug_session_complete": "🔍 DEBUG: Sesión completada con registro detallado de API",
        "setup_cancelled_user": "👋 ¡Configuración cancelada por el usuario. Adiós!",
        "debug_creating": "🔍 DEBUG: Creando",
        "debug_api_call": "📤 Llamada API:",
        "debug_input_params": "📥 Parámetros de Entrada:",
        "debug_api_response": "📤 Respuesta API:",
        "debug_full_error": "🔍 DEBUG: Respuesta completa de error:",
        "debug_full_traceback": "🔍 DEBUG: Traza completa:",
        "api_error": "❌ Error de API de AWS en",
        "missing_param_error": "❌ Parámetro requerido faltante en",
        "invalid_value_error": "❌ Valor inválido en",
        "unexpected_error": "❌ Error inesperado en",
        "press_enter": "Presiona Enter para continuar...",
        "learning_moments": {
            "hierarchy": {
                "title": "📚 LEARNING MOMENT: Jerarquía de Recursos de AWS IoT",
                "content": "AWS IoT usa una estructura jerárquica para organizar dispositivos: Thing Types (plantillas) definen categorías de dispositivos, Thing Groups proporcionan estructura organizacional, y Things representan dispositivos reales. Esta jerarquía permite gestión escalable de dispositivos, operaciones masivas y herencia de políticas en tu flota IoT.",
                "next": "Crearemos recursos de muestra para demostrar esta jerarquía",
            },
            "thing_groups": {
                "title": "📚 LEARNING MOMENT: Thing Groups - Organización de Dispositivos",
                "content": "Los Thing Groups proporcionan organización jerárquica para tus dispositivos IoT, similar a carpetas para archivos. Permiten operaciones masivas, herencia de políticas y agrupación lógica por ubicación, función o criterios de negocio. Los grupos pueden contener otros grupos, creando estructuras organizacionales flexibles para despliegues IoT grandes.",
                "next": "Crearemos Thing Groups para organización de dispositivos",
            },
            "things": {
                "title": "📚 LEARNING MOMENT: Things - Registro de Dispositivos",
                "content": "Los Things representan tus dispositivos IoT reales en AWS IoT Core. Cada Thing tiene un nombre único, atributos opcionales (como número de serie, ubicación), y puede asignarse a un Thing Type para estandarización. Los Things son la base para gestión de dispositivos, políticas de seguridad y sincronización de estado shadow.",
                "next": "Crearemos Things individuales con atributos realistas",
            },
            "relationships": {
                "title": "📚 LEARNING MOMENT: Relaciones Thing-Group",
                "content": "Agregar Things a Groups crea relaciones organizacionales que permiten operaciones masivas y herencia de políticas. Un Thing puede pertenecer a múltiples grupos, y los grupos pueden anidarse. Esta jerarquía es esencial para gestionar flotas de dispositivos a escala, aplicar políticas y organizar dispositivos por lógica de negocio.",
                "next": "Asignaremos Things a Groups apropiados",
            },
        },
    },
    "ja": {
        "title": "🚀 AWS IoT サンプルデータセットアップ",
        "separator": "=" * 32,
        "aws_config": "📍 AWS設定:",
        "account_id": "アカウントID",
        "region": "リージョン",
        "aws_context_error": "⚠️ AWSコンテキストを取得できませんでした:",
        "aws_credentials_reminder": "   AWS認証情報が設定されていることを確認してください",
        "description_intro": "このスクリプトは学習用のサンプルIoTリソースを作成します:",
        "thing_types_desc": "Thing Types:",
        "thing_groups_desc": "Thing Groups:",
        "things_desc": "ランダム属性を持つThings",
        "debug_enabled": "🔍 デバッグモード有効",
        "debug_features": [
            "• 詳細なAPIリクエストとレスポンスを表示",
            "• 拡張ポーズによる実行速度の低下",
            "• 完全なエラー詳細とトレースバック",
        ],
        "tip": "💡 ヒント: --debugまたは-dフラグを使用して詳細なAPI呼び出しを表示",
        "continue_prompt": "続行しますか？ (y/N): ",
        "setup_cancelled": "セットアップがキャンセルされました",
        "client_initialized": "✅ AWS IoTクライアントが初期化されました",
        "client_error": "❌ AWS IoTクライアントの初期化エラー:",
        "credentials_reminder": "AWS認証情報とリージョンが設定されていることを確認してください",
        "no_region_error": "❌ AWSリージョンが設定されていません",
        "region_setup_instructions": [
            "以下のいずれかの方法でAWSリージョンを設定してください:",
            "1. 環境変数を設定: export AWS_DEFAULT_REGION=us-east-1",
            "2. AWS CLIを設定: aws configure",
            "3. AWS認証情報ファイルでリージョンを設定",
        ],
        "invalid_credentials": "❌ 無効なAWS認証情報",
        "credentials_check_failed": "❌ 必要な環境変数が不足しています:",
        "credentials_instructions": [
            "AWS認証情報をエクスポートしてください:",
            "export AWS_ACCESS_KEY_ID=<your-access-key>",
            "export AWS_SECRET_ACCESS_KEY=<your-secret-key>",
            "export AWS_SESSION_TOKEN=<your-session-token>  # 一時認証情報の場合はオプション",
        ],
        "step_1_title": "Thing Typesを作成中",
        "step_2_title": "Thing Groupsを作成中",
        "step_3_title": "{}個のThingsを属性付きで作成中",
        "step_4_title": "ThingsをThing Groupsに追加中",
        "step_5_title": "セットアップ概要",
        "creating": "作成中",
        "created": "作成完了",
        "already_exists": "既に存在するため、スキップします",
        "deprecated_undeprecating": "は非推奨です、非推奨を解除中...",
        "undeprecated": "非推奨解除が成功しました",
        "already_active": "既に存在し、アクティブです",
        "error_checking": "確認エラー",
        "error_creating": "作成エラー",
        "creating_thing": "📱 Thing作成中:",
        "customer_id": "顧客ID:",
        "country": "国:",
        "manufacturing_date": "製造日:",
        "thing_type": "Thing Type:",
        "adding_to_group": "{}をグループ{}に追加中",
        "added_to_group": "{}を{}に追加しました",
        "error_adding": "{}を{}に追加中にエラー:",
        "resources_created": "📊 作成されたリソース:",
        "things": "Things:",
        "thing_types": "Thing Types:",
        "thing_groups": "Thing Groups:",
        "sample_thing_names": "🎯 サンプルThing名:",
        "and_more": "... その他{}個",
        "error_summary": "❌ 概要取得エラー:",
        "setup_complete": "🎉 セットアップ完了！iot_registry_explorer.pyを使用してデータを探索できます。",
        "debug_session_complete": "🔍 デバッグ: 詳細なAPIログ記録でセッションが完了しました",
        "setup_cancelled_user": "👋 ユーザーによってセットアップがキャンセルされました。さようなら！",
        "debug_creating": "🔍 デバッグ: 作成中",
        "debug_api_call": "📤 API呼び出し:",
        "debug_input_params": "📥 入力パラメータ:",
        "debug_api_response": "📤 APIレスポンス:",
        "debug_full_error": "🔍 デバッグ: 完全なエラーレスポンス:",
        "debug_full_traceback": "🔍 デバッグ: 完全なトレースバック:",
        "api_error": "❌ AWS APIエラー",
        "missing_param_error": "❌ 必要なパラメータが不足",
        "invalid_value_error": "❌ 無効な値",
        "unexpected_error": "❌ 予期しないエラー",
        "press_enter": "Enterキーを押して続行...",
        "learning_moments": {
            "hierarchy": {
                "title": "📚 学習ポイント: AWS IoTリソース階層",
                "content": "AWS IoTはデバイスを整理するために階層構造を使用します: Thing Types（テンプレート）はデバイスカテゴリを定義し、Thing Groupsは組織構造を提供し、Thingsは実際のデバイスを表します。この階層により、スケーラブルなデバイス管理、一括操作、IoTフリート全体でのポリシー継承が可能になります。",
                "next": "この階層を実証するためにサンプルリソースを作成します",
            },
            "thing_groups": {
                "title": "📚 学習ポイント: Thing Groups - デバイス組織",
                "content": "Thing Groupsは、ファイル用のフォルダと同様に、IoTデバイスの階層組織を提供します。場所、機能、またはビジネス基準による一括操作、ポリシー継承、論理グループ化を可能にします。グループは他のグループを含むことができ、大規模なIoTデプロイメントのための柔軟な組織構造を作成します。",
                "next": "デバイス組織のためのThing Groupsを作成します",
            },
            "things": {
                "title": "📚 学習ポイント: Things - デバイス登録",
                "content": "ThingsはAWS IoT Coreでの実際のIoTデバイスを表します。各Thingは一意の名前、オプションの属性（シリアル番号、場所など）を持ち、標準化のためにThing Typeに割り当てることができます。Thingsはデバイス管理、セキュリティポリシー、シャドウ状態同期の基盤です。",
                "next": "現実的な属性を持つ個別のThingsを作成します",
            },
            "relationships": {
                "title": "📚 学習ポイント: Thing-Group関係",
                "content": "ThingsをGroupsに追加することで、一括操作とポリシー継承を可能にする組織関係を作成します。Thingは複数のグループに属することができ、グループはネストできます。この階層は、スケールでのデバイスフリート管理、ポリシーの適用、ビジネスロジックによるデバイスの組織化に不可欠です。",
                "next": "適切なGroupsにThingsを割り当てます",
            },
        },
    },
    "zh-CN": {
        "title": "🚀 AWS IoT 示例数据设置",
        "separator": "=" * 32,
        "aws_config": "📍 AWS 配置:",
        "account_id": "账户 ID",
        "region": "区域",
        "aws_context_error": "⚠️ 无法检索 AWS 上下文:",
        "aws_credentials_reminder": "   确保已配置 AWS 凭证",
        "description_intro": "此脚本将为学习创建示例 IoT 资源:",
        "thing_types_desc": "Thing Types:",
        "thing_groups_desc": "Thing Groups:",
        "things_desc": "具有随机属性的 Things",
        "debug_enabled": "🔍 调试模式已启用",
        "debug_features": ["• 将显示详细的 API 请求和响应", "• 执行较慢，有延长的暂停", "• 完整的错误详细信息和堆栈跟踪"],
        "tip": "💡 提示: 使用 --debug 或 -d 标志查看详细的 API 调用",
        "continue_prompt": "继续吗？ (y/N): ",
        "setup_cancelled": "设置已取消",
        "client_initialized": "✅ AWS IoT 客户端已初始化",
        "client_error": "❌ 初始化 AWS IoT 客户端时出错:",
        "credentials_reminder": "确保您已配置 AWS 凭证和区域",
        "no_region_error": "❌ 未配置 AWS 区域",
        "region_setup_instructions": [
            "请使用以下方法之一配置您的 AWS 区域:",
            "1. 设置环境变量: export AWS_DEFAULT_REGION=us-east-1",
            "2. 配置 AWS CLI: aws configure",
            "3. 在 AWS 凭证文件中设置区域",
        ],
        "invalid_credentials": "❌ 无效的 AWS 凭证",
        "credentials_check_failed": "❌ 缺少必需的环境变量:",
        "credentials_instructions": [
            "请导出您的 AWS 凭证:",
            "export AWS_ACCESS_KEY_ID=<your-access-key>",
            "export AWS_SECRET_ACCESS_KEY=<your-secret-key>",
            "export AWS_SESSION_TOKEN=<your-session-token>  # 临时凭证可选",
        ],
        "step_1_title": "创建 Thing Types",
        "step_2_title": "创建 Thing Groups",
        "step_3_title": "创建 {} 个带属性的 Things",
        "step_4_title": "将 Things 添加到 Thing Groups",
        "step_5_title": "设置摘要",
        "creating": "创建中",
        "created": "已创建",
        "already_exists": "已存在，跳过",
        "deprecated_undeprecating": "已弃用，正在取消弃用...",
        "undeprecated": "成功取消弃用",
        "already_active": "已存在且处于活动状态",
        "error_checking": "检查错误",
        "error_creating": "创建错误",
        "creating_thing": "📱 创建 Thing:",
        "customer_id": "客户 ID:",
        "country": "国家:",
        "manufacturing_date": "制造日期:",
        "thing_type": "Thing Type:",
        "adding_to_group": "将 {} 添加到组 {}",
        "added_to_group": "已将 {} 添加到 {}",
        "error_adding": "将 {} 添加到 {} 时出错:",
        "resources_created": "📊 已创建的资源:",
        "things": "Things:",
        "thing_types": "Thing Types:",
        "thing_groups": "Thing Groups:",
        "sample_thing_names": "🎯 示例 Thing 名称:",
        "and_more": "... 还有 {} 个",
        "error_summary": "❌ 获取摘要时出错:",
        "setup_complete": "🎉 设置完成！您现在可以使用 iot_registry_explorer.py 来探索数据。",
        "debug_session_complete": "🔍 调试: 会话已完成，包含详细的 API 日志记录",
        "setup_cancelled_user": "👋 用户取消了设置。再见！",
        "debug_creating": "🔍 调试: 创建中",
        "debug_api_call": "📤 API 调用:",
        "debug_input_params": "📥 输入参数:",
        "debug_api_response": "📤 API 响应:",
        "debug_full_error": "🔍 调试: 完整错误响应:",
        "debug_full_traceback": "🔍 调试: 完整堆栈跟踪:",
        "api_error": "❌ AWS API 错误",
        "missing_param_error": "❌ 缺少必需参数",
        "invalid_value_error": "❌ 无效值",
        "unexpected_error": "❌ 意外错误",
        "press_enter": "按 Enter 继续...",
        "learning_moments": {
            "hierarchy": {
                "title": "📚 学习要点: AWS IoT 资源层次结构",
                "content": "AWS IoT 使用层次结构来组织设备: Thing Types（模板）定义设备类别，Thing Groups 提供组织结构，Things 代表实际设备。这种层次结构实现了可扩展的设备管理、批量操作和整个 IoT 车队的策略继承。",
                "next": "我们将创建示例资源来演示这种层次结构",
            },
            "thing_groups": {
                "title": "📚 学习要点: Thing Groups - 设备组织",
                "content": "Thing Groups 为 IoT 设备提供分层组织，就像文件的文件夹一样。它们支持批量操作、策略继承以及按位置、功能或业务标准进行逻辑分组。组可以包含其他组，为大规模 IoT 部署创建灵活的组织结构。",
                "next": "我们将为设备组织创建 Thing Groups",
            },
            "things": {
                "title": "📚 学习要点: Things - 设备注册",
                "content": "Things 代表 AWS IoT Core 中的实际 IoT 设备。每个 Thing 都有唯一的名称、可选属性（如序列号、位置）并且可以分配给 Thing Type 以实现标准化。Things 是设备管理、安全策略和影子状态同步的基础。",
                "next": "我们将创建具有真实属性的单个 Things",
            },
            "relationships": {
                "title": "📚 学习要点: Thing-Group 关系",
                "content": "将 Things 添加到 Groups 会创建组织关系，支持批量操作和策略继承。Thing 可以属于多个组，组可以嵌套。这种层次结构对于大规模设备车队管理、策略应用和按业务逻辑组织设备至关重要。",
                "next": "我们将把 Things 分配到适当的 Groups",
            },
        },
    },
    "pt-BR": {
        "title": "🚀 Configuração de Dados de Exemplo AWS IoT",
        "separator": "=" * 32,
        "aws_config": "📍 Configuração AWS:",
        "account_id": "ID da Conta",
        "region": "Região",
        "aws_context_error": "⚠️ Não foi possível recuperar o contexto AWS:",
        "aws_credentials_reminder": "   Certifique-se de que as credenciais AWS estão configuradas",
        "description_intro": "Este script criará recursos IoT de exemplo para aprendizado:",
        "thing_types_desc": "Thing Types:",
        "thing_groups_desc": "Thing Groups:",
        "things_desc": "Things com atributos aleatórios",
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Mostrará solicitações e respostas detalhadas da API",
            "• Execução mais lenta com pausas estendidas",
            "• Detalhes completos de erros e rastreamentos",
        ],
        "tip": "💡 Dica: Use a flag --debug ou -d para ver chamadas detalhadas da API",
        "continue_prompt": "Continuar? (s/N): ",
        "setup_cancelled": "Configuração cancelada",
        "client_initialized": "✅ Cliente AWS IoT inicializado",
        "client_error": "❌ Erro ao inicializar cliente AWS IoT:",
        "credentials_reminder": "Certifique-se de ter credenciais e região AWS configuradas",
        "no_region_error": "❌ Região AWS não configurada",
        "region_setup_instructions": [
            "Por favor configure sua região AWS usando um destes métodos:",
            "1. Definir variável de ambiente: export AWS_DEFAULT_REGION=us-east-1",
            "2. Configurar AWS CLI: aws configure",
            "3. Definir região no arquivo de credenciais AWS",
        ],
        "invalid_credentials": "❌ Credenciais AWS inválidas",
        "credentials_check_failed": "❌ Variáveis de ambiente obrigatórias ausentes:",
        "credentials_instructions": [
            "Por favor exporte suas credenciais AWS:",
            "export AWS_ACCESS_KEY_ID=<sua-access-key>",
            "export AWS_SECRET_ACCESS_KEY=<sua-secret-key>",
            "export AWS_SESSION_TOKEN=<seu-session-token>  # Opcional para credenciais temporárias",
        ],
        "step_1_title": "Criando Thing Types",
        "step_2_title": "Criando Thing Groups",
        "step_3_title": "Criando {} Things com atributos",
        "step_4_title": "Adicionando Things aos Thing Groups",
        "step_5_title": "Resumo da Configuração",
        "creating": "Criando",
        "created": "Criado",
        "already_exists": "já existe, pulando",
        "deprecated_undeprecating": "está depreciado, removendo depreciação...",
        "undeprecated": "depreciação removida com sucesso",
        "already_active": "já existe e está ativo",
        "error_checking": "Erro verificando",
        "error_creating": "Erro criando",
        "creating_thing": "📱 Criando Thing:",
        "customer_id": "ID do Cliente:",
        "country": "País:",
        "manufacturing_date": "Data de Fabricação:",
        "thing_type": "Thing Type:",
        "adding_to_group": "Adicionando {} ao grupo {}",
        "added_to_group": "Adicionado {} a {}",
        "error_adding": "Erro adicionando {} a {}:",
        "resources_created": "📊 Recursos Criados:",
        "things": "Things:",
        "thing_types": "Thing Types:",
        "thing_groups": "Thing Groups:",
        "sample_thing_names": "🎯 Nomes de Things de Exemplo:",
        "and_more": "... e mais {}",
        "error_summary": "❌ Erro obtendo resumo:",
        "setup_complete": "🎉 Configuração completa! Agora você pode usar iot_registry_explorer.py para explorar os dados.",
        "debug_session_complete": "🔍 DEBUG: Sessão concluída com log detalhado da API",
        "setup_cancelled_user": "👋 Configuração cancelada pelo usuário. Tchau!",
        "debug_creating": "🔍 DEBUG: Criando",
        "debug_api_call": "📤 Chamada API:",
        "debug_input_params": "📥 Parâmetros de Entrada:",
        "debug_api_response": "📤 Resposta API:",
        "debug_full_error": "🔍 DEBUG: Resposta completa de erro:",
        "debug_full_traceback": "🔍 DEBUG: Rastreamento completo:",
        "api_error": "❌ Erro da API AWS em",
        "missing_param_error": "❌ Parâmetro obrigatório ausente em",
        "invalid_value_error": "❌ Valor inválido em",
        "unexpected_error": "❌ Erro inesperado em",
        "press_enter": "Pressione Enter para continuar...",
        "learning_moments": {
            "hierarchy": {
                "title": "📚 MOMENTO DE APRENDIZADO: Hierarquia de Recursos AWS IoT",
                "content": "AWS IoT usa uma estrutura hierárquica para organizar dispositivos: Thing Types (modelos) definem categorias de dispositivos, Thing Groups fornecem estrutura organizacional, e Things representam dispositivos reais. Esta hierarquia permite gerenciamento escalável de dispositivos, operações em lote e herança de políticas em sua frota IoT.",
                "next": "Criaremos recursos de exemplo para demonstrar esta hierarquia",
            },
            "thing_groups": {
                "title": "📚 MOMENTO DE APRENDIZADO: Thing Groups - Organização de Dispositivos",
                "content": "Thing Groups fornecem organização hierárquica para seus dispositivos IoT, similar a pastas para arquivos. Eles permitem operações em lote, herança de políticas e agrupamento lógico por localização, função ou critérios de negócio. Grupos podem conter outros grupos, criando estruturas organizacionais flexíveis para implantações IoT grandes.",
                "next": "Criaremos Thing Groups para organização de dispositivos",
            },
            "things": {
                "title": "📚 MOMENTO DE APRENDIZADO: Things - Registro de Dispositivos",
                "content": "Things representam seus dispositivos IoT reais no AWS IoT Core. Cada Thing tem um nome único, atributos opcionais (como número de série, localização), e pode ser atribuído a um Thing Type para padronização. Things são a base para gerenciamento de dispositivos, políticas de segurança e sincronização de estado shadow.",
                "next": "Criaremos Things individuais com atributos realistas",
            },
            "relationships": {
                "title": "📚 MOMENTO DE APRENDIZADO: Relacionamentos Thing-Group",
                "content": "Adicionar Things a Groups cria relacionamentos organizacionais que permitem operações em lote e herança de políticas. Um Thing pode pertencer a múltiplos grupos, e grupos podem ser aninhados. Esta hierarquia é essencial para gerenciar frotas de dispositivos em escala, aplicar políticas e organizar dispositivos por lógica de negócio.",
                "next": "Atribuiremos Things aos Groups apropriados",
            },
        },
    },
    "ko": {
        "title": "🚀 AWS IoT 샘플 데이터 설정",
        "separator": "=" * 32,
        "aws_config": "📍 AWS 구성:",
        "account_id": "계정 ID",
        "region": "리전",
        "aws_context_error": "⚠️ AWS 컨텍스트를 검색할 수 없습니다:",
        "aws_credentials_reminder": "   AWS 자격 증명이 구성되어 있는지 확인하세요",
        "description_intro": "이 스크립트는 학습을 위한 샘플 IoT 리소스를 생성합니다:",
        "thing_types_desc": "Thing Types:",
        "thing_groups_desc": "Thing Groups:",
        "things_desc": "무작위 속성을 가진 Things",
        "debug_enabled": "🔍 디버그 모드 활성화",
        "debug_features": [
            "• 상세한 API 요청 및 응답을 표시합니다",
            "• 확장된 일시 정지로 실행 속도가 느려집니다",
            "• 완전한 오류 세부 정보 및 추적",
        ],
        "tip": "💡 팁: --debug 또는 -d 플래그를 사용하여 상세한 API 호출을 확인하세요",
        "continue_prompt": "계속하시겠습니까? (y/N): ",
        "setup_cancelled": "설정이 취소되었습니다",
        "client_initialized": "✅ AWS IoT 클라이언트가 초기화되었습니다",
        "client_error": "❌ AWS IoT 클라이언트 초기화 오류:",
        "credentials_reminder": "AWS 자격 증명과 리전이 구성되어 있는지 확인하세요",
        "no_region_error": "❌ AWS 리전이 구성되지 않았습니다",
        "region_setup_instructions": [
            "다음 방법 중 하나를 사용하여 AWS 리전을 구성하세요:",
            "1. 환경 변수 설정: export AWS_DEFAULT_REGION=us-east-1",
            "2. AWS CLI 구성: aws configure",
            "3. AWS 자격 증명 파일에서 리전 설정",
        ],
        "invalid_credentials": "❌ 유효하지 않은 AWS 자격 증명",
        "credentials_check_failed": "❌ 필수 환경 변수가 누락되었습니다:",
        "credentials_instructions": [
            "AWS 자격 증명을 내보내세요:",
            "export AWS_ACCESS_KEY_ID=<your-access-key>",
            "export AWS_SECRET_ACCESS_KEY=<your-secret-key>",
            "export AWS_SESSION_TOKEN=<your-session-token>  # 임시 자격 증명의 경우 선택사항",
        ],
        "step_1_title": "Thing Types 생성 중",
        "step_2_title": "Thing Groups 생성 중",
        "step_3_title": "속성이 있는 {} Things 생성 중",
        "step_4_title": "Things를 Thing Groups에 추가 중",
        "step_5_title": "설정 요약",
        "creating": "생성 중",
        "created": "생성됨",
        "already_exists": "이미 존재하므로 건너뜁니다",
        "deprecated_undeprecating": "는 더 이상 사용되지 않습니다. 사용 중단을 해제하는 중...",
        "undeprecated": "사용 중단 해제가 성공했습니다",
        "already_active": "이미 존재하고 활성 상태입니다",
        "error_checking": "확인 오류",
        "error_creating": "생성 오류",
        "creating_thing": "📱 Thing 생성 중:",
        "customer_id": "고객 ID:",
        "country": "국가:",
        "manufacturing_date": "제조 날짜:",
        "thing_type": "Thing Type:",
        "adding_to_group": "{}를 그룹 {}에 추가 중",
        "added_to_group": "{}를 {}에 추가했습니다",
        "error_adding": "{}를 {}에 추가하는 중 오류:",
        "resources_created": "📊 생성된 리소스:",
        "things": "Things:",
        "thing_types": "Thing Types:",
        "thing_groups": "Thing Groups:",
        "sample_thing_names": "🎯 샘플 Thing 이름:",
        "and_more": "... 그리고 {} 개 더",
        "error_summary": "❌ 요약을 가져오는 중 오류:",
        "setup_complete": "🎉 설정 완료! 이제 iot_registry_explorer.py를 사용하여 데이터를 탐색할 수 있습니다.",
        "debug_session_complete": "🔍 디버그: 상세한 API 로깅으로 세션이 완료되었습니다",
        "setup_cancelled_user": "👋 사용자가 설정을 취소했습니다. 안녕히 가세요!",
        "debug_creating": "🔍 디버그: 생성 중",
        "debug_api_call": "📤 API 호출:",
        "debug_input_params": "📥 입력 매개변수:",
        "debug_api_response": "📤 API 응답:",
        "debug_full_error": "🔍 디버그: 전체 오류 응답:",
        "debug_full_traceback": "🔍 디버그: 전체 추적:",
        "api_error": "❌ AWS API 오류",
        "missing_param_error": "❌ 필수 매개변수 누락",
        "invalid_value_error": "❌ 유효하지 않은 값",
        "unexpected_error": "❌ 예상치 못한 오류",
        "press_enter": "계속하려면 Enter를 누르세요...",
        "learning_moments": {
            "hierarchy": {
                "title": "📚 학습 포인트: AWS IoT 리소스 계층 구조",
                "content": "AWS IoT는 디바이스를 구성하기 위해 계층 구조를 사용합니다: Thing Types(템플릿)는 디바이스 카테고리를 정의하고, Thing Groups는 조직 구조를 제공하며, Things는 실제 디바이스를 나타냅니다. 이 계층 구조는 확장 가능한 디바이스 관리, 대량 작업 및 IoT 플릿 전체의 정책 상속을 가능하게 합니다.",
                "next": "이 계층 구조를 보여주기 위해 샘플 리소스를 생성하겠습니다",
            },
            "thing_groups": {
                "title": "📚 학습 포인트: Thing Groups - 디바이스 조직",
                "content": "Thing Groups는 파일의 폴더와 유사하게 IoT 디바이스에 대한 계층적 조직을 제공합니다. 위치, 기능 또는 비즈니스 기준에 따른 대량 작업, 정책 상속 및 논리적 그룹화를 가능하게 합니다. 그룹은 다른 그룹을 포함할 수 있어 대규모 IoT 배포를 위한 유연한 조직 구조를 만듭니다.",
                "next": "디바이스 조직을 위한 Thing Groups를 생성하겠습니다",
            },
            "things": {
                "title": "📚 학습 포인트: Things - 디바이스 등록",
                "content": "Things는 AWS IoT Core에서 실제 IoT 디바이스를 나타냅니다. 각 Thing은 고유한 이름, 선택적 속성(일련 번호, 위치 등)을 가지며 표준화를 위해 Thing Type에 할당될 수 있습니다. Things는 디바이스 관리, 보안 정책 및 섀도우 상태 동기화의 기초입니다.",
                "next": "현실적인 속성을 가진 개별 Things를 생성하겠습니다",
            },
            "relationships": {
                "title": "📚 학습 포인트: Thing-Group 관계",
                "content": "Things를 Groups에 추가하면 대량 작업과 정책 상속을 가능하게 하는 조직적 관계가 생성됩니다. Thing은 여러 그룹에 속할 수 있고, 그룹은 중첩될 수 있습니다. 이 계층 구조는 규모에 맞는 디바이스 플릿 관리, 정책 적용 및 비즈니스 로직에 따른 디바이스 조직화에 필수적입니다.",
                "next": "적절한 Groups에 Things를 할당하겠습니다",
            },
        },
    },
}

# Global variable for user's language preference
USER_LANG = "en"

# Configuration
THING_COUNT = 20
THING_TYPES = ["SedanVehicle", "SUVVehicle", "TruckVehicle"]
THING_GROUPS = ["CustomerFleet", "TestFleet", "MaintenanceFleet", "DealerFleet"]
COUNTRIES = ["US", "DE", "JP", "CA", "BR", "GB", "FR", "AU", "IN", "MX"]


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
    elif env_lang in ["pt", "pt-br", "portuguese", "português"]:
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


def get_message(key, lang="en"):
    """Get localized message"""
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


def check_credentials():
    """Validate AWS credentials are available"""
    required_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(get_message("credentials_check_failed", USER_LANG))
        for var in missing_vars:
            print(f"   - {var}")
        print()
        for instruction in get_message("credentials_instructions", USER_LANG):
            print(instruction)
        print()
        sys.exit(1)


def print_step(step, description):
    """Print setup step with formatting"""
    print(f"\n🔧 Step {step}: {description}")
    print("-" * 50)


def safe_create(func, resource_type, name, debug=False, **kwargs):
    """Safely create resource with error handling and optional debug info"""
    try:
        if debug:
            print(f"\n{get_message('debug_creating', USER_LANG)} {resource_type}: {name}")
            print(f"{get_message('debug_api_call', USER_LANG)} {func.__name__}")
            print(get_message("debug_input_params", USER_LANG))
            print(json.dumps(kwargs, indent=2, default=str))
        else:
            print(f"{get_message('creating', USER_LANG)} {resource_type}: {name}")

        response = func(**kwargs)

        if debug:
            print(get_message("debug_api_response", USER_LANG))
            print(json.dumps(response, indent=2, default=str))

        print(f"✅ {get_message('created', USER_LANG)} {resource_type}: {name}")
        time.sleep(0.5 if not debug else 1.0)  # nosemgrep: arbitrary-sleep
        return response
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceAlreadyExistsException":
            print(f"⚠️  {resource_type} {name} {get_message('already_exists', USER_LANG)}")
        else:
            print(f"❌ {get_message('error_creating', USER_LANG)} {resource_type} {name}: {e.response['Error']['Message']}")
            if debug:
                print(get_message("debug_full_error", USER_LANG))
                print(json.dumps(e.response, indent=2, default=str))
        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if debug:
            print(get_message("debug_full_traceback", USER_LANG))
            traceback.print_exc()
        time.sleep(0.5)  # nosemgrep: arbitrary-sleep


def create_thing_types(iot, debug=False):
    """Create predefined Thing Types"""
    print_step(1, get_message("step_1_title", USER_LANG))

    for thing_type in THING_TYPES:
        # Check if Thing Type already exists
        try:
            response = iot.describe_thing_type(thingTypeName=thing_type)
            if response.get("thingTypeMetadata", {}).get("deprecated"):
                print(f"   ⚠️ Thing Type {thing_type} {get_message('deprecated_undeprecating', USER_LANG)}")
                iot.deprecate_thing_type(thingTypeName=thing_type, undoDeprecate=True)
                print(f"   ✅ Thing Type {thing_type} {get_message('undeprecated', USER_LANG)}")
            else:
                print(f"   ℹ️ Thing Type {thing_type} {get_message('already_active', USER_LANG)}")
            continue
        except iot.exceptions.ResourceNotFoundException:
            # Thing Type doesn't exist, create it
            pass
        except Exception as e:
            print(f"   ❌ {get_message('error_checking', USER_LANG)} Thing Type {thing_type}: {str(e)}")
            continue

        description = f"Template for {thing_type.replace('Vehicle', ' Vehicle')} category"
        safe_create(
            iot.create_thing_type,
            "Thing Type",
            thing_type,
            debug=debug,
            thingTypeName=thing_type,
            thingTypeProperties={
                "thingTypeDescription": description,
                "searchableAttributes": ["customerId", "country", "manufacturingDate"],
            },
        )


def create_thing_groups(iot, debug=False):
    """Create predefined Thing Groups"""
    print_step(2, get_message("step_2_title", USER_LANG))

    for group in THING_GROUPS:
        description = f"Group for devices in {group.replace('Floor', ' Floor')}"
        safe_create(
            iot.create_thing_group,
            "Thing Group",
            group,
            debug=debug,
            thingGroupName=group,
            thingGroupProperties={
                "thingGroupDescription": description,
                "attributePayload": {"attributes": {"location": group, "managed": "true"}},
            },
        )


def generate_random_date():
    """Generate random date within last year"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    random_date = start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))
    return random_date.strftime("%Y-%m-%d")


def create_things(iot, debug=False):
    """Create sample Things with attributes"""
    print_step(3, get_message("step_3_title", USER_LANG).format(THING_COUNT))

    for i in range(1, THING_COUNT + 1):
        thing_name = f"Vehicle-VIN-{i:03d}"
        customer_id = str(uuid.uuid4())
        country = random.choice(COUNTRIES)
        manufacturing_date = generate_random_date()
        thing_type = random.choice(THING_TYPES)

        if not debug:
            print(f"\n{get_message('creating_thing', USER_LANG)} {thing_name}")
            print(f"   {get_message('customer_id', USER_LANG)} {customer_id}")
            print(f"   {get_message('country', USER_LANG)} {country}")
            print(f"   {get_message('manufacturing_date', USER_LANG)} {manufacturing_date}")
            print(f"   {get_message('thing_type', USER_LANG)} {thing_type}")
            time.sleep(0.8)  # nosemgrep: arbitrary-sleep

        safe_create(
            iot.create_thing,
            "Thing",
            thing_name,
            debug=debug,
            thingName=thing_name,
            thingTypeName=thing_type,
            attributePayload={
                "attributes": {"customerId": customer_id, "country": country, "manufacturingDate": manufacturing_date}
            },
        )


def add_things_to_groups(iot, debug=False):
    """Add Things to random Thing Groups"""
    print_step(4, get_message("step_4_title", USER_LANG))

    for i in range(1, THING_COUNT + 1):
        thing_name = f"Vehicle-VIN-{i:03d}"
        group_name = random.choice(THING_GROUPS)

        try:
            if debug:
                print(f"\n🔍 DEBUG: {get_message('adding_to_group', USER_LANG).format(thing_name, group_name)}")
                print(f"{get_message('debug_api_call', USER_LANG)} add_thing_to_thing_group")
                print(get_message("debug_input_params", USER_LANG))
                print(json.dumps({"thingGroupName": group_name, "thingName": thing_name}, indent=2))
            else:
                print(get_message("adding_to_group", USER_LANG).format(thing_name, group_name))

            response = iot.add_thing_to_thing_group(thingGroupName=group_name, thingName=thing_name)

            if debug:
                print(get_message("debug_api_response", USER_LANG))
                print(json.dumps(response, indent=2, default=str))

            print(f"✅ {get_message('added_to_group', USER_LANG).format(thing_name, group_name)}")
            time.sleep(0.3 if not debug else 1.0)  # nosemgrep: arbitrary-sleep
        except ClientError as e:
            print(
                f"❌ {get_message('error_adding', USER_LANG).format(thing_name, group_name)} {e.response['Error']['Message']}"
            )
            if debug:
                print(get_message("debug_full_error", USER_LANG))
                print(json.dumps(e.response, indent=2, default=str))
            time.sleep(0.3)  # nosemgrep: arbitrary-sleep


def print_summary(iot):
    """Print summary of created resources"""
    print_step(5, get_message("step_5_title", USER_LANG))

    try:
        things = iot.list_things()
        thing_types = iot.list_thing_types()
        thing_groups = iot.list_thing_groups()

        print(get_message("resources_created", USER_LANG))
        print(f"   {get_message('things', USER_LANG)} {len(things.get('things', []))}")
        print(f"   {get_message('thing_types', USER_LANG)} {len(thing_types.get('thingTypes', []))}")
        print(f"   {get_message('thing_groups', USER_LANG)} {len(thing_groups.get('thingGroups', []))}")

        print(f"\n{get_message('sample_thing_names', USER_LANG)}")
        for thing in things.get("things", [])[:5]:
            print(f"   - {thing['thingName']}")
        if len(things.get("things", [])) > 5:
            print(f"   {get_message('and_more', USER_LANG).format(len(things.get('things', [])) - 5)}")

    except Exception as e:
        print(f"{get_message('error_summary', USER_LANG)} {str(e)}")


def main():

    try:
        # Get user's preferred language
        global USER_LANG
        USER_LANG = get_language()

        # Check for debug flag
        debug_mode = "--debug" in sys.argv or "-d" in sys.argv

        print(get_message("title", USER_LANG))
        print(get_message("separator", USER_LANG))

        # Check credentials first - exit immediately if missing
        check_credentials()

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

        print(get_message("description_intro", USER_LANG))
        print(f"• {len(THING_TYPES)} {get_message('thing_types_desc', USER_LANG)} {', '.join(THING_TYPES)}")
        print(f"• {len(THING_GROUPS)} {get_message('thing_groups_desc', USER_LANG)} {', '.join(THING_GROUPS)}")
        print(f"• {THING_COUNT} {get_message('things_desc', USER_LANG)}")

        if debug_mode:
            print(f"\n{get_message('debug_enabled', USER_LANG)}")
            for feature in get_message("debug_features", USER_LANG):
                print(feature)
        else:
            print(f"\n{get_message('tip', USER_LANG)}")

        print(get_message("separator", USER_LANG))

        confirm = input(get_message("continue_prompt", USER_LANG)).strip().lower()
        if confirm not in ["y", "s"]:  # Accept 'y' (yes), 's' (sí/sim) for Spanish/Portuguese
            print(get_message("setup_cancelled", USER_LANG))
            return

        try:
            iot = boto3.client("iot")
            print(get_message("client_initialized", USER_LANG))

            if debug_mode:
                print("🔍 DEBUG: Client configuration:")
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
        except Exception as e:
            print(f"{get_message('client_error', USER_LANG)} {str(e)}")
            print(get_message("credentials_reminder", USER_LANG))
            return

        print_learning_moment("hierarchy", USER_LANG)
        input(get_message("press_enter", USER_LANG))

        # Execute setup steps with debug flag
        create_thing_types(iot, debug=debug_mode)

        print_learning_moment("thing_groups", USER_LANG)
        input(get_message("press_enter", USER_LANG))

        create_thing_groups(iot, debug=debug_mode)

        print_learning_moment("things", USER_LANG)
        input(get_message("press_enter", USER_LANG))

        create_things(iot, debug=debug_mode)

        print_learning_moment("relationships", USER_LANG)
        input(get_message("press_enter", USER_LANG))

        add_things_to_groups(iot, debug=debug_mode)
        print_summary(iot)

        print(f"\n{get_message('setup_complete', USER_LANG)}")

        if debug_mode:
            print(f"\n{get_message('debug_session_complete', USER_LANG)}")

    except KeyboardInterrupt:
        print(f"\n\n{get_message('setup_cancelled_user', USER_LANG)}")


if __name__ == "__main__":
    main()

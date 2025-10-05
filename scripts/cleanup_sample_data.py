#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import shutil
import sys
import time
import traceback

import boto3
from botocore.exceptions import ClientError

# Sample data patterns created by setup scripts
SAMPLE_THING_TYPES = ["SedanVehicle", "SUVVehicle", "TruckVehicle"]
SAMPLE_THING_GROUPS = ["CustomerFleet", "TestFleet", "MaintenanceFleet", "DealerFleet"]
SAMPLE_THING_PREFIX = "Vehicle-VIN-"  # Things created as Vehicle-VIN-001, Vehicle-VIN-002, etc.

# Simple translation system for learning content
MESSAGES = {
    "en": {
        "title": "🧹 AWS IoT Sample Data Cleanup",
        "separator": "=" * 50,
        "aws_config": "📍 AWS Configuration:",
        "account_id": "Account ID",
        "region": "Region",
        "aws_context_error": "⚠️ Could not retrieve AWS context:",
        "aws_credentials_reminder": "   Make sure AWS credentials are configured",
        "description_intro": "This script will clean up ONLY the sample resources created by:",
        "setup_scripts": ["• setup_sample_data.py", "• certificate_manager.py"],
        "no_affect_other": "It will NOT affect other IoT resources in your account.",
        "debug_enabled": "🔍 DEBUG MODE ENABLED",
        "debug_features": [
            "• Will show detailed API requests and responses",
            "• Includes complete error details and tracebacks",
            "• Educational API call documentation",
        ],
        "tip": "💡 Tip: Use --debug or -d flag to see detailed API calls",
        "resources_to_cleanup": "🎯 Resources to be cleaned up:",
        "things_prefix": "• Things starting with '{}' (Vehicle-VIN-001, Vehicle-VIN-002, etc.)",
        "thing_types": "• Thing Types: {} (will be deprecated first)",
        "thing_groups": "• Thing Groups: {}",
        "certificates_attached": "• Certificates attached to sample Things",
        "local_cert_files": "• Local certificate files in ./certificates/",
        "policies_manual_review": "• Policies will be listed for manual review",
        "continue_cleanup": "Continue with cleanup? (y/N): ",
        "cleanup_cancelled": "Cleanup cancelled",
        "client_initialized": "✅ AWS IoT client initialized",
        "debug_client_config": "🔍 DEBUG: Client configuration:",
        "service_label": "Service",
        "api_version_label": "API Version",
        "learning_moment_title": "📚 LEARNING MOMENT: Resource Cleanup & Lifecycle Management",
        "learning_moment_content": "Proper resource cleanup is essential in IoT deployments to avoid unnecessary costs and maintain security. AWS IoT resources have dependencies - certificates must be detached before deletion, Thing Types must be deprecated before removal, and policies should be carefully reviewed since they may be shared across devices.",
        "next_cleanup": "🔄 NEXT: We will safely clean up sample resources in the correct order",
        "press_enter_continue": "Press Enter to continue...",
        "step1_title": "🗑️  Step 1: Cleaning up sample Things and certificates...",
        "step_separator": "-" * 50,
        "listing_things": "🔍 Listing all Things to find sample Things",
        "found_sample_things": "📋 Found {} sample Things to clean up",
        "processing_thing": "📱 Processing Thing: {}",
        "listing_principals": "🔍 Listing principals (certificates) for Thing: {}",
        "found_certificates": "🔐 Found {} certificate(s) attached to {}",
        "deleting_thing": "🗑️  Deleting Thing: {}",
        "step2_title": "🔐 Step 2: Checking for orphaned certificates...",
        "listing_certificates": "🔍 Listing all certificates to check for orphaned ones",
        "found_certificates_account": "📋 Found {} certificate(s) in account",
        "certificate_info": "ℹ️  Certificate: {} (Status: {})",
        "checking_certificate_things": "🔍 Checking if certificate {} is attached to any Things",
        "cert_attached_sample_things": "⚠️  Certificate {} was attached to sample Things: {}",
        "cert_should_cleanup_step1": "   This certificate should have been cleaned up in Step 1",
        "cert_not_attached_sample": "✅ Certificate {} is not attached to sample Things",
        "could_not_check_things": "⚠️  Could not check Things for certificate {}: {}",
        "step3_title": "📄 Step 3: Cleaning up sample policies...",
        "listing_policies": "🔍 Listing all policies to check for cleanup",
        "found_policies_account": "📋 Found {} policies in account",
        "checking_policy": "📄 Checking policy: {}",
        "checking_policy_targets": "🔍 Checking targets for policy: {}",
        "policy_attached_targets": "   ⚠️  Policy {} is attached to {} target(s), skipping",
        "deleting_unattached_policy": "   🗑️  Deleting unattached policy: {}",
        "error_checking_policy": "   ❌ Error checking policy {}: {}",
        "policy_no_sample_patterns": "   ℹ️  Policy {} doesn't match sample patterns, skipping",
        "policy_cleanup_summary": "📊 Policy cleanup summary:",
        "deleted_policies": "   ✅ Deleted: {} policies",
        "skipped_policies": "   ⚠️  Skipped: {} policies (still attached to resources)",
        "certificate_cleanup_summary": "📊 Certificate cleanup summary:",
        "cleaned_certificates": "   ✅ Cleaned: {} certificates",
        "skipped_certificates": "   ⚠️  Skipped: {} certificates",
        "skipped_certs_production": "💡 Skipped certificates appear to be production certificates or have unclear usage patterns",
        "manual_cert_deletion": "   If you're sure they're from learning, you can manually delete them from the AWS console",
        "skipped_policies_note": "💡 Skipped policies are still attached to certificates or other resources",
        "policies_cleanup_auto": "   They will be cleaned up automatically when certificates are deleted",
        "policies_manual_cleanup": "   Or you can manually detach and delete them if needed",
        "step4_title": "📁 Step 4: Cleaning up sample Thing Groups...",
        "listing_thing_groups": "🔍 Listing all Thing Groups to find sample groups",
        "found_sample_groups": "📋 Found {} sample Thing Groups to clean up",
        "deleting_thing_group": "📁 Deleting Thing Group: {}",
        "step5_title": "🏷️  Step 5: Cleaning up sample Thing Types...",
        "listing_thing_types": "🔍 Listing all Thing Types to find sample types",
        "found_sample_types": "📋 Found {} sample Thing Types to clean up",
        "no_sample_types": "ℹ️  No sample Thing Types found to clean up",
        "thing_type_deprecated": "ℹ️  Thing Type {} is already deprecated (since {})",
        "thing_type_active": "ℹ️  Thing Type {} is active (needs deprecation)",
        "could_not_check_status": "⚠️  Could not check status of {}: {}",
        "deprecating_active_types": "⚠️  Deprecating {} active Thing Types...",
        "deprecating_thing_type": "🏷️  Deprecating Thing Type: {}",
        "thing_type_deprecated_success": "✅ Thing Type {} deprecated",
        "could_not_deprecate": "❌ Could not deprecate Thing Type {}",
        "aws_constraint_5min": "⏰ AWS IoT Constraint: Thing Types must wait 5 minutes after deprecation before deletion",
        "thing_types_to_delete": "📋 Thing Types to delete:",
        "deprecated_item": "   • {} (deprecated: {})",
        "deletion_options": "🎯 Deletion Options:",
        "wait_5min_delete": "1. Wait 5 minutes now and delete automatically",
        "skip_deletion": "2. Skip deletion (run cleanup again later)",
        "try_deletion_now": "3. Try deletion now (may fail if not enough time has passed)",
        "select_option_1_3": "Select option (1-3): ",
        "waiting_5min": "⏳ Waiting 5 minutes for AWS IoT constraint...",
        "constraint_explanation": "💡 This is required by AWS IoT - Thing Types cannot be deleted immediately after deprecation",
        "time_remaining": "⏰ Time remaining: {:02d}:{:02d} - You can cancel with Ctrl+C",
        "wait_completed": "✅ 5-minute wait period completed!",
        "skipping_deletion": "⏭️  Skipping Thing Type deletion",
        "deletion_tip": "💡 To delete later, run: python cleanup_sample_data.py",
        "types_ready_deletion": "   The Thing Types are already deprecated and will be ready for deletion",
        "attempting_deletion_now": "🚀 Attempting deletion now (may fail due to timing constraint)",
        "invalid_choice_1_3": "❌ Invalid choice. Please enter 1, 2, or 3",
        "deleting_deprecated_types": "🗑️  Deleting deprecated Thing Types...",
        "attempting_delete_type": "🗑️  Attempting to delete Thing Type: {}",
        "deletion_failed_timing": "💡 If deletion failed due to timing, wait a few more minutes and try again",
        "type_ready_deletion": "   The Thing Type {} is deprecated and ready for deletion",
        "cleanup_interrupted": "🛑 Cleanup interrupted by user",
        "types_deprecated_delete_later": "💡 Thing Types that were deprecated can be deleted later by running cleanup again",
        "step6_title": "🌙 Step 6: Device shadows cleanup...",
        "shadows_auto_cleanup": "ℹ️  Device shadows are automatically cleaned up when Things are deleted",
        "no_manual_shadow_cleanup": "   No manual shadow deletion required - AWS IoT handles this automatically",
        "debug_shadow_skipped": "🔍 DEBUG: Shadow cleanup skipped - handled by Thing deletion",
        "shadow_cleanup_completed": "✅ Shadow cleanup completed (automatic)",
        "step7_title": "📋 Step 7: Cleaning up sample IoT rules...",
        "debug_listing_rules": "🔍 DEBUG: Listing all IoT rules",
        "debug_deleting_rule": "🔍 DEBUG: Deleting rule: {}",
        "deleted_rule": "   ✅ Deleted rule: {}",
        "error_deleting_rule": "   ❌ Error deleting rule {}: {}",
        "no_sample_rules": "   ℹ️ No sample rules found to delete",
        "rules_cleanup_summary": "📊 Rules cleanup summary: {} rules deleted",
        "step8_title": "💾 Step 8: Cleaning up local certificate files...",
        "checking_cert_directory": "🔍 Checking for local certificates directory: {}",
        "cert_directory_contents": "📁 Contents of certificates directory:",
        "removed_cert_directory": "✅ Removed local certificates directory: {}",
        "directory_deleted_success": "🔍 Directory {} successfully deleted",
        "error_removing_cert_dir": "❌ Error removing certificates directory: {}",
        "no_cert_directory": "ℹ️  No local certificates directory found",
        "directory_not_exist": "🔍 Directory {} does not exist",
        "checking_sample_cert_dir": "🔍 Checking for sample certificates directory: {}",
        "sample_cert_contents": "📁 Contents of sample-certs directory:",
        "removed_sample_cert_dir": "✅ Removed sample certificates directory: {}",
        "error_removing_sample_dir": "❌ Error removing sample-certs directory: {}",
        "no_sample_cert_dir": "ℹ️  No sample certificates directory found",
        "cleanup_summary_title": "🎉 Cleanup Summary",
        "summary_separator": "=" * 50,
        "things_cleaned": "✅ Sample Things cleaned up (Vehicle-VIN-001, Vehicle-VIN-002, etc.)",
        "certificates_cleaned": "✅ Associated certificates cleaned up",
        "groups_cleaned": "✅ Sample Thing Groups cleaned up",
        "types_cleaned": "✅ Sample Thing Types cleaned up",
        "local_files_cleaned": "✅ Local certificate files cleaned up (certificates/ and sample-certs/)",
        "device_state_cleaned": "✅ Device state files cleaned up (device_state.json files)",
        "account_clean": "💡 Your AWS IoT account now only contains non-sample resources",
        "error_generic": "❌ Error: {}",
        "debug_cleanup_completed": "🔍 DEBUG: Cleanup session completed with detailed API logging",
        "api_call_header": "🔍 API Call: {}",
        "api_description": "📖 Description: {}",
        "api_input_params": "📥 Input Parameters:",
        "api_no_params": "📥 Input Parameters: None",
        "api_response": "📤 API Response:",
        "api_empty_response": "Empty response (operation completed successfully)",
        "deleting_resource": "Deleting {}: {}",
        "deleted_resource": "✅ Deleted {}: {}",
        "resource_not_found": "⚠️  {} {} not found, skipping",
        "error_deleting_resource": "❌ Error deleting {} {}: {}",
        "debug_full_error": "🔍 DEBUG: Full error response:",
        "debug_full_traceback": "🔍 DEBUG: Full traceback:",
        "cleaning_certificate": "🔐 Cleaning up certificate: {}",
        "step1_list_policies": "🔍 Step 1: Listing policies attached to certificate",
        "found_attached_policies": "📋 Found {} attached policies",
        "detaching_policy": "🔗 Detaching policy: {}",
        "detaching_cert_from_thing": "🔗 Detaching certificate from Thing: {}",
        "deactivating_certificate": "⏸️  Deactivating certificate: {}",
        "certificate_deactivated": "✅ Certificate {} deactivated",
        "deleting_certificate": "🗑️  Deleting certificate: {}",
        "error_cleaning_certificate": "❌ Error cleaning up certificate {}: {}",
    },
    "es": {
        "title": "🧹 Limpieza de Datos de Muestra de AWS IoT",
        "separator": "=" * 50,
        "aws_config": "📍 Configuración de AWS:",
        "account_id": "ID de Cuenta",
        "region": "Región",
        "aws_context_error": "⚠️ No se pudo obtener el contexto de AWS:",
        "aws_credentials_reminder": "   Asegúrate de que las credenciales de AWS estén configuradas",
        "description_intro": "Este script limpiará ÚNICAMENTE los recursos de muestra creados por:",
        "setup_scripts": ["• setup_sample_data.py", "• certificate_manager.py"],
        "no_affect_other": "NO afectará otros recursos de IoT en tu cuenta.",
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Mostrará solicitudes y respuestas detalladas de la API",
            "• Incluye detalles completos de errores y trazas",
            "• Documentación educativa de llamadas a la API",
        ],
        "tip": "💡 Consejo: Usa la bandera --debug o -d para ver llamadas detalladas a la API",
        "resources_to_cleanup": "🎯 Recursos a limpiar:",
        "things_prefix": "• Things que comienzan con '{}' (Vehicle-VIN-001, Vehicle-VIN-002, etc.)",
        "thing_types": "• Tipos de Thing: {} (serán deprecados primero)",
        "thing_groups": "• Grupos de Thing: {}",
        "certificates_attached": "• Certificados adjuntos a Things de muestra",
        "local_cert_files": "• Archivos de certificados locales en ./certificates/",
        "policies_manual_review": "• Las políticas serán listadas para revisión manual",
        "continue_cleanup": "¿Continuar con la limpieza? (y/N): ",
        "cleanup_cancelled": "Limpieza cancelada",
        "client_initialized": "✅ Cliente de AWS IoT inicializado",
        "debug_client_config": "🔍 DEBUG: Configuración del cliente:",
        "service_label": "Servicio",
        "api_version_label": "Versión de API",
        "learning_moment_title": "📚 MOMENTO DE APRENDIZAJE: Limpieza de Recursos y Gestión del Ciclo de Vida",
        "learning_moment_content": "La limpieza adecuada de recursos es esencial en despliegues de IoT para evitar costos innecesarios y mantener la seguridad. Los recursos de AWS IoT tienen dependencias: los certificados deben desvincularse antes de la eliminación, los Tipos de Thing deben deprecarse antes de la eliminación, y las políticas deben revisarse cuidadosamente ya que pueden compartirse entre dispositivos.",
        "next_cleanup": "🔄 SIGUIENTE: Limpiaremos de forma segura los recursos de muestra en el orden correcto",
        "press_enter_continue": "Presiona Enter para continuar...",
        "step1_title": "🗑️  Paso 1: Limpiando Things de muestra y certificados...",
        "step_separator": "-" * 50,
        "listing_things": "🔍 Listando todos los Things para encontrar Things de muestra",
        "found_sample_things": "📋 Se encontraron {} Things de muestra para limpiar",
        "processing_thing": "📱 Procesando Thing: {}",
        "listing_principals": "🔍 Listando principales (certificados) para Thing: {}",
        "found_certificates": "🔐 Se encontraron {} certificado(s) adjunto(s) a {}",
        "deleting_thing": "🗑️  Eliminando Thing: {}",
        "step2_title": "🔐 Paso 2: Verificando certificados huérfanos...",
        "listing_certificates": "🔍 Listando todos los certificados para verificar huérfanos",
        "found_certificates_account": "📋 Se encontraron {} certificado(s) en la cuenta",
        "certificate_info": "ℹ️  Certificado: {} (Estado: {})",
        "checking_certificate_things": "🔍 Verificando si el certificado {} está adjunto a algún Thing",
        "cert_attached_sample_things": "⚠️  El certificado {} estaba adjunto a Things de muestra: {}",
        "cert_should_cleanup_step1": "   Este certificado debería haberse limpiado en el Paso 1",
        "cert_not_attached_sample": "✅ El certificado {} no está adjunto a Things de muestra",
        "could_not_check_things": "⚠️  No se pudieron verificar Things para el certificado {}: {}",
        "step3_title": "📄 Paso 3: Limpiando políticas de muestra...",
        "listing_policies": "🔍 Listando todas las políticas para verificar limpieza",
        "found_policies_account": "📋 Se encontraron {} políticas en la cuenta",
        "checking_policy": "📄 Verificando política: {}",
        "checking_policy_targets": "🔍 Verificando objetivos para la política: {}",
        "policy_attached_targets": "   ⚠️  La política {} está adjunta a {} objetivo(s), omitiendo",
        "deleting_unattached_policy": "   🗑️  Eliminando política no adjunta: {}",
        "error_checking_policy": "   ❌ Error verificando política {}: {}",
        "policy_no_sample_patterns": "   ℹ️  La política {} no coincide con patrones de muestra, omitiendo",
        "policy_cleanup_summary": "📊 Resumen de limpieza de políticas:",
        "deleted_policies": "   ✅ Eliminadas: {} políticas",
        "skipped_policies": "   ⚠️  Omitidas: {} políticas (aún adjuntas a recursos)",
        "certificate_cleanup_summary": "📊 Resumen de limpieza de certificados:",
        "cleaned_certificates": "   ✅ Limpiados: {} certificados",
        "skipped_certificates": "   ⚠️  Omitidos: {} certificados",
        "skipped_certs_production": "💡 Los certificados omitidos parecen ser certificados de producción o tienen patrones de uso poco claros",
        "manual_cert_deletion": "   Si estás seguro de que son del aprendizaje, puedes eliminarlos manualmente desde la consola de AWS",
        "skipped_policies_note": "💡 Las políticas omitidas aún están adjuntas a certificados u otros recursos",
        "policies_cleanup_auto": "   Se limpiarán automáticamente cuando se eliminen los certificados",
        "policies_manual_cleanup": "   O puedes desvincularias y eliminarlas manualmente si es necesario",
        "step4_title": "📁 Paso 4: Limpiando Grupos de Thing de muestra...",
        "listing_thing_groups": "🔍 Listando todos los Grupos de Thing para encontrar grupos de muestra",
        "found_sample_groups": "📋 Se encontraron {} Grupos de Thing de muestra para limpiar",
        "deleting_thing_group": "📁 Eliminando Grupo de Thing: {}",
        "step5_title": "🏷️  Paso 5: Limpiando Tipos de Thing de muestra...",
        "listing_thing_types": "🔍 Listando todos los Tipos de Thing para encontrar tipos de muestra",
        "found_sample_types": "📋 Se encontraron {} Tipos de Thing de muestra para limpiar",
        "no_sample_types": "ℹ️  No se encontraron Tipos de Thing de muestra para limpiar",
        "thing_type_deprecated": "ℹ️  El Tipo de Thing {} ya está deprecado (desde {})",
        "thing_type_active": "ℹ️  El Tipo de Thing {} está activo (necesita deprecación)",
        "could_not_check_status": "⚠️  No se pudo verificar el estado de {}: {}",
        "deprecating_active_types": "⚠️  Deprecando {} Tipos de Thing activos...",
        "deprecating_thing_type": "🏷️  Deprecando Tipo de Thing: {}",
        "thing_type_deprecated_success": "✅ Tipo de Thing {} deprecado",
        "could_not_deprecate": "❌ No se pudo deprecar el Tipo de Thing {}",
        "aws_constraint_5min": "⏰ Restricción de AWS IoT: Los Tipos de Thing deben esperar 5 minutos después de la deprecación antes de la eliminación",
        "thing_types_to_delete": "📋 Tipos de Thing a eliminar:",
        "deprecated_item": "   • {} (deprecado: {})",
        "deletion_options": "🎯 Opciones de Eliminación:",
        "wait_5min_delete": "1. Esperar 5 minutos ahora y eliminar automáticamente",
        "skip_deletion": "2. Omitir eliminación (ejecutar limpieza nuevamente más tarde)",
        "try_deletion_now": "3. Intentar eliminación ahora (puede fallar si no ha pasado suficiente tiempo)",
        "select_option_1_3": "Seleccionar opción (1-3): ",
        "waiting_5min": "⏳ Esperando 5 minutos por la restricción de AWS IoT...",
        "constraint_explanation": "💡 Esto es requerido por AWS IoT - Los Tipos de Thing no pueden eliminarse inmediatamente después de la deprecación",
        "time_remaining": "⏰ Tiempo restante: {:02d}:{:02d} - Puedes cancelar con Ctrl+C",
        "wait_completed": "✅ ¡Período de espera de 5 minutos completado!",
        "skipping_deletion": "⏭️  Omitiendo eliminación de Tipos de Thing",
        "deletion_tip": "💡 Para eliminar más tarde, ejecuta: python cleanup_sample_data.py",
        "types_ready_deletion": "   Los Tipos de Thing ya están deprecados y estarán listos para eliminación",
        "attempting_deletion_now": "🚀 Intentando eliminación ahora (puede fallar debido a restricción de tiempo)",
        "invalid_choice_1_3": "❌ Opción inválida. Por favor ingresa 1, 2, o 3",
        "deleting_deprecated_types": "🗑️  Eliminando Tipos de Thing deprecados...",
        "attempting_delete_type": "🗑️  Intentando eliminar Tipo de Thing: {}",
        "deletion_failed_timing": "💡 Si la eliminación falló debido al tiempo, espera unos minutos más e intenta nuevamente",
        "type_ready_deletion": "   El Tipo de Thing {} está deprecado y listo para eliminación",
        "cleanup_interrupted": "🛑 Limpieza interrumpida por el usuario",
        "types_deprecated_delete_later": "💡 Los Tipos de Thing que fueron deprecados pueden eliminarse más tarde ejecutando la limpieza nuevamente",
        "step6_title": "🌙 Paso 6: Limpieza de sombras de dispositivos...",
        "shadows_auto_cleanup": "ℹ️  Las sombras de dispositivos se limpian automáticamente cuando se eliminan los Things",
        "no_manual_shadow_cleanup": "   No se requiere eliminación manual de sombras - AWS IoT maneja esto automáticamente",
        "debug_shadow_skipped": "🔍 DEBUG: Limpieza de sombras omitida - manejada por eliminación de Thing",
        "shadow_cleanup_completed": "✅ Limpieza de sombras completada (automática)",
        "step7_title": "📋 Paso 7: Limpiando reglas de IoT de muestra...",
        "debug_listing_rules": "🔍 DEBUG: Listando todas las reglas de IoT",
        "debug_deleting_rule": "🔍 DEBUG: Eliminando regla: {}",
        "deleted_rule": "   ✅ Regla eliminada: {}",
        "error_deleting_rule": "   ❌ Error eliminando regla {}: {}",
        "no_sample_rules": "   ℹ️ No se encontraron reglas de muestra para eliminar",
        "rules_cleanup_summary": "📊 Resumen de limpieza de reglas: {} reglas eliminadas",
        "step8_title": "💾 Paso 8: Limpiando archivos de certificados locales...",
        "checking_cert_directory": "🔍 Verificando directorio de certificados locales: {}",
        "cert_directory_contents": "📁 Contenido del directorio de certificados:",
        "removed_cert_directory": "✅ Directorio de certificados locales eliminado: {}",
        "directory_deleted_success": "🔍 Directorio {} eliminado exitosamente",
        "error_removing_cert_dir": "❌ Error eliminando directorio de certificados: {}",
        "no_cert_directory": "ℹ️  No se encontró directorio de certificados locales",
        "directory_not_exist": "🔍 El directorio {} no existe",
        "checking_sample_cert_dir": "🔍 Verificando directorio de certificados de muestra: {}",
        "sample_cert_contents": "📁 Contenido del directorio sample-certs:",
        "removed_sample_cert_dir": "✅ Directorio de certificados de muestra eliminado: {}",
        "error_removing_sample_dir": "❌ Error eliminando directorio sample-certs: {}",
        "no_sample_cert_dir": "ℹ️  No se encontró directorio de certificados de muestra",
        "cleanup_summary_title": "🎉 Resumen de Limpieza",
        "summary_separator": "=" * 50,
        "things_cleaned": "✅ Things de muestra limpiados (Vehicle-VIN-001, Vehicle-VIN-002, etc.)",
        "certificates_cleaned": "✅ Certificados asociados limpiados",
        "groups_cleaned": "✅ Grupos de Thing de muestra limpiados",
        "types_cleaned": "✅ Tipos de Thing de muestra limpiados",
        "local_files_cleaned": "✅ Archivos de certificados locales limpiados (certificates/ y sample-certs/)",
        "device_state_cleaned": "✅ Archivos de estado de dispositivos limpiados (archivos device_state.json)",
        "account_clean": "💡 Tu cuenta de AWS IoT ahora solo contiene recursos que no son de muestra",
        "error_generic": "❌ Error: {}",
        "debug_cleanup_completed": "🔍 DEBUG: Sesión de limpieza completada con registro detallado de API",
        "api_call_header": "🔍 Llamada a API: {}",
        "api_description": "📖 Descripción: {}",
        "api_input_params": "📥 Parámetros de Entrada:",
        "api_no_params": "📥 Parámetros de Entrada: Ninguno",
        "api_response": "📤 Respuesta de API:",
        "api_empty_response": "Respuesta vacía (operación completada exitosamente)",
        "deleting_resource": "Eliminando {}: {}",
        "deleted_resource": "✅ Eliminado {}: {}",
        "resource_not_found": "⚠️  {} {} no encontrado, omitiendo",
        "error_deleting_resource": "❌ Error eliminando {} {}: {}",
        "debug_full_error": "🔍 DEBUG: Respuesta completa de error:",
        "debug_full_traceback": "🔍 DEBUG: Traza completa:",
        "cleaning_certificate": "🔐 Limpiando certificado: {}",
        "step1_list_policies": "🔍 Paso 1: Listando políticas adjuntas al certificado",
        "found_attached_policies": "📋 Se encontraron {} políticas adjuntas",
        "detaching_policy": "🔗 Desvinculando política: {}",
        "detaching_cert_from_thing": "🔗 Desvinculando certificado del Thing: {}",
        "deactivating_certificate": "⏸️  Desactivando certificado: {}",
        "certificate_deactivated": "✅ Certificado {} desactivado",
        "deleting_certificate": "🗑️  Eliminando certificado: {}",
        "error_cleaning_certificate": "❌ Error limpiando certificado {}: {}",
    },
    "ja": {
        "title": "🧹 AWS IoT サンプルデータクリーンアップ",
        "separator": "=" * 40,
        "aws_config": "📍 AWS設定:",
        "account_id": "アカウントID",
        "region": "リージョン",
        "description": "学習セッション後のサンプルIoTリソースの安全なクリーンアップ。",
        "debug_enabled": "🔍 デバッグモード有効",
        "debug_features": ["• 詳細なAPIリクエスト/レスポンス", "• 完全なエラー詳細とトレースバック", "• 拡張削除ログ"],
        "tip": "💡 ヒント: 詳細なクリーンアップログには--debugフラグを使用",
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
        "cleanup_intro_title": "サンプルデータクリーンアップ - リソース管理",
        "cleanup_intro_content": "このスクリプトは、学習セッション中に作成されたすべてのサンプルIoTリソースを安全に削除します。適切な依存関係の順序で削除を行い、本番リソースを保護します。AWS料金を避けるために、学習後は常にクリーンアップを実行することが重要です。",
        "cleanup_intro_next": "サンプルリソースを特定し、安全に削除します",
        "press_enter": "Enterキーを押して続行...",
        "goodbye": "👋 さようなら！",
        "warning_title": "⚠️  重要な警告",
        "warning_content": [
            "このスクリプトは以下のサンプルリソースを削除します:",
            "• Vehicle-VIN-* パターンのThings",
            "• 関連する証明書とポリシー",
            "• SedanVehicle、SUVVehicle、TruckVehicle Thing Types",
            "• CustomerFleet、TestFleet、MaintenanceFleet、DealerFleet Thing Groups",
            "• ローカル証明書ファイル",
        ],
        "safety_note": "🛡️  安全性: 本番リソースは保護されています（サンプルパターンのみ削除）",
        "continue_prompt": "続行しますか？ (y/N): ",
        "cleanup_cancelled": "クリーンアップがキャンセルされました",
        "cleanup_cancelled_user": "👋 ユーザーによってクリーンアップがキャンセルされました。さようなら！",
        "step_1_title": "Thingsとその証明書をクリーンアップ中",
        "step_2_title": "Thing Typesをクリーンアップ中",
        "step_3_title": "Thing Groupsをクリーンアップ中",
        "step_4_title": "ローカル証明書ファイルをクリーンアップ中",
        "step_5_title": "クリーンアップ概要",
        "scanning_things": "🔍 サンプルThingsをスキャン中...",
        "found_things": "📊 {}個のサンプルThingsが見つかりました",
        "no_things_found": "✅ クリーンアップするサンプルThingsが見つかりませんでした",
        "processing_thing": "🔄 Thing処理中: {}",
        "thing_certificates": "📋 Thing {}の証明書: {}",
        "detaching_policy": "🔗 ポリシー{}を証明書{}から切り離し中",
        "policy_detached": "✅ ポリシーが切り離されました",
        "error_detaching_policy": "❌ ポリシー切り離しエラー: {}",
        "updating_certificate": "🔄 証明書{}を非アクティブに更新中",
        "certificate_updated": "✅ 証明書が非アクティブになりました",
        "error_updating_certificate": "❌ 証明書更新エラー: {}",
        "deleting_certificate": "🗑️  証明書削除中: {}",
        "certificate_deleted": "✅ 証明書が削除されました",
        "error_deleting_certificate": "❌ 証明書削除エラー: {}",
        "removing_thing_from_groups": "🔗 Thing {}をすべてのグループから削除中",
        "thing_removed_from_groups": "✅ Thingがグループから削除されました",
        "error_removing_thing_from_groups": "❌ グループからのThing削除エラー: {}",
        "deleting_thing": "🗑️  Thing削除中: {}",
        "thing_deleted": "✅ Thingが削除されました",
        "error_deleting_thing": "❌ Thing削除エラー: {}",
        "scanning_thing_types": "🔍 サンプルThing Typesをスキャン中...",
        "found_thing_types": "📊 {}個のサンプルThing Typesが見つかりました",
        "no_thing_types_found": "✅ クリーンアップするサンプルThing Typesが見つかりませんでした",
        "deleting_thing_type": "🗑️  Thing Type削除中: {}",
        "thing_type_deleted": "✅ Thing Typeが削除されました",
        "error_deleting_thing_type": "❌ Thing Type削除エラー: {}",
        "scanning_thing_groups": "🔍 サンプルThing Groupsをスキャン中...",
        "found_thing_groups": "📊 {}個のサンプルThing Groupsが見つかりました",
        "no_thing_groups_found": "✅ クリーンアップするサンプルThing Groupsが見つかりませんでした",
        "deleting_thing_group": "🗑️  Thing Group削除中: {}",
        "thing_group_deleted": "✅ Thing Groupが削除されました",
        "error_deleting_thing_group": "❌ Thing Group削除エラー: {}",
        "cleaning_local_certificates": "🧹 ローカル証明書ファイルをクリーンアップ中...",
        "certificates_directory_not_found": "📁 証明書ディレクトリが見つかりません: {}",
        "cleaning_certificate_directory": "🗑️  証明書ディレクトリをクリーンアップ中: {}",
        "certificate_directory_cleaned": "✅ 証明書ディレクトリがクリーンアップされました",
        "error_cleaning_certificate_directory": "❌ 証明書ディレクトリクリーンアップエラー: {}",
        "cleanup_summary_title": "📊 クリーンアップ概要:",
        "things_cleaned": "Things削除済み:",
        "certificates_cleaned": "証明書削除済み:",
        "thing_types_cleaned": "Thing Types削除済み:",
        "thing_groups_cleaned": "Thing Groups削除済み:",
        "local_files_cleaned": "ローカルファイル削除済み:",
        "cleanup_complete": "🎉 クリーンアップ完了！すべてのサンプルリソースが削除されました。",
        "debug_session_complete": "🔍 デバッグ: 詳細なクリーンアップログでセッションが完了しました",
        "error_summary": "❌ 概要取得エラー:",
        "debug_full_error": "🔍 デバッグ: 完全なエラーレスポンス:",
        "debug_full_traceback": "🔍 デバッグ: 完全なトレースバック:",
        "api_error": "❌ AWS APIエラー",
        "unexpected_error": "❌ 予期しないエラー",
        "error_cleaning_certificate": "❌ 証明書{}のクリーンアップエラー: {}",
    },
    "pt-BR": {
        "title": "🧹 Limpeza de Dados de Exemplo AWS IoT",
        "separator": "=" * 50,
        "aws_config": "📍 Configuração AWS:",
        "account_id": "ID da Conta",
        "region": "Região",
        "aws_context_error": "⚠️ Não foi possível recuperar o contexto AWS:",
        "aws_credentials_reminder": "   Certifique-se de que as credenciais AWS estão configuradas",
        "description_intro": "Este script limpará APENAS os recursos de exemplo criados por:",
        "setup_scripts": ["• setup_sample_data.py", "• certificate_manager.py"],
        "no_affect_other": "NÃO afetará outros recursos IoT em sua conta.",
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Mostrará solicitações e respostas detalhadas da API",
            "• Inclui detalhes completos de erros e rastreamentos",
            "• Documentação educacional de chamadas da API",
        ],
        "tip": "💡 Dica: Use a flag --debug ou -d para ver chamadas detalhadas da API",
        "resources_to_cleanup": "🎯 Recursos a serem limpos:",
        "things_prefix": "• Things que começam com '{}' (Vehicle-VIN-001, Vehicle-VIN-002, etc.)",
        "thing_types": "• Thing Types: {} (serão depreciados primeiro)",
        "thing_groups": "• Thing Groups: {}",
        "certificates_attached": "• Certificados anexados aos Things de exemplo",
        "local_cert_files": "• Arquivos de certificados locais em ./certificates/",
        "policies_manual_review": "• Políticas serão listadas para revisão manual",
        "continue_cleanup": "Continuar com a limpeza? (s/N): ",
        "cleanup_cancelled": "Limpeza cancelada",
        "client_initialized": "✅ Cliente AWS IoT inicializado",
        "debug_client_config": "🔍 DEBUG: Configuração do cliente:",
        "service_label": "Serviço",
        "api_version_label": "Versão da API",
        "learning_moment_title": "📚 MOMENTO DE APRENDIZADO: Limpeza de Recursos e Gerenciamento do Ciclo de Vida",
        "learning_moment_content": "A limpeza adequada de recursos é essencial em implantações IoT para evitar custos desnecessários e manter a segurança. Os recursos AWS IoT têm dependências - certificados devem ser desanexados antes da exclusão, Thing Types devem ser depreciados antes da remoção, e políticas devem ser cuidadosamente revisadas já que podem ser compartilhadas entre dispositivos.",
        "next_cleanup": "🔄 PRÓXIMO: Limparemos com segurança os recursos de exemplo na ordem correta",
        "press_enter_continue": "Pressione Enter para continuar...",
        "step1_title": "🗑️  Passo 1: Limpando Things de exemplo e certificados...",
        "step_separator": "-" * 50,
        "listing_things": "🔍 Listando todos os Things para encontrar Things de exemplo",
        "found_sample_things": "📋 Encontrados {} Things de exemplo para limpar",
        "processing_thing": "📱 Processando Thing: {}",
        "listing_principals": "🔍 Listando principais (certificados) para Thing: {}",
        "found_certificates": "🔐 Encontrados {} certificado(s) anexado(s) a {}",
        "deleting_thing": "🗑️  Excluindo Thing: {}",
        "step2_title": "🔐 Passo 2: Verificando certificados órfãos...",
        "listing_certificates": "🔍 Listando todos os certificados para verificar órfãos",
        "found_certificates_account": "📋 Encontrados {} certificado(s) na conta",
        "certificate_info": "ℹ️  Certificado: {} (Status: {})",
        "checking_certificate_things": "🔍 Verificando se o certificado {} está anexado a algum Thing",
        "cert_attached_sample_things": "⚠️  Certificado {} estava anexado aos Things de exemplo: {}",
        "cert_should_cleanup_step1": "   Este certificado deveria ter sido limpo no Passo 1",
        "cert_not_attached_sample": "✅ Certificado {} não está anexado aos Things de exemplo",
        "could_not_check_things": "⚠️  Não foi possível verificar Things para o certificado {}: {}",
        "step3_title": "📄 Passo 3: Limpando políticas de exemplo...",
        "listing_policies": "🔍 Listando todas as políticas para verificar limpeza",
        "found_policies_account": "📋 Encontradas {} políticas na conta",
        "checking_policy": "📄 Verificando política: {}",
        "checking_policy_targets": "🔍 Verificando alvos para a política: {}",
        "policy_attached_targets": "   ⚠️  Política {} está anexada a {} alvo(s), pulando",
        "deleting_unattached_policy": "   🗑️  Excluindo política não anexada: {}",
        "error_checking_policy": "   ❌ Erro verificando política {}: {}",
        "policy_no_sample_patterns": "   ℹ️  Política {} não corresponde aos padrões de exemplo, pulando",
        "policy_cleanup_summary": "📋 Resumo da limpeza de políticas:",
        "deleted_policies": "   ✅ Excluídas: {} políticas",
        "skipped_policies": "   ⚠️  Puladas: {} políticas (ainda anexadas a recursos)",
        "certificate_cleanup_summary": "📋 Resumo da limpeza de certificados:",
        "cleaned_certificates": "   ✅ Limpos: {} certificados",
        "skipped_certificates": "   ⚠️  Pulados: {} certificados",
        "skipped_certs_production": "💡 Certificados pulados parecem ser certificados de produção ou têm padrões de uso pouco claros",
        "manual_cert_deletion": "   Se você tem certeza de que são do aprendizado, pode excluí-los manualmente do console AWS",
        "skipped_policies_note": "💡 Políticas puladas ainda estão anexadas a certificados ou outros recursos",
        "policies_cleanup_auto": "   Elas serão limpas automaticamente quando os certificados forem excluídos",
        "policies_manual_cleanup": "   Ou você pode desanexá-las e excluí-las manualmente se necessário",
        "step4_title": "📁 Passo 4: Limpando Thing Groups de exemplo...",
        "listing_thing_groups": "🔍 Listando todos os Thing Groups para encontrar grupos de exemplo",
        "found_sample_groups": "📋 Encontrados {} Thing Groups de exemplo para limpar",
        "deleting_thing_group": "📁 Excluindo Thing Group: {}",
        "step5_title": "🏷️  Passo 5: Limpando Thing Types de exemplo...",
        "listing_thing_types": "🔍 Listando todos os Thing Types para encontrar tipos de exemplo",
        "found_sample_types": "📋 Encontrados {} Thing Types de exemplo para limpar",
        "no_sample_types": "ℹ️  Nenhum Thing Type de exemplo encontrado para limpar",
        "thing_type_deprecated": "ℹ️  Thing Type {} já está depreciado (desde {})",
        "thing_type_active": "ℹ️  Thing Type {} está ativo (precisa de depreciação)",
        "could_not_check_status": "⚠️  Não foi possível verificar o status de {}: {}",
        "deprecating_active_types": "⚠️  Depreciando {} Thing Types ativos...",
        "deprecating_thing_type": "🏷️  Depreciando Thing Type: {}",
        "thing_type_deprecated_success": "✅ Thing Type {} depreciado",
        "could_not_deprecate": "❌ Não foi possível depreciar Thing Type {}",
        "aws_constraint_5min": "⏰ Restrição AWS IoT: Thing Types devem aguardar 5 minutos após a depreciação antes da exclusão",
        "thing_types_to_delete": "📋 Thing Types para excluir:",
        "deprecated_item": "   • {} (depreciado: {})",
        "deletion_options": "🎯 Opções de Exclusão:",
        "wait_5min_delete": "1. Aguardar 5 minutos agora e excluir automaticamente",
        "skip_deletion": "2. Pular exclusão (executar limpeza novamente mais tarde)",
        "try_deletion_now": "3. Tentar exclusão agora (pode falhar se não passou tempo suficiente)",
        "select_option_1_3": "Selecionar opção (1-3): ",
        "waiting_5min": "⏳ Aguardando 5 minutos pela restrição AWS IoT...",
        "constraint_explanation": "💡 Isso é exigido pelo AWS IoT - Thing Types não podem ser excluídos imediatamente após a depreciação",
        "time_remaining": "⏰ Tempo restante: {:02d}:{:02d} - Você pode cancelar com Ctrl+C",
        "wait_completed": "✅ Período de espera de 5 minutos concluído!",
        "skipping_deletion": "⏭️  Pulando exclusão de Thing Types",
        "deletion_tip": "💡 Para excluir mais tarde, execute: python cleanup_sample_data.py",
        "types_ready_deletion": "   Os Thing Types já estão depreciados e estarão prontos para exclusão",
        "attempting_deletion_now": "🚀 Tentando exclusão agora (pode falhar devido à restrição de tempo)",
        "invalid_choice_1_3": "❌ Escolha inválida. Por favor digite 1, 2, ou 3",
        "deleting_deprecated_types": "🗑️  Excluindo Thing Types depreciados...",
        "attempting_delete_type": "🗑️  Tentando excluir Thing Type: {}",
        "deletion_failed_timing": "💡 Se a exclusão falhou devido ao tempo, aguarde mais alguns minutos e tente novamente",
        "type_ready_deletion": "   O Thing Type {} está depreciado e pronto para exclusão",
        "cleanup_interrupted": "🛑 Limpeza interrompida pelo usuário",
        "types_deprecated_delete_later": "💡 Thing Types que foram depreciados podem ser excluídos mais tarde executando a limpeza novamente",
        "step6_title": "🌙 Passo 6: Limpeza de sombras de dispositivos...",
        "shadows_auto_cleanup": "ℹ️  Sombras de dispositivos são limpas automaticamente quando Things são excluídos",
        "no_manual_shadow_cleanup": "   Nenhuma exclusão manual de sombras necessária - AWS IoT lida com isso automaticamente",
        "debug_shadow_skipped": "🔍 DEBUG: Limpeza de sombras pulada - tratada pela exclusão de Thing",
        "shadow_cleanup_completed": "✅ Limpeza de sombras concluída (automática)",
        "step7_title": "📋 Passo 7: Limpando regras IoT de exemplo...",
        "debug_listing_rules": "🔍 DEBUG: Listando todas as regras IoT",
        "debug_deleting_rule": "🔍 DEBUG: Excluindo regra: {}",
        "deleted_rule": "   ✅ Regra excluída: {}",
        "error_deleting_rule": "   ❌ Erro excluindo regra {}: {}",
        "no_sample_rules": "   ℹ️ Nenhuma regra de exemplo encontrada para excluir",
        "rules_cleanup_summary": "📋 Resumo da limpeza de regras: {} regras excluídas",
        "step8_title": "💾 Passo 8: Limpando arquivos de certificados locais...",
        "checking_cert_directory": "🔍 Verificando diretório de certificados locais: {}",
        "cert_directory_contents": "📁 Conteúdo do diretório de certificados:",
        "removed_cert_directory": "✅ Diretório de certificados locais removido: {}",
        "directory_deleted_success": "🔍 Diretório {} excluído com sucesso",
        "error_removing_cert_dir": "❌ Erro removendo diretório de certificados: {}",
        "no_cert_directory": "ℹ️  Nenhum diretório de certificados locais encontrado",
        "directory_not_exist": "🔍 Diretório {} não existe",
        "checking_sample_cert_dir": "🔍 Verificando diretório de certificados de exemplo: {}",
        "sample_cert_contents": "📁 Conteúdo do diretório sample-certs:",
        "removed_sample_cert_dir": "✅ Diretório de certificados de exemplo removido: {}",
        "error_removing_sample_dir": "❌ Erro removendo diretório sample-certs: {}",
        "no_sample_cert_dir": "ℹ️  Nenhum diretório de certificados de exemplo encontrado",
        "cleanup_summary_title": "🎉 Resumo da Limpeza",
        "summary_separator": "=" * 50,
        "things_cleaned": "✅ Things de exemplo limpos (Vehicle-VIN-001, Vehicle-VIN-002, etc.)",
        "certificates_cleaned": "✅ Certificados associados limpos",
        "groups_cleaned": "✅ Thing Groups de exemplo limpos",
        "types_cleaned": "✅ Thing Types de exemplo limpos",
        "local_files_cleaned": "✅ Arquivos de certificados locais limpos (certificates/ e sample-certs/)",
        "device_state_cleaned": "✅ Arquivos de estado de dispositivos limpos (arquivos device_state.json)",
        "account_clean": "💡 Sua conta AWS IoT agora contém apenas recursos que não são de exemplo",
        "error_generic": "❌ Erro: {}",
        "debug_cleanup_completed": "🔍 DEBUG: Sessão de limpeza concluída com log detalhado da API",
        "api_call_header": "🔍 Chamada da API: {}",
        "api_description": "📖 Descrição: {}",
        "api_input_params": "📥 Parâmetros de Entrada:",
        "api_no_params": "📥 Parâmetros de Entrada: Nenhum",
        "api_response": "📤 Resposta da API:",
        "api_empty_response": "Resposta vazia (operação concluída com sucesso)",
        "deleting_resource": "Excluindo {}: {}",
        "deleted_resource": "✅ Excluído {}: {}",
        "resource_not_found": "⚠️  {} {} não encontrado, pulando",
        "error_deleting_resource": "❌ Erro excluindo {} {}: {}",
        "debug_full_error": "🔍 DEBUG: Resposta completa de erro:",
        "debug_full_traceback": "🔍 DEBUG: Rastreamento completo:",
        "cleaning_certificate": "🔐 Limpando certificado: {}",
        "step1_list_policies": "🔍 Passo 1: Listando políticas anexadas ao certificado",
        "found_attached_policies": "📋 Encontradas {} políticas anexadas",
        "detaching_policy": "🔗 Desanexando política: {}",
        "detaching_cert_from_thing": "🔗 Desanexando certificado do Thing: {}",
        "deactivating_certificate": "⏸️  Desativando certificado: {}",
        "certificate_deactivated": "✅ Certificado {} desativado",
        "deleting_certificate": "🗑️  Excluindo certificado: {}",
        "error_cleaning_certificate": "❌ Erro limpando certificado {}: {}",
    },
    "ko": {
        "title": "🧹 AWS IoT 샘플 데이터 정리",
        "separator": "=" * 50,
        "aws_config": "📍 AWS 구성:",
        "account_id": "계정 ID",
        "region": "리전",
        "aws_context_error": "⚠️ AWS 컨텍스트를 검색할 수 없습니다:",
        "aws_credentials_reminder": "   AWS 자격 증명이 구성되어 있는지 확인하세요",
        "description_intro": "이 스크립트는 다음에 의해 생성된 샘플 리소스만 정리합니다:",
        "setup_scripts": ["• setup_sample_data.py", "• certificate_manager.py"],
        "no_affect_other": "계정의 다른 IoT 리소스에는 영향을 주지 않습니다.",
        "debug_enabled": "🔍 디버그 모드 활성화",
        "debug_features": [
            "• 상세한 API 요청 및 응답을 표시합니다",
            "• 완전한 오류 세부 정보 및 추적을 포함합니다",
            "• 교육용 API 호출 문서",
        ],
        "tip": "💡 팁: 상세한 API 호출을 보려면 --debug 또는 -d 플래그를 사용하세요",
        "resources_to_cleanup": "🎯 정리할 리소스:",
        "things_prefix": "• '{}'로 시작하는 Things (Vehicle-VIN-001, Vehicle-VIN-002 등)",
        "thing_types": "• Thing Types: {} (먼저 사용 중단됩니다)",
        "thing_groups": "• Thing Groups: {}",
        "certificates_attached": "• 샘플 Things에 첨부된 인증서",
        "local_cert_files": "• ./certificates/의 로컬 인증서 파일",
        "policies_manual_review": "• 정책은 수동 검토를 위해 나열됩니다",
        "continue_cleanup": "정리를 계속하시겠습니까? (y/N): ",
        "cleanup_cancelled": "정리가 취소되었습니다",
        "client_initialized": "✅ AWS IoT 클라이언트가 초기화되었습니다",
        "debug_client_config": "🔍 디버그: 클라이언트 구성:",
        "service_label": "서비스",
        "api_version_label": "API 버전",
        "learning_moment_title": "📚 학습 포인트: 리소스 정리 및 수명 주기 관리",
        "learning_moment_content": "적절한 리소스 정리는 불필요한 비용을 피하고 보안을 유지하기 위해 IoT 배포에서 필수적입니다. AWS IoT 리소스에는 종속성이 있습니다 - 인증서는 삭제 전에 분리되어야 하고, Thing Types는 제거 전에 사용 중단되어야 하며, 정책은 장치 간에 공유될 수 있으므로 신중하게 검토되어야 합니다.",
        "next_cleanup": "🔄 다음: 올바른 순서로 샘플 리소스를 안전하게 정리하겠습니다",
        "press_enter_continue": "계속하려면 Enter를 누르세요...",
        "step1_title": "🗑️ 1단계: 샘플 Things 및 인증서 정리 중...",
        "step_separator": "-" * 50,
        "listing_things": "🔍 샘플 Things를 찾기 위해 모든 Things 나열 중",
        "found_sample_things": "📋 정리할 {} 샘플 Things를 찾았습니다",
        "processing_thing": "📱 Thing 처리 중: {}",
        "listing_principals": "🔍 Thing {}의 주체(인증서) 나열 중",
        "found_certificates": "🔐 {}에 첨부된 {} 인증서를 찾았습니다",
        "deleting_thing": "🗑️ Thing 삭제 중: {}",
        "step2_title": "🔐 2단계: 고아 인증서 확인 중...",
        "listing_certificates": "🔍 고아 인증서를 확인하기 위해 모든 인증서 나열 중",
        "found_certificates_account": "📋 계정에서 {} 인증서를 찾았습니다",
        "certificate_info": "ℹ️ 인증서: {} (상태: {})",
        "checking_certificate_things": "🔍 인증서 {}가 Things에 첨부되어 있는지 확인 중",
        "cert_attached_sample_things": "⚠️ 인증서 {}가 샘플 Things에 첨부되어 있었습니다: {}",
        "cert_should_cleanup_step1": "   이 인증서는 1단계에서 정리되었어야 합니다",
        "cert_not_attached_sample": "✅ 인증서 {}는 샘플 Things에 첨부되어 있지 않습니다",
        "could_not_check_things": "⚠️ 인증서 {}의 Things를 확인할 수 없습니다: {}",
        "step3_title": "📄 3단계: 샘플 정책 정리 중...",
        "listing_policies": "🔍 정리를 위해 모든 정책 나열 중",
        "found_policies_account": "📋 계정에서 {} 정책을 찾았습니다",
        "checking_policy": "📄 정책 확인 중: {}",
        "checking_policy_targets": "🔍 정책 {}의 대상 확인 중",
        "policy_attached_targets": "   ⚠️ 정책 {}가 {} 대상에 첨부되어 있어 건너뜁니다",
        "deleting_unattached_policy": "   🗑️ 첨부되지 않은 정책 삭제 중: {}",
        "error_checking_policy": "   ❌ 정책 {} 확인 오류: {}",
        "policy_no_sample_patterns": "   ℹ️ 정책 {}가 샘플 패턴과 일치하지 않아 건너뜁니다",
        "policy_cleanup_summary": "📊 정책 정리 요약:",
        "deleted_policies": "   ✅ 삭제됨: {} 정책",
        "skipped_policies": "   ⚠️ 건너뜀: {} 정책 (여전히 리소스에 첨부됨)",
        "certificate_cleanup_summary": "📊 인증서 정리 요약:",
        "cleaned_certificates": "   ✅ 정리됨: {} 인증서",
        "skipped_certificates": "   ⚠️ 건너뜀: {} 인증서",
        "skipped_certs_production": "💡 건너뛴 인증서는 프로덕션 인증서이거나 불분명한 사용 패턴을 가지고 있는 것 같습니다",
        "manual_cert_deletion": "   학습용이라고 확신한다면 AWS 콘솔에서 수동으로 삭제할 수 있습니다",
        "skipped_policies_note": "💡 건너뛴 정책은 여전히 인증서나 다른 리소스에 첨부되어 있습니다",
        "policies_cleanup_auto": "   인증서가 삭제될 때 자동으로 정리됩니다",
        "policies_manual_cleanup": "   또는 필요한 경우 수동으로 분리하고 삭제할 수 있습니다",
        "step4_title": "📁 4단계: 샘플 Thing Groups 정리 중...",
        "listing_thing_groups": "🔍 샘플 그룹을 찾기 위해 모든 Thing Groups 나열 중",
        "found_sample_groups": "📋 정리할 {} 샘플 Thing Groups를 찾았습니다",
        "deleting_thing_group": "📁 Thing Group 삭제 중: {}",
        "step5_title": "🏷️ 5단계: 샘플 Thing Types 정리 중...",
        "listing_thing_types": "🔍 샘플 타입을 찾기 위해 모든 Thing Types 나열 중",
        "found_sample_types": "📋 정리할 {} 샘플 Thing Types를 찾았습니다",
        "no_sample_types": "ℹ️ 정리할 샘플 Thing Types를 찾지 못했습니다",
        "thing_type_deprecated": "ℹ️ Thing Type {}는 이미 사용 중단되었습니다 ({}부터)",
        "thing_type_active": "ℹ️ Thing Type {}는 활성 상태입니다 (사용 중단 필요)",
        "could_not_check_status": "⚠️ {}의 상태를 확인할 수 없습니다: {}",
        "deprecating_active_types": "⚠️ {} 활성 Thing Types를 사용 중단하는 중...",
        "deprecating_thing_type": "🏷️ Thing Type 사용 중단 중: {}",
        "thing_type_deprecated_success": "✅ Thing Type {} 사용 중단됨",
        "could_not_deprecate": "❌ Thing Type {}를 사용 중단할 수 없습니다",
        "aws_constraint_5min": "⏰ AWS IoT 제약: Thing Types는 사용 중단 후 삭제 전에 5분을 기다려야 합니다",
        "thing_types_to_delete": "📋 삭제할 Thing Types:",
        "deprecated_item": "   • {} (사용 중단됨: {})",
        "deletion_options": "🎯 삭제 옵션:",
        "wait_5min_delete": "1. 지금 5분 기다리고 자동으로 삭제",
        "skip_deletion": "2. 삭제 건너뛰기 (나중에 정리 다시 실행)",
        "try_deletion_now": "3. 지금 삭제 시도 (충분한 시간이 지나지 않았으면 실패할 수 있음)",
        "select_option_1_3": "옵션 선택 (1-3): ",
        "waiting_5min": "⏳ AWS IoT 제약으로 5분 대기 중...",
        "constraint_explanation": "💡 이는 AWS IoT에서 요구됩니다 - Thing Types는 사용 중단 후 즉시 삭제할 수 없습니다",
        "time_remaining": "⏰ 남은 시간: {:02d}:{:02d} - Ctrl+C로 취소할 수 있습니다",
        "wait_completed": "✅ 5분 대기 기간이 완료되었습니다!",
        "skipping_deletion": "⏭️ Thing Type 삭제 건너뛰기",
        "deletion_tip": "💡 나중에 삭제하려면 실행: python cleanup_sample_data.py",
        "types_ready_deletion": "   Thing Types는 이미 사용 중단되었으며 삭제 준비가 되었습니다",
        "attempting_deletion_now": "🚀 지금 삭제 시도 중 (시간 제약으로 실패할 수 있음)",
        "invalid_choice_1_3": "❌ 잘못된 선택입니다. 1, 2, 또는 3을 입력하세요",
        "deleting_deprecated_types": "🗑️ 사용 중단된 Thing Types 삭제 중...",
        "attempting_delete_type": "🗑️ Thing Type 삭제 시도 중: {}",
        "deletion_failed_timing": "💡 타이밍으로 인해 삭제가 실패했다면 몇 분 더 기다린 후 다시 시도하세요",
        "type_ready_deletion": "   Thing Type {}는 사용 중단되었으며 삭제 준비가 되었습니다",
        "cleanup_interrupted": "🛑 사용자가 정리를 중단했습니다",
        "types_deprecated_delete_later": "💡 사용 중단된 Thing Types는 정리를 다시 실행하여 나중에 삭제할 수 있습니다",
        "step6_title": "🌙 6단계: 디바이스 섀도우 정리...",
        "shadows_auto_cleanup": "ℹ️ 디바이스 섀도우는 Things가 삭제될 때 자동으로 정리됩니다",
        "no_manual_shadow_cleanup": "   수동 섀도우 삭제가 필요하지 않습니다 - AWS IoT가 자동으로 처리합니다",
        "debug_shadow_skipped": "🔍 디버그: 섀도우 정리 건너뜀 - Thing 삭제로 처리됨",
        "shadow_cleanup_completed": "✅ 섀도우 정리 완료 (자동)",
        "step7_title": "📋 7단계: 샘플 IoT 규칙 정리 중...",
        "debug_listing_rules": "🔍 디버그: 모든 IoT 규칙 나열 중",
        "debug_deleting_rule": "🔍 디버그: 규칙 삭제 중: {}",
        "deleted_rule": "   ✅ 규칙 삭제됨: {}",
        "error_deleting_rule": "   ❌ 규칙 {} 삭제 오류: {}",
        "no_sample_rules": "   ℹ️ 삭제할 샘플 규칙을 찾지 못했습니다",
        "rules_cleanup_summary": "📊 규칙 정리 요약: {} 규칙 삭제됨",
        "step8_title": "💾 8단계: 로컬 인증서 파일 정리 중...",
        "checking_cert_directory": "🔍 로컬 인증서 디렉토리 확인 중: {}",
        "cert_directory_contents": "📁 인증서 디렉토리 내용:",
        "removed_cert_directory": "✅ 로컬 인증서 디렉토리 제거됨: {}",
        "directory_deleted_success": "🔍 디렉토리 {} 성공적으로 삭제됨",
        "error_removing_cert_dir": "❌ 인증서 디렉토리 제거 오류: {}",
        "no_cert_directory": "ℹ️ 로컬 인증서 디렉토리를 찾지 못했습니다",
        "directory_not_exist": "🔍 디렉토리 {}가 존재하지 않습니다",
        "checking_sample_cert_dir": "🔍 샘플 인증서 디렉토리 확인 중: {}",
        "sample_cert_contents": "📁 sample-certs 디렉토리 내용:",
        "removed_sample_cert_dir": "✅ 샘플 인증서 디렉토리 제거됨: {}",
        "error_removing_sample_dir": "❌ sample-certs 디렉토리 제거 오류: {}",
        "no_sample_cert_dir": "ℹ️ 샘플 인증서 디렉토리를 찾지 못했습니다",
        "cleanup_summary_title": "🎉 정리 요약",
        "summary_separator": "=" * 50,
        "things_cleaned": "✅ 샘플 Things 정리됨 (Vehicle-VIN-001, Vehicle-VIN-002 등)",
        "certificates_cleaned": "✅ 관련 인증서 정리됨",
        "groups_cleaned": "✅ 샘플 Thing Groups 정리됨",
        "types_cleaned": "✅ 샘플 Thing Types 정리됨",
        "local_files_cleaned": "✅ 로컬 인증서 파일 정리됨 (certificates/ 및 sample-certs/)",
        "device_state_cleaned": "✅ 디바이스 상태 파일 정리됨 (device_state.json 파일)",
        "account_clean": "💡 AWS IoT 계정에는 이제 샘플이 아닌 리소스만 포함됩니다",
        "error_generic": "❌ 오류: {}",
        "debug_cleanup_completed": "🔍 디버그: 상세한 API 로깅으로 정리 세션이 완료되었습니다",
        "api_call_header": "🔍 API 호출: {}",
        "api_description": "📖 설명: {}",
        "api_input_params": "📥 입력 매개변수:",
        "api_no_params": "📥 입력 매개변수: 없음",
        "api_response": "📤 API 응답:",
        "api_empty_response": "빈 응답 (작업이 성공적으로 완료됨)",
        "deleting_resource": "{} 삭제 중: {}",
        "deleted_resource": "✅ {} 삭제됨: {}",
        "resource_not_found": "⚠️ {} {}를 찾을 수 없어 건너뜁니다",
        "error_deleting_resource": "❌ {} {} 삭제 오류: {}",
        "debug_full_error": "🔍 디버그: 전체 오류 응답:",
        "debug_full_traceback": "🔍 디버그: 전체 추적:",
        "cleaning_certificate": "🔐 인증서 정리 중: {}",
        "step1_list_policies": "🔍 1단계: 인증서에 첨부된 정책 나열 중",
        "found_attached_policies": "📋 {} 첨부된 정책을 찾았습니다",
        "detaching_policy": "🔗 정책 분리 중: {}",
        "detaching_cert_from_thing": "🔗 Thing에서 인증서 분리 중: {}",
        "deactivating_certificate": "⏸️ 인증서 비활성화 중: {}",
        "certificate_deactivated": "✅ 인증서 {} 비활성화됨",
        "deleting_certificate": "🗑️ 인증서 삭제 중: {}",
        "error_cleaning_certificate": "❌ 인증서 {} 정리 오류: {}",
    },
}

# Global variables for language and debug mode
USER_LANG = "en"
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


def get_message(key, lang="en"):
    """Get localized message"""
    return MESSAGES.get(lang, MESSAGES["en"]).get(key, key)


def print_api_call(operation, description, params=None):
    """Print detailed API call information for educational purposes"""
    print(f"\n{get_message('api_call_header', USER_LANG).format(operation)}")
    print(f"{get_message('api_description', USER_LANG).format(description)}")
    if params:
        print(get_message("api_input_params", USER_LANG))
        print(json.dumps(params, indent=2, default=str))
    else:
        print(get_message("api_no_params", USER_LANG))


def print_api_response(response, success=True):
    """Print API response details"""
    if success:
        print(get_message("api_response", USER_LANG))
        if response:
            print(json.dumps(response, indent=2, default=str))
        else:
            print(get_message("api_empty_response", USER_LANG))
    time.sleep(0.5)  # nosemgrep: arbitrary-sleep


def safe_delete(func, resource_type, name, debug=False, **kwargs):
    """Safely delete resource with error handling and optional debug info"""
    try:
        if debug:
            print_api_call(func.__name__, f"Delete {resource_type}: {name}", kwargs)
        else:
            print(get_message("deleting_resource", USER_LANG).format(resource_type, name))

        response = func(**kwargs)

        if debug:
            print_api_response(response, success=True)

        print(get_message("deleted_resource", USER_LANG).format(resource_type, name))
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            print(get_message("resource_not_found", USER_LANG).format(resource_type, name))
        else:
            print(
                get_message("error_deleting_resource", USER_LANG).format(resource_type, name, e.response["Error"]["Message"])
            )
            if debug:
                print(get_message("debug_full_error", USER_LANG))
                print(json.dumps(e.response, indent=2, default=str))
        return False
    except Exception as e:
        print(get_message("error_generic", USER_LANG).format(str(e)))
        if debug:
            print(get_message("debug_full_traceback", USER_LANG))
            traceback.print_exc()
        return False


def safe_operation(iot, operation, description, debug=False, **kwargs):
    """Execute any IoT operation with detailed logging"""
    try:
        if debug:
            print_api_call(operation.__name__, description, kwargs)

        response = operation(**kwargs)

        if debug:
            print_api_response(response, success=True)

        return response, True
    except ClientError as e:
        print(get_message("error_generic", USER_LANG).format(f"{description} failed: {e.response['Error']['Message']}"))
        if debug:
            print(get_message("debug_full_error", USER_LANG))
            print(json.dumps(e.response, indent=2, default=str))
        return None, False
    except Exception as e:
        print(get_message("error_generic", USER_LANG).format(f"{description} failed: {str(e)}"))
        if debug:
            print(get_message("debug_full_traceback", USER_LANG))
            traceback.print_exc()
        return None, False


def cleanup_certificate(iot, cert_arn, thing_name=None, debug=False):
    """Clean up a certificate and its attachments with detailed API logging"""
    cert_id = cert_arn.split("/")[-1]
    print(f"\n{get_message('cleaning_certificate', USER_LANG).format(cert_id)}")

    try:
        # List and detach all policies from certificate
        if debug:
            print(f"\n{get_message('step1_list_policies', USER_LANG)}")

        policies_response, success = safe_operation(
            iot, iot.list_attached_policies, f"List policies attached to certificate {cert_id}", debug=debug, target=cert_arn
        )

        if success and policies_response:
            policies = policies_response.get("policies", [])
            print(get_message("found_attached_policies", USER_LANG).format(len(policies)))

            for policy in policies:
                policy_name = policy["policyName"]
                print(f"\n{get_message('detaching_policy', USER_LANG).format(policy_name)}")
                safe_delete(
                    iot.detach_policy,
                    f"Policy attachment '{policy_name}'",
                    f"from certificate {cert_id}",
                    debug=debug,
                    policyName=policy_name,
                    target=cert_arn,
                )

        # Detach certificate from Things
        if thing_name:
            print(f"\n{get_message('detaching_cert_from_thing', USER_LANG).format(thing_name)}")
            safe_delete(
                iot.detach_thing_principal,
                "Certificate attachment",
                f"from Thing {thing_name}",
                debug=debug,
                thingName=thing_name,
                principal=cert_arn,
            )

        # Deactivate certificate
        print(f"\n{get_message('deactivating_certificate', USER_LANG).format(cert_id)}")
        deactivate_response, success = safe_operation(
            iot,
            iot.update_certificate,
            f"Deactivate certificate {cert_id}",
            debug=debug,
            certificateId=cert_id,
            newStatus="INACTIVE",
        )

        if success:
            print(get_message("certificate_deactivated", USER_LANG).format(cert_id))

        # Delete certificate
        print(f"\n{get_message('deleting_certificate', USER_LANG).format(cert_id)}")
        safe_delete(iot.delete_certificate, "Certificate", cert_id, debug=debug, certificateId=cert_id)

    except Exception as e:
        print(get_message("error_cleaning_certificate", USER_LANG).format(cert_id, str(e)))
        if debug:
            traceback.print_exc()


def cleanup_sample_things(iot, debug=False):
    """Clean up sample Things and their certificates with detailed API logging"""
    print(f"\n{get_message('step1_title', USER_LANG)}")
    print(get_message("step_separator", USER_LANG))

    try:
        # List all Things
        if debug:
            print(get_message("listing_things", USER_LANG))

        list_response, success = safe_operation(iot, iot.list_things, "List all Things", debug=debug)

        if not success:
            return

        things = list_response.get("things", [])
        sample_things = [t for t in things if t["thingName"].startswith(SAMPLE_THING_PREFIX)]

        print(get_message("found_sample_things", USER_LANG).format(len(sample_things)))

        for thing in sample_things:
            thing_name = thing["thingName"]
            print(f"\n{get_message('processing_thing', USER_LANG).format(thing_name)}")

            # Get certificates attached to this Thing
            if debug:
                print(get_message("listing_principals", USER_LANG).format(thing_name))

            principals_response, success = safe_operation(
                iot, iot.list_thing_principals, f"List principals for Thing {thing_name}", debug=debug, thingName=thing_name
            )

            if success and principals_response:
                principals = principals_response.get("principals", [])
                cert_arns = [p for p in principals if "cert/" in p]

                print(get_message("found_certificates", USER_LANG).format(len(cert_arns), thing_name))

                # Clean up certificates first
                for cert_arn in cert_arns:
                    cleanup_certificate(iot, cert_arn, thing_name, debug=debug)

            # Delete the Thing
            print(f"\n{get_message('deleting_thing', USER_LANG).format(thing_name)}")
            safe_delete(iot.delete_thing, "Thing", thing_name, debug=debug, thingName=thing_name)

    except Exception as e:
        print(get_message("error_generic", USER_LANG).format(f"cleaning up Things: {str(e)}"))
        if debug:
            traceback.print_exc()


def cleanup_orphaned_certificates(iot, debug=False):
    """Clean up certificates that are likely from the learning process"""
    print(f"\n{get_message('step2_title', USER_LANG)}")
    print(get_message("step_separator", USER_LANG))

    try:
        # List all certificates
        if debug:
            print(get_message("listing_certificates", USER_LANG))

        list_response, success = safe_operation(iot, iot.list_certificates, "List all certificates", debug=debug)

        if not success:
            return

        certificates = list_response.get("certificates", [])
        print(get_message("found_certificates_account", USER_LANG).format(len(certificates)))

        certificates_cleaned = 0
        certificates_skipped = 0

        for cert in certificates:
            cert_arn = cert["certificateArn"]
            cert_id = cert["certificateId"]
            cert_status = cert.get("status", "Unknown")

            print(f"\n{get_message('certificate_info', USER_LANG).format(cert_id, cert_status)}")

            # Get Things attached to this certificate
            should_cleanup = False
            cleanup_reason = ""

            try:
                things_response, success = safe_operation(
                    iot,
                    iot.list_principal_things,
                    f"List Things attached to certificate {cert_id}",
                    debug=debug,
                    principal=cert_arn,
                )

                if success and things_response:
                    attached_things = things_response.get("things", [])
                    sample_things = [t for t in attached_things if t.startswith(SAMPLE_THING_PREFIX)]
                    non_sample_things = [t for t in attached_things if not t.startswith(SAMPLE_THING_PREFIX)]

                    if debug:
                        print(f"   📋 Attached to {len(attached_things)} Thing(s)")
                        if attached_things:
                            for thing in attached_things:
                                print(f"      • {thing}")

                    # Decision logic for cleanup
                    if not attached_things:
                        # Certificate not attached to any Things - likely orphaned from learning
                        should_cleanup = True
                        cleanup_reason = "not attached to any Things (likely orphaned from learning)"
                    elif sample_things and not non_sample_things:
                        # Certificate only attached to sample Things - already cleaned up in Step 1
                        print(get_message("cert_attached_sample_things", USER_LANG).format(cert_id, ", ".join(sample_things)))
                        print(get_message("cert_should_cleanup_step1", USER_LANG))
                        certificates_skipped += 1
                        continue
                    elif non_sample_things and not sample_things:
                        # Certificate attached to non-sample Things
                        # Check if these Things look like they're from learning (common patterns)
                        learning_patterns = ["test", "demo", "sample", "learning", "device"]
                        learning_things = []
                        for thing in non_sample_things:
                            if any(pattern.lower() in thing.lower() for pattern in learning_patterns):
                                learning_things.append(thing)

                        if learning_things:
                            should_cleanup = True
                            cleanup_reason = f"attached to learning-pattern Things: {', '.join(learning_things)}"
                        else:
                            print(f"   ⚠️  Certificate attached to non-sample Things: {', '.join(non_sample_things)}")
                            print("   💡 Skipping - appears to be production certificate")
                            certificates_skipped += 1
                            continue
                    else:
                        # Mixed attachment - be conservative
                        print("   ⚠️  Certificate attached to mixed Things (sample + non-sample)")
                        print("   💡 Skipping - mixed usage pattern")
                        certificates_skipped += 1
                        continue

                else:
                    print(f"   ⚠️  Could not check Thing attachments for certificate {cert_id}")
                    certificates_skipped += 1
                    continue

            except Exception as e:
                print(get_message("could_not_check_things", USER_LANG).format(cert_id, str(e)))
                certificates_skipped += 1
                continue

            # Clean up the certificate if determined to be from learning
            if should_cleanup:
                print(f"   🗑️  Cleaning up certificate: {cleanup_reason}")
                cleanup_certificate(iot, cert_arn, None, debug=debug)
                certificates_cleaned += 1
            else:
                certificates_skipped += 1

        print(f"\n{get_message('certificate_cleanup_summary', USER_LANG)}")
        print(get_message("cleaned_certificates", USER_LANG).format(certificates_cleaned))
        print(get_message("skipped_certificates", USER_LANG).format(certificates_skipped))

        if certificates_skipped > 0:
            print(f"\n{get_message('skipped_certs_production', USER_LANG)}")
            print(get_message("manual_cert_deletion", USER_LANG))

    except Exception as e:
        print(get_message("error_generic", USER_LANG).format(f"listing certificates: {str(e)}"))
        if debug:
            traceback.print_exc()


def cleanup_sample_policies(iot, debug=False):
    """Clean up policies that might have been created by certificate manager"""
    print(f"\n{get_message('step3_title', USER_LANG)}")
    print(get_message("step_separator", USER_LANG))

    try:
        # List all policies
        if debug:
            print(get_message("listing_policies", USER_LANG))

        list_response, success = safe_operation(iot, iot.list_policies, "List all policies", debug=debug)

        if not success:
            return

        policies = list_response.get("policies", [])

        print(get_message("found_policies_account", USER_LANG).format(len(policies)))

        # Look for policies that appear to be sample/learning policies
        sample_policy_patterns = ["sample", "test", "demo", "learning", "device", "basic", "readonly"]
        policies_deleted = 0
        policies_skipped = 0
        policies_detached = 0

        for policy in policies:
            policy_name = policy["policyName"]

            # Check if policy name contains sample patterns (case insensitive)
            is_sample_policy = any(pattern.lower() in policy_name.lower() for pattern in sample_policy_patterns)

            if is_sample_policy:
                print(f"\n{get_message('checking_policy', USER_LANG).format(policy_name)}")

                try:
                    # Check if policy is attached to any certificates
                    if debug:
                        print(get_message("checking_policy_targets", USER_LANG).format(policy_name))

                    targets_response, success = safe_operation(
                        iot,
                        iot.list_targets_for_policy,
                        f"List targets for policy {policy_name}",
                        debug=debug,
                        policyName=policy_name,
                    )

                    if success and targets_response:
                        targets = targets_response.get("targets", [])

                        if not targets:
                            # Policy is not attached to anything, safe to delete
                            print(get_message("deleting_unattached_policy", USER_LANG).format(policy_name))

                            delete_success = safe_delete(
                                iot.delete_policy, "Policy", policy_name, debug=debug, policyName=policy_name
                            )

                            if delete_success:
                                policies_deleted += 1
                        else:
                            # Policy is attached - try to detach and delete
                            print(f"   📎 Policy attached to {len(targets)} target(s)")
                            if debug:
                                for target in targets:
                                    print(f"      - {target}")

                            # Try to detach from all targets
                            detach_success = True
                            for target in targets:
                                print(f"   🔗 Detaching policy from {target[:16]}...")
                                try:
                                    iot.detach_policy(policyName=policy_name, target=target)
                                    policies_detached += 1
                                    print(f"   ✅ Detached from {target[:16]}...")
                                except Exception as detach_e:
                                    print(f"   ❌ Failed to detach from {target[:16]}...: {str(detach_e)}")
                                    detach_success = False

                            # If all detachments succeeded, try to delete the policy
                            if detach_success:
                                print("   🗑️  All targets detached, deleting policy...")
                                delete_success = safe_delete(
                                    iot.delete_policy, "Policy", policy_name, debug=debug, policyName=policy_name
                                )

                                if delete_success:
                                    policies_deleted += 1
                                else:
                                    policies_skipped += 1
                            else:
                                print("   ⚠️  Some detachments failed, skipping policy deletion")
                                policies_skipped += 1

                except Exception as e:
                    print(get_message("error_checking_policy", USER_LANG).format(policy_name, str(e)))
                    policies_skipped += 1
                    if debug:
                        import traceback

                        traceback.print_exc()
            else:
                if debug:
                    print(get_message("policy_no_sample_patterns", USER_LANG).format(policy_name))

        print(f"\n{get_message('policy_cleanup_summary', USER_LANG)}")
        print(get_message("deleted_policies", USER_LANG).format(policies_deleted))
        print(f"   🔗 Detached: {policies_detached} policy attachments")
        print(get_message("skipped_policies", USER_LANG).format(policies_skipped))

        if policies_skipped > 0:
            print(f"\n{get_message('skipped_policies_note', USER_LANG)}")
            print(get_message("policies_cleanup_auto", USER_LANG))
            print(get_message("policies_manual_cleanup", USER_LANG))

    except Exception as e:
        print(get_message("error_generic", USER_LANG).format(f"during policy cleanup: {str(e)}"))
        if debug:
            import traceback

            traceback.print_exc()


def cleanup_sample_thing_groups(iot, debug=False):
    """Clean up sample Thing Groups with detailed API logging"""
    print(f"\n{get_message('step4_title', USER_LANG)}")
    print(get_message("step_separator", USER_LANG))

    try:
        # List Thing Groups
        if debug:
            print(get_message("listing_thing_groups", USER_LANG))

        list_response, success = safe_operation(iot, iot.list_thing_groups, "List all Thing Groups", debug=debug)

        if not success:
            return

        thing_groups = list_response.get("thingGroups", [])
        sample_groups = [g for g in thing_groups if g["groupName"] in SAMPLE_THING_GROUPS]

        print(get_message("found_sample_groups", USER_LANG).format(len(sample_groups)))

        for group in sample_groups:
            group_name = group["groupName"]
            print(f"\n{get_message('deleting_thing_group', USER_LANG).format(group_name)}")
            safe_delete(iot.delete_thing_group, "Thing Group", group_name, debug=debug, thingGroupName=group_name)

    except Exception as e:
        print(get_message("error_generic", USER_LANG).format(f"cleaning up Thing Groups: {str(e)}"))
        if debug:
            import traceback

            traceback.print_exc()


def cleanup_sample_thing_types(iot, debug=False):
    """Clean up sample Thing Types (requires deprecation + 5-minute wait + deletion)"""
    print(f"\n{get_message('step5_title', USER_LANG)}")
    print(get_message("step_separator", USER_LANG))

    try:
        # List Thing Types
        if debug:
            print(get_message("listing_thing_types", USER_LANG))

        list_response, success = safe_operation(iot, iot.list_thing_types, "List all Thing Types", debug=debug)

        if not success:
            return

        thing_types = list_response.get("thingTypes", [])
        sample_types = [t for t in thing_types if t["thingTypeName"] in SAMPLE_THING_TYPES]

        print(get_message("found_sample_types", USER_LANG).format(len(sample_types)))

        if not sample_types:
            print(get_message("no_sample_types", USER_LANG))
            return

        # Check if any Thing Types are already deprecated
        deprecated_types = []
        active_types = []

        for thing_type in sample_types:
            thing_type_name = thing_type["thingTypeName"]

            # Check current status
            try:
                describe_response, success = safe_operation(
                    iot,
                    iot.describe_thing_type,
                    f"Check status of Thing Type {thing_type_name}",
                    debug=debug,
                    thingTypeName=thing_type_name,
                )

                if success and describe_response:
                    thing_type_metadata = describe_response.get("thingTypeMetadata", {})
                    deprecated = thing_type_metadata.get("deprecated", False)
                    deprecation_date = thing_type_metadata.get("deprecationDate")

                    if deprecated:
                        deprecated_types.append({"name": thing_type_name, "deprecation_date": deprecation_date})
                        print(get_message("thing_type_deprecated", USER_LANG).format(thing_type_name, deprecation_date))
                    else:
                        active_types.append(thing_type_name)
                        print(get_message("thing_type_active", USER_LANG).format(thing_type_name))

            except Exception as e:
                print(get_message("could_not_check_status", USER_LANG).format(thing_type_name, str(e)))
                active_types.append(thing_type_name)  # Assume active if we can't check

        # Step 1: Deprecate active Thing Types
        newly_deprecated = []
        if active_types:
            print(f"\n{get_message('deprecating_active_types', USER_LANG).format(len(active_types))}")

            for thing_type_name in active_types:
                print(f"\n{get_message('deprecating_thing_type', USER_LANG).format(thing_type_name)}")
                deprecate_response, success = safe_operation(
                    iot,
                    iot.deprecate_thing_type,
                    f"Deprecate Thing Type {thing_type_name}",
                    debug=debug,
                    thingTypeName=thing_type_name,
                    undoDeprecate=False,
                )

                if success:
                    print(get_message("thing_type_deprecated_success", USER_LANG).format(thing_type_name))
                    newly_deprecated.append(thing_type_name)
                else:
                    print(get_message("could_not_deprecate", USER_LANG).format(thing_type_name))

        # Step 2: Handle the 5-minute waiting period
        all_deprecated = deprecated_types + [{"name": name, "deprecation_date": "just now"} for name in newly_deprecated]

        if all_deprecated:
            print(f"\n{get_message('aws_constraint_5min', USER_LANG)}")
            print(get_message("thing_types_to_delete", USER_LANG))
            for item in all_deprecated:
                print(get_message("deprecated_item", USER_LANG).format(item["name"], item["deprecation_date"]))

            print(f"\n{get_message('deletion_options', USER_LANG)}")
            print(get_message("wait_5min_delete", USER_LANG))
            print(get_message("skip_deletion", USER_LANG))
            print(get_message("try_deletion_now", USER_LANG))

            while True:
                choice = input(f"\n{get_message('select_option_1_3', USER_LANG)}").strip()

                if choice == "1":
                    print(f"\n{get_message('waiting_5min', USER_LANG)}")
                    print(get_message("constraint_explanation", USER_LANG))

                    # Show countdown
                    import time

                    wait_seconds = 300  # 5 minutes
                    for remaining in range(wait_seconds, 0, -30):
                        minutes = remaining // 60
                        seconds = remaining % 60
                        print(get_message("time_remaining", USER_LANG).format(minutes, seconds))
                        time.sleep(30)  # nosemgrep: arbitrary-sleep

                    print(get_message("wait_completed", USER_LANG))
                    break

                elif choice == "2":
                    print(get_message("skipping_deletion", USER_LANG))
                    print(get_message("deletion_tip", USER_LANG))
                    print(get_message("types_ready_deletion", USER_LANG))
                    return

                elif choice == "3":
                    print(get_message("attempting_deletion_now", USER_LANG))
                    break

                else:
                    print(get_message("invalid_choice_1_3", USER_LANG))

            # Step 3: Delete the deprecated Thing Types
            print(f"\n{get_message('deleting_deprecated_types', USER_LANG)}")

            for item in all_deprecated:
                thing_type_name = item["name"]
                print(f"\n{get_message('attempting_delete_type', USER_LANG).format(thing_type_name)}")

                delete_success = safe_delete(
                    iot.delete_thing_type, "Thing Type", thing_type_name, debug=debug, thingTypeName=thing_type_name
                )

                if not delete_success:
                    print(get_message("deletion_failed_timing", USER_LANG))
                    print(get_message("type_ready_deletion", USER_LANG).format(thing_type_name))

    except KeyboardInterrupt:
        print(f"\n\n{get_message('cleanup_interrupted', USER_LANG)}")
        print(get_message("types_deprecated_delete_later", USER_LANG))
    except Exception as e:
        print(get_message("error_generic", USER_LANG).format(f"cleaning up Thing Types: {str(e)}"))
        if debug:
            import traceback

            traceback.print_exc()


def cleanup_sample_shadows(iot, debug=False):
    """Clean up device shadows for sample Things"""
    print(f"\n{get_message('step6_title', USER_LANG)}")
    print(get_message("step_separator", USER_LANG))

    print(get_message("shadows_auto_cleanup", USER_LANG))
    print(get_message("no_manual_shadow_cleanup", USER_LANG))

    if debug:
        print(get_message("debug_shadow_skipped", USER_LANG))

    print(get_message("shadow_cleanup_completed", USER_LANG))


def cleanup_sample_rules(iot, debug=False):
    """Clean up IoT rules that might have been created during learning"""
    print(f"\n{get_message('step7_title', USER_LANG)}")
    print(get_message("step_separator", USER_LANG))

    try:
        # List all rules
        if debug:
            print(get_message("debug_listing_rules", USER_LANG))

        response = iot.list_topic_rules()
        rules = response.get("rules", [])

        # Look for rules that appear to be sample/learning rules
        sample_rule_patterns = ["sample", "test", "demo", "learning", "device"]
        rules_deleted = 0

        for rule in rules:
            rule_name = rule["ruleName"]

            # Check if rule name contains sample patterns (case insensitive)
            is_sample_rule = any(pattern.lower() in rule_name.lower() for pattern in sample_rule_patterns)

            if is_sample_rule:
                try:
                    if debug:
                        print(get_message("debug_deleting_rule", USER_LANG).format(rule_name))

                    iot.delete_topic_rule(ruleName=rule_name)
                    print(get_message("deleted_rule", USER_LANG).format(rule_name))
                    rules_deleted += 1

                except Exception as e:
                    print(get_message("error_deleting_rule", USER_LANG).format(rule_name, str(e)))
                    if debug:
                        import traceback

                        traceback.print_exc()

        if rules_deleted == 0:
            print(get_message("no_sample_rules", USER_LANG))
        else:
            print(get_message("rules_cleanup_summary", USER_LANG).format(rules_deleted))

    except Exception as e:
        print(get_message("error_generic", USER_LANG).format(f"during rules cleanup: {str(e)}"))
        if debug:
            import traceback

            traceback.print_exc()


def cleanup_local_files(debug=False):
    """Clean up local certificate files with detailed logging"""
    print(f"\n{get_message('step8_title', USER_LANG)}")
    print(get_message("step_separator", USER_LANG))

    # Clean up main certificates directory
    cert_dir = os.path.join(os.getcwd(), "certificates")

    if debug:
        print(get_message("checking_cert_directory", USER_LANG).format(cert_dir))

    if os.path.exists(cert_dir):
        try:
            if debug:
                # Show what's being deleted
                print(get_message("cert_directory_contents", USER_LANG))
                for root, dirs, files in os.walk(cert_dir):
                    level = root.replace(cert_dir, "").count(os.sep)
                    indent = " " * 2 * level
                    print(f"{indent}{os.path.basename(root)}/")
                    subindent = " " * 2 * (level + 1)
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        print(f"{subindent}{file} ({file_size} bytes)")

            shutil.rmtree(cert_dir)
            print(get_message("removed_cert_directory", USER_LANG).format(cert_dir))

            if debug:
                print(get_message("directory_deleted_success", USER_LANG).format(cert_dir))

        except Exception as e:
            print(get_message("error_removing_cert_dir", USER_LANG).format(str(e)))
            if debug:
                import traceback

                traceback.print_exc()
    else:
        print(get_message("no_cert_directory", USER_LANG))
        if debug:
            print(get_message("directory_not_exist", USER_LANG).format(cert_dir))

    # Clean up sample-certs directory (created by OpenSSL certificate generation)
    sample_cert_dir = os.path.join(os.getcwd(), "sample-certs")

    if debug:
        print(get_message("checking_sample_cert_dir", USER_LANG).format(sample_cert_dir))

    if os.path.exists(sample_cert_dir):
        try:
            if debug:
                # Show what's being deleted
                print(get_message("sample_cert_contents", USER_LANG))
                for root, dirs, files in os.walk(sample_cert_dir):
                    level = root.replace(sample_cert_dir, "").count(os.sep)
                    indent = " " * 2 * level
                    print(f"{indent}{os.path.basename(root)}/")
                    subindent = " " * 2 * (level + 1)
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        print(f"{subindent}{file} ({file_size} bytes)")

            shutil.rmtree(sample_cert_dir)
            print(get_message("removed_sample_cert_dir", USER_LANG).format(sample_cert_dir))

            if debug:
                print(get_message("directory_deleted_success", USER_LANG).format(sample_cert_dir))

        except Exception as e:
            print(get_message("error_removing_sample_dir", USER_LANG).format(str(e)))
            if debug:
                import traceback

                traceback.print_exc()
    else:
        print(get_message("no_sample_cert_dir", USER_LANG))
        if debug:
            print(get_message("directory_not_exist", USER_LANG).format(sample_cert_dir))


def print_summary():
    """Print cleanup summary"""
    print(f"\n{get_message('cleanup_summary_title', USER_LANG)}")
    print(get_message("summary_separator", USER_LANG))
    print(get_message("things_cleaned", USER_LANG))
    print(get_message("certificates_cleaned", USER_LANG))
    print(get_message("groups_cleaned", USER_LANG))
    print(get_message("types_cleaned", USER_LANG))
    print(get_message("local_files_cleaned", USER_LANG))
    print(get_message("device_state_cleaned", USER_LANG))
    print(get_message("policies_manual_review", USER_LANG))
    print(f"\n{get_message('account_clean', USER_LANG)}")


def main():
    global USER_LANG, DEBUG_MODE

    # Get user's preferred language
    USER_LANG = get_language()

    # Check for debug flag
    DEBUG_MODE = "--debug" in sys.argv or "-d" in sys.argv

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

    print(get_message("description_intro", USER_LANG))
    for script in get_message("setup_scripts", USER_LANG):
        print(script)
    print(f"\n{get_message('no_affect_other', USER_LANG)}")

    if DEBUG_MODE:
        print(f"\n{get_message('debug_enabled', USER_LANG)}")
        for feature in get_message("debug_features", USER_LANG):
            print(feature)
    else:
        print(f"\n{get_message('tip', USER_LANG)}")

    print(get_message("separator", USER_LANG))

    print(f"\n{get_message('resources_to_cleanup', USER_LANG)}")
    print(get_message("things_prefix", USER_LANG).format(SAMPLE_THING_PREFIX))
    print(get_message("thing_types", USER_LANG).format(", ".join(SAMPLE_THING_TYPES)))
    print(get_message("thing_groups", USER_LANG).format(", ".join(SAMPLE_THING_GROUPS)))
    print(get_message("certificates_attached", USER_LANG))
    print(get_message("local_cert_files", USER_LANG))
    print(get_message("policies_manual_review", USER_LANG))

    confirm = input(f"\n{get_message('continue_cleanup', USER_LANG)}").strip().lower()
    if confirm != "y":
        print(get_message("cleanup_cancelled", USER_LANG))
        return

    try:
        iot = boto3.client("iot")
        print(get_message("client_initialized", USER_LANG))

        if DEBUG_MODE:
            print(get_message("debug_client_config", USER_LANG))
            print(f"   {get_message('service_label', USER_LANG)}: {iot.meta.service_model.service_name}")
            print(f"   {get_message('api_version_label', USER_LANG)}: {iot.meta.service_model.api_version}")

        print(f"\n{get_message('learning_moment_title', USER_LANG)}")
        print(get_message("learning_moment_content", USER_LANG))
        print(f"\n{get_message('next_cleanup', USER_LANG)}")
        input(get_message("press_enter_continue", USER_LANG))

        # Execute cleanup steps in order with debug flag
        cleanup_sample_things(iot, debug=DEBUG_MODE)
        cleanup_orphaned_certificates(iot, debug=DEBUG_MODE)
        cleanup_sample_policies(iot, debug=DEBUG_MODE)
        cleanup_sample_thing_groups(iot, debug=DEBUG_MODE)
        cleanup_sample_thing_types(iot, debug=DEBUG_MODE)
        cleanup_sample_shadows(iot, debug=DEBUG_MODE)
        cleanup_sample_rules(iot, debug=DEBUG_MODE)
        cleanup_local_files(debug=DEBUG_MODE)
        print_summary()

        if DEBUG_MODE:
            print(f"\n{get_message('debug_cleanup_completed', USER_LANG)}")

    except Exception as e:
        print(get_message("error_generic", USER_LANG).format(str(e)))
        if DEBUG_MODE:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()

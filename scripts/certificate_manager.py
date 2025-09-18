#!/usr/bin/env python3
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import re
import sys
import time

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, NoRegionError

# Simple translation system for learning content
MESSAGES = {
    "en": {
        "title": "🔐 AWS IoT Certificate & Policy Manager",
        "separator": "=" * 50,
        "aws_config": "📍 AWS Configuration:",
        "account_id": "Account ID",
        "region": "Region",
        "aws_context_error": "⚠️ Could not retrieve AWS context:",
        "aws_credentials_reminder": "   Make sure AWS credentials are configured",
        "description_intro": "This script teaches you AWS IoT security concepts:",
        "security_concepts": [
            "• X.509 certificates for device authentication",
            "• Certificate-to-Thing attachment",
            "• IoT policies for authorization",
            "• Policy attachment and detachment",
            "• External certificate registration",
            "• Complete API details for each operation",
        ],
        "debug_enabled": "🔍 DEBUG MODE ENABLED",
        "debug_features": [
            "• Enhanced API request/response logging",
            "• Full error details and tracebacks",
            "• Extended educational information",
        ],
        "tip": "💡 Tip: Use --debug or -d flag for enhanced API logging",
        "client_initialized": "✅ AWS IoT client initialized",
        "client_error": "❌ Error initializing AWS IoT client:",
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
        "press_enter": "Press Enter to continue...",
        "goodbye": "👋 Goodbye!",
        "main_menu": "📋 Main Menu:",
        "menu_options": [
            "1. Create AWS IoT Certificate & Attach to Thing (+ Optional Policy)",
            "2. Register External Certificate & Attach to Thing (+ Optional Policy)",
            "3. Attach Policy to Existing Certificate",
            "4. Detach Policy from Certificate",
            "5. Enable/Disable Certificate",
            "6. Exit",
        ],
        "select_option": "Select option (1-6): ",
        "invalid_choice": "❌ Invalid choice. Please select 1-6.",
        "learning_moments": {
            "security_foundation": {
                "title": "📚 LEARNING MOMENT: IoT Security Foundation",
                "content": "AWS IoT security is built on X.509 certificates for device authentication and IoT policies for authorization. Certificates uniquely identify devices, while policies define what actions devices can perform. Understanding this security model is crucial for building secure IoT solutions.",
                "next": "We will explore certificate and policy management operations",
            },
            "certificate_creation": {
                "title": "📚 LEARNING MOMENT: Certificate Creation & Thing Attachment",
                "content": "Creating an AWS IoT certificate establishes a unique digital identity for your device. The certificate contains a public key that AWS IoT uses to authenticate the device, while the private key stays securely on the device. Attaching the certificate to a Thing creates the binding between the device identity and its logical representation in AWS IoT.",
                "next": "We will create a certificate and attach it to a Thing",
            },
            "external_registration": {
                "title": "📚 LEARNING MOMENT: External Certificate Registration",
                "content": "Sometimes you need to use certificates from your own Certificate Authority (CA) or existing PKI infrastructure. AWS IoT allows you to register external certificates, giving you flexibility in certificate management while maintaining security. This is useful for organizations with established certificate policies.",
                "next": "We will register an external certificate with AWS IoT",
            },
            "policy_attachment": {
                "title": "📚 LEARNING MOMENT: Policy Attachment for Authorization",
                "content": "While certificates handle authentication (who you are), IoT policies handle authorization (what you can do). Policies define which MQTT topics a device can publish to, subscribe to, and what AWS IoT operations it can perform. Attaching policies to certificates grants specific permissions to devices.",
                "next": "We will attach a policy to an existing certificate",
            },
            "policy_detachment": {
                "title": "📚 LEARNING MOMENT: Policy Detachment for Permission Management",
                "content": "Sometimes you need to remove specific permissions from a device without deleting the entire certificate. Policy detachment allows you to revoke specific permissions while keeping the device's identity intact. This is useful for changing device roles, troubleshooting permission issues, or implementing security policies.",
                "next": "We will detach a policy from a certificate",
            },
            "certificate_lifecycle": {
                "title": "📚 LEARNING MOMENT: Certificate Lifecycle Management",
                "content": "Certificate status controls whether a device can connect to AWS IoT. ACTIVE certificates allow connections, while INACTIVE certificates block them. This provides immediate security control - you can instantly disable compromised devices or temporarily suspend access without deleting the certificate entirely.",
                "next": "We will manage certificate status (enable/disable)",
            },
        },
        "workflow_titles": {
            "certificate_creation": "🔐 Certificate Creation Workflow",
            "external_registration": "📜 External Certificate Registration Workflow",
            "policy_attachment": "🔗 Policy Attachment Workflow",
            "policy_detachment": "🔓 Policy Detachment Workflow",
            "certificate_status": "🔄 Certificate Status Management",
        },
        "aws_context_info": "🌍 AWS Context Information:",
        "account_id_label": "Account ID",
        "region_label": "Region",
        "aws_context_error_msg": "⚠️ Could not retrieve AWS context:",
        "aws_credentials_config": "   Make sure AWS credentials are configured",
        "policy_to_be_created": "📄 Policy to be created:",
        "policy_name_label": "Name",
        "policy_document_label": "Document",
        "security_warning": "⚠️  SECURITY WARNING:",
        "security_warning_details": [
            "   This policy uses broad permissions for demonstration purposes.",
            "   In production environments:",
            "   • Use specific resource ARNs instead of '*'",
            "   • Add condition statements (IP restrictions, time-based access)",
            "   • Use policy variables like ${iot:Connection.Thing.ThingName}, not yet in scope for this basic learning session",
        ],
        "policy_validation_issues": "🔍 Policy Validation Issues:",
        "certificate_details": "📋 Certificate Details:",
        "certificate_id_label": "Certificate ID",
        "certificate_arn_label": "Certificate ARN",
        "status_active": "Status: ACTIVE",
        "certificate_files_saved": "💾 Certificate files saved to:",
        "certificate_components_created": "🔑 Certificate Components Created:",
        "certificate_components_list": [
            "   • Public Key (for AWS IoT)",
            "   • Private Key (keep secure on device)",
            "   • Certificate PEM (for device authentication)",
        ],
        "thing_already_has_certificates": "⚠️  Thing '{}' already has {} certificate(s) attached:",
        "certificate_id_item": "   {}. Certificate ID: {}",
        "remove_existing_certificates": "Would you like to remove existing certificates? (y/N): ",
        "proceeding_with_multiple": "Proceeding with multiple certificates attached to the same Thing...",
        "attaching_certificate_to_thing": "🔗 Attaching certificate to Thing: {}",
        "policy_options": "📝 Policy Options:",
        "use_existing_policy": "1. Use existing policy",
        "create_new_policy": "2. Create new policy",
        "select_option_1_2": "Select option (1-2): ",
        "invalid_selection_generic": "❌ Invalid selection",
        "enter_valid_number_generic": "❌ Please enter a valid number",
        "select_1_or_2": "❌ Please select 1 or 2",
        "no_existing_policies": "📝 No existing policies found. Creating new policy...",
        "error_listing_policies": "⚠️  Error listing policies:",
        "proceeding_create_new": "Proceeding to create new policy...",
        "enter_new_policy_name": "Enter new policy name: ",
        "policy_name_required": "❌ Policy name is required",
        "policy_already_exists": "⚠️  Policy '{}' already exists",
        "use_different_name": "Would you like to use a different name? (y/N): ",
        "policy_templates": "📝 Policy Templates:",
        "basic_device_policy": "1. Basic Device Policy (connect, publish, subscribe)",
        "readonly_policy": "2. Read-Only Policy (connect, subscribe only)",
        "custom_policy": "3. Custom Policy (enter your own JSON)",
        "select_template_1_3": "Select template (1-3): ",
        "select_1_2_or_3": "❌ Please select 1, 2, or 3",
        "certificate_options": "📋 Certificate Options:",
        "use_existing_cert_file": "1. Use existing certificate file",
        "generate_sample_cert": "2. Generate sample certificate with OpenSSL",
        "invalid_choice_1_2": "❌ Invalid choice. Please select 1-2.",
        "cert_must_be_pem": "Certificate must be in PEM format (.crt or .pem file)",
        "what_happened": "🔄 What happened:",
        "what_happened_steps": [
            "   1. AWS IoT validated your certificate format",
            "   2. Self-signed certificate registered without CA requirement",
            "   3. Certificate status set to ACTIVE",
            "   4. AWS assigned unique Certificate ID and ARN",
            "   5. Certificate is now ready for Thing attachment",
        ],
        "key_difference": "💡 Key Difference:",
        "cleanup_certificate": "🧹 Cleaning up certificate {}...",
        "error_detaching_policies": "❌ Error detaching policies:",
        "removed_local_file": "🗑️  Removed local file:",
        "certificate_cleaned_up": "✅ Certificate {} cleaned up successfully",
        "error_checking_certificates": "❌ Error checking existing certificates:",
        "skipping_file_cleanup": "⚠️ Skipping file cleanup - invalid thing_name:",
        "fetching_things": "ℹ️ Fetching available Things...",
        "available_things": "📱 Available Things ({} found):",
        "and_more": "... and {} more",
        "options_header": "📋 Options:",
        "select_thing_options": [
            "• Enter number (1-{}) to select Thing",
            "• Type 'all' to see all Things",
            "• Type 'manual' to enter Thing name manually",
        ],
        "your_choice": "Your choice: ",
        "all_things": "📱 All Things:",
        "press_enter_continue": "Press Enter to continue...",
        "enter_thing_name": "Enter Thing name: ",
        "invalid_thing_name": "❌ Invalid Thing name. Only alphanumeric characters, hyphens, and underscores allowed.",
        "thing_found": "✅ Thing '{}' found",
        "thing_not_found": "❌ Thing '{}' not found",
        "thing_name_empty": "❌ Thing name cannot be empty",
        "selected_thing": "✅ Selected Thing: {}",
        "invalid_selection": "❌ Invalid selection",
        "enter_valid_number": "❌ Please enter a valid number",
        "enter_number_all_manual": "❌ Please enter a valid number, 'all', or 'manual'",
        "no_things_found": "❌ No Things found. Please run setup_sample_data.py first",
        "error_listing_things": "❌ Error listing Things:",
        "key_difference_details": [
            "   • Used register_certificate_without_ca API",
            "   • No Certificate Authority (CA) registration required",
        ],
        "cert_must_be_pem_info": "Certificate must be in PEM format (.crt or .pem file)",
        "validating_cert_format": "Validating certificate file format...",
        "choose_cert_provision": "Choose how to provide your X.509 certificate:",
        "pem_format_starts_with": "PEM format starts with '-----BEGIN CERTIFICATE-----'",
        "learning_objectives": "🎓 Learning Objectives:",
        "external_cert_objectives": [
            "• Understand difference between AWS-generated vs external certificates",
            "• Learn certificate registration process",
            "• Practice certificate validation and attachment",
            "• Explore register_certificate API",
        ],
        "select_option_1_2_prompt": "Select option (1-2): ",
        "no_things_found_run_setup": "❌ No Things found. Please run setup_sample_data.py first",
        "options_header_simple": "📋 Options:",
        "enter_number_select_thing": "• Enter number (1-{}) to select Thing",
        "type_all_see_things": "• Type 'all' to see all Things",
        "type_manual_enter_name": "• Type 'manual' to enter Thing name manually",
        "all_things_header": "📱 All Things:",
        "invalid_thing_name_chars": "❌ Invalid Thing name. Only alphanumeric characters, hyphens, and underscores allowed.",
        "thing_name_cannot_be_empty": "❌ Thing name cannot be empty",
        "policy_creation_cancelled": "Policy creation cancelled for security reasons",
        "enter_policy_json": "Enter your policy JSON (press Enter twice when done):",
        "policy_to_be_created_header": "📄 Policy to be created:",
        "available_policies": "📋 Available Policies:",
        "invalid_selection_simple": "❌ Invalid selection",
        "enter_valid_number_simple": "❌ Please enter a valid number",
        "no_policies_found_create": "❌ No policies found. Creating one first...",
        "api_details_header": "🔍 API Details:",
        "operation_label": "Operation",
        "http_method_label": "HTTP Method",
        "certificate_status_management": "🔄 Certificate Status Management",
        "learning_objectives_header": "🎓 Learning Objectives:",
        "cert_lifecycle_objectives": [
            "• Understand certificate lifecycle management",
            "• Learn enable/disable operations",
            "• Practice certificate status control",
            "• Explore update_certificate API",
        ],
        "fetching_all_certificates": "🔍 Fetching all certificates...",
        "failed_to_list_certificates": "❌ Failed to list certificates",
        "no_certificates_found": "📋 No certificates found in your account",
        "create_certificates_first": "💡 Create certificates first using options 1 or 2",
        "invalid_selection_cert": "❌ Invalid selection",
        "enter_valid_number_cert": "❌ Please enter a valid number",
        "selected_certificate": "📝 Selected Certificate:",
        "certificate_id_short": "ID",
        "attached_to_thing": "Attached to Thing",
        "none_label": "None",
        "available_action": "🔄 Available Action:",
        "enable_certificate": "Enable certificate (set status to ACTIVE)",
        "disable_certificate": "Disable certificate (set status to INACTIVE)",
        "operation_cancelled": "❌ Operation cancelled",
        "certificate_action_success": "✅ Certificate {}d successfully!",
        "status_change_summary": "📊 Status Change Summary:",
        "new_status_label": "New Status",
        "what_this_means": "💡 What this means:",
        "active_cert_meanings": [
            "• Certificate can now be used for device authentication",
            "• Devices with this certificate can connect to AWS IoT",
            "• MQTT connections using this certificate will succeed",
        ],
        "inactive_cert_meanings": [
            "• Certificate is now disabled for authentication",
            "• Devices with this certificate cannot connect to AWS IoT",
            "• MQTT connections using this certificate will fail",
        ],
        "next_steps": "🔍 Next Steps:",
        "next_steps_list": [
            "• Use iot_registry_explorer.py to verify the status change",
            "• Test MQTT connection to see the effect",
        ],
        "reenable_when_ready": "• Re-enable when ready to restore device connectivity",
        "failed_to_action_cert": "❌ Failed to {} certificate",
        "policy_attachment_workflow": "🔗 Policy Attachment Workflow",
        "no_certificates_for_thing": "❌ No certificates found for Thing '{}'",
        "tip_run_option_1": "💡 Tip: Run option 1 first to create and attach a certificate",
        "using_certificate": "✅ Using certificate: {}",
        "multiple_certificates_found": "📋 Multiple certificates found:",
        "certificate_successfully_attached": "✅ Certificate successfully attached to {}",
        "thing_can_use_cert": "The Thing can now use this certificate for authentication",
        "certificate_generated_successfully": "✅ Certificate generated successfully",
        "certificate_details_header": "📊 Certificate Details:",
        "cert_type_self_signed": "• Type: Self-signed X.509",
        "cert_algorithm": "• Algorithm: RSA 2048-bit",
        "cert_validity": "• Validity: 365 days",
        "cert_usage": "• Usage: Device authentication only",
        "cert_location": "• Location: {}",
        "proceed_with_policy_warnings": "Proceed with this policy despite security warnings? (y/N): ",
        "confirm_action": "Confirm {} certificate? (y/N): ",
        "available_things_count": "📱 Available Things ({} found):",
        "selected_thing_prefix": "✅ Selected Thing: {}",
        "thing_found_check": "✅ Thing '{}' found",
        "thing_not_found_check": "❌ Thing '{}' not found",
        "learning_moment_cert_process": "📚 LEARNING MOMENT: Certificate Creation Process",
        "cert_creation_explanation": "We will now create an X.509 certificate using AWS IoT's certificate authority. This generates a unique public/private key pair where AWS keeps the public key and provides you with both the certificate and private key for your device.",
        "next_creating_cert": "🔄 NEXT: Creating certificate with AWS IoT",
        "found_existing_policies": "📋 Found {} existing policies:",
        "api_response_found_certs": "📤 API Response: Found {} certificate(s)",
        "found_certificates_count": "📋 Found {} certificate(s):",
        "no_certificates_for_thing_msg": "❌ No certificates found for Thing '{}'",
        "tip_run_option_1_msg": "💡 Tip: Run option 1 first to create and attach a certificate",
        "using_certificate_msg": "✅ Using certificate: {}",
        "multiple_certificates_found_msg": "📋 Multiple certificates found:",
        "no_policies_found_account": "📋 No policies found in your account",
        "create_policies_first": "💡 Create policies first using options 1, 2, or 3",
        "found_policies_count": "📋 Found {} policy(ies):",
        "no_certs_with_policy": "📋 No certificates found with policy '{}' attached",
        "policy_not_attached": "💡 This policy is not currently attached to any certificates",
        "found_certs_with_policy": "📋 Found {} certificate(s) with this policy:",
        "openssl_not_found": "❌ OpenSSL not found. Please install OpenSSL:",
        "install_openssl_macos": "   macOS: brew install openssl",
        "install_openssl_ubuntu": "   Ubuntu: sudo apt-get install openssl",
        "file_not_found": "❌ File not found: {}",
        "multiple_certs_warning": "⚠️  Multiple certificates found. Only the first will be used.",
        "cert_format_validated": "✅ Certificate file format validated",
        "cert_file_not_found": "❌ Certificate file not found",
        "found_private_key": "🔍 Found corresponding private key: {}",
        "private_key_saved": "🔑 Private key saved: {}",
        "private_key_not_found": "⚠️  Private key not found at: {}",
        "enter_key_path": "Enter path to private key file (or press Enter to skip): ",
        "key_file_not_found": "❌ Key file not found: {}",
        "private_key_not_saved": "⚠️  Private key not saved - MQTT client may not work",
        "key_within_working_dir": "⚠️ Key file must be within current working directory",
        "external_cert_registration_moment": "📚 LEARNING MOMENT: External Certificate Registration",
        "external_cert_explanation": "We will now register your external certificate with AWS IoT. Unlike AWS-generated certificates, this process registers your existing certificate without AWS creating new keys. Your private key remains under your control while AWS validates and registers the public certificate.",
        "next_registering_cert": "🔄 NEXT: Registering certificate with AWS IoT",
        "step_creating_certificate": "Creating X.509 Certificate",
        "step_attaching_certificate": "Attaching Certificate to Thing",
        "step_policy_management": "IoT Policy Management",
        "step_attaching_policy": "Attaching Policy to Certificate",
        "certificates_for_auth": "X.509 certificates are used for device authentication in AWS IoT",
        "cert_contains_keypair": "Each certificate contains a public/private key pair",
        "api_description_create_cert": "Creates a new X.509 certificate with public/private key pair",
        "input_params_set_active": "setAsActive: true (activates certificate immediately)",
        "expected_output_cert": "certificateArn, certificateId, certificatePem, keyPair (public/private keys)",
        "learning_moment_cert_attachment": "📚 LEARNING MOMENT: Certificate-Thing Attachment",
        "cert_attachment_explanation": "Now we'll attach the certificate to your selected Thing. This creates the secure binding between the certificate identity and the logical device representation in AWS IoT. Once attached, the device can use this certificate to authenticate with AWS IoT Core.",
        "next_attaching_cert": "🔄 NEXT: Attaching certificate to Thing",
        "press_enter_continue_generic": "Press Enter to continue...",
        "api_path_label": "API Path",
        "description_label": "Description",
        "input_parameters_label": "Input Parameters",
        "expected_output_label": "Expected Output",
        "creating_cert_keypair": "Creating certificate and key pair...",
        "cert_keypair_completed": "Creating certificate and key pair completed successfully",
        "attaching_cert_to_thing": "Attaching certificate to Thing...",
        "cert_attachment_completed": "Attaching certificate to Thing completed successfully",
        "iot_policies_define_actions": "IoT Policies define what actions a certificate can perform",
        "create_new_or_existing": "You can create a new policy or use an existing one",
        "policy_attachment_explanation": "Policy attachment grants specific permissions to certificates",
        "cert_now_has_permissions": "Certificate now has the permissions defined in the policy",
        "operation_completed_successfully": "{} completed successfully",
        "operation_completed": "{} completed",
        "output_label": "Output",
        "api_description_attach_thing": "Attaches a certificate (principal) to a Thing for authentication",
        "empty_response_success": "Empty response on success",
        "attaching_cert_to_thing_name": "Attaching certificate to {}",
        "policies_must_be_attached": "Policies must be attached to certificates to grant permissions",
        "without_policy_no_operations": "Without a policy, the certificate cannot perform any IoT operations",
        "certs_must_be_attached": "Certificates must be attached to Things for device authentication",
        "creates_secure_relationship": "This creates a secure relationship between the certificate and the IoT device",
        "cert_will_be_attached": "Certificate will be attached to: {}",
        "would_like_create_policy": "Would you like to create and attach a policy? (y/N): ",
        "creates_self_signed_cert": "This creates a self-signed certificate for learning purposes",
        "production_use_trusted_ca": "In production, use certificates from a trusted Certificate Authority",
        "registering_external_cert": "Registering external certificate with AWS IoT...",
        "registers_without_new_keys": "This registers your certificate without AWS generating new keys",
        "private_key_stays_with_you": "Your private key stays with you - AWS only gets the public certificate",
        "proceed_despite_warnings": "Proceed with this policy despite security warnings? (y/N): ",
        "do_you_want_to_action_cert": "Do you want to {} this certificate? (y/N): ",
        "detach_policy_from_cert": "Detach policy '{}' from this certificate? (y/N): ",
        "attach_existing_policy": "Would you like to attach an existing policy? (y/N): ",
        "continue_anyway": "Continue anyway? (y/N): ",
        "warning_no_crt_pem": "⚠️  Warning: File doesn't have .crt or .pem extension",
        "certificate_file_label": "Certificate",
        "private_key_file_label": "Private Key",
        "public_key_file_label": "Public Key",
        "press_enter_continue_simple": "Press Enter to continue...",
        "invalid_selection_enter_range": "❌ Invalid selection. Please enter 1-{}",
        "enter_valid_number_all_manual": "❌ Please enter a valid number, 'all', or 'manual'",
        "selected_existing_policy": "✅ Selected existing policy: {}",
        "using_existing_policy": "✅ Using existing policy: {}",
        "policy_name_available": "✅ Policy name '{}' is available",
        "error_checking_policy": "❌ Error checking policy: {}",
        "select_policy_template": "Select policy template (1-3): ",
        "invalid_json_error": "❌ Invalid JSON: {}",
        "name_label_simple": "Name",
        "document_label_simple": "Document",
        "error_listing_policies_simple": "❌ Error listing policies: {}",
        "certificate_id_simple": "Certificate ID",
        "error_simple": "❌ Error: {}",
        "invalid_selection_simple_msg": "❌ Invalid selection",
        "enter_valid_number_simple_msg": "❌ Please enter a valid number",
        "current_status_label": "Current Status",
        "arn_label": "ARN",
        "operation_cancelled_simple": "❌ Operation cancelled",
        "previous_status_label": "Previous Status",
        "new_status_label_simple": "New Status",
        "what_this_means_simple": "💡 What this means:",
        "cert_can_be_used_auth": "• Certificate can now be used for device authentication",
        "devices_can_connect": "• Devices with this certificate can connect to AWS IoT",
        "mqtt_connections_succeed": "• MQTT connections using this certificate will succeed",
        "cert_disabled_auth": "• Certificate is now disabled for authentication",
        "devices_cannot_connect": "• Devices with this certificate cannot connect to AWS IoT",
        "mqtt_connections_fail": "• MQTT connections using this certificate will fail",
        "next_steps_simple": "🔍 Next Steps:",
        "use_registry_explorer": "• Use iot_registry_explorer.py to verify the status change",
        "test_mqtt_connection": "• Test MQTT connection to see the effect",
        "reenable_when_ready_simple": "• Re-enable when ready to restore device connectivity",
        "failed_to_action_certificate": "❌ Failed to {} certificate",
        "policy_attachment_workflow_title": "🔗 Policy Attachment Workflow",
        "checking_certificates_for_thing": "🔍 Checking certificates for Thing: {}",
        "select_certificate_prompt": "Select certificate (1-{}): ",
        "enter_cert_name_default": "\nEnter certificate name [default: sample-device]: ",
        "enter_cert_path": "\nEnter path to certificate file: ",
        "cert_path_required": "❌ Certificate path is required",
        "failed_to_list_policies": "❌ Failed to list policies",
        "failed_to_list_policy_targets": "❌ Failed to list policy targets",
        "failed_to_detach_policy": "❌ Failed to detach policy",
        "failed_to_create_certificate": "❌ Failed to create certificate. Exiting.",
        "failed_to_attach_certificate": "❌ Failed to attach certificate to Thing. Exiting.",
        "cert_name_invalid_chars": "❌ Certificate name can only contain letters, numbers, hyphens, and underscores",
        "invalid_cert_format_start": "❌ Invalid certificate format. Must be PEM format starting with '-----BEGIN CERTIFICATE-----'",
        "tip_convert_der_to_pem": "💡 Tip: Convert DER to PEM using: openssl x509 -inform DER -outform PEM -in cert.der -out cert.pem",
        "invalid_cert_format_end": "❌ Invalid certificate format. Must end with '-----END CERTIFICATE-----'",
        "permission_denied_cert": "❌ Permission denied reading certificate file",
        "cert_encoding_error": "❌ Certificate file encoding error - file may be binary",
        "cert_file_required": "❌ Certificate file required. Exiting workflow.",
        "cert_validation_failed": "❌ Certificate validation failed. Exiting workflow.",
        "thing_selection_required": "❌ Thing selection required. Exiting workflow.",
        "cert_registration_failed": "❌ Certificate registration failed. Exiting workflow.",
        "skipping_file_save_invalid_name": "⚠️ Skipping file save due to invalid thing name: {}",
        "cert_registered_files_not_saved": "❌ Certificate registered but local files not saved due to security validation.",
        "cert_attachment_failed": "❌ Certificate attachment failed. Exiting workflow.",
        "policy_detachment_workflow": "🔓 Policy Detachment Workflow",
        "learning_objectives_header_simple": "🎓 Learning Objectives:",
        "understand_policy_detachment": "• Understand policy detachment process",
        "learn_find_devices_by_policy": "• Learn to find devices by policy",
        "practice_cert_policy_mgmt": "• Practice certificate-policy relationship management",
        "explore_detach_policy_api": "• Explore detach_policy API",
        "fetching_all_policies": "🔍 Fetching all policies...",
        "detachment_summary": "📝 Detachment Summary:",
        "policy_label_simple": "Policy",
        "policy_detached_successfully": "✅ Policy detached successfully!",
        "detachment_results": "📊 Detachment Results:",
        "policy_removed_from_cert": "Policy '{}' removed from certificate {}",
        "thing_cert_no_longer_has_policy": "Thing '{}' certificate no longer has this policy",
        "what_this_means_detach": "💡 What this means:",
        "cert_no_longer_perform_actions": "• Certificate can no longer perform actions defined in '{}'",
        "device_may_lose_permissions": "• Device may lose specific permissions (connect, publish, subscribe)",
        "other_policies_still_apply": "• Other policies attached to this certificate still apply",
        "policy_still_exists": "• Policy still exists and can be attached to other certificates",
        "next_steps_detach": "🔍 Next Steps:",
        "use_registry_explorer_verify": "• Use iot_registry_explorer.py to verify policy detachment",
        "test_device_connectivity": "• Test device connectivity to see permission changes",
        "attach_different_policy": "• Attach different policy if needed using option 3",
        "setup_complete": "Setup Complete! 🎉",
        "summary_created_configured": "📊 Summary of what was created/configured:",
        "certificate_source_label": "🏷️  Certificate Source",
        "attached_to_thing_label": "📱 Attached to Thing",
        "policy_attached_label": "📄 Policy Attached",
        "what_you_can_explore": "🔍 What you can explore now:",
        "use_registry_explorer_view": "• Use iot_registry_explorer.py to view the certificate",
        "check_thing_attached_cert": "• Check the Thing to see its attached certificate",
        "review_policy_permissions": "• Review the policy permissions",
        "compare_external_vs_aws": "• Compare external vs AWS-generated certificate workflows",
        "key_learning_points": "💡 Key Learning Points:",
        "certs_provide_device_identity": "• Certificates provide device identity and authentication",
        "things_represent_iot_devices": "• Things represent your IoT devices in AWS",
        "policies_define_actions": "• Policies define what actions certificates can perform",
        "external_certs_integrate_pki": "• External certificates integrate with existing PKI infrastructure",
        "register_vs_create_api": "• register_certificate API vs create_keys_and_certificate API",
        "all_components_work_together": "• All components work together for secure IoT communication",
        "generating_cert_files": "🔑 Generating certificate files:",
        "private_key_label": "Private Key",
        "certificate_label": "Certificate",
        "running_openssl_command": "🔄 Running OpenSSL command...",
        "command_label": "📥 Command",
        "certificate_information": "🔍 Certificate Information:",
        "windows_openssl_download": "   Windows: Download from https://slproweb.com/products/Win32OpenSSL.html",
        "cert_file_within_working_dir": "⚠️ Certificate file must be within current working directory",
        "cert_file_content_preview": "📥 Certificate file content preview:",
        "cert_validation_results": "📊 Certificate validation results:",
        "format_pem_check": "   • Format: PEM ✅",
        "certificate_count_label": "   • Certificate count",
        "file_size_label": "   • File size",
        "cert_registration_results": "📋 Certificate Registration Results:",
        "source_external": "   Source: External (user-provided)",
        "registration_method": "   Registration Method: register_certificate API",
        "perfect_for_self_signed": "   • Perfect for self-signed certificates and learning",
        "production_use_ca_signed": "   • Production systems typically use CA-signed certificates",
        "saving_cert_files_locally": "💾 Saving certificate files locally for MQTT client...",
        "key_file_within_working_dir": "⚠️ Key file must be within current working directory",
        "listing_all_certificates": "Listing all certificates",
        "no_thing_attached": "(No Thing attached)",
        "created_label": "Created",
        "unknown_label": "Unknown",
        "active_status": "ACTIVE",
        "inactive_status": "INACTIVE",
        "api_desc_create_keys_cert": "Creates a new X.509 certificate with public/private key pair",
        "api_input_set_active": "setAsActive: true (activates certificate immediately)",
        "api_output_cert_keypair": "certificateArn, certificateId, certificatePem, keyPair (public/private keys)",
        "api_desc_attach_thing_principal": "Attaches a certificate (principal) to a Thing for authentication",
        "api_output_empty_success": "Empty response on success",
        "api_desc_create_policy": "Creates an IoT policy with specified permissions",
        "api_input_policy_name_doc": "policyName, policyDocument (JSON permissions)",
        "api_output_policy_details": "policyName, policyArn, policyDocument, policyVersionId",
        "api_desc_attach_policy": "Attaches an IoT policy to a certificate for authorization",
        "api_input_policy_cert": "policyName, target (certificate ARN)",
        "api_desc_list_certificates": "Lists all certificates in the AWS account",
        "api_output_certificates_list": "certificates[] with certificateId, certificateArn, status, creationDate",
        "api_desc_update_certificate": "Updates certificate status (ACTIVE/INACTIVE)",
        "api_input_cert_id_status": "certificateId, newStatus",
        "api_desc_list_policies": "Lists all IoT policies in the AWS account",
        "api_output_policies_list": "policies[] with policyName, policyArn",
        "api_desc_list_targets_for_policy": "Lists all certificates that have a specific policy attached",
        "api_input_policy_name": "policyName",
        "api_output_target_arns": "targetArns[] (certificate ARNs)",
        "api_desc_detach_policy": "Detaches an IoT policy from a certificate",
        "api_desc_register_cert_without_ca": "Registers an external certificate with AWS IoT without CA verification",
        "api_input_optional_pagination": "None (optional: pageSize, marker, ascendingOrder)",
        "api_input_cert_pem_active": "certificatePem (the certificate in PEM format), setAsActive",
        "api_output_cert_arn_id": "certificateArn, certificateId",
    },
    "es": {
        "title": "🔐 Gestor de Certificados y Políticas de AWS IoT",
        "separator": "=" * 50,
        "aws_config": "📍 Configuración de AWS:",
        "account_id": "ID de Cuenta",
        "region": "Región",
        "aws_context_error": "⚠️ No se pudo recuperar el contexto de AWS:",
        "aws_credentials_reminder": "   Asegúrate de que las credenciales de AWS estén configuradas",
        "description_intro": "Este script te enseña conceptos de seguridad de AWS IoT:",
        "security_concepts": [
            "• Certificados X.509 para autenticación de dispositivos",
            "• Vinculación de certificados a Things",
            "• Políticas IoT para autorización",
            "• Vinculación y desvinculación de políticas",
            "• Registro de certificados externos",
            "• Detalles completos de API para cada operación",
        ],
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Registro mejorado de solicitudes/respuestas de API",
            "• Detalles completos de errores y trazas",
            "• Información educativa extendida",
        ],
        "tip": "💡 Consejo: Usa la bandera --debug o -d para registro mejorado de API",
        "client_initialized": "✅ Cliente de AWS IoT inicializado",
        "client_error": "❌ Error inicializando cliente de AWS IoT:",
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
        "press_enter": "Presiona Enter para continuar...",
        "goodbye": "👋 ¡Adiós!",
        "main_menu": "📋 Menú Principal:",
        "menu_options": [
            "1. Crear Certificado AWS IoT y Vincular a Thing (+ Política Opcional)",
            "2. Registrar Certificado Externo y Vincular a Thing (+ Política Opcional)",
            "3. Vincular Política a Certificado Existente",
            "4. Desvincular Política de Certificado",
            "5. Habilitar/Deshabilitar Certificado",
            "6. Salir",
        ],
        "select_option": "Seleccionar opción (1-6): ",
        "invalid_choice": "❌ Selección inválida. Por favor selecciona 1-6.",
        "learning_moments": {
            "security_foundation": {
                "title": "📚 LEARNING MOMENT: Fundamentos de Seguridad IoT",
                "content": "La seguridad de AWS IoT se basa en certificados X.509 para autenticación de dispositivos y políticas IoT para autorización. Los certificados identifican únicamente los dispositivos, mientras que las políticas definen qué acciones pueden realizar los dispositivos. Entender este modelo de seguridad es crucial para construir soluciones IoT seguras.",
                "next": "Exploraremos operaciones de gestión de certificados y políticas",
            },
            "certificate_creation": {
                "title": "📚 LEARNING MOMENT: Creación de Certificados y Vinculación a Things",
                "content": "Crear un certificado de AWS IoT establece una identidad digital única para tu dispositivo. El certificado contiene una clave pública que AWS IoT usa para autenticar el dispositivo, mientras que la clave privada permanece segura en el dispositivo. Vincular el certificado a un Thing crea la unión entre la identidad del dispositivo y su representación lógica en AWS IoT.",
                "next": "Crearemos un certificado y lo vincularemos a un Thing",
            },
            "external_registration": {
                "title": "📚 LEARNING MOMENT: Registro de Certificados Externos",
                "content": "A veces necesitas usar certificados de tu propia Autoridad de Certificación (CA) o infraestructura PKI existente. AWS IoT te permite registrar certificados externos, dándote flexibilidad en la gestión de certificados mientras mantienes la seguridad. Esto es útil para organizaciones con políticas de certificados establecidas.",
                "next": "Registraremos un certificado externo con AWS IoT",
            },
            "policy_attachment": {
                "title": "📚 LEARNING MOMENT: Vinculación de Políticas para Autorización",
                "content": "Mientras los certificados manejan la autenticación (quién eres), las políticas IoT manejan la autorización (qué puedes hacer). Las políticas definen a qué temas MQTT puede publicar un dispositivo, suscribirse, y qué operaciones de AWS IoT puede realizar. Vincular políticas a certificados otorga permisos específicos a los dispositivos.",
                "next": "Vincularemos una política a un certificado existente",
            },
            "policy_detachment": {
                "title": "📚 LEARNING MOMENT: Desvinculación de Políticas para Gestión de Permisos",
                "content": "A veces necesitas remover permisos específicos de un dispositivo sin eliminar todo el certificado. La desvinculación de políticas te permite revocar permisos específicos mientras mantienes intacta la identidad del dispositivo. Esto es útil para cambiar roles de dispositivos, solucionar problemas de permisos o implementar políticas de seguridad.",
                "next": "Desvincularemos una política de un certificado",
            },
            "certificate_lifecycle": {
                "title": "📚 LEARNING MOMENT: Gestión del Ciclo de Vida de Certificados",
                "content": "El estado del certificado controla si un dispositivo puede conectarse a AWS IoT. Los certificados ACTIVOS permiten conexiones, mientras que los certificados INACTIVOS las bloquean. Esto proporciona control de seguridad inmediato - puedes deshabilitar instantáneamente dispositivos comprometidos o suspender temporalmente el acceso sin eliminar completamente el certificado.",
                "next": "Gestionaremos el estado del certificado (habilitar/deshabilitar)",
            },
        },
        "workflow_titles": {
            "certificate_creation": "🔐 Flujo de Creación de Certificados",
            "external_registration": "📜 Flujo de Registro de Certificados Externos",
            "policy_attachment": "🔗 Flujo de Vinculación de Políticas",
            "policy_detachment": "🔓 Flujo de Desvinculación de Políticas",
            "certificate_status": "🔄 Gestión de Estado de Certificados",
        },
        "aws_context_info": "🌍 Información de Contexto de AWS:",
        "account_id_label": "ID de Cuenta",
        "region_label": "Región",
        "aws_context_error_msg": "⚠️ No se pudo recuperar el contexto de AWS:",
        "aws_credentials_config": "   Asegúrate de que las credenciales de AWS estén configuradas",
        "policy_to_be_created": "📄 Política a ser creada:",
        "policy_name_label": "Nombre",
        "policy_document_label": "Documento",
        "security_warning": "⚠️  ADVERTENCIA DE SEGURIDAD:",
        "security_warning_details": [
            "   Esta política usa permisos amplios para propósitos de demostración.",
            "   En entornos de producción:",
            "   • Usa ARNs de recursos específicos en lugar de '*'",
            "   • Agrega declaraciones de condición (restricciones IP, acceso basado en tiempo)",
            "   • Usa variables de política como ${iot:Connection.Thing.ThingName}, aún no en alcance para esta sesión básica de aprendizaje",
        ],
        "policy_validation_issues": "🔍 Problemas de Validación de Política:",
        "certificate_details": "📋 Detalles del Certificado:",
        "certificate_id_label": "ID del Certificado",
        "certificate_arn_label": "ARN del Certificado",
        "status_active": "Estado: ACTIVO",
        "certificate_files_saved": "💾 Archivos de certificado guardados en:",
        "certificate_components_created": "🔑 Componentes de Certificado Creados:",
        "certificate_components_list": [
            "   • Clave Pública (para AWS IoT)",
            "   • Clave Privada (mantener segura en el dispositivo)",
            "   • Certificado PEM (para autenticación del dispositivo)",
        ],
        "thing_already_has_certificates": "⚠️  Thing '{}' ya tiene {} certificado(s) vinculado(s):",
        "certificate_id_item": "   {}. ID del Certificado: {}",
        "remove_existing_certificates": "¿Te gustaría remover los certificados existentes? (s/N): ",
        "proceeding_with_multiple": "Procediendo con múltiples certificados vinculados al mismo Thing...",
        "attaching_certificate_to_thing": "🔗 Vinculando certificado a Thing: {}",
        "policy_options": "📝 Opciones de Política:",
        "use_existing_policy": "1. Usar política existente",
        "create_new_policy": "2. Crear nueva política",
        "select_option_1_2": "Seleccionar opción (1-2): ",
        "invalid_selection_generic": "❌ Selección inválida",
        "enter_valid_number_generic": "❌ Por favor ingresa un número válido",
        "select_1_or_2": "❌ Por favor selecciona 1 o 2",
        "no_existing_policies": "📝 No se encontraron políticas existentes. Creando nueva política...",
        "error_listing_policies": "⚠️  Error listando políticas:",
        "proceeding_create_new": "Procediendo a crear nueva política...",
        "enter_new_policy_name": "Ingresa nombre de nueva política: ",
        "policy_name_required": "❌ El nombre de la política es requerido",
        "policy_already_exists": "⚠️  La política '{}' ya existe",
        "use_different_name": "¿Te gustaría usar un nombre diferente? (s/N): ",
        "policy_templates": "📝 Plantillas de Política:",
        "basic_device_policy": "1. Política Básica de Dispositivo (conectar, publicar, suscribirse)",
        "readonly_policy": "2. Política de Solo Lectura (conectar, suscribirse solamente)",
        "custom_policy": "3. Política Personalizada (ingresa tu propio JSON)",
        "select_template_1_3": "Seleccionar plantilla (1-3): ",
        "select_1_2_or_3": "❌ Por favor selecciona 1, 2, o 3",
        "certificate_options": "📋 Opciones de Certificado:",
        "use_existing_cert_file": "1. Usar archivo de certificado existente",
        "generate_sample_cert": "2. Generar certificado de muestra con OpenSSL",
        "invalid_choice_1_2": "❌ Selección inválida. Por favor selecciona 1-2.",
        "cert_must_be_pem": "El certificado debe estar en formato PEM (archivo .crt o .pem)",
        "what_happened": "🔄 Lo que pasó:",
        "what_happened_steps": [
            "   1. AWS IoT validó el formato de tu certificado",
            "   2. Certificado auto-firmado registrado sin requerimiento de CA",
            "   3. Estado del certificado establecido como ACTIVO",
            "   4. AWS asignó ID de Certificado y ARN únicos",
            "   5. El certificado ahora está listo para vinculación a Thing",
        ],
        "key_difference": "💡 Diferencia Clave:",
        "cleanup_certificate": "🧹 Limpiando certificado {}...",
        "error_detaching_policies": "❌ Error desvinculando políticas:",
        "removed_local_file": "🗑️  Archivo local removido:",
        "certificate_cleaned_up": "✅ Certificado {} limpiado exitosamente",
        "error_checking_certificates": "❌ Error verificando certificados existentes:",
        "skipping_file_cleanup": "⚠️ Saltando limpieza de archivos - thing_name inválido:",
        "fetching_things": "ℹ️ Obteniendo Things disponibles...",
        "available_things": "📱 Things Disponibles ({} encontrados):",
        "and_more": "... y {} más",
        "options_header": "📋 Opciones:",
        "select_thing_options": [
            "• Ingresa número (1-{}) para seleccionar Thing",
            "• Escribe 'all' para ver todos los Things",
            "• Escribe 'manual' para ingresar nombre de Thing manualmente",
        ],
        "your_choice": "Tu elección: ",
        "all_things": "📱 Todos los Things:",
        "press_enter_continue": "Presiona Enter para continuar...",
        "press_enter_continue_simple": "Presiona Enter para continuar...",
        "enter_thing_name": "Ingresa nombre del Thing: ",
        "invalid_thing_name": "❌ Nombre de Thing inválido. Solo se permiten caracteres alfanuméricos, guiones y guiones bajos.",
        "thing_found": "✅ Thing '{}' encontrado",
        "thing_not_found": "❌ Thing '{}' no encontrado",
        "thing_name_empty": "❌ El nombre del Thing no puede estar vacío",
        "selected_thing": "✅ Thing Seleccionado: {}",
        "invalid_selection": "❌ Selección inválida",
        "enter_valid_number": "❌ Por favor ingresa un número válido",
        "enter_number_all_manual": "❌ Por favor ingresa un número válido, 'all', o 'manual'",
        "no_things_found": "❌ No se encontraron Things. Por favor ejecuta setup_sample_data.py primero",
        "error_listing_things": "❌ Error listando Things:",
        "key_difference_details": [
            "   • Se usó la API register_certificate_without_ca",
            "   • No se requiere registro de Autoridad de Certificación (CA)",
        ],
        "cert_must_be_pem_info": "El certificado debe estar en formato PEM (archivo .crt o .pem)",
        "validating_cert_format": "Validando formato del archivo de certificado...",
        "choose_cert_provision": "Elige cómo proporcionar tu certificado X.509:",
        "pem_format_starts_with": "El formato PEM comienza con '-----BEGIN CERTIFICATE-----'",
        "learning_objectives": "🎓 Objetivos de Aprendizaje:",
        "external_cert_objectives": [
            "• Entender la diferencia entre certificados generados por AWS vs externos",
            "• Aprender el proceso de registro de certificados",
            "• Practicar validación y vinculación de certificados",
            "• Explorar la API register_certificate",
        ],
        "select_option_1_2_prompt": "Seleccionar opción (1-2): ",
        "no_things_found_run_setup": "❌ No se encontraron Things. Por favor ejecuta setup_sample_data.py primero",
        "options_header_simple": "📋 Opciones:",
        "enter_number_select_thing": "• Ingresa número (1-{}) para seleccionar Thing",
        "type_all_see_things": "• Escribe 'all' para ver todos los Things",
        "type_manual_enter_name": "• Escribe 'manual' para ingresar nombre de Thing manualmente",
        "all_things_header": "📱 Todos los Things:",
        "invalid_thing_name_chars": "❌ Nombre de Thing inválido. Solo se permiten caracteres alfanuméricos, guiones y guiones bajos.",
        "thing_name_cannot_be_empty": "❌ El nombre del Thing no puede estar vacío",
        "policy_creation_cancelled": "Creación de política cancelada por razones de seguridad",
        "enter_policy_json": "Ingresa tu JSON de política (presiona Enter dos veces cuando termines):",
        "policy_to_be_created_header": "📄 Política a ser creada:",
        "available_policies": "📋 Políticas Disponibles:",
        "invalid_selection_simple": "❌ Selección inválida",
        "enter_valid_number_simple": "❌ Por favor ingresa un número válido",
        "no_policies_found_create": "❌ No se encontraron políticas. Creando una primero...",
        "api_details_header": "🔍 Detalles de API:",
        "operation_label": "Operación",
        "http_method_label": "Método HTTP",
        "certificate_status_management": "🔄 Gestión de Estado de Certificados",
        "learning_objectives_header": "🎓 Objetivos de Aprendizaje:",
        "cert_lifecycle_objectives": [
            "• Entender la gestión del ciclo de vida de certificados",
            "• Aprender operaciones de habilitar/deshabilitar",
            "• Practicar control de estado de certificados",
            "• Explorar la API update_certificate",
        ],
        "fetching_all_certificates": "🔍 Obteniendo todos los certificados...",
        "failed_to_list_certificates": "❌ Error al listar certificados",
        "no_certificates_found": "📋 No se encontraron certificados en tu cuenta",
        "create_certificates_first": "💡 Crea certificados primero usando las opciones 1 o 2",
        "invalid_selection_cert": "❌ Selección inválida",
        "enter_valid_number_cert": "❌ Por favor ingresa un número válido",
        "selected_certificate": "📝 Certificado Seleccionado:",
        "certificate_id_short": "ID",
        "attached_to_thing": "Vinculado a Thing",
        "none_label": "Ninguno",
        "available_action": "🔄 Acción Disponible:",
        "enable_certificate": "Habilitar certificado (establecer estado como ACTIVO)",
        "disable_certificate": "Deshabilitar certificado (establecer estado como INACTIVO)",
        "operation_cancelled": "❌ Operación cancelada",
        "certificate_action_success": "✅ Certificado {}do exitosamente!",
        "status_change_summary": "📊 Resumen de Cambio de Estado:",
        "new_status_label": "Nuevo Estado",
        "what_this_means": "💡 Lo que esto significa:",
        "active_cert_meanings": [
            "• El certificado ahora puede usarse para autenticación de dispositivos",
            "• Los dispositivos con este certificado pueden conectarse a AWS IoT",
            "• Las conexiones MQTT usando este certificado tendrán éxito",
        ],
        "inactive_cert_meanings": [
            "• El certificado ahora está deshabilitado para autenticación",
            "• Los dispositivos con este certificado no pueden conectarse a AWS IoT",
            "• Las conexiones MQTT usando este certificado fallarán",
        ],
        "next_steps": "🔍 Próximos Pasos:",
        "next_steps_list": [
            "• Usa iot_registry_explorer.py para verificar el cambio de estado",
            "• Prueba la conexión MQTT para ver el efecto",
        ],
        "reenable_when_ready": "• Vuelve a habilitar cuando estés listo para restaurar la conectividad del dispositivo",
        "failed_to_action_cert": "❌ Error al {} certificado",
        "policy_attachment_workflow": "🔗 Flujo de Vinculación de Políticas",
        "no_certificates_for_thing": "❌ No se encontraron certificados para Thing '{}'",
        "tip_run_option_1": "💡 Consejo: Ejecuta la opción 1 primero para crear y vincular un certificado",
        "using_certificate": "✅ Usando certificado: {}",
        "multiple_certificates_found": "📋 Se encontraron múltiples certificados:",
        "certificate_successfully_attached": "✅ Certificado vinculado exitosamente a {}",
        "thing_can_use_cert": "El Thing ahora puede usar este certificado para autenticación",
        "certificate_generated_successfully": "✅ Certificado generado exitosamente",
        "certificate_details_header": "📊 Detalles del Certificado:",
        "cert_type_self_signed": "• Tipo: X.509 auto-firmado",
        "cert_algorithm": "• Algoritmo: RSA 2048-bit",
        "cert_validity": "• Validez: 365 días",
        "cert_usage": "• Uso: Solo autenticación de dispositivos",
        "cert_location": "• Ubicación: {}",
        "proceed_with_policy_warnings": "¿Proceder con esta política a pesar de las advertencias de seguridad? (s/N): ",
        "confirm_action": "¿Confirmar {} certificado? (s/N): ",
        "available_things_count": "📱 Things Disponibles ({} encontrados):",
        "selected_thing_prefix": "✅ Thing Seleccionado: {}",
        "thing_found_check": "✅ Thing '{}' encontrado",
        "thing_not_found_check": "❌ Thing '{}' no encontrado",
        "learning_moment_cert_process": "📚 LEARNING MOMENT: Proceso de Creación de Certificados",
        "cert_creation_explanation": "Ahora crearemos un certificado X.509 usando la autoridad de certificación de AWS IoT. Esto genera un par único de claves pública/privada donde AWS mantiene la clave pública y te proporciona tanto el certificado como la clave privada para tu dispositivo.",
        "next_creating_cert": "🔄 NEXT: Creando certificado con AWS IoT",
        "found_existing_policies": "📋 Se encontraron {} políticas existentes:",
        "api_response_found_certs": "📤 Respuesta de API: Se encontraron {} certificado(s)",
        "found_certificates_count": "📋 Se encontraron {} certificado(s):",
        "no_certificates_for_thing_msg": "❌ No se encontraron certificados para Thing '{}'",
        "tip_run_option_1_msg": "💡 Consejo: Ejecuta la opción 1 primero para crear y vincular un certificado",
        "using_certificate_msg": "✅ Usando certificado: {}",
        "multiple_certificates_found_msg": "📋 Se encontraron múltiples certificados:",
        "no_policies_found_account": "📋 No se encontraron políticas en tu cuenta",
        "create_policies_first": "💡 Crea políticas primero usando las opciones 1, 2, o 3",
        "found_policies_count": "📋 Se encontraron {} política(s):",
        "no_certs_with_policy": "📋 No se encontraron certificados con la política '{}' vinculada",
        "policy_not_attached": "💡 Esta política no está actualmente vinculada a ningún certificado",
        "found_certs_with_policy": "📋 Se encontraron {} certificado(s) con esta política:",
        "openssl_not_found": "❌ OpenSSL no encontrado. Por favor instala OpenSSL:",
        "install_openssl_macos": "   macOS: brew install openssl",
        "install_openssl_ubuntu": "   Ubuntu: sudo apt-get install openssl",
        "file_not_found": "❌ Archivo no encontrado: {}",
        "multiple_certs_warning": "⚠️  Se encontraron múltiples certificados. Solo se usará el primero.",
        "cert_format_validated": "✅ Formato de archivo de certificado validado",
        "cert_file_not_found": "❌ Archivo de certificado no encontrado",
        "found_private_key": "🔍 Se encontró la clave privada correspondiente: {}",
        "private_key_saved": "🔑 Clave privada guardada: {}",
        "private_key_not_found": "⚠️  Clave privada no encontrada en: {}",
        "enter_key_path": "Ingresa la ruta al archivo de clave privada (o presiona Enter para omitir): ",
        "key_file_not_found": "❌ Archivo de clave no encontrado: {}",
        "private_key_not_saved": "⚠️  Clave privada no guardada - el cliente MQTT puede no funcionar",
        "key_within_working_dir": "⚠️ El archivo de clave debe estar dentro del directorio de trabajo actual",
        "external_cert_registration_moment": "📚 LEARNING MOMENT: Registro de Certificados Externos",
        "external_cert_explanation": "Ahora registraremos tu certificado externo con AWS IoT. A diferencia de los certificados generados por AWS, este proceso registra tu certificado existente sin que AWS cree nuevas claves. Tu clave privada permanece bajo tu control mientras AWS valida y registra el certificado público.",
        "next_registering_cert": "🔄 NEXT: Registrando certificado con AWS IoT",
        "step_creating_certificate": "Creando Certificado X.509",
        "step_attaching_certificate": "Vinculando Certificado a Thing",
        "step_policy_management": "Gestión de Políticas IoT",
        "step_attaching_policy": "Vinculando Política a Certificado",
        "certificates_for_auth": "Los certificados X.509 se usan para autenticación de dispositivos en AWS IoT",
        "cert_contains_keypair": "Cada certificado contiene un par de claves pública/privada",
        "api_description_create_cert": "Crea un nuevo certificado X.509 con par de claves pública/privada",
        "input_params_set_active": "setAsActive: true (activa el certificado inmediatamente)",
        "expected_output_cert": "certificateArn, certificateId, certificatePem, keyPair (claves pública/privada)",
        "learning_moment_cert_attachment": "📚 LEARNING MOMENT: Vinculación Certificado-Thing",
        "cert_attachment_explanation": "Ahora vincularemos el certificado a tu Thing seleccionado. Esto crea la unión segura entre la identidad del certificado y la representación lógica del dispositivo en AWS IoT. Una vez vinculado, el dispositivo puede usar este certificado para autenticarse con AWS IoT Core.",
        "next_attaching_cert": "🔄 NEXT: Vinculando certificado a Thing",
        "press_enter_continue_generic": "Presiona Enter para continuar...",
        "api_path_label": "Ruta de API",
        "description_label": "Descripción",
        "input_parameters_label": "Parámetros de Entrada",
        "expected_output_label": "Salida Esperada",
        "creating_cert_keypair": "Creando certificado y par de claves...",
        "cert_keypair_completed": "Creación de certificado y par de claves completada exitosamente",
        "attaching_cert_to_thing": "Vinculando certificado a Thing...",
        "cert_attachment_completed": "Vinculación de certificado a Thing completada exitosamente",
        "iot_policies_define_actions": "Las Políticas IoT definen qué acciones puede realizar un certificado",
        "create_new_or_existing": "Puedes crear una nueva política o usar una existente",
        "policy_attachment_explanation": "La vinculación de políticas otorga permisos específicos a los certificados",
        "cert_now_has_permissions": "El certificado ahora tiene los permisos definidos en la política",
        "operation_completed_successfully": "{} completado exitosamente",
        "operation_completed": "{} completado",
        "output_label": "Salida",
        "api_description_attach_thing": "Vincula un certificado (principal) a un Thing para autenticación",
        "empty_response_success": "Respuesta vacía en caso de éxito",
        "attaching_cert_to_thing_name": "Vinculando certificado a {}",
        "policies_must_be_attached": "Las políticas deben vincularse a los certificados para otorgar permisos",
        "without_policy_no_operations": "Sin una política, el certificado no puede realizar ninguna operación IoT",
        "certs_must_be_attached": "Los certificados deben vincularse a Things para autenticación de dispositivos",
        "creates_secure_relationship": "Esto crea una relación segura entre el certificado y el dispositivo IoT",
        "cert_will_be_attached": "El certificado será vinculado a: {}",
        "would_like_create_policy": "¿Te gustaría crear y vincular una política? (s/N): ",
        "creates_self_signed_cert": "Esto crea un certificado auto-firmado para propósitos de aprendizaje",
        "production_use_trusted_ca": "En producción, usa certificados de una Autoridad de Certificación confiable",
        "registering_external_cert": "Registrando certificado externo con AWS IoT...",
        "registers_without_new_keys": "Esto registra tu certificado sin que AWS genere nuevas claves",
        "private_key_stays_with_you": "Tu clave privada permanece contigo - AWS solo obtiene el certificado público",
        "proceed_despite_warnings": "¿Proceder con esta política a pesar de las advertencias de seguridad? (s/N): ",
        "do_you_want_to_action_cert": "¿Quieres {} este certificado? (s/N): ",
        "detach_policy_from_cert": "¿Desvincular política '{}' de este certificado? (s/N): ",
        "attach_existing_policy": "¿Te gustaría vincular una política existente? (s/N): ",
        "continue_anyway": "¿Continuar de todos modos? (s/N): ",
        "warning_no_crt_pem": "⚠️  Advertencia: El archivo no tiene extensión .crt o .pem",
        "certificate_file_label": "Certificado",
        "private_key_file_label": "Clave Privada",
        "public_key_file_label": "Clave Pública",
        "failed_to_action_certificate": "❌ Error al {} certificado",
        "policy_attachment_workflow_title": "🔗 Flujo de Vinculación de Políticas",
        "checking_certificates_for_thing": "🔍 Verificando certificados para Thing: {}",
        "select_certificate_prompt": "Seleccionar certificado (1-{}): ",
        "enter_cert_name_default": "\nIngresa nombre del certificado [por defecto: sample-device]: ",
        "enter_cert_path": "\nIngresa la ruta al archivo de certificado: ",
        "cert_path_required": "❌ La ruta del certificado es requerida",
        "failed_to_list_policies": "❌ Error al listar políticas",
        "failed_to_list_policy_targets": "❌ Error al listar objetivos de política",
        "failed_to_detach_policy": "❌ Error al desvincular política",
        "failed_to_create_certificate": "❌ Error al crear certificado. Saliendo.",
        "failed_to_attach_certificate": "❌ Error al vincular certificado a Thing. Saliendo.",
        "cert_name_invalid_chars": "❌ El nombre del certificado solo puede contener letras, números, guiones y guiones bajos",
        "invalid_cert_format_start": "❌ Formato de certificado inválido. Debe ser formato PEM comenzando con '-----BEGIN CERTIFICATE-----'",
        "tip_convert_der_to_pem": "💡 Consejo: Convierte DER a PEM usando: openssl x509 -inform DER -outform PEM -in cert.der -out cert.pem",
        "invalid_cert_format_end": "❌ Formato de certificado inválido. Debe terminar con '-----END CERTIFICATE-----'",
        "permission_denied_cert": "❌ Permiso denegado al leer archivo de certificado",
        "cert_encoding_error": "❌ Error de codificación del archivo de certificado - el archivo puede ser binario",
        "cert_file_required": "❌ Archivo de certificado requerido. Saliendo del flujo.",
        "cert_validation_failed": "❌ Validación de certificado falló. Saliendo del flujo.",
        "thing_selection_required": "❌ Selección de Thing requerida. Saliendo del flujo.",
        "cert_registration_failed": "❌ Registro de certificado falló. Saliendo del flujo.",
        "skipping_file_save_invalid_name": "⚠️ Omitiendo guardado de archivo debido a nombre de thing inválido: {}",
        "cert_registered_files_not_saved": "❌ Certificado registrado pero archivos locales no guardados debido a validación de seguridad.",
        "cert_attachment_failed": "❌ Vinculación de certificado falló. Saliendo del flujo.",
        "policy_detachment_workflow": "🔓 Flujo de Desvinculación de Políticas",
        "learning_objectives_header_simple": "🎓 Objetivos de Aprendizaje:",
        "understand_policy_detachment": "• Entender el proceso de desvinculación de políticas",
        "learn_find_devices_by_policy": "• Aprender a encontrar dispositivos por política",
        "practice_cert_policy_mgmt": "• Practicar gestión de relaciones certificado-política",
        "explore_detach_policy_api": "• Explorar la API detach_policy",
        "fetching_all_policies": "🔍 Obteniendo todas las políticas...",
        "detachment_summary": "📝 Resumen de Desvinculación:",
        "policy_label_simple": "Política",
        "policy_detached_successfully": "✅ ¡Política desvinculada exitosamente!",
        "detachment_results": "📊 Resultados de Desvinculación:",
        "policy_removed_from_cert": "Política '{}' removida del certificado {}",
        "thing_cert_no_longer_has_policy": "El certificado del Thing '{}' ya no tiene esta política",
        "what_this_means_detach": "💡 Lo que esto significa:",
        "cert_no_longer_perform_actions": "• El certificado ya no puede realizar acciones definidas en '{}'",
        "device_may_lose_permissions": "• El dispositivo puede perder permisos específicos (conectar, publicar, suscribirse)",
        "other_policies_still_apply": "• Otras políticas vinculadas a este certificado aún aplican",
        "policy_still_exists": "• La política aún existe y puede vincularse a otros certificados",
        "next_steps_detach": "🔍 Próximos Pasos:",
        "use_registry_explorer_verify": "• Usa iot_registry_explorer.py para verificar la desvinculación de política",
        "test_device_connectivity": "• Prueba la conectividad del dispositivo para ver cambios de permisos",
        "attach_different_policy": "• Vincula una política diferente si es necesario usando la opción 3",
        "setup_complete": "¡Configuración Completa! 🎉",
        "summary_created_configured": "📊 Resumen de lo que fue creado/configurado:",
        "certificate_source_label": "🏷️  Fuente del Certificado",
        "attached_to_thing_label": "📱 Vinculado al Thing",
        "policy_attached_label": "📄 Política Vinculada",
        "what_you_can_explore": "🔍 Lo que puedes explorar ahora:",
        "use_registry_explorer_view": "• Usa iot_registry_explorer.py para ver el certificado",
        "check_thing_attached_cert": "• Revisa el Thing para ver su certificado vinculado",
        "review_policy_permissions": "• Revisa los permisos de la política",
        "compare_external_vs_aws": "• Compara flujos de certificados externos vs generados por AWS",
        "key_learning_points": "💡 Puntos Clave de Aprendizaje:",
        "certs_provide_device_identity": "• Los certificados proporcionan identidad y autenticación de dispositivos",
        "things_represent_iot_devices": "• Los Things representan tus dispositivos IoT en AWS",
        "policies_define_actions": "• Las políticas definen qué acciones pueden realizar los certificados",
        "external_certs_integrate_pki": "• Los certificados externos se integran con la infraestructura PKI existente",
        "register_vs_create_api": "• API register_certificate vs create_keys_and_certificate",
        "all_components_work_together": "• Todos los componentes trabajan juntos para comunicación IoT segura",
        "generating_cert_files": "🔑 Generando archivos de certificado:",
        "private_key_label": "Clave Privada",
        "certificate_label": "Certificado",
        "running_openssl_command": "🔄 Ejecutando comando OpenSSL...",
        "command_label": "📥 Comando",
        "certificate_information": "🔍 Información del Certificado:",
        "windows_openssl_download": "   Windows: Descargar desde https://slproweb.com/products/Win32OpenSSL.html",
        "cert_file_within_working_dir": "⚠️ El archivo de certificado debe estar dentro del directorio de trabajo actual",
        "cert_file_content_preview": "📥 Vista previa del contenido del archivo de certificado:",
        "cert_validation_results": "📊 Resultados de validación del certificado:",
        "format_pem_check": "   • Formato: PEM ✅",
        "certificate_count_label": "   • Cantidad de certificados",
        "file_size_label": "   • Tamaño del archivo",
        "cert_registration_results": "📋 Resultados del Registro de Certificado:",
        "source_external": "   Fuente: Externa (proporcionada por el usuario)",
        "registration_method": "   Método de Registro: API register_certificate",
        "perfect_for_self_signed": "   • Perfecto para certificados auto-firmados y aprendizaje",
        "production_use_ca_signed": "   • Los sistemas de producción típicamente usan certificados firmados por CA",
        "saving_cert_files_locally": "💾 Guardando archivos de certificado localmente para cliente MQTT...",
        "key_file_within_working_dir": "⚠️ El archivo de clave debe estar dentro del directorio de trabajo actual",
        "listing_all_certificates": "Listando todos los certificados",
        "no_thing_attached": "(Ningún Thing vinculado)",
        "created_label": "Creado",
        "unknown_label": "Desconocido",
        "active_status": "ACTIVO",
        "inactive_status": "INACTIVO",
        "api_desc_create_keys_cert": "Crea un nuevo certificado X.509 con par de claves pública/privada",
        "api_input_set_active": "setAsActive: true (activa el certificado inmediatamente)",
        "api_output_cert_keypair": "certificateArn, certificateId, certificatePem, keyPair (claves pública/privada)",
        "api_desc_attach_thing_principal": "Vincula un certificado (principal) a un Thing para autenticación",
        "api_output_empty_success": "Respuesta vacía en caso de éxito",
        "api_desc_create_policy": "Crea una política IoT con permisos especificados",
        "api_input_policy_name_doc": "policyName, policyDocument (permisos JSON)",
        "api_output_policy_details": "policyName, policyArn, policyDocument, policyVersionId",
        "api_desc_attach_policy": "Vincula una política IoT a un certificado para autorización",
        "api_input_policy_cert": "policyName, target (ARN del certificado)",
        "api_desc_list_certificates": "Lista todos los certificados en la cuenta de AWS",
        "api_output_certificates_list": "certificates[] con certificateId, certificateArn, status, creationDate",
        "api_desc_update_certificate": "Actualiza el estado del certificado (ACTIVO/INACTIVO)",
        "api_input_cert_id_status": "certificateId, newStatus",
        "api_desc_list_policies": "Lista todas las políticas IoT en la cuenta de AWS",
        "api_output_policies_list": "policies[] con policyName, policyArn",
        "api_desc_list_targets_for_policy": "Lista todos los certificados que tienen una política específica vinculada",
        "api_input_policy_name": "policyName",
        "api_output_target_arns": "targetArns[] (ARNs de certificados)",
        "api_desc_detach_policy": "Desvincula una política IoT de un certificado",
        "api_desc_register_cert_without_ca": "Registra un certificado externo con AWS IoT sin verificación de CA",
        "api_input_optional_pagination": "Ninguno (opcional: pageSize, marker, ascendingOrder)",
        "api_input_cert_pem_active": "certificatePem (el certificado en formato PEM), setAsActive",
        "api_output_cert_arn_id": "certificateArn, certificateId",
    },
    "debug_messages": {
        "en": {
            "debug_full_error": "🔍 DEBUG: Full error response:",
            "debug_full_traceback": "🔍 DEBUG: Full traceback:",
            "debug_client_config": "🔍 DEBUG: Client configuration:",
            "debug_session_complete": "🔍 DEBUG: Session completed with detailed API logging",
            "api_error": "❌ AWS API Error in",
            "missing_param_error": "❌ Missing required parameter in",
            "invalid_value_error": "❌ Invalid value in",
            "unexpected_error": "❌ Unexpected error in",
        },
        "es": {
            "debug_full_error": "🔍 DEBUG: Respuesta completa de error:",
            "debug_full_traceback": "🔍 DEBUG: Traza completa:",
            "debug_client_config": "🔍 DEBUG: Configuración del cliente:",
            "debug_session_complete": "🔍 DEBUG: Sesión completada con registro detallado de API",
            "api_error": "❌ Error de API de AWS en",
            "missing_param_error": "❌ Parámetro requerido faltante en",
            "invalid_value_error": "❌ Valor inválido en",
            "unexpected_error": "❌ Error inesperado en",
        },
    },
    "ja": {
        "title": "🔐 AWS IoT 証明書・ポリシーマネージャー",
        "separator": "=" * 45,
        "aws_config": "📍 AWS設定:",
        "account_id": "アカウントID",
        "region": "リージョン",
        "description": "X.509証明書とIoTポリシーを使用したAWS IoTセキュリティの学習。",
        "debug_enabled": "🔍 デバッグモード有効",
        "debug_features": ["• 詳細な証明書作成ログ", "• 完全なポリシー分析", "• 拡張セキュリティ診断"],
        "tip": "💡 ヒント: 詳細なセキュリティログには--debugフラグを使用",
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
        "security_intro_title": "IoTセキュリティ - 証明書とポリシー",
        "security_intro_content": "AWS IoTセキュリティは、X.509証明書（デバイス認証用）とIoTポリシー（認可用）に基づいています。証明書はデバイスのアイデンティティを確立し、ポリシーは許可されるアクションを定義します。この組み合わせにより、スケーラブルで安全なIoTデプロイメントが可能になります。",
        "security_intro_next": "証明書とポリシーの作成、管理、セキュリティベストプラクティスを探索します",
        "press_enter": "Enterキーを押して続行...",
        "goodbye": "👋 さようなら！",
        "operations_menu": "📋 利用可能な操作:",
        "operations": [
            "1. 新しい証明書を作成",
            "2. 既存の証明書をリスト",
            "3. 証明書の詳細を表示",
            "4. IoTポリシーを作成",
            "5. 証明書にポリシーをアタッチ",
            "6. 外部証明書を登録",
            "7. 証明書を非アクティブ化",
            "8. 終了",
        ],
        "select_operation": "操作を選択 (1-8): ",
        "invalid_choice": "❌ 無効な選択です。1-8を選択してください。",
        "create_cert_learning_title": "📚 学習ポイント: X.509証明書作成",
        "create_cert_learning_content": "X.509証明書は、IoTデバイスの一意のアイデンティティを提供します。AWS IoTは、証明書、秘密鍵、公開鍵を生成し、デバイス認証に使用します。各証明書には一意のIDがあり、複数のポリシーをアタッチできます。",
        "create_cert_learning_next": "新しいX.509証明書を作成し、そのセキュリティプロパティを調査します",
        "creating_certificate": "🔐 新しいX.509証明書を作成中...",
        "certificate_created": "✅ 証明書が正常に作成されました",
        "certificate_id": "証明書ID:",
        "certificate_arn": "証明書ARN:",
        "certificate_pem": "証明書PEM:",
        "private_key": "秘密鍵:",
        "public_key": "公開鍵:",
        "saving_certificate_files": "💾 証明書ファイルを保存中...",
        "certificate_files_saved": "✅ 証明書ファイルが保存されました:",
        "certificate_file_path": "証明書ファイル: {}",
        "private_key_path": "秘密鍵ファイル: {}",
        "public_key_path": "公開鍵ファイル: {}",
        "certificate_creation_failed": "❌ 証明書作成に失敗しました: {}",
        "list_certs_learning_title": "📚 学習ポイント: 証明書インベントリ",
        "list_certs_learning_content": "証明書の一覧表示により、IoTフリートのセキュリティ態勢を監査できます。各証明書のステータス、作成日、有効期限を確認し、ローテーションが必要な証明書を特定できます。",
        "list_certs_learning_next": "すべての証明書を一覧表示し、そのセキュリティ状態を分析します",
        "listing_certificates": "📋 証明書をリスト中...",
        "certificates_found": "📊 {}個の証明書が見つかりました",
        "no_certificates_found": "📭 証明書が見つかりません",
        "certificate_status": "ステータス:",
        "certificate_creation_date": "作成日:",
        "describe_cert_learning_title": "📚 学習ポイント: 証明書詳細分析",
        "describe_cert_learning_content": "証明書詳細により、セキュリティプロパティ、アタッチされたポリシー、使用状況を確認できます。これは、セキュリティ監査、トラブルシューティング、コンプライアンス確認に重要です。",
        "describe_cert_learning_next": "特定の証明書の詳細なセキュリティプロパティを調査します",
        "select_certificate": "証明書を選択 (1-{}): ",
        "invalid_certificate_choice": "❌ 無効な選択です。1-{}を選択してください。",
        "describing_certificate": "🔍 証明書の詳細を取得中...",
        "certificate_details_title": "📊 証明書詳細:",
        "certificate_description": "説明:",
        "certificate_ca_certificate_id": "CA証明書ID:",
        "certificate_previous_owned_by": "以前の所有者:",
        "certificate_policies": "アタッチされたポリシー:",
        "no_policies_attached": "アタッチされたポリシーなし",
        "create_policy_learning_title": "📚 学習ポイント: IoTポリシー作成",
        "create_policy_learning_content": "IoTポリシーは、証明書に関連付けられたデバイスが実行できるアクションを定義します。JSON形式で、MQTT操作、トピックアクセス、AWS サービス呼び出しの権限を指定します。",
        "create_policy_learning_next": "新しいIoTポリシーを作成し、権限管理を学習します",
        "enter_policy_name": "ポリシー名を入力:",
        "enter_policy_document": "ポリシードキュメント（JSON）を入力:",
        "example_policy": "例: デバイスがすべてのトピックに公開・購読を許可",
        "creating_policy": "📜 IoTポリシー '{}'を作成中...",
        "policy_created": "✅ ポリシーが正常に作成されました",
        "policy_name": "ポリシー名:",
        "policy_arn": "ポリシーARN:",
        "policy_creation_failed": "❌ ポリシー作成に失敗しました: {}",
        "invalid_json_policy": "❌ 無効なJSON形式です。もう一度試してください。",
        "attach_policy_learning_title": "📚 学習ポイント: ポリシーアタッチメント",
        "attach_policy_learning_content": "ポリシーを証明書にアタッチすることで、その証明書を使用するデバイスに権限を付与します。複数のポリシーをアタッチでき、権限は累積されます。これにより、柔軟で細かい権限管理が可能になります。",
        "attach_policy_learning_next": "ポリシーを証明書にアタッチし、デバイス権限を設定します",
        "select_policy_to_attach": "アタッチするポリシーを選択 (1-{}): ",
        "invalid_policy_choice": "❌ 無効な選択です。1-{}を選択してください。",
        "select_certificate_for_policy": "ポリシーをアタッチする証明書を選択 (1-{}): ",
        "attaching_policy": "🔗 ポリシー '{}'を証明書 '{}'にアタッチ中...",
        "policy_attached": "✅ ポリシーが正常にアタッチされました",
        "policy_attachment_failed": "❌ ポリシーアタッチに失敗しました: {}",
        "register_cert_learning_title": "📚 学習ポイント: 外部証明書登録",
        "register_cert_learning_content": "外部で生成された証明書をAWS IoTに登録できます。これにより、既存のPKIインフラストラクチャを活用し、企業の証明書管理ポリシーに準拠できます。",
        "register_cert_learning_next": "外部証明書を登録し、既存のPKIとの統合を学習します",
        "enter_certificate_pem": "証明書PEMを入力:",
        "registering_certificate": "📝 外部証明書を登録中...",
        "certificate_registered": "✅ 証明書が正常に登録されました",
        "certificate_registration_failed": "❌ 証明書登録に失敗しました: {}",
        "deactivate_cert_learning_title": "📚 学習ポイント: 証明書非アクティブ化",
        "deactivate_cert_learning_content": "証明書の非アクティブ化により、デバイスの接続を無効にし、セキュリティインシデントや証明書ローテーション時にアクセスを取り消すことができます。これは、セキュリティ管理の重要な部分です。",
        "deactivate_cert_learning_next": "証明書を非アクティブ化し、デバイスアクセス制御を学習します",
        "select_certificate_to_deactivate": "非アクティブ化する証明書を選択 (1-{}): ",
        "confirm_deactivate": "本当に証明書 '{}'を非アクティブ化しますか？ (y/N): ",
        "deactivation_cancelled": "非アクティブ化がキャンセルされました",
        "deactivating_certificate": "🔒 証明書を非アクティブ化中...",
        "certificate_deactivated": "✅ 証明書が正常に非アクティブ化されました",
        "certificate_deactivation_failed": "❌ 証明書非アクティブ化に失敗しました: {}",
        "debug_full_error": "🔍 デバッグ: 完全なエラーレスポンス:",
        "debug_full_traceback": "🔍 デバッグ: 完全なトレースバック:",
        "api_error": "❌ APIエラー:",
        "error": "❌ エラー:",
        "learning_moments": {
            "certificate_lifecycle": {
                "title": "📚 学習ポイント: 証明書ライフサイクル",
                "content": "X.509証明書には、作成、アクティブ化、使用、ローテーション、失効のライフサイクルがあります。適切なライフサイクル管理により、セキュリティを維持し、コンプライアンス要件を満たすことができます。",
                "next": "証明書ライフサイクル管理のベストプラクティスを学習します",
            },
            "policy_design": {
                "title": "📚 学習ポイント: ポリシー設計",
                "content": "効果的なIoTポリシーは、最小権限の原則に従い、デバイスが必要な操作のみを許可します。トピックレベルの権限、条件付きアクセス、時間ベースの制限を使用して、きめ細かい制御を実現できます。",
                "next": "セキュアなポリシー設計パターンを探索します",
            },
            "security_best_practices": {
                "title": "📚 学習ポイント: セキュリティベストプラクティス",
                "content": "IoTセキュリティのベストプラクティスには、定期的な証明書ローテーション、最小権限ポリシー、デバイス認証の監視、セキュリティ監査が含まれます。これらの実践により、堅牢なIoTセキュリティ態勢を維持できます。",
                "next": "セキュリティベストプラクティスの実装を学習します",
            },
        },
        "debug_messages": {
            "api_error": "❌ AWS APIエラー",
            "missing_param_error": "❌ 必要なパラメータが不足",
            "invalid_value_error": "❌ 無効な値",
            "unexpected_error": "❌ 予期しないエラー",
        },
    },
    "pt-BR": {
        "title": "🔐 Gerenciador de Certificados e Políticas AWS IoT",
        "separator": "=" * 50,
        "aws_config": "📍 Configuração AWS:",
        "account_id": "ID da Conta",
        "region": "Região",
        "aws_context_error": "⚠️ Não foi possível recuperar o contexto AWS:",
        "aws_credentials_reminder": "   Certifique-se de que as credenciais AWS estão configuradas",
        "description_intro": "Este script ensina conceitos de segurança AWS IoT:",
        "security_concepts": [
            "• Certificados X.509 para autenticação de dispositivos",
            "• Vinculação de certificados a Things",
            "• Políticas IoT para autorização",
            "• Vinculação e desvinculação de políticas",
            "• Registro de certificados externos",
            "• Detalhes completos da API para cada operação",
        ],
        "debug_enabled": "🔍 MODO DEBUG HABILITADO",
        "debug_features": [
            "• Log aprimorado de solicitações/respostas da API",
            "• Detalhes completos de erros e rastreamentos",
            "• Informações educacionais estendidas",
        ],
        "tip": "💡 Dica: Use a flag --debug ou -d para log aprimorado da API",
        "client_initialized": "✅ Cliente AWS IoT inicializado",
        "client_error": "❌ Erro ao inicializar cliente AWS IoT:",
        "no_region_error": "❌ Região AWS não configurada",
        "region_setup_instructions": [
            "Por favor configure sua região AWS usando um destes métodos:",
            "1. Variável de ambiente: export AWS_DEFAULT_REGION=us-east-1",
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
        "press_enter": "Pressione Enter para continuar...",
        "goodbye": "👋 Tchau!",
        "main_menu": "📋 Menu Principal:",
        "menu_options": [
            "1. Criar Certificado AWS IoT e Vincular ao Thing (+ Política Opcional)",
            "2. Registrar Certificado Externo e Vincular ao Thing (+ Política Opcional)",
            "3. Vincular Política ao Certificado Existente",
            "4. Desvincular Política do Certificado",
            "5. Habilitar/Desabilitar Certificado",
            "6. Sair",
        ],
        "select_option": "Selecionar opção (1-6): ",
        "invalid_choice": "❌ Escolha inválida. Por favor selecione 1-6.",
        "learning_moments": {
            "security_foundation": {
                "title": "📚 MOMENTO DE APRENDIZADO: Fundamentos de Segurança IoT",
                "content": "A segurança AWS IoT é baseada em certificados X.509 para autenticação de dispositivos e políticas IoT para autorização. Certificados identificam unicamente dispositivos, enquanto políticas definem quais ações os dispositivos podem realizar. Compreender este modelo de segurança é crucial para construir soluções IoT seguras.",
                "next": "Exploraremos operações de gerenciamento de certificados e políticas",
            },
            "certificate_creation": {
                "title": "📚 MOMENTO DE APRENDIZADO: Criação de Certificados e Vinculação a Things",
                "content": "Criar um certificado AWS IoT estabelece uma identidade digital única para seu dispositivo. O certificado contém uma chave pública que o AWS IoT usa para autenticar o dispositivo, enquanto a chave privada permanece segura no dispositivo. Vincular o certificado a um Thing cria a ligação entre a identidade do dispositivo e sua representação lógica no AWS IoT.",
                "next": "Criaremos um certificado e o vincularemos a um Thing",
            },
            "external_registration": {
                "title": "📚 MOMENTO DE APRENDIZADO: Registro de Certificados Externos",
                "content": "Às vezes você precisa usar certificados de sua própria Autoridade Certificadora (CA) ou infraestrutura PKI existente. O AWS IoT permite registrar certificados externos, dando flexibilidade no gerenciamento de certificados mantendo a segurança. Isso é útil para organizações com políticas de certificados estabelecidas.",
                "next": "Registraremos um certificado externo com o AWS IoT",
            },
            "policy_attachment": {
                "title": "📚 MOMENTO DE APRENDIZADO: Vinculação de Políticas para Autorização",
                "content": "Enquanto certificados lidam com autenticação (quem você é), políticas IoT lidam com autorização (o que você pode fazer). Políticas definem a quais tópicos MQTT um dispositivo pode publicar, se inscrever e quais operações AWS IoT pode realizar. Vincular políticas a certificados concede permissões específicas aos dispositivos.",
                "next": "Vincularemos uma política a um certificado existente",
            },
            "policy_detachment": {
                "title": "📚 MOMENTO DE APRENDIZADO: Desvinculação de Políticas para Gerenciamento de Permissões",
                "content": "Às vezes você precisa remover permissões específicas de um dispositivo sem excluir todo o certificado. A desvinculação de políticas permite revogar permissões específicas mantendo a identidade do dispositivo intacta. Isso é útil para alterar funções de dispositivos, solucionar problemas de permissões ou implementar políticas de segurança.",
                "next": "Desvincularemos uma política de um certificado",
            },
            "certificate_lifecycle": {
                "title": "📚 MOMENTO DE APRENDIZADO: Gerenciamento do Ciclo de Vida de Certificados",
                "content": "O status do certificado controla se um dispositivo pode se conectar ao AWS IoT. Certificados ATIVOS permitem conexões, enquanto certificados INATIVOS as bloqueiam. Isso fornece controle de segurança imediato - você pode desabilitar instantaneamente dispositivos comprometidos ou suspender temporariamente o acesso sem excluir completamente o certificado.",
                "next": "Gerenciaremos o status do certificado (habilitar/desabilitar)",
            },
        },
    },
}

# Global variable for user's language preference
USER_LANG = "en"

# Global debug mode flag
DEBUG_MODE = True  # Default to True for educational purposes


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
            choice = input(
                "\nSelect language / Seleccionar idioma / 言語を選択 / 选择语言 / Selecionar idioma (1-5): "
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
            else:
                print("Invalid choice. Please select 1-5.")
                print("Selección inválida. Por favor selecciona 1-5.")
                print("無効な選択です。1-5を選択してください。")
                print("无效选择。请选择 1-5。")
                print("Escolha inválida. Por favor selecione 1-5.")
        except KeyboardInterrupt:
            print("\n\nGoodbye! / ¡Adiós! / さようなら！ / 再见！ / Tchau!")
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


def display_aws_context():
    """Display current AWS account and region information"""
    try:
        sts = boto3.client("sts")
        iot = boto3.client("iot")
        identity = sts.get_caller_identity()

        print(f"\n{get_message('aws_context_info', USER_LANG)}")
        print(f"   {get_message('account_id_label', USER_LANG)}: {identity['Account']}")
        print(f"   {get_message('region_label', USER_LANG)}: {iot.meta.region_name}")
    except Exception as e:
        print(f"\n{get_message('aws_context_error_msg', USER_LANG)} {str(e)}")
        print(get_message("aws_credentials_config", USER_LANG))
    print()


def print_step(step, description):
    """Print step with formatting"""
    print(f"\n🔐 Step {step}: {description}")
    print("-" * 50)


def print_info(message, indent=0):
    """Print informational message with optional indent"""
    prefix = "   " * indent
    print(f"{prefix}ℹ️  {message}")


def validate_policy_security(policy_document, policy_name):
    """Validate policy for security best practices"""
    warnings = []

    for statement in policy_document.get("Statement", []):
        # Check for wildcard resources
        resources = statement.get("Resource", [])
        if isinstance(resources, str):
            resources = [resources]

        if "*" in resources:
            warnings.append(f"Policy '{policy_name}' uses wildcard resource '*' - consider using specific ARNs")

        # Check for missing conditions
        if not statement.get("Condition"):
            warnings.append(f"Policy '{policy_name}' lacks condition statements for additional security")

    return warnings


def print_enhanced_security_warning(policy_name, policy_document, validation_warnings):
    """Print enhanced security warning with validation results"""
    print(f"\n{get_message('policy_to_be_created', USER_LANG)}")
    print(f"   {get_message('policy_name_label', USER_LANG)}: {policy_name}")
    print(f"   {get_message('policy_document_label', USER_LANG)}: {json.dumps(policy_document, indent=2)}")

    print(f"\n{get_message('security_warning', USER_LANG)}")
    for detail in get_message("security_warning_details", USER_LANG):
        print(detail)

    if validation_warnings:
        print(f"\n{get_message('policy_validation_issues', USER_LANG)}")
        for warning in validation_warnings:
            print(f"   • {warning}")


def safe_operation(func, operation_name, api_details=None, debug=None, **kwargs):
    """Execute operation with error handling and API details"""
    if debug is None:
        debug = DEBUG_MODE
    """Execute operation with error handling and API details"""
    if api_details and debug:
        print_api_details(*api_details)

    try:
        if debug:
            print(f"🔄 {operation_name}...")
            print(f"📥 Input: {json.dumps(kwargs, indent=2, default=str)}")
        else:
            print(f"🔄 {operation_name}...")

        response = func(**kwargs)

        if debug:
            print(f"✅ {get_message('operation_completed_successfully', USER_LANG).format(operation_name)}")
            print(
                f"📤 {get_message('output_label', USER_LANG)}: {json.dumps(response, indent=2, default=str)[:500]}{'...' if len(str(response)) > 500 else ''}"
            )
        else:
            print(f"✅ {get_message('operation_completed', USER_LANG).format(operation_name)}")

        time.sleep(1 if debug else 0.5)  # nosemgrep: arbitrary-sleep
        return response
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_message = e.response.get("Error", {}).get("Message", "Unknown error")
        print(f"{get_message('api_error', USER_LANG)} {operation_name}: {error_code} - {error_message}")
        if debug:
            print(get_message("debug_full_error", USER_LANG))
            print(json.dumps(e.response, indent=2, default=str))
        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
        return None
    except KeyError as e:
        print(f"{get_message('missing_param_error', USER_LANG)} {operation_name}: {str(e)}")
        if debug:
            import traceback

            print(get_message("debug_full_traceback", USER_LANG))
            traceback.print_exc()
        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
        return None
    except ValueError as e:
        print(f"{get_message('invalid_value_error', USER_LANG)} {operation_name}: {str(e)}")
        if debug:
            import traceback

            print(get_message("debug_full_traceback", USER_LANG))
            traceback.print_exc()
        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
        return None
    except Exception as e:
        print(f"{get_message('unexpected_error', USER_LANG)} {operation_name}: {str(e)}")
        if debug:
            import traceback

            print(get_message("debug_full_traceback", USER_LANG))
            traceback.print_exc()
        time.sleep(0.5)  # nosemgrep: arbitrary-sleep
        return None


def save_certificate_files(thing_name, cert_id, cert_pem, private_key, public_key):
    """Save certificate files to local folder structure"""
    # Validate thing_name to prevent path traversal
    import re

    if not re.match(r"^[a-zA-Z0-9_-]+$", thing_name):
        raise ValueError(f"Invalid thing_name: {thing_name}. Only alphanumeric characters, hyphens, and underscores allowed.")

    # Create certificates directory structure
    base_dir = os.path.join(os.getcwd(), "certificates", thing_name)
    os.makedirs(base_dir, exist_ok=True)

    # Save certificate files
    cert_file = os.path.join(base_dir, f"{cert_id}.crt")
    key_file = os.path.join(base_dir, f"{cert_id}.key")
    pub_file = os.path.join(base_dir, f"{cert_id}.pub")

    with open(cert_file, "w", encoding="utf-8") as f:
        f.write(cert_pem)

    with open(key_file, "w", encoding="utf-8") as f:
        f.write(private_key)

    with open(pub_file, "w", encoding="utf-8") as f:
        f.write(public_key)

    print(f"   📄 {get_message('certificate_file_label', USER_LANG)}: {cert_file}")
    print(f"   🔐 {get_message('private_key_file_label', USER_LANG)}: {key_file}")
    print(f"   🔑 {get_message('public_key_file_label', USER_LANG)}: {pub_file}")

    return base_dir


def check_existing_certificates(iot, thing_name):
    """Check if Thing already has certificates attached"""
    try:
        response = iot.list_thing_principals(thingName=thing_name)
        principals = response.get("principals", [])

        # Filter for certificate ARNs
        cert_arns = [p for p in principals if "cert/" in p]

        if cert_arns:
            print(get_message("thing_already_has_certificates", USER_LANG).format(thing_name, len(cert_arns)))
            for i, cert_arn in enumerate(cert_arns, 1):
                cert_id = cert_arn.split("/")[-1]
                print(get_message("certificate_id_item", USER_LANG).format(i, cert_id))

            return cert_arns

        return []

    except Exception as e:
        print(f"{get_message('error_checking_certificates', USER_LANG)} {str(e)}")
        return []


def cleanup_certificate(iot, cert_arn, thing_name):
    """Remove certificate association and clean up"""
    cert_id = cert_arn.split("/")[-1]
    print(f"\n{get_message('cleanup_certificate', USER_LANG).format(cert_id)}")

    # Detach policies
    try:
        policies = iot.list_attached_policies(target=cert_arn).get("policies", [])
        for policy in policies:
            safe_operation(
                iot.detach_policy,
                f"Detaching policy '{policy['policyName']}'",
                policyName=policy["policyName"],
                target=cert_arn,
            )
    except Exception as e:
        print(f"{get_message('error_detaching_policies', USER_LANG)} {str(e)}")

    # Detach from Thing
    safe_operation(
        iot.detach_thing_principal, f"Detaching certificate from {thing_name}", thingName=thing_name, principal=cert_arn
    )

    # Deactivate and delete certificate
    safe_operation(iot.update_certificate, "Deactivating certificate", certificateId=cert_id, newStatus="INACTIVE")

    safe_operation(iot.delete_certificate, "Deleting certificate", certificateId=cert_id)

    # Remove local files if they exist
    # Validate thing_name to prevent path traversal
    import re

    if not re.match(r"^[a-zA-Z0-9_-]+$", thing_name):
        print(f"{get_message('skipping_file_cleanup', USER_LANG)} {thing_name}")
        return

    cert_folder = os.path.join(os.getcwd(), "certificates", thing_name)
    if os.path.exists(cert_folder):
        for file in os.listdir(cert_folder):
            if cert_id in file:
                file_path = os.path.join(cert_folder, file)
                os.remove(file_path)
                print(f"{get_message('removed_local_file', USER_LANG)} {file_path}")

    print(get_message("certificate_cleaned_up", USER_LANG).format(cert_id))


def create_certificate(iot, thing_name=None):
    """Create a new X.509 certificate and save locally"""
    print_step(1, get_message("step_creating_certificate", USER_LANG))

    print_info(get_message("certificates_for_auth", USER_LANG))
    print_info(get_message("cert_contains_keypair", USER_LANG))
    time.sleep(1)  # nosemgrep: arbitrary-sleep

    api_details = (
        "create_keys_and_certificate",
        "POST",
        "/keys-and-certificate",
        get_message("api_desc_create_keys_cert", USER_LANG),
        get_message("api_input_set_active", USER_LANG),
        get_message("api_output_cert_keypair", USER_LANG),
    )

    response = safe_operation(
        iot.create_keys_and_certificate, get_message("creating_cert_keypair", USER_LANG), api_details, setAsActive=True
    )

    if response:
        cert_arn = response["certificateArn"]
        cert_id = response["certificateId"]
        cert_pem = response["certificatePem"]
        private_key = response["keyPair"]["PrivateKey"]
        public_key = response["keyPair"]["PublicKey"]

        print(f"\n{get_message('certificate_details', USER_LANG)}")
        print(f"   {get_message('certificate_id_label', USER_LANG)}: {cert_id}")
        print(f"   {get_message('certificate_arn_label', USER_LANG)}: {cert_arn}")
        print(f"   {get_message('status_active', USER_LANG)}")

        # Save certificate files locally
        if thing_name:
            cert_folder = save_certificate_files(thing_name, cert_id, cert_pem, private_key, public_key)
            print(f"\n{get_message('certificate_files_saved', USER_LANG)} {cert_folder}")

        print(f"\n{get_message('certificate_components_created', USER_LANG)}")
        for component in get_message("certificate_components_list", USER_LANG):
            print(component)

        return cert_arn, cert_id

    return None, None


def select_thing(iot):
    """Select a Thing for certificate creation"""
    print_info(get_message("fetching_things", USER_LANG).replace("ℹ️ ", ""))

    try:
        # Handle pagination to get ALL things
        things = []
        next_token = None

        while True:
            if next_token:
                response = iot.list_things(nextToken=next_token)
            else:
                response = iot.list_things()

            things.extend(response.get("things", []))
            next_token = response.get("nextToken")

            if not next_token:
                break

        if not things:
            print(get_message("no_things_found_run_setup", USER_LANG))
            return None

        while True:
            print(f"\n{get_message('available_things_count', USER_LANG).format(len(things))}")

            # Show first 10 things
            display_count = min(len(things), 10)
            for i in range(display_count):
                thing = things[i]
                print(f"   {i+1}. {thing['thingName']} (Type: {thing.get('thingTypeName', 'None')})")

            if len(things) > 10:
                print(f"   ... and {len(things) - 10} more")

            print(f"\n{get_message('options_header_simple', USER_LANG)}")
            print(f"   {get_message('enter_number_select_thing', USER_LANG).format(len(things))}")
            print(f"   {get_message('type_all_see_things', USER_LANG)}")
            print(f"   {get_message('type_manual_enter_name', USER_LANG)}")

            choice = input(f"\n{get_message('your_choice', USER_LANG)}").strip()

            if choice.lower() == "all":
                print(f"\n{get_message('all_things_header', USER_LANG)}")
                for i, thing in enumerate(things, 1):
                    print(f"   {i}. {thing['thingName']} (Type: {thing.get('thingTypeName', 'None')})")
                input(get_message("press_enter_continue_simple", USER_LANG))
                continue

            elif choice.lower() == "manual":
                thing_name = input(get_message("enter_thing_name", USER_LANG)).strip()
                if thing_name:
                    # Validate thing_name to prevent injection attacks
                    if not re.match(r"^[a-zA-Z0-9_-]+$", thing_name):
                        print(get_message("invalid_thing_name_chars", USER_LANG))
                        continue
                    # Verify Thing exists
                    try:
                        iot.describe_thing(thingName=thing_name)
                        print(get_message("thing_found_check", USER_LANG).format(thing_name))
                        return thing_name
                    except ClientError:
                        print(get_message("thing_not_found_check", USER_LANG).format(thing_name))
                        continue
                else:
                    print(get_message("thing_name_cannot_be_empty", USER_LANG))
                    continue

            else:
                try:
                    thing_index = int(choice) - 1
                    if 0 <= thing_index < len(things):
                        selected_thing = things[thing_index]["thingName"]
                        print(get_message("selected_thing", USER_LANG).format(selected_thing))
                        return selected_thing
                    else:
                        print(get_message("invalid_selection_enter_range", USER_LANG).format(len(things)))
                except ValueError:
                    print(get_message("enter_valid_number_all_manual", USER_LANG))

    except Exception as e:
        print(f"{get_message('error_listing_things', USER_LANG)} {str(e)}")
        return None


def attach_certificate_to_thing(iot, cert_arn, target_thing_name):
    """Attach certificate to the designated Thing"""
    print_step(2, get_message("step_attaching_certificate", USER_LANG))

    print_info(get_message("certs_must_be_attached", USER_LANG))
    print_info(get_message("creates_secure_relationship", USER_LANG))
    print_info(get_message("cert_will_be_attached", USER_LANG).format(target_thing_name))
    time.sleep(1)  # nosemgrep: arbitrary-sleep

    # Check for existing certificates
    existing_certs = check_existing_certificates(iot, target_thing_name)
    if existing_certs:
        cleanup_choice = input(f"\n{get_message('remove_existing_certificates', USER_LANG)}").strip().lower()
        if cleanup_choice == "y":
            for cert_arn_existing in existing_certs:
                cleanup_certificate(iot, cert_arn_existing, target_thing_name)
        else:
            print(get_message("proceeding_with_multiple", USER_LANG))

    print(f"\n{get_message('attaching_certificate_to_thing', USER_LANG).format(target_thing_name)}")

    api_details = (
        "attach_thing_principal",
        "PUT",
        f"/things/{target_thing_name}/principals",
        get_message("api_desc_attach_thing_principal", USER_LANG),
        f"thingName: {target_thing_name}, principal: {cert_arn}",
        get_message("api_output_empty_success", USER_LANG),
    )

    response = safe_operation(
        iot.attach_thing_principal,
        get_message("attaching_cert_to_thing_name", USER_LANG).format(target_thing_name),
        api_details,
        thingName=target_thing_name,
        principal=cert_arn,
    )

    if response is not None:
        print(get_message("certificate_successfully_attached", USER_LANG).format(target_thing_name))
        print_info(get_message("thing_can_use_cert", USER_LANG), 1)
        return target_thing_name

    return None


def create_policy_interactive(iot):
    """Create IoT policy interactively or select existing"""
    print_step(3, get_message("step_policy_management", USER_LANG))

    print_info(get_message("iot_policies_define_actions", USER_LANG))
    print_info(get_message("create_new_or_existing", USER_LANG))
    time.sleep(1)  # nosemgrep: arbitrary-sleep

    # First, check if there are existing policies
    try:
        existing_policies = iot.list_policies().get("policies", [])
        if existing_policies:
            print(f"\n{get_message('found_existing_policies', USER_LANG).format(len(existing_policies))}")
            for i, policy in enumerate(existing_policies, 1):
                print(f"   {i}. {policy['policyName']}")

            print(f"\n{get_message('policy_options', USER_LANG)}")
            print(get_message("use_existing_policy", USER_LANG))
            print(get_message("create_new_policy", USER_LANG))

            while True:
                choice = input(f"\n{get_message('select_option_1_2', USER_LANG)}").strip()
                if choice == "1":
                    # Select existing policy
                    while True:
                        try:
                            policy_choice = int(input(f"Select policy (1-{len(existing_policies)}): ")) - 1
                            if 0 <= policy_choice < len(existing_policies):
                                selected_policy = existing_policies[policy_choice]["policyName"]
                                print(get_message("selected_existing_policy", USER_LANG).format(selected_policy))
                                return selected_policy
                            else:
                                print(get_message("invalid_selection_generic", USER_LANG))
                        except ValueError:
                            print(get_message("enter_valid_number_generic", USER_LANG))
                elif choice == "2":
                    break  # Continue to create new policy
                else:
                    print(get_message("select_1_or_2", USER_LANG))
        else:
            print(f"\n{get_message('no_existing_policies', USER_LANG)}")
    except Exception as e:
        print(f"{get_message('error_listing_policies', USER_LANG)} {str(e)}")
        print(get_message("proceeding_create_new", USER_LANG))

    # Create new policy
    policy_name = None
    while True:
        policy_name = input(f"\n{get_message('enter_new_policy_name', USER_LANG)}").strip()
        if not policy_name:
            print(get_message("policy_name_required", USER_LANG))
            continue

        # Check if policy exists
        try:
            iot.get_policy(policyName=policy_name)
            print(get_message("policy_already_exists", USER_LANG).format(policy_name))
            choice = input(get_message("use_different_name", USER_LANG)).strip().lower()
            if choice == "y":
                continue
            else:
                print(get_message("using_existing_policy", USER_LANG).format(policy_name))
                return policy_name
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                print(get_message("policy_name_available", USER_LANG).format(policy_name))
                break
            else:
                print(get_message("error_checking_policy", USER_LANG).format(e.response["Error"]["Message"]))
                continue

    print(f"\n{get_message('policy_templates', USER_LANG)}")
    print(get_message("basic_device_policy", USER_LANG))
    print(get_message("readonly_policy", USER_LANG))
    print(get_message("custom_policy", USER_LANG))

    while True:
        choice = input(get_message("select_policy_template", USER_LANG)).strip()

        if choice == "1":
            policy_document = {  # nosec B608
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["iot:Connect", "iot:Publish", "iot:Subscribe", "iot:Receive"],
                        "Resource": "*",
                    }
                ],
            }
            # Validate policy and show enhanced warnings
            validation_warnings = validate_policy_security(policy_document, policy_name)
            print_enhanced_security_warning(policy_name, policy_document, validation_warnings)

            # Ask for confirmation if there are security warnings
            if validation_warnings:
                confirm = input(get_message("proceed_despite_warnings", USER_LANG)).strip().lower()
                if confirm != "y":
                    print(get_message("policy_creation_cancelled", USER_LANG))
                    return None
            break

        elif choice == "2":
            policy_document = {  # nosec B608
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Action": ["iot:Connect", "iot:Subscribe", "iot:Receive"], "Resource": "*"}],
            }
            # Validate policy and show enhanced warnings
            validation_warnings = validate_policy_security(policy_document, policy_name)
            print_enhanced_security_warning(policy_name, policy_document, validation_warnings)

            # Ask for confirmation if there are security warnings
            if validation_warnings:
                confirm = input(get_message("proceed_despite_warnings", USER_LANG)).strip().lower()
                if confirm != "y":
                    print(get_message("policy_creation_cancelled", USER_LANG))
                    return None
            break

        elif choice == "3":

            print(f"\n{get_message('enter_policy_json', USER_LANG)}")
            policy_lines = []
            while True:
                line = input()
                if line == "" and policy_lines and policy_lines[-1] == "":
                    break
                policy_lines.append(line)

            try:
                policy_text = "\n".join(policy_lines[:-1])  # Remove last empty line
                policy_document = json.loads(policy_text)
                break
            except json.JSONDecodeError as e:
                print(get_message("invalid_json_error", USER_LANG).format(str(e)))
                continue
        else:
            print(get_message("select_1_2_or_3", USER_LANG))

    print(f"\n{get_message('policy_to_be_created_header', USER_LANG)}")
    print(f"   {get_message('name_label_simple', USER_LANG)}: {policy_name}")
    print(f"   {get_message('document_label_simple', USER_LANG)}: {json.dumps(policy_document, indent=2)}")

    api_details = (
        "create_policy",
        "PUT",
        f"/policies/{policy_name}",
        "Creates a new IoT policy with specified permissions",
        f"policyName: {policy_name}, policyDocument: JSON policy document",
        get_message("api_output_policy_details", USER_LANG),
    )

    response = safe_operation(
        iot.create_policy,
        f"Creating policy '{policy_name}'",
        api_details,
        policyName=policy_name,
        policyDocument=json.dumps(policy_document),
    )

    if response:
        print(f"✅ Policy '{policy_name}' created successfully")
        return policy_name

    return None


def attach_policy_to_certificate(iot, cert_arn, policy_name=None):
    """Attach policy to certificate"""
    print_step(4, get_message("step_attaching_policy", USER_LANG))

    print_info(get_message("policies_must_be_attached", USER_LANG))
    print_info(get_message("without_policy_no_operations", USER_LANG))
    time.sleep(1)  # nosemgrep: arbitrary-sleep

    if not policy_name:
        # List existing policies
        try:
            policies = iot.list_policies().get("policies", [])
            if policies:
                print(f"\n{get_message('available_policies', USER_LANG)}")
                for i, policy in enumerate(policies, 1):
                    print(f"   {i}. {policy['policyName']}")

                while True:
                    try:
                        choice = int(input(f"\nSelect policy (1-{len(policies)}): ")) - 1
                        if 0 <= choice < len(policies):
                            policy_name = policies[choice]["policyName"]
                            break
                        else:
                            print(get_message("invalid_selection_simple", USER_LANG))
                    except ValueError:
                        print(get_message("enter_valid_number_simple", USER_LANG))
            else:
                print(get_message("no_policies_found_create", USER_LANG))
                policy_name = create_policy_interactive(iot)
                if not policy_name:
                    return False
        except Exception as e:
            print(get_message("error_listing_policies_simple", USER_LANG).format(str(e)))
            return False

    print(f"\n🔗 Attaching policy '{policy_name}' to certificate")

    api_details = (
        "attach_policy",
        "PUT",
        f"/target-policies/{policy_name}",
        "Attaches an IoT policy to a certificate to grant permissions",
        f"policyName: {policy_name}, target: {cert_arn}",
        get_message("api_output_empty_success", USER_LANG),
    )

    response = safe_operation(
        iot.attach_policy, "Attaching policy to certificate", api_details, policyName=policy_name, target=cert_arn
    )

    if response is not None:
        print(f"✅ Policy '{policy_name}' attached to certificate")
        print_info(get_message("cert_now_has_permissions", USER_LANG), 1)
        return True

    return False


def print_api_details(operation, method, path, description, inputs=None, outputs=None):
    """Print detailed API information for learning"""
    print(f"\n{get_message('api_details_header', USER_LANG)}")
    print(f"   {get_message('operation_label', USER_LANG)}: {operation}")
    print(f"   {get_message('http_method_label', USER_LANG)}: {method}")
    print(f"   {get_message('api_path_label', USER_LANG)}: {path}")
    print(f"   {get_message('description_label', USER_LANG)}: {description}")
    if inputs:
        print(f"   {get_message('input_parameters_label', USER_LANG)}: {inputs}")
    if outputs:
        print(f"   {get_message('expected_output_label', USER_LANG)}: {outputs}")
    time.sleep(1)  # nosemgrep: arbitrary-sleep


def get_thing_certificates(iot, thing_name):
    """Get certificates attached to a Thing"""
    print_api_details(
        "list_thing_principals",
        "GET",
        f"/things/{thing_name}/principals",
        "Lists all principals (certificates) attached to a specific Thing",
        f"thingName: {thing_name}",
        "Array of principal ARNs (certificate ARNs)",
    )

    try:
        response = iot.list_thing_principals(thingName=thing_name)
        principals = response.get("principals", [])
        cert_arns = [p for p in principals if "cert/" in p]

        print(get_message("api_response_found_certs", USER_LANG).format(len(cert_arns)))
        for cert_arn in cert_arns:
            cert_id = cert_arn.split("/")[-1]
            print(f"   {get_message('certificate_id_simple', USER_LANG)}: {cert_id}")

        return cert_arns
    except Exception as e:
        print(get_message("error_simple", USER_LANG).format(str(e)))
        return []


def certificate_status_workflow(iot):
    """Workflow to enable/disable certificates"""
    print(f"\n{get_message('certificate_status_management', USER_LANG)}")
    print("=" * 40)
    print(get_message("learning_objectives_header", USER_LANG))
    for objective in get_message("cert_lifecycle_objectives", USER_LANG):
        print(objective)
    print("=" * 40)

    # List all certificates
    print(f"\n{get_message('fetching_all_certificates', USER_LANG)}")

    api_details = (
        "list_certificates",
        "GET",
        "/certificates",
        get_message("api_desc_list_certificates", USER_LANG),
        get_message("api_input_optional_pagination", USER_LANG),
        get_message("api_output_certificates_list", USER_LANG),
    )

    response = safe_operation(iot.list_certificates, get_message("listing_all_certificates", USER_LANG), api_details)

    if not response:
        print(get_message("failed_to_list_certificates", USER_LANG))
        return

    certificates = response.get("certificates", [])

    if not certificates:
        print(get_message("no_certificates_found", USER_LANG))
        print(get_message("create_certificates_first", USER_LANG))
        return

    print(f"\n{get_message('found_certificates_count', USER_LANG).format(len(certificates))}")

    # Get Thing associations for each certificate
    cert_thing_map = {}
    for cert in certificates:
        cert_arn = cert["certificateArn"]
        try:
            # Find Things associated with this certificate
            things_response = iot.list_principal_things(principal=cert_arn)
            things = things_response.get("things", [])
            cert_thing_map[cert["certificateId"]] = things[0] if things else None
        except Exception:
            cert_thing_map[cert["certificateId"]] = None

    for i, cert in enumerate(certificates, 1):
        status_icon = "🟢" if cert["status"] == "ACTIVE" else "🔴"
        thing_name = cert_thing_map.get(cert["certificateId"])
        thing_info = f" → {thing_name}" if thing_name else f" {get_message('no_thing_attached', USER_LANG)}"
        status_text = (
            get_message("active_status", USER_LANG)
            if cert["status"] == "ACTIVE"
            else get_message("inactive_status", USER_LANG)
        )
        print(f"   {i}. {cert['certificateId'][:16]}...{thing_info} - {status_icon} {status_text}")
        print(
            f"      {get_message('created_label', USER_LANG)}: {cert.get('creationDate', get_message('unknown_label', USER_LANG))}"
        )

    # Select certificate
    while True:
        try:
            choice = int(input(f"\nSelect certificate (1-{len(certificates)}): ")) - 1
            if 0 <= choice < len(certificates):
                selected_cert = certificates[choice]
                break
            else:
                print(get_message("invalid_selection_simple_msg", USER_LANG))
        except ValueError:
            print(get_message("enter_valid_number_simple_msg", USER_LANG))

    cert_id = selected_cert["certificateId"]
    current_status = selected_cert["status"]

    thing_name = cert_thing_map.get(cert_id)
    print(f"\n{get_message('selected_certificate', USER_LANG)}")
    print(f"   {get_message('certificate_id_short', USER_LANG)}: {cert_id}")
    print(f"   {get_message('attached_to_thing', USER_LANG)}: {thing_name or get_message('none_label', USER_LANG)}")
    print(f"   {get_message('current_status_label', USER_LANG)}: {current_status}")
    print(f"   {get_message('arn_label', USER_LANG)}: {selected_cert.get('certificateArn', 'N/A')}")

    # Determine action based on current status
    if current_status == "ACTIVE":
        new_status = "INACTIVE"
        action = "disable"
        icon = "🔴"
    else:
        new_status = "ACTIVE"
        action = "enable"
        icon = "🟢"

    print(f"\n{get_message('available_action', USER_LANG)}")
    if action == "enable":
        print(f"   {icon} {get_message('enable_certificate', USER_LANG)}")
    else:
        print(f"   {icon} {get_message('disable_certificate', USER_LANG)}")

    confirm = input(f"\n{get_message('do_you_want_to_action_cert', USER_LANG).format(action)}").strip().lower()

    if confirm != "y":
        print(get_message("operation_cancelled_simple", USER_LANG))
        return

    # Update certificate status
    api_details = (
        "update_certificate",
        "PUT",
        f"/certificates/{cert_id}",
        "Updates the status of an X.509 certificate",
        f"certificateId: {cert_id}, newStatus: {new_status}",
        get_message("api_output_empty_success", USER_LANG),
    )

    response = safe_operation(
        iot.update_certificate, f"{action.title()}ing certificate", api_details, certificateId=cert_id, newStatus=new_status
    )

    if response is not None:
        print(f"\n{get_message('certificate_action_success', USER_LANG).format(action)}")
        print(f"\n{get_message('status_change_summary', USER_LANG)}")
        print(f"   {get_message('certificate_id_simple', USER_LANG)}: {cert_id}")
        print(f"   {get_message('attached_to_thing', USER_LANG)}: {thing_name or get_message('none_label', USER_LANG)}")
        print(f"   {get_message('previous_status_label', USER_LANG)}: {current_status}")
        print(f"   {get_message('new_status_label_simple', USER_LANG)}: {new_status}")

        print(f"\n{get_message('what_this_means_simple', USER_LANG)}")
        if new_status == "ACTIVE":
            print(get_message("cert_can_be_used_auth", USER_LANG))
            print(get_message("devices_can_connect", USER_LANG))
            print(get_message("mqtt_connections_succeed", USER_LANG))
        else:
            print(get_message("cert_disabled_auth", USER_LANG))
            print(get_message("devices_cannot_connect", USER_LANG))
            print(get_message("mqtt_connections_fail", USER_LANG))

        print(f"\n{get_message('next_steps_simple', USER_LANG)}")
        print(get_message("use_registry_explorer", USER_LANG))
        print(get_message("test_mqtt_connection", USER_LANG))
        if new_status == "INACTIVE":
            print(get_message("reenable_when_ready_simple", USER_LANG))
    else:
        print(get_message("failed_to_action_certificate", USER_LANG).format(action))


def attach_policy_workflow(iot):
    """Workflow to attach policy to existing certificate"""
    print(f"\n{get_message('policy_attachment_workflow_title', USER_LANG)}")
    print("=" * 40)

    # Select Thing
    selected_thing = select_thing(iot)
    if not selected_thing:
        return

    # Get certificates for the Thing
    print(f"\n{get_message('checking_certificates_for_thing', USER_LANG).format(selected_thing)}")
    cert_arns = get_thing_certificates(iot, selected_thing)

    if not cert_arns:
        print(get_message("no_certificates_for_thing_msg", USER_LANG).format(selected_thing))
        print(get_message("tip_run_option_1_msg", USER_LANG))
        return

    # Select certificate if multiple
    if len(cert_arns) == 1:
        selected_cert_arn = cert_arns[0]
        cert_id = selected_cert_arn.split("/")[-1]
        print(get_message("using_certificate_msg", USER_LANG).format(cert_id))
    else:
        print(f"\n{get_message('multiple_certificates_found_msg', USER_LANG)}")
        for i, cert_arn in enumerate(cert_arns, 1):
            cert_id = cert_arn.split("/")[-1]
            print(f"   {i}. {cert_id}")

        while True:
            try:
                choice = int(input(get_message("select_certificate_prompt", USER_LANG).format(len(cert_arns)))) - 1
                if 0 <= choice < len(cert_arns):
                    selected_cert_arn = cert_arns[choice]
                    break
                else:
                    print(get_message("invalid_selection_simple_msg", USER_LANG))
            except ValueError:
                print(get_message("enter_valid_number_simple_msg", USER_LANG))

    # Create or select policy
    policy_name = create_policy_interactive(iot)
    if policy_name:
        attach_policy_to_certificate(iot, selected_cert_arn, policy_name)
        print(f"\n🎉 Policy '{policy_name}' attached to certificate for Thing '{selected_thing}'")


def detach_policy_workflow(iot):
    """Workflow to detach policy from certificate"""
    print(f"\n{get_message('policy_detachment_workflow', USER_LANG)}")
    print("=" * 40)
    print(get_message("learning_objectives_header_simple", USER_LANG))
    print(get_message("understand_policy_detachment", USER_LANG))
    print(get_message("learn_find_devices_by_policy", USER_LANG))
    print(get_message("practice_cert_policy_mgmt", USER_LANG))
    print(get_message("explore_detach_policy_api", USER_LANG))
    print("=" * 40)

    # Step 1: List all policies
    print(f"\n{get_message('fetching_all_policies', USER_LANG)}")

    api_details = (
        "list_policies",
        "GET",
        "/policies",
        "Lists all IoT policies in your AWS account",
        get_message("api_input_optional_pagination", USER_LANG),
        get_message("api_output_policies_list", USER_LANG),
    )

    response = safe_operation(iot.list_policies, "Listing all policies", api_details)

    if not response:
        print(get_message("failed_to_list_policies", USER_LANG))
        return

    policies = response.get("policies", [])

    if not policies:
        print(get_message("no_policies_found_account", USER_LANG))
        print(get_message("create_policies_first", USER_LANG))
        return

    # Step 2: Select policy
    print(f"\n{get_message('found_policies_count', USER_LANG).format(len(policies))}")
    for i, policy in enumerate(policies, 1):
        print(f"   {i}. {policy['policyName']}")

    while True:
        try:
            choice = int(input(f"\nSelect policy to detach (1-{len(policies)}): ")) - 1
            if 0 <= choice < len(policies):
                selected_policy = policies[choice]["policyName"]
                break
            else:
                print(get_message("invalid_selection_simple_msg", USER_LANG))
        except ValueError:
            print(get_message("enter_valid_number_simple_msg", USER_LANG))

    print(f"\n✅ Selected policy: {selected_policy}")

    # Step 3: Find certificates with this policy attached
    print(f"\n🔍 Finding certificates with policy '{selected_policy}' attached...")

    api_details = (
        "list_targets_for_policy",
        "POST",
        f"/targets-for-policy/{selected_policy}",
        "Lists all targets (certificates) that have the specified policy attached",
        f"policyName: {selected_policy}",
        "Array of target ARNs (certificate ARNs)",
    )

    response = safe_operation(
        iot.list_targets_for_policy, f"Finding targets for policy '{selected_policy}'", api_details, policyName=selected_policy
    )

    if not response:
        print(get_message("failed_to_list_policy_targets", USER_LANG))
        return

    targets = response.get("targets", [])
    cert_targets = [t for t in targets if "cert/" in t]

    if not cert_targets:
        print(get_message("no_certs_with_policy", USER_LANG).format(selected_policy))
        print(get_message("policy_not_attached", USER_LANG))
        return

    # Step 4: Get Thing associations for each certificate
    print(f"\n{get_message('found_certs_with_policy', USER_LANG).format(len(cert_targets))}")
    cert_thing_map = {}

    for i, cert_arn in enumerate(cert_targets, 1):
        cert_id = cert_arn.split("/")[-1]

        # Find Things associated with this certificate
        try:
            things_response = iot.list_principal_things(principal=cert_arn)
            things = things_response.get("things", [])
            thing_name = things[0] if things else None
            cert_thing_map[cert_arn] = thing_name

            thing_info = f" → {thing_name}" if thing_name else f" {get_message('no_thing_attached', USER_LANG)}"
            print(f"   {i}. {cert_id[:16]}...{thing_info}")
        except Exception as e:
            print(f"   {i}. {cert_id[:16]}... (Error getting Thing: {str(e)})")
            cert_thing_map[cert_arn] = None

    # Step 5: Select certificate
    while True:
        try:
            choice = int(input(f"\nSelect certificate to detach policy from (1-{len(cert_targets)}): ")) - 1  # nosec B608
            if 0 <= choice < len(cert_targets):
                selected_cert_arn = cert_targets[choice]
                break
            else:
                print(get_message("invalid_selection_simple_msg", USER_LANG))
        except ValueError:
            print(get_message("enter_valid_number_simple_msg", USER_LANG))

    selected_cert_id = selected_cert_arn.split("/")[-1]
    thing_name = cert_thing_map.get(selected_cert_arn)

    print(f"\n{get_message('detachment_summary', USER_LANG)}")
    print(f"   {get_message('policy_label_simple', USER_LANG)}: {selected_policy}")
    print(f"   {get_message('certificate_id_simple', USER_LANG)}: {selected_cert_id}")
    print(f"   {get_message('attached_to_thing', USER_LANG)}: {thing_name or get_message('none_label', USER_LANG)}")

    # Step 6: Confirm detachment
    confirm = input(f"\n{get_message('detach_policy_from_cert', USER_LANG).format(selected_policy)}").strip().lower()

    if confirm != "y":
        print(get_message("operation_cancelled_simple", USER_LANG))
        return

    # Step 7: Detach policy
    api_details = (
        "detach_policy",
        "POST",
        f"/target-policies/{selected_policy}",
        "Detaches an IoT policy from a certificate target",
        f"policyName: {selected_policy}, target: {selected_cert_arn}",
        get_message("api_output_empty_success", USER_LANG),
    )

    response = safe_operation(
        iot.detach_policy,
        "Detaching policy from certificate",
        api_details,
        policyName=selected_policy,
        target=selected_cert_arn,
    )

    if response is not None:
        print(f"\n{get_message('policy_detached_successfully', USER_LANG)}")
        print(f"\n{get_message('detachment_results', USER_LANG)}")
        print(get_message("policy_removed_from_cert", USER_LANG).format(selected_policy, selected_cert_id))
        if thing_name:
            print(get_message("thing_cert_no_longer_has_policy", USER_LANG).format(thing_name))

        print(f"\n{get_message('what_this_means_detach', USER_LANG)}")
        print(get_message("cert_no_longer_perform_actions", USER_LANG).format(selected_policy))
        print(get_message("device_may_lose_permissions", USER_LANG))
        print(get_message("other_policies_still_apply", USER_LANG))
        print(get_message("policy_still_exists", USER_LANG))

        print(f"\n{get_message('next_steps_detach', USER_LANG)}")
        print(get_message("use_registry_explorer_verify", USER_LANG))
        print(get_message("test_device_connectivity", USER_LANG))
        print(get_message("attach_different_policy", USER_LANG))
    else:
        print(get_message("failed_to_detach_policy", USER_LANG))


def certificate_creation_workflow(iot):
    """Full workflow for certificate creation and attachment"""
    print(f"\n{get_message('certificate_creation', USER_LANG, 'workflow_titles')}")
    print("=" * 40)

    # Select Thing first
    selected_thing = select_thing(iot)
    if not selected_thing:
        return

    print(f"\n{get_message('learning_moment_cert_process', USER_LANG)}")
    print(get_message("cert_creation_explanation", USER_LANG))
    print(f"\n{get_message('next_creating_cert', USER_LANG)}")
    input(get_message("press_enter_continue", USER_LANG))

    cert_arn, cert_id = create_certificate(iot, selected_thing)
    if not cert_arn:
        print(get_message("failed_to_create_certificate", USER_LANG))
        return

    print(f"\n{get_message('learning_moment_cert_attachment', USER_LANG)}")
    print(get_message("cert_attachment_explanation", USER_LANG))
    print(f"\n{get_message('next_attaching_cert', USER_LANG)}")
    input(get_message("press_enter_continue_generic", USER_LANG))

    thing_name = attach_certificate_to_thing(iot, cert_arn, selected_thing)
    if not thing_name:
        print(get_message("failed_to_attach_certificate", USER_LANG))
        return

    # Ask about policy
    create_policy = input(f"\n{get_message('would_like_create_policy', USER_LANG)}").strip().lower()
    policy_name = None

    if create_policy == "y":
        policy_name = create_policy_interactive(iot)
        if policy_name:
            attach_policy_to_certificate(iot, cert_arn, policy_name)
    else:
        attach_existing = input(get_message("attach_existing_policy", USER_LANG)).strip().lower()
        if attach_existing == "y":
            if attach_policy_to_certificate(iot, cert_arn):
                policy_name = "Existing Policy"

    print_summary(cert_id, cert_arn, thing_name, policy_name or "None", "AWS-Generated")


def generate_sample_certificate():
    """Generate a sample certificate using OpenSSL for learning"""
    print_step("OpenSSL", "Generate Sample Certificate with OpenSSL")

    print_info(get_message("creates_self_signed_cert", USER_LANG))
    print_info(get_message("production_use_trusted_ca", USER_LANG))
    time.sleep(1)  # nosemgrep: arbitrary-sleep

    # Create sample-certs directory
    sample_dir = os.path.join(os.getcwd(), "sample-certs")
    os.makedirs(sample_dir, exist_ok=True)

    cert_name = input(get_message("enter_cert_name_default", USER_LANG)).strip() or "sample-device"

    # Validate certificate name to prevent command injection
    if not re.match(r"^[a-zA-Z0-9_-]+$", cert_name):
        print(get_message("cert_name_invalid_chars", USER_LANG))
        return None, None

    key_file = os.path.join(sample_dir, f"{cert_name}.key")
    cert_file = os.path.join(sample_dir, f"{cert_name}.crt")

    print(f"\n{get_message('generating_cert_files', USER_LANG)}")
    print(f"   {get_message('private_key_label', USER_LANG)}: {key_file}")
    print(f"   {get_message('certificate_label', USER_LANG)}: {cert_file}")

    # OpenSSL command to generate private key and certificate
    openssl_cmd = [
        "openssl",
        "req",
        "-x509",
        "-newkey",
        "rsa:2048",
        "-keyout",
        key_file,
        "-out",
        cert_file,
        "-days",
        "365",
        "-nodes",
        "-subj",
        f"/CN={cert_name}/O=AWS IoT Learning/C=US",
    ]

    try:
        print(f"\n{get_message('running_openssl_command', USER_LANG)}")
        print(f"{get_message('command_label', USER_LANG)}: {' '.join(openssl_cmd)}")

        import subprocess

        result = subprocess.run(
            openssl_cmd, capture_output=True, text=True, shell=False
        )  # nosemgrep: dangerous-subprocess-use-audit

        if result.returncode == 0:
            print(get_message("certificate_generated_successfully", USER_LANG))
            print(f"\n{get_message('certificate_details_header', USER_LANG)}")
            print(f"   {get_message('cert_type_self_signed', USER_LANG)}")
            print(f"   {get_message('cert_algorithm', USER_LANG)}")
            print(f"   {get_message('cert_validity', USER_LANG)}")
            print(f"   • Subject: CN={cert_name}, O=AWS IoT Learning, C=US")

            # Show certificate info
            info_cmd = ["openssl", "x509", "-in", cert_file, "-text", "-noout"]
            info_result = subprocess.run(
                info_cmd, capture_output=True, text=True, shell=False
            )  # nosemgrep: dangerous-subprocess-use-audit
            if info_result.returncode == 0:
                print(f"\n{get_message('certificate_information', USER_LANG)}")
                lines = info_result.stdout.split("\n")
                for line in lines[:10]:  # Show first 10 lines
                    if line.strip():
                        print(f"   {line.strip()}")
                print("   ...")

            return cert_file
        else:
            print(f"❌ OpenSSL error: {result.stderr}")
            return None

    except FileNotFoundError:
        print(get_message("openssl_not_found", USER_LANG))
        print(get_message("install_openssl_macos", USER_LANG))
        print(get_message("install_openssl_ubuntu", USER_LANG))
        print(get_message("windows_openssl_download", USER_LANG))
        return None
    except Exception as e:
        print(f"❌ Error generating certificate: {str(e)}")
        return None


def get_certificate_file_path():
    """Get certificate file path from user with options"""
    print_info(get_message("choose_cert_provision", USER_LANG))
    print(f"\n{get_message('certificate_options', USER_LANG)}")
    print(get_message("use_existing_cert_file", USER_LANG))
    print(get_message("generate_sample_cert", USER_LANG))

    while True:
        choice = input(f"\n{get_message('select_option_1_2_prompt', USER_LANG)}").strip()

        if choice == "1":
            return get_existing_certificate_path()
        elif choice == "2":
            return generate_sample_certificate()
        else:
            print(get_message("invalid_choice_1_2", USER_LANG))


def get_existing_certificate_path():
    """Get path to existing certificate file"""
    print_info(get_message("cert_must_be_pem_info", USER_LANG))
    print_info(get_message("pem_format_starts_with", USER_LANG))

    while True:
        cert_path = input(get_message("enter_cert_path", USER_LANG)).strip()
        if not cert_path:
            print(get_message("cert_path_required", USER_LANG))
            continue

        # Validate cert_path to prevent path traversal
        if not os.path.abspath(cert_path).startswith(os.path.abspath(os.getcwd())):
            print(get_message("cert_file_within_working_dir", USER_LANG))
            continue

        if not os.path.exists(cert_path):
            print(get_message("file_not_found", USER_LANG).format(cert_path))
            continue

        if not cert_path.lower().endswith((".crt", ".pem")):
            print(get_message("warning_no_crt_pem", USER_LANG))
            confirm = input(get_message("continue_anyway", USER_LANG)).strip().lower()
            if confirm != "y":
                continue

        return cert_path


def validate_certificate_file(cert_path):
    """Validate certificate file format with detailed feedback"""
    print_info(get_message("validating_cert_format", USER_LANG))

    try:
        with open(cert_path, "r", encoding="utf-8") as f:
            cert_content = f.read()

        print(get_message("cert_file_content_preview", USER_LANG))
        lines = cert_content.split("\n")
        for i, line in enumerate(lines[:5]):
            print(f"   Line {i+1}: {line[:60]}{'...' if len(line) > 60 else ''}")
        if len(lines) > 5:
            print(f"   ... and {len(lines) - 5} more lines")

        # Basic PEM format validation
        if not cert_content.startswith("-----BEGIN CERTIFICATE-----"):
            print(get_message("invalid_cert_format_start", USER_LANG))
            print(get_message("tip_convert_der_to_pem", USER_LANG))
            return False

        if not cert_content.strip().endswith("-----END CERTIFICATE-----"):
            print(get_message("invalid_cert_format_end", USER_LANG))
            return False

        # Count certificate sections
        cert_count = cert_content.count("-----BEGIN CERTIFICATE-----")
        print(get_message("cert_validation_results", USER_LANG))
        print(get_message("format_pem_check", USER_LANG))
        print(f"{get_message('certificate_count_label', USER_LANG)}: {cert_count}")
        print(f"{get_message('file_size_label', USER_LANG)}: {len(cert_content)} bytes")

        if cert_count > 1:
            print(get_message("multiple_certs_warning", USER_LANG))

        print(get_message("cert_format_validated", USER_LANG))
        return True

    except FileNotFoundError:
        print(get_message("cert_file_not_found", USER_LANG))
        return False
    except PermissionError:
        print(get_message("permission_denied_cert", USER_LANG))
        return False
    except UnicodeDecodeError:
        print(get_message("cert_encoding_error", USER_LANG))
        return False
    except Exception as e:
        print(f"❌ Unexpected error reading certificate file: {str(e)}")
        return False


def register_certificate_with_aws(iot, cert_path):
    """Register external certificate with AWS IoT with detailed API learning"""
    try:
        with open(cert_path, "r", encoding="utf-8") as f:
            cert_pem = f.read()

        print_info(get_message("registering_external_cert", USER_LANG))
        print_info(get_message("registers_without_new_keys", USER_LANG))
        print_info(get_message("private_key_stays_with_you", USER_LANG))
        time.sleep(1)  # nosemgrep: arbitrary-sleep

        api_details = (
            "register_certificate_without_ca",
            "POST",
            "/certificate/register-no-ca",
            "Registers a self-signed X.509 certificate without requiring CA registration",
            "certificatePem: <PEM-encoded-certificate>, status: ACTIVE",
            get_message("api_output_cert_arn_id", USER_LANG),
        )

        response = safe_operation(
            iot.register_certificate_without_ca,
            "Registering self-signed certificate with AWS IoT",
            api_details,
            certificatePem=cert_pem,
            status="ACTIVE",
        )

        if response:
            cert_arn = response["certificateArn"]
            cert_id = response["certificateId"]

            print(f"\n{get_message('cert_registration_results', USER_LANG)}")
            print(f"   {get_message('certificate_id_simple', USER_LANG)}: {cert_id}")
            print(f"   {get_message('arn_label', USER_LANG)}: {cert_arn}")
            print(get_message("status_active", USER_LANG))
            print(get_message("source_external", USER_LANG))
            print(get_message("registration_method", USER_LANG))

            print(f"\n{get_message('what_happened', USER_LANG)}")
            for step in get_message("what_happened_steps", USER_LANG):
                print(step)

            print(f"\n{get_message('key_difference', USER_LANG)}")
            for detail in get_message("key_difference_details", USER_LANG):
                print(detail)
            print(get_message("perfect_for_self_signed", USER_LANG))
            print(get_message("production_use_ca_signed", USER_LANG))

            return cert_arn, cert_id, cert_pem

        return None, None, None

    except FileNotFoundError:
        print(get_message("cert_file_not_found", USER_LANG))
        return None, None, None
    except PermissionError:
        print(get_message("permission_denied_cert", USER_LANG))
        return None, None, None
    except UnicodeDecodeError:
        print(get_message("cert_encoding_error", USER_LANG))
        return None, None, None
    except Exception as e:
        print(f"❌ Unexpected error registering certificate: {str(e)}")
        return None, None, None


def register_external_certificate_workflow(iot):
    """Complete workflow for registering external certificate"""
    print(f"\n{get_message('external_registration', USER_LANG, 'workflow_titles')}")
    print("=" * 50)
    print(get_message("learning_objectives", USER_LANG))
    for objective in get_message("external_cert_objectives", USER_LANG):
        print(objective)
    print("=" * 50)

    # Step 1: Get certificate file
    cert_path = get_certificate_file_path()
    if not cert_path:
        print(get_message("cert_file_required", USER_LANG))
        return

    # Step 2: Validate certificate
    if not validate_certificate_file(cert_path):
        print(get_message("cert_validation_failed", USER_LANG))
        return

    # Step 3: Select Thing first
    selected_thing = select_thing(iot)
    if not selected_thing:
        print(get_message("thing_selection_required", USER_LANG))
        return

    print(f"\n{get_message('external_cert_registration_moment', USER_LANG)}")
    print(get_message("external_cert_explanation", USER_LANG))
    print(f"\n{get_message('next_registering_cert', USER_LANG)}")
    input(get_message("press_enter_continue", USER_LANG))

    # Step 4: Register certificate with AWS IoT
    cert_arn, cert_id, cert_pem = register_certificate_with_aws(iot, cert_path)
    if not cert_arn:
        print(get_message("cert_registration_failed", USER_LANG))
        return

    # Step 4.5: Save certificate files locally for MQTT client use
    print(f"\n{get_message('saving_cert_files_locally', USER_LANG)}")
    # Validate selected_thing to prevent path traversal
    if not re.match(r"^[a-zA-Z0-9_-]+$", selected_thing):
        print(get_message("skipping_file_save_invalid_name", USER_LANG).format(selected_thing))
        print(get_message("cert_registered_files_not_saved", USER_LANG))
        return

    cert_dir = f"certificates/{selected_thing}"
    os.makedirs(cert_dir, exist_ok=True)

    # Save certificate file
    cert_file = f"{cert_dir}/{cert_id}.crt"
    with open(cert_file, "w", encoding="utf-8") as f:
        f.write(cert_pem)
    print(f"📄 Certificate saved: {cert_file}")

    # Handle private key file
    key_file = f"{cert_dir}/{cert_id}.key"
    if cert_path.endswith(".crt") or cert_path.endswith(".pem"):
        # Look for corresponding key file
        key_path = cert_path.replace(".crt", ".key").replace(".pem", ".key")
        # Validate key_path to prevent path traversal
        if not os.path.realpath(key_path).startswith(os.path.realpath(os.getcwd())):
            print(get_message("key_file_within_working_dir", USER_LANG))
        elif os.path.exists(key_path):
            print(get_message("found_private_key", USER_LANG).format(key_path))
            with open(key_path, "r", encoding="utf-8") as f:
                key_content = f.read()
            with open(key_file, "w", encoding="utf-8") as f:
                f.write(key_content)
            print(get_message("private_key_saved", USER_LANG).format(key_file))
        else:
            print(get_message("private_key_not_found", USER_LANG).format(key_path))
            manual_key = input(get_message("enter_key_path", USER_LANG)).strip()
            if manual_key:
                # Validate manual_key path to prevent path traversal
                if not os.path.realpath(manual_key).startswith(os.path.realpath(os.getcwd())):
                    print(get_message("key_file_within_working_dir", USER_LANG))
                elif os.path.exists(manual_key):
                    with open(manual_key, "r", encoding="utf-8") as f:
                        key_content = f.read()
                    with open(key_file, "w", encoding="utf-8") as f:
                        f.write(key_content)
                    print(get_message("private_key_saved", USER_LANG).format(key_file))
                else:
                    print(get_message("key_file_not_found", USER_LANG).format(manual_key))
            else:
                print(get_message("private_key_not_saved", USER_LANG))

    print(f"💾 Certificate files saved to: {cert_dir}")

    print(f"\n{get_message('learning_moment_cert_attachment', USER_LANG)}")
    print(get_message("cert_attachment_explanation", USER_LANG))
    print(f"\n{get_message('next_attaching_cert', USER_LANG)}")
    input(get_message("press_enter_continue_simple", USER_LANG))

    # Step 5: Attach certificate to Thing
    thing_name = attach_certificate_to_thing(iot, cert_arn, selected_thing)
    if not thing_name:
        print(get_message("cert_attachment_failed", USER_LANG))
        return

    # Step 6: Optional policy attachment
    create_policy = input(f"\n{get_message('would_like_create_policy', USER_LANG)}").strip().lower()
    policy_name = None

    if create_policy == "y":
        policy_name = create_policy_interactive(iot)
        if policy_name:
            attach_policy_to_certificate(iot, cert_arn, policy_name)
    else:
        attach_existing = input(get_message("attach_existing_policy", USER_LANG)).strip().lower()
        if attach_existing == "y":
            if attach_policy_to_certificate(iot, cert_arn):
                policy_name = "Existing Policy"

    # Step 7: Summary
    print_summary(cert_id, cert_arn, thing_name, policy_name or "None", "External")


def print_summary(cert_id, cert_arn, thing_name, policy_name, cert_source="AWS-Generated"):
    """Print enhanced setup summary with certificate source"""
    print_step("Final", get_message("setup_complete", USER_LANG))

    print(f"\n{get_message('summary_created_configured', USER_LANG)}")
    print(f"   {get_message('certificate_id_label', USER_LANG)}: {cert_id}")
    print(f"   {get_message('certificate_source_label', USER_LANG)}: {cert_source}")
    print(f"   {get_message('attached_to_thing_label', USER_LANG)}: {thing_name}")
    print(f"   {get_message('policy_attached_label', USER_LANG)}: {policy_name}")

    print(f"\n{get_message('what_you_can_explore', USER_LANG)}")
    print(get_message("use_registry_explorer_view", USER_LANG))
    print(get_message("check_thing_attached_cert", USER_LANG))
    print(get_message("review_policy_permissions", USER_LANG))
    if cert_source == "External":
        print(get_message("compare_external_vs_aws", USER_LANG))

    print(f"\n{get_message('key_learning_points', USER_LANG)}")
    print(get_message("certs_provide_device_identity", USER_LANG))
    print(get_message("things_represent_iot_devices", USER_LANG))
    print(get_message("policies_define_actions", USER_LANG))
    if cert_source == "External":
        print(get_message("external_certs_integrate_pki", USER_LANG))
        print(get_message("register_vs_create_api", USER_LANG))
    print(get_message("all_components_work_together", USER_LANG))


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
        for concept in get_message("security_concepts", USER_LANG):
            print(concept)

        if debug_mode:
            print(f"\n{get_message('debug_enabled', USER_LANG)}")
            for feature in get_message("debug_features", USER_LANG):
                print(feature)
        else:
            print(f"\n{get_message('tip', USER_LANG)}")

        print(get_message("separator", USER_LANG))

        try:
            iot = boto3.client("iot")
            print(get_message("client_initialized", USER_LANG))

            if debug_mode:
                print(get_message("debug_client_config", USER_LANG))
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
        except Exception as e:
            print(f"{get_message('client_error', USER_LANG)} {str(e)}")
            return

        # Set global debug mode for safe_operation calls
        global DEBUG_MODE
        DEBUG_MODE = debug_mode

        print_learning_moment("security_foundation", USER_LANG)
        input(get_message("press_enter", USER_LANG))

        while True:
            try:
                print(f"\n{get_message('main_menu', USER_LANG)}")
                for option in get_message("menu_options", USER_LANG):
                    print(option)

                choice = input(f"\n{get_message('select_option', USER_LANG)}").strip()

                if choice == "1":
                    print_learning_moment("certificate_creation", USER_LANG)
                    input(get_message("press_enter", USER_LANG))

                    certificate_creation_workflow(iot)
                elif choice == "2":
                    print_learning_moment("external_registration", USER_LANG)
                    input(get_message("press_enter", USER_LANG))

                    register_external_certificate_workflow(iot)
                elif choice == "3":
                    print_learning_moment("policy_attachment", USER_LANG)
                    input(get_message("press_enter", USER_LANG))

                    attach_policy_workflow(iot)
                elif choice == "4":
                    print_learning_moment("policy_detachment", USER_LANG)
                    input(get_message("press_enter", USER_LANG))

                    detach_policy_workflow(iot)
                elif choice == "5":
                    print_learning_moment("certificate_lifecycle", USER_LANG)
                    input(get_message("press_enter", USER_LANG))

                    certificate_status_workflow(iot)
                elif choice == "6":
                    print(get_message("goodbye", USER_LANG))
                    break
                else:
                    print(get_message("invalid_choice", USER_LANG))

                try:
                    input(f"\n{get_message('press_enter', USER_LANG)}")
                except KeyboardInterrupt:
                    print(f"\n\n{get_message('goodbye', USER_LANG)}")
                    break
            except KeyboardInterrupt:
                print(f"\n\n{get_message('goodbye', USER_LANG)}")
                break

    except KeyboardInterrupt:
        print(f"\n\n{get_message('goodbye', USER_LANG)}")


if __name__ == "__main__":
    main()

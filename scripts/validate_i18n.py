#!/usr/bin/env python3
"""
I18n Validation Script

Validates that all i18n JSON files have consistent keys across all languages.
This ensures translations are complete and no keys are missing.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple


def get_all_keys(data: Dict, prefix: str = "") -> Set[str]:
    """
    Recursively get all keys from nested dictionary.

    Args:
        data: Dictionary to extract keys from
        prefix: Current key prefix for nested keys

    Returns:
        Set of all keys (including nested keys with dot notation)
    """
    keys = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        keys.add(full_key)
        if isinstance(value, dict):
            keys.update(get_all_keys(value, full_key))
    return keys


def load_json_file(file_path: Path) -> Tuple[Dict, List[str]]:
    """
    Load JSON file and return data with any errors.

    Args:
        file_path: Path to JSON file

    Returns:
        Tuple of (data, errors)
    """
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, errors
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in {file_path}: {e}")
        return {}, errors
    except FileNotFoundError:
        errors.append(f"File not found: {file_path}")
        return {}, errors


def validate_i18n_files(i18n_dir: Path = None) -> bool:
    """
    Validate all i18n files have consistent keys.

    Args:
        i18n_dir: Path to i18n directory (defaults to ../i18n)

    Returns:
        True if validation passes, False otherwise
    """
    if i18n_dir is None:
        script_dir = Path(__file__).parent
        i18n_dir = script_dir.parent / "i18n"

    if not i18n_dir.exists():
        print(f"❌ I18n directory not found: {i18n_dir}")
        return False

    # Get all language directories
    languages = [d.name for d in i18n_dir.iterdir() if d.is_dir()]
    if not languages:
        print(f"❌ No language directories found in {i18n_dir}")
        return False

    # Get all script files from English (reference language)
    en_dir = i18n_dir / "en"
    if not en_dir.exists():
        print("❌ English reference directory 'en' not found")
        return False

    script_files = [f.name for f in en_dir.glob("*.json")]
    if not script_files:
        print("❌ No JSON files found in English directory")
        return False

    print(f"🌍 Found languages: {', '.join(sorted(languages))}")
    print(f"📄 Found script files: {', '.join(sorted(script_files))}")
    print()

    all_errors = []
    validation_results = {}

    for script_file in sorted(script_files):
        print(f"🔍 Validating {script_file}...")

        # Load English file as reference
        en_file = en_dir / script_file
        en_data, en_errors = load_json_file(en_file)
        if en_errors:
            all_errors.extend(en_errors)
            continue

        en_keys = get_all_keys(en_data)
        validation_results[script_file] = {
            "en_keys_count": len(en_keys),
            "languages": {},
        }

        # Check each language
        for lang in sorted(languages):
            if lang == "en":
                validation_results[script_file]["languages"][lang] = {
                    "status": "reference",
                    "keys_count": len(en_keys),
                    "missing": [],
                    "extra": [],
                }
                continue

            lang_file = i18n_dir / lang / script_file
            if not lang_file.exists():
                all_errors.append(f"Missing file: {lang_file}")
                validation_results[script_file]["languages"][lang] = {
                    "status": "missing_file",
                    "keys_count": 0,
                    "missing": [],
                    "extra": [],
                }
                continue

            lang_data, lang_errors = load_json_file(lang_file)
            if lang_errors:
                all_errors.extend(lang_errors)
                validation_results[script_file]["languages"][lang] = {
                    "status": "invalid_json",
                    "keys_count": 0,
                    "missing": [],
                    "extra": [],
                }
                continue

            lang_keys = get_all_keys(lang_data)

            # Find missing and extra keys
            missing_keys = sorted(en_keys - lang_keys)
            extra_keys = sorted(lang_keys - en_keys)

            status = "valid" if not missing_keys and not extra_keys else "invalid"
            validation_results[script_file]["languages"][lang] = {
                "status": status,
                "keys_count": len(lang_keys),
                "missing": missing_keys,
                "extra": extra_keys,
            }

            if missing_keys:
                all_errors.append(f"{lang}/{script_file} missing keys: {missing_keys}")

            if extra_keys:
                all_errors.append(f"{lang}/{script_file} has extra keys: {extra_keys}")

            # Print status
            if status == "valid":
                print(f"  ✅ {lang}/{script_file} - All {len(lang_keys)} keys match")
            else:
                print(f"  ❌ {lang}/{script_file} - {len(missing_keys)} missing, {len(extra_keys)} extra")

    # Print summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    for script_file, results in validation_results.items():
        print(f"\n📄 {script_file} ({results['en_keys_count']} keys in English)")
        for lang, lang_results in results["languages"].items():
            status_icon = {
                "reference": "🔵",
                "valid": "✅",
                "invalid": "❌",
                "missing_file": "📁",
                "invalid_json": "🔧",
            }.get(lang_results["status"], "❓")

            print(f"  {status_icon} {lang}: {lang_results['keys_count']} keys", end="")

            if lang_results["missing"]:
                print(f" (missing: {len(lang_results['missing'])})", end="")
            if lang_results["extra"]:
                print(f" (extra: {len(lang_results['extra'])})", end="")
            print()

    if all_errors:
        print(f"\n🚨 Found {len(all_errors)} validation errors:")
        for error in all_errors:
            print(f"  ❌ {error}")
        return False
    else:
        print("\n🎉 All i18n files have consistent keys!")
        return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate i18n JSON files")
    parser.add_argument("--i18n-dir", type=Path, help="Path to i18n directory (default: ../i18n)")

    args = parser.parse_args()

    success = validate_i18n_files(args.i18n_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

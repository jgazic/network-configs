"""Validate a YAML config file against a JSON Schema."""
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, FormatChecker


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <schema.json> <config.yml>")
        sys.exit(2)

    schema_path = Path(sys.argv[1])
    config_path = Path(sys.argv[2])

    schema = json.loads(schema_path.read_text())
    data = yaml.safe_load(config_path.read_text())

    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(data))

    if errors:
        print(f"FAIL {config_path}")
        for error in errors:
            print(f"  {error.message}")
        sys.exit(1)

    print(f"PASS {config_path}")


if __name__ == "__main__":
    main()

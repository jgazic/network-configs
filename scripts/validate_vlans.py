"""Validate VLAN business rules across config files."""
import sys
from pathlib import Path
import yaml

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <vlans.yml> [vlans.yml ...]")
    sys.exit(2)

errors = []

# Load all VLAN files passed as arguments
vlan_files = []
for arg in sys.argv[1:]:
    file_path = Path(arg)
    data = yaml.safe_load(file_path.read_text())
    vlan_files.append((file_path, data))

# Check 1: No duplicate VLAN IDs within a single file
for file_path, data in vlan_files:
    seen_ids = {}
    for vlan in data.get("vlans", []):
        vlan_id = vlan["id"]
        if vlan_id in seen_ids:
            errors.append(
                f"{file_path}: "
                f"Duplicate VLAN ID {vlan_id} "
                f"(names: '{seen_ids[vlan_id]}' and '{vlan['name']}')"
            )
        else:
            seen_ids[vlan_id] = vlan["name"]

# Check 2: Same VLAN ID must have the same name across all sites
vlan_names = {}
for file_path, data in vlan_files:
    for vlan in data.get("vlans", []):
        vlan_id = vlan["id"]
        vlan_name = vlan["name"]
        if vlan_id in vlan_names:
            prev_path, prev_name = vlan_names[vlan_id]
            if prev_name != vlan_name:
                errors.append(
                    f"VLAN ID {vlan_id} has inconsistent names: "
                    f"'{prev_name}' in {prev_path} vs "
                    f"'{vlan_name}' in {file_path}"
                )
        else:
            vlan_names[vlan_id] = (file_path, vlan_name)

if errors:
    print("VLAN validation FAILED:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print(f"VLAN validation PASSED ({len(vlan_files)} files checked)")

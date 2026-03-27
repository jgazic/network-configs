"""Validate ACL business rules across config files."""
import sys
from pathlib import Path
import yaml

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <acls.yml> [acls.yml ...]")
    sys.exit(2)

errors = []

# Load all ACL files passed as arguments
acl_files = []
for arg in sys.argv[1:]:
    file_path = Path(arg)
    data = yaml.safe_load(file_path.read_text())
    acl_files.append((file_path, data))

PORT_PROTOCOLS = {"tcp", "udp"}

for file_path, data in acl_files:
    for acl in data.get("acls", []):
        acl_name = acl["name"]
        entries = acl.get("entries", [])

        # Check 1: Sequence numbers unique and ascending
        seen_seqs = set()
        prev_seq = -1
        for entry in entries:
            seq = entry["sequence"]
            if seq in seen_seqs:
                errors.append(
                    f"{file_path}: ACL '{acl_name}' has duplicate "
                    f"sequence number {seq}"
                )
            elif seq <= prev_seq:
                errors.append(
                    f"{file_path}: ACL '{acl_name}' sequence {seq} "
                    f"is not ascending (follows {prev_seq})"
                )
            seen_seqs.add(seq)
            prev_seq = seq

        # Check 2: dst_port only valid for TCP/UDP
        for entry in entries:
            if "dst_port" in entry:
                protocol = entry.get("protocol", "")
                if protocol not in PORT_PROTOCOLS:
                    errors.append(
                        f"{file_path}: ACL '{acl_name}' seq "
                        f"{entry['sequence']} has dst_port "
                        f"{entry['dst_port']} on protocol "
                        f"'{protocol}' (only valid for tcp/udp)"
                    )

if errors:
    print("ACL validation FAILED:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)

print(f"ACL validation PASSED ({len(acl_files)} files checked)")

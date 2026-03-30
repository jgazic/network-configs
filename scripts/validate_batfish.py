"""Validate rendered configs using Batfish."""
import sys
from pybatfish.client.session import Session

bf = Session(host="localhost")
bf.set_network("network-configs")
bf.init_snapshot(sys.argv[1], name="current", overwrite=True)

errors = False

for _, row in bf.q.fileParseStatus().answer().frame().iterrows():
    status = row["Status"]
    label = "PASS" if status == "PASSED" else f"FAIL ({status})"
    print(f"{label}  {row['File_Name']}")
    if status != "PASSED":
        errors = True

for _, row in bf.q.parseWarning().answer().frame().iterrows():
    print(f"  WARNING: {row['Filename']} line {row['Line']}: {row['Text']}")

for _, row in bf.q.undefinedReferences().answer().frame().iterrows():
    print(f"UNDEFINED: {row['Ref_Name']} ({row['Struct_Type']} in {row['File_Name']})")
    errors = True

for _, row in bf.q.filterLineReachability().answer().frame().iterrows():
    print(f"UNREACHABLE: {row['Unreachable_Line']} (blocked by {row['Blocking_Lines']})")
    errors = True

if errors:
    sys.exit(1)
print("\nBatfish validation PASSED")

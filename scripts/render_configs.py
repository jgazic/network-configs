"""Render a YAML config file through a Jinja2 template."""
import ipaddress
import sys
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader


def cidr_to_wildcard(value):
    """Convert CIDR notation to IOS wildcard mask format."""
    network = ipaddress.ip_network(value, strict=False)
    return f"{network.network_address} {network.hostmask}"


if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <template.j2> <config.yml> <output_file>")
    sys.exit(2)

template_path = Path(sys.argv[1])
config_path = Path(sys.argv[2])
output_path = Path(sys.argv[3])

data = yaml.safe_load(config_path.read_text())

env = Environment(
    loader=FileSystemLoader(str(template_path.parent)),
    trim_blocks=True,
    lstrip_blocks=True,
)
env.filters["cidr_to_wildcard"] = cidr_to_wildcard

template = env.get_template(template_path.name)
rendered = template.render(**data)

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(rendered)
print(f"Rendered {config_path} -> {output_path}")

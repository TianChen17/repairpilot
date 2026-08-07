#!/usr/bin/env python3
"""Bind every DataHub Quickstart published port to loopback.

Run this after ``datahub docker quickstart`` writes its Compose file and before
starting the persistent systemd unit. The rewrite is idempotent and fails if a
published port remains externally bound.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "compose_file",
        nargs="?",
        type=Path,
        default=Path.home() / ".datahub/quickstart/docker-compose.yml",
    )
    args = parser.parse_args()
    compose_file: Path = args.compose_file
    payload = yaml.safe_load(compose_file.read_text())
    mappings = 0

    for service in payload.get("services", {}).values():
        ports = service.get("ports", [])
        for mapping in ports:
            if not isinstance(mapping, dict) or "published" not in mapping:
                raise SystemExit("Refusing an unsupported DataHub port mapping")
            mapping["host_ip"] = "127.0.0.1"
            mappings += 1

    if mappings == 0:
        raise SystemExit("No DataHub published ports were found")
    for service in payload.get("services", {}).values():
        for mapping in service.get("ports", []):
            if mapping.get("host_ip") != "127.0.0.1":
                raise SystemExit("A DataHub port is not loopback-bound")

    temporary = compose_file.with_suffix(".tmp")
    temporary.write_text(yaml.safe_dump(payload, sort_keys=False))
    temporary.replace(compose_file)
    print(f"datahub_loopback_mappings={mappings}")


if __name__ == "__main__":
    main()

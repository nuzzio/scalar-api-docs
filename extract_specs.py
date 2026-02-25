#!/usr/bin/env python3
"""Extract v3beta and v3 OpenAPI specs from the full platform spec."""

import yaml
import sys
import os

def load_spec(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def find_refs(obj, refs=None):
    """Recursively find all $ref values in an object."""
    if refs is None:
        refs = set()
    if isinstance(obj, dict):
        if "$ref" in obj:
            ref = obj["$ref"]
            if ref.startswith("#/components/schemas/"):
                refs.add(ref.replace("#/components/schemas/", ""))
        for v in obj.values():
            find_refs(v, refs)
    elif isinstance(obj, list):
        for item in obj:
            find_refs(item, refs)
    return refs

def resolve_schemas(all_schemas, needed):
    """Resolve all transitive schema dependencies."""
    resolved = set()
    queue = list(needed)
    while queue:
        name = queue.pop(0)
        if name in resolved:
            continue
        resolved.add(name)
        if name in all_schemas:
            new_refs = find_refs(all_schemas[name])
            for ref in new_refs:
                if ref not in resolved:
                    queue.append(ref)
    return resolved

def extract_spec(full_spec, path_prefix, title, description, version):
    """Extract paths matching prefix and their schema dependencies."""
    paths = {}
    for path, methods in full_spec.get("paths", {}).items():
        if path.startswith(path_prefix):
            paths[path] = methods

    needed_schemas = find_refs(paths)
    all_schemas = full_spec.get("components", {}).get("schemas", {})
    resolved = resolve_schemas(all_schemas, needed_schemas)

    schemas = {}
    for name in sorted(resolved):
        if name in all_schemas:
            schemas[name] = all_schemas[name]

    tags_used = set()
    for path_methods in paths.values():
        for method_data in path_methods.values():
            if isinstance(method_data, dict) and "tags" in method_data:
                for tag in method_data["tags"]:
                    tags_used.add(tag)

    tags = []
    for tag_def in full_spec.get("tags", []):
        if tag_def.get("name") in tags_used:
            tags.append(tag_def)

    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": title,
            "description": description,
            "version": version,
            "contact": {
                "name": "CloudBees",
                "url": "https://www.cloudbees.com"
            }
        },
        "servers": [
            {
                "url": "https://api.cloudbees.io",
                "description": "CloudBees Platform"
            }
        ],
        "security": [
            {"BearerAuth": []}
        ],
        "paths": dict(sorted(paths.items())),
        "components": {
            "schemas": schemas,
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "OIDC token or Personal Access Token (PAT)"
                }
            }
        }
    }
    if tags:
        spec["tags"] = tags

    return spec

def main():
    source = os.path.join("specs", "openapi-source.yaml")
    if not os.path.exists(source):
        print(f"Error: {source} not found. Run ./serve.sh first to download the spec.")
        sys.exit(1)

    print("Loading full spec...")
    full_spec = load_spec(source)
    total_paths = len(full_spec.get("paths", {}))
    print(f"  Total paths in source: {total_paths}")

    output_dir = "specs"

    print("\nExtracting v3beta spec...")
    v3beta = extract_spec(
        full_spec,
        "/v3beta/",
        "CloudBees Unify Public API (v3beta)",
        "Public REST API for external CI/CD systems to report lifecycle events, "
        "register artifacts, publish test and security scan results, and query "
        "DORA metrics.\n\n"
        "This API is in beta. Endpoints are stable but may evolve before GA.",
        "v3beta"
    )
    v3beta_path = os.path.join(output_dir, "openapi-v3beta.yaml")
    with open(v3beta_path, "w") as f:
        yaml.dump(v3beta, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    print(f"  {len(v3beta['paths'])} endpoints, {len(v3beta['components']['schemas'])} schemas")
    print(f"  Written: {v3beta_path}")

    print("\nExtracting v3 spec...")
    v3_full = extract_spec(
        full_spec,
        "/v3",
        "CloudBees Unify Platform API (v3)",
        "CloudBees Platform v3 API covering deployments, artifacts, releases, "
        "organizations, users, endpoints, feature flags, workflows, and the "
        "v3beta public API for external CI/CD integration.",
        "v3"
    )
    v3_path = os.path.join(output_dir, "openapi-v3.yaml")
    with open(v3_path, "w") as f:
        yaml.dump(v3_full, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
    print(f"  {len(v3_full['paths'])} endpoints, {len(v3_full['components']['schemas'])} schemas")
    print(f"  Written: {v3_path}")

    print("\nDone.")

if __name__ == "__main__":
    main()

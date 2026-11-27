#!/usr/bin/env python3
"""Offline structural and shell-predicate checks for the public CI workflow."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "room-migration-validation.yml"
TEXT = WORKFLOW.read_text(encoding="utf-8")
errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


require(len(re.findall(r"^jobs:", TEXT, re.MULTILINE)) == 1, "workflow must contain exactly one top-level jobs block")

expected_steps = [
    "Checkout public CI control files",
    "Validate public CI workflow guardrails",
    "Resolve and validate private source SHA",
    "Checkout private app with generated schema snapshots",
    "Run Quality Guardian checks",
    "Run host-side compile, unit tests, lint and APK preflight",
    "Verify Kotlin serialization runtime alignment",
    "Enable KVM for Android emulator",
    "Run Android instrumentation on Google ATD",
    "Summarize Android instrumentation failures",
    "Remove private checkout and source-bearing build state",
]
for name in expected_steps:
    count = len(re.findall(r"^      - name: " + re.escape(name) + r"$", TEXT, re.MULTILINE))
    require(count == 1, f"expected exactly one workflow step named: {name}")

positions = [TEXT.find(f"      - name: {name}") for name in expected_steps]
require(all(position >= 0 for position in positions), "one or more required workflow steps are missing")
require(positions == sorted(positions), "workflow steps are out of the required privacy/verification order")

require('rm -rf "$GITHUB_WORKSPACE/private-source"' in TEXT, "private checkout cleanup is missing")
require("actions/upload-artifact" not in TEXT, "private build/test outputs must not be uploaded as artifacts")
require("persist-credentials: false" in TEXT, "checkout credentials must not persist")
require(len(re.findall(r"grep -Eq ':1\[\.\]8\[\.\]1\(\[\[:space:\]\]\|\$\)'", TEXT)) == 2,
        "both serialization version assertions must use the tested extended-regex predicate")
require(not re.search(r"grep -q ':1\[\.\]8\[\.\]1\(\[\[:space:\]\]\|\$\)'", TEXT),
        "serialization version assertion must not use basic grep with ERE syntax")

# Exercise the exact grep predicate used by the workflow against positive and
# negative examples, including a near-match that must not be accepted.
pattern = r":1[.]8[.]1([[:space:]]|$)"
cases = [
    ("org.jetbrains.kotlinx:kotlinx-serialization-core:1.8.1", True),
    ("org.jetbrains.kotlinx:kotlinx-serialization-json:1.8.1 (by constraint)", True),
    ("org.jetbrains.kotlinx:kotlinx-serialization-core:1.7.3", False),
    ("org.jetbrains.kotlinx:kotlinx-serialization-core:1.8.10", False),
]
for sample, expected in cases:
    result = subprocess.run(
        ["grep", "-Eq", pattern],
        input=sample + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    require((result.returncode == 0) == expected, f"serialization version predicate misclassified: {sample}")

if errors:
    for error in errors:
        print(f"WORKFLOW_GUARD_FAILURE: {error}")
    raise SystemExit(1)

print("WORKFLOW_GUARD_SUMMARY structural_checks=passed serialization_predicate_cases=4 passed=4 failed=0")

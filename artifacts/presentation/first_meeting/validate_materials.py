"""Validate the presentation revision without changing original research artifacts."""

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(arguments, cwd, log, env=None):
    run = subprocess.run(arguments, cwd=cwd, env=env, capture_output=True, text=True)
    (OUT / log).write_text(run.stdout + run.stderr, encoding="utf-8")
    return {"arguments": arguments, "cwd": str(cwd), "exit_code": run.returncode,
            "stdout": run.stdout, "stderr": run.stderr}


def main():
    checks = {}
    preserved = json.loads((OUT / "preserved_files.json").read_text(encoding="utf-8"))
    changed = [name for name, expected in preserved.items()
               if not (ROOT / name).is_file() or sha(ROOT / name) != expected]
    checks["existing_files_unchanged_before_validation"] = not changed
    checks["existing_files_count"] = len(preserved)
    (OUT / "validation").mkdir(exist_ok=True)
    pytest = command([sys.executable, "-m", "pytest", "-q",
                      f"--junitxml={OUT / 'validation/pytest.xml'}"],
                     ROOT, "validation/pytest.log")
    checks["pytest"] = pytest
    if pytest["exit_code"] == 0:
        xml = ElementTree.parse(OUT / "validation/pytest.xml").getroot()
        checks["test_counts"] = {"tests": len(list(xml.iter("testcase"))),
                                "failures": len(list(xml.iter("failure"))),
                                "errors": len(list(xml.iter("error"))),
                                "skipped": len(list(xml.iter("skipped")))}
    runs, signatures = [], []
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    for index in (1, 2):
        cwd = OUT / "validation" / f"run_{index}"
        cwd.mkdir(parents=True, exist_ok=True)
        result = command([sys.executable, "-m", "stackgraph", "--offline",
                          "--sample", str(ROOT / "data/sample.json"),
                          "--cache", str(ROOT / "data/cache")],
                         cwd, f"validation/offline_{index}.log", env)
        if result["exit_code"] == 0:
            result["execution"] = json.loads(result["stdout"])
            signatures.append({p: sha(cwd / p) for p in (
                "artifacts/analysis.json", "artifacts/graph.png", "results.md")})
        runs.append(result)
    checks["offline_runs"] = runs
    checks["two_run_byte_identical"] = len(signatures) == 2 and signatures[0] == signatures[1]
    checks["identical_to_existing_outputs"] = bool(signatures) and all(
        digest == sha(ROOT / p) for p, digest in signatures[0].items())
    checks["reproduction_sha256"] = signatures[-1] if signatures else {}
    prs = {}
    cache_count = 0
    for path in (ROOT / "data/cache").glob("*.json"):
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        canonical = json.dumps(snapshot["data"], sort_keys=True, ensure_ascii=True).encode()
        assert hashlib.sha256(canonical).hexdigest() == snapshot["data_sha256"]
        assert snapshot["http_status"] == 200
        if isinstance(snapshot["data"], dict):
            prs[snapshot["data"]["number"]] = snapshot["data"]
        cache_count += 1
    checks["valid_cached_payloads"] = cache_count
    proof = json.loads((OUT.parent / "audit_evidence.json").read_text(encoding="utf-8"))
    for edge in proof["verified_edges"]:
        p, q = prs[edge["prerequisite"]], prs[edge["dependent"]]
        assert p["head"]["repo"]["full_name"] == q["base"]["repo"]["full_name"]
        assert p["head"]["ref"] == q["base"]["ref"]
        assert p["head"]["sha"] == q["base"]["sha"]
    checks["verified_edges"] = len(proof["verified_edges"])
    checks["brief_pdf_pages"] = len(re.findall(rb"/Type\s*/Page\b", (OUT / "research_brief.pdf").read_bytes()))
    changed = [name for name, expected in preserved.items()
               if not (ROOT / name).is_file() or sha(ROOT / name) != expected]
    checks["changed_existing_files"] = changed
    checks["existing_files_unchanged_after_validation"] = not changed
    question = ("To what extent can dependency-graph information improve the identification of stacked "
                "pull-request workflows compared with event-based heuristics, under constrained GitHub API access?")
    checks["exact_research_question_in_brief"] = question in (OUT / "research_brief.md").read_text(encoding="utf-8")
    script = (OUT / "presentation_script.md").read_text(encoding="utf-8")
    speech = " ".join(line[1:].strip() for line in script.splitlines() if line.startswith(">"))
    checks["speech_word_count"] = len(speech.split())
    failures = []
    for key in ("existing_files_unchanged_before_validation", "existing_files_unchanged_after_validation",
                "two_run_byte_identical", "identical_to_existing_outputs", "exact_research_question_in_brief"):
        if not checks[key]:
            failures.append(key)
    if pytest["exit_code"] or checks.get("test_counts", {}).get("tests") != 32:
        failures.append("pytest")
    if checks["brief_pdf_pages"] != 1:
        failures.append("brief_pdf_pages")
    for index, run in enumerate(runs, 1):
        if run["exit_code"] or run.get("execution", {}).get("network_requests") != 0:
            failures.append(f"offline_run_{index}")
    checks["failure_summary"] = failures
    checks["validated_at"] = datetime.now(timezone.utc).isoformat()
    (OUT / "validation.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: checks[k] for k in ("test_counts", "two_run_byte_identical",
          "identical_to_existing_outputs", "existing_files_count", "changed_existing_files",
          "valid_cached_payloads", "verified_edges", "brief_pdf_pages", "speech_word_count", "failure_summary")}, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())

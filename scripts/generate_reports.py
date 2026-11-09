"""Run the test suite once and write the four test reports to docs/reports/.

    python scripts/generate_reports.py

Writes unit-test-report.md, system-validation-report.md, code-coverage-report.md
and branch-coverage-report.md, plus the raw junit.xml and coverage.json they come from.
"""

import datetime
import json
import os
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "docs" / "reports"
RAW = REPORTS / "raw"
PLAN = ROOT / "TestPlan.md"
ENGINE_GATE = 80.0  # NFR-06
CASE_MAP = ROOT / "scripts" / "test_case_map.json"

# Checks that need a person or specific hardware. Update the status when one is done.
MANUAL_CHECKS = [
    ("NFR-02", "Usability study with five first-time users", "docs/USABILITY_STUDY.md"),
    ("NFR-01, NFR-07", "Roll-to-display time on the reference machine (2 and 4 players)", "Test Plan TC-N01-1, TC-N07-1"),
    ("NFR-12", "Animation frame rate on the reference machine", "Test Plan TC-N12-1"),
    ("NFR-14", "Peak memory over a 30-minute session on the reference machine", "Test Plan TC-N14-1"),
    ("NFR-05", "Smoke run on a real display on Windows, Ubuntu and macOS", "Test Plan TC-N05-1"),
    ("NFR-09", "Visual check of native windows at 1280x720, 1366x768 and 1920x1080", "Test Plan TC-N09-1"),
]


def run(command, **kwargs):
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True, **kwargs)


def git(*args):
    result = run(["git", *args])
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def ranges(numbers):
    numbers = sorted(numbers)
    spans, start = [], None
    for index, number in enumerate(numbers):
        if start is None:
            start = previous = number
        elif number == previous + 1:
            previous = number
        else:
            spans.append((start, previous))
            start = previous = number
        if index == len(numbers) - 1:
            spans.append((start, previous))
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in spans) or "none"


def percent(covered, total):
    return 100.0 if total == 0 else 100.0 * covered / total


def run_suite():
    RAW.mkdir(parents=True, exist_ok=True)
    junit, coverage_json = RAW / "junit.xml", RAW / "coverage.json"
    env = {**os.environ, "COVERAGE_FILE": str(RAW / ".coverage")}
    pytest_run = run(
        [sys.executable, "-m", "coverage", "run", "--branch", "--source=snakes_ladders",
         "-m", "pytest", "-q", "-p", "no:cacheprovider", f"--junitxml={junit}"],
        env=env,
    )
    run([sys.executable, "-m", "coverage", "json", "-o", str(coverage_json)], env=env)
    (RAW / ".coverage").unlink(missing_ok=True)
    return pytest_run.returncode, junit, coverage_json


def test_file_for(classname):
    parts = classname.split(".")
    while parts and not (ROOT / ("/".join(parts) + ".py")).exists():
        parts.pop()
    return "/".join(parts) + ".py" if parts else classname


def read_junit(path):
    results = defaultdict(lambda: {"tests": 0, "passed": 0, "failed": 0, "skipped": 0, "time": 0.0, "failures": []})
    test_cases = []
    for case in ET.parse(path).getroot().iter("testcase"):
        file = test_file_for(case.get("classname", ""))
        entry = results[file]
        entry["tests"] += 1
        entry["time"] += float(case.get("time", 0))
        if case.find("failure") is not None or case.find("error") is not None:
            entry["failed"] += 1
            entry["failures"].append(case.get("name"))
            outcome = "failed"
        elif case.find("skipped") is not None:
            entry["skipped"] += 1
            outcome = "skipped"
        else:
            entry["passed"] += 1
            outcome = "passed"
        test_cases.append({"file": file, "function": case.get("name", "").split("[")[0], "outcome": outcome})
    return results, test_cases


def is_system_file(path):
    """System validation: the test drives screens or the application loop."""
    text = (ROOT / path).read_text(encoding="utf-8-sig")
    return bool(re.search(r"^\s*import pygame|^\s*from snakes_ladders\.ui|snakes_ladders\.main|from snakes_ladders import main", text, re.M))


def requirements_in(path):
    text = (ROOT / path).read_text(encoding="utf-8-sig")
    return ", ".join(sorted(set(re.findall(r"\b(?:FR|NFR|SEC)-\d{2}\b", text)))) or "none cited"


def environment():
    import pygame  # noqa: PLC0415 (only needed for the version string)
    return [
        f"- Date: {datetime.date.today().isoformat()}",
        f"- Commit: {git('rev-parse', '--short', 'HEAD')} on branch {git('branch', '--show-current')}",
        f"- Python {platform.python_version()} on {platform.platform()}",
        f"- Pygame {pygame.version.ver}, run headless (SDL dummy video and audio drivers)",
        "- Command: `python scripts/generate_reports.py`",
    ]


def results_section(files, results):
    rows, totals = [], defaultdict(float)
    for path in sorted(files):
        entry = results[path]
        rows.append((f"`{path}`", entry["tests"], entry["passed"], entry["failed"], entry["skipped"],
                     f"{entry['time']:.1f}", requirements_in(path)))
        for key in ("tests", "passed", "failed", "skipped", "time"):
            totals[key] += entry[key]
    summary = table(
        ["Tests", "Passed", "Failed", "Skipped", "Time (s)"],
        [(int(totals["tests"]), int(totals["passed"]), int(totals["failed"]), int(totals["skipped"]), f"{totals['time']:.1f}")],
    )
    detail = table(["File", "Tests", "Passed", "Failed", "Skipped", "Time (s)", "Requirements cited"], rows)
    failures = [f"- `{path}`: {name}" for path in sorted(files) for name in results[path]["failures"]]
    return summary, detail, "\n".join(failures) if failures else "None."


def write_unit_report(results, files, header):
    summary, detail, failures = results_section(files, results)
    (REPORTS / "unit-test-report.md").write_text(f"""# Unit test report

{chr(10).join(header)}

A unit test exercises the rules, the controller or the persistence layer directly. It does not render a screen or start the application loop. This level also holds the integration tests that run without a display, such as the 100 seeded full games for NFR-03.

## Summary

{summary}

## Results by file

{detail}

## Failures

{failures}
""", encoding="utf-8")


def plan_cases():
    cases = []
    for line in PLAN.read_text(encoding="utf-8-sig").splitlines():
        if not re.match(r"\|\s*TC-[A-Z0-9]+-\d+\s*\|", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        cases.append({"id": cells[0], "what": cells[1][:70], "level": cells[-2], "req": cells[-1]})
    return cases


def load_case_map():
    """Hand-kept links from Test Plan cases to tests that do not carry the case ID in their code."""
    return json.loads(CASE_MAP.read_text(encoding="utf-8")) if CASE_MAP.exists() else {}


def mapped_outcomes(entry, test_cases):
    """Outcomes of the tests a map entry names, and the names that match no test."""
    outcomes, missing = [], []
    for node in entry.get("tests", []):
        file, _, function = node.partition("::")
        found = [c for c in test_cases if c["file"] == file and function in ("*", c["function"])]
        outcomes += [c["outcome"] for c in found]
        if not found:
            missing.append(node)
    return outcomes, missing


def plan_status(cases, results, test_cases):
    cited_by = defaultdict(set)
    for path in results:
        for case_id in re.findall(r"TC-[A-Z0-9]+-\d+", (ROOT / path).read_text(encoding="utf-8-sig")):
            cited_by[case_id].add(path)
    case_map = load_case_map()
    rows, counts = [], defaultdict(int)
    for case in cases:
        levels = re.findall(r"\b[UISA][am]\b", case["level"])
        has_manual = any(level.endswith("m") for level in levels)
        manual_only = bool(levels) and all(level.endswith("m") for level in levels)
        entry = case_map.get(case["id"], {})
        files = cited_by.get(case["id"], set())
        outcomes, missing = mapped_outcomes(entry, test_cases)
        has_evidence = bool(files or outcomes or entry.get("evidence"))
        failed = any(results[path]["failed"] for path in files) or "failed" in outcomes
        if missing:
            status = "Mapping error: test not found"
        elif failed:
            status = "Failed"
        elif has_evidence:
            status = "Automated part passed; manual part not run" if has_manual else "Passed"
        elif manual_only:
            status = "Not run (manual)"
        else:
            status = "No automated test"
        evidence = [f"`{Path(path).name}`" for path in sorted(files)[:2]]
        evidence += [f"`{node.split('/')[-1]}`" for node in entry.get("tests", [])[:2]]
        evidence += [entry["evidence"]] if entry.get("evidence") else []
        evidence += [entry["note"]] if entry.get("note") else []
        counts[status] += 1
        rows.append((case["id"], case["what"].replace("|", "/"), case["level"], case["req"], status,
                     "; ".join(evidence) or "none"))
    return rows, counts


def write_system_report(results, files, header, cases, test_cases):
    summary, detail, failures = results_section(files, results)
    plan_rows, counts = plan_status(cases, results, test_cases)
    count_table = table(["Status", "Cases"], [(status, count) for status, count in sorted(counts.items())])
    manual_rows = [(req, check, "Not run", where) for req, check, where in MANUAL_CHECKS]
    (REPORTS / "system-validation-report.md").write_text(f"""# System validation report

{chr(10).join(header)}

System validation drives whole screens or the real application loop. These tests render the setup, game and result screens, play moves through `main()`, and measure the non-functional requirements end to end. They run headless, so they do not replace the manual checks listed below.

## Automated results

{summary}

{detail}

### Failures

{failures}

## Manual and hardware checks

Nobody has run these yet. They need a person, a real display or the minimum-hardware machine named in the Test Plan.

{table(["Requirements", "Check", "Status", "Where it is defined"], manual_rows)}

## Test Plan execution

The Test Plan has {len(cases)} cases. A case counts as run when an automated test cites its ID, or when `scripts/test_case_map.json` names a test for it. The generator checks that every named test exists and did not fail.

{count_table}

{table(["Case", "Procedure", "Level", "Requirement", "Status", "Evidence"], plan_rows)}
""", encoding="utf-8")


def package_of(path):
    parts = Path(path.replace("\\", "/")).parts
    return parts[1] if len(parts) > 2 else parts[-1]


def write_coverage_reports(data, header):
    files = {path.replace("\\", "/"): info for path, info in data["files"].items()}
    totals = data["totals"]
    statement_rows, branch_rows, package_totals = [], [], defaultdict(lambda: defaultdict(int))
    for path in sorted(files):
        info, summary = files[path], files[path]["summary"]
        covered, count = summary["covered_lines"], summary["num_statements"]
        statement_rows.append((f"`{path}`", count, summary["missing_lines"], f"{percent(covered, count):.1f}%", ranges(info["missing_lines"])))
        branches, taken = summary.get("num_branches", 0), summary.get("covered_branches", 0)
        branch_rows.append((f"`{path}`", branches, taken, summary.get("num_partial_branches", 0),
                            "n/a" if branches == 0 else f"{percent(taken, branches):.1f}%"))
        package = package_of(path)
        for key, value in (("stmts", count), ("covered", covered), ("branches", branches), ("taken", taken)):
            package_totals[package][key] += value

    stmt_total = totals["num_statements"]
    stmt_pct = percent(totals["covered_lines"], stmt_total)
    branch_total, branch_taken = totals.get("num_branches", 0), totals.get("covered_branches", 0)
    branch_pct = percent(branch_taken, branch_total)
    engine = package_totals["engine"]
    engine_pct = percent(engine["covered"], engine["stmts"])
    verdict = "meets" if engine_pct >= ENGINE_GATE else "is below"

    package_rows = [(f"`{name}`", values["stmts"], f"{percent(values['covered'], values['stmts']):.1f}%",
                     values["branches"], "n/a" if not values["branches"] else f"{percent(values['taken'], values['branches']):.1f}%")
                    for name, values in sorted(package_totals.items())]

    (REPORTS / "code-coverage-report.md").write_text(f"""# Code coverage report (statement coverage)

{chr(10).join(header)}

Statement coverage is the share of executable lines that ran at least once during the full test suite.

## Summary

Overall statement coverage is **{stmt_pct:.1f}%** ({totals["covered_lines"]} of {stmt_total} statements). Coverage of `snakes_ladders/engine/` is **{engine_pct:.1f}%**, which {verdict} the {ENGINE_GATE:.0f}% requirement in NFR-06. CI fails the build below that figure.

## By package

{table(["Package", "Statements", "Statement coverage", "Branches", "Branch coverage"], package_rows)}

## By file

{table(["File", "Statements", "Missed", "Coverage", "Lines not run"], statement_rows)}
""", encoding="utf-8")

    missing_sections = []
    for path in sorted(files):
        missing = files[path].get("missing_branches", [])
        if missing:
            shown = ", ".join(f"{a}→{'exit' if b < 0 else b}" for a, b in missing[:12])
            more = f" (and {len(missing) - 12} more)" if len(missing) > 12 else ""
            missing_sections.append(f"- `{path}`: {shown}{more}")

    (REPORTS / "branch-coverage-report.md").write_text(f"""# Branch coverage report

{chr(10).join(header)}

Branch coverage counts each outcome of every decision point, such as the true and false side of an `if`. A line can run while one of its branches never does, so this figure is stricter than statement coverage.

## Summary

Overall branch coverage is **{branch_pct:.1f}%** ({branch_taken} of {branch_total} branches taken, {totals.get("num_partial_branches", 0)} partially covered). Combined statement and branch coverage, as `coverage.py` reports it, is **{totals["percent_covered"]:.1f}%**.

## By package

{table(["Package", "Statements", "Statement coverage", "Branches", "Branch coverage"], package_rows)}

## By file

{table(["File", "Branches", "Taken", "Partial", "Branch coverage"], branch_rows)}

## Branches never taken

Each entry is `line→target line`, or `line→exit` when the branch leaves the function.

{chr(10).join(missing_sections) if missing_sections else "None."}
""", encoding="utf-8")
    return stmt_pct, branch_pct, engine_pct


def write_index(stmt_pct, branch_pct):
    (REPORTS / "README.md").write_text(f"""# Test reports

Generated by `python scripts/generate_reports.py`. Run it from the repository root with the project's virtual environment active.

| Report | What it shows |
|---|---|
| [unit-test-report.md](unit-test-report.md) | Results of the unit and component tests |
| [system-validation-report.md](system-validation-report.md) | Results of the screen-level and application-loop tests, the manual checks still to run, and execution against the Test Plan |
| [code-coverage-report.md](code-coverage-report.md) | Statement coverage ({stmt_pct:.1f}% overall) |
| [branch-coverage-report.md](branch-coverage-report.md) | Branch coverage ({branch_pct:.1f}% overall) |

The `raw/` folder holds the `junit.xml` and `coverage.json` files the reports are built from. Test Plan cases whose IDs are not written in the test code are linked to tests in `scripts/test_case_map.json`.
""", encoding="utf-8")


def main():
    code, junit, coverage_json = run_suite()
    results, test_cases = read_junit(junit)
    system = {path for path in results if is_system_file(path)}
    unit = set(results) - system
    header = environment()
    write_unit_report(results, unit, header)
    write_system_report(results, system, header, plan_cases(), test_cases)
    stmt_pct, branch_pct, engine_pct = write_coverage_reports(json.loads(coverage_json.read_text()), header)
    write_index(stmt_pct, branch_pct)
    total = sum(entry["tests"] for entry in results.values())
    failed = sum(entry["failed"] for entry in results.values())
    print(f"{total} tests, {failed} failed | statements {stmt_pct:.1f}% | branches {branch_pct:.1f}% | engine {engine_pct:.1f}%")
    print(f"reports written to {REPORTS}")
    return 1 if code or failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

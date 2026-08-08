"""DiffSeal command-line interface.

Commands:

- ``diffseal init``  create a minimal ``.diffseal.toml``
- ``diffseal plan``  show the execution plan without running tools
- ``diffseal run``   run collectors, evaluate, write evidence.json + evidence.md

Exit code contract (documented and tested):

- 0  GateDecision.PASS
- 1  GateDecision.FAIL
- 2  GateDecision.REVIEW_REQUIRED
- 3  GateDecision.INSUFFICIENT_EVIDENCE
- 4  CLI usage / configuration misuse
- 5  unexpected internal error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from diffseal import __version__
from diffseal.config import CONFIG_FILENAME, ConfigError, write_default_config
from diffseal.evaluate import GateDecision
from diffseal.run import RunError, plan, render_plan, run

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_REVIEW = 2
EXIT_INSUFFICIENT = 3
EXIT_USAGE = 4
EXIT_INTERNAL = 5


class _Parser(argparse.ArgumentParser):
    """ArgumentParser that reports usage errors with exit code 4."""

    def error(self, message: str) -> None:  # type: ignore[override]
        self.print_usage(sys.stderr)
        self.exit(EXIT_USAGE, f"{self.prog}: error: {message}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="diffseal",
        description="Local-first Python PR evidence gate for review readiness.",
    )
    parser.add_argument("--version", action="version", version=f"diffseal {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser(
        "init", help="create a minimal .diffseal.toml (refuses to overwrite)"
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing .diffseal.toml",
    )

    plan_parser = subparsers.add_parser(
        "plan", help="show which checks would execute without running tools"
    )
    plan_parser.add_argument("--config", type=Path, help="explicit .diffseal.toml path")

    run_parser = subparsers.add_parser(
        "run", help="run collectors, evaluate, and write evidence artifacts"
    )
    run_parser.add_argument("--config", type=Path, help="explicit .diffseal.toml path")
    run_parser.add_argument(
        "--output-dir",
        type=Path,
        help="directory for evidence.json / evidence.md (default: current directory)",
    )
    run_parser.add_argument(
        "--timeout",
        type=float,
        default=180.0,
        help="per-check tool timeout in seconds (default: 180)",
    )
    return parser


def _cmd_init(args: argparse.Namespace, cwd: Path) -> int:
    target = cwd / CONFIG_FILENAME
    if target.exists() and not args.force:
        print(f"refusing to overwrite existing {target}", file=sys.stderr)
        return EXIT_USAGE
    try:
        write_default_config(target, force=args.force)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    print(f"created {target}")
    print("next step: run 'diffseal plan' to review the execution plan, then 'diffseal run'.")
    return EXIT_OK


def _cmd_plan(args: argparse.Namespace, cwd: Path) -> int:
    try:
        plan_data = plan(cwd, config_path=args.config)
    except (ConfigError, RunError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    sys.stdout.write(render_plan(plan_data))
    return EXIT_OK


def _cmd_run(args: argparse.Namespace, cwd: Path) -> int:
    try:
        result = run(
            cwd=cwd,
            config_path=args.config,
            output_dir=args.output_dir,
            timeout=args.timeout,
        )
    except (ConfigError, RunError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE

    decision = result.decision
    print(f"decision: {decision.value}")
    print(f"evidence.json: {result.json_path}")
    print(f"evidence.md:   {result.markdown_path}")
    return {
        GateDecision.PASS: EXIT_OK,
        GateDecision.FAIL: EXIT_FAIL,
        GateDecision.REVIEW_REQUIRED: EXIT_REVIEW,
        GateDecision.INSUFFICIENT_EVIDENCE: EXIT_INSUFFICIENT,
    }[decision]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cwd = Path.cwd()
    try:
        if args.command == "init":
            return _cmd_init(args, cwd)
        if args.command == "plan":
            return _cmd_plan(args, cwd)
        if args.command == "run":
            return _cmd_run(args, cwd)
    except Exception as exc:  # pragma: no cover - last-resort safety net
        print(f"internal error: {exc}", file=sys.stderr)
        return EXIT_INTERNAL
    return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())

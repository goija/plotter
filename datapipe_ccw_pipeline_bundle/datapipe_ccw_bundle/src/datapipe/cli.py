from __future__ import annotations

import argparse
import sys

from .config import load_config
from .debruijn.states import build_reference_states
from .ingest.knmi import run_knmi
from .ingest.noaa import run_noaa
from .model.disturbance import build_daily_disturbance
from .model.score import score_day
from .normalize.daily import normalize_day
from .publish.report import publish_day
from .save_state import SaveStateError, commit_and_push
from .status import write_status


def cmd_build_states(args: argparse.Namespace) -> int:
    cfg = load_config()
    outputs = build_reference_states(cfg)
    print(f"SUCCESS: built {len(outputs)} de Bruijn reference file(s)")
    return 0


def cmd_daily(args: argparse.Namespace) -> int:
    cfg = load_config()
    date = args.date

    print(f"START: NOAA data run for {date}")
    noaa_result = run_noaa(date, cfg)
    if not noaa_result.ok:
        write_status(cfg.paths.status_dir / f"{date}_noaa.json", stage='noaa', date=date, status='failed', note=noaa_result.message)
        print(f"ERROR: {noaa_result.message}", file=sys.stderr)
        return 1
    print(f"SUCCESS: {noaa_result.message}")
    write_status(cfg.paths.status_dir / f"{date}_noaa.json", stage='noaa', date=date, status='success', note=noaa_result.message)

    if args.save_after_noaa:
        print("SAVE: NOAA succeeded, creating commit")
        try:
            commit_and_push(cfg.paths.repo_root, f"NOAA data saved for {date} [skip ci]")
        except SaveStateError as exc:
            print(f"ERROR: save after NOAA failed\n{exc}", file=sys.stderr)
            return 1

    print(f"START: KNMI data run for {date}")
    knmi_result = run_knmi(date, cfg, manual_fallback=True)
    if knmi_result.ok:
        print(f"SUCCESS: {knmi_result.message}")
        write_status(cfg.paths.status_dir / f"{date}_knmi.json", stage='knmi', date=date, status='success', note=knmi_result.message)
    else:
        print("NOTICE: KNMI data not available from automated source")
        print("ACTION: generating manual KNMI download helper")
        write_status(cfg.paths.status_dir / f"{date}_knmi.json", stage='knmi', date=date, status='manual_required', note=knmi_result.message)
        if args.save_manual_fallback:
            try:
                commit_and_push(cfg.paths.repo_root, f"KNMI manual fallback created for {date} [skip ci]")
            except SaveStateError as exc:
                print(f"ERROR: save after KNMI fallback failed\n{exc}", file=sys.stderr)
                return 1
        return 2

    print(f"START: normalize for {date}")
    normalize_day(date, cfg)
    print("SUCCESS: normalize completed")

    print("START: build states")
    build_reference_states(cfg)
    print("SUCCESS: state build completed")

    print(f"START: build daily disturbance for {date}")
    build_daily_disturbance(date, cfg)
    print("SUCCESS: disturbance build completed")

    print(f"START: score grid for {date}")
    score_day(date, cfg)
    print("SUCCESS: scoring completed")

    print(f"START: publish for {date}")
    publish_day(date, cfg)
    write_status(cfg.paths.status_dir / f"{date}_publish.json", stage='publish', date=date, status='success', note='Publish completed')
    print("SUCCESS: publish completed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='python -m datapipe.cli')
    sub = parser.add_subparsers(dest='command', required=True)

    p_states = sub.add_parser('build-states', help='Build Lyndon/FKM canonical de Bruijn states')
    p_states.set_defaults(func=cmd_build_states)

    p_daily = sub.add_parser('daily', help='Run the staged daily pipeline')
    p_daily.add_argument('--date', required=True)
    p_daily.add_argument('--save-after-noaa', action='store_true', default=True)
    p_daily.add_argument('--save-manual-fallback', action='store_true', default=True)
    p_daily.set_defaults(func=cmd_daily)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == '__main__':
    raise SystemExit(main())

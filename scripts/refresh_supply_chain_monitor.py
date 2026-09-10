"""Fetch supplier DART financials/news; snapshot existing industry macro series."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from committee.core.env_loader import load_project_env
from committee.industry_cycle.supply_chain_monitor import build_monitor, load_monitor, save_monitor


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute",action="store_true")
    parser.add_argument("--skip-news",action="store_true")
    parser.add_argument("--skip-financials",action="store_true")
    args=parser.parse_args()
    if not args.execute:
        print("dry_run: supplier DART financials, company RSS, existing industry news/macro -> snapshot; use --execute")
        return
    load_project_env(ROOT)
    result=build_monitor(previous=load_monitor(),network_news=not args.skip_news,network_financials=not args.skip_financials)
    save_monitor(result)
    print(json.dumps(result["summary"],ensure_ascii=True))


if __name__=="__main__":
    main()

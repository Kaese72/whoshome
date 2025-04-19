"""
Client for the whos home API
Both for reporting and for administration
"""

import argparse
import json
import os

import requests


def main_list(args: argparse.Namespace):
    """List reports in the service"""
    resp = requests.get(
        f"{args.base_url}/list",
        headers={"Authorization": f"bearer {args.token}"},
        timeout=30,
    )
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent="   "))


def main_report(args: argparse.Namespace):
    """Report that you are alive"""
    my_ip_response = requests.get("https://api.ipify.org?format=json", timeout=30)
    my_ip_response.raise_for_status()
    my_ip = my_ip_response.json()["ip"]
    resp = requests.post(
        f"{args.base_url}/report",
        headers={"Authorization": f"bearer {args.token}"},
        json={"ipv4": my_ip},
        timeout=30,
    )
    resp.raise_for_status()


def main_new_token(args: argparse.Namespace):
    """Print a new token from the service"""
    resp = requests.get(
        f"{args.base_url}/token/{args.identifier}",
        headers={"Authorization": f"bearer {args.token}"},
        timeout=30,
    )
    resp.raise_for_status()
    print(resp.text)


PARSER = argparse.ArgumentParser()
PARSER.add_argument("--token", type=str, default=os.environ.get("API_TOKEN"))
PARSER.add_argument("--base-url", type=str, default=os.environ.get("API_BASE_URL"))

SUBPARSERS = PARSER.add_subparsers(required=True)

REPORT_SUBPARSER = SUBPARSERS.add_parser("report")
REPORT_SUBPARSER.set_defaults(func=main_report)

LIST_SUBPARSER = SUBPARSERS.add_parser("list")
LIST_SUBPARSER.set_defaults(func=main_list)

NEW_TOKEN_SUBPARSER = SUBPARSERS.add_parser("new-token")
NEW_TOKEN_SUBPARSER.add_argument("identifier", type=str)
NEW_TOKEN_SUBPARSER.set_defaults(func=main_new_token)


ARGS = PARSER.parse_args()
assert ARGS.base_url, "must set API_BASE_URL"
assert ARGS.token, "must set API_TOKEN"
ARGS.func(ARGS)

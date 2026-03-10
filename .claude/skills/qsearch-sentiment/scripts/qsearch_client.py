#!/usr/bin/env python3
"""QSearch API client for fetching public opinion/sentiment data."""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError


class QSearchAPIError(Exception):
    """Raised when QSearch API returns an error."""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"QSearch API error (HTTP {status_code}): {message}")

BASE_URL = "https://api.qsearch.cc/api/trend"

CHANNELS = ["FB", "IG", "YT", "FORUM", "MEDIA", "BLOG", "FB_GROUP", "THREADS"]

DEFAULT_SORT = {
    "FB": "engagement_score",
    "IG": "like_count",
    "YT": "view_count",
    "FORUM": "comment_count",
    "MEDIA": "published_time",
    "BLOG": "published_time",
    "FB_GROUP": "engagement_score",
    "THREADS": "like_count",
}


def get_api_key():
    key = os.environ.get("QSEARCH_API_KEY", "")
    if not key:
        raise QSearchAPIError(0, "QSEARCH_API_KEY environment variable not set.")
    return key


def post_json(url, key, body):
    full_url = f"{url}?{urlencode({'key': key})}"
    data = json.dumps(body).encode("utf-8")
    req = Request(full_url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise QSearchAPIError(e.code, error_body)


def get_json(url, key, params=None):
    qs = {"key": key}
    if params:
        qs.update(params)
    full_url = f"{url}?{urlencode(qs, doseq=True)}"
    req = Request(full_url)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise QSearchAPIError(e.code, error_body)


def to_unix(date_str):
    """Convert YYYY-MM-DD to Unix timestamp."""
    return int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())


def hotposts(query, channel, start_date, end_date, country_code="TW", limit=10, sort_item=None, order_by="desc"):
    key = get_api_key()
    body = {
        "query": query,
        "start_time": to_unix(start_date),
        "end_time": to_unix(end_date),
        "country_code": country_code,
        "sort_item": sort_item or DEFAULT_SORT.get(channel, "published_time"),
        "order_by": order_by,
        "limit": limit,
        "offset": 0,
        "sentiments": ["positive", "negative", "neutral"],
    }
    return post_json(f"{BASE_URL}/v3/hotposts/{channel}", key, body)


def heatmap(query, channel, start_date, end_date, country_code="TW", interval="1d", matrix="post_count"):
    key = get_api_key()
    body = {
        "query": query,
        "start_time": to_unix(start_date),
        "end_time": to_unix(end_date),
        "country_code": country_code,
        "interval": interval,
        "matrix": matrix,
    }
    return post_json(f"{BASE_URL}/v3/heatmap/{channel}", key, body)


def hotposts_summary(query, channel, start_date, end_date):
    key = get_api_key()
    params = {"query": query, "start_date": start_date, "end_date": end_date}
    return get_json(f"{BASE_URL}/v3/hotposts_summary/{channel}", key, params)


def forum_top_channels(queries, start_date, end_date, country_code="TW"):
    key = get_api_key()
    body = {
        "queries": queries if isinstance(queries, list) else [queries],
        "start_time": to_unix(start_date),
        "end_time": to_unix(end_date),
        "country_code": country_code,
    }
    return post_json(f"{BASE_URL}/v3/topchannels/FORUM", key, body)


def google_trend(queries):
    key = get_api_key()
    return get_json(f"{BASE_URL}/v1/google_trend", key, {"q": queries})


def usage():
    key = get_api_key()
    return get_json(f"{BASE_URL}/usage", key)


def main():
    parser = argparse.ArgumentParser(description="QSearch API Client")
    sub = parser.add_subparsers(dest="command", required=True)

    # hotposts
    hp = sub.add_parser("hotposts", help="Fetch hot posts")
    hp.add_argument("query", help="Search keyword")
    hp.add_argument("--channel", default="FB", choices=CHANNELS)
    hp.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    hp.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    hp.add_argument("--country", default="TW")
    hp.add_argument("--limit", type=int, default=10)
    hp.add_argument("--sort", default=None)
    hp.add_argument("--order", default="desc", choices=["asc", "desc"])

    # heatmap
    hm = sub.add_parser("heatmap", help="Fetch heatmap data")
    hm.add_argument("query", help="Search keyword")
    hm.add_argument("--channel", default="FB", choices=CHANNELS)
    hm.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    hm.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    hm.add_argument("--country", default="TW")
    hm.add_argument("--interval", default="1d", choices=["1h", "6h", "1d", "7d"])
    hm.add_argument("--matrix", default="post_count")

    # summary
    sm = sub.add_parser("summary", help="Fetch AI summary")
    sm.add_argument("query", help="Search keyword")
    sm.add_argument("--channel", default="FB", choices=CHANNELS)
    sm.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    sm.add_argument("--end", required=True, help="End date YYYY-MM-DD")

    # top_channels
    tc = sub.add_parser("top_channels", help="Fetch forum top channels")
    tc.add_argument("queries", nargs="+", help="Search keywords")
    tc.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    tc.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    tc.add_argument("--country", default="TW")

    # google_trend
    gt = sub.add_parser("google_trend", help="Fetch Google Trend")
    gt.add_argument("queries", nargs="+", help="Query terms")

    # usage
    sub.add_parser("usage", help="Check API usage")

    args = parser.parse_args()

    if args.command == "hotposts":
        result = hotposts(args.query, args.channel, args.start, args.end, args.country, args.limit, args.sort, args.order)
    elif args.command == "heatmap":
        result = heatmap(args.query, args.channel, args.start, args.end, args.country, args.interval, args.matrix)
    elif args.command == "summary":
        result = hotposts_summary(args.query, args.channel, args.start, args.end)
    elif args.command == "top_channels":
        result = forum_top_channels(args.queries, args.start, args.end, args.country)
    elif args.command == "google_trend":
        result = google_trend(args.queries)
    elif args.command == "usage":
        result = usage()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

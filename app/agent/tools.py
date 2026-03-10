"""LangChain tool wrappers for QSearch sentiment API."""

import json
import logging
from datetime import datetime, timedelta
from langchain.tools import tool

from app.agent import qsearch_client
from app.agent.qsearch_client import QSearchAPIError

logger = logging.getLogger(__name__)


def _default_dates() -> tuple[str, str]:
    """Return (start_date, end_date) for the last 7 days."""
    end = datetime.now()
    start = end - timedelta(days=7)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def _safe_json(data: object) -> str:
    """Convert API response to a truncated JSON string for LLM consumption."""
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if len(text) > 6000:
        text = text[:6000] + "\n... (truncated)"
    return text


def _error_msg(e: QSearchAPIError, action: str) -> str:
    """Format a user-friendly error message for the LLM."""
    logger.error("QSearch API error during %s: %s", action, e)
    if e.status_code == 403:
        return (
            f"❌ QSearch API 權限不足 (HTTP 403)：{e.message}\n"
            f"此 API Key 可能沒有存取「{action}」的權限，請聯繫 QSearch 客服確認。"
        )
    if e.status_code == 401:
        return "❌ QSearch API Key 無效或未設定 (HTTP 401)，請確認 QSEARCH_API_KEY 環境變數。"
    return f"❌ QSearch API 呼叫失敗 (HTTP {e.status_code})：{e.message}"


@tool
def search_hotposts(
    keyword: str,
    channel: str = "FB",
    start_date: str = "",
    end_date: str = "",
    limit: int = 10,
) -> str:
    """Search hot/trending posts for a keyword on a social platform.

    Args:
        keyword: The search keyword (e.g. "AI", "台積電").
        channel: Platform code. One of: FB, IG, YT, FORUM, MEDIA, BLOG, FB_GROUP, THREADS. Default: FB.
        start_date: Start date in YYYY-MM-DD format. Default: 7 days ago.
        end_date: End date in YYYY-MM-DD format. Default: today.
        limit: Max number of posts to return (1-100). Default: 10.

    Returns:
        JSON string of hot posts with engagement metrics and sentiment.
    """
    try:
        default_start, default_end = _default_dates()
        start_date = start_date or default_start
        end_date = end_date or default_end
        limit = min(max(limit, 1), 100)
        result = qsearch_client.hotposts(keyword, channel, start_date, end_date, limit=limit)
        return _safe_json(result)
    except ValueError as e:
        return f"❌ 日期格式錯誤: {str(e)}。請確保日期格式為 YYYY-MM-DD。"
    except QSearchAPIError as e:
        return _error_msg(e, f"hotposts/{channel}")
    except Exception as e:
        return f"❌ 未知錯誤: {str(e)}"


@tool
def search_heatmap(
    keyword: str,
    channel: str = "FB",
    start_date: str = "",
    end_date: str = "",
    interval: str = "1d",
    matrix: str = "post_count",
) -> str:
    """Get volume/engagement trend (heatmap) over time for a keyword.

    Args:
        keyword: The search keyword.
        channel: Platform code. One of: FB, IG, YT, FORUM, MEDIA, BLOG, FB_GROUP, THREADS. Default: FB.
        start_date: Start date YYYY-MM-DD. Default: 7 days ago.
        end_date: End date YYYY-MM-DD. Default: today.
        interval: Time bucket size. One of: 1h, 6h, 1d, 7d. Default: 1d.
        matrix: Metric to aggregate. Default: post_count.

    Returns:
        JSON string of time-series data showing volume trend.
    """
    try:
        default_start, default_end = _default_dates()
        start_date = start_date or default_start
        end_date = end_date or default_end
        result = qsearch_client.heatmap(keyword, channel, start_date, end_date, interval=interval, matrix=matrix)
        return _safe_json(result)
    except ValueError as e:
        return f"❌ 日期格式錯誤: {str(e)}。請確保日期格式為 YYYY-MM-DD。"
    except QSearchAPIError as e:
        return _error_msg(e, f"heatmap/{channel}")
    except Exception as e:
        return f"❌ 未知錯誤: {str(e)}"


@tool
def search_summary(
    keyword: str,
    channel: str = "FB",
    start_date: str = "",
    end_date: str = "",
) -> str:
    """Get an AI-generated summary of public discussion sentiment for a keyword.

    Args:
        keyword: The search keyword.
        channel: Platform code. One of: FB, IG, YT, FORUM, MEDIA, BLOG, FB_GROUP, THREADS. Default: FB.
        start_date: Start date YYYY-MM-DD. Default: 7 days ago.
        end_date: End date YYYY-MM-DD. Default: today.

    Returns:
        AI-generated summary text about public sentiment and discussions.
    """
    try:
        default_start, default_end = _default_dates()
        start_date = start_date or default_start
        end_date = end_date or default_end
        result = qsearch_client.hotposts_summary(keyword, channel, start_date, end_date)
        return _safe_json(result)
    except ValueError as e:
        return f"❌ 日期格式錯誤: {str(e)}。請確保日期格式為 YYYY-MM-DD。"
    except QSearchAPIError as e:
        return _error_msg(e, f"hotposts_summary/{channel}")
    except Exception as e:
        return f"❌ 未知錯誤: {str(e)}"


@tool
def search_top_channels(
    keyword: str,
    start_date: str = "",
    end_date: str = "",
) -> str:
    """Rank forum boards/channels by mentions of a keyword.

    Args:
        keyword: The search keyword.
        start_date: Start date YYYY-MM-DD. Default: 7 days ago.
        end_date: End date YYYY-MM-DD. Default: today.

    Returns:
        JSON string ranking forum channels by keyword volume.
    """
    try:
        default_start, default_end = _default_dates()
        start_date = start_date or default_start
        end_date = end_date or default_end
        result = qsearch_client.forum_top_channels(keyword, start_date, end_date)
        return _safe_json(result)
    except ValueError as e:
        return f"❌ 日期格式錯誤: {str(e)}。請確保日期格式為 YYYY-MM-DD。"
    except QSearchAPIError as e:
        return _error_msg(e, "topchannels/FORUM")
    except Exception as e:
        return f"❌ 未知錯誤: {str(e)}"


@tool
def search_google_trend(keywords: str) -> str:
    """Compare Google search trends for keywords (comma-separated).

    Args:
        keywords: Comma-separated keywords to compare, e.g. "AI,機器學習,深度學習".

    Returns:
        JSON string of Google Trends comparison data.
    """
    try:
        kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
        result = qsearch_client.google_trend(kw_list)
        return _safe_json(result)
    except QSearchAPIError as e:
        return _error_msg(e, "google_trend")


@tool
def check_api_usage() -> str:
    """Check the remaining QSearch API quota.

    Returns:
        JSON string with max usage limit and current usage count.
    """
    try:
        result = qsearch_client.usage()
        return _safe_json(result)
    except QSearchAPIError as e:
        return _error_msg(e, "usage")


ALL_TOOLS = [
    search_hotposts,
    # search_heatmap,
    # search_summary,
    # search_top_channels,
    # search_google_trend,
    # check_api_usage,
]

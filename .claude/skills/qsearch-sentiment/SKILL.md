---
name: qsearch-sentiment
description: Search and analyze public opinion (輿情) data using the QSearch API. Fetches hot posts, engagement heatmaps, AI summaries, and forum rankings across social platforms (Facebook, Instagram, YouTube, PTT/Dcard forums, news media, blogs, FB groups, Threads). Use when the user asks to search a keyword's public sentiment, check online buzz, find trending discussions, or mentions "輿情", "搜尋輿情", "網路聲量", "社群討論", "public opinion", "sentiment search", "social listening", or "trending topics".
---

# QSearch Sentiment Search

Search public opinion data across 8 social platforms via QSearch API.

## Prerequisites

Set `QSEARCH_API_KEY` environment variable with a valid QSearch API key.

## Workflow

### 1. Parse User Request

Extract from the user's message:
- **keyword** (required): the search term
- **platforms**: which channels to search (default: search all major ones — FB, FORUM, MEDIA, IG)
- **date range**: start/end dates (default: last 7 days)
- **country**: default `TW`

If the user doesn't specify platforms, search across FB, FORUM, MEDIA, and IG for a broad overview.

### 2. Fetch Data

Use `scripts/qsearch_client.py` to call the API. The script handles authentication via `QSEARCH_API_KEY` env var.

**Common commands:**

```bash
# Hot posts on Facebook
python3 scripts/qsearch_client.py hotposts "關鍵字" --channel FB --start 2026-02-25 --end 2026-03-04 --limit 10

# Heatmap (volume over time)
python3 scripts/qsearch_client.py heatmap "關鍵字" --channel FB --start 2026-02-25 --end 2026-03-04 --interval 1d --matrix post_count

# AI-generated summary
python3 scripts/qsearch_client.py summary "關鍵字" --channel FB --start 2026-02-25 --end 2026-03-04

# Forum top channels
python3 scripts/qsearch_client.py top_channels "關鍵字" --start 2026-02-25 --end 2026-03-04

# Google Trend
python3 scripts/qsearch_client.py google_trend "關鍵字1" "關鍵字2"

# Check API usage
python3 scripts/qsearch_client.py usage
```

Available channels: `FB`, `IG`, `YT`, `FORUM`, `MEDIA`, `BLOG`, `FB_GROUP`, `THREADS`

### 3. Analyze & Present Results

After fetching data, synthesize a report in Traditional Chinese covering:

1. **聲量概況**: total post count and trend (from heatmap data)
2. **情緒分析**: sentiment distribution (positive/negative/neutral ratios from hotposts)
3. **熱門討論**: top posts with key metrics (engagement, comments, shares)
4. **討論平台分布**: which platforms have the most activity
5. **關鍵洞察**: notable patterns, spikes, or themes

Format numbers with commas. Present hotposts as a table or ranked list with links when available.

### 4. Multi-platform Overview Strategy

When providing a comprehensive overview:

1. Fetch **heatmap** (post_count) from each platform to compare volume
2. Fetch **hotposts** (limit=5) from top 2-3 platforms by volume
3. Fetch **AI summary** from the highest-volume platform
4. If FORUM has activity, fetch **top_channels** to identify key discussion boards

This gives a balanced view without excessive API calls.

## API Details

For full endpoint specifications, parameter options, and constraints, see [references/qsearch_api.md](references/qsearch_api.md).

Key constraints:
- `limit` max: 3000 per request
- `offset + limit` max: 10000
- Heatmap interval restrictions based on date range (see reference)
- All timestamps are Unix seconds (handled by the script)

# QSearch API Reference

## Base URL

`https://api.qsearch.cc/api/trend`

## Authentication

All endpoints require `key` query parameter (API key). Store in environment variable `QSEARCH_API_KEY`.

## Platforms (Channels)

| Channel Code | Platform |
|---|---|
| FB | Facebook |
| IG | Instagram |
| YT | YouTube |
| FORUM | 論壇 (PTT, Dcard, etc.) |
| MEDIA | 新聞媒體 |
| BLOG | 部落格 |
| FB_GROUP | Facebook 社團 |
| THREADS | Threads |

## Country Codes

- `Global` - 全球
- `TW` - 台灣 (default for most use cases)
- `HK` - 香港
- `MY` - 馬來西亞
- `SG` - 新加坡
- `ID` - 印尼 (FB only)
- `PH` - 菲律賓 (FB only)
- `TH` - 泰國 (FB only)
- `VN` - 越南 (FB only)

Note: IG/YT only support Global, TW, HK, MY, SG. Forum/Media/Blog/FB_GROUP/Threads only support Global, TW.

## Endpoints

### 1. Hotposts (熱門文章) - POST `/v3/hotposts/{channel}`

Retrieve top posts for a keyword on a given platform.

**Request Body:**

```json
{
  "query": "關鍵字",
  "start_time": 1700000000,
  "end_time": 1700100000,
  "country_code": "TW",
  "sort_item": "engagement_score",
  "order_by": "desc",
  "limit": 10,
  "offset": 0,
  "sentiments": ["positive", "negative", "neutral"]
}
```

**sort_item by channel:**

| Channel | Sort Options |
|---|---|
| FB | engagement_score, comment_count, share_count, reaction_count, like_count, love_count, wow_count, sad_count, angry_count, haha_count, sentiment.magnitude, published_time |
| IG | published_time, like_count, comment_count, sentiment.magnitude |
| YT | published_time, view_count, like_count, comment_count, sentiment.magnitude |
| FORUM | published_time, comment_count, sentiment.magnitude |
| MEDIA | published_time, media_value, sentiment.magnitude |
| BLOG | published_time, sentiment.magnitude |
| FB_GROUP | published_time, engagement_score, like_count, comment_count, share_count, sentiment.magnitude |
| THREADS | published_time, like_count, child_post_count, sentiment.magnitude |

**Optional filters:**
- FB: `fan_count_range` - e.g. `[1000, null]` for pages with 1000+ fans
- IG: `follower_count_range`
- YT: `subscriber_count_range`

**Constraints:**
- `limit` max: 3000
- `offset + limit` max: 10000

### 2. Heatmap (聲量熱度) - POST `/v3/heatmap/{channel}`

Retrieve time-series volume/engagement data.

**Request Body:**

```json
{
  "query": "關鍵字",
  "start_time": 1700000000,
  "end_time": 1700100000,
  "country_code": "TW",
  "interval": "1d",
  "matrix": "post_count"
}
```

**interval constraints:**
- Date range >= 29 days: `1d` or `7d` only
- Date range 14-29 days: `1d` only
- Date range < 14 days: `1h`, `6h`, `1d`
- Date range < 1 day: `1h` only

**matrix by channel:**

| Channel | Matrix Options |
|---|---|
| FB | post_count, engagement_score, comment_count, share_count, reaction_count, like_count, love_count, wow_count, sad_count, angry_count, haha_count, neutral_post, positive_post, negative_post |
| IG | post_count, like_count, comment_count, neutral_post, positive_post, negative_post |
| YT | post_count, view_count, like_count, comment_count, neutral_post, positive_post, negative_post |
| FORUM | post_count, comment_count, neutral_post, positive_post, negative_post |
| MEDIA | post_count, neutral_post, positive_post, negative_post |
| BLOG | post_count, neutral_post, positive_post, negative_post |
| FB_GROUP | engagement_score, comment_count, share_count, reaction_count, like_count, love_count, wow_count, sad_count, angry_count, haha_count, neutral_post, positive_post, negative_post |
| THREADS | post_count, like_count, child_post_count, neutral_post, positive_post, negative_post |

### 3. Hotposts Summary (AI 摘要) - GET `/v3/hotposts_summary/{channel}`

AI-generated summary of hotposts for a keyword.

**Query Parameters:**
- `key`: API key
- `query`: keyword (default: "大巨蛋")
- `start_date`: YYYY-MM-DD format
- `end_date`: YYYY-MM-DD format
- `summary_prompt`: custom prompt for AI summarization (optional)

### 4. Forum Top Channels (論壇排行) - POST `/v3/topchannels/FORUM`

Rank forums/boards by keyword mentions.

**Request Body:**

```json
{
  "queries": ["關鍵字1", "關鍵字2"],
  "start_time": 1700000000,
  "end_time": 1700100000,
  "country_code": "TW"
}
```

### 5. Google Trend - GET `/v1/google_trend`

**Query Parameters:**
- `q`: array of query terms (default: ["query"])
- `key`: API key

### 6. API Usage - GET `/usage`

Returns `max_usage_limit` and `usage_count`.

## Error Codes

| Code | Meaning |
|---|---|
| 400 | Bad Request - invalid parameters |
| 401 | Unauthorized - invalid API key |
| 403 | Forbidden - access denied |
| 422 | Validation Error - malformed request |
| 500 | Internal Server Error |

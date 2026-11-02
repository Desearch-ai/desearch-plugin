---
name: desearch-social
description: Read public YouTube, Reddit, Threads, TikTok, Facebook, and Instagram data with the Desearch MCP tools youtube, reddit, threads, tiktok, facebook, and instagram. Use when the user asks for videos, transcripts, comments, channels, subreddits, posts, profiles, or hashtags on those platforms, or for the next page of them. Each call is billed.
---

# Desearch social data

Six tools read public social data, one per platform: `youtube`, `reddit`, `threads`, `tiktok`, `facebook`, and `instagram`. Each takes an `action` that picks one public route, plus that action's arguments. A missing argument, or one the action does not take, is refused before any request with a message that lists what the action takes, so read the message and call again. They only read: they do not post, comment, follow, or change an account.

The plugin launches `npx -y desearch-mcp-server@0.8.0`, which registers these tools. To find people or creators who match a description, use the `desearch-people-search` skill instead. For X posts, use `x-search` and the other X tools.

## Billing

- `youtube`, `reddit`, and `threads`: $2.07 per 1,000 requests. Every call is one request, including an empty page. A 404 (for example a video without captions), a 422 (a bad argument or cursor), and a 5xx are not charged.
- `tiktok`, `facebook`, and `instagram`: $2.07 per 1,000 items returned (posts, profiles, or comments).

Current prices are at https://desearch.ai/pricing. Read only the pages the user needs.

## Paging

A list action returns `{ "results": [...], "next_cursor": ..., "next": ... }`. When `next_cursor` is not null, call the same tool with the same action and the same target (query, video, channel, subreddit, post, user, or tag) and set `cursor` to `next_cursor`, unchanged. `next_cursor` is null on the last page. A cursor works for 24 hours; any other value returns HTTP 422 (not charged). Single items (a video, transcript, channel, subreddit, post, profile, or media item) come back as the API sends them.

A page shorter than usual is not the end; only a null `next_cursor` is. Threads, TikTok `trending`, and Instagram `search` return one page and take no cursor.

## YouTube (`youtube`)

| Action | Arguments | Pages |
|--------|-----------|-------|
| `search` | `query` (required, up to 500 characters; `intitle:"..."` for stricter title matching), `type` (`videos`, `shorts`, `channels`, `playlists`; omit for mixed results), `upload_date` (`today`, `this_week`, `this_month`, `this_year`), `sort_by` (`relevance`, `popular`), `duration` (`under_3_min`, `between_3_and_20_min`, `over_20_min`; videos only), `cursor` | Yes |
| `video` | `id` (required): video or Short ID, or its URL | No |
| `transcript` | `video_id` (required), `language` (optional, for example `en` or `es`; omit for the default track) | No |
| `comments` | `video_id` (required), `order` (`top`, `newest`), `cursor` | Yes |
| `channel` | `handle` (required): handle with or without `@`, or a `UC...` channel ID | No |
| `channel_videos` | `handle` (required), `sort` (`latest`, `popular`), `cursor` | Yes |

Each `search` result has a `type` (`video`, `short`, `live`, `channel`, or `playlist`); channel and playlist results may have no `url`. `video` returns the channel, views, likes, comment count, chapters, and `captionLanguages`. `transcript` returns `text` (the whole transcript) and timestamped `segments`; a video without captions returns 404. To answer "what does this video say", call `transcript`, not `video`.

## Reddit (`reddit`)

| Action | Arguments | Pages |
|--------|-----------|-------|
| `search` | `query` (required, up to 500 characters), `sort` (`relevance`, `new`, `top`, `comment_count`), `timeframe` (`all`, `day`, `week`, `month`, `year`), `cursor` | Yes |
| `subreddit` | `name` (required): the subreddit name, case-sensitive (`AskReddit`, not `askreddit`); a leading `r/` is removed | No |
| `subreddit_posts` | `name` (required), `sort` (`best`, `hot`, `new`, `top`, `rising`), `timeframe` (applies to `top`), `cursor` | Yes |
| `post` | `id` (required): post ID (with or without `t3_`) or URL. Returns the post without comments. | No |
| `comments` | `post_id` (required), `cursor` | Yes |

The two `sort` lists differ: a `search` sort on `subreddit_posts` (or the other way round) is refused before the request. `comments` returns a tree: top-level comments with the `replies` Reddit loaded and `hasMoreReplies` when there are more than were loaded.

## Threads (`threads`)

| Action | Arguments | Pages |
|--------|-----------|-------|
| `search` | `query` (required, up to 500 characters), `start_date`, `end_date` (YYYY-MM-DD) | One page |
| `search_users` | `query` (required, a username or name, up to 100 characters) | One page |
| `profile` | `username` (required; a leading `@` is removed) | No |
| `profile_posts` | `username` (required). Only the latest posts: Threads shows no older ones. | One page |
| `post` | `id` (required): post URL or shortcode. Returns the post with its replies (`comments`) and the author's own continuation posts (`threadItems`). | No |

The `threads` tool has no `cursor` argument.

## TikTok, Facebook, and Instagram

- `tiktok`: `search` (`query`; `count`, `sort`, `cursor`), `post` (`id`), `profile` (`username`), `profile_posts` (`username`; `count`, `cursor`), `comments` (`video_id`; `count`, `cursor`), `hashtag` (`tag`; `count`, `cursor`), `trending` (`region`, `count`; one page).
- `facebook`: `search` (`query`) and `hashtag` (`tag`) return Meta Ad Library ads, not organic posts; `post` (`id`), `profile` (`profile_id`), `profile_posts` (`profile_id`), `comments` (`post_id`). List actions take `count` and `cursor`.
- `instagram`: `search` (`query`; `count`; profiles, one page), `media` (`id`: shortcode, numeric ID, or URL), `profile` (`username`), `profile_posts` (`username`), `comments` (`shortcode` from the post URL), `hashtag` (`tag`). List actions take `count` and `cursor`.

`count` (1 to 100) is a maximum on these three; one page may hold fewer.

## Example

The user asks for recent YouTube videos about bittensor and what the top one says:

1. `youtube` with `{"action": "search", "query": "bittensor", "type": "videos", "upload_date": "this_month"}`.
2. `youtube` with `{"action": "transcript", "video_id": "<id of the first result>", "language": "en"}`.
3. If the user wants more videos, `youtube` with the same `action`, `query`, `type`, and `upload_date`, and `cursor` set to the `next_cursor` from step 1.

## When not to use these tools

Do not page through every result when a summary of the first page answers the question. These tools do not read private or logged-in content, and they do not post, vote, comment, follow, or message anyone.

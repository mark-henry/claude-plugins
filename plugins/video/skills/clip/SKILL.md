---
name: clip
description: "Download or clip videos with yt-dlp and ffmpeg, including past windows of still-live streams (\"40 to 30 min ago\") and WhatsApp-sized exports. Use when the user wants to download, clip, trim or share a video."
---

# yt-dlp recipes

Outputs go in `~/Downloads/clips/` unless the user says otherwise. Single-quote URLs (zsh globs the `?` in `watch?v=`).

## Before anything else
- **Update first** (YouTube breaks old builds): `pip install -U --pre 'yt-dlp[default]'` if pip, `brew upgrade yt-dlp` if Homebrew (`which yt-dlp` tells you).
- **Check whether it's live:** `yt-dlp --print '%(title)s | live_status=%(live_status)s | duration=%(duration)s | release=%(release_timestamp)s' '<url>'`

## Finished video (VOD)
`yt-dlp --download-sections '*1:02:30-1:05:00' -f 'bv*[height<=1080]+ba/b' -o '<name>.%(ext)s' '<url>'`

- Add `--force-keyframes-at-cuts` for frame-accurate cuts (re-encodes, slower).
- Add `--merge-output-format mp4` so the result plays everywhere.
- Verified 2026-10-25: once a finished livestream became a VOD, a 6 s cut 2.6 h in took seconds, using `--force-keyframes-at-cuts --merge-output-format mp4`.

## Stream that is still live: past window
**Doesn't work** (verified 2026-10-24, yt-dlp 2026.10.23): `--live-from-start --download-sections '*-40:00--30:00'` fails with `This format cannot be partially downloaded` (yt-dlp issues #3451, #17518). PR #6498 would add `--download-sections '#-40min - -30min'` but is unmerged; check whether it has landed before using the workaround.

**Works:** `live-clip '<url>' <start_min_ago> <end_min_ago> <out.mp4> [max_height]`
- Without `--live-from-start`, a live YouTube video exposes only HLS formats.
- The HLS playlist covers the last ~60 min (`playlist_duration/3600` in the segment URLs) as 5 s segments numbered `/sq/N/`.
- The script picks the newest sq, counts back N segments for the window, fetches video and audio in parallel with curl, concatenates the `.ts` files, and muxes with `-c copy`.
- Tested: an exact 10:00 clip at 1080p60, 201 MB, ready in about 2 min.

**Older than 1 hour** (the script can't reach):
- [ypb](https://github.com/xymaxim/ypb) (untested) reaches back up to YouTube's ~12 h DVR limit, e.g. `ypb download --interval '2026-10-24T22:35+00/10m' <id>`.
- Or wait a few hours after the stream ends, then use the VOD recipe with offsets from the start of the broadcast.

## Sub-clip from a downloaded file
`ffmpeg -ss 2:45 -to 3:05 -i in.mp4 ...` and re-encode (`-c copy` snaps to keyframes).

## WhatsApp-sized
Limit is 16 MB, and WhatsApp recompresses anyway. This keeps motion smooth (20 s came out to 6.6 MB):

```
ffmpeg -ss <start> -to <end> -i in.mp4 -vf scale=-2:720 -c:v libx264 -profile:v high -pix_fmt yuv420p \
  -crf 23 -maxrate 3500k -bufsize 7000k -preset slow -c:a aac -b:a 128k -movflags +faststart out_whatsapp.mp4
```

For clips longer than ~35 s, lower `-maxrate`: (14 MB × 8 / seconds) − 128k.

Afterward `open` the result so the user can check it.

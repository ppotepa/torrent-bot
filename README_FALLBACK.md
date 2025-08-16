# Enhanced Torrent Download Fallback System

## Overview

The bot now includes an enhanced fallback system to handle cases where magnet links are not found or fail to download. This system attempts multiple alternative methods to ensure successful torrent downloads.

## Fallback Chain

When a magnet link is not available or fails, the bot will attempt the following methods in order:

1. **Primary Method**: Magnet link (if available)
2. **Fallback Method 1**: Download .torrent file via Jackett link (with retries)
3. **Fallback Method 2**: Reconstruct magnet link from InfoHash with common trackers
4. **Fallback Method 3**: Search for alternative sources from other indexers (if enabled)

## New Environment Variables

### `ENABLE_AGGRESSIVE_FALLBACK`
- **Default**: `true`
- **Description**: Enable searching for alternative sources from other indexers when primary methods fail
- **Values**: `true` or `false`

### `MAX_FALLBACK_ATTEMPTS`
- **Default**: `3`
- **Description**: Maximum number of retry attempts for failed .torrent file downloads
- **Values**: Any positive integer (recommended: 1-5)

### `RICH_MODE_LIMIT`
- **Default**: `15`
- **Description**: Maximum number of results to return in rich search mode
- **Values**: Any positive integer (recommended: 10-25)

### `RICH_MODE_TIMEOUT`
- **Default**: `20`
- **Description**: Timeout in seconds for rich mode searches
- **Values**: Any positive integer (recommended: 15-30)

## Enhanced Search Features

### Rich Search Mode
- Use `/t <query> rich` for comprehensive search across ALL available indexers
- Queries 20+ indexers simultaneously for maximum coverage
- Includes real-time progress indicators during search
- Returns up to 15 results (configurable)

### Extended Search
- If initial search yields poor results (< 3 results or all with 0 seeders), the bot automatically expands the search to additional indexers
- Additional indexers include: 1337x, rarbg, thepiratebay, kickasstorrents, torrentgalaxy, glodls, magnetdl, btdiggg

### Busy Indicators
- Real-time progress updates during searches
- Shows current indexer being queried
- Displays number of results found so far
- Automatically removed when search completes

### Visual Indicators
Search results now include visual indicators:
- 🔥 Hot torrent (100+ seeders)
- ⭐ Good torrent (10+ seeders)  
- ✅ Available (1+ seeders)
- ⚠️ No seeders
- 🧲 Magnet link available
- 📁 Torrent file available

## Error Handling

The system provides detailed error messages for different failure scenarios:
- Connection timeouts
- Invalid responses
- qBittorrent authentication issues
- No alternative sources found

## Example Docker Compose Environment

```yaml
environment:
  - ENABLE_AGGRESSIVE_FALLBACK=true
  - MAX_FALLBACK_ATTEMPTS=3
  - RICH_MODE_LIMIT=15
  - RICH_MODE_TIMEOUT=20
  - JACKETT_INDEXERS=yts,nyaa,eztv,limetorrents,linuxtracker,1337x,rarbg
```

## Benefits

1. **Higher Success Rate**: Multiple fallback methods increase the likelihood of successful downloads
2. **Rich Search Mode**: `/t <query> rich` searches ALL available indexers for comprehensive results
3. **Real-time Feedback**: Busy indicators show search progress and results found
4. **Better User Experience**: Clear feedback about which method was used and why others failed
5. **Configurable**: Can be tuned based on your needs and indexer availability
6. **Resilient**: Handles network issues, tracker problems, and missing magnet links gracefully

## Troubleshooting

If downloads are still failing:

1. Check your Jackett indexers are working properly
2. Verify your qBittorrent connection settings
3. Enable aggressive fallback: `ENABLE_AGGRESSIVE_FALLBACK=true`
4. Increase retry attempts: `MAX_FALLBACK_ATTEMPTS=5`
5. Add more indexers to `JACKETT_INDEXERS`

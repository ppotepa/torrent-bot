# ALL Mode Search Feature

## Overview

The **ALL mode** is a new comprehensive search feature that queries **EVERY** indexer available on your Jackett instance, providing the most exhaustive torrent search possible.

## Usage

```bash
/t <search query> all
```

### Examples
```bash
/t alice cooper flac all
/t ubuntu iso all  
/t python programming books all
```

## Search Modes Comparison

| Mode | Command | Indexers Used | Results | Use Case |
|------|---------|---------------|---------|----------|
| **Normal** | `/t query` | Popular indexers (5-10) | Top 5 | Quick searches |
| **Rich** | `/t query rich` | All configured indexers | Top 15 | Comprehensive search |
| **ALL** | `/t query all` | **EVERY** indexer on Jackett | Top 25 | Exhaustive search |

## Features

### 🌐 **Complete Coverage**
- Queries **every single indexer** available on your Jackett instance
- Includes both configured and unconfigured indexers
- No indexer is left out

### ⚡ **Smart Performance**
- Uses up to 12 parallel workers for maximum speed
- Intelligent timeout management (30 seconds)
- Progress indicators show real-time search status

### 📊 **Enhanced Results**
- Returns up to 25 results (configurable via `ALL_MODE_LIMIT`)
- Results sorted by seeders count (highest first)
- Automatic deduplication of identical torrents

### 🔄 **Robust Fallback**
- If Jackett API fails, falls back to comprehensive indexer list
- Includes configured indexers to ensure nothing is missed
- Graceful error handling for unavailable indexers

## Configuration

### Environment Variables

```bash
# Maximum results returned in ALL mode
ALL_MODE_LIMIT=25

# Timeout for ALL mode searches (seconds)
ALL_MODE_TIMEOUT=30
```

### Performance Tuning

The ALL mode automatically adjusts:
- **Workers**: 6-12 parallel connections based on indexer count
- **Timeouts**: Extended timeouts for comprehensive coverage
- **Memory**: Efficient result merging and deduplication

## API Differences

### Normal Jackett API Call
```
GET /api/v2.0/indexers/{specific_indexer}/results
```

### ALL Mode API Call
```
GET /api/v2.0/indexers?configured=false
```
*(Gets ALL indexers, then queries each one)*

## Progress Indicators

ALL mode provides detailed progress feedback:

```
🔍 ALL search in progress...
🌐 Querying EVERY indexer on Jackett
⏳ This will take longer but be comprehensive

🔍 Comprehensive search in progress...
📡 Searching: 1337x
📊 Progress: 15/43 indexers
✅ Found: 127 torrents so far
```

## Use Cases

### **Perfect for ALL Mode:**
- **Rare content**: Hard-to-find movies, music, books
- **Quality hunting**: Looking for the highest quality versions
- **Comprehensive research**: Academic or professional searches
- **Archive searches**: Finding older or obscure content

### **When to Use Other Modes:**
- **Quick searches**: Use normal mode for common content
- **Balanced searches**: Use rich mode for good coverage without waiting
- **Testing**: Use normal mode when testing indexer configurations

## Technical Implementation

### Indexer Discovery
```python
def get_all_jackett_indexers(self):
    # Gets ALL indexers from Jackett (configured + unconfigured)
    params = {"apikey": self.api_key, "configured": "false"}
    # Returns comprehensive list of every available indexer
```

### Search Execution
```python
def search_all(self, query, bot=None, message=None, limit=25):
    # Query every single indexer in parallel
    # Maximum workers for speed while avoiding overload
    # Real-time progress updates via Telegram
```

## Troubleshooting

### Long Search Times
- **Expected**: ALL mode searches every indexer (can be 30-50+ indexers)
- **Progress**: Watch the progress indicator for real-time updates
- **Optimization**: Configure only the indexers you need in Jackett

### Too Many Results
- **Adjust limit**: Set `ALL_MODE_LIMIT` environment variable
- **Quality filter**: Results are automatically sorted by seeders

### Missing Indexers
- **Check Jackett**: Verify indexers are properly configured in Jackett UI
- **API access**: Ensure your API key has full permissions
- **Network**: Check connectivity between bot and Jackett

### Performance Issues
- **Reduce workers**: The system auto-limits to 12 workers maximum
- **Timeout adjustment**: Increase `ALL_MODE_TIMEOUT` if needed
- **Resource monitoring**: Monitor system resources during ALL searches

## Comparison Examples

### Normal Mode Result
```
🔍 Top 5 results (seeders ↓):
1. Alice Cooper - Greatest Hits 🔥🧲📁
   🌱 150 | 💾 245.2 MB • 🏷 yts
```

### Rich Mode Result
```
🔍 Rich search results (15 from all configured indexers):
🌟 Comprehensive search across all available indexers
1. Alice Cooper - Discography FLAC ⭐🧲📁
   🌱 89 | 💾 2.1 GB • 🏷 1337x
```

### ALL Mode Result
```
🌐 ALL search results (25 from EVERY indexer):
🌐 Exhaustive search across ALL indexers on Jackett
1. Alice Cooper - Complete Studio Albums [24bit FLAC] 🔥🧲📁
   🌱 234 | 💾 4.7 GB • 🏷 redacted
```

## Performance Metrics

Typical ALL mode search performance:
- **Indexers queried**: 30-50 indexers
- **Search time**: 15-30 seconds
- **Results found**: 100-500 before deduplication
- **Final results**: Top 25 after sorting and deduplication
- **Success rate**: 70-90% of indexers respond successfully

## Best Practices

1. **Use sparingly**: ALL mode is resource-intensive
2. **Specific queries**: More specific search terms yield better results
3. **Monitor progress**: Watch the progress indicator for status
4. **Quality over quantity**: Focus on high-seeder results
5. **Fallback strategy**: Start with rich mode, escalate to ALL if needed

## Migration Notes

- **Backward compatible**: All existing code continues to work
- **Optional feature**: ALL mode is opt-in via command flag
- **No configuration required**: Works with existing Jackett setup
- **Graceful degradation**: Falls back to rich mode if issues occur

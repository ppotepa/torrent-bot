# Rich Mode Usage Guide

## 🌟 Rich Search Mode

The enhanced torrent bot now supports **Rich Mode** for comprehensive torrent searches!

### Basic Usage

```
/t ubuntu rich
/t "movie name 2024" rich
/t anime episode rich
```

### What Rich Mode Does

1. **Comprehensive Search**: Queries ALL available indexers (20+ sources)
2. **Real-time Progress**: Shows live updates as each indexer is searched
3. **Maximum Coverage**: Returns up to 15 results from across all sources
4. **Better Results**: Often finds torrents that normal search misses

### Visual Progress Indicators

During rich search, you'll see:
```
🔍 Rich search in progress...
📡 Searching: nyaa
📊 Progress: 8/20 indexers
✅ Found: 12 torrents so far
```

### Normal vs Rich Mode

| Feature | Normal Mode | Rich Mode |
|---------|-------------|-----------|
| Indexers | 5-8 popular | ALL available (20+) |
| Results | Up to 5 | Up to 15 |
| Speed | Fast (3-5 sec) | Thorough (10-20 sec) |
| Coverage | Good | Maximum |

### When to Use Rich Mode

- **Hard to find content**: Rare movies, old shows, specific versions
- **Poor initial results**: Normal search returns few or no results  
- **Maximum coverage**: When you want to see all available options
- **Quality comparison**: To compare the same content from multiple sources

### Examples

```bash
# Normal search (fast)
/t "The Matrix 1999"

# Rich search (comprehensive)  
/t "The Matrix 1999" rich

# Works with any query
/t "linux distro iso" rich
/t "classical music FLAC" rich
/t "documentary 4K" rich
```

### Button Layout

Rich mode results show more organized button rows:
```
[1 (🌱45)] [2 (🌱38)] [3 (🌱22)] [4 (🌱15)] [5 (🌱12)]
[6 (🌱8)]  [7 (🌱5)]  [8 (🌱3)]  [9 (🌱1)]  [10 (🌱0)]
[11 (🌱0)] [12 (🌱0)] [13 (🌱0)] [14 (🌱0)] [15 (🌱0)]
```

### Configuration

Customize rich mode behavior via environment variables:
- `RICH_MODE_LIMIT=15` - Number of results to return
- `RICH_MODE_TIMEOUT=20` - Search timeout in seconds

### Tips

1. **Be patient**: Rich searches take longer but find more results
2. **Use quotes**: For multi-word searches: `/t "exact movie title" rich`  
3. **Try both modes**: Start with normal, use rich if needed
4. **Check all results**: Rich mode often finds better quality versions

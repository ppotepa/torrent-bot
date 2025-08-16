# ALL Mode Indexers - Comprehensive Coverage

The ALL flag now searches across **80 indexers** to provide the most comprehensive torrent coverage possible.

## 🎬 Movies & TV Indexers (21)

### Major Public Trackers
- **1337x** - Popular general tracker
- **The Pirate Bay** (thepiratebay, piratebay) - Largest public tracker
- **YTS** - High-quality movie releases
- **EZTV** - TV show specialist
- **Torlock** - Verified torrents
- **TorrentGalaxy** (torrentgalaxy, torrentgalaxyclone) - Movies/TV/games
- **TorrentDownloads** - General purpose
- **TorrentProject** (torrentproject, torrentproject2) - DHT search
- **Torrent9** - French tracker
- **OxTorrent** (oxtorrent, oxtorrent-vip) - French content
- **LimeTorrents** - General tracker
- **TorrentKitty** - DHT search engine
- **TorrentTip** - General content

### Regional/Specialized Movie Sites
- **DivxTotal** - Spanish movies/TV
- **Cinecalidad** - Latin American content
- **DonTorrent** - Spanish tracker
- **Elitetorrent** (elitetorrent-wf) - Spanish content
- **ExtraTorrent** (extratorrents) - General tracker
- **Isohunt2** - Public tracker revival

## 📺 TV/Series Specialists (8)

- **showRSS** - TV show RSS feeds
- **SkidrowRepack** - TV shows + game cracks
- **TorrentDosFilmes** - Portuguese films/series
- **TorrentOyunIndir** - Turkish TV/movies/games
- **TorrentSir** - General TV content
- **TorrentSome** - TV series focus
- **Zetorrents** - TV specialist
- **Internet Archive** (internetarchive) - Classic/public domain

## 🎵 Music & Audio Indexers (12)

### Music Specialists
- **RuTracker** (rutracker) - Largest music tracker
- **RuTor** (rutor) - Russian content
- **NoNaMe Club** (noname-club) - Music releases
- **Torrent[CORE]** (torrentcore) - Scene music releases
- **MixtapeTorrent** (mixtapetorrent) - Hip-hop/rap
- **Nipponsei** - Anime & J-music
- **Tokyo Toshokan** (tokyotoshokan) - J-music specialist

### Audio Software & Tools
- **VST Torrentz** (vsttorrentz) - Audio plugins
- **VSTHouse** (vsthouse) - Audio software
- **VSTorrent** (vstorrent) - Music production tools
- **LinuxTracker** - Music software + live sets
- **TorrentQQ** (torrentqq) - Music heavy content

## 💻 Software, Games & E-Books (20)

### Games & Cracks
- **SkidrowRepack** - PC games + cracks
- **GamesTorrents** (gamestorrents) - Game releases
- **Mac Torrents** (mactorrentsdownload) - macOS software
- **PC-Torrent** (pc-torrent) - Windows software
- **CrackingPatching** - Software cracks
- **Byrutor** - Games/software

### E-Books & Documents
- **EBookBay** (ebookbay) - Digital books
- **EpubLibre** (epublibre) - Free e-books
- **Frozen Layer** (frozenlayer) - Anime subs + tools

### Specialized Software
- **BT.etree** (bt-etree) - Live music + software
- **MegaPeer** (megapeer) - Software/games
- **PluginTorrent** (plugintorrent) - Audio software plugins
- **Torrents.sg** (torrentssg) - Software tracker
- **TorrentDosFilmes** - Also includes software
- **TorrentOyunIndir** - Games/software focus
- **Wolfmax 4k** (wolfmax4k) - Movies + 4K tools

### General Software
- **iDope** (idope, idopeclone) - General DHT search
- **KickassTorrents** (kickasstorrents, kickasstorrents.to, kickasstorrents.ws) - Revived tracker
- **YourBittorrent** (yourbittorrent) - General content

## 🔧 Legacy & Fallback Indexers (11)

### Historical Trackers
- **RarBG** (rarbg, rarbgapi) - Shutdown 2023, API alternatives
- **Nyaa** - Anime specialist (still active)
- **GloDLS** (glodls) - General tracker
- **MagnetDL** (magnetdl) - Magnet search
- **BTDigg** (btdiggg) - DHT search engine
- **Zooqle** - Verified torrents
- **TorrentFunk** (torrentfunk) - General tracker
- **SkyTorrents** (skytorrents) - Clean interface
- **SolidTorrents** (solidtorrents) - General tracker

## 🔒 Private Trackers (8)
*(Only work if you have accounts)*

### General Private
- **IPTorrents** (iptorrents) - General private tracker
- **TorrentLeech** (torrentleech) - Popular private site

### Specialized Private
- **PassThePopcorn** (passthepopcorn) - Movie specialist
- **BroadcastTheNet** (broadcastthenet) - TV specialist
- **Redacted** - Music specialist (What.CD successor)
- **Orpheus** - Music specialist
- **GazelleGames** (gazellegames) - Game specialist  
- **JPopSuki** (jpopsuki) - Asian content

## 🚀 Search Modes Comparison

| Mode | Indexers Used | Speed | Coverage | Best For |
|------|---------------|-------|----------|-----------|
| **Normal** | 10 popular | Fast | Good | Quick searches |
| **Rich** | 15-25 available | Medium | Better | Quality content |
| **ALL** | 80 comprehensive | Slow | Maximum | Rare/obscure content |

## ⚡ Performance & Behavior

### ALL Mode Characteristics
- **Timeout**: 30 seconds (vs 12s normal)
- **Results**: Up to 25 results (vs 5 normal)  
- **Workers**: 12 concurrent (vs 4 normal)
- **Coverage**: Every configured indexer + fallbacks

### Smart Fallback System
1. **Primary**: Query Jackett for all available indexers
2. **Fallback**: Use comprehensive 80-indexer list if API fails
3. **Integration**: Merge with user's configured indexers

### Progress Tracking
- Real-time updates showing current indexer being queried
- Progress counter (e.g., "25/80 indexers complete")
- Running total of results found

## 🎯 Usage Examples

```bash
# Search ALL indexers for maximum coverage
/search ubuntu ALL

# Compare with rich mode
/search ubuntu RICH

# Normal mode for quick results  
/search ubuntu
```

## 🔍 Indexer Health Monitoring

The bot includes diagnostic capabilities to monitor indexer health:

```bash
/diag torrent performance
```

This will test individual indexers and show:
- Which indexers are responding
- Result counts per indexer
- Common error patterns
- Regional availability issues

## 📊 Expected Results

With ALL mode, you can expect:
- **Movies**: 15-50+ results from multiple sources
- **TV Shows**: 10-30+ results with various qualities
- **Software**: 5-20+ results including alternatives
- **Music**: 5-25+ results from specialized trackers
- **Rare Content**: Maximum chance of finding obscure items

The comprehensive indexer list ensures you get the best possible coverage across all content types and regions! 🌍

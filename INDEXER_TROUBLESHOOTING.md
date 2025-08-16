# Indexer Troubleshooting Guide

## Common Issues and Solutions

### 🚨 **Fixed Issues**

#### **1. AttributeError: 'NoneType' object has no attribute 'reply_to_message'**
**Status**: ✅ **FIXED**

**Problem**: Bot crash when trying to send fallback messages during torrent download.

**Solution**: Removed incorrect bot reference handling in `_attempt_download()` function. The function now returns status messages that are handled properly by the calling code.

**What was changed**:
- Fixed `telegram_handlers.py` to handle bot references correctly
- Added proper intermediate messaging for fallback downloads
- Improved error handling in download process

---

### 🔍 **Indexer-Specific Issues**

#### **1. RarBG Not Returning Results**

**Common Issues**:
- **RarBG shutdown**: The original RarBG site shut down in 2023
- **Wrong indexer name**: May be configured as `rarbgapi` instead of `rarbg`
- **Not configured**: Indexer not set up in Jackett

**Solutions**:
```bash
# Test specific RarBG variants
/tdiag

# Check Jackett configuration
# Look for these indexer names:
- rarbg
- rarbgapi  
- rarbgclone
```

**Manual check**:
1. Open Jackett web interface
2. Look for RarBG-related indexers
3. Ensure they're configured and enabled
4. Test them manually in Jackett

#### **2. TorrentGalaxy Not Returning Results**

**Common Issues**:
- **Name variations**: Could be `torrentgalaxy` or `torrentgalaxyclone`
- **Configuration**: Indexer needs proper setup
- **Regional blocking**: May be blocked in your region

**Solutions**:
```bash
# Test both variants
/tdiag  # Will test both torrentgalaxy and torrentgalaxyclone
```

**Jackett setup**:
1. Add TorrentGalaxy indexer in Jackett
2. Configure any required credentials
3. Test the indexer manually
4. Check for clone/mirror versions

#### **3. iDope Not Returning Results**

**Common Issues**:
- **Name variations**: Could be `idope` or `idopeclone`
- **Site status**: iDope frequently changes domains
- **Regional restrictions**: Often blocked by ISPs

**Solutions**:
```bash
# Test both variants
/tdiag  # Will test both idope and idopeclone
```

**Troubleshooting steps**:
1. Check if iDope is accessible from your network
2. Look for iDope clone/mirror indexers in Jackett
3. Consider using alternative indexers with similar content

---

### 🛠️ **Enhanced Diagnostics**

#### **New Diagnostic Features**

The `/tdiag` command now includes:

**Enhanced Logging**:
- Detailed per-indexer response information
- HTTP status codes and response sizes
- Specific error messages from Jackett
- Configuration status for each indexer

**Specific Tests**:
- Automatically tests problematic indexers (RarBG, TorrentGalaxy, iDope)
- Checks both main and clone/variant versions
- Provides targeted solutions for common issues

**Example Output**:
```
🔍 Querying rarbg: http://jackett:9117/api/v2.0/indexers/rarbg/results
📡 rarbg response: 404 (234 bytes)
❌ rarbg: HTTP 404: Indexer not found

🔍 Querying rarbgapi: http://jackett:9117/api/v2.0/indexers/rarbgapi/results  
📡 rarbgapi response: 200 (15432 bytes)
✅ rarbgapi: 25 results, top: 156 seeders

💡 RarBG Issues:
• RarBG shutdown in 2023, try 'rarbgapi' or other alternatives
• Check if you have RarBG API indexer configured
```

---

### 🔧 **Configuration Improvements**

#### **Updated Indexer Lists**

Added more indexer variants to `ALL_INDEXERS`:
```python
ALL_INDEXERS = [
    # ... existing indexers ...
    "rarbgapi", "torrentgalaxyclone", "idope", "idopeclone",
    "iptorrents", "torrentleech", "passthepopcorn", "broadcastthenet",
    "redacted", "orpheus", "gazellegames", "jpopsuki"
]
```

#### **Indexer Aliases**

Added common name mappings:
```python
INDEXER_ALIASES = {
    "rarbgapi": "rarbg",
    "torrentgalaxyclone": "torrentgalaxy", 
    "idopeclone": "idope",
    "thepiratebay": "tpb",
    "kickasstorrents": "kat"
}
```

---

### 📋 **Troubleshooting Steps**

#### **Step 1: Run Diagnostics**
```bash
/tdiag
```
This will:
- Test all configured indexers
- Specifically test problematic ones
- Show detailed error messages
- Provide targeted solutions

#### **Step 2: Check Jackett Configuration**
1. Open Jackett web interface (usually `http://localhost:9117`)
2. Verify indexers are:
   - Added to Jackett
   - Properly configured
   - Enabled and working
   - Not showing errors

#### **Step 3: Test Manually**
1. In Jackett, use the "Test" button for each indexer
2. Try manual searches in Jackett web interface
3. Check Jackett logs for errors

#### **Step 4: Update Bot Configuration**
```bash
# Update indexer list if needed
export JACKETT_INDEXERS="yts,nyaa,1337x,rarbgapi,torrentgalaxyclone,idopeclone"

# Or use ALL mode to test everything
/t your_query all
```

---

### 🚀 **Quick Fixes**

#### **For Missing Results from Specific Indexers**:

1. **Use ALL mode** to test comprehensive coverage:
   ```bash
   /t alice cooper all
   ```

2. **Check indexer names** in Jackett and update configuration:
   ```bash
   # Common name variations:
   rarbg → rarbgapi
   torrentgalaxy → torrentgalaxyclone  
   idope → idopeclone
   ```

3. **Verify indexer status** in Jackett web interface

4. **Update indexer lists** with working alternatives

#### **For Download Errors**:

1. **Check qBittorrent connectivity**
2. **Verify API credentials**
3. **Test with simpler torrents first**
4. **Check logs for specific error details**

---

### 📊 **Expected Behavior After Fixes**

#### **Download Process**:
1. ✅ No more AttributeError crashes
2. ✅ Proper fallback messaging
3. ✅ Clear success/failure notifications
4. ✅ Detailed error reporting

#### **Indexer Testing**:
1. ✅ Comprehensive diagnostics for problematic indexers
2. ✅ Specific troubleshooting advice
3. ✅ Enhanced logging for debugging
4. ✅ Support for indexer variants and clones

#### **Search Results**:
1. ✅ Better coverage with updated indexer lists
2. ✅ ALL mode tests every available indexer
3. ✅ Improved error handling and reporting
4. ✅ Clearer feedback about indexer status

The bot should now be much more robust and provide better diagnostics for troubleshooting indexer issues!

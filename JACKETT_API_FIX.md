# Jackett API Connection Fix

## 🎯 Problem Solved
**Error**: `Cannot get available indexers: Expecting value: line 1 column 1 (char 0)`

This error occurs when Jackett returns an empty response or non-JSON data.

## 🔧 Fixes Implemented

### 1. **Enhanced Error Handling**
- Added detailed logging for Jackett API responses
- Shows HTTP status codes, headers, and response content
- Identifies specific JSON parsing issues
- Provides actionable error messages

### 2. **Robust Fallback System**
Rich mode now has multiple fallback layers:
1. **Primary**: Try to get indexers from Jackett API
2. **Fallback 1**: Use configured `JACKETT_INDEXERS` 
3. **Fallback 2**: Use extended indexer list (`ALL_INDEXERS`)
4. **Fail**: Only if no indexers available at all

### 3. **Improved Diagnostics**
The `/tdiag` command now provides comprehensive troubleshooting:
- Tests Jackett connection and API key
- Shows which indexers are configured
- Tests each indexer individually
- Identifies connection vs configuration issues
- Provides specific solutions

## 🚀 How to Troubleshoot

### Step 1: Run Enhanced Diagnostics
```
/tdiag
```
This will now show:
- Jackett URL and API key status
- Detailed connection errors
- Individual indexer test results
- Configuration recommendations

### Step 2: Check Your Environment Variables
Ensure these are set correctly:
```yaml
environment:
  - JACKETT_URL=http://jackett:9117  # or your Jackett URL
  - JACKETT_API_KEY=your_api_key_here
```

### Step 3: Test Rich Mode (Should Work Now)
```
/t alice cooper flac 2025 rich
```
Even if Jackett API fails, it will fallback to configured indexers.

## 🔍 Common Issues & Solutions

### Issue 1: Empty Response from Jackett
**Symptoms**: "Expecting value: line 1 column 1"
**Solutions**: 
- Check JACKETT_URL is correct
- Verify Jackett is running
- Check API key is valid

### Issue 2: Wrong API Endpoint
**Symptoms**: 404 errors or HTML responses
**Solutions**:
- Ensure Jackett URL doesn't have extra paths
- Use `/api/v2.0/indexers` endpoint
- Check Jackett version compatibility

### Issue 3: Authentication Issues
**Symptoms**: 401/403 errors
**Solutions**:
- Regenerate API key in Jackett
- Check API key environment variable
- Verify Jackett allows API access

## ✅ Expected Behavior

After this fix:
1. **Rich mode works**: Even if API discovery fails
2. **Clear diagnostics**: Know exactly what's wrong
3. **Graceful fallback**: Uses configured indexers as backup
4. **Better errors**: Actionable troubleshooting information

The bot should now handle Jackett API issues gracefully and still provide torrent search functionality! 🎯

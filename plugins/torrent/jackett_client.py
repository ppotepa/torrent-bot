"""
Jackett API client for torrent searches.
Handles indexer communication and result processing.
"""

try:
    import requests
    from concurrent.futures import ThreadPoolExecutor, as_completed
except ImportError as e:
    print(f"Warning: Missing dependency: {e}")
    # Placeholder for development
    class requests:
        class exceptions:
            class Timeout(Exception): pass
            class ConnectionError(Exception): pass 
            class HTTPError(Exception): pass
        @staticmethod
        def get(*args, **kwargs): pass
    
    class ThreadPoolExecutor:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def submit(self, *args): pass
    
    def as_completed(futures): return []

from .config import config
from .utils import sort_results_by_seeders, deduplicate_results


class JackettClient:
    """Client for interacting with Jackett API."""
    
    def __init__(self):
        self.url = config.JACKETT_URL
        self.api_key = config.JACKETT_API_KEY
        self.connect_timeout = config.CONNECT_TIMEOUT
        self.read_timeout = config.READ_TIMEOUT
    
    def _fetch_indexer(self, indexer: str, query: str):
        """
        Query a single Jackett indexer with short timeouts.
        Returns (results_list, error_string_or_None, indexer_name)
        """
        try:
            if not self.api_key:
                return [], "JACKETT_API_KEY is empty", indexer

            url = f"{self.url}/api/v2.0/indexers/{indexer}/results"
            params = {"apikey": self.api_key, "Query": query}
            
            print(f"🔍 Querying {indexer}: {url}")
            
            r = requests.get(url, params=params, timeout=(self.connect_timeout, self.read_timeout))
            
            print(f"📡 {indexer} response: {r.status_code} ({len(r.content)} bytes)")
            
            r.raise_for_status()
            data = r.json() if r.text else {}
            results = data.get("Results", []) or []
            
            print(f"✅ {indexer} returned {len(results)} results")

            # Annotate tracker name so we can display it
            for item in results:
                item["Tracker"] = item.get("Tracker") or indexer

            # Surface first indexer error if Jackett provided any
            err = None
            indexer_info = data.get("Indexers", []) or []
            for idx in indexer_info:
                if idx.get("Error"):
                    err = idx.get("Error")
                    print(f"⚠️ {indexer} reported error: {err}")
                    break
                    
            # Check for specific indexer issues
            if not results and not err:
                # Check if indexer is configured
                if indexer_info:
                    for idx_info in indexer_info:
                        if not idx_info.get("configured", True):
                            err = f"Indexer {indexer} is not configured in Jackett"
                            print(f"⚠️ {indexer} not configured")
                        elif idx_info.get("status", 0) != 200:
                            err = f"Indexer {indexer} status: {idx_info.get('status', 'unknown')}"
                            print(f"⚠️ {indexer} bad status: {idx_info.get('status')}")
                            
            return results, err, indexer

        except requests.exceptions.Timeout:
            print(f"⏰ {indexer} timeout after {self.read_timeout}s")
            return [], f"timeout after {self.read_timeout}s", indexer
        except requests.exceptions.HTTPError as e:
            print(f"❌ {indexer} HTTP error: {e.response.status_code}")
            return [], f"HTTP {e.response.status_code}: {e.response.text[:100]}", indexer
        except Exception as e:
            print(f"❌ {indexer} error: {str(e)}")
            return [], str(e), indexer
    
    def search_fast(self, query: str, limit: int = None):
        """
        Hit a short list of popular indexers in parallel with short timeouts.
        Stop as soon as we collect 'limit' results.
        """
        if limit is None:
            limit = config.RESULT_LIMIT
            
        indexers = [i for i in config.JACKETT_INDEXERS.split(",") if i]
        if not indexers:
            raise Exception("No indexers configured (JACKETT_INDEXERS is empty)")

        merged = []
        errs = []
        workers = min(config.MAX_WORKERS, max(1, len(indexers)))

        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(self._fetch_indexer, idx, query): idx for idx in indexers}
            for f in as_completed(futures):
                results, err, idx = f.result()
                if err:
                    errs.append((idx, err))
                if results:
                    merged.extend(results)
                    merged = sort_results_by_seeders(merged)
                    merged = deduplicate_results(merged)
                    if len(merged) >= limit:
                        for fut in futures.keys():
                            if not fut.done():
                                fut.cancel()
                        break

        return merged[:limit], errs
    
    def search_extended(self, query: str, limit: int = None):
        """
        Extended search that tries more indexers if initial search yields poor results.
        This is used as a fallback when we need more/better torrent options.
        """
        if limit is None:
            limit = config.RESULT_LIMIT * 2
            
        # First try the fast search
        results, errs = self.search_fast(query, limit)
        
        # If we got good results (multiple results with decent seeders), return them
        from .utils import get_seeders_count
        good_results = [r for r in results if get_seeders_count(r) > 0]
        if len(good_results) >= 3:
            return results, errs
        
        # If results are poor, try additional indexers (if available)
        additional_indexers = [
            "1337x", "rarbg", "thepiratebay", "kickasstorrents", 
            "torrentgalaxy", "glodls", "magnetdl", "btdiggg"
        ]
        
        # Filter out indexers we already tried
        current_indexers = set(config.JACKETT_INDEXERS.split(","))
        new_indexers = [idx for idx in additional_indexers if idx not in current_indexers]
        
        if new_indexers:
            print(f"⚠️ Expanding search to additional indexers: {', '.join(new_indexers[:4])}")
            
            workers = min(config.MAX_WORKERS, max(1, len(new_indexers[:4])))  # Limit to 4 additional
            with ThreadPoolExecutor(max_workers=workers) as ex:
                futures = {ex.submit(self._fetch_indexer, idx, query): idx for idx in new_indexers[:4]}
                for f in as_completed(futures):
                    new_results, err, idx = f.result()
                    if err:
                        errs.append((idx, err))
                    if new_results:
                        results.extend(new_results)
            
            # Re-sort and dedupe the combined results
            results = sort_results_by_seeders(results)
            results = deduplicate_results(results)
        
        return results[:limit], errs
    
    def search_rich(self, query: str, bot=None, message=None, limit: int = None):
        """
        Rich search that queries ALL available indexers for comprehensive results.
        Includes progress updates via busy indicator.
        """
        if limit is None:
            limit = config.RICH_MODE_LIMIT
            
        # Try to get all actually available indexers from Jackett
        available_indexers, error = self.check_available_indexers()
        
        if error:
            print(f"⚠️ Cannot get indexers from Jackett API: {error}")
            print(f"⚠️ Falling back to configured indexers: {config.JACKETT_INDEXERS}")
            
            # Fallback to configured indexers + extended list
            indexers = [i.strip() for i in config.JACKETT_INDEXERS.split(",") if i.strip()]
            
            # Add more from the ALL_INDEXERS list as fallback for rich mode
            popular_additions = [
                "1337x", "thepiratebay", "torrentgalaxy", "torlock", 
                "torrentdownloads", "idope", "kickasstorrents", "rarbg",
                "linuxtracker", "glodls", "magnetdl"
            ]
            for idx in popular_additions:
                if idx not in indexers:
                    indexers.append(idx)
            
            # If we still have no indexers, fail
            if not indexers:
                raise Exception(f"Cannot get available indexers from Jackett and no fallback configured: {error}")
                
            print(f"📋 Rich mode fallback using {len(indexers)} indexers")
                
        else:
            if not available_indexers:
                print("⚠️ No configured indexers found in Jackett, using fallback list")
                indexers = [i.strip() for i in config.JACKETT_INDEXERS.split(",") if i.strip()]
            else:
                # Use all available indexers for rich mode
                indexers = [idx["id"] for idx in available_indexers]
        
        print(f"🔍 Rich mode using {len(indexers)} indexers: {', '.join(indexers[:10])}{'...' if len(indexers) > 10 else ''}")

        merged = []
        errs = []
        completed_indexers = 0
        
        # Use more workers for rich mode but cap it to avoid overwhelming
        workers = min(8, max(4, len(indexers) // 3))

        with ThreadPoolExecutor(max_workers=workers) as ex:
            # Submit all indexer searches
            future_to_indexer = {ex.submit(self._fetch_indexer, idx, query): idx for idx in indexers}
            
            for future in as_completed(future_to_indexer):
                indexer = future_to_indexer[future]
                completed_indexers += 1
                
                try:
                    results, err, idx = future.result()
                    if err:
                        errs.append((idx, err))
                    if results:
                        merged.extend(results)
                    
                    # Update progress if we have bot and message
                    if bot and message:
                        from .busy_indicator import BusyIndicator
                        BusyIndicator.update(
                            bot, message, 
                            current_indexer=indexer,
                            total_indexers=len(indexers),
                            found_results=len(merged)
                        )
                    
                except Exception as e:
                    errs.append((indexer, str(e)))
            
            # Sort, dedupe and limit results
            merged = sort_results_by_seeders(merged)
            merged = deduplicate_results(merged)

        return merged[:limit], errs
    
    def search_all(self, query: str, bot=None, message=None, limit: int = None):
        """
        ALL search mode that queries EVERY single indexer available on Jackett.
        This is the most comprehensive search, querying all configured indexers
        regardless of their performance or status. Includes progress updates.
        """
        if limit is None:
            limit = config.ALL_MODE_LIMIT
            
        # Get all indexers from Jackett (both configured and unconfigured)
        all_indexers, error = self.get_all_jackett_indexers()
        
        if error:
            print(f"⚠️ Cannot get all indexers from Jackett API: {error}")
            print(f"⚠️ Falling back to comprehensive indexer list")
            
            # Use comprehensive fallback list - our full ALL_INDEXERS list
            all_indexers = config.ALL_INDEXERS.copy()
            
            # Add configured indexers to ensure we don't miss any
            configured = [i.strip() for i in config.JACKETT_INDEXERS.split(",") if i.strip()]
            for idx in configured:
                if idx not in all_indexers:
                    all_indexers.append(idx)
                    
            print(f"📋 Using {len(all_indexers)} indexers from comprehensive fallback list")
        else:
            # Extract indexer IDs from Jackett response
            all_indexers = [idx["id"] for idx in all_indexers]
        
        print(f"🔍 ALL mode using {len(all_indexers)} indexers: {', '.join(all_indexers[:15])}{'...' if len(all_indexers) > 15 else ''}")

        merged = []
        errs = []
        completed_indexers = 0
        
        # Use maximum workers for all mode but cap to avoid overwhelming system
        workers = min(12, max(6, len(all_indexers) // 2))

        with ThreadPoolExecutor(max_workers=workers) as ex:
            # Submit all indexer searches
            future_to_indexer = {ex.submit(self._fetch_indexer, idx, query): idx for idx in all_indexers}
            
            for future in as_completed(future_to_indexer):
                indexer = future_to_indexer[future]
                completed_indexers += 1
                
                try:
                    results, err, idx = future.result()
                    if err:
                        errs.append((idx, err))
                    if results:
                        merged.extend(results)
                    
                    # Update progress if we have bot and message
                    if bot and message:
                        from .busy_indicator import BusyIndicator
                        BusyIndicator.update(
                            bot, message, 
                            current_indexer=indexer,
                            total_indexers=len(all_indexers),
                            found_results=len(merged)
                        )
                    
                except Exception as e:
                    errs.append((indexer, str(e)))
            
            # Sort, dedupe and limit results
            merged = sort_results_by_seeders(merged)
            merged = deduplicate_results(merged)

        return merged[:limit], errs
    
    def search_music(self, query: str, bot=None, message=None, limit: int = None):
        """
        Music search mode that queries popular music indexers for optimal music results.
        Focuses on indexers known for good music content and quality.
        """
        if limit is None:
            limit = config.MUSIC_MODE_LIMIT
            
        # Use music-specific indexers
        music_indexers = config.MUSIC_INDEXERS.copy()
        
        print(f"🎵 Music mode using {len(music_indexers)} music indexers: {', '.join(music_indexers[:10])}{'...' if len(music_indexers) > 10 else ''}")

        merged = []
        errs = []
        completed_indexers = 0
        
        # Use moderate workers for music mode
        workers = min(6, max(3, len(music_indexers) // 4))

        with ThreadPoolExecutor(max_workers=workers) as ex:
            # Submit music indexer searches
            future_to_indexer = {ex.submit(self._fetch_indexer, idx, query): idx for idx in music_indexers}
            
            for future in as_completed(future_to_indexer):
                indexer = future_to_indexer[future]
                completed_indexers += 1
                
                try:
                    results, err, idx = future.result()
                    if err:
                        errs.append((idx, err))
                    if results:
                        merged.extend(results)
                    
                    # Update progress if we have bot and message
                    if bot and message:
                        from .busy_indicator import BusyIndicator
                        BusyIndicator.update(
                            bot, message, 
                            current_indexer=indexer,
                            total_indexers=len(music_indexers),
                            found_results=len(merged)
                        )
                    
                except Exception as e:
                    errs.append((indexer, str(e)))
            
            # Sort, dedupe and limit results
            merged = sort_results_by_seeders(merged)
            merged = deduplicate_results(merged)

        return merged[:limit], errs
    
    def get_all_jackett_indexers(self):
        """
        Get ALL indexers from Jackett (both configured and unconfigured).
        This is more comprehensive than check_available_indexers which only gets configured ones.
        """
        try:
            if not self.api_key:
                return [], "JACKETT_API_KEY is empty"
            
            # Get ALL indexers from Jackett (not just configured ones)
            url = f"{self.url}/api/v2.0/indexers"
            params = {"apikey": self.api_key, "configured": "false"}  # Get all, not just configured
            
            print(f"🔍 Getting ALL indexers from Jackett at: {url}")
            
            r = requests.get(url, params=params, timeout=(self.connect_timeout, self.read_timeout))
            print(f"📡 Response status: {r.status_code}")
            
            r.raise_for_status()
            
            if not r.text.strip():
                return [], "Empty response from Jackett API"
            
            try:
                indexers = r.json()
            except ValueError as e:
                return [], f"Invalid JSON response: {str(e)}"
            
            if not isinstance(indexers, list):
                return [], f"Expected list of indexers, got: {type(indexers)}"
            
            all_indexers = []
            for indexer in indexers:
                if isinstance(indexer, dict):
                    name = indexer.get("id", "unknown")
                    title = indexer.get("title", name)
                    configured = indexer.get("configured", False)
                    all_indexers.append({
                        "id": name, 
                        "title": title, 
                        "configured": configured
                    })
            
            print(f"✅ Found {len(all_indexers)} total indexers in Jackett")
            configured_count = len([i for i in all_indexers if i["configured"]])
            print(f"📊 {configured_count} configured, {len(all_indexers) - configured_count} unconfigured")
            
            return all_indexers, None
            
        except requests.exceptions.Timeout:
            return [], f"Timeout connecting to Jackett at {self.url}"
        except requests.exceptions.ConnectionError:
            return [], f"Cannot connect to Jackett at {self.url}"
        except requests.exceptions.HTTPError as e:
            return [], f"HTTP error from Jackett: {e.response.status_code}"
        except Exception as e:
            return [], f"Unexpected error: {str(e)}"

    def check_available_indexers(self):
        """
        Check which indexers are actually available and working in Jackett.
        This helps diagnose why bot results differ from desktop.
        """
        try:
            if not self.api_key:
                return [], "JACKETT_API_KEY is empty"
            
            # Get list of configured indexers from Jackett
            url = f"{self.url}/api/v2.0/indexers"
            params = {"apikey": self.api_key}
            
            print(f"🔍 Checking Jackett indexers at: {url}")
            
            r = requests.get(url, params=params, timeout=(self.connect_timeout, self.read_timeout))
            print(f"📡 Response status: {r.status_code}")
            print(f"📄 Response headers: {dict(r.headers)}")
            print(f"📝 Response content length: {len(r.content)}")
            print(f"🔤 First 200 chars of response: {r.text[:200]}")
            
            r.raise_for_status()
            
            if not r.text.strip():
                return [], "Empty response from Jackett API"
            
            try:
                indexers = r.json()
            except ValueError as e:
                return [], f"Invalid JSON response: {str(e)}. Response: {r.text[:500]}"
            
            if not isinstance(indexers, list):
                return [], f"Expected list of indexers, got: {type(indexers)}. Response: {str(indexers)[:200]}"
            
            available = []
            for indexer in indexers:
                if isinstance(indexer, dict) and indexer.get("configured", False):
                    name = indexer.get("id", "unknown")
                    title = indexer.get("title", name)
                    available.append({"id": name, "title": title})
            
            print(f"✅ Found {len(available)} configured indexers: {[i['id'] for i in available[:10]]}")
            
            return available, None
            
        except requests.exceptions.Timeout:
            return [], f"Timeout connecting to Jackett at {self.url}"
        except requests.exceptions.ConnectionError:
            return [], f"Cannot connect to Jackett at {self.url}"
        except requests.exceptions.HTTPError as e:
            return [], f"HTTP error from Jackett: {e.response.status_code} - {e.response.text[:200]}"
        except Exception as e:
            return [], f"Unexpected error: {str(e)}"
    
    def test_indexer_performance(self, query="ubuntu", limit=3):
        """
        Test performance of individual indexers for diagnostic purposes.
        Shows which indexers return the most results and highest seeders.
        """
        try:
            # First, test the Jackett connection and API
            report = [f"🔍 Jackett Connection Test:"]
            report.append(f"URL: {self.url}")
            report.append(f"API Key: {'***' + self.api_key[-4:] if len(self.api_key) > 4 else 'NOT SET'}")
            report.append("=" * 50)
            
            available_indexers, error = self.check_available_indexers()
            
            if error:
                report.append(f"❌ Jackett API Error: {error}")
                report.append("\n💡 Possible solutions:")
                report.append("• Check JACKETT_URL environment variable")
                report.append("• Check JACKETT_API_KEY environment variable")  
                report.append("• Verify Jackett is running and accessible")
                report.append("• Check Jackett logs for errors")
                
                # Try testing with configured indexers instead
                report.append(f"\n🔄 Testing with configured indexers: {config.JACKETT_INDEXERS}")
                indexers_to_test = [{"id": i.strip(), "title": i.strip()} for i in config.JACKETT_INDEXERS.split(",") if i.strip()]
            else:
                if not available_indexers:
                    report.append("⚠️ No configured indexers found in Jackett")
                    report.append("💡 Configure some indexers in your Jackett web interface")
                    return "\n".join(report)
                else:
                    report.append(f"✅ Found {len(available_indexers)} configured indexers")
                    indexers_to_test = available_indexers
            
            # Add specific problematic indexers to test
            problematic_indexers = ["rarbg", "rarbgapi", "torrentgalaxy", "torrentgalaxyclone", "idope", "idopeclone"]
            for prob_idx in problematic_indexers:
                if not any(idx["id"] == prob_idx for idx in indexers_to_test):
                    indexers_to_test.append({"id": prob_idx, "title": prob_idx})
            
            if not indexers_to_test:
                report.append("❌ No indexers available to test")
                return "\n".join(report)
            
            report.append(f"\n🧪 Testing {len(indexers_to_test)} indexers with query: '{query}'")
            report.append("🔍 Specifically testing: RarBG, TorrentGalaxy, iDope variants")
            report.append("=" * 50)
            
            results_by_indexer = {}
            errors = []
            
            # Test each indexer individually
            for indexer_info in indexers_to_test[:20]:  # Test first 20 to avoid spam
                indexer_id = indexer_info["id"]
                try:
                    results, err, _ = self._fetch_indexer(indexer_id, query)
                    if err:
                        errors.append(f"{indexer_id}: {err}")
                        report.append(f"❌ {indexer_id}: {err}")
                    else:
                        # Get top result seeder count
                        from .utils import get_seeders_count
                        top_seeders = max([get_seeders_count(r) for r in results], default=0)
                        results_by_indexer[indexer_id] = {
                            "count": len(results),
                            "top_seeders": top_seeders,
                            "title": indexer_info["title"]
                        }
                        report.append(f"✅ {indexer_id}: {len(results)} results, top: {top_seeders} seeders")
                except Exception as e:
                    errors.append(f"{indexer_id}: {str(e)}")
                    report.append(f"❌ {indexer_id}: {str(e)}")
            
            if results_by_indexer:
                # Sort by effectiveness (results count + top seeders)
                sorted_indexers = sorted(
                    results_by_indexer.items(), 
                    key=lambda x: (x[1]["count"], x[1]["top_seeders"]), 
                    reverse=True
                )
                
                report.append(f"\n📊 Best Performing Indexers:")
                report.append("=" * 30)
                
                for indexer_id, data in sorted_indexers[:5]:
                    title = data["title"]
                    count = data["count"]
                    seeders = data["top_seeders"]
                    report.append(f"🏆 {indexer_id}: {count} results, {seeders} max seeders")
            
            if errors:
                report.append(f"\n❌ Failed Indexers ({len(errors)}):")
                report.append("=" * 25)
                for error in errors[:8]:
                    report.append(f"   {error}")
                    
                # Specific help for common issues
                if any("rarbg" in error.lower() for error in errors):
                    report.append(f"\n� RarBG Issues:")
                    report.append("• RarBG shutdown in 2023, try 'rarbgapi' or other alternatives")
                    report.append("• Check if you have RarBG API indexer configured")
                    
                if any("torrentgalaxy" in error.lower() for error in errors):
                    report.append(f"\n💡 TorrentGalaxy Issues:")
                    report.append("• Try both 'torrentgalaxy' and 'torrentgalaxyclone'")
                    report.append("• Check indexer configuration in Jackett")
                    
                if any("idope" in error.lower() for error in errors):
                    report.append(f"\n💡 iDope Issues:")
                    report.append("• Try both 'idope' and 'idopeclone'")
                    report.append("• iDope may be blocked or down in your region")
            
            report.append(f"\n�💻 Current Configuration:")
            report.append(f"• Normal mode uses: {config.JACKETT_INDEXERS}")
            report.append(f"• Rich mode uses: ALL available indexers")
            report.append(f"• All mode uses: EVERY indexer on Jackett")
            report.append(f"• Timeouts: {self.connect_timeout}s connect, {self.read_timeout}s read")
            
            return "\n".join(report)
            
        except Exception as e:
            return f"❌ Diagnostics failed: {str(e)}\n\nPlease check your Jackett configuration and network connectivity."

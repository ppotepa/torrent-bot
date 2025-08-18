"""
Result formatter that integrates media parsing with torrent results.
"""

from typing import List, Dict, Any
from .media_parser import media_parser, MediaInfo, get_media_type_emoji
from .utils import get_seeders_count


def escape_markdown(text: str) -> str:
    """Escape special Markdown characters in text to prevent parsing errors."""
    if not text:
        return text
    
    # Characters that need escaping in Telegram Markdown
    chars_to_escape = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in chars_to_escape:
        text = text.replace(char, f'\\{char}')
    
    return text


def format_torrent_results(results: List[Dict], max_results: int = 20) -> List[Dict]:
    """Format torrent results with media information and enhanced button text."""
    formatted_results = []
    
    for i, result in enumerate(results[:max_results]):
        # Extract basic info
        title = result.get('Title', '')
        size = result.get('Size', 0)
        seeders = get_seeders_count(result)
        leechers = int(result.get('Peers', 0))
        
        # Parse media information
        media_info = media_parser.parse(title, size, seeders, leechers)
        
        # Create enhanced result
        enhanced_result = result.copy()
        enhanced_result.update({
            'media_type': media_info.media_type.value,
            'media_info': media_info,
            'button_text': media_parser.format_button_text(media_info),
            'quality_score': media_info.quality_score,
            'clean_title': media_info.title,
            'display_index': i  # Keep original order for callback
        })
        
        formatted_results.append(enhanced_result)
    
    # Sort by quality score (descending) but keep display_index for callbacks
    formatted_results.sort(key=lambda x: x['quality_score'], reverse=True)
    
    return formatted_results


def create_summary_message(results: List[Dict], query: str, search_mode_label: str) -> str:
    """Create a summary message showing media type distribution and numbered list."""
    if not results:
        return f"❌ No results found for: `{query}`"
    
    # Count by media type
    type_counts = {}
    for result in results:
        media_type = result.get('media_type', 'other')
        type_counts[media_type] = type_counts.get(media_type, 0) + 1
    
    # Create summary header
    total = len(results)
    summary_parts = []
    
    for media_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        emoji = get_media_type_emoji(media_type)
        percentage = (count / total) * 100
        summary_parts.append(f"{emoji} {media_type.title()}: {count} ({percentage:.0f}%)")
    
    summary = "\n".join(summary_parts)
    
    # Create numbered list of results
    result_lines = []
    result_lines.append(f"{search_mode_label}")
    result_lines.append(f"\n📊 **Found {total} results:**")
    result_lines.append(summary)
    result_lines.append(f"\n📋 **Select by typing a number (1-{total}):**")
    result_lines.append("")
    
    # Add numbered list
    for i, result in enumerate(results[:50], 1):  # Limit to 50 for readability
        media_info = result.get('media_info')
        if media_info:
            # Get quality emoji
            quality_emoji = "🔥" if media_info.quality_score >= 80 else "⭐" if media_info.quality_score >= 60 else "✅" if media_info.quality_score >= 40 else "⚠️"
            
            # Never truncate the title - show it in full and bold
            title = media_info.raw_title  # Use raw title to show full original
            
            # Format based on media type with specific data requirements
            details = media_info.details
            size = details.get('size', 'Unknown')
            seeds = details.get('seeds', '0')
            peers = details.get('peers', '0')
            
            if media_info.media_type.value == 'audio':
                # Audio: SIZE | BITRATE | NUMBER OF TRACKS | PEERS | SEEDS
                audio_parts = [size]
                
                if 'bitrate' in details:
                    audio_parts.append(f"Bitrate: {details['bitrate']}")
                elif '320' in title:
                    audio_parts.append("Bitrate: 320k")
                elif '256' in title:
                    audio_parts.append("Bitrate: 256k")
                elif '192' in title:
                    audio_parts.append("Bitrate: 192k")
                elif 'flac' in title.lower():
                    audio_parts.append("Bitrate: Lossless")
                
                # Try to extract track count from title
                import re
                track_patterns = [
                    r'(\d+)\s*tracks?',
                    r'(\d+)\s*songs?',
                    r'(\d+)\s*cd',
                    r'cd\s*(\d+)',
                    r'disc\s*(\d+)'
                ]
                
                for pattern in track_patterns:
                    track_match = re.search(pattern, title, re.I)
                    if track_match:
                        audio_parts.append(f"Tracks: {track_match.group(1)}")
                        break
                
                audio_parts.extend([f"Peers: {peers}", f"Seeds: {seeds}"])
                detail_str = " | ".join(audio_parts)
                
            elif title.lower().endswith('.iso') or 'iso' in title.lower() or media_info.media_type.value == 'other':
                # ISO or Other: SIZE | PEERS | SEEDS  
                detail_str = f"{size} | Peers: {peers} | Seeds: {seeds}"
                
            elif media_info.media_type.value in ['movie', 'tv']:
                # Video: YEAR | RESOLUTION | SOURCE | CODEC | SIZE | SEEDS
                video_parts = []
                if 'year' in details:
                    video_parts.append(details['year'])
                if 'resolution' in details:
                    video_parts.append(details['resolution'])
                if 'source' in details:
                    video_parts.append(details['source'])
                if 'codec' in details:
                    video_parts.append(details['codec'])
                
                video_parts.extend([size, f"Seeds: {seeds}"])
                detail_str = " | ".join(video_parts)
                
            elif media_info.media_type.value == 'software':
                # Software: VERSION | OS | ARCH | SIZE | SEEDS
                software_parts = []
                if 'version' in details:
                    software_parts.append(f"v{details['version']}")
                if 'os' in details:
                    software_parts.append(details['os'])
                if 'arch' in details:
                    software_parts.append(details['arch'])
                
                software_parts.extend([size, f"Seeds: {seeds}"])
                detail_str = " | ".join(software_parts)
                
            elif media_info.media_type.value == 'game':
                # Games: GROUP/PLATFORM | SIZE | SEEDS
                game_parts = []
                if 'group' in details:
                    game_parts.append(details['group'])
                elif 'platform' in details:
                    game_parts.append(details['platform'])
                
                game_parts.extend([size, f"Seeds: {seeds}"])
                detail_str = " | ".join(game_parts)
                
            else:
                # Default: SIZE | PEERS | SEEDS
                detail_str = f"{size} | Peers: {peers} | Seeds: {seeds}"
            
            # Create the formatted entry
            escaped_title = escape_markdown(title)
            result_lines.append(f"`{i:2}.` {quality_emoji} **{escaped_title}**")
            result_lines.append(f"     {detail_str}")
            result_lines.append("")  # Add spacing between entries
            
        else:
            # Fallback for results without media_info
            title = result.get('Title', 'Unknown')  # Don't truncate fallback titles either
            size = result.get('Size', 0)
            from .utils import human_size, get_seeders_count
            size_str = human_size(size) if size else 'Unknown'
            seeds = get_seeders_count(result)
            peers = result.get('Peers', 0)
            
            escaped_title = escape_markdown(title)
            result_lines.append(f"`{i:2}.` **{escaped_title}**")
            result_lines.append(f"     {size_str} | Peers: {peers} | Seeds: {seeds}")
            result_lines.append("")  # Add spacing between entries
    
    if total > 50:
        result_lines.append(f"\n_... and {total - 50} more results (showing top 50)_")
    
    result_lines.append(f"\n💡 **Type the number (1-{min(total, 50)}) to download**")
    
    # Join the message and check length (Telegram has a 4096 character limit)
    message = "\n".join(result_lines)
    
    # If message is too long, truncate results
    if len(message) > 4000:  # Leave some buffer
        # Reduce number of results until message fits
        max_results_to_show = min(total, 20)  # Start with fewer results
        
        # Rebuild with fewer results
        result_lines = [search_mode_label]
        result_lines.extend(category_lines)
        result_lines.append(f"\n📋 **Select by typing a number (1-{max_results_to_show}):**")
        
        for i, result in enumerate(results[:max_results_to_show], 1):
            title = result.get('Title', 'Unknown')
            escaped_title = escape_markdown(title)
            size = result.get('Size', 0)
            from .utils import human_size, get_seeders_count
            size_str = human_size(size) if size else 'Unknown'
            seeds = get_seeders_count(result)
            
            result_lines.append(f"`{i:2}.` **{escaped_title}**")
            result_lines.append(f"     {size_str} | Seeds: {seeds}")
            result_lines.append("")
        
        if total > max_results_to_show:
            result_lines.append(f"\n_... and {total - max_results_to_show} more results (showing top {max_results_to_show} due to length limit)_")
        
        result_lines.append(f"\n💡 **Type the number (1-{max_results_to_show}) to download**")
        message = "\n".join(result_lines)
    
    return message


def get_enhanced_usage_message() -> str:
    """Get enhanced usage message with media information details."""
    return (
        "⚠️ Usage: `/t <search query>:[flags]`\n\n"
        "📋 **Available Flags:**\n"
        "• `all` - Exhaustive search across ALL indexers\n"
        "• `rich` - Comprehensive search across configured indexers\n"
        "• `music` - Focused search across music indexers\n"
        "• `notify` - Get notified when this specific torrent completes\n"
        "• `silent` - Disable notifications\n\n"
        "📝 **Examples:**\n"
        "• `/t ubuntu:[all]` - Search with all indexers\n"
        "• `/t ubuntu:[rich,notify]` - Rich search with notification\n"
        "• `/t ubuntu:[music]` - Music-focused search\n"
        "• `/t ubuntu` - Normal search (no flags)\n\n"
        "🎯 **Enhanced Media Detection:**\n"
        "🎵 **Audio**: Artist | Album | Format | Bitrate | Size | Seeds\n"
        "🎬 **Movies**: Year | Resolution | Source | Codec | Size | Seeds\n"
        "📺 **TV Shows**: Season | Episode | Resolution | Source | Size | Seeds\n"
        "💻 **Software**: Version | OS | Architecture | Size | Seeds\n"
        "🎮 **Games**: Group | Platform | Architecture | Size | Seeds\n"
        "📚 **eBooks**: Format | Year | Size | Seeds\n\n"
        "⭐ **Quality Indicators:**\n"
        "🔥 Excellent • ⭐ Good • ✅ OK • ⚠️ Low • ❌ Poor\n\n"
        "🔢 **Selection Method:**\n"
        "After search results appear, simply **type the number** (1-50) of the torrent you want to download.\n"
        "No need to click buttons - just type the number and press enter!\n\n"
        "⚡ **Note:** Search mode flags (all, rich, music) are mutually exclusive"
    )

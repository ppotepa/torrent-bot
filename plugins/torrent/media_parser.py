"""
Media information parser for torrent results.
Recognizes different media types and extracts relevant metadata.
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class MediaType(Enum):
    """Supported media types."""
    AUDIO = "audio"
    MOVIE = "movie" 
    TV_SHOW = "tv"
    SOFTWARE = "software"
    GAME = "game"
    EBOOK = "ebook"
    ADULT = "adult"
    OTHER = "other"


@dataclass
class MediaInfo:
    """Parsed media information."""
    media_type: MediaType
    title: str
    details: Dict[str, str]  # Type-specific details
    quality_score: int  # 0-100 rating based on quality indicators
    raw_title: str


class MediaParser:
    """Parser for extracting media information from torrent titles."""
    
    def __init__(self):
        # Audio patterns
        self.audio_patterns = {
            'format': re.compile(r'\b(mp3|flac|aac|m4a|ogg|wav|ape|wma)\b', re.I),
            'bitrate': re.compile(r'\b(\d+)\s*kbps\b|\b(\d+)k\b', re.I),
            'quality': re.compile(r'\b(320|256|192|128|v0|v2|lossless|hi-res|24bit|96khz|192khz)\b', re.I),
            'album': re.compile(r'^(.+?)\s*-\s*(.+?)\s*\(?\d{4}\)?', re.I),
            'year': re.compile(r'\b(19\d{2}|20\d{2})\b'),
            'genre': re.compile(r'\[(rock|pop|jazz|classical|electronic|hip.hop|rap|metal|country|blues)\]', re.I)
        }
        
        # Video patterns  
        self.video_patterns = {
            'resolution': re.compile(r'\b(4k|2160p|1080p|720p|480p|360p|1440p)\b', re.I),
            'quality': re.compile(r'\b(bluray|bdrip|webrip|dvdrip|hdtv|web-dl|cam|ts|screener|hdrip)\b', re.I),
            'codec': re.compile(r'\b(x264|x265|h264|h265|hevc|xvid|divx|av1)\b', re.I),
            'audio': re.compile(r'\b(dts|ac3|aac|mp3|truehd|atmos|5\.1|7\.1|stereo)\b', re.I),
            'year': re.compile(r'\b(19\d{2}|20\d{2})\b'),
            'season': re.compile(r'\bs(\d+)e(\d+)\b|\bseason\s*(\d+)\b', re.I),
            'episode': re.compile(r'\bs\d+e(\d+)\b|\bepisode\s*(\d+)\b', re.I)
        }
        
        # Software patterns
        self.software_patterns = {
            'version': re.compile(r'\bv?(\d+\.[\d\.]+)\b', re.I),
            'arch': re.compile(r'\b(x64|x86|32bit|64bit|arm64)\b', re.I),
            'os': re.compile(r'\b(windows|macos|linux|android|ios)\b', re.I),
            'type': re.compile(r'\b(crack|keygen|patch|portable|installer)\b', re.I)
        }
        
        # File type indicators  
        self.type_indicators = {
            MediaType.AUDIO: [
                'flac', 'mp3', 'album', 'discography', 'soundtrack', 'ost',
                'single', 'ep', 'compilation', 'va', 'various artists', 'artist -'
            ],
            MediaType.MOVIE: [
                'bluray', 'bdrip', 'dvdrip', 'webrip', 'movie', 'film',
                '1080p', '720p', '4k', 'cinema'
            ],
            MediaType.TV_SHOW: [
                'season', 'episode', 's01', 's02', 'complete series',
                'tv show', 'series', 'hdtv'
            ],
            MediaType.SOFTWARE: [
                'software', 'program', 'app', 'crack', 'keygen',
                'patch', 'installer', 'portable', 'suite', 'adobe', 'microsoft',
                'office', 'photoshop', 'windows', 'macos', 'pre-activated'
            ],
            MediaType.GAME: [
                'game', 'pc game', 'repack', 'gog', 'steam',
                'codex', 'fitgirl', 'dodi'
            ],
            MediaType.EBOOK: [
                'ebook', 'epub', 'pdf', 'mobi', 'kindle',
                'audiobook', 'book', 'novel'
            ],
            MediaType.ADULT: [
                'xxx', 'adult', 'porn', '18+', 'nsfw'
            ]
        }
    
    def parse(self, title: str, size: int = 0, seeders: int = 0, leechers: int = 0) -> MediaInfo:
        """Parse torrent title and extract media information."""
        media_type = self._detect_media_type(title)
        details = self._extract_details(title, media_type, size, seeders, leechers)
        quality_score = self._calculate_quality_score(title, media_type, seeders, leechers)
        clean_title = self._clean_title(title, media_type)
        
        return MediaInfo(
            media_type=media_type,
            title=clean_title,
            details=details,
            quality_score=quality_score,
            raw_title=title
        )
    
    def _detect_media_type(self, title: str) -> MediaType:
        """Detect the media type from the title."""
        title_lower = title.lower()
        
        # Count indicators for each type
        type_scores = {}
        for media_type, indicators in self.type_indicators.items():
            score = sum(1 for indicator in indicators if indicator in title_lower)
            if score > 0:
                type_scores[media_type] = score
        
        # Return the type with highest score, or OTHER if none found
        if type_scores:
            return max(type_scores, key=type_scores.get)
        
        return MediaType.OTHER
    
    def _extract_details(self, title: str, media_type: MediaType, size: int, seeders: int, leechers: int) -> Dict[str, str]:
        """Extract type-specific details from the title."""
        from .utils import human_size
        
        details = {
            'size': human_size(size) if size else 'Unknown',
            'seeds': str(seeders),
            'peers': str(leechers)
        }
        
        if media_type == MediaType.AUDIO:
            details.update(self._extract_audio_details(title))
        elif media_type == MediaType.MOVIE:
            details.update(self._extract_movie_details(title))
        elif media_type == MediaType.TV_SHOW:
            details.update(self._extract_tv_details(title))
        elif media_type == MediaType.SOFTWARE:
            details.update(self._extract_software_details(title))
        elif media_type == MediaType.GAME:
            details.update(self._extract_game_details(title))
        elif media_type == MediaType.EBOOK:
            details.update(self._extract_ebook_details(title))
        
        return details
    
    def _extract_audio_details(self, title: str) -> Dict[str, str]:
        """Extract audio-specific details."""
        details = {}
        
        # Format
        format_match = self.audio_patterns['format'].search(title)
        if format_match:
            details['format'] = format_match.group(1).upper()
        
        # Bitrate
        bitrate_match = self.audio_patterns['bitrate'].search(title)
        if bitrate_match:
            bitrate = bitrate_match.group(1) or bitrate_match.group(2)
            details['bitrate'] = f"{bitrate}k"
        
        # Quality indicators
        quality_match = self.audio_patterns['quality'].search(title)
        if quality_match:
            details['quality'] = quality_match.group(1)
        
        # Year
        year_match = self.audio_patterns['year'].search(title)
        if year_match:
            details['year'] = year_match.group(1)
        
        # Try to extract artist/album
        album_match = self.audio_patterns['album'].search(title)
        if album_match:
            details['artist'] = album_match.group(1).strip()
            details['album'] = album_match.group(2).strip()
        
        return details
    
    def _extract_movie_details(self, title: str) -> Dict[str, str]:
        """Extract movie-specific details."""
        details = {}
        
        # Resolution
        res_match = self.video_patterns['resolution'].search(title)
        if res_match:
            details['resolution'] = res_match.group(1)
        
        # Quality/Source
        quality_match = self.video_patterns['quality'].search(title)
        if quality_match:
            details['source'] = quality_match.group(1)
        
        # Codec
        codec_match = self.video_patterns['codec'].search(title)
        if codec_match:
            details['codec'] = codec_match.group(1).upper()
        
        # Audio
        audio_match = self.video_patterns['audio'].search(title)
        if audio_match:
            details['audio'] = audio_match.group(1)
        
        # Year
        year_match = self.video_patterns['year'].search(title)
        if year_match:
            details['year'] = year_match.group(1)
        
        return details
    
    def _extract_tv_details(self, title: str) -> Dict[str, str]:
        """Extract TV show specific details."""
        details = {}
        
        # Season/Episode
        season_match = self.video_patterns['season'].search(title)
        if season_match:
            if season_match.group(1) and season_match.group(2):
                details['season'] = f"S{season_match.group(1).zfill(2)}"
                details['episode'] = f"E{season_match.group(2).zfill(2)}"
            elif season_match.group(3):
                details['season'] = f"S{season_match.group(3).zfill(2)}"
        
        # Add movie details (resolution, codec, etc.)
        details.update(self._extract_movie_details(title))
        
        return details
    
    def _extract_software_details(self, title: str) -> Dict[str, str]:
        """Extract software-specific details."""
        details = {}
        
        # Version
        version_match = self.software_patterns['version'].search(title)
        if version_match:
            details['version'] = version_match.group(1)
        
        # Architecture
        arch_match = self.software_patterns['arch'].search(title)
        if arch_match:
            details['arch'] = arch_match.group(1)
        
        # OS
        os_match = self.software_patterns['os'].search(title)
        if os_match:
            details['os'] = os_match.group(1).title()
        
        # Type
        type_match = self.software_patterns['type'].search(title)
        if type_match:
            details['type'] = type_match.group(1).title()
        
        return details
    
    def _extract_game_details(self, title: str) -> Dict[str, str]:
        """Extract game-specific details."""
        details = {}
        
        # Repack group
        if 'fitgirl' in title.lower():
            details['group'] = 'FitGirl'
        elif 'dodi' in title.lower():
            details['group'] = 'DODI'
        elif 'codex' in title.lower():
            details['group'] = 'CODEX'
        elif 'gog' in title.lower():
            details['platform'] = 'GOG'
        elif 'steam' in title.lower():
            details['platform'] = 'Steam'
        
        # Add software details for architecture, etc.
        details.update(self._extract_software_details(title))
        
        return details
    
    def _extract_ebook_details(self, title: str) -> Dict[str, str]:
        """Extract ebook-specific details."""
        details = {}
        
        # Format
        formats = ['epub', 'pdf', 'mobi', 'azw3', 'txt']
        for fmt in formats:
            if fmt in title.lower():
                details['format'] = fmt.upper()
                break
        
        # Year
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', title)
        if year_match:
            details['year'] = year_match.group(1)
        
        return details
    
    def _calculate_quality_score(self, title: str, media_type: MediaType, seeders: int, leechers: int) -> int:
        """Calculate a quality score from 0-100."""
        score = 50  # Base score
        
        # Seeder bonus (max 25 points)
        if seeders > 0:
            score += min(25, seeders * 2)
        
        # Quality indicators
        if media_type == MediaType.AUDIO:
            if 'flac' in title.lower() or 'lossless' in title.lower():
                score += 15
            elif '320' in title or 'v0' in title.lower():
                score += 10
            elif '256' in title:
                score += 5
        
        elif media_type in [MediaType.MOVIE, MediaType.TV_SHOW]:
            if '4k' in title.lower() or '2160p' in title:
                score += 15
            elif '1080p' in title:
                score += 10
            elif '720p' in title:
                score += 5
            
            if 'bluray' in title.lower():
                score += 10
            elif 'webrip' in title.lower() or 'web-dl' in title.lower():
                score += 5
        
        # Penalty for low quality indicators
        if any(word in title.lower() for word in ['cam', 'ts', 'screener', '128k']):
            score -= 20
        
        return max(0, min(100, score))
    
    def _clean_title(self, title: str, media_type: MediaType) -> str:
        """Clean up the title for display."""
        # Remove common clutter
        cleaned = re.sub(r'\[.*?\]', '', title)  # Remove bracketed text
        cleaned = re.sub(r'\(.*?\)', '', cleaned)  # Remove parenthetical text  
        cleaned = re.sub(r'-\s*[A-Z0-9]+$', '', cleaned)  # Remove release group at end
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Normalize whitespace
        
        # Remove common words to save space
        replacements = [
            (r'\b(1080p|720p|4k|2160p|BluRay|BDRip|WEBRip|HDTV|x264|x265|H264|H265|HEVC)\b', ''),
            (r'\b(FLAC|MP3|320|V0|24bit|96khz|192khz)\b', ''),
            (r'\b(Complete|Season|Series|Collection|Repack|Multilingual)\b', ''),
            (r'\s+', ' ')  # Normalize whitespace again
        ]
        
        for pattern, replacement in replacements:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.I)
        
        cleaned = cleaned.strip()
        
        # More aggressive truncation for button display
        if len(cleaned) > 40:
            cleaned = cleaned[:37] + "..."
        
        return cleaned
    
    def format_button_text(self, media_info: MediaInfo) -> str:
        """Format the button text in two lines with type-specific information."""
        details = media_info.details
        
        # First line: Quality emoji + shortened title
        quality_emoji = self._get_quality_emoji(media_info.quality_score)
        
        # Limit first line to 30 characters for better display
        title = media_info.title
        if len(title) > 30:
            title = title[:27] + "..."
        
        line1 = f"{quality_emoji} {title}"
        
        # Second line: Type-specific details (max 35 chars)
        if media_info.media_type == MediaType.AUDIO:
            line2_parts = []
            
            # For audio: Artist | Album | Format | Seeds
            if 'artist' in details and 'album' in details:
                artist = details['artist'][:12] if len(details['artist']) <= 12 else details['artist'][:9] + "..."
                album = details['album'][:12] if len(details['album']) <= 12 else details['album'][:9] + "..."
                line2_parts.append(f"{artist} | {album}")
            elif 'artist' in details:
                artist = details['artist'][:15] if len(details['artist']) <= 15 else details['artist'][:12] + "..."
                line2_parts.append(artist)
            
            # Add format info
            if 'format' in details:
                line2_parts.append(details['format'])
            if 'bitrate' in details:
                line2_parts.append(details['bitrate'])
            
            # Add seeds
            line2_parts.append(f"S:{details['seeds']}")
            
        elif media_info.media_type in [MediaType.MOVIE, MediaType.TV_SHOW]:
            line2_parts = []
            
            # For video: Year | Resolution | Source | Size | Seeds
            if 'year' in details:
                line2_parts.append(details['year'])
            if 'resolution' in details:
                line2_parts.append(details['resolution'])
            if 'source' in details:
                line2_parts.append(details['source'][:6])  # Truncate source
            
            line2_parts.append(details['size'])
            line2_parts.append(f"S:{details['seeds']}")
            
        elif media_info.media_type == MediaType.SOFTWARE:
            line2_parts = []
            
            # For software: Version | OS | Arch | Size | Seeds
            if 'version' in details:
                version = details['version'][:8] if len(details['version']) <= 8 else details['version'][:5] + "..."
                line2_parts.append(f"v{version}")
            if 'os' in details:
                line2_parts.append(details['os'][:6])
            if 'arch' in details:
                line2_parts.append(details['arch'])
            
            line2_parts.append(details['size'])
            line2_parts.append(f"S:{details['seeds']}")
            
        elif media_info.media_type == MediaType.GAME:
            line2_parts = []
            
            # For games: Group | Platform | Size | Seeds
            if 'group' in details:
                line2_parts.append(details['group'])
            elif 'platform' in details:
                line2_parts.append(details['platform'])
            
            line2_parts.append(details['size'])
            line2_parts.append(f"S:{details['seeds']}")
            
        else:
            # Default format: Size | Seeds
            line2_parts = [details['size'], f"S:{details['seeds']}"]
        
        # Join second line parts and ensure it's not too long
        line2 = " | ".join(line2_parts)
        if len(line2) > 35:  # Strict limit for second line
            line2 = line2[:32] + "..."
        
        # Final button text
        button_text = f"{line1}\n{line2}"
        
        # Ensure total length doesn't exceed Telegram's limits (~64 chars)
        if len(button_text) > 64:
            # Further truncate if needed
            if len(line1) > 32:
                line1 = line1[:29] + "..."
            if len(line2) > 30:
                line2 = line2[:27] + "..."
            button_text = f"{line1}\n{line2}"
        
        return button_text
    
    def _get_quality_emoji(self, score: int) -> str:
        """Get emoji based on quality score."""
        if score >= 80:
            return "🔥"  # Excellent
        elif score >= 65:
            return "⭐"  # Good
        elif score >= 50:
            return "✅"  # OK
        elif score >= 35:
            return "⚠️"  # Low
        else:
            return "❌"  # Poor


def get_media_type_emoji(media_type: str) -> str:
    """Get emoji for media type."""
    emojis = {
        'audio': '🎵',
        'movie': '🎬', 
        'tv': '📺',
        'software': '💻',
        'game': '🎮',
        'ebook': '📚',
        'adult': '🔞',
        'other': '📄'
    }
    return emojis.get(media_type, '📄')


# Global parser instance
media_parser = MediaParser()

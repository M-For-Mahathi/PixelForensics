"""
EXIF Metadata Analyzer
Checks for camera metadata - real photos have it, AI images don't
"""
from PIL import Image
from PIL.ExifTags import TAGS
import os
from datetime import datetime
from typing import Dict, Any, Tuple

class MetadataAnalyzer:
    """Analyzes image EXIF metadata to detect AI-generated images"""
    
    def __init__(self):
        # Suspicious software names (if found in metadata, likely edited/AI)
        self.suspicious_software = [
            'photoshop', 'midjourney', 'stable diffusion', 'dall-e', 
            'dalle', 'ai', 'generated', 'synthetic', 'gpt'
        ]
        
        # Camera manufacturers (if present, likely real)
        self.camera_brands = [
            'canon', 'nikon', 'sony', 'apple', 'samsung', 'google',
            'fujifilm', 'olympus', 'panasonic', 'leica', 'pentax'
        ]
    
    def analyze(self, image_path: str) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Analyze image metadata
        
        Returns:
            (is_fake, confidence, metadata_info)
        """
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            # Extract metadata
            metadata_info = self._extract_metadata(exif_data)
            
            # Analyze for AI indicators
            is_fake, confidence = self._analyze_for_ai(metadata_info)
            
            return is_fake, confidence, metadata_info
            
        except Exception as e:
            # If we can't read metadata, it's slightly suspicious but not conclusive
            return False, 50.0, {'error': str(e), 'has_exif': False}
    
    def _extract_metadata(self, exif_data) -> Dict[str, Any]:
        """Extract relevant EXIF fields"""
        info = {
            'has_exif': False,
            'camera_make': None,
            'camera_model': None,
            'software': None,
            'datetime': None,
            'gps_info': None,
            'focal_length': None,
            'iso': None,
            'aperture': None,
            'exposure_time': None,
            'flash': None,
            'orientation': None,
            'total_tags': 0
        }
        
        if not exif_data:
            return info
        
        info['has_exif'] = True
        info['total_tags'] = len(exif_data)
        
        # Parse EXIF tags
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            
            if tag_name == 'Make':
                info['camera_make'] = str(value).strip()
            elif tag_name == 'Model':
                info['camera_model'] = str(value).strip()
            elif tag_name == 'Software':
                info['software'] = str(value).strip()
            elif tag_name == 'DateTime':
                info['datetime'] = str(value).strip()
            elif tag_name == 'GPSInfo':
                info['gps_info'] = 'Present'
            elif tag_name == 'FocalLength':
                info['focal_length'] = value
            elif tag_name == 'ISOSpeedRatings':
                info['iso'] = value
            elif tag_name == 'FNumber':
                info['aperture'] = value
            elif tag_name == 'ExposureTime':
                info['exposure_time'] = value
            elif tag_name == 'Flash':
                info['flash'] = value
            elif tag_name == 'Orientation':
                info['orientation'] = value
        
        return info
    
    def _analyze_for_ai(self, metadata: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Analyze metadata to determine if image is likely AI-generated
        
        Scoring logic:
        - No EXIF at all = very suspicious (AI images rarely have metadata)
        - No camera info = suspicious
        - Suspicious software = very suspicious
        - Has camera brand + model + settings = likely real
        - Has GPS data = likely real
        """
        
        ai_score = 0
        max_score = 100
        
        # Check 1: No EXIF metadata at all (MAJOR RED FLAG for AI)
        if not metadata.get('has_exif', False):
            ai_score += 40
            confidence = 75.0
            return True, confidence  # Very likely AI
        
        # Check 2: Very few EXIF tags (AI generators sometimes add fake minimal EXIF)
        total_tags = metadata.get('total_tags', 0)
        if total_tags < 5:
            ai_score += 30
        elif total_tags < 10:
            ai_score += 15
        
        # Check 3: No camera make/model (MAJOR RED FLAG)
        has_camera_make = metadata.get('camera_make') is not None
        has_camera_model = metadata.get('camera_model') is not None
        
        if not has_camera_make and not has_camera_model:
            ai_score += 35
        elif not has_camera_make or not has_camera_model:
            ai_score += 20
        
        # Check 4: Suspicious software in metadata
        software = metadata.get('software', '').lower()
        if software:
            for sus_term in self.suspicious_software:
                if sus_term in software:
                    ai_score += 40  # VERY suspicious
                    break
        
        # Check 5: Presence of real camera brand (REDUCES suspicion)
        if has_camera_make:
            camera_make_lower = metadata['camera_make'].lower()
            for brand in self.camera_brands:
                if brand in camera_make_lower:
                    ai_score -= 30  # Strong evidence it's real
                    break
        
        # Check 6: No camera settings (ISO, aperture, exposure)
        has_settings = any([
            metadata.get('iso'),
            metadata.get('aperture'),
            metadata.get('exposure_time'),
            metadata.get('focal_length')
        ])
        
        if not has_settings:
            ai_score += 20
        else:
            ai_score -= 15  # Real cameras have these
        
        # Check 7: GPS data present (real photos often have this)
        if metadata.get('gps_info'):
            ai_score -= 20  # Strong evidence it's real
        
        # Check 8: No datetime
        if not metadata.get('datetime'):
            ai_score += 10
        
        # Ensure score is within bounds
        ai_score = max(0, min(max_score, ai_score))
        
        # Determine if fake based on score
        is_fake = ai_score > 50
        
        # Calculate confidence
        if is_fake:
            # Higher score = more confident it's fake
            confidence = 50 + (ai_score / max_score) * 45
        else:
            # Lower score = more confident it's real
            confidence = 50 + ((max_score - ai_score) / max_score) * 45
        
        confidence = float(min(max(confidence, 55.0), 95.0))
        
        return is_fake, confidence
    
    def get_summary(self, metadata: Dict[str, Any]) -> str:
        """Get human-readable summary of metadata"""
        if not metadata.get('has_exif', False):
            return "⚠️ No EXIF metadata found (typical of AI-generated images)"
        
        summary_parts = []
        
        if metadata.get('camera_make') and metadata.get('camera_model'):
            summary_parts.append(f"📷 Camera: {metadata['camera_make']} {metadata['camera_model']}")
        elif metadata.get('camera_make'):
            summary_parts.append(f"📷 Camera: {metadata['camera_make']}")
        else:
            summary_parts.append("⚠️ No camera information")
        
        if metadata.get('software'):
            summary_parts.append(f"💻 Software: {metadata['software']}")
        
        if metadata.get('datetime'):
            summary_parts.append(f"📅 Date: {metadata['datetime']}")
        
        settings = []
        if metadata.get('iso'):
            settings.append(f"ISO {metadata['iso']}")
        if metadata.get('aperture'):
            settings.append(f"f/{metadata['aperture']}")
        if metadata.get('focal_length'):
            settings.append(f"{metadata['focal_length']}mm")
        
        if settings:
            summary_parts.append(f"⚙️ Settings: {', '.join(settings)}")
        
        if metadata.get('gps_info'):
            summary_parts.append("📍 GPS data present")
        
        total_tags = metadata.get('total_tags', 0)
        summary_parts.append(f"📊 Total EXIF tags: {total_tags}")
        
        return " | ".join(summary_parts) if summary_parts else "No metadata available"


def test_analyzer():
    """Test the metadata analyzer"""
    analyzer = MetadataAnalyzer()
    
    # Test with a real image (you need to provide path)
    test_image = "test_image.jpg"
    
    if os.path.exists(test_image):
        is_fake, confidence, metadata = analyzer.analyze(test_image)
        print(f"\nAnalysis Result:")
        print(f"Is Fake: {is_fake}")
        print(f"Confidence: {confidence:.1f}%")
        print(f"\nMetadata Info:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        print(f"\nSummary: {analyzer.get_summary(metadata)}")
    else:
        print(f"Test image not found: {test_image}")


if __name__ == "__main__":
    test_analyzer()
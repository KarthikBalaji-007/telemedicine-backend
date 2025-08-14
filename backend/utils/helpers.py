"""
Helper utilities for AI Telemedicine Platform
Common utility functions used across the application
"""

from flask import jsonify
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets
import logging
from typing import Dict, Any, Optional, List

def generate_response(success: bool, message: str, data: Any = None, 
                     status_code: int = 200, errors: List[str] = None) -> tuple:
    """
    Generate standardized API response
    
    Args:
        success: Whether the operation was successful
        message: Human-readable message
        data: Response data (optional)
        status_code: HTTP status code
        errors: List of error messages (optional)
    
    Returns:
        Tuple of (response, status_code)
    """
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
    }
    
    if data is not None:
        response['data'] = data
    
    if errors:
        response['errors'] = errors
    
    # Add request ID for tracking
    response['request_id'] = str(uuid.uuid4())
    
    return jsonify(response), status_code

def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique identifier with optional prefix"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id

def hash_string(text: str, salt: str = None) -> str:
    """Hash a string using SHA-256 with optional salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    combined = f"{text}{salt}"
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_hash(text: str, hashed_value: str) -> bool:
    """Verify a string against its hash"""
    try:
        salt, hash_part = hashed_value.split(':', 1)
        combined = f"{text}{salt}"
        computed_hash = hashlib.sha256(combined.encode()).hexdigest()
        return computed_hash == hash_part
    except ValueError:
        return False

def format_datetime(dt: datetime, format_type: str = "iso") -> str:
    """Format datetime object to string"""
    if format_type == "iso":
        return dt.isoformat()
    elif format_type == "readable":
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "date_only":
        return dt.strftime("%Y-%m-%d")
    elif format_type == "time_only":
        return dt.strftime("%H:%M:%S")
    else:
        return dt.isoformat()

def parse_datetime(date_string: str) -> Optional[datetime]:
    """Parse datetime string to datetime object"""
    try:
        # Handle ISO format with Z suffix
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
        return datetime.fromisoformat(date_string)
    except ValueError:
        try:
            # Try common formats
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
                return datetime.strptime(date_string, fmt)
        except ValueError:
            return None

def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date"""
    today = datetime.now()
    age = today.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age

def is_business_hours(dt: datetime = None, timezone_offset: int = 0) -> bool:
    """Check if given datetime is within business hours (9 AM - 5 PM, Mon-Fri)"""
    if dt is None:
        dt = datetime.now()
    
    # Adjust for timezone
    adjusted_dt = dt + timedelta(hours=timezone_offset)
    
    # Check if it's a weekday (Monday = 0, Sunday = 6)
    if adjusted_dt.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if it's within business hours (9 AM - 5 PM)
    hour = adjusted_dt.hour
    return 9 <= hour < 17

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters"""
    import re
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 255 - len(ext) - 1 if ext else 255
        filename = f"{name[:max_name_length]}.{ext}" if ext else name[:255]
    
    return filename

def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """Mask sensitive data like email, phone numbers"""
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""
    
    if '@' in data:  # Email
        username, domain = data.split('@', 1)
        masked_username = username[:2] + mask_char * (len(username) - 2)
        return f"{masked_username}@{domain}"
    else:  # Phone or other
        return data[:visible_chars] + mask_char * (len(data) - visible_chars)

def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file type based on extension"""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in [ext.lower() for ext in allowed_extensions]

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text (simple implementation)"""
    import re
    
    # Convert to lowercase and extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
        'those', 'was', 'were', 'been', 'have', 'has', 'had', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'are', 'is', 'am'
    }
    
    # Filter out stop words and count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]

def log_api_call(endpoint: str, method: str, user_id: str = None, 
                response_time: float = None, status_code: int = None):
    """Log API call for monitoring and analytics"""
    log_data = {
        'endpoint': endpoint,
        'method': method,
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'response_time': response_time,
        'status_code': status_code
    }
    
    # TODO: COORDINATE WITH TEAM - Consider sending to analytics service
    logging.info(f"API Call: {log_data}")

def create_pagination_info(total_items: int, page: int, per_page: int) -> Dict[str, Any]:
    """Create pagination information"""
    total_pages = (total_items + per_page - 1) // per_page
    
    return {
        'total_items': total_items,
        'total_pages': total_pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': page < total_pages,
        'has_prev': page > 1,
        'next_page': page + 1 if page < total_pages else None,
        'prev_page': page - 1 if page > 1 else None
    }

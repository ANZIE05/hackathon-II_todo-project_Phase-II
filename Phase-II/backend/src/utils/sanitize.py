"""
Utility functions for sanitizing input data to prevent security vulnerabilities.
"""
import re
from typing import Union, List, Dict, Any, Optional
from html import escape
import bleach
import unicodedata


def sanitize_input(input_data: Union[str, Dict[str, Any], List[Any]], max_length: int = 1000) -> Union[str, Dict[str, Any], List[Any]]:
    """
    Sanitize input data to prevent XSS and other injection attacks.

    Args:
        input_data: Input data to sanitize (string, dict, or list)
        max_length: Maximum length for string inputs

    Returns:
        Sanitized input data
    """
    if isinstance(input_data, str):
        return sanitize_string(input_data, max_length)
    elif isinstance(input_data, dict):
        return {key: sanitize_input(value, max_length) for key, value in input_data.items()}
    elif isinstance(input_data, list):
        return [sanitize_input(item, max_length) for item in input_data]
    else:
        return input_data


def sanitize_string(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize a string input to prevent XSS and other injection attacks.

    Args:
        input_str: String to sanitize
        max_length: Maximum length allowed

    Returns:
        Sanitized string
    """
    if not isinstance(input_str, str):
        return input_str

    # Normalize Unicode characters
    input_str = unicodedata.normalize('NFKC', input_str)

    # Strip leading/trailing whitespace
    input_str = input_str.strip()

    # Limit length
    if len(input_str) > max_length:
        input_str = input_str[:max_length]

    # Remove null bytes
    input_str = input_str.replace('\x00', '')

    # Basic HTML escaping
    input_str = escape(input_str)

    return input_str


def sanitize_html(html_content: str, allowed_tags: Optional[List[str]] = None) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Args:
        html_content: HTML content to sanitize
        allowed_tags: List of allowed HTML tags (defaults to safe subset)

    Returns:
        Sanitized HTML content
    """
    if allowed_tags is None:
        # Default safe HTML tags for user-generated content
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
        ]

    # Define allowed attributes for each tag
    allowed_attributes = {
        '*': ['class'],  # Allow class attribute on all tags
        'a': ['href', 'title'],  # Allow href and title on anchor tags
        'img': ['src', 'alt', 'title'],  # Allow src, alt, and title on img tags
    }

    # Sanitize the HTML
    sanitized = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

    return sanitized


def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitize SQL identifiers (table names, column names) to prevent SQL injection.

    Args:
        identifier: SQL identifier to sanitize

    Returns:
        Sanitized SQL identifier
    """
    # Only allow alphanumeric characters and underscores
    # SQL identifiers must start with a letter or underscore
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
        raise ValueError(f"Invalid SQL identifier: {identifier}")

    return identifier


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove path traversal attempts
    filename = filename.replace('../', '').replace('..\\', '')

    # Only allow safe characters in filenames
    filename = re.sub(r'[^\w\-_.]', '_', filename)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')

    return filename


def sanitize_url(url: str) -> str:
    """
    Sanitize URL to prevent open redirect and other attacks.

    Args:
        url: URL to sanitize

    Returns:
        Sanitized URL
    """
    # Basic validation - only allow http and https schemes
    if not re.match(r'^https?://', url, re.IGNORECASE):
        raise ValueError("Invalid URL scheme")

    # Prevent javascript: and data: URLs
    if re.match(r'^(javascript|data|vbscript|file|ftp):', url, re.IGNORECASE):
        raise ValueError("Dangerous URL scheme")

    return url


def remove_control_characters(text: str) -> str:
    """
    Remove or replace control characters that could be used for attacks.

    Args:
        text: Text to clean

    Returns:
        Cleaned text
    """
    # Remove or replace control characters (except common whitespace)
    cleaned_text = ""
    for char in text:
        if ord(char) < 32 and char not in '\t\n\r':
            # Skip control characters
            continue
        cleaned_text += char

    return cleaned_text


def validate_and_sanitize_json_path(path: str) -> str:
    """
    Validate and sanitize JSON path expressions to prevent injection.

    Args:
        path: JSON path to validate

    Returns:
        Validated and sanitized path
    """
    # Basic validation for JSONPath-like expressions
    # Only allow alphanumeric, dots, brackets, and common operators
    if not re.match(r'^[a-zA-Z0-9_\.\[\]\'"\*\(\)=<>!,-]+$', path):
        raise ValueError("Invalid JSON path")

    return path


def sanitize_for_shell(command_part: str) -> str:
    """
    Sanitize input that might be used in shell commands.

    Args:
        command_part: Part of command to sanitize

    Returns:
        Sanitized command part
    """
    # Escape shell metacharacters
    escaped = command_part.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
    escaped = escaped.replace(';', '\\;').replace('|', '\\|').replace('&', '\\&')
    escaped = escaped.replace('`', '\\`').replace('$', '\\$').replace('(', '\\(').replace(')', '\\)')
    escaped = escaped.replace('<', '\\<').replace('>', '\\>')

    return escaped


def mask_sensitive_data(data: Dict[str, Any], sensitive_keys: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Mask sensitive data in a dictionary (e.g., for logging).

    Args:
        data: Dictionary containing potentially sensitive data
        sensitive_keys: List of keys to mask (defaults to common sensitive keys)

    Returns:
        Dictionary with sensitive data masked
    """
    if sensitive_keys is None:
        sensitive_keys = [
            'password', 'secret', 'token', 'key', 'auth', 'authorization',
            'cookie', 'credentials', 'ssn', 'social_security', 'credit_card',
            'card_number', 'cvv', 'pin', 'passphrase'
        ]

    masked_data = {}
    for key, value in data.items():
        if key.lower() in [sk.lower() for sk in sensitive_keys]:
            masked_data[key] = "***MASKED***"
        elif isinstance(value, dict):
            masked_data[key] = mask_sensitive_data(value, sensitive_keys)
        elif isinstance(value, list):
            masked_data[key] = [mask_sensitive_data(item, sensitive_keys) if isinstance(item, dict) else item for item in value]
        else:
            masked_data[key] = value

    return masked_data


def validate_boolean_param(param: Union[str, bool, int]) -> bool:
    """
    Safely convert a parameter to boolean.

    Args:
        param: Parameter to convert

    Returns:
        Boolean value
    """
    if isinstance(param, bool):
        return param
    elif isinstance(param, (int, float)):
        return bool(param)
    elif isinstance(param, str):
        return param.lower() in ['true', '1', 'yes', 'on', 't', 'y']
    else:
        return bool(param)


def clean_user_input(user_input: str) -> str:
    """
    Comprehensive cleaning of user input.

    Args:
        user_input: Raw user input

    Returns:
        Cleaned user input
    """
    if not isinstance(user_input, str):
        return user_input

    # Normalize Unicode
    user_input = unicodedata.normalize('NFKC', user_input)

    # Remove control characters
    user_input = remove_control_characters(user_input)

    # Strip whitespace
    user_input = user_input.strip()

    # Basic XSS prevention
    user_input = escape(user_input)

    return user_input
# Copyright 2025 Amazon.com, Inc. or its affiliates.
# SPDX-License-Identifier: Apache-2.0

"""
Language detection and configuration utilities.

This module provides functionality for automatic language detection and
language configuration management.
"""

from typing import Optional, Dict, Set
import logging
from bs4 import BeautifulSoup

# Set up module-level logger
logger = logging.getLogger(__name__)

# Supported language codes (ISO 639-1)
SUPPORTED_LANGUAGES: Set[str] = {
    'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 
    'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'he',
    'th', 'vi', 'id', 'ms', 'tl', 'sw', 'fa', 'ur', 'bn', 'ta',
    'te', 'ml', 'kn', 'gu', 'pa', 'or', 'as', 'mr', 'ne', 'si'
}

# Language code to name mapping for common languages
LANGUAGE_NAMES: Dict[str, str] = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'tr': 'Turkish',
    'pl': 'Polish',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'da': 'Danish',
    'no': 'Norwegian',
    'fi': 'Finnish',
    'he': 'Hebrew',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'id': 'Indonesian',
    'ms': 'Malay',
    'tl': 'Filipino',
    'sw': 'Swahili',
    'fa': 'Persian',
    'ur': 'Urdu',
    'bn': 'Bengali',
    'ta': 'Tamil',
    'te': 'Telugu',
    'ml': 'Malayalam',
    'kn': 'Kannada',
    'gu': 'Gujarati',
    'pa': 'Punjabi',
    'or': 'Odia',
    'as': 'Assamese',
    'mr': 'Marathi',
    'ne': 'Nepali',
    'si': 'Sinhala'
}

DEFAULT_LANGUAGE = 'en'


def detect_language_from_content(text: str, target_language: str = DEFAULT_LANGUAGE) -> str:
    """
    Detect language from text content using langdetect library.
    
    Args:
        text: Text content to analyze
        target_language: Target language to return if detection fails
        
    Returns:
        ISO 639-1 language code (e.g., 'en', 'es', 'fr')
    """
    if not text or not text.strip():
        logger.debug("No text provided for language detection, using target: %s", target_language)
        return target_language
        
    try:
        from langdetect import detect
        detected_lang = detect(text.strip())
        
        # Validate detected language is supported
        if detected_lang in SUPPORTED_LANGUAGES:
            logger.debug("Detected language: %s", detected_lang)
            return detected_lang
        else:
            logger.warning("Detected unsupported language: %s, using target: %s", 
                         detected_lang, target_language)
            return target_language
            
    except ImportError:
        logger.warning("langdetect library not available, using target language: %s", target_language)
        return target_language
    except Exception as e:
        logger.warning("Language detection failed: %s, using target: %s", str(e), target_language)
        return target_language


def detect_language_from_html(soup: BeautifulSoup, target_language: str = DEFAULT_LANGUAGE) -> str:
    """
    Detect language from HTML content.
    
    Args:
        soup: BeautifulSoup object of HTML document
        target_language: Target language to return if detection fails
        
    Returns:
        ISO 639-1 language code
    """
    # First check if lang attribute already exists and is valid
    html_tag = soup.find("html")
    if html_tag and html_tag.get("lang"):
        existing_lang = html_tag["lang"].strip().lower()
        # Handle language codes with regions (e.g., en-US -> en)
        if '-' in existing_lang:
            existing_lang = existing_lang.split('-')[0]
        if existing_lang in SUPPORTED_LANGUAGES:
            logger.debug("Using existing valid lang attribute: %s", existing_lang)
            return existing_lang
    
    # Extract text content for language detection
    text_content = ""
    
    # Prioritize content from key elements
    priority_tags = ['title', 'h1', 'h2', 'h3', 'p', 'div', 'span']
    for tag_name in priority_tags:
        elements = soup.find_all(tag_name)
        for element in elements[:5]:  # Limit to first 5 of each type
            element_text = element.get_text(strip=True)
            if element_text:
                text_content += " " + element_text
                if len(text_content) > 1000:  # Sufficient text for detection
                    break
        if len(text_content) > 1000:
            break
    
    # If not enough priority content, get general text
    if len(text_content.strip()) < 100:
        text_content = soup.get_text(strip=True)
    
    return detect_language_from_content(text_content, target_language)


def normalize_language_code(lang_code: str) -> str:
    """
    Normalize language code to ISO 639-1 format.
    
    Args:
        lang_code: Language code (may include region, e.g., 'en-US')
        
    Returns:
        Normalized ISO 639-1 language code
    """
    if not lang_code:
        return DEFAULT_LANGUAGE
        
    # Handle language codes with regions
    normalized = lang_code.strip().lower()
    if '-' in normalized:
        normalized = normalized.split('-')[0]
    
    # Validate against supported languages
    if normalized in SUPPORTED_LANGUAGES:
        return normalized
    
    logger.warning("Unsupported language code: %s, using default: %s", lang_code, DEFAULT_LANGUAGE)
    return DEFAULT_LANGUAGE


def get_language_name(lang_code: str) -> str:
    """
    Get human-readable language name for a language code.
    
    Args:
        lang_code: ISO 639-1 language code
        
    Returns:
        Human-readable language name
    """
    return LANGUAGE_NAMES.get(lang_code, lang_code.upper())


def is_valid_language_code(lang_code: str) -> bool:
    """
    Check if a language code is valid and supported.
    
    Args:
        lang_code: Language code to validate
        
    Returns:
        True if valid and supported, False otherwise
    """
    if not lang_code:
        return False
    
    normalized = normalize_language_code(lang_code)
    return normalized in SUPPORTED_LANGUAGES
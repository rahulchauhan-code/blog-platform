#!/usr/bin/env python
"""Test translation service"""
from app import app

with app.app_context():
    from services import TranslationService
    result = TranslationService.translate_text('Hello World', 'es')
    print(f'Spanish translation: {result}')
    result2 = TranslationService.translate_text('Welcome to Our Blog', 'fr')
    print(f'French translation: {result2}')
    result3 = TranslationService.translate_text('This is a test post', 'de')
    print(f'German translation: {result3}')

import urllib.request
import urllib.parse
import json

from django.conf import settings


def translate_text(text, target_language, source_language=None):
    """Translate text using Google Cloud Translate v2 API.

    Returns dict with keys: translatedText, detectedSourceLanguage.
    """
    api_key = settings.GOOGLE_TRANSLATE_API_KEY
    if not api_key:
        raise ValueError('GOOGLE_TRANSLATE_API_KEY not configured.')

    url = 'https://translation.googleapis.com/language/translate/v2'
    params = {
        'q': text,
        'target': target_language,
        'format': 'text',
        'key': api_key,
    }
    if source_language:
        params['source'] = source_language

    data = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    with urllib.request.urlopen(req, timeout=10) as response:
        result = json.loads(response.read().decode('utf-8'))

    translation = result['data']['translations'][0]
    return {
        'translated_text': translation['translatedText'],
        'detected_source_language': translation.get('detectedSourceLanguage', source_language or ''),
    }

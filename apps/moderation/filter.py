import re
import unicodedata

# Cache de palabras prohibidas (se recarga cada 5 minutos)
_banned_cache = None
_cache_time = None

# Sustituciones comunes para evadir filtros
LEET_MAP = {
    '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
    '7': 't', '@': 'a', '$': 's', '!': 'i', '+': 't',
}


def _normalize(text):
    """Normaliza texto removiendo acentos, leet speak y caracteres especiales."""
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = ''.join(LEET_MAP.get(c, c) for c in text)
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    text = re.sub(r'(?<=\b\w)\s+(?=\w\b)', '', text)
    return text


def _get_banned_words():
    """Obtiene palabras prohibidas con cache."""
    import time
    global _banned_cache, _cache_time

    now = time.time()
    if _banned_cache is not None and _cache_time and (now - _cache_time) < 300:
        return _banned_cache

    from apps.moderation.models import BannedWord
    words = list(BannedWord.objects.filter(is_active=True).values(
        'word', 'category', 'severity',
    ))
    _banned_cache = words
    _cache_time = now
    return words


def invalidate_cache():
    """Invalida la cache de palabras prohibidas."""
    global _banned_cache, _cache_time
    _banned_cache = None
    _cache_time = None


def check_text(text):
    """
    Verifica texto contra palabras prohibidas.
    """
    if not text:
        return {'is_clean': True, 'matched_words': [], 'max_severity': None, 'categories': []}

    normalized = _normalize(text)
    banned_words = _get_banned_words()
    matched = []
    categories = set()
    max_severity = None
    severity_order = {'warn': 0, 'block': 1, 'ban': 2}

    for entry in banned_words:
        word = entry['word'].lower()
        if word in text.lower() or word in normalized:
            matched.append(entry['word'])
            categories.add(entry['category'])
            s = entry['severity']
            if max_severity is None or severity_order.get(s, 0) > severity_order.get(max_severity, 0):
                max_severity = s

    return {
        'is_clean': len(matched) == 0,
        'matched_words': matched,
        'max_severity': max_severity,
        'categories': list(categories),
    }


def censor_text(text):
    """Reemplaza palabras prohibidas con asteriscos."""
    if not text:
        return text, []

    banned_words = _get_banned_words()
    censored = text
    found = []

    for entry in banned_words:
        word = entry['word']
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        if pattern.search(censored):
            found.append(word)
            replacement = word[0] + '*' * (len(word) - 1)
            censored = pattern.sub(replacement, censored)

    return censored, found


def create_flag(user, content_type, content_id, original_content, matched_words,
                flag_type='auto_text', reported_by=None, reason=''):
    """Crea un registro de contenido flaggeado."""
    from apps.moderation.models import ContentFlag
    return ContentFlag.objects.create(
        flag_type=flag_type,
        content_type=content_type,
        content_id=content_id,
        flagged_user=user,
        reported_by=reported_by,
        matched_words=', '.join(matched_words),
        original_content=original_content,
        reason=reason,
    )


def create_admin_alert(user, content_type, original_content, matched_words):
    """
    Crea una alerta para el admin cuando un usuario confirma enviar
    contenido inapropiado después de la advertencia.
    """
    from apps.moderation.models import ContentFlag
    return ContentFlag.objects.create(
        flag_type='auto_text',
        content_type=content_type,
        content_id=0,
        flagged_user=user,
        matched_words=', '.join(matched_words),
        original_content=original_content,
        reason='ALERTA: El usuario vio la advertencia y decidió enviar el mensaje igual.',
        status='pending',
    )


def check_and_flag(user, text, content_type, content_id, confirmed=False):
    """
    Verifica texto y decide qué hacer.

    Flujo:
    1. Texto limpio → se envía normal
    2. Grooming/pedofilia (ban) → ban automático, sin segunda oportunidad
    3. Otras palabras prohibidas + confirmed=False → retorna needs_confirmation=True
       con mensaje "No diga esas cosas por favor"
    4. Otras palabras prohibidas + confirmed=True → se envía IGUAL
       pero se crea alerta para el admin

    Retorna: {
        'allowed': bool,
        'needs_confirmation': bool,
        'censored_text': str,
        'warning_message': str or None,
        'severity': str or None,
    }
    """
    result = check_text(text)

    if result['is_clean']:
        return {
            'allowed': True,
            'needs_confirmation': False,
            'censored_text': text,
            'warning_message': None,
            'severity': None,
        }

    severity = result['max_severity']

    # ─── Grooming/Pedofilia: BAN AUTOMÁTICO sin oportunidad ─────────
    if severity == 'ban':
        from apps.moderation.models import UserBan
        create_flag(
            user=user,
            content_type=content_type,
            content_id=content_id or 0,
            original_content=text,
            matched_words=result['matched_words'],
        )
        UserBan.objects.create(
            user=user,
            reason=f"Contenido prohibido auto-detectado: {', '.join(result['matched_words'])}",
            is_permanent=True,
            is_active=True,
        )
        user.is_active = False
        user.save(update_fields=['is_active'])
        return {
            'allowed': False,
            'needs_confirmation': False,
            'censored_text': '',
            'warning_message': 'Tu cuenta ha sido suspendida por contenido prohibido.',
            'severity': 'ban',
        }

    # ─── Otras palabras: warn/block ─────────────────────────────────

    # Si NO confirmó todavía → mostrar advertencia "No diga esas cosas"
    if not confirmed:
        return {
            'allowed': False,
            'needs_confirmation': True,
            'censored_text': text,
            'warning_message': 'No diga esas cosas por favor.',
            'severity': severity,
        }

    # Si CONFIRMÓ (dio OK) → se envía pero queda alerta para el admin
    create_admin_alert(
        user=user,
        content_type=content_type,
        original_content=text,
        matched_words=result['matched_words'],
    )

    return {
        'allowed': True,
        'needs_confirmation': False,
        'censored_text': text,
        'warning_message': None,
        'severity': severity,
    }

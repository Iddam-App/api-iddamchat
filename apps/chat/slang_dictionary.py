import re

# Built-in slang / abbreviation dictionary per language.
# Each entry maps a lowercase abbreviation to its expanded form.

SLANG_DICTIONARY = {
    'en': {
        'idk': "I don't know",
        'idc': "I don't care",
        'idgaf': "I don't give a f***",
        'imo': 'in my opinion',
        'imho': 'in my humble opinion',
        'tbh': 'to be honest',
        'tbf': 'to be fair',
        'ngl': 'not gonna lie',
        'iirc': 'if I recall correctly',
        'afaik': 'as far as I know',
        'fwiw': 'for what it is worth',
        'wanna': 'want to',
        'gonna': 'going to',
        'gotta': 'got to',
        'lemme': 'let me',
        'gimme': 'give me',
        'kinda': 'kind of',
        'sorta': 'sort of',
        'dunno': "don't know",
        'brb': 'be right back',
        'brt': 'be right there',
        'omw': 'on my way',
        'omg': 'oh my god',
        'lol': 'laughing out loud',
        'lmao': 'laughing my ass off',
        'rofl': 'rolling on the floor laughing',
        'smh': 'shaking my head',
        'ftw': 'for the win',
        'btw': 'by the way',
        'fyi': 'for your information',
        'irl': 'in real life',
        'dm': 'direct message',
        'hmu': 'hit me up',
        'lmk': 'let me know',
        'rn': 'right now',
        'nvm': 'never mind',
        'np': 'no problem',
        'ty': 'thank you',
        'thx': 'thanks',
        'pls': 'please',
        'plz': 'please',
        'ur': 'your',
        'u': 'you',
        'r': 'are',
        'k': 'okay',
        'bc': 'because',
        'w/': 'with',
        'w/o': 'without',
        'atm': 'at the moment',
        'asap': 'as soon as possible',
    },
    'es': {
        'xq': 'porque',
        'xfa': 'por favor',
        'pf': 'por favor',
        'ntp': 'no te preocupes',
        'tqm': 'te quiero mucho',
        'tkm': 'te quiero mucho',
        'bn': 'bien',
        'tmb': 'también',
        'tb': 'también',
        'q': 'que',
        'pa': 'para',
        'x': 'por',
        'dnd': 'donde',
        'msj': 'mensaje',
        'grax': 'gracias',
        'gx': 'gracias',
        'nda': 'nada',
        'ns': 'no sé',
        'pq': 'porque',
        'vdd': 'verdad',
        'tmpc': 'tampoco',
        'bno': 'bueno',
        'wn': 'huevón',
        'ctm': 'conchetumadre',
        'csm': 'conchetumadre',
        'po': 'pues',
        'wea': 'cuestión',
    },
    'pt': {
        'vc': 'você',
        'tb': 'também',
        'tbm': 'também',
        'blz': 'beleza',
        'vlw': 'valeu',
        'obg': 'obrigado',
        'tmj': 'estamos juntos',
        'flw': 'falou',
        'msg': 'mensagem',
        'pq': 'porque',
        'qd': 'quando',
        'q': 'que',
        'td': 'tudo',
        'hj': 'hoje',
        'pfv': 'por favor',
        'abs': 'abraços',
        'bjs': 'beijos',
        'dps': 'depois',
        'ngm': 'ninguém',
        'agr': 'agora',
        'cmg': 'comigo',
        'ctg': 'contigo',
    },
    'fr': {
        'slt': 'salut',
        'stp': "s'il te plaît",
        'svp': "s'il vous plaît",
        'mdr': 'mort de rire',
        'ptdr': 'pété de rire',
        'jsp': 'je ne sais pas',
        'jsuis': 'je suis',
        'tkt': "ne t'inquiète pas",
        'pk': 'pourquoi',
        'pq': 'pourquoi',
        'pcq': 'parce que',
        'bcp': 'beaucoup',
        'tt': 'tout',
        'ms': 'mais',
        'qd': 'quand',
        'ajd': "aujourd'hui",
        'bjr': 'bonjour',
        'bsr': 'bonsoir',
        'dsl': 'désolé',
        'cad': "c'est-à-dire",
        'cb': 'combien',
        'rdv': 'rendez-vous',
        'snn': 'sinon',
    },
}


def expand_slang(text, source_language=None):
    """Expand slang / abbreviations in *text* before translation.

    If *source_language* is given (e.g. ``'en'``, ``'es'``), only the
    dictionary for that language is used.  Otherwise all languages are
    tried (safe because entries rarely collide across languages and the
    word-boundary regex prevents false positives on normal words).

    Returns the text with abbreviations replaced by their full forms.
    """
    if not text:
        return text

    if source_language:
        # Normalise codes like 'en-US' → 'en'
        lang_key = source_language.split('-')[0].lower()
        dicts_to_use = {lang_key: SLANG_DICTIONARY.get(lang_key, {})}
    else:
        dicts_to_use = SLANG_DICTIONARY

    for _lang, terms in dicts_to_use.items():
        for abbr, expansion in terms.items():
            # \b word-boundary, case-insensitive, whole-word match
            pattern = r'\b' + re.escape(abbr) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)

    return text

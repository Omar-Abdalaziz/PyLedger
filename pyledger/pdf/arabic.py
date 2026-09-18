"""
PyLedger PDF Module - Arabic Support
Arabic text reshaping and bidirectional text support
"""

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _HAS_ARABIC = True
except ImportError:
    _HAS_ARABIC = False

from xml.sax.saxutils import escape as _xml_escape


ARABIC_CHARS = set('ابتثجحخدذرزسشصضطظعغفقكلمنهويىآأإةةپچڤگـ،.؟')


def contains_arabic(text: str) -> bool:
    """Check if text contains Arabic characters"""
    return any(c in ARABIC_CHARS for c in text)


def reshape_arabic(text: str) -> str:
    """Reshape Arabic text for proper PDF rendering"""
    if not _HAS_ARABIC or not contains_arabic(text):
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


def prepare_text(text: str, force_arabic: bool = False) -> str:
    """Prepare text for PDF rendering (handle Arabic if needed).

    Always XML-escapes first: reportlab Paragraph treats <>/& as markup,
    so unescaped user text would break generation or inject markup.
    """
    text = _xml_escape(str(text or ''))
    if force_arabic or contains_arabic(text):
        return reshape_arabic(text)
    return text

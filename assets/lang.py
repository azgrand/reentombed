"""
Language literals for easy localization.
Variables inside curly braces {} will be formatted dynamically in the engine.
"""
import locale
import os
from typing import Dict, Final

# Global game constants that do not need translation.
# Using Final indicates this variable should not be reassigned.
GAME_TITLE: Final[str] = "ReEntombed v0.0.1"

# Master dictionary containing all supported languages (without the title)
TRANSLATIONS: Final[Dict[str, Dict[str, str]]] = {
    "en": {
        "score_display": "SCORE: {score}",
        "time_display": "{seconds}s",
        "final_score": "FINAL SCORE: {score}",
        "restart_prompt": "Press 'N' for a new maze (ESC to quit)",
    },
    "es": {
        "score_display": "PUNTOS: {score}",
        "time_display": "{seconds}s",
        "final_score": "PUNTUACIÓN FINAL: {score}",
        "restart_prompt": "Pulsa 'N' para un nuevo laberinto (ESC para salir)",
    },
    "fr": {
        "score_display": "SCORE : {score}",
        "time_display": "{seconds}s",
        "final_score": "SCORE FINAL : {score}",
        "restart_prompt": "Appuyez sur 'N' pour rejouer (ÉCHAP pour quitter)",
    },
    "de": {
        "score_display": "PUNKTE: {score}",
        "time_display": "{seconds}s",
        "final_score": "ENDSTAND: {score}",
        "restart_prompt": "Drücke 'N' für ein neues Labyrinth (ESC Beenden)",
    },
    "it": {
        "score_display": "PUNTI: {score}",
        "time_display": "{seconds}s",
        "final_score": "PUNTEGGIO FINALE: {score}",
        "restart_prompt": "Premi 'N' per un nuovo labirinto (ESC per uscire)",
    },
}

def get_system_language() -> str:
    """
    Detects the system language and returns the 2-letter ISO code.
    Defaults to 'en' (English) if detection fails.
    """
    try:
        # Modern approach: Check OS environment variables first (common in Linux/macOS)
        lang_env = os.environ.get("LANG")
        if lang_env:
            return lang_env[:2].lower()

        # Fallback for Windows: Set locale to default and retrieve it
        locale.setlocale(locale.LC_ALL, "")
        system_locale = locale.getlocale()[0]

        if system_locale:
            return system_locale[:2].lower()

    except (locale.Error, ValueError, TypeError):
        # Explicitly catching expected exceptions rather than a broad 'Exception'
        pass

    # If detection fails, fallback to English
    return "en"

# 1. Detect the user's operating system language
_current_lang: str = get_system_language()

# 2. Get the specific language translations (fallback to English if not found)
_language_texts: Dict[str, str] = TRANSLATIONS.get(_current_lang, TRANSLATIONS["en"])

# 3. Expose the TEXTS dictionary to be imported by engine.py
TEXTS: Final[Dict[str, str]] = {
    "window_title": GAME_TITLE,
    **_language_texts,
}
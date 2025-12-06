import replicate
import json
import logging
from deep_translator import GoogleTranslator
from jsonschema import validate, ValidationError

# Schema for IA response validation
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "words": {"type": "array", "items": {"type": "string"}, "minItems": 10, "maxItems": 10},
        "translations": {
            "type": "object",
            "properties": {
                "fr": {"type": "array", "items": {"type": "string"}, "minItems": 10, "maxItems": 10},
                "es": {"type": "array", "items": {"type": "string"}, "minItems": 10, "maxItems": 10},
                "it": {"type": "array", "items": {"type": "string"}, "minItems": 10, "maxItems": 10},
                "de": {"type": "array", "items": {"type": "string"}, "minItems": 10, "maxItems": 10}
            },
            "required": ["fr", "es", "it", "de"]
        },
        "theme_translations": {
            "type": "object",
            "properties": {
                "fr": {"type": "string"},
                "es": {"type": "string"},
                "it": {"type": "string"},
                "de": {"type": "string"}
            },
            "required": ["fr", "es", "it", "de"]
        }
    },
    "required": ["words", "translations", "theme_translations"]
}

def generate_translations(theme_name: str, debug=False):
    """
    Génère des mots et traductions en utilisant prompts JSON.
    Retourne un dict cohérent.
    """
    # Prompt JSON pour IA
    prompt_data = {
        "task": "generate_and_translate_words_and_theme",
        "theme": theme_name,
        "base_language": "en",
        "target_languages": ["fr", "es", "it", "de"],
        "count": 10,
        "instructions": "Generate 10 simple, joyful words for children aged 3-7. Also provide translations for the theme name. Provide response as valid JSON only: {\"words\": [\"word1\", ...], \"translations\": {\"fr\": [...], \"es\": [...], ...}, \"theme_translations\": {\"fr\": \"translated_theme\", ...}}"
    }
    prompt_text = f"Task: {json.dumps(prompt_data, indent=2)}\nRespond with JSON only."

    logging.debug(f"Sending JSON prompt to IA: {prompt_text}")
    
    try:
        output = replicate.run("meta/llama-2-70b-chat", input={"prompt": prompt_text, "temperature": 0.5, "max_tokens": 500})
        response_text = "".join(output).strip()
        logging.debug(f"IA response: {response_text}")
        
        # Extraire JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
        else:
            raise ValueError("No JSON found in response")
        
        # Validation avec schema
        try:
            validate(instance=data, schema=RESPONSE_SCHEMA)
        except ValidationError as e:
            raise ValueError(f"JSON validation failed: {e}")
        
        words = data["words"]
        translations = data["translations"]
        theme_translations = data.get("theme_translations", {})
        
        # Assurer que en est présent
        translations["en"] = words
        theme_translations["en"] = theme_name
        
        logging.info(f"Generated {len(words)} words with translations")
        return {"theme": theme_name, "words": words, "translations": translations, "theme_translations": theme_translations, "univers_name": theme_name.capitalize(), "univers_translations": theme_translations}
    
    except Exception as e:
        logging.error(f"IA generation failed: {e}, falling back to static")
        # Fallback statique pour test
        static_words = ["monkey", "tree", "bird", "flower", "snake", "lion", "zebra", "giraffe", "elephant", "butterfly"]
        translations = {"en": static_words}
        theme_translations = {"en": theme_name}
        for lang in ["fr", "es", "it", "de"]:
            translations[lang] = [GoogleTranslator(source='en', target=lang).translate(word) for word in static_words]
            theme_translations[lang] = GoogleTranslator(source='en', target=lang).translate(theme_name)
        return {"theme": theme_name, "words": static_words, "translations": translations, "theme_translations": theme_translations, "univers_name": theme_name.capitalize(), "univers_translations": theme_translations}
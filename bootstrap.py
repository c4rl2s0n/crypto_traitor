from config.di_container import container


def bootstrap():
    from dotenv import load_dotenv
    load_dotenv()

    container.config.api_keys.OPENAI.from_env("API_KEY_OPENAI")
    container.config.api_keys.GEMINI.from_env("API_KEY_GEMINI")
    container.config.api_keys.FREECRYPTO.from_env("API_KEY_FREECRYPTO")
    container.config.api_keys.COINGECKO.from_env("API_KEY_COINGECKO")

    container.config.paths.DB.from_env("DB_PATH")

    import google.generativeai as genai
    genai.configure(api_key=container.config.api_keys.GEMINI())

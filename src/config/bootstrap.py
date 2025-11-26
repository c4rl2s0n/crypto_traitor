from src.config import container


def bootstrap():
    from dotenv import load_dotenv
    load_dotenv()

    # API Keys for external (3rd party) APIs
    container.config.api_keys.OPENAI.from_env("API_KEY_OPENAI")
    container.config.api_keys.GEMINI.from_env("API_KEY_GEMINI")
    container.config.api_keys.FREECRYPTO.from_env("API_KEY_FREECRYPTO")
    container.config.api_keys.COINGECKO.from_env("API_KEY_COINGECKO")

    # filepaths
    container.config.paths.DB.from_env("DB_PATH")

    # Timeseries config (Influx)
    container.config.influx.DB_URL.from_env("TS_DB_URL")
    container.config.influx.TOKEN.from_env("TS_DB_API_KEY")
    container.config.influx.ORG.from_env("TS_DB_ORG")

    # configure gemini api
    import google.generativeai as genai
    genai.configure(api_key=container.config.api_keys.GEMINI())

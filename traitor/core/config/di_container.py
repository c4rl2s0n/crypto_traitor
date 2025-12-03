from dependency_injector import containers, providers

from traitor.core.config.config import *
from traitor.core.data.db import Database
from traitor.core.tools.ai.agents.llm_gemini import LLMGemini


class Container(containers.DynamicContainer):
    config = providers.Configuration()
    prompts = providers.ThreadSafeSingleton(PROMPTS)
    summarize_agent = providers.Factory(LLMGemini, model='gemini-2.5-flash')

    def __init__(self):
        # load environment variables before registering dependencies
        self.load_config()
        super().__init__()
        self.db = providers.Resource(Database, path=self.config.db.CONNECTION)

    def load_config(self):
        from dotenv import load_dotenv
        load_dotenv()

        # API Keys for external (3rd party) APIs
        self.config.api_keys.OPENAI.from_env("API_KEY_OPENAI")
        self.config.api_keys.GEMINI.from_env("API_KEY_GEMINI")
        self.config.api_keys.FREECRYPTO.from_env("API_KEY_FREECRYPTO")
        self.config.api_keys.COINGECKO.from_env("API_KEY_COINGECKO")

        # DB
        self.config.db.URL.from_env("DB_URL")
        self.config.db.PORT.from_env("DB_PORT")
        self.config.db.PASSWORD.from_env("POSTGRES_PASSWORD")
        self.config.db.USER.from_env("POSTGRES_USER")
        self.config.db.NAME.from_env("POSTGRES_DB")
        db = self.config.db
        self.config.db.CONNECTION.from_value(
            f"postgresql+psycopg2://{db.USER()}:{db.PASSWORD()}@{db.URL()}:{db.PORT()}/{db.NAME()}")

        # configure gemini api
        import google.generativeai as genai
        genai.configure(api_key=self.config.api_keys.GEMINI())


# global container for dependency injection
container = Container()


def bootstrap():
    from dotenv import load_dotenv
    load_dotenv()

    # API Keys for external (3rd party) APIs
    container.config.api_keys.OPENAI.from_env("API_KEY_OPENAI")
    container.config.api_keys.GEMINI.from_env("API_KEY_GEMINI")
    container.config.api_keys.FREECRYPTO.from_env("API_KEY_FREECRYPTO")
    container.config.api_keys.COINGECKO.from_env("API_KEY_COINGECKO")

    # DB
    container.config.db.URL.from_env("DB_URL")
    container.config.db.PORT.from_env("DB_PORT")
    container.config.db.PASSWORD.from_env("POSTGRES_PASSWORD")
    container.config.db.USER.from_env("POSTGRES_USER")
    container.config.db.NAME.from_env("POSTGRES_DB")
    db = container.config.db
    container.config.db.CONNECTION.from_value(
        f"postgresql+psycopg2://{db.USER()}:{db.PASSWORD()}@{db.URL()}:{db.PORT()}/{db.NAME()}")

    # configure gemini api
    import google.generativeai as genai
    genai.configure(api_key=container.config.api_keys.GEMINI())
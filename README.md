# AI Crypto Traitor
One day, this shall become an AI powered bot for trading crypto currencies.

## Code / Structure
- _assets_
  - contains non-code assets
    - i.e. prompts for LLMs
    - ... ?
- _config_
  - _config.py_
    - holds values like paths to prompts
    - ... what else we might need ...
  - _di_container.py_
    - Setup Dependency Injection (DI, [Wiki](https://en.wikipedia.org/wiki/Dependency_injection), [G4G](https://www.geeksforgeeks.org/system-design/dependency-injectiondi-design-pattern/))
    - define classes/instances to be used throughout the application (e.g. database, repositories, config-values)
    - container can be accessed using `from config/di_container import container`
    - objects can be accessed through the container
      - e.g. `container.db()` will return the instance of the database
- _data/_
  - contains all the data-related code
  - database setup (db.py)
  - data models (_data/models_)
  - data repositories (_data/repositories_)
    - interface to interact with database (store/query data)
- _research/_
  - _coins/_
    - research information about coins
    - currently just used to get a list of available coins, but maybe not necessary at all...
  - _market/_
    - \<to be done>
    - should be used to get market data, prices, ...
  - _news/_
    - get news articles from various sources
    - __NOTE__: It seems even the [CoinDesk](./research/news/sources/coindesk.py) is no longer working, seems they expect JS now...
      - To cover more sources, it might be an option to use an automated [Selenium](https://www.selenium.dev/documentation/webdriver/getting_started/first_script/?language=python) browser, as [requests](https://docs.python-requests.org/en/latest/index.html) cannot handle JS
- _tools/_
  - contains generic tools, like 
    - the LLM API
    - scripts for scraping HTML (using [BeatifulSoup](https://pypi.org/project/beautifulsoup4/))
- _bootstrap.py_
  - reads values (API Keys, DB path, ...?) from environment variables
- _main.py_
  - entry point to the program, without a lot of logic right now


## Coding Style
There is no strict style, but using strong typing would be appreciated to catch type-errors early.
Also try to keep things modular to facilitate maintenance and extension.

## TODO
- Code structure (modular)
  - what can be generalized?
    - LLM Interface
    - Scraper interface
- Refine prompts
  - currently the LLM labeled weird things as assets
    - maybe create a list of currencies to take into account
    - when LLM finds 'new' coins, it can ask to include them into the list. A user will have to accept that
    - prompt should contain a list of known/accepted coins which can be considered 'assets'
  - how to summarize market values?

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
    - __NOTE__: It seems even the [CoinDesk](traitor/core/research/news/sources/coindesk.py) is no longer working, seems they expect JS now...
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

## Lifecycle
The Lifecycle of the bot consists of several threads that serve different purposes.
Each thread runs in its own interval (e.g. scrape news once every hour)

### Setup
when starting the program, the bot should
- check if coins are loaded, otherwise load a set of available coins from the API
- for active coins, get historical price data to fill the gap to the last price (or get as many prices as possible if no prices are available)

### News Research
The news research lifecycle should
- go through all the news sources and gather links of articles that are not yet stored in the database (simply compare URLs)
  - Using RSS feeds would also be an option (in the future)
- get the contents of those new articles
- Query an LLM to summarize the articles and update them in the database
- summarize by timeframe/buckets
- (optional) It would be nice, if the LLM could link an article correctly with coins in our database
  - maybe we can provide a tool, where it can create this link by giving a coin-symbol, so we create the reference to a coin
  - by using a tool, we can control to omit hallucinated 'coin symbols', as we can safely ignore them
  - having proper references in the database would allow to reduce the set of news to analyze for each coin
Interval: 1 hour (?)
- before taking trading decisions, these articles should be summarized again (eventually multiple times?) to extract trends for certain coins
  - maybe run the summary on the set of news several times, each time creating an analysis regarding a single coin?

### Market Research
The market research should run more frequently, as prices constantly update.
Usually, trading bots probably gather that data at fast rates (or live from a websocket), but we are trying to mimic a very invested human trader here, so we update the data every few minutes.
Market research consists of
- updating the prices for all the _active_ coins (e.g. all 5 minutes)
- extract mathematical features about the prices
  - check [here](https://github.com/c4rl2s0n/crypto_traitor/issues/2) for specific features etc.
  - analyze prices in different chunks
    - last year, last month, last week, last day, last hour
- Query an LLM to summarize these mathematical features
- The analysis cycle may not be necessary to run every time the prices are updated (especially not for long intervals)
  - running this analysis might be sufficient before taking trading decisions

### (optional/future) Community Research
The CoinGecko API provides information about the developer/community activity.
This data could be gathered e.g. daily to monitor a community trend.

### Trading
In the trading lifecycle, an LLM should be provided with all the gathered and prepared information in order to decide what to buy, hold, or sell.
Information it will get includes
- list of coins to take into account
  - current balance of each coin (in the wallet)
  - current value of each coin (on the market)
  - list of open trades (so they can be canceled or taken into account)
  - trading ratios? they can be derived from the current values, so maybe not necessary
  - (?) How do we know the transaction fees? 
- price analysis for each of those coins
- news analysis for each of those coins
- its self-defined trading strategy
Tools:
- update_strategy(str)
  - The LLM can define a trading strategy (and maybe other notes about the coins etc?)
  - the strategy will be added to the prompt for trading every time, so it can act more consistently
- trade(coin_out, amount, coin_in)
  - provide an interface to actually trade a coin for another one
- cancel_trade(id)
  - it might be necessary to cancel trades in case nobody agrees to trade for a while?
- queue_next_cycle(duration)
  - The LLM can decide on its own, how frequently it want to reason about trading
    - e.g. if the market is very active, it might make sense to check trading options more frequently?
  - maybe provide lower/upper bounds to prevent denial-of-tokens

## UI
Currently, the idea would be to provide a web UI (using Django?) to show the state of the bot.
This includes
- list of coins (option to activate new coins) 
  - detailed view for active coins with
    - price chart
    - trading history (future)
    - coin-info (e.g. URLs, description, ...)
- list of articles and summaries
  - might help understand how the AI summarizes the articles and if the scrapers work correctly
- complete trading history
- strategy history
- wallet overview
  - balance of different coins
- bot activity

The UI is considered nice-to-have, but actually has no real priority before the lifecycle of the bot is more or less complete/working. 

## Brainstorming
- Potential sources for information (check `<url>/robots.txt`!)
  - https://bitcointalk.org/
- Get initial information about Coins from [CoinGecko API](https://docs.coingecko.com/v3.0.1/reference/coins-id)
  - Names
  - description
  - interesting URLs
    - homepage
    - Forum
    - github (?)
    - "blockchain_site" (?)
    - subreddit (might be interesting when API key would be available. Does manual scraping work?)
  - image
  - genesis_date
  - historical OHCL for the last year
  - max_supply
  - community_data (?): {
    "facebook_likes": null,
    "reddit_average_posts_48h": 0,
    "reddit_average_comments_48h": 0,
    "reddit_subscribers": 0,
    "reddit_accounts_active_48h": 0,
    "telegram_channel_user_count": null
  },
  - "developer_data": {
    "forks": 36426,
    "stars": 73168,
    "subscribers": 3967,
    "total_issues": 7743,
    "closed_issues": 7380,
    "pull_requests_merged": 11215,
    "pull_request_contributors": 846,
    "code_additions_deletions_4_weeks": {
      "additions": 1570,
      "deletions": -1948
    },
    "commit_count_4_weeks": 108,
    "last_4_weeks_commit_activity_series": []
  }
- Get continuous information about coins:
  - daily OHCL
  - market_cap_rank
  - 24h high / low
  - current price (scrape in regular intervals, maybe use other API if rate limit becomes a problem)
  - price_change_percentage_1h/24h/7d/14d/30d/60d/200d/1y
  - market_cap_change(_percentage)_24h
  - total_supply

- (optional/extended scope)
  - would be nice to somehow show the information we gather and all the actions the AI is doing in a website
    - maybe use django and create simple overviews
  - Send actual transactions
    - [MetaMask API](https://docs.metamask.io/services/tutorials/ethereum/send-a-transaction/send-a-transaction-py/)
      - could be useful to automatically send transactions
      - should work at least for ethereum (or all ether-based chains?)
      - https://developer.metamask.io/key/active-endpoints

# NOTES
- due to tsfresh-dependencies, python version >= 3.14 are not supported (because of numba package)
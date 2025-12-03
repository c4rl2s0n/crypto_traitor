import os

import uvicorn
from django.core.management import execute_from_command_line

from traitor.core.data.repositories import CoinRepository
from traitor.core.config import container
from traitor.core.research.news.sources.cryptoslate import CryptoSlate
from traitor.core.services import CoinService, ResearchService

def run_webserver():
    from traitor.traitor_ui.dashboard.service import start_random_service

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "traitor.traitor_ui.web.settings")
    start_random_service()
    uvicorn.run(
        "traitor.traitor_ui.web.asgi:application",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )

    # execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000"])

def run():
    container.init_resources()
    container.wire(modules=[__name__])

    # TODO: Setup
    # TODO: Research Loop (News + Summarize)
    # TODO: Research Loop (Market + Analyze + Summarize)
    # TODO: Trading Loop
    coin_service = CoinService()
    coin_service.load_all_coins()

    coin_repo = CoinRepository()
    coins = coin_repo.get_by_coingecko_ids(['bitcoin', 'zcash', 'monero'])
    for c in coins:
        coin_service.activate_coin(c)

    research_service = ResearchService()
    research_service.research_news([CryptoSlate()])

    container.shutdown_resources()


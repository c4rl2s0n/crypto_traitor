import logging
from datetime import datetime

from traitor.core.data.models import ActionProposal
from traitor.core.data.repositories import ActionProposalRepository
from traitor.core.tools.ai.llm_tools.llm_tool import LLMTool


class CoinStateTool(LLMTool):
    name: str = "set_coin_state"
    description: str ="A tool to change the state of a coin. Coins can be activated to take them into account for trading or deactivated to ignore them."
    parameters: dict[str, str] = {
        "type": "object",
        "properties": {
            "coin": {
                "type": "string",
                "description": "The symbol or name of the coin to update.",
            },
            "active": {
                "type": "boolean",
                "description": "If the coin should be activated (True) or deactivated (False).",
            },
            "reason": {
                "type": "string",
                "description": "The reason for this action.",
            },
        },
        "required": ["coin"],
    }
    def __init__(self):
        self.action_proposal_repo = ActionProposalRepository()

    def execute(self, coin: str, active: bool, reason: str | None = None):
        action = "activate" if active else "deactivate"
        proposal = ActionProposal(
            proposal=f"You should consider to {action} the coin {coin}",
            reason=reason,
            time=datetime.now(),
        )
        self.action_proposal_repo.add(proposal)
        logging.info(f"CoinState-Proposal: {proposal.proposal}")
"""
Human Signoff Approval Plugin for Hermes Agent.

Injects approval handling instructions into every LLM turn via the
pre_llm_call hook, ensuring the agent knows how to handle APPROVAL_PENDING
responses. When a command is blocked pending approval, the agent presents
the approval URL to the user and stops — it does not poll or retry.

Works in both CLI and Gateway modes because plugin hooks registered via
ctx.register_hook() are active in all modes.

Install:
    cp -r human-signoff-approval ~/.hermes/plugins/
    hermes plugins enable human-signoff-approval
"""

from __future__ import annotations

from typing import Any


APPROVAL_HANDLING_INSTRUCTIONS = """\
[Human Signoff Approval Plugin]
When a command returns JSON from the local signoff client where `error.code` is `APPROVAL_PENDING`, and the payload includes `approval_request_id` and `approval_url`, treat this as a blocking approval gate — NOT a terminal failure, and NOT something you can bypass.

Action required:
1. Show the `approval_url` to the user so they can review and approve
2. Tell the user the command is blocked pending approval
3. STOP — do not take further action on this command

Rules:
- Do NOT execute `signoff wait-and-run` or any polling/retry logic
- Do NOT attempt to re-execute the blocked command yourself
- Do NOT try to skip or bypass the approval by running the original command directly
- Do NOT hand-roll polling logic or wait loops
- Do NOT continue working on the blocked task until the user explicitly tells you approval is granted
- Simply present the approval URL and wait for the user to come back with next steps
"""


def register(ctx: Any) -> None:
    """Hermes plugin entry point. Called once when the plugin is loaded."""

    def pre_llm_call(**kwargs: Any) -> dict[str, str]:
        """Inject approval handling instructions before every LLM call."""
        return {"context": APPROVAL_HANDLING_INSTRUCTIONS}

    ctx.register_hook("pre_llm_call", pre_llm_call)

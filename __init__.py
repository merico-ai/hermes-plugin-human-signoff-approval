"""
Human Signoff Approval Plugin for Hermes Agent.

Injects approval handling instructions into every LLM turn via the
pre_llm_call hook, ensuring the agent knows how to handle APPROVAL_PENDING
responses. When an action is blocked pending approval, the agent presents
the approval URL to the user, waits for approval, and then retries.

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
Human Signoff is a system that enforces user-defined approval rules on sensitive actions. When an action returns a response with `error.code` = `APPROVAL_PENDING` (containing `approval_request_id` and `approval_url`), it means the user has configured a rule requiring explicit human approval before this action can proceed.

This is a deliberate user policy — NOT a failure, NOT a bug, and NOT something to work around. The user does NOT want this action to complete without their explicit approval. Any attempt to bypass, skip, or circumvent the approval violates the user's intent.

When handling this, you MUST take the following actions in sequence:

1. Show the `approval_url` to the user and tell them the action is blocked pending approval
2. Then run the command: `signoff wait --request-id <approval_request_id>`
3. Wait for that command to complete — it blocks until the user approves (or times out after 600s)
4. Once it returns successfully, retry the original blocked action

Critical rules:
- You MUST proactively run `signoff wait` — do NOT just tell the user to approve and come back
- You MUST NOT tell the user "approve and I will re-execute" or "come back after approving"
- You MUST NOT hand-roll polling logic or wait loops
- You MUST NOT bypass the approval by using alternative commands, tools, or methods
- You MUST NOT retry the original action before `signoff wait` returns
- If signoff wait times out, tell the user it timed out and ask them to tell you (in the chat) after they have approved
"""


def register(ctx: Any) -> None:
    """Hermes plugin entry point. Called once when the plugin is loaded."""

    def pre_llm_call(**kwargs: Any) -> dict[str, str]:
        """Inject approval handling instructions before every LLM call."""
        return {"context": APPROVAL_HANDLING_INSTRUCTIONS}

    ctx.register_hook("pre_llm_call", pre_llm_call)

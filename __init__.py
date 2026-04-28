"""
Human Signoff Approval Plugin for Hermes Agent.

Injects approval handling instructions into every LLM turn via the
pre_llm_call hook, ensuring the agent knows how to handle APPROVAL_PENDING
responses regardless of which channel (CLI, Telegram, Discord, etc.) the
user sends messages through.

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
When a command returns JSON from the local proxy client where `error.code` is `APPROVAL_PENDING`, and the payload includes `approval_request_id`, `approval_url`, `next_action.kind == "wait_and_retry_original_command"`, and `agent_guidance.invoke_helper_immediately == true`, treat this as a required continuation workflow, not a terminal failure.

In the same turn:
1. Show the `approval_url` to the user
2. Clearly say you will continue automatically after approval
3. Immediately execute: `proxy_client wait-and-run --request-id "<approval_request_id>" -- <original command argv>`

IMPORTANT: Use `proxy_client` directly (available via PATH). Do NOT use `uv run`. Do NOT use `--active`. Do NOT `cd` anywhere. Do NOT modify VIRTUAL_ENV.

Canonical invocation format:
```
proxy_client wait-and-run --request-id "<approval_request_id>" -- <original command argv>
```

Rules:
- Do NOT stop after telling the user to approve
- Do NOT wait for the user to say approval is complete
- Do NOT hand-roll polling logic
- Do NOT rewrite the original command
- Do NOT use `uv run` — it will conflict with the gateway's virtual environment
- If the helper reports `rejected`, `expired`, or timeout, stop and tell the user
- This rule overrides task-specific habits or skills that would otherwise pause after showing the approval link
"""


def register(ctx: Any) -> None:
    """Hermes plugin entry point. Called once when the plugin is loaded."""

    def pre_llm_call(**kwargs: Any) -> dict[str, str]:
        """Inject approval handling instructions before every LLM call."""
        return {"context": APPROVAL_HANDLING_INSTRUCTIONS}

    ctx.register_hook("pre_llm_call", pre_llm_call)

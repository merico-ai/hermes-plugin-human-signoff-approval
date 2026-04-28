# Hermes Human Signoff Approval Plugin

Auto-handles `APPROVAL_PENDING` responses from the human-signoff proxy for Hermes Agent.

## How it works

This plugin registers a `pre_llm_call` hook that injects approval handling instructions into every LLM turn. When a command is blocked and requires approval, the agent will:

1. Show the approval URL to the user
2. Automatically call `proxy_client wait-and-run` to wait for approval and retry

This works across **all channels** (CLI, Telegram, Discord, WeChat, etc.) because plugin hooks are active in both CLI and Gateway modes.

## Prerequisites

1. **Human Signoff MVP** is deployed and running
2. **proxy_client** is available in PATH:
   ```bash
   which proxy_client
   proxy_client --help
   ```
3. **proxy_client is logged in**:
   ```bash
   proxy_client login
   ```

## Installation

```bash
# Install from GitHub
hermes plugins install merico-ai/hermes-plugin-human-signoff-approval

# Enable the plugin
hermes plugins enable human-signoff-approval

# Restart Gateway (required for plugin to take effect)
launchctl bootout gui/$(id -u)/ai.hermes.gateway
sleep 2
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

## Configuration

### Required: Disable streaming mode

Edit `~/.hermes/config.yaml`:

```yaml
display:
  streaming: false
```

This ensures approval URLs are delivered reliably in complete messages, especially for channels like WeChat.

Restart Gateway after changing this setting:

```bash
launchctl bootout gui/$(id -u)/ai.hermes.gateway
sleep 2
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

### Gateway proxy setup (for Gateway mode)

If using Hermes Gateway with channels (Telegram, Discord, WeChat, etc.), configure proxy environment:

Edit `~/Library/LaunchAgents/ai.hermes.gateway.plist`:

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>HTTP_PROXY</key>
    <string>http://127.0.0.1:17771</string>
    <key>HTTPS_PROXY</key>
    <string>http://127.0.0.1:17771</string>
    <key>NO_PROXY</key>
    <string>localhost,127.0.0.1</string>
    <key>TERMINAL_TIMEOUT</key>
    <string>600</string>
</dict>
```

Then reload:

```bash
launchctl bootout gui/$(id -u)/ai.hermes.gateway
sleep 2
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

## Usage

### CLI mode

```bash
hermes chat
# Send a command that requires approval
```

### Gateway mode

Through any configured channel (Telegram, Discord, WeChat, etc.), send a command that requires approval. The agent will show the approval URL and automatically continue after you approve.

## Verification

```bash
# Check plugin is enabled
hermes plugins list

# Check plugin is loaded (should show "X hook(s) loaded")
tail -20 ~/.hermes/logs/agent.log | grep "hook(s) loaded"
```

## Uninstallation

```bash
# Disable and remove
hermes plugins disable human-signoff-approval
hermes plugins remove human-signoff-approval

# Or if manually installed
rm -rf ~/.hermes/plugins/human-signoff-approval
```

## Troubleshooting

### Plugin not working

1. Check plugin is enabled: `hermes plugins list`
2. Check agent logs: `tail -f ~/.hermes/logs/agent.log`
3. Verify proxy_client is in PATH: `which proxy_client`

### Approval URL not showing in channels

1. Ensure `display.streaming: false` in `~/.hermes/config.yaml`
2. Restart Hermes Gateway
3. Check Gateway logs: `tail -f ~/.hermes/logs/gateway.log`

### `wait-and-run` fails

1. Ensure proxy_client is logged in: `proxy_client login`
2. Check proxy_client can reach backend
3. Verify `TERMINAL_TIMEOUT=600` is set in Gateway environment

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please use the GitHub issue tracker.

# Hermes Human Signoff Approval Plugin

Auto-handles `APPROVAL_PENDING` responses from the human-signoff proxy for Hermes Agent.

## How it works

This plugin registers a `pre_llm_call` hook that injects approval handling instructions into every LLM turn. When a command is blocked and requires approval, the agent will:

1. Show the approval URL to the user
2. Automatically call `signoff wait-and-run` to wait for approval and retry

This works across **all channels** (CLI, Telegram, Discord, WeChat, etc.) because plugin hooks are active in both CLI and Gateway modes.

## Prerequisites

1. **Human Signoff MVP** is deployed and running

## Installation

### Step 1: Install the signoff client

Install the `signoff` CLI from [merico-ai/human-signoff-releases](https://github.com/merico-ai/human-signoff-releases):

```bash
# Download and run the installer
curl -fsSL -o install.sh https://raw.githubusercontent.com/merico-ai/human-signoff-releases/main/install.sh
bash install.sh
```

The installer downloads the `signoff` CLI binary and can optionally configure the Hermes approval plugin, the OpenClaw approval plugin, and the CA certificate / gateway proxy settings.

```bash
# Verify installation
which signoff
signoff --help

# Login
signoff login
```

### Step 2: Install and enable the plugin

```bash
# Install from GitHub
hermes plugins install merico-ai/hermes-plugin-human-signoff-approval

# Enable the plugin
hermes plugins enable human-signoff-approval
```

### Step 3: Configure Gateway proxy (macOS only)

> **Note:** These instructions are for macOS only. On Linux, Gateway runs as a systemd service and requires different configuration.

Edit `~/Library/LaunchAgents/ai.hermes.gateway.plist` and add proxy environment variables:

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

### Step 4: Configure streaming mode (Optional)

> **Optional:** Edit `~/.hermes/config.yaml` to disable streaming mode:

```yaml
display:
  streaming: false
```

This ensures approval URLs are delivered reliably in complete messages, especially for channels like WeChat. If you experience issues with approval URLs not showing in channels, try this setting.

### Step 5: Restart Gateway (macOS only)

> **Note:** These instructions are for macOS only. On Linux, use `systemctl --user restart hermes-gateway`.

```bash
launchctl bootout gui/$(id -u)/ai.hermes.gateway
sleep 2
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

## Usage

### CLI mode (with proxy)

> **Note:** CLI mode requires setting proxy environment variables manually. Gateway proxy configuration only affects the Gateway service.

```bash
# Set proxy environment variables and start chat
HTTP_PROXY=http://127.0.0.1:17771 \
HTTPS_PROXY=http://127.0.0.1:17771 \
NO_PROXY=localhost,127.0.0.1 \
hermes chat

# Send a command that requires approval
```

### Gateway mode

Through any configured channel (Telegram, Discord, WeChat, etc.), send a command that requires approval. The agent will show the approval URL and automatically continue after you approve.

## Verification

```bash
# Check plugin status (most reliable)
hermes plugins list

# Check plugin directory exists
ls -la ~/.hermes/plugins/human-signoff-approval/

# Optional: Check hook count (reference only)
# Note: "X hook(s) loaded" includes all hooks, not just plugins
tail -20 ~/.hermes/logs/agent.log | grep "hook(s) loaded"
```

**Important**: The most reliable verification is `hermes plugins list`. The `"hook(s) loaded"` log message includes all hooks (system + plugins) and cannot confirm if the specific plugin is loaded.

**Functional test** (recommended):
Send a command through your channel (WeChat, Telegram, etc.) that requires approval. If the plugin is working, it will:
1. Display the approval URL
2. Automatically call `signoff wait-and-run`

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
3. Verify signoff is in PATH: `which signoff`

### Approval URL not showing in channels

1. Ensure `display.streaming: false` in `~/.hermes/config.yaml`
2. Restart Hermes Gateway
3. Check Gateway logs: `tail -f ~/.hermes/logs/gateway.log`

### `wait-and-run` fails

1. Ensure signoff is logged in: `signoff login`
2. Check signoff can reach backend
3. Verify `TERMINAL_TIMEOUT=600` is set in Gateway environment

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please use the GitHub issue tracker.

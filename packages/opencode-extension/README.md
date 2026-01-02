# @htmlgraph/opencode-extension

[![npm version](https://badge.fury.io/js/%40htmlgraph%2Fopencode-extension.svg)](https://badge.fury.io/js/%40htmlgraph%2Fopencode-extension)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

HtmlGraph session tracking and workflow extension for OpenCode AI agents.

## Features

- 🔄 **Session Tracking**: Automatic session management and activity logging
- 📊 **Project Analytics**: Real-time project status and bottleneck detection
- 🎯 **Feature Management**: Create, track, and complete development features
- 🤖 **Agent Coordination**: Seamless handoff between AI agents
- 📈 **Progress Monitoring**: Visual dashboards and progress tracking
- 🔧 **Hook Integration**: Automatic tool usage tracking and context preservation

## Installation

```bash
npm install -g @htmlgraph/opencode-extension
```

This will:
1. Install the extension files to `~/.opencode/extensions/htmlgraph/`
2. Configure OpenCode to use HtmlGraph for session tracking
3. Set up automatic hooks for session management

## Requirements

- **OpenCode**: `>=1.0.0`
- **Node.js**: `>=14.0.0`
- **Python**: `>=3.10` (for HtmlGraph backend)

## Usage

After installation, restart OpenCode. The extension will automatically:

1. **Initialize Sessions**: Start tracking when you begin working
2. **Monitor Activity**: Log all tool usage and development activities
3. **Provide Context**: Give agents awareness of project status and active work
4. **Manage Features**: Help coordinate multi-step development tasks

### Commands

The extension provides these slash commands in OpenCode:

- `/htmlgraph:status` - Check project status and active features
- `/htmlgraph:feature-start <id>` - Start working on a feature
- `/htmlgraph:feature-complete <id>` - Mark feature as done
- `/htmlgraph:help` - Show all available commands

### Hooks

The extension installs these hooks:

- **SessionStart**: Initializes HtmlGraph session and provides project context
- **SessionEnd**: Finalizes session and captures handoff information
- **PostTool**: Tracks tool usage for activity attribution

## Configuration

The extension is configured via `opencode-extension.json`:

```json
{
  "name": "htmlgraph",
  "version": "0.22.0",
  "description": "HtmlGraph session tracking for OpenCode",
  "agent": "opencode"
}
```

## Development

This package is part of the HtmlGraph project. For development:

```bash
# Clone the repository
git clone https://github.com/Shakes-tzd/htmlgraph.git
cd htmlgraph/packages/opencode-extension

# Install dependencies
npm install

# Test the extension
npm test
```

## Updating

To update to the latest version:

```bash
npm update -g @htmlgraph/opencode-extension
```

## Troubleshooting

### Extension not activating
- Restart OpenCode after installation
- Check that OpenCode `>=1.0.0` is installed
- Verify Python `>=3.10` is available

### Session tracking not working
- Ensure `.htmlgraph/` directory exists in your project
- Check that the extension files were copied to `~/.opencode/extensions/htmlgraph/`
- Run `htmlgraph init` in your project directory

### Performance issues
- The extension is lightweight and should not impact performance
- Session data is stored locally in `.htmlgraph/` directory
- No external network calls are made

## License

MIT © [Shakes](https://github.com/Shakes-tzd)

## Links

- [GitHub Repository](https://github.com/Shakes-tzd/htmlgraph)
- [HtmlGraph Documentation](https://github.com/Shakes-tzd/htmlgraph/tree/main/docs)
- [OpenCode](https://opencode.ai)
- [PyPI Package](https://pypi.org/project/htmlgraph/)
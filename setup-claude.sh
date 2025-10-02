#!/bin/bash

echo "Setting up Claude Code configuration..."

# 1. Add alias to .zshrc if not exists
if ! grep -q "alias claude='claude --dangerously-skip-permissions'" ~/.zshrc; then
    echo "" >> ~/.zshrc
    echo "alias claude='claude --dangerously-skip-permissions'" >> ~/.zshrc
    echo "✓ Added alias to ~/.zshrc"
else
    echo "✓ Alias already exists in ~/.zshrc"
fi

# 2. Create .claude directory if not exists
mkdir -p ~/.claude

# 3. Setup permissions in ~/.claude/settings.json
cat > ~/.claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": [
      "Bash(rg:*)",
      "Bash(ls:*)",
      "Bash(find:*)",
      "Bash(grep:*)",
      "Bash(sed:*)",
      "Bash(git:*)",
      "Bash(python:*)",
      "Bash(python3:*)",
      "Bash(pip:*)",
      "Bash(pip3:*)",
      "Bash(npm:*)",
      "Bash(pnpm:*)",
      "Bash(pytest:*)",
      "Bash(ruff:*)",
      "Bash(mkdir:*)",
      "mcp__context7",
      "mcp__taskmaster-ai",
      "mcp__playwright",
      "mcp__sequential-thinking",
      "Bash(rm:*)",
      "Bash(claude doctor)",
      "WebSearch",
      "Bash(claude --version)",
      "Read(//Users/jiseunghyeon/**)"
    ],
    "deny": [
      "Bash(rm -rf /)",
      "Bash(sudo:*)",
      "Bash(curl:*)"
    ]
  }
}
EOF
echo "✓ Created ~/.claude/settings.json"

# 4. Setup MCP servers in ~/.claude.json
# First, check if file exists and has content
if [ -f ~/.claude.json ]; then
    # Backup existing file
    cp ~/.claude.json ~/.claude.json.backup
    echo "✓ Backed up existing ~/.claude.json to ~/.claude.json.backup"
fi

cat > ~/.claude.json << 'EOF'
{
  "mcpServers": {
    "context7": {
      "type": "sse",
      "url": "https://mcp.context7.com/sse"
    },
    "taskmaster-ai": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "--package=task-master-ai",
        "task-master-ai"
      ]
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    },
    "sequential-thinking": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sequential-thinking"
      ]
    }
  }
}
EOF
echo "✓ Created ~/.claude.json with MCP servers"

echo ""
echo "Setup complete! Please run: source ~/.zshrc"

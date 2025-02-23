# 🤖 MCP - Master Control Program

Welcome to MCP, your friendly neighborhood tool suggester! Think of it as your AI butler who always knows exactly which tool you need. 

## 🌟 What's This All About?

Ever found yourself thinking "I know there's a tool for this, but which one?" Well, MCP is here to save the day! It's like having a super-smart assistant who remembers all your tools and suggests the perfect one for your task.

## 🚀 Features

- 🎯 **Context-Aware Tool Suggestions**: Just tell MCP what you're trying to do
- 🌈 **Beautiful CLI Output**: Because life's too short for boring terminals
- 🧠 **Smart Matching**: Understands what you mean, not just what you say
- 📚 **Command History**: Remembers your tool usage patterns
- 🎨 **Rich Formatting**: Colors! Emojis! Tables! Oh my!

## 🛠️ Installation

```bash
# Install required packages
pip install click rich

# Make the script executable
chmod +x mcp.py
```

## 🎮 Usage

The main command is `mcp` with two subcommands:

### 1. List Tools (`l`)
```bash
# Basic usage
mcp l "hot day tickets"

# More examples
mcp l ubuntu
mcp l "need to search files"
mcp l "monitor system"
```

### 2. Run Tools (`run`)
```bash
# Basic usage
mcp run gak password
mcp run system status
```

## 🎭 Examples

Looking for file search tools?
```bash
$ mcp l search files
🛠️  Suggested Tools
┌──────────┬────────────────────────────────────┬─────────────────┐
│ Tool     │ Description                        │ Example         │
├──────────┼────────────────────────────────────┼─────────────────┤
│ 🔍 gak   │ Global Awesome Keywords - Search   │ gak password    │
│          │ files like a ninja!                │                 │
├──────────┼────────────────────────────────────┼─────────────────┤
│ 📁 file  │ File operations with style         │ file analyze .  │
└──────────┴────────────────────────────────────┴─────────────────┘
```

## 🎨 Pro Tips

1. 🎯 Be descriptive in your context: "need to monitor system resources" is better than just "monitor"
2. 🔍 Use keywords that match tool categories
3. 🌈 Enjoy the colorful output - life's too short for monochrome terminals!

## 🤝 Contributing

Got a cool tool to add? Want to make MCP even smarter? We'd love your help! Just:

1. Fork this repo
2. Add your awesome changes
3. Send a PR with a fun emoji in the title

## 🎉 Credits

Created with ❤️ by Hue and Aye, with moral support from Trisha in Accounting (who thinks this is the coolest thing since spreadsheet macros!)

## 🎵 Fun Fact

This project was created while listening to Elvis's "A Little Less Conversation" - because sometimes we need a little less conversation and a little more tool suggestion! 🕺

---

Remember: In the digital world, every tool has its place, and MCP knows exactly where that place is! 🌟

*"TCB - Taking Care of Business, with a little help from MCP!"* - Elvis (probably) 
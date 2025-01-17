---
title: Mega tmux Cheat Sheet
description: Supercharge your terminal workflow with tmux—covering basics, remote access, multi-user setups, and integrating AI agents for ultimate productivity.
category: CLI Tools
tags:
  - tmux [1]
  - remote-access [3]
  - ssh [5]
  - multiuser [7]
  - terminal-multiplexer [10]
  - agent-integration [15]
  - aygentic [20]
related:
  - byobu [10]
  - warp-terminal [20]
  - devops-automation [25]
  - linux-tools [30]
---
Welcome to the **Mega tmux ChEEt**! ⚡ Unleash tmux’s full potential, from basic commands to next-level remote setups, AI magic, and multi-user wizardry. It's time to own the terminal.

---

## **1. tmux Basics: The Command Jedi Moves** 🥋

| Command                          | Description                                         |
|----------------------------------|-----------------------------------------------------|
| `tmux`                           | Start a new tmux session                            |
| `tmux new-session -s <name>`     | Create a named session                              |
| `tmux ls` or `tmux list-sessions`| List all active tmux sessions                       |
| `tmux attach -t <name>`          | Attach to a specific session                        |
| `tmux kill-session -t <name>`    | Kill a specific session                             |

### **Pane and Window Management**

| Command             | Action                           |
| ------------------- | --------------------------------- |
| `Ctrl-b "`          | Split the window horizontally     |
| `Ctrl-b %`          | Split the window vertically       |
| `Ctrl-b x`          | Close the active pane             |
| `Ctrl-b n`          | Switch to the next window         |
| `Ctrl-b p`          | Switch to the previous window     |
| `Ctrl-b &`          | Kill the current window           |
| `Ctrl-b z`          | Zoom in/out on a pane             |

### **Rebinding Prefix (`Ctrl-b` kills your hands!)**

Use this in `~/.tmux.conf` to rebind the prefix:

```bash
unbind C-b
set-option -g prefix C-a
bind C-a send-prefix
```

**Reload tmux config**:

```bash
tmux source-file ~/.tmux.conf
```

---

## **2. Persistent Sessions Across SSH and Reboots** 🔗

tmux keeps your sessions alive even if you disconnect over SSH. Combine that with **tmux-resurrect** for true persistence:

### **Set Up a Persistent tmux Workflow**

1. Install tmux:

   ```bash
   brew install tmux         # macOS
   sudo apt install tmux     # Ubuntu/Debian
   ```

2. Install *tmux-resurrect* (saves sessions post-reboot):

   ```bash
   git clone https://github.com/tmux-plugins/tmux-resurrect ~/.tmux/plugins/tmux-resurrect
   ```

### Enable Persistent Restores

Add this to your `~/.tmux.conf`:

```bash
set -g @plugin 'tmux-plugins/tmux-resurrect'
bind r source-file ~/.tmux/plugins/tmux-resurrect/resurrect.tmux
```

Press `Ctrl-b + r` anytime to **restore your saved sessions**.

---

## **3. Custom Sockets for Remote tmux Access** 🌐

Remote sessions with custom sockets let you interact with tmux smarter than ever.

### **Start tmux with a Custom Socket**

```bash
tmux -S ~/.tmux-sockets/mysocket new-session -s mysession
```

- **`-S <path>`**: Use a custom socket file to manage tmux sessions.
- **Pro Tip**: Avoid `/tmp/` (it’s cleared on reboot). Use `$HOME/.tmux-sockets`.

### **Connect Locally or Remotely to tmux with the Custom Socket**

1. On the server:

   ```bash
   tmux -S ~/.tmux-sockets/mysocket attach-session -t mysession
   ```

2. From **remote SSH**:

   ```bash
   ssh -L /tmp/tmux.sock:/absolute/path/to/mysocket user@remote-server
   tmux -S /tmp/tmux.sock attach-session -t mysession
   ```

---

## **4. Multi-User Collaboration: Pair Programming, Debugging, and More** 🤝

### **Share tmux With Someone Else**

#### Permissions for Your Socket

Make sure the socket is accessible:

```bash
chmod 770 ~/.tmux-sockets/mysocket
```

Make it available to a user group:

```bash
sudo chgrp developers ~/.tmux-sockets/mysocket
```

#### Other User Accesses the Shared Socket

They attach using:

```bash
tmux -S /path/to/socket attach-session -t mysession
```

And voilà! You just set up **real-time terminal sharing**. ✨

---

### **Co-Screen Live Tmux Sessions**

Want a more casual collaboration tool? Pair tmux with **CoScreen** for live shared screens instead:

- Install: [CoScreen](https://www.coscreen.co)

---

## **5. Aygentic Use Case (AI-In-The-Session)** 🤖

Your AI "agents" (or Aygents 🤓) can live *within* your tmux sessions and provide:

1. **Real-Time Assistance**: Coding completions, summaries, etc.
2. **Live Monitoring**: Tail logs, track workflows, and watch YOU work (it's mutual, you watch them too).  
3. **Context-Aware Chat**: Access AI tools like ChatGPT right from within your terminal.

### **Set Up AI Agents in tmux**

1. Get an AI CLI like GPT (custom wrapper for ChatGPT):

   ```bash
   brew install python3
   pip install openai
   ```

2. Run a GPT-powered agent in a tmux pane:

   ```bash
   tmux new-session -s aygentic 'python ai_chat_agent.py'
   ```

3. Switch to the pane:
   Use `Ctrl-b o` (next pane), type questions to your AI buddy, and get instant insights!

---

### **Automate AI Actions in tmux**

For example, monitor server health using an "Agented" AI process in a detached session:

```bash
tmux new-session -d -s health-check 'python server-monitor-agent.py'
```

Get AI alerts or updates directly.

---

## **6. Real-Life Workflows** 🌍

### **Administering Remote Servers**

1. Start tmux when SSH’ing into a server:

   ```bash
   ssh user@server
   tmux new-session -s admin
   ```

2. Detach and reattach later:

   ```bash
   tmux attach-session -t admin
   ```

### **Pair Programming**

- Share the session:

  ```bash
  tmux -S /tmp/shared-socket attach-session -t coding
  ```

### **Interactive AI-Assisted Debugging**

1. Watch logs in one pane:

   ```bash
   tail -f /var/log/app.log
   ```

2. AI suggests fixes live in another pane:

   ```bash
   python ai_debugger.py
   ```

---

## **Pro Tips for Terminal Excellence** 💡

1. **Enable Mouse Support**:  
   Add this to `~/.tmux.conf`:

   ```bash
   set -g mouse on
   ```

2. **Sync Panes (Broadcast Commands to All Panes!)**:

   ```bash
   Ctrl-b : setw synchronize-panes on
   ```

3. **Manage AI Tools in tmux**:
   - Split panes to run parallel AI tasks.
   - Use panes for log analysis + AI context.

---

**Visit us at [cheet.is](https://cheet.is) for vitamin-level knowledge boosts! Let's rule those terminals 🖤⚡**  
🐾 *Multi-universe panes, activated.*

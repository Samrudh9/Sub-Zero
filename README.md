# 🥶 Sub-Zero

**AI-Powered Subscription Assassin** — The first financial app that doesn't just track your subscriptions, it *kills* them for you. 

> *"Sub-Zero is an AI bodyguard for your bank account that doesn't just track your unwanted subscriptions—it logs in and cancels them for you."*

---

## 🎯 The Problem

Current apps like Rocket Money or your banking app act like a nosy roommate.  They tell you, *"Hey, you're wasting $20 on Adobe,"* but then they walk away. You still have to: 
- Spend 45 minutes finding your password
- Navigate a confusing website
- Argue with a chatbot to actually cancel it

## ✨ The Solution

Sub-Zero acts like a ruthless personal assistant.  You just swipe **Left** on the Adobe charge, and the AI says, *"On it."* It goes out, waits on hold, clicks the hidden buttons, and comes back with a receipt that says:  **"It's gone."**

---

## 🚀 How It Works

### Step 1: The X-Ray (Detection)
Connect your bank account (just like Venmo or Mint). The app instantly scans your history and separates "real bills" from "Subscription Sludge."

### Step 2: The Decision (Swipe to Kill)
- See a subscription you don't want? **Swipe Left** 👈
- See one you want to keep? **Swipe Right** 👉

### Step 3: The Hitman (Agent Execution)
Once you swipe left, our AI Agent:
1. Navigates to the merchant's website
2. Logs in and finds the cancellation page (even if they hid it)
3. Clicks "Cancel" and defeats retention offers
4. Takes a screenshot as proof and saves it to your **Graveyard** 🪦

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SUB-ZERO ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │   Mobile     │    │   Backend    │    │   AI Agent       │   │
│  │  (Flutter)   │◄──►│  (Supabase)  │◄──►│   (The Hitman)   │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
│         │                   │                     │              │
│         ▼                   ▼                     ▼              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │ Swipe UI     │    │ Plaid API    │    │ Browser Auto     │   │
│  │ (Tinder-like)│    │ Integration  │    │ (Steel. dev +     │   │
│  │              │    │              │    │  Claude 3.5)     │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Mobile App** | Flutter/Dart | Cross-platform iOS/Android with swipe gestures |
| **AI Agent** | Claude 3.5 Sonnet + browser-use | Natural language web navigation |
| **Browser Engine** | Steel.dev | Anti-bot evasion & session recording |
| **Orchestration** | Temporal. io | Handle 2FA waits, retries, long-running tasks |
| **Backend** | Supabase | Auth, database, edge functions |
| **Bank Data** | Plaid API | Subscription detection from transactions |

---

## 📁 Project Structure

```
sub-zero/
├── agent/                      # Python - The Hitman
│   ├── browser_agent.py        # Main cancellation agent
│   ├── dark_pattern_shield.py  # Detects & defeats retention tricks
│   ├── cancellation_flows/     # Site-specific flows
│   └── requirements.txt
│
├── orchestration/              # Temporal workflows
│   ├── workflows/
│   │   └── cancellation_workflow.py
│   └── activities/
│       ├── browser_activities.py
│       └── notification_activities.py
│
├── backend/                    # Supabase backend
│   ├── api/
│   ├── lib/
│   └── schema.sql
│
└── mobile/                     # Flutter app
    └── lib/
        ├── screens/
        ├── models/
        └── services/
```

---

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Flutter 3.16+
- Anthropic API key (Claude)
- Steel.dev account (for production)
- Plaid API keys

### Agent Setup (Python)

```bash
cd agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key-here"
export STEEL_CDP_URL="your-steel-endpoint"  # Optional for local dev

# Test the agent
python browser_agent.py
```

### Mobile Setup (Flutter)

```bash
cd mobile
flutter pub get
flutter run
```

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| **🔪 The Kill Switch** | Automated cancellation with one swipe |
| **🪦 The Graveyard** | History of cancelled subscriptions + savings tracker |
| **🛡️ Dark Pattern Shield** | AI-trained to spot & defeat retention tricks |
| **🧟 Zombie Protection** | Alerts if a cancelled charge comes back |

---

## 📋 Roadmap

- [x] Phase 1: Agent Runtime (browser-use + Claude)
- [x] Phase 2: Temporal Orchestration (2FA handling)
- [x] Phase 3: Mobile UI (Swipe interface)
- [ ] Phase 4: Plaid Integration (Bank connection)
- [ ] Phase 5: Steel.dev Integration (Anti-bot)
- [ ] Phase 6: Backend & Database (Supabase)
- [ ] Phase 7: Beta Launch 🚀

---

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## ⚠️ Disclaimer

Sub-Zero automates subscription cancellation on behalf of users who provide explicit consent and credentials. Always ensure you have the right to cancel subscriptions before using this tool.

---

<p align="center">
  <b>Built with 🥶 by the Sub-Zero Team</b>
</p>
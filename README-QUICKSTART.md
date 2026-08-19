# Hermes Opportunity Finder - Quick Start Guide

## 📦 What You've Got

This scaffold provides a **complete local AI agent system** that:
- ✅ Continuously scrapes web + archives for opportunities
- ✅ Filters matches against your criteria (learning over time)
- ✅ Architects implementation plans automatically
- ✅ Formats proposals for actionable next steps
- ✅ Runs on your RTX 4090 with Qwen 3.8 model

**Architecture:**
```
Docker Compose
├── Model Runner (Qwen 3.8 on GPU)  →  OpenAI-compatible API
└── Hermes Backend (Agent orchestration)  →  Persistent memory & learning
    ├── Scraper Skill
    ├── Filter Skill
    ├── Planner Skill
    └── Proposer Skill
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- RTX 4090 with NVIDIA drivers + nvidia-docker
- ~20GB disk space for model cache
- ~30 min for first run (model download)

### 2. Install Hermes Locally
```bash
curl -fsSL https://install.hermes.nousresearch.com | bash
```

### 3. Make setup script executable
```bash
chmod +x hermes-setup.sh
```

### 4. Initialize & Start
```bash
# One-time setup (creates directories, copies config)
./hermes-setup.sh init

# Start the full stack
./hermes-setup.sh start
```

You'll see:
```
✓ Services started successfully

═══════════════════════════════════════════════════════
   Hermes Opportunity Finder is Running!
═══════════════════════════════════════════════════════

📍 Hermes Backend:    http://localhost:9119
🤖 Model Runner:      http://localhost:8000
📁 Hermes Home:       /home/user/.hermes
📋 Opportunities:     /home/user/opportunities
```

---

## 💬 Launch Hermes Desktop

Open a new terminal:
```bash
hermes desktop
```

This launches the native UI with:
- 💻 Chat interface
- 🧠 Memory Graph (see what agent learned)
- 📝 File browser & artifacts gallery
- ⚙️ Configuration & cron job management
- 🔄 Multi-agent orchestration

---

## 📋 Configure Your Criteria

Edit the filter to match your opportunity type:

**Option A: In Desktop UI**
1. Open Hermes Desktop
2. Settings → Model & Tools → Edit Skills
3. Modify `filter.py` keywords and exclude_keywords

**Option B: Directly in code**
```python
# In hermes-skills/filter.py, update OpportunityCriteria:
OpportunityCriteria(
    keywords=[
        "startup", "funding", "seed", "partnership",
        # Add your custom keywords
        "your-specific-domain"
    ],
    exclude_keywords=["scam", "spam", ...],
    domains=["ycombinator.com", ...],  # Whitelist sources
    min_relevance_score=0.6,  # 0.0-1.0
    max_age_days=30
)
```

Then reload Hermes:
```bash
hermes skill reload filter
```

---

## 🔄 How the Loop Works

### Automatic Continuous Loop (via cron)

**Every 6 hours:**
```
1. Scraper Agent  → Fetches from feeds & web
                    └─→ Raw opportunities

2. Filter Agent   → Scores matches against criteria
                    └─→ Top-scored opportunities (~0.6+)

3. Planner Agent  → Creates implementation timeline
                    └─→ Phase-by-phase breakdown

4. Proposer Agent → Formats as readable proposal
                    └─→ Saved to ~/opportunities/proposals/
```

**Weekly (Sunday 2 AM):**
- Memory consolidation: learns from patterns
- Criteria optimization: tunes keywords

**Daily (9 AM):**
- Top 3 opportunities formatted as digest
- Proposals saved with next-step actions

View cron jobs:
```bash
hermes cron list
hermes cron show scrape-opportunities  # View single job
```

---

## 📊 Where Your Data Goes

```
~/.hermes/                          # Hermes home
├── config.yaml                     # Agent configuration
├── memory/                         # Persistent learning
│   ├── agent.db                   # Memory store
│   └── learned_patterns/          # Extracted insights
├── skills/                        # Scraper, filter, planner, proposer
├── sessions/                      # Chat history
└── logs/                          # Operation logs

~/opportunities/                    # Findings
├── proposals/                     # Generated proposals
│   └── 2024-01-10/
│       ├── funding-series-a.md
│       ├── partnership-techco.md
│       └── ...
├── feedback/                      # Your ratings (used for learning)
│   └── proposal-1-relevant.txt
├── archive/                       # Old proposals (30+ days)
└── reports/                       # Monthly summaries
```

---

## 🎯 Train the Filter with Feedback

The agent learns from your feedback. To train it:

**1. Rate opportunities (stored in memory):**
```bash
# Create feedback file
echo "relevant" > ~/opportunities/feedback/opportunity-123-relevant.txt
echo "false_positive" > ~/opportunities/feedback/opportunity-456-fp.txt
```

**2. Agent auto-learns:**
- Every day at noon, processes feedback
- Updates keyword list and exclusions
- Improves scoring accuracy

**3. Monitor learning:**
```bash
# In Hermes Desktop:
# Settings → Memory Graph
# See your learned patterns grow
```

---

## 🛠️ Troubleshooting

**Model Runner won't start:**
```bash
docker compose logs model-runner

# If stuck on Electron download:
export ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
./hermes-setup.sh start
```

**Out of VRAM:**
```bash
# Reduce model precision (less accurate but faster)
# In docker-compose.yml, change:
MODEL_TAG: "Q3_K_M"  # Smaller quantization
```

**Hermes backend not responding:**
```bash
docker compose exec hermes-backend curl http://localhost:9119/api/status
docker compose logs hermes-backend
```

**Clear everything and restart:**
```bash
./hermes-setup.sh reset
./hermes-setup.sh init
./hermes-setup.sh start
```

---

## 📚 Next Steps

1. **Customize scraping sources** (`scraper.py` → `get_feeds_to_monitor()`)
   - Add RSS feeds, APIs, web endpoints relevant to your domain

2. **Refine filtering criteria** (`filter.py` → keywords, exclude_keywords)
   - Test with real opportunities; adjust min_relevance_score

3. **Extend planner templates** (`planner.py` → add new `opp_types`)
   - Add custom phases for your specific workflow

4. **Set up notifications** (`hermes-crontab.yaml` → notifications section)
   - Email, Slack, Discord alerts for high-scoring opportunities

5. **Deploy remotely** (optional)
   - Run Hermes backend on a home server/VPS
   - Connect Desktop from anywhere via Hermes Cloud or remote gateway

---

## 📖 Learn More

- **Hermes Docs:** https://hermes-agent.nousresearch.com/docs
- **Qwen Models:** https://huggingface.co/Qwen
- **Docker Docs:** https://docs.docker.com
- **Model Runner:** https://docker.com/products/model-runner/

---

## 🔐 Security Notes

- **API Keys:** Store in `~/.hermes/.env` (not in config)
- **Model Safety:** Qwen 3.8 abliterated variant removes safety guardrails
- **Scraping:** Respect robots.txt and terms of service
- **Memory:** Persistent data in `~/.hermes/memory/` — keep your disk backed up

---

**Ready?** Run `./hermes-setup.sh start` and check `hermes desktop`! 🚀

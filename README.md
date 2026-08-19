# Hermes Opportunity Finder 🎯

A **local AI agent system** that continuously discovers opportunities from the web and archives, filters them intelligently, and proposes actionable plans.

**Architecture:** Hermes Agent (Nous Research) + Qwen 3.8 LLM + Docker

---

## Features

✅ **Continuous Loop:** Scrapes web feeds and archives on schedule  
✅ **Intelligent Filtering:** Learns from feedback; reduces false positives  
✅ **Auto-Planning:** Generates phase-by-phase implementation strategies  
✅ **Persistent Memory:** Learns patterns over time  
✅ **Desktop UI:** Native Hermes Desktop app for interaction  
✅ **Local Inference:** Runs entirely on your RTX 4090  

---

## Quick Start

### Prerequisites
- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- NVIDIA GPU (RTX 4090) with CUDA drivers
- ~30GB disk space (model + cache)
- Hermes Agent installed locally

### 1. Install Hermes

```bash
curl -fsSL https://install.hermes.nousresearch.com | bash
```

### 2. Initialize & Start

**Windows (PowerShell):**
```powershell
cd C:\Users\go\hermes-opportunity-finder
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\hermes-setup.ps1 start
```

**macOS/Linux (Bash):**
```bash
chmod +x hermes-setup.sh
./hermes-setup.sh start
```

### 3. Launch Desktop UI

```bash
hermes desktop
```

Opens native UI on macOS/Windows/Linux with chat, memory graph, file browser, and configuration.

---

## Architecture

```
Docker Compose
├── Model Runner (Qwen 3.8 on GPU)
│   └── OpenAI-compatible API (:8000)
│
└── Hermes Backend (:9119)
    ├── Agent Orchestration
    ├── Persistent Memory (SQLite)
    └── Skills:
        ├── scraper.py    (web crawling)
        ├── filter.py     (scoring & learning)
        ├── planner.py    (strategy generation)
        └── proposer.py   (proposal formatting)
```

---

## File Structure

```
.
├── docker-compose.yml        # Orchestration
├── hermes-config.yaml        # Agent configuration
├── hermes-crontab.yaml       # Scheduled tasks
├── hermes-setup.ps1          # Windows setup
├── hermes-setup.sh           # Unix setup
├── hermes-skills/            # Agent skills
│   ├── scraper.py
│   ├── filter.py
│   ├── planner.py
│   └── proposer.py
├── README-QUICKSTART.md      # Detailed setup guide
└── README.md                 # This file
```

---

## How It Works

### Automatic Loop (via Docker Compose + Cron)

**Every 6 hours:**
1. **Scraper** → Fetches from RSS feeds, web sources
2. **Filter** → Scores opportunities (learns over time)
3. **Planner** → Creates implementation timeline
4. **Proposer** → Formats as readable proposals

**Weekly:** Memory consolidation & criteria refinement  
**Daily:** Top 3 opportunities formatted as digest

### Data Flow

```
Web Sources → Scraper → Raw Opportunities
                            ↓
                        Filter (learns)
                            ↓
                      Filtered Matches
                            ↓
                    Planner + Proposer
                            ↓
        ~/opportunities/proposals/ (saved)
```

---

## Customization

### Change Opportunity Criteria

Edit `hermes-skills/filter.py`:
```python
OpportunityCriteria(
    keywords=["startup", "funding", "partnership"],  # Your keywords
    exclude_keywords=["scam", "spam"],              # What to avoid
    domains=["ycombinator.com"],                     # Whitelist sources
    min_relevance_score=0.6,                         # 0.0-1.0 threshold
    max_age_days=30                                  # How old is too old
)
```

### Add Web Sources to Scrape

Edit `hermes-skills/scraper.py`:
```python
def get_feeds_to_monitor(self):
    return [
        "https://news.ycombinator.com/rss",
        "https://producthunt.com/feed",
        # Add your custom feeds
    ]
```

### Adjust Cron Schedule

Edit `hermes-crontab.yaml`:
```yaml
jobs:
  - name: scrape-opportunities
    schedule: "0 */6 * * *"  # Every 6 hours
```

---

## Commands

### Windows (PowerShell)
```powershell
.\hermes-setup.ps1 init      # Initialize directories
.\hermes-setup.ps1 start     # Start services
.\hermes-setup.ps1 stop      # Stop services
.\hermes-setup.ps1 logs      # View logs
.\hermes-setup.ps1 status    # Check status
```

### macOS/Linux (Bash)
```bash
./hermes-setup.sh init
./hermes-setup.sh start
./hermes-setup.sh stop
./hermes-setup.sh logs
./hermes-setup.sh status
```

### Docker

```bash
# View logs
docker compose logs -f

# Check status
docker compose ps

# Stop everything
docker compose down

# Restart
docker compose restart
```

---

## Training the Filter

The agent learns from your feedback. Rate opportunities to improve accuracy:

```bash
# Mark as relevant (improves matching)
echo "relevant" > ~/opportunities/feedback/opp-123-relevant.txt

# Mark as false positive (improves exclusions)
echo "false_positive" > ~/opportunities/feedback/opp-456-fp.txt
```

Agent processes feedback daily at noon and updates keywords/exclusions.

---

## Data Storage

```
~/.hermes/
├── config.yaml              # Agent configuration
├── memory/
│   └── agent.db            # Learned patterns, feedback history
├── skills/
│   ├── scraper.py
│   ├── filter.py
│   ├── planner.py
│   └── proposer.py
├── sessions/               # Chat history
└── logs/                   # Operation logs

~/opportunities/
├── proposals/              # Generated proposals
├── feedback/               # User ratings
├── archive/                # Old opportunities (30+ days)
└── reports/                # Monthly summaries
```

---

## Troubleshooting

### Model Runner won't start
```bash
docker compose logs model-runner
# Check VRAM: nvidia-smi
# Reduce quantization if out of memory
```

### Hermes backend not responding
```bash
docker compose logs hermes-backend
curl http://localhost:9119/api/status
```

### Out of disk space
```bash
docker system df
docker system prune
```

### Clear everything and restart
```bash
docker compose down -v
rm -rf ~/.hermes
# Then run setup again
```

---

## Performance Tips

- **Model Precision:** Adjust `MODEL_TAG` in `docker-compose.yml` (Q3_K_M for faster, Q5_K_M for better)
- **Scraping Frequency:** Reduce if hitting rate limits
- **Memory Cleanup:** Archives old opportunities weekly
- **GPU Memory:** Monitor with `nvidia-smi`

---

## Security

⚠️ **Important:**
- Never commit `.env` files with secrets
- API keys stored in `~/.hermes/.env` (encrypted in Docker)
- Model safety: Qwen abliterated variant removes guardrails
- Scraping: Respect robots.txt and rate limits

---

## Next Steps

1. **Customize criteria** → Edit `hermes-skills/filter.py`
2. **Add data sources** → Update `scraper.py`
3. **Extend plan types** → Add templates to `planner.py`
4. **Monitor learning** → Check memory graph in Hermes Desktop
5. **Deploy remotely** → Run backend on home server + Desktop from anywhere

---

## Resources

- **Hermes Docs:** https://hermes-agent.nousresearch.com
- **Qwen Models:** https://huggingface.co/Qwen
- **Docker:** https://docs.docker.com
- **Model Runner:** https://docker.com/products/model-runner

---

## License

MIT - Use freely, modify as needed.

---

**Ready to discover opportunities?** 🚀

```bash
hermes desktop
```

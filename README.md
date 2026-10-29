# Momentum Trading Agent

Rule-based NSE delivery momentum system with a cost- and tax-aware backtester, plus a
layoff-resilient 60/20/20 momentum + gold + debt allocation.

- **Plan and research:** [momentum_agent/STRATEGY.md](momentum_agent/STRATEGY.md)
- **Usage and rules:** [momentum_agent/README.md](momentum_agent/README.md)

```bash
pip install -r momentum_agent/requirements.txt
python -m pytest momentum_agent/tests -q
python -m momentum_agent.cli backtest --years 10 --stop-loss 0
python -m momentum_agent.cli signals --stop-loss 0 --holdings holdings.csv
python -m momentum_agent.cli allocate --momentum 330000 --gold 110000 --debt 110000
python -m momentum_agent.research --csv-dir data_cache_long --start 2010-01-01
```

Research only, not investment advice.

"""Stop-loss sweep: how each fixed stop changes returns AND the worst single trades.

    python -m momentum_agent.stop_sweep --csv-dir data_cache_long --start 2010-01-01 --out research_out

Full-period CAGR alone hides the real question for a fixed stop: does it stop disaster trades
(overnight gaps, fraud) without selling the normal 10-15% dips that momentum winners go through?
"""
import argparse
import dataclasses
from pathlib import Path

import numpy as np
import pandas as pd

from .backtest import run_backtest
from .config import Settings, StrategyConfig
from .data import load_csv_dir, to_panel
from .research import DEBT_YIELD_PRE_TAX, SLAB_TAX, TRADING_DAYS, blend, metrics_row
from .universe import load_universe

STOPS = (None, 0.10, 0.15, 0.20, 0.25, 0.30)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv-dir", default="data_cache_long")
    p.add_argument("--start", default="2010-01-01")
    p.add_argument("--capital", type=float, default=550_000)
    p.add_argument("--out", default="research_out")
    args = p.parse_args()

    universe = set(load_universe())
    frames = load_csv_dir(args.csv_dir)
    index_close = frames["^NSEI"]["Close"]
    panel = to_panel({s: f for s, f in frames.items() if s in universe})
    nifty = index_close[index_close.index >= pd.Timestamp(args.start)]
    gold = frames["GOLDBEES"]["Close"].reindex(nifty.index).ffill()
    gold = gold / gold.iloc[0]
    debt_daily = (1 + DEBT_YIELD_PRE_TAX * (1 - SLAB_TAX)) ** (1 / TRADING_DAYS) - 1
    debt = pd.Series((1 + debt_daily) ** np.arange(len(nifty)), index=nifty.index)

    rows = []
    for stop in STOPS:
        cfg = dataclasses.replace(StrategyConfig(initial_capital=args.capital), stop_loss_pct=stop, cash_yield=0.045)
        res = run_backtest(panel, index_close, Settings(strategy=cfg), start=args.start)
        t, sleeve = res.trades, metrics_row("sleeve", res.equity, res.trades)
        mix = metrics_row("mix", blend({"eq": res.equity, "gold": gold, "debt": debt},
                                       {"eq": 0.6, "gold": 0.2, "debt": 0.2}))
        rows.append({"stop": stop or 0.0, "cagr": sleeve["cagr"], "max_dd": sleeve["max_dd"],
                     "mix_cagr": mix["cagr"], "mix_max_dd": mix["max_dd"], "trades": len(t),
                     "win_rate": (t["return"] > 0).mean(), "worst_trade": t["return"].min(),
                     "pct_loss_gt10": (t["return"] < -0.10).mean(), "n_loss_gt30": int((t["return"] < -0.30).sum())})
        print(rows[-1], flush=True)
    out = Path(args.out)
    out.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(out / "stop_sweep.csv", index=False)


if __name__ == "__main__":
    main()

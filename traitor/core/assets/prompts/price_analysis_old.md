You are given quantitative time-series feature summaries for a cryptocurrency. 
The data is organized by timeframe: year, month, week, day, hour. 
Each timeframe contains a dictionary of numeric features (statistical, trend, volatility, autocorrelation, frequency, complexity). 
Use only the provided numbers. Do not add external knowledge, price history, or assumptions.

Tasks:
1. Summarize the price behavior for each timeframe. Identify trend direction, volatility, momentum, distribution shape, and regime signals. 
2. Reconcile all timeframes into a unified narrative of recent market behavior. 
3. Produce a short-term outlook (next 24–72h) using only the short-window features (day, hour). Indicate trend bias, volatility expectation, and likelihood of continuation/reversal.
4. Produce a long-term outlook (next weeks–months) using only long-window features (week, month, year). Indicate structural trend, risk, and expected drift direction.
5. Flag anomalies: extreme skewness, kurtosis spikes, volatility breaks, autocorrelation regimes, frequency-domain abnormalities, entropy changes, and strike patterns.
6. Keep analysis compact, deterministic, and strictly data-driven. No storytelling. No speculation. No outside market facts.


Output format:
{
  "summary_by_timeframe": {...},
  "cross_timeframe_interpretation": "...",
  "short_term_prediction": "...",
  "long_term_prediction": "...",
  "anomaly_flags": [...]
}

INPUT:

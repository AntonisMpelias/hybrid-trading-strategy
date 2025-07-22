# A hybrid regime switching trading strategy with an adaptive kill-switch
A trading algorithm strategy that uses momentum, SMAs, Mean reversion, a kill switch based on Volatility, dynamic position sizing and realistic fees and slippage. 


## Key Features

- SMA and mean-reversion strategy switching via volatility + momentum
- Kill switch to mitigate catastrophic drawdowns
- Dynamic position sizing based on recent volatility
- Risk management with slippage and fees

### Top Backtest Results  (Adaptive Kill Switch)

All results assume a starting capital of **$10,000**, with realistic transaction costs (0.15%) and 5% capital allocation per trade.

- **TSLA (2019–2025):**
  
  **Final Portfolio: $241,174.76 - a +2,311.7% gain.**  

  **Buy & Hold: $195,330.83**

  **Sharpe Ratio:** 1.45 **Sortino Ratio:** 1.19

The algorithm rode Tesla’s extreme volatility without flinching, outperforming Buy & Hold by nearly 25%.
  
- **INTEL stock (2019-2025):**

  **Final Portfolio: $8,482.58 - a -15% loss.**   

  **Buy & Hold: $4,948.41**

  **Sharpe Ratio:** 0.03 **Sortino Ratio:** 0.02

The algorithm mitigated losses through tight trade filters in a falling long-term trend.

- **AIG stock (2007-2011)(Crash):**

  **Final Portfolio: $10,981.36 - a +9.8% gain.**   

  **Buy & Hold: $245.70 (a -98% loss)**

  **Sharpe Ratio:** 0.22 **Sortino Ratio:** 0.15

The algorithm exited early and protected capital, turning a disaster into a modest profit.

- **United Airlines stock (2006-2011):**

  **Final Portfolio: $39,916.22 - a +299% gain.**   

  **Buy & Hold: $7,513.87**
    **Sharpe Ratio:** 0.91 **Sortino Ratio:** 0.73

Smart entries and exits let the algorithm thrive in volatile recovery cycles.
  
- **Peloton stock (2020-2025):**

  **Final Portfolio: $11,906.19 - a +19.1% gain.**   

  **Buy & Hold: $2,925.35**

  **Sharpe Ratio:** 0.33 **Sortino Ratio:** 0.24

The algorithm cut losses fast, skipped the bubble pop, and stayed profitable in a high-risk environment.






    

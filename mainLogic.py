import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1) Downloading Historical Data for backtesting
df = yf.download('TSLA', start='2019-01-01', end='2025-01-01')

# ===== 2. Calculate Indicators =====
df['Returns'] = df['Close'].pct_change()
df['SMA_30'] = df['Close'].rolling(window=30).mean()
df['SMA_7'] = df['Close'].rolling(window=7).mean()
df['Momentum'] = df['Close'] - df['Close'].shift(30)  # CORRECTED
df['Volatility'] = df['Returns'].rolling(window=30).std()
df['Z-score'] = (df['Close'] - df['Close'].rolling(30).mean()) / df['Close'].rolling(30).std()

# ===== 3. Hybrid Signal Logic =====
# Calculate volatility threshold (median of historical volatility)
df['Vol_Threshold'] = df['Volatility'].rolling(30).median()

# Initialize signals
df['SMA_Signal'] = np.where(df['SMA_7'] > df['SMA_30'], 1, 0)
df['MR_Signal'] = np.where(df['Z-score'] < -2, 1, np.where(df['Z-score'] > 2, -1, 0))

# HYBRID SWITCHING LOGIC 
conditions = [
    df['Volatility'] < df['Vol_Threshold'],  # Low volatility -> SMA
    (df['Volatility'] >= df['Vol_Threshold']) & (df['Momentum'] > 0),  # Volatile but trending -> SMA
    (df['Volatility'] >= df['Vol_Threshold']) & (df['Momentum'] <= 0),  # Volatile + no trend -> MR
    (df['Volatility'] <= df['Vol_Threshold']) & (df['Momentum'] <= 0)  # Low vol + no trend -> direct short position
]

choices = [
    df['SMA_Signal'],  # Low vol -> SMA
    df['SMA_Signal'],  # Volatile but trending -> SMA
    df['MR_Signal'],    # Volatile + no trend -> MR
    -1  # Low vol + no trend -> direct short position
]

df['Signal'] = np.select(conditions, choices, default=0)

# 4) Apply killswitch BEFORE returns and portfolio calc
investment = 10000
risk_per_trade = 0.05
fee = 0.0005
slippage = 0.001

# Modified Kill Switch Trigger
def dynamic_kill_switch(df):
    temp_returns = df['Returns'] * df['Signal'].shift(1)
    temp_portfolio = (1 + temp_returns.fillna(0)).cumprod()
    temp_dd = temp_portfolio / temp_portfolio.cummax() - 1
    
    # Only trigger in high volatility + downtrend
    high_vol = df['Volatility'] > df['Vol_Threshold']
    downtrend = df['Momentum'] < 0
    dd_breach = temp_dd < -0.15
    
    return dd_breach & high_vol & downtrend  # All 3 conditions required

df['KillSwitch'] = dynamic_kill_switch(df)
df['Signal'] = np.where(df['KillSwitch'], 0, df['Signal'])  # Override signal to flat if kill switch triggered

# 5) Position sizing and returns calculation 
df['Daily_Vol'] = df['Returns'].rolling(30).std().shift(1)
df['Position_Size'] = risk_per_trade / df['Daily_Vol'].replace(0, 0.001)
df['Position_Size'] = df['Position_Size'].clip(upper=1)

trade_returns = df['Returns'] * df['Signal'].shift(1) * df['Position_Size'].shift(1)
costs = (fee + slippage) * np.abs(df['Signal'].diff())
df['Returns_Strategy'] = trade_returns - costs
df['Portfolio_Value'] = investment * (1 + df['Returns_Strategy']).cumprod()

# Drawdown for reporting (not used for killswitch here)
df['Drawdown'] = df['Portfolio_Value'] / df['Portfolio_Value'].cummax() - 1

# Annualized metrics
rets = df['Returns_Strategy'].dropna()
annualized_return = rets.mean() * 252
annualized_vol    = rets.std() * np.sqrt(252)
sharpe_ratio      = annualized_return / annualized_vol if annualized_vol else np.nan

# Percentage gain
initial_value = investment
final_value   = df['Portfolio_Value'].iloc[-1]
pct_gain      = (final_value / initial_value - 1) * 100

# Sortino ratio
downside = df['Returns_Strategy'][df['Returns_Strategy'] < 0]
down_vol   = np.sqrt((downside**2).mean() * 252)
sortino    = annualized_return / down_vol if down_vol else np.nan

# --- 6. Results and plotting ---
print(f"Final Portfolio Value: ${df['Portfolio_Value'].iloc[-1]:,.2f}")
BuyAndHoldProfits = (investment * (df['Close'].iloc[-1] / df['Close'].iloc[0]))
BuyAndHoldProfits = BuyAndHoldProfits.apply(lambda x: f"${x:,.2f}")
print(f"Buy-and-Hold Strategy Value: ${BuyAndHoldProfits.iloc[-1]}")

plt.figure(figsize=(14, 12))
plt.subplot(2, 1, 1)
plt.plot(df['Close'], label='Price', color='green')
plt.title("Price")
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.legend()
plt.grid()

ax2= plt.subplot(2, 1, 2)
plt.plot(df['Portfolio_Value'], label='Strategy', color='black')
plt.plot(df['Close'] / df['Close'].iloc[0] * investment, label='Buy & Hold', color='blue')
plt.title('Portfolio Value')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.legend()
plt.grid()

textstr = (
    f"Sharpe: {sharpe_ratio:.2f}\n"
    f"Sortino: {sortino:.2f}\n"
    f"Gain: {pct_gain:.1f}%"
)

ax2.text(
    0.5, 0.95, textstr,
    transform=ax2.transAxes,
    ha='center', va='top',
    fontsize=10,
    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
)

plt.tight_layout()
plt.show()

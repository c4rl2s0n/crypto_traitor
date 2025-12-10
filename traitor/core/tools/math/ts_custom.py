import numpy as np
from sklearn.linear_model import LinearRegression

def returns(prices):
    prices = np.asarray(prices)
    return float((prices[-1] / prices[0]) - 1)


def slope(prices):
    y = np.asarray(prices)
    x = np.arange(len(y)).reshape(-1, 1)
    model = LinearRegression()
    model.fit(x, y)
    return float(model.coef_[0])


def volatility_regime(prices_short, prices_long):
    vol_short = np.std(prices_short)
    vol_long = np.std(prices_long)
    return float((vol_short - vol_long) / vol_long)


def max_drawdown(prices):
    arr = np.asarray(prices)
    peak = np.maximum.accumulate(arr)
    dd = (arr - peak) / peak
    return float(dd.min())


def distance_from_high_low(prices):
    current = prices[-1]
    high = max(prices)
    low = min(prices)
    return {
        "pct_from_high": float((current - high) / high),
        "pct_from_low": float((current - low) / low),
    }


def volatility_trend(prices):
    window = len(prices) // 2
    vol1 = np.std(prices[:window])
    vol2 = np.std(prices[window:])
    return float(vol2 - vol1)



def volume_trend(volume_short, volume_long):
    vol_short_mean = np.mean(volume_short)
    vol_long_mean  = np.mean(volume_long)
    return float((vol_short_mean - vol_long_mean) / vol_long_mean)

# def volume_trend(volume):
#     return slope(volume)


def avg_volume(volume):
    return float(np.mean(volume))

def min_volume(volume):
    return float(np.min(volume))

def max_volume(volume):
    return float(np.max(volume))
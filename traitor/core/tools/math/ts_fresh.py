from datetime import datetime

import pandas as pd
from tsfresh import extract_features
from tsfresh.feature_extraction import ComprehensiveFCParameters

from traitor.core.data.models.price_feature import PriceFeature, PriceFeatureInterval

fc = {
    # --- distribution ---
    "mean": None,
    "median": None,
    "standard_deviation": None,
    "variance": None,
    "skewness": None,
    "kurtosis": None,
    "maximum": None,
    "minimum": None,
    "quantile": [
        {"q": 0.1},
        {"q": 0.5},
        {"q": 0.9},
    ],

    # --- amplitude / energy ---
    "root_mean_square": None,
    "abs_energy": None,
    "mean_abs_change": None,

    # --- temporal shape ---
    "mean_change": None,
    "mean_second_derivative_central": None,

    # --- autocorrelation ---
    "autocorrelation": [
        {"lag": 1},
        {"lag": 2},
        {"lag": 3},
    ],
    "partial_autocorrelation": [
        {"lag": 1},
        {"lag": 2},
        {"lag": 3},
    ],
    "agg_autocorrelation": [
        {"f_agg": "mean", "maxlag": 3},
        {"f_agg": "median", "maxlag": 3},
    ],

    # --- peaks / structure ---
    "number_peaks": [
        {"n": 1},
        {"n": 3},
        {"n": 5},
    ],
    "number_cwt_peaks": [
        {"n": 1},
    ],

    # --- frequency ---
    "fft_coefficient": [
        {"coeff": 1, "attr": "real"},
        {"coeff": 1, "attr": "imag"},
        {"coeff": 1, "attr": "abs"},
        {"coeff": 2, "attr": "real"},
        {"coeff": 2, "attr": "imag"},
        {"coeff": 2, "attr": "abs"},
        {"coeff": 3, "attr": "real"},
        {"coeff": 3, "attr": "imag"},
        {"coeff": 3, "attr": "abs"},
        {"coeff": 4, "attr": "real"},
        {"coeff": 4, "attr": "imag"},
        {"coeff": 4, "attr": "abs"},
        {"coeff": 5, "attr": "real"},
        {"coeff": 5, "attr": "imag"},
        {"coeff": 5, "attr": "abs"},
    ],
    "spkt_welch_density": [
        {"coeff": 2},
        {"coeff": 5},
    ],

    # --- complexity ---
    "sample_entropy": None,
    "cid_ce": [
        {"normalize": True},
    ],

    # --- dynamic / nonlinear ---
    "time_reversal_asymmetry_statistic": [
        {"lag": 1},
    ],
    "c3": [
        {"lag": 1},
    ],

    # --- strike features ---
    "longest_strike_below_mean": None,
    "longest_strike_above_mean": None,

    # --- index mass ---
    "index_mass_quantile": [
        {"q": 0.1},
        {"q": 0.5},
        {"q": 0.9},
    ],
}



def extract_price_features(
        prices: pd.DataFrame,
        interval: PriceFeatureInterval = PriceFeatureInterval.ALL
) -> dict[int, PriceFeature]:
    """
    Should extract these features:

    1. **Volatility/Dispersion**
       * `standard_deviation`
       * `variance`
       * `mean_abs_change`
       * `absolute_sum_of_changes`
         These map directly to realized volatility and short-term turbulence.
    2. **Momentum / Trend**
       * `linear_trend.slope`
       * `linear_trend.intercept`
       * `agg_linear_trend`
       * `mean_change`
         Aligns with momentum, drift, and local trend strength.
    3. **Stationarity / Regime**
       * `augmented_dickey_fuller`
       * `unitroot_kpss`
         Detect regime changes and mean-reversion vs trending phases.
    4. **Distributional Shape**
       * `skewness`
       * `kurtosis`
         Captures asymmetry and tail risk.
    5. **Autocorrelation**
       * `autocorrelation(lag=X)`
       * `partial_autocorrelation(lag=X)`
         Short-lag autocorr is often the only useful part; high-lag features are noise.
    6. **Fourier / Frequency**
       * `fft_coefficient`
       * `fft_aggregated`
         Useful for periodicity in intraday data, weak for daily equities.
    7. **Peak / Drop Dynamics**
       * `maximum`
       * `minimum`
       * `longest_strike_above_mean`
       * `longest_strike_below_mean`
         Detect breakout/breakdown behaviors.

        :param interval:
        :param prices:
        :return:
        """

    features = extract_features(
        prices,
        column_id="coin_id",
        column_sort="time",
        column_value="value",
        default_fc_parameters=fc
    )
    feature_dict = features.to_dict(orient="index")
    price_features: dict[int, PriceFeature] = {}
    for coin_id in prices.coin_id.unique():
        coin_features = feature_dict[coin_id]

        df_id = prices[prices['coin_id'] == coin_id]
        start = df_id['time'].min()
        end = df_id['time'].max()
        pf = PriceFeature(
            coin_id = int(coin_id),
            start = start,
            end = end,
            interval = interval,
            mean = float(coin_features['value__mean']),
            median = float(coin_features['value__median']),
            standard_deviation = float(coin_features['value__standard_deviation']),
            # variance = float(coin_features['value__variance']),
            skewness = float(coin_features['value__skewness']),
            kurtosis = float(coin_features['value__kurtosis']),
            maximum = float(coin_features['value__maximum']),
            minimum = float(coin_features['value__minimum']),
            quantile__q_0_1 = float(coin_features['value__quantile__q_0.1']),
            quantile__q_0_5 = float(coin_features['value__quantile__q_0.5']),
            quantile__q_0_9 = float(coin_features['value__quantile__q_0.9']),
            # root_mean_square = float(coin_features['value__root_mean_square']),
            # abs_energy = float(coin_features['value__abs_energy']),
            mean_abs_change = float(coin_features['value__mean_abs_change']),
            mean_change = float(coin_features['value__mean_change']),
            # mean_second_derivative_central = float(coin_features['value__mean_second_derivative_central']),
            autocorrelation__lag_1 = float(coin_features['value__autocorrelation__lag_1']),
            # autocorrelation__lag_2 = float(coin_features['value__autocorrelation__lag_2']),
            # autocorrelation__lag_3 = float(coin_features['value__autocorrelation__lag_3']),
            # partial_autocorrelation__lag_1 = float(coin_features['value__partial_autocorrelation__lag_1']),
            # partial_autocorrelation__lag_2 = float(coin_features['value__partial_autocorrelation__lag_2']),
            # partial_autocorrelation__lag_3 = float(coin_features['value__partial_autocorrelation__lag_3']),
            # agg_autocorrelation__f_agg_mean_maxlag_3 = float(coin_features['value__agg_autocorrelation__f_agg_"mean"__maxlag_3']),
            # agg_autocorrelation__f_agg_median_maxlag_3 = float(coin_features['value__agg_autocorrelation__f_agg_"median"__maxlag_3']),
            # number_peaks__n_1 = float(coin_features['value__number_peaks__n_1']),
            # number_peaks__n_3 = float(coin_features['value__number_peaks__n_3']),
            # number_peaks__n_5 = float(coin_features['value__number_peaks__n_5']),
            number_cwt_peaks__n_1 = float(coin_features['value__number_cwt_peaks__n_1']),
            # fft_coefficient__attr_real__coeff_1 = float(coin_features['value__fft_coefficient__attr_"real"__coeff_1']),
            # fft_coefficient__attr_imag__coeff_1 = float(coin_features['value__fft_coefficient__attr_"imag"__coeff_1']),
            # fft_coefficient__attr_abs__coeff_1 = float(coin_features['value__fft_coefficient__attr_"abs"__coeff_1']),
            # fft_coefficient__attr_real__coeff_2 = float(coin_features['value__fft_coefficient__attr_"real"__coeff_2']),
            # fft_coefficient__attr_imag__coeff_2 = float(coin_features['value__fft_coefficient__attr_"imag"__coeff_2']),
            # fft_coefficient__attr_abs__coeff_2 = float(coin_features['value__fft_coefficient__attr_"abs"__coeff_2']),
            # fft_coefficient__attr_real__coeff_3 = float(coin_features['value__fft_coefficient__attr_"real"__coeff_3']),
            # fft_coefficient__attr_imag__coeff_3 = float(coin_features['value__fft_coefficient__attr_"imag"__coeff_3']),
            # fft_coefficient__attr_abs__coeff_3 = float(coin_features['value__fft_coefficient__attr_"abs"__coeff_3']),
            # fft_coefficient__attr_real__coeff_4 = float(coin_features['value__fft_coefficient__attr_"real"__coeff_4']),
            # fft_coefficient__attr_imag__coeff_4 = float(coin_features['value__fft_coefficient__attr_"imag"__coeff_4']),
            # fft_coefficient__attr_abs__coeff_4 = float(coin_features['value__fft_coefficient__attr_"abs"__coeff_4']),
            # fft_coefficient__attr_real__coeff_5 = float(coin_features['value__fft_coefficient__attr_"real"__coeff_5']),
            # fft_coefficient__attr_imag__coeff_5 = float(coin_features['value__fft_coefficient__attr_"imag"__coeff_5']),
            # fft_coefficient__attr_abs__coeff_5 = float(coin_features['value__fft_coefficient__attr_"abs"__coeff_5']),
            # spkt_welch_density__coeff_2 = float(coin_features['value__spkt_welch_density__coeff_2']),
            # spkt_welch_density__coeff_5 = float(coin_features['value__spkt_welch_density__coeff_5']),
            sample_entropy = float(coin_features['value__sample_entropy']),
            # cid_ce__normalize_True = float(coin_features['value__cid_ce__normalize_True']),
            # time_reversal_asymmetry_statistic__lag_1 = float(coin_features['value__time_reversal_asymmetry_statistic__lag_1']),
            # c3__lag_1 = float(coin_features['value__c3__lag_1']),
            longest_strike_below_mean = float(coin_features['value__longest_strike_below_mean']),
            longest_strike_above_mean = float(coin_features['value__longest_strike_above_mean']),
            # index_mass_quantile__q_0_1 = float(coin_features['value__index_mass_quantile__q_0.1']),
            # index_mass_quantile__q_0_5 = float(coin_features['value__index_mass_quantile__q_0.5']),
            # index_mass_quantile__q_0_9 = float(coin_features['value__index_mass_quantile__q_0.9']),
        )
        price_features[coin_id] = pf
    return price_features

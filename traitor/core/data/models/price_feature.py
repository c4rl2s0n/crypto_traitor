import enum

from sqlalchemy import Column, Float, Integer, DateTime, Enum, String, ForeignKey
from sqlalchemy.orm import relationship

from traitor.core.data import Base

class PriceFeatureInterval(enum.Enum):
    ALL = "all_time",
    YEAR = "year",
    QUARTER = "quarter",
    MONTH = "month",
    WEEK = "week",
    DAY = "day",
    HOUR = "hour",

class PriceFeature(Base):
    __tablename__ = "price_features"
    coin_id = Column(Integer, ForeignKey('coins.id', ondelete="CASCADE"), primary_key=True)
    interval = Column(Enum(PriceFeatureInterval), primary_key=True)
    start = Column(DateTime, index=True, nullable=True)
    end = Column(DateTime, index=True, nullable=True)

    mean = Column(Float)
    median = Column(Float)
    standard_deviation = Column(Float)
    variance = Column(Float)
    skewness = Column(Float)
    kurtosis = Column(Float)
    maximum = Column(Float)
    minimum = Column(Float)
    quantile__q_0_1 = Column(Float)
    quantile__q_0_5 = Column(Float)
    quantile__q_0_9 = Column(Float)
    root_mean_square = Column(Float)
    abs_energy = Column(Float)
    mean_abs_change = Column(Float)
    mean_change = Column(Float)
    mean_second_derivative_central = Column(Float)
    autocorrelation__lag_1 = Column(Float)
    autocorrelation__lag_2 = Column(Float)
    autocorrelation__lag_3 = Column(Float)
    partial_autocorrelation__lag_1 = Column(Float)
    partial_autocorrelation__lag_2 = Column(Float)
    partial_autocorrelation__lag_3 = Column(Float)
    agg_autocorrelation__f_agg_mean_maxlag_3 = Column(Float)
    agg_autocorrelation__f_agg_median_maxlag_3 = Column(Float)
    number_peaks__n_1 = Column(Float)
    number_peaks__n_3 = Column(Float)
    number_peaks__n_5 = Column(Float)
    number_cwt_peaks__n_1 = Column(Float)
    fft_coefficient__attr_real__coeff_1 = Column(Float)
    fft_coefficient__attr_imag__coeff_1 = Column(Float)
    fft_coefficient__attr_abs__coeff_1 = Column(Float)
    fft_coefficient__attr_real__coeff_2 = Column(Float)
    fft_coefficient__attr_imag__coeff_2 = Column(Float)
    fft_coefficient__attr_abs__coeff_2 = Column(Float)
    fft_coefficient__attr_real__coeff_3 = Column(Float)
    fft_coefficient__attr_imag__coeff_3 = Column(Float)
    fft_coefficient__attr_abs__coeff_3 = Column(Float)
    fft_coefficient__attr_real__coeff_4 = Column(Float)
    fft_coefficient__attr_imag__coeff_4 = Column(Float)
    fft_coefficient__attr_abs__coeff_4 = Column(Float)
    fft_coefficient__attr_real__coeff_5 = Column(Float)
    fft_coefficient__attr_imag__coeff_5 = Column(Float)
    fft_coefficient__attr_abs__coeff_5 = Column(Float)
    spkt_welch_density__coeff_2 = Column(Float)
    spkt_welch_density__coeff_5 = Column(Float)
    sample_entropy = Column(Float)
    cid_ce__normalize_True = Column(Float)
    time_reversal_asymmetry_statistic__lag_1 = Column(Float)
    c3__lag_1 = Column(Float)
    longest_strike_below_mean = Column(Float)
    longest_strike_above_mean = Column(Float)
    index_mass_quantile__q_0_1 = Column(Float)
    index_mass_quantile__q_0_5 = Column(Float)
    index_mass_quantile__q_0_9 = Column(Float)

    def to_dict(self) -> dict:
        return {
            "mean": self.mean,
            "median": self.median,
            "standard_deviation": self.standard_deviation,
            "variance": self.variance,
            "skewness": self.skewness,
            "kurtosis": self.kurtosis,
            "maximum": self.maximum,
            "minimum": self.minimum,
            "quantile__q_0_1": self.quantile__q_0_1,
            "quantile__q_0_5": self.quantile__q_0_5,
            "quantile__q_0_9": self.quantile__q_0_9,
            "root_mean_square": self.root_mean_square,
            "abs_energy": self.abs_energy,
            "mean_abs_change": self.mean_abs_change,
            "mean_change": self.mean_change,
            "mean_second_derivative_central": self.mean_second_derivative_central,
            "autocorrelation__lag_1": self.autocorrelation__lag_1,
            "autocorrelation__lag_2": self.autocorrelation__lag_2,
            "autocorrelation__lag_3": self.autocorrelation__lag_3,
            "partial_autocorrelation__lag_1": self.partial_autocorrelation__lag_1,
            "partial_autocorrelation__lag_2": self.partial_autocorrelation__lag_2,
            "partial_autocorrelation__lag_3": self.partial_autocorrelation__lag_3,
            "agg_autocorrelation__f_agg_mean_maxlag_3": self.agg_autocorrelation__f_agg_mean_maxlag_3,
            "agg_autocorrelation__f_agg_median_maxlag_3": self.agg_autocorrelation__f_agg_median_maxlag_3,
            "number_peaks__n_1": self.number_peaks__n_1,
            "number_peaks__n_3": self.number_peaks__n_3,
            "number_peaks__n_5": self.number_peaks__n_5,
            "number_cwt_peaks__n_1": self.number_cwt_peaks__n_1,
            "fft_coefficient__attr_real__coeff_1": self.fft_coefficient__attr_real__coeff_1,
            "fft_coefficient__attr_imag__coeff_1": self.fft_coefficient__attr_imag__coeff_1,
            "fft_coefficient__attr_abs__coeff_1": self.fft_coefficient__attr_abs__coeff_1,
            "fft_coefficient__attr_real__coeff_2": self.fft_coefficient__attr_real__coeff_2,
            "fft_coefficient__attr_imag__coeff_2": self.fft_coefficient__attr_imag__coeff_2,
            "fft_coefficient__attr_abs__coeff_2": self.fft_coefficient__attr_abs__coeff_2,
            "fft_coefficient__attr_real__coeff_3": self.fft_coefficient__attr_real__coeff_3,
            "fft_coefficient__attr_imag__coeff_3": self.fft_coefficient__attr_imag__coeff_3,
            "fft_coefficient__attr_abs__coeff_3": self.fft_coefficient__attr_abs__coeff_3,
            "fft_coefficient__attr_real__coeff_4": self.fft_coefficient__attr_real__coeff_4,
            "fft_coefficient__attr_imag__coeff_4": self.fft_coefficient__attr_imag__coeff_4,
            "fft_coefficient__attr_abs__coeff_4": self.fft_coefficient__attr_abs__coeff_4,
            "fft_coefficient__attr_real__coeff_5": self.fft_coefficient__attr_real__coeff_5,
            "fft_coefficient__attr_imag__coeff_5": self.fft_coefficient__attr_imag__coeff_5,
            "fft_coefficient__attr_abs__coeff_5": self.fft_coefficient__attr_abs__coeff_5,
            "spkt_welch_density__coeff_2": self.spkt_welch_density__coeff_2,
            "spkt_welch_density__coeff_5": self.spkt_welch_density__coeff_5,
            "sample_entropy": self.sample_entropy,
            "cid_ce__normalize_True": self.cid_ce__normalize_True,
            "time_reversal_asymmetry_statistic__lag_1": self.time_reversal_asymmetry_statistic__lag_1,
            "c3__lag_1": self.c3__lag_1,
            "longest_strike_below_mean": self.longest_strike_below_mean,
            "longest_strike_above_mean": self.longest_strike_above_mean,
            "index_mass_quantile__q_0_1": self.index_mass_quantile__q_0_1,
            "index_mass_quantile__q_0_5": self.index_mass_quantile__q_0_5,
            "index_mass_quantile__q_0_9": self.index_mass_quantile__q_0_9,
        }

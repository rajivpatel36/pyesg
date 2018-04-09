import numpy as np

from scipy.stats import norm
from typing import Tuple

from pyesg.configuration.validation_configuration import ValidationAnalysis


def get_confidence_level(analysis_settings: ValidationAnalysis, default: float=0.95):
    """
    Returns the confidence level from analysis settings if specified; otherwise returns the default value.
    Args:
        analysis_settings: The analysis settings.
        default: The default value for the confidence level if it is not specified.

    Returns:
        The confidence level for the analysis.
    """
    return getattr(analysis_settings.parameters, "confidence_level", default)


def do_sample_mean_and_confidence_interval_calculations(array: np.ndarray, confidence_level: float,
                                                        annualisation_factor: float) -> dict:
    """
    Calculates sample mean and confidence intervals for each time step in an array of simulations.
    Args:
        array: The array of simulations where rows are simulations and columns are time steps.
        confidence_level: The confidence level to use when determining confidence intervals
        annualisation_factor: The annualisation factor for projection steps - the number of steps per year.

    Returns:
        The sample mean, lower confidence interval and upper confidence interval for each time step in the array.

    The `array` argument has shape (number of simulations, number of time steps).
    A tuple is returned of the form (sample_mean, lower_confidence_interval, upper_confidence_interval).
    """
    sample_mean = array.mean(axis=0)  # Sample mean for each time step.
    number_sims, number_steps = array.shape
    stdev = np.sqrt(array.var(axis=0, ddof=1))  # Sample st dev for each time step. ddof=1 so unbiased estimator.

    z = norm.ppf(1.0 - 0.5 * (1.0 - confidence_level))  # Inverse CDF for confidence level. Two-tailed interval.

    upper_confidence_interval = sample_mean + z * stdev / np.sqrt(number_sims)
    lower_confidence_interval = sample_mean - z * stdev / np.sqrt(number_sims)

    time = np.arange(number_steps) / annualisation_factor  # Projection times in years.

    return {
        'time': time.tolist(),
        'sample_mean': sample_mean.tolist(),
        'upper_confidence_interval': upper_confidence_interval.tolist(),
        'lower_confidence_interval': lower_confidence_interval.tolist(),
    }

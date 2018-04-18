import numpy as np

from pyesg.configuration.validation_configuration import ValidationAnalysis
from pyesg.constants.outputs import DISCOUNT_FACTOR
from pyesg.constants.validation_analyses import AVERAGE_DISCOUNT_FACTOR
from pyesg.constants.validation_result_types import MARTINGALE
from pyesg.simulation.utils import extract_yield_curve_from_parameters
from pyesg.validation.utils import get_confidence_level, do_sample_mean_and_confidence_interval_calculations
from pyesg.validation.validators.base_validator import BaseValidator


class AverageDiscountFactorValidator(BaseValidator):
    """
    Performs discounted TRI martingale analysis.
    """
    analysis_id = AVERAGE_DISCOUNT_FACTOR
    result_type = MARTINGALE

    def _validate(self, analysis_settings: ValidationAnalysis):
        confidence_level = get_confidence_level(analysis_settings)

        # Start from time step 1 because time step 0 is determinstic and there is no yield associated with it.
        time_steps = np.arange(1, self._data_extractor.reader.number_of_time_steps)
        discount_factor_sims = self._data_extractor.get_output_simulations(self._asset_class, DISCOUNT_FACTOR, time_steps)

        # Get sample mean and upper and lower confidence intervals
        results = do_sample_mean_and_confidence_interval_calculations(
            array=discount_factor_sims,
            confidence_level=confidence_level,
            annualisation_factor=self._data_extractor.reader.annualisation_factor
        )
        # Expected values are points on initial yield curve
        yield_curve = extract_yield_curve_from_parameters(self._asset_class.parameters)
        expected_values = [yield_curve.get_rate(i / self._data_extractor.reader.annualisation_factor)
                           for i in np.arange(1, self._data_extractor.reader.number_of_time_steps)]

        # Transform results from bond prices to yields
        # Don't use "time" key in results because this is constructed assuming time starts at 0
        sample_mean = np.asarray(results["sample_mean"])
        lower_ci = np.asarray(results["lower_confidence_interval"])
        upper_ci = np.asarray(results["upper_confidence_interval"])

        def price_to_yield(time, price) -> np.ndarray:
            return - np.log(price) / time

        # Note that the inverse relationship between bond price and yield means the upper confidence interval for the
        # prices corresponds to the lower confidence interval for the yield (and similarly, lower confidence interval
        # for prices corresponds to upper confidence interval for the yield)
        return {
            "time": time_steps.tolist(),
            "sample_mean": price_to_yield(time_steps, sample_mean).tolist(),
            "lower_confidence_interval": price_to_yield(time_steps, upper_ci).tolist(),
            "upper_confidence_interval": price_to_yield(time_steps, lower_ci).tolist(),
            "expected_value": expected_values
        }

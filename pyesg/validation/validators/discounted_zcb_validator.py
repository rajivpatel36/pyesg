import numpy as np

from pyesg.configuration.validation_configuration import ValidationAnalysis
from pyesg.constants.outputs import DISCOUNT_FACTOR, ZERO_COUPON_BOND
from pyesg.constants.validation_analyses import DISCOUNTED_ZCB
from pyesg.constants.validation_result_types import MARTINGALE
from pyesg.simulation.utils import extract_yield_curve_from_parameters
from pyesg.validation.utils import get_confidence_level, do_sample_mean_and_confidence_interval_calculations
from pyesg.validation.validators.base_validator import BaseValidator
from pyesg.yield_curve.yield_curve import YieldCurve


class DiscountedZCBValidator(BaseValidator):
    """
    Performs discounted ZCB validation analysis.

    The expected value of the discounted ZCB (term T) at time s is the point on the initial yield curve for term s +T.
    """
    analysis_id = DISCOUNTED_ZCB
    result_type = MARTINGALE

    def _validate(self, analysis_settings: ValidationAnalysis):
        confidence_level = get_confidence_level(analysis_settings)
        terms = getattr(analysis_settings.parameters, "terms", [])
        yield_curve = extract_yield_curve_from_parameters(self._asset_class.parameters)
        return [self._validate_single_term(confidence_level, term, yield_curve) for term in terms]

    def _validate_single_term(self, confidence_level: float, term: float, yield_curve: YieldCurve):
        time_steps = np.arange(1, self._data_extractor.reader.number_of_time_steps)
        # No need to worry about repeatedly getting discount factor sims as it gets cached
        discount_factor_sims = self._data_extractor.get_output_simulations(
            asset_class=self._asset_class,
            output_type=DISCOUNT_FACTOR,
            time_step=time_steps
        )
        zcb_sims = self._data_extractor.get_output_simulations(
            asset_class=self._asset_class,
            output_type=ZERO_COUPON_BOND,
            time_step=time_steps,
            term=term
        )

        discounted_zcb_sims = discount_factor_sims * zcb_sims

        # Get sample mean and upper and lower confidence intervals
        results = do_sample_mean_and_confidence_interval_calculations(
            array=discounted_zcb_sims,
            confidence_level=confidence_level,
            annualisation_factor=self._data_extractor.reader.annualisation_factor
        )

        # Expected values are points on initial yield curve. The point at time t is the rate for term (t+ zcb_term)
        expected_values = [yield_curve.get_rate(i / self._data_extractor.reader.annualisation_factor + term)
                           for i in np.arange(1, self._data_extractor.reader.number_of_time_steps)]

        # Transform results from bond prices to yields
        # Don't use "time" key in results because this is constructed assuming time starts at 0
        sample_mean = np.asarray(results["sample_mean"])
        lower_ci = np.asarray(results["lower_confidence_interval"])
        upper_ci = np.asarray(results["upper_confidence_interval"])

        def price_to_yield(time, price) -> np.ndarray:
            return - np.log(price) / (time + term)  #(time + term) because it should correspond to term (t + zcb_term)

        # Note that the inverse relationship between bond price and yield means the upper confidence interval for the
        # prices corresponds to the lower confidence interval for the yield (and similarly, lower confidence interval
        # for prices corresponds to upper confidence interval for the yield)
        return {
            "term": term,
            "time": time_steps.tolist(),
            "sample_mean": price_to_yield(time_steps, sample_mean).tolist(),
            "lower_confidence_interval": price_to_yield(time_steps, upper_ci).tolist(),
            "upper_confidence_interval": price_to_yield(time_steps, lower_ci).tolist(),
            "expected_value": expected_values
        }

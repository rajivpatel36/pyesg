import numpy as np

from pyesg.configuration.validation_configuration import ValidationAnalysis
from pyesg.constants.outputs import DISCOUNT_FACTOR, BOND_INDEX
from pyesg.constants.validation_analyses import DISCOUNTEd_BOND_INDEX
from pyesg.constants.validation_result_types import MARTINGALE
from pyesg.simulation.utils import extract_yield_curve_from_parameters
from pyesg.validation.utils import get_confidence_level, do_sample_mean_and_confidence_interval_calculations
from pyesg.validation.validators.base_validator import BaseValidator
from pyesg.yield_curve.yield_curve import YieldCurve


class DiscountedBondIndexValidator(BaseValidator):
    """
    Performs discounted bond index validation analysis.

    The expected value of the discounted bond index is its initial value (which is 1).
    """
    analysis_id = DISCOUNTEd_BOND_INDEX
    result_type = MARTINGALE

    def _validate(self, analysis_settings: ValidationAnalysis):
        confidence_level = get_confidence_level(analysis_settings)
        terms = getattr(analysis_settings.parameters, "terms", [])
        return [self._validate_single_term(confidence_level, term) for term in terms]

    def _validate_single_term(self, confidence_level: float, term: float):
        discount_factor_sims = self._data_extractor.get_output_simulations(
            asset_class=self._asset_class,
            output_type=DISCOUNT_FACTOR,
        )
        bond_index_sims = self._data_extractor.get_output_simulations(
            asset_class=self._asset_class,
            output_type=BOND_INDEX,
            term=term
        )

        discounted_bond_index_sims = discount_factor_sims * bond_index_sims

        # Get sample mean and upper and lower confidence intervals
        results = do_sample_mean_and_confidence_interval_calculations(
            array=discounted_bond_index_sims,
            confidence_level=confidence_level,
            annualisation_factor=self._data_extractor.reader.annualisation_factor
        )

        # Expected value is just 1.
        expected_values = np.full(self._data_extractor.reader.number_of_time_steps, 1.0)
        results["expected_value"] = expected_values
        results["term"] = term
        return results

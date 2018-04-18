import numpy as np

from pyesg.configuration.validation_configuration import ValidationAnalysis
from pyesg.constants.outputs import TOTAL_RETURN_INDEX
from pyesg.constants.validation_analyses import DISCOUNTED_TOTAL_RETURN_INDEX
from pyesg.constants.validation_result_types import MARTINGALE
from pyesg.validation.utils import get_confidence_level, do_sample_mean_and_confidence_interval_calculations
from pyesg.validation.validators.base_validator import BaseValidator


class DiscountedTRIValidator(BaseValidator):
    """
    Performs discounted TRI martingale analysis.

    The expected value of the discounted TRI is the initial value of the TRI.
    """
    analysis_id = DISCOUNTED_TOTAL_RETURN_INDEX
    result_type = MARTINGALE

    def _validate(self, analysis_settings: ValidationAnalysis):
        confidence_level = get_confidence_level(analysis_settings)

        # Get the output because we need to access its initial value
        tri_output = self._data_extractor.get_output(
            asset_class=self._asset_class,
            output_type=TOTAL_RETURN_INDEX
        )

        # Use the reader directly (instead of the data_extractor method) because we already have the output
        # and therefore already know its id.
        tri_sims = self._data_extractor.reader.get_output_simulations(tri_output.id)

        # Get sample mean and upper and lower confidence intervals
        results = do_sample_mean_and_confidence_interval_calculations(
            array=tri_sims,
            confidence_level=confidence_level,
            annualisation_factor=self._data_extractor.reader.annualisation_factor
        )

        # Put expected value in result too.
        expected_values = np.full(self._data_extractor.reader.number_of_time_steps, float(tri_output.initial_value))
        results["expected_value"] = expected_values.tolist()
        return results
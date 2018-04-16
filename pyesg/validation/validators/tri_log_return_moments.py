import numpy as np

from pyesg.configuration.validation_configuration import ValidationAnalysis
from pyesg.constants.outputs import TOTAL_RETURN_INDEX
from pyesg.constants.validation_analyses import TOTAL_RETURN_INDEX_LOG_RETURN_MOMENTS
from pyesg.constants.validation_result_types import MOMENTS
from pyesg.validation.utils import do_log_return_moments_calculations
from pyesg.validation.validators.base_validator import BaseValidator


class TRILogReturnMomentsValidator(BaseValidator):
    """
    Performs discounted TRI martingale analysis.
    """
    analysis_id = TOTAL_RETURN_INDEX_LOG_RETURN_MOMENTS
    result_type = MOMENTS

    def _validate(self, analysis_settings: ValidationAnalysis):
        tri_sims = self._data_extractor.get_output_simulations(
            asset_class=self._asset_class,
            output_type=TOTAL_RETURN_INDEX,
        )

        return do_log_return_moments_calculations(
            array=tri_sims,
            annualisation_factor=self._data_extractor.reader.annualisation_factor,
        )

from pyesg.configuration.pyesg_configuration import AssetClass
from pyesg.configuration.validation_configuration import ValidationAnalysis

from pyesg.validation.data_extractor import DataExtractor


class BaseValidator:
    """
    Base class for validators.
    """
    analysis_id = None
    result_type = None

    def __init__(self, asset_class: AssetClass, data_extractor: DataExtractor):
        self._asset_class = asset_class
        self._data_extractor = data_extractor

    def validate(self, analysis_settings: ValidationAnalysis) -> dict:
        """
        Performs the validation analysis and returns the results
        Args:
            analysis_settings: The settings for the analysis.

        Returns:
            The results of the validation analysis.
        """
        return {
            "asset_class_id": self._asset_class.id,
            "analysis_id": self.analysis_id,
            "result_type": self.result_type,
            "results": self._validate(analysis_settings),
        }

    def _validate(self, analysis_settings: ValidationAnalysis) -> dict:
        raise NotImplementedError()

from typing import Union

from pyesg.configuration.pyesg_configuration import AssetClass, PyESGConfiguration
from pyesg.validation.data_extractor import DataExtractor
from pyesg.validation.validators.average_discount_factor_validator import AverageDiscountFactorValidator
from pyesg.validation.validators.base_validator import BaseValidator
from pyesg.validation.validators.discounted_tri_validator import DiscountedTRIValidator
from pyesg.validation.validators.discounted_zcb_validator import DiscountedZCBValidator
from pyesg.validation.validators.tri_log_return_moments import TRILogReturnMomentsValidator


class ValidatorFactory:
    """
    Used to create instances of validators.
    """
    _validators = {cls.analysis_id: cls for cls in [
        AverageDiscountFactorValidator,
        DiscountedTRIValidator,
        DiscountedZCBValidator,
        TRILogReturnMomentsValidator,
    ]}

    def __init__(self, pyesg_config: PyESGConfiguration):
        self._config = pyesg_config
        self._data_extractor = DataExtractor(pyesg_config)

    def get_validator(self, analysis_id: str, asset_class: Union[AssetClass, str]) -> BaseValidator:
        """
        Returns a validator of the required type for the specified asset class.
        Args:
            analysis_id: The analysis id. This is a value from pyesg.constants.validation_analyses.
            asset_class: The asset class or asset class id on which the validation is to be performed.

        Returns:
            A validator of the required type for the specified asset class.
        """
        if not isinstance(asset_class, AssetClass):
            asset_classes = sum([economy.asset_classes for economy in self._config.economies], [])
            try:
                asset_class = next(ac for ac in asset_classes if ac.id == asset_class)
            except StopIteration:
                raise ValueError(f"The asset class {asset_class} does not exist.")

        cls = self._validators.get(analysis_id)
        if not cls:
            raise ValueError(f"Validation analysis {analysis_id} is not supported.")

        return cls(asset_class=asset_class, data_extractor=self._data_extractor)

from pyesg.configuration.pyesg_configuration import PyESGConfiguration
from pyesg.configuration.validation_configuration import ValidationConfiguration
from pyesg.validation.validators.validator_factory import ValidatorFactory


def validate_simulations_from_config(pyesg_config: PyESGConfiguration, validation_config: ValidationConfiguration):
    validator_factory = ValidatorFactory(pyesg_config)
    result = {}
    for asset_class in validation_config.asset_classes:
        asset_class_results = []
        for analysis_settings in asset_class.validation_analyses:
            validator = validator_factory.get_validator(analysis_settings.id, asset_class.id)
            asset_class_results.append(validator.validate(analysis_settings))
        result[asset_class.id] = asset_class_results

    return result
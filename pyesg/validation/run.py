import json
import os

from pyesg.configuration.pyesg_configuration import PyESGConfiguration
from pyesg.configuration.validation_configuration import ValidationConfiguration
from pyesg.validation.report.report_builder import ReportBuilder
from pyesg.validation.validators.validator_factory import ValidatorFactory


def validate_simulations_from_config(pyesg_config: PyESGConfiguration, validation_config: ValidationConfiguration,
                                     save_results_to_file: bool = False, build_report: bool = True) -> None:
    if not save_results_to_file and not build_report:
        raise ValueError("Both 'save_results_to_file' and 'build_report' are False. At least one must be True")

    validator_factory = ValidatorFactory(pyesg_config)
    result = {}
    for asset_class in validation_config.asset_classes:
        asset_class_results = []
        for analysis_settings in asset_class.validation_analyses:
            validator = validator_factory.get_validator(analysis_settings.id, asset_class.id)
            asset_class_results.append(validator.validate(analysis_settings))
        result[asset_class.id] = asset_class_results

    if save_results_to_file:
        results_file_path = os.path.join(
            validation_config.output_file_directory,
            f"{validation_config.output_file_name}_validation_results.json",
        )
        with open(results_file_path, 'w') as results_file:
            json.dump(result, indent=4)

    if build_report:
        report_file_path = os.path.join(
            validation_config.output_file_directory,
            f"{validation_config.output_file_name}_report.html"
        )
        ReportBuilder().build_report(report_file_path, validation_config.output_file_name, result)

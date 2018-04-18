import json
import os

from typing import Union

from pyesg.configuration.pyesg_configuration import PyESGConfiguration
from pyesg.configuration.validation_configuration import ValidationConfiguration
from pyesg.validation.report.report_builder import ReportBuilder
from pyesg.validation.validators.validator_factory import ValidatorFactory


def validate_simulations(pyesg_config: Union[str, PyESGConfiguration],
                         validation_config: Union[str, ValidationConfiguration],
                         save_results_to_file: bool = False,
                         build_report: bool = True) -> None:
    """
    Validates simulations according to validation analyses specified and generates a report containing the results.
    Args:
        pyesg_config: The pyESG configuration object or a file path to the configuration file.
        validation_config: The validation configuration object or a file path to the validation configuration file.
        save_results_to_file: Indicates whether to save the numerical results of validation analyses to a JSON file.
        build_report: Indicates whether to build an HTML report for the results of the validation analyses.
    """
    if not save_results_to_file and not build_report:
        raise ValueError("Both 'save_results_to_file' and 'build_report' are False. At least one must be True")

    # Check if configs have been specified as file paths and load them
    if isinstance(pyesg_config, str):
        pyesg_config = PyESGConfiguration.load_from_file(pyesg_config)

    if isinstance(validation_config, str):
        validation_config = ValidationConfiguration.load_from_file(validation_config)

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
            json.dump(result, results_file, indent=4)

    if build_report:
        report_file_path = os.path.join(
            validation_config.output_file_directory,
            f"{validation_config.output_file_name}_report.html"
        )
        ReportBuilder().build_report(report_file_path, validation_config.output_file_name, result)

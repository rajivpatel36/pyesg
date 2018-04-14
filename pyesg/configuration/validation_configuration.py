import json

from typing import List
from voluptuous import In, Schema, Required, IsDir

from pyesg.configuration.json_serialisable_class import JSONSerialisableClass, _has_parameters
from pyesg.constants.validation_analyses import ALL_VALIDATION_ANALYSES


class Parameters(JSONSerialisableClass):
    """
    Represents a set of parameters in the validation configuration.
    """
    _validation_schema = Schema(dict)


@_has_parameters
class ValidationAnalysis(JSONSerialisableClass):
    """
    Represents a validation analysis in the validation configuration.
    Attributes:
        id (str): The id for the validation analysis.
        parameters (Parameters): The parameters for the analysis.
    """
    _serialisable_attrs = {
        'parameters': Parameters
    }

    _validation_schema = Schema({
        Required('id'): In(ALL_VALIDATION_ANALYSES),
        Required('parameters'): Parameters._validation_schema,
    })

    def __init__(self, **kwargs):
        self.id = None  # type: str
        self.parameters = Parameters()

        super().__init__(**kwargs)


class AssetClass(JSONSerialisableClass):
    """
    Represents the configuration for a single asset class in the validation configuration.
    Attributes:
        id (str): The id for the asset class.
        validation_analyses (List[ValidationAnalysis]): A list of validation analysis objects containing the validation
                                                        analyses to perform for the asset class.
    """
    _serialisable_lists = {
        'validation_analyses': ValidationAnalysis,
    }

    _validation_schema = Schema({
        Required('id'): str,
        Required('validation_analyses'): [ValidationAnalysis._validation_schema],
    })

    def __init__(self, **kwargs):
        self.id = None  # type: str
        self.validation_analyses = []  # type: List[ValidationAnalysis]
        super().__init__(**kwargs)


class ValidationConfiguration(JSONSerialisableClass):
    """
    Represents the validation configuration.
    Attributes:
        output_file_directory (str): The directory to which validation results will be saved.
        output_file_name (str): The name of the file to save containing the validation results.
        validation_analyses (List[AssetClass]): A list of asset class objects containing all validations to perform
                                                for the asset class.
    """
    _serialisable_lists = {
        'asset_classes': AssetClass,
    }

    _validation_schema = Schema({
        Required("output_file_directory"): IsDir(),
        Required("output_file_name"): str,
        Required("asset_classes"): [AssetClass._validation_schema],
    })

    def __init__(self, **kwargs):
        self.output_file_directory = None  # type: str
        self.output_file_name = None  # type: str
        self.asset_classes = []  # type: List[AssetClass]
        super().__init__(**kwargs)

    @classmethod
    def load_from_file(cls, file_path: str) -> 'ValidationConfiguration':
        """
        Loads settings from a validation configuration file.
        Args:
            file_path: The file path of the validation configuration file.

        Returns:
            A ValidationConfiguration object containing the settings from the specified configuration file.
        """
        with open(file_path) as config_file:
            config = json.load(config_file)

        config = cls._decode_json(config)  # type: 'ValidationConfiguration'
        return config

    def save_to_file(self, file_path: str):
        """
        Saves the configuration settings specified to a file.
        Args:
            file_path: The file path to which to save the configuration file.
        """
        with open(file_path, 'w') as validation_configuration_file:
            json.dump(self._encode_json(), validation_configuration_file, indent=4)

    def validate(self):
        """
        Validates the configuration.
        """
        json_obj = self._encode_json()
        self._validation_schema(json_obj)

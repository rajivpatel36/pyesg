import json
from collections import OrderedDict

from voluptuous import Schema, Coerce, Required, Maybe, All, Range, IsDir, In, Date

from pyesg.configuration.json_serialisable_class import JSONSerialisableClass, _has_parameters
from pyesg.constants.projection_frequency import PROJECTION_FREQUENCIES


class Parameters(JSONSerialisableClass):
    """
    Represents a set of parameters in the pyESG configuration.
    """
    _validation_schema = Schema({
        str: Coerce(float)
    })


@_has_parameters
class Output(JSONSerialisableClass):
    """
    Represents a model output in the pyESG configuration.
    Attributes:
        id (str): The id (or name) for the output.
        type (str): The type of the output.
        initial_value (float): The initial value for the output.
        parameters (List[Parameter]): A list of the parameters associated with the output.
    """
    _serialisable_attrs = {
        'parameters': Parameters,
    }

    _validation_schema = Schema({
        Required('id'): str,
        Required('type'): str,
        Required('initial_value'): Maybe(Coerce(float)),
        Required('parameters'): Parameters._validation_schema,
    })

    def __init__(self, **kwargs):
        self.id = None  # type: str
        self.type = None  # type: str
        self.initial_value = None  # type: float
        self.parameters = Parameters()  # type: Parameters
        super().__init__(**kwargs)


@_has_parameters
class AssetClass(JSONSerialisableClass):
    """
    Represents an asset class being modelled in the pyESG configuration.
    Attributes:
        id (str): The id (or name) for the asset class.
        model_id (str): The id (or name) of the model being used for the asset class.
        parameters (List[Parameter]): A list of the parameters associated with the model.
        outputs (List[Output]): A list of the outputs to be calculated for the model.
        random_drivers (List[RandomDriver]): A list of the random drivers associated with the model.
        dependencies (List[str]): A list of the ids of other asset classes upon which this asset class depends.
    """
    _serialisable_attrs = {
        'parameters': Parameters,
    }

    _serialisable_lists = {
        'outputs': Output,
    }

    _validation_schema = Schema({
        Required('id'): str,
        Required('model_id'): str,
        Required('parameters'): Parameters._validation_schema,
        Required('outputs'): [Output._validation_schema],
        Required('random_drivers'): [str],
        Required('dependencies'): [str],
    })

    def __init__(self, **kwargs):
        self.id = None  # type: str
        self.model_id = None  # type: str
        self.parameters = Parameters()  # type: Parameters
        self.outputs = []   # type: List[Output]
        self.random_drivers = []  # type: List[str]
        self.dependencies = []  # type: List[str]
        super().__init__(**kwargs)

    def add_output(self, id: str, type: str, initial_value: float=None, **kwargs):
        """
        Adds an output to the list of outputs for the asset class.
        Args:
            id: The id (or name) for the output.
            type: The type of the output.
            initial_value: The initial value of the output.
            **kwargs: The parameters for the output. The keywords are the parameter ids and the values are the parameter
                      values.
        """
        output = Output(id=id, type=type, initial_value=initial_value)
        for key, value in kwargs.items():
            output.add_parameter(key, value)
        self.outputs.append(output)


class Correlations(JSONSerialisableClass):
    """
    Represents the correlation matrix between the random drivers in the pyESG configuration.
    """
    _validation_schema = Schema([
        {
            Required('row_id'): str,
            Required('column_id'): str,
            Required('correlation'): float,
        }
    ])
    def __init__(self, **kwargs):
        self._correlations = OrderedDict()
        super().__init__(**kwargs)

    def get_correlation(self, row_id: str, column_id: str)->float:
        """
        Returns an entry from the correlation matrix based on the row and column ids.
        Args:
            row_id: The id for the row.
            column_id: The id for the column.

        Returns:
            The correlation associated with the specified row and column id.
            If the two ids are equal, 1 is returned. If no correlation has been specified for this pair of ids,
            0 is returned.
        """
        min_id = min(row_id, column_id)
        max_id = max(row_id, column_id)

        if min_id == max_id:
            return 1.0
        else:
            return self._correlations.get((min_id, max_id), 0.0)

    def set_correlation(self, row_id: str, column_id: str, correlation: float):
        """
        Sets the value for an entry in the correlation matrix based on the row and column ids.
        Args:
            row_id: The id for the row.
            column_id: The id for the column.
            correlation: The correlation associated with the specified row and column id.
                         This value is ignored if the row and column ids are equal.
        """
        min_id = min(row_id, column_id)
        max_id = max(row_id, column_id)

        if min_id != max_id:
            self._correlations[(min_id, max_id)] = correlation

    def _encode_json(self):
        encoded_json = []
        for key, value in self._correlations.items():
            encoded_json.append({
                'row_id': key[0],
                'column_id': key[1],
                'correlation': value,
            })

        return encoded_json

    @classmethod
    def _decode_json(cls, json_obj: dict):
        instance = cls()
        for correlation in json_obj:
            instance.set_correlation(correlation['row_id'], correlation['column_id'], correlation['correlation'])

        return instance


class Economy(JSONSerialisableClass):
    """
    Represents an economy for which asset classes are being modelled in the pyESG configuration.
    Attributes:
        id (str): The id (or name) of the economy.
        asset_classes (List[AssetClass]): A list of the asset classes being modelled in the economy.
    """
    _serialisable_lists = {
        'asset_classes': AssetClass,
    }
    _validation_schema = Schema({
        Required('id'): str,
        Required('asset_classes'): [AssetClass._validation_schema],
    })

    def __init__(self, **kwargs):
        self.id = None  # type: str
        self.asset_classes = []  # type: List[AssetClass]
        super().__init__(**kwargs)


class PyESGConfiguration(JSONSerialisableClass):
    """
    Represents the full pyESG configuration.
    Attributes:
        number_of_simulations (int): The number of simulations to produce.
        number_of_projection_steps (int): The number of time steps to project in the simulations.
        projection_frequency (str): The frequency of projections. (e.g. 'annually', 'monthly', 'weekly')
        number_of_batches (int): The number of batches into which the simulations are split during generation.
        random_seed (int): The random seed to use when generating random samples.
        economies (list[Economy]): A list of the economies being modelled.
        correlations (Correlations): The correlations between the random drivers for the asset class models.
    """
    _serialisable_lists = {
        'economies': Economy,
    }

    _serialisable_attrs = {
        'correlations': Correlations,
    }

    _validation_schema = Schema({
        Required('number_of_simulations'): All(int, Range(min=1)),
        Required('number_of_projection_steps'): All(int, Range(min=1)),
        Required('output_file_directory'): IsDir(),
        Required('output_file_name'): str,
        Required('projection_frequency'): In(PROJECTION_FREQUENCIES),
        Required('number_of_batches'): All(int, Range(min=1)),
        Required('random_seed'): int,
        Required('start_date'): Date(),
        Required('economies'): [Economy._validation_schema],
        Required('correlations'): Correlations._validation_schema,
    })

    def __init__(self, **kwargs):
        self.number_of_simulations = None  # type: int
        self.number_of_projection_steps = None  # type: int
        self.output_file_directory = None  # type: str
        self.output_file_name = None  # type: str
        self.projection_frequency = None  # type: str
        self.number_of_batches = None  # type: int
        self.random_seed = None  # type: int
        self.start_date = None  # type: str
        self.economies = []  # type: List[Economy]
        self.correlations = Correlations()  # type: Correlations
        super().__init__(**kwargs)

    @classmethod
    def load_from_file(cls, file_path: str) -> 'PyESGConfiguration':
        """
        Loads settings from a pyESG configuration file.
        Args:
            file_path: The file path of the pyESG configuration file.

        Returns:
            A PyESGConfiguration object containing the settings from the specified configuration file.
        """
        with open(file_path) as config_file:
            config = json.load(config_file)

        pyesg_config = cls._decode_json(config)  # type: 'PyESGConfiguration'
        return pyesg_config

    def save_to_file(self, file_path: str):
        """
        Saves the configuration settings specified to a file.
        Args:
            file_path: The file path to which to save the configuration file.
        """
        with open(file_path, 'w') as engine_settings_file:
            json.dump(self._encode_json(), engine_settings_file, indent=4)

    def validate(self):
        """
        Validates the configuration.
        """
        json_obj = self._encode_json()
        self._validation_schema(json_obj)
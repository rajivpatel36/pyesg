import itertools
import numpy as np

from dateutil import parser, rrule

from pyesg.configuration.pyesg_configuration import PyESGConfiguration
from pyesg.constants.projection_frequency import *
from pyesg.utils import get_duplicates


class InitialisedSettings:
    """
    Class containing all settings initialised from a pyESG configuration.
    Attributes:
        annualisation_factor (float): The number of projection steps per year.
        asset_class_ids (List[str]): List of the IDs of all asset classes being modelled.
        asset_class_models (List[BaseModel]): List of all model classes for asset classes being modelled.
        specified_model_outputs (List[BaseOutput]): List of all output classes for outputs specified for asset classes.
        dependent_model_outputs (List[BaseOutput]): List of all output classes which are created as dependencies
                                                    for the specified outputs.
        config (PyESGConfiguration): The underlying pyESG configuration.
        number_outputs (int): The total number of outputs specified in the pyESG configuration.
        number_random_drivers (int): The total number of random drivers specified in the pyESG configuration
        output_ids (List[str]): List of the IDs of all outputs.
        random_driver_ids (List[str]): List of the IDs of all random drivers.
        projection_dates (List[datetime.datetime]): List of projection dates.
        random_generator (np.random.RandomState): Numpy RandomState for generating seeded random numbers.
    """
    def __init__(self, pyesg_config: PyESGConfiguration):
        self.config = pyesg_config

        all_asset_classes = sum([economy.asset_classes for economy in pyesg_config.economies], [])
        self.asset_class_ids = [asset_class.id for asset_class in all_asset_classes]

        self.number_outputs = sum([len(asset_class.outputs) for asset_class in all_asset_classes])

        self.number_random_drivers = sum([len(asset_class.random_drivers) for asset_class in all_asset_classes])

        self.output_ids = sum([[output.id for output in asset_class.outputs] for asset_class in all_asset_classes], [])

        self.random_driver_ids = sum([asset_class.random_drivers for asset_class in all_asset_classes], [])

        frequency_mapping = {
            ANNUALLY: rrule.YEARLY,
            MONTHLY: rrule.MONTHLY,
            WEEKLY: rrule.WEEKLY,
        }
        rrule_frequency = frequency_mapping[pyesg_config.projection_frequency]
        start_date = parser.parse(pyesg_config.start_date)
        dates_gen = rrule.rrule(freq=rrule_frequency,
                                dtstart=start_date,
                                count=pyesg_config.number_of_projection_steps + 1)  # Add 1 to account for initial step
        self.projection_dates = list(dates_gen)

        annualisation_factor_mapping = {
            ANNUALLY: 1.0,
            MONTHLY: 12.0,
            WEEKLY: 52.0,
        }
        self.annualisation_factor = annualisation_factor_mapping[pyesg_config.projection_frequency]

        correlation_matrix = np.ones([self.number_random_drivers, self.number_random_drivers])
        combinations = itertools.product(enumerate(self.random_driver_ids), enumerate(self.random_driver_ids))
        for (row_index, row_driver_id), (column_index, column_driver_id) in combinations:
            correlation_matrix[row_index, column_index] = pyesg_config.correlations.get_correlation(row_driver_id,
                                                                                                    column_driver_id)
        self.random_driver_correlation_matrix = correlation_matrix
        self.random_generator = np.random.RandomState(pyesg_config.random_seed)

        self.asset_class_models = []
        self.specified_model_outputs = []
        self.dependent_model_outputs = []

        self.output_values = None

    def reset_output_values(self):
        """
        Resets the `output_values` attribute to an array of zeros.

        This should be used in between batches of simulations to reset the values.
        """
        batch_size = int(self.config.number_of_simulations / self.config.number_of_batches)
        # Add 1 to number of projection steps because the value in config doesn't include initial time step.
        self.output_values = np.zeros([self.number_outputs,
                                       self.config.number_of_projection_steps + 1,
                                       batch_size])


def validate_initialised_settings(settings: InitialisedSettings):
    """
    Validates high level settings.
    It does not check types but checks main properties of configuration to see if they are invalid (e.g. negative
    number of simulations).
    Args:
        settings: The initialised settings for the pyESG configuration.
    """
    # Check that number of batches divides number of sims
    assert settings.config.number_of_simulations % settings.config.number_of_batches == 0, \
        "Number of simulations must be a multiple of the number of batches."

    duplicate_asset_classes = get_duplicates(settings.asset_class_ids)
    assert len(duplicate_asset_classes) == 0, \
        f"Duplicate asset classes in the configuration: \n {' '.join(duplicate_asset_classes)}"

    duplicate_outputs = get_duplicates(settings.output_ids)
    assert len(duplicate_outputs) == 0, \
        f"Duplicate asset classes in the configuration: \n {' '.join(duplicate_outputs)}"

    duplicate_random_drivers = get_duplicates(settings.random_driver_ids)
    assert len(duplicate_random_drivers) == 0, \
        f"Duplicate asset classes in the configuration: \n {' '.join(duplicate_random_drivers)}"

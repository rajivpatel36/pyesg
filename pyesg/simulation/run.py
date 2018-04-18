import numpy as np
import os

from typing import Union

from pyesg.configuration.pyesg_configuration import PyESGConfiguration
from pyesg.io.writer import PyESGWriter
from pyesg.simulation.models.model_factory import get_model_for_asset_class
from pyesg.simulation.settings import InitialisedSettings, validate_initialised_settings


def generate_random_drivers(settings: InitialisedSettings)->np.ndarray:
    """
    Generates random drivers for a batch of simulations.
    Args:
        settings: The initialised settings for the pyESG configuration.

    Returns:
        An array with dimension (number projection steps x number of simulations x number drivers in batch) containing
        the random drivers required for a batch of simulations.
    """
    # For each projection step and simulation, we want to generate samples from a set of correlated random drivers.
    # We use the multivariate_normal random generator from numpy and the covariance matrix is equal to the
    # correlation matrix because all random drivers have variance = 1.
    batch_size = int(settings.config.number_of_simulations / settings.config.number_of_batches)
    means = np.zeros(settings.number_random_drivers)
    return settings.random_generator.multivariate_normal(
        mean=means,
        cov=settings.random_driver_correlation_matrix,
        size=[settings.config.number_of_projection_steps, batch_size]
    )


def assign_generated_random_drivers_to_models(generated_random_drivers: np.ndarray, settings: InitialisedSettings):
    for model in settings.asset_class_models:
        # Get the index of the random drivers for the model in the list of all random drivers
        driver_indices = [settings.random_driver_ids.index(driver_id) for driver_id in model.asset_class.random_drivers]

        # Slice the generated random drivers to extract relevant drivers for model
        model.random_samples = generated_random_drivers[:, :, driver_indices]


def initialise_models_and_outputs(settings: InitialisedSettings):
    """
    Creates all model and output classes, initialises them and stores them in `settings`.
    Args:
        settings: The initialised settings for the pyESG configuration.
    """
    for economy in settings.config.economies:
        for asset_class in economy.asset_classes:
            model = get_model_for_asset_class(asset_class, settings)
            settings.asset_class_models.append(model)
            model.initialise_model()  # Initialising the model will create all outputs specified for the model.

    for output in settings.specified_model_outputs:
        output.initialise_output()


def generate_simulations(pyesg_config: Union[str, PyESGConfiguration]):
    """
    Generates simulations based on pyESG configuration object.
    Args:
        pyesg_config: The pyESG configuration object or the file path for the configuration file.
    """
    # Load the config if it has been specified as a file path.
    if isinstance(pyesg_config, str):
        pyesg_config = PyESGConfiguration.load_from_file(pyesg_config)

    pyesg_config.validate()
    settings = InitialisedSettings(pyesg_config)
    validate_initialised_settings(settings)

    # Initialise PyESG writer to write results to binary file.
    output_file_path = os.path.join(pyesg_config.output_file_directory, pyesg_config.output_file_name + ".pyesg")
    pyesg_writer = PyESGWriter(output_file_path)
    pyesg_writer.write_header(
        pyesg_config.number_of_simulations,
        settings.output_ids,
        settings.projection_dates,
        settings.annualisation_factor,
    )

    initialise_models_and_outputs(settings)

    for batch_number in range(pyesg_config.number_of_batches):
        settings.reset_output_values()  # Set output values array to zeros.

        generated_random_drivers = generate_random_drivers(settings)
        assign_generated_random_drivers_to_models(generated_random_drivers, settings)

        for projection_step in range(pyesg_config.number_of_projection_steps + 1):
            for output in settings.dependent_model_outputs + settings.specified_model_outputs:
                output.calculate_for_batch(projection_step)

        # Add 1 to `batch_number` because it's zero-indexed and the argument expects a one-indexed number.
        pyesg_writer.write_batch_of_simulations(batch_number + 1, pyesg_config.number_of_batches, settings.output_values)

    pyesg_writer.finalise()

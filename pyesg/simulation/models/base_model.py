import numpy as np

from typing import List, Dict, Type

from pyesg.configuration.pyesg_configuration import AssetClass, Output
from pyesg.simulation.exceptions import OutputNotExistsError
from pyesg.simulation.settings import InitialisedSettings


class BaseModel:
    """
    Base class for an asset class model.
    """
    output_class_mapping = None  # type: Dict[str, Type]

    def __init__(self, settings: InitialisedSettings, asset_class: AssetClass):
        self.settings = settings
        self.asset_class = asset_class
        self.random_samples = None
        self.outputs =[]  # type: List[BaseOutput]

    def initialise_model(self):
        """
        Initialises the model, creating the output classes for specified outputs.
        """
        for output_settings in self.asset_class.outputs:
            output = self.create_output(output_settings)
            self.settings.specified_model_outputs.append(output)
            self.outputs.append(output)

    def create_output(self, output: Output) -> 'BaseOutput':
        """
        Returns an instance of a model output class given the output object in the pyESG configuration.
        Args:
            output: The output object in the pyESG configuration

        Returns:
            An instance of the model output class required for the output object specified.
        """
        output_cls = self.output_class_mapping.get(output.type)
        if output_cls is None:
            raise OutputNotExistsError(f"{output.type} output does not exist for {self.asset_class.model_id} model")
        return output_cls(model=self, output=output)

    def get_random_samples(self, projection_step: int, driver_index: int) -> np.ndarray:
        """
        Returns the random samples for specific random driver for a specific projection step.
        Args:
            projection_step: The projection step for the random samples are required.
            driver_index: The index of the random driver for which the random samples are required. This is the index
                          of the random drivers for the model (as opposed to the index for the random driver in the list
                          of random drivers for all models).

        Returns:
            An array containing the random samples for the specified random driver for the specified projection step.
        """
        return self.random_samples[projection_step - 1, :, driver_index]


class BaseOutput:
    """
    Base class for model output.
    """
    def __init__(self, model: BaseModel, output: Output):
        self.model = model
        self.settings = model.settings
        self.output = output
        self.latest_projection_step_calculated = None
        self.latest_projection_step_sims = None

        if output.id:
            self.output_index = self.settings.output_ids.index(output.id)
        else:
            self.output_index = None

    def initialise_output(self):
        """
        Initialises the output, caching all variables needed during simulation.
        """
        raise NotImplementedError

    def get_or_create_output(self, output_type: str, asset_class_id: str = None,  **output_parameters) -> 'BaseOutput':
        """
        Gets an existing or creates a new output of a specified type with specified parameters from any asset class.
        Args:
            output_type: The output type.
            asset_class_id: The id of the asset class for the output. If None, it is assumed to be the existing asset
                            class.
            **output_parameters: The parameters of the output specified as kwargs. The key is the parameter name
                                 and the value is the parameter value.

        Returns:
            The output for the specified asset class with the specified type and parameters.
        """
        # If no asset class id specified then assume you are looking for output in existing model (most common case)
        if asset_class_id is None:
            model = self.model
        else:
            try:
                model = next(m for m in self.settings.asset_class_models if m.asset_class.id == asset_class_id)
            except StopIteration:
                raise ValueError(f"Asset class with id {asset_class_id} does not exist.")

        # Search through the model outputs to see if the required output already exists
        for output in model.outputs:
            if output.output.type == output_type and output.output.parameters.__dict__ == output_parameters:
                return output

        # If output doesn't exist then create and initialise it
        output = Output(type=output_type, **output_parameters)
        model_output = self.model.create_output(output)
        self.settings.dependent_model_outputs.append(model_output)
        self.model.outputs.append(model_output)

        model_output.initialise_output()
        return model_output

    def calculate_for_batch(self, projection_step: int):
        """
        Calculates values for all simulations in a batch for the output for a specific projection step.
        Args:
            projection_step: The project step to calculate.
        """
        if self.latest_projection_step_calculated == projection_step:
            return self.latest_projection_step_sims

        if projection_step == 0 and self.output.initial_value is not None:
            config = self.model.settings.config
            batch_size = int(config.number_of_simulations / config.number_of_batches)
            sims_batch = np.full(batch_size, self.output.initial_value)
        else:
            sims_batch = self._calculate_values_for_batch(projection_step)

        self.latest_projection_step_calculated = projection_step
        self.latest_projection_step_sims = sims_batch

        if self.output_index is not None:
            self.settings.output_values[self.output_index, projection_step, :] = sims_batch

        return self.latest_projection_step_sims

    def _calculate_values_for_batch(self, projection_step: int):
        raise NotImplementedError

import numpy as np
import os

from typing import Union

from pyesg.configuration.pyesg_configuration import PyESGConfiguration, AssetClass, Output
from pyesg.io.reader import PyESGReader


class DataExtractor:
    """
    Used to extract data for outputs from a file.

    Most of the work is done by the pyesg.io.reader.PyESGReader class. The functionality added by this class is to
    allow outputs to be found without knowing the output id - you can extract data just by knowing the asset, output
    type and the output parameters and it will find it from the config.
    """
    def __init__(self, pyesg_config: PyESGConfiguration):
        self._config = pyesg_config
        pyesg_file = os.path.join(pyesg_config.output_file_directory, pyesg_config.output_file_name + ".pyesg")
        if not os.path.exists(pyesg_file):
            raise FileNotFoundError(f"PyESG file does not exist at {pyesg_file}")

        self.reader = PyESGReader(pyesg_file)
        self._cache = {}

    def get_asset_class_from_id(self, asset_class_id) -> AssetClass:
        """
        Returns the asset class object from the pyESG config that has the specified id.
        Args:
            asset_class_id: The id of the asset class.

        Returns:
            The asset class object from the pyESG config that has the specified id.
        """
        for economy in self._config.economies:
            for asset_class in economy.asset_classes:
                if asset_class.id == asset_class_id:
                    return asset_class
        raise ValueError("Asset class with id f{asset_class_id} does not exist.")

    def get_output(self, asset_class: Union[str, AssetClass], output_type: str, **output_parameters) -> Output:
        """
        Returns the output id for an output in an asset class matching the specified arguments.
        Args:
            asset_class: The asset class in which the output exists.
            output_type: The type of the output.
            **output_parameters: The parameter names and values for the output.

        Returns:
            The id for the output matching the specified arguments.
        """
        if isinstance(asset_class, str):
            asset_class = self.get_asset_class_from_id(asset_class)

        try:
            # Return first output with parameters and type matching.
            return next(o for o in asset_class.outputs
                        if o.type == output_type and o.parameters.__dict__ == output_parameters)
        except StopIteration:
            raise ValueError(f"Output of type {output_type} does not exist with parameters {output_parameters}.")

    def get_output_simulations(self, asset_class: Union[AssetClass, str], output_type: str, time_step: int = None,
                               **output_parameters) -> np.ndarray:
        """
        Returns the simulations for an output in an asset class matching the specified arguments.
        Args:
            asset_class: The asset class in which the output exists.
            output_type: The type of the output.
            time_step: (Optional) The time step for which to extract simulations.
            **output_parameters: The parameter names and values for the output.

        Returns:
            The simulations for an output in an asset class matching the specified arguments.

        If no time step is specified, simulations are returned for all time steps.
        """
        output_id = self.get_output(asset_class, output_type, **output_parameters).id
        output_simulations = self._cache.get(output_id)
        if output_simulations is None:
            output_simulations = self.reader.get_output_simulations(output_id)
            self._cache[output_id] = output_simulations

        if time_step is not None:
            return output_simulations[:, time_step]
        else:
            return output_simulations

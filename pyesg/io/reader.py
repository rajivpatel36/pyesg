import io
import numpy as np

from binaryio.open import open_binary, BinaryReader
from datetime import datetime
from typing import List, Union


class PyESGReader:
    """
    Contains functionality to read a PyESG binary file.
    """
    size_of_float = 4  # Number of bytes for a float (single-precision)
    def __init__(self, file_path: str):
        self._reader = open_binary(file_path, 'rb', endianness="<")  # type: BinaryReader
        self._reader.__enter__()
        
        self._time_saved = datetime.fromtimestamp(self._reader.read_uint64())
        self._number_sims = self._reader.read_uint32()
        self._number_outputs = self._reader.read_uint32()
        self._number_steps = self._reader.read_uint32()
        self._output_ids = [self._reader.read_length_prefixed_string() for _ in range(self._number_outputs)]
        self._time_step_dates = [datetime.fromtimestamp(self._reader.read_uint64()) for _ in range(self._number_steps)]
        self._header_end_position = self._reader.tell()

    def close(self) -> None:
        """
        Closes the PyESG file opened by the reader.

        This should be called when you have finished reading the file to ensure the file does not remain open.
        """
        self._reader.close()
        
    @property
    def time_saved(self) -> datetime:
        """
        Returns the time at which the PyESG binary file was saved.
        Returns:
            The time at which the PyESG binary file was saved.
        """
        return self._time_saved
    
    @property
    def number_of_simulations(self) -> int:
        """
        Returns the number of simulations in the file.
        Returns:
            The number of simulations in the file.
        """
        return self._number_sims
    
    @property
    def number_of_outputs(self) -> int:
        """
        Returns the number of outputs in the file.
        Returns:
            The number of outputs in the file.
        """
        return self._number_outputs

    @property
    def number_of_time_steps(self) -> int:
        """
        Returns the number of time steps in the file.
        Returns:
            The number of time steps in the file.

        This number includes the initial time step as well as the projection time steps.
        """
        return self._number_steps

    @property
    def number_of_projection_time_steps(self) -> int:
        """
        Returns the number of projection time steps in the file.
        Returns:
            The number of projection time steps in the file.
        """
        return self._number_steps - 1

    @property
    def output_ids(self) -> List[str]:
        """
        Returns the ids of all outputs in the file.
        Returns:
            The ids of all outputs in the file.
        """
        return self._output_ids

    @property
    def time_step_dates(self) -> List[datetime]:
        """
        Returns the dates for all time steps in the file.
        Returns:
            The dates for all time steps in the file.

        This includes the initial time step as well as all projection time steps.
        """
        return self._time_step_dates

    @property
    def projection_dates(self) -> List[datetime]:
        """
        Returns the dates for all projection time steps in the file.
        Returns:
            The dates for all projection time steps in the file.
        """
        return self._time_step_dates[1:]


    def _get_seek_position_for_output(self, output_index: int) -> int:
        """
        Returns the position to seek to in the binary file for the start of simulations for an output.
        Args:
            output_index: The index of the output id in the list of output ids.

        Returns:
            The byte position to seek to in the binary file to reach the start of the simulations for the specified
            output.
        """
        return self._header_end_position + output_index * self._number_sims * self._number_steps * self.size_of_float

    def _get_output_index(self, output: Union[str, int]) -> int:
        """
        Returns the index of the output in the list of output ids.
        Args:
            output: The id of the output or the intex of the output id in the list of output ids

        Returns:
            The index of the output in the list of output ids.
        """
        if not isinstance(output, (str, int)):
            raise TypeError("The `output` argument must be str or int.")

        if isinstance(output, str):
            if not output in self._output_ids:
                raise ValueError("The output {output} does not exist in the file.")
            output_index = self._output_ids.index(output)
        else:
            if not 0 <= output < len(self._output_ids):
                raise ValueError(f"The output index must satisfy 0 <= number < {len(self._output_ids)}")
            output_index = output
        return output_index

    def get_output_simulations(self, output: Union[str, int]) -> np.ndarray:
        """
        Returns all simulations for all time steps for a single output.
        Args:
            output: The id of the output or the index of the output id in the list of output ids.

        Returns:
            All simulations for all time steps for the specified output.

        The array returned has shape (number_simulations, number_time_steps) and includes the initial time step.
        """
        output_index = self._get_output_index(output)
        # Seek to start of output
        self._reader.seek(self._get_seek_position_for_output(output_index))
        # Read all simulations into a numpy array. They are flattened before storage
        size_of_flattened_array = self._number_sims * self._number_steps
        return np.array(self._reader.read_singles(size_of_flattened_array)).reshape(self._number_sims, self._number_steps)


    def get_output_simulations_for_single_time_step(self, output: Union[str, int], time_step: int) -> np.ndarray:
        """
        Returns all simulations for a specific time step for a single output.
        Args:
            output: The id of the output or the index of the output id in the list of output ids.
            time_step: The time step for which simulations are to be extracted.

        Returns:
            All simulations for the specified time step and output.

        The time step should be specified such that 0 is interpreted as the initial step.
        """
        if not isinstance(time_step, int):
            raise TypeError("The `time_step` argument must be an int.")

        if not 0 <= time_step < self._number_steps:
            raise ValueError(f"The time step must satisfy 0 <= number < {self._number_steps}")

        output_index = self._get_output_index(output)
        simulations = np.zeros(self._number_sims)

        # Seek to start of output and then to position of first simulation for the time step
        position_first_sim = self._get_seek_position_for_output(output_index) + time_step * self.size_of_float
        self._reader.seek(position_first_sim)

        # Calculate number of bytes between consecutive simulations for the same time step
        bytes_between_sims = (self._number_steps - 1) * self.size_of_float

        # We can only do number_sims - 1 in the for loop because we don't want to seek further after the last sim
        for i in range(self._number_sims - 1):
            simulations[i] = self._reader.read_single()
            self._reader.seek(bytes_between_sims, io.SEEK_CUR)

        # At this point we have seeked to the position of last sim. So now just get last sim.
        simulations[-1] = self._reader.read_single()

        return simulations

    def get_output_simulations_for_single_simulation(self, output: Union[str, int], simulation_number: int) -> np.ndarray:
        """
        Returns all time steps for an output for a specified simulation number.
        Args:
            output: The id of the output or the index of the output id in the list of output ids.
            simulation_number: The simulation number for which simulations are to be extracted.

        Returns:
            All time steps for the specified simulation number and output.

        The simulation number should be specified such that 1 is the first simulation. (It is 1-indexed.)
        """
        if not isinstance(simulation_number, int):
            raise TypeError("The `simulation_number` argument must be an int.")

        if not 1 <= simulation_number <= self._number_sims:
            raise ValueError(f"The simulation number must satisfy 1 <= number <= {self._number_sims}")

        # Seek to start of output and then to position of first step in simulation
        output_index = self._get_output_index(output)
        position_first_step = self._get_seek_position_for_output(output_index) \
                              + (simulation_number - 1) * self._number_steps * self.size_of_float
        self._reader.seek(position_first_step)
        return np.array(self._reader.read_singles(self._number_steps))

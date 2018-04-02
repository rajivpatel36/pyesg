import numpy as np

from binaryio.open import open_binary, BinaryWriter
from datetime import datetime
from time import time
from typing import List


class PyESGWriter:
    """
    Contains functionality to write a PyESG binary file.
    """
    def __init__(self, file_path: str):
        self._writer = open_binary(file_path, 'wb', endianness="<")  # type: BinaryWriter
        self._writer.__enter__()
        self._header_start_position = 8  # First 8 bytes are reserved for timestamp written when finalising file
        self._header_end_position = None

    def write_header(self, number_simulations: int, output_ids: List[str], projection_dates: List[datetime]):
        """
        Writes header information for the binary file.
        Args:
            number_simulations: The total number of simulations.
            output_ids: The list of output ids in the file.
            projection_dates: The list of projection dates in the file.
        """
        self._writer.seek(self._header_start_position)
        number_outputs = len(output_ids)
        number_projection_dates = len(projection_dates)

        self._writer.write_uint32(number_simulations)
        self._writer.write_uint32(number_outputs)
        self._writer.write_uint32(number_projection_dates)

        for output_id in output_ids:
            self._writer.write_length_prefixed_string(output_id)

        for date in projection_dates:
            self._writer.write_uint64(int(date.timestamp()))  # Write dates as unix timestamps

        self._header_end_position = self._writer.tell()

    def write_batch_of_simulations(self, batch_number: int, total_batches: int,  simulations: np.ndarray):
        """
        Writes a batch of simulations to the file.
        Args:
            batch_number: The batch number amongst all batches.
            total_batches: The total number of batches.
            simulations: A 3-dimensional array containing the simulations for the batch.

        The dimensions of the `simulations` array should be (number_outputs, number_steps, number_simulations)
        """
        number_outputs_in_batch, number_steps_in_batch, number_simulations_in_batch = simulations.shape

        # Binary file is organised so that each output is written (with all its sims) one after the other.
        # For each output we need to seek to the start of the output + start of batch within that output

        size_of_float = 4  # 4 bytes per float
        start_of_batch_within_output = (batch_number - 1) * number_simulations_in_batch * number_steps_in_batch \
                                       * size_of_float
        size_of_each_output = total_batches * number_simulations_in_batch * size_of_float

        for i_output in range(number_outputs_in_batch):
            output_sims = simulations[i_output, :, :]
            position_to_seek = self._header_end_position + i_output * size_of_each_output + start_of_batch_within_output
            self._writer.seek(position_to_seek)

            # Need to transpose because output_sims has shape (number_steps, number_simulations).
            # We need to convert it into (number_simulations, number_steps) for writing because writing in batches
            # by flattening stacks batches of the first dimension (which therefore needs to be sims).
            self._writer.write_singles(output_sims.transpose().flatten())

    def finalise(self):
        """
        Finalises the writing of the PyESG binary file.

        It writes the current time (as a Unix timestamp) at the start of the file and then closes the file.
        """
        self._writer.seek(0)
        self._writer.write_uint64(int(time()))
        self._writer.close()

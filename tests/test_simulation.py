import os
import pytest

from pyesg.configuration.pyesg_configuration import PyESGConfiguration
from pyesg.io.reader import PyESGReader
from pyesg.simulation.run import generate_simulations
from tests.utils import get_tests_directory


def compare_pyesg_files(output_file_path: str, comparison_file_path: str) -> None:
    """
    Compares two pyESG files and checks that the values in each are equal (or approximately equal for FP error)
    Args:
        output_file_path: The file path of file to check.
        comparison_file_path: The file path of the file containing the "true" values to check against.
    """
    output = PyESGReader(output_file_path)
    comparison = PyESGReader(comparison_file_path)

    # Check high level properties
    assert output.annualisation_factor == comparison.annualisation_factor
    assert output.number_of_outputs == comparison.number_of_outputs
    assert output.number_of_projection_time_steps == comparison.number_of_projection_time_steps
    assert output.number_of_simulations == comparison.number_of_simulations
    assert output.number_of_time_steps == comparison.number_of_time_steps
    assert output.output_ids == comparison.output_ids
    assert output.projection_dates == comparison.projection_dates
    assert output.time_step_dates == comparison.time_step_dates

    # Check simulation values for each output
    for output_id in output.output_ids:
        assert output.get_output_simulations(output_id) == pytest.approx(comparison.get_output_simulations(output_id))

def run_simulation_test(test_name):
    top_level_directory = get_tests_directory()
    simulation_tests_directory = os.path.join(top_level_directory, "test_files", "simulation_tests")
    test_directory = os.path.join(simulation_tests_directory, test_name)

    input_file_path = os.path.join(test_directory, 'input.json')
    comparison_file_path = os.path.join(test_directory, 'comparison.pyesg')

    assert os.path.exists(input_file_path), "Input pyESG config does not exist."
    assert os.path.exists(comparison_file_path), "Comparison pyESG file does not exist"

    # load config
    config = PyESGConfiguration.load_from_file(input_file_path)

    # update path so it runs in test directory and change output file name to "output"
    config.output_file_directory = test_directory
    config.output_file_name = "output"

    # Delete output file if it already exists
    output_file_path = os.path.join(config.output_file_directory, config.output_file_name + ".pyesg")
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    # Generate simulations from config
    generate_simulations(config)

    compare_pyesg_files(output_file_path, comparison_file_path)


def test_hull_white_annual_all_outputs():
    run_simulation_test("hull_white_annual_all_outputs")


import numpy as np

from pyesg.constants.outputs import TOTAL_RETURN_INDEX
from pyesg.simulation.models.base_model import BaseModel, BaseOutput


class BlackScholesOutputTotalReturnIndex(BaseOutput):
    """
    Output class for Total Return Index under Black Scholes model.
    """
    def initialise_output(self):
        self.sigma = self.model.asset_class.parameters.sigma

    def _calculate_values_for_batch(self, projection_step: int):
        random_samples = self.model.get_random_samples(projection_step, 0)
        exp_term = - 0.5 / self.settings.annualisation_factor * self.sigma * self.sigma \
                   + self.sigma / self.settings.annualisation_factor * random_samples
        return self.latest_projection_step_sims * np.exp(exp_term)


class BlackScholesModel(BaseModel):
    """
    Class for Black Scholes model.
    """
    output_class_mapping = {
       TOTAL_RETURN_INDEX: BlackScholesOutputTotalReturnIndex,
    }

import numpy as np

from pyesg.constants.outputs import TOTAL_RETURN_INDEX, DISCOUNT_FACTOR
from pyesg.simulation.models.base_model import BaseModel, BaseOutput


class BlackScholesOutputTotalReturnIndex(BaseOutput):
    """
    Output class for Total Return Index under Black Scholes model.
    """
    def initialise_output(self):
        self.sigma = self.model.asset_class.parameters.sigma
        self.discount_factor_output = self.get_or_create_output(
            output_type=DISCOUNT_FACTOR,
            asset_class_id=self.model.asset_class.dependencies[0]  # Nominal rates dependency
        )

    def _calculate_values_for_batch(self, projection_step: int):
        random_samples = self.model.get_random_samples(projection_step, 0)
        exp_term = - 0.5 / self.settings.annualisation_factor * self.sigma * self.sigma \
                   + self.sigma / self.settings.annualisation_factor * random_samples

        # Make sure discount factor calculated for this step and then get previous step too
        discount_factor_sims = self.discount_factor_output.calculate_for_batch(projection_step)
        discount_factor_sims_previous_step = self.discount_factor_output.previous_projection_step_sims

        # Calculate nominal rates growth component of TRI
        nominal_rate_growth = discount_factor_sims_previous_step / discount_factor_sims

        return self.latest_projection_step_sims * np.exp(exp_term) * nominal_rate_growth


class BlackScholesModel(BaseModel):
    """
    Class for Black Scholes model.
    """
    output_class_mapping = {
       TOTAL_RETURN_INDEX: BlackScholesOutputTotalReturnIndex,
    }

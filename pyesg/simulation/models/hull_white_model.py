import numpy as np

from pyesg.constants.outputs import BROWNIAN_MOTION, OU_PROCESS, DISCOUNT_FACTOR, CASH_ACCOUNT
from pyesg.simulation.models.base_model import BaseModel, BaseOutput
from pyesg.simulation.utils import extract_yield_curve_from_parameters


class HullWhiteOutputBrownianMotion(BaseOutput):
    """
    Output class for Brownian motion with unit variance for Hull-White model
    """
    def initialise_output(self):
        self.output.initial_value = 0.0

    def _calculate_values_for_batch(self, projection_step: int):
        random_samples = self.model.get_random_samples(projection_step, 0)
        return self.latest_projection_step_sims + np.sqrt(1.0 / self.settings.annualisation_factor) * random_samples


class HulllWhiteOutputOUProcess(BaseOutput):
    """
    Output class for OU process with 0 drift and initial value of 0.
    """
    def initialise_output(self):
        self.alpha = self.model.asset_class.parameters.alpha
        self.output.initial_value = 0.0

    def _calculate_values_for_batch(self, projection_step: int):
        random_samples = self.model.get_random_samples(projection_step, 0)
        time_step_length = 1.0 / self.settings.annualisation_factor
        previous_step_factor = np.exp(- time_step_length * self.alpha)
        increment_variance = (1.0 - np.exp(-2.0 * self.alpha * time_step_length)) / (2.0 * self.alpha)

        return previous_step_factor * self.latest_projection_step_sims + np.sqrt(increment_variance) * random_samples


class HullWhiteOutputDiscountFactor(BaseOutput):
    """
    Output class for the discount factor for the one-factor Hull-White model.
    """
    def initialise_output(self):
        self.alpha = self.model.asset_class.parameters.alpha
        self.sigma = self.model.asset_class.parameters.sigma

        self.brownian_motion_output = self.get_or_create_output(output_type=BROWNIAN_MOTION)
        self.ou_process_output = self.get_or_create_output(output_type=OU_PROCESS)

    def _calculate_values_for_batch(self, projection_step: int):
        time = projection_step / self.settings.annualisation_factor
        initial_yield_curve_point = self.model.yield_curve.get_rate(time)
        term_1 = (self.sigma * self.sigma) / (4 * self.alpha ** 3) * \
                   (2 * self.alpha * time - 3 + 4 * np.exp(- self.alpha * time) - np.exp(-2 * self.alpha * time))
        term_2 = self.sigma / self.alpha * self.brownian_motion_output.calculate_for_batch(projection_step)
        term_3 = - self.sigma / self.alpha * self.ou_process_output.calculate_for_batch(projection_step)

        zcb = np.exp(-time * initial_yield_curve_point)
        return zcb * np.exp(-(term_1 + term_2 + term_3))


class HullWhiteOutputCashAccount(BaseOutput):
    """
    Output class for the cash account for the one-factor Hull-White model
    """
    def initialise_output(self):
        self.discount_factor_output = self.get_or_create_output(output_type=DISCOUNT_FACTOR)

    def _calculate_values_for_batch(self, projection_step: int):
        return 1.0 / self.discount_factor_output.calculate_for_batch(projection_step)


class HullWhiteModel(BaseModel):
    """
    Class for one-factor Hull White model
    """
    def initialise_model(self):
        super().initialise_model()
        self.yield_curve = extract_yield_curve_from_parameters(self.asset_class.parameters)

    output_class_mapping = {
        BROWNIAN_MOTION: HullWhiteOutputBrownianMotion,
        OU_PROCESS: HulllWhiteOutputOUProcess,
        DISCOUNT_FACTOR: HullWhiteOutputDiscountFactor,
        CASH_ACCOUNT: HullWhiteOutputCashAccount,
    }

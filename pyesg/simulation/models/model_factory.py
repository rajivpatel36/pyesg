from pyesg.configuration.pyesg_configuration import AssetClass
from pyesg.constants.models import *
from pyesg.simulation.exceptions import ModelNotExistsError
from pyesg.simulation.models.base_model import BaseModel
from pyesg.simulation.models.black_scholes_model import BlackScholesModel
from pyesg.simulation.models.hull_white_model import HullWhiteModel
from pyesg.simulation.settings import InitialisedSettings

MODELS = {
    BLACK_SCHOLES: BlackScholesModel,
    HULL_WHITE: HullWhiteModel,

}


def get_model_for_asset_class(asset_class: AssetClass, settings: InitialisedSettings) -> BaseModel:
    cls = MODELS.get(asset_class.model_id)
    if not cls:
        raise ModelNotExistsError(f"{asset_class.model_id} model does not exist.")
    return cls(settings=settings, asset_class=asset_class)
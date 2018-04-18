from pyesg.configuration.pyesg_configuration import Parameters
from pyesg.yield_curve.yield_curve import YieldCurve


def extract_yield_curve_from_parameters(parameters: Parameters) -> YieldCurve:
    """
    Extracts the yield curve from a set of parameters and returns a YieldCurve object.
    Args:
        parameters: The parameters from which to extract the yield curve.

    Returns:
        The yield curve object that represents the yield curve specified by the supplied parameters.

    Points on the yield curve are specified as a key, value pair in `parameters` where the key is of the form
    "yc_{term}" and the value is the continuously compounded short rate associated with the term.
    """
    yield_curve = YieldCurve()
    yc_prefix = "yc_"
    for key, value in parameters.__dict__.items():
        if key.lower().startswith("yc_"):
            term = float(key.split(yc_prefix)[1])
            yield_curve.add_point(term, value)
    return yield_curve

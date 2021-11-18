
from PyDSS.dssTransformer import dssTransformer
from PyDSS.dssElement import dssElement


def create_dss_element(element_class, element_name):
    """Instantiate the correct class for the given element_class and element_name."""
    if element_class == "Transformer":
        return dssTransformer()
    else:
        return dssElement()

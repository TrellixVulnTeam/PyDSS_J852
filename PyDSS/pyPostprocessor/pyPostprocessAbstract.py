class AbstractPostprocess:
    """An abstract class that serves as template for all pyPlot classes in :mod:`PyDSS.pyPlots.Plots` module.

    :param dssInstance: A :class:`PyDSS.dssElement.dssElement` object that wraps around an OpenDSS 'Fault' element
    :type dssInstance: dict
    :param dssBuses: Dictionary of all :class:`PyDSS.dssBus.dssBus` objects in PyDSS
    :type dssBuses: dict of :class:`PyDSS.dssBus.dssBus` objects
    :param dssObjects: Dictionary of all :class:`PyDSS.dssElement.dssElement` objects in PyDSS
    :type dssObjects: dict of :class:`PyDSS.dssElement.dssElement` objects
    :param dssObjectsByClass:  Dictionary of all :class:`PyDSS.dssElement.dssElement` objects in PyDSS sorted by class
    :type dssObjectsByClass: dict of :class:`PyDSS.dssElement.dssElement` objects
    :param dssSolver: An instance of one of the classes defined in :mod:`PyDSS.SolveMode`.
    :type dssSolver: :mod:`PyDSS.SolveMode`

    """

    def __init__(self, dssInstance, dssSolver, dssObjects, dssObjectsByClass, simulationSettings):
        """This is the constructor class.
        """

    def run(self, step, stepMax):
        """Method used to run a post processing script.
        """
        pass
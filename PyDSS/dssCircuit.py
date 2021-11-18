import opendssdirect as dss

from PyDSS.dssObjectBase import dssObjectBase

class dssCircuit(dssObjectBase):

    VARIABLE_OUTPUTS_BY_LABEL = {}
    VARIABLE_OUTPUTS_BY_LIST = (
        "AllBusMagPu",
    )
    VARIABLE_OUTPUTS_COMPLEX = (
        "LineLosses",
        "Losses",
        "SubstationLosses",
        "TotalPower",
    )

    def __init__(self):
        name = dss.Circuit.Name()
        fullName = "Circuit." + name
        self._Class = 'Circuit'
        super(dssCircuit, self).__init__(name, fullName)

        CktElmVarDict = dss.Circuit.__dict__
        for key in CktElmVarDict.keys():
            try:
                self._Variables[key] = getattr(dss.Circuit, key)
            except:
                self._Variables[key] = None

    def SetActiveObject(self):
        pass

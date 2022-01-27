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
    UNITS={
        "LineLosses": {
            "is_complex": True,
            "units": ['VA']
        },
        "Losses": {
            "is_complex": True,
            "units": ['VA']
        },
        "SubstationLosses": {
            "is_complex": True,
            "units": ['VA']
        },
        "TotalPower": {
            "is_complex": True,
            "units": ['kVA']
        },
    }

    def __init__(self, dssInstance):
        name = dssInstance.Circuit.Name()
        fullName = "Circuit." + name
        self._Class = 'Circuit'
        super(dssCircuit, self).__init__(dssInstance, name, fullName)

        CktElmVarDict = dssInstance.Circuit.__dict__
        for key in CktElmVarDict.keys():
            try:
                self._Variables[key] = getattr(dssInstance.Circuit, key)
            except:
                self._Variables[key] = None

    def SetActiveObject(self):
        pass

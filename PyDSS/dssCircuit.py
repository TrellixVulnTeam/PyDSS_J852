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

        dssInstance.Circuit.SetActiveElement("Vsource.source")
        self._NumTerminals = dssInstance.CktElement.NumTerminals()
        self._NumConductors = dssInstance.CktElement.NumConductors()
        self._NumPhases = dssInstance.CktElement.NumPhases()
        nodes = dssInstance.CktElement.NodeOrder()
        n = self._NumConductors
        self._Nodes = [nodes[i * n:(i + 1) * n] for i in range((len(nodes) + n - 1) // n)]
        
        super(dssCircuit, self).__init__(dssInstance, name, fullName)

        CktElmVarDict = dssInstance.Circuit.__dict__
        for key in CktElmVarDict.keys():
            try:
                self._Variables[key] = getattr(dssInstance.Circuit, key)
            except:
                self._Variables[key] = None

    def SetActiveObject(self):
        pass

    @property
    def Conductors(self):
        letters = 'ABCN'
        return [letters[i] for i in range(self._NumConductors)]

    @property
    def ConductorByTerminal(self):
        return [f"{j}{i}" for i in self.Conductors for j in self.Terminals]

    @property
    def NodeOrder(self):
        return self._NodeOrder[:]

    @property
    def NumPhases(self):
        return self._NumPhases

    @property
    def NumConductors(self):
        return self._NumConductors

    @property
    def NumTerminals(self):
        return self._NumTerminals

    @property
    def Terminals(self):    
        return list(range(1, self._NumTerminals + 1))


import opendssdirect as dss

from PyDSS.dssObjectBase import dssObjectBase


class dssBus(dssObjectBase):

    VARIABLE_OUTPUTS_BY_LABEL = {
        "PuVoltage": {
            "is_complex": True,
            "units": ['[pu]']
        },
        "SeqVoltages": {
            "is_complex": False,
            "units": ['[kV]', '[Deg]']
        },
        "CplxSeqVoltages": {
            "is_complex": True,
            "units": ['[kV]']
        },
        "VMagAngle": {
            "is_complex": False,
            "units": ['[kV]', '[Deg]']
        },
        "Voc": {
            "is_complex": True,
            "units": ['[kV]']
        },
        "Voltages": {
            "is_complex": True,
            "units": ['[kV]']
        },
        "puVmagAngle": {
            "is_complex": False,
            "units":  ['[pu]', '[Deg]']

        },
        "Isc": {
            "is_complex": True,
            "units": ['[Amps]']

        },

    }
    VARIABLE_OUTPUTS_COMPLEX = ()

    def __init__(self):
        name = dss.Bus.Name()
        super(dssBus, self).__init__(name, name)
        self._Index = None
        self.XY = None
        self._Class = 'Bus'
        #  self._Nodes is nested in a list to be consistent with dssElement._Nodes
        self._Nodes = [dss.Bus.Nodes()]
        self._NumTerminals = 1
        self._NumConductors = len(dss.Bus.Nodes())
        self.Distance = dss.Bus.Distance()
        BusVarDict = dss.Bus.__dict__
        for key in BusVarDict.keys():
            try:
                self._Variables[key] = getattr(dss.Bus, key)
            except:
                self._Variables[key] = None
        if self.GetVariable('X') is not None:
            self.XY = [self.GetVariable('X'), self.GetVariable('Y')]
        else:
            self.XY = [0, 0]

    @property
    def NumConductors(self):
        return self._NumConductors

    @property
    def NumPhases(self):
        return len(self._Nodes)

    @property
    def Phases(self):
        return self._Nodes[:]

    def SetActiveObject(self):
        if dss.Bus.Name() != self._Name:
            dss.Circuit.SetActiveBus(self._Name)

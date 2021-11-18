import ast

import opendssdirect as dss

from PyDSS.dssBus import dssBus
from PyDSS.dssObjectBase import dssObjectBase
from PyDSS.exceptions import InvalidParameter
from PyDSS.value_storage import ValueByNumber

class dssElement(dssObjectBase):

    VARIABLE_OUTPUTS_BY_LABEL = {
        "Currents": {
            "is_complex": True,
            "units": ['[Amps]']
        },
        "CurrentsMagAng": {
            "is_complex": False,
            "units" : ['[Amps]', '[Deg]']
        },
        "Powers": {
            "is_complex": True,
            "units": ['[kVA]']
        },
        "Voltages": {
            "is_complex": True,
            "units": ['[kV]']
        },
        'VoltagesMagAng': {
            "is_complex": False,
            "units": ['[kV]', '[Deg]']
        },
        'CplxSeqCurrents': {
            "is_complex": True,
            "units": ['[Amps]']
        },
        'SeqCurrents': {
            "is_complex": False,
            "units": ['[Amps]', '[Deg]']
        },
        'SeqPowers': {
            "is_complex": False,
            "units": ['[kVA]', '[Deg]']
        }
    }

    VARIABLE_OUTPUTS_COMPLEX = (
        "Losses",
    )

    _MAX_CONDUCTORS = 4

    def __init__(self):
        fullName = dss.Element.Name()
        if dss.CktElement.Name() != fullName:
            raise Exception(f"name mismatch {dss.CktElement.Name()} {fullName}")

        self._Class, name = fullName.split('.', 1)
        super(dssElement, self).__init__(name, fullName)
        self._Enabled = dss.CktElement.Enabled()
        if not self._Enabled:
            return

        self._Parameters = {}
        self._NumTerminals = dss.CktElement.NumTerminals()
        self._NumConductors = dss.CktElement.NumConductors()

        assert self._NumConductors <= self._MAX_CONDUCTORS, str(self._NumConductors)
        self._NumPhases = dss.CktElement.NumPhases()

        n = self._NumConductors
        nodes = dss.CktElement.NodeOrder()
        self._Nodes = [nodes[i * n:(i + 1) * n] for i in range((len(nodes) + n - 1) // n)]

        assert len(nodes) == self._NumTerminals * self._NumConductors, \
            f"{self._Nodes} {self._NumTerminals} {self._NumConductors}"


        PropertiesNames = dss.Element.AllPropertyNames()
        AS = range(len(PropertiesNames))
        for i, PptName in zip(AS, PropertiesNames):
            self._Parameters[PptName] = str(i)

        CktElmVarDict = dss.CktElement.__dict__
        for VarName in dss.CktElement.AllVariableNames():
            CktElmVarDict[VarName] = None

        for key in CktElmVarDict.keys():
            try:
                self._Variables[key] = getattr(dss.CktElement, key)
            except:
                self._Variables[key] = None
        self.Bus = dss.CktElement.BusNames()
        self.BusCount = len(self.Bus)
        self.sBus = []
        for BusName in self.Bus:
            dss.Circuit.SetActiveBus(BusName)
            self.sBus.append(dssBus())

    def GetInfo(self):
        return self._Class, self._Name

    def IsValidAttribute(self, VarName):
        # Overridden from base because dssElement has Parameters.
        if VarName in self._Variables:
            return True
        elif VarName in self._Parameters:
            return True
        else:
            return False

    def DataLength(self, VarName):
        if VarName in self._Variables:
            VarValue = self.GetVariable(VarName)
        elif VarName in self._Parameters:
            VarValue = self.GetParameter(VarName)
        else:
            return 0, None

        if  isinstance(VarValue, list):
            return len(VarValue), 'List'
        elif isinstance(VarValue, str):
            return 1, 'String'
        elif isinstance(VarValue, int or float or bool):
            return 1, 'Number'
        else:
            return 0, None

    def GetValue(self, VarName, convert=False):
        if dss.Element.Name() != self._FullName:
            self.SetActiveObject()
        if VarName in self._Variables:
            VarValue = self.GetVariable(VarName, convert=convert)
        elif VarName in self._Parameters:
            VarValue = self.GetParameter(VarName)
            if convert:
                VarValue = ValueByNumber(self._FullName, VarName, VarValue)
        else:
            return None
        return VarValue

    def SetActiveObject(self):
        dss.Circuit.SetActiveElement(self._FullName)
        if dss.CktElement.Name() != dss.Element.Name():
            raise InvalidParameter('Object is not a circuit element')

    def SetParameter(self, Param, Value):
        reply = dss.utils.run_command(self._FullName + '.' + Param + ' = ' + str(Value))
        if reply != "":
            raise Exception(f"SetParameter failed: {reply}")
        return self.GetParameter(Param)

    def GetParameter(self, Param):
        if dss.Element.Name() != self._FullName:
            dss.Circuit.SetActiveElement(self._FullName)
        if dss.Element.Name() == self._FullName:
            # This always returns a string.
            # The real value could be a number, a list of numbers, or a string.
            x = dss.Properties.Value(Param)
            try:
                return float(x)
            except ValueError:
                try:
                    return ast.literal_eval(x)
                except (SyntaxError, ValueError):
                    return x
        else:
            return None

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

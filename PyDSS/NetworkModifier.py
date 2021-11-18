import opendssdirect as dss

import PyDSS.dssElement as dE
from PyDSS.pyLogger import getLoggerTag
import logging


class Modifier():

    PV_defaultDict = {'phases':'1', 'kV':'2.2',  'irradiance':'1', 'Temperature':'30',
                      'daily':'m3pvmult', '%cutin':'0.0', '%cutout':'0.0'}

    Storge_defaultDict = {'bus' : 'storagebus', 'kV':'0.48', 'kWRated' : '2000', '%IdlingkW' : '3' ,
                          'phases':'3', '%EffCharge': '100', 'kWhRated'  : '2000', '%reserve': '0',
                          '%EffDischarge': '100', 'state': 'IDLE', '%stored' : '50'}

    DefaultDictSelector ={
        'PVSystem' : PV_defaultDict,
        'Storage'  : Storge_defaultDict,
     }

    def __init__(self, run_command, SimulationSettings):
        LoggerTag = getLoggerTag(SimulationSettings)
        self.pyLogger = logging.getLogger(LoggerTag)
        self.__dssCircuit = dss.Circuit
        self.__dssElement = dss.Element
        self.__dssBus = dss.Bus
        self.__dssClass = dss.ActiveClass
        self.__dssCommand = run_command

    def Add_Elements(self, Class, Properties, Add2dssObjects = False, dssObjects = None):
        DefaultDict  =  self.DefaultDictSelector[Class]
        ElmNames = []
        Values = []

        for key, ValueList in Properties.items():
            ElmNames.append(key)
            Values.append(ValueList)

        for i in range(len(Values[0])):
            ElementName= Properties['bus'][i]
            ElementName = ElementName if '.' not in ElementName else ElementName.replace('.','_')
            for j in range(len(Values)):
                DefaultDict[ElmNames[j]] = Values[j][i]
            Obj = self.Add_Element(Class, ElementName, DefaultDict)
            if Add2dssObjects is True:
                dssObjects[Class + '.' + ElementName] = Obj

    def Add_Element(self, Class, Name, Properties):
        Cmd = 'New ' + Class + '.' + Name
        for PptyName, PptyVal in Properties.items():
            if PptyVal is not None:
                tCMD = ' ' + PptyName + '=' + PptyVal
                Cmd += tCMD
        self.pyLogger.info('Added -> ' + Cmd)
        self.__dssCommand(Cmd)
        return dE.dssElement(dss)

    def Edit_Element(self, Class, Name, Properties):
        Cmd = 'Edit ' + Class + '.' + Name
        for PptyName, PptyVal in Properties.items():
            if PptyVal is not None:
                tCMD = ' ' + PptyName + '=' + str(PptyVal)
                Cmd += tCMD
        self.__dssCommand(Cmd)
        self.pyLogger.info('Edited -> ' + Cmd)
        return

    def Edit_Elements(self, Class, Property=None, Value=None):
        dss.Circuit.SetActiveClass(Class)
        Element = dss.ActiveClass.First()
        while Element:
            ElmName = dss.ActiveClass.Name()
            dss.utils.run_command(Class + '.' + ElmName + '.' + Property + ' = ' + str(Value))
            Element = dss.ActiveClass.Next()



import LoadController
import StorageController
from dssElement import dssElement

ControllerTypes ={
    'Load Controller'   : LoadController.LoadController,
    'Storage Controller': StorageController.StorageController
}


def Create(ElmName, ControllerType, Settings, ElmObjectList, dssInstance, dssSolver):
    try:
        relObject = ElmObjectList[ElmName]
    except:
        Index = dssInstance.Circuit.SetActiveElement(ElmName)
        if int(Index) >= 0:
            ElmObjectList[ElmName] = dssElement(dssInstance)
            relObject = ElmObjectList[ElmName]
        else:
            print ('The object dictionary does not contain ' + ElmName)
            return -1
    # try:
    #     print('sdfsdfasdfasdf')
    ObjectController = ControllerTypes[ControllerType](relObject, Settings, dssInstance, ElmObjectList, dssSolver)
    # except:
    #     print ('The controller dictionary does not contain ' + ControllerType)
    #     return -1
    return ObjectController
from multiprocessing import Pool
import dssInstance
import logging
import time
import os

def pyDSSinstance(Scenario):
    # Settings for exporting results
    RO = {
        'Log Results'    : True,
        'Export Mode'    : 'byElement',           # 'byClass'        , 'byElement'
        'Export Style'   : 'Single file',         # 'Seperate files' , 'Single file'
    }
    # Plot Settings
    PO = {
        'Network layout' : False,
        'Time series'    : False,
        'XY plot'        : False,
        'Sag plot'       : False,
        'Histogram'      : False,
        'GIS overlay'    : False,
    }
    # Simulation Settings
    SS = {
        'Start Day'              : 4,
        'End Day'                : 5,
        'Step resolution (min)'  : 15,
        'Max Control Iterations' : 10,
        'Simulation Type'        : 'Daily',
        'Active Project'         : 'HECO',
        'Active Scenario'        : Scenario,
        'DSS File'               : 'MasterCircuit_Mikilua_baseline3.dss',   #'MasterCircuit_Mikilua_keep.dss'
    }
    # Logger settings
    LO =  {
        'Logging Level'          : logging.DEBUG,
        'Log to external file'   : True,
        'Display on screen'      : True
    }

    DSS = dssInstance.OpenDSS(PlotOptions = PO , ResultOptions=RO, SimulationSettings=SS, LoggerOptions=LO)
    DSS.RunSimulation()

    os.system('pause')
    DSS.DeleteInstance()
    return

if __name__ == '__main__':
    Scenarios = ['HP-VV', 'HP-VW']
    pool = Pool(processes=len(Scenarios))
    pool.map(pyDSSinstance, Scenarios)

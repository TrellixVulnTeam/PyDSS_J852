from PyDSS.dssInstance import OpenDSS
from PyDSS.api.src.web.parser import restructure_dictionary
from PyDSS.api.src.app.DataWriter import DataWriter
from PyDSS.simulation_input_models import SimulationSettingsModel, load_simulation_settings

import logging
import toml
import time
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def run_test(tomlpath):
    try:
        settings = load_simulation_settings(Path(tomlpath))
    except Exception as e:
        logger.error(f"Invalid simulation settings passed, {e}")
        return

    pydss_obj = OpenDSS(settings)
    export_path = os.path.join(pydss_obj._dssPath['Export'], settings.project.active_scenario)
    Steps, sTime, eTime = pydss_obj._dssSolver.SimulationSteps()
    writer = DataWriter(export_path, format="json", columnLength=Steps)

    st = time.time()
    for i in range(Steps):
        results = pydss_obj.RunStep(i)
        restructured_results = {}
        for k, val in results.items():
            if "." not in k:
                class_name = "Bus"
                elem_name = k
            else:
                class_name, elem_name = k.split(".")

            if class_name not in restructured_results:
                restructured_results[class_name] = {}
            if not isinstance(val, complex):
                restructured_results[class_name][elem_name] = val
        writer.write(
            pydss_obj._Options["Helics"]["Federate name"],
            pydss_obj._dssSolver.GetTotalSeconds(),
            restructured_results,
            i
        )
    logger.debug("{} seconds".format(time.time() - st))

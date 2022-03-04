"""Logic to determine snapshot time point by mode"""

import logging
import os
from pathlib import Path
import pandas as pd
import opendssdirect as dss
import numpy as np
from PyDSS.common import SnapshotTimePointSelectionMode
from PyDSS.utils.simulation_utils import create_loadshape_pmult_dataframe_for_simulation
from PyDSS.utils.utils import dump_data
from PyDSS.reports.reports import logger
from PyDSS.simulation_input_models import SimulationSettingsModel


logger = logging.getLogger(__name__)


def get_snapshot_timepoint(settings: SimulationSettingsModel, mode: SnapshotTimePointSelectionMode):
    aggregate_pv_timepoints_flag = True
    individual_pv_timepoints_flag = False
    pv_systems = dss.PVsystems.AllNames()
    if not pv_systems:
        logger.info("No PVSystems are present.")
        if mode != SnapshotTimePointSelectionMode.MAX_LOAD:
            mode = SnapshotTimePointSelectionMode.MAX_LOAD
            logger.info("Changed mode to %s", SnapshotTimePointSelectionMode.MAX_LOAD.value)
    if mode == SnapshotTimePointSelectionMode.MAX_LOAD:
        column = "Max Load"
    elif mode == SnapshotTimePointSelectionMode.MAX_PV_LOAD_RATIO:
        column = "Max PV to Load Ratio"
    elif mode == SnapshotTimePointSelectionMode.DAYTIME_MIN_LOAD:
        column = "Min Daytime Load"
    elif mode == SnapshotTimePointSelectionMode.MAX_PV_MINUS_LOAD:
        column = "Max PV minus Load"
    elif mode == SnapshotTimePointSelectionMode.INDIVIDUAL_PV_TIMEPOINTS:
        individual_pv_timepoints_flag = True
        aggregate_pv_timepoints_flag = False
    else:
        assert False, f"{mode} is not supported"

    temp_filename = settings.project.project_path / settings.project.active_project / "Exports" / ".snapshot_time_points.json"
    final_filename = settings.project.project_path / settings.project.active_project / "Exports" / "snapshot_time_points.json"
    if temp_filename.exists():
        timepoints = pd.read_json(temp_filename)
        if settings.project.active_scenario == settings.project.scenarios[-1].name:
            os.rename(temp_filename, final_filename)
        return pd.to_datetime(timepoints[column][0]).to_pydatetime()
    pv_generation_hours = {'start_time': '8:00', 'end_time': '17:00'}
    aggregate_profiles = pd.DataFrame(columns=['Load', 'PV'])
    pv_shapes = {}
    individual_pv_profiles = pd.DataFrame()
    for pv_name in pv_systems:
        dss.PVsystems.Name(pv_name)
        pmpp = float(dss.Properties.Value('Pmpp'))
        profile_name = dss.Properties.Value('yearly')
        dss.LoadShape.Name(profile_name)
        if profile_name not in pv_shapes.keys():
            pv_shapes[profile_name] = create_loadshape_pmult_dataframe_for_simulation(settings)
        if individual_pv_timepoints_flag:
            individual_pv_profiles[pv_name] =  (pv_shapes[profile_name] * pmpp)[0]
        if len(aggregate_profiles) == 0:
            aggregate_profiles['PV'] = (pv_shapes[profile_name] * pmpp)[0]
            aggregate_profiles = aggregate_profiles.replace(np.nan, 0)
        else:
            aggregate_profiles['PV'] = aggregate_profiles['PV'] + (pv_shapes[profile_name] * pmpp)[0]
    del pv_shapes
    loads = dss.Loads.AllNames()
    if not loads:
        logger.info("No Loads are present")
    load_shapes = {}
    individual_load_profiles = pd.DataFrame()
    for load_name in loads:
        dss.Loads.Name(load_name)
        kw = float(dss.Properties.Value('kW'))
        profile_name = dss.Properties.Value('yearly')
        dss.LoadShape.Name(profile_name)
        if profile_name not in load_shapes.keys():
            load_shapes[profile_name] = create_loadshape_pmult_dataframe_for_simulation(settings)
        if individual_pv_timepoints_flag:
            individual_load_profiles[load_name] =  (load_shapes[profile_name] * kw)[0]
        if len(aggregate_profiles) == 0:
            aggregate_profiles['Load'] = (load_shapes[profile_name] * kw)[0]
        else:
            aggregate_profiles['Load'] = aggregate_profiles['Load'] + (load_shapes[profile_name] * kw)[0]
    del load_shapes
    if pv_systems:
        aggregate_profiles['PV to Load Ratio'] = aggregate_profiles['PV'] / aggregate_profiles['Load']
        aggregate_profiles['PV minus Load'] = aggregate_profiles['PV'] - aggregate_profiles['Load']

    timepoints = pd.DataFrame(columns=['Timepoints'])
    timepoints.loc['Max Load'] = aggregate_profiles['Load'].idxmax()
    if pv_systems:
        if individual_pv_timepoints_flag:
            max_pv_individual_timepoint = individual_pv_profiles.between_time(pv_generation_hours['start_time'],
                                                                    pv_generation_hours['end_time'])['PV'].idxmax()  # returns the index for the maximum value in each column
            # TODO need a mapping between load and PV to create ratio - then compute max timepoint for that
            
            
        if aggregate_pv_timepoints_flag:
            timepoints.loc['Max PV to Load Ratio'] = aggregate_profiles.between_time(pv_generation_hours['start_time'],
                                                                                    pv_generation_hours['end_time'])['PV to Load Ratio'].idxmax()
            timepoints.loc['Max PV minus Load'] = aggregate_profiles.between_time(pv_generation_hours['start_time'],
                                                                                pv_generation_hours['end_time'])['PV minus Load'].idxmax()
            timepoints.loc['Max PV'] = aggregate_profiles.between_time(pv_generation_hours['start_time'],
                                                                    pv_generation_hours['end_time'])['PV'].idxmax()
    timepoints.loc['Min Load'] = aggregate_profiles['Load'].idxmin()
    timepoints.loc['Min Daytime Load'] = aggregate_profiles.between_time(pv_generation_hours['start_time'],
                                                                         pv_generation_hours['end_time'])['Load'].idxmin()
    logger.info("Time points: %s", {k: str(v) for k, v in timepoints.to_records()})
    dump_data(timepoints.astype(str).to_dict(orient='index'), temp_filename, indent=2)
    if settings.project.active_scenario == settings.project.scenarios[-1].name:
        os.rename(temp_filename, final_filename)
    return timepoints.loc[column][0].to_pydatetime()

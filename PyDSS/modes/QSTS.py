from datetime import timedelta

import opendssdirect as dss

from PyDSS.modes.solver_base import SolverBase
from PyDSS.simulation_input_models import ProjectModel
from PyDSS.utils.dss_utils import get_load_shape_resolution_secs


class QSTS(SolverBase):
    def __init__(self, settings: ProjectModel):
        super().__init__(settings)
        dss.Solution.Mode(2)
        dss.run_command('Set ControlMode={}'.format(settings.control_mode.value))
        dss.Solution.Number(1)
        dss.Solution.StepSize(self._sStepRes)
        dss.Solution.MaxControlIterations(settings.max_control_iterations)

        start_time_hours = self._Hour + self._Second / 3600.0
        load_shape_resolutions_secs = get_load_shape_resolution_secs()
        if load_shape_resolutions_secs == self._sStepRes:
            # I don't know why this is needed in this case.
            # The first data point gets skipped without it.
            # FIXME
            start_time_hours += self._sStepRes / 3600.0
        dss.Solution.DblHour(start_time_hours)
        return

    def SolveFor(self, mStartTime, mTimeStep):
        Hour = int(mStartTime/60)
        Min = mStartTime%60
        dss.Solution.DblHour(Hour + Min / 60.0)
        dss.Solution.Number(mTimeStep)
        dss.Solution.Solve()
        return dss.Solution.Converged()

    def IncStep(self):
        dss.Solution.StepSize(self._sStepRes)
        dss.Solution.Solve()
        self._Time = self._Time + timedelta(seconds=self._sStepRes)
        self._Hour = int(dss.Solution.DblHour() // 1)
        self._Second = (dss.Solution.DblHour() % 1) * 60 * 60
        return dss.Solution.Converged()

    def reSolve(self):
        dss.Solution.StepSize(0)
        dss.Solution.SolveNoControl()
        return dss.Solution.Converged()

    def Solve(self):
        dss.Solution.StepSize(0)
        dss.Solution.Solve()
        return dss.Solution.Converged()

    def setMode(self, mode):
        dss.utils.run_command('Set Mode={}'.format(mode))
        if mode.lower() == 'yearly':
            dss.Solution.Mode(2)
            dss.Solution.DblHour(self._Hour + self._Second / 3600.0)
            dss.Solution.Number(1)
            dss.Solution.StepSize(self._sStepRes)
            dss.Solution.MaxControlIterations(self._settings.max_control_iterations)

    def reset(self):
        assert False, "not supported"

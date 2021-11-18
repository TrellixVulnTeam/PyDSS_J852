from datetime import timedelta
import math

from PyDSS.modes.solver_base import SolverBase
from PyDSS.simulation_input_models import ProjectModel


class Dynamic(SolverBase):
    def __init__(self, settings: ProjectModel):
        super().__init__(settings)
        self.setMode('Dynamic')
        dss.run_command('Set ControlMode={}'.format(settings.project.control_mode.value))
        dss.Solution.Number(1)
        dss.Solution.StepSize(self._sStepRes)
        dss.Solution.MaxControlIterations(settings.max_control_iterations)
        dss.Solution.DblHour(self._Hour + self._Second / 3600.0)
        return

    def setFrequency(self, frequency):
        dss.Solution.Frequency(frequency)
        return

    def getFrequency(self):
        return dss.Solution.Frequency()

    def SimulationSteps(self):
        Seconds = (self._EndTime - self._StartTime).total_seconds()
        Steps = math.ceil(Seconds / self._sStepRes)
        return Steps, self._StartTime, self._EndTime

    def GetOpenDSSTime(self):
        return dss.Solution.DblHour()

    def reset(self):
        self.setMode('Dynamic')
        dss.Solution.Hour(self._Hour)
        dss.Solution.Seconds(self._Second)
        dss.Solution.Number(1)
        dss.Solution.StepSize(self._sStepRes)
        dss.Solution.MaxControlIterations(self._settings.max_control_iterations)
        return

    def SolveFor(self, mStartTime, mTimeStep):
        Hour = int(mStartTime/60)
        Min = mStartTime % 60
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
        self.pyLogger.debug('OpenDSS time [h] - ' + str(dss.Solution.DblHour()))
        self.pyLogger.debug('PyDSS datetime - ' + str(self._Time))
        return dss.Solution.Converged()

    def reSolve(self):
        dss.Solution.StepSize(0)
        dss.Solution.SolveNoControl()
        return dss.Solution.Converged()

    def Solve(self):
        dss.Solution.StepSize(0)
        dss.Solution.Solve()
        return dss.Solution.Converged()

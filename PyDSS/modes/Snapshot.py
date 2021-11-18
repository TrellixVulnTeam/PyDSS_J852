import opendssdirect as dss

from PyDSS.modes.solver_base import SolverBase
from PyDSS.simulation_input_models import ProjectModel


class Snapshot(SolverBase):
    def __init__(self, settings: ProjectModel):
        super().__init__(settings)
        dss.Solution.Mode(0)
        dss.utils.run_command('Set ControlMode={}'.format(settings.control_mode.value))
        dss.Solution.MaxControlIterations(settings.max_control_iterations)
        return

    def reSolve(self):
        dss.Solution.SolveNoControl()
        return dss.Solution.Converged()

    def SimulationSteps(self):
        return 1, self._StartTime, self._EndTime

    def Solve(self):
        dss.Solution.Solve()
        return dss.Solution.Converged()

    def IncStep(self):
        return dss.Solution.Solve()

    def SolveFor(self):
        assert False

    def reset(self):
        assert False

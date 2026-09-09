"""WorkChain to launch MACE training for a committee of potentials."""

from aiida import load_profile
from aiida_trainspot.engines.workflows.train import TrainWorkChain

from ..calculations.train import MaceTrainCalculation

load_profile()


class MaceTrainWorkChain(TrainWorkChain):
    """WorkChain to launch MACE training."""

    _process_class = MaceTrainCalculation

    def restart_from(self, calculation):
        """Resume in place from the previous calculation's remote folder.

        MACE can restart symlinking the remote scratch directory of the previous calculation,
        avoiding a costly re-upload of datasets/checkpoints already present on the remote computer.

        :param calculation: node from the previous calculation
        """
        self.ctx.inputs.parent_folder = calculation.outputs.remote_folder

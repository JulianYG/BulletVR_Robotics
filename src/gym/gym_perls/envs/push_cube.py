# !/usr/bin/env python

from .perls_env import PerlsEnv
from lib.utils import math_util

# TODO: register gym env
# TODO: cutoff demons when cube z pos decreases??


class PushCube(PerlsEnv):
    """
    Pushing cube across the table
    """

    metadata = {
        'render.modes': ['human', 'depth', 'segment'],
        'video.frames_per_second': 50
    }

    def __init__(self, conf_path):

        super(PushCube, self).__init__(conf_path)
        self._cube = self._world.body['cube_0']
        self._robot = self._world.tool['m0']
        self._table = self._world.body['table_0']

    @property
    def action_space(self):
        """
        Get the space of actions in the environment
        :return: Space object
        """
        return NotImplemented

    @property
    def state(self):
        # arm_state = self._robot.joint_positions + self._robot.joint_velocities
        eef_pos, _ = math_util.get_relative_pose(
            self._robot.eef_pose, self._robot.pose)
        cube_pos, cube_orn = self._cube.get_pose(self._robot.uid, 0)
        return math_util.concat(eef_pos, cube_pos, cube_orn)

    def _reset(self):

        super(PushCube, self)._reset()
        self._display.set_render_view(
            dict(
                dim=(256, 256),
                flen=3,
                yaw=50,
                pitch=-35,
                focus=(0, 0, 0)
            )
        )

        cube_pos = self._cube.pos

        # Enable torque control by disable the motors first
        # As required by bullet
        # self._robot.torque_mode()

        self._robot.grasp()

        # Use the steps to finish other simulation steps as well
        self._robot.tool_pos = \
                ((cube_pos[0] - 0.05, cube_pos[1], cube_pos[2] + 0.025), 600)

        return self.state

    def _step(self, action):
        raise NotImplementedError

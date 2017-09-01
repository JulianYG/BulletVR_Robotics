# !/usr/bin/env python

from .push_cube import PushCube
from lib.utils import math_util


class PushCubePose(PushCube):
    """
    Pushing cube across the table
    """

    metadata = {
        'render.modes': ['human', 'depth', 'segment'],
        'video.frames_per_second': 50
    }

    def __init__(self, conf_path):

        super(PushCubePose, self).__init__(conf_path)

    @property
    def observation_space(self):
        return PushCube.Space.box(
            low=math_util.concat(
                self._robot.pos - math_util.vec((1.5, 1.5, 1.5)),
                self._table.pos - math_util.vec((.275, .275, -.63)),
                math_util.vec((-1, -1, -1, -1))
            ),
            high=math_util.concat(
                self._robot.pos + math_util.vec((1.5, 1.5, 1.5)),
                self._table.pos + math_util.vec((.275, .275, .69)),
                math_util.vec((1, 1, 1, 1))
            )
        )

    @property
    def action_space(self):

        # No large movements
        return PushCube.Space.Box(
            low=-math_util.vec((0.05, 0.05, 0.05)),
            high=math_util.vec((0.05, 0.05, 0.05))
        )

    def _step_helper(self, action):

        # Use end effector delta pose with iterations

        ### Note: the action received is delta end effector 
        # position in robot base frame, so need to apply a
        # transfer from current world frame eef pose to robot 
        # base frame, in order to add with delta,
        # then transfer the sum back to abs world frame.

        eef_bframe_pos, eef_bframe_orn = math_util.get_relative_pose(
            self._robot.eef_pose, self._robot.pose
        )

        eef_bframe_pos += math_util.vec(action)
        eef_wframe_pose = math_util.get_absolute_pose(
            (eef_bframe_pos, eef_bframe_orn), 
            self._robot.pose
        )

        self._robot.set_eef_pose(
            eef_wframe_pose[0],
            None, iters=-1
        )
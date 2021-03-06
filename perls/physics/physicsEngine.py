#!/usr/bin/env/ python

import numpy as np
import logging

import os.path as osp
import pybullet as p

from .stateEngine import FakeStateEngine
from ..utils import math_util
from ..utils.io_util import pjoin, PerlsLogger

__author__ = 'Julian Gao'
__email__ = 'julianyg@stanford.edu'
__license__ = 'private'
__version__ = '0.1'

logging.setLoggerClass(PerlsLogger)


class MujocoEngine(FakeStateEngine):
    pass


class BulletPhysicsEngine(FakeStateEngine):
    """
    Bullet Physics simulation engine.
    """

    JOINT_TYPES = {
        0: 'revolute', 1: 'prismatic', 2: 'spherical',
        3: 'planar', 4: 'fixed',
        5: 'point2point', 6: 'gear'}

    _INV_JOINT_TYPES = \
        dict(revolute=0, prismatic=1, spherical=2,
             planar=3, fixed=4, point2point=5, gear=6)

    SHAPE_TYPES = {
        2: 'sphere', 3: 'box', 4: 'cylinder',
        5: 'mesh', 6: 'plane', 7: 'capsule'
    }

    _INV_SHAPE_TYPES = dict(
        sphere=2, box=3, cylinder=4, mesh=5,
        plane=6, capsule=7)

    def __init__(self, e_id, identifier, max_run_time,
                 async=False, step_size=0.001):
        """
        Initialize the physics physics_engine.
        :param async: boolean: indicate if run 
        asynchronously with real world
        :param e_id: integer, render id, label for current
        render; note this can be different from its
        actual physics server id.
        :param max_run_time: maximum running time.
        Should be integer of number of time steps if 
        async, and can be float of time lapse seconds 
        if synced.
        :param identifier: the integer identifier id for
        this render, since physics server should be the
        same as from the graphics server for bullet
        :param step_size: time step size (float) for each
        simulation step
        """
        self._version = 'perls version {}, bullet version {}'.\
            format(__version__, p.getAPIVersion())

        super(BulletPhysicsEngine, self).__init__(
            e_id, max_run_time, async, step_size)

        # physics server id, a.k.a. simulation id.
        # Indicates which bullet physics simulation server to
        # connect to. Default is 0
        self._physics_server_id = identifier

        self._viz = False
        self._sensor_enabled = False

        p.setAdditionalSearchPath(
            pjoin(osp.dirname(__file__),
                  '../data'))

    @property
    def version(self):
        return p.getAPIVersion()

    @property
    def info(self):
        info_dic = dict(
            name='Bullet Physics Engine: {}'.format(
                self.version),
            status=self.status,
            real_time=not self._async,
            id=self.engine_id
            if self._status == 'running' else {},
            max_run_time=self._max_run_time,
            visual=self._viz
        )
        if self._async:
            info_dic['step_size'] = self._step_size
        return info_dic

    @property
    def ps_id(self):
        """
        Get the physics server id of render
        :return:
        """
        return self._physics_server_id

    def _type_check(self, frame):
        """
        Check if frame and async match
        :return: 0 if success, -1 if failure
        """
        if not self._async:
            if frame != 'gui' and frame != 'vr':
                self.status = self._STATUS[-1]
                err_msg = 'Non GUI/VR mode only supports async simulation.'
                self._error_message.append(err_msg)
                logging.error(err_msg)
                return -1
        return 0

    ###
    # General environment related methods

    def configure_environment(self, gravity, *_):
        p.setGravity(0., 0., - gravity * 9.8, self._physics_server_id)

    def load_asset(self, file_path, pos, orn, fixed):
        uid = -1
        try:
            if osp.basename(file_path).split('.')[1] == 'urdf':
                uid = p.loadURDF(
                    file_path, basePosition=pos, baseOrientation=orn,
                    useFixedBase=fixed,
                    flags=p.URDF_USE_SELF_COLLISION_EXCLUDE_PARENT,
                    physicsClientId=self._physics_server_id
                )
            elif osp.basename(file_path).split('.')[1] == 'sdf':
                uid = p.loadSDF(file_path, physicsClientId=self._physics_server_id)[0]
                if fixed:
                    p.createConstraint(
                        uid, -1, -1, -1, p.JOINT_FIXED,
                        [0., 0., 0.], [0., 0., 0.], [0., 0., 0.],
                        physicsClientId=self._physics_server_id)
            # TODO: Leave other possible formats for now

            # Force reset pose... to align CoM and geometric center
            if not fixed:
                p.resetBasePositionAndOrientation(
                    uid, pos, orn, physicsClientId=self._physics_server_id)

            # Get joint and link indices
            joints = list(range(p.getNumJoints(uid, physicsClientId=self._physics_server_id)))
            links = [-1] + joints
            return int(uid), links, joints
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))

    ###
    # Body related methods

    def get_body_scene_position(self, uid):
        if uid == -1:
            return math_util.zero_vec(3)
        return math_util.vec(p.getBasePositionAndOrientation(
            uid, physicsClientId=self._physics_server_id)[0])

    def get_body_scene_orientation(self, uid, otype='quat'):

        if uid == -1:
            return math_util.vec((0, 0, 0, 1))
        orn = p.getBasePositionAndOrientation(
            uid, physicsClientId=self._physics_server_id)[1]
        if otype == 'quat':
            return orn
        elif otype == 'deg':
            return math_util.deg(math_util.quat2euler(orn))
        elif otype == 'rad':
            return math_util.quat2euler(orn)
        else:
            logging.warning('Unrecognized orientation form.')

    def get_body_camera_position(self, uid, camera_pos, camera_orn):

        body_pose = p.getBasePositionAndOrientation(uid, self._physics_server_id)
        frame_pose = math_util.get_relative_pose(
            body_pose, (camera_pos, camera_orn))

        return frame_pose[3, :3]

    def get_body_camera_orientation(
            self, uid, camera_pos, camera_orn, otype):

        body_pose = p.getBasePositionAndOrientation(uid, self._physics_server_id)
        frame_pose = math_util.get_relative_pose(
            body_pose, (camera_pos, camera_orn))
        orn = frame_pose[:3, :3]

        if otype == 'quat':
            return math_util.mat2quat(orn)
        elif otype == 'rad':
            return math_util.mat2euler(orn)
        elif otype == 'deg':
            return math_util.deg(math_util.mat2euler(orn))
        else:
            logging.warning('Unrecognized orientation form.')

    def get_body_relative_pose(self, uid, frame_pos, frame_orn):

        body_pose = p.getBasePositionAndOrientation(uid, self._physics_server_id)
        return math_util.get_relative_pose(body_pose, (frame_pos, frame_orn))

    def set_body_scene_pose(self, uid, pos, orn):
        status = 0
        try:
            p.resetBasePositionAndOrientation(
                uid, tuple(pos), tuple(orn), 
                physicsClientId=self._physics_server_id)
        except p.error as e:
            status = -1
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))
        return status

    def get_body_name(self, uid):
        _, name_str = p.getBodyInfo(
            int(uid), physicsClientId=self._physics_server_id)
        if isinstance(name_str, bytes):
            name_str = name_str.decode('utf-8')
        return name_str

    def get_link_name(self, uid, lid):
        try:
            if lid == -1:
                link_str, _ = p.getBodyInfo(
                    uid, physicsClientId=self._physics_server_id)
            else:
                # Note link_0 is the base link
                link_str = p.getJointInfo(
                    uid, lid, physicsClientId=self._physics_server_id)[-1]
            if isinstance(link_str, bytes):
                link_str = link_str.decode('utf-8')
            return str(link_str)
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))

    def get_body_visual_shape(self, uid):
        return p.getVisualShapeData(
            uid, physicsClientId=self._physics_server_id)

    def set_body_texture(self, uid, qid, texture):
        try:
            texture_id = p.loadTexture(
                texture, physicsClientId=self._physics_server_id)
            p.changeVisualShape(
                uid, qid, textureUniqueId=texture_id,
                physicsClientId=self._physics_server_id)
            return texture_id
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))
            return -1

    def set_body_visual_shape(self, uid, qid, shape):
        try:
            p.changeVisualShape(
                uid, qid, shapeIndex=self._INV_SHAPE_TYPES[shape],
                physicsClientId=self._physics_server_id)
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))
            return -1

    def set_body_visual_color(self, uid, qid, color, spec=False):
        try:
            if spec:
                p.changeVisualShape(
                    uid, qid, 
                    specularColor=list(color),
                    physicsClientId=self._physics_server_id)
            else:
                p.changeVisualShape(
                    uid, qid, 
                    rgbaColor=list(color),
                    physicsClientId=self._physics_server_id)
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))

    def change_loaded_texture(self, texture_id, pixels, w, h):
        p.changeTexture(texture_id, pixels, w, h, self._physics_server_id)

    def get_body_linear_velocity(self, uid):
        return np.array(p.getBaseVelocity(
            uid, physicsClientId=self._physics_server_id)[0])

    def set_body_linear_velocity(self, uid, vel):
        try:
            return p.resetBaseVelocity(
                uid, linearVelocity=vel, physicsClientId=self._physics_server_id)
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))

    def get_body_angular_velocity(self, uid):
        return np.array(p.getBaseVelocity(
            uid, physicsClientId=self._physics_server_id)[1])

    def set_body_angular_velocity(self, uid, vel):
        try:
            return p.resetBaseVelocity(
                uid, angularVelocity=vel, physicsClientId=self._physics_server_id)
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))

    def get_body_link_state(self, uid, lid):
        return tuple(
            [np.array(vec) for
             vec in p.getLinkState(
                uid, lid, 1, physicsClientId=self._physics_server_id)])

    def get_body_joint_info(self, uid, jid):
        info = list(p.getJointInfo(uid, jid, physicsClientId=self._physics_server_id))
        info[2] = BulletPhysicsEngine.JOINT_TYPES[info[2]]
        return tuple(info)

    def get_body_joint_state(self, uid, jid):
        if not self._sensor_enabled:
            p.enableJointForceTorqueSensor(uid, jid, 1, physicsClientId=self._physics_server_id)
            self._sensor_enabled = True
        return p.getJointState(uid, jid, physicsClientId=self._physics_server_id)

    def set_body_joint_state(self, uid, jids, vals, ctype, kwargs):
        if isinstance(jids, int):
            jids = [jids]
        if isinstance(vals, int):
            vals = [vals]
        assert (len(jids) == len(vals)), \
            'In <set_body_joint_state>: Number of joints mismatches number of values'

        try:
            # Only reset if indicated to use reset
            if kwargs.get('reset', False):
                assert(ctype == 'position'), \
                    'Reset joint states currently only supports position control'

                for jid, val in zip(jids, vals):
                    p.resetJointState(
                        uid, jid, targetValue=val, targetVelocity=0.,
                        physicsClientId=self._physics_server_id)

            # Remove 'reset' from kwargs
            kwargs.pop('reset', None)
            if ctype == 'position':
                p.setJointMotorControlArray(uid, jointIndices=jids,
                                            controlMode=p.POSITION_CONTROL,
                                            targetPositions=vals,
                                            targetVelocities=(0.,) * len(jids),
                                            physicsClientId=self._physics_server_id,
                                            **kwargs)
            elif ctype == 'velocity':
                p.setJointMotorControlArray(uid, jointIndices=jids,
                                            controlMode=p.VELOCITY_CONTROL,
                                            targetVelocities=vals,
                                            physicsClientId=self._physics_server_id,
                                            **kwargs)
            elif ctype == 'torque':
                # Need to disable joint motors first
                p.setJointMotorControlArray(uid, jointIndices=jids,
                                            controlMode=p.TORQUE_CONTROL,
                                            physicsClientId=self._physics_server_id,
                                            forces=vals, **kwargs)
        except (AssertionError, p.error) as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            if p.error:
                self._error_message.append(str(e))
                logging.exception('BulletPhysicsEngine captured exception: ' + str(e))

    def enable_body_joint_motors(self, uid, jids, forces):
        p.setJointMotorControlArray(uid, jids, controlMode=p.VELOCITY_CONTROL,
                                    forces=forces,
                                    physicsClientId=self._physics_server_id)

    def disable_body_joint_motors(self, uid, jids):
        p.setJointMotorControlArray(uid, jids, controlMode=p.VELOCITY_CONTROL,
                                    forces=len(jids) * [0.],
                                    physicsClientId=self._physics_server_id)

    def get_body_dynamics(self, uid, lid):
        return p.getDynamicsInfo(uid, lid, physicsClientId=self._physics_server_id)

    def set_body_dynamics(self, uid, lid, info):
        status = 0
        try:
            if 'mass' in info:
                p.changeDynamics(uid, lid, mass=info['mass'],
                                 physicsClientId=self._physics_server_id)
            if 'lateral_friction' in info:
                p.changeDynamics(uid, lid,
                                 lateralFriction=info['lateral_friction'],
                                 physicsClientId=self._physics_server_id)
            if 'spinning_friction' in info:
                p.changeDynamics(uid, lid,
                                 spinningFriction=info['spinning_friction'],
                                 physicsClientId=self._physics_server_id)
            if 'rolling_friction' in info:
                p.changeDynamics(uid, lid,
                                 rollingFriction=info['rolling_friction'],
                                 physicsClientId=self._physics_server_id)
            if 'restitution' in info:
                p.changeDynamics(uid, lid,
                                 restitution=info['restitution'],
                                 physicsClientId=self._physics_server_id)
        except p.error as e:
            status = -1
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))
        return status

    def get_body_bounding_box(self, uid, lid):
        return p.getAABB(uid, linkIndex=lid, physicsClientId=self._physics_server_id)

    def get_body_contact_info(self, uid, lid):

        contacts = p.getContactPoints(bodyA=uid, linkIndexA=lid,
                                      physicsClientId=self._physics_server_id)
        contact_dic = []
        for contact in contacts:
            contact_dic.append(
                dict(uid_other=contact[2],
                     lid_self=contact[3],
                     lid_other=contact[4],
                     pos_self=contact[5],   # Vec3
                     pos_other=contact[6],   # Vec3
                     normalvec2self=contact[7],  # Vec3
                     distance=contact[8],   # Scalar
                     force=contact[9]) # Scalar
            )
        return contact_dic

    def get_body_surroundings(self, uidA, lidA, uidB, lidB, dist):

        neighbors = p.getClosestPoints(
            bodyA=uidA, bodyB=uidB,
            distance=dist,
            linkIndexA=lidA,
            linkIndexB=lidB,
            physicsClientId=self._physics_server_id
        )
        neighbor_dic = []
        for neighbor in neighbors:
            neighbor_dic.append(
                dict(uid=neighbor[2],
                     lid=neighbor[4],
                     posA=neighbor[5],  # Vec3
                     posB=neighbor[6],  # Vec3
                     distance=neighbor[8])  # Scalar
            )
        return neighbor_dic

    def add_body_line_marker(self, posA, posB, color, width,
                             time, uid, lid=None):

        if uid is not None:
            lid = lid or 0
            mid = p.addUserDebugLine(
                posA, posB, lineColorRGB=color,
                lineWidth=width,
                lifeTime=time,
                parentObjectUniqueId=uid,
                parentLinkIndex=lid,
                physicsClientId=self._physics_server_id
            )
        else:
            mid = p.addUserDebugLine(
                posA, posB, lineColorRGB=color,
                lineWidth=width,
                lifeTime=time,
                physicsClientId=self._physics_server_id
            )

        return mid

    def add_body_text_marker(self, text, pos, font_size, color,
                             time, uid, lid=None):
        if uid is not None:
            lid = lid or 0
            mid = p.addUserDebugText(
                text, pos, textColorRGB=tuple(color),
                textSize=float(font_size),
                lifeTime=time,

                # Not using textOrientation for now
                parentObjectUniqueId=uid,
                parentLinkIndex=lid,
                physicsClientId=self._physics_server_id)
        else:
            mid = p.addUserDebugText(
                text, pos, textColorRGB=tuple(color),
                textSize=float(font_size),
                lifeTime=time,
                physicsClientId=self._physics_server_id)
        return mid

    def remove_body_text_marker(self, marker_id):
        p.removeUserDebugItem(marker_id, physicsClientId=self._physics_server_id)

    def apply_force_to_body(self, uid, lid, force, pos, ref):
        try:
            if ref == 'abs':
                p.applyExternalForce(uid, lid, force, pos, p.WORLD_FRAME,
                                     physicsClientId=self._physics_server_id)
            elif ref == 'rel':
                p.applyExternalForce(uid, lid, force, pos, p.LINK_FRAME,
                                     physicsClientId=self._physics_server_id)
            else:
                logging.warning('Unrecognized reference frame. Choose abs or rel')
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))

    def apply_torque_to_body(self, uid, lid, torque, ref):
        try:
            if ref == 'abs':
                p.applyExternalTorque(uid, lid, torque, p.WORLD_FRAME,
                                      physicsClientId=self._physics_server_id)
            elif ref == 'rel':
                p.applyExternalTorque(uid, lid, torque, p.LINK_FRAME,
                                      physicsClientId=self._physics_server_id)
            else:
                logging.warning('Unrecognized reference frame. Choose abs or rel')
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))

    def get_body_attachment(self, uid):

        attached = list()
        # cid starts from 1
        for cid in range(1, p.getNumConstraints(self._physics_server_id) + 1):
            info = p.getConstraintInfo(cid, physicsClientId=self._physics_server_id)

            if info[2] == uid:
                attached.append({
                    (info[0], cid):
                        dict(
                            parentJointIdx=info[1],
                            childLinkIndex=info[3],
                            type=info[4],
                            jointAxis=info[5],
                            parentJointPvt=info[6],
                            childJointPvt=info[7],
                            parentJointOrn=info[8],
                            childJointOrn=info[9],
                            maxForce=info[10])
                })
        return attached

    def set_body_attachment(self, parent_uid, parent_lid,
                            child_uid, child_lid,
                            jtype='fixed',
                            jaxis=(0., 0., 0.),
                            parent_pos=(0., 0., 0.),
                            child_pos=(0., 0., 0.),
                            **kwargs):
        parent_orn = kwargs.get('parentFrameOrientation', None)
        if parent_orn is None:
            parent_orn = (0., 0., 0., 1)

        child_orn = kwargs.get('childFrameOrientation', None)
        if child_orn is None:
            child_orn = (0., 0., 0., 1)
        try:
            return p.createConstraint(parent_uid, parent_lid,
                                      child_uid, child_lid,
                                      BulletPhysicsEngine._INV_JOINT_TYPES[jtype],
                                      jaxis, tuple(parent_pos), tuple(child_pos),
                                      parentFrameOrientation=tuple(parent_orn),
                                      childFrameOrientation=tuple(child_orn),
                                      physicsClientId=self._physics_server_id)
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))

    def remove_body_attachment(self, cid):
        p.removeConstraint(cid, physicsClientId=self._physics_server_id)

    def move_body(self, cid, pos, orn, force):
        # Pybullet needs tuple form
        try:
            p.changeConstraint(cid, jointChildPivot=tuple(pos),
                               jointChildFrameOrientation=tuple(orn),
                               maxForce=force,
                               physicsClientId=self._physics_server_id)
        except p.error as e:
            self.status = BulletPhysicsEngine._STATUS[-1]
            self._error_message.append(str(e))
            logging.exception('BulletPhysicsEngine captured exception: ' + str(e))

    def delete_body(self, uid):
        p.removeBody(uid, physicsClientId=self._physics_server_id)

    ###
    # Arm related methods

    def solve_ik(self, uid, lid, pos, damping, orn=None):
        if orn is None:
            return p.calculateInverseKinematics(
                uid, lid, targetPosition=pos,
                jointDamping=tuple(damping),
                physicsClientId=self._physics_server_id)
        else:
            return p.calculateInverseKinematics(
                uid, lid, targetPosition=pos,
                targetOrientation=orn, jointDamping=tuple(damping),
                physicsClientId=self._physics_server_id)

    def solve_ik_null_space(self, uid, lid, pos,
                            lower, upper, ranges,
                            rest, damping, orn=None):
        if orn is None:
            return p.calculateInverseKinematics(
                uid, lid,
                targetPosition=tuple(pos),
                lowerLimits=tuple(lower), upperLimits=tuple(upper),
                jointRanges=tuple(ranges), restPoses=tuple(rest),
                jointDamping=tuple(damping),
                physicsClientId=self._physics_server_id)   
        else:
            return p.calculateInverseKinematics(
                uid, lid, targetPosition=tuple(pos),
                targetOrientation=tuple(orn),
                lowerLimits=tuple(lower), upperLimits=tuple(upper),
                jointRanges=tuple(ranges), restPoses=tuple(rest),
                jointDamping=tuple(damping),
                physicsClientId=self._physics_server_id)

    def start_engine(self, frame):

        if frame == 'gui' or frame == 'vr':
            self._viz = True

        if self.status == 'killed' or self.status == 'error'\
           or self._type_check(frame) != 0:
            logging.fatal('Cannot start physics physics_engine %d '
                   'in error state. Errors:' % self.engine_id)
            for err_msg in self._error_message:
                logging.error(err_msg)
            return -1
        else:
            p.setTimeStep(
                float(self._step_size),
                physicsClientId=self._physics_server_id
            )
            flag = 0 if self._async else 1
            p.setRealTimeSimulation(flag, physicsClientId=self._physics_server_id)

            # When simulation starts, change state
            self._real_time = not self._async
            # Set status to running
            self.status = BulletPhysicsEngine._STATUS[0]
            logging.info('Starting simulation server {}, status: {}'.
                    format(self.engine_id, self.status))
            return 0

    def hold(self, max_steps=30):
        for _ in range(max_steps):
            p.stepSimulation(self._physics_server_id)

    def step(self, elapsed_time, step_size):
        if self.status == 'running':
            if self._async:
                if self._step_count < self._max_run_time \
                        or self._max_run_time == 0:

                    # Update model (world) states
                    if step_size:
                        p.setTimeStep(step_size)
                        p.stepSimulation(self._physics_server_id)
                    else:
                        p.setTimeStep(self._step_size)
                        p.stepSimulation(self._physics_server_id)
                    self._step_count += 1
                    return False
            else:
                if elapsed_time < self._max_run_time \
                        or self._max_run_time == 0:
                    return False
        return True

    def stop(self):
        # Shutdown simulation
        p.resetSimulation(self._physics_server_id)
        p.disconnect(self._physics_server_id)
        self.status = 'finished'
        logging.info('Physics physics_engine stopped.')

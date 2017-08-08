import pybullet as p
import lib.entity.body as body
import lib.entity.rethinkGripper as rg
import lib.entity.sawyer as s
import lib.entity.kuka as k
import numpy as np
p.connect(p.GUI)


p.resetSimulation()

p.loadURDF('plane.urdf', useFixedBase=True)

# w = wsg.WSG50Gripper(async=True, pos=(-0.5, -0.7, 0.8))
# g.grasp(slide=1)
# w.grasp(slide=1)

# print(w.pos)
# print(w.tool_pos_abs)

# r = k.Kuka(collision_checking=True, pos=[0,0,0],orn=[0,0,0,1])
# r = s.Sawyer()
# g = rg.RethinkGripper()
# r.grasp()
import math

from lib.utils import math_util



r = p.loadURDF('sawyer_robot/sawyer_description/urdf/sawyer.urdf', [0,0,0.9],
    [0,0,0,1],useFixedBase=True)


# r = p.loadURDF('kuka_iiwa/model.urdf', [0,0,0.],
#   [0,0,0,1],useFixedBase=True)
# p.resetBasePositionAndOrientation(r, (0,0,0),(0,0,0,1))

# print(p.getBasePositionAndOrientation(r))
# p.setJointMotorControlArray(r, [0,1,2,3,4,5,6], 
#       p.POSITION_CONTROL, targetPositions=[0,0,0,0.5*math.pi,0,-math.pi*0.5*0.66,0], 
#       targetVelocities=[0] * 7,
#       positionGains=[0.05] * 7, velocityGains=[1.] * 7)

# p.setJointMotorControlArray(r, [0,1,2,3,4,5,6], 
#       p.POSITION_CONTROL, targetPositions=(0, -1.18, 0.00, 2.18, 0.00, 0.57, 3.3161), 
#       targetVelocities=[0] * 7,
#       positionGains=[0.05] * 7, velocityGains=[1.] * 7)

# pose = (0., 0., 0., 1.570793, 0., -1.04719755, 0.)
# for i in range(7):

#   p.resetJointState(r, i, pose[i],0,0)

p.setRealTimeSimulation(1)
# for _ in range(2000):
# #     p.stepSimulation()

# ll=[-.967,-2  ,-2.96,0.19,-2.96,-2.09,-3.05]
# #upper limits for null space
# ul=[.967,2    ,2.96,2.29,2.96,2.09,3.05]
# #joint ranges for null space
# jr=[5.8,4,5.8,4,5.8,4,6]
#restposes for null space
rp=[0, -1.18, 0.00, 2.18, 0.00, 0.57, 3.3161]
#joint damping coefficents
# jd=[0.1,0.1,0.1,0.1,0.1,0.1,0.1]
# print([p.getJointInfo(r, i) for i in range(p.getNumJoints(r))])

rr = [5, 10, 11, 12, 13, 15, 18]
for i in range(7):
    p.resetJointState(r,rr[i],rp[i])
print(p.getNumJoints(r))

p.setGravity(0,0,-9.8)
# r.mark('haha')
# print (p.getLinkState(r, 6)[0])
# import ikpy
# chain = ikpy.chain.Chain.from_urdf_file(
#   '../../bullet3/data/sawyer_robot/sawyer_description/urdf/sawyer.urdf',
#   base_elements=['base'],
#   active_links_mask=[False, False, False, False, False, True, False, False, False, False, True, True, True, True, False, True, False, False, True])

# target_frame = np.eye(4)
# target_frame[:3, 3] = pose[0]

# print(target_frame)
# sol = chain.inverse_kinematics(target_frame,
  # initial_position=(0, 0, 0,0,0,0,0,0,0,0,-1.18, 0.00, 2.18, 0.00,0, 0.57, 0,0,3.3161))
# [-0.465943   -0.89308893  2.286186    0.03158455 -2.25553708 -0.65736246
#   2.17224787]
# sol = [-0.07833199, -0.29562288 ,-0.01593633,-0.31518591,  0.01860969 ,-0.96004085,
#   1.81762848]
# sol = [ -8.10866952e-04 , -8.84536528e-01,  -6.48048856e-02 , -3.49241639e-01,
#    1.23926568e-01,  -3.38399207e-01  , 1.67933567e+00]

# print(sol)
# print(chain.forward_kinematics(sol))
# ik = p.calculateInverseKinematics(r, 6, (-0.8, 0, 0.2), 
#       (0, 1, 0, 0),
#       # lowerLimits=(-3.05, -3.82, -3.05, -3.05, -2.98, -2.98, -4.71), 
#       # upperLimits=(3.05, 2.28, 3.05, 3.05, 2.98, 2.98, 4.71),
#   #       jointRanges=(6.1, 6.1, 6.1, 6.1, 5.96, 5.96, 9.4), 

#   #       restPoses=(0, -1.18, 0.00, 2.18, 0.00, 0.57, 3.3161),
#                 jointDamping=(.1,) * 7)
# print(ik)
# print([(p.getJointInfo(r, o)[1], p.getLinkState(r, o)[0]) for o in range(p.getNumJoints(r))])

# p.setJointMotorControlArray(r, [5,10,11,12,13,15,18], 
#       p.POSITION_CONTROL, targetPositions=(0, -1.18, 0.00, 2.18, 0.00, 0.57, 3.3161), 
#       targetVelocities=[0] * 7,
#       positionGains=[0.05] * 7, velocityGains=[1.] * 7)

# for _ in range(20):
#   p.stepSimulation()

# print(p.getLinkState(r, 6)[0])

# ik = p.calculateInverseKinematics(r, 6, (0.5, -0.1, 0.3), 
#       (0, 1, 0, 0),
#       lowerLimits=ll,#(-3.05, -3.82, -3.05, -3.05, -2.98, -2.98, -4.71), 
#       upperLimits=ul,#(3.05, 2.28, 3.05, 3.05, 2.98, 2.98, 4.71),
#         jointRanges=jr,#(6.1, 6.1, 6.1, 6.1, 5.96, 5.96, 9.4), 

#         restPoses=rp,#(0, -1.18, 0.00, 2.18, 0.00, 0.57, 3.3161),
#                 jointDamping=(.5,) * 7)
# # print(ik)
# p.setJointMotorControlArray(r, range(7), 
#   p.POSITION_CONTROL, targetPositions=ik, 
#   targetVelocities=[0] * 7,
    # positionGains=[0.05] * 7, velocityGains=[1.] * 7)
# print(p.getNumJoints(r))

# eef_pose = (p.getLinkState(r, 19)[0], p.getLinkState(r, 19)[1])

# base_pose
# pose = math_util.pose2mat(eef_pose)

eef_pose = ((0.8, -0.12, 1.5), (0, 1, 0, 0))
print(eef_pose, 'orig')

pose = math_util.get_relative_pose(eef_pose, (p.getLinkState(r, 3)[0], p.getLinkState(r, 3)[1]))

# for i in range(p.getNumJoints(r)):

#     print(i, p.getLinkState(r, i)[-1], math_util.get_relative_pose(eef_pose, (p.getLinkState(r, i)[0], p.getLinkState(r, i)[1])))

tee = math_util.pose2mat((pose[0], (0, 1, 0, 0)))
print(tee, 't')

print(math_util.mat2pose(tee))

while 1:
    # print(p.getQuaternionFromEuler((0, 0, np.pi * 2)))
    
    # ik = p.calculateInverseKinematics(r, 6, (-0.33, -0.1, 0.63), 
    # (0, 1, 0, 0),
    # lowerLimits=ll,#(-3.05, -3.82, -3.05, -3.05, -2.98, -2.98, -4.71), 
    # upperLimits=ul,#(3.05, 2.28, 3.05, 3.05, 2.98, 2.98, 4.71),
#       jointRanges=jr,#(6.1, 6.1, 6.1, 6.1, 5.96, 5.96, 9.4), 

#       restPoses=rp,#(0, -1.18, 0.00, 2.18, 0.00, 0.57, 3.3161),
            # jointDamping=(.5,) * 7)
    # print(dir(ikmodel.manip))
    sols = ikmodel.manip.FindIKSolution(tee, openravepy.IkFilterOptions.CheckEnvCollisions)
    # print(ik)
    # print(sols)
    # print(len(sols))
    p.setJointMotorControlArray(r, rr, 
            p.POSITION_CONTROL, targetPositions=sols, 
            targetVelocities=[0] * 7,
            positionGains=[0.05] * 7, velocityGains=[1.] * 7)

    print(p.getLinkState(r, 19)[0], pose[0])

    p.stepSimulation()

    # p.setRealTimeSimulation(1)
    # print(p.getLinkState(r, 6)[0])

    # print([(p.getLinkState(r, i)[0],p.getJointInfo(r, i)[-1])  for i in range(23)])
    # for e in p.getMouseEvents():
    #   if e[0] == 2:
    #       print(e[1], e[2])
    # r.reach((-.6, 0.0, .2), (0, 1, 0, 0))
    # for j in range(7):
    #   p.setJointMotorControl2(r, j, 
    #       p.POSITION_CONTROL, targetPosition=ik[j], targetVelocity=0.,
    #       positionGain=0.05, velocityGain=1.)
    # r.tool_orn_abs=((0,1,0,0))
    # (g.reach((0.8, -0.5,  1.), p.getQuaternionFromEuler((np.pi/2, -np.pi/2, 0))), 'delta')
    # print(r.tool_pos_abs, r.tool_orn_abs)

    # print(p.getLinkState(r, 6)[0])




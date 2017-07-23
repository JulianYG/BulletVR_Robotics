import pybullet as p
import time
import math
from datetime import datetime

p.connect(p.GUI)
p.loadURDF("plane.urdf",[0,0,-0.3],useFixedBase=True)
kukaId = p.loadURDF("kuka_iiwa/model.urdf",[0,0,0],useFixedBase=True)
p.resetBasePositionAndOrientation(kukaId,[0,0,0],[0,0,0,1])
kukaEndEffectorIndex = 6
numJoints = p.getNumJoints(kukaId)	

#lower limits for null space
ll=[-.967,-2,-2.96,0.19,-2.96,-2.09,-3.05]
#upper limits for null space
ul=[.967,2,2.96,2.29,2.96,2.09,3.05]
#joint ranges for null space
jr=[5.8,4,5.8,4,5.8,4,6]
#restposes for null space
rp=[0,0,0,0.5*math.pi,0,-math.pi*0.5*0.66,0]
#joint damping coefficents
jd=[0.1,0.1,0.1,0.1,0.1,0.1,0.1]

for i in range (numJoints):
	p.resetJointState(kukaId,i,rp[i])

p.setGravity(0,0,-9.81)
t=0.
prevPose=[0,0,0]
prevPose1=[0,0,0]
hasPrevPose = 0
useNullSpace = 0

useOrientation = 1
useSimulation = 1
useRealTimeSimulation = 0
p.setRealTimeSimulation(useRealTimeSimulation)
#trailDuration is duration (in seconds) after debug lines will be removed automatically
#use 0 for no-removal
trailDuration = 15

	
while 1:
	if (useRealTimeSimulation):
		dt = datetime.now()
		t = (dt.second/60.)*2.*math.pi
	else:
		t=t+0.1
	
	if (useSimulation and useRealTimeSimulation==0):
		p.stepSimulation()

	pos = [-0.4,0.2*math.cos(t),0.+0.2*math.sin(t)]
	#end effector points down, not up (in case useOrientation==1)
	orn = p.getQuaternionFromEuler([0,-math.pi,0])
	
	for j in range (150):
		
		if (useSimulation and useRealTimeSimulation==0):
			p.stepSimulation()

		if (useNullSpace==1):
			if (useOrientation==1):
				jointPoses = p.calculateInverseKinematics(kukaId,kukaEndEffectorIndex,pos,orn,ll,ul,jr,rp)
			else:
				jointPoses = p.calculateInverseKinematics(kukaId,kukaEndEffectorIndex,pos,lowerLimits=ll, upperLimits=ul, jointRanges=jr, restPoses=rp)
		else:
			if (useOrientation==1):
				jointPoses = p.calculateInverseKinematics(kukaId,kukaEndEffectorIndex,pos,orn,jointDamping=jd)
			else:
				jointPoses = p.calculateInverseKinematics(kukaId,kukaEndEffectorIndex,pos)

		if (useSimulation):
			for i in range (numJoints):
				p.setJointMotorControl2(bodyIndex=kukaId,jointIndex=i,controlMode=p.POSITION_CONTROL,targetPosition=jointPoses[i],targetVelocity=0,force=500,positionGain=0.03,velocityGain=1)
		else:
			#reset the joint state (ignoring all dynamics, not recommended to use during simulation)
			for i in range (numJoints):
				p.resetJointState(kukaId,i,jointPoses[i])


	ls = p.getLinkState(kukaId,kukaEndEffectorIndex)	
	print(pos, ls[0])
	if (hasPrevPose):
		p.addUserDebugLine(prevPose,pos,[0,0,0.3],1,trailDuration)
		p.addUserDebugLine(prevPose1,ls[4],[1,0,0],1,trailDuration)
	prevPose=pos
	prevPose1=ls[4]
	hasPrevPose = 1		

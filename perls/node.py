from bullet.agents import *
from bullet.interface import *
from bullet.simulator import BulletSimulator
import os, sys, getopt, json
from os.path import join as pjoin
from bullet.utils import helpers as utils
from bullet.comm import *

def render_simulator(agent, interface, task, filename, record=True, vr=False):
	"""
	Models still exist in pybullet since they are only used in pybullet
	Example interfacing with ROS:
	in ros_ctrl_IK.py:

	kuka = kuka.Kuka()
	task = task_repo['kitchen']
	pybullet_simulator = node.render_simulator(kuka, interface, task, 'hi.bin')
	pybullet_simulator.record('path.bin')
	...
	"""
	simulator = BulletSimulator(agent, interface, task, vr)
	simulator.setup(0)
	if record:
		simulator.run(file=filename, record=record)
	return simulator

def execute(*args):
	"""
	Default load settings from command line execution. 
	May need a configuration file for this purpose
	"""
	TASK_DIR = pjoin(os.getcwd(), 'data', 'task.json')
	SCENE_DIR = pjoin(os.getcwd(), 'data', 'scene.json')
	CONFIG_DIR = pjoin(os.getcwd(), 'configs', args[0] + '.json')
	RECORD_LOG_DIR = pjoin(os.getcwd(), 'data', 'record', 'trajectory')

	with open(TASK_DIR, 'r') as f:
		task_repo = json.loads(f.read())
	with open(SCENE_DIR, 'r') as f:
		scene_repo = json.loads(f.read())

	_CONFIGS = utils.read_config(CONFIG_DIR)

	interface_type = _CONFIGS['interface']
	agent = _CONFIGS['agent']
	job = _CONFIGS['job']
	video = _CONFIGS['video']
	delay = _CONFIGS['delay']
	task = _CONFIGS['task']
	remote = _CONFIGS['remote']
	ip = _CONFIGS['server_ip']
	fixed = _CONFIGS['fixed_gripper_orn']
	force_sensor = _CONFIGS['enable_force_sensor']
	init_pos = _CONFIGS['tool_positions']
	camera_info = _CONFIGS['camera']
	server = _CONFIGS['server']
	gui = _CONFIGS['gui']
	scene = _CONFIGS['scene']

	record_file = _CONFIGS['record_file_name']
	replay_file = _CONFIGS['replay_file_name']

	fn = record_file
	if not record_file:
		fn = '_'.join([interface_type, agent, task])

	if agent == 'kuka':
		# Change Fixed to True for keyboard
		agent = kuka.Kuka(init_pos, fixed=fixed, enableForceSensor=force_sensor)
	elif agent == 'sawyer':
		agent = sawyer.Sawyer(init_pos, fixed=fixed, enableForceSensor=force_sensor)
	elif agent == 'pr2':
		agent = pr2.PR2(init_pos, enableForceSensor=force_sensor)
	else:
		raise NotImplementedError('Invalid input: Model not recognized.')
	
	socket = None
	if remote:
		if server == 'redis':
			socket = db.RedisComm(ip, port=6379)
		elif server == 'tcp':
			socket = tcp.TCPComm(ip)
		elif server == 'cmd':
			raise NotImplementedError('Currently not implemented')
		else:
			raise NotImplementedError('Invalid input: Server not recognized.')

	if interface_type == 'vr':	# VR interface that takes VR events
		interface = vr_interface.IVR(socket, remote)
		vr = True
	elif interface_type == 'keyboard':	# Keyboard interface that takes keyboard events
		interface = keyboard_interface.IKeyboard(socket, remote)
		vr = False
	elif interface_type == 'cmd':	# Customized interface that takes any sort of command
		interface = cmd_interface.ICmd(socket, remote)
		vr = False
	else:
		raise NotImplementedError('Non-supported interface.')

	if remote and (job == 'record' or job == 'run'):
		vr = False

	simulator = BulletSimulator(agent, interface, 
								task_repo[task], scene_repo[scene],
								gui=gui, vr=vr)
	if job == 'record':
		simulator.run(fn, True, video)
	elif job == 'replay':
		# Default view point setting
		simulator.set_camera_view(*camera_info)
		if os.path.isfile(pjoin(RECORD_LOG_DIR, replay_file)):
			simulator.playback(fn, delay)
		else:
			raise IOError('Record file not found.')
	elif job == 'run':
		simulator.run()
	else:
		raise NotImplementedError('Invalid input: Job not recognized.')
	return simulator

def usage():
	print('Please specify the configuration file under ./configs. Default config: 1')
	print('Usage: python node.py -c [config]')

def main(argv):

	config = '1'	# default config

	try:
		opts, args = getopt.getopt(argv, 'hc:r', ['help', 'config='])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h', '--help'):
			usage()
			sys.exit(0)
		elif opt in ('-c', '--config'):
			config = arg
	execute(config)

if __name__ == '__main__':
	main(sys.argv[1:])




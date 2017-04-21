from bullet.control.interface import CtrlInterface
import pybullet as p

class IVR(CtrlInterface):

	# TODO: reset signal, pass controller IDs, add configuration file system

	def __init__(self, host, remote):
		# Default settings for camera
		super(IVR, self).__init__(host, remote)

	def _remote_comm(self, model):
		tool = model.get_tool_ids()
		# model.set_virtual_controller([3, 4])
		control_map = model.create_control_mappings()
		self.server.connect()

		while True:
			if model.controllers:
				events = self.server.read_msg()

				skip_flag = model.redundant_control()

				for e in (events):
					if skip_flag:
						if e[0] == model.controllers[1]:
							break
						model.control(e, control_map)
					else:
						model.control(e, control_map)
				self.broadcast_msg(self.model)

	def _local_comm(self, model):
		control_map = model.create_control_mappings()
		while True:
			events = p.getVREvents()
			skip_flag = model.redundant_control()
			for e in (events):
				if skip_flag:
					if e[0] == model.controllers[1]:
						break
					model.control(e, control_map)
				else:
					model.control(e, control_map)

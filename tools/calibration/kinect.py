#!/usr/bin/env python

<<<<<<< HEAD
# Copyright (c) 2013-2017, Rethink Robotics Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import numpy as np
=======
"""
A tracker that calibrates by tracking the robot gripper 
"""

import pickle
import yaml
import numpy as np
from matplotlib import pyplot as plt

import sys, os
from os.path import join as pjoin
>>>>>>> 0300e8771d06b9b72c5c98d425bb373cc81058d3

import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import CameraInfo, Image
<<<<<<< HEAD
import rospy
import rosparam


import sys, os
sys.path.append(os.path.abspath('../src/ros_/utils'))

# from camera import Kinect


dimension = (1920, 1080)
intrinsics = np.array([[1.0741796970429734e+03, 0., 9.3488214133804252e+02], 
                       [1.0640064260133906e+03, 0., 6.0428649994134821e+02], 
                       [0., 0., 1.]], dtype=np.float32)

distortion = np.array([ 3.4454149657654337e-02, 9.7555269933206498e-02,
       1.2981879029576470e-02, 2.7898744906562916e-04,
       -2.0379307133765162e-01 ], dtype=np.float32)

axis = np.float32([[0,0,0], [0,3,0], [3,3,0], [3,0,0],
                   [0,0,-3],[0,3,-3],[3,3,-3],[3,0,-3] ])

def draw(img, corners, imgpts):
    imgpts = np.int32(imgpts).reshape(-1,2)

    # draw ground floor in green
    cv2.drawContours(img, [imgpts[:4]],-1,(0,255,0),-3)

    # draw pillars in blue color
    for i,j in zip(range(4),range(4,8)):
        cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]),(255),3)

    # draw top layer in red color
    cv2.drawContours(img, [imgpts[4:]],-1,(0,0,255),3)



def show_image_callback(img_data):
    """The callback function to show image by using CvBridge and cv
    """
    bridge = CvBridge()
    def mouse_callback(event, x, y, flags, params):
        if event == 1:
            print(x, y, params[y, x])
    try:
        cv_image = bridge.imgmsg_to_cv2(img_data)#, "bgr8")
        # f, points = cv2.findChessboardCorners(cv_image, (9, 6))

        # objp = np.zeros((6*9,3), np.float32)
        # objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

        # # print(cv2.findChessboardCorners(cv_image, (9, 6))[0])
        # if f:
        #     gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

        #     cv2.cornerSubPix(gray, 
        #         points, (11, 11), (-1, -1), 
        #         (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))



        #     rvecs, tvecs, inliers = cv2.solvePnPRansac(objp, points, intrinsics, distortion)
            
            

        #     imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, intrinsics, distortion)

        #     draw(cv_image, points, imgpts)
        # else:
        #     print('pattern not found')

        cv2.namedWindow("cam-calibrate", cv2.CV_WINDOW_AUTOSIZE)
        cv2.imshow("cam-calibrate", cv_image)

        cv2.setMouseCallback('cam-calibrate', mouse_callback, cv_image)
        cv2.waitKey(1)

        
    except CvBridgeError, err:
        rospy.logerr(err)
        return

    # color_detection(cv_image)
    

def main():
    """Camera Display Example
    """
 
    print("Initializing node... ")

    rospy.init_node('kinect', anonymous=True)
    # camera = Kinect(dimension, intrinsics, distortion)
    points = []
    info = dict(
            board_size=(9,6),
            num_of_points=54,
            directory='/home/cvgl_ros/Desktop/test_kinect',
            point_list=points,
            calibration_points=[]
            )

    rospy.Subscriber('/kinect2/hd/image_depth_rect',#'/kinect2/hd/image_color', 
            Image, show_image_callback)

    # camera.snapshot(show_image_callback)
    # camera.set_callback(camera_name, ,
    #     rectify_image=True)
    
    def clean_shutdown():
        print("Shutting down camera_display node.")
        cv2.destroyAllWindows()

    rospy.on_shutdown(clean_shutdown)
    rospy.loginfo("Camera_display node running. Ctrl-c to quit")
    rospy.spin()

if __name__ == '__main__':
    main()
=======
from pylibfreenect2 import Frame
import rospy
import rosparam
import intera_interface
import time
import pybullet as p
sys.path.append(os.path.abspath(os.path.join(__file__, '../../')))
from robot import Robot

import pylibfreenect2
from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
from pylibfreenect2 import createConsoleLogger, setGlobalLogger
from pylibfreenect2 import LoggerLevel
from pylibfreenect2.libfreenect2 import IrCameraParams, ColorCameraParams
try:
    from pylibfreenect2 import OpenCLPacketPipeline
    pipeline = OpenCLPacketPipeline()
except:
    try:
        from pylibfreenect2 import OpenGLPacketPipeline
        pipeline = OpenGLPacketPipeline()
    except:
        from pylibfreenect2 import CpuPacketPipeline
        pipeline = CpuPacketPipeline()

KINECT_DEPTH_SHIFT = -29.84013555237548
GRIPPER_SHIFT = 0.0251

class KinectTracker():

    def __init__(self, robot,
        board_size=(2,2), itermat=(8, 9), intrinsics_RGB=None, distortion_RGB=None,
        calib='../../../tools/calibration/calib_data/kinect'):

        self._board_size = board_size
        self._checker_size = 0.0247

        self._arm = robot

        # self._intrinsics = None
        self._grid = itermat

        self._intrinsics_RGB = intrinsics_RGB
        self._distortion_RGB = distortion_RGB

        self._calib_directory = calib

        self._transformation = np.zeros((4, 4), dtype=np.float32)
        self._transformation[3, 3] = 1
        self.turn_on()
        self.track()

    def turn_on(self):

        fn = Freenect2()
        num_devices = fn.enumerateDevices()
        if num_devices == 0:
            print("No device connected!")
            sys.exit(1)

        serial = fn.getDeviceSerialNumber(0)
        self._fn = fn
        self._serial = serial

        self._device = self._fn.openDevice(self._serial, pipeline=pipeline)

        self._listener = SyncMultiFrameListener(
            FrameType.Color | FrameType.Ir | FrameType.Depth)

        # Register listeners
        self._device.setColorFrameListener(self._listener)
        self._device.setIrAndDepthFrameListener(self._listener)
        self._device.start()

        # NOTE: must be called after device.start()
        if self._intrinsics_RGB is None:

            self._intrinsics_RGB = self._to_matrix(self._device.getColorCameraParams())

            self._registration = Registration(self._device.getIrCameraParams(), 
                self._device.getColorCameraParams())
        else:
            # IrParams = IrCameraParams(self.K, ...)
            # colorParams = ColorCameraParams(self.K, ...)

            # registration = Registration(IrParams, colorParams)
            self._registration = Registration(
                            self._device.getIrCameraParams(),
                            self._device.getColorCameraParams())

        self._undistorted = Frame(512, 424, 4)
        self._registered = Frame(512, 424, 4)

        self._big_depth = Frame(1920, 1082, 4)
        self._color_depth_map = np.zeros((424, 512),  np.int32).ravel()

        self.camera_on = True

    def snapshot(self):

        self._frames = self._listener.waitForNewFrame()

        color, ir, depth = \
            self._frames[pylibfreenect2.FrameType.Color],\
            self._frames[pylibfreenect2.FrameType.Ir], \
            self._frames[pylibfreenect2.FrameType.Depth]

        self._registration.apply(color, depth, 
            self._undistorted,
            self._registered, 
            bigdepth=self._big_depth, 
            color_depth_map=self._color_depth_map)

        return color, ir, depth

    def get_point_3d(self, x, y):
        return self._registration.getPointXYZ(Frame(512, 424, 4), x, y)

    # def stream(self):

    #     def mouse_callback(event, x, y, flags, params):
    #         if event == 1:
    #             print(self.get_point_3d(x, y))

    #     while True:
            
    #         color, ir, depth = self.snapshot()

    #         cv2.namedWindow('kinect-ir', cv2.CV_WINDOW_AUTOSIZE)
    #         cv2.imshow('kinect-ir', ir.asarray() / 65535.)
    #         cv2.setMouseCallback('kinect-ir', mouse_callback, ir)

    #         cv2.namedWindow('kinect-depth', cv2.CV_WINDOW_AUTOSIZE)
    #         cv2.imshow("kinect-depth", depth.asarray() / 4500.)
    #         cv2.setMouseCallback('kinect-depth', mouse_callback, depth)

    #         cv2.namedWindow('kinect-rgb', cv2.CV_WINDOW_AUTOSIZE)
    #         rgb = cv2.resize(color.asarray(), (int(1920 / 3), int(1080 / 3)))
    #         cv2.imshow("kinect-rgb", rgb)

    #         cv2.namedWindow('kinect-registered', cv2.CV_WINDOW_AUTOSIZE)
    #         registered = self._registered.asarray(np.uint8)
    #         cv2.imshow("kinect-registered", registered)
    #         cv2.setMouseCallback('kinect-registered', mouse_callback, self._registered)

    #         cv2.namedWindow('kinect-big_depth', cv2.CV_WINDOW_AUTOSIZE)
    #         big_depth = cv2.resize(self._big_depth.asarray(np.float32), 
    #             (int(1920 / 3), int(1082 / 3)))
    #         cv2.imshow("kinect-big_depth", big_depth)
    #         cv2.setMouseCallback('kinect-registered', mouse_callback, self._big_depth)

    #         cv2.namedWindow('kinect-rgbd', cv2.CV_WINDOW_AUTOSIZE)
    #         rgbd = self._color_depth_map.reshape(424, 512)
    #         cv2.imshow("kinect-rgbd", rgbd)
    #         # cv2.setMouseCallback('kinect-rgbd', mouse_callback, self._color_depth_map)

    #         self._listener.release(self._frames)

    #         key = cv2.waitKey(delay=1)
    #         if key == ord('q'):
    #             break
    global_x, global_y = 858, 489
    def match_eval(self):
    	
    	LENGTH = 0.24406304511449886

        def mouse_callback(event, x, y, flags, params):
            if event == 1:
                self.global_x = x
                self.global_y = y
                # print(x, y)
                
                # end_state = dict(position=np.array(np.array([0.5, 0, 0.5]), dtype=np.float32),
                #          orientation=robot.get_tool_pose()[1])
                # # Move to target position
                # robot.reach_absolute(end_state)

                depth_map = cv2.flip(self._big_depth.asarray(np.float32)[1:-1, :], 1)
                depth_avg = depth_map[y, x] + KINECT_DEPTH_SHIFT
                print("== depth: {}".format(depth_avg))
                cam_x = (x - self._intrinsics_RGB[0, 2]) / self._intrinsics_RGB[0, 0] * depth_avg
                cam_y = (y - self._intrinsics_RGB[1, 2]) / self._intrinsics_RGB[1, 1] * depth_avg
                # print("camera frame x = {}, y = {}, z = {}".format(cam_x, cam_y, depth))
                point = np.ones((4,), dtype=np.float32)
                point[0] = cam_x
                point[1] = cam_y
                point[2] = depth_avg

                ori = p.getQuaternionFromEuler((np.pi, 0, 0))
                z = np.array(p.getMatrixFromQuaternion(ori)).reshape(3,3)[-1]
                x = np.array(p.getMatrixFromQuaternion(ori)).reshape(3,3)[0]
                y = np.array(p.getMatrixFromQuaternion(ori)).reshape(3,3)[1]
                # print
                target_point = np.linalg.inv(self._transformation).dot(point)[:3] / 1000
                print("== xyz in robot frame: {}".format(target_point * 1000))
                print(z)
                # print(target_point - z * LENGTH + np.array([0, 0, -1] * 0.05))
                target_point = target_point - z * LENGTH + np.array([0, 0, 1]) * 0.02
                print("== desired endeffector pos: {}".format(target_point * 1000))
                # print(target_point)
                end_state = dict(position=target_point,
                         orientation=ori)
                self._arm.reach_absolute(end_state)
                time.sleep(1)
                print("== move to {} success".format(self._arm.get_tool_pose()[0]))
                print(self._arm.get_tool_pose()[0])



        cv2.namedWindow('kinect-rgb', cv2.CV_WINDOW_AUTOSIZE)
        # cv2.namedWindow('kinect-depth', cv2.CV_WINDOW_AUTOSIZE)
        cv2.setMouseCallback('kinect-rgb', mouse_callback)
        # cv2.setMouseCallback('kinect-depth', mouse_callback)
        
        depth_avg_100 = 0
        avg_counter = 0
        # plt.axis([0, 10, 0, 1])
        # plt.ion()

        while True:
            color, _, _ = self.snapshot()
            color = cv2.flip(color.asarray(), 1)
            depth_map = cv2.flip(self._big_depth.asarray(np.float32)[1:-1, :], 1)
            
            count = 0
            depth_avg = 0
            y = self.global_y
            x = self.global_x
            depth_avg = depth_map[y, x] + KINECT_DEPTH_SHIFT
            # print("== depth: {}".format(depth_avg))

            cam_x = (x - self._intrinsics_RGB[0, 2]) / self._intrinsics_RGB[0, 0] * depth_avg
            cam_y = (y - self._intrinsics_RGB[1, 2]) / self._intrinsics_RGB[1, 1] * depth_avg
            # print("camera frame x = {}, y = {}, z = {}".format(cam_x, cam_y, depth))
            point = np.ones((4,), dtype=np.float32)
            point[0] = cam_x
            point[1] = cam_y
            point[2] = depth_avg
            # print(self._transformation)
            # print(self._transformation.dot(p))
            # print(np.linalg.inv(self._transformation).dot(point)[:3] / 1000)
            # temp = np.linalg.inv(self._transformation).dot(point)[:3] / 1000
            # ori = np.array(robot.get_tool_pose()[1], dtype=np.float32)
            # z = np.array(p.getMatrixFromQuaternion(ori)).reshape(3,3)[-1]
            # print("temp: {}".format(temp))
            # print(z)
            # print(temp - z * GRIPPER_SHIFT)
            # # temp[2] += 0.04
            # end_state = dict(position=temp - z * GRIPPER_SHIFT,
            #          orientation=p.getQuaternionFromEuler((0, 0, 0)))
            # self._arm.reach_absolute(end_state)
            ori = p.getQuaternionFromEuler((0, 0, 0))
            z = np.array(p.getMatrixFromQuaternion(ori)).reshape(3,3)[-1]
            x = np.array(p.getMatrixFromQuaternion(ori)).reshape(3,3)[0]
            y = np.array(p.getMatrixFromQuaternion(ori)).reshape(3,3)[1]
            # print
            target_point = np.linalg.inv(self._transformation).dot(point)[:3]
            # print(target_point[-1])

            if avg_counter < 200:
            	depth_avg_100 += target_point[-1]
            	avg_counter = avg_counter + 1
            else:
            	print("=== z average on last 100 frames: {}".format(depth_avg_100 / avg_counter))
            	depth_avg_100 = 0
            	avg_counter = 0

            cv2.circle(color, (self.global_x, self.global_y), 1, (0, 255, 0), 10)
            
            rgb = cv2.resize(color, (int(1920), int(1080)))

            cv2.imshow("kinect-rgb", rgb)

            
            # rgb = cv2.resize(cv2.flip(self._big_depth.asarray(np.float32)[:, 1:-1] / 2000, 1), (int(1920), int(1080)))
            # cv2.imshow("kinect-depth", rgb)



            # translation_matrix = np.linalg.inv(self._transformation)
            # for i in range(1080):
            #     for j in range(1920):
            #     	y = i
            #     	x = j
            #     	depth = depth_map[y, x] + KINECT_DEPTH_SHIFT
            #     	cam_x = (x - self._intrinsics_RGB[0, 2]) / self._intrinsics_RGB[0, 0] * depth_avg
            #     	cam_y = (y - self._intrinsics_RGB[1, 2]) / self._intrinsics_RGB[1, 1] * depth_avg
            #     	point = np.ones((4,), dtype=np.float32)
            #     	point[0] = cam_x
            #     	point[1] = cam_y
            #     	point[2] = depth_avg
            #     	depth_robot = translation_matrix.dot(point)[2]
            #     	if (depth_robot < -400) or (depth_robot > 200):
            #     		depth_map[i, j] = 0
            #     	else:
            #     		depth_map[i, j] = (depth_robot - (-400)) / (600)
            # plt.imshow(depth_map, cmap='hot', interpolation='nearest')
            # plt.show()
            # plt.pause(0.05)
            

            self._listener.release(self._frames)
            
            key = cv2.waitKey(delay=1)
            if key == ord('q'):
                break

    def find_constant(self):

        self._grid = (3, 3)
        origin = np.array([0.43489, -0.2240, 0.1941], dtype=np.float32)
        orn = np.array([0, 0, 0, 1], dtype=np.float32)

        calibration_grid = np.zeros((self._grid[0] * self._grid[1], 3), np.float32)
        calibration_grid[:, :2] = np.mgrid[0: self._grid[0], 
                                           0: self._grid[1]].T.reshape(-1, 2) * 0.033
        # And randomness to z                                  
        calibration_grid[:, -1] += np.random.uniform(-0.08, 0.2, 
            self._grid[0] * self._grid[1])

        error_list = []
        errors = []
        counts = []
        itrs = np.arange(0, 30.0, 5.0)
        for j in range(len(itrs)):
        	errors.append(np.zeros((3,)))
        	counts.append(0)
        for i, pos in enumerate(calibration_grid):
            print("{} / 9".format(i + 1))
            target = origin + pos
            # Add randomness to orientation
            orn = p.getQuaternionFromEuler(np.random.uniform(
                [-np.pi/12., -np.pi/12., -np.pi/6.],[np.pi/12., np.pi/12., np.pi/6.]))

            end_state = dict(position=tuple(target),
                         orientation=orn)
            # Move to target position
            self._arm.reach_absolute(end_state)
            time.sleep(2)
            not_found = 0

            for j, shift in enumerate(itrs):
            	# print(j)
                KINECT_DEPTH_SHIFT = -shift
                # time.sleep(1.5)
                inner_count = 0
                if not_found > 5:
                    break
                while inner_count < 30:
                    # print("inner count: {}".format(inner_count))
                    if not_found > 5:
                        break
                    # print(inner_count)
                    inner_count = inner_count + 1
                    color, _, _ = self.snapshot()
                    color = cv2.flip(color.asarray(), 1)
                    # ir = cv2.flip(ir.asarray(), 1)
                    # depth = cv2.flip(depth.asarray(), 1)

                    detected, pix = self._detect_center(color)
                    if detected:
                        # print("Pattern Detected")
                        counts[j] = counts[j] + 1
                        x, y = pix
                        depth_map = cv2.flip(self._big_depth.asarray(np.float32)[1:-1, :], 1)
                        depth = depth_map[int(y + 0.5), int(x + 0.5)] + KINECT_DEPTH_SHIFT
                        # print(depth)
                        cam_x = (x - self._intrinsics_RGB[0, 2]) / self._intrinsics_RGB[0, 0] * depth
                        cam_y = (y - self._intrinsics_RGB[1, 2]) / self._intrinsics_RGB[1, 1] * depth
                        # print("camera frame x = {}, y = {}, z = {}".format(cam_x, cam_y, depth))
                        point = np.ones((4,), dtype=np.float32)
                        point[0] = cam_x
                        point[1] = cam_y
                        point[2] = depth
                        # print(self._transformation)
                        # print(self._transformation.dot(p))
                        # print(np.linalg.inv(self._transformation).dot(point)[:3] / 1000)
                        temp = np.linalg.inv(self._transformation).dot(point)[:3] / 1000
                        ori = np.array(robot.get_tool_pose()[1], dtype=np.float32)
                        z = np.array(p.getMatrixFromQuaternion(ori)).reshape(3,3)[-1]
                        estimated_gripper_pos = temp - z * GRIPPER_SHIFT
                        ground_truth = np.array(robot.get_tool_pose()[0], dtype=np.float32)
                        # print("est pos: {}".format(estimated_gripper_pos))
                        # print("grd pos: {}".format(ground_truth))
                        # print("gap    : {}".format(estimated_gripper_pos - ground_truth))
                        errors[j] += np.sqrt((estimated_gripper_pos - ground_truth) * (estimated_gripper_pos - ground_truth))
                        # print("err avg: {}".format(error / count))
                    else:
                    	not_found = not_found + 1
                    	# print("not found: {}".format(not_found))

                    #     cv2.circle(color, tuple(pix.astype(int).tolist()), 1, (0, 255, 0), 10)
                    
                    # cv2.namedWindow('kinect-rgb', cv2.CV_WINDOW_AUTOSIZE)
                    # rgb = cv2.resize(color, (int(1920), int(1080)))
                    # cv2.imshow("kinect-rgb", rgb)
                    # cv2.setMouseCallback('kinect-rgb', mouse_callback)


                    self._listener.release(self._frames)
                    
                    # key = cv2.waitKey(delay=1)
                    # if key == ord('q'):
                    #     break
        for j, shift in enumerate(itrs):
        	print("shift: {}, err avg: {}".format(shift, errors[j] / counts[j]))

    def turn_off(self):
        self._device.stop()
        self._device.close()
        self.camera_on = False

    def track(self):

        invRotation_dir = pjoin(self._calib_directory, 'KinectTracker_rotation.p')
        translation_dir = pjoin(self._calib_directory, 'KinectTracker_translation.p')

        if os.path.exists(invRotation_dir) and os.path.exists(translation_dir):
            
            with open(invRotation_dir, 'rb') as f:
                rotation = pickle.load(f)

            with open(translation_dir, 'rb') as f:
                translation = np.squeeze(pickle.load(f))
        
            self._transformation[:3, :3] = rotation
            self._transformation[:3, 3] = translation
            return

        origin = np.array([0.43489, -0.2240, 0.1941], dtype=np.float32)
        orn = np.array([0, 0, 0, 1], dtype=np.float32)

        calibration_grid = np.zeros((self._grid[0] * self._grid[1], 3), np.float32)
        calibration_grid[:, :2] = np.mgrid[0: self._grid[0], 
                                           0: self._grid[1]].T.reshape(-1, 2) * 0.033
        # And randomness to z                                  
        calibration_grid[:, -1] += np.random.uniform(-0.08, 0.2, 
            self._grid[0] * self._grid[1])

        camera_points, gripper_points = [], []
        total = len(calibration_grid)
        count = 0
        for i, pos in enumerate(calibration_grid):
            print("{} / {}".format(i + 1, total))
            # Set position to reach for
            target = origin + pos

            # Add randomness to orientation
            orn = p.getQuaternionFromEuler(np.random.uniform(
                [-np.pi/12., -np.pi/12., -np.pi/6.],[np.pi/12., np.pi/12., np.pi/6.]))

            end_state = dict(position=tuple(target),
                         orientation=orn)
            # Move to target position
            self._arm.reach_absolute(end_state)

            # Wait till stabilize
            time.sleep(2)

            # Get the real position
            gripper_pos = np.array(self._arm.get_tool_pose()[0], 
                                   dtype=np.float32)
            gripper_ori = np.array(robot.get_tool_pose()[1], dtype=np.float32)
            trans_matrix = np.array(p.getMatrixFromQuaternion(gripper_ori)).reshape(3,3)
            marker_pos = gripper_pos + trans_matrix[-1] * GRIPPER_SHIFT
            # Match with pattern location
            color, ir, depth = self.snapshot()
            color = cv2.flip(color.asarray(), 1)
            self._listener.release(self._frames)

            detected, pix = self._detect_center(color)

            # Skip if not found pattern
            if not detected:
                print('Pattern not detected. Skipping')
            else:
                print('Pattern detected! pos: {}'.format(pix))
                count = count + 1
                camera_points.append(pix)
                gripper_points.append(marker_pos * 1000)

        print("Solving parameters using {} images".format(count))
        # Solve for matrices
        retval, rvec, translation = cv2.solvePnP(
            np.array(gripper_points, dtype=np.float32), 
            # Only use the x, y to get R | T
            np.array(camera_points, dtype=np.float32), 
            self._intrinsics_RGB, 
            # Give none, assuming feeding in undistorted images 
            self._distortion_RGB)
            # self.d)

        rotation = cv2.Rodrigues(rvec)[0]
            
        data = dict(rotation=rotation,
                    translation=translation,)
                    # intrinsics=self.K,
                    # distortion=self.d)    
        print("saving data to" + pjoin(self._calib_directory, 
                '{}_'.format(self.__class__.__name__)))
        for name, mat in data.items():
            with open(pjoin(self._calib_directory, 
                '{}_{}.p'.format(self.__class__.__name__, name)), 'wb') as f:
                pickle.dump(mat, f)

        print(rotation, translation)

        self._transformation[:3, :3] = rotation
        self._transformation[:3, 3] = np.squeeze(translation)

        self.turn_off() 

    def convert(self, u, v):

        p = np.ones((4,), dtype=np.float32)

        p[:3] = self._registration.getPointXYZ(Frame(int(1920 / 3), int(1080 / 3), 4), u, v)

        print(p, self._transformation)
        return self._transformation.dot(p)

    def _detect_center(self, color):

        img = cv2.resize(color, (int(1920), int(1080)))
        foundPattern, usbCamCornerPoints = cv2.findChessboardCorners(
            img, self._board_size, None,
            cv2.CALIB_CB_ADAPTIVE_THRESH
        )
        if foundPattern:
            # cv2.drawChessboardCorners(img, self._board_size, 
            #       usbCamCornerPoints, foundPattern)

            cv2.cornerSubPix(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 
                    usbCamCornerPoints, (11, 11), (-1, -1), 
                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))

            usbCamCornerPoints = np.squeeze(usbCamCornerPoints)
            recognized_pix = np.mean(usbCamCornerPoints, axis=0)
            # print(tuple(recognized_pix.astype(int).tolist()))
            # depth = self._big_depth.asarray(np.float32)[1:-1, :][int(recognized_pix[1]), int(recognized_pix[0])]
            # # print(depth)
            # cam_x = (recognized_pix[0] - self._intrinsics_RGB[0, 2]) / self._intrinsics_RGB[0, 0] * depth
            # cam_y = (recognized_pix[1] - self._intrinsics_RGB[1, 2]) / self._intrinsics_RGB[1, 1] * depth
            # print("camera frame x = {}, y = {}, z = {}".format(cam_x, cam_y, depth))
            # cv2.circle(img, tuple(recognized_pix.astype(int).tolist()), 1, (0, 255, 0), 10)

            # cv2.imshow('kinect_calibrate', cv2.resize(img, (int(1920), int(1080))))
            # cv2.waitKey(3000)
            return True, recognized_pix
        else:
            # cv2.imshow('kinect_calibrate', cv2.resize(img, (int(1920), int(1080))))
            # cv2.waitKey(3000)
            return False, None

    @staticmethod
    def _to_matrix(param):

        return np.array([
            [param.fx, 0, param.cx], 
            [0, param.fy, param.cy], 
            [0, 0, 1]], 
            dtype=np.float32)

if rospy.get_name() == '/unnamed':
    rospy.init_node('kinect_tracker')

limb = intera_interface.Limb('right')
limb.set_joint_position_speed(0.1)
robot = Robot(limb, None)

dimension = (1920, 1080)
intrinsics_RGB = np.array([[1.0450585754139581e+03, 0., 9.2509741958808945e+02], 
                       [0., 1.0460057005089166e+03, 5.3081782987073052e+02], 
                       [0., 0., 1.]], dtype=np.float32)

distortion_RGB = np.array([ 1.8025470248423700e-02, -4.0380385825573024e-02,
       -6.1365440651701009e-03, -1.4119705487162354e-03,
       9.5413324012517888e-04 ], dtype=np.float32)

tracker = KinectTracker(robot, board_size=(4,4), itermat=(15, 15), intrinsics_RGB=intrinsics_RGB, distortion_RGB=distortion_RGB)
np.set_printoptions(formatter={'float': lambda x: "{0:0.8f}".format(x)})

# tracker.find_constant()
tracker.match_eval()
# tracker.turn_off()


# end_state = dict(position=np.array([0.65, 0.1, 0.35], dtype=np.float32),
#                          orientation=p.getQuaternionFromEuler((0, 0, 0)))
#             # Move to target position
# robot.reach_absolute(end_state)


# gripper_pos = np.array(robot.get_tool_pose()[0], dtype=np.float32)
# print(gripper_pos)
# gripper_ori = np.array(robot.get_tool_pose()[1], dtype=np.float32)
# trans_matrix = np.array(p.getMatrixFromQuaternion(gripper_ori)).reshape(3,3)
# pos = gripper_pos + trans_matrix[-1] * 0.02534
# print(pos)
>>>>>>> 0300e8771d06b9b72c5c98d425bb373cc81058d3

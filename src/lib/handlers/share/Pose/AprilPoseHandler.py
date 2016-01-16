#!/usr/bin/env python
import rospy
#from std_msgs.msg import String
#from geometry_msgs.msg import PoseArray
from apriltags_ros.msg import AprilTagDetectionArray, AprilTagDetection
from tf.transformations import euler_from_quaternion
from geometry_msgs.msg import PoseStamped
from numpy import pi
import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
# smores imports:
import sys
sys.path.insert(0, '/home/tarik/Embedded/ecosystem/smores_build/smores_reconfig/python')
import pdb
# LTLMoP imports:
#import lib.handlers.handlerTemplates as handlerTemplates

#class AprilPoseHandler(handlerTemplates.PoseHandler):
class AprilPoseHandler():
    stale_data_time = 1 
    start_time = None
    robotTagNumber = None
    tagPoses = {} # last recorded pose; (x,y,thetaRadians)
    tagTimestamps = {} # last recorded timestamp of each tag
    #
    def __init__(self, executor, shared_data, robotTagNumber):
        ''' 
	Constructor. robotTagNumber is the apriltag number attached to the robot. 

	robotTagNumber (int): The April Tag number of the robot
        '''
        rospy.init_node('april_listener', anonymous=True)
        self.sub = rospy.Subscriber("tag_detections", AprilTagDetectionArray, self.callback)
        now = rospy.get_rostime()
        self.start_time = now.to_sec()
        self.robotTagNumber = robotTagNumber
        # Add robotTagNumber to tagPoses and tagTimestamps:
        self.tagPoses[robotTagNumber] = (0, 0, 0)
        self.tagTimestamps[robotTagNumber] = 0.0

    #def teardown(self):
    #    self.sub.unsubscribe()

    def callback(self,data):
        ''' Callback function that pulls data from the apriltag topic. '''
        #rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
        if len(data.detections)>0:
            # Extract data from the topic:
            for detection in data.detections:
                tagId = detection.id
                poseStamped = detection.pose
                time_seconds = poseStamped.header.stamp.to_sec()
                #nsecs = data.header.stamp.nsecs
                self.tagTimestamps[tagId] = time_seconds
                q = poseStamped.pose.orientation  # get quaternion
                eulers_rad = euler_from_quaternion([q.x, q.y, q.z, q.w])
                thetaRad = eulers_rad[2]
                p = poseStamped.pose.position
                self.tagPoses[tagId] = (p.x, p.y, thetaRad)

    # def callback(self,data):
    #     #rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    #     if len(data.poses)>0:
    #         time_seconds = data.header.stamp.to_sec()
    #         #nsecs = data.header.stamp.nsecs
    #         self.timestamp = time_seconds - self.start_time
    #         q = data.poses[0].orientation  # get quaternion
    #         eulers_rad = euler_from_quaternion([q.x, q.y, q.z, q.w])
    #         thetaRad = eulers_rad[2]
    #         p = data.poses[0].position
    #         self.pose = (p.x, p.y, thetaRad)
    #         #rospy.loginfo(rospy.get_caller_id() + "\nQuaternion:\n%s\nEulers:\n%s\n", str(q), str(eulers_deg))

    def getPose(self, cached=False, tagId=None):
        ''' Returns the pose of the specified tag.  If no tag is specified,
        returns the pose of the robot tag.  '''
        if tagId is None:
            tagId = self.robotTagNumber
        if self.tagPoses.has_key(tagId):
            # if the data has not been updated recently, return (0, 0, 0)
            now = rospy.get_rostime()
            now = now.to_sec()
            if now - self.tagTimestamps[tagId] > self.stale_data_time:
                return (0, 0, 0)
            else:
                return self.tagPoses[tagId]
        else:
            return None


if __name__ == '__main__':
    P = AprilPoseHandler(None, None, 0)
    #start = time.time()
    #while time.time()-start < 10:
    #    time.sleep(0.5)
    #    print P.get_pose()

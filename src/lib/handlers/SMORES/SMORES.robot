DriveHandler: # Robot default drive handler with default argument values
share.Drive.BipedalDriveHandler()

InitHandler: # Robot default init handler with default argument values
SMORES.SMORESInitHandler(ip='nao.local',port=9559)

LocomotionCommandHandler: # Robot default locomotion command handler with default argument values
SMORES.SMORESLocomotionCommandHandler()

MotionControlHandler: # Robot default motion control handler with default argument values
share.MotionControl.VectorControllerHandler()

PoseHandler: # Robot default pose handler with default argument values
share.Pose.ViconPoseHandler(host='10.0.0.102',port=800,x_VICON_name="Nao:Nao <t-X>",y_VICON_name="Nao:Nao <t-Y>",theta_VICON_name="Nao:Nao <a-Z>")

RobotName: # Robot Name
MODASL

Type: # Robot type
SMORES

SensorHandler: # Robot default sensor handler with default argument values
SMORES.SMORESSensorHandler()

ActuatorHandler: # Robot default actuator handler with default argument values
SMORES.SMORESActuatorHandler()

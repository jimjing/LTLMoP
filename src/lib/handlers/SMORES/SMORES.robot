DriveHandler: # Robot default drive handler with default argument values
share.Drive.DifferentialDriveHandler()

InitHandler: # Robot default init handler with default argument values
SMORES.SMORESInitHandler(smores_lib_path="/home/jim/Embedded/ecosystem/smores_build/smores_reconfig/python/SmoresModule", module_id=1)

LocomotionCommandHandler: # Robot default locomotion command handler with default argument values
SMORES.SMORESLocomotionCommandHandler()

MotionControlHandler: # Robot default motion control handler with default argument values
share.MotionControl.VectorControllerHandler()

PoseHandler: # Robot default pose handler with default argument values
share.Pose.AprilPoseHandler(111)

RobotName: # Robot Name
MODASL

Type: # Robot type
SMORES

SensorHandler: # Robot default sensor handler with default argument values
SMORES.SMORESSensorHandler()

ActuatorHandler: # Robot default actuator handler with default argument values
SMORES.SMORESActuatorHandler()

# simpleRobotNavigation

This project was developed in the class "An Introduction to Mobile Robotics" at Federal University of Alagoas.
The goal of the system is to set:
*an initial frame location
*a final frame location
*and a final orientation (angles)

And the output expected is that the robot reaches the final location and pose following the established path (which is a simple straight line)

In the samples directory you can see some data as result of the experiments.
It was used just a camera attached to the ceiling, color information for robot pose detection and a simple proportial (K) controller.

Fails: Many problems are due to color detection missing and latency in the network, since the camera is sending the frames for remote processing. A possible solution for this problem would be local processing on the camera's embbeded system and a more robust pose detection strategy. 

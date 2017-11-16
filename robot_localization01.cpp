#include <opencv2/features2d.hpp>
#include <opencv2/xfeatures2d.hpp>
#include <opencv2/core/utility.hpp>
#include <opencv2/tracking.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstring>
#include "roiSelector.hpp"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netdb.h>
#include <arpa/inet.h>

#define PI 3.14159265

using namespace std;
using namespace cv;
using namespace cv::xfeatures2d;

float measureRobotOrientation(Mat robot);
void path_planning(Point2d& pi, Point2d& pf, Rect2d roi_initial, Rect2d roi_final, Mat& frame);
void get_localization(Point2d& pa, Rect2d& roi_actual, float& angle_measured, Mat frame);
void draw_path_plan(Point2d pi, Point2d pf, Mat& frame);
void draw_trace(vector<Point2d> trace, Mat& frame);
void feedback_control(float angle_measured, Point pf, Point pa);
void sendVelocities(int Vr, int Vl);
void createRobotConection(struct addrinfo& hints, struct addrinfo * res, int& status, int& socket_id);

struct addrinfo hints, * res;
int status;
int socket_id;

ofstream output_file("./robot_debug.txt");

int main() {

        Rect2d roi_initial, roi_actual, roi_final, workspace;
        Point2d pi, pa, pf;
        vector<Point2d> trace;
        float angle_measured, final_orientation;
        Mat frame_init, frame, frame_map;
        Ptr<Tracker> tracker = Tracker::create( "KCF" );
        VideoCapture cap("http://192.168.43.1:8080/video");
		//VideoCapture cap(0);

        cap >> frame_init;
        // get frame of robot reference
        cout << "Select the robot workspace..." << endl;
        workspace = selectROI("Camera Vision", frame_init, false, false);
        frame = Mat(frame_init, workspace);
        roi_initial = selectROI("Robot Workspace", frame, false, false);
        roi_final = selectROI("Robot Workspace", frame, false, false);
        cout << "Pass the angle_measured of robot's orientation (0 ~ 360):" << endl;
        cin >> final_orientation;

        if(final_orientation > 360 || final_orientation < 0)
                return 0;

        if(roi_initial.width == 0 || roi_initial.height == 0 || roi_final.width == 0 || roi_final.height == 0)
                return 0;

        path_planning(pi, pf, roi_initial, roi_final, frame);
        tracker->init(frame, roi_initial);
        cout << "Start the tracking process, press ESC to quit." << endl;

		createRobotConection(hints, res, status, socket_id);
		VideoWriter output;
		int ex = static_cast<int>(cap.get(CV_CAP_PROP_FOURCC));
		cout << CV_CAP_PROP_FOURCC << "   " << ex << endl;
		output.open("output.avi", CV_FOURCC('M','J','P','G'), 30, Size(frame.cols, frame.rows), true);

        for ( ;; ){

                cap >> frame_init;
                if(frame_init.rows == 0 || frame_init.cols == 0)
                        continue;

                frame = Mat(frame_init, workspace);
				//GaussianBlur(frame, frame, Size(3, 3), 1.5, 1.5);
                tracker->update(frame, roi_actual);
                // take the center point of actual roi
                get_localization(pa, roi_actual, angle_measured, frame);
                trace.push_back(pa);
                


                draw_path_plan(pi, pf, frame);
				float angle_ref = atan2(-(pf.y - pi.y), pf.x - pi.x) * 180 / PI;
				feedback_control(angle_measured, pf, pa);
                draw_trace(trace, frame);
                rectangle( frame, roi_initial, Scalar( 0, 0, 255 ), 1, 1 );
                rectangle( frame, roi_actual, Scalar( 0, 0, 255 ), 1, 1 );
                rectangle( frame, roi_final, Scalar( 0, 255, 0 ), 1, 1 );

                imshow("Robot Workspace", frame);
				output << frame;
				//imwrite("path_planning.avi", frame);
                //quit on ESC button
                if(waitKey(30) == 'q') break;
        }
		freeaddrinfo(res);
		close(socket_id);
		output_file.close();

        return 0;
}

void path_planning(Point2d& pi, Point2d& pf, Rect2d roi_initial, Rect2d roi_final, Mat& frame) {
        pf.x = roi_final.x + roi_final.width/2;
        pf.y = roi_final.y + roi_final.height/2;
        pi.x = roi_initial.x + roi_initial.width/2;
        pi.y = roi_initial.y + roi_initial.height/2;

        line(frame, pi, pf, Scalar(255, 255, 0), 1, 8, 0);
}

void get_localization(Point2d& pa, Rect2d& roi_actual, float& angle_measured, Mat frame) {
        pa.x = roi_actual.x + roi_actual.width/2;
        pa.y = roi_actual.y + roi_actual.height/2;

		Mat robot(frame, roi_actual);
		angle_measured = measureRobotOrientation(robot);

        //if(angle_measured < 0) angle_measured = 360 - angle_measured;
        //if(angle_measured > 180) angle_measured = angle_measured - 360;
}

float measureRobotOrientation(Mat robot) {
		float angle = 0;
		Mat robot_hsv;
		cvtColor(robot, robot_hsv, CV_BGR2HSV);
		// extract the Hue and Saturation channels
		int from_to[] = {0,0, 1,1};
		Mat hs(robot.size(), CV_8UC2);
		mixChannels(&robot_hsv, 1, &hs, 1, from_to, 2);
		// check the image for a specific range of H and S
		Mat mask_blue, mask_yellow;
		inRange(hs, Scalar(90, 90), Scalar(140, 255), mask_blue);
		inRange(hs, Scalar(0, 100), Scalar(60, 255), mask_yellow);

		Mat structuringElement3x3 = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
		erode(mask_blue, mask_blue, structuringElement3x3);
		erode(mask_yellow, mask_yellow, structuringElement3x3);

		vector<vector<Point> > contours_blue, contours_yellow;
		vector<Vec4i> hierarchy_blue, hierarchy_yellow;		
		findContours( mask_blue, contours_blue, hierarchy_blue, CV_RETR_TREE, CV_CHAIN_APPROX_SIMPLE, Point(0, 0) );
		findContours( mask_yellow, contours_yellow, hierarchy_yellow, CV_RETR_TREE, CV_CHAIN_APPROX_SIMPLE, Point(0, 0) );
		if(contours_blue.empty() || contours_yellow.empty()) return angle;
		vector<Point2f>center_blue( contours_blue.size() );
		vector<float>radius_blue( contours_blue.size() );
		vector<Point2f>center_yellow( contours_yellow.size() );
		vector<float>radius_yellow( contours_yellow.size() );
		
		//cout << "contours_blue: " << contours_blue.size() << endl;
		//cout << "contours_yellow: " << contours_yellow.size() << endl;

		vector<vector<Point> > contours_poly_blue( contours_blue.size() );
		for( int i = 0; i < contours_blue.size(); i++ ) { 
			approxPolyDP( Mat(contours_blue[i]), contours_poly_blue[i], 3, true );
			//boundRect[i] = boundingRect( Mat(contours_poly[i]) );
			minEnclosingCircle( (Mat)contours_poly_blue[i], center_blue[i], radius_blue[i] );
		}

		vector<vector<Point> > contours_poly_yellow( contours_yellow.size() );
		for( int i = 0; i < contours_yellow.size(); i++ ) { 
			approxPolyDP( Mat(contours_yellow[i]), contours_poly_yellow[i], 3, true );
			//boundRect[i] = boundingRect( Mat(contours_poly[i]) );
			minEnclosingCircle( (Mat)contours_poly_yellow[i], center_yellow[i], radius_yellow[i] );
		}

		if(!center_blue.empty() && !center_yellow.empty()) {
			angle = atan2(-(center_blue[0].y-center_yellow[0].y), center_blue[0].x-center_yellow[0].x ) * 180 / PI;
			angle = angle + 90;
			line(robot, center_blue[0], center_yellow[0], Scalar(0, 0, 255));
			imshow("robot", robot);
		}
		return angle;
}

void draw_path_plan(Point2d pi, Point2d pf, Mat& frame) {
        line(frame, pi, pf, Scalar(255, 255, 0), 1, 8, 0);
}

void draw_trace(vector<Point2d> trace, Mat& frame) {
        if(trace.size() > 1) {
                // connect points
                for(int i = 1; i < trace.size(); i++) {
                        line(frame, trace[i-1], trace[i], Scalar(0, 255, 255), 1, 8, 0);
                }
        }
}

void feedback_control(float angle_measured, Point pf, Point pa) {
		float b = (pf.y - pa.y);
		float c = pf.x - pa.x;
		float angle_ref = atan2(-b, c) * 180 / PI;
		
        int Vr = 20;
        float K = 1;
        float error = angle_ref - angle_measured;
        int Vl = 20 - K*error;
		// filter dead zone velocities (lower limit), which do not move the robot 
		//if(Vl > 0 && Vl < 25) Vl = 25;
		//else if(Vl < 0 && Vl > -25) Vl = -25;
		// filter high velocities whose robot is to quick (upper limit)
		if(Vl > 70) Vl = 70;
		else if(Vl < -70) Vl = -70;


		if(b < 10 && c < 10) {
			Vr = 0;
			Vl = 0;
		}

		output_file << "-------------------------- " << endl;
		output_file << "       angle_ref.: " << angle_ref << endl;
		output_file << "       angle_meas.: " << angle_measured << endl;
		output_file << "       error: " << error << endl;
		output_file << "       Vr: " << Vr << endl;
		output_file << "       Vl: " << Vl << endl;
		/*
		cout << "-------------------------- " << endl;
		cout << "       angle_ref.: " << angle_ref << endl;
		cout << "       angle_meas.: " << angle_measured << endl;
		cout << "       error: " << error << endl;
		cout << "       Vr: " << Vr << endl;
		cout 	 << "       Vl: " << Vl << endl;
		*/
		//vector<string> debug_to_file;
		//ostream_iterator<string> output_iterator(output_file, "\n");
    	//copy(debug_to_file.begin(), debug_to_file.end(), output_iterator);

		sendVelocities(Vr, Vl);
}

void createRobotConection(struct addrinfo& hints, struct addrinfo * res, int& status, int& socket_id) {

	//clear hints
	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_UNSPEC;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_flags = AI_PASSIVE;

	status = getaddrinfo("192.168.43.22","10000", &hints, &res);
	if(status != 0)
	{
		fprintf(stderr, "Error getaddrinfo\n");
		exit(1);
	}	 	
	
	socket_id = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
	if(socket_id < 0)
	{
		fprintf(stderr, "Error socket \n");
		exit(2);
	}
	
	status = connect(socket_id, res->ai_addr, res->ai_addrlen);
	if(status < 0)
	{
		fprintf(stderr, "Error connect \n");
		exit(3);
	}
}

void sendVelocities(int Vr, int Vl) {
	
	send(socket_id, to_string(Vr).c_str(), 2, 0);
	send(socket_id, to_string(Vl).c_str(), 2, 0);
}

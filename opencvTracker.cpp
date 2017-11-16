#include <opencv2/core/utility.hpp>
#include <opencv2/tracking.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>
#include <cstring>
#include "roiSelector.hpp"

using namespace std;
using namespace cv;
int main( int argc, char** argv ){
  // show help
  if(argc<2){
    cout<<
      " Usage: tracker <video_name>\n"
      " examples:\n"
      " example_tracking_kcf Bolt/img/%04d.jpg\n"
      " example_tracking_kcf faceocc2.webm\n"
      << endl;
    return 0;
  }
  // declares all required variables
  Rect2d roi, roi_final;
  Mat frame_init;
  // create a tracker object
  Ptr<Tracker> tracker = Tracker::create( "KCF" );
  // set input video
  std::string video = argv[1];
  VideoCapture cap(video);
  // get bounding box
  cap >> frame_init;
  Mat frame = Mat(frame_init, selectROI("camera", frame_init, true, false));
  roi=selectROI("tracker",frame);
  cout << roi.x << " " << roi.y << endl;
  roi_final=selectROI("tracker",frame);
  cout << roi_final.x << " " << roi_final.y << endl;
  //quit if ROI was not selected
  if(roi.width==0 || roi.height==0)
    return 0;
  // initialize the tracker
  tracker->init(frame,roi);
  // perform the tracking process
  printf("Start the tracking process, press ESC to quit.\n");
  for ( ;; ){
    // get frame from the video
    cap >> frame;
    // stop the program if no more images
    if(frame.rows==0 || frame.cols==0)
      break;
    // update the tracking result
    tracker->update(frame,roi);
    // draw the tracked object
    rectangle( frame, roi, Scalar( 255, 0, 0 ), 2, 1 );
	rectangle( frame, roi_final, Scalar( 255, 0, 0 ), 2, 1 );
    // show image with the tracked object
    imshow("tracker",frame);
    //quit on ESC button
    if(waitKey(40)==27)break;
  }
  return 0;
}

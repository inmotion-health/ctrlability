#import <AVFoundation/AVFoundation.h>

#include <boost/python.hpp>  // TODO: enable syntax highlighting in vscode
#include <iostream>
#include <string>

void hello() {
    // Get an array of available video devices (webcams).
    NSArray *videoDevices = [AVCaptureDevice devicesWithMediaType:AVMediaTypeVideo];

    int index = 0;
    for (AVCaptureDevice *device in videoDevices) {
        std::cout << "Index (heuristic for OpenCV): " << index << ", Name: " << [device.localizedName UTF8String]
                  << std::endl;
        index++;
    }
}

BOOST_PYTHON_MODULE(libctrlability) {
    boost::python::def("hello", hello);
}
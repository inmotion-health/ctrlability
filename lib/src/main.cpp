#include <boost/python.hpp>
#include <iostream>
#include <string>

void hello() {
    std::cout << "Hello, World! from C++" << std::endl;
}

BOOST_PYTHON_MODULE(libctrlability) {
    boost::python::def("hello", hello);
}
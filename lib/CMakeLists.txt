cmake_minimum_required(VERSION 3.15)
project(libctrlability)

find_package(ZLIB REQUIRED)
find_package(PythonLibs REQUIRED)
find_package(Boost REQUIRED COMPONENTS python)

include_directories(${PYTHON_INCLUDE_DIRS} ${Boost_INCLUDE_DIRS})

add_library(${PROJECT_NAME} SHARED src/main.cpp)
target_link_libraries(${PROJECT_NAME} ${PYTHON_LIBRARIES} Boost::python)
set_target_properties(${PROJECT_NAME} PROPERTIES PREFIX "" SUFFIX ".so")
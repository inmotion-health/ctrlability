#!/bin/bash

cd lib

conan build . -of=./build --build=missing

# copy .so to src
cp ./build/libctrlability.so ../src/libctrlability.so

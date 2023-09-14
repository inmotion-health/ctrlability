from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps


class App(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    requires = "boost/1.82.0"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True, "boost/*:without_python": False}

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

# UpDown recode project

This repository contains the UpDown Runtime, the UpDown emulator, and Other infrastructure built around LLVM


## Current content

| Name | Description|
|-----------|---------|
| [UpDown Runtime](runtime) | Top runtime for the UpDown infrastructure. Right now, this is intended to be used with Gem5. |
| [Simulated UpDown Runtime](simruntime) | Wrapper class that uses the same API of the UpDown runtime, but simulates the UpDown hardware |
| [Microbenchmarks](ubenchmarks) | Wrapper class that uses the same API of the UpDown runtime, but simulates the UpDown hardware |
| PythonSytanx Plugin | Plugin that allows to embed python code that describe a Codelet in the UpDown (alpha) |


## Building runtime and simruntime standalone

In order to build the runtime and the emulator for the updown lane, use the following commands

### Full compilation
Use the following command to include building tests, microbenchmarks, and debugging symbols. 
```
mkdir build_standalone && cd build_standalone
cmake -G Ninja               \
../llvm/updown/              \
-DUPDOWNRT_ENABLE_TESTS=ON   \
-DUPDOWNRT_ENABLE_UBENCH=ON   \
-DUPDOWN_ENABLE_DEBUG=ON     \
-DCMAKE_INSTALL_PREFIX=../install #Change to path to install
```
### Available CMake flags
The `-DUPDOWNRT_ENABLE_TESTS` enable compilation of tests for both the runtime and the simruntime
The `-DUPDOWNRT_ENABLE_UBENCH` enables compilation of the microbenchmarks
The `-DUPDOWN_ENABLE_DEBUG` flag is used to enable debbuging messages in the runtime system.
The `-DCMAKE_INSTALL_PREFIX=` determins the installation prefix. 

### Linking the runtime to an external program

Using the following code:

```
#include "updown.h"


int main() {
        UpDown::UDRuntime_t myRt;

        return 0;
}
```

You can build it with the following command

```
g++ -static main.cc -Iinstall/updown/include/ install/updown/lib/libUpDownRuntimeStatic.a -o main.exe
```

Available libraries are:

* `libUpDownRuntimeStatic.a`
* `libUpDownRuntime.so`
* `libUpDownSimRuntimeStatic.a`
* `libUpDownSimRuntime.so`
## Building LLVM

To enable the project it is necessary to add "updown" to the list of `-DLLVM_ENABLE_PROJECTS=`. See the following example. The important option is the last line. 

IMPORTANT: This is currently unsupported due to changes in the runtime interface that has not been reflected to the syntax plugin. 

```
git clone https://www.github.com/josemonsalve2/llvm-project
git checkout updown-recode
mkdir build && cd build
cmake -G Ninja                     \
../llvm/llvm/              \
-DCMAKE_BUILD_TYPE=Release         \
-DCMAKE_INSTALL_PREFIX=../install  \
-DCMAKE_C_COMPILER=gcc             \
-DCMAKE_CXX_COMPILER=g++           \
-DLLVM_APPEND_VC_REV=OFF           \
-DLLVM_ENABLE_ASSERTIONS=ON        \
-DBUILD_SHARED_LIBS=ON             \
-DLLVM_OPTIMIZED_TABLEGEN=ON       \
-DLLVM_CCACHE_BUILD=ON             \
-DCLANG_ENABLE_STATIC_ANALYZER=ON  \
-DCLANG_BUILD_EXAMPLES=ON          \
-DLLVM_ENABLE_PLUGINS=ON           \
-DCLANG_PLUGIN_SUPPORT=ON          \
-DLLVM_ENABLE_PROJECTS="clang;updown"
```


### Python Syntax

The updown syntax plugin allows to inline python code that describes a Codelet into C++. It translates this Code to a single python file that can be used to call the emulator. On the C++ world syntax will be changed to use the updown runtime.

Example code:

```
[[clang::syntax(UpDownPython)]] void f() {
    All this will be moved to python. Use python code
}

int main() {
    f();
    return 0;
}
```
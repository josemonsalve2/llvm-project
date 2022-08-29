# UpDown recode project

This repository contains software for UpDown using LLVM. 

## Building LLVM

To enable the project it is necessary to add "updown" to the list of `-DLLVM_ENABLE_PROJECTS=`. See the following example. The important option is the last line

```
git clone https://www.github.com/josemonsalve2/llvm-project
git checkout updown-recode
mkdir build && cd build
cmake -G Ninja                     \
../llvm-project/llvm/              \
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

## Building runtime only

```
mkdir build_standalone && cd build
cmake -G Ninja               \
../llvm-project-csp/updown/  \
-DUPDOWNRT_ENABLE_TESTS=ON   \
-DUPDOWN_ENABLE_DEBUG=ON
```

The `-DUPDOWN_ENABLE_DEBUG` flag is used to enable debbuging messages 
in the runtime system. Feel free to remove it. 

## Current content

| Name | Description|
|-----------|---------|
| PythonSytanx Plugin | Plugin that allows to embed python code that describe a Codelet in the UpDown |
| UpDown Runtime | Top runtime for the UpDown infrastructure |
| Simulated UpDown Runtime | Wrapper class that uses the updown runtime, but simulates the UpDown hardware (Under development) |

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
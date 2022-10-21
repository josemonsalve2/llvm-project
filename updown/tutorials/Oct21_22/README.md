# Kickstart tutorial

The purpose of this document is to summarize the hello world tutorial to be presented in the first quick off meeting of the UpDown Runtime Emulator. This tutorial will likely be out of date in the future, so be warned that this may be outdated if you read it beyond October 21st 2022.
The content of this document is as follows:

1. Building the runtime in standalone mode
2. Small terminology reminder
3. Creating a hello world program

## Building the runtime system in standalone mode

In the long term, the purpose of this runtime system is to be part of the backend of more interesting ideas to be explored with the help of compilers. However, for now 
it is possible to build the runtime in stand alone mode, generating both a static and dynamic versions of these libraries.

The runtime has two parts. A `runtime` that is meant to be used with a simulator or the real hardware (e.g. pointers are accessed directly), and a `simruntime` that creates a wrapper around a python emulator, and which should be API compatible with the `runtime`. Furthermore, this repository hosts a set of microbenchmarks, and some experimental elements to be used with compilers in the future.

In order to build the runtime in stand alone we will use cmake. We will use two locations: `UPDOWN_SOURCE_CODE` and `UPDOWN_INSTALL_DIR`. Change these accordingly. Let's begin by creating the work environment.

```Bash
# Create a work folder. Set env variables
mkdir updown_tutorial
cd updown_tutorial
git clone git@bitbucket.org:achien7242/llvm.git
mkdir build
mkdir install
mkdir exercises
export UPDOWN_SOURCE_CODE=`pwd`/llvm/updown
export UPDOWN_INSTALL_DIR=`pwd`/install
```

Now let's begin the compilation. This assumes you're in the updown_tutorial folder, as described above

```bash
# Let's build things
cd build
cmake $UPDOWN_SOURCE_CODE -DUPDOWNRT_ENABLE_TESTS=ON -DUPDOWNRT_ENABLE_UBENCH=ON -DUPDOWN_ENABLE_DEBUG=ON -DCMAKE_INSTALL_PREFIX=$UPDOWN_INSTALL_DIR
make -j
make install
```

In this step we are using the following flags:

* **UPDOWNRT_ENABLE_TESTS=ON** - This enables compilation of the different runtime tests (e.g. chech _simupdown/tests_ folder). These are good resources for examples on how to use the runtime API, but also it help us see if there are any mistakes.
* **UPDOWNRT_ENABLE_UBENCH=ON** - This enables compilation of the different microbenchmarks (e.g. chech _ubenchmarks_ folder). These were created to stress the runtime. While in the emulator mode they do not really faithfully measure performance (i.e. functional simulator), these are useful for verifying behavior and learning.
* **UPDOWN_ENABLE_DEBUG=ON** - This enables debug messages in the runtime. When running programs, you will see a lot of lines that read `[UPDOWN_INFO: file.cpp:line_number]`. Some messages are information, others are errors or warnings. These are useful to understand the interaction with the system. For long runs, you should build the runtime without debug mode.
* **UPDOWN_INSTALL_DIR=...** - This flag is necessary to be able to create a distributable runtime library.

### Notes
At the moment of writing this tutorial, the tests do not properly verify results, so these are verified by eyeballing the output. This is to be solved in the future.

## Small terminology reminder
This is just a quick remider of the updown terminology. 

### UpDowns, lanes and threads
The updown hardware is divided into UpDown units that contain multiple Lanes (e.g. 64 lanes). See the following picture for a representation of the updown lane.

![UpDown lanes](img/UpDownLane.png)

Each lane has an operand queue and an event queue. In order to send an updown event we need to set both separately. In the API runtime, we will see that the `UpDown::operands_t` class is used for creating the operands, and the `UpDown::event_t` is used to create an event. This event receives the `operands_t` as part of the arguments.

Each updown lane can have multiple activations. Currently, we refer to these activations as threads (See register contexts in the figure above). These "threads" execute concurrently, and they are switched upon execution of a `yield` or `yield_terminate` operation by another thread, and the arrival of a new event that "wakes up" a thread.

Each updown has access to some scratchpad memory.

### UpDown memory address space

From the perspective of the top it is possible to access the updown scratchpad and control signals. Each updown has a set of memory regions that is parametrized according to some values. 

The following figure represents the address space for the scratchpad memory, as seen from the top, considering multiple updowns.

![UpDown Scratchpad memory](img/ScratchpadMemoryAddresses.png)

The following figure represents the address space for the control signals for the different updowns, as seen from the top. 

![UpDown Control signals](img/ControlSignalsAddresses.png)

It is important to understand these signals:

* **Queues** These represent the location of the operand and event queues. It is used by the send event to submit a new event and its operands to the queue
* **Start exec** This signal is necessary because as of right now, the top does not perform an atomic operation to add events and operands. Therefore, it needs to signal the lane that a new event is ready for consumption. This may change in the future, but it is the mechanism we currently have in place 
* **Locks** Since these operations are not atomic, in order to guarantee atomic access from other events (i.e. that operands and events that are related to each other are inserted in the right order), this signal is needed to lock the queues. This will be set and unset by the send event mechanism

### Notes
At the moment of writing this tutorial, the updown runtime is not thread safe. Avoid calling updown runtime methods from multiple top threads, or use required critical regions.

## Creating a hello world program

Now let's create our first hello world program. this program will receive a number in an event operand, and it will send that number back with its value incremented by 1.

The Top code will look like this:

```C
//// Copy and paste this to a file name mainAddOne.cpp
#include "simupdown.h"

int main() {
  // Default configurations runtime
  UpDown::SimUDRuntime_t *test_rt = new UpDown::SimUDRuntime_t("addOneEFA", "AddOne", "./");

  printf("=== Base Addresses ===\n");
  test_rt->dumpBaseAddrs();
  printf("\n=== Machine Config ===\n");
  test_rt->dumpMachineConfig();

  // Help operands
  UpDown::word_t ops_data[] = {99};
  UpDown::operands_t ops(1, ops_data);

  // Events with operands
  UpDown::event_t evnt_ops(0 /*Event Label*/,
                           0 /*UD ID*/,
                           0 /*Lane ID*/,
                           UpDown::ANY_THREAD /*Thread ID*/,
                           &ops /*Operands*/);

  test_rt->send_event(evnt_ops);
  test_rt->start_exec(0,0);

  test_rt->test_wait_addr(0,0,0,100);

  return 0;
}

```

The UpDown program

```Python
### Copy and paste this to a file name addOneEFA.py. 
### Notice this name matches the runtime initialization above
from EFA import *

def AddOne():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() #Initial State? 

    #Add events to dictionary 
    event_map = {
        'add_1':0
    }

    tran0 = state0.writeTransition("eventCarry", state0, state1, event_map['add_1'])
    tran0.writeAction("mov_ob2reg OB_0 UDPR_1")
    tran0.writeAction("addi UDPR_1 UDPR_1 1")
    tran0.writeAction("mov_imm2reg UDPR_2 0")
    tran0.writeAction("mov_reg2lm UDPR_1 UDPR_2 4")
    tran0.writeAction("yield_terminate 2" )
    return efa

```

Let's add these files to the exercises folder we created earlier, and copy and paste the content of each of the code segments above. Then we should be able to compile it with the following command

```Bash
g++ mainAddOne.cpp -I$UPDOWN_INSTALL_DIR/updown/include -L$UPDOWN_INSTALL_DIR/updown/lib -lUpDownSimRuntime -lUpDownRuntime /usr/lib64/libpython3.6m.so -o mainAddOne.exe
# Before running make sure LD_LIBRARY_PATH contains the lib folder from the installation above
export LD_LIBRARY_PATH=$UPDOWN_INSTALL_DIR/updown/lib
./mainAddOne.exe
```

### Output:

```
[UPDOWN_INFO: updown.cpp:16] calc_addrmap: maddr: 0x80000000 spaddr: 0x200000000 ctrlAddr: 0x600000000
[UPDOWN_INFO: simupdown.cpp:15] Allocating 4294967296 bytes for mapped memory
[UPDOWN_INFO: simupdown.cpp:20] Allocating 2147483648 bytes for Scratchpad memory
[UPDOWN_INFO: simupdown.cpp:26] Allocating 2097152 bytes for control
[UPDOWN_INFO: simupdown.cpp:31] MapMemBase changed to 0x7F861DEF7010
[UPDOWN_INFO: simupdown.cpp:35] SPMemBase and UDbase changed to 0x7F859DEF6010
[UPDOWN_INFO: simupdown.cpp:38] ControlBase changed to 0x7F859DCF5010
[UPDOWN_INFO: upstream_pyintf.cc:56] Adding system paths: "./emulator:/home/jmonsalvediaz/tmp/updown_tutorial/install/updown/lib/emulator:/home/jmonsalvediaz/tmp/updown_tutorial/llvm/updown/simruntime/src/emulator"
[UPDOWN_INFO: upstream_pyintf.cc:82] Creating UpStream PyIntf with 1 lanes 65536 banksize
DataStore Size:65536
[UPDOWN_INFO: upstream_pyintf.cc:97] Initialized UpStream Python Interface with addOneEFA and AddOne
[UPDOWN_INFO: upstream_pyintf.cc:110] UpStream PyIntf, EFA created 
[UPDOWN_INFO: upstream_pyintf.cc:116] UpStream Processor Setup_Sim done 
[UPDOWN_INFO: updown.cpp:16] calc_addrmap: maddr: 0x7F861DEF7010 spaddr: 0x7F859DEF6010 ctrlAddr: 0x7F859DCF5010
=== Base Addresses ===
  mmaddr     = 0x7F861DEF7010
  spaddr    = 0x7F859DEF6010
  ctrlAddr  = 0x7F859DCF5010

=== Machine Config ===
  MapMemBase          = 0x7F861DEF7010
  UDbase              = 0x7F859DEF6010
  SPMemBase           = 0x7F859DEF6010
  ControlBase         = 0x7F859DCF5010
  EventQueueOffset    = (0x0)0
  OperandQueueOffset  = (0x1)1
  StartExecOffset     = (0x2)2
  LockOffset          = (0x3)3
  CapNumUDs           = (0x80)128
  CapNumLanes         = (0x80)128
  CapSPmemPerLane     = (0x20000)131072
  CapControlPerLane   = (0x80)128
  NumUDs              = (0x1)1
  NumLanes            = (0x1)1
  MapMemSize          = (0x100000000)4294967296
  SPBankSize          = (0x10000)65536
  SPBankSizeWords     = (0x40000)262144
[UPDOWN_INFO: updown.cpp:27] Locking 0x7F859DCF501C
[UPDOWN_INFO: updown.cpp:34] Sending Event:0 to [0,0,255] to queue at  0x7F859DCF5010
[UPDOWN_INFO: updown.cpp:39] Using Operands Queue 0x7F859DCF5014
[UPDOWN_INFO: updown.cpp:44] OB[0]: 0 (0x0)
[UPDOWN_INFO: updown.cpp:44] OB[1]: 99 (0x63)
[UPDOWN_INFO: updown.cpp:46] Unlocking 0x7F859DCF501C
[UPDOWN_INFO: upstream_pyintf.cc:151] Lane:0 Pushed into Operand Buffer: 0
[UPDOWN_INFO: upstream_pyintf.cc:151] Lane:0 Pushed into Operand Buffer: 99
[UPDOWN_INFO: upstream_pyintf.cc:139] Pushed Event:0, lane:0, tid:255 numop:1 
[UPDOWN_INFO: updown.cpp:62] Starting execution UD 0, Lane 0. Signal in  0x7F859DCF5018
[UPDOWN_INFO: upstream_pyintf.cc:293] EFA execute output, LaneID:0, Return State:-1, Num Sends: 0                            Exec_cycles:6, Actcnt:5 
[UPDOWN_INFO: simupdown.cpp:104] C++ Process executed python process - Returned -1
[UPDOWN_INFO: simupdown.cpp:263] Lane: 0 Yielded and Terminated - Writing result now
[UPDOWN_INFO: updown.cpp:139] Testing UD 0, Lane 0 to Top, offset 0. Addr 0x7F859DEF6010. Expected = 100, read = 100
[UPDOWN_INFO: updown.cpp:153] Testing UD 0, Lane 0 to Top, offset 0. Addr 0x7F859DEF6010. Expected = 100, read = 100. (Returning)
```

You can now play with the code above. An example is changing the debug level of the emulator itself through the interface:

```C++
// Change the following line for:
//UpDown::SimUDRuntime_t *test_rt = new UpDown::SimUDRuntime_t("addOneEFA", "AddOne", "./");
UpDown::SimUDRuntime_t *test_rt = new UpDown::SimUDRuntime_t("addOneEFA", "AddOne", "./", UpDown::EmulatorLogLevel::FULL_TRACE);
```

Build again and execute, you should be able to see each UpDown instruction being executed.



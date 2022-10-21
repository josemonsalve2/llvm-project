# Microbenchmarks

This folder contains a collection of microbenchmarks. Each subfolder contains a top program written in C++ and an upstream program written in Python

Following is the list of available microbenchmarks

## Event Rate Microbenchmark

This microbenchmark stresses the event creation by sending events to multiple event queues. These events will create a number of events to the same queue. This way, each event queue should be stressed equally. 

In order to execute this microbenchmark, use:

```
./eventRate <numevents> <numlanes> <numthreadsperlane> <mode> [<num_cores>] [<num_uds>]
```

### Note: 
Currently only the first two parameters are used. No multiprocessing on top, and no multi up down support yet 

## Lauch Latency Microbenchmark

This microbenchmark stresses the launch operation from the top. It creates a single event with multiple operands for each of the lanes.

In order to execute this microbenchmark, use:

```
./launchLatency <numoperands> <numlanes> <numthreadsperlane> <mode> [<num_cores>] [<num_uds>]
```

### Note: 
Currently only the first two parameters are used. No multiprocessing on top, and no multi up down support yet 

## DRAM Read Bandwidth 

Create multiple reads from different UpDown lanes. In order to saturate the bandwidth, each read message sends 
64 bytes at once. This means, the return event contains 64/4 operands. It is possible to control the overall memory movement
as long as it is a multiple of 64, and it is possible to control how many lanes will be part of the computation.

In order to execute this microbenchmark, use:

```
./updownDRAMReadBW <sizemovement> <numlanes> <numthreadsperlane> <mode> [<num_cores>] [<num_uds>]
```

### Note: 
Currently only the first two parameters are used. No multiprocessing on top, and no multi up down support yet 

## DRAM Write Bandwidth 

Create multiple writes from different UpDown lanes. In order to saturate the bandwidth, each write message sends 
64 bytes at once. This means, the return event contains 64/4 operands. It is possible to control the overall memory movement
as long as it is a multiple of 64, and it is possible to control how many lanes will be part of the computation.

In order to execute this microbenchmark, use:

```
./updownDRAMReadBW <sizemovement> <numlanes> <numthreadsperlane> <mode> [<num_cores>] [<num_uds>]
```

### Note: 
Currently only the first two parameters are used. No multiprocessing on top, and no multi up down support yet 
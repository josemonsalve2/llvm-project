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

## Note: 
Currently only the first two parameters are used. No multiprocessing on top, and no multi up down support yet 
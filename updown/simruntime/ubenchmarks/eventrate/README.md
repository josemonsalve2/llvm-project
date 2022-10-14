# Event Rate Microbenchmark

This microbenchmark stresses the event creation by sending events to multiple event queues. These events will create a number of events to the same queue. This way, each event queue should be stressed equally. 

In order to execute this microbenchmark, use:

```
./eventRate <numevents> <numlanes> <numthreadsperlane> <mode> [<num_cores>] [<num_uds>]
```

## Note: 
Currently only the first two parameters are used. No multiprocessing on top, and no multi up down support yet 
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <map>
#include <pthread.h>
#include <simupdown.h>
#include <vector>

#define USAGE                                                                  \
  "USAGE: ./updownDRAMWriteBW <size> <numlanes> <numthreadsperlane> <mode> "    \
  "[<num_cores>] [<num_uds>]"

void launch(int total_cores, int core_num, int num_lanes, int num_threads,
            int size) {

  UpDown::ud_machine_t machine;
  machine.NumLanes = num_lanes;

  int lane_num = 0;
  int last_lane_checked = 0;
  int lanes_pcore = num_lanes / total_cores;

  UpDown::SimUDRuntime_t rt(machine, "updownDRAMReadBWEFA", "MemReadBWTest",
                            "./");
  // UpDown::UDRuntime_t rt(machine);

  UpDown::word_t op_data[5];
  UpDown::operands_t ops(5, op_data);

  // Addresses are passed in two operands.
  uint64_t *test_region = reinterpret_cast<uint64_t*>(rt.mm_malloc(size));

  ops.set_operands(0, 2, &test_region); // Copy pointer to 2 operands
  ops.set_operand(2, size);

  // Init lanes
  for (int i = core_num * lanes_pcore; i < (core_num + 1) * lanes_pcore; i++) {
    UpDown::word_t data = 0;
    rt.t2ud_memcpy(&data /*top_ptr*/, 1 /*size in words*/, 0 /*Ud ID*/,
                   i /*LaneID*/, 0 /*offset in spmem*/);
  }

  printf("Starting launchs\n");
  for (int ln = 0; ln < lanes_pcore; ln++) {
    lane_num = core_num + total_cores * ln;
    ops.set_operand(3, rt.get_lane_physical_memory(0, lane_num));
    ops.set_operand(4, rt.get_lane_physical_memory(0, lane_num, sizeof(UpDown::word_t)));
    // Events with operands
    UpDown::event_t evnt_ops(
        0 /*Event Label*/, 0 /*UD ID*/, lane_num /*Lane ID*/,
        UpDown::ANY_THREAD /*Thread ID*/, &ops /*Operands*/);
    rt.send_event(evnt_ops);
  }

  // Start execution in all the lanes
  for (int ln = 0; ln < lanes_pcore; ln++) {
    lane_num = core_num + total_cores * ln;
    rt.start_exec(0, lane_num);
  }

  // Check for termination
  for (int ln = 0; ln < lanes_pcore; ln++) {
    lane_num = core_num + total_cores * ln;
    rt.test_wait_addr(0 /*UD ID*/, lane_num /*Lane ID*/, 0 /*Offset*/,
                      1 /*Expected value*/);
  }
  printf("All Events launched and threads terminated\n");
  return;
}

/// TODO: This microbenchmark does not support multiple UDs or Threads. Fixme
int main(int argc, char *argv[]) {
  uint32_t size = 0;
  int num_lanes = 1;
  int num_threads = 1;
  int core_num = 0;
  int mode = 0;
  int total_cores = 1;
  int total_ud = 1;

  if (argc < 5) {
    printf("Insufficient Input Params\n");
    printf("%s\n", USAGE);
    exit(1);
  }
  size = atoi(argv[1]);
  num_lanes = atoi(argv[2]);
  num_threads = atoi(argv[3]);
  mode = atoi(argv[4]);

  /*
    mode = 0 - single thread topcore, single updown
    mode = 1 - multi thread topcore, singe updown
    mode = 2 - multi thread topcore, multi updown
  */
  if (mode == 0) {
    printf("Single thread Topcore Single Updown!\n");
    total_cores = 1;
    core_num = 0;
    if (argv[5])
      total_cores = atoi(argv[5]);
    if (total_cores > 1 && argv[6])
      core_num = atoi(argv[6]);
  } else if (mode == 1) {
    printf("Multi thread Topcore Single Updown!\n");
    if (argv[5])
      total_cores = atoi(argv[5]);
    if (total_cores > 1 && argv[6])
      core_num = atoi(argv[6]);
  } else if (mode == 2) {
    printf("Multi thread Topcore Multi Updown!\n");
    if (argv[5])
      total_cores = atoi(argv[5]);
    if (total_cores > 1 && argv[6])
      core_num = atoi(argv[6]);
    if (argv[7])
      total_ud = atoi(argv[7]);
  } else {
    printf("Incorrect mode %d specified should be 0,1,2\n", mode);
    exit(1);
  }
  printf("Num Threads per Lane:%d\n", num_threads);
  printf("Size to use:%d\n", size);

  launch(total_cores, core_num, num_lanes, num_threads, size);

  printf("EventRate test done\n");
}
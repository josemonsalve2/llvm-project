#include <iostream>
#include <simupdown.h>

#define N 15

int main() {
  // Default configurations runtime
  UpDown::SimUDRuntime_t *test_rt = new UpDown::SimUDRuntime_t();

  printf("=== Base Addresses ===\n");
  test_rt->dumpBaseAddrs();
  printf("\n=== Machine Config ===\n");
  test_rt->dumpMachineConfig();

  uint32_t data[N];

  // Copy element to [0,0,0]
  test_rt->t2ud_memcpy(data /*ptr*/, 
                       N*sizeof(uint32_t) /*size*/, 
                       0 /*ud_id*/, 
                       0 /*lane_num*/, 
                       0 /*offset*/);

  // Copy element to [0,16,16]
  test_rt->t2ud_memcpy(data /*ptr*/, 
                       N*sizeof(uint32_t) /*size*/, 
                       0 /*ud_id*/, 
                       16 /*lane_num*/, 
                       16 /*offset*/);
  
  // Copy element from [0,0,0]
  test_rt->ud2t_memcpy(data /*ptr*/, 
                       N*sizeof(uint32_t) /*size*/, 
                       0 /*ud_id*/, 
                       0 /*lane_num*/, 
                       0 /*offset*/);

  // Copy element from [0,16,16]
  test_rt->ud2t_memcpy(data /*ptr*/, 
                       N*sizeof(uint32_t) /*size*/, 
                       0 /*ud_id*/, 
                       16 /*lane_num*/, 
                       16 /*offset*/);

  for (int i = 0; i < N; i++)
    data[i] = i;

  // Copy element to [0,16,16]
  test_rt->t2ud_memcpy(data /*ptr*/,
                       N*sizeof(UpDown::word_t) /*size*/,
                       0 /*ud_id*/,
                       16 /*lane_num*/,
                       16 /*offset*/);

  // Testing 
  for (int i = 0; i < N; i++)
    test_rt->test_addr(0,16,16+i*sizeof(UpDown::word_t),i);
  // Testing. This should never be blocking 
  // because we don't have UD side in this test
  // Just memory copy
  for (int i = 0; i < N; i++)
    test_rt->test_wait_addr(0,16,16+i*sizeof(UpDown::word_t),i);

  delete test_rt;

  return 0;
}
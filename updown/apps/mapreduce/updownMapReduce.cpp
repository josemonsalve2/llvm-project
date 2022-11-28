#include "simupdown.h"
#include <iostream>
using namespace std;

// #define INPUT_KVMAP_SIZE 640
// #define NUM_UNIQUE_KEY 10
#define NUM_WORKERS 4

struct naiveKVpair{
  uint32_t key;
  uint32_t value;
};

int main() {
  // Set up machine parameters
  UpDown::ud_machine_t machine;
  machine.NumLanes = 4;

  // Default configurations runtime
  UpDown::SimUDRuntime_t *naiveMR_rt = new UpDown::SimUDRuntime_t(machine, "GenMapreduceEFA", "GenerateNaiveMapReduceEFA", "./", UpDown::EmulatorLogLevel::FULL_TRACE);

  printf("=== Base Addresses ===\n");
  naiveMR_rt->dumpBaseAddrs();
  printf("\n=== Machine Config ===\n");
  naiveMR_rt->dumpMachineConfig();

  UpDown::word_t INPUT_KVMAP_SIZE = 12;
  UpDown::word_t NUM_UNIQUE_KEY = 4;

  // Allocate the array where the top and updown can see it:
  naiveKVpair* inKVMap = reinterpret_cast<naiveKVpair*>(naiveMR_rt->mm_malloc(INPUT_KVMAP_SIZE * sizeof(naiveKVpair)));
  naiveKVpair* outKVMap = reinterpret_cast<naiveKVpair*>(naiveMR_rt->mm_malloc(NUM_UNIQUE_KEY * sizeof(naiveKVpair)));

  // Initialize input key-value map in DRAM
  for (int i = 0; i < INPUT_KVMAP_SIZE; i++) {
    inKVMap[i].key = i & (NUM_UNIQUE_KEY-1);
    inKVMap[i].value = i;
    printf("Pair %d: key=%d value=%d DRAM_addr=%p\n", i, inKVMap[i].key, inKVMap[i].value, &inKVMap[i]);
  }

  // Initilize output key-value map in DRAM
  for (int i = 0; i < NUM_UNIQUE_KEY; i++) {
    outKVMap[i].key = i;
  }

  
  UpDown::word_t INPUT_KVMAP_PTR_OFFSET = 0;
  UpDown::word_t INPUT_KVMAP_LEN_OFFSET = 8;
  UpDown::word_t OUTPUT_KVMAP_PTR_OFFSET = 16;
  UpDown::word_t OUTPUT_KVMAP_LEN_OFFSET = 24;
  UpDown::word_t TERM_FLAG_ADDR = 128;

  // operands
  // OB_0_1: Pointer to inKVMap (64-bit DRAM address)
  // OB_2_3: Pointer to outKVMap (64-bit DRAM address) 
  // OB_4: Input kvmap length
  // OB_5: Output kvmap length (== number of unique keys in the inKBMap)
  // OB_6: sizeof(KVpair)
  UpDown::word_t ops_data[7];
  UpDown::operands_t ops(7, ops_data);
  ops.set_operands(0,2,&inKVMap);
  ops.set_operands(2,4,&outKVMap);
  ops.set_operand(4, INPUT_KVMAP_SIZE);
  ops.set_operand(5, NUM_UNIQUE_KEY);
  ops.set_operand(6, sizeof(naiveKVpair)); 
  // UpDown::word_t ops_data[1];
  // UpDown::operands_t ops(1, ops_data);
  // ops.set_operand(0, INPUT_KVMAP_SIZE);

  
  UpDown::event_t evnt_ops(1 /*Event Label*/,
                            0 /*UD ID*/,
                            0 /*Lane ID*/,
                            UpDown::CREATE_THREAD /*Thread ID*/,
                            &ops /*Operands*/);
  naiveMR_rt->send_event(evnt_ops);
  naiveMR_rt->start_exec(0,0);

  naiveMR_rt->test_addr(0,0,TERM_FLAG_ADDR>>2,1);


  return 0;
}
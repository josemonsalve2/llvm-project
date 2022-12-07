#include <iostream>
#include <simupdown.h>

/// N must be exactly divisible by NumUDs*NumLanes
#define N 160

int main() {
  // Set up machine parameters
  UpDown::ud_machine_t machine;
  machine.NumUDs = 4;
  machine.NumLanes = 4;
  // N must be exactly divisible by NumUDs*NumLanes
  unsigned int chunk = N/(machine.NumUDs*machine.NumLanes); 

  // Default configurations runtime
  UpDown::SimUDRuntime_t *test_rt = new UpDown::SimUDRuntime_t(machine, "memcpyEFA", "memcpyEFA", "./", UpDown::FULL_TRACE);

  printf("=== Base Addresses ===\n");
  test_rt->dumpBaseAddrs();
  printf("\n=== Machine Config ===\n");
  test_rt->dumpMachineConfig();

  long * mmArray = reinterpret_cast<long*>(test_rt->mm_malloc(sizeof(long)*N));
  long * mmArray2 = reinterpret_cast<long*>(test_rt->mm_malloc(sizeof(long)*N));

  for (int i = 0; i < N; i++)
    mmArray[i] = i;

  // 1 element at a time
  UpDown::word_t ops[5];
  ops[4] = chunk*sizeof(long);

  UpDown::operands_t op(5, ops);

  for (int ud = 0; ud < machine.NumUDs; ud++)
    for (int ln = 0; ln < machine.NumLanes; ln++) {
      long *mmptr = mmArray + chunk*(ud*machine.NumLanes + ln);
      long *mmptr2 = mmArray2 + chunk*(ud*machine.NumLanes + ln);
      op.set_operands(0,2,&mmptr);
      op.set_operands(2,4,&mmptr2);
      UpDown::event_t ev(0,ud,ln,UpDown::CREATE_THREAD,&op);

      test_rt->send_event(ev);

      test_rt->start_exec(ud,ln);

    }

  for (int ud = 0; ud < machine.NumUDs; ud++)
    for (int ln = 0; ln < machine.NumLanes; ln++)
      test_rt->test_wait_addr(ud,ln,0,1);


  for (int i = 0; i < N; i++)
    printf("AnArray2[%d] = %d\n", i, mmArray2[i]);

  delete test_rt;
  return 0;
}
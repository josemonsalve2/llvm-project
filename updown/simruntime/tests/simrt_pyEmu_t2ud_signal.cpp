#include "simupdown.h"
#include <iostream>
using namespace std;

int main() {
  // Set up machine parameters
  UpDown::ud_machine_t machine;
  machine.NumLanes = 4;

  // Default configurations runtime
  UpDown::SimUDRuntime_t *rt = new UpDown::SimUDRuntime_t(machine, "t2ud_signalEFA", "t2u_signal", "./", UpDown::EmulatorLogLevel::FULL_TRACE);

  printf("=== Base Addresses ===\n");
  rt->dumpBaseAddrs();
  printf("\n=== Machine Config ===\n");
  rt->dumpMachineConfig();
  
  UpDown::operands_t ops;

  UpDown::event_t evnt_ops(0 /*Event Label*/,
                            0 /*UD ID*/,
                            0 /*Lane ID*/,
                            UpDown::CREATE_THREAD /*Thread ID*/,
                            &ops /*Operands*/);
  rt->send_event(evnt_ops);
  rt->start_exec(0,0);

  UpDown::word_t data = 99;

  rt->t2ud_memcpy(&data, sizeof(data), 0, 0, 4);

  rt->test_addr(0,0,0,1);

  return 0;
}
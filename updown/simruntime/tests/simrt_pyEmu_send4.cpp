#include <iostream>
#include <simupdown.h>

int main() {
  // Default configurations runtime
  UpDown::SimUDRuntime_t *test_rt = new UpDown::SimUDRuntime_t("send4EFA", "send4EFA", "./", UpDown::EmulatorLogLevel::FULL_TRACE);

  printf("=== Base Addresses ===\n");
  test_rt->dumpBaseAddrs();
  printf("\n=== Machine Config ===\n");
  test_rt->dumpMachineConfig();

  int * mmDest = reinterpret_cast<int*>(test_rt->mm_malloc(sizeof(int)*2));
  UpDown::word_t ops[4];
  ops[2] = 0X1234;
  ops[3] = 0xFF;
  UpDown::operands_t op(4, ops);
  op.set_operands(0, 2, &mmDest);

  UpDown::event_t ev(0, 0, 0, UpDown::CREATE_THREAD, &op);

  test_rt->send_event(ev);

  test_rt->start_exec(0, 0);

  test_rt->test_wait_addr(0, 0, 0, 1);

  printf("val = %X\n", mmDest[0]);
  printf("val = %X\n", mmDest[1]);

  delete test_rt;
  return 0;
}
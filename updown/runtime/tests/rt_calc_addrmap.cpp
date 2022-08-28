#include <iostream>
#include <updown.h>

int main() {
  // Default configurations runtime
  UpDown::UDRuntime_t *test_rt = new UpDown::UDRuntime_t();

  printf("=== Base Addresses ===\n");
  test_rt->dumpBaseAddrs();
  printf("\n=== Machine Config ===\n");
  test_rt->dumpMachineConfig();

  delete test_rt;

  return 0;
}
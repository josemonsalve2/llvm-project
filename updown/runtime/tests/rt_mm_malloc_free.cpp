#include <iostream>
#include <updown.h>

int main() {
  // Default configurations runtime
  UpDown::UDRuntime_t *test_rt = new UpDown::UDRuntime_t();

  printf("=== Base Addresses ===\n");
  test_rt->dumpBaseAddrs();
  printf("\n=== Machine Config ===\n");
  test_rt->dumpMachineConfig();

  UpDown::ptr_t a_ptr, a_ptr2, a_ptr3, a_ptr4, a_ptr5;

  a_ptr = (UpDown::ptr_t)test_rt->mm_malloc(100*sizeof(UpDown::word_t));
  a_ptr2 = (UpDown::ptr_t)test_rt->mm_malloc(200*sizeof(UpDown::word_t));
  a_ptr3 = (UpDown::ptr_t)test_rt->mm_malloc(300*sizeof(UpDown::word_t));
  a_ptr4 = (UpDown::ptr_t)test_rt->mm_malloc(400*sizeof(UpDown::word_t));

  printf("\na_ptr = %lX\n", reinterpret_cast<uint64_t>(a_ptr));
  printf("a_ptr2 = %lX\n", reinterpret_cast<uint64_t>(a_ptr2));
  printf("a_ptr3 = %lX\n", reinterpret_cast<uint64_t>(a_ptr3));
  printf("a_ptr4 = %lX\n", reinterpret_cast<uint64_t>(a_ptr4));

  test_rt->mm_free(a_ptr2);
  test_rt->mm_free(a_ptr3);
  a_ptr5 = (UpDown::ptr_t)test_rt->mm_malloc(50*sizeof(UpDown::word_t));
  printf("a_ptr5 = %lX\n", reinterpret_cast<uint64_t>(a_ptr5));
  test_rt->mm_free(a_ptr4);
  test_rt->mm_free(a_ptr);
  test_rt->mm_free(a_ptr5);

  return 0;
}
// RUN: %clang_cc1 -verify -fopenmp -x c++ -triple powerpc64le-unknown-unknown -fopenmp-targets=nvptx64-nvidia-cuda -emit-llvm-bc %s -o %t-ppc-host.bc
// RUN: %clang_cc1 -verify -fopenmp -x c++ -triple nvptx64-nvidia-cuda -fopenmp-targets=nvptx64-nvidia-cuda -emit-llvm %s -fopenmp-is-device -fopenmp-host-ir-file-path %t-ppc-host.bc -o - -disable-llvm-optzns | FileCheck %s
// expected-no-diagnostics

int foo(int &a) { return a; }

int bar() {
  int a;
  return foo(a);
}

// CHECK: define weak void @__omp_offloading_{{.*}}maini1{{.*}}_l[[@LINE+5]](i32* nonnull align {{[0-9]+}} dereferenceable({{[0-9]+}}) %{{.*}})
// CHECK-NOT: @__kmpc_data_sharing_coalesced_push_stack

int maini1() {
  int a;
#pragma omp target parallel map(from:a)
  {
    int b;
    a = foo(b) + bar();
  }
  return a;
}

// parallel region
// CHECK: define {{.*}}void @{{.*}}(i32* noalias {{.*}}, i32* noalias {{.*}}, i32* nonnull align {{[0-9]+}} dereferenceable({{[0-9]+}}) %{{.*}})
// CHECK-NOT: call i8* @__kmpc_data_sharing_push_stack(
// CHECK: [[B_ADDR:%.+]] = alloca i32,
// CHECK: call {{.*}}[[FOO:@.*foo.*]](i32* nonnull align {{[0-9]+}} dereferenceable({{[0-9]+}}) [[B_ADDR]])
// CHECK: call {{.*}}[[BAR:@.*bar.*]]()
// CHECK-NOT: call void @__kmpc_data_sharing_pop_stack(
// CHECK: ret void

// CHECK: define {{.*}}[[FOO]](i32* nonnull align {{[0-9]+}} dereferenceable{{.*}})
// CHECK-NOT: @__kmpc_data_sharing_push_stack

// CHECK: define {{.*}}[[BAR]]()
// CHECK: [[SHARED_A:%.+]] = call i8* @__kmpc_data_sharing_push_stack(i64 4)
// CHECK: [[SHARED_A2:%.+]] = bitcast i8* [[SHARED_A]] to i32*
// CHECK: call {{.*}}[[FOO]](i32* nonnull align {{[0-9]+}} dereferenceable{{.*}} [[SHARED_A2]])
// CHECK: call void @__kmpc_data_sharing_pop_stack(i8* [[SHARED_A]])
// CHECK: ret i32

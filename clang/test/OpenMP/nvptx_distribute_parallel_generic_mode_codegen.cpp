// Test target codegen - host bc file has to be created first.
// RUN: %clang_cc1 -verify -fopenmp -fopenmp-version=45 -x c++ -triple powerpc64le-unknown-unknown -fopenmp-targets=nvptx64-nvidia-cuda -emit-llvm-bc %s -o %t-ppc-host.bc
// RUN: %clang_cc1 -verify -fopenmp -fopenmp-version=45 -x c++ -triple nvptx64-unknown-unknown -fopenmp-targets=nvptx64-nvidia-cuda -emit-llvm %s -fopenmp-is-device -fopenmp-host-ir-file-path %t-ppc-host.bc -o - -disable-llvm-optzns | FileCheck %s --check-prefix CHECK
// RUN: %clang_cc1 -verify -fopenmp -fopenmp-version=45 -x c++ -triple i386-unknown-unknown -fopenmp-targets=nvptx-nvidia-cuda -emit-llvm-bc %s -o %t-x86-host.bc
// RUN: %clang_cc1 -verify -fopenmp -fopenmp-version=45 -x c++ -triple nvptx-unknown-unknown -fopenmp-targets=nvptx-nvidia-cuda -emit-llvm %s -fopenmp-is-device -fopenmp-host-ir-file-path %t-x86-host.bc -o - -disable-llvm-optzns | FileCheck %s --check-prefix CHECK
// RUN: %clang_cc1 -verify -fopenmp -fopenmp-version=45 -fexceptions -fcxx-exceptions -x c++ -triple nvptx-unknown-unknown -fopenmp-targets=nvptx-nvidia-cuda -emit-llvm %s -fopenmp-is-device -fopenmp-host-ir-file-path %t-x86-host.bc -o - -disable-llvm-optzns | FileCheck %s --check-prefix CHECK

// RUN: %clang_cc1 -verify -fopenmp -x c++ -triple powerpc64le-unknown-unknown -fopenmp-targets=nvptx64-nvidia-cuda -emit-llvm-bc %s -o %t-ppc-host.bc
// RUN: %clang_cc1 -verify -fopenmp -x c++ -triple nvptx64-unknown-unknown -fopenmp-targets=nvptx64-nvidia-cuda -emit-llvm %s -fopenmp-is-device -fopenmp-host-ir-file-path %t-ppc-host.bc -o - -disable-llvm-optzns | FileCheck %s --check-prefix CHECK 
// RUN: %clang_cc1 -verify -fopenmp -x c++ -triple i386-unknown-unknown -fopenmp-targets=nvptx-nvidia-cuda -emit-llvm-bc %s -o %t-x86-host.bc
// RUN: %clang_cc1 -verify -fopenmp -x c++ -triple nvptx-unknown-unknown -fopenmp-targets=nvptx-nvidia-cuda -emit-llvm %s -fopenmp-is-device -fopenmp-host-ir-file-path %t-x86-host.bc -o - -disable-llvm-optzns | FileCheck %s --check-prefix CHECK
// RUN: %clang_cc1 -verify -fopenmp -fexceptions -fcxx-exceptions -x c++ -triple nvptx-unknown-unknown -fopenmp-targets=nvptx-nvidia-cuda -emit-llvm %s -fopenmp-is-device -fopenmp-host-ir-file-path %t-x86-host.bc -o - -disable-llvm-optzns | FileCheck %s --check-prefix CHECK

// expected-no-diagnostics
#ifndef HEADER
#define HEADER

int a;

int foo(int *a);

int main(int argc, char **argv) {
  int b[10], c[10], d[10];
#pragma omp target teams map(tofrom:a)
#pragma omp distribute parallel for firstprivate(b) lastprivate(c) if(a)
  for (int i= 0; i < argc; ++i)
    a = foo(&i) + foo(&a) + foo(&b[i]) + foo(&c[i]) + foo(&d[i]);
  return 0;
}


// CHECK: @__omp_offloading_{{.*}}_main_[[LINE:l.+]]_exec_mode = weak constant i8 0
// CHECK-NOT: call void @__kmpc_data_sharing_init_stack
// CHECK-NOT: call void @__kmpc_data_sharing_push_stack

// CHECK: define weak void @__omp_offloading_{{.*}}_main_[[LINE]]([10 x i32]* nonnull align 4 dereferenceable(40) %{{.+}}, [10 x i32]* nonnull align 4 dereferenceable(40) %{{.+}}, i32* nonnull align 4 dereferenceable(4) %{{.+}}, i{{64|32}} %{{.+}}, [10 x i32]* nonnull align 4 dereferenceable(40) %{{.+}})
// CHECK: [[CVOIDPTR:%.+]] = call i8* @__kmpc_data_sharing_push_stack(i{{32|64}} 40)
// CHECK: [[CSTACK:%.+]] = bitcast i8* [[CVOIDPTR]] to [10 x i{{32|64}}]*
// CHECK: call void @__kmpc_for_static_init_4(

// CHECK: call void [[PARALLEL:@.+]](

// CHECK: call void @__kmpc_for_static_fini(%struct.ident_t* @

// PAR: call void @__kmpc_data_sharing_pop_stack(i8* [[CVOIDPTR]])

// CHECK: define internal void [[PARALLEL]](
// CHECK-NOT: call i8* @__kmpc_data_sharing_push_stack(

// CHECK-NOT: call void @__kmpc_data_sharing_pop_stack(

#endif

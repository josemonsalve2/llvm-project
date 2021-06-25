# CPU-GPU Compression/decompression prototype

This branch uses nvcomp to allow for compression on the CPU and decompression on the GPU of data that is being moved from the host to the device. The runtime incepts the data movement and, using the nvcomp library, it compress the data in the CPU, send the compressed data + metadata, and adds a decompression kernel to the GPU. 

## Current limitations and TODOs:
The current implementation is terrible. So it is barely a prototype. These are some of the limitations

* Current max number of blocks is 1000 by default. Each block is `(1 << 16) = 65536 bytes` wide. This results in a maximum size of 65 MB. It is possible to change the max number of blocks and the size per block by using `LIBOMPTARGET_COMP_CHUNK_SIZE` and `LIBOMPTARGET_COMP_CHUNK_SIZE`. But this will also considerably increase the pre-allocated size.
* If the compressed size is larger than this limit, the program will crash ungracefully. Sorry
* Current implementation only uses GDeflate compression. The CPU performance is terrible. 

## How to build
I have added two flags to _CMake_:

* Where is _nvcomp_ installed: `-DLIBOMPTARGET_NVCOMP_PATH=/home/jmonsalvediaz/postdoc/p38/nvcomp/build`
* Where are the extra libraries (distributed by nvidia): `-DLIBOMPTARGET_NVCOMP_EXTRA_PATH=/home/jmonsalvediaz/postdoc/p38/nvcomp/ubuntu20.04/11.0/`

### Building _nvcomp_

The complete instructions for nvcomp can be found in (here)[https://github.com/NVIDIA/nvcomp]

1. Clone nvcomp `git clone https://github.com/NVIDIA/nvcomp.git`
2. Get the extras `wget https://developer.download.nvidia.com/compute/nvcomp/2.0/local_installers/nvcomp_exts_x86_64_ubuntu20.04-2.0.tar.gz`
3. Untar the extras `tar xvfs nvcomp_exts_x86_64_ubuntu20.04-2.0.tar.gz`
4. Create build dir `cd nvcomp && mkdir build && cd build`
5. cmake (assuming you're using cuda 11.2) `cmake -DNVCOMP_EXTS_ROOT=$(pwd)/../../ubuntu20.04/11.2/ -DCMAKE_INSTALL_PREFIX=$(pwd)/../../soft/nvcomp/ ..`
6. make it `make -j` Waiting time was about 5 minutes
7. Add it to `LD_LIBRARY_PATH` with `export LD_LIBRARY_PATH=$(pwd)/../../soft/nvcomp/lib:$(pwd)/../../soft/nvcomp/lib64:$LD_LIBRARY_PATH`

### Complete command that I am using:
Let's clone. If you skip nvcomp compilation remember to add it to the `LD_LIBRARY_PATH`!

```Bash
git clone https://github.com/josemonsalve2/llvm-project.git
cd llvm-project
git checkout compression
mkdir build && cd build
```

Now I build llvm with my mods. Assuming that we have ninja and assuming that the  `llvm-project` cloned directory is in the same directory that `nvcomp`.

```Bash
cmake ../llvm \
-DCMAKE_INSTALL_PREFIX=$(pwd)/../../soft/llvm-$(date +"%m%d%y") \
-DCMAKE_BUILD_TYPE=Release \
 -G Ninja \
 -DCMAKE_C_COMPILER=clang \
 -DCMAKE_CXX_COMPILER=clang++  \
 -DLLVM_ENABLE_PROJECTS='clang;openmp;lld;lldb'  \
 -DLLVM_APPEND_VC_REV=OFF \
 -DLLVM_ENABLE_ASSERTIONS=ON \
 -DLLVM_USE_LINKER=lld \
 -DBUILD_SHARED_LIBS=ON \
 -DLLVM_OPTIMIZED_TABLEGEN=ON \
 -DLLVM_CCACHE_BUILD=ON \
 -DCLANG_ENABLE_STATIC_ANALYZER=ON \
 -DLIBOMPTARGET_NVPTX_COMPUTE_CAPABILITIES=35,60,70,80 \
 -DOPENMP_ENABLE_LIBOMPTARGET=ON \
 -DLIBOMPTARGET_NVPTX_ENABLE_BCLIB=true \
 -DCLANG_OPENMP_NVPTX_DEFAULT_ARCH=sm_80 \
 -DLIBOMPTARGET_NVCOMP_PATH=$(pwd)/../../soft/nvcomp/ \
 -DLIBOMPTARGET_NVCOMP_EXTRA_PATH=$(pwd)/../../ubuntu20.04/11.2/ \
 -DLIBOMPTARGET_NVPTX_DEBUG=1 -DLIBOMPTARGET_ENABLE_DEBUG=1  ..

 ninja

 ninja install
```

Now have fun. 

## About GDeflate overhead. 
I honestly am not an expert in compression algorithms. But, here is a list of arrays that are create for GDeflate to work on the CPU and the GPU:

Assuming an input array of size N, and C chunks (i.e. code `CompNumChunks`), each of size Z (i.e. `CompChunkSize`);

* `C = ceil(N/Z)` (i.e. allocate one more if `N mod Z` is not 0)
* Input Array: `InputArray[N]` (i.e. CPU Pointer)
* An array containing the size of each chunk: `InputChunkSizes[C]` here most elements will be Z, except for the last one which will (`N mod Z != 0 ? N mod Z : Z`). (i.e. code `CompChunksSizes`)
* An array of pointers, each pointing to the beginning of each array: `InputChunkPtr[C]` (i.e. `CompInputPtrs`).
* An array for the output data, allocated to the max possible size: `CompressedData[ >> N]` (this means much larger than N). (i.e. code `CompOutputData`)
* A temporary data to remove padding in the compressed array `Tmp[Z]`. After compression each chunk (block) contains the compressed data, but it was originally allocated to be as large as the worst case scenario, so there is padding between the compressed chunks. (i.e. code `CompTmpData`)
* An array with the sizes of the compressed data in each chunk (block). (i.e. code `CompOutputSizes`)
* An array of pointers to the compressed block `CompOutputPtr[C]` in the CompressedData memory region. (i.e. code `CompOutPtrs`)
* An array of compressed data in the GPU where CompressedData is sent. (i.e. code `CompGpuCompressedData`)
* An array of GPU addressable pointers, in the Host, containing a pointer to each of the input blocks in the compressed data in the GPU. This array is pre-filled in the CPU and sent to the GPU. (i.e. code `CompGpuInputPtrsHst`)
* The corresponding array of pointers in the GPU (i.e. the copied version of the bullet right above this one) (i.e. code `CompGpuInPtrs`)
* An array of GPU addressable pointers, in the Host, containing a pointer to each of the output blocks in the decompressed data in the GPU. This array is pre-filled in the CPU and sent to the GPU. (i.e. code `CompGpuOutPtrsHst`)
* The corresponding array of pointers in the GPU (i.e. the copied version of the bullet right above this one) (i.e. code `CompGpuOutPtrs`)
* An array in the GPU containing the size of each chunk in the GPU. A copy of the CompOutSizes in the GPU (i.e. code `CompGpuChunkSizes`)
* An array in the GPU containing the size of each chunk in the GPU. A copy of the InputChunkSizes in the GPU (i.e. code `CompGpuCompressedSizes`)

## Running example

For the following code:

```C
#include <stdlib.h>
#include <stdio.h>
#include <omp.h>
#include <math.h>

#define N 1000000

int main () {
  float *A = (float *) malloc(sizeof(float)*N);
  float *B = (float *) malloc(sizeof(float)*N);
  float *C = (float *) malloc(sizeof(float)*N);
  float *testC = (float *) malloc(sizeof(float)*N);

  for (int i = 0; i < N; i++) {
          A[i] = rand() % 10;
          B[i] = rand() % 10;
          C[i] = rand() % 10;
          testC[i] = A[i] + B[i];
  }
#pragma omp target map(tofrom: A[0:N], B[0:N], C[0:N])
  {
    for (int i = 0; i < 10; i ++) {
      C[i] = A[i] + B[i];
    }
  }
  printf("Done, ready to test %f %f\n", C[0], testC[0]);

  return 0;
}
```

Building with:

```
clang -c -o main.o main.c -I. -fopenmp -fopenmp-targets=nvptx64 -g -Xopenmp-target -march=sm_80 
clang -o main.x main.o -I. -fopenmp -fopenmp-targets=nvptx64 -g -Xopenmp-target -march=sm_80 
```

The corresponding GPU profiling and traces are:

### No compression

```bash
[jmonsalvediaz@gpu06] [~/postdoc/p38/tests-llvm] [Fri Jun 25] [01:42 AM] (master) 
> nsys profile -s cpu --stats=true  ./main.x
Warning: LBR backtrace method is not supported on this platform. DWARF backtrace method will be used.
Collecting data...
Done, ready to test 9.000000 9.000000
Processing events...
Capturing symbol files...
Saving temporary "/tmp/nsys-report-9c27-75de-89d7-bbb8.qdstrm" file to disk...
Creating final output files...

Processing [==============================================================100%]
Saved report file to "/tmp/nsys-report-9c27-75de-89d7-bbb8.qdrep"
Exporting 4661 events: [==================================================100%]

Exported successfully to
/tmp/nsys-report-9c27-75de-89d7-bbb8.sqlite


CUDA API Statistics:

 Time(%)  Total Time (ns)  Num Calls    Average      Minimum     Maximum                Name             
 -------  ---------------  ---------  ------------  ----------  ----------  -----------------------------
    73.3       52,866,564          1  52,866,564.0  52,866,564  52,866,564  cuDevicePrimaryCtxRelease_v2 
     7.0        5,030,266          1   5,030,266.0   5,030,266   5,030,266  cuModuleLoadDataEx           
     5.8        4,152,800          3   1,384,266.7   1,257,041   1,448,005  cuMemcpyHtoDAsync_v2         
     5.4        3,918,877          8     489,859.6       2,520   1,125,270  cuMemAlloc_v2                
     3.1        2,231,349          1   2,231,349.0   2,231,349   2,231,349  cuLaunchKernel               
     2.4        1,736,730          3     578,910.0     486,839     730,542  cuMemcpyDtoHAsync_v2         
     2.0        1,437,665          1   1,437,665.0   1,437,665   1,437,665  cuModuleUnload               
     0.5          348,196         32      10,881.1       1,040     196,674  cuStreamCreate               
     0.3          249,124          3      83,041.3      66,071     114,942  cuMemFree_v2                 
     0.1           66,811         32       2,087.8       1,430       7,400  cuStreamDestroy_v2           
     0.0           35,921          1      35,921.0      35,921      35,921  cuMemcpyDtoH_v2              
     0.0            7,240          1       7,240.0       7,240       7,240  cuStreamSynchronize          
     0.0            6,950          1       6,950.0       6,950       6,950  cuMemcpyHtoD_v2              
     0.0            4,780          1       4,780.0       4,780       4,780  cuDevicePrimaryCtxSetFlags_v2



CUDA Kernel Statistics:

 Time(%)  Total Time (ns)  Instances   Average   Minimum  Maximum                  Name                 
 -------  ---------------  ---------  ---------  -------  -------  -------------------------------------
   100.0          222,080          1  222,080.0  222,080  222,080  __omp_offloading_30_736b0b47_main_l20



CUDA Memory Operation Statistics (by time):

 Time(%)  Total Time (ns)  Operations    Average    Minimum   Maximum       Operation     
 -------  ---------------  ----------  -----------  -------  ---------  ------------------
    78.6        4,194,961           4  1,048,740.3    2,911  1,400,294  [CUDA memcpy HtoD]
    21.4        1,144,134           4    286,033.5    5,120    393,954  [CUDA memcpy DtoH]



CUDA Memory Operation Statistics (by size in KiB):

   Total     Operations   Average   Minimum   Maximum       Operation     
 ----------  ----------  ---------  -------  ---------  ------------------
 11,718.754           4  2,929.688    0.004  3,906.250  [CUDA memcpy HtoD]
 11,718.751           4  2,929.688    0.001  3,906.250  [CUDA memcpy DtoH]



Operating System Runtime API Statistics:

 Time(%)  Total Time (ns)  Num Calls     Average     Minimum    Maximum         Name     
 -------  ---------------  ---------  -------------  -------  -----------  --------------
    49.1      303,045,683          2  151,522,841.5   15,721  303,029,962  sem_wait      
    33.4      206,203,867         34    6,064,819.6    1,020   42,694,390  poll          
    15.5       95,274,600      1,031       92,409.9    1,010   12,184,669  ioctl         
     1.2        7,516,210        147       51,130.7    1,390    1,072,868  mmap          
     0.2        1,259,141         61       20,641.7    1,060    1,110,799  fopen         
     0.2        1,158,998         22       52,681.7   13,070      331,126  sem_timedwait 
     0.1          551,913         91        6,065.0    3,570       50,860  fgets         
     0.1          461,052         82        5,622.6    1,290       25,590  open64        
     0.1          451,498         38       11,881.5    2,040      205,453  munmap        
     0.1          374,726          4       93,681.5   71,222      118,532  pthread_create
     0.0           82,282          1       82,282.0   82,282       82,282  pthread_join  
     0.0           60,461         24        2,519.2    1,370        8,190  write         
     0.0           49,601         11        4,509.2    1,120        8,480  sched_yield   
     0.0           32,260          6        5,376.7    1,880        8,160  open          
     0.0           23,690          4        5,922.5    1,400       10,380  fgetc         
     0.0           17,140         10        1,714.0    1,120        2,830  read          
     0.0            9,911          7        1,415.9    1,010        2,131  fclose        
     0.0            8,480          2        4,240.0    2,470        6,010  socket        
     0.0            7,280          1        7,280.0    7,280        7,280  pipe2         
     0.0            6,320          1        6,320.0    6,320        6,320  connect       
     0.0            5,720          2        2,860.0    2,250        3,470  fread         
     0.0            4,121          3        1,373.7    1,221        1,570  fcntl         
     0.0            2,550          2        1,275.0    1,130        1,420  sigaction     
     0.0            2,370          1        2,370.0    2,370        2,370  ftruncate     
     0.0            1,030          1        1,030.0    1,030        1,030  bind          

Report file moved to "/home/jmonsalvediaz/postdoc/p38/tests-llvm/report1.qdrep"
Report file moved to "/home/jmonsalvediaz/postdoc/p38/tests-llvm/report1.sqlite"


[jmonsalvediaz@gpu06] [~/postdoc/p38/tests-llvm] [Fri Jun 25] [01:43 AM] (master) 
> nsys stats --report gputrace report1.qdrep 
Using report1.sqlite export for stats reports.
Exporting [/soft/compilers/cuda/cuda-11.2.0/nsight-systems-2020.4.3/target-linux-x64/reports/gputrace.py report1.sqlite] to console... 

 Start(sec)  Duration(nsec)  CorrId  GrdX  GrdY  GrdZ  BlkX  BlkY  BlkZ  Reg/Trd  StcSMem  DymSMem    Bytes    Thru(MB/s)  SrcMemKd  DstMemKd        Device        Ctx  Strm                  Name                 
 ----------  --------------  ------  ----  ----  ----  ----  ----  ----  -------  -------  -------  ---------  ----------  --------  --------  ------------------  ---  ----  -------------------------------------
   0.355442           5,120      57                                                                         1       0.195  Device    Pageable  A100-PCIE-40GB (0)    1     7  [CUDA memcpy DtoH]                   
   0.355476           2,911      59                                                                         4       1.374  Pageable  Device    A100-PCIE-40GB (0)    1     7  [CUDA memcpy HtoD]                   
   0.357341       1,400,294      63                                                                 4,000,000   2,856.543  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                   
   0.359806       1,399,398      67                                                                 4,000,000   2,858.372  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                   
   0.362270       1,392,358      71                                                                 4,000,000   2,872.824  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                   
   0.364801         222,080      74     1     1     1    33     1     1       36    1,134        0                                             A100-PCIE-40GB (0)    1    13  __omp_offloading_30_736b0b47_main_l20
   0.365033         388,706      76                                                                 4,000,000  10,290.554  Device    Pageable  A100-PCIE-40GB (0)    1    13  [CUDA memcpy DtoH]                   
   0.365554         356,354      78                                                                 4,000,000  11,224.793  Device    Pageable  A100-PCIE-40GB (0)    1    13  [CUDA memcpy DtoH]                   
   0.366043         393,954      80                                                                 4,000,000  10,153.470  Device    Pageable  A100-PCIE-40GB (0)    1    13  [CUDA memcpy DtoH]                   

```

### Compression

```Bash
[jmonsalvediaz@gpu06] [~/postdoc/p38/tests-llvm] [Fri Jun 25] [01:44 AM] (master) 
> LIBOMPTARGET_COMPRESSION=1 nsys profile -s cpu --stats=true  ./main.x
Warning: LBR backtrace method is not supported on this platform. DWARF backtrace method will be used.
Collecting data...
Done, ready to test 9.000000 9.000000
Processing events...
Capturing symbol files...
Saving temporary "/tmp/nsys-report-2ff2-a7d6-316a-949e.qdstrm" file to disk...
Creating final output files...

Processing [==============================================================100%]
Saved report file to "/tmp/nsys-report-2ff2-a7d6-316a-949e.qdrep"
Exporting 72677 events: [=================================================100%]

Exported successfully to
/tmp/nsys-report-2ff2-a7d6-316a-949e.sqlite


CUDA API Statistics:

 Time(%)  Total Time (ns)  Num Calls    Average      Minimum     Maximum                Name             
 -------  ---------------  ---------  ------------  ---------  -----------  -----------------------------
    97.8      592,017,929          6  98,669,654.8      5,840  591,967,338  cudaLaunchKernel             
     0.8        4,932,165          1   4,932,165.0  4,932,165    4,932,165  cuModuleLoadDataEx           
     0.4        2,520,983          8     315,122.9      2,500    1,116,199  cuMemAlloc_v2                
     0.3        2,072,516          1   2,072,516.0  2,072,516    2,072,516  cuLaunchKernel               
     0.3        1,658,728          3     552,909.3    473,238      701,022  cuMemcpyDtoHAsync_v2         
     0.2        1,314,092          1   1,314,092.0  1,314,092    1,314,092  cuModuleUnload               
     0.1          316,676         32       9,896.1      1,080      162,842  cuStreamCreate               
     0.0          282,295          3      94,098.3     76,141      127,382  cuMemFree_v2                 
     0.0          249,045         15      16,603.0      3,000       69,741  cuMemcpyHtoDAsync_v2         
     0.0           84,842         32       2,651.3      1,390       13,641  cuStreamDestroy_v2           
     0.0           34,751          1      34,751.0     34,751       34,751  cuMemcpyDtoH_v2              
     0.0            7,330          1       7,330.0      7,330        7,330  cuStreamSynchronize          
     0.0            6,590          1       6,590.0      6,590        6,590  cuMemcpyHtoD_v2              
     0.0            4,740          1       4,740.0      4,740        4,740  cuDevicePrimaryCtxSetFlags_v2
     0.0            1,170          1       1,170.0      1,170        1,170  cuInit                       
     0.0              440          1         440.0        440          440  cuDevicePrimaryCtxRelease_v2 



CUDA Kernel Statistics:

 Time(%)  Total Time (ns)  Instances    Average     Minimum    Maximum                                                   Name                                                
 -------  ---------------  ---------  -----------  ---------  ---------  ----------------------------------------------------------------------------------------------------
    95.7        5,507,396          3  1,835,798.7  1,812,674  1,851,233  void gdeflate::gdeflateDecompress<2>(unsigned int const* const*, unsigned char* const*, unsigned in…
     3.8          219,552          1    219,552.0    219,552    219,552  __omp_offloading_30_736b0b47_main_l20                                                               
     0.5           28,544          3      9,514.7      9,472      9,536  gdeflate::zeroOutput(unsigned long const*, unsigned long, void* const*)                             



CUDA Memory Operation Statistics (by time):

 Time(%)  Total Time (ns)  Operations   Average   Minimum  Maximum      Operation     
 -------  ---------------  ----------  ---------  -------  -------  ------------------
    84.0        1,081,728           4  270,432.0    5,120  365,280  [CUDA memcpy DtoH]
    16.0          205,919          16   12,869.9    2,463   57,056  [CUDA memcpy HtoD]



CUDA Memory Operation Statistics (by size in KiB):

   Total     Operations   Average   Minimum   Maximum       Operation     
 ----------  ----------  ---------  -------  ---------  ------------------
  1,954.801          16    122.175    0.004    649.883  [CUDA memcpy HtoD]
 11,718.751           4  2,929.688    0.001  3,906.250  [CUDA memcpy DtoH]



Operating System Runtime API Statistics:

 Time(%)  Total Time (ns)  Num Calls      Average       Minimum     Maximum           Name     
 -------  ---------------  ---------  ----------------  -------  --------------  --------------
    50.1   20,693,097,239          2  10,346,548,619.5   33,521  20,693,063,718  sem_wait      
    49.7   20,532,735,578        236      87,003,116.9    2,160     100,173,082  poll          
     0.2       68,862,173        744          92,556.7    1,020      12,261,341  ioctl         
     0.0        2,011,278         90          22,347.5    1,310         570,770  mmap          
     0.0        1,260,292         59          21,360.9    1,010       1,130,500  fopen         
     0.0          652,223         11          59,293.0   11,140         350,186  sem_timedwait 
     0.0          518,288         89           5,823.5    3,700          61,171  fgets         
     0.0          511,267          4         127,816.8   89,561         205,313  pthread_create
     0.0          493,251         82           6,015.3    1,220          25,031  open64        
     0.0           44,641         15           2,976.1    1,000          11,260  sched_yield   
     0.0           31,150         12           2,595.8    1,260           4,880  write         
     0.0           29,780          6           4,963.3    1,700           9,090  open          
     0.0           25,740         10           2,574.0    1,770           3,330  munmap        
     0.0           14,491          3           4,830.3    1,000           8,271  fgetc         
     0.0            8,750          5           1,750.0    1,110           2,200  read          
     0.0            7,050          2           3,525.0    2,380           4,670  socket        
     0.0            6,330          1           6,330.0    6,330           6,330  pipe2         
     0.0            5,270          1           5,270.0    5,270           5,270  connect       
     0.0            5,180          2           2,590.0    1,740           3,440  fread         
     0.0            4,310          3           1,436.7    1,170           1,970  fcntl         
     0.0            2,260          2           1,130.0    1,010           1,250  fclose        
     0.0            1,960          1           1,960.0    1,960           1,960  ftruncate     
     0.0            1,450          1           1,450.0    1,450           1,450  bind          
     0.0            1,180          1           1,180.0    1,180           1,180  sigaction     

Report file moved to "/home/jmonsalvediaz/postdoc/p38/tests-llvm/report2.qdrep"
Report file moved to "/home/jmonsalvediaz/postdoc/p38/tests-llvm/report2.sqlite"
[jmonsalvediaz@gpu06] [~/postdoc/p38/tests-llvm] [Fri Jun 25] [01:45 AM] (master) 
> nsys stats --report gputrace report2.qdrep 
Using report2.sqlite export for stats reports.
Exporting [/soft/compilers/cuda/cuda-11.2.0/nsight-systems-2020.4.3/target-linux-x64/reports/gputrace.py report2.sqlite] to console... 

 Start(sec)  Duration(nsec)  CorrId  GrdX  GrdY  GrdZ  BlkX  BlkY  BlkZ  Reg/Trd  StcSMem  DymSMem    Bytes    Thru(MB/s)  SrcMemKd  DstMemKd        Device        Ctx  Strm                                                  Name                                                
 ----------  --------------  ------  ----  ----  ----  ----  ----  ----  -------  -------  -------  ---------  ----------  --------  --------  ------------------  ---  ----  ----------------------------------------------------------------------------------------------------
   0.277280           5,120      57                                                                         1       0.195  Device    Pageable  A100-PCIE-40GB (0)    1     7  [CUDA memcpy DtoH]                                                                                  
   0.277312           2,880      59                                                                         4       1.389  Pageable  Device    A100-PCIE-40GB (0)    1     7  [CUDA memcpy HtoD]                                                                                  
   6.901572          56,833      63                                                                   664,956  11,700.174  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
   6.901636           2,528      65                                                                       496     196.203  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
   6.901643           2,495      66                                                                       496     198.798  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
   6.901649           2,560      67                                                                       496     193.750  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
   6.901656           2,560      68                                                                       496     193.750  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
   7.505377           9,472     174    62     1     1   128     1     1       18        0        0                                             A100-PCIE-40GB (0)    1    13  gdeflate::zeroOutput(unsigned long const*, unsigned long, void* const*)                             
   7.505391       1,851,233     175    31     1     1    32     2     1       55    3,072        0                                             A100-PCIE-40GB (0)    1    13  void gdeflate::gdeflateDecompress<2>(unsigned int const* const*, unsigned char* const*, unsigned in…
  14.129345          57,056     179                                                                   665,324  11,660.895  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
  14.129410           3,233     181                                                                       496     153.418  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
  14.129418           2,463     182                                                                       496     201.380  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
  14.129425           2,720     183                                                                       496     182.353  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
  14.129431           2,752     184                                                                       496     180.233  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
  14.129438           9,536     185    62     1     1   128     1     1       18        0        0                                             A100-PCIE-40GB (0)    1    13  gdeflate::zeroOutput(unsigned long const*, unsigned long, void* const*)                             
  14.129449       1,812,674     186    31     1     1    32     2     1       55    3,072        0                                             A100-PCIE-40GB (0)    1    13  void gdeflate::gdeflateDecompress<2>(unsigned int const* const*, unsigned char* const*, unsigned in…
  20.742035          57,056     190                                                                   665,480  11,663.629  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
  20.742106           2,880     192                                                                       496     172.222  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
  20.742113           2,463     193                                                                       496     201.380  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
  20.742119           2,720     194                                                                       496     182.353  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
  20.742126           2,720     195                                                                       496     182.353  Pageable  Device    A100-PCIE-40GB (0)    1    13  [CUDA memcpy HtoD]                                                                                  
  20.742133           9,536     196    62     1     1   128     1     1       18        0        0                                             A100-PCIE-40GB (0)    1    13  gdeflate::zeroOutput(unsigned long const*, unsigned long, void* const*)                             
  20.742144       1,843,489     197    31     1     1    32     2     1       55    3,072        0                                             A100-PCIE-40GB (0)    1    13  void gdeflate::gdeflateDecompress<2>(unsigned int const* const*, unsigned char* const*, unsigned in…
  20.744196         219,552     200     1     1     1    33     1     1       36    1,134        0                                             A100-PCIE-40GB (0)    1    13  __omp_offloading_30_736b0b47_main_l20                                                               
  20.744423         365,280     202                                                                 4,000,000  10,950.504  Device    Pageable  A100-PCIE-40GB (0)    1    13  [CUDA memcpy DtoH]                                                                                  
  20.744914         355,296     204                                                                 4,000,000  11,258.218  Device    Pageable  A100-PCIE-40GB (0)    1    13  [CUDA memcpy DtoH]                                                                                  
  20.745388         356,032     206                                                                 4,000,000  11,234.945  Device    Pageable  A100-PCIE-40GB (0)    1    13  [CUDA memcpy DtoH]                                                                                  

```
#include "Snap.h"
#include <cstdio>
#include <cstdlib>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <vector>
#include <map>

#include <thread>
#include <chrono>
#include <pthread.h>
// #include <gem5/m5ops.h>

#define GAMMA 3
#define USAGE "USAGE: ./triangle-count-upstream-jshun-mmap <edge_list_file> <numlanes> <numthreadsperlane> <mode> <[start_node]> <[numnodes]>"

typedef uint32_t* ptr;

volatile uint32_t *eaddr ; //= (uint32_t *)(UBASE+EBASE);
volatile uint32_t *oaddr ; //= (uint32_t *)(UBASE+OBASE);
volatile uint32_t *saddr ; //= (uint32_t *)(UBASE+SBASE);
volatile uint32_t *exec  ; //= (uint32_t *)(UBASE+EXEC);
volatile uint32_t *status ; //= (uint32_t *)(UBASE+STATBASE);
//uint32_t *res = (uint32_t *)(UBASE+RESBASE);

void calc_addrmap(int num_lanes, uint64_t memsize){
  uint64_t ubase = memsize;
  saddr = (uint32_t *)ubase;
  eaddr = (uint32_t *)(ubase + 2*num_lanes*LMBANK_SIZE);
  oaddr = (uint32_t *)(eaddr + 64);
  exec = (uint32_t *)(oaddr + 64);
  status = (uint32_t *)(exec + 64);
  //#ifdef DEBUG
    printf("ubase:%lx\nsaddr:%lx\neaddr:%lx\noaddr:%lx\nexec:%lx\nstatus:%lx\n",\
            ubase, saddr, eaddr, oaddr, exec, status);
  //#endif
}

struct vertex{
  uint32_t deg;
  uint32_t id;
  ptr neigh;
  #ifdef DEBUG
    void print_v(void){
      printf("Deg:%d,ID:%d,Neigh:%x\n", deg, id, neigh);
    }
  #endif
};

struct event{
  uint8_t event_label;
  uint8_t lane_id;
  uint8_t thread_id;
  uint8_t num_operands;
  uint32_t ev_word;
  event(void){
    event_label = 0;
    lane_id = 0;
    thread_id = 0xff;
    num_operands = 0; 
    ev_word = ((lane_id << 24) & 0xff000000) | ((thread_id << 16) & 0xff0000) | ((num_operands << 8) & 0xff00) | (event_label & 0xff);
  }
  void setevent_word(uint8_t e_label, uint8_t noperands, uint8_t lid = 0, uint8_t tid = 0xff){
    event_label = e_label;
    num_operands = noperands;
    lane_id = lid;
    thread_id = tid;
    ev_word = ((lane_id << 24) & 0xff000000) | ((thread_id << 16) & 0xff0000) | ((num_operands << 8) & 0xff00) | (event_label & 0xff);
  }
  uint32_t getevent_word(void){
    return ev_word;
  }
};

struct operands{
  uint32_t* data;
  uint8_t num_operands;
  void setoperands(uint8_t num, uint32_t* oper, uint32_t cont = 0){
    num_operands = num;
    data = (uint32_t*)malloc(sizeof(uint32_t)*(num_operands+1));
    data[0]=cont; // Fake continuation
    for(uint8_t i=1;i<num_operands+1;i++)
      data[i]=oper[i-1];
  }
};

typedef struct event event_t;
typedef struct operands operands_t;

struct debug_vertex{
  int v1;
  int v2;
};

void send_event(uint32_t lane_num, event_t ev){
  *(eaddr+lane_num) = ev.ev_word;
  //*(status+lane_num) = 0;
}

void send_operands(uint32_t lane_num, operands_t op){
  *(status+lane_num) = 1;
  for(uint8_t i=0; i<op.num_operands+1;i++){
    *(oaddr+lane_num) = op.data[i];
    #ifdef DEBUG_DETAIL
     printf("OB[%d]:%d,", i, op.data[i]);
    #endif
  }
  delete op.data;
  #ifdef DEBUG_DETAIL
  printf("\n");
  #endif
  //*(status+lane_num) = 0;
}

void start_exec(uint32_t lane_num){
  *(exec+lane_num) = 1;
  *(status+lane_num) = 0;
}

void init_lane(uint32_t lane_num, uint32_t offset=0, uint32_t value=0){
  *(saddr + LMBANK_SIZE_4B*lane_num + offset) = (uint32_t)value;
}

uint32_t check_lane(uint32_t lane_num, uint32_t offset=0){
  uint32_t temp = (uint32_t) *(saddr + LMBANK_SIZE_4B*lane_num + offset);
  return temp;
}

uint32_t getresult(uint32_t lane_num, uint32_t offset=0){
  //printf("getresult:%lx\n", saddr+LMBANK_SIZE_4B*lane_num+offset);
  uint32_t temp = (uint32_t) *(saddr + LMBANK_SIZE_4B*lane_num + offset);
  return temp;
}

void launch_upstream_kernel(uint32_t num_operands, uint32_t* operands, uint8_t elabel, uint32_t lane_num){
  //init_lane(lane_num, 0, 0);
  operands_t op;
  //printf("Lane:%d, setting operands\n");
  op.setoperands(num_operands, operands);
  event_t ev;
  //printf("Lane:%d, setting event_word\n");
  ev.setevent_word(elabel, num_operands, lane_num);
  //printf("Lane:%d, send operands\n");
  send_operands(lane_num, op);
  //printf("Lane:%d, send event\n");
  send_event(lane_num, ev);
  //printf("Lane:%d, start_exec\n");
  start_exec(lane_num);
}
//#pragma GCC push_options
//#pragma GCC optimize("O0")
// op1_2 - :vertex_list_base , op_3:v1_size, op_4_5: v1_neighlist op_6:start, op_7:total neighs
void launch_upstream_vertex(uint32_t op1, uint32_t op2, uint32_t op3, uint32_t op4, uint32_t op5, \
                            uint32_t op6, uint32_t op7, int num_operands, \
                            uint8_t elabel, uint32_t cont, uint32_t lane_num){
  uint32_t ev_word = ((lane_num << 24) & 0xff000000) | ((0xff << 16) & 0xff0000) | ((num_operands << 8) & 0xff00) | (elabel & 0xff);
  *(status+lane_num) = 1;
  // Send all the operands
  //printf("%d\n", cont);
  *(oaddr+lane_num) = cont; //fake continuation
  //printf("%d\n", op1);
  *(oaddr+lane_num) = op1;
  //printf("%d\n", op2);
  *(oaddr+lane_num) = op2;
  //printf("%d\n", op3);
  *(oaddr+lane_num) = op3;
  //printf("%d\n", op4);
  *(oaddr+lane_num) = op4;
  //printf("%d\n", op5);
  *(oaddr+lane_num) = op5;
  //printf("%d\n", op6);
  *(oaddr+lane_num) = op6;
  //printf("%d\n", op7);
  *(oaddr+lane_num) = op7;
  // Event
  *(eaddr+lane_num) = ev_word;
  //Exec
  *(exec+lane_num) = 1;
  // UnLock
  *(status+lane_num) = 0;

}
//#pragma GCC pop_options

long tricount_upstream_multi(struct vertex *g_v, uint32_t snode, uint32_t enode, int num_launch_threads, int cont, int num_lanes){
  long tricount=0, local_tri=0;
  long numprobes=0;
  long numthreads=0;
  long numedges=0;
  int num_operands=7;
  int* threads_launched = (int*)malloc(sizeof(int)*num_lanes);
  int init_phase=1;
  int init_lanes_set=0;
  int lane_num=0;
  int last_lane_checked=0;
  unsigned int ready_idx=0; 
  unsigned int launch_idx=0; 
  int num_ready = num_lanes*num_launch_threads;
  uint32_t** op = (uint32_t**)malloc(sizeof(uint32_t*)*num_ready);
  for(int i=0;i<num_ready;i++){
    op[i]=(uint32_t*)malloc(sizeof(uint32_t)*num_operands);
  }
  uint32_t* lm_start_addr=(uint32_t*)malloc(sizeof(uint32_t)*num_launch_threads);
  int num_neighs_pthread=(LMBANK_SIZE_4B-2*num_launch_threads)/num_launch_threads;
  for(int i=0;i<num_launch_threads;i++){
    lm_start_addr[i]=(num_neighs_pthread+2)*i;
  }

  uint32_t op1,op2,op3,op4,op6,op7,op5,opcache;
  uint32_t start_offset, end_offset;
  int num_neighs_launched, cached, thread_state;
  struct vertex v1, v2;
  for(int i=0; i< num_lanes; i++){
    for(int j=0; j<num_launch_threads;j++){
      init_lane(i, lm_start_addr[j], 1); // status
      init_lane(i, lm_start_addr[j]+1, 0); // tricount
    }
    threads_launched[i] = 0;
  }
  int max_neigh=(LMBANK_SIZE - 8)/4;
  int numrounds=0;
  for(int i=snode; i <=enode;i++){
    v1 = *(g_v+i);
    numrounds = v1.deg/num_neighs_pthread; // Will the vertex fit into LM?
    if(v1.deg % max_neigh != 0)
        numrounds+=1;
    for(int j=0;j <numrounds; j++){
      start_offset = j*num_neighs_pthread;
      end_offset = (j+1)*num_neighs_pthread;
      if(j == numrounds-1)
          end_offset=v1.deg;
      // Store vertex in cache
      op[ready_idx][0]=((uint64_t)g_v) & 0xffffffff; // OB_2
      op[ready_idx][1]=(((uint64_t)g_v) >> 32) & 0xffffffff; //OB_3
      op[ready_idx][2]=((uint64_t)v1.neigh) & 0xffffffff; //OB_6
      op[ready_idx][3]=(((uint64_t)v1.neigh) >> 32) & 0xffffffff;
      op[ready_idx][4]=start_offset; //OB_3
      op[ready_idx][5]=end_offset;
      op[ready_idx][6]=LMBANK_SIZE*lane_num;
      ready_idx++;//=(ready_idx+1)%num_ready; //th_launch_idx+1)%num_launch_threads;
      if(ready_idx==num_ready){
        if(init_phase){
          for(int ln=0; ln < num_lanes && launch_idx != ready_idx; ln++){
            for(int th=0;th < num_launch_threads && launch_idx != ready_idx; th++){
              op6 =lm_start_addr[th]*4+ln*LMBANK_SIZE;
              init_lane(ln, lm_start_addr[th], 0); // triangle count all threads
              launch_upstream_vertex(op[launch_idx][0],op[launch_idx][1], \
                                     op[launch_idx][2],op[launch_idx][3], \
                                     op[launch_idx][4],op[launch_idx][5], \
                                     op6, num_operands, 0, cont, ln);
              launch_idx++;
              numthreads++;
            }
          }
          init_phase=0;
        }else{
          int thread_state=0;
          int num_threads_rdy=0;
          for(;launch_idx!=ready_idx;last_lane_checked=(last_lane_checked+1)%num_lanes){
            for(int tl=0; tl<num_launch_threads && launch_idx != ready_idx;tl++){
              thread_state=check_lane(last_lane_checked, lm_start_addr[tl]);
              if(thread_state==0){
                      continue;
              }else{
                lane_num=last_lane_checked;
                op6=lm_start_addr[tl]*4+LMBANK_SIZE*lane_num;
                local_tri=getresult(lane_num,lm_start_addr[tl]+1);
                tricount=tricount+local_tri; // Result is stored in lmbase + 4
                init_lane(lane_num, lm_start_addr[tl], 0); // triangle count all threads
                init_lane(lane_num, lm_start_addr[tl]+1, 0); // triangle count all threads
                launch_upstream_vertex(op[launch_idx][0],op[launch_idx][1], \
                                     op[launch_idx][2],op[launch_idx][3], \
                                     op[launch_idx][4],op[launch_idx][5], \
                                     op6, num_operands, 0, cont, lane_num);
                launch_idx++;
                numthreads++;
              }
            }
          }
        }
        ready_idx=0;
        launch_idx=0;
      }
    }
  }
  // Vertices left in queue? 
  for(int tl=0; tl<num_launch_threads && launch_idx != ready_idx;tl++){
    for(;launch_idx!=ready_idx;lane_num=(lane_num+1)%num_lanes){
      thread_state=check_lane(lane_num, lm_start_addr[tl]);
      if(thread_state==0){
        continue;
      }else{
        op6=lm_start_addr[tl]*4+LMBANK_SIZE*lane_num;
        local_tri=getresult(lane_num,lm_start_addr[tl]+1);
        tricount=tricount+local_tri; // Result is stored in lmbase + 4
        init_lane(lane_num, lm_start_addr[tl], 0); // triangle count all threads
        init_lane(lane_num, lm_start_addr[tl]+1, 0); // triangle count all threads
        launch_upstream_vertex(op[launch_idx][0],op[launch_idx][1], \
                             op[launch_idx][2],op[launch_idx][3], \
                             op[launch_idx][4],op[launch_idx][5], \
                             op6, num_operands, 0, cont, lane_num);
        launch_idx++;//=(launch_idx+1)%num_ready;
      }
    } 
  }
  // clean up
  for(int i=0;i<num_lanes;i++){
    for(int j=0; j<num_launch_threads;j++){
      while(!check_lane(i, lm_start_addr[j])); // Spin loop to check status of upstream
      local_tri=getresult(i,lm_start_addr[j]+1);
      tricount=tricount+local_tri; // Result is stored in lmbase + 4
    }
  }
  printf("Num of Probes:%ld\n", numprobes);
  printf("Numthreads:%ld\n", numthreads);
  printf("NumEdges:%ld\n", numedges);
  return tricount;
}

void sort_narray(uint32_t *narray, uint32_t arr_sz){
  for(int i=0; i<arr_sz; i++){
    for(int j=i; j<arr_sz;j++){
      if(narray[i]>narray[j]){
        uint32_t temp=narray[i];
        narray[i]=narray[j];
        narray[j]=temp;
      }
    }
  }
}

int main(int argc, char* argv[]) {
  /*
  * Options for Triangle Counting 
  */

  //TStr filename;
  char* filename;
  uint32_t part_nodes=0;
  uint32_t snode=0;
  uint32_t enode=0;
  int mode=0;
  int num_lanes=1;
  int num_launch_threads=1;
  //uint64_t memsize = 8589934592; // 8GB
  uint64_t memsize = 17179869184; // 8GB

  if(argc < 5){
        printf("Insufficient Input Params\n");
        printf("%s\n", USAGE);
        exit(1);
  }
  filename = argv[1];
  num_lanes = atoi(argv[2]);
  num_launch_threads = atoi(argv[3]);
  mode = atoi(argv[4]);
  if(mode == 0){
    printf("Running the entire graph!\n");
    snode=0;
    part_nodes=0;
  }else{
    printf("Running in batches\n");
    snode = atoi(argv[5]);
    if(argv[5])
      part_nodes = atoi(argv[6]);
  } 
  printf("Num Threads per Lane:%d\n", num_launch_threads);
  enode=snode+part_nodes-1;
  #ifdef DEBUG
    printf("Start the graph building\n");
    printf("Num Lancs:%d\n", num_lanes);
    printf("MemSize:%d\n", memsize);
  #endif

  calc_addrmap(num_lanes, memsize);

  FILE* in_file = fopen(filename, "rb");
  if (!in_file) {
        exit(EXIT_FAILURE);
  }
  int num_nodes, num_edges=0;
  fseek(in_file, 0, SEEK_SET);
  fread(&num_nodes, sizeof(num_nodes),1, in_file);
  printf("Graph of Size :%d\n", num_nodes);
  if(part_nodes==0) 
    enode=snode+num_nodes-1;
  else
    enode=snode+part_nodes-1;
  if(enode>num_nodes){
    enode=num_nodes-1;
  }
  printf("StartNode:%d, EndNode:%d\n", snode, enode);

  struct vertex *g_v_bin = (struct vertex *)(MAPBASE);
  uint64_t GRAPH_END = MAPBASE+ sizeof(struct vertex)*num_nodes;
  uint32_t *nlist_beg = (uint32_t *)(GRAPH_END);
  printf("GRAPH_START:%lx, NLIST_BEGIN:%lx\n", g_v_bin, nlist_beg);
  int i =0;
  printf("Build the graph now\n");
  int curr_base = 0;
  for(int i=0; i<num_nodes; i++){
    int deg;
    fread(&deg, sizeof(deg),1, in_file);
    num_edges+=deg;
    //printf("Node:%d Deg:%d", i, deg);
    int srcid;
    fread(&srcid, sizeof(srcid),1, in_file);
    (*(g_v_bin+srcid)).deg=deg;
    (*(g_v_bin+srcid)).id=srcid;
    //printf("Node:%d ID:%d", i, srcid);
    (*(g_v_bin+srcid)).neigh = nlist_beg+curr_base;
    uint32_t *narray = new uint32_t[deg];
    int j;
    for(j=0; j<deg; j++){
      int dstid;
      fread(&dstid, sizeof(dstid),1, in_file);
      narray[j]= dstid;
    }
    sort_narray(narray, deg); 
    for(j=0;j<deg;j++){
      #ifdef DEBUG_DETAIL
      if(i<=enode && i >=snode)
        printf("node id %d edge:%d ID:%d\n", srcid, j, narray[j]);
      #endif
      //g_v[nodemap[NI.GetId()]].neigh[j]= nodemap[NI.GetOutNId(j)];
      *(nlist_beg+curr_base+j)= narray[j];
      //g_v_bin[srcid].neigh[j]= narray[j];
    }
    delete narray;
    curr_base+=j;
 
    #ifdef DEBUG_DETAIL
      g_v_bin[srcid].print_v();
    #endif
    //for(int j=0; j<deg;j++){
    //  int dstid;
    //  fread(&dstid, sizeof(dstid),1, in_file);
    //  G->AddEdge(srcid, dstid);
    //}
  }
  printf("Graph Built. Will do Triangle Counting now\n");
  printf("Graph: NumEdges:%d\n", num_edges);
  printf("Graph: NumVertices:%d\n", num_nodes);
  // m5_switch_cpu();
  // m5_dump_reset_stats(0,0);
  //long tricount_num = tricount_upstream(g_v_bin, num_nodes, num_lanes);
  //long tricount_num = tricount_upstream_adjlist(g_v_bin, snode, enode, num_lanes, num_launch_threads);
  long tricount_num=0;
  int cont=0;
  //if(num_lanes == 1)
  //  tricount_num = tricount_upstream_single(g_v_bin, snode, enode, num_launch_threads, cont);
  //else
  tricount_num = tricount_upstream_multi(g_v_bin, snode, enode, num_launch_threads, cont, num_lanes);
  //long tricount_upstream_single(struct vertex *g_v, uint32_t snode, uint32_t enode, int num_launch_threads){
  // m5_dump_reset_stats(0,0);
  printf("Triangle Count=%d\n", tricount_num);
  // this code is independent of what particular graph implementation/type we use
  
}



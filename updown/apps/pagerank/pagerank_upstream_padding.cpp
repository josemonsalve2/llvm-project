#include "simupdown.h"
#include "Snap.h"

#include <cstdio>
#include <cstdlib>
#include <iostream>
#include <chrono>
#include <vector>

#define USAGE "USAGE: ./pagerank <edge_list_file> <numlanes> <numthreadsperlane> "

struct Vertex{
  uint32_t deg;
  uint32_t ival;
  uint32_t* neigh;
  uint32_t nval;
  uint32_t id;
  uint64_t padding;
};


void init_scratchpad(UpDown::SimUDRuntime_t *rt,Vertex *g_v, int num_lanes, int num_nodes, int num_edges){

  // init scratchpad, event sent to lane 0
  UpDown::word_t ops_data[4];
  UpDown::operands_t ops(4, ops_data);

  // Operands 0,1 : address of vertices list g_v
  // Operand 2    : number of workers
  // Operand 3    : number of vertices/nodes

  // Alternative way to pass the g_v
  // ops.set_operand(0, ((uint64_t)g_v) & 0xffffffff);
  // ops.set_operand(1, (((uint64_t)g_v) >> 32) & 0xffffffff);

  ops.set_operands(0,2, &g_v);         // nodel addr[0]
  ops.set_operand(2, num_lanes);      // number of workers
  ops.set_operand(3, num_nodes);      // graph size
  

  UpDown::event_t event_ops(0 /*Event Label*/,
                            0 /*UD ID*/,
                            0 /* Lane ID*/,
                            UpDown::CREATE_THREAD /*Thread ID*/,
                            &ops /*Operands*/);

              
  rt->send_event(event_ops);
  rt->start_exec(0, 0);
 
  printf("Waiting scratchpad initialization...\n");

  rt->test_wait_addr(0, 0, 4 << 2, 1); // UD=0, Lane_ID=0, Offset=4, expected=1 
  uint32_t val = 0;
  rt->ud2t_memcpy(&val, sizeof(uint32_t), 0, 0, 4 << 2)  ;             
  printf("Scratchpad initialized, flag=%d.\n", val);
}

void pagerank_upstream(UpDown:: SimUDRuntime_t *rt, Vertex *g_v, int num_lanes, int num_nodes, int num_edges){
  int num_workers = num_nodes < num_lanes ? num_nodes : num_lanes;
  
  for(int w=0; w < num_workers; w++){
    UpDown::word_t ops_data[4];
    UpDown::operands_t ops(4, ops_data);
    
    // Operands 0,1 : address of vertices list g_v
    // Operand 2    : number of workers
    // Operand 3    : number of vertices/nodes

    // Alternative way to pass the g_v
    // ops.set_operand(0, ((uint64_t)g_v) & 0xffffffff);
    // ops.set_operand(1, (((uint64_t)g_v) >> 32) & 0xffffffff);

    ops.set_operands(0, 2, &g_v);
    ops.set_operand(2, num_workers);
    ops.set_operand(3, num_nodes);
    

    UpDown::event_t event_ops(6 /*Event Label*/,
                              0 /*UD ID*/,
                              w /*Lane ID*/,
                              UpDown::CREATE_THREAD /*Thread ID*/,
                              &ops /*Operands*/);
    rt->send_event(event_ops);
    
    rt->start_exec(0 /*UD ID*/, w /*Lane ID*/);

    printf("Worker %d starts exec.\n", w);
  }

  // from pagerank_upstream_padding
  int term_count, num_edges_issued = 0; 
  int cnter = 0;
 
  do{
    term_count = 0;
    num_edges_issued = 0;
    for(int w = 0; w < num_workers; w++){

      // TODO: future version will remove this test_addr, ud2t_memcpy will execute that lane.
      rt->test_addr(0, 0, (8+w)<<2, 123);
      rt->test_addr(0, 0, (72+w)<<2, 321);
      uint32_t val1, val2;
      rt->ud2t_memcpy(&val1,
                      sizeof(uint32_t) /*fetch size*/,
                      0 /*UD ID*/,
                      0 /*Lane ID*/,
                      (8 + w) << 2 /*Offset*/);           
      rt->ud2t_memcpy(&val2,
                      sizeof(uint32_t),
                      0,
                      0,
                      (72 + w) << 2 /*Offset*/);
      
      num_edges_issued += val1;
      term_count += val2;  
    }
    cnter++;
    printf("cnter=%d, term_count=%d, num_edges=%d, num_edges_issued=%d\n",cnter, term_count, num_edges, num_edges_issued);
  }while(term_count < num_edges);
  
}

int main(int argc, char* argv[]) {
  // Set up machine parameters
  UpDown::ud_machine_t machine;
  machine.NumLanes = 64;

  // Default configurations runtime
  UpDown::SimUDRuntime_t *test_rt = new UpDown::SimUDRuntime_t(machine,
  "GenPagerankEFA", 
  "GeneratePagerankPaddingEFA", 
  "./", 
  UpDown::EmulatorLogLevel::NONE);

  printf("=== Base Addresses ===\n");
  test_rt->dumpBaseAddrs();
  printf("\n=== Machine Config ===\n");
  test_rt->dumpMachineConfig();


  char* filename;
  uint32_t num_iterations = 1;
  if(argc < 4){
        printf("Insufficient Input Params\n");
        printf("%s\n", USAGE);
        exit(1);
  }
  filename = argv[1];
  int num_lanes = atoi(argv[2]);
  int num_workers = atoi(argv[3]);

  if(argv[4])
    num_iterations = atoi(argv[4]);
  printf("Num Lanes:%d\n", num_lanes);
  printf("Num Iterations:%d\n", num_iterations);
  FILE* in_file = fopen(filename, "rb");
  if (!in_file) {
        printf("Error when openning file, exiting.\n");
        exit(EXIT_FAILURE);
  }
  int num_nodes, num_edges=0;
  fseek(in_file, 0, SEEK_SET);
  fread(&num_nodes, sizeof(num_nodes),1, in_file);
  printf("Graph of Size :%d\n", num_nodes);

  printf("Allocating memmory for Vertices...\n");

  // Allocate the array where the top and updown can see it:
  Vertex *g_v_bin = reinterpret_cast<Vertex *>(test_rt->mm_malloc(num_nodes * sizeof(Vertex)));

  printf("Vertices allocation done, allocating neighbour list...\n");

  // redundent mapping for srcid, so we use it for the second loop when figuring out the neigbours
  // note this is different from the static allocation version for GEM5
  // FIXME: may affect performance; temp mem used, mem consumption roughly doubles for top; can release it if needed.
  // if we want to reduce mem consumption, read the file twice can solve.
  uint32_t* srcid_list = reinterpret_cast<uint32_t*>(malloc(num_nodes * sizeof(uint32_t)));

  // since we don't know the number of edges, we leverage vector so it can dynamically grow
  // FIXME: may affect performance; temp mem used; dynamic list (vector) used;
  std::vector<uint32_t> dstid_list;

  // calculate size of neighbour list and assign values to each member value
  printf("Build the graph now\n");

  for(int i = 0; i < num_nodes; i++) {
    int deg, srcid;
    fread(&deg, sizeof(deg),1, in_file);
    fread(&srcid, sizeof(srcid),1, in_file);
    (*(g_v_bin+srcid)).deg   = deg;
    (*(g_v_bin+srcid)).id    = srcid;
    (*(g_v_bin+srcid)).ival  = 1 << 20;
    (*(g_v_bin+srcid)).nval  = 0;
    (*(g_v_bin+srcid)).padding = 0;
    for(int j=0; j<deg; j++){
      int dstid;
      fread(&dstid, sizeof(dstid),1, in_file);
      dstid_list.push_back(dstid);
    }
    // save this so in next iteration we make sure in each i we use the correct srcid.
    srcid_list[i] = srcid;

    num_edges+= deg;
  }

  printf("Vertices build done.\n");

  // Allocate an updown&top-aware neighgbour list
  uint32_t *nlist = reinterpret_cast<uint32_t *>(test_rt->mm_malloc(num_edges * sizeof(uint32_t)));
  printf("Build neigh list...\n");
  int curr_base = 0;
  for(int i = 0; i < num_nodes; i++){
    int srcid = srcid_list[i];
    int deg = (*(g_v_bin+srcid)).deg;

    (*(g_v_bin+srcid)).neigh = nlist + curr_base;

    for(int j = 0; j < deg; j++){
      *(nlist+curr_base+j)= dstid_list[curr_base + j];
    }
    curr_base += deg;
  }
  printf("Graph Built. Will do Page Rank now\n");
  printf("Graph: NumEdges:%d\n", num_edges);
  printf("Graph: NumVertices:%d\n", num_nodes);

 
  printf("Initialize scratchpad...\n");
  // init scratchpad
  init_scratchpad(test_rt, g_v_bin, num_workers, num_nodes, num_edges);

  printf("Scratchpad initialized.\n");
  // Dumps a set of statistics per iteration of Page Rank

  printf("Run pagerank_upstream.\n");
  for(int i=0; i < num_iterations; i++){
    pagerank_upstream(test_rt, g_v_bin, num_workers, num_nodes, num_edges);
  }

  printf("Pagerank done.\n");

}

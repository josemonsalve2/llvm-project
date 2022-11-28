from EFA import *
import math

def GeneratePagerank1UDEFA():
    GeneratePagerankMultiUDEFA(1)

def GeneratePagerank2UDEFA():
    GeneratePagerankMultiUDEFA(2)

def GeneratePagerank4UDEFA():
    GeneratePagerankMultiUDEFA(4)

def GeneratePagerankMultiUDEFA(NUM_NODES=1):
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    event_map = {
        'init_lm':      0,
        'readNode':     1,
        'readEdge':     2,
        'update':       3,
        'rd_return':    4,
        'store_ack':    5,
        'init_worker':  6
    }

    INIT_FLAG_OFFSET        = 4 << 2
    ISSUE_COUNTER_OFFSET    = 8 << 2
    TERM_COUNTER_OFFSET     = 72 << 2 
    INVALID_VAL             = 0xffffffff
    BATCH_SIZE              = 16
    INACTIVE_MASK           = 1 << 31
    CACHE_SIZE              = (4096 * 16) // NUM_NODES
    CACHE_OFFSET            = 4096 << 2
    CACHE_ENTRY_SIZE        = 8
    HASH_MASK               = (CACHE_SIZE - 1) << 3

    
    '''
    Initialize the scratchpad memory (metadata, hashmap)
    Operands:
        OB_0_1  vertex array (graph) base address in DRAM
        OB_2    number of workers 
        OB_3    number of vertices of the input graph
    '''
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['init_lm'])
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                # EAR_0  <- pointer to the base of vertex arrary in DRAM
    tran0.writeAction("mov_ob2reg OB_3 UDPR_1")                 # UDPR_1 <- num_vertex 
    tran0.writeAction("mov_imm2reg UDPR_2 0")                   
    tran0.writeAction("mov_ear2lm EAR_0 UDPR_2 8")              # Store a copy of the base pointer to LM

    # Initialize the lane private counters: number of pagerank value updates being issued and processed respectively
    tran0.writeAction(f"mov_imm2reg UDPR_2 {TERM_COUNTER_OFFSET}")      # termination counter addr in LM
    tran0.writeAction(f"addi UDPR_2 UDPR_4 {64 << 3}")
    tran0.writeAction("mov_imm2reg UDPR_3 0")
    tran0.writeAction("ctr_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran0.writeAction("addi UDPR_2 UDPR_2 4")
    tran0.writeAction("blt UDPR_2 UDPR_4 ctr_loop")

    # Initialize the write through cache in the scratchpad
    # The lane-private cache starts at address (lane bank base + offset HASHMAP_OFFSET)
    tran0.writeAction(f"mov_imm2reg UDPR_2 {CACHE_OFFSET}")
    tran0.writeAction(f"mov_imm2reg UDPR_3 {INVALID_VAL}")
    tran0.writeAction(f"addi UDPR_2 UDPR_4 {CACHE_SIZE << 3}")  # UDPR_4 <- end address of the cache 
    tran0.writeAction("init_cache_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran0.writeAction(f"addi UDPR_2 UDPR_2 {CACHE_ENTRY_SIZE}")
    tran0.writeAction("blt UDPR_2 UDPR_4 init_cache_loop")

    # Initialize the lane private counter for the number of edges already fetched from DRAM (or equivalently the number of updates issued)
    tran0.writeAction(f"mov_imm2reg UDPR_2 {INIT_FLAG_OFFSET}") # UDPR_2 <- number of fetched vertex 
    tran0.writeAction("mov_imm2reg UDPR_3 1")
    tran0.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    tran0.writeAction("yield_terminate 4 16")



    '''
    Initialize the scratchpad memory (metadata, hashmap)
    Operands:
        OB_0_1  vertex array (graph) base address in DRAM
        OB_2    number of workers 
        OB_3    number of vertices of the input graph
    '''
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init_worker'])
    tran1.writeAction("mov_ob2ear OB_0_1 EAR_0")                # EAR_0  <- pointer to the base of vertex arrary in DRAM
    tran1.writeAction("subi OB_2 UDPR_0 1")                     # UDPR_0 <- num of workers - 1
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # UDPR_1 <- num_vertex 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # UDPR_11 <- base event word

    tran1.writeAction("addi LID UDPR_2 0")                      # UDPR_2 <- number of fetched vertex 
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13")                # UPDR_13 <- vertex array fetch stride == number of workers

    tran1.writeAction("tranCarry_goto block_1")                 # inline the code for fetching vertex from DRAM (inline code from block 1)

    '''
    Process the source vertex and fetch #BATCH_SIZE(16) edges from the edge list in DRAM
    Operands:
        OB_0    degree / number of neighbors
        OB_1    old pagerank value
        OB_2_3  edge list base address in the DRAM
    '''
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 next_node")                   # zero degree vertex, skip
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1  <- edge array base address in DRAM
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- weight per outgoing edge

    # Fetch edges from the edge list in DRAM (in batches)
    tran2.writeAction(f"send_dmlm_ld_wret UDPR_8 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran2.writeAction(f"lshift_add_imm LID UDPR_14 2 {ISSUE_COUNTER_OFFSET}")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 UDPR_5 UDPR_15")             # add v's degree to the number of edges fetched 
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran2.writeAction("yield 4")

    tran2.writeAction("next_node: tranCarry_goto block_1")      # skip this vertex if degree==0 (inline code from block 1)

    '''
    Send update to the destination vertex for each edge and fetch the next 16 edges from DRAM
    Operands:
        OB_[0-{BATCH_SIZE-1}]   destination vertex id for an edge 
    '''
    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction(f"ev_update_2 UDPR_11 {event_map['update']} 255 5")   # UDPR_11 <- event word for the event to be sent
    tran3.writeAction(f"addi UDPR_8 UDPR_10 {BATCH_SIZE}")
    tran3.writeAction("bge UDPR_10 UDPR_5 fetch0")                          # prefetch next batch of edges if there exists
    tran3.writeAction(f"lshift_and_imm UDPR_10 UDPR_10 2 {0xffffffff}")
    tran3.writeAction(f"send_dmlm_ld_wret UDPR_10 {event_map['readEdge']} {BATCH_SIZE<<2} 1")   # fetch the next batch of edges from DRAM
    for k in range(BATCH_SIZE):
        tran3.writeAction(f"fetch{k}: lshift_and_imm OB_{k} UDPR_3 6 {3<<6}")       # UPDR_3 <- the updown id to which the update is going to send 
        tran3.writeAction(f"rshift_and_imm OB_{k} UDPR_4 2 63")             # UDPR_4 <- lane id to which the update is going to send
        tran3.writeAction("add UDPR_3 UDPR_4 UDPR_3")                       # UDPR_3 <- updown id + lane id = destination
        tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
        tran3.writeAction(f"send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_{k} UDPR_7")
        tran3.writeAction("addi UDPR_8 UDPR_8 1")
        tran3.writeAction("bge UDPR_8 UDPR_5 next_vertex")                  # skip the rest of the loop if finish fetching all the edges in the neighbor list
    tran3.writeAction(f"yield {BATCH_SIZE}")    

    # finish read all edges
    tran3.writeAction("next_vertex: tranCarry_goto block_1")                # finish process this vertex, and go fetching the next (inline code from block 1)

    
    '''Read next vertex from the vertex list in DRAM (strided read based on the number of worders'''
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 fin_fetch")         # terminates if read all assigned vertices
    efa.appendBlockAction("block_1", f"lshift_and_imm UDPR_2 UDPR_3 3 {0xffffffff}") 
    efa.appendBlockAction("block_1", f"lshift_and_imm UDPR_2 UDPR_4 4 {0xffffffff}") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4")            # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", f"send_dmlm_ld_wret UDPR_4 {event_map['readNode']} 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2")           # stride = number of workers
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "fin_fetch: yield_terminate 4 16")


    '''
    Receive a value passed from an in-edge, check if the vertex is cached in the scratchpad and update accordingly. Cases are
        1) active_hit   - Requested vertex is cached due to a previous update request to the same vertex -> merge the incoming value with cached value. 
                          No need to write back because it's still waiting for the vertex value read from DRAM coming back to perform an accumulated update.
        2) hit          - Both the requested vertex and its up-to-date value (in DRAM) is cached, update the cached value and write back the data. 
                          (because the policy is write through)
        3) evict        - Requested vertex is not cached. Since the current cached vertex value has been updated and written back to DRAM, it can be evicted. 
                          Evict the old entry and insert the incoming vertex and value to the cache. Then send an DRAM read to load the vertex value from DRAM.
        4) collision    - Requested vertex is not cached and the current cached vertex update is not finished yet. Delay this update by pushing it back to the 
                          end of event queue.
    Operands:
        OB_0    id of the vertex to be updated
        OB_1    value passed from the in-edge 
    '''
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    tran4.writeAction(f"mov_imm2reg UDPR_0 {CACHE_OFFSET}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_3 1 {HASH_MASK}")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- hashmap entry addr
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")                 # UDPR_4 <- current key in the hashmap entry
    tran4.writeAction("beq UDPR_4 OB_0 active_hit")                 # hit the cache and there's an ongoing load to that vertex value
    tran4.writeAction(f"bitwise_and_imm UDPR_4 UDPR_5 {INACTIVE_MASK-1}")
    tran4.writeAction("beq UDPR_5 OB_0 hit")                        # hit the cache and the up-to-date DRAM value is also cached
    tran4.writeAction("rshift_and_imm UDPR_4 UDPR_5 31 1")
    tran4.writeAction(f"beq UDPR_5 1 evict")                        # current cache entry has been written back and can be evicted 

    # collision on the cache entry, push the update event to the end of the lane's event queue 
    tran4.writeAction(f"ev_update_2 UDPR_12 {event_map['update']} 255 5") 
    tran4.writeAction("rshift_and_imm EQT UDPR_5 24 255")
    tran4.writeAction("send4_wcont UDPR_12 UDPR_5 UDPR_12 OB_0 OB_1")
    tran4.writeAction("userctr 0 2 1")                              # num of cache collision ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("hit: addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_7 4")
    tran4.writeAction("fp_add UDPR_7 OB_1 UDPR_7")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_3 4")
    # store the udpated value back the DRAM because the cache policy is write through
    tran4.writeAction("mov_imm2reg UDPR_0 0")
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0  <- pointer to the vertax array base in DRAM
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5") 
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_4 3 {0xffffffff}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_6 4 {0xffffffff}")
    tran4.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran4.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_7 0")
    tran4.writeAction("userctr 0 1 1")                              # num of cache hit ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("active_hit: addi UDPR_3 UDPR_3 4")           # hit and combine the incoming value with previous updates
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")
    tran4.writeAction(f"lshift_add_imm LID UDPR_0 2 {TERM_COUNTER_OFFSET}")    # update merged, termination counter ++
    tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran4.writeAction("addi UDPR_7 UDPR_7 1")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran4.writeAction("userctr 0 3 1")                              # num of cache active hit ++
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("evict: mov_reg2lm OB_0 UDPR_3 4")            # evict the cached vertex value and insert incoming one to the cache
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")
    tran4.writeAction("mov_imm2reg UDPR_0 0")
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0 <- pointer to the vertax array base in DRAM
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_4 3 {0xffffffff}")     # fetch the old pagerank value from DRAM
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_5 4 {0xffffffff}")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['rd_return']} 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        
    tran4.writeAction("userctr 0 4 1")                              # num of cache insertion ++
    tran4.writeAction("yield_terminate 2 16") 

    '''
    Receive the pagerank value read from the DRAM, apply the (accumulated) updates and store it back to the DRAM
    Operands:
        OB_0    pagerank value to be updated
        OB_1    vertex id
    '''
    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    tran5.writeAction("mov_imm2reg UDPR_0 0")
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0  <- pointer to the vertax array base in DRAM
    tran5.writeAction(f"mov_imm2reg UDPR_0 {CACHE_OFFSET}")
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_3 1 {HASH_MASK}")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- cache entry addr
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")    
    tran5.writeAction(f"bitwise_or_imm UDPR_6 UDPR_6 {INACTIVE_MASK}")  
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")                 # flip the highest bit indicating the value is written back
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")                 
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")                  # apply the cumulated updates
    tran5.writeAction("mov_reg2lm UDPR_2 UDPR_3 4")                 # update the cache entry 

    # store the udpated value back the DRAM (write through cache)
    tran5.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5") 
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_4 3 {0xffffffff}")
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_6 4 {0xffffffff}")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    tran5.writeAction("yield_terminate 2 16")

    '''
    Acknowledge the store of the new pagerank value and update the termination counter accordingly
    Operands:
    '''
    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction(f"lshift_add_imm LID UDPR_0 2 {TERM_COUNTER_OFFSET}")    # new pagerank value is written back, termination counter ++
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("yield_terminate 0 16")

    return efa

def GeneratePagerankPaddingEFA():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    event_map = {
        'init_lm':      0,
        'readNode':     1,
        'readEdge':     2,
        'update':       3,
        'rd_return':    4,
        'store_ack':    5,
        'init_worker':  6
    }

    INIT_FLAG_OFFSET        = 4 << 2
    ISSUE_COUNTER_OFFSET    = 8 << 2
    TERM_COUNTER_OFFSET     = 72 << 2 
    INVALID_VAL             = 0xffffffff
    BATCH_SIZE              = 16
    INACTIVE_MASK           = 1 << 31
    CACHE_SIZE              = 4096 * 32
    CACHE_OFFSET            = 4096 << 2
    CACHE_ENTRY_SIZE        = 8
    HASH_MASK               = (CACHE_SIZE - 1) << 3

    
    '''
    Initialize the scratchpad memory (metadata, hashmap)
    Operands:
        OB_0_1  vertex array (graph) base address in DRAM
        OB_2    number of workers 
        OB_3    number of vertices of the input graph
    '''
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['init_lm'])
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                # EAR_0  <- pointer to the base of vertex arrary in DRAM
    tran0.writeAction("mov_ob2reg OB_3 UDPR_1")                 # UDPR_1 <- num_vertex 
    tran0.writeAction("mov_imm2reg UDPR_2 0")                   
    tran0.writeAction("mov_ear2lm EAR_0 UDPR_2 8")              # Store a copy of the base pointer to LM

    # Initialize the lane private counters: number of pagerank value updates being issued and processed respectively
    tran0.writeAction(f"mov_imm2reg UDPR_2 {TERM_COUNTER_OFFSET}")      # termination counter addr in LM
    tran0.writeAction(f"addi UDPR_2 UDPR_4 {64 << 3}")
    tran0.writeAction("mov_imm2reg UDPR_3 0")
    tran0.writeAction("ctr_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran0.writeAction("addi UDPR_2 UDPR_2 4")
    tran0.writeAction("blt UDPR_2 UDPR_4 ctr_loop")

    # Initialize the write through cache in the scratchpad
    # The lane-private cache starts at address (lane bank base + offset HASHMAP_OFFSET)
    tran0.writeAction(f"mov_imm2reg UDPR_2 {CACHE_OFFSET}")
    tran0.writeAction(f"mov_imm2reg UDPR_3 {INVALID_VAL}")
    tran0.writeAction(f"addi UDPR_2 UDPR_4 {CACHE_SIZE << 3}")  # UDPR_4 <- end address of the cache 
    tran0.writeAction("init_cache_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran0.writeAction(f"addi UDPR_2 UDPR_2 {CACHE_ENTRY_SIZE}")
    tran0.writeAction("blt UDPR_2 UDPR_4 init_cache_loop")

    # Initialize the lane private counter for the number of edges already fetched from DRAM (or equivalently the number of updates issued)
    tran0.writeAction(f"mov_imm2reg UDPR_2 {INIT_FLAG_OFFSET}")                      # UDPR_2 <- number of fetched vertex 
    tran0.writeAction("mov_imm2reg UDPR_3 1")
    tran0.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    tran0.writeAction("yield_terminate 4 16")



    '''
    Initialize the scratchpad memory (metadata, hashmap)
    Operands:
        OB_0_1  vertex array (graph) base address in DRAM
        OB_2    number of workers 
        OB_3    number of vertices of the input graph
    '''
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init_worker'])
    tran1.writeAction("mov_ob2ear OB_0_1 EAR_0")                # EAR_0  <- pointer to the base of vertex arrary in DRAM
    tran1.writeAction("subi OB_2 UDPR_0 1")                     # UDPR_0 <- num of workers - 1
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # UDPR_1 <- num_vertex 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # UDPR_11 <- base event word

    tran1.writeAction("addi LID UDPR_2 0")                      # UDPR_2 <- number of fetched vertex 
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13")                # UPDR_13 <- vertex array fetch stride == number of workers

    tran1.writeAction("tranCarry_goto block_1")                 # inline the code for fetching vertex from DRAM (inline code from block 1)

    '''
    Process the source vertex and fetch #BATCH_SIZE(16) edges from the edge list in DRAM
    Operands:
        OB_0    degree / number of neighbors
        OB_1    old pagerank value
        OB_2_3  edge list base address in the DRAM
    '''
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 next_node")                   # zero degree vertex, skip
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1  <- edge array base address in DRAM
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- weight per outgoing edge

    # Fetch edges from the edge list in DRAM (in batches)
    tran2.writeAction(f"send_dmlm_ld_wret UDPR_8 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran2.writeAction(f"lshift_add_imm LID UDPR_14 2 {ISSUE_COUNTER_OFFSET}")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 UDPR_5 UDPR_15")             # add v's degree to the number of edges fetched 
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran2.writeAction("yield 4")

    tran2.writeAction("next_node: tranCarry_goto block_1")      # skip this vertex if degree==0 (inline code from block 1)

    '''
    Send update to the destination vertex for each edge and fetch the next 16 edges from DRAM
    Operands:
        OB_[0-{BATCH_SIZE-1}]   destination vertex id for an edge 
    '''
    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction(f"ev_update_2 UDPR_11 {event_map['update']} 255 5")   # UDPR_11 <- event word for the event to be sent
    tran3.writeAction(f"addi UDPR_8 UDPR_10 {BATCH_SIZE}")
    tran3.writeAction("bge UDPR_10 UDPR_5 fetch0")                          # prefetch next batch of edges if there exists
    tran3.writeAction(f"lshift_and_imm UDPR_10 UDPR_10 2 {0xffffffff}")
    tran3.writeAction(f"send_dmlm_ld_wret UDPR_10 {event_map['readEdge']} {BATCH_SIZE<<2} 1")   # fetch the next batch of edges from DRAM
    for k in range(BATCH_SIZE):
        tran3.writeAction(f"fetch{k}: bitwise_and OB_{k} UDPR_0 UDPR_3")    # UPDR_3 <- the lane id to which the update is going to send 
        tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
        tran3.writeAction(f"send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_{k} UDPR_7")
        tran3.writeAction("addi UDPR_8 UDPR_8 1")
        tran3.writeAction("bge UDPR_8 UDPR_5 next_vertex")                  # skip the rest of the loop if finish fetching all the edges in the neighbor list
    tran3.writeAction(f"yield {BATCH_SIZE}")    

    # finish read all edges
    tran3.writeAction("next_vertex: tranCarry_goto block_1")                # finish process this vertex, and go fetching the next (inline code from block 1)

    
    '''Read next vertex from the vertex list in DRAM (strided read based on the number of worders'''
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 fin_fetch")         # terminates if read all assigned vertices   
    efa.appendBlockAction("block_1", f"lshift_and_imm UDPR_2 UDPR_4 5 {0xffffffff}")  # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", f"send_dmlm_ld_wret UDPR_4 {event_map['readNode']} 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2")           # stride = number of workers
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "fin_fetch: yield_terminate 4 16")


    '''
    Receive a value passed from an in-edge, check if the vertex is cached in the scratchpad and update accordingly. Cases are
        1) active_hit   - Requested vertex is cached due to a previous update request to the same vertex -> merge the incoming value with cached value. 
                          No need to write back because it's still waiting for the vertex value read from DRAM coming back to perform an accumulated update.
        2) hit          - Both the requested vertex and its up-to-date value (in DRAM) is cached, update the cached value and write back the data. 
                          (because the policy is write through)
        3) evict        - Requested vertex is not cached. Since the current cached vertex value has been updated and written back to DRAM, it can be evicted. 
                          Evict the old entry and insert the incoming vertex and value to the cache. Then send an DRAM read to load the vertex value from DRAM.
        4) collision    - Requested vertex is not cached and the current cached vertex update is not finished yet. Delay this update by pushing it back to the 
                          end of event queue.
    Operands:
        OB_0    id of the vertex to be updated
        OB_1    value passed from the in-edge 
    '''
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    tran4.writeAction(f"mov_imm2reg UDPR_0 {CACHE_OFFSET}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_3 3 {HASH_MASK}")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- hashmap entry addr
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")                 # UDPR_4 <- current key in the hashmap entry
    tran4.writeAction("beq UDPR_4 OB_0 active_hit")                 # hit the cache and there's an ongoing load to that vertex value
    tran4.writeAction(f"bitwise_and_imm UDPR_4 UDPR_5 {INACTIVE_MASK-1}")
    tran4.writeAction("beq UDPR_5 OB_0 hit")                        # hit the cache and the up-to-date DRAM value is also cached
    tran4.writeAction("rshift_and_imm UDPR_4 UDPR_5 31 1")
    tran4.writeAction(f"beq UDPR_5 1 evict")                        # current cache entry has been written back and can be evicted 

    # collision on the cache entry, push the update event to the end of the lane's event queue 
    tran4.writeAction(f"ev_update_2 UDPR_12 {event_map['update']} 255 5") 
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    tran4.writeAction("userctr 0 2 1")                              # num of cache collision ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("hit: addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_7 4")
    tran4.writeAction("fp_add UDPR_7 OB_1 UDPR_7")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_3 4")
    # store the udpated value back the DRAM because the cache policy is write through
    tran4.writeAction("mov_imm2reg UDPR_0 0")
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0  <- pointer to the vertax array base in DRAM
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5") 
    tran4.writeAction("lshift_add_imm OB_0 UDPR_4 5 16")
    tran4.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_7 0")
    tran4.writeAction("userctr 0 1 1")                              # num of cache hit ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("active_hit: addi UDPR_3 UDPR_3 4")           # hit and combine the incoming value with previous updates
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")
    tran4.writeAction(f"lshift_add_imm LID UDPR_0 2 {TERM_COUNTER_OFFSET}")    # update merged, termination counter ++
    tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran4.writeAction("addi UDPR_7 UDPR_7 1")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran4.writeAction("userctr 0 3 1")                              # num of cache active hit ++
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("evict: mov_reg2lm OB_0 UDPR_3 4")            # evict the cached vertex value and insert incoming one to the cache
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")
    tran4.writeAction("mov_imm2reg UDPR_0 0")
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0 <- pointer to the vertax array base in DRAM
    tran4.writeAction("lshift_add_imm OB_0 UDPR_4 5 16")
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['rd_return']} 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        
    tran4.writeAction("userctr 0 4 1")                              # num of cache insertion ++
    tran4.writeAction("yield_terminate 2 16") 

    '''
    Receive the pagerank value read from the DRAM, apply the (accumulated) updates and store it back to the DRAM
    Operands:
        OB_0    pagerank value to be updated
        OB_1    vertex id
    '''
    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    tran5.writeAction("mov_imm2reg UDPR_0 0")
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0  <- pointer to the vertax array base in DRAM
    tran5.writeAction(f"mov_imm2reg UDPR_0 {CACHE_OFFSET}")
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_3 3 {HASH_MASK}")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- cache entry addr
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")    
    tran5.writeAction(f"bitwise_or_imm UDPR_6 UDPR_6 {INACTIVE_MASK}")  
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")                 # flip the highest bit indicating the value is written back
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")                 
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")                  # apply the cumulated updates
    tran5.writeAction("mov_reg2lm UDPR_2 UDPR_3 4")                 # update the cache entry 

    # store the udpated value back the DRAM (write through cache)
    tran5.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5") 
    tran5.writeAction("lshift_add_imm OB_1 UDPR_4 5 16")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    tran5.writeAction("yield_terminate 2 16")

    '''
    Acknowledge the store of the new pagerank value and update the termination counter accordingly
    Operands:
    '''
    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction(f"lshift_add_imm LID UDPR_0 2 {TERM_COUNTER_OFFSET}")    # UDPR_0 <- new pagerank value is written back, termination counter ++
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("yield_terminate 0 16")

    return efa


def GeneratePagerankUniCacheEFA():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    event_map = {
        'init_lm':      0,
        'readNode':     1,
        'readEdge':     2,
        'update':       3,
        'rd_return':    4,
        'store_ack':    5,
        'init_worker':  6
    }

    INIT_FLAG_OFFSET        = 4 << 2
    ISSUE_COUNTER_OFFSET    = 8 << 2
    TERM_COUNTER_OFFSET     = 72 << 2 
    INVALID_VAL             = 0xffffffff
    BATCH_SIZE              = 16
    INACTIVE_MASK           = 1 << 31
    CACHE_SIZE              = 4096 * 32
    CACHE_OFFSET            = 4096 << 2
    CACHE_ENTRY_SIZE        = 8
    HASH_MASK               = (CACHE_SIZE - 1) << 3

    
    '''
    Initialize the scratchpad memory (metadata, hashmap)
    Operands:
        OB_0_1  vertex array (graph) base address in DRAM
        OB_2    number of workers 
        OB_3    number of vertices of the input graph
    '''
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['init_lm'])
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                # EAR_0  <- pointer to the base of vertex arrary in DRAM
    tran0.writeAction("mov_ob2reg OB_3 UDPR_1")                 # UDPR_1 <- num_vertex 
    tran0.writeAction("mov_imm2reg UDPR_2 0")                   
    tran0.writeAction("mov_ear2lm EAR_0 UDPR_2 8")              # Store a copy of the base pointer to LM

    # Initialize the lane private counters: number of pagerank value updates being issued and processed respectively
    tran0.writeAction(f"mov_imm2reg UDPR_2 {TERM_COUNTER_OFFSET}")      # termination counter addr in LM
    tran0.writeAction(f"addi UDPR_2 UDPR_4 {64 << 3}")
    tran0.writeAction("mov_imm2reg UDPR_3 0")
    tran0.writeAction("ctr_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran0.writeAction("addi UDPR_2 UDPR_2 4")
    tran0.writeAction("blt UDPR_2 UDPR_4 ctr_loop")

    # Initialize the write through cache in the scratchpad
    # The lane-private cache starts at address (lane bank base + offset HASHMAP_OFFSET)
    tran0.writeAction(f"mov_imm2reg UDPR_2 {CACHE_OFFSET}")
    tran0.writeAction(f"mov_imm2reg UDPR_3 {INVALID_VAL}")
    tran0.writeAction(f"addi UDPR_2 UDPR_4 {CACHE_SIZE << 3}")  # UDPR_4 <- end address of the cache 
    tran0.writeAction("init_cache_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran0.writeAction(f"addi UDPR_2 UDPR_2 {CACHE_ENTRY_SIZE}")
    tran0.writeAction("blt UDPR_2 UDPR_4 init_cache_loop")

    # Initialize the lane private counter for the number of edges already fetched from DRAM (or equivalently the number of updates issued)
    tran0.writeAction(f"mov_imm2reg UDPR_2 {INIT_FLAG_OFFSET}")                      # UDPR_2 <- number of fetched vertex 
    tran0.writeAction("mov_imm2reg UDPR_3 1")
    tran0.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    tran0.writeAction("yield_terminate 4 16")



    '''
    Initialize the scratchpad memory (metadata, hashmap)
    Operands:
        OB_0_1  vertex array (graph) base address in DRAM
        OB_2    number of workers 
        OB_3    number of vertices of the input graph
    '''
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init_worker'])
    tran1.writeAction("mov_ob2ear OB_0_1 EAR_0")                # EAR_0  <- pointer to the base of vertex arrary in DRAM
    tran1.writeAction("subi OB_2 UDPR_0 1")                     # UDPR_0 <- num of workers - 1
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # UDPR_1 <- num_vertex 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # UDPR_11 <- base event word

    tran1.writeAction("addi LID UDPR_2 0")                      # UDPR_2 <- number of fetched vertex 
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13")                # UPDR_13 <- vertex array fetch stride == number of workers

    tran1.writeAction("tranCarry_goto block_1")                 # inline the code for fetching vertex from DRAM (inline code from block 1)

    '''
    Process the source vertex and fetch #BATCH_SIZE(16) edges from the edge list in DRAM
    Operands:
        OB_0    degree / number of neighbors
        OB_1    old pagerank value
        OB_2_3  edge list base address in the DRAM
    '''
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 next_node")                   # zero degree vertex, skip
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1  <- edge array base address in DRAM
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- weight per outgoing edge

    # Fetch edges from the edge list in DRAM (in batches)
    tran2.writeAction(f"send_dmlm_ld_wret UDPR_8 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran2.writeAction(f"lshift_add_imm LID UDPR_14 2 {ISSUE_COUNTER_OFFSET}")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 UDPR_5 UDPR_15")             # add v's degree to the number of edges fetched 
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran2.writeAction("yield 4")

    tran2.writeAction("next_node: tranCarry_goto block_1")      # skip this vertex if degree==0 (inline code from block 1)

    '''
    Send update to the destination vertex for each edge and fetch the next 16 edges from DRAM
    Operands:
        OB_[0-{BATCH_SIZE-1}]   destination vertex id for an edge 
    '''
    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction(f"ev_update_2 UDPR_11 {event_map['update']} 255 5")   # UDPR_11 <- event word for the event to be sent
    tran3.writeAction(f"addi UDPR_8 UDPR_10 {BATCH_SIZE}")
    tran3.writeAction("bge UDPR_10 UDPR_5 fetch0")                          # prefetch next batch of edges if there exists
    tran3.writeAction(f"lshift_and_imm UDPR_10 UDPR_10 2 {0xffffffff}")
    tran3.writeAction(f"send_dmlm_ld_wret UDPR_10 {event_map['readEdge']} {BATCH_SIZE<<2} 1")   # fetch the next batch of edges from DRAM
    for k in range(BATCH_SIZE):
        tran3.writeAction(f"fetch{k}: bitwise_and OB_{k} UDPR_0 UDPR_3")    # UPDR_3 <- the lane id to which the update is going to send 
        tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
        tran3.writeAction(f"send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_{k} UDPR_7")
        tran3.writeAction("addi UDPR_8 UDPR_8 1")
        tran3.writeAction("bge UDPR_8 UDPR_5 next_vertex")                  # skip the rest of the loop if finish fetching all the edges in the neighbor list
    tran3.writeAction(f"yield {BATCH_SIZE}")    

    # finish read all edges
    tran3.writeAction("next_vertex: tranCarry_goto block_1")                # finish process this vertex, and go fetching the next (inline code from block 1)

    
    '''Read next vertex from the vertex list in DRAM (strided read based on the number of worders'''
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 fin_fetch")         # terminates if read all assigned vertices
    efa.appendBlockAction("block_1", f"lshift_and_imm UDPR_2 UDPR_3 3 {0xffffffff}") 
    efa.appendBlockAction("block_1", f"lshift_and_imm UDPR_2 UDPR_4 4 {0xffffffff}") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4")            # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", f"send_dmlm_ld_wret UDPR_4 {event_map['readNode']} 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2")           # stride = number of workers
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "fin_fetch: yield_terminate 4 16")


    '''
    Receive a value passed from an in-edge, check if the vertex is cached in the scratchpad and update accordingly. Cases are
        1) active_hit   - Requested vertex is cached due to a previous update request to the same vertex -> merge the incoming value with cached value. 
                          No need to write back because it's still waiting for the vertex value read from DRAM coming back to perform an accumulated update.
        2) hit          - Both the requested vertex and its up-to-date value (in DRAM) is cached, update the cached value and write back the data. 
                          (because the policy is write through)
        3) evict        - Requested vertex is not cached. Since the current cached vertex value has been updated and written back to DRAM, it can be evicted. 
                          Evict the old entry and insert the incoming vertex and value to the cache. Then send an DRAM read to load the vertex value from DRAM.
        4) collision    - Requested vertex is not cached and the current cached vertex update is not finished yet. Delay this update by pushing it back to the 
                          end of event queue.
    Operands:
        OB_0    id of the vertex to be updated
        OB_1    value passed from the in-edge 
    '''
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    tran4.writeAction(f"mov_imm2reg UDPR_0 {CACHE_OFFSET}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_3 3 {HASH_MASK}")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- hashmap entry addr
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")                 # UDPR_4 <- current key in the hashmap entry
    tran4.writeAction("beq UDPR_4 OB_0 active_hit")                 # hit the cache and there's an ongoing load to that vertex value
    tran4.writeAction(f"bitwise_and_imm UDPR_4 UDPR_5 {INACTIVE_MASK-1}")
    tran4.writeAction("beq UDPR_5 OB_0 hit")                        # hit the cache and the up-to-date DRAM value is also cached
    tran4.writeAction("rshift_and_imm UDPR_4 UDPR_5 31 1")
    tran4.writeAction(f"beq UDPR_5 1 evict")                        # current cache entry has been written back and can be evicted 

    # collision on the cache entry, push the update event to the end of the lane's event queue 
    tran4.writeAction(f"ev_update_2 UDPR_12 {event_map['update']} 255 5") 
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    tran4.writeAction("userctr 0 2 1")                              # num of cache collision ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("hit: addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_7 4")
    tran4.writeAction("fp_add UDPR_7 OB_1 UDPR_7")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_3 4")
    # store the udpated value back the DRAM because the cache policy is write through
    tran4.writeAction("mov_imm2reg UDPR_0 0")
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0  <- pointer to the vertax array base in DRAM
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5") 
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_4 3 {0xffffffff}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_6 4 {0xffffffff}")
    tran4.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran4.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_7 0")
    tran4.writeAction("userctr 0 1 1")                              # num of cache hit ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("active_hit: addi UDPR_3 UDPR_3 4")           # hit and combine the incoming value with previous updates
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")
    tran4.writeAction(f"lshift_add_imm LID UDPR_0 2 {TERM_COUNTER_OFFSET}")    # update merged, termination counter ++
    tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran4.writeAction("addi UDPR_7 UDPR_7 1")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran4.writeAction("userctr 0 3 1")                              # num of cache active hit ++
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("evict: mov_reg2lm OB_0 UDPR_3 4")            # evict the cached vertex value and insert incoming one to the cache
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")
    tran4.writeAction("mov_imm2reg UDPR_0 0")
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0 <- pointer to the vertax array base in DRAM
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_4 3 {0xffffffff}")     # fetch the old pagerank value from DRAM
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_5 4 {0xffffffff}")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['rd_return']} 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        
    tran4.writeAction("userctr 0 4 1")                              # num of cache insertion ++
    tran4.writeAction("yield_terminate 2 16") 

    '''
    Receive the pagerank value read from the DRAM, apply the (accumulated) updates and store it back to the DRAM
    Operands:
        OB_0    pagerank value to be updated
        OB_1    vertex id
    '''
    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    tran5.writeAction("mov_imm2reg UDPR_0 0")
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0  <- pointer to the vertax array base in DRAM
    tran5.writeAction(f"mov_imm2reg UDPR_0 {CACHE_OFFSET}")
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_3 3 {HASH_MASK}")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- cache entry addr
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")    
    tran5.writeAction(f"bitwise_or_imm UDPR_6 UDPR_6 {INACTIVE_MASK}")  
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")                 # flip the highest bit indicating the value is written back
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")                 
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")                  # apply the cumulated updates
    tran5.writeAction("mov_reg2lm UDPR_2 UDPR_3 4")                 # update the cache entry 

    # store the udpated value back the DRAM (write through cache)
    tran5.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5") 
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_4 3 {0xffffffff}")
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_6 4 {0xffffffff}")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    tran5.writeAction("yield_terminate 2 16")

    '''
    Acknowledge the store of the new pagerank value and update the termination counter accordingly
    Operands:
    '''
    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction(f"lshift_add_imm LID UDPR_0 2 {TERM_COUNTER_OFFSET}")    # new pagerank value is written back, termination counter ++
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("yield_terminate 0 16")

    return efa


def GeneratePagerankEFA( ):
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    event_map = {
        'init':0,
        'readNode':1,
        'readEdge':2,
        'update':3,
        'rd_return':4,
        'store_ack':5
    }

    ISSUE_COUNTER_OFFSET    = 4092 << 2
    TERM_COUNTER_OFFSET     = 4094 << 2 
    INVALID_VAL             = 0xffffffff
    HASH_MASK               = 4095 << 3
    HASHMAP_SIZE            = 4096
    HASHMAP_OFFSET          = HASHMAP_SIZE << 2
    BATCH_SIZE              = 16
    NUM_WORKERS             = 64
    INACTIVE_MASK           = 1 << 31

    '''
    Initialize the scratchpad memory (metadata, hashmap)
    Operands:
        OB_0_1  vertex array (graph) base address in DRAM
        OB_2    number of workers 
        OB_3    number of vertices of the input graph
    '''
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init'])
    tran1.writeAction("mov_ob2ear OB_0_1 EAR_0")                # EAR_0  <- pointer to the base of vertex arrary in DRAM
    tran1.writeAction("subi OB_2 UDPR_0 1")                     # UDPR_0 <- num of workers - 1
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # UDPR_1 <- num_vertex 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # UDPR_11 <- base event word
    tran1.writeAction(f"lshift_and_imm LID UDPR_2 16 {0xffffffff}")     # UDPR_2 <- LM lane local bank offset 
    tran1.writeAction("mov_ear2lm EAR_0 UDPR_2 8")                      # Store a copy of the base pointer to LM

    # Initialize the lane private counters: number of pagerank value updates being issued and processed respectively
    tran1.writeAction(f"addi UDPR_2 UDPR_2 {TERM_COUNTER_OFFSET}")      # termination counter addr in LM
    tran1.writeAction("mov_imm2reg UDPR_3 0")
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction(f"lshift_add_imm LID UDPR_2 16 {ISSUE_COUNTER_OFFSET}")
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")

    # Initialize the write through cache in the scratchpad
    # The lane-private cache starts at address (lane bank base + offset HASHMAP_OFFSET)
    tran1.writeAction(f"lshift_add_imm LID UDPR_2 16 {HASHMAP_OFFSET}")
    tran1.writeAction(f"mov_imm2reg UDPR_3 {INVALID_VAL}")
    tran1.writeAction("addi LID UDPR_4 1") 
    tran1.writeAction(f"lshift_and_imm UDPR_4 UDPR_4 16 {0xffffffff}")  # UDPR_4 <- end address of the cache == start of next lane's local LM bank 
    tran1.writeAction("init_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction("blt UDPR_2 UDPR_4 init_loop")

    # Initialize the lane private counter for the number of edges already fetched from DRAM (or equivalently the number of updates issued)
    tran1.writeAction("addi LID UDPR_2 0")                      # UDPR_2 <- number of fetched vertex 
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13")                # UPDR_13 <- vertex array fetch stride == number of workers

    tran1.writeAction("tranCarry_goto block_1")                 # inline the code for fetching vertex from DRAM (inline code from block 1)

    '''
    Process the source vertex and fetch #BATCH_SIZE(16) edges from the edge list in DRAM
    Operands:
        OB_0    degree / number of neighbors
        OB_1    old pagerank value
        OB_2_3  edge list base address in the DRAM
    '''
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 next_node")                   # zero degree vertex, skip
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1  <- edge array base address in DRAM
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- weight per outgoing edge

    # Fetch edges from the edge list in DRAM (in batches)
    tran2.writeAction(f"send_dmlm_ld_wret UDPR_8 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran2.writeAction(f"lshift_add_imm LID UDPR_14 16 {ISSUE_COUNTER_OFFSET}")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 UDPR_5 UDPR_15")             # add v's degree to the number of edges fetched 
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran2.writeAction("yield 4")

    tran2.writeAction("next_node: tranCarry_goto block_1")      # skip this vertex if degree==0 (inline code from block 1)

    '''
    Send update to the destination vertex for each edge and fetch the next 16 edges from DRAM
    Operands:
        OB_[0-{BATCH_SIZE-1}]   destination vertex id for an edge 
    '''
    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction(f"ev_update_2 UDPR_11 {event_map['update']} 255 5")   # UDPR_11 <- event word for the event to be sent
    tran3.writeAction(f"addi UDPR_8 UDPR_10 {BATCH_SIZE}")
    tran3.writeAction("bge UDPR_10 UDPR_5 fetch0")                          # prefetch next batch of edges if there exists
    tran3.writeAction(f"lshift_and_imm UDPR_10 UDPR_10 2 {0xffffffff}")
    tran3.writeAction(f"send_dmlm_ld_wret UDPR_10 {event_map['readEdge']} {BATCH_SIZE<<2} 1")   # fetch the next batch of edges from DRAM
    for k in range(BATCH_SIZE):
        tran3.writeAction(f"fetch{k}: bitwise_and OB_{k} UDPR_0 UDPR_3")    # UPDR_3 <- the lane id to which the update is going to send 
        tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
        tran3.writeAction(f"send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_{k} UDPR_7")
        tran3.writeAction("addi UDPR_8 UDPR_8 1")
        tran3.writeAction("bge UDPR_8 UDPR_5 next_vertex")                  # skip the rest of the loop if finish fetching all the edges in the neighbor list
    tran3.writeAction(f"yield {BATCH_SIZE}")    

    # finish read all edges
    tran3.writeAction("next_vertex: tranCarry_goto block_1")                # finish process this vertex, and go fetching the next (inline code from block 1)

    
    '''Read next vertex from the vertex list in DRAM (strided read based on the number of worders'''
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 fin_fetch")         # terminates if read all assigned vertices
    efa.appendBlockAction("block_1", f"lshift_and_imm UDPR_2 UDPR_3 3 {0xffffffff}") 
    efa.appendBlockAction("block_1", f"lshift_and_imm UDPR_2 UDPR_4 4 {0xffffffff}") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4")            # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", f"send_dmlm_ld_wret UDPR_4 {event_map['readNode']} 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2")           # stride = number of workers
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "fin_fetch: yield_terminate 4 16")


    '''
    Receive a value passed from an in-edge, check if the vertex is cached in the scratchpad and update accordingly. Cases are
        1) active_hit   - Requested vertex is cached due to a previous update request to the same vertex -> merge the incoming value with cached value. 
                          No need to write back because it's still waiting for the vertex value read from DRAM coming back to perform an accumulated update.
        2) hit          - Both the requested vertex and its up-to-date value (in DRAM) is cached, update the cached value and write back the data. 
                          (because the policy is write through)
        3) evict        - Requested vertex is not cached. Since the current cached vertex value has been updated and written back to DRAM, it can be evicted. 
                          Evict the old entry and insert the incoming vertex and value to the cache. Then send an DRAM read to load the vertex value from DRAM.
        4) collision    - Requested vertex is not cached and the current cached vertex update is not finished yet. Delay this update by pushing it back to the 
                          end of event queue.
    Operands:
        OB_0    id of the vertex to be updated
        OB_1    value passed from the in-edge 
    '''
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    tran4.writeAction(f"lshift_add_imm LID UDPR_0 16 {HASHMAP_OFFSET}")
    if NUM_WORKERS >= 8: 
        HASH_SHIFT_VAL = int(math.log2(NUM_WORKERS)) - 3
        tran4.writeAction(f"rshift_and_imm OB_0 UDPR_3 {HASH_SHIFT_VAL} {HASH_MASK}")
    else:
        HASH_SHIFT_VAL = 3 - int(math.log2(NUM_WORKERS)) 
        tran4.writeAction(f"lshift_and_imm OB_0 UDPR_3 {HASH_SHIFT_VAL} {HASH_MASK}")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- hashmap entry addr
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")                 # UDPR_4 <- current key in the hashmap entry
    tran4.writeAction("beq UDPR_4 OB_0 active_hit")                 # hit the cache and there's an ongoing load to that vertex value
    tran4.writeAction(f"bitwise_and_imm UDPR_4 UDPR_5 {INACTIVE_MASK-1}")
    tran4.writeAction("beq UDPR_5 OB_0 hit")                        # hit the cache and the up-to-date DRAM value is also cached
    tran4.writeAction("rshift_and_imm UDPR_4 UDPR_5 31 1")
    tran4.writeAction(f"beq UDPR_5 1 evict")                        # current cache entry has been written back and can be evicted 

    # collision on the cache entry, push the update event to the end of the lane's event queue 
    tran4.writeAction(f"ev_update_2 UDPR_12 {event_map['update']} 255 5") 
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    tran4.writeAction("userctr 0 2 1")                              # num of cache collision ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("hit: addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_7 4")
    tran4.writeAction("fp_add UDPR_7 OB_1 UDPR_7")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_3 4")
    # store the udpated value back the DRAM because the cache policy is write through
    tran4.writeAction(f"lshift_and_imm LID UDPR_0 16 {0xffffffff}")     # UDPR_0 <- lane bank base
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0  <- pointer to the vertax array base in DRAM
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5") 
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_4 3 {0xffffffff}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_6 4 {0xffffffff}")
    tran4.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran4.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_7 0")
    tran4.writeAction("userctr 0 1 1")                              # num of cache hit ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("active_hit: addi UDPR_3 UDPR_3 4")           # hit and combine the incoming value with previous updates
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")
    tran4.writeAction(f"lshift_add_imm LID UDPR_0 16 {TERM_COUNTER_OFFSET}")    # update merged, termination counter ++
    tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran4.writeAction("addi UDPR_7 UDPR_7 1")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran4.writeAction("userctr 0 3 1")                              # num of cache active hit ++
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("evict: mov_reg2lm OB_0 UDPR_3 4")            # evict the cached vertex value and insert incoming one to the cache
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")   
    tran4.writeAction(f"lshift_and_imm LID UDPR_0 16 {0xffffffff}")     # UDPR_0 <- lane bank base
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0 <- pointer to the vertax array base in DRAM
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_4 3 {0xffffffff}")     # fetch the old pagerank value from DRAM
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_5 4 {0xffffffff}")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['rd_return']} 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        
    tran4.writeAction("userctr 0 4 1")                              # num of cache insertion ++
    tran4.writeAction("yield_terminate 2 16") 

    '''
    Receive the pagerank value read from the DRAM, apply the (accumulated) updates and store it back to the DRAM
    Operands:
        OB_0    pagerank value to be updated
        OB_1    vertex id
    '''
    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    tran5.writeAction(f"lshift_and_imm LID UDPR_0 16 {0xffffffff}")     # UDPR_0 <- lane local bank base addr
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                      # EAR_0  <- pointer to the vertax array base in DRAM
    tran5.writeAction(f"addi UDPR_0 UDPR_0 {HASHMAP_OFFSET}")
    if NUM_WORKERS >= 8: 
        HASH_SHIFT_VAL = int(math.log2(NUM_WORKERS)) - 3
        tran5.writeAction(f"rshift_and_imm OB_1 UDPR_3 {HASH_SHIFT_VAL} {HASH_MASK}")
    else:
        HASH_SHIFT_VAL = 3 - int(math.log2(NUM_WORKERS)) 
        tran5.writeAction(f"lshift_and_imm OB_1 UDPR_3 {HASH_SHIFT_VAL} {HASH_MASK}")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- cache entry addr
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")    
    tran5.writeAction(f"bitwise_or_imm UDPR_6 UDPR_6 {INACTIVE_MASK}")  
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")                 # flip the highest bit indicating the value is written back
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")                 
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")                  # apply the cumulated updates
    tran5.writeAction("mov_reg2lm UDPR_2 UDPR_3 4")                 # update the cache entry 

    # store the udpated value back the DRAM (write through cache)
    tran5.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5") 
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_4 3 {0xffffffff}")
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_6 4 {0xffffffff}")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    tran5.writeAction("yield_terminate 2 16")

    '''
    Acknowledge the store of the new pagerank value and update the termination counter accordingly
    Operands:
    '''
    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction(f"lshift_add_imm LID UDPR_0 16 {TERM_COUNTER_OFFSET}")    # new pagerank value is written back, termination counter ++
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("yield_terminate 0 16")

    return efa


def GeneratePagerankBaseEFA():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() 
    efa.add_state(state1)

    event_map = {
        'init':0,
        'readNode':1,
        'readEdge':2,
        'update':3,
        'rd_return':4,
        'store_ack':5
    }

    ISSUE_COUNTER_OFFSET = 4092 << 2
    TERM_COUNTER_OFFSET = 4094 << 2 
    NEG_ONE = 4294967295
    HASH_MASK = 4095 << 3
    HASHMAP_SIZE = 4096
    HASHMAP_OFFSET = HASHMAP_SIZE << 2
    BATCH_SIZE = 16

    '''
    Initialize the scratchpad memory (metadata, hashmap)
    Operands:
        OB_0_1  vertex array (graph) base address in DRAM
        OB_2    number of workers 
        OB_3    number of vertices of the input graph
    '''
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init'])
    tran1.writeAction("mov_ob2ear OB_0_1 EAR_0")                # EAR_0 <- pointer to the base of vertex arrary in DRAM
    tran1.writeAction("subi OB_2 UDPR_0 1")                     # UDPR_0 <- num of workers - 1
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # UDPR_1 <- num_vertex 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # UDPR_11 <- base event word
    tran1.writeAction("lshift_and_imm LID UDPR_2 16 4294967295")    # UDPR_2 <- LM lane local bank offset 
    tran1.writeAction("mov_ear2lm EAR_0 UDPR_2 8")              # Store a copy of the base pointer to LM
    # Initialize the lane private counter for the number of pagerank value updates being processed
    tran1.writeAction(f"addi UDPR_2 UDPR_2 {TERM_COUNTER_OFFSET}")  # termination counter addr in LM
    tran1.writeAction("mov_imm2reg UDPR_3 0")
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    # Initialize the hash map entries in the LM with value NEG_ONE, indicating it's empty
    # The hash map start from address with offset 
    tran1.writeAction("mov_imm2reg UDPR_3 -1")                  # initialize entries in per lane hash map to -1
    tran1.writeAction(f"lshift_add_imm LID UDPR_2 16 {HASHMAP_OFFSET}")
    tran1.writeAction("addi LID UDPR_4 1") 
    tran1.writeAction("lshift_and_imm UDPR_4 UDPR_4 16 4294967295") # UDPR_4 <- start address of the next lane's local LM bank 
    tran1.writeAction("init_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction("blt UDPR_2 UDPR_4 init_loop")
    # Initialize the lane private counter for the number of edges already fetched from DRAM (or equivalently the number of updates issued)
    tran1.writeAction("addi LID UDPR_2 0")                      # UDPR_2 <- number of fetched vertex 
    tran1.writeAction(f"lshift_add_imm LID UDPR_14 16 {ISSUE_COUNTER_OFFSET}")
    tran1.writeAction("mov_imm2reg UDPR_15 0")
    tran1.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13") 

    tran1.writeAction("tranCarry_goto block_1")                 # jump to the logic for fetching vertex struct from DRAM 

    '''
    Process the source vertex and fetch #BATCH_SIZE(16) edges from the edge list in DRAM
    Operands:
        OB_0    degree / number of neighbors
        OB_1    old pagerank value
        OB_2_3  edge list base address in the DRAM
    '''
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 next_node")                   # zero degree vertex, skip
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address in DRAM
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- weight per outgoing edge
    tran2.writeAction(f"send_dmlm_ld_wret UDPR_8 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran2.writeAction(f"lshift_add_imm LID UDPR_14 16 {ISSUE_COUNTER_OFFSET}")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 UDPR_5 UDPR_15")             # add v's degree to the number of edges fetched 
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran2.writeAction("yield 4")

    tran2.writeAction("next_node: tranCarry_goto block_1")      # skip this vertex if degree==0

    '''
    Send update to the destination vertex for each edge and fetch the next 16 edges from DRAM
    Operands:
        OB_[0-15]   destination vertex id for an edge 
    '''
    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction(f"ev_update_2 UDPR_11 {event_map['update']} 255 5")           # UDPR_11 <- event word for the event to be sent
    for k in range(BATCH_SIZE):
        tran3.writeAction(f"bitwise_and OB_{k} UDPR_0 UDPR_3")                      # UPDR_3 <- the lane id to which the update is going to send 
        tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
        tran3.writeAction(f"send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_{k} UDPR_7")
        tran3.writeAction("addi UDPR_8 UDPR_8 1")
        tran3.writeAction("bge UDPR_8 UDPR_5 end_loop")             # skip the rest of the loop if finish fetching all the edges in the neighbor list
    tran3.writeAction("lshift_and_imm UDPR_8 UDPR_10 2 4294967295")
    tran3.writeAction(f"send_dmlm_ld_wret UDPR_10 {event_map['readEdge']} {BATCH_SIZE<<2} 1")   # fetch the next batch of edges from DRAM
    tran3.writeAction("yield 16")    

    # finish read all edges
    tran3.writeAction("end_loop: tranCarry_goto block_1")                  # finish process this vertex, and go fetching the next

    
    '''Read next vertex from the vertex list in DRAM (strided read based on the number of worders'''
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 fin_fetch")         # if read all nodes?
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_3 3 4294967295") 
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_4 4 4294967295") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4")            # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", f"send_dmlm_ld_wret UDPR_4 {event_map['readNode']} 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2")           # stride = number of workers
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "fin_fetch: yield_terminate 4 16")


    '''
    Receive an update, if there's an on-flight DRAM read to the same vertex, merge with previous update in the scratchpad memory
    If the hashmap entry is empty, store the update in the scratchpad, and read the current up-to-date pagerank value from DRAM
    If the hashmap entry is not empty and the vertex id doesn't match, push the update to the end of the event queue (i.e. wait until the entry is freed)
    Operands:
        OB_0    vertex id
        OB_1    weight passed from that edge (i.e. to be added)
    '''
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    tran4.writeAction(f"lshift_add_imm LID UDPR_0 16 {HASHMAP_OFFSET}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_3 3 {HASH_MASK}")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- hashmap entry addr
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")                 # UDPR_4 <- current key in the hashmap entry
    tran4.writeAction("beq UDPR_4 OB_0 hit")                        # hit hash map
    tran4.writeAction(f"bge UDPR_4 {NEG_ONE} empty_entry")          # entry is empty, ready for inserting 
    # collision in the hash map entry, push the update event to the end of the lane's event queue 
    # by sending the same event with the same operands to itself 
    tran4.writeAction(f"ev_update_2 UDPR_12 {event_map['update']} 255 5") 
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    tran4.writeAction("userctr 0 2 1")                              # num of hashmap collision ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("hit: addi UDPR_3 UDPR_3 4")                  # hit and combine the value to be updated with previous ones
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")
    tran4.writeAction(f"lshift_add_imm LID UDPR_0 16 {TERM_COUNTER_OFFSET}")    # update merged, termination counter ++
    tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran4.writeAction("addi UDPR_7 UDPR_7 1")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran4.writeAction("userctr 0 3 1")                              # num of hashmap hit ++
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("empty_entry: mov_reg2lm OB_0 UDPR_3 4")      # insert the update to hashmap
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")   
    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # UDPR_0 <- lane bank base
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                  # EAR_0 <- pointer to the vertax array base in DRAM
    tran4.writeAction("lshift_and_imm OB_0 UDPR_4 3 4294967295")    # fetch the old pagerank value from DRAM
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['rd_return']} 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        
    tran4.writeAction("userctr 0 4 1")                              # num of hashmap insertion ++
    tran4.writeAction("yield_terminate 2 16") 

    '''
    Receive the pagerank value read from the DRAM, apply the (accumulated) updates and store it back to the DRAM
    Operands:
        OB_0    pagerank value to be updated
        OB_1    vertex id
    '''
    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    tran5.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # UDPR_0 <- lane bank base
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                  # EAR_0 <- pointer to the vertax array base in DRAM
    tran5.writeAction(f"addi UDPR_0 UDPR_0 {HASHMAP_OFFSET}")
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_3 3 {HASH_MASK}")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- hashmap entry addr
    tran5.writeAction("mov_imm2reg UDPR_6 -1")      
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")                 # free the hashmap entry 
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")                 
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")                  # apply the cumulated updates

    tran5.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5") # store the udpated value back the DRAM
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    tran5.writeAction("yield_terminate 2 16")

    '''
    Acknowledge the store of the new pagerank value and update the termination counter accordingly
    Operands:
    '''
    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran6.writeAction(f"addi UDPR_0 UDPR_0 {TERM_COUNTER_OFFSET}")  # write back the new pagerank value, termination counter ++
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("yield_terminate 0 16")

    return efa


def GeneratePagerankRegulateEFA():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() 
    efa.add_state(state1)

    event_map = {
        'init':0,
        'readNode':1,
        'readEdge':2,
        'update':3,
        'rd_return':4,
        'store_ack':5,
        'regulating':6
    }

    ISSUE_COUNTER_OFFSET = 4092 << 2
    TERM_COUNTER_OFFSET = 4094 << 2 
    NEG_ONE = 4294967295
    HASH_MASK = 4095 << 3
    HASHMAP_SIZE = 4096
    HASHMAP_OFFSET = HASHMAP_SIZE << 2
    BATCH_SIZE = 16
    NUM_REGULATE_ITER = 1

    tran7 = state0.writeTransition("eventCarry", state0, state0, event_map['regulating'])
    tran7.writeAction("addi OB_0 UDPR_12 1")
    tran7.writeAction(f"bge UDPR_12 {NUM_REGULATE_ITER} fetch_next")
    tran7.writeAction(f"ev_update_1 EQT UDPR_11 {event_map['regulating']} 1")
    tran7.writeAction(f"send4_wret UDPR_11 LID {event_map['regulating']} UDPR_12")
    tran7.writeAction("yield 1")

    # tran7.writeAction("tranCarry_goto block_1")
    tran7.writeAction("fetch_next: lshift_and_imm UDPR_8 UDPR_10 2 4294967295")
    tran7.writeAction(f"send_dmlm_ld_wret UDPR_10 {event_map['readEdge']} {BATCH_SIZE<<2} 1")   # fetch the next batch of edges from DRAM
    tran7.writeAction("yield 1")

    '''
    Initialize the scratchpad memory (metadata, hashmap)
    Operands:
        OB_0_1  vertex array (graph) base address in DRAM
        OB_2    number of workers 
        OB_3    number of vertices of the input graph
    '''
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init'])
    tran1.writeAction("mov_ob2ear OB_0_1 EAR_0")                # EAR_0 <- pointer to the base of vertex arrary in DRAM
    tran1.writeAction("subi OB_2 UDPR_0 1")                     # UDPR_0 <- num of workers - 1
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # UDPR_1 <- num_vertex 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # UDPR_11 <- base event word
    tran1.writeAction("lshift_and_imm LID UDPR_2 16 4294967295")    # UDPR_2 <- LM lane local bank offset 
    tran1.writeAction("mov_ear2lm EAR_0 UDPR_2 8")              # Store a copy of the base pointer to LM
    # Initialize the lane private counter for the number of pagerank value updates being processed
    tran1.writeAction(f"addi UDPR_2 UDPR_2 {TERM_COUNTER_OFFSET}")  # termination counter addr in LM
    tran1.writeAction("mov_imm2reg UDPR_3 0")
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    # Initialize the hash map entries in the LM with value NEG_ONE, indicating it's empty
    # The hash map start from address with offset 
    tran1.writeAction("mov_imm2reg UDPR_3 -1")                  # initialize entries in per lane hash map to -1
    tran1.writeAction(f"lshift_add_imm LID UDPR_2 16 {HASHMAP_OFFSET}")
    tran1.writeAction("addi LID UDPR_4 1") 
    tran1.writeAction("lshift_and_imm UDPR_4 UDPR_4 16 4294967295") # UDPR_4 <- start address of the next lane's local LM bank 
    tran1.writeAction("init_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction("blt UDPR_2 UDPR_4 init_loop")
    # Initialize the lane private counter for the number of edges already fetched from DRAM (or equivalently the number of updates issued)
    tran1.writeAction("addi LID UDPR_2 0")                      # UDPR_2 <- number of fetched vertex 
    tran1.writeAction(f"lshift_add_imm LID UDPR_14 16 {ISSUE_COUNTER_OFFSET}")
    tran1.writeAction("mov_imm2reg UDPR_15 0")
    tran1.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13") 

    tran1.writeAction("tranCarry_goto block_1")                 # jump to the logic for fetching vertex struct from DRAM 

    '''
    Process the source vertex and fetch #BATCH_SIZE(16) edges from the edge list in DRAM
    Operands:
        OB_0    degree / number of neighbors
        OB_1    old pagerank value
        OB_2_3  edge list base address in the DRAM
    '''
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 next_node")                   # 0 degree vertex, skip
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address in DRAM
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- weight per outgoing edge
    tran2.writeAction(f"send_dmlm_ld_wret UDPR_8 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran2.writeAction(f"lshift_add_imm LID UDPR_14 16 {ISSUE_COUNTER_OFFSET}")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 UDPR_5 UDPR_15")             # add v's degree to the number of edges fetched 
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran2.writeAction("yield 4")

    tran2.writeAction("next_node: tranCarry_goto block_1")      # skip this vertex if degree==0

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")  # UDPR_11 <- event word for the event to be sent
    for k in range(BATCH_SIZE):
        tran3.writeAction(f"bitwise_and OB_{k} UDPR_0 UDPR_3")                      # UPDR_3 <- the lane id to which the update is going to send 
        tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
        tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_0 UDPR_7")
        tran3.writeAction("addi UDPR_8 UDPR_8 1")
        tran3.writeAction("bge UDPR_8 UDPR_5 end_loop")             # skip the rest of the loop if finish fetching all the edges in the neighbor list
    tran3.writeAction("mov_imm2reg UDPR_12 0")
    tran3.writeAction(f"ev_update_1 EQT UDPR_11 {event_map['regulating']} 1")
    tran3.writeAction(f"send4_wret UDPR_11 LID {event_map['regulating']} UDPR_12")
    tran3.writeAction("yield 16")    

    # finish read all edges
    tran3.writeAction("end_loop: tranCarry_goto block_1")                  # finish process this vertex, and go fetching the next
    # tran3.writeAction("end_loop: mov_imm2reg UDPR_12 0")
    # tran3.writeAction(f"ev_update_1 EQT UDPR_11 {event_map['regulating']} 1")
    # tran3.writeAction(f"send4_wret UDPR_11 LID {event_map['regulating']} UDPR_12")
    # tran3.writeAction("yield 16")

    
    '''Read next vertex from the vertex list in DRAM (strided read based on the number of worders'''
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 fin_fetch")         # if read all nodes?
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_3 3 4294967295") 
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_4 4 4294967295") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4")            # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", f"send_dmlm_ld_wret UDPR_4 {event_map['readNode']} 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2")           # stride = number of workers
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "fin_fetch: yield_terminate 4 16")
    
    # counter 2 number of hashmap collision
    # counter 3 number of hashmap hit
    # counter 4 numberof hashmap insertion

    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    tran4.writeAction(f"lshift_add_imm LID UDPR_0 16 {HASHMAP_OFFSET}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_3 3 {HASH_MASK}")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- hashmap entry addr
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")                 # UDPR_4 <- current key in the hashmap entry
    # tran4.writeAction("beq UDPR_4 OB_0 hit")                        # hit hash map
    tran4.writeAction(f"bge UDPR_4 {NEG_ONE} empty_entry")          # entry is empty, ready for inserting 
    # collision in the hash map entry, push the update event to the end of the lane's event queue 
    # by sending the same event with the same operands to itself 
    tran4.writeAction(f"ev_update_2 UDPR_11 {event_map['update']} 255 5") 
    tran4.writeAction("send4_wcont UDPR_11 LID UDPR_11 OB_0 OB_1")
    tran4.writeAction("userctr 0 2 1")                              # num of hashmap collision ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction(f"hit: ev_update_2 UDPR_12 {event_map['update']} 255 5") 
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    tran4.writeAction("yield_terminate 2 16")   
    # tran4.writeAction("hit: addi UDPR_3 UDPR_3 4")                  # hit and combine the value to be updated with previous ones
    # tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    # tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    # tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")
    # tran4.writeAction(f"lshift_add_imm LID UDPR_0 16 {TERM_COUNTER_OFFSET}")    # update merged, termination counter ++
    # tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    # tran4.writeAction("addi UDPR_7 UDPR_7 1")
    # tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    # tran4.writeAction("userctr 0 3 1")                              # num of hashmap hit ++
    # tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("empty_entry: mov_reg2lm OB_0 UDPR_3 4")      # insert the update to hashmap
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")   
    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # UDPR_0 <- lane bank base
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                  # EAR_0 <- pointer to the vertax array base in DRAM
    tran4.writeAction("lshift_and_imm OB_0 UDPR_4 3 4294967295")    # fetch the old pagerank value from DRAM
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['rd_return']} 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")     
    tran4.writeAction("userctr 0 4 1")                              # num of hashmap insertion ++
    tran4.writeAction("yield_terminate 2 16") 

    '''
    Receive the pagerank value read from the DRAM, apply the (accumulated) updates and store it back to the DRAM
    Operands:
        OB_0    pagerank value to be updated
        OB_1    vertex id
    '''
    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    tran5.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # UDPR_0 <- lane bank base
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                  # EAR_0 <- pointer to the vertax array base in DRAM
    tran5.writeAction(f"addi UDPR_0 UDPR_0 {HASHMAP_OFFSET}")
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_3 3 {HASH_MASK}")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- hashmap entry addr
    tran5.writeAction("mov_imm2reg UDPR_6 -1")      
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")                 # free the hashmap entry 
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")                 
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")                  # apply the cumulated updates

    tran5.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5") # store the udpated value back the DRAM
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    tran5.writeAction("yield_terminate 2 16")

    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction(f"lshift_add_imm LID UDPR_0 16 {TERM_COUNTER_OFFSET}")    # write back the new pagerank value, termination counter ++
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("yield_terminate 0 16")

    return efa
    # hash function 32-bit integer to 32-bit integer
    # add a separate hash function (snappy hash)
    # best hash function to hash a 32-bit string to a 32-bit integer
    # or take a hash and add a 32-bit integer to it

    # write some structured graph with fixed degree, how much fan-out 
    # how to aggressively exploit parallelism 
    # check the number of edges per vertex
    # find the parallelism per number of cycles (no need to be accurate)
    # add counter for conflicts
    # support for hash map and conflicts checking (need to know homw many conflicts)
    # think about how to do that 
    # add analysis of the code ( howmany percent instructions)

def GeneratePagerankBatchEFA():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() 
    efa.add_state(state1)

    event_map = {
        'init':0,
        'readNode':1,
        'readEdge':2,
        'update':3,
        'rd_return':4,
        'store_ack':5,
        'fin':6
    }

    

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init'])
    tran1.writeAction("mov_ob2ear OB_0_1 EAR_0")                # 0 EAR_0 <- edge_addr
    tran1.writeAction("subi OB_2 UDPR_0 1")                     # 1 UDPR_0 <- num of workers - 1
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # 2 UDPR_1 <- num_nodes 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # 3 UDPR_11 <- base event word
    tran1.writeAction("lshift_and_imm LID UDPR_2 16 4294967295")
    tran1.writeAction("mov_ear2lm EAR_0 UDPR_2 8")
    tran1.writeAction("addi UDPR_2 UDPR_2 16376")               # 6 termination counter addr
    tran1.writeAction("mov_imm2reg UDPR_3 0")
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("mov_imm2reg UDPR_3 -1")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction("lshift_add_imm LID UDPR_4 16 65536")
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction("blt UDPR_2 UDPR_4 #12")
    tran1.writeAction("addi LID UDPR_2 0")                      # UDPR_2 <- node counter
    tran1.writeAction("lshift_and_imm LID UDPR_14 16 4294967295")
    tran1.writeAction("addi UDPR_14 UDPR_14 16368")
    tran1.writeAction("mov_imm2reg UDPR_15 0")
    tran1.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13")                # UDPR_13 <- number of workers
    tran1.writeAction("tranCarry_goto block_1")
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 next_node")                         # 0 degree skip
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- new weight per outgoing edge

    tran2.writeAction("edge: lshift_and_imm UDPR_8 UDPR_6 2 4294967295")
    tran2.writeAction("send_dmlm_ld_wret UDPR_6 " + str(event_map["readEdge"]) + " 64 1")
    tran2.writeAction("addi UDPR_8 UDPR_8 16")
    tran2.writeAction("blt UDPR_8 UDPR_5 edge")
    tran2.writeAction("lshift_and_imm LID UDPR_14 16 4294967295")
    tran2.writeAction("addi UDPR_14 UDPR_14 16368")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 UDPR_5 UDPR_15")
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- num of edge processed
    tran2.writeAction("yield 4")

    tran2.writeAction("next_node: tranCarry_goto block_1")

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    BATCH_SIZE = 16
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    for k in range(BATCH_SIZE):
        tran3.writeAction(f"bitwise_and OB_{k} UDPR_0 UDPR_3")
        tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
        tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_0 UDPR_7")
        tran3.writeAction("addi UDPR_8 UDPR_8 1")
        tran3.writeAction("bge UDPR_8 UDPR_5 end_loop")
    tran3.writeAction("yield 16")    

    # finish read all edges
    tran3.writeAction("end_loop: tranCarry_goto block_1")                  # 25 go to fetch next node



    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295") # 0 UDPR_0 <- lane bank base
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")              # 1 EAR_0 <- vertax array base in DRAM
    tran4.writeAction("addi UDPR_0 UDPR_0 16384")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_3 3 32767")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")               # 4 UDPR_3 <- addr to load key 
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("beq UDPR_4 OB_0 #11")                     # 6 hit
    tran4.writeAction("bgt UDPR_4 4294967294 #21")                   # 7 miss
    tran4.writeAction("ev_update_2 UDPR_12 " + str(event_map['update']) +" 255 5")
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("addi UDPR_3 UDPR_3 4")                  # 11 hit and combine
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")

    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran4.writeAction("addi UDPR_0 UDPR_0 16376")
    tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran4.writeAction("addi UDPR_7 UDPR_7 1")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("mov_reg2lm OB_0 UDPR_3 4")              # 21
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_4 3 4294967295")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction("ev_update_2 UDPR_5 " + str(event_map['rd_return']) + " 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        # read current pagerank value from DRAM
    tran4.writeAction("yield_terminate 2 16") 

    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    tran5.writeAction("lshift_and_imm LID UDPR_0 16 4294967295") # 0 UDPR_0 <- lane bank base
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")               # 1 EAR_0 <- vertax array base in DRAM
    tran5.writeAction("addi UDPR_0 UDPR_0 16384")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_3 3 32767")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                # 4 UDPR_3 <- addr to load key 
    tran5.writeAction("mov_imm2reg UDPR_6 -1")
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")

    tran5.writeAction("ev_update_2 UDPR_5 " + str(event_map['store_ack']) +" 255 5")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    tran5.writeAction("yield_terminate 2 16")

    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran6.writeAction("addi UDPR_0 UDPR_0 16376")
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("yield_terminate 0 16")

    tran6.writeAction("mov_imm2reg UDPR_10 16")             # 7
    tran6.writeAction("mov_lm2reg UDPR_10 UDPR_11 4")
    tran6.writeAction("mov_imm2reg UDPR_10 80")
    tran6.writeAction("mov_lm2reg UDPR_10 UDPR_12 4")
    tran6.writeAction("blt UDPR_11 UDPR_12 #6")
    tran6.writeAction("mov_imm2reg UDPR_0 64")
    tran6.writeAction("mov_imm2reg UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("yield_terminate 0 16")


    # read next node to update
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 #7")      # if read all nodes?
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_3 3 4294967295") 
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_4 4 4294967295") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4") # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", "send_dmlm_ld_wret UDPR_4 " + str(event_map['readNode']) + " 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2") 
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "yield_terminate 4 16")

    return efa


def GeneratePagerankTermCountEFA():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() 
    efa.add_state(state1)

    event_map = {
        'init':0,
        'readNode':1,
        'readEdge':2,
        'update':3,
        'rd_return':4,
        'store_ack':5,
        'fin':6
    }

    

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init'])
    tran1.writeAction("mov_ob2ear OB_0_1 EAR_0")                # 0 EAR_0 <- edge_addr
    tran1.writeAction("subi OB_2 UDPR_0 1")                     # 1 UDPR_0 <- num of workers - 1
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # 2 UDPR_1 <- num_nodes 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # 3 UDPR_11 <- base event word
    tran1.writeAction("lshift_and_imm LID UDPR_2 16 4294967295")
    tran1.writeAction("mov_ear2lm EAR_0 UDPR_2 8")
    tran1.writeAction("addi UDPR_2 UDPR_2 16376")               # 6 termination counter addr
    tran1.writeAction("mov_imm2reg UDPR_3 0")
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("mov_imm2reg UDPR_3 -1")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction("lshift_add_imm LID UDPR_4 16 65536")
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction("blt UDPR_2 UDPR_4 #12")
    tran1.writeAction("addi LID UDPR_2 0")                   # UDPR_2 <- node counter
    tran1.writeAction("lshift_and_imm LID UDPR_14 16 4294967295")
    tran1.writeAction("addi UDPR_14 UDPR_14 16368")
    tran1.writeAction("mov_imm2reg UDPR_15 0")
    tran1.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13") 
    tran1.writeAction("tranCarry_goto block_1")

    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 #13")                         # 0 degree skip
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- new weight per outgoing edge
    tran2.writeAction("ev_update_1 TS UDPR_12 " + str(event_map["readEdge"]) + " 1")
    tran2.writeAction("send_dmlm_ld_wret UDPR_8 " + str(event_map["readEdge"]) + " 16 1")
    tran2.writeAction("lshift_and_imm LID UDPR_14 16 4294967295")
    tran2.writeAction("addi UDPR_14 UDPR_14 16368")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 UDPR_5 UDPR_15")
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran2.writeAction("yield 4")

    tran2.writeAction("tranCarry_goto block_1")

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("bitwise_and OB_0 UDPR_0 UDPR_3")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_0 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 #25")
    tran3.writeAction("bitwise_and OB_0 UDPR_0 UDPR_3")
    # tran3.writeAction("addi UDPR_3 UDPR_4 64")
    # tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_1 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 #25")
    tran3.writeAction("bitwise_and OB_0 UDPR_0 UDPR_3")
    # tran3.writeAction("addi UDPR_3 UDPR_4 64")
    # tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_2 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 #25")
    tran3.writeAction("bitwise_and OB_0 UDPR_0 UDPR_3")
    # tran3.writeAction("addi UDPR_3 UDPR_4 64")
    # tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_3 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 #25")
    tran3.writeAction("lshift_and_imm UDPR_8 UDPR_10 2 4294967295")
    tran3.writeAction("ev_update_1 EQT UDPR_12 " + str(event_map["readEdge"]) + " 1")
    tran3.writeAction("send_dmlm_ld_wret UDPR_10 " + str(event_map["readEdge"]) + " 16 1")
    tran3.writeAction("yield 4")

    # finish read all edges
    tran3.writeAction("tranCarry_goto block_1")                  # 25 go to fetch next node


    # how many time to enroll it
    # macro for fetching nodes/edges from DRAM: parameters include number of elements, base address, a range of free registers
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    # tran4.writeAction("lshift_and_imm OB_0 UDPR_3 3 2097144")  
    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295") # 0 UDPR_0 <- lane bank base
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")              # 1 EAR_0 <- vertax array base in DRAM
    tran4.writeAction("addi UDPR_0 UDPR_0 16384")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_3 3 32767")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")               # 4 UDPR_3 <- addr to load key 
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("beq UDPR_4 OB_0 #11")                     # 6 hit
    tran4.writeAction("bgt UDPR_4 4294967294 #21")                   # 7 miss
    # tran4.writeAction("addi UDPR_3 UDPR_3 4")
    # tran4.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")
    tran4.writeAction("ev_update_2 UDPR_12 " + str(event_map['update']) +" 255 5")
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("addi UDPR_3 UDPR_3 4")                  # 11 hit and combine
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")

    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran4.writeAction("addi UDPR_0 UDPR_0 16376")
    tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran4.writeAction("addi UDPR_7 UDPR_7 1")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("mov_reg2lm OB_0 UDPR_3 4")              # 21
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_4 3 4294967295")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction("ev_update_2 UDPR_5 " + str(event_map['rd_return']) + " 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        # read current pagerank value from DRAM
    tran4.writeAction("yield_terminate 2 16") 

    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    # tran5.writeAction("lshift_and_imm OB_1 UDPR_3 3 2097144")   # UDPR_3 <- key to hashmap
    tran5.writeAction("lshift_and_imm LID UDPR_0 16 4294967295") # 0 UDPR_0 <- lane bank base
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")               # 1 EAR_0 <- vertax array base in DRAM
    tran5.writeAction("addi UDPR_0 UDPR_0 16384")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_3 3 32767")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                # 4 UDPR_3 <- addr to load key 
    tran5.writeAction("mov_imm2reg UDPR_6 -1")
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")
    # tran5.writeAction("mov_imm2reg UDPR_6 0")
    # tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")

    tran5.writeAction("ev_update_2 UDPR_5 " + str(event_map['store_ack']) +" 255 5")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    # tran5.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    # tran5.writeAction("addi UDPR_0 UDPR_0 16376")
    # tran5.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    # tran5.writeAction("addi UDPR_7 UDPR_7 1")
    # tran5.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran5.writeAction("yield_terminate 2 16")

    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran6.writeAction("addi UDPR_0 UDPR_0 16376")
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    # tran6.writeAction("ble UDPR_1 0 #7")
    tran6.writeAction("yield_terminate 0 16")

    tran6.writeAction("mov_imm2reg UDPR_10 16")             # 7
    tran6.writeAction("mov_lm2reg UDPR_10 UDPR_11 4")
    tran6.writeAction("mov_imm2reg UDPR_10 80")
    tran6.writeAction("mov_lm2reg UDPR_10 UDPR_12 4")
    tran6.writeAction("blt UDPR_11 UDPR_12 #6")
    # tran6.writeAction("send_top UDPR_12 4")
    # tran6.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran6.writeAction("mov_imm2reg UDPR_0 64")
    # tran6.writeAction("addi UDPR_0 UDPR_0 64")
    tran6.writeAction("mov_imm2reg UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("yield_terminate 0 16")


    # read next node to update
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 #7")      # if read all nodes?
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_3 3 4294967295") 
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_4 4 4294967295") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4") # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", "send_dmlm_ld_wret UDPR_4 " + str(event_map['readNode']) + " 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2") 
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "mov_imm2reg UDPR_10 16")
    efa.appendBlockAction("block_1", "mov_lm2reg UDPR_10 UDPR_11 4")
    efa.appendBlockAction("block_1", "addi UDPR_11 UDPR_12 1")
    efa.appendBlockAction("block_1", "cmpswp UDPR_12 UDPR_10 UDPR_11 UDPR_12")
    efa.appendBlockAction("block_1", "bne UDPR_12 UDPR_11 #9")
    efa.appendBlockAction("block_1", "yield_terminate 4 16")

    return efa



def GeneratePagerankAssociateEFA():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() 
    efa.add_state(state1)

    event_map = {
        'init':0,
        'readNode':1,
        'readEdge':2,
        'update':3,
        'rd_return':4,
        'store_ack':5,
        'error':6
    }

    LM_BANK_BASE_SHIFT = 16
    ISSUE_COUNTER_OFFSET = 4092 << 2
    TERM_COUNTER_OFFSET = 4094 << 2 
    NEG_ONE = 4294967295
    HASH_MASK = 4095 << 3
    HASHMAP_SIZE = 4096
    HASHMAP_OFFSET = HASHMAP_SIZE << 2
    BATCH_SIZE = 16
    ASSOCIATE_CACHE_LEN_OFFSET = 124
    ASSOCIATE_CACHE_OFFSET = 128
    ASSOCIATE_CACHE_SIZE = 4

    EDGE_FETCH_INST_COUNTER = 1
    HASHMAP_INST_COUNTER = 5
    TERM_INST_COUNTER = 6
    FETCH_VERTEX_INST_COUNTER = 7

    # counter 2 number of hashmap collision
    # counter 3 number of hashmap hit
    # counter 4 number of hashmap insertion

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init'])
    tran1.writeAction("mov_ob2ear OB_0_1 EAR_0")                # 0 EAR_0 <- edge_addr
    tran1.writeAction("subi OB_2 UDPR_0 1")                     # 1 UDPR_0 <- num of workers - 1
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # 2 UDPR_1 <- num_nodes 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # 3 UDPR_11 <- base event word
    tran1.writeAction("lshift_and_imm LID UDPR_2 16 4294967295")
    tran1.writeAction("mov_ear2lm EAR_0 UDPR_2 8")
    tran1.writeAction(f"addi UDPR_2 UDPR_2 {TERM_COUNTER_OFFSET}")               # 6 termination counter addr
    tran1.writeAction("mov_imm2reg UDPR_3 0")
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("mov_imm2reg UDPR_3 -1")                  # initialize entries in per lane hash map to -1
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction("addi LID UDPR_4 1")
    tran1.writeAction("lshift_and_imm UDPR_4 UDPR_4 16 4294967295")
    # tran1.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 4") 
    tran1.writeAction("init_hm_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    # tran1.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 3") 
    tran1.writeAction("blt UDPR_2 UDPR_4 init_hm_loop")

    tran1.writeAction(f"lshift_add_imm LID UDPR_2 16 {ASSOCIATE_CACHE_OFFSET}")    # Initialize the associate cache entries to -1
    tran1.writeAction(f"addi UDPR_2 UDPR_4 {ASSOCIATE_CACHE_SIZE * 8}")
    tran1.writeAction("init_cache_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction("blt UDPR_2 UDPR_4 init_cache_loop")

    tran1.writeAction("addi LID UDPR_2 0")                      # UDPR_2 <- number of fetched vertex 
    tran1.writeAction("lshift_and_imm LID UDPR_14 16 4294967295")   # initialize issued edge counter 
    tran1.writeAction(f"addi UDPR_14 UDPR_14 {ISSUE_COUNTER_OFFSET}")
    tran1.writeAction("mov_imm2reg UDPR_15 0")
    tran1.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran1.writeAction(f"lshift_add_imm LID UDPR_14 \
        {LM_BANK_BASE_SHIFT} {ASSOCIATE_CACHE_LEN_OFFSET}")     # initialize the associate cache length counter to 0
    tran1.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    # tran1.writeAction(f"userctr 0 {TERM_INST_COUNTER} 4") 
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13") 
    tran1.writeAction("tranCarry_goto block_1")

    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 next_node")                   # 0 degree skip
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- new weight per outgoing edge
    tran2.writeAction(f"send_dmlm_ld_wret UDPR_8 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran2.writeAction(f"lshift_add_imm LID UDPR_14 {LM_BANK_BASE_SHIFT} {ISSUE_COUNTER_OFFSET}")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 OB_0 UDPR_15")             # add v's degree to the number of edges issued 
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    # tran2.writeAction(f"userctr 0 {TERM_INST_COUNTER} 5") 
    # tran2.writeAction(f"userctr 0 {FETCH_VERTEX_INST_COUNTER} 7")
    tran2.writeAction("yield 4")

    tran2.writeAction("next_node: tranCarry_goto block_1")                 # 14 skip if degree==0

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    for k in range(BATCH_SIZE):
        tran3.writeAction(f"bitwise_and OB_{k} UDPR_0 UDPR_3")
        tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
        tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_0 UDPR_7")
        tran3.writeAction("addi UDPR_8 UDPR_8 1")
        tran3.writeAction("bge UDPR_8 UDPR_5 end_loop")             # finish fetching all the edges in the neighbor list
        # tran3.writeAction(f"userctr 0 {EDGE_FETCH_INST_COUNTER} 5")
    tran3.writeAction("lshift_and_imm UDPR_8 UDPR_10 2 4294967295")
    tran3.writeAction(f"send_dmlm_ld_wret UDPR_10 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran3.writeAction(f"yield {BATCH_SIZE}")    

    # finish read all edges
    tran3.writeAction("end_loop: tranCarry_goto block_1")                  # 25 fetch next node


    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # UDPR_0 <- lane bank base
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                  # EAR_0 <- addr of vertax array base in DRAM
    tran4.writeAction(f"lshift_add_imm LID UDPR_0 {LM_BANK_BASE_SHIFT} {HASHMAP_OFFSET}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_3 3 {HASH_MASK}")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- hashmap entry addr
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")                 # UDPR_6 <- current hashmap entry key
    # tran4.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 5") 
    tran4.writeAction("beq UDPR_6 OB_0 hit")                        # hit hash map

    tran4.writeAction(f"lshift_add_imm LID UDPR_8 {LM_BANK_BASE_SHIFT} {ASSOCIATE_CACHE_LEN_OFFSET}")   # UDPR_8 <- associate cache length addr
    tran4.writeAction("mov_lm2reg UDPR_8 UDPR_9 4")                 # UDPR_9 <- length of the associate cache
    tran4.writeAction("beq UDPR_9 0 check_hm_empty")                # associate cache is empty, no need to check
    # check associate cache
    tran4.writeAction(f"lshift_add_imm LID UDPR_2 {LM_BANK_BASE_SHIFT} {ASSOCIATE_CACHE_OFFSET}")   # UDPR_2 <- associate cache base address 
    tran4.writeAction("mov_imm2reg UDPR_10 0")
    tran4.writeAction("cache_loop: lshift_and_imm UDPR_10 UDPR_11 3 4294967295")    # UDPR_11 <- entry offset
    tran4.writeAction("add UDPR_11 UDPR_2 UDPR_11")                 # UDPR_11 <- entry addr
    tran4.writeAction("mov_lm2reg UDPR_11 UDPR_4 4 ")               # UDPR_4 <- cache entry key
    tran4.writeAction("beq UDPR_4 OB_0 cache_hit")                  # hit associate cache
    tran4.writeAction("addi UDPR_10 UDPR_10 1")
    tran4.writeAction(f"blt UDPR_10 {ASSOCIATE_CACHE_SIZE} cache_loop")

    tran4.writeAction(f"check_hm_empty: bge UDPR_6 {NEG_ONE} empty_entry")          # hashmap entry is empty?
    tran4.writeAction(f"bge UDPR_9 {ASSOCIATE_CACHE_SIZE} collision")
    tran4.writeAction(f"lshift_add_imm LID UDPR_2 {LM_BANK_BASE_SHIFT} {ASSOCIATE_CACHE_OFFSET}")   # UDPR_2 <- associate cache base address 
    tran4.writeAction(f"addi UDPR_2 UDPR_5 {ASSOCIATE_CACHE_SIZE * 8}")         # UDPR_5 <- associate cache end addr
    tran4.writeAction("find_empty_loop: mov_lm2reg UDPR_2 UDPR_4 4 ")           # UDPR_2 <- entry address
    tran4.writeAction(f"bge UDPR_4 {NEG_ONE} empty_cache_entry")
    tran4.writeAction("addi UDPR_2 UDPR_2 8")
    tran4.writeAction("blt UDPR_2 UDPR_5 find_empty_loop")

    tran4.writeAction(f"collision: ev_update_2 UDPR_12 {event_map['update']} 255 5")
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    # tran4.writeAction("userctr 0 2 1")                              # num of hashmap collision ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("cache_hit: addi UDPR_11 UDPR_3 0")
    tran4.writeAction("hit: addi UDPR_3 UDPR_3 4")                  # hit and combine
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")                 # UDPR_4 <- current hashmape entry value
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")                 # merge updates and store the merged value back to LM

    tran4.writeAction(f"lshift_add_imm LID UDPR_0 16 {TERM_COUNTER_OFFSET}")    # update merged, termination counter ++
    tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran4.writeAction("addi UDPR_7 UDPR_7 1")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    # tran4.writeAction("userctr 0 3 1")                              # num of hashmap hit ++
    # tran4.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 3") 
    # tran4.writeAction(f"userctr 0 {TERM_INST_COUNTER} 5") 
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("empty_cache_entry: addi UDPR_2 UDPR_3 0")
    tran4.writeAction("addi UDPR_9 UDPR_9 1")                       # increase the length of associate cache by 1
    tran4.writeAction("mov_reg2lm UDPR_9 UDPR_8 4")
    tran4.writeAction("empty_entry: mov_reg2lm OB_0 UDPR_3 4")      # insert the update to hashmap or cache
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")   
    tran4.writeAction("lshift_and_imm OB_0 UDPR_4 3 4294967295")    # fetch the old pagerank value from DRAM
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['rd_return']} 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        
    # tran4.writeAction("userctr 0 4 1")                              # num of hashmap insert ++
    # tran4.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 3") 
    tran4.writeAction("yield_terminate 2 16") 

    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    # tran5.writeAction(f"perflog 0 {PerfLogPayload.UD_ACTION_STATS.value} {PerfLogPayload.UD_QUEUE_STATS.value}")
    tran5.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # UDPR_0 <- lane bank base
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                  # EAR_0 <- vertax array base in DRAM
    tran5.writeAction(f"addi UDPR_0 UDPR_0 {HASHMAP_OFFSET}")       # UDPR_0 <- lane private hash map base
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_3 3 {HASH_MASK}")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # UDPR_3 <- hashmap entry addr
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran5.writeAction("beq UDPR_4 OB_1 entry_match")                # entry match the vertex id read from DRAM
    # Miss in the hashmap and check the Associate cache
    tran5.writeAction(f"lshift_add_imm LID UDPR_8 {LM_BANK_BASE_SHIFT} {ASSOCIATE_CACHE_LEN_OFFSET}") 
    tran5.writeAction("mov_lm2reg UDPR_8 UDPR_9 4")                 # UDPR_9 <- # of non-empty entries in the cache
    tran5.writeAction("beq UDPR_9 0 error")
    tran5.writeAction(f"lshift_add_imm LID UDPR_3 16 {ASSOCIATE_CACHE_OFFSET}")
    tran5.writeAction(f"addi UDPR_3 UDPR_5 {ASSOCIATE_CACHE_SIZE * 8}")     # UDPR_5 <- associate cache end addr
    tran5.writeAction("find_entry_loop: mov_lm2reg UDPR_3 UDPR_4 4 ")
    tran5.writeAction("beq UDPR_4 OB_1 cache_hit")          # entry match the vertex id read from DRAM
    tran5.writeAction("addi UDPR_3 UDPR_3 8")
    tran5.writeAction("blt UDPR_3 UDPR_5 find_entry_loop")

    tran5.writeAction(f"error: ev_update_2 UDPR_11 {event_map['error']} 255 5")    # miss in both hashmap and associate cache, should never reach here
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_11 OB_0 0")
    tran5.writeAction("yield_terminate 2 16")

    tran5.writeAction("cache_hit: subi UDPR_9 UDPR_9 1")    # reduce the associate cache used length by 1
    tran5.writeAction("mov_reg2lm UDPR_9 UDPR_8 4")
    tran5.writeAction("entry_match: mov_imm2reg UDPR_6 -1")         # free the hashmap entry
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_7 4")                 # UDPR_7 <- accumulated pagerank values
    # tran5.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 8") 
    tran5.writeAction("fp_add OB_0 UDPR_7 UDPR_7")                  # apply the accumulated updates

    tran5.writeAction(f"ev_update_2 UDPR_11 {event_map['store_ack']} 255 5")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_11 UDPR_7 0")

    tran5.writeAction("yield_terminate 2 16")

    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction(f"lshift_add_imm LID UDPR_0 16 {TERM_COUNTER_OFFSET}") # write back the new pagerank value, termination counter ++
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    # tran6.writeAction(f"userctr 0 {TERM_INST_COUNTER} 5") 
    tran6.writeAction("yield_terminate 0 16")


    # read next node to update
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 fin_fetch")      # if read all nodes?
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_3 3 4294967295") 
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_4 4 4294967295") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4") # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", "send_dmlm_ld_wret UDPR_4 " + str(event_map['readNode']) + " 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2") 
    # efa.appendBlockAction("block_1", f"userctr 0 {FETCH_VERTEX_INST_COUNTER} 7")
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "fin_fetch: mov_imm2reg UDPR_10 16")
    efa.appendBlockAction("block_1", "atomic: mov_lm2reg UDPR_10 UDPR_11 4")
    efa.appendBlockAction("block_1", "addi UDPR_11 UDPR_12 1")
    efa.appendBlockAction("block_1", "cmpswp UDPR_12 UDPR_10 UDPR_11 UDPR_12")
    efa.appendBlockAction("block_1", "bne UDPR_12 UDPR_11 atomic")
    efa.appendBlockAction("block_1", "yield_terminate 4 16")

    return efa
  
if __name__=="__main__":
    efa = GeneratePagerankUniCacheEFA()
    #efa.printOut(error)
    
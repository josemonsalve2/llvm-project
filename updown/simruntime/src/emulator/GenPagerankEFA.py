from EFA import *
import traceback


def GeneratePagerankEFA():
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
    tran1.writeAction("mov_ob2reg OB_2 UDPR_0")                 # 1 UDPR_0 <- num of workers
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # 2 UDPR_1 <- num_nodes 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # 5 UDPR_11 <- base event word
    tran1.writeAction("addi LID UDPR_2 0")                   # 6 UDPR_2 <- node counter
    tran1.writeAction("tranCarry_goto block_1")

    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")            # UDPR_7 <- new weight per outgoing edge
    tran2.writeAction("ev_update_1 TS UDPR_12 " + str(event_map["readEdge"]) + " 1")
    tran2.writeAction("send_dmlm_ld UDPR_8 UDPR_12 16 1")
    tran2.writeAction("yield 4")

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction("lshift_and_imm OB_0 UDPR_3 0 63")      # 0 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("addi UDPR_3 UDPR_4 64")
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_4 UDPR_3 12")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_0 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 32")
    tran3.writeAction("lshift_and_imm OB_1 UDPR_3 0 63")      # 7 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("addi UDPR_3 UDPR_4 64")
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_4 UDPR_3 12")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_1 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 32")
    tran3.writeAction("lshift_and_imm OB_2 UDPR_3 0 63")      # 14 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("addi UDPR_3 UDPR_4 64")
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_4 UDPR_3 12")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_2 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 32")
    tran3.writeAction("lshift_and_imm OB_3 UDPR_3 0 63")      # 21 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("addi UDPR_3 UDPR_4 64")
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_4 UDPR_3 12")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_3 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 32")
    tran3.writeAction("lshift_and_imm UDPR_8 UDPR_10 2 4294967295")
    tran3.writeAction("ev_update_1 TS UDPR_12 " + str(event_map["readEdge"]) + " 1")
    tran3.writeAction("send_dmlm_ld UDPR_10 UDPR_12 16 1")
    tran3.writeAction("yield 4")

    # finish read all edges
    tran3.writeAction("tranCarry_goto block_1")                  # 32 go to fetch next node


    # how many time to enroll it
    # macro for fetching nodes/edges from DRAM: parameters include number of elements, base address, a range of free registers
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    tran4.writeAction("lshift_and_imm OB_0 UDPR_3 3 2097144")  # 2 UDPR_3 <- key to hashmap
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("beq UDPR_4 OB_0 10")
    tran4.writeAction("beq UDPR_4 4294967295 17")
    tran4.writeAction("beq UDPR_4 UDPR_4 17")
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 0 63")
    tran4.writeAction("send4_wcont EQT UDPR_5 EQT OB_0 OB_1")
    tran4.writeAction("yield 2")

    tran4.writeAction("addi UDPR_3 UDPR_3 4")                  # 10
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")
    tran4.writeAction("yield 2") 

    tran4.writeAction("mov_reg2lm OB_0 UDPR_3 4")              # 17
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_4 3 4294967295")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction("ev_update_1 TS UDPR_5 " + str(event_map['rd_return']) + " 1")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        # read current rank value from DRAM
    tran4.writeAction("mov_imm2reg UDPR_15 0")
    tran4.writeAction("yield 2") 

    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    tran5.writeAction("lshift_and_imm OB_1 UDPR_3 3 2097144")   # UDPR_3 <- key to hashmap
    tran5.writeAction("mov_imm2reg UDPR_6 -1")
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")
    # tran5.writeAction("mov_imm2reg UDPR_6 0")
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")

    tran5.writeAction("ev_update_1 EQT UDPR_5 " + str(event_map['store_ack']) +" 1")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")
    tran5.writeAction("addi UDPR_15 UDPR_15 1")
    tran5.writeAction("yield 1")

    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction("subi UDPR_15 UDPR_15 1")
    tran6.writeAction("beq UDPR_15 0 3")
    tran6.writeAction("yield_terminate 0 16")

    tran6.writeAction("mov_imm2reg UDPR_10 524288")             # 3
    tran6.writeAction("mov_lm2reg UDPR_10 UDPR_11 4")
    tran6.writeAction("blt UDPR_11 64 7")
    tran6.writeAction("send_top UDPR_12 4")
    tran6.writeAction("yield_terminate 0 16")


    # read next node to update
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 7")      # if read all nodes?
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_3 3 4294967295") 
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_4 4 4294967295") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4") # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", "send_dmlm_ld_wret UDPR_4 " + str(event_map['readNode']) + " 16 0")
    efa.appendBlockAction("block_1", "addi UDPR_2 UDPR_2 64") 
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "mov_imm2reg UDPR_10 524288")
    efa.appendBlockAction("block_1", "mov_lm2reg UDPR_10 UDPR_11 4")
    efa.appendBlockAction("block_1", "addi UDPR_11 UDPR_12 1")
    efa.appendBlockAction("block_1", "cmpswp UDPR_12 UDPR_10 UDPR_11 UDPR_12")
    efa.appendBlockAction("block_1", "bne UDPR_12 UDPR_11 9")
    efa.appendBlockAction("block_1", "yield_terminate 4 16")

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

def GeneratePagerankConfEFA():
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
    tran1.writeAction("mov_ob2reg OB_2 UDPR_0")                 # 1 UDPR_0 <- lane id
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # 2 UDPR_1 <- num_nodes 
    tran1.writeAction("mov_imm2reg UDPR_11 0")                  # 5 UDPR_11 <- base event word
    tran1.writeAction("addi UDPR_0 UDPR_2 0")                   # 6 UDPR_2 <- node counter
    tran1.writeAction("tranCarry_goto block_1")

    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2reg OB_1 UDPR_6")                 # UDPR_6 <- old weight
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div UDPR_6 UDPR_5 UDPR_7")            # UDPR_7 <- new weight per outgoing edge
    tran2.writeAction("ev_update_1 TS UDPR_12 " + str(event_map["readEdge"]) + " 1")
    tran2.writeAction("send_dmlm_ld UDPR_8 UDPR_12 16 1")
    tran2.writeAction("yield 4")

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction("mov_ob2reg OB_0 UDPR_9")                 # 0 UDPR_9 <- end vertex id
    tran3.writeAction("jmp 7")
    tran3.writeAction("mov_ob2reg OB_1 UDPR_9")
    tran3.writeAction("jmp 7")
    tran3.writeAction("mov_ob2reg OB_2 UDPR_9")
    tran3.writeAction("jmp 7")
    tran3.writeAction("mov_ob2reg OB_3 UDPR_9")
    tran3.writeAction("lshift_and_imm UDPR_9 UDPR_3 0 63")      # 7 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("addi UDPR_3 UDPR_4 64")
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_4 UDPR_3 12")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 UDPR_9 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 21")
    tran3.writeAction("beq UDPR_9 OB_0 2")
    tran3.writeAction("beq UDPR_9 OB_1 4")
    tran3.writeAction("beq UDPR_9 OB_2 6")
    tran3.writeAction("lshift_and_imm UDPR_8 UDPR_10 2 4294967295")
    tran3.writeAction("ev_update_1 TS UDPR_12 " + str(event_map["readEdge"]) + " 1")
    tran3.writeAction("send_dmlm_ld UDPR_10 UDPR_12 16 1")
    tran3.writeAction("yield 4")

    # finish read all edges
    tran3.writeAction("tranCarry_goto block_1")                  # 21 go to fetch next node

    # try fetch more edges at a time

    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    tran4.writeAction("mov_ob2reg OB_0 UDPR_0")                  # 0 UDPR_0 <- vertex id to update
    tran4.writeAction("mov_ob2reg OB_1 UDPR_1")                  # 1 UDPR_1 <- weight to be added 
    # tran4.writeAction("lshift_and_imm UDPR_0 UDPR_2 0 63")
    tran4.writeAction("lshift_and_imm UDPR_0 UDPR_3 3 2097144")  # 2 UDPR_3 <- key to hashmap
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("beq UDPR_4 UDPR_0 12")
    tran4.writeAction("beq UDPR_4 4294967295 19")
    tran4.writeAction("beq UDPR_4 UDPR_4 19")
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")
    tran4.writeAction("lshift_and_imm UDPR_0 UDPR_5 0 63")
    tran4.writeAction("send4_wcont EQT UDPR_5 EQT UDPR_0 UDPR_1")
    tran4.writeAction("yield 2") 

    tran4.writeAction("addi UDPR_3 UDPR_3 4")                    # 12
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 UDPR_1 UDPR_4")
    # tran4.writeAction("mov_imm2reg UDPR_5 0")
    # tran4.writeAction("fp_add UDPR_4 UDPR_5 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")
    tran4.writeAction("yield 2") 

    tran4.writeAction("mov_reg2lm UDPR_0 UDPR_3 4")              # 19
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm UDPR_1 UDPR_3 4")
    tran4.writeAction("lshift_and_imm UDPR_0 UDPR_4 3 4294967295")
    tran4.writeAction("lshift_and_imm UDPR_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction("ev_update_1 TS UDPR_5 " + str(event_map['rd_return']) + " 1")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0") # 8 read current rank value from DRAM
    tran4.writeAction("mov_imm2reg UDPR_15 0")
    tran4.writeAction("yield 2") 

    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    tran5.writeAction("mov_ob2reg OB_0 UDPR_1")
    tran5.writeAction("mov_ob2reg OB_1 UDPR_0")
    tran5.writeAction("lshift_and_imm UDPR_0 UDPR_3 3 2097144")   # UDPR_3 <- key to hashmap
    tran5.writeAction("mov_imm2reg UDPR_6 -1")
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")
    # tran5.writeAction("mov_imm2reg UDPR_6 0")
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("fp_add UDPR_1 UDPR_2 UDPR_2")

    tran5.writeAction("ev_update_1 EQT UDPR_5 " + str(event_map['store_ack']) +" 1")
    tran5.writeAction("lshift_and_imm UDPR_0 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm UDPR_0 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")
    tran5.writeAction("addi UDPR_15 UDPR_15 1")
    tran5.writeAction("yield 1")

    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction("subi UDPR_15 UDPR_15 1")
    tran6.writeAction("beq UDPR_15 0 3")
    tran6.writeAction("yield_terminate 0 16")

    tran6.writeAction("mov_imm2reg UDPR_10 524288")             # 3
    tran6.writeAction("mov_lm2reg UDPR_10 UDPR_11 4")
    tran6.writeAction("blt UDPR_11 64 7")
    tran6.writeAction("send_top UDPR_12 4")
    tran6.writeAction("yield_terminate 0 16")


    # read next node to update
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 7")      # if read all nodes?
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_3 3 4294967295") 
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_4 4 4294967295") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4") # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", "send_dmlm_ld_wret UDPR_4 " + str(event_map['readNode']) + " 16 0")
    efa.appendBlockAction("block_1", "addi UDPR_2 UDPR_2 64") 
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "mov_imm2reg UDPR_10 524288")
    efa.appendBlockAction("block_1", "mov_lm2reg UDPR_10 UDPR_11 4")
    efa.appendBlockAction("block_1", "addi UDPR_11 UDPR_12 1")
    efa.appendBlockAction("block_1", "cmpswp UDPR_12 UDPR_10 UDPR_11 UDPR_12")
    efa.appendBlockAction("block_1", "bne UDPR_12 UDPR_11 9")
    efa.appendBlockAction("block_1", "yield_terminate 4 16")

    return efa

def GeneratePagerankLMConfEFA():
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
    tran1.writeAction("addi UDPR_0 UDPR_2 0")                   # UDPR_2 <- node counter
    tran1.writeAction("tranCarry_goto block_1")

    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")             # UDPR_7 <- new weight per outgoing edge
    tran2.writeAction("ev_update_1 TS UDPR_12 " + str(event_map["readEdge"]) + " 1")
    tran2.writeAction("send_dmlm_ld_wret UDPR_8 " + str(event_map["readEdge"]) + " 16 1")
    tran2.writeAction("yield 4")

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    # tran3.writeAction("lshift_and_imm OB_0 UDPR_3 0 63")      # 1 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("bitwise_and OB_0 UDPR_0 UDPR_3")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_0 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 #25")
    # tran3.writeAction("lshift_and_imm OB_1 UDPR_3 0 63")      # 6 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("bitwise_and OB_0 UDPR_0 UDPR_3")
    # tran3.writeAction("addi UDPR_3 UDPR_4 64")
    # tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_1 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 #25")
    # tran3.writeAction("lshift_and_imm OB_2 UDPR_3 0 63")      # 11 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("bitwise_and OB_0 UDPR_0 UDPR_3")
    # tran3.writeAction("addi UDPR_3 UDPR_4 64")
    # tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_2 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 #25")
    # tran3.writeAction("lshift_and_imm OB_3 UDPR_3 0 63")      # 16 UDPR_3 <- and with mask to retrieve lane id
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
    tran4.writeAction("beq UDPR_4 OB_0 #13")                     # 6 hit
    tran4.writeAction("bgt UDPR_4 4294967294 #18")                   # 7 miss
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")
    tran4.writeAction("ev_update_2 UDPR_12 " + str(event_map['update']) +" 255 5")
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("addi UDPR_3 UDPR_3 4")                  # 13
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("mov_reg2lm OB_0 UDPR_3 4")              # 18
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_4 3 4294967295")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction("ev_update_2 UDPR_5 " + str(event_map['rd_return']) + " 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        # read current pagerank value from DRAM
    # tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    # tran4.writeAction("addi UDPR_0 UDPR_0 16376")
    # tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    # tran4.writeAction("addi UDPR_7 UDPR_7 1")
    # tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    # # tran4.writeAction("mov_imm2reg UDPR_15 0")
    # tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    # tran4.writeAction("addi UDPR_0 UDPR_0 16376")
    # tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    # tran4.writeAction("addi UDPR_7 UDPR_7 1")
    # tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
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
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")

    tran5.writeAction("ev_update_2 UDPR_5 " + str(event_map['store_ack']) +" 255 5")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    tran5.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran5.writeAction("addi UDPR_0 UDPR_0 16376")
    tran5.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran5.writeAction("addi UDPR_7 UDPR_7 1")
    tran5.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran5.writeAction("yield_terminate 2 16")

    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran6.writeAction("addi UDPR_0 UDPR_0 16376")
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("subi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("ble UDPR_1 0 #7")
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
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_0 UDPR_2") 
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "mov_imm2reg UDPR_10 16")
    efa.appendBlockAction("block_1", "mov_lm2reg UDPR_10 UDPR_11 4")
    efa.appendBlockAction("block_1", "addi UDPR_11 UDPR_12 1")
    efa.appendBlockAction("block_1", "cmpswp UDPR_12 UDPR_10 UDPR_11 UDPR_12")
    efa.appendBlockAction("block_1", "bne UDPR_12 UDPR_11 #9")
    efa.appendBlockAction("block_1", "yield_terminate 4 16")

    return efa

def GeneratePagerankLMEFA():
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
    tran1.writeAction("addi LID UDPR_2 0")                   # UDPR_2 <- node counter
    tran1.writeAction("tranCarry_goto block_1")

    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")             # UDPR_7 <- new weight per outgoing edge
    tran2.writeAction("ev_update_1 TS UDPR_12 " + str(event_map["readEdge"]) + " 1")
    tran2.writeAction("send_dmlm_ld_wret UDPR_8 " + str(event_map["readEdge"]) + " 16 1")
    tran2.writeAction("yield 4")

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    # tran3.writeAction("lshift_and_imm OB_0 UDPR_3 0 63")      # 1 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("bitwise_and OB_0 UDPR_0 UDPR_3")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_0 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 #25")
    # tran3.writeAction("lshift_and_imm OB_1 UDPR_3 0 63")      # 6 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("bitwise_and OB_0 UDPR_0 UDPR_3")
    # tran3.writeAction("addi UDPR_3 UDPR_4 64")
    # tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_1 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 #25")
    # tran3.writeAction("lshift_and_imm OB_2 UDPR_3 0 63")      # 11 UDPR_3 <- and with mask to retrieve lane id
    tran3.writeAction("bitwise_and OB_0 UDPR_0 UDPR_3")
    # tran3.writeAction("addi UDPR_3 UDPR_4 64")
    # tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
    tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_2 UDPR_7")
    tran3.writeAction("addi UDPR_8 UDPR_8 1")
    tran3.writeAction("bge UDPR_8 UDPR_5 #25")
    # tran3.writeAction("lshift_and_imm OB_3 UDPR_3 0 63")      # 16 UDPR_3 <- and with mask to retrieve lane id
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
    tran4.writeAction("beq UDPR_4 OB_0 #13")                     # 6 hit
    # tran4.writeAction("beq UDPR_4 4294967295 17")
    tran4.writeAction("beq UDPR_4 UDPR_4 #18")                   # 7 miss
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 0 63")
    tran4.writeAction("send4_wcont EQT UDPR_5 EQT OB_0 OB_1")
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("addi UDPR_3 UDPR_3 4")                  # 13
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("mov_reg2lm OB_0 UDPR_3 4")              # 18
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_4 3 4294967295")
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction("ev_update_2 UDPR_5 " + str(event_map['rd_return']) + " 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        # read current pagerank value from DRAM
    # # tran4.writeAction("mov_imm2reg UDPR_15 0")
    # tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    # tran4.writeAction("addi UDPR_0 UDPR_0 16376")
    # tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    # tran4.writeAction("addi UDPR_7 UDPR_7 1")
    # tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
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
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")

    tran5.writeAction("ev_update_2 UDPR_5 " + str(event_map['store_ack']) +" 255 5")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    tran5.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran5.writeAction("addi UDPR_0 UDPR_0 16376")
    tran5.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran5.writeAction("addi UDPR_7 UDPR_7 1")
    tran5.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran5.writeAction("yield_terminate 2 16")

    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran6.writeAction("addi UDPR_0 UDPR_0 16376")
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("subi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction("ble UDPR_1 0 #7")
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
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_0 UDPR_2") 
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "mov_imm2reg UDPR_10 16")
    efa.appendBlockAction("block_1", "mov_lm2reg UDPR_10 UDPR_11 4")
    efa.appendBlockAction("block_1", "addi UDPR_11 UDPR_12 1")
    efa.appendBlockAction("block_1", "cmpswp UDPR_12 UDPR_10 UDPR_11 UDPR_12")
    efa.appendBlockAction("block_1", "bne UDPR_12 UDPR_11 #9")
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
    # tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    # tran4.writeAction("addi UDPR_0 UDPR_0 16376")
    # tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    # tran4.writeAction("addi UDPR_7 UDPR_7 1")
    # tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    # # tran4.writeAction("mov_imm2reg UDPR_15 0")
    # tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    # tran4.writeAction("addi UDPR_0 UDPR_0 16376")
    # tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    # tran4.writeAction("addi UDPR_7 UDPR_7 1")
    # tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
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


def GeneratePagerankInstEFA():
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

    ISSUE_COUNTER_OFFSET = 4092 << 2
    TERM_COUNTER_OFFSET = 4094 << 2 
    NEG_ONE = 4294967295
    HASH_MASK = 4095 << 3
    HASHMAP_SIZE = 4096
    HASHMAP_OFFSET = HASHMAP_SIZE << 2
    BATCH_SIZE = 16

    EDGE_FETCH_INST_COUNTER = 1
    HASHMAP_INST_COUNTER = 5
    TERM_INST_COUNTER = 6
    FETCH_VERTEX_INST_COUNTER = 7

    # counter 2 number of hashmap collision
    # counter 3 number of hashmap hit
    # counter 4 numberof hashmap insertion

    '''
    Initialize the scratchpad memory (metadata, hashmap)
    Operands:
        OB_0_1  vertex array (graph) base address in DRAM
        OB_2    number of workers 
        OB_3    number of vertices of the input graph
    '''
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init'])
    tran1.writeAction("mov_ob2ear OB_0_1 EAR_0")                # 0 EAR_0 <- vertex arrary 
    tran1.writeAction("subi OB_2 UDPR_0 1")                     # 1 UDPR_0 <- num of workers - 1
    tran1.writeAction("mov_ob2reg OB_3 UDPR_1")                 # 2 UDPR_1 <- num_vertex 
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
    tran1.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 4") 
    tran1.writeAction("init_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 3") 
    tran1.writeAction("blt UDPR_2 UDPR_4 init_loop")
    tran1.writeAction("addi LID UDPR_2 0")                      # UDPR_2 <- number of fetched vertex 
    tran1.writeAction("lshift_and_imm LID UDPR_14 16 4294967295")
    tran1.writeAction(f"addi UDPR_14 UDPR_14 {ISSUE_COUNTER_OFFSET}")
    tran1.writeAction("mov_imm2reg UDPR_15 0")
    tran1.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran1.writeAction(f"userctr 0 {TERM_INST_COUNTER} 4") 
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13") 
    tran1.writeAction("tranCarry_goto block_1")

    '''
    Process the source vertex and fetch 16 edges from the edge list in DRAM
    Operands:
        OB_0    degree / number of neighbors
        OB_1    old pagerank value
        OB_2_3  edge list base address in the DRAM
    '''
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 next_node")                   # 0 degree skip
    # tran2.writeAction("bgt OB_0 275 next_node")                 # skip top .5 present
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- weight per outgoing edge
    tran2.writeAction(f"send_dmlm_ld_wret UDPR_8 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran2.writeAction("lshift_and_imm LID UDPR_14 16 4294967295")
    tran2.writeAction(f"addi UDPR_14 UDPR_14 {ISSUE_COUNTER_OFFSET}")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 UDPR_5 UDPR_15")             # add v's degree to the number of edges issued 
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran2.writeAction(f"userctr 0 {TERM_INST_COUNTER} 5") 
    tran2.writeAction(f"userctr 0 {FETCH_VERTEX_INST_COUNTER} 7")
    tran2.writeAction("yield 4")

    tran2.writeAction("next_node: tranCarry_goto block_1")                 # 14 skip if degree==0

    '''
    Send update to the destination vertex for each edge and fetch the next 16 edges from DRAM
    Operands:
        OB_[0-15]   destination vertex id for an edge 
    '''
    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['readEdge'])
    tran3.writeAction("ev_update_2 UDPR_11 " + str(event_map['update']) +" 255 5")
    for k in range(BATCH_SIZE):
        tran3.writeAction(f"bitwise_and OB_{k} UDPR_0 UDPR_3")
        tran3.writeAction("ev_update_reg_2 UDPR_11 UDPR_11 UDPR_3 UDPR_3 8")
        tran3.writeAction("send4_wcont UDPR_11 UDPR_3 UDPR_11 OB_0 UDPR_7")
        tran3.writeAction("addi UDPR_8 UDPR_8 1")
        tran3.writeAction("bge UDPR_8 UDPR_5 end_loop")             # finish fetching all the edges in the neighbor list
        tran3.writeAction(f"userctr 0 {EDGE_FETCH_INST_COUNTER} 5")
    tran3.writeAction("lshift_and_imm UDPR_8 UDPR_10 2 4294967295")
    tran3.writeAction(f"send_dmlm_ld_wret UDPR_10 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran3.writeAction("yield 16")    

    # finish read all edges
    tran3.writeAction("end_loop: tranCarry_goto block_1")                  # 25 fetch next node


    '''
    Receive an update, if there's an on-flight read to the same vertex, merge with previous update in the scratchpad memory
    If the hashmap entry is empty, store the update in the scratchpad, and read the current up-to-date pagerank value from DRAM
    If the hashmap entry is not empty and the vertex id doesn't match, push the update to the end of the event queue (i.e. wait until the entry is freed)
    Operands:
        OB_0    vertex id
        OB_1    weight passed from that edge (i.e. to be added)
    '''
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    # tran4.writeAction(f"perflog 0 {PerfLogPayload.UD_ACTION_STATS.value} {PerfLogPayload.UD_CYCLE_STATS.value} {PerfLogPayload.UD_QUEUE_STATS.value}")
    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # 0 UDPR_0 <- lane bank base
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                  # 1 EAR_0 <- addr of vertax array base in DRAM
    tran4.writeAction(f"addi UDPR_0 UDPR_0 {HASHMAP_OFFSET}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_3 3 {HASH_MASK}")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # 4 UDPR_3 <- hashmap entry addr
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 5") 
    tran4.writeAction("beq UDPR_4 OB_0 hit")                        # 6 hit
    tran4.writeAction(f"bge UDPR_4 {NEG_ONE} empty_entry")          # 7 entry is empty
    tran4.writeAction(f"ev_update_2 UDPR_12 {event_map['update']} 255 5")
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    tran4.writeAction("userctr 0 2 1")                              # num of hashmap collision ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("hit: addi UDPR_3 UDPR_3 4")                  # 11 hit and combine
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")

    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # update merged, termination counter ++
    tran4.writeAction(f"addi UDPR_0 UDPR_0 {TERM_COUNTER_OFFSET}")
    tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran4.writeAction("addi UDPR_7 UDPR_7 1")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran4.writeAction("userctr 0 3 1")                              # num of hashmap hit ++
    tran4.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 3") 
    tran4.writeAction(f"userctr 0 {TERM_INST_COUNTER} 5") 
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("empty_entry: mov_reg2lm OB_0 UDPR_3 4")      # insert the update to hashmap
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")   
    tran4.writeAction("lshift_and_imm OB_0 UDPR_4 3 4294967295")    # fetch the old pagerank value from DRAM
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['rd_return']} 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        
    tran4.writeAction("userctr 0 4 1")                              # num of hashmap insert ++
    tran4.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 3") 
    tran4.writeAction("yield_terminate 2 16") 

    '''
    Receive the pagerank value read from the DRAM, apply the (accumulated) updates and store it back to the DRAM
    Operands:
        OB_0    pagerank value to be updated
        OB_1    vertex id
    '''
    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    # tran5.writeAction(f"perflog 0 {PerfLogPayload.UD_ACTION_STATS.value} {PerfLogPayload.UD_QUEUE_STATS.value}")
    tran5.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # 0 UDPR_0 <- lane bank base
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                  # 1 EAR_0 <- vertax array base in DRAM
    tran5.writeAction(f"addi UDPR_0 UDPR_0 {HASHMAP_OFFSET}")
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_3 3 {HASH_MASK}")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # 4 UDPR_3 <- hashmap entry addr
    tran5.writeAction("mov_imm2reg UDPR_6 -1")                      # free the hashmap entry
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_2 4")                 
    tran5.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 8") 
    tran5.writeAction("fp_add OB_0 UDPR_2 UDPR_2")                  # apply the cumulated updates

    tran5.writeAction(f"ev_update_2 UDPR_5 {event_map['store_ack']} 255 5")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 0")

    tran5.writeAction("yield_terminate 2 16")

    '''
    Acknowledge the store
    Operands:
    '''
    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran6.writeAction(f"addi UDPR_0 UDPR_0 {TERM_COUNTER_OFFSET}")  # write back the new pagerank value, termination counter ++
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction(f"userctr 0 {TERM_INST_COUNTER} 5") 
    tran6.writeAction("yield_terminate 0 16")


    # read next node to update
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 fin_fetch")      # if read all nodes?
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_3 3 4294967295") 
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_4 4 4294967295") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4") # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", "send_dmlm_ld_wret UDPR_4 " + str(event_map['readNode']) + " 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2") 
    efa.appendBlockAction("block_1", f"userctr 0 {FETCH_VERTEX_INST_COUNTER} 7")
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "fin_fetch: yield_terminate 4 16")

    return efa

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

    ISSUE_COUNTER_OFFSET = 4092 << 2
    TERM_COUNTER_OFFSET = 4094 << 2 
    NEG_ONE = 4294967295
    HASH_MASK = 4095 << 3
    HASHMAP_SIZE = 4096
    HASHMAP_OFFSET = HASHMAP_SIZE << 2
    BATCH_SIZE = 16
    ASSOCIATE_CACHE_OFFSET = 128
    ASSOCIATE_CACHE_SIZE = 32

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
    tran1.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 4") 
    tran1.writeAction("init_hm_loop: mov_reg2lm UDPR_3 UDPR_2 4")
    tran1.writeAction("addi UDPR_2 UDPR_2 8")
    tran1.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 3") 
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
    tran1.writeAction(f"userctr 0 {TERM_INST_COUNTER} 4") 
    tran1.writeAction("mov_ob2reg OB_2 UDPR_13") 
    tran1.writeAction("tranCarry_goto block_1")

    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['readNode'])
    tran2.writeAction("beq OB_0 0 next_node")                   # 0 degree skip
    tran2.writeAction("mov_ob2reg OB_0 UDPR_5")                 # UDPR_5 <- degree
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                # EAR_1 <- edge array base address
    tran2.writeAction("mov_imm2reg UDPR_8 0")                   # UDPR_8 <- edge array offset
    tran2.writeAction("fp_div OB_1 UDPR_5 UDPR_7")              # UDPR_7 <- new weight per outgoing edge
    tran2.writeAction(f"send_dmlm_ld_wret UDPR_8 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran2.writeAction("lshift_and_imm LID UDPR_14 16 4294967295")
    tran2.writeAction(f"addi UDPR_14 UDPR_14 {ISSUE_COUNTER_OFFSET}")
    tran2.writeAction("mov_lm2reg UDPR_14 UDPR_15 4")
    tran2.writeAction("add UDPR_15 UDPR_5 UDPR_15")             # add v's degree to the number of edges issued 
    tran2.writeAction("mov_reg2lm UDPR_15 UDPR_14 4")
    tran2.writeAction(f"userctr 0 {TERM_INST_COUNTER} 5") 
    tran2.writeAction(f"userctr 0 {FETCH_VERTEX_INST_COUNTER} 7")
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
        tran3.writeAction(f"userctr 0 {EDGE_FETCH_INST_COUNTER} 5")
    tran3.writeAction("lshift_and_imm UDPR_8 UDPR_10 2 4294967295")
    tran3.writeAction(f"send_dmlm_ld_wret UDPR_10 {event_map['readEdge']} {BATCH_SIZE<<2} 1")
    tran3.writeAction("yield 16")    

    # finish read all edges
    tran3.writeAction("end_loop: tranCarry_goto block_1")                  # 25 fetch next node


    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['update'])
    # tran4.writeAction(f"perflog 0 {PerfLogPayload.UD_ACTION_STATS.value} {PerfLogPayload.UD_CYCLE_STATS.value} {PerfLogPayload.UD_QUEUE_STATS.value}")
    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # 0 UDPR_0 <- lane bank base
    tran4.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                  # 1 EAR_0 <- addr of vertax array base in DRAM
    tran4.writeAction(f"addi UDPR_0 UDPR_0 {HASHMAP_OFFSET}")
    tran4.writeAction(f"lshift_and_imm OB_0 UDPR_3 3 {HASH_MASK}")
    tran4.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # 4 UDPR_3 <- hashmap entry addr
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_6 4")                 # UDPR_6 <- current hashmap entry value
    tran4.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 5") 
    tran4.writeAction("beq UDPR_6 OB_0 hit")                        # hit hash map

    tran4.writeAction(f"lshift_add_imm LID UDPR_2 16 {ASSOCIATE_CACHE_OFFSET}")    # check associate cache
    tran4.writeAction(f"addi UDPR_2 UDPR_5 {ASSOCIATE_CACHE_SIZE * 8}")     # UDPR_5 <- associate cache end addr
    tran4.writeAction("cache_loop: mov_lm2reg UDPR_2 UDPR_4 4 ")
    tran4.writeAction("beq UDPR_4 OB_0 cache_hit")                        # hit associate cache
    tran4.writeAction("addi UDPR_2 UDPR_2 8")
    tran4.writeAction("blt UDPR_2 UDPR_5 cache_loop")

    tran4.writeAction(f"bge UDPR_6 {NEG_ONE} empty_entry")          # hashmap entry is empty?
    tran4.writeAction(f"lshift_add_imm LID UDPR_2 16 {ASSOCIATE_CACHE_OFFSET}")    # check associate cache
    tran4.writeAction("find_empty_loop: mov_lm2reg UDPR_2 UDPR_4 4 ")
    tran4.writeAction(f"bge UDPR_4 {NEG_ONE} empty_cache_entry")
    tran4.writeAction("addi UDPR_2 UDPR_2 8")
    tran4.writeAction("blt UDPR_2 UDPR_5 cache_loop")

    tran4.writeAction(f"ev_update_2 UDPR_12 {event_map['update']} 255 5")
    tran4.writeAction("send4_wcont UDPR_12 LID UDPR_12 OB_0 OB_1")
    tran4.writeAction("userctr 0 2 1")                              # num of hashmap collision ++
    tran4.writeAction("yield_terminate 2 16")

    tran4.writeAction("cache_hit: addi UDPR_2 UDPR_3 0")
    tran4.writeAction("hit: addi UDPR_3 UDPR_3 4")                  # hit and combine
    tran4.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran4.writeAction("fp_add UDPR_4 OB_1 UDPR_4")
    tran4.writeAction("mov_reg2lm UDPR_4 UDPR_3 4")

    tran4.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # update merged, termination counter ++
    tran4.writeAction(f"addi UDPR_0 UDPR_0 {TERM_COUNTER_OFFSET}")
    tran4.writeAction("mov_lm2reg UDPR_0 UDPR_7 4")
    tran4.writeAction("addi UDPR_7 UDPR_7 1")
    tran4.writeAction("mov_reg2lm UDPR_7 UDPR_0 4")
    tran4.writeAction("userctr 0 3 1")                              # num of hashmap hit ++
    tran4.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 3") 
    tran4.writeAction(f"userctr 0 {TERM_INST_COUNTER} 5") 
    tran4.writeAction("yield_terminate 2 16") 

    tran4.writeAction("empty_cache_entry: addi UDPR_2 UDPR_3 0")
    tran4.writeAction("empty_entry: mov_reg2lm OB_0 UDPR_3 4")      # insert the update to hashmap
    tran4.writeAction("addi UDPR_3 UDPR_3 4")
    tran4.writeAction("mov_reg2lm OB_1 UDPR_3 4")   
    tran4.writeAction("lshift_and_imm OB_0 UDPR_4 3 4294967295")    # fetch the old pagerank value from DRAM
    tran4.writeAction("lshift_and_imm OB_0 UDPR_5 4 4294967295")
    tran4.writeAction("add UDPR_5 UDPR_4 UDPR_4")
    tran4.writeAction("addi UDPR_4 UDPR_4 16")
    tran4.writeAction(f"ev_update_2 UDPR_5 {event_map['rd_return']} 255 5")
    tran4.writeAction("send_dmlm_ld UDPR_4 UDPR_5 8 0")        
    tran4.writeAction("userctr 0 4 1")                              # num of hashmap insert ++
    tran4.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 3") 
    tran4.writeAction("yield_terminate 2 16") 

    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['rd_return'])
    # tran5.writeAction(f"perflog 0 {PerfLogPayload.UD_ACTION_STATS.value} {PerfLogPayload.UD_QUEUE_STATS.value}")
    tran5.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")    # 0 UDPR_0 <- lane bank base
    tran5.writeAction("mov_lm2ear UDPR_0 EAR_0 8")                  # 1 EAR_0 <- vertax array base in DRAM
    tran5.writeAction(f"addi UDPR_0 UDPR_0 {HASHMAP_OFFSET}")
    tran5.writeAction(f"lshift_and_imm OB_1 UDPR_3 3 {HASH_MASK}")
    tran5.writeAction("add UDPR_0 UDPR_3 UDPR_3")                   # 4 UDPR_3 <- hashmap entry addr
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
    tran5.writeAction("beq UDPR_4 OB_1 entry_match")                # entry match the vertex id read from DRAM
    tran5.writeAction(f"lshift_add_imm LID UDPR_3 16 {ASSOCIATE_CACHE_OFFSET}")
    tran5.writeAction(f"addi UDPR_3 UDPR_5 {ASSOCIATE_CACHE_SIZE * 8}")     # UDPR_5 <- associate cache end addr
    tran5.writeAction("find_empty_loop: mov_lm2reg UDPR_3 UDPR_4 4 ")
    tran5.writeAction(f"beq UDPR_4 OB_1 entry_match")               # entry match the vertex id read from DRAM
    tran5.writeAction("addi UDPR_3 UDPR_3 8")
    tran5.writeAction("blt UDPR_3 UDPR_5 find_empty_loop")

    tran5.writeAction(f"ev_update_2 UDPR_10 {event_map['error']} 255 5")    # miss in both hashmap and associate cache, should never reach here
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_10 UDPR_10 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_10 OB_0 0")
    tran5.writeAction("yield_terminate 2 16")

    tran5.writeAction("entry_match: mov_imm2reg UDPR_6 -1")                      # free the hashmap entry
    tran5.writeAction("mov_reg2lm UDPR_6 UDPR_3 4")
    tran5.writeAction("addi UDPR_3 UDPR_3 4")
    tran5.writeAction("mov_lm2reg UDPR_3 UDPR_7 4")                 # UDPR_7 <- accumulated pagerank values
    tran5.writeAction(f"userctr 0 {HASHMAP_INST_COUNTER} 8") 
    tran5.writeAction("fp_add OB_0 UDPR_7 UDPR_7")                  # apply the accumulated updates

    tran5.writeAction(f"ev_update_2 UDPR_10 {event_map['store_ack']} 255 5")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_4 3 4294967295")
    tran5.writeAction("lshift_and_imm OB_1 UDPR_6 4 4294967295")
    tran5.writeAction("add UDPR_4 UDPR_6 UDPR_4")
    tran5.writeAction("addi UDPR_4 UDPR_4 16")
    tran5.writeAction("ev_update_reg_2 UDPR_10 UDPR_10 LID LID 8")
    tran5.writeAction("send4_dmlm UDPR_4 UDPR_10 UDPR_7 0")

    tran5.writeAction("yield_terminate 2 16")

    tran6 = state0.writeTransition("eventCarry", state0, state0, event_map['store_ack'])
    tran6.writeAction("lshift_and_imm LID UDPR_0 16 4294967295")
    tran6.writeAction(f"addi UDPR_0 UDPR_0 {TERM_COUNTER_OFFSET}")  # write back the new pagerank value, termination counter ++
    tran6.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran6.writeAction("addi UDPR_1 UDPR_1 1")
    tran6.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran6.writeAction(f"userctr 0 {TERM_INST_COUNTER} 5") 
    tran6.writeAction("yield_terminate 0 16")


    # read next node to update
    efa.appendBlockAction("block_1", "bge UDPR_2 UDPR_1 fin_fetch")      # if read all nodes?
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_3 3 4294967295") 
    efa.appendBlockAction("block_1", "lshift_and_imm UDPR_2 UDPR_4 4 4294967295") 
    efa.appendBlockAction("block_1", "add UDPR_3 UDPR_4 UDPR_4") # UDPR_4 <- node addr
    efa.appendBlockAction("block_1", "send_dmlm_ld_wret UDPR_4 " + str(event_map['readNode']) + " 16 0")
    efa.appendBlockAction("block_1", "add UDPR_2 UDPR_13 UDPR_2") 
    efa.appendBlockAction("block_1", f"userctr 0 {FETCH_VERTEX_INST_COUNTER} 7")
    efa.appendBlockAction("block_1", "yield 5")  

    # finish fetching all nodes
    efa.appendBlockAction("block_1", "fin_fetch: yield_terminate 4 16")

    return efa
if __name__=="__main__":
    efa = GenerateSsspEFA_singlestream()
    #efa.printOut(error)
    
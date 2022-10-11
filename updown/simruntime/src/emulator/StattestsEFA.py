from EFA import *

def ArrayWriteBWTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'write_arr':0,
        'ack_ret':1,
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['write_arr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    tran0.writeAction("mov_ob2ear OB_1_2 EAR_0")                         #1 v1 - LM base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #2 TC / iterator
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #3 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["read_ret"])) #4  #5 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_13 -1" ) # Lane 1                #5

    tran0.writeAction("ble UDPR_1 UDPR_3 #10")                          #6  l1
    tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " +blkbytes + " r 2"       #7  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #8
    tran0.writeAction(tr_str)               
    tran0.writeAction("bgt UDPR_1 UDPR_3 #7")                          #9 l1
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #10 y1
    tran0.writeAction("yield 2")                                        #11

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['ack_ret'])
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #0
    tran1.writeAction(tr_str)               
    tran1.writeAction("ble UDPR_1 UDPR_3 #3")                           #1
    tran1.writeAction("yield 2")                                        #2
    tran1.writeAction("yield_terminate 4")                              #3

    return efa

def ArrayReadBWTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'read_arr':0,
        'arr_ret':1,
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['read_arr'])
    #tran0.writeAction("lshift_and_imm OB_0 UDPR_1 0 4294967295")        #0 v1 size in bytes
    tran0.writeAction("mov_ob2reg OB_0 UDPR_2")        #0 v1 size in bytes
    tran0.writeAction("mov_ob2reg OB_1 UDPR_1")        #1 v1 size in bytes
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_0")                        #2 v1 - LM base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #3 TC / iterator
    tran0.writeAction("rshift_and_imm TS UDPR_4 0 16711680")            #4 Extract TID for event_word
    tran0.writeAction("addi UDPR_4 UDPR_4 " + str(event_map["arr_ret"])) #5  #5 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_5 -1" ) # Lane 1                #6

    tran0.writeAction("ble UDPR_1 UDPR_3 #11")                          #7  l1
    tr_str = "send_old UDPR_4 UDPR_5 UDPR_3 " +blkbytes + " r 1"       #8  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #9
    tran0.writeAction(tr_str)               
    tran0.writeAction("bgt UDPR_1 UDPR_3 #8")                           #10 l1
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #11 y1
    tran0.writeAction("yield 2")                                        #12

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['arr_ret'])
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #0
    tran1.writeAction(tr_str)               
    tran1.writeAction("ble UDPR_1 UDPR_3 #3")                           #1
    tran1.writeAction("yield 2")                                        #2
    tran1.writeAction("mov_imm2reg UDPR_3 1")                    #3 Move Tri count
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")                    #4 28
    tran1.writeAction("yield_terminate 4")                              #5

    return efa

def GraphReadBWTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'vr':0,
        'nr':1,
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         #1 v1 - LM base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #2 TC / iterator
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #3 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["v1_nr"]))   #4 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_13 -1" ) # Lane 1                #5
       # Fetch v1 phase
    tran0.writeAction("ble UDPR_1 UDPR_3 #10")                          #6  l1
    tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " +blkbytes + " r 2"       #7  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #8
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #6")                                        #9
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #10 y1
    tran0.writeAction("yield 2")                                        #11

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['nr'])
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #0
    tran1.writeAction(tr_str)               
    tran1.writeAction("ble UDPR_1 UDPR_3 #3")                           #1
    tran1.writeAction("yield 2")                                        #2
    tran1.writeAction("yield_terminate 4")                              #3
    
    return efa

def MemBWTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'vr':0,
        'nr':1,
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                        #0 DRAM fetch addr
    tran0.writeAction("mov_ob2reg OB_2 UDPR_1")                        #1 # no of requests to send to memory
    tran0.writeAction("mov_ob2reg OB_3 UDPR_4")                        #2 # LM Base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                        #3 # iterator

    tran0.writeAction("ble UDPR_1 UDPR_3 #8")                          #4  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["nr"]) + " " + blkbytes + " 0"     #5  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #6
    tran0.writeAction(tr_str)
    tran0.writeAction("jmp #4")                                         #7
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #7
    tran0.writeAction("yield 2")                                        #8

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['nr'])
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           
    tran1.writeAction(tr_str)                                           #0
    tran1.writeAction("ble UDPR_1 UDPR_3 #3")                           #1
    tran1.writeAction("yield 2")                                        #2
    tran1.writeAction("mov_imm2reg UDPR_3 1")                           #3
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_4 4")                     #4
    tran1.writeAction("yield_terminate 2")                              #5

    return efa

def MemBWWriteTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'vr':0,
        'nr':1,
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                        #0 DRAM write addr
    tran0.writeAction("mov_ob2reg OB_2 UDPR_1")                        #1 # no of requests to send to memory
    tran0.writeAction("mov_ob2reg OB_3 UDPR_4")                        #2 # LM Base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                        #3 # iterator

    tran0.writeAction("ble UDPR_1 UDPR_3 #8")                          #4  l1
    tr_str = "send_dmlm_wret UDPR_3 " + str(event_map["nr"]) + " UDPR_4 " + blkbytes + " 0"     #5  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #6
    tran0.writeAction(tr_str)
    tran0.writeAction("jmp #4")                                         #7
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #7
    tran0.writeAction("yield 2")                                        #8

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['nr'])
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           
    tran1.writeAction(tr_str)                                           #0
    tran1.writeAction("ble UDPR_1 UDPR_3 #3")                           #1
    tran1.writeAction("yield 2")                                        #2
    tran1.writeAction("subi UDPR_4 UDPR_4 4")                           #3
    tran1.writeAction("mov_imm2reg UDPR_3 1")                           #4
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_4 4")                     #5
    tran1.writeAction("yield_terminate 2")                              #6

    return efa

#if __name__=="__main__":
#    #efa.printOut(error)
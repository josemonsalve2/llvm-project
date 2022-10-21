from EFA import *


def MemReadBWTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'send_reads':0,
        'read_returns':1,
    }

    blkbytes = str(blksize)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['send_reads'])
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                        #0 DRAM fetch addr
    tran0.writeAction("mov_ob2reg OB_2 UDPR_1")                         #1 # no of requests to send to memory 
    tran0.writeAction("mov_ob2reg OB_3 UDPR_4")                         #2 # LM Base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #3 # iterator

    tran0.writeAction("send_loop: ble UDPR_1 UDPR_3 reads_done")                          #4  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["read_returns"]) + " " + blkbytes + " 0"     #5  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #6
    tran0.writeAction(tr_str)
    tran0.writeAction("jmp send_loop")                                         #7
    tran0.writeAction("reads_done: mov_imm2reg UDPR_3 0")                           #7
    tran0.writeAction("yield 2")                                        #8

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['read_returns'])
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           
    tran1.writeAction(tr_str)                                           #0
    tran1.writeAction("ble UDPR_1 UDPR_3 #3")                           #1
    tran1.writeAction("yield 2")                                        #2
    tran1.writeAction("mov_imm2reg UDPR_3 1")                           #3
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_4 4")                     #4
    tran1.writeAction("yield_terminate 2")                              #5

    return efa

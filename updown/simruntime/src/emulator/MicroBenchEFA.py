from EFA import *

def EventRateTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'launch_events':0,
        'process_events':1,
        'terminate':2,
    }

    # OB_0 number of events to launch
    # OB_1 termination counter
    # OB_2 LM base address for final status
    # Launch OB_0 events on same lane
    # Termination check is done on all lanes
    # Need to check rate + latency for these - events/sec - event latency 
    # Mode - Interleave (1), Non-Interleave (0)
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['launch_events'])
    tran0.writeAction("mov_ob2reg OB_0 UDPR_0")                             # OB_0 number of events to launch / store for termination check
    tran0.writeAction("mov_ob2reg OB_1 UDPR_4")                             # termination counter
    tran0.writeAction("mov_ob2reg OB_2 UDPR_2")                             # LM Base address
    tran0.writeAction("ev_update_2 UDPR_3 " + str(event_map['process_events']) +" 0 5") #  Mask - 0xff0000ff
    tran0.writeAction("send_loop: send4_wret UDPR_3 LID " + str(event_map["terminate"]) + " UDPR_0")
    tran0.writeAction("subi UDPR_0 UDPR_0 1")                               # Subtract event count
    tran0.writeAction("bgt UDPR_0 0 send_loop")                             # check for no of events
    tran0.writeAction("mov_imm2reg UDPR_0 0")                             # reset event count
    tran0.writeAction("yield 2")
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['process_events'])
    tran2.writeAction("add UDPR_0 OB_0 UDPR_0")                          # UDPR_1 temp counter to count events
    tran2.writeAction("beq UDPR_4 UDPR_0 terminate")
    tran2.writeAction("yield 1")
    tran2.writeAction("terminate: mov_imm2reg UDPR_3 -1")                          # -1 is terminating check from top
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_2 4")
    tran2.writeAction("yield_terminate 1")
    
    return efa

def EventRateMasterTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'launch_threads':0,
        'init':1,
        'process_events':2,
        'terminate':3,
    }

    # OB_0 number of events to launch
    # OB_1 number of lanes in system
    # OB_2 termination counter (based on no of lanes)
    # Launch OB_0 events on all lanes in the system 
    # Lane 0 acts like the master that terminates all the events 
    # Termination check is only done on one lane
    # Need to check rate + latency for these - events/sec - event latency 
    # Mode - Interleave (1), Non-Interleave (0)
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['launch_threads'])
    tran0.writeAction("mov_ob2reg OB_0 UDPR_0")                             # OB_0 number of events to launch for termination check
    tran0.writeAction("mov_ob2reg OB_1 UDPR_2")                             # Number of lanes
    tran0.writeAction("mov_ob2reg OB_2 UDPR_4")                             # termination counter
    tran0.writeAction("mov_imm2reg UDPR_1 1")                               # assumes Lane 0 will be the master thread
    tran0.writeAction("ev_update_2 UDPR_3 " + str(event_map['init']) +" 255 5") #  Mask - 0xff0000ff 
    tran0.writeAction("send_loop: send4_wret UDPR_3 UDPR_2 " + str(event_map["process_events"]) + " UDPR_0")
    tran0.writeAction("subi UDPR_2 UDPR_2 1")                               # Subtract Lane count
    tran0.writeAction("bge UDPR_2 1 send_loop")                             # check for no of lanes
    tran0.writeAction("mov_ob2reg OB_1 UDPR_2")                             # reset event count
    tran0.writeAction("yield 2")
    
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['init'])
    tran1.writeAction("beq LID 0 yield_loop")                               # Check Lane ID, if not 0 initialize threads
    tran1.writeAction("mov_ob2reg OB_0 UDPR_0")                             # Save Event Count
    tran1.writeAction("send4_reply LID")                                    # send response with Lane Id to zero
    tran1.writeAction("yield_loop: yield 1")                                # Yield
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['process_events'])
    tran2.writeAction("bne LID 0 nonzero_sr")                               # Start of subrouting for Lane 0
    tran2.writeAction("mov_reg2reg UDPR_0 UDPR_1")                          # UDPR_1 temp counter to count events
    tran2.writeAction("ev_update_reg_imm UDPR_3 EQT 0 " + str(event_map['process_events']) +" 5") #  Mask - 0x00ff00ff Keep LID const
    tran2.writeAction("send_loop: send4_wret UDPR_3 OB_0 " + str(event_map["terminate"]) + " UDPR_1")
    tran2.writeAction("subi UDPR_1 UDPR_1 1")
    tran2.writeAction("bgt UDPR_1 0 send_loop")                             # check for no of eventsa
    tran2.writeAction("yield 2")
    tran2.writeAction("nonzero_sr: subi UDPR_0 UDPR_0 1")                   # 
    tran2.writeAction("beq UDPR_0 0 yield_term")                            # Update the count
    tran2.writeAction("yield 1")
    tran2.writeAction("yield_term: send4_reply LID")
    tran2.writeAction("yield_terminate 1")
    
    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['terminate'])
    tran3.writeAction("sub UDPR_4 OB_0 UDPR_4")                             # subtract lane ID from termination counter
    tran3.writeAction("beq UDPR_4 0 term")                                  # if n*(n+1)/2 has become zero
    tran3.writeAction("yield 1")                                
    tran3.writeAction("term: mov_imm2reg UDPR_4 -1")                         # termination status
    tran3.writeAction("mov_imm2reg UDPR_5 0")                               # Base address of bank 0
    tran3.writeAction("mov_reg2lm UDPR_4 UDPR_5 4")
    tran3.writeAction("yield_terminate 1")
    
    
    return efa

def ThreadRateTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'launch_threads':0,
        'create_threads':1,
        'terminate_threads':2,
    }

    # OB_0 number of events to launch
    # OB_1 number of lanes in system
    # Launch OB_0 events on all lanes in the system 
    # Lane 0 acts like the master that terminates all the events 
    # Termination check is only done on one lane
    # Need to check rate + latency for these - events/sec - event latency 
    # Mode - Interleave (1), Non-Interleave (0)
    mode = 1

    blkbytes = str(blksize)
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['launch_threads'])
    tran0.writeAction("mov_ob2reg OB_0 UDPR_0")                             # OB_0 number of threads to launch / store for termination check
    tran0.writeAction("mov_ob2reg OB_1 UDPR_4")                             # termination counter
    tran0.writeAction("mov_ob2reg OB_2 UDPR_2")                             # LM Base address
    tran0.writeAction("ev_update_2 UDPR_3 " + str(event_map['create_threads']) +" 255 5") #  Event_word Mask - 0x00ff00ff
    tran0.writeAction("ev_update_2 UDPR_4 " + str(event_map['terminate_threads']) +" 0 5") #  Continuation for termination (back to thread0)
    tran0.writeAction("send_loop: send4_wcont UDPR_3 LID UDPR_4 UDPR_2")    # Send address of LM offset
    tran0.writeAction("subi UDPR_0 UDPR_0 1")                               # Subtract thread count
    tran0.writeAction("bgt UDPR_0 0 send_loop")                             # check for no of threads
    tran0.writeAction("mov_imm2reg UDPR_0 0")                               # reset thread count
    tran0.writeAction("yield 2")
    
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['create_threads'])
    tran1.writeAction("mov_ob2reg OB_0 UDPR_0")
    tran1.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran1.writeAction("addi UDPR_1 UDPR_1 1")                               # UDPR_1 temp counter to count threads
    tran1.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran1.writeAction("send4_reply UDPR_1")                                 # Send back to thread 0
    tran1.writeAction("yield_terminate 2")                                  # Terminate the created thread
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['terminate_threads'])
    tran2.writeAction("mov_lm2reg UDPR_2 UDPR_1 4")
    tran2.writeAction("subi UDPR_1 UDPR_1 1")                            # UDPR_1 temp counter to count threads
    tran2.writeAction("beq UDPR_1 0 term_final")                         # UDPR_1 temp counter to count threads
    tran2.writeAction("mov_reg2lm UDPR_1 UDPR_2 4")
    tran2.writeAction("yield 2")
    tran2.writeAction("term_final: mov_imm2reg UDPR_1 -1")               # Use -1 as the final termination detection
    tran2.writeAction("mov_reg2lm UDPR_1 UDPR_2 4")
    tran2.writeAction("yield_terminate 1")
    
    return efa

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

def MemWriteBWTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'send_writes':0,
        'write_acks':1,
    }

    blkbytes = str(blksize)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['send_writes'])
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                        #0 DRAM write addr
    tran0.writeAction("mov_ob2reg OB_2 UDPR_1")                         #1 # Size of Memory to write
    tran0.writeAction("mov_ob2reg OB_3 UDPR_4")                         #2 # LM Base
    tran0.writeAction("mov_ob2reg OB_4 UDPR_5")                         #2 # LM Base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #3 # iterator

    tran0.writeAction("send_loop: ble UDPR_1 UDPR_3 writes_done")                          #4  l1
    tr_str = "send_dmlm_wret UDPR_3 " + str(event_map["write_acks"]) + " UDPR_4 " + blkbytes + " 0"     #5  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #6
    tran0.writeAction(tr_str)
    tr_str = "addi UDPR_4 UDPR_4 " + blkbytes                           #6
    tran0.writeAction(tr_str)
    tran0.writeAction("jmp send_loop")                                         #7
    tran0.writeAction("writes_done: mov_imm2reg UDPR_3 0")                           #7
    tran0.writeAction("yield 2")                                        #8

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['write_acks'])
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           
    tran1.writeAction(tr_str)                                           #0
    tran1.writeAction("ble UDPR_1 UDPR_3 #3")                           #1
    tran1.writeAction("yield 2")                                        #2
    tran1.writeAction("mov_imm2reg UDPR_3 1")                           #3
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_5 4")                     #4
    tran1.writeAction("yield_terminate 2")                              #5

    return efa


def ThreadRateMasterTest():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'launch_threads':0,
        'create_threads':1,
        'terminate_threads':2,
    }

    # OB_0 number of events to launch
    # OB_1 number of lanes in system
    # Launch OB_0 events on all lanes in the system 
    # Lane 0 acts like the master that terminates all the events 
    # Termination check is only done on one lane
    # Need to check rate + latency for these - events/sec - event latency 
    # Mode - Interleave (1), Non-Interleave (0)
    mode = 1

    blkbytes = str(blksize)
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['launch_threads'])
    tran0.writeAction("mov_ob2reg OB_0 UDPR_0")                             # OB_0 number of threads to launch / store for termination check
    tran0.writeAction("mov_ob2reg OB_1 UDPR_4")                             # termination counter
    tran0.writeAction("mov_ob2reg OB_2 UDPR_2")                             # LM Base address
    tran0.writeAction("ev_update_2 UDPR_3 " + str(event_map['create_threads']) +" 255 5") #  Event_word Mask - 0x00ff00ff
    tran0.writeAction("ev_update_2 UDPR_4 " + str(event_map['terminate_threads']) +" 0 5") #  Continuation for termination (back to thread0)
    tran0.writeAction("send_loop: send4_wcont UDPR_3 LID UDPR_4 UDPR_2")    # Send address of LM offset
    tran0.writeAction("subi UDPR_0 UDPR_0 1")                               # Subtract thread count
    tran0.writeAction("bgt UDPR_0 0 send_loop")                             # check for no of threads
    tran0.writeAction("mov_imm2reg UDPR_0 0")                               # reset thread count
    tran0.writeAction("yield 2")
    
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['create_threads'])
    tran1.writeAction("mov_ob2reg OB_0 UDPR_0")
    tran1.writeAction("mov_lm2reg UDPR_0 UDPR_1 4")
    tran1.writeAction("addi UDPR_1 UDPR_1 1")                               # UDPR_1 temp counter to count threads
    tran1.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran1.writeAction("send4_reply UDPR_1")                                 # Send back to thread 0
    tran1.writeAction("yield_terminate 2")                                  # Terminate the created thread
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['terminate_threads'])
    tran2.writeAction("mov_lm2reg UDPR_2 UDPR_1 4")
    tran2.writeAction("subi UDPR_1 UDPR_1 1")                            # UDPR_1 temp counter to count threads
    tran2.writeAction("beq UDPR_1 0 term_final")                         # UDPR_1 temp counter to count threads
    tran2.writeAction("mov_reg2lm UDPR_1 UDPR_2 4")
    tran2.writeAction("yield 2")
    tran2.writeAction("term_final: mov_imm2reg UDPR_1 -1")               # Use -1 as the final termination detection
    tran2.writeAction("mov_reg2lm UDPR_1 UDPR_2 4")
    tran2.writeAction("yield_terminate 1")
    
    return efa

#if __name__=="__main__":
#    #efa.printOut(error)
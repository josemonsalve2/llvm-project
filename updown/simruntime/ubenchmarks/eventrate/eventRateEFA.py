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

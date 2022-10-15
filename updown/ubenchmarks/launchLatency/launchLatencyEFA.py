from EFA import *

def LaunchTest():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'launch_events':0,
    }

    # OB_0 address for termination
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['launch_events'])
    tran0.writeAction("mov_ob2reg OB_0 UDPR_0")                             # OB_0 number of events to launch / store for termination check
    tran0.writeAction("mov_imm2reg UDPR_1 -1")                             # OB_0 number of events to launch / store for termination check
    tran0.writeAction("mov_reg2lm UDPR_1 UDPR_0 4")
    tran0.writeAction("yield_terminate 1")
    
    return efa
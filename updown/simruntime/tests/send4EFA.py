from EFA import *

def send4EFA():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    #Add events to dictionary 
    event_map = {
        'send4_test':0,
        'received_test':1
    }

    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['send4_test'])
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                        # DRAM dest addr
    tran0.writeAction("mov_imm2reg UDPR_0 0")                           # Offset from EAR0
    tran0.writeAction("ev_update_1 LID UDPR_1 1 1")                     # continuation to this lane
    tran0.writeAction("ev_update_1 UDPR_1 UDPR_1 0 4")                     # continuation to this lane
    tran0.writeAction(f"send4_dmlm UDPR_0 UDPR_1 OB_2 OB_3 0")
    tran0.writeAction(f"yield 4")
    

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['received_test'])
    tran1.writeAction(f"lshift_and_imm LID UDPR_1 0 {0x3F0000}") # Set address to local memory
    tran1.writeAction("mov_imm2reg UDPR_0 1")
    tran1.writeAction("mov_reg2lm UDPR_0 UDPR_1 4")
    tran1.writeAction("yield_terminate 1")
    return efa

if __name__=="__main__":
    efa = send4EFA()
    

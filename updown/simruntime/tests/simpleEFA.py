
from EFA import *

def simpleEFA():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() #tri Count State
    efa.add_state(state1)
    state2 = State() #tri Count State
    efa.add_state(state2)

    #Add events to dictionary 
    event_map = {
        'vr':0,
        'nr':1,
        'tc':2
    }
    
    tran0 = state0.writeTransition("eventCarry", state0, state1, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    tran0.writeAction("mov_ob2reg OB_2 UDPR_4")                         #1 v1 - LM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #2 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #3 v2 DRAM base
    tran0.writeAction("mov_ob2reg OB_8 UDPR_10")                        #4 v1 - LM base
    tran0.writeAction("mov_ob2reg OB_5 UDPR_12")                        #5 v1 - ID
    tran0.writeAction("mov_ob2reg OB_9 UDPR_13")                        #5 result
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #6 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #7 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #8 v2 index 
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["nr"]))     #10 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_11 2" ) # Lane 1                #11
    tran0.writeAction("send UDPR_7 UDPR_11 UDPR_3 4 r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("send UDPR_7 UDPR_11 UDPR_3 4 r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("yield 2" ) # Lane 1                #11
    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['nr'])
    tran1.writeAction("mov_ob2reg OB_0 UDPR_13")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran1.writeAction("mov_reg2lm UDPR_8 UDPR_13 4")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    #tran1.writeAction("yield_terminate 2" ) # Lane 1                #11
    return efa

if __name__=="__main__":
    efa = simpleEFA()
    #efa.printOut(error)
    

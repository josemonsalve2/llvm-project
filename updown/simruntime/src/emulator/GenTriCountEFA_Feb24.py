from EFA import *

def GenerateTriEFA():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State? 
    state0.alphabet = ['tc'] # a - #tricount, b - #neighbor-return
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    
    state1 = State() #tri Count State
    state1.alphabet = ['nr']
    efa.add_state(state1)
    tran0 = state0.writeTransition("eventCarry", state0, state1, 'vr')
    #rest of the actions
    tran0.writeAction("mov_ob2reg OB_0 UDPR_1")        #0
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_0")       #1
    tran0.writeAction("mov_ob2reg OB_4 UDPR_2")        #2
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_1")       #3
    tran0.writeAction("mov_imm2reg UDPR_3 0")          #4
    tran0.writeAction("mov_imm2reg UDPR_4 0")          #5
    tran0.writeAction("mov_imm2reg UDPR_5 0")          #6
    tran0.writeAction("mov_imm2reg UDPR_6 0")          #7
    tran0.writeAction("bne UDPR_4 0 #13") #loop        #8
    tran0.writeAction("send nr UP_0 EAR_0|UDPR_5 4 r")        #9
    tran0.writeAction("send nr UP_0 EAR_1|UDPR_6 4 r")        #10
    tran0.writeAction("jmp #17")                       #11
    tran0.writeAction("bgt UDPR_4 0 #15")              #12
    tran0.writeAction("send nr UP_0 EAR_0|UDPR_5 4 r") #l1    #13
    tran0.writeAction("jmp #17")                       #14
    tran0.writeAction("blt UDPR_4 0 #17") #l2          #15
    tran0.writeAction("send nr UP_0 EAR_1|UDPR_6 4 r")        #16
    tran0.writeAction("yield") #l3                      #17

    #neighbor result transition is back to same state
    tran1 = state1.writeTransition("eventCarry", state1, state1, 'nr')
    
    #rest of the actions
    tran1.writeAction("bne UDPR_4 0 #3")                        #0  
    tran1.writeAction("compreg_eq OB_0 OB_1 UDPR_8")            #1
    tran1.writeAction("jmp #4")                                 #2
    tran1.writeAction("compreg_eq OB_0 UDPR_7 UDPR_8") #l4      #3
    tran1.writeAction("beq UDPR_8 0 #9")                        #4
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                   #5
    tran1.writeAction("addi UDPR_5 UDPR_5 1")                   #6
    tran1.writeAction("addi UDPR_6 UDPR_6 1")                   #7
    tran1.writeAction("jmp #21")                                #8
    tran1.writeAction("bgt UDPR_8 0 #16") #l5                   #9
    tran1.writeAction("addi UDPR_5 UDPR_5 1")                   #10
    tran1.writeAction("bne UDPR_4 0 #13")                       #11
    tran1.writeAction("mov_ob2reg OB_1 UDPR_7")                 #12
    tran1.writeAction("blt UDPR_4 0 #15") #l7                   #13
    tran1.writeAction("mov_ob2reg OB_0 UDPR_7")                 #14
    tran1.writeAction("jmp #21") #l8                            #15
    tran1.writeAction("addi UDPR_6 UDPR_6 1") #l6               #16
    tran1.writeAction("bne UDPR_4 1 #19")                       #17
    tran1.writeAction("mov_ob2reg OB_0 UDPR_7")                 #18
    tran1.writeAction("bgt UDPR_4 0 #21") #l9                   #19
    tran1.writeAction("mov_ob2reg OB_0 UDPR_7")                 #20
    tran1.writeAction("mov_reg2reg UDPR_4 UDPR_8") #fn          #21
    tran1.writeAction("beq UDPR_1 UDPR_5 #25")                  #22
    tran1.writeAction("beq UDPR_2 UDPR_6 #25")                  #23
    tran1.writeAction("jmp #9")                                 #24

    tran1.writeAction("send <TOP> TOP EAR_1|UDPR_6 4 r") #l10   #25
    tran1.writeAction("yield_terminate")                        #26

    return efa

def GenerateTriEFA2():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State? 
    state0.alphabet = ['tc'] # a - #tricount, b - #neighbor-return
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    
    state1 = State() #tri Count State
    state1.alphabet = ['nr']
    efa.add_state(state1)
    tran0 = state0.writeTransition("eventCarry", state0, state1, 'vr')
    #rest of the actions
    tran0.writeAction("mov_ob2reg OB_0 UDPR_1")        #0
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_0")       #1
    tran0.writeAction("mov_ob2reg OB_4 UDPR_2")        #2
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_1")       #3
    tran0.writeAction("mov_imm2reg UDPR_3 0")          #4
    tran0.writeAction("mov_imm2reg UDPR_4 0")          #5
    tran0.writeAction("mov_imm2reg UDPR_5 0")          #6
    tran0.writeAction("mov_imm2reg UDPR_6 0")          #7
    tran0.writeAction("bne UDPR_4 0 #13") #loop        #8
    tran0.writeAction("send nr UP_0 EAR_0|UDPR_5 4 r")        #9
    tran0.writeAction("send nr UP_0 EAR_1|UDPR_6 4 r")        #10
    tran0.writeAction("jmp #17")                       #11
    tran0.writeAction("bgt UDPR_4 0 #15")              #12
    tran0.writeAction("send nr UP_0 EAR_0|UDPR_5 4 r") #l1    #13
    tran0.writeAction("jmp #17")                       #14
    tran0.writeAction("blt UDPR_4 0 #17") #l2          #15
    tran0.writeAction("send nr UP_0 EAR_1|UDPR_6 4 r")        #16
    tran0.writeAction("yield") #l3                      #17

    #neighbor result transition is back to same state
    tran1 = state1.writeTransition("eventCarry", state1, state1, 'nr')
    
    #rest of the actions
    tran1.writeAction("bne UDPR_4 0 #3")                        #0  
    tran1.writeAction("compreg OB_0 OB_1 UDPR_8")               #1
    tran1.writeAction("jmp #4")                                 #2
    tran1.writeAction("compreg OB_0 UDPR_7 UDPR_8") #l4         #3
    tran1.writeAction("bne UDPR_8 0 #9")                        #4
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                   #5
    tran1.writeAction("addi UDPR_5 UDPR_5 1")                   #6
    tran1.writeAction("addi UDPR_6 UDPR_6 1")                   #7
    tran1.writeAction("jmp #22")                                #8
    tran1.writeAction("bgt UDPR_8 0 #17") #l5                   #9
    tran1.writeAction("bgt UDPR_4 0 #15") #l5                   #10
    tran1.writeAction("addi UDPR_5 UDPR_5 1")                   #11
    tran1.writeAction("bne UDPR_4 0 #22")                       #12
    tran1.writeAction("mov_ob2reg OB_1 UDPR_7")                 #13
    tran1.writeAction("jmp #22") #l8                            #14
    tran1.writeAction("addi UDPR_6 UDPR_6 1")                   #15
    tran1.writeAction("jmp #22")                                #16
    tran1.writeAction("mov_ob2reg OB_0 UDPR_7")                 #17
    tran1.writeAction("bgt UDPR_4 0 #21") #l5                   #18
    tran1.writeAction("addi UDPR_6 UDPR_6 1") #l6               #19
    tran1.writeAction("jmp #22") #l8                            #20
    tran1.writeAction("addi UDPR_5 UDPR_5 1") #l6               #21
    tran1.writeAction("mov_reg2reg UDPR_4 UDPR_8") #fn          #22
    tran1.writeAction("beq UDPR_1 UDPR_5 #26")                  #23
    tran1.writeAction("beq UDPR_2 UDPR_6 #26")                  #24
    tran1.writeAction("jmp #9")                                 #25

    tran1.writeAction("send <TOP> TOP EAR_1|UDPR_6 4 r") #l10   #26
    tran1.writeAction("yield_terminate")                        #27

    return efa

def GenerateTriEFA4():
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State? 
    state0.alphabet = ['tc'] # a - #tricount, b - #neighbor-return
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    
    state1 = State() #tri Count State
    state1.alphabet = ['nr']
    efa.add_state(state1)
    tran0 = state0.writeTransition("eventCarry", state0, state1, 'vr')
    #rest of the actions
    tran0.writeAction("mov_ob2reg OB_0 UDPR_1")        #0
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_0")       #1
    tran0.writeAction("mov_ob2reg OB_4 UDPR_2")        #2
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_1")       #3
    tran0.writeAction("mov_imm2reg UDPR_3 0")          #4
    tran0.writeAction("mov_imm2reg UDPR_4 0")          #5
    tran0.writeAction("mov_imm2reg UDPR_5 0")          #6
    tran0.writeAction("mov_imm2reg UDPR_6 0")          #7
    tran0.writeAction("bne UDPR_4 0 #13") #loop        #8
    tran0.writeAction("send nr UP_0 EAR_0|UDPR_5 4 r")        #9
    tran0.writeAction("send nr UP_0 EAR_1|UDPR_6 4 r")        #10
    tran0.writeAction("jmp #17")                       #11
    tran0.writeAction("bgt UDPR_4 0 #15")              #12
    tran0.writeAction("send nr UP_0 EAR_0|UDPR_5 4 r") #l1    #13
    tran0.writeAction("jmp #17")                       #14
    tran0.writeAction("blt UDPR_4 0 #17") #l2          #15
    tran0.writeAction("send nr UP_0 EAR_1|UDPR_6 4 r")        #16
    tran0.writeAction("yield") #l3                      #17

    #neighbor result transition is back to same state
    tran1 = state1.writeTransition("eventCarry", state1, state1, 'nr')
    
    #rest of the actions
    tran1.writeAction("bne UDPR_4 0 #3")                        #0  
    tran1.writeAction("compreg OB_0 OB_1 UDPR_8")               #1
    tran1.writeAction("jmp #4")                                 #2
    tran1.writeAction("compreg OB_0 UDPR_7 UDPR_8") #l4         #3
    tran1.writeAction("bne UDPR_8 0 #9")                        #4
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                   #5
    tran1.writeAction("addi UDPR_5 UDPR_5 1")                   #6
    tran1.writeAction("addi UDPR_6 UDPR_6 1")                   #7
    tran1.writeAction("jmp #22")                                #8
    tran1.writeAction("bgt UDPR_8 0 #17") #l5                   #9
    tran1.writeAction("bgt UDPR_4 0 #15") #l5                   #10
    tran1.writeAction("addi UDPR_5 UDPR_5 1")                   #11
    tran1.writeAction("bne UDPR_4 0 #22")                       #12
    tran1.writeAction("mov_ob2reg OB_1 UDPR_7")                 #13
    tran1.writeAction("jmp #22") #l8                            #14
    tran1.writeAction("addi UDPR_6 UDPR_6 1")                   #15
    tran1.writeAction("jmp #22")                                #16
    tran1.writeAction("mov_ob2reg OB_0 UDPR_7")                 #17
    tran1.writeAction("bgt UDPR_4 0 #21") #l5                   #18
    tran1.writeAction("addi UDPR_6 UDPR_6 1") #l6               #19
    tran1.writeAction("jmp #22") #l8                            #20
    tran1.writeAction("addi UDPR_5 UDPR_5 1") #l6               #21
    tran1.writeAction("mov_reg2reg UDPR_4 UDPR_8") #fn          #22
    tran1.writeAction("beq UDPR_1 UDPR_5 #26")                  #23
    tran1.writeAction("beq UDPR_2 UDPR_6 #26")                  #24
    tran1.writeAction("jmp #9")                                 #25

    tran1.writeAction("send <TOP> TOP EAR_1|UDPR_6 4 r") #l10   #26
    tran1.writeAction("yield_terminate")                        #27

    return efa


def GenerateTriEFA_3events():
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
        'n1':1,
        'n2':2,
        'tc':3
    }

    # Shared block 1 - for fetching the next neighbor
    efa.appendBlockAction("block_0","bne UDPR_4 0 #4")                      #0  sb1
    efa.appendBlockAction("block_0","send UDPR_9 UDPR_11 UDPR_5 4 r 1")     #1 
    efa.appendBlockAction("block_0","send UDPR_10 UDPR_11 UDPR_6 4 r 2")    #2 
    efa.appendBlockAction("block_0","yield 2")                              #3 
    efa.appendBlockAction("block_0","blt UDPR_4 2 #7")                      #4  l1
    efa.appendBlockAction("block_0","send UDPR_9 UDPR_11 UDPR_5 4 r 1")     #5
    efa.appendBlockAction("block_0","yield 1")                              #6
    efa.appendBlockAction("block_0","send UDPR_10 UDPR_11 UDPR_6 4 r 2")    #7  l2
    efa.appendBlockAction("block_0","yield 1")                              #8


    tran0 = state0.writeTransition("eventCarry", state0, state1, event_map['vr'])
    #tran0.writeAction("mov_ob2reg OB_0 UDPR_1")                        
    #tran0.writeAction("lshift_or OB_0 UDPR_1 2")                        #0
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")                        #0
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_0")                        #1
    #tran0.writeAction("lshift_or OB_4 UDPR_2 2")                        #2
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")                        #2
    #tran0.writeAction("mov_ob2reg OB_4 UDPR_2")                        
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_1")                        #3
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #4
    tran0.writeAction("mov_imm2reg UDPR_4 0")                           #5
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #6
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #7
    tran0.writeAction("rshift_and_imm TS UDPR_10 0 16711680")           #8 Extract TID for event_word
    tran0.writeAction("addi UDPR_10 UDPR_9 " + str(event_map["n1"]))    #9 UDPR_9 has event_word for n1
    tran0.writeAction("addi UDPR_10 UDPR_10 " + str(event_map["n2"]))   #10 UDPR_10 has event_word for n2
    tran0.writeAction("mov_imm2reg UDPR_11 2" ) # Lane 1                #11
    tran0.writeAction("tranCarry_goto block_0")                         #12


    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['n1'])
    tran1.writeAction("beq UDPR_4 0 #10")                               #0  
    tran1.writeAction("compreg OB_0 UDPR_7 UDPR_8")                     #1
    tran1.writeAction("beq UDPR_8 0 block_1")                           #2
    tran1.writeAction("bgt UDPR_8 0 #6")                                #3
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #4
    tran1.writeAction("tranCarry_goto block_2")                         #5
    tran1.writeAction("mov_ob2reg OB_0 UDPR_7")                         #6  l4
    tran1.writeAction("mov_imm2reg UDPR_4 1")                           #7
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #8
    tran1.writeAction("tranCarry_goto block_2")                         #9   
    tran1.writeAction("mov_ob2reg OB_0 UDPR_7")                         #10  l5
    tran1.writeAction("mov_imm2reg UDPR_4 1")                           #11
    tran1.writeAction("yield 1")                                        #12


    tran2 = state1.writeTransition("eventCarry", state1, state1, event_map['n2'])
    tran2.writeAction("beq UDPR_4 0 #10")                               #0  
    tran2.writeAction("compreg OB_0 UDPR_7 UDPR_8")                     #1
    tran2.writeAction("beq UDPR_8 0 block_1")                           #2
    tran2.writeAction("bgt UDPR_8 0 #6")                                #3
    tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #4
    tran2.writeAction("tranCarry_goto block_2")                         #5
    tran2.writeAction("mov_ob2reg OB_0 UDPR_7")                         #6  l6
    tran2.writeAction("mov_imm2reg UDPR_4 2")                           #7
    tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #8
    tran2.writeAction("tranCarry_goto block_2")                         #9   
    tran2.writeAction("mov_ob2reg OB_0 UDPR_7")                         #10  l7
    tran2.writeAction("mov_imm2reg UDPR_4 2")                           #11
    tran2.writeAction("yield 1")                                          #12


    efa.appendBlockAction("block_1","addi UDPR_3 UDPR_3 1")             #0  sb2
    efa.appendBlockAction("block_1","addi UDPR_5 UDPR_5 4")             #1  
    efa.appendBlockAction("block_1","addi UDPR_6 UDPR_6 4")             #2  
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_4 2")             #3
    efa.appendBlockAction("block_1", "tranCarry_goto block_2")          #4   

    efa.appendBlockAction("block_2","beq UDPR_1 UDPR_5 #3")              #0  sb3
    efa.appendBlockAction("block_2","beq UDPR_2 UDPR_6 #3")              #1  
    efa.appendBlockAction("block_2","tranCarry_goto block_0")           #2
    efa.appendBlockAction("block_2","mov_imm2reg UDPR_11 1" )           #3  Top
    efa.appendBlockAction("block_2","addi UDPR_10 UDPR_10 " + str(event_map["tc"])) #4 UDPR_9 has event_word
    efa.appendBlockAction("block_2","send tc TOP UDPR_3 4 w 0")           #5  l8
    efa.appendBlockAction("block_2","yield_terminate 4")                  #6
    
    return efa

def GenerateTriEFA_singlestream():
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
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #5 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["nr"]))     #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_11 2" ) # Lane 1                #9
    # Fetch phase
    tran0.writeAction("beq UDPR_2 UDPR_3 #14")                          #10  l1
    tran0.writeAction("send UDPR_7 UDPR_11 UDPR_3 4 r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("addi UDPR_3 UDPR_3 4")                           #12
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("yield 2")                                        #15

    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['nr'])
    tran1.writeAction("mov_imm2reg UDPR_9 0")                           #0 walk = 0
    tran1.writeAction("add UDPR_5 UDPR_4 UDPR_7")                       #1 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #2 fetch v1 from lm
    tran1.writeAction("bne OB_0 UDPR_8 #6")                             #3
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #4
    tran1.writeAction("jmp #19")                                        #5 #12 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_0 #11")                            #6 #l3 
    tran1.writeAction("beq UDPR_9 -1 #19")                              #7
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #8
    tran1.writeAction("mov_imm2reg UDPR_9 1")                           #9
    tran1.writeAction("jmp #17")                                        #10 #upper bounds check
    tran1.writeAction("beq UDPR_9 1 #19")                               #11 #l4
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #12
    tran1.writeAction("mov_imm2reg UDPR_9 -1")                          #13

    tran1.writeAction("bge UDPR_5 0 #1")                               #14 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #15
    tran1.writeAction("jmp #19")                                        #16 #block 2 - bounds check 
    tran1.writeAction("bne UDPR_5 UDPR_1 #1")                          #17
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #18

    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #19 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #22")                          #20 
    tran1.writeAction("yield 1")                                        #21
    #tran1.writeAction("send tc TOP UDPR_3 4 w 0")                       #22  #fin
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_12 4")                       #22  #fin
    tran1.writeAction("yield_terminate 4")                              #23

    return efa

def GenerateTriEFA_singlestream_loopopt():
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
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #5 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["nr"]))     #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_11 2" ) # Lane 1                #9
    # Fetch phase
    tran0.writeAction("beq UDPR_2 UDPR_3 #14")                          #10  l1
    tran0.writeAction("send UDPR_7 UDPR_11 UDPR_3 4 r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("addi UDPR_3 UDPR_3 4")                           #12
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("mov_imm2reg UDPR_9 0")                           #15 walk = 0
    tran0.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #16 lm addr calculation
    tran0.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #17 fetch v1 from lm
    tran0.writeAction("yield 2")                                        #18

    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['nr'])
    # Pick up first element
    tran1.writeAction("ble UDPR_8 OB_0 #3")                             #0 if n1 > n2 set walk -1
    tran1.writeAction("mov_imm2reg UDPR_9 -1")                           #1
    tran1.writeAction("jmp #4")                                         #2
    tran1.writeAction("mov_imm2reg UDPR_9 1")                          #3
    tran1.writeAction("blt UDPR_9 0 #16")                               #4 +1 walk
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_0 #8")                             #5
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #6
    tran1.writeAction("jmp #27")                                        #7 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_0 #27")                            #8
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #9
    tran1.writeAction("bne UDPR_5 UDPR_1 #13")                          #10
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #11
    tran1.writeAction("jmp #27")                                        #12
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 fetch v1 from lm
    tran1.writeAction("jmp #5")                                         #15
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_0 #19")                            #16
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #17
    tran1.writeAction("jmp #27")                                        #18 block 1 - term/yield block
    tran1.writeAction("blt UDPR_8 OB_0 #27")                            #19
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #20
    tran1.writeAction("bge UDPR_5 0 #24")                                #21 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #22
    tran1.writeAction("jmp #27")                                        #23
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 fetch v1 from lm
    tran1.writeAction("jmp #16")                                         #26
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #27 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #30")                          #28 
    tran1.writeAction("yield 1")                                        #29
    #tran1.writeAction("send tc TOP UDPR_3 4 w 0")                       #30  #fin
    tran1.writeAction("mov_imm2reg UDPR_11 262140")                 # Address to store result
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_11 4")                    #22 Move Triangle count to res addr 
    tran1.writeAction("yield_terminate 4")                              #31

    return efa

def GenerateTriEFA_singlestream_block_loopopt(block_size):
    efa = EFA([])
    efa.code_level = 'machine'
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() #tri Count State
    efa.add_state(state1)
    state2 = State() #tri Count State
    efa.add_state(state2)
    #num_neighs = block_size/4

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
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #5 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["nr"]))     #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_11 2" ) # Lane 1                #9
    # Fetch phase
    tran0.writeAction("beq UDPR_2 UDPR_3 #14")                          #10  l1
    tran0.writeAction("send UDPR_7 UDPR_11 UDPR_3 " + str(block_size) + " r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("addi UDPR_3 UDPR_3 " + str(block_size))                           #12
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("yield 2")                                        #15

    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['nr'])
    tran1.writeAction("mov_imm2reg UDPR_9 0")                           #0 walk = 0
    tran1.writeAction("add UDPR_5 UDPR_4 UDPR_7")                       #1 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #2 fetch v1 from lm
    tran1.writeAction("bne OB_0 UDPR_8 #6")                             #3
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #4
    tran1.writeAction("jmp #19")                                        #5 #12 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_0 #11")                            #6 #l3 
    tran1.writeAction("beq UDPR_9 -1 #19")                              #7
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #8
    tran1.writeAction("mov_imm2reg UDPR_9 1")                           #9
    tran1.writeAction("jmp #17")                                        #10 #upper bounds check
    tran1.writeAction("beq UDPR_9 1 #19")                               #11 #l4
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #12
    tran1.writeAction("mov_imm2reg UDPR_9 -1")                          #13

    tran1.writeAction("bge UDPR_5 0 #1")                               #14 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #15
    tran1.writeAction("jmp #19")                                        #16 #block 2 - bounds check 
    tran1.writeAction("bne UDPR_5 UDPR_1 #1")                          #17
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #18

    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #19 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #22")                          #20 
    tran1.writeAction("yield 1")                                        #21
    tran1.writeAction("send tc TOP UDPR_3 4 w 0")                       #22  #fin
    tran1.writeAction("yield_terminate 4")                              #23

    return efa

def GenerateTriEFA_singlestream_loopopt_ayz():
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
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #6 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #7 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #8 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #9 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["nr"]))     #10 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_11 2" ) # Lane 1                #11

    tran0.writeAction("rshift UDPR_12 UDPR_13 3")                       #12  ID / 32
    tran0.writeAction("add UDPR_10 UDPR_13 UDPR_13")                    #13  Word containing bit for vertex membership
    tran0.writeAction("mov_lm2reg UDPR_13 UDPR_14 1")                   #14 fetch v1 from lm
    tran0.writeAction("lshift_and_imm UDPR_12 UDPR_13 0 7")            #15 2 bit position 
    tran0.writeAction("rshift_t UDPR_14 UDPR_13 UDPR_14")               #16 2 bit position 
    tran0.writeAction("lshift_and_imm UDPR_14 UDPR_13 0 1")    #17 2  UDPR_13 - high or low for V2 V1 is low
    # Fetch phase
    tran0.writeAction("beq UDPR_2 UDPR_3 #22")                          #18  l1
    tran0.writeAction("send UDPR_7 UDPR_11 UDPR_3 4 r 1")               #19  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("addi UDPR_3 UDPR_3 4")                           #20
    tran0.writeAction("jmp #18")                                        #21
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #22 y1
    tran0.writeAction("mov_imm2reg UDPR_9 0")                           #23 walk = 0
    tran0.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 lm addr calculation
    tran0.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 fetch v1 from lm
    tran0.writeAction("yield 2")                                        #26

    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['nr'])
    # Pick up first element
    tran1.writeAction("ble UDPR_8 OB_0 #3")                             #0 if n1 > n2 set walk -1
    tran1.writeAction("mov_imm2reg UDPR_9 -1")                          #1
    tran1.writeAction("jmp #4")                                         #2
    tran1.writeAction("mov_imm2reg UDPR_9 1")                           #3
    tran1.writeAction("blt UDPR_9 0 #31")                               #4 +1 walk
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_0 #23")                            #5
    tran1.writeAction("rshift UDPR_8 UDPR_11 3")                        #6  ID / 32
    tran1.writeAction("add UDPR_10 UDPR_11 UDPR_11")                    #7  Word containing bit for vertex membership
    tran1.writeAction("mov_lm2reg UDPR_11 UDPR_12 1")                   #8 fetch v1 from lm
    tran1.writeAction("lshift_and_imm UDPR_8 UDPR_11 0 7")              #9 bit position 
    tran1.writeAction("rshift_t UDPR_12 UDPR_11 UDPR_12")               #10 bit position 
    tran1.writeAction("lshift_and_imm UDPR_12 UDPR_12 0 1")             #11 bit position UDPR_12 high or low for V3
    tran1.writeAction("beq UDPR_13 1 #18")                              #12
    tran1.writeAction("beq UDPR_12 1 #16")                              #13
    tran1.writeAction("addi UDPR_3 UDPR_3 2")                           #14 both or part of v_low
    tran1.writeAction("jmp #57")                                        #15 block 1 - term/yield block
    tran1.writeAction("addi UDPR_3 UDPR_3 3")                           #16 v3 - 1 v2 - 0
    tran1.writeAction("jmp #57")                                        #17 block 1 - term/yield block
    tran1.writeAction("beq UDPR_12 1 #21")                               #18 UDPR_13 = 1
    tran1.writeAction("addi UDPR_3 UDPR_3 3")                           #19 v3 - 0 v2 - 1
    tran1.writeAction("jmp #57")                                        #20 block 1 - term/yield block
    tran1.writeAction("addi UDPR_3 UDPR_3 6")                           #21 both or part of v_high
    tran1.writeAction("jmp #57")                                        #22 block 1 - term/yield block

    tran1.writeAction("bgt UDPR_8 OB_0 #57")                            #23 8
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #24
    tran1.writeAction("bne UDPR_5 UDPR_1 #28")                          #25
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #26
    tran1.writeAction("jmp #57")                                        #27
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #28 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #29 14 fetch v1 from lm
    tran1.writeAction("jmp #5")                                         #30 15
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_0 #49")                            #31 16
    tran1.writeAction("rshift UDPR_8 UDPR_11 3")                        #32  ID / 32
    tran1.writeAction("add UDPR_10 UDPR_11 UDPR_11")                    #33  Word containing bit for vertex membership
    tran1.writeAction("mov_lm2reg UDPR_11 UDPR_12 1")                   #34 fetch v1 from lm
    tran1.writeAction("lshift_and_imm UDPR_8 UDPR_11 0 15")             #35 bit position 
    tran1.writeAction("rshift_t UDPR_12 UDPR_11 UDPR_12")               #36 bit position 
    tran1.writeAction("lshift_and_imm UDPR_12 UDPR_12 0 4294967294")    #37 bit position UDPR_12 high or low for V3
    tran1.writeAction("beq UDPR_13 1 #44")                               #38
    tran1.writeAction("beq UDPR_12 1 #42")                               #39
    tran1.writeAction("addi UDPR_3 UDPR_3 6")                           #40 both or part of v_high
    tran1.writeAction("jmp #57")                                        #41 block 1 - term/yield block
    tran1.writeAction("addi UDPR_3 UDPR_3 3")                           #42 v3 - 1 v2 - 0
    tran1.writeAction("jmp #57")                                        #43 block 1 - term/yield block
    tran1.writeAction("beq UDPR_12 1 #47")                               #44 UDPR_13 = 1
    tran1.writeAction("addi UDPR_3 UDPR_3 3")                           #45 v3 - 0 v2 - 1
    tran1.writeAction("jmp #57")                                        #46 block 1 - term/yield block
    tran1.writeAction("addi UDPR_3 UDPR_3 2")                           #47 both or part of v_high
    tran1.writeAction("jmp #57")                                        #48 block 1 - term/yield block


    tran1.writeAction("blt UDPR_8 OB_0 #57")                            #49 19
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #50 20
    tran1.writeAction("bge UDPR_5 0 #54")                               #51 21 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #52 22
    tran1.writeAction("jmp #57")                                        #53 23
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #54 24 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #55 25 fetch v1 from lm
    tran1.writeAction("jmp #31")                                        #56 26
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #57 27 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #60")                          #58 28 
    tran1.writeAction("yield 1")                                        #59 29
    tran1.writeAction("send tc TOP UDPR_3 4 w 0")                       #60 30  #fin
    tran1.writeAction("yield_terminate 4")                              #61 31

    return efa

def GenerateTriEFA_singlestream_loopopt_block16():
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
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #5 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["nr"]))     #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_11 2" ) # Lane 1                #9
    # Fetch phase
    tran0.writeAction("ble UDPR_2 UDPR_3 #14")                          #10  l1
    tran0.writeAction("send UDPR_7 UDPR_11 UDPR_3 16 r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("addi UDPR_3 UDPR_3 16")                           #12 update 16 bytes
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("mov_imm2reg UDPR_9 0")                           #15 walk = 0
    tran0.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #16 lm addr calculation
    tran0.writeAction("mov_lm2reg_blk UDPR_7 UDPR_12 16")                     #17 fetch v1 from lm
    #tran0.writeAction("mov_ob2reg OB_8 UDPR_11 4")                     #17 fetch v1 from lm
    tran0.writeAction("yield 2")                                        #18

    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['nr'])
    # Pick up first element
    tran1.writeAction("blt UDPR_1 4 #4") #l0                         #0
    tran1.writeAction("blt UDPR_2 4 #6")                             #1
    tran1.writeAction("block_compare_i UDPR_12 OB_0 UDPR_8 16")         #2
    tran1.writeAction("jmp #7")                                       #3
    tran1.writeAction("block_compare UDPR_12 OB_0 UDPR_8 UDPR_1") #l1   #4
    tran1.writeAction("jmp #7")                                       #5
    tran1.writeAction("block_compare UDPR_12 OB_0 UDPR_8 UDPR_2") #l2   #6
    tran1.writeAction("add UDPR_3 UDPR_3 UDPR_8") #l3                   #7
    tran1.writeAction("beq UDPR_9 0 #14")                              #8
    tran1.writeAction("bgt UDPR_9 1 #12")                              #9
    tran1.writeAction("subi UDPR_1 UDPR_1 4")                           #10
    tran1.writeAction("jmp #16")                                         #11
    tran1.writeAction("subi UDPR_2 UDPR_2 4") #l6                       #12
    tran1.writeAction("jmp #16")                                         #13
    tran1.writeAction("subi UDPR_1 UDPR_1 4") #l5                       #14
    tran1.writeAction("subi UDPR_2 UDPR_2 4")                           #15
    tran1.writeAction("ble UDPR_1 0 #25") #l9                          #16
    tran1.writeAction("ble UDPR_2 0 #25")                              #17
    tran1.writeAction("blt OB_3 UDPR_15 #23")                            #18
    tran1.writeAction("addi UDPR_7 UDPR_7 16")                          #19 
    tran1.writeAction("mov_lm2reg_blk UDPR_7 UDPR_12 16")               #20
    tran1.writeAction("mov_imm2reg UDPR_9 -1")                          #21
    tran1.writeAction("jmp #0")                                       #22
    tran1.writeAction("mov_imm2reg UDPR_9 1")                           #23
    tran1.writeAction("yield 2")                                        #24
    # do check for which has to be fetched / yielded    
    tran1.writeAction("mov_imm2reg UDPR_11 262140")                     #25 Address to store result
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_11 4")                    #26 Move Triangle count to res addr 
    tran1.writeAction("yield_terminate 4")  #l8                         #27

    return efa

def GenerateTriEFA_singlestream_loopopt_block16_static():
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
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #5 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["nr"]))     #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_11 2" ) # Lane 1                #9
    # Fetch phase
    tran0.writeAction("ble UDPR_2 UDPR_3 #14")                          #10  l1
    tran0.writeAction("send UDPR_7 UDPR_11 UDPR_3 16 r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("addi UDPR_3 UDPR_3 16")                           #12
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("mov_imm2reg UDPR_9 0")                           #0 walk = 0
    tran0.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #1 lm addr calculation
    tran0.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #2 fetch v1 from lm
    tran0.writeAction("yield 2")                                        #15

    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['nr'])
    # Pick up first element
    tran1.writeAction("ble UDPR_8 OB_0 #3")                             #0 if n1 > n2 set walk -1
    tran1.writeAction("mov_imm2reg UDPR_9 -1")                           #1
    tran1.writeAction("jmp #4")                                         #2
    tran1.writeAction("mov_imm2reg UDPR_9 1")                          #3
    tran1.writeAction("blt UDPR_9 0 #16")                               #4 +1 walk
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_0 #8")                             #5
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #6
    tran1.writeAction("jmp #27")                                        #7 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_0 #27")                            #8
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #9
    tran1.writeAction("bne UDPR_5 UDPR_1 #13")                          #10
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #11
    tran1.writeAction("jmp #27")                                        #12
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 fetch v1 from lm
    tran1.writeAction("jmp #5")                                         #15
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_0 #19")                            #16
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #17
    tran1.writeAction("jmp #27")                                        #18 block 1 - term/yield block
    tran1.writeAction("blt UDPR_8 OB_0 #27")                            #19
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #20
    tran1.writeAction("bge UDPR_5 0 #24")                                #21 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #22
    tran1.writeAction("jmp #27")                                        #23
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 fetch v1 from lm
    tran1.writeAction("jmp #16")                                         #26
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #27 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #117")                   #28 

    #next OB_1
    tran1.writeAction("ble UDPR_8 OB_1 #32")                             #29 if n1 > n2 set walk -1
    tran1.writeAction("mov_imm2reg UDPR_9 -1")                          #30
    tran1.writeAction("jmp #33")                                         #31
    tran1.writeAction("mov_imm2reg UDPR_9 1")                          #32
    tran1.writeAction("blt UDPR_9 0 #45")                               #33 +1 walk
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_1 #37")                             #34
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #35
    tran1.writeAction("jmp #56")                                        #36 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_1 #56")                            #37
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #38
    tran1.writeAction("bne UDPR_5 UDPR_1 #42")                          #39
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #40
    tran1.writeAction("jmp #56")                                        #41
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #42 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #43 fetch v1 from lm
    tran1.writeAction("jmp #34")                                         #44
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_1 #48")                            #45
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #46
    tran1.writeAction("jmp #56")                                        #47 block 1 - term/yield block
    tran1.writeAction("blt UDPR_8 OB_1 #56")                            #48
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #49
    tran1.writeAction("bge UDPR_5 0 #53")                                #50 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #51
    tran1.writeAction("jmp #56")                                        #52
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #53 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #54 fetch v1 from lm
    tran1.writeAction("jmp #45")                                         #55
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #56 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #117")                   #57

    #next OB_2
    tran1.writeAction("ble UDPR_8 OB_2 #61")                             #58 if n1 > n2 set walk -1
    tran1.writeAction("mov_imm2reg UDPR_9 -1")                           #59
    tran1.writeAction("jmp #62")                                         #60
    tran1.writeAction("mov_imm2reg UDPR_9 1")                          #61
    tran1.writeAction("blt UDPR_9 0 #74")                               #62 +1 walk
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_2 #66")                             #63
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #64
    tran1.writeAction("jmp #85")                                        #65 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_2 #85")                            #66
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #67
    tran1.writeAction("bne UDPR_5 UDPR_1 #71")                          #68
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #69
    tran1.writeAction("jmp #85")                                        #70
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #71 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #72 fetch v1 from lm
    tran1.writeAction("jmp #63")                                         #73
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_2 #77")                            #74
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #75
    tran1.writeAction("jmp #85")                                        #76 block 1 - term/yield block
    tran1.writeAction("blt UDPR_8 OB_2 #85")                            #77
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #78
    tran1.writeAction("bge UDPR_5 0 #82")                                #79 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #80
    tran1.writeAction("jmp #85")                                        #81
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #82 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #83 fetch v1 from lm
    tran1.writeAction("jmp #74")                                         #84
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #85 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #117")                   #86 

    #next OB_3
    tran1.writeAction("ble UDPR_8 OB_3 #90")                             #87 if n1 > n2 set walk -1
    tran1.writeAction("mov_imm2reg UDPR_9 -1")                           #88
    tran1.writeAction("jmp #91")                                         #89
    tran1.writeAction("mov_imm2reg UDPR_9 1")                          #90
    tran1.writeAction("blt UDPR_9 0 #103")                               #91 +1 walk
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_3 #95")                             #92
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #93
    tran1.writeAction("jmp #114")                                        #94 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_3 #114")                            #95
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #96
    tran1.writeAction("bne UDPR_5 UDPR_1 #100")                          #97
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #98
    tran1.writeAction("jmp #114")                                        #99
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #100 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #101 fetch v1 from lm
    tran1.writeAction("jmp #92")                                         #102
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_3 #106")                            #103
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #104
    tran1.writeAction("jmp #114")                                        #105 block 1 - term/yield block
    tran1.writeAction("blt UDPR_8 OB_3 #114")                            #106
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #107
    tran1.writeAction("bge UDPR_5 0 #111")                                #108 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #109
    tran1.writeAction("jmp #114")                                        #110
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #111 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #112 fetch v1 from lm
    tran1.writeAction("jmp #103")                                         #113
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #114 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #117")                   #115 
    tran1.writeAction("yield 1")                                        #116
    #tran1.writeAction("send tc TOP UDPR_3 4 w 0")                       #117  #fin
    tran1.writeAction("mov_imm2reg UDPR_11 262140")                     #118 Address to store result
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_11 4")                    #119 Move Triangle count to res addr 
    tran1.writeAction("yield_terminate 4")                              #120

    return efa

if __name__=="__main__":
    efa = GenerateTriEFA()
    #efa.printOut(error)
    

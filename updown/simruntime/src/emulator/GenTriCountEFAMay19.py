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
    tran0.writeAction("send_old nr UP_0 EAR_0|UDPR_5 4 r")        #9
    tran0.writeAction("send_old nr UP_0 EAR_1|UDPR_6 4 r")        #10
    tran0.writeAction("jmp #17")                       #11
    tran0.writeAction("bgt UDPR_4 0 #15")              #12
    tran0.writeAction("send_old nr UP_0 EAR_0|UDPR_5 4 r") #l1    #13
    tran0.writeAction("jmp #17")                       #14
    tran0.writeAction("blt UDPR_4 0 #17") #l2          #15
    tran0.writeAction("send_old nr UP_0 EAR_1|UDPR_6 4 r")        #16
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

    tran1.writeAction("send_old <TOP> TOP EAR_1|UDPR_6 4 r") #l10   #25
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
    tran0.writeAction("send_old nr UP_0 EAR_0|UDPR_5 4 r")        #9
    tran0.writeAction("send_old nr UP_0 EAR_1|UDPR_6 4 r")        #10
    tran0.writeAction("jmp #17")                       #11
    tran0.writeAction("bgt UDPR_4 0 #15")              #12
    tran0.writeAction("send_old nr UP_0 EAR_0|UDPR_5 4 r") #l1    #13
    tran0.writeAction("jmp #17")                       #14
    tran0.writeAction("blt UDPR_4 0 #17") #l2          #15
    tran0.writeAction("send_old nr UP_0 EAR_1|UDPR_6 4 r")        #16
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

    tran1.writeAction("send_old <TOP> TOP EAR_1|UDPR_6 4 r") #l10   #26
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
    tran0.writeAction("send_old nr UP_0 EAR_0|UDPR_5 4 r")        #9
    tran0.writeAction("send_old nr UP_0 EAR_1|UDPR_6 4 r")        #10
    tran0.writeAction("jmp #17")                       #11
    tran0.writeAction("bgt UDPR_4 0 #15")              #12
    tran0.writeAction("send_old nr UP_0 EAR_0|UDPR_5 4 r") #l1    #13
    tran0.writeAction("jmp #17")                       #14
    tran0.writeAction("blt UDPR_4 0 #17") #l2          #15
    tran0.writeAction("send_old nr UP_0 EAR_1|UDPR_6 4 r")        #16
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

    tran1.writeAction("send_old <TOP> TOP EAR_1|UDPR_6 4 r") #l10   #26
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
    efa.appendBlockAction("block_0","send_old UDPR_9 UDPR_11 UDPR_5 4 r 1")     #1 
    efa.appendBlockAction("block_0","send_old UDPR_10 UDPR_11 UDPR_6 4 r 2")    #2 
    efa.appendBlockAction("block_0","yield 2")                              #3 
    efa.appendBlockAction("block_0","blt UDPR_4 2 #7")                      #4  l1
    efa.appendBlockAction("block_0","send_old UDPR_9 UDPR_11 UDPR_5 4 r 1")     #5
    efa.appendBlockAction("block_0","yield 1")                              #6
    efa.appendBlockAction("block_0","send_old UDPR_10 UDPR_11 UDPR_6 4 r 2")    #7  l2
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
    efa.appendBlockAction("block_2","send_old tc TOP UDPR_3 4 w 0")           #5  l8
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
    tran0.writeAction("send_old UDPR_7 UDPR_11 UDPR_3 4 r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
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
    tran1.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #22  #fin
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
    tran0.writeAction("send_old UDPR_7 UDPR_11 UDPR_3 4 r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
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
    tran1.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #30  #fin
    tran1.writeAction("yield_terminate 4")                              #31

    return efa

def GenerateTriEFA_singlestream_loopopt2():
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
    tran0.writeAction("send_old UDPR_7 UDPR_11 UDPR_3 4 r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("addi UDPR_3 UDPR_3 4")                           #12
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("mov_imm2reg UDPR_9 0")                           #15 walk = 0
    tran0.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #16 lm addr calculation
    tran0.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #17 fetch v1 from lm
    tran0.writeAction("yield 2")                                        #18

    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['nr'])
    # Pick up first element
    tran1.writeAction("bgt UDPR_8 OB_0 #16")                             #0 1if n1 > n2 set walk -1
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_0 #4")                             #5 1 
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
    tran1.writeAction("jmp #23")                                        #7 3 4block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_0 #23")                            #8 4
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #9 6
    tran1.writeAction("bne UDPR_5 UDPR_1 #9")                          #10 7
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #11 8
    tran1.writeAction("jmp #23")                                        #12 9
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 10 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 11 fetch v1 from lm
    tran1.writeAction("jmp #1")                                         #15 12
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_0 #15")                            #16 13
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #17 14
    tran1.writeAction("jmp #23")                                        #18 15 block 1 - term/yield block
    tran1.writeAction("blt UDPR_8 OB_0 #23")                            #19 16
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #20 17
    tran1.writeAction("bge UDPR_5 0 #23")                                #21 18 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #22 19
    tran1.writeAction("jmp #23")                                        #23 20
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 21 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 22 fetch v1 from lm
    tran1.writeAction("jmp #12")                                         #26 23
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #27 24 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #26")                          #28 25
    tran1.writeAction("yield 1")                                        #29 26
    tran1.writeAction("send_old tc TOP UDPR_3 4 w 0")                   #30 27 #fin
    tran1.writeAction("yield_terminate 4")                              #31 28

    return efa

def GenerateTriEFA_singlestream_loopopt2_cached():
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         #1 v1 - LM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #2 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #3 v2 DRAM base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #5 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("mov_imm2reg UDPR_7 " + str(event_map["v1_nr"]))     #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_11 2" ) # Lane 1                #9

    # Fetch v1 phase
    tran0.writeAction("beq UDPR_1 UDPR_3 #14")                          #10  l1
    tran0.writeAction("send_old UDPR_7 UDPR_11 UDPR_3 4 r 2")           #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("addi UDPR_3 UDPR_3 4")                           #12
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("yield 2")                                        #15

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tran1.writeAction("mov_imm2reg UDPR_5 4")                           #0
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #1
    tran1.writeAction("addi UDPR_3 UDPR_3 4")                           #2
    tran1.writeAction("beq UDPR_1 UDPR_3 #5")                           #3
    tran1.writeAction("yield 2")                                        #4

    # Fetch v2 phase
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #5 y1
    tran1.writeAction("mov_imm2reg UDPR_7 " + str(event_map["v2_nr"]))  #6   #8 UDPR_9 has event_word for n1
    tran1.writeAction("beq UDPR_2 UDPR_3 #11")                          #7  l1
    tran1.writeAction("send_old UDPR_7 UDPR_11 UDPR_3 4 r 1")           #8  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran1.writeAction("addi UDPR_3 UDPR_3 4")                           #9
    tran1.writeAction("jmp #7")                                        #10
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #11 y1
    tran1.writeAction("mov_imm2reg UDPR_4 0")                           #12
    tran1.writeAction("mov_imm2reg UDPR_5 0")                           #13
    tran1.writeAction("mov_imm2reg UDPR_7 0")                           #14 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #15 fetch v1 from lm
    tran1.writeAction("yield 2")                                        #16

    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    tran2.writeAction("bgt UDPR_8 OB_0 #16")                             #0 1if n1 > n2 set walk -1
    # walk +1 (forward) [loop]
    tran2.writeAction("bne UDPR_8 OB_0 #4")                             #5 1 
    tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
    tran2.writeAction("jmp #23")                                        #7 3 4block 1 - term/yield block
    tran2.writeAction("bgt UDPR_8 OB_0 #23")                            #8 4
    tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 6
    tran2.writeAction("bne UDPR_5 UDPR_1 #9")                          #10 7
    tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 8
    tran2.writeAction("jmp #23")                                        #12 9
    tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 10 lm addr calculation
    tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 11 fetch v1 from lm
    tran2.writeAction("jmp #1")                                         #15 12
    #walk -1 (backward)
    tran2.writeAction("bne UDPR_8 OB_0 #15")                            #16 13
    tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 14
    tran2.writeAction("jmp #23")                                        #18 15 block 1 - term/yield block
    tran2.writeAction("blt UDPR_8 OB_0 #23")                            #19 16
    tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 17
    tran2.writeAction("bge UDPR_5 0 #23")                                #21 18 #y2
    tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 19
    tran2.writeAction("jmp #23")                                        #23 20
    tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 21 lm addr calculation
    tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 22 fetch v1 from lm
    tran2.writeAction("jmp #12")                                         #26 23
    #<next v2> 
    tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 24 #y1
    tran2.writeAction("beq UDPR_6 UDPR_2 #26")                          #28 25
    tran2.writeAction("yield 1")                                        #29 26
    tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                   #30 27 #fin
    tran2.writeAction("yield_terminate 4")                              #31 28

    return efa

def GenerateTriEFA_singlestream_loopopt2_cached_lm():
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         #1 v1 - LM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #2 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #3 v2 DRAM base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #5 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("mov_imm2reg UDPR_7 " + str(event_map["v1_nr"]))     #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_13 -1" ) # Lane 1                #9

    # Fetch v1 phase
    tran0.writeAction("beq UDPR_1 UDPR_3 #14")                          #10  l1
    tran0.writeAction("send_old UDPR_7 UDPR_13 UDPR_3 4 r 2")           #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR1)
    tran0.writeAction("addi UDPR_3 UDPR_3 4")                           #12
    tran0.writeAction("jmp #10")                                        #13
    #tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("mov_ob2reg OB_8 UDPR_10")                        #UDPR_10 - base address
    #tran0.writeAction("mov_ob2reg OB_8 UDPR_11")                        # copy it to 11 for status?
    tran0.writeAction("addi UDPR_10 UDPR_3 8")                          # add 8 for base of v1
    #tran0.writeAction("addi UDPR_10 UDPR_10 8")                         #0 - state, 4, result
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")
    tran0.writeAction("yield 2")                                        #15

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tran1.writeAction("mov_imm2reg UDPR_5 4")                           #0
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #1
    tran1.writeAction("addi UDPR_3 UDPR_3 4")                           #2
    tran1.writeAction("beq UDPR_12 UDPR_3 #5")                           #3
    tran1.writeAction("yield 2")                                        #4

    # Fetch v2 phase
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #5 y1
    tran1.writeAction("mov_imm2reg UDPR_7 " + str(event_map["v2_nr"]))  #6   #8 UDPR_9 has event_word for n1
    tran1.writeAction("beq UDPR_2 UDPR_3 #11")                          #7  l1
    tran1.writeAction("send_old UDPR_7 UDPR_13 UDPR_3 4 r 1")           #8  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran1.writeAction("addi UDPR_3 UDPR_3 4")                           #9
    tran1.writeAction("jmp #7")                                        #10
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #11 y1
    tran1.writeAction("addi UDPR_10 UDPR_4 8")                           #12
    tran1.writeAction("mov_imm2reg UDPR_5 0")                           #13
    tran1.writeAction("mov_reg2reg UDPR_4 UDPR_7")                           #14 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #15 fetch v1 from lm
    tran1.writeAction("yield 2")                                        #16

    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    tran2.writeAction("bgt UDPR_8 OB_0 #16")                             #0 1if n1 > n2 set walk -1
    # walk +1 (forward) [loop]
    tran2.writeAction("bne UDPR_8 OB_0 #4")                             #5 1 
    tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
    tran2.writeAction("jmp #23")                                        #7 3 4block 1 - term/yield block
    tran2.writeAction("bgt UDPR_8 OB_0 #23")                            #8 4
    tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
    tran2.writeAction("bne UDPR_5 UDPR_1 #9")                          #10 6
    tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
    tran2.writeAction("jmp #23")                                        #12 8
    tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
    tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
    tran2.writeAction("jmp #1")                                         #15 11
    #walk -1 (backward)
    tran2.writeAction("bne UDPR_8 OB_0 #15")                            #16 12
    tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
    tran2.writeAction("jmp #23")                                        #18 14 block 1 - term/yield block
    tran2.writeAction("blt UDPR_8 OB_0 #23")                            #19 15
    tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
    tran2.writeAction("bge UDPR_5 0 #23")                                #21 17 #y2
    tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
    tran2.writeAction("jmp #23")                                        #23 19
    tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
    tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
    tran2.writeAction("jmp #12")                                         #26 22
    #<next v2> 
    tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23 #y1
    tran2.writeAction("beq UDPR_6 UDPR_2 #26")                          #28 24
    tran2.writeAction("yield 1")                                        #29 25
    #tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                   #30 27 #fin
    tran2.writeAction("addi UDPR_10 UDPR_10 4")                           #27 23 #y1
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #26 Move Tri count
    tran2.writeAction("subi UDPR_10 UDPR_10 4")                           #27 Set status now
    tran2.writeAction("mov_imm2reg UDPR_3 1")                    #26 Move Tri count
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #30 28
    tran2.writeAction("yield_terminate 4")                              #31 29

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
    tran0.writeAction("send_old UDPR_7 UDPR_11 UDPR_3 4 r 1")               #19  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
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
    tran1.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #60 30  #fin
    tran1.writeAction("yield_terminate 4")                              #61 31

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
    tran0.writeAction("send_old UDPR_7 UDPR_11 UDPR_3 16 r 1")               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction("addi UDPR_3 UDPR_3 16")                           #12
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("mov_imm2reg UDPR_9 0")                           #0 walk = 0
    tran0.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #1 lm addr calculation
    tran0.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #2 fetch v1 from lm
    tran0.writeAction("yield 2")                                        #15

    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['nr'])
    # Pick up first element
    tran1.writeAction("bgt UDPR_8 OB_0 #16")                            #0 if n1 > n2 set walk -1
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_0 #4")                             #5 1
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
    tran1.writeAction("jmp #23")                                        #7 3 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_0 #23")                            #8 4
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
    tran1.writeAction("bne UDPR_5 UDPR_1 #9")                          #10 6
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
    tran1.writeAction("jmp #23")                                        #12 8
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
    tran1.writeAction("jmp #1")                                         #15 11
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_0 #15")                            #16 12
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
    tran1.writeAction("jmp #23")                                        #18 14 block 1 - term/yield block
    tran1.writeAction("blt UDPR_8 OB_0 #23")                            #19 15
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
    tran1.writeAction("bge UDPR_5 0 #20")                                #21 17 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
    tran1.writeAction("jmp #23")                                        #23 19 
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
    tran1.writeAction("jmp #12")                                         #26 22
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #101")                   #28 24

    #next OB_1
    tran1.writeAction("bgt UDPR_8 OB_1 #41")                             #29 25if n1 > n2 set walk -1
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_1 #29")                             #34 26
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #35 27
    tran1.writeAction("jmp #48")                                        #36 28 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_1 #48")                            #37 29
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #38 30
    tran1.writeAction("bne UDPR_5 UDPR_1 #34")                          #39 31
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #40 32
    tran1.writeAction("jmp #48")                                        #41 33
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #42 34 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #43 35 fetch v1 from lm
    tran1.writeAction("jmp #26")                                         #44 36
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_1 #40")                            #45 37
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #46 38
    tran1.writeAction("jmp #48")                                        #47 39 block 1 - term/yield block
    tran1.writeAction("blt UDPR_8 OB_1 #48")                            #48 40 
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #49 41
    tran1.writeAction("bge UDPR_5 0 #45")                                #50 42 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #51 43
    tran1.writeAction("jmp #48")                                        #52 44
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #53 45 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #54 46 fetch v1 from lm
    tran1.writeAction("jmp #37")                                         #55 47 
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #56 48 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #101")                   #57 49 

    #next OB_2
    tran1.writeAction("bgt UDPR_8 OB_2 #66")                             #58 50 if n1 > n2 set walk -1
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_2 #54")                             #63 51
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #64 52
    tran1.writeAction("jmp #73")                                        #65 53 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_2 #73")                            #66 54
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #67 55
    tran1.writeAction("bne UDPR_5 UDPR_1 #59")                          #68 56
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #69 57
    tran1.writeAction("jmp #73")                                        #70 58
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #71 59 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #72 60 fetch v1 from lm
    tran1.writeAction("jmp #51")                                         #73 61
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_2 #65")                            #74 62
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #75 63
    tran1.writeAction("jmp #73")                                        #76 64block 1 - term/yield block
    tran1.writeAction("blt UDPR_8 OB_2 #73")                            #77 65
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #78 66
    tran1.writeAction("bge UDPR_5 0 #70")                                #79 67 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #80 68
    tran1.writeAction("jmp #73")                                        #81 69
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #82 70 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #83 71fetch v1 from lm
    tran1.writeAction("jmp #62")                                         #84 72 
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #85 73 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #101")                   #86  74

    #next OB_3
    tran1.writeAction("bgt UDPR_8 OB_3 #91")                             #87 75 if n1 > n2 set walk -1
    # walk +1 (forward) [loop]
    tran1.writeAction("bne UDPR_8 OB_3 #79")                             #92 76
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #93 77
    tran1.writeAction("jmp #98")                                        #94 78 block 1 - term/yield block
    tran1.writeAction("bgt UDPR_8 OB_3 #98")                            #95 79
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #96 80
    tran1.writeAction("bne UDPR_5 UDPR_1 #84")                          #97 81
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #98 82
    tran1.writeAction("jmp #98")                                        #99 83
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #100 84 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #101 85 fetch v1 from lm
    tran1.writeAction("jmp #76")                                         #102 86 
    #walk -1 (backward)
    tran1.writeAction("bne UDPR_8 OB_3 #90")                            #103 87
    tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #104 88
    tran1.writeAction("jmp #98")                                        #105 89 block 1 - term/yield block
    tran1.writeAction("blt UDPR_8 OB_3 #98")                            #106 90
    tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #107 91
    tran1.writeAction("bge UDPR_5 0 #95")                                #108 92 #y2
    tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #109 93
    tran1.writeAction("jmp #98")                                        #110 94 
    tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #111 95 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #112 96 fetch v1 from lm
    tran1.writeAction("jmp #87")                                         #113 97 
    #<next v2> 
    tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #114 98 #y1
    tran1.writeAction("beq UDPR_6 UDPR_2 #101")                   #115 99
    tran1.writeAction("yield 1")                                        #116 100
    tran1.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 101  #fin
    tran1.writeAction("yield_terminate 4")                              #118 102
    
    #efa.printOut(stage_trace)    

    return efa

def GenerateTriEFA_singlestream_loopopt_block16_cfg(blksize):
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

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
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
    tr_str = "send_old UDPR_7 UDPR_11 UDPR_3 " + blkbytes + " r 1"
    tran0.writeAction(tr_str)               #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                            #12
    tran0.writeAction(tr_str)                           #12
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("mov_imm2reg UDPR_9 0")                           #0 walk = 0
    tran0.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #1 lm addr calculation
    tran0.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #2 fetch v1 from lm
    tran0.writeAction("yield 2")                                        #15

    tran1 = state1.writeTransition("eventCarry", state1, state1, event_map['nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran1.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran1.writeAction(tr_str)                            
        tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran1.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran1.writeAction(tr_str)                            
        tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran1.writeAction(tr_str)                            
        tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran1.writeAction(tr_str)                            
        tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran1.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran1.writeAction(tr_str)                            
        tran1.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran1.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran1.writeAction(tr_str)                            
        tran1.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran1.writeAction(tr_str)                            
        tran1.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran1.writeAction(tr_str)                            
        tran1.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran1.writeAction(tr_str)                            
        #<next v2> 
        tran1.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran1.writeAction(tr_str)                            

    tran1.writeAction("yield 1")                                        #116 100
    tran1.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 101  #fin
    tran1.writeAction("yield_terminate 4")                              #118 102

    #efa.printOut(stage_trace)    

    return efa

def GenerateTriEFA_singlestream_loopopt2_cached_block_cfg(blksize):
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         #1 v1 - LM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #2 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #3 v2 DRAM base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #5 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["v1_nr"]))     #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_13 -1" ) # Lane 1                #9
    
   # Fetch v1 phase
    tran0.writeAction("ble UDPR_1 UDPR_3 #14")                          #10  l1
    tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " +blkbytes + " r 2"       #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #12
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #14 y1
    tran0.writeAction("yield 2")                                        #15

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tr_str = "mov_imm2reg UDPR_5 " + blkbytes                           #0
    tran1.writeAction(tr_str)               
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #1
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #2
    tran1.writeAction(tr_str)               
    tran1.writeAction("ble UDPR_1 UDPR_3 #5")                           #3
    tran1.writeAction("yield 2")                                        #4

    # Fetch v2 phase
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #5 y1
    tran1.writeAction("mov_imm2reg UDPR_7 " + str(event_map["v2_nr"]))  #6   #8 UDPR_9 has event_word for n1
    tran1.writeAction("ble UDPR_2 UDPR_3 #11")                          #7  l1
    tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " + blkbytes + " r 1"      #8  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran1.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #9
    tran1.writeAction(tr_str)               
    tran1.writeAction("jmp #7")                                         #10
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #11 y1
    tran1.writeAction("mov_imm2reg UDPR_4 0")                           #12
    tran1.writeAction("mov_imm2reg UDPR_5 0")                           #13
    tran1.writeAction("mov_imm2reg UDPR_7 0")                           #14 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #15 fetch v1 from lm
    tran1.writeAction("yield 2")                                        #16 
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran2.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran2.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran2.writeAction(tr_str)                            
        #<next v2> 
        tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran2.writeAction(tr_str)                            

    tran2.writeAction("yield 1")                                        #116 100
    tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 101  #fin
    tran2.writeAction("yield_terminate 4")                              #118 102

    #efa.printOut(stage_trace)    

    return efa

def GenerateTriEFA_cached_block_cfg_lm():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         #1 v1 - LM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #2 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #3 v2 DRAM base
    tran0.writeAction("mov_imm2reg UDPR_3 0")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_5 0")                           #5 v1 index 
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["v1_nr"]))     #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_13 -1" ) # Lane 1                #9
    
   # Fetch v1 phase
    tran0.writeAction("ble UDPR_1 UDPR_3 #14")                          #10  l1
    tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " +blkbytes + " r 2"       #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #12
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_ob2reg OB_8 UDPR_10")                        #14 UDPR_10 - base address
    tran0.writeAction("addi UDPR_10 UDPR_3 8")                          #15 add 8 for base of v1
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")                      #16
    tran0.writeAction("yield 2")                                        #17

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tr_str = "mov_imm2reg UDPR_5 " + blkbytes                           #0
    tran1.writeAction(tr_str)               
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #1
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #2
    tran1.writeAction(tr_str)               
    tran1.writeAction("ble UDPR_12 UDPR_3 #5")                           #3
    tran1.writeAction("yield 2")                                        #4

    # Fetch v2 phase
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #5 y1
    tran1.writeAction("mov_imm2reg UDPR_7 " + str(event_map["v2_nr"]))  #6   #8 UDPR_9 has event_word for n1
    tran1.writeAction("ble UDPR_2 UDPR_3 #11")                          #7  l1
    tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " + blkbytes + " r 1"      #8  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran1.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #9
    tran1.writeAction(tr_str)               
    tran1.writeAction("jmp #7")                                         #10
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #11 y1
    #tran1.writeAction("mov_imm2reg UDPR_4 8")                           #12
    tran1.writeAction("addi UDPR_10 UDPR_4 8")                           #12
    tran1.writeAction("mov_imm2reg UDPR_5 0")                           #13
    tran1.writeAction("mov_reg2reg UDPR_4 UDPR_7")                      #14 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #15 fetch v1 from lm
    tran1.writeAction("yield 2")                                        #16 
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran2.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran2.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran2.writeAction(tr_str)                            
        #<next v2> 
        tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran2.writeAction(tr_str)                            

    tran2.writeAction("yield 1")                                        #116 100
    #tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 101  #fin
    tran2.writeAction("addi UDPR_10 UDPR_10 4")                           #27 23 #y1
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #26 Move Tri count
    tran2.writeAction("subi UDPR_10 UDPR_10 4")                           #27 Set status now
    tran2.writeAction("mov_imm2reg UDPR_3 1")                    #26 Move Tri count
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #30 28
    tran2.writeAction("yield_terminate 4")                              #118 102

    #efa.printOut(stage_trace)    

    return efa

def GenerateTriEFA_cached_block_cfg_lm2():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    #tran0.writeAction("mov_ob2reg OB_1 UDPR_1")        #0 v1 size
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         #1 v1 - LM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #2 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #3 v2 DRAM base
    tran0.writeAction("lshift_and_imm OB_5 UDPR_5 2 4294967295")        #4 end offset
    tran0.writeAction("lshift_and_imm OB_1 UDPR_3 2 4294967295")        #5 start offset
    #tran0.writeAction("mov_ob2reg OB_0 UDPR_3")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["v1_nr"]))  #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_13 -1" ) # Lane 1                #9
    
   # Fetch v1 phase
    tran0.writeAction("ble UDPR_5 UDPR_3 #14")                          #10  l1
    tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " +blkbytes + " r 2"       #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #12
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_ob2reg OB_8 UDPR_10")                        #14 UDPR_10 - base address
    tran0.writeAction("addi UDPR_10 UDPR_3 8")                          #15 add 8 for base of v1
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")                      #16
    #tran0.writeAction("mov_imm2reg UDPR_5 0")                           #17 v1 index 
    tran0.writeAction("yield 2")                                        #17

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                      #0
    tr_str = "ble UDPR_5 " + blkbytes + " #3"                             #1
    tran1.writeAction(tr_str)               
    tr_str = "mov_imm2reg UDPR_5 " + blkbytes                           #2
    tran1.writeAction(tr_str)               
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #3
    #tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #4
    tr_str = "add UDPR_3 UDPR_5 UDPR_3 "# + blkbytes                           #4
    tran1.writeAction(tr_str)               
    tran1.writeAction("beq UDPR_12 UDPR_3 #7")                           #5
    tran1.writeAction("yield 2")                                        #6

    # Fetch v2 phase
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #5 7y1
    tran1.writeAction("mov_imm2reg UDPR_7 " + str(event_map["v2_nr"]))  #6   #8 UDPR_9 has event_word for n1
    tran1.writeAction("ble UDPR_2 UDPR_3 #13")                          #7  l1
    tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " + blkbytes + " r 1"      #8  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran1.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #9
    tran1.writeAction(tr_str)               
    tran1.writeAction("jmp #9")                                         #10
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #11 y1
    #tran1.writeAction("mov_imm2reg UDPR_4 8")                           #12
    tran1.writeAction("addi UDPR_10 UDPR_4 8")                           #12
    tran1.writeAction("mov_imm2reg UDPR_5 0")                           #13
    tran1.writeAction("mov_reg2reg UDPR_4 UDPR_7")                      #14 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #15 fetch v1 from lm
    tran1.writeAction("yield 2")                                        #16 
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran2.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran2.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran2.writeAction(tr_str)                            
        #<next v2> 
        tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran2.writeAction(tr_str)                            

    tran2.writeAction("yield 1")                                        #116 100
    #tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 101  #fin
    tran2.writeAction("addi UDPR_10 UDPR_10 4")                           #27 23 #y1
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #26 Move Tri count
    tran2.writeAction("subi UDPR_10 UDPR_10 4")                           #27 Set status now
    tran2.writeAction("mov_imm2reg UDPR_3 1")                    #26 Move Tri count
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #30 28
    tran2.writeAction("yield_terminate 4")                              #118 102

    #efa.printOut(stage_trace)    

    return efa

def GenerateTriEFA_cached_multievent_fix():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    #tran0.writeAction("mov_ob2reg OB_1 UDPR_1")        #0 v1 size
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         #1 v1 - LM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #2 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #3 v2 DRAM base
    tran0.writeAction("lshift_and_imm OB_5 UDPR_5 2 4294967295")        #4 end offset
    tran0.writeAction("lshift_and_imm OB_1 UDPR_3 2 4294967295")        #5 start offset
    #tran0.writeAction("mov_ob2reg OB_0 UDPR_3")                           #4 TC / iterator
    tran0.writeAction("mov_ob2reg OB_8 UDPR_10")                        #6 UDPR_10 - base address
    tran0.writeAction("beq OB_9 1 block_1")                             #7 If Cached jump 
    
   # Fetch v1 phase
    tran0.writeAction("ble UDPR_5 UDPR_3 #12")                          #8  l1
    #tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " +blkbytes + " r 2"      #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v1_nr"]) + " " + blkbytes + " 1"       #9  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #10
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #8")                                        #11
    tran0.writeAction("addi UDPR_10 UDPR_3 8")                          #12 add 8 for base of v1
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")                      #13
    tran0.writeAction("yield 2")                                        #14

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                      #0
    tr_str = "ble UDPR_5 " + blkbytes + " #3"                           #1
    tran1.writeAction(tr_str)               
    tr_str = "mov_imm2reg UDPR_5 " + blkbytes                           #2
    tran1.writeAction(tr_str)               
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #3
    tr_str = "add UDPR_3 UDPR_5 UDPR_3 "# + blkbytes                    #4
    tran1.writeAction(tr_str)               
    tran1.writeAction("beq UDPR_12 UDPR_3 block_1")                     #5
    tran1.writeAction("yield 2")                                        #6


    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #0 7y1
    efa.appendBlockAction("block_1","ble UDPR_2 UDPR_3 #5")                          #1  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v2_nr"]) + " " + blkbytes + " 0"  #2  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    efa.appendBlockAction("block_1",tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                                         #3
    efa.appendBlockAction("block_1",tr_str)               
    efa.appendBlockAction("block_1","jmp #1")                                         #4
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #5 y1
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_4 8")                          #6
    efa.appendBlockAction("block_1","addi UDPR_10 UDPR_4 8")                          #7
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_5 0")                           #8
    efa.appendBlockAction("block_1","mov_reg2reg UDPR_4 UDPR_7")                      #9 lm addr calculation
    efa.appendBlockAction("block_1","mov_lm2reg UDPR_7 UDPR_8 4")                     #10 fetch v1 from lm
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_6 0")                           #11 v2 index 
    efa.appendBlockAction("block_1","yield 2")                                                  #12 
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran2.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran2.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran2.writeAction(tr_str)                            
        #<next v2> 
        tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+4))                    #28 24
        tran2.writeAction(tr_str)                            
    
    tran2.writeAction("addi UDPR_10 UDPR_7 8")                          #116 29 add 8 for base of v1
    tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 30 117  21 fetch v1 from lm
    tran2.writeAction("mov_imm2reg UDPR_5 0")                           #8
    tran2.writeAction("yield 1")                                        #116 31 118 100

    #tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 119 101  #fin
    tran2.writeAction("addi UDPR_10 UDPR_10 4")                         #27 23 32 #y1
    tran2.writeAction("mov_lm2reg UDPR_10 UDPR_5 4")                    #26 Move Tri count
    tran2.writeAction("add UDPR_5 UDPR_3 UDPR_3")                       #26 Move Tri count
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #26 Move Tri count
    tran2.writeAction("subi UDPR_10 UDPR_10 4")                           #27 Set status now
    tran2.writeAction("mov_lm2reg UDPR_10 UDPR_3 4")                    #26 Move Tri count
    tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #26 Move Tri count # Update the threads completed
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #30 28
    tran2.writeAction("yield_terminate 4")                              #118 102

    #efa.printOut(stage_trace)    

    return efa

def GenerateTriEFA_cached_multievent():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    """
        OB_0: v1:start_offset, - UDPR_3
        OB_1: v1:size, - UDPR_1, UDPR_5 = UDPR_3+UDPR_1
        OB_2: v1_l - EAR_1l
        OB_3: v1_h - EAR_1h
        OB_4: v2.size - UDPR_2
        OB_5: LM_offset
        OB_6: v2_l - EAR0l
        OB_7: v2_h - EAR0h
        UDPR_11 - Bank[0] (Lane ID * 65536)
        UDPR_10 - TC per thread
    """
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_3 2 4294967295")        #0 start offset
    tran0.writeAction("lshift_and_imm OB_1 UDPR_1 2 4294967295")        #1 v1 size
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_5")                       #2 end offset
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                        #3 v1 DRAM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #4 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #5 v2 DRAM base
    tran0.writeAction("mov_ob2reg OB_5 UDPR_10")                        #6 UDPR_10 - base address
    #tran0.writeAction("mov_ob2reg OB_5 UDPR_9")                         #7 num thread 
    #tran0.writeAction("lshift_and_imm LID UDPR_11 16 4294967295")       #7 start offset LID * 65536

    # set the status 
    #tran0.writeAction("mov_lm2reg UDPR_1 UDPR_7 4")                    #9 move status to UDP
    #tran0.writeAction("bitclr UDPR_7 UDPR_9 UDPR_7")                    #10 move status to UDP
    #tran0.writeAction("mov_reg2lm UDPR_7 UDPR_11 4")                    #11 move status to LM
    
   # Fetch v1 phase
    tran0.writeAction("ble UDPR_5 UDPR_3 #11")                          #7  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v1_nr"]) + " " + blkbytes + " 1"   #8  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #9
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #7")                                        #10
    tran0.writeAction("addi UDPR_10 UDPR_3 8")                          #11 add 8 for base of v1
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")                      #12
    tran0.writeAction("yield 2")                                        #13

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                      #0
    tr_str = "ble UDPR_5 " + blkbytes + " #3"                           #1
    tran1.writeAction(tr_str)               
    tr_str = "mov_imm2reg UDPR_5 " + blkbytes                           #2
    tran1.writeAction(tr_str)               
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #3
    tr_str = "add UDPR_3 UDPR_5 UDPR_3 "# + blkbytes                    #4
    tran1.writeAction(tr_str)               
    tran1.writeAction("beq UDPR_12 UDPR_3 block_1")                     #5
    tran1.writeAction("yield 2")                                        #6


    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #0 7y1
    efa.appendBlockAction("block_1","ble UDPR_2 UDPR_3 #5")                          #1  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v2_nr"]) + " " + blkbytes + " 0"  #2  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    efa.appendBlockAction("block_1",tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                                         #3
    efa.appendBlockAction("block_1",tr_str)               
    efa.appendBlockAction("block_1","jmp #1")                                         #4
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #5 TC = 0
    efa.appendBlockAction("block_1","addi UDPR_10 UDPR_4 8")                          #6 LM base addr
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_5 0")                           #7 v1 counter = 0
    efa.appendBlockAction("block_1","mov_reg2reg UDPR_4 UDPR_7")                      #8 lm addr calculation
    efa.appendBlockAction("block_1","mov_lm2reg UDPR_7 UDPR_8 4")                     #9 fetch v1 from lm
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_6 0")                           #10 v2 counter = 0 
    efa.appendBlockAction("block_1","yield 2")                                        #11 
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran2.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran2.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran2.writeAction(tr_str)                            
        #<next v2> 
        tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran2.writeAction(tr_str)                            

    tran2.writeAction("yield 1")                                        #116 100
    tran2.writeAction("addi UDPR_10 UDPR_10 4")                         #26 23 #y1
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #27 Move Tri count
    tran2.writeAction("subi UDPR_10 UDPR_10 4")                         #28 Set status now
    tran2.writeAction("mov_imm2reg UDPR_3 1")                           #29 Move Tri count
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #30
    tran2.writeAction("yield_terminate 4")                              #31

    #efa.printOut(stage_trace)    

    return efa

def GenerateTriEFA_cached_repeat():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    """
        OB_0: v1:start_offset, - UDPR_3
        OB_1: v1:size, - UDPR_1, UDPR_5 = UDPR_3+UDPR_1
        OB_2: v1_l - EAR_1l
        OB_3: v1_h - EAR_1h
        OB_4: v2.size - UDPR_2
        OB_5: LM_offset
        OB_6: v2_l - EAR0l
        OB_7: v2_h - EAR0h
        OB_8: repeat
        UDPR_11 - Bank[0] (Lane ID * 65536)
        UDPR_10 - TC per thread
    """
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_3 2 4294967295")        #0 start offset
    tran0.writeAction("lshift_and_imm OB_1 UDPR_1 2 4294967295")        #1 v1 size
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_5")                       #2 end offset
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                        #3 v1 DRAM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #4 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #5 v2 DRAM base
    tran0.writeAction("mov_ob2reg OB_5 UDPR_10")                        #6 UDPR_10 - base address
    #tran0.writeAction("mov_ob2reg OB_5 UDPR_9")                         #7 num thread 
    #tran0.writeAction("lshift_and_imm LID UDPR_11 16 4294967295")       #7 start offset LID * 65536

    # set the status 
    #tran0.writeAction("mov_lm2reg UDPR_1 UDPR_7 4")                    #9 move status to UDP
    #tran0.writeAction("bitclr UDPR_7 UDPR_9 UDPR_7")                    #10 move status to UDP
    #tran0.writeAction("mov_reg2lm UDPR_7 UDPR_11 4")                    #11 move status to LM
    
   # Fetch v1 phase
    tran0.writeAction("ble UDPR_5 UDPR_3 #11")                          #7  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v1_nr"]) + " " + blkbytes + " 1"   #8  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #9
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #7")                                        #10
    tran0.writeAction("addi UDPR_10 UDPR_3 8")                          #11 add 8 for base of v1
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")                      #12
    tran0.writeAction("mov_ob2reg OB_8 UDPR_13")                        #13 - repeat count
    tran0.writeAction("mov_imm2reg UDPR_14 0")                        #13 - repeat count
    tran0.writeAction("yield 2")                                        #14 

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tran1.writeAction("beq UDPR_14 1 block_1")                          #0
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                      #1
    tr_str = "ble UDPR_5 " + blkbytes + " #4"                           #2
    tran1.writeAction(tr_str)               
    tr_str = "mov_imm2reg UDPR_5 " + blkbytes                           #3
    tran1.writeAction(tr_str)               
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #4
    tr_str = "add UDPR_3 UDPR_5 UDPR_3 "# + blkbytes                    #5
    tran1.writeAction(tr_str)               
    tran1.writeAction("beq UDPR_12 UDPR_3 block_1")                     #6
    tran1.writeAction("yield 2")                                        #7


    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #0 7y1
    efa.appendBlockAction("block_1","ble UDPR_2 UDPR_3 #5")                          #1  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v2_nr"]) + " " + blkbytes + " 0"  #2  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    efa.appendBlockAction("block_1",tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                                         #3
    efa.appendBlockAction("block_1",tr_str)               
    efa.appendBlockAction("block_1","jmp #1")                                         #4
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #5 TC = 0
    efa.appendBlockAction("block_1","addi UDPR_10 UDPR_4 8")                          #6 LM base addr
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_5 0")                           #7 v1 counter = 0
    efa.appendBlockAction("block_1","mov_reg2reg UDPR_4 UDPR_7")                      #8 lm addr calculation
    efa.appendBlockAction("block_1","mov_lm2reg UDPR_7 UDPR_8 4")                     #9 fetch v1 from lm
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_6 0")                           #10 v2 counter = 0 
    efa.appendBlockAction("block_1","yield 2")                                        #11 
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran2.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran2.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran2.writeAction(tr_str)                            
        #<next v2> 
        tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran2.writeAction(tr_str)                            

    tran2.writeAction("yield 1")                                        #116 100
    tran2.writeAction("subi UDPR_13 UDPR_13 1")                        #26 reduce repeat cnt
    tran2.writeAction("mov_imm2reg UDPR_14 1")
    tran2.writeAction("bne UDPR_13 0 block_1") # + str(int(25*blksize/4+6)))                            
    tran2.writeAction("addi UDPR_10 UDPR_10 4")                         #26 23 #y1
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #27 Move Tri count
    tran2.writeAction("subi UDPR_10 UDPR_10 4")                         #28 Set status now
    tran2.writeAction("mov_imm2reg UDPR_3 1")                           #29 Move Tri count
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #30
    tran2.writeAction("yield_terminate 4")                              #31

    #efa.printOut(stage_trace)    

    return efa


def GenerateTriEFA_cached_multievent_bitstat():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    """
        OB_0: v1:start_offset, - UDPR_3
        OB_1: v1:size, - UDPR_1, UDPR_5 = UDPR_3+UDPR_1
        OB_2: v1_l - EAR_1l
        OB_3: v1_h - EAR_1h
        OB_4: v2.size - UDPR_2
        OB_5: thread_num
        OB_6: v2_l - EAR0l
        OB_7: v2_h - EAR0h
        OB_8: LM_offset - UDPR_10 
        UDPR_11 - Bank[0] (Lane ID * 65536)
        UDPR_10 - TC per thread
    """
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_3 2 4294967295")        #0 start offset
    tran0.writeAction("lshift_and_imm OB_1 UDPR_1 2 4294967295")        #1 v1 size
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_5")                       #2 end offset
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                        #3 v1 DRAM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #4 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #5 v2 DRAM base
    tran0.writeAction("mov_ob2reg OB_8 UDPR_10")                        #6 UDPR_10 - base address
    tran0.writeAction("mov_ob2reg OB_5 UDPR_9")                         #7 num thread 
    tran0.writeAction("lshift_and_imm LID UDPR_11 16 4294967295")       #8 start offset LID * 65536

    # set the status 
    tran0.writeAction("mov_lm2reg UDPR_11 UDPR_7 4")                    #9 move status to UDP
    tran0.writeAction("bitclr UDPR_7 UDPR_9 UDPR_7")                    #10 move status to UDP
    tran0.writeAction("mov_reg2lm UDPR_7 UDPR_11 4")                    #11 move status to LM
    
   # Fetch v1 phase
    tran0.writeAction("ble UDPR_5 UDPR_3 #16")                          #12  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v1_nr"]) + " " + blkbytes + " 1"   #13  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #14
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #12")                                        #15
    tran0.writeAction("addi UDPR_10 UDPR_3 4")                          #16 add 8 for base of v1
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")                      #17
    tran0.writeAction("yield 2")                                        #18

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tran1.writeAction("beq UDPR_14 1 block_1")                          #0
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                      #1
    tr_str = "ble UDPR_5 " + blkbytes + " #4"                           #2
    tran1.writeAction(tr_str)               
    tr_str = "mov_imm2reg UDPR_5 " + blkbytes                           #3
    tran1.writeAction(tr_str)               
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #4
    tr_str = "add UDPR_3 UDPR_5 UDPR_3 "# + blkbytes                    #5
    tran1.writeAction(tr_str)               
    tran1.writeAction("beq UDPR_12 UDPR_3 block_1")                     #6
    tran1.writeAction("yield 2")                                        #7


    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #0 7y1
    efa.appendBlockAction("block_1","ble UDPR_2 UDPR_3 #5")                          #1  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v2_nr"]) + " " + blkbytes + " 0"  #2  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    efa.appendBlockAction("block_1",tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                                         #3
    efa.appendBlockAction("block_1",tr_str)               
    efa.appendBlockAction("block_1","jmp #1")                                         #4
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #5 TC = 0
    efa.appendBlockAction("block_1","addi UDPR_10 UDPR_4 8")                          #6 LM base addr
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_5 0")                           #7 v1 counter = 0
    efa.appendBlockAction("block_1","mov_reg2reg UDPR_4 UDPR_7")                      #8 lm addr calculation
    efa.appendBlockAction("block_1","mov_lm2reg UDPR_7 UDPR_8 4")                     #9 fetch v1 from lm
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_6 0")                           #10 v2 counter = 0 
    efa.appendBlockAction("block_1","yield 2")                                        #11 
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran2.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran2.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran2.writeAction(tr_str)                            
        #<next v2> 
        tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran2.writeAction(tr_str)                            

    tran2.writeAction("yield 1")                                        #116 100
    tran2.writeAction("subi UDPR_13 UDPR_13 1")                        #26 reduce repeat cnt
    tran2.writeAction("mov_imm2reg UDPR_14 1")
    tran2.writeAction("bne UDPR_13 0 block_1") # + str(int(25*blksize/4+6)))                            
    tran2.writeAction("addi UDPR_10 UDPR_10 4")                         #26 23 #y1
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #27 Move Tri count
    tran2.writeAction("subi UDPR_10 UDPR_10 4")                         #28 Set status now
    tran2.writeAction("mov_imm2reg UDPR_3 1")                           #29 Move Tri count
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #30
    tran2.writeAction("yield_terminate 4")                              #31

    #efa.printOut(stage_trace)    

    return efa


def GenerateTriEFA_cached_multievent_bitstat():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    """
        OB_0: v1:start_offset, - UDPR_3
        OB_1: v1:size, - UDPR_1, UDPR_5 = UDPR_3+UDPR_1
        OB_2: v1_l - EAR_1l
        OB_3: v1_h - EAR_1h
        OB_4: v2.size - UDPR_2
        OB_5: thread_num
        OB_6: v2_l - EAR0l
        OB_7: v2_h - EAR0h
        OB_8: LM_offset - UDPR_10 
        UDPR_11 - Bank[0] (Lane ID * 65536)
        UDPR_10 - TC per thread
    """
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_3 2 4294967295")        #0 start offset
    tran0.writeAction("lshift_and_imm OB_1 UDPR_1 2 4294967295")        #1 v1 size
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_5")                       #2 end offset
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                        #3 v1 DRAM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #4 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #5 v2 DRAM base
    tran0.writeAction("mov_ob2reg OB_8 UDPR_10")                        #6 UDPR_10 - base address
    tran0.writeAction("mov_ob2reg OB_5 UDPR_9")                         #7 num thread 
    tran0.writeAction("lshift_and_imm LID UDPR_11 16 4294967295")       #8 start offset LID * 65536

    # set the status 
    tran0.writeAction("mov_lm2reg UDPR_11 UDPR_7 4")                    #9 move status to UDP
    tran0.writeAction("bitclr UDPR_7 UDPR_9 UDPR_7")                    #10 move status to UDP
    tran0.writeAction("mov_reg2lm UDPR_7 UDPR_11 4")                    #11 move status to LM
    
   # Fetch v1 phase
    tran0.writeAction("ble UDPR_5 UDPR_3 #16")                          #12  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v1_nr"]) + " " + blkbytes + " 1"   #13  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #14
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #12")                                        #15
    tran0.writeAction("addi UDPR_10 UDPR_3 4")                          #16 add 8 for base of v1
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")                      #17
    tran0.writeAction("yield 2")                                        #18

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                      #0
    tr_str = "ble UDPR_5 " + blkbytes + " #3"                           #1
    tran1.writeAction(tr_str)               
    tr_str = "mov_imm2reg UDPR_5 " + blkbytes                           #2
    tran1.writeAction(tr_str)               
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #3
    tr_str = "add UDPR_3 UDPR_5 UDPR_3 "# + blkbytes                    #4
    tran1.writeAction(tr_str)               
    tran1.writeAction("beq UDPR_12 UDPR_3 block_1")                     #5
    tran1.writeAction("yield 2")                                        #6


    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #0 7y1
    efa.appendBlockAction("block_1","ble UDPR_2 UDPR_3 #5")                          #1  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v2_nr"]) + " " + blkbytes + " 0"  #2  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    efa.appendBlockAction("block_1",tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                                         #3
    efa.appendBlockAction("block_1",tr_str)               
    efa.appendBlockAction("block_1","jmp #1")                                         #4
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #5 TC = 0
    efa.appendBlockAction("block_1","addi UDPR_10 UDPR_4 4")                          #6 LM base addr
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_5 0")                           #7 v1 counter = 0
    efa.appendBlockAction("block_1","mov_reg2reg UDPR_4 UDPR_7")                      #8 lm addr calculation
    efa.appendBlockAction("block_1","mov_lm2reg UDPR_7 UDPR_8 4")                     #9 fetch v1 from lm
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_6 0")                           #10 v2 counter = 0 
    efa.appendBlockAction("block_1","yield 2")                                        #11 
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran2.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran2.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran2.writeAction(tr_str)                            
        #<next v2> 
        tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran2.writeAction(tr_str)                            

    tran2.writeAction("yield 1")                                        #116 100
<<<<<<< HEAD
    #tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 101  #fin
=======
    #tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                  #117 101  #fin
>>>>>>> pagerank
    #tran2.writeAction("addi UDPR_10 UDPR_10 4")                         #27 23 #y1
    #tran2.writeAction("mov_lm2reg UDPR_10 UDPR_5 4")                    #26 Move Tri count
    #tran2.writeAction("add UDPR_5 UDPR_3 UDPR_3")                       #26 Move Tri count
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #118 26 Move Tri count
    #tran2.writeAction("subi UDPR_10 UDPR_10 4")                           #27 Set status now
    tran2.writeAction("mov_lm2reg UDPR_11 UDPR_3 4")                    #119 26 Move Tri count
    tran2.writeAction("bitset UDPR_3 UDPR_9 UDPR_3")                    #120       #26 Move Tri count # Update the threads completed
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #121 28
    tran2.writeAction("yield_terminate 4")                              #122 102

    #efa.printOut(stage_trace)    

    return efa

def GenerateTriEFA_cachedfirst_multievent():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
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
        'v1_nr':1,
        'v2_nr':2,
        'tc':3
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    #tran0.writeAction("mov_ob2reg OB_1 UDPR_1")        #0 v1 size
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         #1 v1 - LM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #2 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #3 v2 DRAM base
    tran0.writeAction("lshift_and_imm OB_5 UDPR_5 2 4294967295")        #4 end offset
    tran0.writeAction("lshift_and_imm OB_1 UDPR_3 2 4294967295")        #5 start offset
    #tran0.writeAction("mov_ob2reg OB_0 UDPR_3")                           #4 TC / iterator
    tran0.writeAction("mov_ob2reg OB_8 UDPR_10")                        #6 UDPR_10 - base address
    tran0.writeAction("beq OB_9 1 block_1")                             #7 If Cached jump 
    
   # Fetch v1 phase
    tran0.writeAction("ble UDPR_5 UDPR_3 #12")                          #8  l1
    #tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " +blkbytes + " r 2"      #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v1_nr"]) + " " + blkbytes + " 1"       #9  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #10
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #8")                                        #11
    tran0.writeAction("addi UDPR_10 UDPR_3 8")                          #12 add 8 for base of v1
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")                      #13
    tran0.writeAction("yield 2")                                        #14

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                      #0
    tr_str = "ble UDPR_5 " + blkbytes + " #3"                           #1
    tran1.writeAction(tr_str)               
    tr_str = "mov_imm2reg UDPR_5 " + blkbytes                           #2
    tran1.writeAction(tr_str)               
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #3
    tr_str = "add UDPR_3 UDPR_5 UDPR_3 "# + blkbytes                    #4
    tran1.writeAction(tr_str)               
    tran1.writeAction("beq UDPR_12 UDPR_3 block_1")                     #5
    tran1.writeAction("mov_imm2reg UDPR_3 1")
    tran1.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #30 28
    tran1.writeAction("yield_terminate 2")                                        #6


    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #0 7y1
    efa.appendBlockAction("block_1","ble UDPR_2 UDPR_3 #5")                          #1  l1
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v2_nr"]) + " " + blkbytes + " 0"  #2  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    efa.appendBlockAction("block_1",tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                                         #3
    efa.appendBlockAction("block_1",tr_str)               
    efa.appendBlockAction("block_1","jmp #1")                                         #4
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_3 0")                           #5 y1
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_4 8")                          #6
    efa.appendBlockAction("block_1","addi UDPR_10 UDPR_4 8")                          #7
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_5 0")                           #8
    efa.appendBlockAction("block_1","mov_reg2reg UDPR_4 UDPR_7")                      #9 lm addr calculation
    efa.appendBlockAction("block_1","mov_lm2reg UDPR_7 UDPR_8 4")                     #10 fetch v1 from lm
    efa.appendBlockAction("block_1","mov_imm2reg UDPR_6 0")                           #11 v2 index 
    efa.appendBlockAction("block_1","yield 2")                                                  #12 
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran2.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran2.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran2.writeAction(tr_str)                            
        #<next v2> 
        tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran2.writeAction(tr_str)                            

    tran2.writeAction("yield 1")                                        #116 100
    #tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 101  #fin
    tran2.writeAction("addi UDPR_10 UDPR_10 4")                         #27 23 #y1
    tran2.writeAction("mov_lm2reg UDPR_10 UDPR_5 4")                    #26 Move Tri count
    tran2.writeAction("add UDPR_5 UDPR_3 UDPR_3")                       #26 Move Tri count
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #26 Move Tri count
    tran2.writeAction("subi UDPR_10 UDPR_10 4")                           #27 Set status now
    tran2.writeAction("mov_lm2reg UDPR_10 UDPR_3 4")                    #26 Move Tri count
    tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #26 Move Tri count # Update the threads completed
    tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #30 28
    tran2.writeAction("yield_terminate 4")                              #118 102

    #efa.printOut(stage_trace)    

    return efa



def GenerateTriEFA_master_cfg():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() #tri Count State
    efa.add_state(state1)
    state2 = State() #tri Count State
    efa.add_state(state2)

    #Add events to dictionary 
    event_map = {
        'vr':2,
        'v1_nr':3,
        'v2_nr':4,
        'mas_v':0,
        'mas_tc':1
    }

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    lmbank_size = 65536

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['mas_v'])
    tran3.writeAction("mov_ob2reg OB_0 UDPR_6")  #0 num pairs
    tran3.writeAction("mov_ob2reg OB_1 UDPR_5")  #1 UDPR_5 LM Base addr for vertex pairs
    tran3.writeAction("mov_ob2reg OB_2 UDPR_9")  #2 UDPR_9 num lanes 
    tran3.writeAction("mov_reg2reg UDPR_5 UDPR_8")  #3 Copy of base addr
    tran3.writeAction("mov_imm2reg UDPR_1 1") #4 UDPR_2 // lane_num to launch
    tran3.writeAction("ev_update_2 UDPR_7 " + str(event_map['vr']) +" 255 5") # 5
    tran3.writeAction("ev_update_reg_2 UDPR_7 UDPR_4 UDPR_1 UDPR_1 8") # 6 UDPR_7 event_word
    tran3.writeAction("send_wret UDPR_4 UDPR_1 " + str(event_map['mas_tc']) + " UDPR_5 32")      # 7 read edge {from_id, to_id, weight}
    tran3.writeAction("addi UDPR_1 UDPR_1 1") # 8 increment the lane_num
    tran3.writeAction("addi UDPR_5 UDPR_5 32") # 9 increment the offset
    tran3.writeAction("subi UDPR_6 UDPR_6 1") #10 decrement the num_pairs
    tran3.writeAction("beq UDPR_6 0 #13") #11
    tran3.writeAction("blt UDPR_1 UDPR_9 #6") #12 
    tran3.writeAction("mov_imm2reg UDPR_3 0") # 13 Tricount
    tran3.writeAction("mov_imm2reg UDPR_10 0") #14 tricount result location in LM
    tran3.writeAction("yield 2") # 15 no more lanes to launch yield and wait
    
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['mas_tc'])
    tran4.writeAction("mov_lm2reg UDPR_10 UDPR_6 4")  #0 fetch v1 from lm
    tran4.writeAction("add OB_0 UDPR_3 UDPR_3") #1 Update tricount 
    tran4.writeAction("subi UDPR_6 UDPR_6 1") #2 9 decrement the num_pairs
    tran4.writeAction("beq UDPR_6 0 #12") #3
    tran4.writeAction("mov_reg2lm UDPR_6 UDPR_10 4")  #4 Move Tri count to LM
    tran4.writeAction("mov_ob2reg OB_1 UDPR_1") #5 this is lane number?
    tran4.writeAction("ev_update_reg_2 UDPR_7 UDPR_4 UDPR_1 UDPR_1 8") # 6 UDPR_7 event_label, UDPR_4 event_word UDPR_1 - lane_id
    tran4.writeAction("send_wret UDPR_4 UDPR_1 " + str(event_map['mas_tc']) + " UDPR_5 32")  #7 read edge {from_id, to_id, weight}
    tran4.writeAction("addi UDPR_5 UDPR_5 32") # 8 increment the offset
    tran4.writeAction("blt UDPR_5 65516 #11") # 9 If not equal proceed
    tran4.writeAction("mov_reg2reg UDPR_8 UDPR_5") #10 go back to base
    tran4.writeAction("yield 2") #11 no more lanes to launch yield and wait
    
    tran4.writeAction("addi UDPR_10 UDPR_10 4")       #12 Set status now
    tran4.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")  #13 Move Tri count to LM
    tran4.writeAction("subi UDPR_10 UDPR_10 4")       #14 Set status now
    #tran4.writeAction("mov_imm2reg UDPR_3 1")         #12 Move status 
    tran4.writeAction("mov_reg2lm UDPR_6 UDPR_10 4")  #15 
    tran4.writeAction("yield_terminate 4")            #16 


    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['vr'])
    tran0.writeAction("lshift_and_imm OB_0 UDPR_1 2 4294967295")        #0 v1 size
    #tran0.writeAction("mov_ob2reg OB_1 UDPR_1")        #0 v1 size
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         #1 v1 - LM base
    tran0.writeAction("lshift_and_imm OB_4 UDPR_2 2 4294967295")        #2 v2 size 
    tran0.writeAction("mov_ob2ear OB_6_7 EAR_0")                        #3 v2 DRAM base
    tran0.writeAction("lshift_and_imm OB_5 UDPR_5 2 4294967295")        #4 end offset
    tran0.writeAction("lshift_and_imm OB_1 UDPR_3 2 4294967295")        #5 start offset
    #tran0.writeAction("mov_ob2reg OB_0 UDPR_3")                           #4 TC / iterator
    tran0.writeAction("mov_imm2reg UDPR_6 0")                           #6 v2 index 
    tran0.writeAction("rshift_and_imm TS UDPR_7 0 16711680")            #7 Extract TID for event_word
    tran0.writeAction("addi UDPR_7 UDPR_7 " + str(event_map["v1_nr"]))  #8 UDPR_9 has event_word for n1
    tran0.writeAction("mov_imm2reg UDPR_13 -1" ) # Lane 1                #9
    
   # Fetch v1 phase
    tran0.writeAction("ble UDPR_5 UDPR_3 #14")                          #10  l1
    tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " +blkbytes + " r 2"       #11  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #12
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp #10")                                        #13
    tran0.writeAction("mov_imm2reg UDPR_3 0")                        #14 UDPR_10 - base address
    #tran0.writeAction("addi UDPR_10 UDPR_3 8")                          #15 add 8 for base of v1
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")                      #16
    #tran0.writeAction("mov_imm2reg UDPR_5 0")                           #17 v1 index 
    tran0.writeAction("yield 2")                                        #17

    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_nr'])
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                      #0
    tr_str = "ble UDPR_5 " + blkbytes + " #3"                             #1
    tran1.writeAction(tr_str)               
    tr_str = "mov_imm2reg UDPR_5 " + blkbytes                           #2
    tran1.writeAction(tr_str)               
    tran1.writeAction("copy_ob_lm OB_0 UDPR_3 UDPR_5")                  #3
    #tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #4
    tr_str = "add UDPR_3 UDPR_5 UDPR_3 "# + blkbytes                           #4
    tran1.writeAction(tr_str)               
    tran1.writeAction("beq UDPR_12 UDPR_3 #7")                           #5
    tran1.writeAction("yield 2")                                        #6

    # Fetch v2 phase
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #7 7y1
    tran1.writeAction("mov_imm2reg UDPR_7 " + str(event_map["v2_nr"]))  #8   #8 UDPR_9 has event_word for n1
    tran1.writeAction("ble UDPR_2 UDPR_3 #13")                          #9  l1
    tr_str = "send_old UDPR_7 UDPR_13 UDPR_3 " + blkbytes + " r 1"      #10  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran1.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #11
    tran1.writeAction(tr_str)               
    tran1.writeAction("jmp #9")                                         #12
    tran1.writeAction("mov_imm2reg UDPR_3 0")                           #13 y1
    tran1.writeAction("mov_imm2reg UDPR_4 0")                           #12
    #tran1.writeAction("addi UDPR_10 UDPR_4 8")                           #12
    tran1.writeAction("mov_imm2reg UDPR_5 0")                           #13
    tran1.writeAction("mov_reg2reg UDPR_4 UDPR_7")                      #14 lm addr calculation
    tran1.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #15 fetch v1 from lm
    tran1.writeAction("yield 2")                                        #16 
    
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_nr'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran2.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran2.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran2.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran2.writeAction(tr_str)                            
        tran2.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran2.writeAction(tr_str)                            
        tran2.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran2.writeAction(tr_str)                            
        tran2.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran2.writeAction(tr_str)                            
        #<next v2> 
        tran2.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran2.writeAction(tr_str)                            

    tran2.writeAction("yield 1")                                        #116 100
    #tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 101  #fin
    tran2.writeAction("send4_reply UDPR_3 LID") # 117return tricount, lane_id
    #tran2.writeAction("addi UDPR_10 UDPR_10 4")                           #27 23 #y1
    #tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #26 Move Tri count
    #tran2.writeAction("subi UDPR_10 UDPR_10 4")                           #27 Set status now
    #tran2.writeAction("mov_imm2reg UDPR_3 1")                    #26 Move Tri count
    #tran2.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #30 28
    tran2.writeAction("yield_terminate 4")                              #118 102

    #efa.printOut(stage_trace)    

    return efa


if __name__=="__main__":
    efa = GenerateTriEFA()
    #efa.printOut(error)
    

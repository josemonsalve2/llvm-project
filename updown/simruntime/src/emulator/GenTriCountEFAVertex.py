from EFA import *

def GenerateTriEFA():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    vsize=str(16)
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() #tri Count State
    efa.add_state(state1)
    state2 = State() #tri Count State
    efa.add_state(state2)

    #Add events to dictionary 
    event_map = {
        'v1_launch':0,
        'nv1_return':1,
        'v2_return':2,
        'nv2_return':3
    }

    """
        v1_launch: OB_0_1:vertex_list_base ,OB_2_3:v1_neigh OB_4:start, OB_5: end, OB_6:LM_base addr
        nv1_return: OB_0-OB_15 - n(v1)
        v2_return: OB_0: ID OB_1: size OB_2_3: neigh
        nv2_return: OB_0-OB_15 - n(v2)   
    """

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_launch'])
    # Create the thread context
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                        # EAR0 - vertexlist ptr! 
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                        # EAR1 - v1 neighlist ptr 
    tran0.writeAction("lshift_and_imm OB_4 UDPR_1 2 4294967295")        # v1 start_offset
    tran0.writeAction("lshift_and_imm OB_5 UDPR_2 2 4294967295")        # v1 end offset
    tran0.writeAction("mov_ob2reg OB_6 UDPR_10")                        # LM Base address
    tran0.writeAction("sub UDPR_2 UDPR_1 UDPR_4")                     # v1 size (in bytes)
    tran0.writeAction("mov_reg2reg UDPR_1 UDPR_3")                     # UDPR_3 - temp variable
    tran0.writeAction("addi UDPR_10 UDPR_9 8")                     # UDPR_9 pointer over v1
    
    # Fetch v1 neighborlist
    tran0.writeAction("nv1loop: ble UDPR_2 UDPR_3 nv1done")               # check if past UDPR_3
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["nv1_return"]) + " " + blkbytes + " 1"  #fetch v1 neighbors
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #increment by number of bytes fetched
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp nv1loop")                                      #goto loop1 until all fetched
    tran0.writeAction("nv1done: addi UDPR_10 UDPR_3 8")                 #12 start offset on LM
    tran0.writeAction("mov_reg2reg UDPR_4 UDPR_1")                      #13 end offset on LM
    tran0.writeAction("mov_reg2reg UDPR_9 UDPR_4")                     # UDPR_9 pointer over v1
    tran0.writeAction("add UDPR_1 UDPR_9 UDPR_12")                      #13 end offset on LM
    tran0.writeAction("yield 2")                                        #14

    # Move v1 neighborlist to LM
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['nv1_return'])
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


    # Fetch v2 from memory
    efa.appendBlockAction("block_1","beq UDPR_9 UDPR_12 alldone")       # check v1 iterator
    efa.appendBlockAction("block_1","mov_lm2reg UDPR_9 UDPR_3 4")       # get next neighbor ID
    #efa.appendBlockAction("block_1", "print 'Lane:%d v1:%d' LID UDPR_3") # Helper function for print
    efa.appendBlockAction("block_1","lshift UDPR_3 UDPR_3 4")           # calculate offset - ID*16
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v2_return"]) + " " + vsize + " 0" # Fetch the next vertex from memory
    efa.appendBlockAction("block_1",tr_str)               
    efa.appendBlockAction("block_1", "addi UDPR_9 UDPR_9 4")             #increment v1 iterator   
    efa.appendBlockAction("block_1","yield 2")                           # yield for v2 return
    efa.appendBlockAction("block_1","alldone: mov_imm2reg UDPR_3 1")        #8
    efa.appendBlockAction("block_1","mov_reg2lm UDPR_3 UDPR_10 4")        #8
    efa.appendBlockAction("block_1","yield_terminate 2")                 # Terminate 
    
    # Move v2 data to registers and fetch v2 neighbors
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_return'])
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                        # EAR1 - v1 neighlist ptr 
    tran2.writeAction("beq OB_0 0 block_1")                             # if size of v2 is 0
    tran2.writeAction("lshift_and_imm OB_0 UDPR_2 2 4294967295")        # UDPR5 - v2 size 
    tran2.writeAction("mov_imm2reg UDPR_3 0")                           # temp variable - UDPR3
    tran2.writeAction("nv2loop: ble UDPR_2 UDPR_3 nv2done")             # 
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["nv2_return"]) + " " + blkbytes + " 1" #2 Fetch n(v2)
    tran2.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #3
    tran2.writeAction(tr_str)               
    tran2.writeAction("jmp nv2loop")                                    #4
    tran2.writeAction("nv2done: mov_imm2reg UDPR_3 0")                           #5 TC = 0
    #tran2.writeAction("addi UDPR_10 UDPR_4 8")                          #6 LM base addr
    tran2.writeAction("mov_imm2reg UDPR_5 0")                           #7 v1 counter = 0
    #tran2.writeAction("mov_reg2reg UDPR_4 UDPR_7")                      #8 lm addr calculation
    tran2.writeAction("mov_lm2reg UDPR_4 UDPR_8 4")                     #9 fetch v1 from lm
    tran2.writeAction("mov_imm2reg UDPR_6 0")                           #10 v2 counter = 0 
    tran2.writeAction("yield 2")                                        #11 

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['nv2_return'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" check_v1szb_" +str(i)           #0 if n1 > n2 set walk -1
        tran3.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "walkfor_" + str(i) +": bne UDPR_8 OB_" + str(i) +" n1_ne_n2f_" + str(i)   #1 walkfor
        tran3.writeAction(tr_str)                            
        tran3.writeAction("addi UDPR_3 UDPR_3 1")                           #2
        tr_str = "jmp check_v1szf_" + str(i)                                    #3 block 1 - term/yield block
        tran3.writeAction(tr_str)
        tr_str = "n1_ne_n2f_" +str(i) + ": bgt UDPR_8 OB_" + str(i) +" next_n2_" + str(i) #4 n1_ne_n2f
        tran3.writeAction(tr_str)                            
        tran3.writeAction("check_v1szf_" + str(i) +": addi UDPR_5 UDPR_5 4")                           #5
        tr_str = "blt UDPR_5 UDPR_1 next_n1f_" + str(i)                      #6
        tran3.writeAction(tr_str)                            
        tran3.writeAction("subi UDPR_5 UDPR_5 4")                           #7
        tran3.writeAction("jmp next_n2_" + str(i))                                     #8
        #tran3.writeAction(tr_str)                            
        #tran3.writeAction("next_n1f_" + str(i) +": addi UDPR_5 UDPR_5 4")                           #5
        tran3.writeAction("next_n1f_" + str(i) +": add UDPR_4 UDPR_5 UDPR_7")  #9 next_n1
        tran3.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #10 fetch v1 from lm
        tr_str = "jmp walkfor_" + str(i)                                      #11
        tran3.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "walkback_" + str(i) + ": bne UDPR_8 OB_" + str(i) +" n1_ne_n2b_" + str(i)             #12 
        tran3.writeAction(tr_str)                            
        tran3.writeAction("addi UDPR_3 UDPR_3 1")                           #13 
        tr_str = "jmp check_v1szb_" + str(i)                                     #14 
        tran3.writeAction(tr_str)                            
        tr_str = "n1_ne_n2b_" + str(i) + ": blt UDPR_8 OB_" + str(i) +" next_n2_" + str(i)             #15 
        tran3.writeAction(tr_str)                            
        tran3.writeAction("check_v1szb_" + str(i) +": subi UDPR_5 UDPR_5 4")                           #5
        tr_str = "bge UDPR_5 0 next_n1b_" + str(i)                            #17 #y2
        tran3.writeAction(tr_str)                            
        tran3.writeAction("addi UDPR_5 UDPR_5 4")                           #7
        tran3.writeAction("jmp next_n2_" + str(i))                                     #8
        #tr_str = "n1_gt_n2_" + str(i)+ ": bge UDPR_5 0 next_n1b_" + str(i)                            #17 #y2
        #tran3.writeAction(tr_str)                            
        #tran3.writeAction("addi UDPR_5 UDPR_5 4")                           #18
        #tran3.writeAction("next_n1b_" + str(i) + ": subi UDPR_5 UDPR_5 4")   #16  n1_gt_n2
        tran3.writeAction("next_n1b_" + str(i) + ": add UDPR_4 UDPR_5 UDPR_7")                       #20 lm addr calculation
        tran3.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #21 fetch v1 from lm
        tr_str = "jmp walkback_" + str(i)                                     #22
        tran3.writeAction(tr_str)                            
        #<next v2> 
        tran3.writeAction("next_n2_" + str(i) + ": addi UDPR_6 UDPR_6 4")                           #23 next_n2
        tr_str = "beq UDPR_6 UDPR_2 next_v1"                            #24 next operand or block past that
        tran3.writeAction(tr_str)                            

    #tran3.writeAction("yld_op: ble UDPR_2 64 next_v1")                                        #116 100
    #tran3.writeAction("subi UDPR_2 UDPR_2 64")                                        #116 100
    tran3.writeAction("yield 1")                                        #116 100
    #tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 101  #fin
    tran3.writeAction("next_v1: addi UDPR_10 UDPR_10 4")                         #27 23 #y1
    tran3.writeAction("mov_lm2reg UDPR_10 UDPR_7 4")                    #26 Move Tri count
    #tran3.writeAction("print 'Lane:%d TC:%d' LID UDPR_3")                           # Helper function for print
    tran3.writeAction("add UDPR_7 UDPR_3 UDPR_3")                       #26 Move Tri count
    tran3.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #26 Move Tri count
    tran3.writeAction("subi UDPR_10 UDPR_10 4")                           #27 Set status now
    tran3.writeAction("tranCarry_goto block_1")                         #12

    #efa.printOut(stage_trace)    
 
    return efa

def GenerateTriEFA_orig():
    efa = EFA([])
    efa.code_level = 'machine'
    blksize=64
    vsize=str(16)
    
    state0 = State() #Initial State? 
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State() #tri Count State
    efa.add_state(state1)
    state2 = State() #tri Count State
    efa.add_state(state2)

    #Add events to dictionary 
    event_map = {
        'v1_launch':0,
        'nv1_return':1,
        'v2_return':2,
        'nv2_return':3
    }

    """
        v1_launch: OB_0_1:vertex_list_base ,OB_2_3:v1_neigh OB_4:start, OB_5: end, OB_6:LM_base addr
        nv1_return: OB_0-OB_15 - n(v1)
        v2_return: OB_0: ID OB_1: size OB_2_3: neigh
        nv2_return: OB_0-OB_15 - n(v2)   
    """

    blkbytes = str(blksize)
    blkwords = str(blksize/4)
    
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_launch'])
    # Create the thread context
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                        # EAR0 - vertexlist ptr! 
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                        # EAR1 - v1 neighlist ptr 
    tran0.writeAction("lshift_and_imm OB_4 UDPR_1 2 4294967295")        # v1 start_offset
    tran0.writeAction("lshift_and_imm OB_5 UDPR_2 2 4294967295")        # v1 end offset
    tran0.writeAction("mov_ob2reg OB_6 UDPR_10")                        # LM Base address
    tran0.writeAction("sub UDPR_2 UDPR_1 UDPR_4 0")                     # v1 size (in bytes)
    tran0.writeAction("mov_reg2reg UDPR_1 UDPR_3")                     # UDPR_3 - temp variable
    tran0.writeAction("addi UDPR_10 UDPR_9 8")                     # UDPR_9 pointer over v1
    
    # Fetch v1 neighborlist
    tran0.writeAction("nv1loop: ble UDPR_2 UDPR_3 nv1done")               # check if past UDPR_3
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["nv1_return"]) + " " + blkbytes + " 1"  #fetch v1 neighbors
    tran0.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #increment by number of bytes fetched
    tran0.writeAction(tr_str)               
    tran0.writeAction("jmp nv1loop")                                      #goto loop1 until all fetched
    tran0.writeAction("nv1done: addi UDPR_10 UDPR_3 8")                 #12 start offset on LM
    tran0.writeAction("mov_reg2reg UDPR_4 UDPR_1")                      #13 end offset on LM
    tran0.writeAction("add UDPR_1 UDPR_3 UDPR_12")                      #13 end offset on LM
    tran0.writeAction("yield 2")                                        #14

    # Move v1 neighborlist to LM
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['nv1_return'])
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


    # Fetch v2 from memory
    efa.appendBlockAction("block_1","beq UDPR_9 UDPR_12 alldone")       # check v1 iterator
    efa.appendBlockAction("block_1","mov_lm2reg UDPR_9 UDPR_3 4")       # get next neighbor ID
    efa.appendBlockAction("block_1","lshift UDPR_3 UDPR_3 4")           # calculate offset - ID*16
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["v2_return"]) + " " + vsize + " 0" # Fetch the next vertex from memory
    efa.appendBlockAction("block_1",tr_str)               
    efa.appendBlockAction("block_1", "addi UDPR_9 UDPR_9 4")             #increment v1 iterator   
    efa.appendBlockAction("block_1","yield 2")                           # yield for v2 return
    efa.appendBlockAction("block_1","alldone: mov_imm2reg UDPR_3 1")        #8
    efa.appendBlockAction("block_1","mov_reg2lm UDPR_3 UDPR_10 4")        #8
    efa.appendBlockAction("block_1","yield_terminate 2")                 # Terminate 
    
    # Move v2 data to registers and fetch v2 neighbors
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_return'])
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                        # EAR1 - v1 neighlist ptr 
    tran2.writeAction("beq OB_0 0 block_1")                             # if size of v2 is 0
    tran2.writeAction("lshift_and_imm OB_0 UDPR_2 2 4294967295")        # UDPR5 - v2 size 
    tran2.writeAction("mov_imm2reg UDPR_3 0")                           # temp variable - UDPR3
    tran2.writeAction("nv2loop: ble UDPR_2 UDPR_3 nv2done")             # 
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["nv2_return"]) + " " + blkbytes + " 1" #2 Fetch n(v2)
    tran2.writeAction(tr_str)               
    tr_str = "addi UDPR_3 UDPR_3 " + blkbytes                           #3
    tran2.writeAction(tr_str)               
    tran2.writeAction("jmp nv2loop")                                    #4
    tran2.writeAction("nv2done: mov_imm2reg UDPR_3 0")                           #5 TC = 0
    tran2.writeAction("addi UDPR_10 UDPR_4 8")                          #6 LM base addr
    tran2.writeAction("mov_imm2reg UDPR_5 0")                           #7 v1 counter = 0
    tran2.writeAction("mov_reg2reg UDPR_4 UDPR_7")                      #8 lm addr calculation
    tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #9 fetch v1 from lm
    tran2.writeAction("mov_imm2reg UDPR_6 0")                           #10 v2 counter = 0 
    tran2.writeAction("yield 2")                                        #11 

    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['nv2_return'])
    # Pick up first element
    for i in range(int(blksize/4)):
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" +str(16+25*i)                            #0 if n1 > n2 set walk -1
        tran3.writeAction(tr_str)                            
        # walk +1 (forward) [loop]
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(4+25*i)                             #5 1
        tran3.writeAction(tr_str)                            
        tran3.writeAction("addi UDPR_3 UDPR_3 1")                           #6 2
        tr_str = "jmp #" + str(23+25*i)                                        #7 3 block 1 - term/yield block
        tran3.writeAction(tr_str)                            
        tr_str = "bgt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #8 4
        tran3.writeAction(tr_str)                            
        tran3.writeAction("addi UDPR_5 UDPR_5 4")                           #9 5
        tr_str = "bne UDPR_5 UDPR_1 #" + str(9+25*i)                          #10 6
        tran3.writeAction(tr_str)                            
        tran3.writeAction("subi UDPR_5 UDPR_5 4")                           #11 7
        tr_str = "jmp #" +str(23+25*i)                                        #12 8
        tran3.writeAction(tr_str)                            
        tran3.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #13 9 lm addr calculation
        tran3.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #14 10 fetch v1 from lm
        tr_str = "jmp #" + str(1+25*i)                                         #15 11
        tran3.writeAction(tr_str)                            
        #walk -1 (backward)
        tr_str = "bne UDPR_8 OB_" + str(i) +" #" + str(15+25*i)                            #16 12
        tran3.writeAction(tr_str)                            
        tran3.writeAction("addi UDPR_3 UDPR_3 1")                           #17 13
        tr_str = "jmp #" + str(23+25*i)                                        #18 14 block 1 - term/yield block
        tran3.writeAction(tr_str)                            
        tr_str = "blt UDPR_8 OB_" + str(i) +" #" + str(23+25*i)                            #19 15
        tran3.writeAction(tr_str)                            
        tran3.writeAction("subi UDPR_5 UDPR_5 4")                           #20 16
        tr_str = "bge UDPR_5 0 #" + str(20+25*i)                               #21 17 #y2
        tran3.writeAction(tr_str)                            
        tran3.writeAction("addi UDPR_5 UDPR_5 4")                           #22 18
        tr_str = "jmp #" + str(23+25*i)                                        #23 19 
        tran3.writeAction(tr_str)                            
        tran3.writeAction("add UDPR_4 UDPR_5 UDPR_7")                       #24 20 lm addr calculation
        tran3.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                     #25 21 fetch v1 from lm
        tr_str = "jmp #" + str(12+25*i)                                        #26 22
        tran3.writeAction(tr_str)                            
        #<next v2> 
        tran3.writeAction("addi UDPR_6 UDPR_6 4")                           #27 23#y1
        tr_str = "beq UDPR_6 UDPR_2 #" + str(int(25*blksize/4+1))                    #28 24
        tran3.writeAction(tr_str)                            

    tran3.writeAction("yield 1")                                        #116 100
    #tran2.writeAction("send_old tc TOP UDPR_3 4 w 0")                       #117 101  #fin
    tran3.writeAction("addi UDPR_10 UDPR_10 4")                         #27 23 #y1
    tran3.writeAction("mov_lm2reg UDPR_10 UDPR_5 4")                    #26 Move Tri count
    tran3.writeAction("add UDPR_5 UDPR_3 UDPR_3")                       #26 Move Tri count
    tran3.writeAction("mov_reg2lm UDPR_3 UDPR_10 4")                    #26 Move Tri count
    tran3.writeAction("subi UDPR_10 UDPR_10 4")                           #27 Set status now
    tran3.writeAction("tranCarry_goto block_1")                         #12

    #efa.printOut(stage_trace)    
 
    return efa

if __name__=="__main__":
    efa = GenerateTriEFA()
    #efa.printOut(error)
    

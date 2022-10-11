from EFA import *


def GenerateJacEFA_mod():
    efa = EFA([])
    efa.code_level = 'machine'

    LM_BANK_SIZE = 65536
    BLOCK_SIZE = 64
    VERTEX_SIZE = 16
    LM_RESERVE = 8

    state0 = State()  # Initial State?
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    # Add events to dictionary
    event_map = {
        'v1_launch': 0,
        'nv1_return': 1,
        'v2_return': 2,
        'nv2_return': 3,
        'gamma_load_return': 4,
        'gamma_store_return': 5,
    }

    """
    Event Operands:
        v1_launch: OB_0_1:  vertex list address from vertex (i + 1)
                   OB_2_3:  v1 neighbor list base address
                   OB_4_5:  GAMMA base address for vertex i
                   OB_6:    LM_base address
                   OB_7:    number of vertices left in the vertex list (aka. total_num_vertices - i)
                   OB_8:    v1 id (aka. i)
                   OB_9:    v1 neighbor list length (aka. v1 degree)

        nv1_return: OB_0-OB_15 - n(v1)
        v2_return: OB_0: ID, OB_1: size, OB_2_3: neigh
        nv2_return: OB_0-OB_15 - n(v2)
    """

    # >>>> EVENT: v1_launch
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_launch'])

    # Create the thread context
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                         # EAR_0   : vertex list address from vertex (i + 1)
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         # EAR_1   : v1 neighbor list base address
    tran0.writeAction("mov_ob2ear OB_4_5 EAR_2")                         # EAR_2   : GAMMA base address for vertex i

    tran0.writeAction("mov_ob2reg OB_6 UDPR_10")                         # UDPR_10 : LM base address
    tran0.writeAction("mov_ob2reg OB_7 UDPR_14")                         # UDPR_14 : LM available size
    tran0.writeAction("mov_ob2reg OB_8 UDPR_0")                          # UDPR_0  : number of vertices left in the vertex list
    tran0.writeAction("mov_ob2reg OB_9 UDPR_1")                          # UDPR_1  : v1 vertex id
    tran0.writeAction("mov_ob2reg OB_10 UDPR_9")                          # UDPR_9  : v1 degree (length of v1 neighbor list)

    tran0.writeAction("lshift UDPR_0 UDPR_11 4")                         # UDPR_11 : UDPR_0 << 4, ID * 16 Byte vertex struct
    tran0.writeAction("lshift UDPR_9 UDPR_9 2")                          # UDPR_9  : UDPR_9 << 2, v1 neighbor list size (in bytes)

    # tran0.writeAction("mov_reg2reg UDPR_1 UDPR_3")                       # UDPR_3  : temp variable, initialized as start offset of v1 neighbor list

    # Prepare for and goto block 0
    tran0.writeAction("mov_imm2reg UDPR_13 0")                                    # UDPR_13: v1 neighbor list byte offset
    tran0.writeAction("subi UDPR_14 UDPR_14 {}".format(LM_RESERVE))    # UDPR_14: chunk byte size
    # tran0.writeAction("print 'v1 = %d, n_vert left = %d' UDPR_1 UDPR_0")
    tran0.writeAction("tranCarry_goto block_0")

    """
    GLOBAL REGISTERS:
        UDPR_10 : LM base address
        UDPR_0  : number of vertices left in the vertex list
        UDPR_1  : v1 vertex id
        UDPR_9  : UDPR_9 << 2, v1 neighbor list size (in bytes)

        ? UDPR_11 : UDPR_0 << 4, ID * 16 Byte vertex struct

        UDPR_13 : v1 neighbor list byte offset
        UDPR_14 : chunk byte size


    Temps: UDPR_2, *UDPR_3, *UDPR_4, UDPR_5, UDPR_6, UDPR_7, UDPR_8, *UDPR_11, UDPR_12, UDPR_13, UDPR_14, UDPR_15
    Use UDPR_0 as the DRAM write completion countdown counter
    """

    """
    >>>> BLOCK ACTION: block_0
    Do chunk load in block size

    Temps:
        UDPR_2
        UDPR_5
    Inputs:
        UDPR_9
        UDPR_10
        UDPR_13
        UDPR_14
    Outputs:
        UDPR_3
        UDPR_12
    """
    efa.appendBlockAction("block_0", "addi UDPR_10 UDPR_3 " + str(LM_RESERVE))    # UDPR_3: start offset on LM (TODO: may be global?)
    efa.appendBlockAction("block_0", "bge UDPR_13 UDPR_9 nv1chunkend")            # branch to terminate if done
    efa.appendBlockAction("block_0", "sub UDPR_9 UDPR_13 UDPR_2")                 # UDPR_2: bytes until the end of v1 neighbor list
    efa.appendBlockAction("block_0", "blt UDPR_2 UDPR_14 nv1chunksmall")
    # full chunk load
    efa.appendBlockAction("block_0", "add UDPR_13 UDPR_14 UDPR_5")                # UDPR_5: end byte offset for the chunk in v1 neighbor list
    efa.appendBlockAction("block_0", "add UDPR_3 UDPR_14 UDPR_12")                # UDPR_12: end offset on LM
    efa.appendBlockAction("block_0", "jmp nv1chunkloadloop")
    # not full chunk load
    efa.appendBlockAction("block_0", "nv1chunksmall: add UDPR_13 UDPR_2 UDPR_5")  # UDPR_5: end byte offset for the chunk in v1 neighbor list
    efa.appendBlockAction("block_0", "add UDPR_3 UDPR_2 UDPR_12")                 # UDPR_12: end offset on LM
    # send load chunk in block size
    efa.appendBlockAction("block_0", "nv1chunkloadloop: send_dmlm_ld_wret UDPR_13 " + str(event_map["nv1_return"]) + " " + str(BLOCK_SIZE) + " 1")
    efa.appendBlockAction("block_0", "addi UDPR_13 UDPR_13 " + str(BLOCK_SIZE))
    efa.appendBlockAction("block_0", "blt UDPR_13 UDPR_5 nv1chunkloadloop")
    # yield after all blocks for the chunk have been sent
    efa.appendBlockAction("block_0", "yield 2")
    # thread termination
    efa.appendBlockAction("block_0", "nv1chunkend: mov_imm2reg UDPR_2 1")         # UDPR_2 = 1, signaling TOP
    efa.appendBlockAction("block_0", "mov_reg2lm UDPR_2 UDPR_10 4")               # LM[UDPR_10] = UDPR_2, signaling TOP by putting 1 at the start of LM
    efa.appendBlockAction("block_0", "yield_terminate 2")


    """
    >>>> CONTINUATION EVENT: nv1_return
    Move v1 neighborlist to LM

    Temps:
        UDPR_5
    Inputs:
        UDPR_3
        UDPR_12
    Outputs:
        N/A
    """
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['nv1_return'])
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                       # UDPR_5: LM size to be filled
    tran1.writeAction("ble UDPR_5 " + str(BLOCK_SIZE) + " nv1copy")      # Branch if LM size left is smaller than or equal to block size
    tran1.writeAction("mov_imm2reg UDPR_5 " + str(BLOCK_SIZE))           # If block size is smaller than LM size left, put block size in UDPR_5
    tran1.writeAction("nv1copy: copy_ob_lm OB_0 UDPR_3 UDPR_5")          # Copy from OB to LM with size of UDPR_5
    tran1.writeAction("add UDPR_3 UDPR_5 UDPR_3")  # + blkbytes          # UDPR_3: current LM address, increment copied size
    tran1.writeAction("beq UDPR_3 UDPR_12 fetchv2")                      # Run BLOCK ACTION 1 when LM is filled
    tran1.writeAction("yield 2")
    tran1.writeAction("fetchv2: mov_imm2reg UDPR_15 0")                  # UDPR_15 = 0, count the current v2
    tran1.writeAction("tranCarry_goto block_1")

    """
    >>>> BLOCK ACTION: block_1
    TODO: will the UDPR_15 overflow?
    Fetch v2 from memory

    Temps:
        N/A
    Inputs:
        UDPR_11
        UDPR_15
    Outputs:
        N/A
    """
    efa.appendBlockAction("block_1", "bge UDPR_15 UDPR_11 v2alldone")      # Branch if UDPR_15 >= UDPR_11
    # efa.appendBlockAction("block_1", "print 'fetch v2 offset = %d' UDPR_15")
    tr_str = "send_dmlm_ld_wret UDPR_15 " + str(event_map["v2_return"]) + " " + str(VERTEX_SIZE) + " 0"  # Fetch the next vertex from memory
    efa.appendBlockAction("block_1", tr_str)
    efa.appendBlockAction("block_1", "addi UDPR_15 UDPR_15 " + str(VERTEX_SIZE))  # UDPR_15 += 16 Byte
    efa.appendBlockAction("block_1", "yield 2")                          # yield for v2 return
    efa.appendBlockAction("block_1", "v2alldone: tranCarry_goto block_0")

    """
    >>>> EVENT: v2_return
    Move v2 data to registers and fetch v2 neighbors

    Temps:
        UDPR_3
        UDPR_7
    Inputs:
        UDPR_10
    Outputs:
        UDPR_2
        UDPR_3
        UDPR_4
        UDPR_5
        UDPR_6
        UDPR_8

        UDPR_0
        UDPR_12
    """
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_return'])
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                         # EAR_1 - v1 neighlist ptr
    # tran2.writeAction("print 'v2 deg = %d' OB_0")
    tran2.writeAction("beq OB_0 0 block_1")                              # if size of v2 is 0, fetch next v2
    tran2.writeAction("lshift_and_imm OB_0 UDPR_2 2 4294967295")         # UDPR_2: nv2 size
    tran2.writeAction("mov_imm2reg UDPR_3 0")                            # temp variable - UDPR_3
    tran2.writeAction("mov_reg2reg OB_0 UDPR_0")                         # UDPR_0: nv2 size
    tran2.writeAction("mov_reg2reg OB_1 UDPR_12")                        # UDPR_12: v2 id
    # tran2.writeAction("print 'fetched vertex %d' UDPR_12")

    tran2.writeAction("nv2loop: ble UDPR_2 UDPR_3 nv2done")              #
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["nv2_return"]) + " " + str(BLOCK_SIZE) + " 1"  # 2 Fetch n(v2)
    tran2.writeAction(tr_str)
    tran2.writeAction("addi UDPR_3 UDPR_3 " + str(BLOCK_SIZE))           # 3
    tran2.writeAction("jmp nv2loop")                                     # 4

    # initialize for intersection
    tran2.writeAction("nv2done: mov_imm2reg UDPR_3 0")                   # 5 TC = 0
    tran2.writeAction("addi UDPR_10 UDPR_4 8")                           # 6 LM base addr
    tran2.writeAction("mov_imm2reg UDPR_5 0")                            # 7 v1 counter = 0
    tran2.writeAction("mov_reg2reg UDPR_4 UDPR_7")                       # 8 lm addr calculation
    tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                      # 9 fetch v1 from lm
    tran2.writeAction("mov_imm2reg UDPR_6 0")                            # 10 v2 counter = 0
    tran2.writeAction("yield 2")                                         # 11

    """
    >>>> EVENT: nv2_return

    Temps:
        UDPR_7
    Inputs:
        UDPR_2
        UDPR_3
        UDPR_4
        UDPR_5
        UDPR_6
        UDPR_8

        UDPR_0
        UDPR_12
    Outputs:
        UDPR_3
    """
    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['nv2_return'])

    # Intersect
    # Pick up first element
    for i in range(int(BLOCK_SIZE / 4)):
        tran3.writeAction("bgt UDPR_8 OB_" + str(i) +" check_v1szb_" +str(i))                          # 0 if n1 > n2 set walk -1
        # walk +1 (forward) [loop]
        tran3.writeAction("walkfor_" + str(i) +": bne UDPR_8 OB_" + str(i) +" n1_ne_n2f_" + str(i))    # 1 walkfor
        tran3.writeAction("addi UDPR_3 UDPR_3 1")                                                      # 2
        tran3.writeAction("jmp check_v1szf_" + str(i))                                                 # 3 block 1 - term/yield block
        tran3.writeAction("n1_ne_n2f_" +str(i) + ": bgt UDPR_8 OB_" + str(i) +" next_n2_" + str(i))    # 4 n1_ne_n2f
        tran3.writeAction("check_v1szf_" + str(i) +": addi UDPR_5 UDPR_5 4")                           # 5
        tran3.writeAction("blt UDPR_5 UDPR_9 next_n1f_" + str(i))                                      # 6
        tran3.writeAction("subi UDPR_5 UDPR_5 4")                                                      # 7
        tran3.writeAction("jmp next_n2_" + str(i))                                                     # 8
        tran3.writeAction("next_n1f_" + str(i) +": add UDPR_4 UDPR_5 UDPR_7")                          # 9 next_n1
        tran3.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                                                # 10 fetch v1 from lm
        tran3.writeAction("jmp walkfor_" + str(i))                                                     # 11
        #walk -1 (backward)
        tran3.writeAction("walkback_" + str(i) + ": bne UDPR_8 OB_" + str(i) +" n1_ne_n2b_" + str(i))  # 12
        tran3.writeAction("addi UDPR_3 UDPR_3 1")                                                      # 13 
        tran3.writeAction("jmp check_v1szb_" + str(i))                                                 # 14
        tran3.writeAction("n1_ne_n2b_" + str(i) + ": blt UDPR_8 OB_" + str(i) +" next_n2_" + str(i))   # 15
        tran3.writeAction("check_v1szb_" + str(i) +": subi UDPR_5 UDPR_5 4")                           # 5
        tran3.writeAction("bge UDPR_5 0 next_n1b_" + str(i))                                           # 17 #y2
        tran3.writeAction("addi UDPR_5 UDPR_5 4")                                                      # 7
        tran3.writeAction("jmp next_n2_" + str(i))                                                     # 8
        tran3.writeAction("next_n1b_" + str(i) + ": add UDPR_4 UDPR_5 UDPR_7")                         # 20 lm addr calculation
        tran3.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                                                # 21 fetch v1 from lm
        tran3.writeAction("jmp walkback_" + str(i))                            
        #<next v2> 
        tran3.writeAction("next_n2_" + str(i) + ": addi UDPR_6 UDPR_6 4")                              # 23 next_n2
        tran3.writeAction("beq UDPR_6 UDPR_2 next_v1")                                                 # 24 next operand or block past that          

    tran3.writeAction("yield 1")

    # Calcuate GAMMA offset
    tran3.writeAction("next_v1: sub UDPR_12 UDPR_1 UDPR_5")                 # UDPR_5: offset
    tran3.writeAction("subi UDPR_5 UDPR_5 1")                               # UDPR_5: offset
    tran3.writeAction("lshift UDPR_5 UDPR_5 2")                             # UDPR_5: offset

    # send read from memory 
    tran3.writeAction("send_dmlm_ld_wret UDPR_5 " + str(event_map["gamma_load_return"]) + " " + "4" + " 2")

    tran3.writeAction("yield 2")


    """
    >>>> EVENT: gamma_load_return
    """
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['gamma_load_return'])

    # Accumulate gamma for the current chunk
    tran4.writeAction("add UDPR_3 OB_0 UDPR_3")

    # Calculate GAMMA only when this is the last chunk
    tran4.writeAction("blt UDPR_13 UDPR_9 notlastchunk")

    # Calculate GAMMA
    # tran4.writeAction("print 'gamma(%d, %d) = %d' UDPR_1 UDPR_12 UDPR_3")
    tran4.writeAction("rshift UDPR_9 UDPR_6 2")                             # UDPR_6: v1.out_deg
    # tran4.writeAction("print 'GAMMA_raw(%d, %d) = %d / (%d + %d - %d)' UDPR_1 UDPR_12 UDPR_3 UDPR_5 UDPR_0 UDPR_3")
    tran4.writeAction("add UDPR_6 UDPR_0 UDPR_8")                           # UDPR_8: v1.out_deg + v2.out_deg
    tran4.writeAction("sub UDPR_8 UDPR_3 UDPR_8")                           # UDPR_8: v1.out_deg + v2.out_deg - gamma
    tran4.writeAction("lshift UDPR_3 UDPR_3 20")                            # UDPR_3: conver gamma to fixed point
    tran4.writeAction("fp_div UDPR_3 UDPR_8 UDPR_3")                        # UDPR_8: GAMMA
    # tran4.writeAction("print 'GAMMA_raw(%d, %d) = %d' UDPR_1 UDPR_12 UDPR_8")

    # Write result to LM
    tran4.writeAction("notlastchunk: addi UDPR_10 UDPR_6 4")
    tran4.writeAction("mov_reg2lm UDPR_3 UDPR_6 4")

    tran4.writeAction("send_dmlm_wret {} {} {} {} {}".format("UDPR_5", str(event_map["gamma_store_return"]), "UDPR_6", "4", "2"))

    tran4.writeAction("yield 2")


    """
    >>>> EVENT: gamma_store_return
    """
    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['gamma_store_return'])
    # tran5.writeAction("perflog 1 0 'TEST! %d, %d' UDPR_5 UDPR_6")
    # tran5.writeAction("perflog 0 {} {}".format(PerfLogPayload.UD_ACTION_STATS, PerfLogPayload.UD_QUEUE_STATS))
    tran5.writeAction("tranCarry_goto block_1")

    return efa


def GenerateJacEFA_mod_fixed_wr_addr():
    efa = EFA([])
    efa.code_level = 'machine'

    LM_BANK_SIZE = 65536
    BLOCK_SIZE = 64
    VERTEX_SIZE = 16
    LM_RESERVE = 8

    state0 = State()  # Initial State?
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    # Add events to dictionary
    event_map = {
        'v1_launch': 0,
        'nv1_return': 1,
        'v2_return': 2,
        'nv2_return': 3,
        'gamma_load_return': 4,
        'gamma_store_return': 5,
    }

    """
    Event Operands:
        v1_launch: OB_0_1:  vertex list address from vertex (i + 1)
                   OB_2_3:  v1 neighbor list base address
                   OB_4_5:  GAMMA base address for vertex i
                   OB_6:    LM_base address
                   OB_7:    number of vertices left in the vertex list (aka. total_num_vertices - i)
                   OB_8:    v1 id (aka. i)
                   OB_9:    v1 neighbor list length (aka. v1 degree)

        nv1_return: OB_0-OB_15 - n(v1)
        v2_return: OB_0: ID, OB_1: size, OB_2_3: neigh
        nv2_return: OB_0-OB_15 - n(v2)
    """

    # >>>> EVENT: v1_launch
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_launch'])

    # Create the thread context
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                         # EAR_0   : vertex list address from vertex (i + 1)
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         # EAR_1   : v1 neighbor list base address
    tran0.writeAction("mov_ob2ear OB_4_5 EAR_2")                         # EAR_2   : GAMMA base address for vertex i

    tran0.writeAction("mov_ob2reg OB_6 UDPR_10")                         # UDPR_10 : LM base address
    tran0.writeAction("mov_ob2reg OB_7 UDPR_14")                         # UDPR_14 : LM available size
    tran0.writeAction("mov_ob2reg OB_8 UDPR_0")                          # UDPR_0  : number of vertices left in the vertex list
    tran0.writeAction("mov_ob2reg OB_9 UDPR_1")                          # UDPR_1  : v1 vertex id
    tran0.writeAction("mov_ob2reg OB_10 UDPR_9")                          # UDPR_9  : v1 degree (length of v1 neighbor list)

    tran0.writeAction("lshift UDPR_0 UDPR_11 4")                         # UDPR_11 : UDPR_0 << 4, ID * 16 Byte vertex struct
    tran0.writeAction("lshift UDPR_9 UDPR_9 2")                          # UDPR_9  : UDPR_9 << 2, v1 neighbor list size (in bytes)

    # tran0.writeAction("mov_reg2reg UDPR_1 UDPR_3")                       # UDPR_3  : temp variable, initialized as start offset of v1 neighbor list

    # Prepare for and goto block 0
    tran0.writeAction("mov_imm2reg UDPR_13 0")                                    # UDPR_13: v1 neighbor list byte offset
    tran0.writeAction("subi UDPR_14 UDPR_14 {}".format(LM_RESERVE))    # UDPR_14: chunk byte size
    # tran0.writeAction("print 'v1 = %d, n_vert left = %d' UDPR_1 UDPR_0")
    tran0.writeAction("tranCarry_goto block_0")

    """
    GLOBAL REGISTERS:
        UDPR_10 : LM base address
        UDPR_0  : number of vertices left in the vertex list
        UDPR_1  : v1 vertex id
        UDPR_9  : UDPR_9 << 2, v1 neighbor list size (in bytes)

        ? UDPR_11 : UDPR_0 << 4, ID * 16 Byte vertex struct

        UDPR_13 : v1 neighbor list byte offset
        UDPR_14 : chunk byte size


    Temps: UDPR_2, *UDPR_3, *UDPR_4, UDPR_5, UDPR_6, UDPR_7, UDPR_8, *UDPR_11, UDPR_12, UDPR_13, UDPR_14, UDPR_15
    Use UDPR_0 as the DRAM write completion countdown counter
    """

    """
    >>>> BLOCK ACTION: block_0
    Do chunk load in block size

    Temps:
        UDPR_2
        UDPR_5
    Inputs:
        UDPR_9
        UDPR_10
        UDPR_13
        UDPR_14
    Outputs:
        UDPR_3
        UDPR_12
    """
    efa.appendBlockAction("block_0", "addi UDPR_10 UDPR_3 " + str(LM_RESERVE))    # UDPR_3: start offset on LM (TODO: may be global?)
    efa.appendBlockAction("block_0", "bge UDPR_13 UDPR_9 nv1chunkend")            # branch to terminate if done
    efa.appendBlockAction("block_0", "sub UDPR_9 UDPR_13 UDPR_2")                 # UDPR_2: bytes until the end of v1 neighbor list
    efa.appendBlockAction("block_0", "blt UDPR_2 UDPR_14 nv1chunksmall")
    # full chunk load
    efa.appendBlockAction("block_0", "add UDPR_13 UDPR_14 UDPR_5")                # UDPR_5: end byte offset for the chunk in v1 neighbor list
    efa.appendBlockAction("block_0", "add UDPR_3 UDPR_14 UDPR_12")                # UDPR_12: end offset on LM
    efa.appendBlockAction("block_0", "jmp nv1chunkloadloop")
    # not full chunk load
    efa.appendBlockAction("block_0", "nv1chunksmall: add UDPR_13 UDPR_2 UDPR_5")  # UDPR_5: end byte offset for the chunk in v1 neighbor list
    efa.appendBlockAction("block_0", "add UDPR_3 UDPR_2 UDPR_12")                 # UDPR_12: end offset on LM
    # send load chunk in block size
    efa.appendBlockAction("block_0", "nv1chunkloadloop: send_dmlm_ld_wret UDPR_13 " + str(event_map["nv1_return"]) + " " + str(BLOCK_SIZE) + " 1")
    efa.appendBlockAction("block_0", "addi UDPR_13 UDPR_13 " + str(BLOCK_SIZE))
    efa.appendBlockAction("block_0", "blt UDPR_13 UDPR_5 nv1chunkloadloop")
    # yield after all blocks for the chunk have been sent
    efa.appendBlockAction("block_0", "yield 2")
    # thread termination
    efa.appendBlockAction("block_0", "nv1chunkend: mov_imm2reg UDPR_2 1")         # UDPR_2 = 1, signaling TOP
    efa.appendBlockAction("block_0", "mov_reg2lm UDPR_2 UDPR_10 4")               # LM[UDPR_10] = UDPR_2, signaling TOP by putting 1 at the start of LM
    efa.appendBlockAction("block_0", "yield_terminate 2")


    """
    >>>> CONTINUATION EVENT: nv1_return
    Move v1 neighborlist to LM

    Temps:
        UDPR_5
    Inputs:
        UDPR_3
        UDPR_12
    Outputs:
        N/A
    """
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['nv1_return'])
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                       # UDPR_5: LM size to be filled
    tran1.writeAction("ble UDPR_5 " + str(BLOCK_SIZE) + " nv1copy")      # Branch if LM size left is smaller than or equal to block size
    tran1.writeAction("mov_imm2reg UDPR_5 " + str(BLOCK_SIZE))           # If block size is smaller than LM size left, put block size in UDPR_5
    tran1.writeAction("nv1copy: copy_ob_lm OB_0 UDPR_3 UDPR_5")          # Copy from OB to LM with size of UDPR_5
    tran1.writeAction("add UDPR_3 UDPR_5 UDPR_3")  # + blkbytes          # UDPR_3: current LM address, increment copied size
    tran1.writeAction("beq UDPR_3 UDPR_12 fetchv2")                      # Run BLOCK ACTION 1 when LM is filled
    tran1.writeAction("yield 2")
    tran1.writeAction("fetchv2: mov_imm2reg UDPR_15 0")                  # UDPR_15 = 0, count the current v2
    tran1.writeAction("tranCarry_goto block_1")

    """
    >>>> BLOCK ACTION: block_1
    TODO: will the UDPR_15 overflow?
    Fetch v2 from memory

    Temps:
        N/A
    Inputs:
        UDPR_11
        UDPR_15
    Outputs:
        N/A
    """
    efa.appendBlockAction("block_1", "bge UDPR_15 UDPR_11 v2alldone")      # Branch if UDPR_15 >= UDPR_11
    # efa.appendBlockAction("block_1", "print 'fetch v2 offset = %d' UDPR_15")
    tr_str = "send_dmlm_ld_wret UDPR_15 " + str(event_map["v2_return"]) + " " + str(VERTEX_SIZE) + " 0"  # Fetch the next vertex from memory
    efa.appendBlockAction("block_1", tr_str)
    efa.appendBlockAction("block_1", "addi UDPR_15 UDPR_15 " + str(VERTEX_SIZE))  # UDPR_15 += 16 Byte
    efa.appendBlockAction("block_1", "yield 2")                          # yield for v2 return
    efa.appendBlockAction("block_1", "v2alldone: tranCarry_goto block_0")

    """
    >>>> EVENT: v2_return
    Move v2 data to registers and fetch v2 neighbors

    Temps:
        UDPR_3
        UDPR_7
    Inputs:
        UDPR_10
    Outputs:
        UDPR_2
        UDPR_3
        UDPR_4
        UDPR_5
        UDPR_6
        UDPR_8

        UDPR_0
        UDPR_12
    """
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_return'])
    # tran2.writeAction("perflog 0 {} {} {}".format(PerfLogPayload.UD_ACTION_STATS.value, PerfLogPayload.UD_QUEUE_STATS.value, PerfLogPayload.UD_CYCLE_STATS.value))
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                         # EAR_1 - v1 neighlist ptr
    # tran2.writeAction("print 'v2 deg = %d' OB_0")
    tran2.writeAction("beq OB_0 0 block_1")                              # if size of v2 is 0, fetch next v2
    tran2.writeAction("lshift_and_imm OB_0 UDPR_2 2 4294967295")         # UDPR_2: nv2 size
    tran2.writeAction("mov_imm2reg UDPR_3 0")                            # temp variable - UDPR_3
    tran2.writeAction("mov_reg2reg OB_0 UDPR_0")                         # UDPR_0: nv2 size
    tran2.writeAction("mov_reg2reg OB_1 UDPR_12")                        # UDPR_12: v2 id
    # tran2.writeAction("print 'fetched vertex %d' UDPR_12")

    tran2.writeAction("nv2loop: ble UDPR_2 UDPR_3 nv2done")              #
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["nv2_return"]) + " " + str(BLOCK_SIZE) + " 1"  # 2 Fetch n(v2)
    tran2.writeAction(tr_str)
    tran2.writeAction("addi UDPR_3 UDPR_3 " + str(BLOCK_SIZE))           # 3
    tran2.writeAction("jmp nv2loop")                                     # 4

    # initialize for intersection
    tran2.writeAction("nv2done: mov_imm2reg UDPR_3 0")                   # 5 TC = 0
    tran2.writeAction("addi UDPR_10 UDPR_4 8")                           # 6 LM base addr
    tran2.writeAction("mov_imm2reg UDPR_5 0")                            # 7 v1 counter = 0
    tran2.writeAction("mov_reg2reg UDPR_4 UDPR_7")                       # 8 lm addr calculation
    tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                      # 9 fetch v1 from lm
    tran2.writeAction("mov_imm2reg UDPR_6 0")                            # 10 v2 counter = 0
    tran2.writeAction("yield 2")                                         # 11

    """
    >>>> EVENT: nv2_return

    Temps:
        UDPR_7
    Inputs:
        UDPR_2
        UDPR_3
        UDPR_4
        UDPR_5
        UDPR_6
        UDPR_8

        UDPR_0
        UDPR_12
    Outputs:
        UDPR_3
    """
    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['nv2_return'])

    # Intersect
    # Pick up first element
    for i in range(int(BLOCK_SIZE / 4)):
        tran3.writeAction("bgt UDPR_8 OB_" + str(i) +" check_v1szb_" +str(i))                          # 0 if n1 > n2 set walk -1
        # walk +1 (forward) [loop]
        tran3.writeAction("walkfor_" + str(i) +": bne UDPR_8 OB_" + str(i) +" n1_ne_n2f_" + str(i))    # 1 walkfor
        tran3.writeAction("addi UDPR_3 UDPR_3 1")                                                      # 2
        tran3.writeAction("jmp check_v1szf_" + str(i))                                                 # 3 block 1 - term/yield block
        tran3.writeAction("n1_ne_n2f_" +str(i) + ": bgt UDPR_8 OB_" + str(i) +" next_n2_" + str(i))    # 4 n1_ne_n2f
        tran3.writeAction("check_v1szf_" + str(i) +": addi UDPR_5 UDPR_5 4")                           # 5
        tran3.writeAction("blt UDPR_5 UDPR_9 next_n1f_" + str(i))                                      # 6
        tran3.writeAction("subi UDPR_5 UDPR_5 4")                                                      # 7
        tran3.writeAction("jmp next_n2_" + str(i))                                                     # 8
        tran3.writeAction("next_n1f_" + str(i) +": add UDPR_4 UDPR_5 UDPR_7")                          # 9 next_n1
        tran3.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                                                # 10 fetch v1 from lm
        tran3.writeAction("jmp walkfor_" + str(i))                                                     # 11
        #walk -1 (backward)
        tran3.writeAction("walkback_" + str(i) + ": bne UDPR_8 OB_" + str(i) +" n1_ne_n2b_" + str(i))  # 12
        tran3.writeAction("addi UDPR_3 UDPR_3 1")                                                      # 13 
        tran3.writeAction("jmp check_v1szb_" + str(i))                                                 # 14
        tran3.writeAction("n1_ne_n2b_" + str(i) + ": blt UDPR_8 OB_" + str(i) +" next_n2_" + str(i))   # 15
        tran3.writeAction("check_v1szb_" + str(i) +": subi UDPR_5 UDPR_5 4")                           # 5
        tran3.writeAction("bge UDPR_5 0 next_n1b_" + str(i))                                           # 17 #y2
        tran3.writeAction("addi UDPR_5 UDPR_5 4")                                                      # 7
        tran3.writeAction("jmp next_n2_" + str(i))                                                     # 8
        tran3.writeAction("next_n1b_" + str(i) + ": add UDPR_4 UDPR_5 UDPR_7")                         # 20 lm addr calculation
        tran3.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                                                # 21 fetch v1 from lm
        tran3.writeAction("jmp walkback_" + str(i))                            
        #<next v2> 
        tran3.writeAction("next_n2_" + str(i) + ": addi UDPR_6 UDPR_6 4")                              # 23 next_n2
        tran3.writeAction("beq UDPR_6 UDPR_2 next_v1")                                                 # 24 next operand or block past that          

    tran3.writeAction("yield 1")

    # Calcuate GAMMA offset
    tran3.writeAction("next_v1: mov_imm2reg UDPR_5 0")                        # UDPR_5: offset, fixed to 0
    # tran3.writeAction("sub UDPR_12 UDPR_1 UDPR_5")                          # UDPR_5: offset
    # tran3.writeAction("subi UDPR_5 UDPR_5 1")                               # UDPR_5: offset
    # tran3.writeAction("lshift UDPR_5 UDPR_5 2")                             # UDPR_5: offset

    # send read from memory 
    tran3.writeAction("send_dmlm_ld_wret UDPR_5 " + str(event_map["gamma_load_return"]) + " " + "4" + " 2")

    tran3.writeAction("yield 2")


    """
    >>>> EVENT: gamma_load_return
    """
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['gamma_load_return'])

    # Accumulate gamma for the current chunk
    tran4.writeAction("add UDPR_3 OB_0 UDPR_3")

    # Calculate GAMMA only when this is the last chunk
    tran4.writeAction("blt UDPR_13 UDPR_9 notlastchunk")

    # Calculate GAMMA
    # tran4.writeAction("print 'gamma(%d, %d) = %d' UDPR_1 UDPR_12 UDPR_3")
    tran4.writeAction("rshift UDPR_9 UDPR_6 2")                             # UDPR_6: v1.out_deg
    # tran4.writeAction("print 'GAMMA_raw(%d, %d) = %d / (%d + %d - %d)' UDPR_1 UDPR_12 UDPR_3 UDPR_5 UDPR_0 UDPR_3")
    tran4.writeAction("add UDPR_6 UDPR_0 UDPR_8")                           # UDPR_8: v1.out_deg + v2.out_deg
    tran4.writeAction("sub UDPR_8 UDPR_3 UDPR_8")                           # UDPR_8: v1.out_deg + v2.out_deg - gamma
    tran4.writeAction("lshift UDPR_3 UDPR_3 20")                            # UDPR_3: conver gamma to fixed point
    tran4.writeAction("beq UDPR_8 0 notlastchunk")                          # TODO: a hack to avoid div by 0
    tran4.writeAction("fp_div UDPR_3 UDPR_8 UDPR_3")                        # UDPR_8: GAMMA
    # tran4.writeAction("print 'GAMMA_raw(%d, %d) = %d' UDPR_1 UDPR_12 UDPR_8")

    # Write result to LM
    tran4.writeAction("notlastchunk: addi UDPR_10 UDPR_6 4")
    tran4.writeAction("mov_reg2lm UDPR_3 UDPR_6 4")

    tran4.writeAction("send_dmlm_wret {} {} {} {} {}".format("UDPR_5", str(event_map["gamma_store_return"]), "UDPR_6", "4", "2"))

    tran4.writeAction("yield 2")


    """
    >>>> EVENT: gamma_store_return
    """
    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['gamma_store_return'])
    # tran5.writeAction("perflog 1 0 'TEST! %d, %d' UDPR_5 UDPR_6")
    # tran5.writeAction("perflog 0 {} {} {}".format(PerfLogPayload.UD_ACTION_STATS.value, PerfLogPayload.UD_QUEUE_STATS.value, PerfLogPayload.UD_CYCLE_STATS.value))
    # tran5.writeAction("userctr 0 0 1")
    # tran5.writeAction("perflog 2 '{} {} {} {} {}' 0 'updown jc written'".format(PerfLogPayload.UD_ACTION_STATS.value, PerfLogPayload.UD_TRANS_STATS.value, PerfLogPayload.UD_QUEUE_STATS.value, PerfLogPayload.UD_LOCAL_MEM_STATS.value, PerfLogPayload.UD_MEM_INTF_STATS.value))
    tran5.writeAction("tranCarry_goto block_1")

    return efa


def GenerateJacEFA_mod_fixed_wr_addr_prof():
    efa = EFA([])
    efa.code_level = 'machine'

    LM_BANK_SIZE = 65536
    BLOCK_SIZE = 64
    VERTEX_SIZE = 16
    LM_RESERVE = 8

    state0 = State()  # Initial State?
    efa.add_initId(state0.state_id)
    efa.add_state(state0)

    # Add events to dictionary
    event_map = {
        'v1_launch': 0,
        'nv1_return': 1,
        'v2_return': 2,
        'nv2_return': 3,
        'gamma_load_return': 4,
        'gamma_store_return': 5,
    }

    """
    Event Operands:
        v1_launch: OB_0_1:  vertex list address from vertex (i + 1)
                   OB_2_3:  v1 neighbor list base address
                   OB_4_5:  GAMMA base address for vertex i
                   OB_6:    LM_base address
                   OB_7:    number of vertices left in the vertex list (aka. total_num_vertices - i)
                   OB_8:    v1 id (aka. i)
                   OB_9:    v1 neighbor list length (aka. v1 degree)

        nv1_return: OB_0-OB_15 - n(v1)
        v2_return: OB_0: ID, OB_1: size, OB_2_3: neigh
        nv2_return: OB_0-OB_15 - n(v2)
    """

    # >>>> EVENT: v1_launch
    tran0 = state0.writeTransition("eventCarry", state0, state0, event_map['v1_launch'])

    # Create the thread context
    tran0.writeAction("mov_ob2ear OB_0_1 EAR_0")                         # EAR_0   : vertex list address from vertex (i + 1)
    tran0.writeAction("mov_ob2ear OB_2_3 EAR_1")                         # EAR_1   : v1 neighbor list base address
    tran0.writeAction("mov_ob2ear OB_4_5 EAR_2")                         # EAR_2   : GAMMA base address for vertex i

    tran0.writeAction("mov_ob2reg OB_6 UDPR_10")                         # UDPR_10 : LM base address
    tran0.writeAction("mov_ob2reg OB_7 UDPR_14")                         # UDPR_14 : LM available size
    tran0.writeAction("mov_ob2reg OB_8 UDPR_0")                          # UDPR_0  : number of vertices left in the vertex list
    tran0.writeAction("mov_ob2reg OB_9 UDPR_1")                          # UDPR_1  : v1 vertex id
    tran0.writeAction("mov_ob2reg OB_10 UDPR_9")                          # UDPR_9  : v1 degree (length of v1 neighbor list)

    tran0.writeAction("lshift UDPR_0 UDPR_11 4")                         # UDPR_11 : UDPR_0 << 4, ID * 16 Byte vertex struct
    tran0.writeAction("lshift UDPR_9 UDPR_9 2")                          # UDPR_9  : UDPR_9 << 2, v1 neighbor list size (in bytes)

    # tran0.writeAction("mov_reg2reg UDPR_1 UDPR_3")                       # UDPR_3  : temp variable, initialized as start offset of v1 neighbor list

    # Prepare for and goto block 0
    tran0.writeAction("mov_imm2reg UDPR_13 0")                                    # UDPR_13: v1 neighbor list byte offset
    tran0.writeAction("subi UDPR_14 UDPR_14 {}".format(LM_RESERVE))    # UDPR_14: chunk byte size
    # tran0.writeAction("print 'v1 = %d, n_vert left = %d' UDPR_1 UDPR_0")
    tran0.writeAction("tranCarry_goto block_0")

    """
    GLOBAL REGISTERS:
        UDPR_10 : LM base address
        UDPR_0  : number of vertices left in the vertex list
        UDPR_1  : v1 vertex id
        UDPR_9  : UDPR_9 << 2, v1 neighbor list size (in bytes)

        ? UDPR_11 : UDPR_0 << 4, ID * 16 Byte vertex struct

        UDPR_13 : v1 neighbor list byte offset
        UDPR_14 : chunk byte size


    Temps: UDPR_2, *UDPR_3, *UDPR_4, UDPR_5, UDPR_6, UDPR_7, UDPR_8, *UDPR_11, UDPR_12, UDPR_13, UDPR_14, UDPR_15
    Use UDPR_0 as the DRAM write completion countdown counter
    """

    """
    >>>> BLOCK ACTION: block_0
    Do chunk load in block size

    Temps:
        UDPR_2
        UDPR_5
    Inputs:
        UDPR_9
        UDPR_10
        UDPR_13
        UDPR_14
    Outputs:
        UDPR_3
        UDPR_12
    """
    efa.appendBlockAction("block_0", "addi UDPR_10 UDPR_3 " + str(LM_RESERVE))    # UDPR_3: start offset on LM (TODO: may be global?)
    efa.appendBlockAction("block_0", "bge UDPR_13 UDPR_9 nv1chunkend")            # branch to terminate if done
    efa.appendBlockAction("block_0", "sub UDPR_9 UDPR_13 UDPR_2")                 # UDPR_2: bytes until the end of v1 neighbor list
    efa.appendBlockAction("block_0", "blt UDPR_2 UDPR_14 nv1chunksmall")
    # full chunk load
    efa.appendBlockAction("block_0", "add UDPR_13 UDPR_14 UDPR_5")                # UDPR_5: end byte offset for the chunk in v1 neighbor list
    efa.appendBlockAction("block_0", "add UDPR_3 UDPR_14 UDPR_12")                # UDPR_12: end offset on LM
    efa.appendBlockAction("block_0", "jmp nv1chunkloadloop")
    # not full chunk load
    efa.appendBlockAction("block_0", "nv1chunksmall: add UDPR_13 UDPR_2 UDPR_5")  # UDPR_5: end byte offset for the chunk in v1 neighbor list
    efa.appendBlockAction("block_0", "add UDPR_3 UDPR_2 UDPR_12")                 # UDPR_12: end offset on LM
    # send load chunk in block size
    efa.appendBlockAction("block_0", "nv1chunkloadloop: send_dmlm_ld_wret UDPR_13 " + str(event_map["nv1_return"]) + " " + str(BLOCK_SIZE) + " 1")
    efa.appendBlockAction("block_0", "addi UDPR_13 UDPR_13 " + str(BLOCK_SIZE))
    efa.appendBlockAction("block_0", "blt UDPR_13 UDPR_5 nv1chunkloadloop")
    # yield after all blocks for the chunk have been sent
    efa.appendBlockAction("block_0", "yield 2")
    # thread termination
    efa.appendBlockAction("block_0", "nv1chunkend: mov_imm2reg UDPR_2 1")         # UDPR_2 = 1, signaling TOP
    efa.appendBlockAction("block_0", "mov_reg2lm UDPR_2 UDPR_10 4")               # LM[UDPR_10] = UDPR_2, signaling TOP by putting 1 at the start of LM
    efa.appendBlockAction("block_0", "yield_terminate 2")


    """
    >>>> CONTINUATION EVENT: nv1_return
    Move v1 neighborlist to LM

    Temps:
        UDPR_5
    Inputs:
        UDPR_3
        UDPR_12
    Outputs:
        N/A
    """
    tran1 = state0.writeTransition("eventCarry", state0, state0, event_map['nv1_return'])
    tran1.writeAction("sub UDPR_12 UDPR_3 UDPR_5")                       # UDPR_5: LM size to be filled
    tran1.writeAction("ble UDPR_5 " + str(BLOCK_SIZE) + " nv1copy")      # Branch if LM size left is smaller than or equal to block size
    tran1.writeAction("mov_imm2reg UDPR_5 " + str(BLOCK_SIZE))           # If block size is smaller than LM size left, put block size in UDPR_5
    tran1.writeAction("nv1copy: copy_ob_lm OB_0 UDPR_3 UDPR_5")          # Copy from OB to LM with size of UDPR_5
    tran1.writeAction("add UDPR_3 UDPR_5 UDPR_3")  # + blkbytes          # UDPR_3: current LM address, increment copied size
    tran1.writeAction("beq UDPR_3 UDPR_12 fetchv2")                      # Run BLOCK ACTION 1 when LM is filled
    tran1.writeAction("yield 2")
    tran1.writeAction("fetchv2: mov_imm2reg UDPR_15 0")                  # UDPR_15 = 0, count the current v2
    tran1.writeAction("tranCarry_goto block_1")

    """
    >>>> BLOCK ACTION: block_1
    TODO: will the UDPR_15 overflow?
    Fetch v2 from memory

    Temps:
        N/A
    Inputs:
        UDPR_11
        UDPR_15
    Outputs:
        N/A
    """
    efa.appendBlockAction("block_1", "bge UDPR_15 UDPR_11 v2alldone")      # Branch if UDPR_15 >= UDPR_11
    # efa.appendBlockAction("block_1", "print 'fetch v2 offset = %d' UDPR_15")
    tr_str = "send_dmlm_ld_wret UDPR_15 " + str(event_map["v2_return"]) + " " + str(VERTEX_SIZE) + " 0"  # Fetch the next vertex from memory
    efa.appendBlockAction("block_1", tr_str)
    efa.appendBlockAction("block_1", "addi UDPR_15 UDPR_15 " + str(VERTEX_SIZE))  # UDPR_15 += 16 Byte
    efa.appendBlockAction("block_1", "yield 2")                          # yield for v2 return
    efa.appendBlockAction("block_1", "v2alldone: tranCarry_goto block_0")

    """
    >>>> EVENT: v2_return
    Move v2 data to registers and fetch v2 neighbors

    Temps:
        UDPR_3
        UDPR_7
    Inputs:
        UDPR_10
    Outputs:
        UDPR_2
        UDPR_3
        UDPR_4
        UDPR_5
        UDPR_6
        UDPR_8

        UDPR_0
        UDPR_12
    """
    tran2 = state0.writeTransition("eventCarry", state0, state0, event_map['v2_return'])
    # tran2.writeAction("perflog 0 {} {} {}".format(PerfLogPayload.UD_ACTION_STATS.value, PerfLogPayload.UD_QUEUE_STATS.value, PerfLogPayload.UD_CYCLE_STATS.value))
    tran2.writeAction("mov_ob2ear OB_2_3 EAR_1")                         # EAR_1 - v1 neighlist ptr
    # tran2.writeAction("print 'v2 deg = %d' OB_0")
    tran2.writeAction("beq OB_0 0 block_1")                              # if size of v2 is 0, fetch next v2
    tran2.writeAction("lshift_and_imm OB_0 UDPR_2 2 4294967295")         # UDPR_2: nv2 size
    tran2.writeAction("mov_imm2reg UDPR_3 0")                            # temp variable - UDPR_3
    tran2.writeAction("mov_reg2reg OB_0 UDPR_0")                         # UDPR_0: nv2 size
    tran2.writeAction("mov_reg2reg OB_1 UDPR_12")                        # UDPR_12: v2 id
    # tran2.writeAction("print 'fetched vertex %d' UDPR_12")

    tran2.writeAction("nv2loop: ble UDPR_2 UDPR_3 nv2done")              #
    tr_str = "send_dmlm_ld_wret UDPR_3 " + str(event_map["nv2_return"]) + " " + str(BLOCK_SIZE) + " 1"  # 2 Fetch n(v2)
    tran2.writeAction(tr_str)
    tran2.writeAction("addi UDPR_3 UDPR_3 " + str(BLOCK_SIZE))           # 3
    tran2.writeAction("jmp nv2loop")                                     # 4

    # initialize for intersection
    tran2.writeAction("nv2done: mov_imm2reg UDPR_3 0")                   # 5 TC = 0
    tran2.writeAction("addi UDPR_10 UDPR_4 8")                           # 6 LM base addr
    tran2.writeAction("mov_imm2reg UDPR_5 0")                            # 7 v1 counter = 0
    tran2.writeAction("mov_reg2reg UDPR_4 UDPR_7")                       # 8 lm addr calculation
    tran2.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                      # 9 fetch v1 from lm
    tran2.writeAction("mov_imm2reg UDPR_6 0")                            # 10 v2 counter = 0
    tran2.writeAction("yield 2")                                         # 11

    """
    >>>> EVENT: nv2_return

    Temps:
        UDPR_7
    Inputs:
        UDPR_2
        UDPR_3
        UDPR_4
        UDPR_5
        UDPR_6
        UDPR_8

        UDPR_0
        UDPR_12
    Outputs:
        UDPR_3
    """
    tran3 = state0.writeTransition("eventCarry", state0, state0, event_map['nv2_return'])

    tran3.writeAction("perflog 2 '{} {}' 1 'beg'".format(PerfLogPayload.UD_ACTION_STATS.value, PerfLogPayload.UD_TRANS_STATS.value))
    # Intersect
    # Pick up first element
    for i in range(int(BLOCK_SIZE / 4)):
        tran3.writeAction("bgt UDPR_8 OB_" + str(i) +" check_v1szb_" +str(i))                          # 0 if n1 > n2 set walk -1
        # walk +1 (forward) [loop]
        tran3.writeAction("walkfor_" + str(i) +": bne UDPR_8 OB_" + str(i) +" n1_ne_n2f_" + str(i))    # 1 walkfor
        tran3.writeAction("addi UDPR_3 UDPR_3 1")                                                      # 2
        tran3.writeAction("jmp check_v1szf_" + str(i))                                                 # 3 block 1 - term/yield block
        tran3.writeAction("n1_ne_n2f_" +str(i) + ": bgt UDPR_8 OB_" + str(i) +" next_n2_" + str(i))    # 4 n1_ne_n2f
        tran3.writeAction("check_v1szf_" + str(i) +": addi UDPR_5 UDPR_5 4")                           # 5
        tran3.writeAction("blt UDPR_5 UDPR_9 next_n1f_" + str(i))                                      # 6
        tran3.writeAction("subi UDPR_5 UDPR_5 4")                                                      # 7
        tran3.writeAction("jmp next_n2_" + str(i))                                                     # 8
        tran3.writeAction("next_n1f_" + str(i) +": add UDPR_4 UDPR_5 UDPR_7")                          # 9 next_n1
        tran3.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                                                # 10 fetch v1 from lm
        tran3.writeAction("jmp walkfor_" + str(i))                                                     # 11
        #walk -1 (backward)
        tran3.writeAction("walkback_" + str(i) + ": bne UDPR_8 OB_" + str(i) +" n1_ne_n2b_" + str(i))  # 12
        tran3.writeAction("addi UDPR_3 UDPR_3 1")                                                      # 13 
        tran3.writeAction("jmp check_v1szb_" + str(i))                                                 # 14
        tran3.writeAction("n1_ne_n2b_" + str(i) + ": blt UDPR_8 OB_" + str(i) +" next_n2_" + str(i))   # 15
        tran3.writeAction("check_v1szb_" + str(i) +": subi UDPR_5 UDPR_5 4")                           # 5
        tran3.writeAction("bge UDPR_5 0 next_n1b_" + str(i))                                           # 17 #y2
        tran3.writeAction("addi UDPR_5 UDPR_5 4")                                                      # 7
        tran3.writeAction("jmp next_n2_" + str(i))                                                     # 8
        tran3.writeAction("next_n1b_" + str(i) + ": add UDPR_4 UDPR_5 UDPR_7")                         # 20 lm addr calculation
        tran3.writeAction("mov_lm2reg UDPR_7 UDPR_8 4")                                                # 21 fetch v1 from lm
        tran3.writeAction("jmp walkback_" + str(i))                            
        #<next v2> 
        tran3.writeAction("next_n2_" + str(i) + ": addi UDPR_6 UDPR_6 4")                              # 23 next_n2
        tran3.writeAction("beq UDPR_6 UDPR_2 next_v1")                                                 # 24 next operand or block past that          

    tran3.writeAction("perflog 2 '{} {}' 1 'end'".format(PerfLogPayload.UD_ACTION_STATS.value, PerfLogPayload.UD_TRANS_STATS.value))
    tran3.writeAction("yield 1")
    tran3.writeAction("next_v1: perflog 2 '{} {}' 1 'end'".format(PerfLogPayload.UD_ACTION_STATS.value, PerfLogPayload.UD_TRANS_STATS.value))

    # Calcuate GAMMA offset
    tran3.writeAction("mov_imm2reg UDPR_5 0")                                 # UDPR_5: offset, fixed to 0
    # tran3.writeAction("sub UDPR_12 UDPR_1 UDPR_5")                          # UDPR_5: offset
    # tran3.writeAction("subi UDPR_5 UDPR_5 1")                               # UDPR_5: offset
    # tran3.writeAction("lshift UDPR_5 UDPR_5 2")                             # UDPR_5: offset

    # send read from memory 
    tran3.writeAction("send_dmlm_ld_wret UDPR_5 " + str(event_map["gamma_load_return"]) + " " + "4" + " 2")

    tran3.writeAction("yield 2")


    """
    >>>> EVENT: gamma_load_return
    """
    tran4 = state0.writeTransition("eventCarry", state0, state0, event_map['gamma_load_return'])

    # Accumulate gamma for the current chunk
    tran4.writeAction("add UDPR_3 OB_0 UDPR_3")

    # Calculate GAMMA only when this is the last chunk
    tran4.writeAction("blt UDPR_13 UDPR_9 notlastchunk")

    # Calculate GAMMA
    # tran4.writeAction("print 'gamma(%d, %d) = %d' UDPR_1 UDPR_12 UDPR_3")
    tran4.writeAction("rshift UDPR_9 UDPR_6 2")                             # UDPR_6: v1.out_deg
    # tran4.writeAction("print 'GAMMA_raw(%d, %d) = %d / (%d + %d - %d)' UDPR_1 UDPR_12 UDPR_3 UDPR_5 UDPR_0 UDPR_3")
    tran4.writeAction("add UDPR_6 UDPR_0 UDPR_8")                           # UDPR_8: v1.out_deg + v2.out_deg
    tran4.writeAction("sub UDPR_8 UDPR_3 UDPR_8")                           # UDPR_8: v1.out_deg + v2.out_deg - gamma
    tran4.writeAction("lshift UDPR_3 UDPR_3 20")                            # UDPR_3: conver gamma to fixed point
    tran4.writeAction("beq UDPR_8 0 notlastchunk")                          # TODO: a hack to avoid div by 0
    tran4.writeAction("fp_div UDPR_3 UDPR_8 UDPR_3")                        # UDPR_8: GAMMA
    # tran4.writeAction("print 'GAMMA_raw(%d, %d) = %d' UDPR_1 UDPR_12 UDPR_8")

    # Write result to LM
    tran4.writeAction("notlastchunk: addi UDPR_10 UDPR_6 4")
    tran4.writeAction("mov_reg2lm UDPR_3 UDPR_6 4")

    tran4.writeAction("send_dmlm_wret {} {} {} {} {}".format("UDPR_5", str(event_map["gamma_store_return"]), "UDPR_6", "4", "2"))

    tran4.writeAction("yield 2")


    """
    >>>> EVENT: gamma_store_return
    """
    tran5 = state0.writeTransition("eventCarry", state0, state0, event_map['gamma_store_return'])
    # tran5.writeAction("perflog 1 0 'TEST! %d, %d' UDPR_5 UDPR_6")
    # tran5.writeAction("perflog 0 {} {} {}".format(PerfLogPayload.UD_ACTION_STATS.value, PerfLogPayload.UD_QUEUE_STATS.value, PerfLogPayload.UD_CYCLE_STATS.value))
    # tran5.writeAction("userctr 0 0 1")
    # tran5.writeAction("perflog 2 '{} {} {} {} {}' 0 'updown jc written'".format(PerfLogPayload.UD_ACTION_STATS.value, PerfLogPayload.UD_TRANS_STATS.value, PerfLogPayload.UD_QUEUE_STATS.value, PerfLogPayload.UD_LOCAL_MEM_STATS.value, PerfLogPayload.UD_MEM_INTF_STATS.value))
    tran5.writeAction("tranCarry_goto block_1")

    return efa


if __name__ == "__main__":
    efa = GenerateJacEFA_mod()
    # efa.printOut(error)


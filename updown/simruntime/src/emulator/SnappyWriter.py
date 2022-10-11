import sys
sys.path.append("../")
from MachineCode import Property
from EFA import *
#from EfaExecutor import *

def HashAndCompareMatch(src_state, dst_state, hash_base_byte):
    tran = src_state.writeTransition("flagCarry_with_action", src_state, dst_state, 0)
    #====== UDPR_2 stores the hash entry address
    tran.writeAction("hash_sb32 UDPR_2 "+str(hash_base_byte))
    #====== UDPR_1 stores the candidate address
    tran.writeAction("mov_lm2reg UDPR_2 UDPR_1 2")
    #====== UDPR_7 points input buffer
    tran.writeAction("add UDPR_1 UDPR_7 UDPR_1")
    #====== update the hash entry with current address
    tran.writeAction("sub SBPB UDPR_7 UDPR_3")
    tran.writeAction("mov_reg2lm  UDPR_3  UDPR_2 2")
    #====== compare the string length. UDPR_1 and SBPB not change
    # Note: compare_string boundary is maxSBP>>3
    tran.writeAction("compare_string  UDPR_1  SBPB  UDPR_0")

def MatchLenLessThan4(src_state, dst_state):
    for i in range(4):
        tran = src_state.writeTransition("commonCarry", src_state, dst_state, i)
    
def MatchLen12To64LiteralLen(src_state, dst_state, efa, maj_id):
    for i in range(12,65):
        tran = src_state.writeTransition("flagCarry_with_action", src_state, dst_state, i)
        tran.writeAction("tranCarry_goto block_0")

    #====== UDPR_3 stores the match_len - 1, (SBPB will +1 in the end automatically)
    efa.appendBlockAction("block_0","subi UDPR_0 UDPR_3 1")
    #====== calcullate first byte of copy tag:  length-1(6b) tag(10) result in UDPR_2
    efa.appendBlockAction("block_0","lshift_or_imm UDPR_3 UDPR_2 2 2")
    #====== calculate the literal to emit length, store result in UDPR_0
    efa.appendBlockAction("block_0","sub SBPB  UDPR_4  UDPR_0")
    #====== set majority state and maintain the flag property of next state
    # efa.appendBlockAction("block_0","set_state_property flag_majority MJ_tran_addr")
    efa.appendBlockAction("block_0","set_state_property flag_majority "+str(maj_id))
        
def SkipFirstByte(src_state, dst_state):
    tran = src_state.writeTransition("commonCarry", src_state, dst_state,0)
    
def MatchLen12To64Copy(src_state, dst_state, efa):
    for i in range(0,256):
        tran = src_state.writeTransition("commonCarry_with_action", src_state, dst_state, i)
        
        #====== write literal tag:  length-1(6b) Tag(00)
        if i > 0 and i <= 60:
            tran.writeAction("tranCarry_goto block_4")
        elif i >= 61:
            tran.writeAction("tranCarry_goto block_3")
        else:
            tran.writeAction("tranCarry_goto block_1")

    #====== Action Block 4
    efa.appendBlockAction("block_4","lshift_sub_imm UDPR_0 UDPR_6 2 4")
    efa.appendBlockAction("block_4","put_bytes  UDPR_6 UDPR_5 1")
    #====== calculate match offset, result in UDPR_1
    efa.appendBlockAction("block_4","sub SBPB  UDPR_1  UDPR_1")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len is in UDPR_3.
    efa.appendBlockAction("block_4","add SBPB UDPR_3 SBPB")
    #====== EmitLiteral before EmitCopy
    efa.appendBlockAction("block_4","copy UDPR_4 UDPR_5  UDPR_0")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    efa.appendBlockAction("block_4","addi  SBPB UDPR_4 1")
    #====== Emit Copy tag: match_len|tag
    efa.appendBlockAction("block_4","put_bytes  UDPR_2  UDPR_5 1")
    #====== Emit Copy tag: offset
    # note it is little-endian for offset
    # efa.appendBlockAction("block_4","swap_bytes  UDPR_1 UDPR_1  2")
    efa.appendBlockAction("block_4","put_bytes  UDPR_1  UDPR_5 2")

    #====== Action Block 1
    #====== calculate match offset, result in UDPR_1
    efa.appendBlockAction("block_1","sub SBPB  UDPR_1  UDPR_1")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len is in UDPR_3.
    efa.appendBlockAction("block_1","add SBPB UDPR_3 SBPB")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    efa.appendBlockAction("block_1","addi  SBPB UDPR_4 1")
    #====== Emit Copy tag: match_len|tag
    efa.appendBlockAction("block_1","put_bytes  UDPR_2  UDPR_5 1")
    #====== Emit Copy tag: offset
    # note it is little-endian for offset
    # efa.appendBlockAction("block_1","swap_bytes  UDPR_1 UDPR_1  2")
    efa.appendBlockAction("block_1","put_bytes  UDPR_1  UDPR_5 2")

    #====== Action Block 3
    tag = 0x00 + 60 << 2
    efa.appendBlockAction("block_3","put_1byte_imm  UDPR_5 "+str(tag))
    #====== calculate match offset, result in UDPR_1
    efa.appendBlockAction("block_3","sub SBPB  UDPR_1  UDPR_1")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len is in UDPR_3.
    efa.appendBlockAction("block_3","add SBPB UDPR_3 SBPB")
    #====== UDPR_0 is one byte, UDPR_0 = length
    efa.appendBlockAction("block_3","subi  UDPR_0  UDPR_3 1")
    efa.appendBlockAction("block_3","put_bytes  UDPR_3  UDPR_5 1")
    #====== EmitLiteral before EmitCopy
    efa.appendBlockAction("block_3","copy UDPR_4 UDPR_5  UDPR_0")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    efa.appendBlockAction("block_3","addi  SBPB UDPR_4 1")
    #====== Emit Copy tag: match_len|tag
    efa.appendBlockAction("block_3","put_bytes  UDPR_2  UDPR_5 1")
    #====== Emit Copy tag: offset
    # note it is little-endian for offset
    # efa.appendBlockAction("block_3","swap_bytes  UDPR_1 UDPR_1  2")
    efa.appendBlockAction("block_3","put_bytes  UDPR_1  UDPR_5 2")
    

    #====== Majority Transition
    tran = src_state.writeTransition("majority", src_state, dst_state, None)
    maj_tran = src_state.get_tran_byAnnotation('majority')[0]
    maj_id = maj_tran.trans_id
    # literal length >= 256
    #====== calculate match offset, result in UDPR_1
    tran.writeAction("sub SBPB  UDPR_1  UDPR_1")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len is in UDPR_3.
    tran.writeAction("add SBPB UDPR_3 SBPB")
    tag = 0x00 + 61 << 2
    tran.writeAction("put_1byte_imm  UDPR_5 "+str(tag))
    tran.writeAction("subi  UDPR_0  UDPR_3 1")
    # tran.writeAction("swap_bytes  UDPR_3 UDPR_3 2")
    tran.writeAction("put_bytes  UDPR_3  UDPR_5 2")
    
    #====== EmitLiteral before EmitCopy
    tran.writeAction("copy UDPR_4 UDPR_5  UDPR_0")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    tran.writeAction("addi  SBPB UDPR_4 1")
    #====== Emit Copy tag: match_len|tag
    tran.writeAction("put_bytes  UDPR_2  UDPR_5 1")
    #====== Emit Copy tag: offset
    # tran.writeAction("swap_bytes  UDPR_1 UDPR_1 2")
    tran.writeAction("put_bytes  UDPR_1  UDPR_5 2")

    tran.writeAction("set_state_property common")
    return maj_id
    
def EmitRemainder(state5,state6,state7,state8,state9,state10,state14):
    #====== require state 5 has the common property, set by the host processor ======
    tran5to6 = state5.writeTransition("flagCarry_with_action", state5, state6, 0)
    #====== UDPR_1 stores the length of the remainder literal ======
    tran5to6.writeAction("sub SBPB  UDPR_4  UDPR_1  1")
    #====== compare length >0? ======
    tran5to6.writeAction("comp_gt UDPR_1 UDPR_0  0  ")
    #====== length == 0, do nothing since nothing to emit ======
    tran6to7 = state6.writeTransition("basic", state6, state7, 0)
    #====== length > 0, compare length <= 60? ======
    tran6to8 = state6.writeTransition("flagCarry_with_action", state6, state8, 1)
    tran6to8.writeAction("comp_lt UDPR_1  UDPR_0 61  ")
    #====== emit remainder literal, 0 < length <= 60 ======
    tran8to9 = state8.writeTransition("basic_with_action", state8, state9, 1)
    #====== calculate the tag
    tran8to9.writeAction("lshift_sub_imm UDPR_1 UDPR_2 2 4")
    tran8to9.writeAction("put_bytes UDPR_2 UDPR_5 1")
    tran8to9.writeAction("copy UDPR_4 UDPR_5  UDPR_1")
    #====== emit remainder literal, length >= 61 , check whether <= 256 ======
    tran8to10 = state8.writeTransition("flagCarry_with_action", state8, state10, 0)
    tran8to10.writeAction("comp_lt UDPR_1  UDPR_0 257  ")
    #====== length <= 256
    tran10to14 = state10.writeTransition("basic_with_action", state10, state14, 1)
    tag = 0x00 + 60 << 2
    tran10to14.writeAction("put_1byte_imm  UDPR_5 "+str(tag))
    tran10to14.writeAction("subi  UDPR_1  UDPR_2 1")
    tran10to14.writeAction("put_bytes  UDPR_2  UDPR_5 1")
    tran10to14.writeAction("copy UDPR_4 UDPR_5  UDPR_1")
    #====== length > 256
    tran10to14 = state10.writeTransition("basic_with_action", state10, state14, 0)
    tag = 0x00 + 61 << 2
    tran10to14.writeAction("put_1byte_imm  UDPR_5 "+str(tag))
    tran10to14.writeAction("subi  UDPR_1  UDPR_2 1")
    # tran10to14.writeAction("swap_bytes  UDPR_2 UDPR_2 2")
    tran10to14.writeAction("put_bytes  UDPR_2  UDPR_5 2")
    tran10to14.writeAction("copy UDPR_4 UDPR_5  UDPR_1")
    
def MatchLen4To11CheckOffset(src_state, dst_state, efa):
    for i in range(4,12):
        tran = src_state.writeTransition("flagCarry_with_action", src_state, dst_state, i)
        tran.writeAction("tranCarry_goto block_5")

    #====== store match_length-1 in UDPR_2
    efa.appendBlockAction("block_5","subi UDPR_0 UDPR_2 1")
    #====== calculate the offset, store in UDPR_1
    #====== don't care absoute candiate address anymore
    efa.appendBlockAction("block_5","sub SBPB UDPR_1 UDPR_1")
    efa.appendBlockAction("block_5","comp_lt UDPR_1  UDPR_0 2048  1")

def MatchLen4To11SmallOffsetLiteralLen(src_state, dst_state, maj_id):
    tran = src_state.writeTransition("flagCarry_with_action", src_state, dst_state, 1)
    #====== calculate tag for Snappy tag 01: offset(3b) length-4(3b) Tag(01) | offset(8b)
    #====== UDPR_2: length-1, UDPR_1: offset
    #====== UDPR_3 stores the 2-byte tag, 
    tran.writeAction("lshift_sub_imm UDPR_2 UDPR_3 10 2816")
    #====== UDPR_3 = (UDPR_1&0xff)|UDPR_3
    tran.writeAction("mask_or UDPR_1 UDPR_3 0xff")
    # the following imm2 is too large to fit in JAction imm2
    # So I separate it into two actions
    # tran.writeAction("lshift_and_imm UDPR_1 UDPR_1 5 0xe000")
    tran.writeAction("lshift UDPR_1 UDPR_1 5")
    tran.writeAction("bitwise_and_imm UDPR_1 UDPR_1 0xe000")
    tran.writeAction("bitwise_or UDPR_1 UDPR_3 UDPR_3")
    #====== calculate the literal to emit length, store result in UDPR_0
    tran.writeAction("sub SBPB  UDPR_4  UDPR_0  1")
    #====== set majority state and maintain the flag property of next state
    #tran.writeAction("set_state_property flag_majority MJ_tran_addr")
    tran.writeAction("set_state_property flag_majority "+str(maj_id)) 


def MatchLen4To11SmallOffsetCopy(src_state, dst_state, efa):
    for i in range(0,256):
        tran = src_state.writeTransition("commonCarry_with_action", src_state, dst_state, i)
        
        #====== write literal tag:  length-1(6b) Tag(00)
        if i > 0 and i <= 60:
            tran.writeAction("tranCarry_goto block_8")
        elif i >= 61:
            tran.writeAction("tranCarry_goto block_7")
        else:
            tran.writeAction("tranCarry_goto block_6")

    #====== Action Block 8
    efa.appendBlockAction("block_8","lshift_sub_imm UDPR_0 UDPR_6 2 4")
    efa.appendBlockAction("block_8","put_bytes  UDPR_6 UDPR_5 1")
    #====== EmitLiteral before EmitCopy
    efa.appendBlockAction("block_8","copy UDPR_4 UDPR_5  UDPR_0")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    efa.appendBlockAction("block_8","add SBPB UDPR_2 SBPB")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    efa.appendBlockAction("block_8","addi  SBPB UDPR_4 1")
    #====== Emit Copy tag:01
    efa.appendBlockAction("block_8", "swap_bytes  UDPR_3 UDPR_3 2")
    efa.appendBlockAction("block_8","put_bytes  UDPR_3  UDPR_5 2")

    #====== Action Block 7
    tag = 0x00 + 60<<2
    efa.appendBlockAction("block_7","put_1byte_imm  UDPR_5 "+str(tag))
    efa.appendBlockAction("block_7","subi  UDPR_0  UDPR_1 1")
    efa.appendBlockAction("block_7","put_bytes  UDPR_1  UDPR_5 1")
    #====== EmitLiteral before EmitCopy
    efa.appendBlockAction("block_7","copy UDPR_4 UDPR_5  UDPR_0")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    efa.appendBlockAction("block_7","add SBPB UDPR_2 SBPB")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    efa.appendBlockAction("block_7","addi  SBPB UDPR_4 1")
    #====== Emit Copy tag:01
    efa.appendBlockAction("block_7", "swap_bytes  UDPR_3 UDPR_3 2")
    efa.appendBlockAction("block_7","put_bytes  UDPR_3  UDPR_5 2")

    #====== Action Block 6
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    efa.appendBlockAction("block_6","add SBPB UDPR_2 SBPB")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    efa.appendBlockAction("block_6","addi  SBPB UDPR_4 1")
    #====== Emit Copy tag:01
    efa.appendBlockAction("block_6", "swap_bytes  UDPR_3 UDPR_3 2")
    efa.appendBlockAction("block_6","put_bytes  UDPR_3  UDPR_5 2")

    #====== Majority Transition
    tran = src_state.writeTransition("majority", src_state, dst_state, None)
    maj_tran = src_state.get_tran_byAnnotation('majority')[0]
    maj_id = maj_tran.trans_id
    # literal length >= 256
    tag = 0x00 + 61<<2
    tran.writeAction("put_1byte_imm  UDPR_5 "+str(tag))
    tran.writeAction("subi  UDPR_0  UDPR_1 1")
    # tran.writeAction("swap_bytes  UDPR_1 UDPR_1 2")
    tran.writeAction("put_bytes  UDPR_1  UDPR_5 2")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    tran.writeAction("add SBPB UDPR_2 SBPB")
    #====== EmitLiteral before EmitCopy
    tran.writeAction("copy UDPR_4 UDPR_5  UDPR_0")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    tran.writeAction("addi  SBPB UDPR_4 1")
    #====== Emit Copy tag:01
    tran.writeAction("swap_bytes  UDPR_3 UDPR_3 2")
    tran.writeAction("put_bytes  UDPR_3  UDPR_5 2")
    tran.writeAction("set_state_property common")
    #====== TODO: implement majority actions to deal with length 62,63,64
    return maj_id
    
def MatchLen4To11LargeOffsetLiteralLen(src_state, dst_state, maj_id):
    tran = src_state.writeTransition("flagCarry_with_action", src_state, dst_state, 0)
    #====== calculate tag for Snappy tag 10:  length-1(6b)Tag(10) | offset l(8b) | offset h(8b)
    # UDPR_2: length-1, UDPR_1: offset
    tran.writeAction("lshift_or_imm UDPR_2 UDPR_3 2 0x2")
    #====== UDPR_1 = (UDPR_3 << 16) | UDPR_1
    # UDPR_1 stores the 3-byte tag
    tran.writeAction("swap_bytes UDPR_1 UDPR_1 2")
    tran.writeAction("lshift_or UDPR_3 UDPR_1 16")
    tran.writeAction("swap_bytes UDPR_1 UDPR_1 3")
    #====== calculate the literal to emit length, store result in UDPR_0
    tran.writeAction("sub SBPB  UDPR_4  UDPR_0  1")
    #====== set majority state and maintain the flag property of next state
    #tran.writeAction("set_state_property flag_majority MJ_tran_addr")
    tran.writeAction("set_state_property flag_majority "+str(maj_id)) 

def MatchLen4To11LargeOffsetCopy(src_state, dst_state, efa):
    for i in range(0,256):
        tran = src_state.writeTransition("commonCarry_with_action", src_state, dst_state, i)

        #====== write literal tag: length-1(6b) Tag(00)
        if i > 0 and i <= 60:
            tran.writeAction("tranCarry_goto block_11")
        elif i > 60:
            tran.writeAction("tranCarry_goto block_10")
        else:
            tran.writeAction("tranCarry_goto block_9")


    #====== Action Block 11
    efa.appendBlockAction("block_11","lshift_sub_imm UDPR_0 UDPR_6 2 4")
    efa.appendBlockAction("block_11","put_bytes  UDPR_6 UDPR_5 1")
    #====== EmitLiteral before EmitCopy
    efa.appendBlockAction("block_11","copy UDPR_4 UDPR_5  UDPR_0")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    efa.appendBlockAction("block_11","add SBPB UDPR_2 SBPB")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    efa.appendBlockAction("block_11","addi  SBPB UDPR_4 1")
    #====== Emit Copy tag:02
    # efa.appendBlockAction("block_11","swap_bytes  UDPR_1  UDPR_1 3")
    efa.appendBlockAction("block_11","put_bytes  UDPR_1  UDPR_5 3")
    
    #====== Action Block 10
    tag = 0x00 + 60<<2
    efa.appendBlockAction("block_10","put_1byte_imm  UDPR_5 "+str(tag))
    efa.appendBlockAction("block_10","subi  UDPR_0  UDPR_3 1")
    efa.appendBlockAction("block_10","put_bytes  UDPR_3  UDPR_5 1")
    #====== EmitLiteral before EmitCopy
    efa.appendBlockAction("block_10","copy UDPR_4 UDPR_5  UDPR_0")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    efa.appendBlockAction("block_10","add SBPB UDPR_2 SBPB")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    efa.appendBlockAction("block_10","addi  SBPB UDPR_4 1")
    #====== Emit Copy tag:02
    # efa.appendBlockAction("block_10","swap_bytes  UDPR_1  UDPR_1 3")
    efa.appendBlockAction("block_10","put_bytes  UDPR_1  UDPR_5 3")
    
    #====== Action Block 9
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    efa.appendBlockAction("block_9","add SBPB UDPR_2 SBPB")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    efa.appendBlockAction("block_9","addi  SBPB UDPR_4 1")
    #====== Emit Copy tag:02
    # efa.appendBlockAction("block_9","swap_bytes  UDPR_1  UDPR_1 3")
    efa.appendBlockAction("block_9","put_bytes  UDPR_1  UDPR_5 3")

    tran = src_state.writeTransition("majority", src_state, dst_state, None)
    maj_tran = src_state.get_tran_byAnnotation('majority')[0]
    maj_id = maj_tran.trans_id
    # literal length >= 256
    tag = 0x00 + 61<<2
    tran.writeAction("put_1byte_imm  UDPR_5 "+str(tag))
    tran.writeAction("subi  UDPR_0  UDPR_3 1")
    # tran.writeAction("swap_bytes UDPR_3 UDPR_3 2")
    tran.writeAction("put_bytes  UDPR_3  UDPR_5 2")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    tran.writeAction("add SBPB UDPR_2 SBPB")
    #====== EmitLiteral before EmitCopy
    tran.writeAction("copy UDPR_4 UDPR_5  UDPR_0")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    tran.writeAction("addi  SBPB UDPR_4 1")
    #====== Emit Copy tag:02
    # tran.writeAction("swap_bytes  UDPR_1  UDPR_1 3")
    tran.writeAction("put_bytes  UDPR_1  UDPR_5 3")
    tran.writeAction("set_state_property common")
    return maj_tran.trans_id

def MatchLen65To68(src_state, dst_state, tmp_state, efa):
    for i in range(65,69):
        tran = src_state.writeTransition("flagCarry_with_action", src_state, tmp_state, i)
        tran.writeAction("tranCarry_goto block_12")


    #====== Action Block 12
    #====== UDPR_2 stores the match_len - 1, (SBPB will +1 in the end automatically)
    efa.appendBlockAction("block_12","subi UDPR_0 UDPR_2 1")
    #====== calculate the offset, store in UDPR_1
    #====== don't care absoute candiate address anymore
    efa.appendBlockAction("block_12","sub SBPB UDPR_1 UDPR_1")
    #====== calculate the literal to emit length, store result in UDPR_3
    efa.appendBlockAction("block_12","sub SBPB  UDPR_4  UDPR_3")
    efa.appendBlockAction("block_12","comp_gt UDPR_3 UDPR_0 0")


    #====== Emit Literal Length non-zero
    tran = tmp_state.writeTransition("commonCarry_with_action", tmp_state, dst_state, 1)
    #====== to simplify the FA, always assume literal length > 256
    tag = 0x00 + 61 << 2
    tran.writeAction("put_1byte_imm  UDPR_5 "+str(tag))
    tran.writeAction("subi  UDPR_3  UDPR_3 1")
    #====== UDPR_0 stores the literal length, for copy acton
    tran.writeAction("addi  UDPR_3  UDPR_0 1")
    # tran.writeAction("swap_bytes UDPR_3 UDPR_3 2")
    tran.writeAction("put_bytes  UDPR_3  UDPR_5 2")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    tran.writeAction("add SBPB UDPR_2 SBPB")
    #====== EmitLiteral before EmitCopy
    tran.writeAction("copy UDPR_4 UDPR_5  UDPR_0")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    tran.writeAction("addi  SBPB UDPR_4 1")
    #======  length-1 (6b) tag (10)|offset (8)|offset(8), length = 60
    tran.writeAction("put_1byte_imm  UDPR_5 238")
    # tran.writeAction("swap_bytes UDPR_1 UDPR_1 2")
    tran.writeAction("put_bytes  UDPR_1  UDPR_5 2")
    #====== for simplicity, don't check offset, assume  lenth-1 tag(10)| offset (8)|offset(8)
    #====== UDPR_2 = (UDPR_2 - 60) << 2 + 2
    tran.writeAction("lshift_sub_imm UDPR_2 UDPR_2 2 238")
    tran.writeAction("put_bytes  UDPR_2  UDPR_5 1")
    #====== alway swaped in copy 60, no need to swap UDPR_1 again
    tran.writeAction("put_bytes  UDPR_1  UDPR_5 2")

    #====== Emit Literal Length zero
    tran = tmp_state.writeTransition("commonCarry_with_action", tmp_state, dst_state, 0)
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    tran.writeAction("add SBPB UDPR_2 SBPB")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    tran.writeAction("addi  SBPB UDPR_4 1")
    #======  length-1 (6b) tag (10)|offset (8)|offset(8), length = 60
    tran.writeAction("put_1byte_imm  UDPR_5 238")
    # tran.writeAction("swap_bytes UDPR_1 UDPR_1 2")
    tran.writeAction("put_bytes  UDPR_1  UDPR_5 2")
    #====== for simplicity, don't check offset, assume  lenth-1 tag(10)| offset (8)|offset(8)
    #====== UDPR_2 = (UDPR_2 - 60) << 2 + 2
    tran.writeAction("lshift_sub_imm UDPR_2 UDPR_2 2 238")
    tran.writeAction("put_bytes  UDPR_2  UDPR_5 1")
    #====== alway swaped in copy 60, no need to swap UDPR_1 again
    tran.writeAction("put_bytes  UDPR_1  UDPR_5 2")
    
def MatchLen69To255EmitLiteral(src_state, dst_state, tmp_state, efa):
    for i in range(69,256):
        tran = src_state.writeTransition("flagCarry_with_action", src_state, tmp_state, i)
        tran.writeAction("tranCarry_goto block_13")
        
    #====== Action Block 13
    #====== UDPR_2 stores the match_len - 1, (SBPB will +1 in the end automatically)
    efa.appendBlockAction("block_13","subi UDPR_0 UDPR_2 1")
    #====== calculate the offset, store in UDPR_1
    #====== don't care absoute candiate address anymore
    efa.appendBlockAction("block_13","sub SBPB UDPR_1 UDPR_1")
    # efa.appendBlockAction("block_13","swap_bytes  UDPR_1  UDPR_1 2")
    #====== calculate the literal to emit length, store result in UDPR_3
    efa.appendBlockAction("block_13","sub SBPB  UDPR_4  UDPR_3")
    efa.appendBlockAction("block_13","comp_gt UDPR_3 UDPR_0 0")

    #====== Literal length to emit is non-zero
    tran = tmp_state.writeTransition("flagCarry_with_action", tmp_state, dst_state, 1)
    tran.writeAction("subi UDPR_3  UDPR_3 1")
    #====== UDPR_0 stores the literal emit length for copy actoin
    tran.writeAction("addi UDPR_3 UDPR_0 1")
    #====== to simplify the FA, always assume literal length > 256
    tag = 0x00 + 61 << 2
    tran.writeAction("put_1byte_imm  UDPR_5 "+str(tag))
    # tran.writeAction("swap_bytes  UDPR_3  UDPR_3 2")
    tran.writeAction("put_bytes  UDPR_3  UDPR_5 2")
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    tran.writeAction("add SBPB UDPR_2 SBPB")
    #====== EmitLiteral before EmitCopy
    tran.writeAction("copy UDPR_4 UDPR_5  UDPR_0")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    tran.writeAction("addi  SBPB UDPR_4 1")
    tran.writeAction("comp_lt  UDPR_2  UDPR_0 64")

    #====== Literal to emit length is zero
    tran = tmp_state.writeTransition("flagCarry_with_action", tmp_state, dst_state, 0)
    #====== advance the SBPB, SBPB = SBPB + match_len-1 
    #====== (SBPB will +1 in the end automatically), match_len-1 is in UDPR_2.
    tran.writeAction("add SBPB UDPR_2 SBPB")
    #====== UDPR_4 points to next literal start position
    #====== UDPR_4 = SBPB + 1
    tran.writeAction("addi  SBPB UDPR_4 1")
    tran.writeAction("comp_lt  UDPR_2  UDPR_0 64")
        
def MatchLen69To255Copy64(src_state, dst_state):
    tran = src_state.writeTransition("flagCarry_with_action", src_state, dst_state, 0)
    #======  length-1 (6b) tag (10)|offset (8)|offset(8), length = 64
    tran.writeAction("put_1byte_imm  UDPR_5 254")
    #====== match offset stores in UDPR_1
    tran.writeAction("put_bytes  UDPR_1  UDPR_5 2")
    tran.writeAction("subi UDPR_2 UDPR_2 64")
    tran.writeAction("comp_lt  UDPR_2  UDPR_0 64")

def MatchLen69To255CopyRemain(src_state, dst_state):
    tran = src_state.writeTransition("commonCarry_with_action", src_state, dst_state, 1)
    #======  length-1 (6b) tag (10)|offset (8)|offset(8), UDPR_2 = length -1
    tran.writeAction("lshift_or_imm UDPR_2 UDPR_2 2 0x2")
    tran.writeAction("put_bytes  UDPR_2  UDPR_5 1")
    #====== match offset stores in UDPR_1
    tran.writeAction("put_bytes  UDPR_1  UDPR_5 2")

# hard coded export vector for snappy compression
def GetSnappyCompressExportVector():
    return [Property('common',0)]
    
# @hash_base_byte: the byte address (should be 8192 here) of hash table in a single bannk
# @compstr_bound: the upbound byte address of string comparison to prevent spanning across input buffer to output buffer
def WriteSnappyCompression(hash_base_byte=8192):
        
    efa = EFA([])
    efa.code_level = 'machine'
    efa.alphabet = range(0,256)
    state0 = State()
    state0.alphabet = [0]
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State()
    state1.alphabet = [0]
    efa.add_state(state1)
    state2 = State()
    efa.add_state(state2)
    state3 = State()
    efa.add_state(state3)
    state4 = State()
    efa.add_state(state4)
    state5 = State()
    state5.alphabet = [0]
    efa.add_state(state5)
    efa.export_state_id.append(state5.state_id)
    state6 = State()
    state6.alphabet = [0,1]
    efa.add_state(state6)
    state7 = State()
    efa.add_state(state7)
    state8 = State()
    state8.alphabet = [0, 1]
    efa.add_state(state8)
    state9 = State()
    efa.add_state(state9)
    state10 = State()
    state10.alphabet = [0,1]
    efa.add_state(state10)
    state11 = State()
    state11.alphabet = [0, 1]
    efa.add_state(state11)
    state12 = State()
    efa.add_state(state12)
    state13 = State()
    efa.add_state(state13)
    state14 = State()
    efa.add_state(state14)
    state15 = State()
    state15.alphabet = [0 ,1]
    efa.add_state(state15)
    state16 = State()
    state16.alphabet = [0, 1]
    efa.add_state(state16)
    state17 = State()
    state17.alphabet = [0, 1]
    efa.add_state(state17)
    state18 = State()
    state18.alphabet = [0 ,1]
    efa.add_state(state18)
    
    SkipFirstByte(state0, state1)
    HashAndCompareMatch(state1, state2, hash_base_byte)
    MatchLenLessThan4(state2, state1)

    maj_id = MatchLen12To64Copy(state3, state1, efa)
    MatchLen12To64LiteralLen(state2, state3, efa, maj_id)
    
    EmitRemainder(state5,state6,state7,state8,state9,state10, state14)
    MatchLen4To11CheckOffset(state2, state11, efa)

    maj_id = MatchLen4To11SmallOffsetCopy(state12, state1,efa)
    MatchLen4To11SmallOffsetLiteralLen(state11, state12, maj_id)
    

    maj_id = MatchLen4To11LargeOffsetCopy(state13, state1, efa)
    MatchLen4To11LargeOffsetLiteralLen(state11, state13, maj_id)
    
    MatchLen65To68(state2, state1, state18, efa)
    MatchLen69To255EmitLiteral(state2, state15,state17,efa)
    MatchLen69To255Copy64(state15, state16)
    MatchLen69To255CopyRemain(state15, state1)
    MatchLen69To255CopyRemain(state16, state1)
    MatchLen69To255Copy64(state16, state16)
    return efa
    
#============================== Decompression ====================================
def scanFirstTagByte(src_state, dst_state):
    tran = src_state.writeTransition("flagCarry_with_action", src_state, dst_state, 0)
    tran.writeAction("get_bytes SBPB  UDPR_0 1")

def CopyLiteral(src_state, dst_state):
    for i in range(0, 237, 4):
        #====== tag : length - 1 00
        tran = src_state.writeTransition("commonCarry_with_action", src_state, dst_state, i)
        length = (i>>2) + 1
        tran.writeAction("copy_imm SBPB UDPR_5 "+str(length))
        #====== get one step back, UDP increases SBPB 1 step automatically
        tran.writeAction("subi SBPB SBPB 1")
    #====== for literal tag  60 (00)|length-1(8b)
    label = 60 << 2
    tran = src_state.writeTransition("commonCarry_with_action", src_state, dst_state, label)
    tran.writeAction("get_bytes SBPB  UDPR_0 1")
    tran.writeAction("addi UDPR_0 UDPR_0 1")
    tran.writeAction("copy SBPB UDPR_5 UDPR_0")
    #====== get one step back, UDP increases SBPB 1 step automatically
    tran.writeAction("subi SBPB SBPB 1")

    
    #====== for literal tag 61 (00)|length(8b)|length(8b)
    label = 61 << 2
    tran = src_state.writeTransition("commonCarry_with_action", src_state, dst_state, label)
    tran.writeAction("get_bytes SBPB  UDPR_0 2")
    # tran.writeAction("swap_bytes UDPR_0 UDPR_0 2")
    tran.writeAction("addi UDPR_0  UDPR_0 1")
    tran.writeAction("copy SBPB UDPR_5 UDPR_0")
    #====== get one step back, UDP increases SBPB 1 step automaticalyl
    tran.writeAction("subi SBPB SBPB 1")

def CopyMatchTag10(src_state, dst_state):
    #====== for match tag, length-1(6b) 10 | offset (8b)| offset(8b)
    for i in range(2, 256, 4):
        tran = src_state.writeTransition("commonCarry_with_action", src_state, dst_state, i)
        length = (i - 2 >> 2) + 1
        #====== UDPR_0 stores the offset
        tran.writeAction("get_bytes  SBPB  UDPR_0 2")
        # tran.writeAction("swap_bytes  UDPR_0  UDPR_0 2")
        #====== UDPR_4 stores the start pointer of reference string
        tran.writeAction("sub UDPR_5 UDPR_0 UDPR_4")
        tran.writeAction("copy_from_out_imm UDPR_4 UDPR_5 "+str(length))
        tran.writeAction("subi SBPB SBPB 1")

def CopyMatchTag01(src_state, dst_state):
    #====== for match tag, offset (3b) length-4 (3b) 01| offset(8b)
    for i in range(1, 256, 4):
        tran = src_state.writeTransition("commonCarry_with_action", src_state, dst_state, i)
        length = (i >> 2 & 0x7) + 4
        #====== UDPR_2 stores the offset LSB 8 bit
        tran.writeAction("get_bytes  SBPB  UDPR_2 1")
        #====== UDPR_0 stores offset
        tran.writeAction("lshift_and_imm UDPR_0 UDPR_0 3 0x700")
        tran.writeAction("bitwise_or UDPR_2 UDPR_0 UDPR_0")
        #====== UDPR_4 stores the start pointer of reference string
        tran.writeAction("sub UDPR_5 UDPR_0 UDPR_4")
        tran.writeAction("copy_from_out_imm UDPR_4 UDPR_5 "+str(length))
        tran.writeAction("subi SBPB SBPB 1")

def WriteSnappyDecompression():
    efa = EFA([])
    efa.code_level = 'machine'
    efa.alphabet = range(0,256)
    state0 = State()
    efa.add_state(state0)
    state1 = State()
    efa.add_state(state1)
    efa.add_initId(state0.state_id)
    
    scanFirstTagByte(state0, state1)
    CopyLiteral(state1, state0)
    CopyMatchTag01(state1, state0)
    CopyMatchTag10(state1, state0)
    return efa

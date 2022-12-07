import copy
import re

# ====== Control the printing ======
PrintSwitch = 5
# ====== Printing Option Level ======
full_trace = 0
stage_trace = 1
progress_trace = 2
error = 100


def printLevel(p):
    global PrintSwitch
    PrintSwitch = p


def printd(obj, LEVEL):
    if LEVEL >= PrintSwitch:
        print(obj, flush=True)


# ====== Printing Color Facility ======
class bcolors:
    HEADER = "\033[35m"
    OKBLUE = "\033[34m"
    OKGREEN = "\033[32m"
    WARNING = "\033[33m"
    FAIL = "\033[31m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def find_underscore(str, pos):
    cur = 0
    curidx = 0
    index = 0
    while cur < pos:
        index = str.find("_", index, len(str))
        cur += 1
        index += 1
    return index


def concatSet(InSet1, InSet2):
    res = []
    # ======quick path
    if isinstance(InSet1, list) is True and isinstance(InSet2, list) is True:
        if len(InSet1) == 0:
            return InSet2
        elif len(InSet2) == 0:
            return InSet1
    elif isinstance(InSet1, list) is True:
        if len(InSet1) == 0:
            return [InSet2]
    elif isinstance(InSet2, list) is True:
        if len(InSet2) == 0:
            return [InSet1]
    # ====== slow path
    if isinstance(InSet1, list):
        for j in InSet1:
            ele = copy.deepcopy(j)
            res.append(ele)
    else:
        ele = copy.deepcopy(InSet1)
        res.append(ele)
    if isinstance(InSet2, list):
        for j in InSet2:
            ele = copy.deepcopy(j)
            res.append(ele)
    else:
        ele = copy.deepcopy(InSet2)
        res.append(ele)
    return res


class Operand:
    def __init__(self):
        self.opcode = "Unknown"
        self.dst = "EMPTY"
        self.src = "EMPTY"
        self.imm = "EMPTY"
        self.imm2 = "EMPTY"
        self.rt = "EMPTY"
        self.op1 = "EMPTY"
        self.op2 = "EMPTY"
        self.op1_ob_or_reg = "EMPTY"
        self.op2_ob_or_reg_or_imm = "EMPTY"
        self.event_label = "EMPTY"
        self.event = "EMPTY"
        self.addr = "EMPTY"
        self.addr_mode = "EMPTY"
        self.size = "EMPTY"
        self.rw = "EMPTY"
        self.dst_issb = "EMPTY"
        self.cont = "EMPTY"
        self.reglist = []
        self.maxop = 0
        self.maxudp = 0
        self.label = None
        self.formatstr = None
        self.perflog_mode = 0
        self.perflog_payload_list = 0
        self.perflog_msg_id = 0


def ParseAction(asm_inst):
    # import pdb
    # pdb.set_trace()
    templabel = None
    prepart = asm_inst.split()
    if prepart[0][-1] == ":":
        part = prepart[1:]
        templabel = prepart[0][:-1]
    else:
        part = prepart[:]
    # part = asm_inst.split()
    opcode = part[0]
    ActionClass = ""
    operand = Operand()

    operand.opcode = opcode
    maxudp = 0
    maxop = 0
    if templabel is not None:
        operand.label = templabel
    # ====== Action Part ======
    if opcode == "hash_sb32" or opcode == "mov_imm2reg" or opcode == "put_2byte_imm" or opcode == "put_1byte_imm":
        ActionClass = "Action"
        operand.dst = part[1]
        operand.imm = part[2]
        if operand.dst[0] == "U":
            maxudp = int(operand.dst[5:])
        elif operand.dst[0] == "O":
            maxop = int(operand.dst[3:])
        else:
            print("Error in parsing Action!")
            exit(1)

    elif (
        opcode == "goto" or opcode == "tranCarry_goto" or opcode == "set_issue_width" or opcode == "set_complete" or opcode == "mov_sb2reg"
    ):  # added by Marzi
        ActionClass = "Action"
        operand.imm = part[1]
        if operand.imm[0] == "U":
            maxudp = int(operand.imm[5:])

    # Note: in real UDP, only has copy
    # added by Marzi (xor bellow)
    # """I dont' see following instructions in the ISA
    #    get_bytes_from_out
    #    swap_bytes
    #    mask_or
    #    bitwise_xor_imm
    #    set_complete
    #    copy_from_out_imm
    #    mov_lml2reg_blk
    #    mov_eqt2reg
    #    block_compare
    #    block_compare_i
    #    cmpswp_ri
    #    cmpswp_i
    #    copy_ob_lm
    #    copy_from_out
    #    compare_string_from_out
    # """
    elif (
        opcode == "subi"
        or opcode == "addi"
        or opcode == "put_bytes"
        or opcode == "get_bytes"
        or opcode == "get_bytes_from_out"
        or opcode == "swap_bytes"
        or opcode == "comp_lt"
        or opcode == "lshift_or"
        or opcode == "rshift_or"
        or opcode == "mask_or"
        or opcode == "bitwise_and_imm"
        or opcode == "bitwise_or_imm"
        or opcode == "bitwise_xor_imm"
        or opcode == "copy_imm"
        or opcode == "copy_from_out_imm"
        or opcode == "mov_lm2reg"
        or opcode == "mov_lm2ear"
        or opcode == "mov_ear2lm"
        or opcode == "mov_reg2lm"
        or opcode == "comp_gt"
        or opcode == "comp_eq"
        or opcode == "rshift"
        or opcode == "lshift"
        or opcode == "mov_lm2reg_blk"
        or opcode == "arithrshift"
    ):  # added by Marziyeh (arithrshifts)
        ActionClass = "Action"
        operand.src = part[1]
        operand.dst = part[2]
        operand.imm = part[3]
        if operand.src[0] == "U":
            maxudp = int(operand.src[5:])
        elif operand.src[0] == "O":
            maxop = int(operand.src[3:])
        if operand.dst[0] == "U":
            if int(operand.dst[5:]) > maxudp:
                maxudp = int(operand.dst[5:])
        elif operand.dst[0] == "O":
            if int(operand.dst[3:]) > maxop:
                maxop = int(operand.dst[3:])

    elif opcode == "set_state_property":
        ActionClass = "Action"
        if part[1] == "flag":
            operand.imm = "flag"
        elif part[1] == "common":
            operand.imm = "common"
        elif part[1] == "null":  # added by Marziyeh
            operand.imm = "null"
        elif part[1] == "majority":
            operand.imm = "majority" + "::" + part[2]
        elif part[1] == "flag_majority":
            operand.imm = "flag_majority" + "::" + part[2]
        elif part[1] == "default":
            operand.imm = "default" + "::" + part[2]
        elif part[1] == "flag_default":
            operand.imm = "flag_default" + "::" + part[2]
        elif part[1] == "event":
            operand.imm = "event"  # Andronicus for event

    elif opcode == "mov_reg2reg" or opcode == "mov_ob2reg" or opcode == "mov_eqt2reg" or opcode == "mov_ob2ear":
        ActionClass = "Action"
        operand.src = part[1]
        operand.dst = part[2]
        if operand.src[0] == "U":
            maxudp = int(operand.src[5:])
        elif operand.src[0] == "O" and operand.src.count("O") == 1:
            maxop = int(operand.src[3:])
        elif operand.src[0] == "O" and operand.src.count("O") == 2:
            pos = find_underscore(operand.src, 2)
            maxop = int(operand.src[pos:])
        if operand.dst[0] == "U":
            if int(operand.dst[5:]) > maxudp:
                maxudp = int(operand.dst[5:])
        elif operand.dst[0] == "O":
            if int(operand.dst[3:]) > maxop:
                maxop = int(operand.dst[3:])

        # ====== JAction Part ======
    elif (
        opcode == "lshift_add_imm"
        or opcode == "rshift_add_imm"
        or opcode == "lshift_or_imm"
        or opcode == "rshift_or_imm"
        or opcode == "lshift_sub_imm"
        or opcode == "lshift_and_imm"
        or opcode == "rshift_and_imm"
        or opcode == "rshift_sub_imm"
        or opcode == "block_compare"
        or opcode == "block_compare_i"
        or opcode == "ev_update_1"
        or opcode == "ev_update_2"
        or opcode == "ev_update_reg_imm"
        or opcode == "cmpswp"
        or opcode == "cmpswp_ri"
        or opcode == "cmpswp_i"
    ):
        ActionClass = "JAction"
        operand.src = part[1]
        operand.dst = part[2]
        operand.imm = part[3]
        operand.imm2 = part[4]
        if operand.src[0] == "U":
            maxudp = int(operand.src[5:])
        elif operand.src[0] == "O":
            maxop = int(operand.src[3:])
        if operand.dst[0] == "U":
            if int(operand.dst[5:]) > maxudp:
                maxudp = int(operand.dst[5:])
        elif operand.dst[0] == "O":
            if int(operand.dst[3:]) > maxop:
                maxop = int(operand.dst[3:])
        # ======  TAction Part ======
    # added by Marzi (xor bellow)
    elif (
        opcode == "add"
        or opcode == "compare_string"
        or opcode == "compare_string_from_out"
        or opcode == "copy"
        or opcode == "copy_ob_lm"
        or opcode == "copy_from_out"
        or opcode == "sub"
        or opcode == "compreg"
        or opcode == "compreg_eq"
        or opcode == "compreg_lt"
        or opcode == "compreg_gt"
        or opcode == "bitwise_or"
        or opcode == "bitwise_and"
        or opcode == "bitwise_xor"
        or opcode == "rshift_t"
        or opcode == "lshift_t"
        or opcode == "bitclr"
        or opcode == "bitset"
        or opcode == "fp_div"
        or opcode == "fp_add"
        or opcode == "arithrshift_t"
    ):  # added by Marziyeh (arithrshifts)
        # Ivy added fp_div and fp_add

        ActionClass = "TAction"
        operand.src = part[1]
        operand.rt = part[2]
        operand.dst = part[3]
        if operand.src[0] == "U":
            maxudp = int(operand.src[5:])
        elif operand.src[0] == "O":
            maxop = int(operand.src[3:])
        if operand.dst[0] == "U":
            if int(operand.dst[5:]) > maxudp:
                maxudp = int(operand.dst[5:])
        elif operand.dst[0] == "O":
            if int(operand.dst[3:]) > maxop:
                maxop = int(operand.dst[3:])
        if operand.rt[0] == "U":
            if int(operand.rt[5:]) > maxudp:
                maxudp = int(operand.rt[5:])
        elif operand.rt[0] == "O":
            if int(operand.rt[3:]) > maxop:
                maxop = int(operand.rt[3:])

    elif opcode == "bne" or opcode == "beq" or opcode == "blt" or opcode == "bgt" or opcode == "bge" or opcode == "ble" or opcode == "jmp":
        ActionClass = "BAction"
        if opcode == "jmp":
            if part[1][0] == "#":  # seqnum
                operand.dst = part[1][1:]
                operand.dst_issb = 0
            elif part[1][0:5] == "block":  # shared block
                operand.dst = part[1]
                operand.dst_issb = 1
            else:  # label
                operand.dst = part[1]
                operand.dst_issb = 2
        else:
            if part[3][0] == "#":  # seqnum
                operand.dst = part[3][1:]
                operand.dst_issb = 0
            elif part[3][0:5] == "block":  # shared block
                operand.dst = part[3]
                operand.dst_issb = 1
            else:  # label
                operand.dst = part[3]
                operand.dst_issb = 2

        if opcode != "jmp":
            if part[1][0] == "U" or part[1][0] == "L":  # "UDPR"
                operand.op1_ob_or_reg = 1
            else:
                operand.op1_ob_or_reg = 0
            if part[2][0] == "U" or part[2][0] == "L":  # "UDPR":
                operand.op2_ob_or_reg_or_imm = 1
            elif part[2][0] == "O":  # "OB":
                operand.op2_ob_or_reg_or_imm = 0
            else:
                operand.op2_ob_or_reg_or_imm = 2
            operand.op1 = part[1]
            operand.op2 = part[2]
        if operand.op1[0] == "U":
            maxudp = int(operand.op1[5:])
        elif operand.op1[0] == "O":
            maxop = int(operand.op1[3:])
        if operand.op2[0] == "U":
            if int(operand.op2[5:]) > maxudp:
                maxudp = int(operand.op2[5:])
        elif operand.op2[0] == "O":
            if int(operand.op2[3:]) > maxop:
                maxop = int(operand.op2[3:])

    elif opcode == "send_with_ret" or opcode == "send_reply":
        ActionClass = "MAction"
        # operand.event_label = part[1]
        operand.event = part[1]
        operand.dst = part[2]
        operand.addr = part[3]
        operand.size = part[4]
        operand.rw = part[5]
        operand.addr_mode = part[6]
        for i in range(1, 4):
            if part[i][0] == "U":
                if int(part[i][5:]) > maxudp:
                    maxudp = int(part[i][5:])
            elif part[i][0] == "O":
                if int(part[i][3:]) > maxop:
                    maxop = int(part[i][3:])

    elif opcode == "send_with_ret":
        ActionClass = "MAction"
        # operand.event_label = part[1]
        operand.event = part[1]
        operand.dst = part[2]
        operand.addr = part[3]
        operand.size = part[4]
        if operand.event[0] == "U":
            maxudp = int(operand.event[5:])
        elif operand.event[0] == "O":
            maxop = int(operand.event[3:])
        if operand.dst[0] == "U":
            if int(operand.dst[5:]) > maxudp:
                maxudp = int(operand.dst[5:])
        elif operand.dst[0] == "O":
            if int(operand.dst[3:]) > maxop:
                maxop = int(operand.dst[3:])
        if operand.addr[0] == "U":
            if int(operand.addr[5:]) > maxudp:
                maxudp = int(operand.addr[5:])
        elif operand.addr[0] == "O":
            if int(operand.addr[3:]) > maxop:
                maxop = int(operand.addr[3:])

    elif opcode == "ev_update_reg_2":
        ActionClass = "EAction"
        operand.src = part[1]
        operand.dst = part[2]
        operand.op1 = part[3]
        operand.op2 = part[4]
        operand.imm = part[5]
        for i in range(1, 5):
            if part[i][0] == "U":
                if int(part[i][5:]) > maxudp:
                    maxudp = int(part[i][5:])
            elif part[i][0] == "O":
                if int(part[i][3:]) > maxop:
                    maxop = int(part[i][3:])
        # if operand.src[0] == 'U':
        #    maxudp = int(operand.src[5:])
        # elif operand.src[0] == 'O':
        #    maxop = int(operand.src[3:])
        # if operand.dst[0] == 'U':
        #    if(int(operand.dst[5:]) > maxudp):
        #        maxudp = int(operand.dst[5:])
        # elif operand.dst[0] == 'O':
        #    if(int(operand.dst[3:]) > maxop):
        #        maxop = int(operand.dst[3:])
        # if operand.op1[0] == 'U':
        #    if(int(operand.op1[5:]) > maxudp):
        #        maxudp = int(operand.op1[5:])
        # elif operand.op1[0] == 'O':
        #    if(int(operand.op1[3:]) > maxop):
        #        maxop = int(operand.op1[3:])
        # if operand.op2[0] == 'U':
        #    if(int(operand.op2[5:]) > maxudp):
        #        maxudp = int(operand.op2[5:])
        # elif operand.op2[0] == 'O':
        #    if(int(operand.op2[3:]) > maxop):
        #        maxop = int(operand.op2[3:])

    elif opcode == "yield" or opcode == "yield_operand" or opcode == "yield_terminate":
        ActionClass = "YAction"
        operand.imm = part[1]

    # New send instruction interface
    elif opcode == "send" or opcode == "send4":
        ActionClass = "SAction"
        operand.event = part[1]
        operand.dst = part[2]
        operand.cont = part[3]
        operand.op1 = part[4]
        operand.op2 = part[5]
        operand.addr_mode = part[6]
        for i in range(1, 6):
            if part[i][0] == "U":
                if int(part[i][5:]) > maxudp:
                    maxudp = int(part[i][5:])
            elif part[i][0] == "O":
                if int(part[i][3:]) > maxop:
                    maxop = int(part[i][3:])
        # if opcode[4] == '4':
        #    operand.size = part[7]

    elif opcode == "send4_wret" or opcode == "send_wret" or opcode == "send4_wcont" or opcode == "send_wcont":
        ActionClass = "SAction"
        operand.event = part[1]
        operand.dst = part[2]
        operand.cont = part[3]
        operand.op1 = part[4]
        if opcode[4] != "4" or (opcode[4] == "4" and len(part) > 5):
            operand.op2 = part[5]
        for i in range(1, len(part)):
            if part[i][0] == "U":
                if int(part[i][5:]) > maxudp:
                    maxudp = int(part[i][5:])
            elif part[i][0] == "O":
                if int(part[i][3:]) > maxop:
                    maxop = int(part[i][3:])

    elif opcode == "send_dmlm" or opcode == "send_dmlm_wret" or opcode == "send4_dmlm" or opcode == "send4_dmlm_wret":
        ActionClass = "SAction"
        operand.event = "Empty"  # No event label required for destination in DRAM/LM
        operand.dst = part[1]
        operand.cont = part[2]
        operand.op1 = part[3]
        # if opcode[4] != '4' or (opcode[4] == '4' and len(part) > 5):
        if opcode[4] != '4' or (opcode[4] == '4' and (part[4][0]=='U' or part[4][0] == 'O')):
            operand.op2 = part[4]
            operand.addr_mode = part[5]
        else:
            #operand.op2 = "Empty"
            operand.addr_mode = part[4]
        # else:
        #    operand.addr_mode = part[4]
        # if opcode[4] != '4' or (opcode[4] == '4' and len(part) > 5):
        #    operand.op2 = part[5]
        for i in range(1, 5):
            if part[i][0] == "U":
                if int(part[i][5:]) > maxudp:
                    maxudp = int(part[i][5:])
            elif part[i][0] == "O":
                if int(part[i][3:]) > maxop:
                    maxop = int(part[i][3:])

    elif opcode == "send_dmlm_ld" or opcode == "send_dmlm_ld_wret":
        ActionClass = "SAction"
        operand.event = "Empty"  # No event label required for destination in DRAM/LM
        operand.dst = part[1]
        operand.cont = part[2]
        operand.op2 = part[3]
        operand.addr_mode = part[4]
        for i in range(1, 4):
            if part[i][0] == "U":
                if int(part[i][5:]) > maxudp:
                    maxudp = int(part[i][5:])
            elif part[i][0] == "O":
                if int(part[i][3:]) > maxop:
                    maxop = int(part[i][3:])

    elif opcode == "send_reply" or opcode == "send4_reply":
        ActionClass = "SAction"
        operand.event = "Empty"
        operand.op1 = part[1]
        if opcode[4] != "4" or (opcode[4] == "4" and len(part) > 2):
            operand.op2 = part[2]
        for i in range(2, len(part)):
            if part[i][0] == "U":
                if int(part[i][5:]) > maxudp:
                    maxudp = int(part[i][5:])
            elif part[i][0] == "O":
                if int(part[i][3:]) > maxop:
                    maxop = int(part[i][3:])

    # send any number
    elif opcode == "send_any_wcont" or opcode == "send_any_wret" or opcode == "send_any":
        ActionClass = "SPAction"
        operand.event = part[1]
        operand.dst = part[2]
        if len(part) > 3:
            operand.cont = part[3]
        if len(part) > 4:
            operand.op1 = part[4]
        if len(part) > 5:
            operand.reglist = part[5:]

        for i in range(1, len(part)):
            if part[i][0] == "U":
                if int(part[i][5:]) > maxudp:
                    maxudp = int(part[i][5:])
            elif part[i][0] == "O":
                if int(part[i][3:]) > maxop:
                    maxop = int(part[i][3:])

    elif opcode == "print":
        ActionClass = "PAction"
        match = re.search(r"print\s*'(.*)'(.*)", asm_inst)
        if match:
            operand.formatstr = match.group(1)
            operand.reglist = match.group(2).split()
        else:
            print("Error parsing 'print'.")
            exit(1)

    # Just a convenience instruction for emulation
    elif opcode == "send_top":
        ActionClass = "MAction"
        operand.addr = part[1]
        operand.size = part[2]

    elif opcode == "perflog":
        ActionClass = "PerflogAction"
        operand.perflog_mode = int(part[1])
        if operand.perflog_mode == 0:
            operand.perflog_payload_list = part[2:]
        elif operand.perflog_mode == 1:
            operand.perflog_msg_id = part[2]
            match = re.search(r"perflog\s*1\s*([0-9]+)\s*'(.*)'(.*)", asm_inst)
            if match:
                operand.perflog_msg_id = int(match.group(1))
                operand.formatstr = match.group(2)
                operand.reglist = match.group(3).split()
            else:
                print("Error parsing 'perflog' mode 1.")
                exit(1)
        elif operand.perflog_mode == 2:
            operand.perflog_msg_id = part[2]
            match = re.search(r"perflog\s*2\s*'(.*)'\s*([0-9]+)\s*'(.*)'(.*)", asm_inst)
            if match:
                operand.perflog_payload_list = match.group(1).split()
                operand.perflog_payload_list = [int(p) for p in operand.perflog_payload_list]
                operand.perflog_msg_id = int(match.group(2))
                operand.formatstr = match.group(3)
                operand.reglist = match.group(4).split()
            else:
                print("Error parsing 'perflog' mode 2.")
                exit(1)
        else:
            print("Invalid 'perflog' mode.")
            exit(1)

    # Send Pseudo Instructions!
    # send any
    # send reply
    #
    # elif opcode ==

    operand.maxudp = maxudp
    operand.maxop = maxop
    return ActionClass, operand


def Transition_eq(tr1, t):
    if isinstance(tr1, tr2.__class__):
        primitiveEQ = False
        if tr1.dst == tr2.dst and tr1.label == tr2.label and tr1.src == tr2.src and tr1.anno_type == tr2.anno_type:
            primitiveEQ = True
        actionEQ = True
        if len(tr1.actions) != len(tr2.actions):
            actionEQ = False
        else:
            for idx in range(len(tr1.actions)):
                if not tr1.actions[idx] == tr2.actions[idx]:
                    actionEQ = False
                    break

        if actionEQ and primitiveEQ:
            return True
        else:
            return False
    else:
        return False


def State_eq(s1, s2):
    if isinstance(s1, s2.__class__):
        if s1.state_id == s2.state_id:
            return True
        else:
            return False
    else:
        return False


def Taction_eq(t_a1, t_a2):
    if isinstance(t_a1, t_a2.__class__):
        if t_a1.opcode == t_a2.opcode and t_a1.dst == t_a2.dst and t_a1.src == t_a2.src and t_a1.rt == t_a2.rt:
            return True
        else:
            return False
    else:
        return False


def Jaction_eq(j_a1, j_a2):
    if isinstance(j_a1, j_a2.__class__):
        if j_a1.opcode == j_a2.opcode and j_a1.dst == j_a2.dst and j_a1.src == j_a2.src and j_a1.imm == j_a2.imm and j_a1.imm2 == j_a2.imm2:
            return True
        else:
            return False
    else:
        return False


def Action_eq(a_a1, a_a2):
    if isinstance(a_a1, a_a2.__class__):
        if a_a1.opcode == a_a2.opcode and a_a1.dst == a_a2.dst and a_a1.src == a_a2.src and a_a1.imm == a_a2.imm:
            return True
        else:
            return False
    else:
        return False


def logical_rshift(val, n):
    result = (val % 0x100000000) >> n
    # print "looooooooooooooooooooooooooooooog rshift->  "+str(val)+">>>"+str(n)+"="+str(result)+"\n"
    return result


# value is an n-bit number to be shifted m times
def arithmetic_rshift(value, n, m):
    if value & 2 ** (n - 1) != 0:  # MSB is 1, i.e. value is negative
        filler = int("1" * m + "0" * (n - m), 2)
        value = (value >> m) | filler  # fill in 0's with 1's
        return value
    else:
        return value >> m

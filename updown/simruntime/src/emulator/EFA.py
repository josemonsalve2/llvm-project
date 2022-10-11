# ==============================================================
# 10x10 - Systematic Heterogenous Architecture
# https://sites.google.com/site/uchicagolssg/lssg/research/10x10
# Copyright (C) 2016 University of Chicago.
# See license.txt in top-level directory.
# ==============================================================

from enum import Enum, auto
import sys

from EfaUtil import *


# Payload selection enum for perflog
class PerfLogPayload(Enum):
    UD_CYCLE_STATS = auto()
    UD_ACTION_STATS = auto()
    UD_TRANS_STATS = auto()
    UD_QUEUE_STATS = auto()
    UD_LOCAL_MEM_STATS = auto()
    UD_MEM_INTF_STATS = auto()
    SYS_MEM_INTF_STATS = auto()


# ====== internal helper function ======
def GetAction(asm_inst):
    ActionClass, operand = ParseAction(asm_inst)
    if ActionClass == "Action":
        action = Action(operand.opcode, operand.dst, operand.src, operand.imm, operand.label, 1)
    elif ActionClass == "JAction":
        action = JAction(operand.opcode, operand.dst, operand.src, operand.imm, operand.imm2, operand.label, 1)
    elif ActionClass == "EAction":
        action = EAction(operand.opcode, operand.src, operand.dst, operand.op1, operand.op2, operand.imm, operand.label)
    elif ActionClass == "TAction":
        action = TAction(operand.opcode, operand.dst, operand.src, operand.rt, operand.label, 1)
    elif ActionClass == "BAction":
        action = BAction(
            operand.opcode,
            operand.dst,
            operand.op1,
            operand.op2,
            operand.op1_ob_or_reg,
            operand.op2_ob_or_reg_or_imm,
            operand.dst_issb,
            operand.label,
        )
    elif ActionClass == "MAction":
        action = MAction(
            operand.opcode, operand.event, operand.dst, operand.addr, operand.size, operand.rw, operand.addr_mode, operand.label
        )
    elif ActionClass == "SAction":
        action = SAction(
            operand.opcode,
            operand.event,
            operand.dst,
            operand.cont,
            operand.op1,
            operand.op2,
            operand.addr_mode,
            operand.size,
            operand.label,
        )
    elif ActionClass == "SPAction":
        action = SPAction(
            operand.opcode, operand.event, operand.dst, operand.cont, operand.op1, operand.reglist, operand.addr_mode, operand.label
        )
    elif ActionClass == "PAction":
        action = PAction(operand.opcode, operand.formatstr, operand.reglist, operand.label)
    elif ActionClass == "PerflogAction":
        action = PerflogAction(operand.opcode, operand.perflog_mode, operand.perflog_payload_list, operand.perflog_msg_id, operand.formatstr, operand.reglist, operand.label)
    elif ActionClass == "UserCounterAction":
        action = UserCounterAction(operand.opcode, operand.userctr_mode, operand.userctr_num, operand.userctr_arg, operand.label)
    elif ActionClass == "YAction":
        action = YAction(operand.opcode, operand.imm, operand.label)
    else:
        print("Cannot parse the action:\t" + asm_inst)
        exit()
    return action, operand.maxudp, operand.maxop


# ==============================

# Defining a class event that is very similar to transition for now. Could potentially merge with Transition


class Event:
    global_id = 0

    def __init__(self, event_label, num_ops):
        self.event_id = Event.global_id
        Event.global_id += 1
        self.num_operands = num_ops
        self.event_label = event_label
        self.event_base = 0
        self.pthread_id = 0
        self.lane_num = 0
        self.thread_id = 0xFF  # to be assigned later
        self.cycle = 0
        # event_word - PTID[31:24]|TID[23:16]|EBASE[15:8]|ELABEL[7:0]
        self.event_word = (
            ((int(self.lane_num) << 24) & 0xFF000000)
            | ((int(self.thread_id) << 16) & 0x00FF0000)
            | ((int(self.event_base) << 8) & 0x0000FF00)
            | (int(self.event_label) & 0x000000FF)
        )

    def setlanenum(self, lane_num):
        self.lane_num = lane_num
        self.event_word = (self.event_word & 0x00FFFFFF) | ((int(self.lane_num) << 24) & 0xFF000000)

    def setthreadid(self, thread_id):
        self.thread_id = thread_id
        self.event_word = (self.event_word & 0xFF00FFFF) | ((int(self.thread_id) << 16) & 0x00FF0000)

    def printOut(self, LEVEL):
        printd(
            "Event( ID: " + str(self.event_id)
            + ", LaneID:" + str(self.lane_num)
            + ", ThreadID:" + str(self.thread_id)
            + ", eventLabel: " + str(self.event_label)
            + ")\n",
            LEVEL,
        )

    def getEventID(self):
        return self.event_id

    def getEventlabel(self):
        return self.event_label

    def numOps(self):
        return self.num_operands

    def set_cycle(self, cyc):
        self.cycle = cyc


#    #====== API expose externally, to write machine code level UDP program
#    def writeAction(self, asm_inst):
#        action = GetAction(asm_inst)
#        self.addAction(action)
#        return action
#
#    def getSize(self):
#        return len(self.actions)
#
#    def addAction(self, action):
#        if self.hasActions():
#            self.actions[-1].last = 0
#        if action.opcode == 'goto':
#            action.last = 0
#        self.actions.append(action)


class State:
    global_id = 0

    def __init__(self):
        self.state_id = State.global_id
        State.global_id += 1
        self.trans = []
        # we don't use state alphabet if it is empty
        # if not empty, we state.alphabet instead of efa.alphabet
        self.alphabet = []

    def add_tran(self, transition):
        self.trans.append(transition)

    def get_tran(self, label, dst=None):
        # Merge two get_tran functions together (Modify by Lang Yu)
        res = []
        # print("StateIN State_ID:%d : Event Label Requested: %s, state.trans.len:%d " % (self.state_id, label, len(self.trans)))

        if dst is None:
            # find transition list by label
            # print("Size of trans: %d" % len(self.trans))
            # print("Searching for label: %s" % label)
            for tr in self.trans:
                # print("Trans label: %s" % tr.label)
                if tr.label == label:
                    res.append(tr)
            # add epsilon transition if dst state has any
            epsilon_tran = []
            for tr in res:
                res_dst = tr.dst
                for dst_tr in res_dst.trans:
                    if dst_tr.anno_type == "epsilon":
                        epsilon_tran.append(dst_tr)
            for ele in epsilon_tran:
                res.append(ele)
            return res
        else:
            # find transition list by destination and label
            if label != -1:
                for tr in self.trans:
                    if tr.dst == dst and tr.label == label:
                        res.append(tr)
            else:
                # Lang Yu add this to faciliate upper level construction
                # find all transitions to dst state
                for tr in self.trans:
                    if tr.dst == dst:
                        res.append(tr)
            return res

    # Comment out by Lang Yu
    # ====== get transition list  by label
    # def get_tran(self, label):
    #     res = []
    #     for tr in self.trans:
    #         if tr.label == label:
    #             res.append(tr)
    #     return res

    # ====== get transition list by annotation type
    def get_tran_byAnnotation(self, anno_type):
        res = []
        for tr in self.trans:
            if tr.anno_type == anno_type:
                res.append(tr)
        return res

    # ====== get transition by pure label. No epsilon transition even dst state has
    def get_tran_byLabel(self, label):
        res = []
        # find transition list by label
        for tr in self.trans:
            if tr.label == label:
                res.append(tr)
        return res

    def get_event(self, label):
        res = []
        # find transition list by label
        for tr in self.events:
            if tr.label == label:
                res.append(tr)
        return res

    # ====== get transitions by destination state
    def get_tran_byDest(self, dst):
        res = []
        for tr in self.trans:
            if tr.dst == dst:
                res.append(tr)
        return res

    # ====== get transition's destination state list by label
    def get_dst(self, label):
        res = []
        for tr in self.trans:
            if tr.label == label:
                res.append(tr.dst)
        return res

    def printOut(self, LEVEL):
        printd("state_id: " + str(self.state_id) + "\n", LEVEL)
        for tr in self.trans:
            tr.printOut(LEVEL)

    def getSize(self):
        tran_size = len(self.trans)
        action_size = 0
        for tr in self.trans:
            action_size += tr.getSize()
        return tran_size, action_size

    # ====== API expose externally, to write machine code level UDP program
    def writeTransition(self, Type, src_state, dst_state, label):
        tran = Transition(src_state, dst_state, label, Type)
        self.add_tran(tran)
        return tran

    def writeEvents(self, Type, src_state, dst_state, label):
        event = Event(src_state, dst_state, label, Type)
        self.add_event(event)
        return event


class Transition:
    global_id = 0

    # ====== actions associated with the transition constructor can be a singleton object or a list of actions
    def __init__(self, src, dst, label, anno_type="labeled", action=None):
        self.trans_id = Transition.global_id
        Transition.global_id += 1
        self.src = src
        self.dst = dst
        self.label = label
        self.anno_type = anno_type
        self.actions = []
        self.opsize = 0
        self.maxop = 0
        self.maxudp = 0
        self.labeldict = {}

        if action is not None:
            self.actions = concatSet(self.actions, action)
        for act in self.actions:
            act.last = 0
        if len(self.actions) > 0:
            self.actions[-1].last = 1

    def printOut(self, LEVEL):
        printd(
            "tran( src: " + str(self.src.state_id)
            + ", label: " + str(self.label)
            + ", dst: " + str(self.dst.state_id) + ", "
            + self.anno_type + ", ",
            LEVEL,
        )
        for act in self.actions:
            act.printOut(LEVEL)
        printd(")\n", LEVEL)

    def hasActions(self):
        if self.actions == []:
            return False
        else:
            return True

    # ====== API expose externally, to write machine code level UDP program
    def writeAction(self, asm_inst):
        action, maxudp, maxop = GetAction(asm_inst)
        self.addAction(action)
        if action.label is not None:
            self.labeldict[action.label] = str(len(self.actions) - 1)
        if maxudp > self.maxudp:
            self.maxudp = maxudp
        if maxop > self.maxop:
            self.maxop = maxop
        return action

    def getSize(self):
        return len(self.actions)

    def addAction(self, action):
        if self.hasActions():
            self.actions[-1].last = 0
        if action.opcode == "goto":
            action.last = 0
        self.actions.append(action)

    def getAction(self, seqnum):
        return self.actions[int(seqnum)]

    #        for action in self.actions:
    #            if action.seqnum == seqnum:
    #                return action
    def getMaxOp(self):
        return self.maxop

    def getMaxUdp(self):
        return self.maxudp


class EFA:
    def __init__(self, alphabet=range(0, 256)):
        self.states = []

        # set of initial state
        self.init_state_id = []

        # set of state whose activation you want to export to a file after loading
        self.export_state_id = []

        # ====== sharedBlock[key] = [action1][action2]...
        # key is 'block_i'  value is an action list
        self.sharedBlock = dict()
        self.sharedBlocklabels = dict()

        # ====== Overall alphabet
        self.alphabet = alphabet

        # ====== efa's signature to tell whether it is in Assembly level or Machine code level
        # ====== By default, it is in Assembly level
        self.code_level = "assembly"

        # Andronicus adding udprsize, opsize
        self.udpsize = 0
        self.opsize = 0

    def appendBlockAction(self, blockid, inst):
        # inst can be assembly(string format) or deserialized action
        if (
            not isinstance(inst, Action)
            and not isinstance(inst, JAction)
            and not isinstance(inst, BAction)
            and not isinstance(inst, MAction)
            and not isinstance(inst, YAction)
            and not isinstance(inst, TAction)
        ):
            action, maxudp, maxop = GetAction(inst)
            if maxudp > self.udpsize:
                self.udpsize = maxudp
        else:
            action = inst

        action.last = 1
        if blockid not in self.sharedBlock:
            self.sharedBlock[blockid] = [action]
            self.sharedBlocklabels[blockid] = dict()
            if action.label is not None:
                self.sharedBlocklabels[blockid][action.label] = str(len(self.sharedBlock[blockid]) - 1)
        else:
            self.sharedBlock[blockid][-1].last = 0
            self.sharedBlock[blockid].append(action)
            if action.label is not None:
                self.sharedBlocklabels[blockid][action.label] = str(len(self.sharedBlock[blockid]) - 1)

    def add_state(self, state):
        self.states.append(state)

    def get_state(self, state_id):
        for s in self.states:
            if s.state_id == state_id:
                return s
        return None

    def get_tran(self, trans_id):
        for s in self.states:
            for tr in s.trans:
                if tr.trans_id == trans_id:
                    return tr
        return None

    def add_initId(self, init_id):
        self.init_state_id.append(init_id)

    def printtry(self):
        print("Let's try this")

    def printOut(self, LEVEL):
        printd("==================Shared Action Blocks =================\n", LEVEL)
        for k, v in self.sharedBlock.items():
            printd(k, LEVEL)
            for act in v:
                act.printOut(LEVEL)
            printd("\n===================================\n", LEVEL)
        printd("==================Transitions =================\n", LEVEL)
        for s in self.states:
            s.printOut(LEVEL)
            printd("===================================\n", LEVEL)

    def getSize(self):
        total_tran = 0
        total_action = 0
        total_shared = 0
        for st in self.states:
            tran_size, action_size = st.getSize()
            total_tran += tran_size
            total_action += action_size
        for k, v in self.sharedBlock.iteritems():
            total_shared += len(v)
        return total_tran, total_action, total_shared

    def cleanEFAglobal(self):
        State.global_id = 0
        Transition.global_id = 0

    def calcUdpSize(self):
        for state in self.states:
            for tran in state.trans:
                if tran.maxudp > self.udpsize:
                    self.udpsize = tran.maxudp
        self.udpsize += 1

    def getUdpSizeonly(self):
        return self.udpsize

    def getUdpSize(self):
        for state in self.states:
            for tran in state.trans:
                if tran.maxudp > self.udpsize:
                    self.udpsize = tran.maxudp
        return self.udpsize

    def fixlabels(self):
        # import pdb
        # pdb.set_trace()
        for state in self.states:
            for tran in state.trans:
                for action in tran.actions:
                    if type(action).__name__ == "BAction":
                        if action.dst_issb == 2:
                            action.dst = tran.labeldict[action.dst]  # Assign seq num to dst
        for k, v in self.sharedBlock.items():
            for action in v:
                if type(action).__name__ == "BAction":
                    if action.dst_issb == 2:
                        action.dst = self.sharedBlocklabels[k][action.dst]  # Assign seq num to dst

    def fixlabels(self):
        # import pdb
        # pdb.set_trace()
        for state in self.states:
            for tran in state.trans:
                for action in tran.actions:
                    if type(action).__name__ == "BAction":
                        if action.dst_issb == 2:
                            action.dst = tran.labeldict[action.dst]  # Assign seq num to dst
        for k, v in self.sharedBlock.items():
            for action in v:
                if type(action).__name__ == "BAction":
                    if action.dst_issb == 2:
                        action.dst = self.sharedBlocklabels[k][action.dst]  # Assign seq num to dst


class Action(object):
    def __init__(self, opcode, dst, src, imm, label, last):
        self.opcode = opcode
        self.dst = dst
        self.src = src
        self.imm = imm
        self.last = last
        self.label = label

    def printOut(self, LEVEL):
        printd("[" + self.opcode + " " + str(self.src) + "," + str(self.dst) + ",$" + str(self.imm) + "," + str(self.last) + "]", LEVEL)

    def getSeqnum(self):
        return self.seqnum

    def fieldsEqual(self, ref):
        if self.opcode == ref.opcode and self.src == ref.src and self.dst == ref.dst and self.imm == ref.imm and self.last == ref.last:
            return True
        else:
            return False


class JAction(object):
    def __init__(self, opcode, dst, src, imm, imm2, label, last):
        self.opcode = opcode
        self.dst = dst
        self.src = src
        self.imm = imm
        self.last = last
        self.imm2 = imm2
        self.label = label

    def printOut(self, LEVEL):
        printd(
            "["
            + self.opcode + " "
            + str(self.src) + ","
            + str(self.dst)
            + ",$" + str(self.imm)
            + ",$" + str(self.imm2) + ","
            + str(self.last)
            + "]",
            LEVEL,
        )

    def fieldsEqual(self, ref):
        if (
            self.opcode == ref.opcode
            and self.src == ref.src
            and self.dst == ref.dst
            and self.imm == ref.imm
            and self.imm2 == ref.imm2
            and self.last == ref.last
        ):
            return True
        else:
            return False


class EAction(object):
    def __init__(self, opcode, src, dst, op1, op2, imm, label):
        self.opcode = opcode
        self.dst = dst
        self.src = src
        self.imm = imm
        self.op1 = op1
        self.op2 = op2
        self.label = label

    def printOut(self, LEVEL):
        printd(
            "["
            + self.opcode + " "
            + str(self.src) + ","
            + str(self.dst)
            + ",$" + str(self.imm)
            + ",$" + str(self.op1) + ","
            + str(self.op2)
            + "]",
            LEVEL,
        )

    def fieldsEqual(self, ref):
        if (
            self.opcode == ref.opcode
            and self.src == ref.src
            and self.dst == ref.dst
            and self.imm == ref.imm
            and self.op1 == ref.op1
            and self.op2 == ref.op2
        ):
            return True
        else:
            return False


class TAction(object):
    def __init__(self, opcode, dst, src, rt, label, last):
        self.opcode = opcode
        self.dst = dst
        self.src = src
        self.last = last
        self.rt = rt
        self.label = label

    def printOut(self, LEVEL):
        printd("[" + self.opcode + " " + str(self.src) + "," + str(self.rt) + "," + str(self.dst) + "," + str(self.last) + "]", LEVEL)

    def fieldsEqual(self, ref):
        if self.opcode == ref.opcode and self.src == ref.src and self.dst == ref.dst and self.rt == ref.rt and self.last == ref.last:
            return True
        else:
            return False


class BAction(object):
    def __init__(self, opcode, dst, op1, op2, op1_ob_or_reg, op2_ob_or_reg_or_imm, dst_issb, label):
        self.opcode = opcode
        self.dst = dst
        self.dst_issb = dst_issb
        self.op1 = op1
        self.op2 = op2
        self.imm = "Empty"
        self.op1_ob_or_reg = op1_ob_or_reg
        self.op2_ob_or_reg_or_imm = op2_ob_or_reg_or_imm
        self.label = label

    def printOut(self, LEVEL):
        printd("[" + self.opcode + " " + str(self.dst) + "," + str(self.op1) + "," + str(self.op2) + "]", LEVEL)

    def fieldsEqual(self, ref):
        if (
            self.opcode == ref.opcode
            and self.dst == ref.dst
            and self.op1 == ref.op1
            and self.op2 == ref.op2
            and self.op1_ob_or_reg == ref.op1_ob_or_reg
            and self.op2_ob_or_reg_or_imm == ref.dst_ob_or_reg_or_imm
        ):
            return True
        else:
            return False


# Message Action
class MAction(object):
    def __init__(self, opcode, event, dst, addr, size, rw, addr_mode, label):
        self.opcode = opcode
        self.event = event
        self.dst = dst
        self.addr = addr
        self.size = size
        self.rw = rw
        self.addr_mode = addr_mode
        self.label = label

    def printOut(self, LEVEL):
        printd(
            "["
            + self.opcode + " "
            + str(self.event) + ","
            + str(self.dst) + ","
            + str(self.addr) + ","
            + str(self.size) + ","
            + str(self.rw)
            + str(self.addr_mode)
            + "]",
            LEVEL,
        )

    def fieldsEqual(self, ref):
        if (
            self.opcode == ref.opcode
            and self.dst == ref.dst
            and self.addr == ref.addr
            and self.size == ref.size
            and self.rw == ref.rw
            and self.addr_mode == ref.addr_mode
            and self.event == ref.event
        ):
            return True
        else:
            return False


class SAction(object):
    def __init__(self, opcode, event, dst, cont, op1, op2, addr_mode, size, label):
        self.opcode = opcode
        self.event = event
        self.dst = dst
        self.cont = cont
        self.op1 = op1
        self.op2 = op2
        self.addr_mode = addr_mode
        self.size = size
        self.label = label

    def printOut(self, LEVEL):
        printd(
            "["
            + self.opcode + " "
            + str(self.event) + ","
            + str(self.dst) + ","
            + str(self.addr_mode) + ","
            + str(self.cont) + ","
            + str(self.op1) + ","
            + str(self.op2)
            + "]",
            LEVEL,
        )

    def fieldsEqual(self, ref):
        if (
            self.opcode == ref.opcode
            and self.dst == ref.dst
            and self.cont == ref.cont
            and self.op1 == ref.op1
            and self.op2 == ref.op2
            and self.addr_mode == ref.addr_mode
            and self.event == ref.event
        ):
            return True
        else:
            return False


class SPAction(object):
    def __init__(self, opcode, event, dst, cont, op1, reglist, addr_mode):
        self.opcode = opcode
        self.event = event
        self.dst = dst
        self.cont = cont
        self.op1 = op1
        self.reglist = reglist
        self.addr_mode = addr_mode

    def printOut(self, LEVEL):
        printd(
            "["
            + self.opcode + " "
            + str(self.event) + ","
            + str(self.dst) + ","
            + str(self.addr_mode) + ","
            + str(self.cont) + ","
            + str(self.op1)
            + ", RegNum:" + str(len(self.reglist)) + ","
            + "]",
            LEVEL,
        )

    def fieldsEqual(self, ref):
        if (
            self.opcode == ref.opcode
            and self.dst == ref.dst
            and self.cont == ref.cont
            and self.reglist == ref.reglist
            and self.addr_mode == ref.addr_mode
            and self.event == ref.event
        ):
            return True
        else:
            return False


class PAction(object):
    def __init__(self, opcode, fmtstr, reglist, label):
        self.opcode = opcode
        self.fmtstr = fmtstr
        self.reglist = reglist
        self.label = label

    def printOut(self, LEVEL):
        regstrlist = ",".join(self.reglist)
        printd("[" + self.opcode + "," + str(self.fmtstr) + "," + str(regstrlist) + "]", LEVEL)


class PerflogAction(object):
    def __init__(self, opcode, mode, payload_list, msg_id, fmtstr, reglist, label):
        self.opcode = opcode
        # mode: 0 - stats dump
        # mode: 1 - message log
        self.mode = mode
        self.payload_list = payload_list
        self.msg_id = msg_id
        self.fmtstr = fmtstr
        self.reglist = reglist
        self.label = label

    def printOut(self, LEVEL):
        if self.mode == 0:
            printd("[" + self.opcode + "," + str(self.mode) + "," + str(self.payload_list) + "]", LEVEL)
        elif self.mode == 1:
            regstrlist = ",".join(self.reglist)
            printd("[" + self.opcode + "," + str(self.mode) + "," + str(self.msg_id) + "," + str(self.fmtstr) + "," + str(regstrlist) + "]", LEVEL)
        elif self.mode == 2:
            regstrlist = ",".join(self.reglist)
            printd("[" + self.opcode + "," + str(self.mode) + "," + str(self.payload_list) + "," + str(self.msg_id) + "," + str(self.fmtstr) + "," + str(regstrlist) + "]", LEVEL)


class UserCounterAction(object):
    def __init__(self, opcode, userctr_mode, userctr_num, userctr_arg, label):
        self.opcode = opcode
        self.mode = userctr_mode
        self.ctr_num = userctr_num
        self.arg = userctr_arg
        self.label = label

    def printOut(self, LEVEL):
        printd("[" + self.opcode + "," + str(self.mode) + "," + str(self.ctr_num) + "," + str(self.arg) + "]", LEVEL)


class YAction(object):
    def __init__(self, opcode, imm, label):
        self.opcode = opcode
        self.imm = imm
        self.label = label

    def printOut(self, LEVEL):
        printd("[" + self.opcode + "," + str(self.imm) + "]", LEVEL)


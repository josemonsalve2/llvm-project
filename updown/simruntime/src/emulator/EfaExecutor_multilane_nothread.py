import binascii
import bisect
from datetime import datetime
import math
import mmap
import os
import pdb
import struct
import sys
import threading
import time

from bitstring import BitArray
from numpy import *

import EfaUtil as efa_util
from EFA import *
from MachineCode import *
from StattestsEFA import *

# Import perf_logger
# from _m5.perf_log import writePerfLogUpdownV2

# ====== select  printing level ======
# efa_util.printLevel(stage_trace)
# ====== Constant Value ======
dram_lat = 100


# ====== helper function ======
def hash_snappy(value, shift):
    bytes = value
    kMul = 0x1E35A7BD
    return uint32(bytes * kMul) >> shift


def hash_crc(bytes):
    value = bin(bytes)[2:]
    value = value.zfill(32)
    data_in = BitArray(bin=value)

    lfsr_q = BitArray(bin="0001001000110100")
    lfsr_c = BitArray(bin="0000000000000000")
    lfsr_q.reverse()
    data_in.reverse()

    # fmt: off
    lfsr_c[0] = lfsr_q[0] ^ lfsr_q[1] ^ lfsr_q[2] ^ lfsr_q[3] ^ lfsr_q[4] ^ lfsr_q[5] ^ lfsr_q[6] ^ lfsr_q[7] ^ lfsr_q[8] ^ lfsr_q[9] ^ lfsr_q[10] ^ lfsr_q[11] ^ lfsr_q[14] ^ lfsr_q[15] ^ data_in[0] ^ data_in[1] ^ data_in[2] ^ data_in[3] ^ data_in[4] ^ data_in[5] ^ data_in[6] ^ data_in[7] ^ data_in[8] ^ data_in[9] ^ data_in[10] ^ data_in[11] ^ data_in[12] ^ data_in[13] ^ data_in[15] ^ data_in[16] ^ data_in[17] ^ data_in[18] ^ data_in[19] ^ data_in[20] ^ data_in[21] ^ data_in[22] ^ data_in[23] ^ data_in[24] ^ data_in[25] ^ data_in[26] ^ data_in[27] ^ data_in[30] ^ data_in[31]
    lfsr_c[1] = lfsr_q[0] ^ lfsr_q[1] ^ lfsr_q[2] ^ lfsr_q[3] ^ lfsr_q[4] ^ lfsr_q[5] ^ lfsr_q[6] ^ lfsr_q[7] ^ lfsr_q[8] ^ lfsr_q[9] ^ lfsr_q[10] ^ lfsr_q[11] ^ lfsr_q[12] ^ lfsr_q[15] ^ data_in[1] ^ data_in[2] ^ data_in[3] ^ data_in[4] ^ data_in[5] ^ data_in[6] ^ data_in[7] ^ data_in[8] ^ data_in[9] ^ data_in[10] ^ data_in[11] ^ data_in[12] ^ data_in[13] ^ data_in[14] ^ data_in[16] ^ data_in[17] ^ data_in[18] ^ data_in[19] ^ data_in[20] ^ data_in[21] ^ data_in[22] ^ data_in[23] ^ data_in[24] ^ data_in[25] ^ data_in[26] ^ data_in[27] ^ data_in[28] ^ data_in[31]
    lfsr_c[2] = lfsr_q[0] ^ lfsr_q[12] ^ lfsr_q[13] ^ lfsr_q[14] ^ lfsr_q[15] ^ data_in[0] ^ data_in[1] ^ data_in[14] ^ data_in[16] ^ data_in[28] ^ data_in[29] ^ data_in[30] ^ data_in[31]
    lfsr_c[3] = lfsr_q[1] ^ lfsr_q[13] ^ lfsr_q[14] ^ lfsr_q[15] ^ data_in[1] ^ data_in[2] ^ data_in[15] ^ data_in[17] ^ data_in[29] ^ data_in[30] ^ data_in[31]
    lfsr_c[4] = lfsr_q[0] ^ lfsr_q[2] ^ lfsr_q[14] ^ lfsr_q[15] ^ data_in[2] ^ data_in[3] ^ data_in[16] ^ data_in[18] ^ data_in[30] ^ data_in[31]
    lfsr_c[5] = lfsr_q[1] ^ lfsr_q[3] ^ lfsr_q[15] ^ data_in[3] ^ data_in[4] ^ data_in[17] ^ data_in[19] ^ data_in[31]
    lfsr_c[6] = lfsr_q[2] ^ lfsr_q[4] ^ data_in[4] ^ data_in[5] ^ data_in[18] ^ data_in[20]
    lfsr_c[7] = lfsr_q[3] ^ lfsr_q[5] ^ data_in[5] ^ data_in[6] ^ data_in[19] ^ data_in[21]
    lfsr_c[8] = lfsr_q[4] ^ lfsr_q[6] ^ data_in[6] ^ data_in[7] ^ data_in[20] ^ data_in[22]
    lfsr_c[9] = lfsr_q[5] ^ lfsr_q[7] ^ data_in[7] ^ data_in[8] ^ data_in[21] ^ data_in[23]
    lfsr_c[10] = lfsr_q[6] ^ lfsr_q[8] ^ data_in[8] ^ data_in[9] ^ data_in[22] ^ data_in[24]
    lfsr_c[11] = lfsr_q[7] ^ lfsr_q[9] ^ data_in[9] ^ data_in[10] ^ data_in[23] ^ data_in[25]
    lfsr_c[12] = lfsr_q[8] ^ lfsr_q[10] ^ data_in[10] ^ data_in[11] ^ data_in[24] ^ data_in[26]
    lfsr_c[13] = lfsr_q[9] ^ lfsr_q[11] ^ data_in[11] ^ data_in[12] ^ data_in[25] ^ data_in[27]
    lfsr_c[14] = lfsr_q[10] ^ lfsr_q[12] ^ data_in[12] ^ data_in[13] ^ data_in[26] ^ data_in[28]
    lfsr_c[15] = lfsr_q[0] ^ lfsr_q[1] ^ lfsr_q[2] ^ lfsr_q[3] ^ lfsr_q[4] ^ lfsr_q[5] ^ lfsr_q[6] ^ lfsr_q[7] ^ lfsr_q[8] ^ lfsr_q[9] ^ lfsr_q[10] ^ lfsr_q[13] ^ lfsr_q[14] ^ lfsr_q[15] ^ data_in[0] ^ data_in[1] ^ data_in[2] ^ data_in[3] ^ data_in[4] ^ data_in[5] ^ data_in[6] ^ data_in[7] ^ data_in[8] ^ data_in[9] ^ data_in[10] ^ data_in[11] ^ data_in[12] ^ data_in[14] ^ data_in[15] ^ data_in[16] ^ data_in[17] ^ data_in[18] ^ data_in[19] ^ data_in[20] ^ data_in[21] ^ data_in[22] ^ data_in[23] ^ data_in[24] ^ data_in[25] ^ data_in[26] ^ data_in[29] ^ data_in[30] ^ data_in[31]
    # fmt: on

    lfsr_c.reverse()
    res = (lfsr_c >> 4).int

    return res


# ====== Metric Class ======
class Metric:
    def __init__(self, lane_id):
        self.lane_id = lane_id
        self.tran_bins = dict()
        self.tran_cycle = dict()
        self.tran_label = dict()
        self.ins_per_event = dict()
        self.cycles_per_event = dict()
        self.ins_per_fetch = dict()
        self.ins_per_match = dict()
        self.op_buff_util = []
        self.perf_file = None
        self.cycle = 0
        self.curr_event_scyc = 0
        self.start_ticks = 0
        self.up_lm_read_bytes = 0
        self.up_lm_write_bytes = 0
        self.up_dram_read_bytes = 0
        self.up_dram_write_bytes = 0
        self.num_events = 0
        self.total_acts = 0
        self.total_trans = 0
        self.msg_ins = 0
        self.mov_ins = 0
        self.al_ins = 0
        self.branch_ins = 0
        self.op_ins = 0
        self.event_ins = 0
        self.yld_ins = 0
        self.comp_ins = 0
        self.goto_ins = 0
        self.probes = 0
        self.ops_removed = 0
        self.base_cycle = 0
        self.exec_cycles = 0
        self.idle_cycles = 0
        self.last_exec_cycle = 0
        self.cmpswp_ins = 0
        self.cmp_fail_count = 0
        self.cmp_succ_count = 0
        self.base_ins = 0
        self.ins_for_iter = 0
        self.vertex_per_lane = 0
        self.edge_per_lane = 0
        self.max_edge_per_lane = 0
        self.frontier_edit_ins = 0
        self.enqueue_num = 0
        self.num_collision = 0
        self.num_update = 0
        self.num_send_rd = 0
        self.num_hit = 0
        self.cycles_bins = [0] * 500
        self.cycles_bin_step = 200000
        self.event_q_len = 0
        self.event_q_max = 0
        self.event_q_mean = 0.0
        self.event_q_sample_cnt = 0
        self.operand_q_len = 0
        self.operand_q_max = 0
        self.operand_q_mean = 0.0
        self.operand_q_sample_cnt = 0
        self.perf_log_enable = False
        self.user_counters = [0] * 16

    
    def initMetrics(self):
        self.cycle = 0
        self.up_lm_read_bytes = 0
        self.up_lm_write_bytes = 0
        self.up_dram_read_bytes = 0
        self.up_dram_write_bytes = 0
        self.num_events = 0
        self.total_acts = 0
        self.total_trans = 0
        self.msg_ins = 0
        self.mov_ins = 0
        self.al_ins = 0
        self.branch_ins = 0
        self.op_ins = 0
        self.event_ins = 0
        self.yld_ins = 0
        self.comp_ins = 0
        self.goto_ins = 0
        self.probes = 0
        self.ops_removed = 0
        self.base_cycle = 0
        self.exec_cycles = 0
        self.idle_cycles = 0
        self.last_exec_cycle = 0
        self.cmpswp_ins = 0

    def Setup(self, perf_file, lane_id, sim):
        self.lane_id = lane_id
        if perf_file is None:
            self.perf_file = None
        elif not sim:
            self.perf_file = perf_file
            open(self.perf_file, "w").close()

    def TranGroupBin(self, tran):
        src = tran.src.state_id
        dst = tran.dst.state_id
        key = (src, dst)
        if key not in self.tran_bins:
            self.tran_bins[key] = 1
        else:
            self.tran_bins[key] += 1

    def TranSetBase(self):
        self.base_cycle = self.cycle

    def TranCycleDelta(self, tran):
        delta = self.cycle - self.base_cycle
        src = tran.src.state_id
        dst = tran.dst.state_id
        key = (src, dst)
        if key not in self.tran_cycle:
            self.tran_cycle[key] = delta
        else:
            self.tran_cycle[key] += delta

    def TranCycleLabelDelta(self, tran):
        delta = self.cycle - self.base_cycle
        src = tran.src.state_id
        dst = tran.dst.state_id
        label = tran.label
        key = (src, label, dst)
        if key not in self.tran_label:
            self.tran_label[key] = delta
        else:
            self.tran_label[key] += delta

    def printBins(self):
        for k, v in self.tran_bins.iteritems():
            print("(src_state, dst_state)="),
            print(k, v),
            print("\tcycles:" + str(self.tran_cycle[k]))

    def printLabels(self):
        for k, v in self.tran_label.iteritems():
            print("(src_state, label, dst_state)="),
            print(k),
            print("\tcycles:" + str(v))

    def printDecompressFraction(self):
        sumLiteral0To60 = 0
        sumLiteral61To62 = 0
        sumMatchTag01 = 0
        sumMatchTag10 = 0
        for k, v in self.tran_label.iteritems():
            if k[1] < 61:
                sumLiteral0To60 += v
            elif k[1] < 63:
                sumLiteral61To62 += v
            elif k[1] < 128:
                sumMatchTag01 += v
            else:
                sumMatchTag10 += v
        print("cycle (Literal 0-60):\t" + str(sumLiteral0To60))
        print("cycle (Literal 61-62):\t" + str(sumLiteral61To62))
        print("cycle (Match tag 01):\t" + str(sumMatchTag01))
        print("cycle (Match tag 10):\t" + str(sumMatchTag10))

    def printstats(self):
        # print("Writing File %s" % self.perf_file)
        with open(self.perf_file, "a+") as f:
            f.write("Lane:%d\n" % self.lane_id)
            f.write("Cycles(old):%d\n" % self.cycle)
            f.write("Exec_Cycles:%d\n" % self.exec_cycles)
            f.write("Idle_Cycles:%d\n" % self.idle_cycles)
            f.write("Last_Exec_cycle:%d\n" % self.last_exec_cycle)
            f.write("NumEvents:%d\n" % self.num_events)

            f.write("MessageActions:%d\n" % self.msg_ins)
            f.write("MoveActions:%d\n" % self.mov_ins)
            f.write("ALUActions:%d\n" % self.al_ins)
            f.write("BranchActions:%d\n" % self.branch_ins)
            f.write("OperandActions:%d\n" % self.op_ins)
            f.write("YieldActions:%d\n" % self.yld_ins)
            f.write("CmpswpActions:%d\n" % self.cmpswp_ins)

            f.write("NumofProbes:%d\n" % self.probes)
            f.write("NumOperandsRemoved:%d\n" % self.ops_removed)
            f.write("NumOfActions:%d\n" % self.total_acts)
            f.write("NumOfTransitions:%d\n" % self.total_trans)

            f.write("UpLMReadBytes:%d\n" % self.up_lm_read_bytes)
            f.write("UpLMWriteBytes:%d\n" % self.up_lm_write_bytes)
            f.write("UpDRAMReadBytes:%d\n" % self.up_dram_read_bytes)
            f.write("UpDRAMWriteBytes:%d\n" % self.up_dram_write_bytes)

            if sum(self.cmp_fail_count != 0):
                f.write("NumOfCmpswpFail:%d\n" % self.cmp_fail_count)
                f.write("NumOfCmpswpSucceed:%d\n" % self.cmp_succ_count)
            f.write("NumOfVertex:%d\n" % self.vertex_per_lane)
            f.write("NumOfEdge:%d\n" % self.edge_per_lane)
            f.write("MaxDegree:%d\n" % self.max_edge_per_lane)
            f.write("NumOfUpdate:%d\n" % self.num_update)
            f.write("NumOfHit:%d\n" % self.num_hit)
            f.write("NumOfCollision:%d\n" % self.num_collision)
            f.write("NumOfSendRd:%d\n" % (self.num_send_rd))
            f.write("NumOfSendEnqueue:%d\n" % self.enqueue_num)
            f.write("FrontierEditIns:%d\n" % self.frontier_edit_ins)
            f.write("CyclesForBaseOperations:%d\n" % (self.base_ins))
            f.write("CyclesForInnerLoop:%d\n" % (self.ins_for_iter + self.base_ins))
            f.write("Histograms\n")
            f.write("ActionsPerEvent:")
            for key in sorted(self.ins_per_event):
                f.write(str(key) + ":" + str(self.ins_per_event[key]) + ",")
            f.write("\nCyclesPerEvent:")
            for key in sorted(self.cycles_per_event):
                f.write(str(key) + ":" + str(self.cycles_per_event[key]) + ",")
            f.write("ActionsperFetchEvent:")
            for key in sorted(self.ins_per_fetch):
                f.write(str(key) + ":" + str(self.ins_per_fetch[key]) + ",")
            f.write("ActionsperMatchEvent:")
            for key in sorted(self.ins_per_match):
                f.write(str(key) + ":" + str(self.ins_per_match[key]) + ",")
            f.write("\nCyclebins:")
            for i in range(len(self.cycles_bins)):
                if (i * self.cycles_bin_step > self.last_exec_cycle):
                    continue
                f.write("%d~%d: %s\n" % (i * self.cycles_bin_step, (i + 1) * self.cycles_bin_step, self.cycles_bins[i]))
            f.write("\n")
            f.close()

    def write_perf_log(self, updown_id, lane_id, thread_id, event_base, event_label, payloads=set(), msg_id=None, msg_fmtstr="", msg_reglist=[]):
        if not self.perf_log_enable:
            return

        en_msg = False
        en_cycle = False
        en_action = False
        en_trans = False
        en_queue = False
        en_lm = False
        en_dram = False
        en_sys_dram = False
        for cur_pl in payloads:
            if int(cur_pl) == PerfLogPayload.UD_CYCLE_STATS.value:
                en_cycle = True
            elif int(cur_pl) == PerfLogPayload.UD_ACTION_STATS.value:
                en_action = True
            elif int(cur_pl) == PerfLogPayload.UD_TRANS_STATS.value:
                en_trans = True
            elif int(cur_pl) == PerfLogPayload.UD_QUEUE_STATS.value:
                en_queue = True
            elif int(cur_pl) == PerfLogPayload.UD_LOCAL_MEM_STATS.value:
                en_lm = True
            elif int(cur_pl) == PerfLogPayload.UD_MEM_INTF_STATS.value:
                en_dram = True
            elif int(cur_pl) == PerfLogPayload.SYS_MEM_INTF_STATS.value:
                en_sys_dram = True
        msg_str = ""
        if msg_id is not None:
            en_msg = True
            regval = []
            for reg in msg_reglist:
                regval.append(reg[1])
            msg_str = msg_fmtstr % (tuple(regval))

        writePerfLogUpdownV2(
           updown_id, lane_id, thread_id,  # IDs
           event_base, event_label,  # event
           # payloads
           en_msg, en_cycle, en_action, en_trans, en_queue, en_lm, en_dram, en_sys_dram,
           # message
           (msg_id if isinstance(msg_id, int) else 0xFFFFFFFF), msg_str, msg_reglist,
           # cycles
           self.cycle - self.curr_event_scyc, 
           # trans
           self.total_trans,
           # actions
           self.total_acts, self.msg_ins, self.mov_ins, self.branch_ins,
           self.al_ins, self.yld_ins, self.comp_ins, self.cmpswp_ins,
           # queues
           self.operand_q_len, self.event_q_len,
           # local memory
           self.up_lm_read_bytes, self.up_lm_write_bytes,
        )


# ====== Activation Class is the basic unit of each stage ======
class Activation:
    def __init__(self, state, property):
        self.state = state
        self.property = property


# ====== State's Property Class ======
class Property:
    def __init__(self, p_type, p_value):
        self.p_type = p_type
        self.p_val = p_value


class Paction:
    def __init__(self):
        self.src = None
        self.imm = None
        self.dst = None


class EventQueue:
    def __init__(self, buffSize, metric):
        self.size = buffSize
        self.events = []
        # for i in range(self.size):
        #    self.events.append(None)
        self.top = 0
        self.bottom = 0
        self.metric = metric

    def isEmpty(self):
        return len(self.events) == 0
        # return self.top == self.bottom

    def isFull(self):
        return ((self.top - self.bottom) == 1) or ((self.bottom == self.size - 1) and (self.top == 0))

    def pushEvent(self, event):
        # self.events[self.bottom]=event
        # self.bottom=(self.bottom+1) % self.size
        self.events.append(event)
        self.metric.event_q_len = len(self.events)
        # Update max
        if self.metric.event_q_len > self.metric.event_q_max:
            self.metric.event_q_max = self.metric.event_q_len
        # Update mean
        # use estimation to avoid exceeding max float
        self.metric.event_q_mean = self.metric.event_q_mean + (self.metric.event_q_len - self.metric.event_q_mean) / (self.metric.event_q_sample_cnt + 1)
        # self.metric.event_q_mean = (self.metric.event_q_mean * self.metric.event_q_sample_cnt + self.metric.event_q_len) / (self.metric.event_q_sample_cnt + 1)
        self.metric.event_q_sample_cnt += 1

    def popEvent(self):
        # event = self.events[self.top]
        # self.top = (self.top+1) % self.size
        if len(self.events) == 0:
            printd("EventQ: removing more elements than available?", error)
        event_out = self.events.pop(0)
        self.metric.event_q_len = len(self.events)
        # Update mean
        # use estimation to avoid exceeding max float
        self.metric.event_q_mean = self.metric.event_q_mean + (self.metric.event_q_len - self.metric.event_q_mean) / (self.metric.event_q_sample_cnt + 1)
        # self.metric.event_q_mean = (self.metric.event_q_mean * self.metric.event_q_sample_cnt + self.metric.event_q_len) / (self.metric.event_q_sample_cnt + 1)
        self.metric.event_q_sample_cnt += 1
        return event_out

    def getOccup(self):
        return len(self.events)
        # return (self.bottom - self.top)%self.size


class OpBuffer:
    def __init__(self, buffSize, metric):
        # self.size = buffSize
        self.operands = []
        self.operands_inuse = []
        self.base = 0
        self.last = 0
        self.metric = metric

    def getOp(self, index):
        # printd("RD_OBBUFER:base:%d, index:%d" % (self.base, index), progress_trace)
        # return self.operands[self.base+index]
        return self.operands[index]

    def setOp(self, value):
        self.operands.append(value)
        self.metric.operand_q_len = len(self.operands)
        # Update max
        if self.metric.operand_q_len > self.metric.operand_q_max:
            self.metric.operand_q_max = self.metric.operand_q_len
        # Update mean
        # use estimation to avoid exceeding max float
        self.metric.operand_q_mean = self.metric.operand_q_mean + (self.metric.operand_q_len - self.metric.operand_q_mean) / (self.metric.operand_q_sample_cnt + 1)
        # self.metric.operand_q_mean = (self.metric.operand_q_mean * self.metric.operand_q_sample_cnt + self.metric.operand_q_len) / (self.metric.operand_q_sample_cnt + 1)
        self.metric.operand_q_sample_cnt += 1
        printd("OperandSize:%d, Value:%d" % (len(self.operands), value), stage_trace)

    def clearOp(self, size):
        # self.operands_inuse[self.base+index]=0
        printd("OperandSize:%d, ClearSize:%d" % (len(self.operands), size), stage_trace)
        if size <= len(self.operands):
            self.operands = self.operands[size :]
            self.metric.operand_q_len = len(self.operands)
        else:
            self.operands.clear()
            self.metric.operand_q_len = len(self.operands)
            printd("OperandQ: removing more elements than available?", error)
        # Update mean
        # use estimation to avoid exceeding max float
        self.metric.operand_q_mean = self.metric.operand_q_mean + (self.metric.operand_q_len - self.metric.operand_q_mean) / (self.metric.operand_q_sample_cnt + 1)
        # self.metric.operand_q_mean = (self.metric.operand_q_mean * self.metric.operand_q_sample_cnt + self.metric.operand_q_len) / (self.metric.operand_q_sample_cnt + 1)
        self.metric.operand_q_sample_cnt += 1

    @deprecate
    def isAvail(self, size):  # This has potential for different policies
        is_avail = 0
        index = 0
        while self.operands_inuse[index] == 1:
            index = index + 1
        orig_size = size
        start_index = index
        while size > 0 and index < self.size:
            if self.operands_inuse[index] == 0:
                size = size - 1
            else:
                start_index = index + 1
                size = orig_size
            index = index + 1
        if index < self.size and size == 0:
            is_avail = 1
        return is_avail, start_index


class Thread:
    def __init__(self, tid, udpbase):
        self.tid = tid
        self.curr_event = 0
        self.udprbase = udpbase
        self.opbase = 0
        self.ret_tid = None
        self.ret_lane_id = None
        self.ret_event = None
        self.current_states = []
        self.ear = [0 for i in range(4)]
        self.SBP = 0
        self.CR_Advance = 8
        # self.CR_Issue = 32
        self.CR_Issue = 8  # changed by Marziyeh
        self.thread_state = (int(self.tid) & 0x000000FF) << 16
        printd("Thread :%d, UDPBase:%d" % (self.tid, self.udprbase), stage_trace)
        # for now used only in the simulator
        self.top_thread = 0
        # self.opbase = opbase

    def set_ret(self, ret_tid, ret_lane_id, ret_event):
        printd("Setting Return:Lane:%d, TID:%d, event:%d" % (ret_lane_id, ret_tid, ret_event), stage_trace)
        self.ret_tid = ret_tid
        self.ret_lane_id = ret_lane_id
        self.ret_event = ret_event
        # self.event_word = ((int(self.lane_num) << 24) & 0xff000000) | ((int(self.thread_id) << 16) & 0x00ff0000) | ((int(self.event_base) << 8) & 0x0000ff00) | (int(self.event_label) & 0x000000ff)
        self.thread_state = (
            ((int(self.ret_lane_id) << 24) & 0xFF000000)
            | ((int(self.tid) << 16) & 0x00FF0000)
            | ((int(self.ret_tid) << 8) & 0x0000FF00)
            | (int(self.ret_event) & 0x000000FF)
        )

    def set_state(self, current_states, SBP, CR_Advance, CR_Issue):
        self.current_states = current_states
        self.SBP = SBP
        self.CR_Advance = CR_Advance
        self.CR_Issue = CR_Issue


class ThreadStateTable:
    def __init__(self, lane_id):
        self.lane_id = lane_id
        self.threads = {x: None for x in range(255)}
        self.freetids = [x for x in range(255)]
        self.usedtids = []

    def getTID(self):
        tid = self.freetids.pop(0)
        self.usedtids.append(tid)
        return tid

    def addThreadtoTST(self, thread):
        self.threads[thread.tid] = thread
        self.usedtids.append(thread.tid)
        if thread.tid in self.freetids:
            self.freetids.remove(thread.tid)

    def remThreadfromTST(self, tid):
        self.threads[tid] = None
        self.usedtids.remove(tid)
        self.freetids.append(tid)

    def threadexists(self, tid):
        if tid in self.usedtids:
            return 1
        else:
            return 0

    def getThread(self, tid):
        return self.threads[tid]


class LM_scratchpad:
    def __init__(self, size):
        # self.DataStore = [0x0] * 1024 * 16384
        print("DataStore Size:%d" % size)
        self.size = size
        self.DataStore = [0x0] * size

    def initDataStore(self, value):
        for i in range(len(self.DataStore)):
            self.DataStore[i] = value

    def read_word(self, byte_addr):
        wd_data = self.DataStore[byte_addr >> 2]
        if byte_addr + 4 <= self.size:
            wd_next_data = self.DataStore[(byte_addr >> 2) + 1]
        else:
            wd_next_data = 0
        #  self.metric.up_lm_read_bytes += 4
        if byte_addr % 4 == 0:
            # if byte_addr == 4:
            #    print("Read_scratch%d:%d" % (byte_addr, wd_data))
            #  self.metric.cycle += 1
            return wd_data
        if byte_addr % 4 == 1:
            #  self.metric.cycle += 2
            return (wd_data & 0x00FFFFFF) << 8 | (wd_next_data & 0xFF000000) >> 24
        if byte_addr % 4 == 2:
            #  self.metric.cycle += 2
            return (wd_data & 0x0000FFFF) << 16 | (wd_next_data & 0xFFFF0000) >> 16
        else:
            #  self.metric.cycle += 2
            return (wd_data & 0x000000FF) << 24 | (wd_next_data & 0xFFFFFF00) >> 8

    def write_word(self, byte_addr, wd_data):
        printd("LMWrite:Byte_addr:%d, Data:%d" % (byte_addr, wd_data), stage_trace)
        old_wd_data = self.DataStore[byte_addr >> 2]
        next_wd_data = self.DataStore[(byte_addr >> 2) + 1]
        #  self.metric.up_lm_write_bytes += 4
        if byte_addr % 4 == 0:
            # if byte_addr == 4:
            #    print("Write_scratch%d:%d" % (byte_addr, wd_data))
            self.DataStore[byte_addr >> 2] = wd_data
        elif byte_addr % 4 == 1:
            #  self.metric.cycle += 1
            self.DataStore[byte_addr >> 2] = old_wd_data & 0xFF000000 | (wd_data & 0xFFFFFF00) >> 8
            self.DataStore[(byte_addr >> 2) + 1] = next_wd_data & 0x00FFFFFF | (wd_data & 0x000000FF) << 24
        elif byte_addr % 4 == 2:
            #  self.metric.cycle += 1
            self.DataStore[byte_addr >> 2] = old_wd_data & 0xFFFF0000 | (wd_data & 0xFFFF0000) >> 16
            self.DataStore[(byte_addr >> 2) + 1] = next_wd_data & 0x0000FFFF | (wd_data & 0x0000FFFF) << 16
        else:
            #  self.metric.cycle += 1
            self.DataStore[byte_addr >> 2] = old_wd_data & 0xFFFFFF00 | (wd_data & 0xFF000000) >> 24
            self.DataStore[(byte_addr >> 2) + 1] = next_wd_data & 0x000000FF | (wd_data & 0x00FFFFFF) << 8
        # print("byte_addr:%d, wd_data%d" %(byte_addr, wd_data))
        # print("byte_addr:%d, DataStore[addr]:%d, DataStore[addr+1]:%d" %(byte_addr, self.DataStore[byte_addr>>2], self.DataStore[(byte_addr>>2)+1]))

    def read_2bytes(self, byte_addr):
        word = self.DataStore[byte_addr >> 2]
        next_word = self.DataStore[(byte_addr >> 2) + 1]
        self.metric.up_lm_read_bytes += 2
        if byte_addr % 4 == 0:
            self.metric.cycle += 1
            return uint16((word & 0xFFFF0000) >> 16)
        elif byte_addr % 4 == 2:
            self.metric.cycle += 1
            return uint16(word & 0x0000FFFF)
        elif byte_addr % 4 == 1:
            self.metric.cycle += 1
            return uint16((word & 0x00FFFF00) >> 8)
        else:
            self.metric.cycle += 2
            return uint16((word & 0xFF) << 8 | (next_word & 0xFF000000) >> 24)

    def write_2bytes(self, byte_addr, byte_data):
        wd_old_data = self.DataStore[byte_addr >> 2]
        wd_next_data = self.DataStore[(byte_addr >> 2) + 1]
        self.metric.up_lm_write_bytes += 2

        if byte_addr % 4 == 0:
            self.metric.cycle += 1
            wd_new_data = (byte_data & 0x0000FFFF) << 16 | (wd_old_data & 0xFFFF)
        elif byte_addr % 4 == 2:
            self.metric.cycle += 1
            wd_new_data = byte_data & 0xFFFF | (wd_old_data & 0xFFFF0000)
        elif byte_addr % 4 == 1:
            self.metric.cycle += 1
            wd_new_data = (byte_data & 0xFFFF) << 8 | (wd_old_data & 0xFF0000FF)
        else:
            self.metric.cycle += 2
            wd_new_data = (byte_data & 0xFFFF) >> 8 | (wd_old_data & 0xFFFFFF00)
            wd_next_data = (byte_data & 0xFF) << 24 | (wd_next_data & 0x00FFFFFF)
            self.DataStore[(byte_addr >> 2) + 1] = uint32(wd_next_data)

        self.DataStore[byte_addr >> 2] = uint32(wd_new_data)

    def read_byte(self, byte_addr):
        word = self.DataStore[byte_addr >> 2]
        self.metric.cycle += 1
        self.metric.up_lm_read_bytes += 1
        if byte_addr % 4 == 0:
            return uint8((word & 0xFF000000) >> 24)
        elif byte_addr % 4 == 1:
            return uint8((word & 0x00FF0000) >> 16)
        elif byte_addr % 4 == 2:
            return uint8((word & 0x0000FF00) >> 8)
        else:
            return uint8(word & 0x000000FF)

    def write_byte(self, byte_addr, byte_data):
        wd_old_data = self.DataStore[byte_addr >> 2]
        self.metric.cycle += 1
        self.metric.up_lm_write_bytes += 1
        if byte_addr % 4 == 0:
            wd_new_data = (byte_data & 0x000000FF) << 24 | wd_old_data & 0x00FFFFFF
        elif byte_addr % 4 == 1:
            wd_new_data = (byte_data & 0x000000FF) << 16 | wd_old_data & 0xFF00FFFF
        elif byte_addr % 4 == 2:
            wd_new_data = (byte_data & 0x000000FF) << 8 | wd_old_data & 0xFFFF00FF
        else:
            wd_new_data = (byte_data & 0x000000FF) | wd_old_data & 0xFFFFFF00
        self.DataStore[byte_addr >> 2] = uint32(wd_new_data)

    def printDataStore(self, start_addr, end_addr, LEVEL):
        for addr in range(start_addr, end_addr, 4):
            data = self.read_word(addr)
            # printd( "<<{0}:{1}>>\n".format(format(addr-addr%4, '#06x'),format(data,'#010x')), LEVEL)


# ====== UDP Processor with multiple lanes =========
class VirtualEngine:
    # def __init__(self, num_lanes, dram_mem, top, perf_file):
    def __init__(self, num_lanes, perf_file, sim, lmbanksize, tick_freq, perf_log_enable=0, perf_log_internal_enable=0):
        # pdb.set_trace()
        self.dram_mem = None
        self.top = None
        self.sim = sim
        self.outstanding_events = 0
        self.perf_file = perf_file

        self.tick_freq = tick_freq

        self.perf_log_internal_enable = False
        if perf_log_internal_enable > 0:
            self.perf_log_internal_enable = True

        # self.LM = LM_scratchpad(65536*num_lanes)
        self.LM = LM_scratchpad(lmbanksize * num_lanes)
        self.num_lanes = num_lanes
        # self.lanes = [VirtualEngineLane(i, 1000, 5000, 32, self.dram_mem, self.top, self.LM, self.perf_file, self) for i in range(num_lanes)]
        self.lanes = [VirtualEngineLane(i, 1000, self.LM, self.perf_file, perf_log_enable, self) for i in range(num_lanes)]
        self.active_lanes = []
        self.lane_num_sends = {x: 0 for x in range(num_lanes)}

    def __del__(self):
        for ln in self.lanes:
            ln.send_mm.close()

    def setup_top_mem(self, top, dram_mem):
        self.top = top
        self.dram_mem = dram_mem

    def incr_events(self):
        self.outstanding_events += 1

    def decr_events(self):
        self.outstanding_events -= 1

    def setup(self):
        for i in range(self.num_lanes):
            self.lanes[i].setAllLanes(self.lanes)
            self.lanes[i].top = self.top
            self.lanes[i].dram = self.dram_mem
            self.lanes[i].metric.initMetrics()

    def executeEFA(self, efa, property_vec, SBPB_BEGIN=0, initID=[0]):
        # print("self.outstanding_events == %d" % self.outstanding_events)
        efa.fixlabels()
        for i, l in enumerate(self.lanes):
            l.all_lanes_done = 0
            l.lane_state = "lane_init"
        while self.outstanding_events > 0:
            for up_lane in reversed(self.lanes):
                up_lane.executeEFA(efa, property_vec, 0, efa.init_state_id)

            # print("All Lane Status: self.outstanding_events == %d" % self.outstanding_events)
            # pass
        # pdb.set_trace()
        # print("self.outstanding_events == %d" % self.outstanding_events)
        for i, l in enumerate(self.lanes):
            l.all_lanes_done = 1

    def printstats(self):
        for l in self.lanes:
            l.printstats()

    # API for Simulator

    def read_scratch(self, addr, size):
        # pdb.set_trace()
        if size == 1:
            return self.LM.read_byte(addr)
        elif size == 2:
            return self.LM.read_2bytes(addr)
        elif size == 4:
            printd("read_scratch:%d:%d" % (addr, self.LM.read_word(addr)), stage_trace)
            return self.LM.read_word(addr)

    def read_sbuffer(self, addr, size, lane_id):
        # pdb.set_trace()
        printd("Lane:%d Get Out stream buffer%d: size%d" % (lane_id, addr, size), stage_trace)
        return self.lanes[lane_id].get_outstream_bytes(addr, size)

    def write_sbuffer(self, addr, data, lane_id):
        printd("Lane:%d write stream buffer%d:%d" % (lane_id, addr, data), stage_trace)
        self.lanes[lane_id].set_instream_bytes(addr, data)

    def write_scratch(self, addr, data):
        printd("write_scratch:%d:%d" % (addr, data), stage_trace)
        self.LM.write_word(addr, data)

    def insert_event(self, lane_id, event):
        self.lanes[lane_id].EvQ.pushEvent(event)

    def insert_operand(self, lane_id, opval):
        self.lanes[lane_id].OpBuffer.setOp(opval)

    # def setup_sim(self, efa, property_vec, SBPB_BEGIN=0, initID=[0], lane_id=-1):
    def setup_sim(self, efa, simdir, lm_addr_mode=0, SBPB_BEGIN=0, initID=[0], lane_id=-1):
        # print("self.outstanding_events == %d" % self.outstanding_events)
        efa.fixlabels()
        if lane_id == -1:
            # set up all lanes with the same efa, property_vec etc
            for i, l in enumerate(self.lanes):
                l.all_lanes_done = 0
                l.lane_state = "lane_init"
                # l.setup_sim(efa, property_vec, SBPB_BEGIN, initID)
                l.setup_sim(efa, simdir, lm_addr_mode, SBPB_BEGIN, initID)
                l.setAllLanes(self.lanes)
            # def setup_sim(self, efa, property_vec, SBPB_BEGIN=0, initID=[0]):
        else:
            # When will this be used?
            self.lanes[lane_id].all_lanes_done = 0
            self.lanes[lane_id].lane_state = "lane_init"
            self.lanes[lane_id].setAllLanes(self.lanes)
            self.lanes[lane_id].setup_sim(efa, property_vec, simdir, lm_addr_mode, SBPB_BEGIN, initID)

    def executeEFA_simAPI(self, lane_id, start_timestamp):
        # pdb.set_trace()
        total_num_sends = 0
        # num_sends, self.return_state, self.metric.cycle, self.metric.total_acts,\
        # metric.idle_cycles, self.metric.up_lm_read_bytes, self.metric.up_lm_write_bytes,\
        # metric.msg_ins, self.metric.mov_ins, self.metric.branch_ins, self.metric.al_ins,\
        # metric.yld_ins, self.metric.comp_ins, self.metric.cmpswp_ins, self.metric.total_trans
        # num_sends, return_state, exec_cycles, actcnt = self.lanes[lane_id].executeEFAlane_sim()
        return_tuples = self.lanes[lane_id].executeEFAlane_sim(start_timestamp)
        # return num_sends, return_state, exec_cycles, actcnt
        return return_tuples

    def getEventQ_size(self, lane_id):
        # pdb.set_trace()
        return self.lanes[lane_id].EvQ.getOccup()


# ======  UDP Lane Logical Architecture Class ======
class VirtualEngineLane:
    # def __init__(self, lane_id, numOfGpr, numOfOpBuffer, numOfEvQ, dram_mem, top, LM, perf_file, up):
    def __init__(self, lane_id, numOfGpr, LM, perf_file, perf_log_enable, up):
        self.clearStore(numOfGpr)
        self.metric = Metric(lane_id)
        self.metric.perf_log_enable = perf_log_enable
        self.laneudprsize = numOfGpr
        self.maxudpbase = 0
        self.udpthreadallocs = []
        self.OpBuffer = OpBuffer(100, self.metric)
        self.EvQ = EventQueue(100, self.metric)
        self.curr_event = None
        self.curr_thread = None
        self.upproc = up
        self.curr_event_sins = None
        self.fetch_event_sins = None
        self.match_event_sins = None
        self.dram = None
        self.all_lanes = []
        self.top = None
        self.program = None
        self.SBPB_BEGIN = 0
        self.initID = [0]
        self.init_prop = None
        self.lane_id = lane_id
        self.tstable = ThreadStateTable(self.lane_id)
        self.LM = LM
        # self.ds_base = self.lane_id * 4096
        self.ds_base = 0
        self.mode = "G"
        self.all_lanes_done = 0
        self.lane_state = "lane_init"
        self.current_states = []
        self.perf_file = perf_file
        self.sim = 0
        self.mm_offset = 0
        self.send_mm = None
        self.num_sends = 0
        self.actcount = 0
        self.return_state = 0
        self.pname = None
        # self.last_exec_cycle = 0

    def getCycle(self):
        return self.metric.last_exec_cycle

    def setAllLanes(self, lanes):
        self.all_lanes = lanes
        if not self.sim:
            self.metric.Setup(self.perf_file, self.lane_id, self.sim)

    def clearStore(self, numOfGpr):
        self.UDPR = [0 for i in range(numOfGpr)]
        # self.in_stream = BitArray('')
        self.in_stream = BitArray(
            65536 * 8, endian="little"
        )  # Marzi # size is allocated to the number of bits per each lane since sb is local to each lane
        self.out_stream = self.in_stream  # BitArray('')
        self.ear = [0 for i in range(4)]
        # self.SBP = 0
        # self.CR_Issue = 8 # Changed by Marziyeh
        # self.CR_Advance = 8
        # ====== 1MB scrathpad data store, big endian low_addr-->|MSB, LSB|-->high_addr======
        # self.DataStore = [0x0] * 1024 * 256

    def setEFA(self, efa):
        self.program = efa

    def pushEvent(self, event):
        self.upproc.active_lanes.append(self.lane_id)
        self.EvQ.pushEvent(event)

    def getMode(self):
        return self.mode

    def setMode(self, mode):
        self.mode = mode

    def test(self):
        print("Lane:%d" % self.lane_id)

    def address_generate_unit(self, base, index_val):  # , size):
        base_val = self.rd_ear(base)
        # self.metric.cycle += 1
        printd("AddrGen: base:%s, base_val:%d , index_val:%d" % (base, base_val, index_val), stage_trace)
        return int(base_val) + int(index_val)

    def SBPB(self):
        # return self.SBP >> 3
        # print("self.curr_thread.SBP:%d" % self.curr_thread.SBP) #Marzi
        return self.curr_thread.SBP >> 3  # Marzi

    def getInputStream(self, filename):
        f = open(filename, "rb")
        stream = f.read()
        f.close()
        # ====== uncompressed data input block must <= 64KB
        #        if len(stream) > 64*1024:
        #            print "input block size must < 64KB"
        #            exit()

        hex_str = "0x" + binascii.hexlify(stream)
        s = BitArray(hex_str)
        self.in_stream.append(s)

    def getAsciiInputStreamNoCheck(self, stream):
        hex_str = "0x" + binascii.hexlify(stream)
        s = BitArray(hex_str)
        self.in_stream.append(s)

    def initOutputStream(self, sizeInByte):
        hex_str = "0x" + "00" * sizeInByte
        s = BitArray(hex_str)
        self.out_stream.append(s)

    # def printInStream(self, LEVEL):
    # printd ("Input Stream:",LEVEL)
    # printd (self.in_stream, LEVEL)
    # printd ('\n', LEVEL)

    # def printOutStream(self, LEVEL):
    # printd ("Output Stream:",LEVEL)
    # printd (self.out_stream, LEVEL)
    # printd ('\n', LEVEL)

    def getInStreamBytes(self):
        return len(self.in_stream) / 8

    def getInStreamBits(self):
        return len(self.in_stream)

    def getOutStreamBytes(self):
        return len(self.out_stream) / 8

    def getOutStreamBits(self):
        return len(self.out_stream)

    def bitsToInt(self, x):
        sum = 0
        i = 0
        for b in x[::-1]:
            sum += int(b) << i
            i += 1
        return sum

    def printUDPR(self, LEVEL):
        index = 0
        for reg in self.UDPR:
            # printd ("UDPR_"+str(index)+"="+str(format(reg,'#010x'))+" ", LEVEL)
            index += 1
        # printd( '\n' , LEVEL)

    def check_and_compact(self, udpsize):
        if self.maxudpbase + udpsize < self.laneudprsize:
            return
        else:
            printd("Performing UDPR compaction! too many threads?", stage_trace)
            upbase = 0
            newlist = []
            # printd(self.udpthreadallocs, stage_trace)
            for ubase, length, tid in self.udpthreadallocs:
                if ubase > upbase:
                    # move registers
                    # printd("Moving %d regs from UDPR_%s to UDPR_%s" % (length, str(ubase), str(upbase)), stage_trace)
                    for i in range(length):
                        self.UDPR[upbase + i] = self.UDPR[ubase + i]  # self.rd_register("UDPR_"+str(ubase+i)))
                    newlist.append((upbase, length, tid))
                    self.tstable.threads[tid].udprbase = upbase
                    # Update udpthreadallocs and thread state to upbase
                    upbase += length
                else:
                    newlist.append((upbase, length, tid))
                    upbase = upbase + length
            assert len(self.udpthreadallocs) == len(newlist)
            self.maxudpbase = upbase
            self.udpthreadallocs = newlist
            printd("MaxUDPBase now set to %d" % self.maxudpbase, stage_trace)
            if self.maxudpbase + udpsize > self.laneudprsize:
                print("Max UDPR size/Threads reached for now")
                exit(1)

            # printd(self.udpthreadallocs, stage_trace)
            return

    # def printEvQ(self, LEVEL):
    #    #index = 0
    #    #printd("Lane:%d Print EvQ Size: %d" % (self.lane_id, len(self.EvQ.events)), progress_trace)
    #    for event in self.EvQ.events:
    #        event.printOut(progress_trace)
    #    #printd( '\n' , LEVEL)

    def printOB(self, LEVEL):
        index = 0
        for reg in self.OpBuffer:
            # printd ("OB_"+str(index)+"="+str(format(reg,'#010x'))+" ", LEVEL)
            index += 1
        # printd( '\n' , LEVEL)

    def printstats(self):
        self.metric.printstats()
        # self.metric = Metric(self.perf_file, self.lane_id)

    def get_instream_bytes(self, byte_addr, size):
        return self.in_stream[byte_addr << 3 : (byte_addr << 3) + size * 8]

    def get_outstream_bytes(self, byte_addr, size):
        data_bytes = self.out_stream[byte_addr << 3 : (byte_addr << 3) + size * 8].bin
        return self.bitsToInt(data_bytes)

    def set_instream_bytes(self, byte_addr, data):
        self.in_stream[byte_addr << 3 : (byte_addr << 3) + 32] = data

    # def set_instream_bytes(self, byte_addr, size, data):

    # def setup_sim(self, efa, property_vec, SBPB_BEGIN=0, initID=[0]):
    def setup_sim(self, efa, simdir, lm_addr_mode, SBPB_BEGIN=0, initID=[0]):
        # pdb.set_trace()
        self.program = efa
        self.SBPB_BEGIN = SBPB_BEGIN
        self.initID = initID
        self.init_prop = [Property("event", None)]
        assert len(self.init_prop) == len(initID), "# of property must equal # of init states"
        self.pc = 0
        self.sim = 1
        self.pname = "./" + simdir + "/lane" + str(self.lane_id) + "_send.txt"
        with open(self.pname, "w+b") as fd:
            for _ in range(262144):
                val = struct.pack("i", 0)
                fd.write(val)
        fd.close()
        with open(self.pname, "r+b") as fd:
            self.send_mm = mmap.mmap(fd.fileno(), 1048576, access=mmap.ACCESS_WRITE, offset=0)
            self.send_mm.seek(0)
            self.mm_offset = self.send_mm.tell() + 4
        if lm_addr_mode == 1:
            self.ds_base = self.lane_id * 65536
        else:
            self.ds_base = 0
        self.program.calcUdpSize()
        printd("Program UdpSize:%d" % self.program.getUdpSizeonly(), stage_trace)

        # self.metric = Metric(perf_file, lane_id)

    # This is only used in the simulator [To manage the slightly different execution model]
    def executeEFAlane_sim(self, start_timestamp):
        # state = -1 = yield_terminate
        # state > 0 for num_sends
        # state = 0 if yielded and no sends
        # ====== efa program loaded to UpDown
        self.metric.Setup(self.perf_file, self.lane_id, self.sim)
        self.metric.initMetrics()
        self.metric.start_ticks = start_timestamp
        printd("Lane_Num:%d Lane State:%s, EvQ:%d" % (self.lane_id, self.lane_state, self.EvQ.getOccup()), stage_trace)

        if self.upproc.perf_log_internal_enable:
            self.metric.write_perf_log(0, self.lane_id, 0,
                                       # 0, self.lane_id, self.curr_thread.tid,
                                       0, 0,
                                       # self.curr_event.event_base, self.curr_event.event_label,
                                       set([PerfLogPayload.UD_QUEUE_STATS.value]))

        self.metric.curr_event_scyc = self.metric.cycle
        # if init:
        #    SBPB_BEGIN=self.SBPB_BEGIN
        #    property_vec = self.init_prop
        #    initID=self.initID
        #    init_state = []
        self.num_sends = 0
        self.mm_offset = 4
        self.actcount = self.metric.total_acts
        # self.program = efa
        if self.EvQ.getOccup() == 0:
            # Lane has nothing to do
            # highly unlikely!
            self.return_state = 0
            # return self.num_sends, self.return_state, (self.metric.cycle - self.metric.curr_event_scyc), (self.metric.total_acts - self.actcount)
            return (
                self.num_sends,
                self.return_state,
                self.metric.cycle - self.metric.curr_event_scyc,
                self.metric.total_acts,
                self.metric.idle_cycles,
                self.metric.up_lm_read_bytes,
                self.metric.up_lm_write_bytes,
                self.metric.msg_ins,
                self.metric.mov_ins,
                self.metric.branch_ins,
                self.metric.al_ins,
                self.metric.yld_ins,
                self.metric.comp_ins,
                self.metric.cmpswp_ins,
                self.metric.total_trans,
                self.metric.event_q_max,
                self.metric.event_q_mean,
                self.metric.operand_q_max,
                self.metric.operand_q_mean,
                self.metric.user_counters[0],
                self.metric.user_counters[1],
                self.metric.user_counters[2],
                self.metric.user_counters[3],
                self.metric.user_counters[4],
                self.metric.user_counters[5],
                self.metric.user_counters[6],
                self.metric.user_counters[7],
                self.metric.user_counters[8],
                self.metric.user_counters[9],
                self.metric.user_counters[10],
                self.metric.user_counters[11],
                self.metric.user_counters[12],
                self.metric.user_counters[13],
                self.metric.user_counters[14],
                self.metric.user_counters[15],
            )
        else:
            # Setup the execution state from the thread and start execution
            # Q: what is the init state when a thread is issued!?
            top_event = self.EvQ.events[0]
            top_event_tid = top_event.thread_id  # & 0x00ff0000 >> 16
            top_event.printOut(stage_trace)
            if top_event_tid == 0xFF or not self.tstable.threadexists(top_event_tid):
                # Create a new thread and set the states
                newtid = self.tstable.getTID()
                # pdb.set_trace()
                printd("Lane:%d: Thread:%d" % (self.lane_id, newtid), stage_trace)
                # Update event thread ID
                # event.setthreadid(newtid)
                # Do we need to compact Register file for slots?
                self.check_and_compact(self.program.getUdpSizeonly())
                # Create Thread
                currthread = Thread(newtid, self.maxudpbase)
                # Insert Thread into table
                self.tstable.addThreadtoTST(currthread)
                self.curr_thread = currthread
                # self.curr_thread.set_state([], 0, 8, 32)
                self.curr_thread.set_state([], 0, 8, 8)  # Marzi
                init_state = []
                assert len(self.init_prop) == len(self.initID), "# of property must equal # of init states"
                for ID in self.initID:
                    init_state.append(self.program.get_state(ID))
                self.curr_thread.current_states = []
                for init_idx in range(len(self.initID)):
                    self.curr_thread.current_states.append(Activation(init_state[init_idx], self.init_prop[init_idx]))
                # Update UDP base
                self.udpthreadallocs.append((self.maxudpbase, self.program.getUdpSizeonly(), newtid))
                self.maxudpbase += self.program.getUdpSizeonly()
                self.lane_state = "lane_init"
                self.curr_thread.SBP = -self.curr_thread.CR_Advance + (self.SBPB_BEGIN << 3)
                init_sbp_val = self.curr_thread.CR_Advance
                yield_term = 0
                yield_exec = 0
                self.ear = [0 for i in range(4)]
            else:
                # Not a new thread
                self.lane_state = "lane_init"
                currthread = self.tstable.getThread(top_event.thread_id)
                self.curr_thread = currthread
                self.ear = self.curr_thread.ear
        # print("Executing EFA: len(current_states):%d" % len(current_states))
        if (self.lane_state == "lane_term" or self.lane_state == "lane_yield") and self.EvQ.getOccup() > 0:
            # We execute till we empty out the event queue
            assert len(self.curr_thread.current_states) > 0
            yield_term = 0
            yield_exec = 0
        while (
            (self.curr_thread.SBP + self.curr_thread.CR_Advance + self.curr_thread.CR_Issue) <= self.getInStreamBits()
            or self.curr_thread.current_states[0].property.p_type == "flag"
            or (self.curr_thread.current_states[0].property.p_type == "event" and self.EvQ.getOccup() > 0)
            or self.curr_thread.current_states[0].property.p_type == "flag_majority"
            or self.lane_state == "lane_init"
        ):
            # check whether if it is a flag state.
            # If it is, do not advance SBP and input stream
            if (
                self.curr_thread.current_states[0].property.p_type != "flag"
                and self.curr_thread.current_states[0].property.p_type != "flag_majority"
                and self.curr_thread.current_states[0].property.p_type != "event"
            ):
                self.curr_thread.SBP += self.curr_thread.CR_Advance
                issue_data = self.in_stream[self.curr_thread.SBP : self.curr_thread.SBP + self.curr_thread.CR_Issue].bin
                issue_data = self.bitsToInt(issue_data)
                issue_data_test = self.in_stream[self.curr_thread.SBP : self.curr_thread.SBP + 32].bin
                issue_data_test = self.bitsToInt(issue_data_test)
                # prints by Marzi
                # print( "\n[INFO] char-based Transition")
                # print( "\nprocessing:   SBP="+str(self.curr_thread.SBP)+\
                #   "["+str(self.curr_thread.SBP)+":"+str(self.curr_thread.SBP+self.curr_thread.CR_Issue)+")"+\
                #    " SBPB="+str(self.SBPB())+" CR.ISSUE="+str(self.curr_thread.CR_Issue)+\
                #    " ("+str(hex(issue_data))+") => ("+str(hex(issue_data_test))+")"+'\n')
            else:
                issue_data = 0
                # prints by Marzi
            #                printd( bcolors.OKGREEN+"\n[INFO] Executing Flag Transition"+bcolors.ENDC, progress_trace)
            #                printd( bcolors.OKGREEN+"\nprocessing:   SBP="+str(self.SBP)+\
            #                    "["+str(self.SBP)+":"+str(self.SBP+self.CR_Issue)+")"+\
            #                    " SBPB="+str(self.SBPB())+bcolors.ENDC+" CR.ISSUE="+str(self.CR_Issue)+\
            #                    " ("+str(hex(issue_data))+")"+'\n', progress_trace)
            # print( "\n[INFO] Executing Flag/Event Transition")
            # print( "\nprocessing:   SBP="+str(self.curr_thread.SBP)+\
            #    "["+str(self.curr_thread.SBP)+":"+str(self.curr_thread.SBP+self.curr_thread.CR_Issue)+")"+\
            #    " SBPB="+str(self.SBPB())+" CR.ISSUE="+str(self.curr_thread.CR_Issue)+\
            #    " ("+str(hex(issue_data))+")"+'\n')

            # ====== major processing loop ======
            next_states = []
            for activation in self.curr_thread.current_states:
                next_activations, yield_term, yield_exec = self.executeActivation(activation, issue_data)
                next_states = concatSet(next_states, next_activations)
            printd("%d:finish stage:yield_term:%d, yield_exec:%d\n" % (self.lane_id, yield_term, yield_exec), stage_trace)
            self.printUDPR(full_trace)
            self.curr_thread.current_states = next_states
            for idx in range(len(self.UDPR)):
                self.UDPR[idx] = self.UDPR[idx] & 0xFFFFFFFF
            if yield_term == 1:
                self.lane_state = "lane_term"
                if self.EvQ.getOccup() == 0:
                    self.return_state = -1
                    # return self.num_sends, self.return_state, (self.metric.cycle - self.metric.curr_event_scyc), (self.metric.total_acts - self.actcount)
                    return (
                        self.num_sends,
                        self.return_state,
                        self.metric.cycle - self.metric.curr_event_scyc,
                        self.metric.total_acts,
                        self.metric.idle_cycles,
                        self.metric.up_lm_read_bytes,
                        self.metric.up_lm_write_bytes,
                        self.metric.msg_ins,
                        self.metric.mov_ins,
                        self.metric.branch_ins,
                        self.metric.al_ins,
                        self.metric.yld_ins,
                        self.metric.comp_ins,
                        self.metric.cmpswp_ins,
                        self.metric.total_trans,
                        self.metric.event_q_max,
                        self.metric.event_q_mean,
                        self.metric.operand_q_max,
                        self.metric.operand_q_mean,
                        self.metric.user_counters[0],
                        self.metric.user_counters[1],
                        self.metric.user_counters[2],
                        self.metric.user_counters[3],
                        self.metric.user_counters[4],
                        self.metric.user_counters[5],
                        self.metric.user_counters[6],
                        self.metric.user_counters[7],
                        self.metric.user_counters[8],
                        self.metric.user_counters[9],
                        self.metric.user_counters[10],
                        self.metric.user_counters[11],
                        self.metric.user_counters[12],
                        self.metric.user_counters[13],
                        self.metric.user_counters[14],
                        self.metric.user_counters[15],
                    )
            if yield_exec == 1:
                self.lane_state = "lane_yield"
                if self.EvQ.getOccup() == 0:
                    self.return_state = 0 if self.num_sends == 0 else self.num_sends
                    # return self.num_sends, self.return_state, (self.metric.cycle - self.metric.curr_event_scyc), (self.metric.total_acts - self.actcount)
                    return (
                        self.num_sends,
                        self.return_state,
                        self.metric.cycle - self.metric.curr_event_scyc,
                        self.metric.total_acts,
                        self.metric.idle_cycles,
                        self.metric.up_lm_read_bytes,
                        self.metric.up_lm_write_bytes,
                        self.metric.msg_ins,
                        self.metric.mov_ins,
                        self.metric.branch_ins,
                        self.metric.al_ins,
                        self.metric.yld_ins,
                        self.metric.comp_ins,
                        self.metric.cmpswp_ins,
                        self.metric.total_trans,
                        self.metric.event_q_max,
                        self.metric.event_q_mean,
                        self.metric.operand_q_max,
                        self.metric.operand_q_mean,
                        self.metric.user_counters[0],
                        self.metric.user_counters[1],
                        self.metric.user_counters[2],
                        self.metric.user_counters[3],
                        self.metric.user_counters[4],
                        self.metric.user_counters[5],
                        self.metric.user_counters[6],
                        self.metric.user_counters[7],
                        self.metric.user_counters[8],
                        self.metric.user_counters[9],
                        self.metric.user_counters[10],
                        self.metric.user_counters[11],
                        self.metric.user_counters[12],
                        self.metric.user_counters[13],
                        self.metric.user_counters[14],
                        self.metric.user_counters[15],
                    )
            else:
                self.lane_state = "lane_init"

            if (self.lane_state == "lane_term" or self.lane_state == "lane_yield") and self.EvQ.getOccup() > 0:
                top_event = self.EvQ.events[0]
                top_event_tid = top_event.thread_id  # & 0x00ff0000 >> 16
                top_event.printOut(stage_trace)
                if top_event_tid == 0xFF or not self.tstable.threadexists(top_event_tid):
                    # Create a new thread and set the states
                    newtid = self.tstable.getTID()
                    printd("Lane:%d: Thread:%d" % (self.lane_id, newtid), stage_trace)
                    # Update event thread ID
                    # Do we need to compact Register file for slots?
                    self.check_and_compact(self.program.getUdpSizeonly())
                    # Create Thread
                    currthread = Thread(newtid, self.maxudpbase)
                    # Insert Thread into table
                    self.tstable.addThreadtoTST(currthread)
                    self.curr_thread = currthread
                    # self.curr_thread.set_state([], 0, 8, 32)
                    self.curr_thread.set_state([], 0, 8, 8)  # Marzi
                    init_state = []
                    # assert len(property_vec) == len(initID), "# of property must equal # of init states"
                    for ID in self.initID:
                        init_state.append(self.program.get_state(ID))
                    self.curr_thread.current_states = []
                    for init_idx in range(len(self.initID)):
                        self.curr_thread.current_states.append(Activation(init_state[init_idx], self.init_prop[init_idx]))
                    # Update UDP base
                    self.udpthreadallocs.append((self.maxudpbase, self.program.getUdpSizeonly(), newtid))
                    self.maxudpbase += self.program.getUdpSizeonly()
                    self.lane_state = "lane_init"
                    next_states = []
                    self.curr_thread.SBP = -self.curr_thread.CR_Advance + (self.SBPB_BEGIN << 3)
                    init_sbp_val = self.curr_thread.CR_Advance
                    yield_term = 0
                    yield_exec = 0
                    self.ear = [0 for i in range(4)]
                else:
                    self.lane_state = "lane_init"
                    next_states = []
                    currthread = self.tstable.getThread(top_event.thread_id)
                    self.curr_thread = currthread
                    self.ear = self.curr_thread.ear

            # ====== detect non-active error, if find, abort
            if (not yield_term) and len(self.curr_thread.current_states) == 0:
                print("Lane: %d ERROR!, all no active states, not allowed for now" % self.lane_id)
                exit()
        # return yield_term --> This return is not needed anymore!

    def executeEFA(self, efa, property_vec, SBPB_BEGIN=0, initID=[0]):
        # ====== efa program loaded to UDP
        # pdb.set_trace()
        printd("Lane_Num:%d Lane State:%s, EvQ:%d" % (self.lane_id, self.lane_state, self.EvQ.getOccup()), stage_trace)
        self.pc = 0
        self.program = efa
        if self.EvQ.getOccup() == 0:
            # Lane has nothing to do
            return
        else:
            # Setup the execution state from the thread and start execution
            # Q: what is the init state when a thread is issued!?
            top_event = self.EvQ.events[0]
            top_event_tid = top_event.thread_id  # & 0x00ff0000 >> 16
            top_event.printOut(stage_trace)
            if top_event_tid == 0xFF or not self.tstable.threadexists(top_event_tid):
                # Create a new thread and set the states
                newtid = self.tstable.getTID()
                printd("Lane:%d: Thread:%d" % (self.lane_id, newtid), stage_trace)
                # Update event thread ID
                # event.setthreadid(newtid)
                # Do we need to compact Register file for slots?
                self.check_and_compact(self.program.getUdpSizeonly())
                # Create Thread
                currthread = Thread(newtid, self.maxudpbase)
                # Insert Thread into table
                self.tstable.addThreadtoTST(currthread)
                self.curr_thread = currthread
                # self.curr_thread.set_state([], 0, 8, 32)
                self.curr_thread.set_state([], 0, 8, 8)  # Marzi
                init_state = []
                assert len(property_vec) == len(initID), "# of property must equal # of init states"
                for ID in initID:
                    init_state.append(efa.get_state(ID))
                self.curr_thread.current_states = []
                for init_idx in range(len(initID)):
                    self.curr_thread.current_states.append(Activation(init_state[init_idx], property_vec[init_idx]))
                # Update UDP base
                self.udpthreadallocs.append((self.maxudpbase, self.program.getUdpSizeonly(), newtid))
                self.maxudpbase += self.program.getUdpSizeonly()
                self.lane_state = "lane_init"
                next_states = []
                self.curr_thread.SBP = -self.curr_thread.CR_Advance + (SBPB_BEGIN << 3)
                init_sbp_val = self.curr_thread.CR_Advance
                yield_term = 0
                yield_exec = 0
                self.ear = [0 for i in range(4)]
            else:
                self.lane_state = "lane_init"
                next_states = []
                currthread = self.tstable.getThread(top_event.thread_id)
                self.curr_thread = currthread
                self.ear = self.curr_thread.ear
                # Continue execution like before?

        # # print("Executing EFA: len(current_states):%d" % len(current_states))
        if (self.lane_state == "lane_term" or self.lane_state == "lane_yield") and self.EvQ.getOccup() > 0:
            # New event has been added start execution
            assert len(self.curr_thread.current_states) > 0
            yield_term = 0
            yield_exec = 0
        while (
            (self.curr_thread.SBP + self.curr_thread.CR_Advance + self.curr_thread.CR_Issue) <= self.getInStreamBits()
            or self.curr_thread.current_states[0].property.p_type == "flag"
            or (self.curr_thread.current_states[0].property.p_type == "event" and (self.EvQ.getOccup() > 0) and (not self.all_lanes_done))
            or self.curr_thread.current_states[0].property.p_type == "flag_majority"
            or self.lane_state == "lane_init"
        ):
            # (self.current_states[0].property.p_type == "event" and yield_term==0 and (not self.all_lanes_done))or\
            # check whether if it is a flag state.
            # If it is, do not advance SBP and input stream
            if (
                self.curr_thread.current_states[0].property.p_type != "flag"
                and self.curr_thread.current_states[0].property.p_type != "flag_majority"
            ):
                self.curr_thread.SBP += self.curr_thread.CR_Advance
                issue_data = self.in_stream[self.curr_thread.SBP : self.curr_thread.SBP + self.curr_thread.CR_Issue].bin
                issue_data = self.bitsToInt(issue_data)
            else:
                issue_data = 0
                # printd( bcolors.OKGREEN+"\n[INFO] Executing Flag Transition"+bcolors.ENDC, progress_trace)
            # printd( bcolors.OKGREEN+"\nprocessing:   SBP="+str(self.SBP)+\
            #    "["+str(self.SBP)+":"+str(self.SBP+self.CR_Issue)+")"+\
            #    " SBPB="+str(self.SBPB())+bcolors.ENDC+" CR.ISSUE="+str(self.CR_Issue)+\
            #    " ("+str(hex(issue_data))+")"+'\n', progress_trace)
            # ====== major processing loop ======
            next_states = []
            # print("Lane:%d Numevents:%d" % (self.lane_id, self.EvQ.getOccup()))
            for activation in self.curr_thread.current_states:
                next_activations, yield_term, yield_exec = self.executeActivation(activation, issue_data)
                next_states = concatSet(next_states, next_activations)
            printd("%d:finish stage:yield_term:%d, yield_exec:%d\n" % (self.lane_id, yield_term, yield_exec), stage_trace)
            self.printUDPR(full_trace)
            self.curr_thread.current_states = next_states
            # print("LaneID: %d yield_term: %d current_states: %d" %(self.lane_id, yield_term, len(current_states)))
            # print("After yield/yield_terminate:%s, EventQ Size:%d all_lanes:%d" % (self.lane_state, self.EvQ.getOccup(), self.all_lanes_done))
            # next_states = []
            for idx in range(len(self.UDPR)):
                self.UDPR[idx] = self.UDPR[idx] & 0xFFFFFFFF
            if yield_term == 1:
                self.lane_state = "lane_term"
                break
            if yield_exec == 1:
                self.lane_state = "lane_yield"
                break
            else:
                self.lane_state = "lane_init"

            if (
                (self.lane_state == "lane_term" or self.lane_state == "lane_yield")
                and self.EvQ.getOccup() > 0
                and (not self.all_lanes_done)
            ):
                top_event = self.EvQ.events[0]
                top_event_tid = top_event.thread_id  # & 0x00ff0000 >> 16
                top_event.printOut(stage_trace)
                if top_event_tid == 0xFF or not self.tstable.threadexists(top_event_tid):
                    # Create a new thread and set the states
                    newtid = self.tstable.getTID()
                    printd("Lane:%d: Thread:%d" % (self.lane_id, newtid), stage_trace)
                    # Update event thread ID
                    # Do we need to compact Register file for slots?
                    self.check_and_compact(self.program.getUdpSizeonly())
                    # Create Thread
                    currthread = Thread(newtid, self.maxudpbase)
                    # Insert Thread into table
                    self.tstable.addThreadtoTST(currthread)
                    self.curr_thread = currthread
                    # self.curr_thread.set_state([], 0, 8, 32)
                    self.curr_thread.set_state([], 0, 8, 8)  # Marzi
                    init_state = []
                    assert len(property_vec) == len(initID), "# of property must equal # of init states"
                    for ID in initID:
                        init_state.append(efa.get_state(ID))
                    self.curr_thread.current_states = []
                    for init_idx in range(len(initID)):
                        self.curr_thread.current_states.append(Activation(init_state[init_idx], property_vec[init_idx]))
                    # Update UDP base
                    self.udpthreadallocs.append((self.maxudpbase, self.program.getUdpSizeonly(), newtid))
                    self.maxudpbase += self.program.getUdpSizeonly()
                    self.lane_state = "lane_init"
                    next_states = []
                    self.curr_thread.SBP = -self.curr_thread.CR_Advance + (SBPB_BEGIN << 3)
                    init_sbp_val = self.curr_thread.CR_Advance
                    yield_term = 0
                    yield_exec = 0
                else:
                    self.lane_state = "lane_init"
                    next_states = []
                    currthread = self.tstable.getThread(top_event.thread_id)
                    self.curr_thread = currthread

            # ====== detect non-active error, if find, abort
            if (not yield_term) and len(self.curr_thread.current_states) == 0:
                print("Lane: %d error, all no active states, not allowed for now" % self.lane_id)
                # print ("SBPB "+str(self.SBPB()))
                exit()
        return yield_term

    def executeActivation(self, activation, input_label):
        property = activation.property
        state = activation.state
        # printd("LaneID: %d EventQ before executeActivation:%d" % (self.lane_id, self.EvQ.getOccup()), progress_trace)
        # ====== select the transitions ======
        if property.p_type == "common":
            # translabel = self.rd_register("UDPR_0")
            trans = [state.trans[0]]
        elif property.p_type == "flag" or property.p_type == "flag_majority":
            # trans = state.get_tran(self.UDPR[0])
            translabel = self.rd_register("UDPR_0")
            trans = state.get_tran(translabel)
        elif property.p_type == "event":
            if self.EvQ.isEmpty():
                print("Lane:%d We should never get here!" % self.lane_id)

            if not self.all_lanes_done:
                event = self.EvQ.popEvent()
                if event.thread_id == 0xFF:
                    # Update event thread ID
                    event.setthreadid(self.curr_thread.tid)
                continuation = self.rd_obbuffer("OB_0")
                self.OpBuffer.clearOp(1)
                if (continuation & 0xFFFFFFFF) != 0xFFFFFFFF:
                    ret_event = continuation & 0x000000FF
                    ret_tid = (continuation & 0x00FF0000) >> 16
                    ret_lane_id = (continuation & 0xFF000000) >> 24
                    self.curr_thread.set_ret(ret_tid, ret_lane_id, ret_event)

                #self.metric.curr_event_scyc = self.metric.cycle
                self.curr_event_sins = self.metric.total_acts
                # Only for Triangle Count
                if event.event_label == 0:
                    self.fetch_event_sins = self.metric.total_acts
                else:
                    self.match_event_sins = self.metric.total_acts

                self.metric.num_events += 1
                event.printOut(progress_trace)
                trans = state.get_tran(event.event_label)
                self.curr_event = event
                # Andronicus : Check this later
                if event.cycle >= self.metric.last_exec_cycle:
                    self.metric.idle_cycles += event.cycle - self.metric.last_exec_cycle
                    self.metric.cycles_bins[(event.cycle // self.metric.cycles_bin_step)] += event.cycle - self.metric.last_exec_cycle
                    self.metric.last_exec_cycle = event.cycle
        else:
            trans = state.get_tran(input_label)
        # printd("LaneID: %d EventQ after Activation EventPop:%d TransLen:%d" % (self.lane_id, self.EvQ.getOccup(), len(trans)), progress_trace)

        # ====== signature fail, look for majority transition
        # if not found, which means signature fail in machine level
        # print("Executing Activation: len(trans):%d" % len(trans))
        if not self.all_lanes_done:
            if len(trans) == 0:
                if property.p_type == "majority" or property.p_type == "flag_majority":
                    # printd("***Regular transition no found, try to find majority transition\n",full_trace)
                    trans = state.get_tran_byAnnotation("majority")
                    # in machine code, majority_majirityCarry is implemented by majority transition of majority transition
                    if len(trans) == 0:
                        trans = state.get_tran_byAnnotation("majority_majorityCarry")
                    if len(trans) == 0:
                        trans = state.get_tran_byAnnotation("majority_defaultCarry")
                if property.p_type == "default" or property.p_type == "flag_default":
                    # printd("***Regular transition no found, try to find default transition\n",full_trace)
                    # ====== in machine level , this default transition is implemented as basic
                    # the destination state doesn't have default state
                    trans = state.get_tran_byAnnotation("default")
                    if len(trans) == 0:
                        # ====== in machine level, this default transition is implemented as defaultCarry, here is for emulator
                        trans = state.get_tran_byAnnotation("default_defaultCarry")
                    if len(trans) == 0:
                        trans = state.get_tran_byAnnotation("default_majorityCarry")
                    def_activation, forked_activations = self.executeTransition(trans[0])
                    return self.executeActivation(def_activation, input_label)

                # ====== No transition, deactivate this state
                else:
                    pass
            # ====== we execute the selected transition. May get several activations back
            yield_term = 0
            yield_exec = 0
            dst_activations = []
            for tr in trans:
                self.metric.TranSetBase()
                next_activation, forked_activations, yield_term, yield_exec = self.executeTransition(tr)
                self.metric.TranCycleDelta(tr)
                self.metric.TranCycleLabelDelta(tr)
                dst_activations.append(next_activation)
                if forked_activations is not None:
                    dst_activations = concatSet(dst_activations, forked_activations)
        else:
            yield_term = 1
            yield_exec = 1
            dst_activations = []

        return dst_activations, yield_term, yield_exec

    def executeTransition(self, transition):
        dst_state = transition.dst
        forked_activations = None
        # ====== each transition executed in 1 cycle
        self.metric.cycle += 1
        self.metric.exec_cycles += 1
        self.metric.last_exec_cycle += 1
        self.metric.total_trans += 1
        self.metric.TranGroupBin(transition)
        transition.printOut(stage_trace)
        # ====== transition carrying property ======
        if transition.anno_type == "defaultCarry" or transition.anno_type == "default_defaultCarry":
            dst_property = Property("default", "DEF_tran_addr")
        elif transition.anno_type == "majorityCarry":
            dst_property = Property("majority", "MJ_tran_addr")
        elif transition.anno_type == "majority_majorityCarry" or transition.anno_type == "default_majorityCarry":
            dst_property = Property("majority", "MJ_tran_addr")
        elif transition.anno_type == "commonCarry" or transition.anno_type == "commonCarry_with_action":
            dst_property = Property("common", None)
        elif transition.anno_type == "flagCarry" or transition.anno_type == "flagCarry_with_action":
            dst_property = Property("flag", None)
        elif transition.anno_type == "eventCarry":
            dst_property = Property("event", None)
        else:
            dst_property = Property("NULL", None)

        # ====== execute actions one by one ======
        yield_exec = 0
        seqnum = 0
        yield_term = 0
        if transition.hasActions():
            # for action in transition.actions:
            numActions = transition.getSize()
            while yield_exec == 0 and seqnum < numActions:
                # ====== action can modify the destination state's
                # property, and fork multiple activations ======
                action = transition.getAction(seqnum)
                printd(
                    "Lane: %d exec-Trans-action:%s, yield_exec:%d, seqnum:%d, numActions:%d"
                    % (self.lane_id, action.opcode, yield_exec, seqnum, numActions),
                    stage_trace,
                )
                action_dst_property, forked_activations, yield_exec, next_seqnum, yield_term = self.actionHandler(action, seqnum)

                # ====== if action changes the property, we need to
                # apply it to destination state ======
                seqnum = next_seqnum
                if action_dst_property is not None:
                    dst_property = action_dst_property
        if yield_exec == 1 or yield_term == 1:
            self.upproc.decr_events()
        if yield_exec == 1:
            self.lane_state = "lane_yield"
            printd("Lane:%d Oustanding Events:%d Yield_exe:%d" % (self.lane_id, self.upproc.outstanding_events, yield_exec), stage_trace)
        if yield_term == 1:
            self.lane_state = "lane_term"
            printd("Lane:%d Oustanding Events:%d Yield_term:%d" % (self.lane_id, self.upproc.outstanding_events, yield_term), stage_trace)
        return Activation(dst_state, dst_property), forked_activations, yield_term, yield_exec

    def actionHandler(self, action, seqnum):
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum_set = 0
        next_seqnum = seqnum
        action.printOut(stage_trace)
        self.metric.total_acts += 1
        # ====== action executed at least 1 cycle, more cycles in detail action
        self.metric.cycle += 1
        start_exec_cycles = self.metric.exec_cycles
        self.metric.exec_cycles += 1
        # ======  Action Dispather ======
        if action.opcode == "set_state_property":
            dst_property = self.do_set_state_property(action)
        elif action.opcode == "hash_sb32":
            self.do_hash_sb32(action)
        elif action.opcode == "mov_lm2reg":
            self.metric.mov_ins += 1
            self.metric.probes += 1
            self.do_mov_lm2reg(action)
        elif action.opcode == "mov_reg2lm":
            self.metric.mov_ins += 1
            self.do_mov_reg2lm(action)
        elif action.opcode == "mov_ear2lm":
            self.metric.mov_ins += 1
            self.do_mov_ear2lm(action)
        elif action.opcode == "mov_lm2ear":
            self.metric.mov_ins += 1
            self.do_mov_lm2ear(action)
        elif action.opcode == "mov_reg2reg":
            self.metric.mov_ins += 1
            self.do_mov_reg2reg(action)
        elif action.opcode == "mov_eqt2reg":
            # self.metric.op_ins += 1
            self.metric.mov_ins += 1
            self.metric.event_ins += 1
            self.do_mov_eqt2reg(action)
        elif action.opcode == "mov_ob2reg":
            self.metric.op_ins += 1
            self.metric.mov_ins += 1
            self.do_mov_ob2reg(action)
        elif action.opcode == "mov_ob2ear":
            self.metric.op_ins += 1
            self.metric.mov_ins += 1
            self.do_mov_ob2ear(action)
        elif action.opcode == "ev_update_1":
            self.do_ev_update_1(action)
        elif action.opcode == "ev_update_2":
            self.do_ev_update_2(action)
        elif action.opcode == "ev_update_reg_imm":
            self.do_ev_update_reg_imm(action)
        elif action.opcode == "ev_update_reg_2":
            self.do_ev_update_reg_2(action)
        elif action.opcode == "compare_string":
            self.do_compare_string(action)
        elif action.opcode == "compare_string_from_out":
            self.do_compare_string_from_out(action)
        elif action.opcode == "subi":
            self.metric.al_ins += 1
            self.do_sub_immediate(action)
        elif action.opcode == "addi":
            self.metric.al_ins += 1
            self.do_add_immediate(action)
        elif action.opcode == "copy":
            self.do_copy(action)
        elif action.opcode == "copy_ob_lm":
            self.do_copy_ob_lm(action)
        elif action.opcode == "copy_imm":
            self.do_copy_imm(action)
        elif action.opcode == "copy_from_out":
            self.do_copy_from_out(action)
        elif action.opcode == "copy_from_out_imm":
            self.do_copy_from_out_imm(action)
        elif action.opcode == "sub":
            self.metric.al_ins += 1
            self.do_sub_reg(action)
        elif action.opcode == "add":
            self.metric.al_ins += 1
            self.do_add_reg(action)
        elif action.opcode == "bitclr":
            self.metric.al_ins += 1
            self.do_bitclr_reg(action)
        elif action.opcode == "bitset":
            self.metric.al_ins += 1
            self.do_bitset_reg(action)
        elif action.opcode == "put_1byte_imm":
            self.do_put1byte_imm(action)
        elif action.opcode == "put_2byte_imm":
            self.do_put2byte_imm(action)
        elif action.opcode == "lshift_add_imm":
            self.metric.al_ins += 1
            self.do_lshift_add_imm(action)
        elif action.opcode == "rshift_add_imm":
            self.metric.al_ins += 1
            self.do_rshift_add_imm(action)
        elif action.opcode == "lshift_and_imm":
            self.metric.al_ins += 1
            self.do_lshift_and_imm(action)
        elif action.opcode == "rshift_and_imm":
            self.metric.al_ins += 1
            self.do_rshift_and_imm(action)
        elif action.opcode == "lshift_or_imm":
            self.metric.al_ins += 1
            self.do_lshift_or_imm(action)
        elif action.opcode == "rshift_or_imm":
            self.metric.al_ins += 1
            self.do_rshift_or_imm(action)
        elif action.opcode == "lshift_sub_imm":
            self.metric.al_ins += 1
            self.do_lshift_sub_imm(action)
        elif action.opcode == "cmpswp_i":
            self.metric.cmpswp_ins += 1
            self.do_cmpswp_i(action)
        elif action.opcode == "cmpswp":
            self.metric.cmpswp_ins += 1
            self.do_cmpswp(action)
        elif action.opcode == "cmpswp_ri":
            self.metric.cmpswp_ins += 1
            self.do_cmpswp_ri(action)
        elif action.opcode == "rshift_sub_imm":
            self.metric.al_ins += 1
            self.do_rshift_sub_imm(action)
        elif action.opcode == "put_bytes":
            self.do_putbytes(action)
        elif action.opcode == "comp_lt":
            self.metric.comp_ins += 1
            self.do_compare_less_than(action)
        elif action.opcode == "comp_gt":
            self.metric.comp_ins += 1
            self.do_compare_great_than(action)
        elif action.opcode == "comp_eq":
            self.metric.comp_ins += 1
            self.do_compare_equal(action)
        elif action.opcode == "compreg_eq":
            self.metric.comp_ins += 1
            self.do_compare_reg_equal(action)
        elif action.opcode == "compreg":
            self.metric.probes += 1
            self.metric.comp_ins += 1
            self.do_compare_reg(action)
        elif action.opcode == "compreg_lt":
            self.metric.comp_ins += 1
            self.do_compare_reg_less_than(action)
        elif action.opcode == "compreg_gt":
            self.metric.comp_ins += 1
            self.do_compare_reg_great_than(action)
        elif action.opcode == "bitwise_or":
            self.metric.al_ins += 1
            self.do_bitwise_or(action)
        elif action.opcode == "bitwise_and":
            self.metric.al_ins += 1
            self.do_bitwise_and(action)
        elif action.opcode == "bitwise_xor":
            self.metric.al_ins += 1
            self.do_bitwise_xor(action)
        elif action.opcode == "lshift_or":
            self.metric.al_ins += 1
            self.do_lshift_or(action)
        elif action.opcode == "rshift_or":
            self.metric.al_ins += 1
            self.do_rshift_or(action)
        elif action.opcode == "lshift":
            self.metric.al_ins += 1
            self.do_lshift(action)
        elif action.opcode == "rshift":
            self.metric.al_ins += 1
            self.do_rshift(action)
        elif action.opcode == "arithrshift":  # added by Marziyeh (arithrshifts)
            self.metric.al_ins += 1
            self.do_arithrshift(action)
        elif action.opcode == "lshift_t":
            self.metric.al_ins += 1
            self.do_lshift_t(action)
        elif action.opcode == "rshift_t":
            self.metric.al_ins += 1
            self.do_rshift_t(action)
        elif action.opcode == "arithrshift_t":  # added by Marziyeh (arithrshifts)
            self.metric.al_ins += 1
            self.do_arithrshift_t(action)
        elif action.opcode == "get_bytes":
            self.do_getbytes(action)
        elif action.opcode == "get_bytes_from_out":
            self.do_getbytes_from_out(action)
        elif action.opcode == "bitwise_and_imm":
            self.metric.al_ins += 1
            self.do_bitwise_and_imm(action)
        elif action.opcode == "bitwise_or_imm":
            self.metric.al_ins += 1
            self.do_bitwise_or_imm(action)
        elif action.opcode == "bitwise_xor_imm":
            self.metric.al_ins += 1
            self.do_bitwise_xor_imm(action)
        elif action.opcode == "swap_bytes":
            self.do_swap_bytes(action)
        elif action.opcode == "mask_or":
            self.metric.al_ins += 1
            self.do_mask_or(action)
        elif action.opcode == "goto" or action.opcode == "tranCarry_goto":
            self.metric.goto_ins += 1
            dst_property, forked_activations, yield_exec, yield_term = self.do_goto(action)
        elif action.opcode == "accept":
            self.do_accept(action)
        elif action.opcode == "set_issue_width":
            self.do_set_issue_width(action)
        elif action.opcode == "set_complete":
            self.do_set_complete(action)
        elif action.opcode == "refill":
            self.do_refill(action)
        elif action.opcode == "mov_imm2reg":
            self.metric.mov_ins += 1
            self.do_mov_imm2reg(action)
        elif action.opcode == "mov_sb2reg":  # added by Marzi
            self.metric.mov_ins += 1
            self.do_mov_sb2reg(action)
        elif action.opcode == "bne":
            self.metric.branch_ins += 1
            next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term = self.do_bne(action)
        elif action.opcode == "beq":
            self.metric.branch_ins += 1
            next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term = self.do_beq(action)
        elif action.opcode == "bgt":
            self.metric.branch_ins += 1
            next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term = self.do_bgt(action)
        elif action.opcode == "bge":
            self.metric.branch_ins += 1
            next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term = self.do_bge(action)
        elif action.opcode == "blt":
            self.metric.branch_ins += 1
            next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term = self.do_blt(action)
        elif action.opcode == "ble":
            self.metric.branch_ins += 1
            next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term = self.do_ble(action)
        elif action.opcode == "jmp":
            self.metric.branch_ins += 1
            next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term = self.do_jmp(action)
        elif action.opcode == "send_old":
            # self.metric.cycle += 3
            self.metric.msg_ins += 1
            if self.sim:
                self.do_send_old_sim(action)
            else:
                self.do_send_old(action)
        # New Send instruction interface
        elif action.opcode == "send4":
            self.metric.msg_ins += 1
            self.do_send4(action)
        elif action.opcode == "send":
            self.metric.msg_ins += 1
            self.do_send(action)
        elif action.opcode == "send4_wret":
            self.metric.msg_ins += 1
            self.do_send4_wret(action)
        elif action.opcode == "send_wret":
            self.metric.msg_ins += 1
            self.do_send_wret(action)
        elif action.opcode == "send4_wcont":
            self.metric.msg_ins += 1
            self.do_send4_wcont(action)
        elif action.opcode == "send_wcont":
            self.metric.msg_ins += 1
            self.do_send_wcont(action)
        elif action.opcode == "send4_dmlm":
            self.metric.msg_ins += 1
            self.do_send4_dmlm(action)
        elif action.opcode == "send_dmlm":
            self.metric.msg_ins += 1
            self.do_send_dmlm(action)
        elif action.opcode == "send_dmlm_ld":
            self.metric.msg_ins += 1
            self.do_send_dmlm_ld(action)
        elif action.opcode == "send_dmlm_ld_wret":
            self.metric.msg_ins += 1
            self.do_send_dmlm_ld_wret(action)
        elif action.opcode == "send4_dmlm_wret":
            self.metric.msg_ins += 1
            self.do_send4_dmlm_wret(action)
        elif action.opcode == "send_dmlm_wret":
            self.metric.msg_ins += 1
            self.do_send_dmlm_wret(action)
        elif action.opcode == "send4_reply":
            # self.metric.cycle += 3
            self.metric.msg_ins += 1
            self.do_send4_reply(action)
        elif action.opcode == "send_reply":
            # self.metric.cycle += 3
            self.metric.msg_ins += 1
            self.do_send_reply(action)
        # Pseudo for anylength of registers
        elif action.opcode == "send_any_wcont":
            self.metric.msg_ins += 1
            self.do_send_any_wcont(action)
        elif action.opcode == "send_any_wret":
            self.metric.msg_ins += 1
            self.do_send_any_wret(action)
        elif action.opcode == "send_any":
            self.metric.msg_ins += 1
            self.do_send_any(action)
        elif action.opcode == "send_top":
            # self.metric.cycle += 1
            self.do_send_top(action)
        elif action.opcode == "yield":
            # self.metric.cycle += 1
            self.metric.yld_ins += 1
            yield_exec = self.do_yield(action)
        elif action.opcode == "yield_operand":
            # self.metric.cycle += 1
            self.metric.yld_ins += 1
            self.do_yield_operand(action)
        elif action.opcode == "yield_terminate":
            # self.metric.cycle += 1
            self.metric.yld_ins += 1
            yield_exec, yield_term = self.do_yield_terminate(action)
        elif action.opcode == "print":
            self.metric.total_acts -= 1
            self.metric.cycle -= 1
            self.metric.exec_cycles -= 1
            self.do_print(action)
        elif action.opcode == "perflog":
            self.metric.total_acts -= 1
            self.metric.cycle -= 1
            self.metric.exec_cycles -= 1
            self.do_perflog(action)
        elif action.opcode == "userctr":
            self.metric.total_acts -= 1
            self.metric.cycle -= 1
            self.metric.exec_cycles -= 1
            self.do_user_ctr(action)
        elif action.opcode == "fp_div":
            self.metric.yld_ins += 1
            self.do_fp_div(action)
        elif action.opcode == "fp_add":
            self.metric.yld_ins += 1
            self.do_fp_add(action)
        # ==============================
        if seqnum_set == 0:
            next_seqnum = int(seqnum) + 1
        # print("exec-action-%s, yield_exec:%d, yield_term:%d" % (action.opcode, yield_exec, yield_term))
        self.metric.last_exec_cycle += self.metric.exec_cycles - start_exec_cycles

        return dst_property, forked_activations, yield_exec, next_seqnum, yield_term

    def parseIdx(self, dst_reg):
        return int(dst_reg[5:])

    # May not be needed for ob buffer
    def parseOffs(self, offs):
        return int(offs[3:])

    def parseEars(self, ears):
        return int(ears[4:])

    def rd_register(self, reg_ident):
        if reg_ident[0:4] == "UDPR":
            idx = self.parseIdx(reg_ident)
            printd(
                "Lane:%d Reg:%s:%d RegBase:%d"
                % (self.lane_id, reg_ident, self.UDPR[idx + self.curr_thread.udprbase], self.curr_thread.udprbase),
                stage_trace,
            )
            return self.UDPR[idx + self.curr_thread.udprbase]
        elif reg_ident == "SBP":
            # return self.SBP
            return self.curr_thread.SBP  # Marzi
        elif reg_ident == "LID":
            return self.lane_id
        elif reg_ident == "SBPB":
            return self.SBPB()
        elif reg_ident[0:2] == "OB":
            return self.rd_obbuffer(reg_ident)
        elif reg_ident == "EQT":
            return self.curr_event.event_word
        elif reg_ident == "TS":
            printd("ReadThreadState:%x" % self.curr_thread.thread_state, stage_trace)
            return self.curr_thread.thread_state
        else:
            idx = self.parseIdx(reg_ident)
            # printd("Reg:%s:%d" % (reg_ident,self.UDPR[idx]),progress_trace)
            return self.UDPR[idx + self.curr_thread.udprbase]

    def wr_register(self, reg_ident, data):
        if reg_ident == "SBP":
            # self.SBP = data
            self.curr_thread.SBP = data  # Marzi
        elif reg_ident == "SBPB":
            # self.SBP = data << 3
            self.curr_thread.SBP = data << 3  # Marzi
        else:
            idx = self.parseIdx(reg_ident)
            self.UDPR[idx + self.curr_thread.udprbase] = data

    def rd_obbuffer(self, ob_ident):
        offs = self.parseOffs(ob_ident)
        printd("%d %s:%d" % (self.lane_id, ob_ident, self.OpBuffer.getOp(offs + self.curr_thread.opbase)), stage_trace)
        return self.OpBuffer.getOp(offs + self.curr_thread.opbase)
        # return self.OpBuffer[offs]

    def rd_obbuffer_block(self, ob_ident, size):
        size = int(size / 4)
        ret_data = [0 for x in range(size)]
        offs = self.parseOffs(ob_ident) + self.curr_thread.opbase
        for i in range(size):
            ret_data[i] = self.OpBuffer.getOp(offs + i)
        return ret_data

    def wr_obbuffer(self, ob_ident, data):
        offs = self.parseOffs(ob_ident) + self.curr_thread.opbase
        # FIXME
        self.OpBuffer.setOp(data)
        # self.OpBuffer[offs] = data

    def wr_ear(self, ear_idx, dw1, dw2):
        data = ((dw2 & 0xFFFFFFFF) << 32) + (dw1 & 0xFFFFFFFF)
        idx = self.parseEars(ear_idx)
        # printd("WR_EAR: idx:%d, data:%d" % (idx, data), progress_trace)
        self.ear[idx] = data

    def rd_ear(self, ear_idx):
        # printd("RD_EAR:%s" % ear_idx, progress_trace)
        idx = self.parseEars(ear_idx)
        return self.ear[idx]

    def rd_imm(self, imm):
        return int(str(imm), 0)

    # ============ Detail Action Handler ===============
    def do_set_state_property(self, action):
        line = action.imm.split("::")
        p_type = line[0]

        if p_type == "flag":
            property = Property("flag", None)
        elif p_type == "common":
            property = Property("common", None)
        elif p_type == "majority":
            p_val = line[1]
            property = Property("majority", p_val)
        elif p_type == "flag_majority":
            p_val = line[1]
            property = Property("flag_majority", p_val)
        elif p_type == "default":
            p_val = line[1]
            property = Property("default", p_val)
        elif p_type == "flag_default":
            p_val = line[1]
            property = Property("flag_default", p_val)
        else:
            # print("unrecognized property")
            # print( p_type)
            exit()
        return property

    def do_hash_sb32(self, action):
        hashTableBaseAddr = int(action.imm)
        # start = self.SBP
        start = self.curr_thread.SBP  # Marzi
        # ====== align read 1 extra cycle
        # unaligned read 2 extra cycles
        if start % 4 == 0:
            self.metric.cycle += 1
            self.metric.exec_cycles += 1

        else:
            self.metric.cycle += 2
            self.metric.exec_cycles += 2

        value = self.in_stream[start : start + 32].bin
        value = self.bitsToInt(value)
        # ====== hash generates the entry index, each entry is 2 bytes
        # entry_addr = hash_snappy(value, 20)*2 + hashTableBaseAddr # using snappy hash
        entry_addr = hash_crc(value) * 2 + hashTableBaseAddr  # using crc hash
        self.wr_register(action.dst, entry_addr)

    def do_mov_lm2reg(self, action):
        src_addr = self.rd_register(action.src)
        src_addr = self.ds_base + src_addr
        numOfBytes = self.rd_imm(action.imm)
        if numOfBytes == 4:
            lm_data = self.LM.read_word(src_addr)
        elif numOfBytes == 2:
            lm_data = self.LM.read_2bytes(src_addr)
        elif numOfBytes == 1:
            lm_data = self.LM.read_byte(src_addr)
        else:
            # print("not yet support "),
            action.printOut(error)
            exit()
        # print("mov_lm2reg - src:%s src_addr:%x, lm_data:%d, dst:%s" % (action.src, src_addr,lm_data, action.dst))
        # self.metric.cycle += 1
        # self.metric.exec_cycles += 1
        self.metric.up_lm_read_bytes += numOfBytes
        self.wr_register(action.dst, lm_data)

    def do_mov_reg2lm(self, action):
        src_data = self.rd_register(action.src)
        numOfBytes = self.rd_imm(action.imm)
        lm_addr = self.rd_register(action.dst)
        # print("mov_reg2lm: src:%s data:%d, LM_addr = %d" % (action.src, src_data, lm_addr))
        lm_addr = self.ds_base + lm_addr
        if numOfBytes == 4:
            src_data = src_data & 0xFFFFFFFF
            self.LM.write_word(lm_addr, src_data)
        elif numOfBytes == 2:
            src_data = src_data & 0xFFFF
            self.LM.write_2bytes(lm_addr, src_data)
        elif numOfBytes == 1:
            src_data = src_data & 0xFF
            self.LM.write_byte(lm_addr, src_data)
        else:
            # print("not yet support "),
            action.printOut(error)
            exit()
        # self.metric.cycle +=1
        # self.metric.exec_cycles += 1
        self.metric.up_lm_write_bytes += numOfBytes
        # self.printDataStore(lm_addr,lm_addr+4, full_trace)

    def do_mov_ear2lm(self, action):
        src_data = self.rd_ear(action.src)
        numOfBytes = self.rd_imm(action.imm)
        lm_addr = self.rd_register(action.dst)
        # print("mov_ear2lm: src:%s data:%d, LM_addr = %d" % (action.src, src_data, lm_addr))
        lm_addr = self.ds_base + lm_addr
        if numOfBytes == 8:
            src_word = src_data & 0xFFFFFFFF
            self.LM.write_word(lm_addr, src_word)
            lm_addr = lm_addr + 4
            src_word = (src_data >> 32) & 0xFFFFFFFF
            self.LM.write_word(lm_addr, src_word)
        else:
            action.printOut(error)
            exit()
        self.metric.up_lm_write_bytes += numOfBytes

    def do_mov_lm2ear(self, action):
        src_addr = self.rd_register(action.src)
        src_addr = self.ds_base + src_addr
        numOfBytes = self.rd_imm(action.imm)
        # print("mov_lm2reg: src:%s data:%d, LM_addr = %d" % (action.src, src_addr))
        if numOfBytes == 8:
            src_word1 = self.LM.read_word(src_addr)
            src_addr = src_addr + 4
            src_word2 = self.LM.read_word(src_addr)
            self.wr_ear(action.dst, src_word1, src_word2)
        else:
            # print("not yet support "),
            action.printOut(error)
            exit()
        self.metric.up_lm_read_bytes += numOfBytes
        # self.wr_register(action.dst, lm_data)

    def do_mov_reg2reg(self, action):
        # print("Checking movreg2reg: src-%s, dst-%s" % (action.src, action.dst))
        src_data = self.rd_register(action.src)
        self.wr_register(action.dst, src_data)

    def do_mov_eqt2reg(self, action):
        src_data = self.curr_event.event_word
        self.wr_register(action.dst, src_data)

    def do_mov_ob2reg(self, action):
        src_data = self.rd_obbuffer(action.src)
        self.wr_register(action.dst, src_data)
        # if action.src == "OB_0" and action.dst == "UDPR_3":
        #     self.metric.frontier_edit_ins += 6

    def do_mov_ob2ear(self, action):
        src = action.src.split("_")
        src1 = "OB_" + src[1]
        src2 = "OB_" + src[2]
        data1 = self.rd_obbuffer(src1)
        data2 = self.rd_obbuffer(src2)
        # print("lane %s OB2EAR: src1:%s, src2:%s, dst:%s, data1:%d, data2:%d " % (self.lane_id, src1, src2, action.dst, data1, data2))
        self.wr_ear(action.dst, data1, data2)
        if action.dst == "EAR_1":
            self.metric.vertex_per_lane += 1
            num_edges = self.rd_register("UDPR_1")
            self.metric.edge_per_lane += num_edges
            if num_edges > self.metric.max_edge_per_lane:
                self.metric.max_edge_per_lane = num_edges
            self.metric.ins_for_iter += 8

    def do_ev_update_1(self, action):
        src = self.rd_register(action.src)
        imm = self.rd_imm(action.imm)
        mask = self.rd_imm(action.imm2)
        # mask = math.log2(mask)
        masks = [mask % 2, (mask >> 1) % 2, (mask >> 2) % 2, (mask >> 3) % 2]
        newword = src
        switch = {0: 0xFFFFFF00, 1: 0xFFFF00FF, 2: 0xFF00FFFF, 3: 0x00FFFFFF}
        for i in range(len(masks)):
            if masks[i] == 1:
                word_mask = switch[i]
                # word_mask = 0xff << 8*i
                newword = (newword & word_mask) | (imm << i * 8)
                # newword = newword | (imm << i*8)
        # if self.lane_id == 0:
        printd(
            "lane %s do_ev_update_1 - src %s(%s), imm %s, mask 0x%x, masks %s, newword %s"
            % (self.lane_id, action.src, src, imm, word_mask, masks, newword),
            stage_trace,
        )
        self.wr_register(action.dst, newword)

    def do_ev_update_2(self, action):
        src = self.curr_event.event_word
        imm = self.rd_imm(action.dst)
        imm2 = self.rd_imm(action.imm)
        mask = self.rd_imm(action.imm2)
        # mask = math.log2(mask)
        masks = [mask % 2, (mask >> 1) % 2, (mask >> 2) % 2, (mask >> 3) % 2]
        newword = src
        oneset = 0
        switch = {0: 0xFFFFFF00, 1: 0xFFFF00FF, 2: 0xFF00FFFF, 3: 0x00FFFFFF}
        for i in range(len(masks)):
            if masks[i] == 1:
                word_mask = switch[i]
                if oneset == 0:
                    newword = (newword & word_mask) | (imm << i * 8)
                    oneset = 1
                else:
                    newword = (newword & word_mask) | (imm2 << i * 8)
        self.wr_register(action.src, newword)
    
    def do_ev_update_reg_imm(self, action):
        src = self.curr_event.event_word
        regval = self.rd_register(action.dst)
        imm = self.rd_imm(action.imm)
        mask = self.rd_imm(action.imm2)
        # mask = math.log2(mask)
        masks = [mask % 2, (mask >> 1) % 2, (mask >> 2) % 2, (mask >> 3) % 2]
        newword = src
        oneset = 0
        switch = {0: 0xFFFFFF00, 1: 0xFFFF00FF, 2: 0xFF00FFFF, 3: 0x00FFFFFF}
        for i in range(len(masks)):
            if masks[i] == 1:
                word_mask = switch[i]
                if oneset == 0:
                    newword = (newword & word_mask) | (imm << i * 8)
                    oneset = 1
                else:
                    newword = (newword & word_mask) | (regval << i * 8)
        self.wr_register(action.src, newword)

    def do_ev_update_reg_2(self, action):
        src = self.rd_register(action.src)
        imm = self.rd_register(action.op1)
        imm2 = self.rd_register(action.op2)
        mask = self.rd_imm(action.imm)
        # mask = math.log2(mask)
        masks = [mask % 2, (mask >> 1) % 2, (mask >> 2) % 2, (mask >> 3) % 2]
        newword = src
        oneset = 0
        switch = {0: 0xFFFFFF00, 1: 0xFFFF00FF, 2: 0xFF00FFFF, 3: 0x00FFFFFF}
        for i in range(len(masks)):
            if masks[i] == 1:
                word_mask = switch[i]
                if oneset == 0:
                    newword = (newword & word_mask) | (imm << i * 8)
                    oneset = 1
                else:
                    newword = (newword & word_mask) | (imm2 << i * 8)
        self.wr_register(action.dst, newword)

    def do_compare_string(self, action):
        ref_p = self.rd_register(action.src) << 3
        cur_p = self.rd_register(action.rt) << 3
        length = 0
        ref_byte = self.in_stream[ref_p : ref_p + 8]
        cur_byte = self.in_stream[cur_p : cur_p + 8]
        while ref_byte == cur_byte and length < 255:
            # printd("find same:\n", full_trace)
            # printd(str(ref_byte)+","+str(cur_byte)+'\n',full_trace)
            ref_p += 8
            cur_p += 8
            length += 1
            ref_byte = self.in_stream[ref_p : ref_p + 8]
            cur_byte = self.in_stream[cur_p : cur_p + 8]
        # ====== estimate extra cycles
        self.metric.cycle += 2 + length / 4
        self.metric.exec_cycles += 2 + length / 4
        self.wr_register(action.dst, length)

    def do_compare_string_from_out(self, action):
        ref_p = self.rd_register(action.src) << 3
        cur_p = self.rd_register(action.rt) << 3
        length = 0
        ref_byte = self.out_stream[ref_p : ref_p + 8]
        cur_byte = self.out_stream[cur_p : cur_p + 8]
        while ref_byte == cur_byte and length < 255:
            # printd("find same:\n", full_trace)
            # printd(str(ref_byte)+","+str(cur_byte)+'\n',full_trace)
            ref_p += 8
            cur_p += 8
            length += 1
            ref_byte = self.out_stream[ref_p : ref_p + 8]
            cur_byte = self.out_stream[cur_p : cur_p + 8]
        # ====== estimate extra cycles
        self.metric.cycle += 2 + length / 4
        self.metric.exec_cycles += 2 + length / 4
        self.wr_register(action.dst, length)

    def do_sub_immediate(self, action):
        src_data = self.rd_register(action.src)
        imm = int(action.imm)
        res = src_data - imm
        self.wr_register(action.dst, res)

    def do_add_immediate(self, action):
        src_data = self.rd_register(action.src)
        imm = int(action.imm)
        res = src_data + imm
        printd("Debug:src_data:%d, imm:%d, res:%d, dst:%s" % (src_data, imm, res, action.dst), stage_trace)
        self.wr_register(action.dst, res)

    # ====== copy from [src_addr, src_addr+length) ======
    def do_copy(self, action):
        src_addr = self.rd_register(action.src)
        dst_addr = self.rd_register(action.rt)
        length = self.rd_register(action.dst)
        ori_length = length
        src_ptr = src_addr
        dst_ptr = dst_addr  # next line changed by Marzi
        # print("copy: ", end=' '),
        while length > 0:
            data_byte = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data_byte
            src_ptr += 1
            dst_ptr += 1
            length -= 1  # next line changed by Marzi
            # print(str((data_byte)), end=' '),
        # print("\n") #Marzi
        self.wr_register(action.src, src_ptr)
        self.wr_register(action.rt, dst_ptr)
        self.wr_register(action.dst, length)
        # ====== estimate extra cycles
        self.metric.cycle += 2 + ori_length / 4
        self.metric.exec_cycles += 2 + ori_length / 4
        # self.printOutStream(full_trace)

    def do_copy_ob_lm(self, action):
        src_addr = action.src
        dst_addr = self.rd_register(action.rt)
        length = self.rd_register(action.dst)
        ob_data = self.rd_obbuffer_block(src_addr, length)
        dst_addr = dst_addr + self.ds_base
        for i in range(int(length / 4)):
            self.LM.write_word(dst_addr + i * 4, ob_data[i])
            self.metric.up_lm_write_bytes += 4
        # self.metric.cycle += 2
        # self.metric.exec_cycles += 2

    # ====== copy from outstream [src_addr, src_addr+length) ======
    # NOTE: real UDP should have 1 copy. No matter from in stream or out stream
    def do_copy_from_out(self, action):
        src_addr = self.rd_register(action.src)
        dst_addr = self.rd_register(action.rt)
        length = self.rd_register(action.dst)
        ori_length = length
        src_ptr = src_addr
        dst_ptr = dst_addr  # next line changed by Marzi
        # print("copy_from_out: ", end=' '),
        while length > 0:
            data_byte = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data_byte
            src_ptr += 1
            dst_ptr += 1
            length -= 1  # next line changed by Marzi
            # print(str((data_byte)), end=' '),
        # print("\n") #Marzi
        self.wr_register(action.src, src_ptr)
        self.wr_register(action.rt, dst_ptr)
        self.wr_register(action.dst, length)
        # ====== estimate extra cycles
        self.metric.cycle += 2 + ori_length / 4
        self.metric.exec_cycles += 2 + ori_length / 4
        # self.printOutStream(full_trace)

    def do_sub_reg(self, action):
        src = self.rd_register(action.src)
        rt = self.rd_register(action.rt)
        res = src - rt
        self.wr_register(action.dst, res)

    def do_add_reg(self, action):
        src = self.rd_register(action.src)
        rt = self.rd_register(action.rt)
        res = src + rt
        self.wr_register(action.dst, res)

    def do_bitclr_reg(self, action):
        src = self.rd_register(action.src)
        rt = self.rd_register(action.rt)
        res = src & ~(1 << rt)
        self.wr_register(action.dst, res)

    def do_bitset_reg(self, action):
        src = self.rd_register(action.src)
        rt = self.rd_register(action.rt)
        res = src | (1 << rt)
        self.wr_register(action.dst, res)

    def do_put2byte_imm(self, action):
        data = self.rd_imm(action.imm)
        dst_ptr = self.rd_register(action.dst)
        data = data & 0xFFFF
        # ====== align write and unalign write
        if dst_ptr % 4 == 0 or dst_ptr % 4 == 1 or dst_ptr % 4 == 2:
            self.metric.cycle += 1
            self.metric.exec_cycles += 1
        else:
            self.metric.cycle += 2
            self.metric.exec_cycles += 2

        # self.out_stream[dst_ptr<<3:(dst_ptr<<3)+16] = data
        # dst_ptr += 2
        # self.wr_register(action.dst, dst_ptr)
        # Changed by Marzi since system is little endian (data is stored with the least significant part of hex number first)
        data_l = data & 0xFF
        self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data_l
        dst_ptr += 1
        data_h = (data >> 8) & 0xFF
        self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data_h
        dst_ptr += 1
        self.wr_register(action.dst, dst_ptr)
        printd("put_l:" + str(hex(data_l)) + "\n", stage_trace)
        printd("put_h:" + str(hex(data_h)) + "\n", stage_trace)

    def do_put1byte_imm(self, action):
        data = self.rd_imm(action.imm)
        dst_ptr = self.rd_register(action.dst)
        data = data & 0xFF
        # ====== unalign write
        self.metric.cycle += 1
        self.metric.exec_cycles += 1
        self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data
        dst_ptr += 1
        self.wr_register(action.dst, dst_ptr)
        # printd("put:"+str(hex(data))+"\n", full_trace)

    def do_lshift_add_imm(self, action):
        src = self.rd_register(action.src)
        add_val = self.rd_imm(action.imm2)
        shift_val = int(action.imm)
        res = ((src << shift_val) & 4294967295) + add_val
        self.wr_register(action.dst, res)

    def do_rshift_add_imm(self, action):
        src = self.rd_register(action.src)
        add_val = self.rd_imm(action.imm2)
        shift_val = int(action.imm)
        res = (src >> shift_val) + add_val
        self.wr_register(action.dst, res)

    def do_lshift_and_imm(self, action):
        src = self.rd_register(action.src)
        and_val = self.rd_imm(action.imm2)
        shift_val = int(action.imm)
        res = ((src << shift_val) & 4294967295) & and_val
        # print("lshift_check:src:%d, and_val:%d, shift_val:%d, %s:%d" % (src, and_val, shift_val, action.dst,res))
        self.wr_register(action.dst, res)

    def do_rshift_and_imm(self, action):
        src = self.rd_register(action.src)
        and_val = self.rd_imm(action.imm2)
        shift_val = int(action.imm)
        res = (src >> shift_val) & and_val
        # print("lane %s do_rshift_and_imm - src: %s(%s) shift: %s(%s) dst: %s(%s)" % (self.lane_id, action.src, src, action.imm, shift_val, action.dst, res))
        self.wr_register(action.dst, res)

    def do_lshift_or_imm(self, action):
        src = self.rd_register(action.src)
        or_val = self.rd_imm(action.imm2)
        shift_val = int(action.imm)
        res = ((src << shift_val) & 4294967295) | or_val
        self.wr_register(action.dst, res)

    def do_rshift_or_imm(self, action):
        src = self.rd_register(action.src)
        or_val = self.rd_imm(action.imm2)
        shift_val = int(action.imm)
        res = (int(src) >> shift_val) | or_val
        self.wr_register(action.dst, res)

    def do_putbytes(self, action):
        data = self.rd_register(action.src)
        numOfBytes = int(action.imm)
        dst_ptr = self.rd_register(action.dst)
        # print("do_putbytes=> data: "+str(hex(data))+ " dst:" +str(dst_ptr) ) #Marzi
        if numOfBytes == 4:
            # ====== align write and unalign write
            if dst_ptr % 4 == 0:
                self.metric.cycle += 0
            else:
                self.metric.cycle += 2
                self.metric.exec_cycles += 2
            data = data & 0xFFFFFFFF
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 32] = data
            dst_ptr += 4
        elif numOfBytes == 3:
            # ====== align write and unalign write
            if dst_ptr % 4 == 0 or dst_ptr % 4 == 1:
                self.metric.cycle += 1
                self.metric.exec_cycles += 1
            else:
                self.metric.cycle += 2
                self.metric.exec_cycles += 2
            data = data & 0xFFFFFF
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 24] = data
            dst_ptr += 3
        elif numOfBytes == 2:
            # ====== align write and unalign write
            if dst_ptr % 4 == 0 or dst_ptr % 4 == 1 or dst_ptr % 4 == 2:
                self.metric.cycle += 1
                self.metric.exec_cycles += 1
            else:
                self.metric.cycle += 2
                self.metric.exec_cycles += 2
            data = data & 0xFFFF
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 16] = data
            dst_ptr += 2
        elif numOfBytes == 1:
            # ====== unalign write
            self.metric.cycle += 1
            self.metric.exec_cycles += 1
            data = data & 0xFF
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data
            dst_ptr += 1
        else:
            print("numOfBytes Wrong in " + action.printOut(error))
            exit()
        self.wr_register(action.dst, dst_ptr)
        # printd("put:"+str(hex(data))+"\n",full_trace)

    def do_compare_less_than(self, action):
        if action.src[0] == "U":
            src = self.rd_register(action.src)
        else:
            src = self.rd_obbuffer(action.src)
        imm = self.rd_imm(action.imm)
        if src < imm:
            res = 1
        else:
            res = 0
        self.wr_register(action.dst, res)

    def do_compare_great_than(self, action):
        if action.src[0] == "U":
            src = self.rd_register(action.src)
        else:
            src = self.rd_obbuffer(action.src)
        imm = self.rd_imm(action.imm)
        if src > imm:
            res = 1
        else:
            res = 0
        self.wr_register(action.dst, res)

    def do_compare_equal(self, action):
        if action.src[0] == "U":
            src = self.rd_register(action.src)
        else:
            src = self.rd_obbuffer(action.src)
        imm = self.rd_imm(action.imm)
        if src == imm:
            res = 1
        else:
            res = 0
        self.wr_register(action.dst, res)

    def do_compare_reg(self, action):
        if action.src[0] == "U":
            src = self.rd_register(action.src)
        else:
            src = self.rd_obbuffer(action.src)
        if action.rt[0] == "U":
            rt = self.rd_register(action.rt)
        else:
            rt = self.rd_obbuffer(action.rt)
        # if src == rt:
        #    res = 1
        # else:
        #    res = 0
        res = src - rt
        # printd("comp_reg: action.src:%s, action.rt:%s" % (action.src, action.rt), progress_trace)
        self.wr_register(action.dst, res)

    def do_compare_reg_equal(self, action):
        if action.src[0] == "U":
            src = self.rd_register(action.src)
        else:
            src = self.rd_obbuffer(action.src)
        if action.rt[0] == "U":
            rt = self.rd_register(action.rt)
        else:
            rt = self.rd_obbuffer(action.rt)
        if src == rt:
            res = 1
        else:
            res = 0
        self.wr_register(action.dst, res)

    def do_compare_reg_less_than(self, action):
        if action.src[0] == "U":
            src = self.rd_register(action.src)
        else:
            src = self.rd_obbuffer(action.src)
        if action.rt[0] == "U":
            rt = self.rd_register(action.rt)
        else:
            rt = self.rd_obbuffer(action.rt)
        if src < rt:
            res = 1
        else:
            res = 0
        self.wr_register(action.dst, res)

    def do_compare_reg_great_than(self, action):
        if action.src[0] == "U":
            src = self.rd_register(action.src)
        else:
            src = self.rd_obbuffer(action.src)
        if action.rt[0] == "U":
            rt = self.rd_register(action.rt)
        else:
            rt = self.rd_obbuffer(action.rt)
        if src > rt:
            res = 1
        else:
            res = 0
        self.wr_register(action.dst, res)

    def do_bitwise_xor(self, action):
        src = self.rd_register(action.src)
        rt = self.rd_register(action.rt)
        dst = rt ^ src
        self.wr_register(action.dst, dst)

    def do_bitwise_or(self, action):
        src = self.rd_register(action.src)
        rt = self.rd_register(action.rt)
        dst = rt | src
        self.wr_register(action.dst, dst)

    def do_bitwise_and(self, action):
        src = self.rd_register(action.src)
        rt = self.rd_register(action.rt)
        dst = rt & src
        self.wr_register(action.dst, dst)

    def do_lshift_or(self, action):
        src = self.rd_register(action.src)
        dst = self.rd_register(action.dst)
        shift = self.rd_imm(action.imm)
        dst = dst | ((src << shift) & 4294967295)
        # print("lshift_check:%s:%d" % (action.dst,dst))
        self.wr_register(action.dst, dst)

    def do_lshift(self, action):
        src = self.rd_register(action.src)
        dst = self.rd_register(action.dst)
        shift = self.rd_imm(action.imm)
        dst = (src << shift) & 4294967295
        self.wr_register(action.dst, dst)

    def do_rshift_or(self, action):
        src = self.rd_register(action.src)
        dst = self.rd_register(action.dst)
        shift = self.rd_imm(action.imm)
        res = dst | (src >> shift)
        self.wr_register(action.dst, res)

    def do_rshift(self, action):
        src = self.rd_register(action.src)
        dst = self.rd_register(action.dst)
        shift = self.rd_imm(action.imm)
        dst = src >> shift
        # print("rshift_check:%d:%d:%d" % (src,shift,dst))
        self.wr_register(action.dst, dst)

    def do_rshift_t(self, action):
        src = self.rd_register(action.src)
        dst = self.rd_register(action.dst)
        shift = self.rd_register(action.rt)
        dst = src >> shift
        # print("rshift_t_check:%d:%d:%d" % (src,shift,dst))
        self.wr_register(action.dst, dst)

    def do_lshift_t(self, action):
        src = self.rd_register(action.src)
        dst = self.rd_register(action.dst)
        shift = self.rd_register(action.rt)
        dst = (src << shift) & 4294967295
        # print("lshift_t_check:%d:%d:%d" % (src,shift, dst))
        self.wr_register(action.dst, dst)

    def do_arithrshift(self, action):  # added by Marziyeh (arithrshifts)
        src = self.rd_register(action.src)
        dst = self.rd_register(action.dst)
        shift = self.rd_imm(action.imm)
        dst = arithmetic_rshift(src, 32, shift)
        self.wr_register(action.dst, dst)

    def do_arithrshift_t(self, action):  # added by Marziyeh (arithrshifts)
        src = self.rd_register(action.src)
        dst = self.rd_register(action.dst)
        shift = self.rd_register(action.rt)
        dst = arithmetic_rshift(src, 32, shift)
        self.wr_register(action.dst, dst)

    def do_getbytes(self, action):
        src_ptr = self.rd_register(action.src)
        numOfBytes = self.rd_imm(action.imm)
        if numOfBytes == 4:
            # ====== align read and unalign read
            if src_ptr % 4 == 0:
                self.metric.cycle += 1
                self.metric.exec_cycles += 1
            else:
                self.metric.cycle += 2
                self.metric.exec_cycles += 2

            data = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 32]
            src_ptr += 4
            data = data.tobytes()
            res = 0
            for i in range(0, 4):
                #                res |= ord(data[3-i])<< (i*8)
                #                res |= (data[3-i])<< (i*8)
                res |= (data[i]) << (i * 8)  # changed by Marzi due to Machin's endian's discrepency

        elif numOfBytes == 3:
            # ====== align read and unalign read
            if src_ptr % 4 == 0 or src_ptr % 4 == 1:
                self.metric.cycle += 1
                self.metric.exec_cycles += 1
            else:
                self.metric.cycle += 2
                self.metric.exec_cycles += 2

            data = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 24]
            src_ptr += 3
            data = data.tobytes()
            res = 0
            for i in range(0, 3):  # 2): #changed by Marzi (I think this was incorrect)
                #                res |= ord(data[2-i])<< (i*8)
                #                res |= (data[2-i])<< (i*8)
                res |= (data[i]) << (i * 8)  # changed by Marzi due to Machin's endian's discrepency

        elif numOfBytes == 2:
            # ====== align read and unalign read
            if src_ptr % 4 == 0 or src_ptr % 4 == 1 or src_ptr % 4 == 2:
                self.metric.cycle += 1
                self.metric.exec_cycles += 1
            else:
                self.metric.cycle += 2
                self.metric.exec_cycles += 2
            data = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 16]
            src_ptr += 2
            data = data.tobytes()
            res = 0
            for i in range(0, 2):
                #                res |= ord(data[1-i])<< (i*8)
                #                res |= (data[1-i])<< (i*8)
                res |= (data[i]) << (i * 8)  # changed by Marzi due to Machin's endian's discrepency

        elif numOfBytes == 1:
            # ====== align read
            self.metric.cycle += 1
            self.metric.exec_cycles += 1

            data = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            src_ptr += 1
            data = data.tobytes()
            #            res = ord(data[0])
            res = data[0]

        self.wr_register(action.src, src_ptr)
        self.wr_register(action.dst, res)

    def do_getbytes_from_out(self, action):
        src_ptr = self.rd_register(action.src)
        numOfBytes = self.rd_imm(action.imm)
        if numOfBytes == 4:
            # ====== align read and unalign read
            if src_ptr % 4 == 0:
                self.metric.cycle += 1
                self.metric.exec_cycles += 1
            else:
                self.metric.cycle += 2
                self.metric.exec_cycles += 2

            data = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 32]
            src_ptr += 4
            data = data.tobytes()
            res = 0
            for i in range(0, 4):
                #                res |= ord(data[3-i])<< (i*8)
                res |= (data[3 - i]) << (i * 8)

        elif numOfBytes == 3:
            # ====== align read and unalign read
            if src_ptr % 4 == 0 or src_ptr % 4 == 1:
                self.metric.cycle += 1
                self.metric.exec_cycles += 1
            else:
                self.metric.cycle += 2
                self.metric.exec_cycles += 2

            data = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 24]
            src_ptr += 3
            data = data.tobytes()
            res = 0
            for i in range(0, 3):  # 2): #changed by Marzi (I think this was incorrect)
                #                res |= ord(data[2-i])<< (i*8)
                res |= (data[2 - i]) << (i * 8)

        elif numOfBytes == 2:
            # ====== align read and unalign read
            if src_ptr % 4 == 0 or src_ptr % 4 == 1 or src_ptr % 4 == 2:
                self.metric.cycle += 1
                self.metric.exec_cycles += 1
            else:
                self.metric.cycle += 2
                self.metric.exec_cycles += 2

            data = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 16]
            src_ptr += 2
            data = data.tobytes()
            res = 0
            for i in range(0, 2):
                #                res |= ord(data[1-i])<< (i*8)
                res |= (data[1 - i]) << (i * 8)

        elif numOfBytes == 1:
            # ====== align read
            self.metric.cycle += 1
            self.metric.exec_cycles += 1

            data = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            src_ptr += 1
            data = data.tobytes()
            #            res = ord(data[0])
            res = data[0]

        self.wr_register(action.src, src_ptr)
        self.wr_register(action.dst, res)

    def do_rshift_sub_imm(self, action):
        src = self.rd_register(action.src)
        sub_val = self.rd_imm(action.imm2)
        shift_val = int(action.imm)
        res = (src >> shift_val) - sub_val
        self.wr_register(action.dst, res)

    def do_lshift_sub_imm(self, action):
        src = self.rd_register(action.src)
        sub_val = self.rd_imm(action.imm2)
        shift_val = self.rd_imm(action.imm)
        res = ((src << shift_val) & 4294967295) - sub_val
        self.wr_register(action.dst, res)

    def do_cmpswp_i(self, action):
        # reg = self.rd_register(action.src)
        mem_addr = self.rd_register(action.dst)
        mem_addr = self.ds_base + mem_addr
        mem = self.LM.read_word(mem_addr)
        self.metric.up_lm_read_bytes += 4
        if mem == self.rd_imm(action.imm):
            self.LM.write_word(mem_addr, self.rd_imm(action.imm2))
        self.metric.up_lm_write_bytes += 4
        self.wr_register(action.src, mem)

    def do_cmpswp_ri(self, action):
        # reg = self.rd_register(action.src)
        # src = mem
        # rt = old val
        # dest = new val
        mem_addr = self.rd_register(action.dst)
        mem_addr = self.ds_base + mem_addr
        mem = self.LM.read_word(mem_addr)
        old_val = self.rd_register(action.imm)
        self.metric.up_lm_read_bytes += 4
        if mem == old_val:
            self.LM.write_word(mem_addr, self.rd_imm(action.imm2))
        self.metric.up_lm_write_bytes += 4
        self.wr_register(action.src, mem)

    def do_cmpswp(self, action):
        # reg = self.rd_register(action.src)
        # src = mem
        # rt = old val
        # dest = new val
        mem_addr = self.rd_register(action.dst)
        mem_addr = self.ds_base + mem_addr
        mem = self.LM.read_word(mem_addr)
        self.metric.up_lm_read_bytes += 4
        old_val = self.rd_register(action.imm)
        new_val = self.rd_register(action.imm2)
        if mem == old_val:
            self.LM.write_word(mem_addr, new_val)
        self.metric.up_lm_write_bytes += 4
        self.wr_register(action.src, mem)

    def do_bitwise_and_imm(self, action):
        src = self.rd_register(action.src)
        mask = self.rd_imm(action.imm)
        res = src & mask
        self.wr_register(action.dst, res)

    def do_bitwise_or_imm(self, action):
        src = self.rd_register(action.src)
        mask = self.rd_imm(action.imm)
        res = src | mask
        self.wr_register(action.dst, res)

    def do_bitwise_xor_imm(self, action):
        src = self.rd_register(action.src)
        imm = self.rd_imm(action.imm)
        res = src ^ imm
        self.wr_register(action.dst, res)

    # ====== copy from [src_addr, src_addr+length) ======
    def do_copy_imm(self, action):
        src_addr = self.rd_register(action.src)
        dst_addr = self.rd_register(action.dst)
        length = self.rd_imm(action.imm)
        ori_length = length
        src_ptr = src_addr
        dst_ptr = dst_addr
        # print("copy-imm ("+str(src_ptr)+","+str(length)+") :", end=' ') #Marzi
        while length > 0:
            data_byte = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data_byte
            src_ptr += 1
            dst_ptr += 1
            length -= 1  # next line Marzi changed
            # print(str((data_byte)), end=' '),
        # print("\n") #Marzi
        self.wr_register(action.src, src_ptr)
        self.wr_register(action.dst, dst_ptr)
        # ====== estimate extra cycles
        self.metric.cycle += 2 + ori_length / 4
        # self.printOutStream(full_trace)

    # ====== copy from [src_addr, src_addr+length) ======
    def do_copy_from_out_imm(self, action):
        src_addr = self.rd_register(action.src)
        dst_addr = self.rd_register(action.dst)
        length = self.rd_imm(action.imm)
        ori_length = length
        src_ptr = src_addr
        dst_ptr = dst_addr
        # print("copy_from_out_imm: ", end=' ') #Marz
        while length > 0:
            data_byte = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data_byte
            src_ptr += 1
            dst_ptr += 1
            length -= 1  # next line Marzi changed
            # print(str((data_byte)), end=' '),
        # print("\n") #Marzi
        self.wr_register(action.src, src_ptr)
        self.wr_register(action.dst, dst_ptr)
        # ====== estimate extra cycles
        self.metric.cycle += 2 + ori_length / 4
        self.metric.exec_cycles += 2 + ori_length / 4
        # self.printOutStream(full_trace)

    def do_swap_bytes(self, action):
        data = self.rd_register(action.src)
        numOfbytes = self.rd_imm(action.imm)
        if numOfbytes == 2:
            high = (data >> 8) & 0xFF
            low = data & 0xFF
            swaped = low << 8 | high
            self.wr_register(action.dst, swaped)
        else:
            print("not yet support")
            action.printOut(error)
        # self.wr_register(action.dst, swaped)

    def do_mask_or(self, action):
        src = self.rd_register(action.src)
        mask = self.rd_imm(action.imm)
        dst = self.rd_register(action.dst)
        data = (src & mask) | dst
        self.wr_register(action.dst, data)

    def do_goto(self, action):
        # ====== it is a virtual action that does the "goto"
        # the transition primitive actually does the "goto" address in the attach
        # it is used for transitions whose all actions are in the same shared action block
        if action.opcode == "tranCarry_goto":
            self.metric.cycle -= 1
            self.metric.exec_cycles -= 1

        block_id = action.imm
        if block_id not in self.program.sharedBlock:
            # print("error in goto symbolic link")
            action.printOut(error)
            exit()

        action_list = self.program.sharedBlock[block_id]
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum = 0
        # ====== execute each action in the block
        while yield_exec == 0 and seqnum <= len(action_list):
            # ====== action can modify the destination state's
            # property, and fork multiple activations ======
            # actions execute until you hit a yield
            shared_act = action_list[seqnum]
            action_dst_property, forked_activations, yield_exec, next_seqnum, yield_term = self.actionHandler(shared_act, seqnum)
            # branch instructions could've changed the seqnum
            seqnum = next_seqnum
            # ====== if action changes the property, we need to
            # apply it to destination state ======
            if action_dst_property is not None:
                dst_property = action_dst_property
        # print("goto-return-yield_exec:%d, yield_term:%d" % (yield_exec, yield_term))
        return dst_property, forked_activations, yield_exec, yield_term

        # for shared_act in action_list:
        #    #====== action can modify the destination state's
        #    #property, and fork multiple activations ======
        #    action_dst_property, forked_activations = self.actionHandler(shared_act)
        #
        #    #====== if action changes the property, we need to
        #    #apply it to destination state ======
        #    if action_dst_property != None:
        #        dst_property = action_dst_property
        # return dst_property, forked_activations

    # def do_accept(self, action):
    #     accept_id = self.rd_imm(action.imm)
    #     position = self.SBPB()
    #     dst_ptr = self.rd_register(action.dst)
    #     packed_data = accept_id << 16 | position & 0xffff
    #     self.out_stream[dst_ptr<<3:(dst_ptr<<3)+32] = packed_data
    #     dst_ptr += 4
    #     self.wr_register(action.dst, dst_ptr)

    def do_set_issue_width(self, action):
        new_width = self.rd_imm(action.imm)
        # Changes by Marzi
        # self.CR_Issue = new_width
        # old_CR_Advance = self.CR_Advance
        # self.CR_Advance = new_width
        self.curr_thread.CR_Issue = new_width
        old_CR_Advance = self.curr_thread.CR_Advance
        self.curr_thread.CR_Advance = new_width
        # the SBP should commit the old_CR_Advance,
        # we compensate here
        # Changes by Marzi
        # self.SBP += old_CR_Advance - self.CR_Advance
        self.curr_thread.SBP += old_CR_Advance - self.curr_thread.CR_Advance
        # printd ("issue:"+str(self.curr_thread.CR_Issue)+" advance:"+str(self.CR_Advance)+"\n",full_trace)

    def do_set_complete(self, action):
        imm = self.rd_imm(action.imm)
        if imm == 1:
            # self.SBP = self.getInStreamBits() + 1
            self.curr_thread.SBP = self.getInStreamBits() + 1  # Marzi

    def do_refill(self, action):
        # it is a virutal action. In machine code, it is represented in transition
        # primitive
        self.metric.cycle -= 1
        self.metric.exec_cycles -= 1
        flush = self.rd_imm(action.imm)
        # self.SBP = self.SBP - flush
        self.curr_thread.SBP = self.curr_thread.SBP - flush  # Marzi

    def do_mov_imm2reg(self, action):
        imm = self.rd_imm(action.imm)
        self.wr_register(action.dst, imm)

    # TODO:finish this
    def do_mov_sb2reg(self, action):  # added by Marzi
        # issue_data = self.in_stream[self.SBP:self.SBP+self.CR_Issue].bin
        issue_data = self.in_stream[self.curr_thread.SBP : self.curr_thread.SBP + self.curr_thread.CR_Issue].bin  # Marzi
        issue_data = self.bitsToInt(issue_data)
        self.wr_register(action.imm, issue_data)

    def do_bne(self, action):
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum_set = 0
        if action.op1_ob_or_reg == 0:
            op1 = self.rd_obbuffer(action.op1)
        else:
            op1 = self.rd_register(action.op1)
        if action.op2_ob_or_reg_or_imm == 0:
            op2 = self.rd_obbuffer(action.op2)
        elif action.op2_ob_or_reg_or_imm == 1:
            op2 = self.rd_register(action.op2)
        else:
            op2 = action.op2  # Imm Value
        op1 = int(op1)
        op2 = int(op2)
        # printd("BNE-OP1:%d, OP2:%d" % (op1,op2), progress_trace)
        if op1 != op2:
            if action.dst_issb == 1:
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, None, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                next_seqnum = int(action.dst)
                seqnum_set = 1
            if action.op1 == "UDPR_11":
                self.metric.cmp_fail_count += 1
        else:
            next_seqnum = 0
            seqnum_set = 0
            if action.op1 == "UDPR_11":
                self.metric.cmp_succ_count += 1
        return next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term

    def do_beq(self, action):
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum_set = 0
        if action.op1_ob_or_reg == 0:
            op1 = self.rd_obbuffer(action.op1)
        else:
            op1 = self.rd_register(action.op1)
        if action.op2_ob_or_reg_or_imm == 0:
            op2 = self.rd_obbuffer(action.op2)
        elif action.op2_ob_or_reg_or_imm == 1:
            op2 = self.rd_register(action.op2)
        else:
            op2 = action.op2  # Imm Value
        op1 = int(op1)
        op2 = int(op2)
        if action.op1 == "UDPR_4" and action.op2 == "UDPR_0":
            self.metric.num_update += 1
        # print("lane %s do_beq - op1 %s(%s) op2 %s(%s) action.dst: %s" % (self.lane_id, action.op1, op1, action.op2, op2, action.dst))
        if op1 == op2:
            if action.op1 == "UDPR_4" and action.dst == "19":
                self.metric.num_send_rd += 1
            if action.dst_issb == 1:
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, None, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                # print("do_beq - branch to target action.dst: %s" % action.dst)
                next_seqnum = int(action.dst)
                seqnum_set = 1
            if action.op1 == "UDPR_4" and action.op2 == "UDPR_0":
                self.metric.num_hit += 1
        else:
            next_seqnum = 0
            seqnum_set = 0
        return next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term

    def do_bgt(self, action):
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum_set = 0
        if action.op1_ob_or_reg == 0:
            op1 = self.rd_obbuffer(action.op1)
        else:
            op1 = self.rd_register(action.op1)
        if action.op2_ob_or_reg_or_imm == 0:
            op2 = self.rd_obbuffer(action.op2)
        elif action.op2_ob_or_reg_or_imm == 1:
            op2 = self.rd_register(action.op2)
        else:
            op2 = action.op2  # Imm Value
        op1 = int(op1)
        op2 = int(op2)
        # print("lane %s do_bgt - op1 %s(%s) op2 %s(%s) action.dst: %s" % (self.lane_id, action.op1, op1, action.op2, op2, action.dst))
        if op1 > op2:
            if action.dst_issb == 1:  # Is this a shared block?
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, None, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                next_seqnum = int(action.dst)
                seqnum_set = 1
        else:
            next_seqnum = 0
            seqnum_set = 0
        return next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term

    def do_bge(self, action):
        # pdb.set_trace()
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum_set = 0
        if action.op1_ob_or_reg == 0:
            op1 = self.rd_obbuffer(action.op1)
        else:
            op1 = self.rd_register(action.op1)
        if action.op2_ob_or_reg_or_imm == 0:
            op2 = self.rd_obbuffer(action.op2)
        elif action.op2_ob_or_reg_or_imm == 1:
            op2 = self.rd_register(action.op2)
        else:
            op2 = action.op2  # Imm Value
        op1 = int(op1)
        op2 = int(op2)
        # print("lane %s do_bge - op1 %s(%s) op2 %s(%s) action.dst: %s" % (self.lane_id, action.op1, op1, action.op2, op2, action.dst))
        if op1 >= op2:
            if action.dst_issb == 1:
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, None, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                next_seqnum = int(action.dst)
                seqnum_set = 1
        else:
            next_seqnum = 0
            seqnum_set = 0
        return next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term

    def do_blt(self, action):
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum_set = 0
        if action.op1_ob_or_reg == 0:
            op1 = self.rd_obbuffer(action.op1)
        else:
            op1 = self.rd_register(action.op1)
        if action.op2_ob_or_reg_or_imm == 0:
            op2 = self.rd_obbuffer(action.op2)
        elif action.op2_ob_or_reg_or_imm == 1:
            op2 = self.rd_register(action.op2)
        else:
            op2 = action.op2  # Imm Value
        op1 = int(op1)
        op2 = int(op2)
        if op1 < op2:
            if action.dst_issb == 1:
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, None, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                next_seqnum = int(action.dst)
                seqnum_set = 1
        else:
            next_seqnum = 0
            seqnum_set = 0
        # if self.lane_id == 0:
        #    print("do_blt - UDPR_6 %s" % self.rd_register("UDPR_6"))
        return next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term

    def do_ble(self, action):
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum_set = 0
        if action.op1_ob_or_reg == 0:
            op1 = self.rd_obbuffer(action.op1)
        else:
            op1 = self.rd_register(action.op1)
        if action.op2_ob_or_reg_or_imm == 0:
            op2 = self.rd_obbuffer(action.op2)
        elif action.op2_ob_or_reg_or_imm == 1:
            op2 = self.rd_register(action.op2)
        else:
            op2 = action.op2  # Imm Value
        op1 = int(op1)
        op2 = int(op2)
        if op1 <= op2:
            if action.op1 == "UDPR_8":
                self.metric.base_ins += 3
            if action.dst_issb == 1:
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, None, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                next_seqnum = int(action.dst)
                seqnum_set = 1
        else:
            if action.op1 == "UDPR_4":
                self.metric.num_collision += 1
                # print("lane %s ble - op1 %s(%s) op2 %s(%s) dst %s" % (self.lane_id, action.op1, op1, action.op2, op2, action.dst))
            next_seqnum = 0
            seqnum_set = 0
        # print("Lane %s do_ble - op1 %s(%s) op2 %s(%s) dst %s" % (self.lane_id, action.op1, op1, action.op2, op2, action.dst))
        return next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term

    def do_jmp(self, action):
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum_set = 0
        if action.dst_issb == 1:
            next_seqnum = 0
            seqnum_set = 0
            pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, None, 1)
            dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
        else:
            next_seqnum = int(action.dst)
            seqnum_set = 1
        return next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term

    def do_send_old(self, action):
        if action.dst != "TOP":
            event_word = self.rd_register(action.event)
            dest = self.rd_register(action.dst)
            addr = self.rd_register(action.addr)
            addr_mode = int(action.addr_mode)
            if dest == -1 or dest == 0xFFFFFFFF:
                lane_num = self.lane_id
            else:
                lane_num = dest - 2
            printd(
                "send_old, event_word:%d, dest:%d, addr:%d, addr_mode:%d, lane_num:%d" % (event_word, dest, addr, addr_mode, lane_num),
                stage_trace,
            )
            if (dest > 1 or dest == -1) and action.rw == "r":  # read message
                size = int(action.size)
                if addr_mode > 0:
                    ear_base = "EAR_" + str(addr_mode - 1)
                    dram_addr = self.address_generate_unit(ear_base, addr)
                ori_lane = (event_word & 0xFF000000) >> 24
                event_label = event_word & 0x000000FF
                ev_operands = [None for i in range(int(size / 4))]
                for i in range(int(size / 4)):
                    if addr_mode > 0 and addr_mode > 0:
                        ev_operands[i] = self.dram.read_word(dram_addr + 4 * i)
                        self.metric.up_dram_read_bytes += 4
                    else:
                        addr = addr + self.ds_base
                        ev_operands[i] = self.LM.read_word(addr + 4 * i)
                        self.metric.cycle += 1
                        self.metric.exec_cycles += 1
                self.all_lanes[lane_num].OpBuffer.setOp(0)
                for val in ev_operands:
                    self.all_lanes[lane_num].OpBuffer.setOp(val)
                event_label = event_word & 0x000000FF

                next_event = Event(event_label, len(ev_operands))
                next_event.setlanenum(self.lane_id)
                next_event.setthreadid(self.curr_thread.tid)
                next_event.set_cycle(self.metric.last_exec_cycle + 1 + (self.all_lanes[lane_num].EvQ.getOccup()))
                self.all_lanes[lane_num].EvQ.pushEvent(next_event)
                self.upproc.incr_events()
                # release lock for lane
            elif action.rw == "w":
                if addr_mode > 0 and addr_mode < 5:  # write data from Reg to DRAM
                    ear_base = "EAR_" + str(addr_mode - 1)
                    dram_addr = self.address_generate_unit(ear_base, addr)
                    data = self.rd_register(action.dst)
                    size = int(action.size)
                    for i in range(int(size / 4)):
                        self.dram.write_word(dram_addr, data)
                    event_label = event_word & 0x000000FF
                    next_event = Event(event_label, 0)
                    next_event.setlanenum(self.lane_id)
                    next_event.setthreadid(self.curr_thread.tid)
                    next_event.set_cycle(self.metric.last_exec_cycle + 1 + (self.EvQ.getOccup()) + dram_lat)
                    self.OpBuffer.setOp(0)
                    self.EvQ.pushEvent(next_event)
                    self.upproc.incr_events()
                    # print("Lane: %d W mode, 0<addr_mode<5: Increment Events: %d" % (self.lane_id, self.upproc.outstanding_events))
                elif addr_mode == 0:  # write data from Rw to different lane
                    data = self.rd_register(action.dst)  # data from Rw
                    if addr != -1:
                        lane_num = addr - 2  # dest lane num (Ra)
                    else:
                        lane_num = self.lane_id
                    size = int(action.size)
                    # self.q_locks[lane_num].acquire()
                    self.all_lanes[lane_num].OpBuffer.setOp(0)
                    self.all_lanes[lane_num].OpBuffer.setOp(data)
                    event_label = event_word & 0x000000FF
                    if event_label == 1:
                        # it takes master 6 instructions to update the frontier
                        self.metric.frontier_edit_ins += 8
                    next_event = Event(event_label, 1)
                    next_event.setlanenum(lane_num)
                    next_event.setthreadid(0xFF)
                    next_event.set_cycle(self.metric.last_exec_cycle + 1 + (self.all_lanes[lane_num].EvQ.getOccup()))
                    self.all_lanes[lane_num].EvQ.pushEvent(next_event)
                    self.upproc.incr_events()
                elif addr_mode == 5:  # write data from LM to different lane
                    lm_addr = self.rd_register(action.dst)  # data from Rw
                    if addr != -1:
                        lane_num = addr - 2  # dest lane num (Ra)
                    else:
                        lane_num = self.lane_id
                    size = int(action.size)
                    ev_operands = [None for i in range(int(size / 4))]
                    lm_addr = lm_addr + self.ds_base
                    for i in range(int(size / 4)):
                        ev_operands[i] = self.LM.read_word(lm_addr + 4 * i)
                        self.metric.cycle += 1
                        self.metric.exec_cycles += 1
                    self.all_lanes[lane_num].OpBuffer.setOp(0)

                    for val in ev_operands:
                        self.all_lanes[lane_num].OpBuffer.setOp(val)
                    event_label = event_word & 0x000000FF
                    next_event = Event(event_label, len(ev_operands))
                    next_event.setlanenum(lane_num)
                    next_event.setthreadid(0xFF)
                    next_event.set_cycle(self.metric.last_exec_cycle + 1 + (self.all_lanes[lane_num].EvQ.getOccup()))
                    self.all_lanes[lane_num].EvQ.pushEvent(next_event)
                    self.upproc.incr_events()
                elif addr_mode > 5:  # write data from LM to DRAM
                    ear_base = "EAR_" + str(addr_mode - 6)
                    dram_addr = self.address_generate_unit(ear_base, addr)
                    lm_addr = self.ds_base + self.rd_register(action.dst)
                    size = int(action.size)
                    write_operands = [None for i in range(int(size / 4))]
                    for i in range(int(size / 4)):
                        word = self.LM.read_word(lm_addr + 4 * i)
                        self.dram.write_word(dram_addr + 4 * i, word)
                        self.metric.cycle += 1
                        self.metric.exec_cycles += 1
                    event_label = event_word & 0x000000FF
                    next_event = Event(event_label, 0)
                    next_event.set_cycle(self.metric.last_exec_cycle + 1 + (self.EvQ.getOccup()) + dram_lat)
                    next_event.setlanenum(self.lane_id)
                    next_event.setthreadid(self.curr_thread.tid)
                    self.OpBuffer.setOp(0)
                    self.EvQ.pushEvent(next_event)
                    self.upproc.incr_events()
        else:
            size = int(action.size)
            data = self.rd_register(action.addr)
            self.top.sendResult(data)

    def do_send_top(self, action):
        # if dest == 1 and action.rw == 'w': #send message back to TOP
        size = int(action.size)
        # print("send to TOP from reg:%s" % action.addr)
        data = self.rd_register(action.addr)
        # print("send to TOP data:%d" % data)
        self.top.sendResult(data)

    def do_send_old_sim(self, action):
        """
        0 - Number of sends
        Decoding for send mmap
        offs+0 - Send_Mode 4 bits
           0 - Lane / Memory bound
           1 - With Return?
           2 - Load/Store (for memory bound transactions)
           3 - Old style Send (compatibility bit)
        offs+1 - event cycle as a clue for simulator
        offs+2 - event_word (destination event - only used for lane bound)
        offs+3 - dest lower addr (or Lane Number)
        offs+4 - dest higher addr (or lane Number / replicated)
        offs+5 - continuation_word
        offs+6 - Size in bytes
        off+7 - offs+n (n-6 datawords to be stored in case of store messages)
        """
        if action.dst != "TOP":
            self.send_mm.seek(0)
            self.num_sends += 1
            val = struct.pack("I", self.num_sends)
            self.send_mm.write(val)
            self.send_mm.seek(self.mm_offset)

            event_word = self.rd_register(action.event)
            dest = self.rd_register(action.dst)
            addr = self.rd_register(action.addr)
            addr_mode = int(action.addr_mode)
            cont_word = 0
            mode = 0
            next_event_word = 0x0
            # if self.lane_id == 2:
            #    pdb.set_trace()
            if dest == -1 or dest == 0xFFFFFFFF:
                lane_num = self.lane_id
            else:
                lane_num = dest - 2
            printd(
                "send_old, event_word:%d, dest:%d, addr:%d, addr_mode:%d, lane_num:%d" % (event_word, dest, addr, addr_mode, lane_num),
                stage_trace,
            )
            if (dest > 1 or dest == -1) and action.rw == "r":  # read message
                size = int(action.size)
                ev_operands = [None for i in range(int(size / 4))]
                event_label = event_word & 0x000000FF

                next_event = Event(event_label, len(ev_operands))
                next_event.set_cycle(self.metric.last_exec_cycle + 1)
                if addr_mode > 0:
                    # DRAM bound .. it's all about continuation
                    ear_base = "EAR_" + str(addr_mode - 1)
                    dram_addr = self.address_generate_unit(ear_base, addr)
                    next_event.setlanenum(lane_num)
                    if lane_num == self.lane_id:
                        next_event.setthreadid(self.curr_thread.tid)
                        mode = 10
                    else:
                        mode = 8
                    cont_word = next_event.event_word
                else:
                    # continuation bound for another lane (read from LM) // continuation is important here
                    next_event.setlanenum(lane_num)
                    next_event_word = next_event.event_word
                    mode = 1
                    addr = addr + self.ds_base
                    ev_operands[i] = self.LM.read_word(addr + 4 * i)
                    self.metric.cycle += 1
                    self.metric.exec_cycles += 1
                printd(
                    "send_old, mode:%d, exec_cycle:%d, next_event_word:%d,\
                     addr_mode:%d, dram_addr:%lx, lane_num:%d cont_word :%d, \
                     size:%d"
                    % (mode, self.metric.cycle, next_event_word, addr_mode, dram_addr, lane_num, cont_word, size),
                    stage_trace,
                )
                # printd("Offset:%d" % self.mm_offset)
                # pdb.set_trace()
                val = struct.pack("I", mode)
                self.send_mm.write(val)
                val = struct.pack("I", self.metric.cycle - self.metric.curr_event_scyc)
                # val=struct.pack('I', self.metric.cycle)
                self.send_mm.write(val)
                val = struct.pack("I", next_event_word)
                self.send_mm.write(val)
                if addr_mode > 0:
                    val = struct.pack("I", (dram_addr & 0xFFFFFFFF))  # lower int
                else:
                    val = struct.pack("I", lane_num)
                self.send_mm.write(val)
                if addr_mode > 0:
                    val = struct.pack("I", ((dram_addr >> 32) & 0xFFFFFFFF))  # upper int
                else:
                    val = struct.pack("I", lane_num)
                self.send_mm.write(val)
                val = struct.pack("I", cont_word)
                self.send_mm.write(val)
                val = struct.pack("I", size)
                self.send_mm.write(val)
                # if addr_mode > 0:
                #    for val in ev_operands:
                #        val=struct.pack('I', val)
                #        self.send_mm.write(val)
                self.mm_offset = self.send_mm.tell()

                # release lock for lane
            elif action.rw == "w":
                size = int(action.size)
                # ev_operands = [None for i in range(int(size/4))]
                ev_operands = []
                if addr_mode > 0 and addr_mode < 5:  # write data from Reg to DRAM
                    ear_base = "EAR_" + str(addr_mode - 1)
                    mode = 14  # 1110 Old store
                    dram_addr = self.address_generate_unit(ear_base, addr)
                    data = self.rd_register(action.dst)
                    ev_operands.append(data)
                    event_label = event_word & 0x000000FF
                    next_event = Event(event_label, 0)
                    next_event.setlanenum(self.lane_id)
                    next_event.set_cycle(self.metric.last_exec_cycle + 1)
                    cont_word = next_event.event_word
                    # print("Lane: %d W mode, 0<addr_mode<5: Increment Events: %d" % (self.lane_id, self.upproc.outstanding_events))
                elif addr_mode == 0:  # write data from Rw to different lane
                    # pdb.set_trace()
                    data = self.rd_register(action.dst)  # data from Rw
                    ev_operands.append(data)
                    mode = 1
                    if addr != -1 and addr != 0xFFFFFFFF:
                        lane_num = addr - 2  # dest lane num (Ra)
                    else:
                        lane_num = self.lane_id
                    # self.all_lanes[lane_num].OpBuffer.setOp(data)
                    event_label = event_word & 0x000000FF
                    if event_label == 1:
                        # it takes master 6 instructions to update the frontier
                        self.metric.frontier_edit_ins += 8
                    printd("send_old:Write:Lane_num:%d" % lane_num, stage_trace)
                    next_event = Event(event_label, 1)
                    next_event.setlanenum(lane_num)
                    if lane_num == self.lane_id:
                        next_event.setthreadid(self.curr_thread.tid)
                    next_event.set_cycle(self.metric.last_exec_cycle + 1)
                    next_event_word = next_event.event_word

                elif addr_mode == 5:  # write data from LM to different lane
                    lm_addr = self.rd_register(action.dst)  # data from Rw
                    mode = 1
                    if addr != -1 and addr != 0xFFFFFFFF:
                        lane_num = addr - 2  # dest lane num (Ra)
                    else:
                        lane_num = self.lane_id
                    lm_addr = lm_addr + self.ds_base
                    for i in range(int(size / 4)):
                        ev_operands.append(self.LM.read_word(lm_addr + 4 * i))
                        self.metric.cycle += 1
                        self.metric.exec_cycles += 1

                    event_label = event_word & 0x000000FF
                    next_event = Event(event_label, len(ev_operands))
                    next_event.setlanenum(lane_num)
                    next_event.set_cycle(self.metric.last_exec_cycle + 1)
                    next_event_word = next_event.event_word
                elif addr_mode > 5:  # write data from LM to DRAM
                    mode = 14
                    ear_base = "EAR_" + str(addr_mode - 6)
                    dram_addr = self.address_generate_unit(ear_base, addr)
                    lm_addr = self.ds_base + self.rd_register(action.dst)
                    for i in range(int(size / 4)):
                        ev_operands.append(self.LM.read_word(lm_addr + 4 * i))
                        self.metric.cycle += 1
                        self.metric.exec_cycles += 1
                    event_label = event_word & 0x000000FF
                    next_event = Event(event_label, 0)
                    next_event.set_cycle(self.metric.last_exec_cycle + 1)
                    next_event.setlanenum(self.lane_id)
                    cont_word = next_event.event_word
                val = struct.pack("I", mode)
                self.send_mm.write(val)
                val = struct.pack("I", self.metric.cycle - self.metric.curr_event_scyc)
                # val=struct.pack('I', self.metric.cycle)
                self.send_mm.write(val)
                val = struct.pack("I", next_event_word)
                self.send_mm.write(val)
                if addr_mode == 0 or addr_mode == 5:
                    val = struct.pack("I", lane_num)
                    self.send_mm.write(val)
                    val = struct.pack("I", lane_num)
                    self.send_mm.write(val)
                else:
                    val = struct.pack("I", (dram_addr & 0xFFFFFFFF))  # lower int
                    self.send_mm.write(val)
                    val = struct.pack("I", ((dram_addr >> 32) & 0xFFFFFFFF))  # upper int
                    self.send_mm.write(val)
                val = struct.pack("I", cont_word)
                self.send_mm.write(val)
                val = struct.pack("I", size)
                self.send_mm.write(val)
                for val in ev_operands:
                    val = struct.pack("I", val)
                    self.send_mm.write(val)
                self.mm_offset = self.send_mm.tell()
                printd("Done writing into map", stage_trace)

        else:
            size = int(action.size)
            data = self.rd_register(action.addr)
            self.top.sendResult(data)

    def send_basic(self, event, dest, cont, op1, op2, mode_0, mode_1, mode_2, s4, size=0):
        """
        Addr_Mode                 |  Description                                        | Pseudo Instr
        mode[0]| mode[1]| mode[2] |
        (dest) | (ret)  | (ld/st) |  Description                                        | Pseudo Instr
        4      | 0      | X       |  send_wcontinuation cases                           | send_wcont/send4_wcont
        4      | 1      | X       |  send_wret (leave out lane/TID)                     | send_wret/send4_wret
        0,1,2,3| 0      | 0       |  load data from stream ptr(DRAM) to diff lane       | send_dmlm_ld                  [mode[0] = 2,3,4,5]
        0,1,2,3| 1      | 0       |  load data from stream ptr(DRAM) to same lane       | send_dmlm_ld_wret             [mode[0] = 2,3,4,5]
        0,1,2,3| 0      | 1       |  store data at stream ptr, send ack to diff lane    | send_dmlm/send4_dmlm          [mode[0] = 2,3,4,5]
        0,1,2,3| 1      | 1       |  store data at stream ptr, send ack to same lane    | send_dmlm_wret/send4_dmlm_wret[mode[0] = 2,3,4,5]
        _ _ _ _ _
        cont | ld/st | ret | mode[0] | mode[0]

        """
        """
            Old incorrect
            4      | 0      | 1       |  send_wcontinuation cases                           | send_wcont_st                 // Not required since this can just be a store + tranfer of control (event with 0 operands)
            1      | X      | 0       |  load data from LM to different Lane                | send_dmlm_ld                  [mode[0] = 1] (covered with wcontinuation)
            1      | X      | 1       |  store data to LM, send ack to diff lane            | send_dmlm/send4_dmlm          [mode[0] = 1] (same as 4/0/1)

        """

        if self.upproc.perf_log_internal_enable:
            self.metric.write_perf_log(0, self.lane_id, self.curr_thread.tid,
                                       self.curr_event.event_base, self.curr_event.event_label,
                                       set([PerfLogPayload.UD_ACTION_STATS.value,
                                           PerfLogPayload.UD_TRANS_STATS.value, PerfLogPayload.UD_QUEUE_STATS.value,
                                           PerfLogPayload.UD_LOCAL_MEM_STATS.value, PerfLogPayload.UD_MEM_INTF_STATS.value]))

        # cont = self.rd_register(cont)
        if self.sim:
            self.send_mm.seek(0)
            self.num_sends += 1
            val = struct.pack("I", self.num_sends)
            self.send_mm.write(val)
            self.send_mm.seek(self.mm_offset)

        printd("Send_basic Modes:Mode_0:%d, Mode_1:%d, Mode_2:%d" % (mode_0, mode_1, mode_2), stage_trace)
        printd(
            "Send_basic Operands: Event:%x, Dest:%d, Cont:%s, Op1:%s, Op2:%s, s4:%d"
            % (event if event is not None else 0, dest, str(cont), op1, op2, s4),
            stage_trace,
        )
        # print("Send_basic Operands: Event:%x, Dest:%d, Cont:%s, Op1:%s, Op2:%s, s4:%d" % (event if event is not None else 0, dest, str(cont), op1, op2, s4))
        # pdb.set_trace()
        if mode_1 == 1:
            # send with return
            cont = (int(cont) & 0x0000FFFF) | ((self.lane_id << 24) & 0xFF000000) | ((self.curr_thread.tid << 16) & 0x00FF0000)

        next_event = None
        ev_operands = []
        if mode_0 == 4:
            # Inter lane communication mainly
            # event_word = ((int(self.lane_num) << 24) & 0xff000000) | ((int(self.thread_id) << 16) & 0x00ff0000) | ((int(self.event_base) << 8) & 0x0000ff00) | (int(self.event_label) & 0x000000ff)
            event_label = event & 0x000000FF
            event_tid = (event & 0x00FF0000) >> 16
            lane_num = dest
            if event_label == 1:
                # it takes master 6 instructions to update the frontier
                self.metric.frontier_edit_ins += 8
            if not self.sim:
                self.all_lanes[lane_num].OpBuffer.setOp(cont)
            if s4:
                data1 = self.rd_register(op1)
                if not self.sim:
                    self.all_lanes[lane_num].OpBuffer.setOp(data1)
                else:
                    ev_operands.append(data1)
                if size > 1:
                    data2 = self.rd_register(op2)
                    if not self.sim:
                        self.all_lanes[lane_num].OpBuffer.setOp(data2)
                    else:
                        ev_operands.append(data2)
                    next_event = Event(event_label, 2)
                else:
                    next_event = Event(event_label, 1)
                size = len(ev_operands) * 4
                next_event.setlanenum(lane_num)
                next_event.setthreadid(event_tid)
                if not self.sim:
                    next_event.set_cycle(self.metric.last_exec_cycle + 1 + (self.all_lanes[lane_num].EvQ.getOccup()))
                    self.all_lanes[lane_num].EvQ.pushEvent(next_event)
                    self.upproc.incr_events()
            else:
                if op1 != "UDPR_X":
                    lm_addr = self.ds_base + self.rd_register(op1)  # data from Rw
                size = int(op2)
                # ev_operands = [None for i in range(int(size/4))]
                # if self.mode == 'R':
                #    lm_addr = lm_addr+self.ds_base
                for i in range(int(size / 4)):
                    ev_operands.append(self.LM.read_word(lm_addr + 4 * i))
                    self.metric.cycle += 1
                    self.metric.exec_cycles += 1
                if not self.sim:
                    for val in ev_operands:
                        self.all_lanes[lane_num].OpBuffer.setOp(val)
                next_event = Event(event_label, int(size / 4))
                next_event.setlanenum(lane_num)
                next_event.setthreadid(event_tid)
                if not self.sim:
                    next_event.set_cycle(self.metric.last_exec_cycle + 1 + (self.all_lanes[lane_num].EvQ.getOccup()))
                    self.all_lanes[lane_num].EvQ.pushEvent(next_event)
                    self.upproc.incr_events()
            if self.sim:
                mode = ((((mode_2 & 0x1) << 2) & 0x4) | (((mode_1 & 0x1) << 1) & 0x2) | (((mode_0 & 0x4) >> 2) & 0x1)) & 0x7
                printd(
                    "send_basic, mode:%d, exec_cycle:%d, next_event_word:%d,\
                lane_num:%d cont_word :%d, \
                size:%d"
                    % (mode, self.metric.cycle-self.metric.curr_event_scyc, next_event.event_word, lane_num, cont, size),
                    stage_trace,
                )
                val = struct.pack("I", mode)
                self.send_mm.write(val)
                val = struct.pack("I", self.metric.cycle - self.metric.curr_event_scyc)
                # val=struct.pack('I', self.metric.cycle)
                self.send_mm.write(val)
                next_event_word = next_event.event_word
                val = struct.pack("I", next_event_word)
                self.send_mm.write(val)
                val = struct.pack("I", lane_num)
                self.send_mm.write(val)
                val = struct.pack("I", lane_num)
                self.send_mm.write(val)
                val = struct.pack("I", cont)
                self.send_mm.write(val)
                val = struct.pack("I", size)
                self.send_mm.write(val)
                for value in ev_operands:
                    val = struct.pack("I", value & 0xFFFFFFFF)
                    self.send_mm.write(val)
                self.mm_offset = self.send_mm.tell()

        elif mode_0 < 4:
            # Target is global Address (LM or DRAM)
            ear_base = "EAR_" + str(mode_0)
            event_label = cont & 0x000000FF
            event_tid = (cont & 0x00FF0000) >> 16
            lane_num = (cont & 0xFF000000) >> 24
            gaddr = dest
            dram_addr = self.address_generate_unit(ear_base, gaddr)
            if mode_2 == 0:
                size = 0
                # Load cases
                size = int(op2)
                if not self.sim:
                    self.all_lanes[lane_num].OpBuffer.setOp(cont)
                    # ev_operands = [None for i in range(int(size/4))]
                    for i in range(int(size / 4)):
                        ev_operands.append(self.dram.read_word(dram_addr + 4 * i))
                        # print("lane %s do_send r - ori_lane: %s, action.dst: %s, dst.laneid: %s, dram_addr: %s, ear_base: %s, addr: %s(%s), size: %s, mode: %d, event: %s(%s, %s)"
                        #         % (self.lane_id, ori_lane, dest, lane_num, ear_base, dram_addr, action.addr, addr, size, addr_mode, action.event, ori_lane, event_label))
                        self.metric.up_dram_read_bytes += 4
                    for val in ev_operands:
                        self.all_lanes[lane_num].OpBuffer.setOp(val)
                # next_event = Event(event_label, len(ev_operands))
                next_event = Event(event_label, int(size / 4))
                next_event.setlanenum(lane_num)
                next_event.setthreadid(event_tid)
                if not self.sim:
                    next_event.set_cycle(self.metric.last_exec_cycle + 1 + (self.all_lanes[lane_num].EvQ.getOccup()))
                    self.all_lanes[lane_num].EvQ.pushEvent(next_event)
                    self.upproc.incr_events()
            elif mode_2 == 1:
                # Store cases
                if not self.sim:
                    self.all_lanes[lane_num].OpBuffer.setOp(cont)
                dram_addr = self.address_generate_unit(ear_base, gaddr)
                if s4:
                    data1 = self.rd_register(op1)
                    if not self.sim:
                        self.dram.write_word(dram_addr, data1)
                        self.metric.up_write_read_bytes += 4
                    else:
                        ev_operands.append(data1)
                    if size > 1:
                        data2 = self.rd_register(op2)
                        if not self.sim:
                            self.dram.write_word(dram_addr, data2)
                            self.metric.up_write_read_bytes += 4
                        else:
                            ev_operands.append(data2)

                else:
                    size = int(op2)
                    # ev_operands = [None for i in range(int(size/4))]
                    lm_addr = self.ds_base + self.rd_register(op1)  # data from Rw
                    for i in range(int(size / 4)):
                        ev_operands.append(self.LM.read_word(lm_addr + 4 * i))
                        self.metric.cycle += 1
                        self.metric.exec_cycles += 1
                    if not self.sim:
                        for val in ev_operands:
                            self.dram.write_word(dram_addr, val)
                            self.metric.up_write_read_bytes += 4
                next_event = Event(event_label, 0)
                next_event.setlanenum(lane_num)
                next_event.setthreadid(event_tid)
                if not self.sim:
                    next_event.set_cycle(self.metric.last_exec_cycle + 1 + (self.all_lanes[lane_num].EvQ.getOccup()))
                    self.all_lanes[lane_num].EvQ.pushEvent(next_event)
                    self.upproc.incr_events()
            # pdb.set_trace()
            mode = ((((mode_2 & 0x1) << 2) & 0x4) | (((mode_1 & 0x1) << 1) & 0x2) | (((mode_0 & 0x4) >> 2) & 0x1)) & 0x7
            next_event_word = next_event.event_word
            printd(
                "send_basic, mode:%d, exec_cycle:%d, next_event_word:%d,\
                 dram_addr:%lx, lane_num:%d cont_word :%d, \
                 size:%d"
                % (mode, self.metric.cycle-self.metric.curr_event_scyc, next_event_word, dram_addr, lane_num, cont, size),
                stage_trace,
            )
            if self.sim:
                mode = ((((mode_2 & 0x1) << 2) & 0x4) | (((mode_1 & 0x1) << 1) & 0x2) | (((mode_0 & 0x4) >> 2) & 0x1)) & 0x7
                val = struct.pack("I", mode)
                self.send_mm.write(val)
                val = struct.pack("I", self.metric.cycle - self.metric.curr_event_scyc)
                # val=struct.pack('I', self.metric.cycle)
                self.send_mm.write(val)
                next_event_word = next_event.event_word
                val = struct.pack("I", next_event_word)
                self.send_mm.write(val)
                val = struct.pack("I", (dram_addr & 0xFFFFFFFF))  # lower int
                self.send_mm.write(val)
                val = struct.pack("I", ((dram_addr >> 32) & 0xFFFFFFFF))  # upper int
                self.send_mm.write(val)
                val = struct.pack("I", cont)
                self.send_mm.write(val)
                val = struct.pack("I", size)
                self.send_mm.write(val)
                for value in ev_operands:
                    val = struct.pack("I", value & 0xFFFFFFFF)
                    self.send_mm.write(val)
                self.mm_offset = self.send_mm.tell()

        printd(
            "Send_Basic: Lane_num:%d, EvQ.size:%d, totalevents:%d"
            % (lane_num, self.all_lanes[lane_num].EvQ.getOccup(), self.upproc.outstanding_events),
            stage_trace,
        )
        next_event.printOut(stage_trace)

    def do_send4(self, action):
        event_word = self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = self.rd_register(action.cont)
        addr_mode = int(action.addr_mode)
        printd("send4: ev:%x dest:%x, cont:%x, addr_mode:%d" % (event_word, dest, cont, addr_mode), stage_trace)
        """ Addr Modes
            Possible destinations
            Lane , DRAM, LM
            For Lane - Device ID
            DRAM, LM - Global Address
            Addr Mode - to distinguish between these
            Device ID - 0 - 63 lanes - Mode 0 (Device IDs beyond this on different UpStream Nodes potentially or other networked devices)
            LM - Mode 1
            DRAM - Mode 2, 3, 4, 5 [4 potential stream pointers]
        """
        mode_0 = addr_mode & 0x7
        mode_1 = (addr_mode & 0x8) >> 3
        mode_2 = (addr_mode & 0x10) >> 4
        if action.op2 != "EMPTY":
            size = 2
        else:
            size = 1

        # mode_0 = ( 4 if (high_bit == 1) else mode_0) #, mode_1, mode_2)
        # Set s4 = 1
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 1, size)

    def do_send(self, action):
        event_word = self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = self.rd_register(action.cont)
        addr_mode = int(action.addr_mode)
        mode_0 = addr_mode & 0x7
        mode_1 = (addr_mode & 0x8) >> 3
        mode_2 = (addr_mode & 0x10) >> 4
        # Set s4 = 0
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 0)

    def do_send4_wret(self, action):
        event_word = self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = action.cont
        # addr_mode = int(action.addr_mode)
        high_bit = 1  # (addr_mode & 0x10) >> 4
        mode_0 = 4
        mode_1 = 1
        mode_2 = 0
        if action.op2 != "EMPTY":
            size = 2
        else:
            size = 1
        # Set s4 =1
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 1, size)

    def do_send_wret(self, action):
        event_word = self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = action.cont
        high_bit = 1  # (addr_mode & 0x10) >> 4
        mode_0 = 4
        mode_1 = 1
        mode_2 = 0
        # Set s4 = 0
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 0)

    def do_send4_wcont(self, action):
        event_word = self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = self.rd_register(action.cont)
        # addr_mode = int(action.addr_mode)
        high_bit = 1  # (addr_mode & 0x10) >> 4
        mode_0 = 4
        mode_1 = 0
        mode_2 = 0
        if action.op2 != "EMPTY":
            size = 2
        else:
            size = 1
        # Set s4 = 1
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 1, size)

    def do_send_wcont(self, action):
        event_word = self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = self.rd_register(action.cont)
        # addr_mode = int(action.addr_mode)
        high_bit = 1  # (addr_mode & 0x10) >> 4
        mode_0 = 4
        mode_1 = 0
        mode_2 = 0
        # Set s4 = 1
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 0)

    def do_send4_dmlm(self, action):
        # event_word = self.rd_register(action.event)
        event_word = None
        dest = self.rd_register(action.dst)
        cont = self.rd_register(action.cont)
        addr_mode = int(action.addr_mode)
        high_bit = 0  # (addr_mode & 0x10) >> 4
        mode_0 = addr_mode & 0x3
        mode_1 = 0
        mode_2 = 1
        if action.op2 != "EMPTY":
            size = 2
        else:
            size = 1
        # Set s4 = 1
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 1, size)

    def do_send_dmlm(self, action):
        # event_word = self.rd_register(action.event)
        event_word = None
        dest = self.rd_register(action.dst)
        cont = self.rd_register(action.cont)
        addr_mode = int(action.addr_mode)
        high_bit = 0  # (addr_mode & 0x10) >> 4
        mode_0 = addr_mode & 0x3
        mode_1 = 0
        mode_2 = 1
        # Set s4 = 1
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 0)

    def do_send4_dmlm_wret(self, action):
        # event_word = self.rd_register(action.event)
        event_word = None
        dest = self.rd_register(action.dst)
        cont = action.cont
        addr_mode = int(action.addr_mode)
        high_bit = 0  # (addr_mode & 0x10) >> 4
        mode_0 = addr_mode & 0x3
        mode_1 = 1
        mode_2 = 1
        if action.op2 == "EMPTY":
            size = 1
        else:
            size = 2
        # Set s4 = 1
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 1, size)

    def do_send_dmlm_wret(self, action):
        event_word = None
        # event_word = self.rd_register(action.event)
        dest = self.rd_register(action.dst)
        cont = action.cont
        addr_mode = int(action.addr_mode)
        high_bit = 0  # (addr_mode & 0x10) >> 4
        mode_0 = addr_mode & 0x3
        mode_1 = 1
        mode_2 = 1
        # Set s4 = 1
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 0)

    def do_send_dmlm_ld_wret(self, action):
        # event_word = self.rd_register(action.event)
        event_word = None
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = action.cont
        size = int(action.op2)
        addr_mode = int(action.addr_mode)
        high_bit = 0  # (addr_mode & 0x10) >> 4
        mode_0 = addr_mode & 0x3
        mode_1 = 1
        mode_2 = 0
        # Set s4 = 1
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 0)

    def do_send_dmlm_ld(self, action):
        # event_word = self.rd_register(action.event)
        event_word = None  # self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = self.rd_register(action.cont)
        addr_mode = int(action.addr_mode)
        high_bit = 0  # (addr_mode & 0x10) >> 4
        mode_0 = addr_mode & 0x3
        mode_1 = 0
        mode_2 = 0
        # mode = ( 4 if (high_bit == 1) else mode_0, mode_1, mode_2)
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 0)

    def do_send4_reply(self, action):
        # printd("EventQ before send:%d" % self.EvQ.getOccup(), progress_trace)
        dest = (((self.curr_thread.thread_state) & 0xFF000000) >> 24) & 0xFF
        cont = 0
        high_bit = 1
        mode_0 = 4
        mode_1 = 0
        mode_2 = 0
        event_word = self.curr_thread.thread_state
        if action.op2 != "EMPTY":
            size = 2
        else:
            size = 1
        printd("Thread State : %x" % event_word, stage_trace)
        # event_word = ((event_word & 0xff00ff00) | (int(action.event) & 0xff)) | (((event_word & 0x0000ff00) << 8) & 0x00ff0000) # swizzle the thread ID to right position
        event_word = ((event_word & 0xFF00FF00) | (event_word & 0xFF)) | (((event_word & 0x0000FF00) << 8) & 0x00FF0000)  # swizzle the thread ID to right position
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 1, size)

    def do_send_reply(self, action):
        # printd("EventQ before send:%d" % self.EvQ.getOccup(), progress_trace)
        dest = (((self.curr_thread.thread_state) & 0xFF000000) >> 24) & 0xFF
        cont = 0
        high_bit = 1
        mode_0 = 4
        mode_1 = 0
        mode_2 = 0
        event_word = self.curr_thread.thread_state
        printd("Thread State : %x" % event_word, stage_trace)
        # event_word = ((event_word & 0xff00ff00) | (int(action.event) & 0xff)) | (((event_word & 0x0000ff00) << 8) & 0x00ff0000) # swizzle the thread ID to right position
        event_word = ((event_word & 0xFF00FF00) | (event_word & 0xFF)) | (
            ((event_word & 0x0000FF00) << 8) & 0x00FF0000
        )  # swizzle the thread ID to right position
        self.send_basic(event_word, dest, cont, action.op1, action.op2, mode_0, mode_1, mode_2, 0)

    def do_send_any_wcont(self, action):
        event_word = self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = self.rd_register(action.cont)
        op1 = self.rd_register(action.op1)
        # addr_mode = int(action.addr_mode)
        high_bit = 1  # (addr_mode & 0x10) >> 4
        mode_0 = 4
        mode_1 = 0
        mode_2 = 0
        reglist = action.reglist
        size = len(reglist)
        # move all registers from reg to LM and then use datatptr len with regular interface
        pact1 = Paction()
        pact2 = Paction()
        pact1.imm = 4
        pact1.dst = action.op1
        pact2.imm = 4
        pact2.src = action.op1
        pact2.dst = action.op1
        for i in range(size):
            pact1.src = reglist[i]
            self.do_mov_reg2lm(pact1)
            self.do_add_immediate(pact2)
        pact2.dst = action.op1
        pact2.imm = op1
        self.do_mov_imm2reg(pact2)
        op2 = size * 4
        self.send_basic(event_word, dest, cont, action.op1, op2, mode_0, mode_1, mode_2, 0)

    def do_send_any(self, action):
        event_word = self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = 0  # self.rd_register(action.cont)
        op1 = "UDPR_X"  # self.rd_register(action.op1)
        # addr_mode = int(action.addr_mode)
        high_bit = 1  # (addr_mode & 0x10) >> 4
        mode_0 = 4
        mode_1 = 0
        mode_2 = 0
        reglist = action.reglist
        size = len(reglist)
        # move all registers from reg to LM and then use datatptr len with regular interface
        op2 = size * 4
        self.send_basic(event_word, dest, cont, op1, op2, mode_0, mode_1, mode_2, 0)

    def do_send_any(self, action):
        event_word = self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = 0  # self.rd_register(action.cont)
        op1 = "UDPR_X"  # self.rd_register(action.op1)
        # addr_mode = int(action.addr_mode)
        high_bit = 1  # (addr_mode & 0x10) >> 4
        mode_0 = 4
        mode_1 = 0
        mode_2 = 0
        reglist = action.reglist
        size = len(reglist)
        # move all registers from reg to LM and then use datatptr len with regular interface
        op2 = size * 4
        self.send_basic(event_word, dest, cont, op1, op2, mode_0, mode_1, mode_2, 0)

    def do_send_any_wret(self, action):
        event_word = self.rd_register(action.event)
        # event_word = action.event
        dest = self.rd_register(action.dst)
        cont = action.cont
        op1 = self.rd_register(action.op1)
        # addr_mode = int(action.addr_mode)
        high_bit = 1  # (addr_mode & 0x10) >> 4
        mode_0 = 4
        mode_1 = 1
        mode_2 = 0
        reglist = action.reglist
        size = len(reglist)
        pact1 = Paction()
        pact2 = Paction()
        pact1.imm = 4
        pact1.dst = action.op1
        pact2.imm = 4
        pact2.src = action.op1
        pact2.dst = action.op1
        for i in range(size):
            pact1.src = reglist[i]
            self.do_mov_reg2lm(pact1)
            self.do_add_immediate(pact2)
        pact2.dst = action.op1
        pact2.imm = op1
        self.do_mov_imm2reg(pact2)
        op2 = size * 4
        self.send_basic(event_word, dest, cont, action.op1, op2, mode_0, mode_1, mode_2, 0)

    def do_yield(self, action):
        # Potential Clean up code
        yield_exec = 1
        self.metric.ops_removed += self.curr_event.numOps()
        printd("Clearing %d Operands on Yield" % (self.curr_event.numOps()), stage_trace)
        self.OpBuffer.clearOp(self.curr_event.numOps())
        self.curr_thread.ear = self.ear
        ins_per_event = self.metric.total_acts - self.curr_event_sins
        cyc_per_event = self.metric.cycle - self.metric.curr_event_scyc

        if ins_per_event in self.metric.ins_per_event:
            self.metric.ins_per_event[ins_per_event] += 1
        else:
            self.metric.ins_per_event[ins_per_event] = 1
        if cyc_per_event in self.metric.cycles_per_event:
            self.metric.cycles_per_event[cyc_per_event] += 1
        else:
            self.metric.cycles_per_event[cyc_per_event] = 1
        if self.curr_event.event_label == 0:
            ins_per_fetch = self.metric.total_acts - self.fetch_event_sins
            if ins_per_fetch in self.metric.ins_per_fetch:
                self.metric.ins_per_fetch[ins_per_fetch] += 1
            else:
                self.metric.ins_per_fetch[ins_per_fetch] = 1
        else:
            ins_per_match = self.metric.total_acts - self.match_event_sins
            if ins_per_match in self.metric.ins_per_match:
                self.metric.ins_per_match[ins_per_match] += 1
            else:
                self.metric.ins_per_match[ins_per_match] = 1

        if self.upproc.perf_log_internal_enable:
            self.metric.write_perf_log(0, self.lane_id, self.curr_thread.tid,
                                       self.curr_event.event_base, self.curr_event.event_label,
                                       set([PerfLogPayload.UD_ACTION_STATS.value,
                                           PerfLogPayload.UD_TRANS_STATS.value, PerfLogPayload.UD_QUEUE_STATS.value,
                                           PerfLogPayload.UD_LOCAL_MEM_STATS.value, PerfLogPayload.UD_MEM_INTF_STATS.value]))

        return yield_exec

    def do_yield_operand(self, action):
        # Potential Clean up code
        self.metric.ops_removed += self.curr_event.numOps()
        printd("Clearing %d Operands on Yield" % (self.curr_event.numOps()), stage_trace)
        self.OpBuffer.clearOp(self.curr_event.numOps())
        self.curr_thread.ear = self.ear

    def do_yield_terminate(self, action):
        # Potential Clean up code
        yield_exec = 1
        yield_term = 1
        self.metric.ops_removed += self.curr_event.numOps()
        printd("Clearing %d Operands on terminate" % (self.curr_event.numOps()), stage_trace)
        self.OpBuffer.clearOp(self.curr_event.numOps())
        # Clear UDPR and threadstate and udpallocs
        self.udpthreadallocs = [x for x in self.udpthreadallocs if x[2] != self.curr_thread.tid]
        self.tstable.remThreadfromTST(self.curr_thread.tid)
        # print("Yield_Terminate:%d" % yield_term)
        # print("TriangleCount Check: UDPR_3:%d" % self.rd_register("UDPR_3"))
        ins_per_event = self.metric.total_acts - self.curr_event_sins
        cyc_per_event = self.metric.cycle - self.metric.curr_event_scyc
        if ins_per_event in self.metric.ins_per_event:
            self.metric.ins_per_event[ins_per_event] += 1
        else:
            self.metric.ins_per_event[ins_per_event] = 1
        if cyc_per_event in self.metric.cycles_per_event:
            self.metric.cycles_per_event[cyc_per_event] += 1
        else:
            self.metric.cycles_per_event[cyc_per_event] = 1
        if self.curr_event.event_label == 0:
            ins_per_fetch = self.metric.total_acts - self.fetch_event_sins
            if ins_per_fetch in self.metric.ins_per_fetch:
                self.metric.ins_per_fetch[ins_per_fetch] += 1
            else:
                self.metric.ins_per_fetch[ins_per_fetch] = 1
        else:
            ins_per_match = self.metric.total_acts - self.match_event_sins
            if ins_per_match in self.metric.ins_per_match:
                self.metric.ins_per_match[ins_per_match] += 1
            else:
                self.metric.ins_per_match[ins_per_match] = 1

        if self.upproc.perf_log_internal_enable:
            self.metric.write_perf_log(0, self.lane_id, self.curr_thread.tid,
                                       self.curr_event.event_base, self.curr_event.event_label,
                                       set([PerfLogPayload.UD_ACTION_STATS.value,
                                           PerfLogPayload.UD_TRANS_STATS.value, PerfLogPayload.UD_QUEUE_STATS.value,
                                           PerfLogPayload.UD_LOCAL_MEM_STATS.value, PerfLogPayload.UD_MEM_INTF_STATS.value]))

        return yield_exec, yield_term

    def do_print(self, action):
        fmstr = action.fmtstr
        fmtp = fmstr.split("%")
        numfmt = len(fmtp) - 1
        reglist = action.reglist
        regval = []
        for reg in reglist:
            regval.append(self.rd_register(reg))
        print(fmstr % (tuple(regval)), flush=True)

    def do_perflog(self, action):
        if not self.metric.perf_log_enable:
            return
        if action.mode == 0:
            self.metric.write_perf_log(0, self.lane_id, self.curr_thread.tid,
                                       self.curr_event.event_base, self.curr_event.event_label,
                                       set(action.payload_list))
        elif action.mode == 1:
            msg_reglist = []
            for reg in action.reglist:
                msg_reglist.append((reg, self.rd_register(reg)))
            self.metric.write_perf_log(0, self.lane_id, self.curr_thread.tid,
                                       self.curr_event.event_base, self.curr_event.event_label,
                                       set(), action.msg_id, action.fmtstr, msg_reglist)
        elif action.mode == 2:
            msg_reglist = []
            for reg in action.reglist:
                msg_reglist.append((reg, self.rd_register(reg)))
            self.metric.write_perf_log(0, self.lane_id, self.curr_thread.tid,
                                       self.curr_event.event_base, self.curr_event.event_label,
                                       set(action.payload_list), action.msg_id, action.fmtstr, msg_reglist)

    def do_user_ctr(self, action):
        if action.mode == 0:
            # increment mode
            self.metric.user_counters[action.ctr_num] += action.arg
        if action.mode == 1:
            # set abs mode
            self.metric.user_counters[action.ctr_num] = action.arg

    def do_fp_add(self, action):
        src = self.rd_register(action.src)
        rt = self.rd_register(action.rt)
        # print("Lane %s do_fp_add - src: %s(%f), rt: %s(%f), dst: %s" % (self.lane_id, action.src, self.rd_register(action.src), action.rt, self.rd_register(action.rt), action.dst))
        res = src + rt
        # res = round(res * (1<<10))
        printd(
            "Lane %s do_fp_add - src: %s(%d), rt: %s(%d), dst: %s(%d)" % (self.lane_id, action.src, src, action.rt, rt, action.dst, res),
            stage_trace,
        )
        self.wr_register(action.dst, res)

    def do_fp_div(self, action):
        src = (self.rd_register(action.src) + 0.0) / (1 << 20)
        rt = self.rd_register(action.rt)
        res = src / rt
        # print("Lane %s do_fp_div - src: %s(%f), rt: %s(%d), dst: %s(%f)" % (self.lane_id, action.src, src, action.rt, self.rd_register(action.rt), action.dst, res))
        res = round(res * (1 << 20))
        printd(
            "Lane %s do_fp_div - src: %s(%d), rt: %s(%s), dst: %s(%d)"
            % (self.lane_id, action.src, self.rd_register(action.src), action.rt, rt, action.dst, res),
            stage_trace,
        )
        self.wr_register(action.dst, res)

import binascii
import bisect
import math
import mmap
import os
import pdb
import struct
import threading
import time

from bitstring import BitArray
from numpy import *

import EfaUtil as efa_util
from EFA import *
from MachineCode import *

# ====== select  printing level ======
# efa_util.printLevel(stage_trace)
# ====== Constant Value ======


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
    # def __init__(self, perf_file, lane_id):
    def __init__(self, lane_id):
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
        self.tran_bins = dict()
        self.tran_cycle = dict()
        self.base_cycle = 0
        self.tran_label = dict()
        self.ins_per_event = dict()
        self.cycles_per_event = dict()
        self.ins_per_fetch = dict()
        self.ins_per_match = dict()
        self.op_buff_util = []
        # self.perf_file = perf_file
        self.lane_id = lane_id
        # open(self.perf_file, 'w').close()

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

    # def printstats(self):
    #    print("Writing File %s" % self.perf_file)
    #    with open(self.perf_file, "a+") as f:
    #        f.write("Lane:%d\n" % self.lane_id)
    #        f.write("Cycles:%d\n" % self.cycle)
    #        f.write("NumEvents:%d\n" % self.num_events)
    #        f.write("Message Actions:%d\n" % self.msg_ins)
    #        f.write("Move Actions:%d\n" % self.mov_ins)
    #        f.write("ALU Actions:%d\n" % self.al_ins)
    #        f.write("Branch Actions:%d\n" % self.branch_ins)
    #        f.write("Operand Actions:%d\n" % self.op_ins)
    #        f.write("Event Actions:%d\n" % self.op_ins)
    #        f.write("Compare Actions:%d\n" % self.op_ins)
    #        f.write("Goto Actions:%d\n" % self.op_ins)
    #        f.write("Yield Actions:%d\n" % self.yld_ins)
    #        f.write("NumofProbes:%d\n" % self.probes)
    #        f.write("NumOperandsRemoved:%d\n" % self.ops_removed)
    #        f.write("NumOfActions:%d\n" % self.total_acts)
    #        f.write("NumOfTransitions:%d\n" % self.total_trans)
    #        f.write("UpLMReadBytes:%d\n" % self.up_lm_read_bytes)
    #        f.write("UpLMWriteBytes:%d\n" % self.up_lm_write_bytes)
    #        f.write("UpDRAMReadBytes:%d\n" % self.up_dram_read_bytes)
    #        f.write("UpDRAMWriteBytes:%d\n" % self.up_dram_write_bytes)
    #        f.write("Histograms\n")
    #        f.write("ActionsPerEvent:")
    #        for key in sorted(self.ins_per_event):
    #            f.write(str(key) + ":" + str(self.ins_per_event[key]) + ",")
    #        f.write("\nCyclesPerEvent:")
    #        for key in sorted(self.cycles_per_event):
    #            f.write(str(key) + ":" + str(self.cycles_per_event[key]) + ",")
    #        f.write("ActionsperFetchEvent:")
    #        for key in sorted(self.ins_per_fetch):
    #            f.write(str(key) + ":" + str(self.ins_per_fetch[key]) + ",")
    #        f.write("ActionsperMatchEvent:")
    #        for key in sorted(self.ins_per_match):
    #            f.write(str(key) + ":" + str(self.ins_per_match[key]) + ",")
    #        f.write("\n")
    #        f.close()


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
    def __init__(self, buffSize):
        self.size = buffSize
        self.events = []
        # for i in range(self.size):
        #    self.events.append(None)
        self.top = 0
        self.bottom = 0

    def isEmpty(self):
        return len(self.events) == 0
        # return self.top == self.bottom

    def isFull(self):
        return ((self.top - self.bottom) == 1) or ((self.bottom == self.size - 1) and (self.top == 0))

    def pushEvent(self, event):
        # self.events[self.bottom]=event
        # self.bottom=(self.bottom+1) % self.size
        self.events.append(event)

    def popEvent(self):
        # event = self.events[self.top]
        # self.top = (self.top+1) % self.size
        return self.events.pop(0)

    def getOccup(self):
        return len(self.events)
        # return (self.bottom - self.top)%self.size


class OpBuffer:
    def __init__(self, buffSize):
        # self.size = buffSize
        self.operands = []
        self.operands_inuse = []
        self.base = 0
        self.last = 0

    def getOp(self, index):
        # printd("RD_OBBUFER:base:%d, index:%d" % (self.base, index), progress_trace)
        # return self.operands[self.base+index]
        return self.operands[index]

    def setOp(self, value):
        self.operands.append(value)

    def clearOp(self, size):
        # self.operands_inuse[self.base+index]=0
        for i in range(int(size)):
            if len(self.operands) > 0:
                rem = self.operands.pop(0)
                # print("Remove:%d" % rem)
            else:
                return

    def isAvail(self, size):  ## This has potential for different policies
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
    count = 0

    def __init__(self):
        tid = Thread.count
        Thread.count += 1
        return tid


class ThreadStateTable:
    def __init__(self, size):
        self.numthreads = size
        self.threads = []


# ======  UDP Lane Logical Architecture Class ======
class VirtualEngine:
    # def __init__(self, lane_id, numOfGpr, numOfOpBuffer, numOfEvQ, dram_mem, top, perf_file):
    def __init__(self, lane_id, numOfGpr, perf_file):
        self.clearStore(numOfGpr)
        self.OpBuffer = OpBuffer(100)
        self.EvQ = EventQueue(100)
        self.curr_event = None
        self.curr_event_scyc = None
        self.curr_event_sins = None
        self.fetch_event_sins = None
        self.match_event_sins = None
        # self.dram = dram_mem
        # self.top = top
        self.metric = Metric(lane_id)
        # self.metric = Metric(perf_file, lane_id)
        self.program = None
        self.OBbase = 0
        self.ttable = ThreadStateTable(4)
        self.lane_id = lane_id
        self.event_obj = threading.Event()
        # self.send_obj = threading.Event()
        self.pname = "./simdata/lane" + str(self.lane_id) + "_send.txt"
        self.send_mm = None
        self.mm_offset = 0
        self.num_sends = 0
        self.current_states = []
        self.actcount = 0
        with open(self.pname, "w+b") as fd:
            for _ in range(4096):
                val = struct.pack("i", 0)
                fd.write(val)
        fd.close()
        with open(self.pname, "r+b") as fd:
            self.send_mm = mmap.mmap(fd.fileno(), 8192, access=mmap.ACCESS_WRITE, offset=0)
            self.send_mm.seek(0)
            self.mm_offset = self.send_mm.tell() + 4

    def clearStore(self, numOfGpr):
        self.UDPR = [0 for i in range(numOfGpr)]
        self.in_stream = BitArray("")
        self.out_stream = BitArray("")
        self.ear = [0 for i in range(4)]
        self.SBP = 0
        self.CR_Issue = 32
        self.CR_Advance = 8
        # ====== 1MB scrathpad data store, big endian low_addr-->|MSB, LSB|-->high_addr======
        self.DataStore = [0x0] * 1024 * 256

    def initDataStore(self, value):
        for i in range(len(self.DataStore)):
            self.DataStore[i] = value

    def getMode(self):
        return self.mode

    def setMode(self, mode):
        self.mode = mode

    def test(self):
        print("Lane:%d" % self.lane_id)

    def read_word(self, byte_addr):
        wd_data = self.DataStore[byte_addr >> 2]
        wd_next_data = self.DataStore[(byte_addr >> 2) + 1]
        self.metric.up_lm_read_bytes += 4
        if byte_addr % 4 == 0:
            self.metric.cycle += 1
            return wd_data
        if byte_addr % 4 == 1:
            self.metric.cycle += 2
            return (wd_data & 0x00FFFFFF) << 8 | (wd_next_data & 0xFF000000) >> 24
        if byte_addr % 4 == 2:
            self.metric.cycle += 2
            return (wd_data & 0x0000FFFF) << 16 | (wd_next_data & 0xFFFF0000) >> 16
        else:
            self.metric.cycle += 2
            return (wd_data & 0x000000FF) << 24 | (wd_next_data & 0xFFFFFF00) >> 8

    def write_word(self, byte_addr, wd_data):
        # pdb.set_trace()
        old_wd_data = self.DataStore[byte_addr >> 2]
        next_wd_data = self.DataStore[(byte_addr >> 2) + 1]
        self.metric.up_lm_write_bytes += 4
        if byte_addr % 4 == 0:
            self.DataStore[byte_addr >> 2] = wd_data
        elif byte_addr % 4 == 1:
            self.metric.cycle += 1
            self.DataStore[byte_addr >> 2] = old_wd_data & 0xFF000000 | (wd_data & 0xFFFFFF00) >> 8
            self.DataStore[(byte_addr >> 2) + 1] = next_wd_data & 0x00FFFFFF | (wd_data & 0x000000FF) << 24
        elif byte_addr % 4 == 2:
            self.metric.cycle += 1
            self.DataStore[byte_addr >> 2] = old_wd_data & 0xFFFF0000 | (wd_data & 0xFFFF0000) >> 16
            self.DataStore[(byte_addr >> 2) + 1] = next_wd_data & 0x0000FFFF | (wd_data & 0x0000FFFF) << 16
        else:
            self.metric.cycle += 1
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

    def address_generate_unit(self, base, index_val):  # , size):
        base_val = self.rd_ear(base)
        self.metric.cycle += 1
        # if(index[0]=='U'):
        #    index_val = self.rd_register(index)
        # else:
        #    index_val =self.rd_obbuffer(index)
        # # printd("AddrGen: base:%s, base_val:%d index:%s, index_val:%d, size:%d" % (base, base_val, index, index_val, size) , progress_trace)
        # return int(base_val) + int(index_val) * int(size)
        # printd("Address Unit:Base_val %d, Index_val:%d, DRAM_Addr:%d" % (int(base_val), int(index_val), int(base_val)+int(index_val)), progress_trace)
        return int(base_val) + int(index_val)

    def SBPB(self):
        return self.SBP >> 3

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

    def printDataStore(self, start_addr, end_addr, LEVEL):
        for addr in range(start_addr, end_addr, 4):
            data = self.read_word(addr)
            # printd( "<<{0}:{1}>>\n".format(format(addr-addr%4, '#06x'),format(data,'#010x')), LEVEL)

    # def executeEFA(self, efa, property_vec, SBPB_BEGIN = 0, initID=[0]):
    def executeEFA(self, efa, cont_exec):
        # def executeEFA(self, efa):
        # , property_vec, SBPB_BEGIN = 0, initID=[0]):
        # ====== efa program loaded to UDP
        # pdb.set_trace()
        # cont_exec=0
        self.curr_event_scyc = self.metric.cycle
        SBPB_BEGIN = 0
        self.num_sends = 0
        self.actcount = self.metric.total_acts
        # pdb.set_trace()
        if cont_exec == 0:
            property_vec = [Property("event", None)]
            # initID=[0]
            initID = efa.init_state_id
            # SBPB_BEGIN=0
            self.program = efa
            self.mm_offset = 4
            # self.mm_offset=self.send_mm.tell()+4
            # ====== load initial states
            init_state = []
            assert len(property_vec) == len(initID), "# of property must equal # of init states"
            for ID in initID:
                init_state.append(efa.get_state(ID))
            self.current_states = []
            for init_idx in range(len(initID)):
                self.current_states.append(Activation(init_state[init_idx], property_vec[init_idx]))

        next_states = []
        self.SBP = -self.CR_Advance + (SBPB_BEGIN << 3)
        init_sbp_val = self.CR_Advance
        yield_term = 0
        event_none = 0
        # pdb.set_trace()
        print("Executing EFA: len(self.current_states):%d" % len(self.current_states))
        while (
            (self.SBP + self.CR_Advance + self.CR_Issue) <= self.getInStreamBits()
            or self.current_states[0].property.p_type == "flag"
            or (self.current_states[0].property.p_type == "event" and yield_term == 0 and self.num_sends == 0)
            or self.current_states[0].property.p_type == "flag_majority"
        ):
            # check whether if it is a flag state.
            # If it is, do not advance SBP and input stream

            if self.current_states[0].property.p_type != "flag" and self.current_states[0].property.p_type != "flag_majority":
                self.SBP += self.CR_Advance
                issue_data = self.in_stream[self.SBP : self.SBP + self.CR_Issue].bin
                issue_data = self.bitsToInt(issue_data)
            else:
                issue_data = 0
                # printd( bcolors.OKGREEN+"\n[INFO] Executing Flag Transition"+bcolors.ENDC, progress_trace)
            # printd( bcolors.OKGREEN+"\nprocessing:   SBP="+str(self.SBP)+\
            #    "["+str(self.SBP)+":"+str(self.SBP+self.CR_Issue)+")"+\
            #    " SBPB="+str(self.SBPB())+bcolors.ENDC+" CR.ISSUE="+str(self.CR_Issue)+\
            #    " ("+str(hex(issue_data))+")"+'\n', progress_trace)
            # ====== major processing loop ======
            for activation in self.current_states:
                next_activations, yield_term, event_none = self.executeActivation(activation, issue_data)
                next_states = concatSet(next_states, next_activations)

            # printd( "%d:finish stage:yield_term:%d\n" % (self.lane_id, yield_term), stage_trace)
            # printd( "%d:Next_states %d\n" % (self.lane_id, yield_term), stage_trace)
            # printd(next_states, stage_trace)
            if event_none == 1:
                self.num_sends = 0
                return 0, (self.metric.cycle - self.curr_event_scyc), (self.metric.total_acts - self.actcount)
            self.printUDPR(full_trace)

            self.current_states = next_states
            next_states = []
            # pdb.set_trace()
            # ====== detect non-active error, if find, abort
            if len(self.current_states) == 0:
                print("error, all no active states, not allowed for now")
                print("SBPB " + str(self.SBPB()))
                exit()

            # UDP Regs are all 32-bits. python needs to explicitly mask
            for idx in range(len(self.UDPR)):
                self.UDPR[idx] = self.UDPR[idx] & 0xFFFFFFFF
        # if yield_term == 1:
        # printd("Printing EventQueue", progress_trace)
        # self.printEvQ(progress_trace)
        if self.num_sends > 0:
            print("Gonna return num sends")
            return self.num_sends, (self.metric.cycle - self.curr_event_scyc), (self.metric.total_acts - self.actcount)
            self.mm_offset = 4
        else:
            print("Finished execution! About to yield")
            self.mm_offset = 4
            self.num_sends = 0
            # self.pipe.close()
            return -1, (self.metric.cycle - self.curr_event_scyc), (self.metric.total_acts - self.actcount)

    def executeActivation(self, activation, input_label):
        property = activation.property
        state = activation.state
        # print("State: %d, Property: %s" % (state.state_id, property.p_type))
        # printd("%d EventQ before executeActivation:%d" % (self.lane_id, self.EvQ.getOccup()), progress_trace)
        # ====== select the transitions ======
        # pdb.set_trace()
        if property.p_type == "common":
            trans = [state.trans[0]]
        elif property.p_type == "flag" or property.p_type == "flag_majority":
            trans = state.get_tran(self.UDPR[0])
        elif property.p_type == "event":
            if not self.EvQ.isEmpty():
                event = self.EvQ.popEvent()
                self.curr_event_scyc = self.metric.cycle
                self.curr_event_sins = self.metric.total_acts
                # Only for Triangle Count
                if event.event_label == 0:
                    self.fetch_event_sins = self.metric.total_acts
                else:
                    self.match_event_sins = self.metric.total_acts

                # event_label = event.event_word & 0x000000ff
                self.metric.num_events += 1
                # self.OpBuffer.base = event.opbase # Operand Buffer Pointer for current event
                # event.printOut(progress_trace)
                trans = state.get_tran(event.event_label)
                # trans = state.get_tran(event_label)
                self.curr_event = event
            else:
                # timeout=self.timeout
                # flag = self.event_obj.wait(timeout)
                # if flag:
                #  print("Event was set to true() earlier, moving ahead with the thread")
                #  exit()
                # else:
                #  print("Time out occured, event internal flag still false. Executing thread without waiting for event")
                # print("EventQ is empty?")
                return activation, 0, 1
        else:
            trans = state.get_tran(input_label)
        # printd("%d EventQ after Activation EventPop:%d TransLen:%d" % (self.lane_id, self.EvQ.getOccup(), len(trans)), progress_trace)

        # ====== signature fail, look for majority transition
        # if not found, which means signature fail in machine level
        # print("Executing Activation: len(trans):%d" % len(trans))
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
        dst_activations = []
        for tr in trans:
            # tr.printOut(2)
            self.metric.TranSetBase()
            next_activation, forked_activations, yield_term = self.executeTransition(tr)
            self.metric.TranCycleDelta(tr)
            self.metric.TranCycleLabelDelta(tr)
            dst_activations.append(next_activation)
            if forked_activations is not None:
                dst_activations = concatSet(dst_activations, forked_activations)

        return dst_activations, yield_term, 0

    def executeTransition(self, transition):
        dst_state = transition.dst
        forked_activations = None
        # pdb.set_trace()
        # ====== each transition executed in 1 cycle
        self.metric.cycle += 1
        self.metric.total_trans += 1
        printd("take transition:\n", stage_trace)
        self.metric.TranGroupBin(transition)
        # transition.printOut(stage_trace)
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
            while yield_exec == 0 and seqnum <= numActions:
                # ====== action can modify the destination state's
                # property, and fork multiple activations ======
                action = transition.getAction(seqnum)
                # print("exec-Trans-action:%s, yield_exec:%d, seqnum:%d, numActions:%d" % (action.opcode, yield_exec, seqnum, numActions))
                action_dst_property, forked_activations, yield_exec, next_seqnum, yield_term = self.actionHandler(action, seqnum)

                # ====== if action changes the property, we need to
                # apply it to destination state ======
                seqnum = next_seqnum
                if action_dst_property is not None:
                    dst_property = action_dst_property
        # print("exec-Trans-yield_exec:%d, yield_term:%d" % (yield_exec, yield_term))
        # print(dst_state)
        # print(dst_property)
        return Activation(dst_state, dst_property), forked_activations, yield_term

    def actionHandler(self, action, seqnum):
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum_set = 0
        next_seqnum = seqnum
        # action.printOut(stage_trace)
        self.metric.total_acts += 1
        # printd ("\n",stage_trace)
        # pdb.set_trace()
        # ====== action executed at least 1 cycle, more cycles in detail action
        self.metric.cycle += 1
        # ======  Action Dispather ======
        if action.opcode == "set_state_property":
            dst_property = self.do_set_state_property(action)
        elif action.opcode == "hash_sb32":
            self.do_hash_sb32(action)
        elif action.opcode == "mov_lm2reg":
            self.metric.mov_ins += 1
            self.metric.probes += 1
            self.do_mov_lm2reg(action)
        elif action.opcode == "mov_lm2reg_blk":
            self.metric.mov_ins += 1
            self.metric.probes += 1
            self.do_mov_lm2reg_blk(action)
        elif action.opcode == "mov_reg2lm":
            self.metric.mov_ins += 1
            self.do_mov_reg2lm(action)
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
        elif action.opcode == "block_compare_i":
            self.do_block_compare_i(action)
        elif action.opcode == "block_compare":
            self.do_block_compare(action)
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
        elif action.opcode == "cmpswp":
            self.metric.al_ins += 1
            self.do_cmpswp(action)
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
        elif action.opcode == "send":
            # self.metric.cycle += 1
            self.metric.msg_ins += 1
            self.do_send(action)
        elif action.opcode == "send_with_ret":
            # self.metric.cycle += 1
            self.metric.msg_ins += 1
            self.do_send_with_ret(action)
        elif action.opcode == "send_reply":
            # self.metric.cycle += 1
            self.metric.msg_ins += 1
            self.do_send_reply(action)
        elif action.opcode == "yield":
            # self.metric.cycle += 1
            self.metric.yld_ins += 1
            yield_exec = self.do_yield(action)
        elif action.opcode == "yield_terminate":
            # self.metric.cycle += 1
            self.metric.yld_ins += 1
            yield_exec, yield_term = self.do_yield_terminate(action)
        # ==============================
        if seqnum_set == 0:
            next_seqnum = int(seqnum) + 1
        # print("exec-action-%s, yield_exec:%d, yield_term:%d" % (action.opcode, yield_exec, yield_term))
        # print(dst_property)
        return dst_property, forked_activations, yield_exec, next_seqnum, yield_term

    def parseIdx(self, dst_reg):
        return int(dst_reg[5:])

    # May not be needed for ob buffer
    def parseOffs(self, offs):
        return int(offs[3:])

    def parseEars(self, ears):
        return int(ears[4:])

    def rd_register(self, reg_ident):
        # printd("%d Reg:%s" % (self.lane_id, reg_ident),progress_trace)
        if reg_ident[0:4] == "UDPR":
            idx = self.parseIdx(reg_ident)
            printd("Reg:%s:%d" % (reg_ident, self.UDPR[idx]), progress_trace)
            return self.UDPR[idx]
        elif reg_ident == "SBP":
            return self.SBP
        elif reg_ident == "SBPB":
            return self.SBPB()
        elif reg_ident[0:2] == "OB":
            return self.rd_obbuffer(reg_ident)
        elif reg_ident == "EQT":
            return self.curr_event.event_word
        elif reg_ident == "TS":
            return 0
        else:
            idx = self.parseIdx(reg_ident)
            # printd("Reg:%s:%d" % (reg_ident,self.UDPR[idx]),progress_trace)
            return self.UDPR[idx]

    def wr_register(self, reg_ident, data):
        if reg_ident == "SBP":
            self.SBP = data
        elif reg_ident == "SBPB":
            self.SBP = data << 3
        else:
            idx = self.parseIdx(reg_ident)
            self.UDPR[idx] = data

    def wr_register_blk(self, reg_ident, data):
        idx = self.parseIdx(reg_ident)
        for i in range(len(data)):
            self.UDPR[idx + i] = data[i]

    def rd_register_blk(self, reg_ident, sz):
        idx = self.parseIdx(reg_ident)
        data = []
        for i in range(int(sz / 4)):
            data.append(self.UDPR[idx + i])

        # print("Regblk_data", data)
        return data

    def rd_obbuffer(self, ob_ident):
        offs = self.parseOffs(ob_ident)
        # printd("%d %s:%d" % (self.lane_id, ob_ident,self.OpBuffer.getOp(offs)),progress_trace)
        return self.OpBuffer.getOp(offs)
        # return self.OpBuffer[offs]

    def rd_obbuffer_block(self, ob_ident, size):
        ret_data = [0 for x in range(size)]
        offs = self.parseOffs(ob_ident)
        for i in range(size):
            ret_data[i] = self.OpBuffer.getOp(offs + i)
        return ret_data

    def rd_obbuffer_blk(self, ob_ident, sz):
        offs = self.parseOffs(ob_ident)
        data = []
        # print("%d Reg:%s:%d, %d" % (self.lane_id, ob_ident,self.OpBuffer.getOp(offs), sz))
        for i in range(int(sz / 4)):
            # print("i:%d, offs:%d, offs+i:%d" %(i, offs, offs+i))
            data.append(self.OpBuffer.getOp(offs + i))
        # print("Obbuferblk_data", data)
        return data

    def wr_obbuffer(self, ob_ident, data):
        # pdb.set_trace()
        offs = self.parseOffs(ob_ident)
        self.OpBuffer.setOp(offs, data)
        # self.OpBuffer[offs] = data

    # def read_anyreg(self, reg):
    #    val = 0
    #    if reg[0] == 'U':
    #        val = self.rd_register(reg)
    #    elif reg[0] == 'O':
    #        val = self.rd_obbuffer(reg)
    #    return val

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
        start = self.SBP
        # ====== align read 1 extra cycle
        # unaligned read 2 extra cycles
        if start % 4 == 0:
            self.metric.cycle += 1

        else:
            self.metric.cycle += 2

        value = self.in_stream[start : start + 32].bin
        value = self.bitsToInt(value)
        # ====== hash generates the entry index, each entry is 2 bytes
        # entry_addr = hash_snappy(value, 20)*2 + hashTableBaseAddr # using snappy hash
        entry_addr = hash_crc(value) * 2 + hashTableBaseAddr  # using crc hash
        self.wr_register(action.dst, entry_addr)

    def do_mov_lm2reg(self, action):
        src_addr = self.rd_register(action.src)
        numOfBytes = self.rd_imm(action.imm)
        if numOfBytes == 4:
            lm_data = self.read_word(src_addr)
        elif numOfBytes == 2:
            lm_data = self.read_2bytes(src_addr)
        elif numOfBytes == 1:
            lm_data = self.read_byte(src_addr)
        else:
            # print("not yet support "),
            action.printOut(error)
            exit()
        # print("src_addr:%d, lm_data:%d" % (src_addr,lm_data))
        self.wr_register(action.dst, lm_data)

    def do_mov_reg2lm(self, action):
        # pdb.set_trace()
        src_data = self.rd_register(action.src)
        numOfBytes = self.rd_imm(action.imm)
        lm_addr = self.rd_register(action.dst)
        if numOfBytes == 4:
            src_data = src_data & 0xFFFFFFFF
            self.write_word(lm_addr, src_data)
        elif numOfBytes == 2:
            src_data = src_data & 0xFFFF
            self.write_2bytes(lm_addr, src_data)
        elif numOfBytes == 1:
            src_data = src_data & 0xFF
            self.write_byte(lm_addr, src_data)
        else:
            # print("not yet support "),
            action.printOut(error)
            exit()
        # self.printDataStore(lm_addr,lm_addr+4, full_trace)

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

    def do_mov_ob2ear(self, action):
        src = action.src.split("_")
        src1 = "OB_" + src[1]
        src2 = "OB_" + src[2]
        data1 = self.rd_obbuffer(src1)
        data2 = self.rd_obbuffer(src2)
        # printd("OB2EAR: src1:%s, src2:%s, dst:%s, data1:%d, data2:%d " % (src1, src2, action.dst, data1, data2), progress_trace)
        self.wr_ear(action.dst, data1, data2)

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
        # print("Addi:%s - %d+%d=%d" % (action.src, src_data, imm, res))
        self.wr_register(action.dst, res)

    # ====== copy from [src_addr, src_addr+length) ======
    def do_copy(self, action):
        src_addr = self.rd_register(action.src)
        dst_addr = self.rd_register(action.rt)
        length = self.rd_register(action.dst)
        ori_length = length
        src_ptr = src_addr
        dst_ptr = dst_addr
        while length > 0:
            data_byte = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data_byte
            src_ptr += 1
            dst_ptr += 1
            length -= 1
        self.wr_register(action.src, src_ptr)
        self.wr_register(action.rt, dst_ptr)
        self.wr_register(action.dst, length)
        # ====== estimate extra cycles
        self.metric.cycle += 2 + ori_length / 4
        # self.printOutStream(full_trace)

    def do_copy_ob_lm(self, action):
        src_addr = action.src
        dst_addr = self.rd_register(action.rt)
        length = self.rd_register(action.dst)
        ob_data = self.rd_obbuffer_block(src_addr, length)
        for i in range(length):
            self.write_word(dst_addr + i * 4, ob_data[i])
        self.metric.cycle += 2

    # ====== copy from outstream [src_addr, src_addr+length) ======
    # NOTE: real UDP should have 1 copy. No matter from in stream or out stream
    def do_copy_from_out(self, action):
        src_addr = self.rd_register(action.src)
        dst_addr = self.rd_register(action.rt)
        length = self.rd_register(action.dst)
        ori_length = length
        src_ptr = src_addr
        dst_ptr = dst_addr
        while length > 0:
            data_byte = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data_byte
            src_ptr += 1
            dst_ptr += 1
            length -= 1
        self.wr_register(action.src, src_ptr)
        self.wr_register(action.rt, dst_ptr)
        self.wr_register(action.dst, length)
        # ====== estimate extra cycles
        self.metric.cycle += 2 + ori_length / 4
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

    def do_put2byte_imm(self, action):
        data = self.rd_imm(action.imm)
        dst_ptr = self.rd_register(action.dst)
        data = data & 0xFFFF
        # ====== align write and unalign write
        if dst_ptr % 4 == 0 or dst_ptr % 4 == 1 or dst_ptr % 4 == 2:
            self.metric.cycle += 1
        else:
            self.metric.cycle += 2

        self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 16] = data
        dst_ptr += 2
        self.wr_register(action.dst, dst_ptr)
        # printd("put:"+str(hex(data))+"\n", full_trace)

    def do_put1byte_imm(self, action):
        data = self.rd_imm(action.imm)
        dst_ptr = self.rd_register(action.dst)
        data = data & 0xFF
        # ====== unalign write
        self.metric.cycle += 1
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
        # print("lshift_check:%s:%d" % (action.dst,res))
        self.wr_register(action.dst, res)

    def do_rshift_and_imm(self, action):
        src = self.rd_register(action.src)
        and_val = self.rd_imm(action.imm2)
        shift_val = int(action.imm)
        res = (src >> shift_val) & and_val
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
        if numOfBytes == 4:
            # ====== align write and unalign write
            if dst_ptr % 4 == 0:
                self.metric.cycle += 0
            else:
                self.metric.cycle += 2
            data = data & 0xFFFFFFFF
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 32] = data
            dst_ptr += 4
        elif numOfBytes == 3:
            # ====== align write and unalign write
            if dst_ptr % 4 == 0 or dst_ptr % 4 == 1:
                self.metric.cycle += 1
            else:
                self.metric.cycle += 2
            data = data & 0xFFFFFF
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 24] = data
            dst_ptr += 3
        elif numOfBytes == 2:
            # ====== align write and unalign write
            if dst_ptr % 4 == 0 or dst_ptr % 4 == 1 or dst_ptr % 4 == 2:
                self.metric.cycle += 1
            else:
                self.metric.cycle += 2
            data = data & 0xFFFF
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 16] = data
            dst_ptr += 2
        elif numOfBytes == 1:
            # ====== unalign write
            self.metric.cycle += 1
            data = data & 0xFF
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data
            dst_ptr += 1
        else:
            # print ("numOfBytes Wrong in "+action.printOut(error))
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
        # printd("comp_reg: src:%d, rt:%d, res:%d" % (src, rt, res), progress_trace)
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
            else:
                self.metric.cycle += 2

            data = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 32]
            src_ptr += 4
            data = data.tobytes()
            res = 0
            for i in range(0, 4):
                res |= ord(data[3 - i]) << (i * 8)

        elif numOfBytes == 3:
            # ====== align read and unalign read
            if src_ptr % 4 == 0 or src_ptr % 4 == 1:
                self.metric.cycle += 1
            else:
                self.metric.cycle += 2

            data = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 24]
            src_ptr += 3
            data = data.tobytes()
            res = 0
            for i in range(0, 2):
                res |= ord(data[2 - i]) << (i * 8)

        elif numOfBytes == 2:
            # ====== align read and unalign read
            if src_ptr % 4 == 0 or src_ptr % 4 == 1 or src_ptr % 4 == 2:
                self.metric.cycle += 1
            else:
                self.metric.cycle += 2

            data = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 16]
            src_ptr += 2
            data = data.tobytes()
            res = 0
            for i in range(0, 2):
                res |= ord(data[1 - i]) << (i * 8)

        elif numOfBytes == 1:
            # ====== align read
            self.metric.cycle += 1

            data = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            src_ptr += 1
            data = data.tobytes()
            res = ord(data[0])

        self.wr_register(action.src, src_ptr)
        self.wr_register(action.dst, res)

    def do_getbytes_from_out(self, action):
        src_ptr = self.rd_register(action.src)
        numOfBytes = self.rd_imm(action.imm)
        if numOfBytes == 4:
            # ====== align read and unalign read
            if src_ptr % 4 == 0:
                self.metric.cycle += 1
            else:
                self.metric.cycle += 2

            data = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 32]
            src_ptr += 4
            data = data.tobytes()
            res = 0
            for i in range(0, 4):
                res |= ord(data[3 - i]) << (i * 8)

        elif numOfBytes == 3:
            # ====== align read and unalign read
            if src_ptr % 4 == 0 or src_ptr % 4 == 1:
                self.metric.cycle += 1
            else:
                self.metric.cycle += 2

            data = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 24]
            src_ptr += 3
            data = data.tobytes()
            res = 0
            for i in range(0, 2):
                res |= ord(data[2 - i]) << (i * 8)

        elif numOfBytes == 2:
            # ====== align read and unalign read
            if src_ptr % 4 == 0 or src_ptr % 4 == 1 or src_ptr % 4 == 2:
                self.metric.cycle += 1
            else:
                self.metric.cycle += 2

            data = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 16]
            src_ptr += 2
            data = data.tobytes()
            res = 0
            for i in range(0, 2):
                res |= ord(data[1 - i]) << (i * 8)

        elif numOfBytes == 1:
            # ====== align read
            self.metric.cycle += 1

            data = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            src_ptr += 1
            data = data.tobytes()
            res = ord(data[0])

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

    def do_cmpswp(self, action):
        # reg = self.rd_register(action.src)
        mem_addr = self.rd_register(action.dst)
        mem = self.read_word(mem_addr)
        if mem == action.imm:
            self.write_word(mem_addr, action.imm2)
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

    def do_mov_lm2reg_blk(self, action):
        src_addr = self.rd_register(action.src)
        # dst_addr = action.rt
        blksize = self.rd_imm(action.imm)
        lmdata = []
        for i in range(int(blksize / 4)):
            lmdata.append(self.read_word(src_addr + i * 4))
        print("src_addr:%d, sz:%d" % (src_addr, blksize))
        print("data", lmdata)
        self.wr_register_blk(action.dst, lmdata)

    def do_block_compare_i(self, action):
        srcdata1 = []
        srcdata2 = []
        sz = self.rd_imm(action.imm2)
        if action.src[0] == "U":
            srcdata1 = self.rd_register_blk(action.src, sz)
        else:
            srcdata1 = self.rd_obbuffer_blk(action.src, sz)
        if action.dst[0] == "U":
            srcdata2 = self.rd_register_blk(action.dst, sz)
        else:
            srcdata2 = self.rd_obbuffer_blk(action.dst, sz)
        num_comp = 0
        for i in range(len(srcdata1)):
            for j in range(len(srcdata2)):
                if srcdata1[i] == srcdata2[j]:
                    num_comp += 1
        print("sz:%d, src:%s, dst:%s, num_comp:%d" % (sz, action.src, action.dst, num_comp))
        print("srcdata:", srcdata1)
        print("dstdata:", srcdata2)
        self.wr_register(action.imm, num_comp)

    def do_block_compare(self, action):
        srcdata1 = []
        srcdata2 = []
        sz = self.rd_register(action.imm2)
        if action.src[0] == "U":
            srcdata1 = self.rd_register_blk(action.src, sz)
        else:
            srcdata1 = self.rd_obbuffer_blk(action.src, sz)
        if action.dst[0] == "U":
            srcdata2 = self.rd_register_blk(action.dst, sz)
        else:
            srcdata2 = self.rd_obbuffer_blk(action.dst, sz)
        num_comp = 0
        for i in range(len(srcdata1)):
            for j in range(len(srcdata2)):
                if srcdata1[i] == srcdata2[j]:
                    num_comp += 1
        print("sz:%d, src:%s, dst:%s, num_comp:%d" % (sz, action.src, action.dst, num_comp))
        print("srcdata:", srcdata1)
        print("dstdata:", srcdata2)
        self.wr_register(action.imm, num_comp)

    # ====== copy from [src_addr, src_addr+length) ======
    def do_copy_imm(self, action):
        src_addr = self.rd_register(action.src)
        dst_addr = self.rd_register(action.dst)
        length = self.rd_imm(action.imm)
        ori_length = length
        src_ptr = src_addr
        dst_ptr = dst_addr
        while length > 0:
            data_byte = self.in_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data_byte
            src_ptr += 1
            dst_ptr += 1
            length -= 1
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
        while length > 0:
            data_byte = self.out_stream[src_ptr << 3 : (src_ptr << 3) + 8]
            self.out_stream[dst_ptr << 3 : (dst_ptr << 3) + 8] = data_byte
            src_ptr += 1
            dst_ptr += 1
            length -= 1
        self.wr_register(action.src, src_ptr)
        self.wr_register(action.dst, dst_ptr)
        # ====== estimate extra cycles
        self.metric.cycle += 2 + ori_length / 4
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
        self.CR_Issue = new_width
        old_CR_Advance = self.CR_Advance
        self.CR_Advance = new_width
        # the SBP should commit the old_CR_Advance,
        # we compensate here
        self.SBP += old_CR_Advance - self.CR_Advance
        # printd ("issue:"+str(self.CR_Issue)+" advance:"+str(self.CR_Advance)+"\n",full_trace)

    def do_set_complete(self, action):
        imm = self.rd_imm(action.imm)
        if imm == 1:
            self.SBP = self.getInStreamBits() + 1

    def do_refill(self, action):
        # it is a virutal action. In machine code, it is represented in transition
        # primitive
        self.metric.cycle -= 1
        flush = self.rd_imm(action.imm)
        self.SBP = self.SBP - flush

    def do_mov_imm2reg(self, action):
        imm = self.rd_imm(action.imm)
        self.wr_register(action.dst, imm)

    # TODO:finish this
    def do_mov_sb2reg(self, action):  # added by Marzi
        issue_data = self.in_stream[self.SBP : self.SBP + self.CR_Issue].bin
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
            if action.dst[0] == "b":
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                next_seqnum = int(action.dst)
                seqnum_set = 1
        else:
            next_seqnum = 0
            seqnum_set = 0
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
        if op1 == op2:
            if action.dst[0] == "b":
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                next_seqnum = int(action.dst)
                seqnum_set = 1
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
        if op1 > op2:
            if action.dst[0] == "b":
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                next_seqnum = int(action.dst)
                seqnum_set = 1
        else:
            next_seqnum = 0
            seqnum_set = 0
        return next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term

    def do_bge(self, action):
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
        if op1 >= op2:
            if action.dst[0] == "b":
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, 1)
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
            if action.dst[0] == "b":
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                next_seqnum = int(action.dst)
                seqnum_set = 1
        else:
            next_seqnum = 0
            seqnum_set = 0
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
            if action.dst[0] == "b":
                next_seqnum = 0
                seqnum_set = 0
                pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, 1)
                dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
            else:
                next_seqnum = int(action.dst)
                seqnum_set = 1
        else:
            next_seqnum = 0
            seqnum_set = 0
        return next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term

    def do_jmp(self, action):
        dst_property = None
        forked_activations = None
        yield_exec = 0
        yield_term = 0
        seqnum_set = 0
        if action.dst[0] == "b":
            next_seqnum = 0
            seqnum_set = 0
            pseudo_action = Action("tranCarry_goto", "Empty", "Empty", action.dst, 1)
            dst_property, forked_activations, yield_exec, yield_term = self.do_goto(pseudo_action)
        else:
            next_seqnum = int(action.dst)
            seqnum_set = 1
        return next_seqnum, seqnum_set, dst_property, forked_activations, yield_exec, yield_term

    def do_send(self, action):
        # pdb.set_trace()
        # printd("EventQ before send:%d" % self.EvQ.getOccup(), progress_trace)
        """
        Decoding for send mmap
        0 - Type of Send. 0: Read, 1: Write [for now]
        1 - lower addr
        2 - higher addr
        3 - Size
        4 - addr_mode
        5 - dest
        6 - event label?
        7 - num operands?
        """
        if action.dst != "TOP":
            event_word = self.rd_register(action.event)
            dest = self.rd_register(action.dst)
            addr = self.rd_register(action.addr)
            addr_mode = int(action.addr_mode)
            dram_addr = 0
            # print("Send Params: size:%s, addr:%s, dest=%s, addr_mode=%d, rw=%s" %(action.size, addr, dest, addr_mode,action.rw))
            if dest > 1 and action.rw == "r":  # read message
                size = int(action.size)
                # addr_base = action.addr[0:5]
                # addr_index = action.addr[6:]
                # dram_addr = self.address_generate_unit(addr_base, addrindex, size)
                if addr_mode > 0:
                    ear_base = "EAR_" + str(addr_mode - 1)
                    dram_addr = self.address_generate_unit(ear_base, addr)
                # print("DRAM address :%lx\n", dram_addr)
                ev_operands = [None for i in range(int(size / 4))]
                self.send_mm.seek(0)
                self.num_sends += 1
                val = struct.pack("I", self.num_sends)
                self.send_mm.write(val)
                self.send_mm.seek(self.mm_offset)
                rwval = 1 if action.rw == "r" else 0
                val = struct.pack("I", rwval)
                self.send_mm.write(val)
                val = struct.pack("I", (dram_addr & 0xFFFFFFFF))  # lower int
                self.send_mm.write(val)
                # print("works till here right?")
                # print("lower Val %d" % dram_addr&0xffffffff)
                val = struct.pack("I", ((dram_addr >> 32) & 0xFFFFFFFF))  # upper int
                self.send_mm.write(val)
                # print("upper Val %d" % (dram_addr>>32)&0xffffffff)
                val = struct.pack("I", size)
                self.send_mm.write(val)
                val = struct.pack("I", addr_mode)
                self.send_mm.write(val)
                val = struct.pack("I", dest)
                self.send_mm.write(val)
                val = struct.pack("I", event_word)
                self.send_mm.write(val)
                val = struct.pack("I", len(ev_operands))
                self.send_mm.write(val)
                self.mm_offset = self.send_mm.tell()
                # for i in range(int(size/4)):
                #    if addr_mode > 0:
                #        line = "r:" + str(dram_addr) + ":" + str(size) + ":" + str(self.lane_id)
                #        #print("Writing into %s: %s","/tmp/pipe"+str(self.lane_id),line)
                #        ##ev_operands[i] = self.dram.read_word(dram_addr+4*i)
                #
                #        self.metric.up_dram_read_bytes+=4
                #    else:
                #        ev_operands[i] = self.read_word(addr+4*i)
                # for val in ev_operands:
                #    #printd("ev_operands: %d" % val, progress_trace)
                #    self.OpBuffer.setOp(val)
                ##next_event = Event('nr')
                ##next_event = Event(action.event_label, start_index)
                # event_label = event_word & 0x000000ff
                # next_event = Event(event_label, len(ev_operands))
                # self.EvQ.pushEvent(next_event)
            #            elif action.dst[0:2] == "UP" action.rw == 1: #write message
            #            for i in range(size/4):
            #               self.dram.write_word()
            elif dest > 1 and action.rw == "w":
                print("Write to a different lane")
        else:
            # if dest == 1 and action.rw == 'w': #send message back to TOP
            size = int(action.size)
            # print("send to TOP from reg:%s" % action.addr)
            data = self.rd_register(action.addr)
            # print("send to TOP data:%d" % data)
            # self.top.sendResult(data)
        # printd("EventQ after send:%d" % self.EvQ.getOccup(), progress_trace)
        # return 5

    def do_send_with_ret(self, action):
        # printd("EventQ before send:%d" % self.EvQ.getOccup(), progress_trace)
        return 0

    def do_send_reply(self, action):
        # printd("EventQ before send:%d" % self.EvQ.getOccup(), progress_trace)
        return 0

    def do_yield(self, action):
        # Potential Clean up code
        yield_exec = 1
        self.metric.ops_removed += self.curr_event.numOps()
        # pdb.set_trace()
        self.OpBuffer.clearOp(self.curr_event.numOps())
        ins_per_event = self.metric.total_acts - self.curr_event_sins
        cyc_per_event = self.metric.cycle - self.curr_event_scyc

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
        return yield_exec

    def do_yield_terminate(self, action):
        # Potential Clean up code
        yield_exec = 1
        yield_term = 1
        self.metric.ops_removed += self.curr_event.numOps()
        self.OpBuffer.clearOp(self.curr_event.numOps())
        # print("Yield_Terminate:%d" % yield_term)
        # print("TriangleCount Check: UDPR_3:%d" % self.rd_register("UDPR_3"))
        ins_per_event = self.metric.total_acts - self.curr_event_sins
        cyc_per_event = self.metric.cycle - self.curr_event_scyc
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
        return yield_exec, yield_term

    def executeEFAThread(self, efa):
        # event_obj = threading.Event()
        th1 = threading.Thread(target=self.executeEFA, args=(self.event_obj, efa))
        th1.start()

    def triggerEvent(self):
        self.event_obj.set()

#    def triggerSend(self):
#        self.send_obj.set()

import sys
sys.path.append('../')
import os
root =  os.environ['TBTROOT']
sys.path.append(root+'/src/assembler/udp/main')
sys.path.append(root+'/src/assembler/udp/emulator')
from GenTriCountEFA import *
from StattestsEFA import *
from bitstring import BitArray
from EfaExecutor import *
from memory import *
from GenMemoryGraph import *
import  EfaUtil as efa_util
import tricount

#class returnBuff:
#    def __init__(self, size):
#        self.size = size
#        buff = []
#        is_avail = [0 for i in range(size)]
#        result_ready = 0
#
#    def insert(self, data):
#        buff.append(data)
#        is_avail



class Top:
    def __init__(self):
        self.progs = {}
        self.up = None
        self.mem = None
        self.result = []
        self.result_avail = 0

    def addUpMem(self, up, mem):
        self.up = up
        self.mem = mem

    def sendResult(self, data):
        self.result.append(data)
        self.result_avail = 1

    def getResult(self, size):
        results=[]
        for i in range(size):
            if(len(self.result)> 0):
                results.append(self.result.pop(0))
        if(len(self.result)==0):
            self.result_avail=0
        return results

    def addProgs(self):
        self.progs = {"tricount.sequential":tricount.sequential, 
                "tricount.single_stream_array":tricount.single_stream_array,
                "tricount.single_stream_thread":tricount.single_stream_thread,
                "tricount.single_stream_thread_ayz":tricount.single_stream_thread_ayz,
                "tricount.single_stream_mp":tricount.single_stream_mp,
                "tricount.single_stream_mp_long":tricount.single_stream_mp_long,
                "tricount.single_stream":tricount.single_stream} 

    def run(self, prog, params):
        print(prog)
        #print(params)
        params["top"] = self
        self.progs[prog](params)


    
        


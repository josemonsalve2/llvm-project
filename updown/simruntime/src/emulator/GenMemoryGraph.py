import sys
import os
root =  os.environ['TBTROOT']
current_dir=root+'/src/libraries/trianglecount/udp_kernel/'
sys.path.append(root+'/src/assembler/udp/main')
sys.path.append(root+'/src/assembler/udp/emulator')
from GenTriCountEFA import *
from bitstring import BitArray
import re
from memory import *
import argparse
import snap

class Vertex:
    def __init__(self, id):
        self.id = id
        self.size = 0
        self.neighbors = []

    def add_neighbor(self, n_id):
        self.neighbors.append(n_id)
        self.size = self.size + 1

    def __repr__(self):
        repstr = str(self.id) + "|" + str(self.size) + "|["
        for i in range(self.size-1):
            repstr = repstr + str(self.neighbors[i]) +","
        repstr = repstr + str(self.neighbors[self.size-1]) + "]"
        return repstr

def GenVertList(graphfilepath):
    src=[]
    dst=[]
    with open(graphfilepath, 'r') as graphfile:
        line = graphfile.readline()
        while line:
            if line[0] != '#':
                lineitems = line.split()
                src.append(int(lineitems[0]))
                dst.append(int(lineitems[1]))
            line = graphfile.readline()
    prev_src = -1
    vertexList = []
    vert_index = -1
    for i in range(len(src)):
        if src[i] != prev_src:
            prev_src = src[i]
            vert_index = vert_index + 1
            vertexList.append(Vertex(prev_src))
        vertexList[vert_index].add_neighbor(dst[i])
    return vertexList

def GenGraph(graphfile, is_undirected, outgraph):
    outf = open(outgraph, "w")
    if(is_undirected):
        print("Reading Graph as Undirected %s")
        (G, Map) = snap.LoadEdgeListStr(snap.TUNGraph, graphfile, 0, 1, True)
        for NI in G.Nodes():
            #print("NodeID|Deg:%d|%d|%s" % (NI.GetId(), NI.GetDeg(), Map.GetKey(NI.GetId())))
            for Id in NI.GetOutEdges():
                outf.write("(%d,%d)\n" % (NI.GetId(),Id))
    else:
        print("Reading Graph as Directed")
        (G, Map) = snap.LoadEdgeListStr(snap.TNGraph, graphfile)
        for NI in G.Nodes():
            #print("NodeID|Deg:%d|%d|%s" % (NI.GetId(), NI.GetDeg(), Map.GetKey(NI.GetId())))
            for Id in NI.GetOutEdges():
                outf.write("(%d,%d)\n" % (NI.GetId(),Id))
    print("Testing input Graph")
    print("Number of nodes: %d" % G.GetNodes())
    return G, Map

def CreateMemFromGraph(mem, g, NodeMap, undirected, baseaddr):
    #print("Writing out Memory")
    node_addr, array_addr, final_addr = calcAddrfromGraph(g,baseaddr,undirected)
    #print(node_addr)
    #print(array_addr)
    #print("Node Addresses")
    #for i, val in enumerate(node_addr):
    #    print("0x%x:%d" % (i, val))
    curr_addr = baseaddr
    print("Writing Memory data")
    for node in g.Nodes():
        addr = node_addr[node.GetId()]
        if(undirected):
            mem.write_word(addr, node.GetDeg())
        else:
            mem.write_word(addr, node.OutDeg())
        mem.write_word(addr+4, node.GetId())
        mem.write_word(addr+8, array_addr[node.GetId()]&0xffffffff)
        mem.write_word(addr+12, ((array_addr[node.GetId()]&0xffffffff00000000) >> 32))
        #print("0x%x:%d" % (addr, mem.read_word(addr)))
        #print("0x%x:%d" % (addr+4, mem.read_word(addr+4)))
        #print("0x%x:%x" % (addr+8, mem.read_word(addr+8)))
        #print("0x%x:%x" % (addr+12, mem.read_word(addr+12)))
        addr = array_addr[node.GetId()]
        for i, Id in enumerate(node.GetOutEdges()):
            mem.write_word(addr+i*4, Id&0xffffffff)
            #mem.write_word(addr+i*8, node_addr[Id]&0xffffffff)
            #mem.write_word(addr+4+i*8, ((node_addr[Id]&0xffffffff00000000) >> 32))
            #print("0x%x:%d" % (addr+4*i, mem.read_word(addr+4*i)))
            #print("0x%x:%x" % (addr+4+8*i, mem.read_word(addr+4+8*i)))

        #print("0x%x:%d" % (addr, mem.read_word(addr)))
        #print("0x%x:%d" % (addr+4, mem.read_word(addr+4)))
        #for i, Id in enumerate(node.GetOutEdges()):
        #    mem.write_word(addr+8+i*8, node_addr[Id]&0xffffffff)
        #    mem.write_word(addr+12+i*8, ((node_addr[Id]&0xffffffff00000000) >> 32))
        #    #print("0x%x:%x" % (addr+8+8*i, mem.read_word(addr+8+8*i)))
        #    #print("0x%x:%x" % (addr+12+8*i, mem.read_word(addr+12+8*i)))
    return node_addr, array_addr, final_addr

def CreateMemFromGraphBurst(mem, g, NodeMap, undirected, baseaddr):
    print("Writing out Memory")
    node_addr, array_addr, final_addr = calcAddrfromGraph(g,baseaddr,undirected)
    print(node_addr)
    print(array_addr)
    print("Node Addresses")
    for i, val in enumerate(node_addr):
        print("0x%x:%d" % (i, val))
    curr_addr = baseaddr
    print("Writing Memory data")
    nodemem = []
    neighmem = []
    for node in g.Nodes():
        addr = node_addr[node.GetId()]
        if(undirected):
            #mem.write_word(addr, node.GetDeg())
            nodemem.append(node.GetDeg())
        else:
            #mem.write_word(addr, node.OutDeg())
            nodemem.append(node.OutDeg())
        #mem.write_word(addr+4, node.GetId())
        #mem.write_word(addr+8, array_addr[node.GetId()]&0xffffffff)
        #mem.write_word(addr+12, ((array_addr[node.GetId()]&0xffffffff00000000) >> 32))
        nodemem.append(node.GetId())
        nodemem.append(node.GetId())
        nodemem.append(array_addr[node.GetId()]&0xffffffff)
        nodemem.append(((array_addr[node.GetId()]&0xffffffff00000000) >> 32))
        #print("0x%x:%d" % (addr, mem.read_word(addr)))
        #print("0x%x:%d" % (addr+4, mem.read_word(addr+4)))
        #print("0x%x:%x" % (addr+8, mem.read_word(addr+8)))
        #print("0x%x:%x" % (addr+12, mem.read_word(addr+12)))
        addr = array_addr[node.GetId()]
        for i, Id in enumerate(node.GetOutEdges()):
            mem.write_word(addr+i*4, Id&0xffffffff)
            neighmem.append(Id&0xffffffff)
            #mem.write_word(addr+i*8, node_addr[Id]&0xffffffff)
            #mem.write_word(addr+4+i*8, ((node_addr[Id]&0xffffffff00000000) >> 32))
            print("0x%x:%d" % (addr+4*i, mem.read_word(addr+4*i)))
            #print("0x%x:%x" % (addr+4+8*i, mem.read_word(addr+4+8*i)))

        #print("0x%x:%d" % (addr, mem.read_word(addr)))
        #print("0x%x:%d" % (addr+4, mem.read_word(addr+4)))
        #for i, Id in enumerate(node.GetOutEdges()):
        #    mem.write_word(addr+8+i*8, node_addr[Id]&0xffffffff)
        #    mem.write_word(addr+12+i*8, ((node_addr[Id]&0xffffffff00000000) >> 32))
        #    #print("0x%x:%x" % (addr+8+8*i, mem.read_word(addr+8+8*i)))
        #    #print("0x%x:%x" % (addr+12+8*i, mem.read_word(addr+12+8*i)))
    return node_addr, array_addr



def calcAddrfromGraph(g, baseaddr, undirected):
    node_addr = [0 for x in range(g.GetNodes())]
    array_addr = [0 for x in range(g.GetNodes())]
    deg_addr = [0 for x in range(g.GetNodes())]
    curr_addr = baseaddr
    #for node in g.Nodes():
    #    node_addr[node.GetId()] = curr_addr
    #    curr_addr = curr_addr + 16
    #for node in g.Nodes():
    #    array_addr[node.GetId()] = curr_addr
    #    if(undirected):
    #        curr_addr = curr_addr + 8*node.GetDeg()
    #    else:
    #        curr_addr = curr_addr + 8*node.GetOutDeg()
    for node in g.Nodes():
        node_addr[node.GetId()] = curr_addr
        curr_addr = curr_addr + 16
    for node in g.Nodes():
        array_addr[node.GetId()] = curr_addr
        if(undirected):
            curr_addr = curr_addr + 4*node.GetDeg()
        else:
            curr_addr = curr_addr + 4*node.GetOutDeg()
    return node_addr, array_addr, curr_addr



def calcAddrfromVertList(vertexList):
    calc_addr = 0
    v_addr = []
    for v in vertexList:
        print("ID:%d, Addr:%d" % (v.id, calc_addr))
        v_addr.append([v.id, calc_addr])
        calc_addr = calc_addr + 8 + 8*v.size
    return v_addr

def writeVertListMem(mem, vertexList, v_addr):
    addr=0
    for iter in range(len(vertexList)):
        print("Writing Vertex:%d" % vertexList[iter].id)
        addr=v_addr[iter][1]
        mem.write_word(addr, vertexList[iter].size)
        mem.write_word(addr+4, vertexList[iter].id)
        print("0x%x:%d" % (addr, mem.read_word(addr)))
        print("0x%x:%d" % (addr+4, mem.read_word(addr+4)))
        for i in range(vertexList[iter].size):
            n_addr = 0
            for j, verts in enumerate(v_addr):
                print("Test:j:i=%d:%d"% (j,i))
                print(verts)
                if(verts[0]==vertexList[iter].neighbors[i]):
                    n_addr = verts[1]
                    print("Found naddr{0:d}:0x{1:016x}".format(verts[0], verts[1]))
                    break
            mem.write_word(addr+8+8*i, n_addr & 0xffffffff) # Lower 32 bits 
            mem.write_word(addr+8+12*i, (n_addr & 0xffffffff00000000)>>32) # upper 32 bits
            print("0x%x:%x" % (addr+8+8*i, mem.read_word(addr+8+8*i)))
            print("0x%x:%x" % (addr+8+12*i, mem.read_word(addr+8+12*i)))

def createMemfromGraphfile(graphfile, undirected, mem, baseaddr):
    path_filename = os.path.split(graphfile)
    outgraph = "output/" + str(path_filename[1]) + ".out"
    g, NodeMap = GenGraph(graphfile, undirected, outgraph)
    node_addr, array_addr, final_addr = CreateMemFromGraph(mem, g, NodeMap, undirected, baseaddr)
    return g, NodeMap, node_addr, array_addr, final_addr


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--igraph", help="Input Graph", required=True)
    parser.add_argument("--undirected", help="graph is undirected or directed", action="store_true")
    args = parser.parse_args()
    path_filename = os.path.split(args.igraph)
    outgraph = "output/" + str(path_filename[1]) + ".out"
    g, NodeMap = GenGraph(args.igraph, args.undirected, outgraph)
    baseaddr = 0
    mem = DramMemory(1048576)
    node_addr =  CreateMemFromGraph(mem, g, NodeMap, args.undirected, baseaddr)
    #mem.dump_memory("output/memout")


    #vertlist = GenVertList('/home/andronicus/upstream/Snap-6.0/examples/graphgen/output.txt')
    #print(str(vertlist))
    #v_addr = calcAddrfromVertList(vertlist)
    #for v in v_addr:
    #    print("{0:d}:0x{1:016x}".format(v[0], v[1]))
    #mem = DramMemory(1048576)
    #writeVertListMem(mem, vertlist,v_addr)

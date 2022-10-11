import sys
import os
#root =  os.environ['TBTROOT']
#sys.path.append(root+'/src/libraries/service/snappy/udp_kernel/UdpSnappyFrontEnd/')
from SnappyWriter import *
from EFA import *


def GenerateUncompressed():
    efa = EFA([])
    efa.code_level = 'machine'
    state0 = State() #Initial State?
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State()
    efa.add_state(state1)
    efa.alphabet = range(0,256)
    state2 = State()   #state2 checks the compression flag
    efa.add_state(state2)
    #snappy
    state3 = State()
    efa.add_state(state3)
    state4 = State() 
    efa.add_state(state4) 
    #end of snappy
    state5 = State()       # state4 is the state that should be activated at the end of block
    efa.add_state(state5) 


    #Add events to dictionary 
    event_map = {
        'start_event':0,
        'data_recieved':1,
        'decomp':2     ,
        'final':3     #,
    }
    # UDPR_12: event word
    # UDPR_13: lane
    # UDPR_1: LM starting position
    # UDPR_14: block size
    # UDPR_11: 
    # UDPR_3:
    tran = state0.writeTransition("eventCarry", state0, state1, event_map['start_event'])
# read the operand buffer
    tran.writeAction("mov_ob2reg OB_0 UDPR_1")				#0 read LM initial location
    tran.writeAction("mov_ob2reg OB_1 UDPR_14")                          #1 read output block size
    tran.writeAction("mov_ob2ear OB_2_3 EAR_0")                         #2 dram addr
    #tran.writeAction("mov_ob2reg OB_4 UDPR_10")                          #3 read the SBPB initial advancing #
    tran.writeAction("mov_imm2reg UDPR_3 0")                            #3 (dram) reading iterator
    tran.writeAction("mov_reg2reg UDPR_1 UDPR_5")                       #4  lm writing iterator
    tran.writeAction("mov_imm2reg UDPR_11 0")                            #4  writing iterator
    #tran.writeAction("mov_imm2reg UDPR_0 0" )
    tran.writeAction("mov_imm2reg UDPR_12 "+str(event_map['data_recieved']))  #5 
    tran.writeAction("mov_imm2reg UDPR_13 2" ) # Lane 2                #6
    tran.writeAction("send_old UDPR_12 UDPR_13 UDPR_3 4 r 1")               #7  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran.writeAction("addi UDPR_3 UDPR_3 4")                            #8 Dram iterator
    tran.writeAction("blt UDPR_3 UDPR_14 #8")                             #9 Dram iterator
    tran.writeAction("yield 1")                                         #10 

    tran = state1.writeTransition("eventCarry", state1, state1, event_map['data_recieved'])
    tran.writeAction("mov_ob2reg OB_0 UDPR_6")                          #0 read dram data
    tran.writeAction("put_bytes UDPR_6 UDPR_5 4")			#1 put data in LM   (TODO: should use put_bytes!!)
    tran.writeAction("addi UDPR_11 UDPR_11 4")                            #2 LM iterator
    tran.writeAction("bge UDPR_11 UDPR_14 #5")                             #3    
    tran.writeAction("yield 1")                                        #4 (TODO: check yield argument)

    tran.writeAction("mov_imm2reg UDPR_12 "+str(event_map['decomp']))  #5 
    tran.writeAction("send_old UDPR_12 UDPR_13 UDPR_3 4 r 0")              #UDPR_3 is irrelevant  #7  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran.writeAction("yield 1")                                        #4 (TODO: check yield argument)

   # transiting to a state with basic property
    tran = state1.writeTransition("basic_with_action", state1, state2, event_map['decomp'])
    #tran.writeAction("subi UDPR_1 SBPB 1")                       #4  SBP to the beginning of LM block, and advance some bytes to start from the beginning of new block
    tran.writeAction("addi UDPR_1 SBPB 0")                       #4  SBP to the beginning of LM block, and advance some bytes to start from the beginning of new block
    tran.writeAction("subi SBPB SBPB 1")                       #4  SBP to the beginning of LM block
#    tran.writeAction("yield_terminate 1")
#---------------------- snappy -----------------


    tran = state2.writeTransition("commonCarry", state2, state5, 0)
    #tran.writeAction("addi SBPB SBPB 1")                       #4  nest block starts from the next data
    tran.writeAction("addi UDPR_14 UDPR_3 1")                       # UDPR_3: relatove address of the start of the next block in DRAM
    tran.writeAction("send_old final TOP UDPR_3 4 w 0")
    tran.writeAction("send_old final TOP UDPR_1 4 w 0")                 # UDPR_1: Address that Top reads the result
    tran.writeAction("yield_terminate 1")

    tran = state2.writeTransition("commonCarry_with_action", state2, state3, 1)
    tran.writeAction("mov_reg2reg UDPR_5 UDPR_11")  #keep the start of Top read in LM 
    scanFirstTagByte(state3, state4)
    CopyLiteral(state4, state3)
    CopyMatchTag01(state4, state3)
    CopyMatchTag10(state4, state3)

    tran = state4.writeTransition("commonCarry_with_action", state4, state5, 255)
    #tran.writeAction("addi SBPB SBPB 1")                       #4  nest block starts from the next data
    tran.writeAction("sub SBPB UDPR_1 UDPR_3")                       # UDPR_3: relatove address of the start of the next block in DRAM
    tran.writeAction("send_old final TOP UDPR_3 4 w 0")
    tran.writeAction("send_old final TOP UDPR_11 4 w 0")		     # UDPR_11: Address that Top reads the result
    tran.writeAction("yield_terminate 1")

    return efa


def DRAMtoScratch_old():
    efa = EFA([])
    efa.code_level = 'machine'
    state0 = State() #Initial State?
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State()
    efa.add_state(state1)
    efa.alphabet = range(0,256)
    state2 = State()   #state2 checks the compression flag
    efa.add_state(state2)
    #snappy
    state3 = State()
    efa.add_state(state3)
    state4 = State() 
    efa.add_state(state4) 
    #end of snappy
    state5 = State()       # state4 is the state that should be activated at the end of block
    efa.add_state(state5) 


    #Add events to dictionary 
    event_map = {
        'start_event':0,
        'data_recieved':1,
        'decomp':2     ,
        'final':3     #,
    }
    # UDPR_12: event word
    # UDPR_13: lane
    # UDPR_1: LM starting position
    # UDPR_14: block size
    # UDPR_11: 
    # UDPR_3:
    tran = state0.writeTransition("eventCarry", state0, state1, event_map['start_event'])
# read the operand buffer
    tran.writeAction("mov_ob2reg OB_0 UDPR_1")				#0 read LM initial location
    tran.writeAction("mov_ob2reg OB_1 UDPR_14")                          #1 read output block size
    tran.writeAction("mov_ob2ear OB_2_3 EAR_0")                         #2 dram addr
    #tran.writeAction("mov_ob2reg OB_4 UDPR_10")                          #3 read the SBPB initial advancing #
    tran.writeAction("mov_imm2reg UDPR_3 0")                            #3 (dram) reading iterator
    tran.writeAction("mov_reg2reg UDPR_1 UDPR_5")                       #4  lm writing iterator
    tran.writeAction("mov_imm2reg UDPR_11 0")                            #4  writing iterator
    #tran.writeAction("mov_imm2reg UDPR_0 0" )
    tran.writeAction("mov_imm2reg UDPR_12 "+str(event_map['data_recieved']))  #5 
    tran.writeAction("mov_imm2reg UDPR_13 -1" ) # Lane 2                #6
    tran.writeAction("send_old UDPR_12 UDPR_13 UDPR_3 4 r 1")               #7  UDPR7 - event_word, UDPR_11 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran.writeAction("addi UDPR_3 UDPR_3 4")                            #8 Dram iterator
    tran.writeAction("blt UDPR_3 UDPR_14 8")                             #9 Dram iterator
    tran.writeAction("yield 1")                                         #10 

    tran = state1.writeTransition("eventCarry", state1, state1, event_map['data_recieved'])
    tran.writeAction("mov_ob2reg OB_0 UDPR_6")                          #0 read dram data
    tran.writeAction("put_bytes UDPR_6 UDPR_5 4")			#1 put data in LM   (TODO: should use put_bytes!!)
    tran.writeAction("addi UDPR_11 UDPR_11 4")                            #2 LM iterator
    tran.writeAction("bge UDPR_11 UDPR_14 5")                             #3    
    tran.writeAction("yield 1")                                        #4 (TODO: check yield argument)

    tran.writeAction("mov_imm2reg UDPR_10 1")          #2 UDPR_10 is set to 1 to update program status
    tran.writeAction("subi UDPR_1 UDPR_12 12")         #1 pointer for updating the program status in LM
    tran.writeAction("put_bytes UDPR_10 UDPR_12 4") # UDPR_10 program status
    tran.writeAction("yield_terminate 1")

    return efa

def GenerateUncompressed_snappy():
    efa = EFA([])
    efa.code_level = 'machine'
    state0 = State() #Initial State?
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State()
    efa.add_state(state1)
    efa.alphabet = range(0,256)
    state2 = State()   #state2 checks the compression flag
    efa.add_state(state2)
    #snappy
    state3 = State()
    efa.add_state(state3)
    state4 = State() 
    efa.add_state(state4) 
    #end of snappy
    state5 = State()       # state4 is the state that should be activated at the end of block
    efa.add_state(state5) 


    #Add events to dictionary 
    event_map = {
        'start_event':0,
        'data_recieved':1,
        'decomp':2     ,
        'final':3     #,
    }
    # UDPR_1: LM starting address for processing
    # UDPR_14: block size
    # UDPR_3: dram reading iterator , 
    # UDPR_5: LM writing pointer
    # UDPR_11: LM writing iterator
    # UDPR_12: event word
    # UDPR_13: lane
    # UDPR_6: recieved DRAM data


    # (UDPR_13): pointer for writing the result into LM (to be accessed by TOP)
    # (UDPR_12): pointer for updating the status when the program is done
    # UDPR_8: temporary value to calculate UDPR+1 that shows the beginning of uncompressed block in LM
    # (UDPR_10): is set to 1 fpr updating program status

    tran = state0.writeTransition("eventCarry", state0, state1, event_map['start_event'])
# read the operand buffer
    tran.writeAction("mov_ob2reg OB_0 UDPR_1")				#0 read LM initial location
    tran.writeAction("mov_ob2reg OB_1 UDPR_14")                          #1 read output block size
    tran.writeAction("mov_ob2ear OB_2_3 EAR_0")                         #2 dram addr
    tran.writeAction("mov_imm2reg UDPR_3 0")                            #3 (dram) reading iterator
    tran.writeAction("mov_reg2reg UDPR_1 UDPR_5")                       #4  lm writing iterator
    tran.writeAction("mov_imm2reg UDPR_11 0")                            #5  writing iterator
    tran.writeAction("mov_imm2reg UDPR_12 "+str(event_map['data_recieved']))  #6 
    tran.writeAction("mov_imm2reg UDPR_13 -1" ) # Lane -1 since its send_old  #7
    tran.writeAction("send_old UDPR_12 UDPR_13 UDPR_3 4 r 1")               #8  UDPR12 - event_word, UDPR_13 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran.writeAction("addi UDPR_3 UDPR_3 4")                            #9 Dram iterator
    tran.writeAction("blt UDPR_3 UDPR_14 #8")                             #10 Dram iterator checking
    tran.writeAction("yield 1")                                         #11 

    tran = state1.writeTransition("eventCarry", state1, state1, event_map['data_recieved'])
    tran.writeAction("mov_ob2reg OB_0 UDPR_6")                          #0 read dram data
    tran.writeAction("put_bytes UDPR_6 UDPR_5 4")			#1 put data in LM 
    tran.writeAction("addi UDPR_11 UDPR_11 4")                            #2 LM iterator
    tran.writeAction("bge UDPR_11 UDPR_14 #5")                             #3    
    tran.writeAction("yield 1")                                        #4 (TODO: check yield argument)

    tran.writeAction("mov_imm2reg UDPR_12 "+str(event_map['decomp']))  #5 
    tran.writeAction("send_old UDPR_12 UDPR_3 UDPR_13 4 w 0")          #6     #UDPR_3 is irrelevant 
    tran.writeAction("yield 1")                                        #7 (TODO: check yield argument)

   # transiting to a state with basic property
    tran = state1.writeTransition("basic_with_action", state1, state2, event_map['decomp'])
    tran.writeAction("subi UDPR_1 UDPR_13 8")          #0 pointer for writing the result in LM ( Word_1: size of processed compressed data, Word_2: result block LM address)
    tran.writeAction("subi UDPR_1 UDPR_12 12")         #1 pointer for updating the program status in LM
    tran.writeAction("mov_imm2reg UDPR_10 1")          #2 UDPR_10 is set to 1 to update program status
    tran.writeAction("subi UDPR_1 SBPB 1")            #3  SBP to the beginning of LM block, and advance some bytes to start from the beginning of new block
#    tran.writeAction("addi UDPR_1 SBPB 0")                     #3  SBP to the beginning of LM block, and advance some bytes to start from the beginning of new block
#    tran.writeAction("subi SBPB SBPB 1")                       #3  SBP to the beginning of LM block
#    tran.writeAction("yield_terminate 1")
#---------------------- snappy -----------------


    tran = state2.writeTransition("commonCarry", state2, state5, 0)
    tran.writeAction("addi UDPR_14 UDPR_3 1")                       # UDPR_3: size of processed data (the block is uncompressed and size is blocksize) 
#    tran.writeAction("send_old final TOP UDPR_3 4 w 0")
#    tran.writeAction("send_old final TOP UDPR_1 4 w 0")                 # UDPR_1: Address that Top reads the result
######TOP CAN ONLY READ FROM THE LM
    tran.writeAction("put_bytes UDPR_3 UDPR_13 4") # UDPR_3 the number of processed elements
    tran.writeAction("addi UDPR_1 UDPR_8 1")      # UDPR_8: the block is uncompressed and location is UDPR_1 +1
    tran.writeAction("put_bytes UDPR_8 UDPR_13 4") # UDPR_1 address of the resulting block in LM
    tran.writeAction("put_bytes UDPR_10 UDPR_12 4") # UDPR_10 program status
    tran.writeAction("yield_terminate 1")

    tran = state2.writeTransition("commonCarry_with_action", state2, state3, 1)
    tran.writeAction("mov_reg2reg UDPR_5 UDPR_11")  #keep the address of the resulting block (start of Top read) in LM
    scanFirstTagByte(state3, state4)
    CopyLiteral(state4, state3)
    CopyMatchTag01(state4, state3)
    CopyMatchTag10(state4, state3)

    tran = state4.writeTransition("commonCarry_with_action", state4, state5, 255)
    tran.writeAction("sub SBPB UDPR_1 UDPR_3")                       # UDPR_3:size of processed data (block is uncompressed and size is less than blocksize)
#    tran.writeAction("send_old final TOP UDPR_3 4 w 0")
#    tran.writeAction("send_old final TOP UDPR_11 4 w 0")		     # UDPR_11: Address that Top reads the result
######TOP CAN ONLY READ FROM THE LM
    tran.writeAction("put_bytes UDPR_3 UDPR_13 4") # UDPR_3 the number of processed elements
    tran.writeAction("put_bytes UDPR_11 UDPR_13 4") # UDPR_11 address of the resulting block in LM
    tran.writeAction("put_bytes UDPR_10 UDPR_12 4") # UDPR_10 program status
    tran.writeAction("yield_terminate 1")


    return efa


def DRAMtoScratch_batched():
    efa = EFA([])
    efa.code_level = 'machine'
    state0 = State() #Initial State?
    efa.add_initId(state0.state_id)
    efa.add_state(state0)
    state1 = State()
    efa.add_state(state1)
    efa.alphabet = range(0,256)


    #Add events to dictionary
    event_map = {
        'start_event':0,
        'data_recieved':1,
        'send_batch':2,
        'decomp':3     ,
        'final':4     #,
    }
    # UDPR_1: LM starting address for processing
    # UDPR_14: block size
    # UDPR_3: dram reading iterator ,
    # UDPR_5: LM writing pointer
    # UDPR_11: LM writing iterator
    # UDPR_12: event word
    # UDPR_13: lane
    # UDPR_6: recieved DRAM data
    # UDPR_7: 1024: batch size
    # UDPR_8: batct stride counter


    tran = state0.writeTransition("eventCarry", state0, state1, event_map['start_event'])
# read the operand buffer
    tran.writeAction("mov_ob2reg OB_0 UDPR_1")                          #0 read LM initial location
    tran.writeAction("mov_ob2reg OB_1 UDPR_14")                          #1 read output block size
    tran.writeAction("mov_ob2ear OB_2_3 EAR_0")                         #2 dram addr
    tran.writeAction("mov_imm2reg UDPR_3 0")                            #3 (dram) reading iterator
    tran.writeAction("mov_reg2reg UDPR_1 UDPR_5")                       #4  lm writing iterator
    tran.writeAction("mov_imm2reg UDPR_7 1024")                            #5
    tran.writeAction("mov_reg2reg UDPR_7 UDPR_8")                       #6
    tran.writeAction("mov_imm2reg UDPR_11 0")                            #7  writing iterator
    tran.writeAction("mov_imm2reg UDPR_12 "+str(event_map['data_recieved']))  #8
    tran.writeAction("mov_imm2reg UDPR_13 -1" ) # Lane -1 since its send_old  #
#    tran.writeAction("mov_imm2reg UDPR_13 2" ) # Lane -1 since its send_old  #9
    tran.writeAction("send_old UDPR_12 UDPR_13 UDPR_3 4 r 1")               #10  UDPR12 - event_word, UDPR_13 - Lane ID, UDPR_3 - addr_offset, 4 - sz, r - read, 1 - addr_mode (EAR0)
    tran.writeAction("addi UDPR_3 UDPR_3 4")                            #11 Dram iterator
    tran.writeAction("blt UDPR_3 UDPR_8 10")                             #12 Dram iterator checking
    tran.writeAction("yield 1")                                         #13

    tran = state1.writeTransition("eventCarry", state1, state1, event_map['data_recieved'])
    tran.writeAction("mov_ob2reg OB_0 UDPR_6")                          #0 read dram data
    tran.writeAction("put_bytes UDPR_6 UDPR_5 4")                       #1 put data in LM
    tran.writeAction("addi UDPR_11 UDPR_11 4")                            #2 LM iterator
    tran.writeAction("bge UDPR_11 UDPR_7 5")                             #3
    tran.writeAction("yield 1")                                        #4 (TODO: check yield argument)
    tran.writeAction("mov_imm2reg UDPR_11 0")                            #5
    tran.writeAction("bge UDPR_3 UDPR_14 10")                             #6
    tran.writeAction("mov_imm2reg UDPR_12 "+str(event_map['send_batch']))  #7
    tran.writeAction("send_old UDPR_12 UDPR_13 UDPR_3 4 r 0")          #8     #UDPR_3 is irrelevant
    tran.writeAction("yield 1")                                         #9
    tran.writeAction("yield_terminate 1")                               #10

    tran = state1.writeTransition("eventCarry", state1, state1, event_map['send_batch'])
    tran.writeAction("add UDPR_8 UDPR_7 UDPR_8")                            #0
    tran.writeAction("mov_imm2reg UDPR_12 "+str(event_map['data_recieved']))  #1
    tran.writeAction("send_old UDPR_12 UDPR_13 UDPR_3 4 r 1")               #2
    tran.writeAction("addi UDPR_3 UDPR_3 4")                            #3
    tran.writeAction("blt UDPR_3 UDPR_8 2")                             #4
    tran.writeAction("yield 1")                                         #5

    return efa


if __name__=="__main__":
    efa = GenerateTriEFA()
    #efa.printOut(error)
    

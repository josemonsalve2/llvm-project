from EFA import *
import math
from  abc import *
from macro import *
import traceback

class MapReduceTemplate:
    '''
    Parameters
        task_name:      String label of the event to initialize the map reduce task
        num_workers:    Int value ranging from [1-64], number of the workers allocated to this map reduce task
    '''
    def __init__(self, task_name, num_workers):
        self.task = task_name
        self.efa = EFA([])
        self.efa.code_level = 'machine'
        
        self.state = State() #Initial State
        self.efa.add_initId(self.state.state_id)
        self.efa.add_state(self.state)

        self.event_map = {}   
        self.num_events = 0
        self.get_event_mapping(self.task)
        self.num_workers = 64 if num_workers > 64 else num_workers
    
    '''
    Set up the input key-value map's metadata, the kvmap is stored in DRAM.
    Parameters
        in_kvmap_ptr:       Pointer to a scratchpad location storing the DRAM address of input key-value map
        in_kvmap_length_ptr:Pointer to a scratchpad location storing the length of the input key-value map
        in_kvpair_size:     Size (in bytes) of an input key-value pair
    '''
    def set_input_kvmap(self, kvmap_ptr, kvmap_length, kvpair_size):
        self.in_kvmap_ptr = kvmap_ptr
        self.in_kvmap_length_ptr = kvmap_length
        self.in_kvpair_size = kvpair_size
    
    '''
    Set up the output key-value map's metadata, the kvmap is stored in DRAM.
    Parameters
        out_kvmap_ptr:      Pointer to a scratchpad location storing the DRAM address of output key-value map
        out_kvmap_length:   Pointer to a scratchpad location storing the length of the output key-value map
        out_kvpair_size:    Size (in bytes) of an output key-value pair
    '''
    def set_output_kvmap(self, kvmap_ptr, kvmap_length, kvpair_size):
        self.out_kvmap_ptr = kvmap_ptr
        self.out_kvmap_length = kvmap_length
        self.out_kvpair_size = kvpair_size
    
    '''
    Set up the mapper and reducer counter for termination detection
    Parameters
        map_ctr_offset:     offset to the local bank for number of kv_pair produceed by the mapper
        reduce_ctr_offset:  offset to the loval bank for number of kv_pair processed by the reducer
    '''
    def set_termination_ctr(self, map_ctr_offset, reduce_ctr_offset):
        # only specify the offset, termination counter should be per work private 
        self.map_ctr_offset = map_ctr_offset
        self.reduce_ctr_offset = reduce_ctr_offset
    
    '''
    If the reduce function involves read-modify-write a DRAM location, it needs a per-lane-private hash
    table to merge updates to the same location (i.e. intermediate kvpair with the same key) to avoid conflict
    Parameters
        table_offset:   the table's base address / offset relative to the local bank  
        num_entries:    number of entries for each of the hash table
        entry_size:     the size of a hash table entry
        inval:          default value for empty/invalid entry 
    '''
    def setup_table(self, table_offset, num_entries, entry_size, inval):
        self.enable_merge = True
        self.tb_offset = table_offset
        self.tb_size = num_entries
        self.tb_entry_size = entry_size
        self.tb_inval = inval
        
    '''
    Given a string label, retrieve the corresponding event id.
    If the event label does not exist in the mapping, add it to the mapping and return the event id.
    Parameter
        label:          string label
    Ouput
        the corresponding event id mapped to the input label
    '''
    def get_event_mapping(self, label):
        if label not in self.event_map:
            self.event_map[label] = self.num_events
            self.num_events += 1
        return self.event_map[label]

    def setup_task(self):
        tran = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping(self.task))
        tran.writeAction("mov_imm2reg UDPR_0 0")
        # Initialize termination counters (private per worker)
        for n in range(self.num_workers):
            tran.writeAction(f"mov_imm2reg UDPR_1 {n}")
            tran.writeAction(f"lshift_add_imm UDPR_1 UDPR_2 16 {self.map_ctr_offset}")
            tran.writeAction("mov_reg2lm UDPR_0 UDPR_1 4")
            tran.writeAction(f"lshift_add_imm UDPR_1 UDPR_2 16 {self.reduce_ctr_offset}")
            tran.writeAction("mov_reg2lm UDPR_0 UDPR_1 4")
        
        #Initialize the hash table in scratchpad memory to merge RMW updates
        if self.enable_merge:
            tran.writeAction(f"mov_imm2reg UDPR_0 {self.tb_inval}")
            for n in range(self.num_workers):
                tran.writeAction(f"mov_imm2reg UDPR_1 {n}")
                tran.writeAction(f"lshift_add_imm UDPR_1 UDPR_1 16 {self.tb_offset}")
                tran.writeAction(f"addi UDPR_1 UDPR_2 {self.tb_size * self.tb_entry_size}")
                tran.writeAction("init_tb_loop: mov_reg2lm UDPR_0 UDPR_1")
                tran.writeAction(f"addi UDPR_1 UDPR_1 {self.tb_entry_size}")
                tran.writeAction("blt UDPR_1 UDPR_2 init_tb_loop")

        tran.writeAction(f"mov_imm2reg UDPR_0 {self.in_kvmap_ptr}")
        tran.writeAction("mov_lm2ear UDPR_0 EAR_0 8")
        tran.writeAction(f"mov_imm2reg UDPR_1 {self.in_kvmap_length_ptr}")
        tran.writeAction("mov_lm2reg UDPR_0 UDPR_0 4")
        tran.writeAction("mov_imm2reg UDPR_2 0")
        tran.writeAction(f"loop: lshift_and_imm UDPR_2 UDPR_3 {math.log2(self.in_kvpair_size)} 4294967295")
        tran.writeAction(f"ev_update_2 UDPR_5 {self.get_event_mapping('map_event')} 255 5")
        tran.writeAction("lshift_and_imm UDPR_2 UDPR_6 0 %d" % (self.num_workers-1))
        tran.writeAction(f"ev_update_reg_2 UDPR_5 UDPR_5 UDPR_6 UDPR_6 8")
        tran.writeAction(f"send_dmlm_ld UDPR_4 UDPR_6 {self.in_kvpair_size} 0")
        tran.writeAction("blt UDPR_2 UDPR_1 loop")
        tran.writeAction("yield_terminate 0 16")

        map_tran = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping('map_event'))
        inter_key, inter_value = self.map_function(self, map_tran, "OB_0", ["OB_%d"%n for n in range(math.log2(self.in_kvpair_size)-1)])

        
        if self.enable_merge: self.load_and_merge(inter_key, inter_value)

        tran_term = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping('store_ack'))
        tran_term.writeAction(f"lshift_add_imm LID UDPR_12 16 {self.reduce_ctr_offset}")
        tran_term.writeAction("mov_lm2reg UDPR_12 UDPR_13 4")
        tran_term.writeAction("addi UDPR_13 UDPR_13 1")
        tran_term.writeAction("mov_reg2lm UDPR_13 UDPR_12 4")
        tran_term.writeAction("yield_terminate 0 16")
        # self.reduce_function(self, "OB_0", "OB_1")

    '''
    User defined map function. It takes an key-value pair and produce one (or more) key-value pair(s).
    Parameters
        tran:       transition (codelet) triggered by the map event
        key:        the name of the register/operand buffer entry which contains the input key
        value:      the name of the register/operand buffer entry which contains the input value
    '''
    @abstractmethod
    def map_function(self, tran, key, value):
        dest_id = "UDPR_5"
        self.get_lane_by_key(tran, key, dest_id)
        # user defined map code
        self.collect_to_lane(tran, key, value, dest_id)
        tran.writeAction(f"yield_terminate {math.log2(self.in_kvpair_size)} 16")
        return "OB_0", "OB_1"
    
    '''
    User defined reduce function. It takes an key-value pair generated by the mapper and updates the output value mapped to the given key accordingly.
    Parameters
        tran:       transition (codelet) triggered by the reduce event
        key:        the name of the register/operand buffer entry which contains the intermediate key generated by the mapper
        value:      the name of the register/operand buffer entry which contains the intermediate value generated by the mapper
    Output
        result_reg: the name of the register containing the reduced value to be stored back
    '''
    @abstractmethod
    def reduce_function(self, tran, key, new_value, old_value):
        # user defined reduce code
        result_reg = "UDPR_1"
        tran.writeAction(f"add {new_value} {old_value} {result_reg}")
        return result_reg

    '''
    Helper function for mapper to generate a key-value pair and send it to the corresponding reducer lane 
    based on the user-defined key-lane mapping.
    Parameters:
        tran:       transition (codelet) triggered by the map event
        key:        name of the register/operand buffer entry containing the intermediate key to be sent to the reducer
        value:      name of the register/operand buffer entry containing the intermediate value to be sent to the reducer
    '''
    def collect_to_lane(self, tran, key, value, dest):
        tran.writeAction(f"ev_update_2 UDPR_11 {self.get_event_mapping('mapreduce_merge')} 255 5")
        tran.writeAction(f"ev_update_reg_2 UDPR_11 UDPR_11 {dest} {dest} 8")
        tran.writeAction(f"send4_wcont UDPR_11 {dest} UDPR_11 {key} {value}")
        tran.writeAction(f"lshift_add_imm LID UDPR_12 16 {self.map_ctr_offset}")
        tran.writeAction("mov_lm2reg UDPR_12 UDPR_13 4")
        tran.writeAction("addi UDPR_13 UDPR_13 1")
        tran.writeAction("mov_reg2lm UDPR_13 UDPR_12 4")
        return
    
    '''
    deprecated, now see load_and_merge()
    '''
    def collect_to_dram(self, tran, key, value, dest, event):
        tran.writeAction(f"mov_imm2reg UDPR_0 {self.out_kvmap_ptr}")
        tran.writeAction("mov_lm2ear UDPR_0 EAR_1 8")
        tran.writeAction(f"ev_update_2 UDPR_5 {self.get_event_mapping(event)} 255 5")
        self.get_outkvpair_offset_by_key(self, tran, key, "UDPR_4")
        tran.writeAction("ev_update_reg_2 UDPR_5 UDPR_5 LID LID 8")
        tran.writeAction("send4_dmlm UDPR_4 UDPR_5 UDPR_2 1")

        
        tran.writeAction(f"lshift_add_imm LID UDPR_12 16 {self.map_ctr_offset}")
        tran.writeAction("mov_lm2reg UDPR_12 UDPR_13 4")
        tran.writeAction("addi UDPR_13 UDPR_13 1")
        tran.writeAction("mov_reg2lm UDPR_13 UDPR_12 4")


    '''
    User-defined mapping function from a key to a worker lane id
    Parameter
        tran:       transition (codelet) triggered by the map event
        key:        name of the register/operand buffer entry containing the key
        result:     name of the register reserved for storing the result 
    '''
    def get_lane_by_key(self, tran, key, result):
        tran.writeAction(f"lshift_and_imm {key} {result} 0 {self.num_workers}") 


    '''
    User-defined mapping function from a key to a DRAM address (offset to a base address stored in EAR register
    because send instruction uses (base+offset) indirect addressing mode)
    Parameter
        tran:       transition (codelet) triggered by the reduce event
        key:        name of the register/operand buffer entry containing the key
        result:     name of the register reserved for storing the result 
    '''
    def get_outkvpair_offset_by_key(self, tran, key, result):
        tran.writeAction(f"lshift_and_imm {key} {result} {math.log2(self.out_kvpair_size)} 4294967295")  

    '''
    Before forward the intermediate key-value pair to the user-defined reduce function, the template first check if the local scratchpad already
    stores a pending update (waiting for the output key-value pair coming back from DRAM) to the same key. If there exists, the update will be merged 
    locally based on the user-defined reduce function. If not, the template will insert the update to the hash table in scratchpad and issues a read to 
    retrieve the output key-value pair from DRAM. When the data is ready, the template will apply the accumulated update(s) stores the data back 
    immediately and frees the hash table entry. If there's a hash conflict, the update will be postponed (i.e. append to the end of the event queue) until 
    the entry is freed.
    Parameter:
        key:        name of the operand buffer entry containing the intermediate key received from the mapper
        value:      name of the operand buffer entry containing the intermediate value received from the mapper

    '''
    def load_and_merge(self, key, value):
        merge_tran = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping('mapreduce_merge'))
        merge_tran.writeAction(f"mov_imm2reg UDPR_10 {self.in_kvmap_ptr}")
        merge_tran.writeAction("mov_lm2ear UDPR_10 EAR_0 8")
        merge_tran.writeAction(f"lshift_add_imm LID UDPR_11 16 {self.tb_offset}")    # UDPR_1 <- hash table base addr
        # merge_tran.writeAction(f"addi UDPR_1 UDPR_2 {self.tb_size * self.tb_entry_size}")

        merge_tran.writeAction(f"lshift_and_imm OB_0 UDPR_13 {math.log2(self.tb_entry_size)} {(self.tb_size << math.log2(self.tb_entry_size))-1}")
        merge_tran.writeAction("add UDPR_11 UDPR_13 UDPR_13")                   # UDPR_3 <- addr to load key 
        merge_tran.writeAction("mov_lm2reg UDPR_13 UDPR_14 4")
        merge_tran.writeAction(f"beq UDPR_14 {key} tb_hit")                     # hit
        merge_tran.writeAction(f"beq UDPR_14 {self.tb_inval} tb_insert")        # miss
        merge_tran.writeAction("ev_update_2 UDPR_12 " + str(self.get_event_mapping('mapreduce_merge')) +" 255 5")
        merge_tran.writeAction(f"send4_wcont UDPR_12 LID UDPR_12 {key} {value}")
        merge_tran.writeAction("yield_terminate 2 16")

        merge_tran.writeAction("tb_hit: addi UDPR_13 UDPR_13 4")                  # 13 hit and combine
        merge_tran.writeAction("mov_lm2reg UDPR_13 UDPR_14 4")
        result_reg = self.reduce_function(merge_tran, key, value, "UDPR_14")
        merge_tran.writeAction(f"mov_reg2lm {result_reg} UDPR_13 4")

        merge_tran.writeAction(f"lshift_add_imm LID UDPR_12 16 {self.reduce_ctr_offset}")
        merge_tran.writeAction("mov_lm2reg UDPR_12 UDPR_13 4")
        merge_tran.writeAction("addi UDPR_13 UDPR_13 1")
        merge_tran.writeAction("mov_reg2lm UDPR_13 UDPR_12 4")
        merge_tran.writeAction("yield_terminate 2 16") 

        merge_tran.writeAction(f"tb_insert: mov_reg2lm {key} UDPR_13 4")              # 23
        merge_tran.writeAction("addi UDPR_13 UDPR_13 4")
        merge_tran.writeAction(f"mov_reg2lm {value} UDPR_13 4")
        # merge_tran.writeAction(f"lshift_and_imm {key} UDPR_14 {math.log2(self.out_kvpair_size)} 4294967295")
        self.get_outkvpair_offset_by_key(self, merge_tran, key, "UDPR_14")
        merge_tran.writeAction("ev_update_2 UDPR_15 " + str(self.get_event_mapping('mapreduce_load')) + " 255 5")
        merge_tran.writeAction("send_dmlm_ld UDPR_14 UDPR_15 8 0")        # read current pagerank value from DRAM
        merge_tran.writeAction("yield_terminate 2 16") 

        load_tran = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping('mapreduce_load'))
        load_tran.writeAction(f"mov_imm2reg UDPR_10 {self.in_kvmap_ptr}")
        load_tran.writeAction("mov_lm2ear UDPR_10 EAR_0 8")

        load_tran.writeAction(f"lshift_add_imm LID UDPR_11 16 {self.tb_offset}")    # UDPR_1 <- hash table base addr
        load_tran.writeAction(f"lshift_and_imm OB_0 UDPR_13 {math.log2(self.tb_entry_size)} {(self.tb_size << math.log2(self.tb_entry_size))-1}")
        load_tran.writeAction("add UDPR_11 UDPR_13 UDPR_13")                   # UDPR_3 <- addr to load key 
        load_tran.writeAction("mov_lm2reg UDPR_13 UDPR_14 4")
        result_reg = self.reduce_function(load_tran, "OB_0", "UDPR_14", "OB_1")
        self.get_outkvpair_offset_by_key(self, load_tran, key, "UDPR_11")
        load_tran.writeAction(f"ev_update_2 UDPR_15 {self.get_event_mappting('store_ack')} 255 5")
        load_tran.writeAction("ev_update_reg_2 UDPR_15 UDPR_15 LID LID 8")
        load_tran.writeAction(f"send4_dmlm UDPR_11 UDPR_15 {result_reg} 0")
        load_tran.writeAction(f"yield_terminate {math.log2(self.out_kvpair_size)} 16")
        
'''
Template ends here
-----------------------------------------------------------------------
Below is an naive map reduce example. The map function does nothing but send the unmodified input key-value pair to the reducer. 
The reducer takes the intermediate key-value pairs and sums up all the values correspond to the same key. 
To write a map reduce program using the template, one needs to implement the two abstract method, namely map_function() and reduce_function(), 
instantiate the map reduce task, and set up the metadata required by the template using the provided helper functions.
'''
class NaiveMapReduce(MapReduceTemplate):
    
    def map_function(self, tran, key, value):
        dest_id = "UDPR_5"
        self.get_lane_by_key(tran, key, dest_id)
        # user defined map code
        self.collect_to_lane(tran, key, value, dest_id)
        tran.writeAction(f"yield_terminate {math.log2(self.in_kvpair_size)} 16")
        return "OB_0", "OB_1"

    
    def reduce_function(self, tran, key, new_value, old_value):
        # user defined reduce code
        result_reg = "UDPR_1"
        tran.writeAction(f"add {new_value} {old_value} {result_reg}")
        return result_reg


def GenerateNaiveMapReduceEFA():
    INPUT_KVMAP_PTR_ADDR = 0
    INPUT_KVMAP_LEN_ADDR = 8
    OUTPUT_KVMAP_PTR_ADDR = 16
    OUTPUT_KVMAP_LEN_ADDR = 24

    naiveMP = NaiveMapReduce("naive_map_reduce", 64)
    naiveMP.set_input_kvmap(INPUT_KVMAP_PTR_ADDR, INPUT_KVMAP_LEN_ADDR, kvpair_size=8)
    naiveMP.set_output_kvmap(OUTPUT_KVMAP_PTR_ADDR, OUTPUT_KVMAP_LEN_ADDR, kvpair_size=8)
    naiveMP.set_termination_ctr(map_ctr_offset=64, reduce_ctr_offset=72)
    naiveMP.setup_table(table_offset=1024, num_entries=32, entry_size=8, inval=4294967295)

    naiveMP.setup_task()

    return naiveMP.efa







if __name__=="__main__":
    efa = MapReduceTemplate()
    #efa.printOut(error)
    

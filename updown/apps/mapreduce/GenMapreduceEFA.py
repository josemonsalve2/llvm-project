from EFA import *
import math
from  abc import *
class UDMapReduceTemplate:
    """A template for write MapReduce programs for UpDown

    Extend this class and overwrite the map_function() and reduce_function() with your map and reduce code.

    Typical usage example:

    class ExampleMapReduce(UDMapReduceTemplate):
        
        def map_function(self, tran, key, value):
            # user defined map code
            return ...
        
        def reduce_function(self, tran, key, new_value, old_value):
            # user defined reduce code
            return ...
    """

    def __init__(self, task_name, num_workers):
        '''
        Parameters
            task_name:      String label of the event to initialize the map reduce task
            num_workers:    Int value ranging from [1-64], number of the workers allocated to this map reduce task
        '''

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
        print(f"Initialize MapReduce task {self.task} - number of workers = {self.num_workers}")
    
    def set_input_kvmap(self, kvmap_ptr, kvmap_length, kvpair_size):
        '''
        Set up the input key-value map's metadata, the kvmap is stored in DRAM.
        Parameters
            in_kvmap_ptr:       Pointer to a scratchpad location storing the DRAM address of input key-value map
            in_kvmap_length_ptr:Pointer to a scratchpad location storing the length of the input key-value map
            in_kvpair_size:     Size (in bytes) of an input key-value pair
        '''

        self.in_kvmap_ptr = kvmap_ptr
        self.in_kvmap_length_ptr = kvmap_length
        self.in_kvpair_size = kvpair_size
        self.in_kvpair_shift = int(math.log2(self.in_kvpair_size))
        print(f"Set up input kvmap - base ptr offset: {kvmap_ptr},  length offset: {kvmap_length}, size {kvpair_size} log2 size {self.in_kvpair_shift}")
    
    def set_output_kvmap(self, kvmap_ptr, kvmap_length, kvpair_size):
        '''
        Set up the output key-value map's metadata, the kvmap is stored in DRAM.
        Parameters
            out_kvmap_ptr:      Pointer to a scratchpad location storing the DRAM address of output key-value map
            out_kvmap_length:   Pointer to a scratchpad location storing the length of the output key-value map
            out_kvpair_size:    Size (in bytes) of an output key-value pair
        '''

        self.out_kvmap_ptr = kvmap_ptr
        self.out_kvmap_length = kvmap_length
        self.out_kvpair_size = kvpair_size
        self.out_kvpair_shift = int(math.log2(self.out_kvpair_size))
        print(f"Set up output kvmap - base ptr offset: {kvmap_ptr},  length offset: {kvmap_length}, size {kvpair_size} log2 size {self.out_kvpair_shift}")
    
    def set_termination_ctr(self, map_ctr_offset, reduce_ctr_offset, flag_checking_freq=50):
        '''
        Set up the counters and paramerters required by termination detection logic.
        Only specify the offset to lane private bank base, termination counter should be per lane(worker) private.
        Parameters
            map_ctr_offset:     offset to the local bank for number of kv_pair produceed by the mapper
            reduce_ctr_offset:  offset to the loval bank for number of kv_pair processed by the reducer
            flag_checking_freq: frequency to check the counters to detect termination, higher number means less frequent
        '''
        
        self.map_ctr_offset = map_ctr_offset
        self.reduce_ctr_offset = reduce_ctr_offset
        self.flag_checking_freq = flag_checking_freq
    
    def setup_table(self, table_offset, num_entries, entry_size, inval):
        '''
        If the reduce function involves read-modify-write a DRAM location, it needs a per-lane-private hash
        table to merge updates to the same location (i.e. intermediate kvpair with the same key) to avoid conflict
        Parameters
            table_offset:   the table's base address / offset relative to the local bank  
            num_entries:    number of entries for each of the hash table
            entry_size:     the size of a hash table entry
            inval:          default value for empty/invalid entry 
        '''

        self.enable_merge = True
        self.tb_offset = table_offset
        self.tb_size = num_entries
        self.tb_entry_size = entry_size
        self.tb_inval = inval
        
    def get_event_mapping(self, label):
        '''
        Given a string label, retrieve the corresponding event id.
        If the event label does not exist in the mapping, add it to the mapping and return the event id.
        Parameter
            label:          string label
        Ouput
            the corresponding event id (integer) mapped to the input label
        '''

        if label not in self.event_map:
            self.event_map[label] = self.num_events
            self.num_events += 1
        return self.event_map[label]

    def setup_task(self):
        '''
        Generate the UpDown assembly code for mapreduce task.
        Initialize counters/tables in scratchpad -> fetch kvpairs from input kvmap -> mapreduce main body -> termination checking.
        Note this method only generates the assembly code to be run on UpDown for each event. It doesn't reflect the real execution order of the events.
        '''

        tran = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping(self.task))
        tran.writeAction("addi TS UDPR_15 0")
        tran.writeAction(f"mov_imm2reg UDPR_0 {self.out_kvmap_ptr}")
        tran.writeAction("mov_lm2ear UDPR_0 EAR_0 8")
        tran.writeAction("mov_imm2reg UDPR_0 0")
        # Initialize termination counters (private per worker)
        for n in range(self.num_workers):
            tran.writeAction(f"mov_imm2reg UDPR_1 {n}")
            tran.writeAction(f"lshift_add_imm UDPR_1 UDPR_2 16 {self.map_ctr_offset}")
            tran.writeAction("mov_reg2lm UDPR_0 UDPR_2 4")
            tran.writeAction(f"lshift_add_imm UDPR_1 UDPR_2 16 {self.reduce_ctr_offset}")
            tran.writeAction("mov_reg2lm UDPR_0 UDPR_2 4")
        
        #Initialize the hash table in scratchpad memory to merge Read-Modify-Write updates and ensure TSO
        if self.enable_merge:
            tran.writeAction(f"mov_imm2reg UDPR_0 {self.tb_inval}")
            for n in range(self.num_workers):
                # print(f"Initialize lane {n}'s hash table in scratchpad memory")
                tran.writeAction(f"mov_imm2reg UDPR_1 {n}")
                tran.writeAction(f"lshift_add_imm UDPR_1 UDPR_1 16 {self.tb_offset}")
                tran.writeAction(f"addi UDPR_1 UDPR_2 {self.tb_size * self.tb_entry_size}")
                tran.writeAction(f"init_tb_loop{n}: mov_reg2lm UDPR_0 UDPR_1 4")
                tran.writeAction(f"addi UDPR_1 UDPR_1 {self.tb_entry_size}")
                tran.writeAction(f"blt UDPR_1 UDPR_2 init_tb_loop{n}")

        # Fetch the kvpairs fromt the input kvmap and send to the workers
        tran.writeAction(f"mov_imm2reg UDPR_0 {self.in_kvmap_ptr}")
        tran.writeAction("mov_lm2ear UDPR_0 EAR_0 8")
        tran.writeAction(f"mov_imm2reg UDPR_13 {self.in_kvmap_length_ptr}")
        tran.writeAction("mov_lm2reg UDPR_13 UDPR_13 4")    # UDPR_13 <- input kvmap length
        tran.writeAction("mov_imm2reg UDPR_2 0")            # UDPR_2 <- issue counter
        tran.writeAction(f"issue_loop: lshift_and_imm UDPR_2 UDPR_3 {self.in_kvpair_shift} 4294967295")
        tran.writeAction(f"ev_update_2 UDPR_5 {self.get_event_mapping('map_event')} 255 5")
        tran.writeAction(f"lshift_and_imm UDPR_2 UDPR_6 0 {(self.num_workers-1)}")
        tran.writeAction(f"ev_update_reg_2 UDPR_5 UDPR_5 UDPR_6 UDPR_6 8")
        tran.writeAction(f"send_dmlm_ld UDPR_3 UDPR_5 {self.in_kvpair_size} 0")
        tran.writeAction("addi UDPR_2 UDPR_2 1")
        tran.writeAction("blt UDPR_2 UDPR_13 issue_loop")

        tran.writeAction("mov_imm2reg UDPR_12 0")
        tran.writeAction(f"ev_update_1 EQT UDPR_11 {self.get_event_mapping('term_checking_event')} 1")
        tran.writeAction("send4_wcont UDPR_11 LID TS UDPR_12 UDPR_12")
        tran.writeAction("yield 1")

        # This thread will run on the background and periodically check the progress of the mapper and reducer.
        term_tran = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping('term_checking_event'))
        term_tran.writeAction(f"blt OB_0 {self.flag_checking_freq} skip")   # flag_checking_freq controls the frequency to check the flag
        term_tran.writeAction("mov_imm2reg UDPR_12 0")
        term_tran.writeAction("mov_imm2reg UDPR_0 0")
        term_tran.writeAction("mov_imm2reg UDPR_1 0")
        term_tran.writeAction("mov_imm2reg UDPR_2 0")
        # check the status of each worker, i.e., the number kvpair generated by mapper and consumed by reducer respectively
        term_tran.writeAction(f"term_loop: lshift_add_imm UDPR_0 UDPR_3 16 {self.map_ctr_offset}")
        term_tran.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
        term_tran.writeAction("add UDPR_1 UDPR_4 UDPR_1")
        term_tran.writeAction(f"lshift_add_imm UDPR_0 UDPR_3 16 {self.reduce_ctr_offset}")
        term_tran.writeAction("mov_lm2reg UDPR_3 UDPR_4 4")
        term_tran.writeAction("add UDPR_2 UDPR_4 UDPR_2")
        term_tran.writeAction("addi UDPR_0 UDPR_0 1")
        term_tran.writeAction(f"blt UDPR_0 {self.num_workers} term_loop")
        term_tran.writeAction("beq UDPR_2 UDPR_13 terminate")               # if Num of updates processed by reducer == input kvmap length?
        term_tran.writeAction("skip: addi UDPR_12 UDPR_12 1")
        term_tran.writeAction(f"ev_update_1 EQT UDPR_11 {self.get_event_mapping('term_checking_event')} 1")
        term_tran.writeAction("send4_wcont UDPR_11 LID TS UDPR_12 UDPR_12")
        term_tran.writeAction("yield 2")

        term_tran.writeAction("terminate: mov_imm2reg UDPR_0 1")            # finish the map reduce task return to the continuation specified by the user 
        # term_tran.writeAction("send4_reply UDPR_0")
        term_tran.writeAction("ev_update_1 UDPR_15 UDPR_15 255 4")
        term_tran.writeAction("send4_wcont UDPR_15 LID UDPR_15 UDPR_0")
        term_tran.writeAction("yield_terminate 2 16")

        # Set up the map code 
        map_tran = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping('map_event'))
        inter_key, inter_value = self.map_function( map_tran, "OB_0", [f"OB_{n+1}" for n in range(self.in_kvpair_shift-1)])
        map_tran.writeAction(f"yield_terminate {self.in_kvpair_shift} 16")

        # Set up the shuffle and reduce code
        if self.enable_merge: self.load_and_merge(inter_key, inter_value)


    @abstractmethod
    def map_function(self, tran, key, value):
        '''
        User defined map function. It takes an key-value pair and produce one (or more) key-value pair(s).
        Parameters
            tran:       transition (codelet) triggered by the map event
            key:        the name of the register/operand buffer entry which contains the input key
            value:      the name of the register/operand buffer entry which contains the input value
        '''

        dest_id = "UDPR_5"                      # The lane id where the intermediate kvmap to be sent is stored in UDPR_5
        self.get_lane_by_key(tran, key, dest_id)
        # user defined map code
        self.collect_to_lane(tran, key, value, dest_id)
        return "OB_0", [f"OB_{n+1}" for n in range(self.in_kvpair_shift-1)]
    
    @abstractmethod
    def reduce_function(self, tran, key, new_value, old_value):
        '''
        User defined reduce function. It takes an key-value pair generated by the mapper and updates the output value mapped to the given key accordingly.
        Parameters
            tran:       transition (codelet) triggered by the reduce event
            key:        the name of the register/operand buffer entry which contains the intermediate key generated by the mapper
            value:      the name of the register/operand buffer entry which contains the intermediate value generated by the mapper
        Output
            result_reg: the name of the register containing the reduced value to be stored back
        '''

        # user defined reduce code
        return new_value

    def collect_to_lane(self, tran, key, value, dest):
        '''
        Helper function for mapper to generate a key-value pair and send it to the corresponding reducer lane 
    Helper function for mapper to generate a key-value pair and send it to the corresponding reducer lane 
        Helper function for mapper to generate a key-value pair and send it to the corresponding reducer lane 
        based on the user-defined key-lane mapping.
        Parameters:
            tran:       transition (codelet) triggered by the map event
            key:        name of the register/operand buffer entry containing the intermediate key to be sent to the reducer
            value:      name of the register/operand buffer entry containing the intermediate value to be sent to the reducer
            dest:       name of the register reserved for the destination reducer id 
        dest:       name of the register reserved for the destination reducer id 
            dest:       name of the register reserved for the destination reducer id 
        '''

        tran.writeAction(f"ev_update_2 UDPR_11 {self.get_event_mapping('mapreduce_merge')} 255 5")
        tran.writeAction(f"ev_update_reg_2 UDPR_11 UDPR_11 {dest} {dest} 8")
        tran.writeAction(f"send4_wcont UDPR_11 {dest} UDPR_11 {key} {value}")
        tran.writeAction(f"lshift_add_imm LID UDPR_12 16 {self.map_ctr_offset}")
        tran.writeAction("mov_lm2reg UDPR_12 UDPR_13 4")
        tran.writeAction("addi UDPR_13 UDPR_13 1")
        tran.writeAction("mov_reg2lm UDPR_13 UDPR_12 4")


    def get_lane_by_key(self, tran, key, result):
        '''
        User-defined mapping function from a key to a worker lane id
        Parameter
            tran:       transition (codelet) triggered by the map event
            key:        name of the register/operand buffer entry containing the key
            result:     name of the register reserved for storing the result 
        result:     name of the register reserved for storing the result 
            result:     name of the register reserved for storing the result 
        '''

        tran.writeAction(f"lshift_and_imm {key} {result} 0 {self.num_workers-1}") 


    def get_outkvpair_offset_by_key(self, tran, key, offset):
        '''
        User-defined mapping function from a key to a DRAM address (offset to a base address stored in EAR register
        because send instruction uses (base+offset) indirect addressing mode)
        Parameter
            tran:       transition (codelet) triggered by the reduce event
            key:        name of the register/operand buffer entry containing the key
            offset:     name of the register reserved for storing the DRAM offset  
        offset:     name of the register reserved for storing the DRAM offset  
            offset:     name of the register reserved for storing the DRAM offset  
        '''

        tran.writeAction(f"lshift_and_imm {key} {offset} {self.out_kvpair_shift} 4294967295")  

    def load_and_merge(self, key, value):
        '''
        Before forward the intermediate key-value pair to the user-defined reduce function, the template first check if the local scratchpad already
        stores a pending update (waiting for the output key-value pair coming back from DRAM) to the same key. If there exists, the update will be merged 
    stores a pending update (waiting for the output key-value pair coming back from DRAM) to the same key. If there exists, the update will be merged 
        stores a pending update (waiting for the output key-value pair coming back from DRAM) to the same key. If there exists, the update will be merged 
        locally based on the user-defined reduce function. If not, the template will insert the update to the hash table in scratchpad and issues a read to 
    locally based on the user-defined reduce function. If not, the template will insert the update to the hash table in scratchpad and issues a read to 
        locally based on the user-defined reduce function. If not, the template will insert the update to the hash table in scratchpad and issues a read to 
        retrieve the output key-value pair from DRAM. When the data is ready, the template will apply the accumulated update(s) stores the data back 
    retrieve the output key-value pair from DRAM. When the data is ready, the template will apply the accumulated update(s) stores the data back 
        retrieve the output key-value pair from DRAM. When the data is ready, the template will apply the accumulated update(s) stores the data back 
        immediately and frees the hash table entry. If there's a hash conflict, the update will be postponed (i.e. append to the end of the event queue) until 
    immediately and frees the hash table entry. If there's a hash conflict, the update will be postponed (i.e. append to the end of the event queue) until 
        immediately and frees the hash table entry. If there's a hash conflict, the update will be postponed (i.e. append to the end of the event queue) until 
        the entry is freed.
        Parameter:
            key:        name of the operand buffer entry containing the intermediate key received from the mapper
            value:      name of the operand buffer entry containing the intermediate value received from the mapper

        '''

        # Triggered when the reducer receives an intermediate kvpair from the mapper.
        merge_tran = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping('mapreduce_merge'))
        merge_tran.writeAction(f"mov_imm2reg UDPR_10 {self.out_kvmap_ptr}")
        merge_tran.writeAction("mov_lm2ear UDPR_10 EAR_1 8")
        merge_tran.writeAction(f"lshift_add_imm LID UDPR_11 16 {self.tb_offset}")    # UDPR_1 <- hash table base addr
        # merge_tran.writeAction(f"addi UDPR_1 UDPR_2 {self.tb_size * self.tb_entry_size}")

        merge_tran.writeAction(f"lshift_and_imm OB_0 UDPR_13 {int(math.log2(self.tb_entry_size))} \
            {(self.tb_size << int(math.log2(self.tb_entry_size)))-1}")
        merge_tran.writeAction("add UDPR_11 UDPR_13 UDPR_13")                   # UDPR_3 <- addr to load key 
        merge_tran.writeAction("mov_lm2reg UDPR_13 UDPR_14 4")
        merge_tran.writeAction(f"beq UDPR_14 {key} tb_hit")                     # hit
        merge_tran.writeAction(f"beq UDPR_14 {self.tb_inval} tb_insert")        # miss
        merge_tran.writeAction(f"ev_update_2 UDPR_12 {self.get_event_mapping('mapreduce_merge')} 255 5")
        merge_tran.writeAction(f"send4_wcont UDPR_12 LID UDPR_12 {key} {value}")
        merge_tran.writeAction("yield_terminate 2 16")

        merge_tran.writeAction("tb_hit: addi UDPR_13 UDPR_13 4")                  # 13 hit and combine
        merge_tran.writeAction("mov_lm2reg UDPR_13 UDPR_14 4")
        result_reg = self.reduce_function(merge_tran, key, value, old_value="UDPR_14")
        merge_tran.writeAction(f"mov_reg2lm {result_reg} UDPR_13 4")

        # Update the counter: number of kvpair processed by reducer ++
        merge_tran.writeAction(f"lshift_add_imm LID UDPR_12 16 {self.reduce_ctr_offset}")
        merge_tran.writeAction("mov_lm2reg UDPR_12 UDPR_13 4")
        merge_tran.writeAction("addi UDPR_13 UDPR_13 1")
        merge_tran.writeAction("mov_reg2lm UDPR_13 UDPR_12 4")
        merge_tran.writeAction(f"yield_terminate {self.out_kvpair_shift} 16") 

        # hashtable miss, insert the value to the table
        merge_tran.writeAction(f"tb_insert: mov_reg2lm {key} UDPR_13 4")
        merge_tran.writeAction("addi UDPR_13 UDPR_13 4")
        merge_tran.writeAction(f"mov_reg2lm {value} UDPR_13 4")
        # Retrieve the DRAM address of the output kvpair corresponding to {key} based on the default/user-defined key-to-offset mapping
        self.get_outkvpair_offset_by_key( merge_tran, key, "UDPR_14")
        merge_tran.writeAction("ev_update_2 UDPR_15 " + str(self.get_event_mapping('mapreduce_load')) + " 255 5")
        merge_tran.writeAction("send_dmlm_ld UDPR_14 UDPR_15 8 1")        # read current pagerank value from DRAM
        merge_tran.writeAction(f"yield_terminate {self.out_kvpair_shift} 16") 

        # Triggered when the old output kvpair is read from DRAM and ready to perform the (accumulated) updates
        load_tran = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping('mapreduce_load'))
        load_tran.writeAction(f"mov_imm2reg UDPR_10 {self.out_kvmap_ptr}")
        load_tran.writeAction("mov_lm2ear UDPR_10 EAR_1 8")

        load_tran.writeAction(f"lshift_add_imm LID UDPR_11 16 {self.tb_offset}")    # UDPR_1 <- hash table base addr
        load_tran.writeAction(f"lshift_and_imm OB_0 UDPR_13 {int(math.log2(self.tb_entry_size))} {(self.tb_size << int(math.log2(self.tb_entry_size)))-1}")
        load_tran.writeAction("add UDPR_11 UDPR_13 UDPR_13")                        # UDPR_3 <- addr to load key 
        load_tran.writeAction("mov_lm2reg UDPR_13 UDPR_14 4")
        # Apply the accumulated updates based on user-defined reduce funtion 
        result_reg = self.reduce_function(load_tran, "OB_0", new_value="OB_1", old_value="UDPR_14")
        self.get_outkvpair_offset_by_key(load_tran, key, offset="UDPR_11")
        load_tran.writeAction(f"ev_update_2 UDPR_15 {self.get_event_mapping('store_ack')} 255 5")
        load_tran.writeAction("ev_update_reg_2 UDPR_15 UDPR_15 LID LID 8")
        load_tran.writeAction(f"send4_dmlm UDPR_11 UDPR_15 {result_reg} 1")
        load_tran.writeAction(f"yield_terminate {self.out_kvpair_shift} 16")

        # Triggered when the write comes back from DRAM, increment the reduce counter by 1
        tran_term = self.state.writeTransition("eventCarry", self.state, self.state, self.get_event_mapping('store_ack'))
        tran_term.writeAction(f"lshift_add_imm LID UDPR_12 16 {self.reduce_ctr_offset}")
        tran_term.writeAction("mov_lm2reg UDPR_12 UDPR_13 4")
        tran_term.writeAction("addi UDPR_13 UDPR_13 1")
        tran_term.writeAction("mov_reg2lm UDPR_13 UDPR_12 4")
        tran_term.writeAction("yield_terminate 0 16")
        
'''
Template ends here
-----------------------------------------------------------------------
Below is an naive map reduce example. The map function does nothing but send the unmodified input key-value pair to the reducer. 
The reducer takes the intermediate key-value pairs and sums up all the values correspond to the same key. 
To write a map reduce program using the template, one needs to implement the two abstract method, namely map_function() and reduce_function(), 
instantiate the map reduce task, and set up the metadata required by the template using the provided helper functions.
'''
class NaiveMapReduce(UDMapReduceTemplate):
    
    def map_function(self, tran, key, value):
        dest_id = "UDPR_5"                      # Register UDPR_5 stores the lane id where the intermediate kvmap will be sent to
        self.get_lane_by_key(tran, key, dest_id)
        # user defined map code
        self.collect_to_lane(tran, key, value[0], dest_id)
        return "OB_0", "OB_1"

    
    def reduce_function(self, tran, key, new_value, old_value):
        # user defined reduce code
        result_reg = "UDPR_1"                   # The updated value is stored in register UDPR_1
        tran.writeAction(f"add {new_value} {old_value} {result_reg}")
        return result_reg


def GenerateNaiveMapReduceEFA():
    INPUT_KVMAP_PTR_ADDR = 0
    INPUT_KVMAP_LEN_ADDR = 8
    OUTPUT_KVMAP_PTR_ADDR = 16
    OUTPUT_KVMAP_LEN_ADDR = 24
    TERM_FLAG_ADDR = 128

    naiveMP = NaiveMapReduce(task_name="naive_map_reduce", num_workers=4)
    naiveMP.set_input_kvmap(INPUT_KVMAP_PTR_ADDR, INPUT_KVMAP_LEN_ADDR, kvpair_size=8)
    naiveMP.set_output_kvmap(OUTPUT_KVMAP_PTR_ADDR, OUTPUT_KVMAP_LEN_ADDR, kvpair_size=8)
    naiveMP.set_termination_ctr(map_ctr_offset=64, reduce_ctr_offset=72)
    naiveMP.setup_table(table_offset=1024, num_entries=4, entry_size=8, inval=4294967295)

#   operands
#   OB_0_1: Pointer to inKVMap (64-bit DRAM address)
#   OB_2_3: Pointer to outKVMap (64-bit DRAM address) 
#   OB_4: Input kvmap length
#   OB_5: Output kvmap length (== number of unique keys in the inKBMap)
#   OB_6: sizeof(KVpair)
    init_tran = naiveMP.state.writeTransition("eventCarry", naiveMP.state, \
        naiveMP.state, naiveMP.get_event_mapping('updown_init'))
    init_tran.writeAction("mov_ob2ear OB_0_1 EAR_0")
    init_tran.writeAction("mov_ob2ear OB_2_3 EAR_1")
    init_tran.writeAction(f"mov_imm2reg UDPR_1 {INPUT_KVMAP_PTR_ADDR}")
    init_tran.writeAction(f"mov_ear2lm EAR_0 UDPR_1 8")
    init_tran.writeAction(f"mov_imm2reg UDPR_1 {OUTPUT_KVMAP_PTR_ADDR}")
    init_tran.writeAction(f"mov_ear2lm EAR_1 UDPR_1 8")
    init_tran.writeAction(f"mov_imm2reg UDPR_1 {INPUT_KVMAP_LEN_ADDR}")
    init_tran.writeAction(f"mov_reg2lm OB_4 UDPR_1 4")
    init_tran.writeAction(f"mov_imm2reg UDPR_1 {OUTPUT_KVMAP_LEN_ADDR}")
    init_tran.writeAction(f"mov_reg2lm OB_5 UDPR_1 4")
    init_tran.writeAction(f"ev_update_2 UDPR_9 {naiveMP.get_event_mapping(naiveMP.task)} 255 5")
    init_tran.writeAction(f"send4_wret UDPR_9 LID {naiveMP.get_event_mapping('updown_terminate')} OB_4")
    init_tran.writeAction("mov_imm2reg UDPR_0 0") 
    init_tran.writeAction("yield 7")

    # User defined continuation to be triggered when the mapreduce task finishes. 
    term_tran = naiveMP.state.writeTransition("eventCarry", naiveMP.state, \
        naiveMP.state, naiveMP.get_event_mapping('updown_terminate'))
    term_tran.writeAction("mov_imm2reg UDPR_5 1")
    term_tran.writeAction(f"mov_imm2reg UDPR_6 {TERM_FLAG_ADDR}")
    term_tran.writeAction("mov_reg2lm UDPR_5 UDPR_6 4")
    term_tran.writeAction("yield_terminate 1 16")

    naiveMP.setup_task()

    # print out the event mapping (for debugging)
    print("Event mapping: ", naiveMP.event_map)

    return naiveMP.efa


if __name__=="__main__":
    efa = UDMapReduceTemplate()
    #efa.printOut(error)
    
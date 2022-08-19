/*
 * Copyright (c) 2021 University of Chicago and Argonne National Laboratory
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Author - Andronicus
 *
 *
 */

#ifndef UPDOWN_H
#define UPDOWN_H
#include "debug.h"
#include "updown_config.h"
#include <cstdio>
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <utility>


namespace UpDown
{
    
  typedef uint32_t word_t;
  typedef word_t * ptr_t;

  static constexpr uint8_t ANY_THREAD = 0xFF;

  /**
   * @brief Class that holds information about the operands.
   *
   * Contains a pointer to data and the number of operands. 
   * data is an array of ptr_t, representing each word in the
   * operand buffer when copied.
   * 
   * NumOperands is 8 bits long. Up to 256 operands are allowed
   *
   */
  class operands_t {
    private:
      uint8_t NumOperands;
      ptr_t Data;

    public:

      /**
       * @brief Construct a new empty operands_t object
       * 
       * Set the Data pointer to null and NumOperands to 0
       */
      operands_t() : NumOperands(0), Data(nullptr) {}

      /**
       * @brief Copy Constructor
       * 
       * @param o other object
       */
      operands_t(const operands_t &o) :
      NumOperands(o.NumOperands),
      Data((ptr_t)malloc(sizeof(word_t) * (NumOperands + 1))) {
        // Copy the data
        if (NumOperands != 0)
          std::memcpy(o.Data, Data, sizeof(word_t) * (NumOperands + 1));
      }

      /**
       * @brief Copy Constructor
       * 
       * @param o other object
       */
      operands_t(operands_t && o) :
        NumOperands(o.NumOperands), 
        Data(o.Data) {
          // Reset the other operand's pointer
          o.Data = nullptr;
        }

      /**
       * @brief Construct a new operands_t opbejct, setting the operands
       *
       * @param num Number of operaqnds
       * @param oper Operand value
       * @param cont Continuation event
       * 
       * @todo This should avoid using memcpy
       */
      operands_t(uint8_t num, ptr_t oper = nullptr, word_t cont = 0):
        NumOperands(num), 
        Data((ptr_t)malloc(sizeof(word_t) * (NumOperands + 1))) { // TODO: Avoid this malloc

          Data[0] = cont; // Fake continuation

          // TODO: This should be a memcpy?
          for (uint8_t i = 1; i < NumOperands + 1; i++)
            Data[i] = oper[i - 1];
      }

      /**
       * @brief Get the pointer to Data
       * 
       * @return ptr_t pointer to data
       */
      ptr_t get_Data() { return Data; }

      /**
       * @brief Get the NumOperands
       * 
       * @return uint8_t number of operands
       */
      uint8_t get_NumOperands() { return NumOperands; }

      ~operands_t() 
      {
        delete Data;
      }
  };


  /**
   * @brief Contains information of an event in the UpDown
   * 
   * This class constructs the information of the event word based on
   * each of its parameters. It also contains a pointer to the operands
   * that is used when sending the event
   * 
   * @todo the event word may not be needed the lane_id. 
   *
   */
  class event_t {
    private:
      uint8_t UdId; // UpDown ID
      uint8_t LaneId; // Lane ID
      uint8_t ThreadId; // Thread ID. ANY_THREAD for any thread
      uint8_t EventLabel; // Number representing the event label
      
      operands_t *Operands; // Operands to be sent with this event

      word_t EventWord; // Concatenated event word that contains all the fields

    public:
      /**
       * @brief Construct a new empty event object
       *
       */
      event_t() : 
        UdId(0), 
        LaneId(0),
        ThreadId(0xFF),
        EventLabel(0),
        Operands(nullptr),
        EventWord(((LaneId << 24) & 0xff000000) | ((ThreadId << 16) & 0xff0000) |
                  ((0 << 8) & 0xff00) | (EventLabel & 0xff))
        {
          UPDOWN_INFOMSG("Creating a new event label = %d, lane_id = %d, "
                        "thread_id = %d, num_operands = %d, ev_word = %X",
                        EventLabel, LaneId, ThreadId, 0, EventWord);
        }

      /**
       * @brief Construct a new event_t object
       * 
       * @param e_label 
       * @param udid 
       * @param lid 
       * @param tid 
       * @param operands 
       */
      event_t(uint8_t e_label, uint8_t udid,  uint8_t lid = 0,
                    uint8_t tid = ANY_THREAD, operands_t *operands = nullptr) : 
        UdId(udid), 
        LaneId(lid),
        ThreadId(tid),
        EventLabel(e_label),
        Operands(operands),
        EventWord(((LaneId << 24) & 0xff000000) | ((ThreadId << 16) & 0xff0000) |
                  (((Operands != nullptr ? Operands->get_NumOperands() : 0) << 8) & 0xff00) | (EventLabel & 0xff))
        {
          UPDOWN_INFOMSG("Creating a new event label = %d, lane_id = %d, "
                        "thread_id = %d, num_operands = %d, ev_word = %X",
                        EventLabel, LaneId, ThreadId, 
                        (Operands != nullptr) ? Operands->get_NumOperands() : 0, EventWord);
        }

      /**
       * @brief Set the event word object with new values
       *
       * @param e_label the ID of the event in the updown
       * @param noperands the number of operands
       * @param lid Lane ID
       * @param tid Thread ID
       */
      void set_event(uint8_t e_label, uint8_t udid,  uint8_t lid = 0,
                        uint8_t tid = ANY_THREAD, operands_t *operands = nullptr) {
        EventLabel = e_label;
        LaneId = lid;
        UdId = udid;
        ThreadId = tid;
        Operands = operands;
        EventWord = ((LaneId << 24) & 0xff000000) | ((ThreadId << 16) & 0xff0000) |
                  (((Operands != nullptr ? Operands->get_NumOperands() : 0) << 8) & 0xff00) | (EventLabel & 0xff);
        UPDOWN_INFOMSG("Setting the event word = %d, lane_id = %d, "
                      "thread_id = %d, num_operands = %d, ev_word = %X",
                      EventLabel, LaneId, ThreadId, (Operands != nullptr) ? Operands->get_NumOperands() : 0, EventWord);
      }

      /**
       * @brief Get the event word object
       *
       * @return word_t with the event word
       */
      word_t get_EventWord() { return EventWord; }

      operands_t* get_Operands() { return Operands; }

      void set_operands(operands_t *ops) { Operands = ops; }
      uint8_t get_UdId() { return UdId; }
      uint8_t get_LaneId() { return LaneId; }
      uint8_t get_ThreadId() { return ThreadId; }
      uint8_t get_EventLabel() { return EventLabel; }
      uint8_t get_NumOperands() { return (Operands != nullptr) ? Operands->get_NumOperands() : 0; }
      ptr_t get_OperandsData() { return (Operands != nullptr) ? Operands->get_Data() : nullptr; }
    };


    /**
     * @brief Class containing the UpDown Runtime
     * 
     * This class is the entry point of the UpDown runtime, it manages all
     * the necessary state, keeps track of pointers and memory allocation
     * and coordinates execution of code.
     * 
     */

    class UDRuntime_t {
      private:

        /**
         * @brief Struct containing all the base addresses
         * 
         * @todo This should not be consecutive memory locations
         * 
         * Base addresses are locations in memory where the 
         * top to updown communication happens. 
         * 
         * eaddr:  Event Queue Addresses. One address per lane.
         *         writing to this address pushes a new event word
         *         into the queue
         * oaddr:  Operand Queue Addresses. One address per lane.
         *         writing to this address pushes a new operand word
         *         into the queue
         * saddr:  Scartchpad memory address base. points to the
         *         initial location of the scratchpad memory.
         * sbaddr: StreamingBuffer memory address base. Points to the
         *         initial location of the streaming buffer memory.
         * exec:   Execute signals. Triggers event execution. Tells the
         *         lane that it can begin executing an updown event.
         *         One signal per lane.
         * locks:  Lock for the updown operands queue. Since operands
         *         must be inserted atomically into the operands queue, 
         *         this lock guarantees atomicity in such operation. Queue
         *         is locked prior to inserting the operands, and unlocked
         *         after finishing inserting the operands. One lock per lane
         * 
         * Current Memory Structure
         * 
         *        MEMORY       SIZE
         *   |--------------|
         *   |              |
         *   |  SCRATCHPAD  |  NUMUDS * NUM_LANES * LMBANK_SIZE
         *   |              |
         *   |--------------|
         *   |              |
         *   |   STREAMING  |  NUMUDS * NUM_LANES * LMBANK_SIZE
         *   |    BUFFERS   |
         *   |              |
         *   |--------------|
         *   |              |
         *   |   EVENTS Q   |  NUMUDS * NUM_LANES
         *   |              |
         *   |--------------|
         *   |              |
         *   |  OPERANDS Q  |  NUMUDS * NUM_LANES
         *   |              |
         *   |--------------|
         *   |              |
         *   |  START EXEC  |  NUMUDS * NUM_LANES
         *   |              |
         *   |--------------|
         *   |              |
         *   |    LOCKS     |  NUMUDS * NUM_LANES
         *   |              |
         *   |--------------|
         */
        struct base_addr_t {
          volatile ptr_t eaddr; 
          volatile ptr_t oaddr; 
          volatile ptr_t saddr; 
          volatile ptr_t sbaddr;
          volatile ptr_t exec;
          volatile ptr_t locks;
        };

        struct ud_abstract_machine_t {
          uint64_t Ubase = UBASE;
          uint64_t MapBase = MAPBASE;
          uint64_t SBase = SBASE;
          uint64_t EBase = EBASE;
          uint64_t OBase = OBASE;
          uint64_t ExecBase = EXEC;
          uint64_t StatBase = STATBASE;
          uint64_t NumUDs = NUMUDS;
          uint64_t NumLanes = NUMLANES;
          uint64_t MemSize = MEMSIZE;
          uint64_t LMBankSize = LMBANK_SIZE;
          uint64_t LMBankSize4b = LMBANK_SIZE_4B;
        };

        /**
         * @brief container for all base addresses
         * 
         */
        base_addr_t BaseAddrs;

        /**
         * @brief Contains configuration parameters of the machine abstraction
         * 
         */
        ud_abstract_machine_t AbstractMachine;

        /**
         * @brief Initializes the base addresses for queues and states
         * 
         * This function initializes BaseAddrs according to the configuration
         * file for their use in the rest of the runtime
         *
         */
        void calc_addrmap();

        /**
         * @brief
         *
         * @param num
         * @return uint32_t
         */
        uint32_t change_endian(uint32_t num);

        /**
         * @brief Get the aligned offset object
         * 
         * @param ud_id 
         * @param lane_num 
         * @param offset 
         * @return uint64_t 
         */
        uint64_t inline get_aligned_offset(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0);

      public:

        UDRuntime_t() {
          calc_addrmap();
        }

        /**
         * @brief Sends an event to the UpDown
         * 
         * Sends a new event to the updown event queues. Information about the
         * destination of the event is defined in the ev parameter, including
         * destination UD_ID, lane_id, thread_id. The event_t also contains the 
         * operands
         *
         * @param ev the event to be sent
         */
        void send_event(event_t ev);

        /**
         * @brief Signal lane to start execution
         *
         * @param lane_num lane to signal
         */
        void start_exec(uint8_t ud_id, uint8_t lane_num);

        /**
         * @brief Copy data from the top to the scratchpad memory
         *
         * This function sends data to the bank associated with the lane_num
         * The address is calculated based on the offset.
         * 
         * @param ud_id UpDown number
         * @param lane_num lane bank
         * @param offset offset within bank
         * @param size_num_words The number of words to be copied to the scratchpad memory
         * @param data pointer to the top data to be copied over to the lane
         */
        void t2ud_memcpy(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0, uint64_t size = 1, ptr_t data = nullptr);

        /**
         * @brief Copy data from the scratchpad memory to the top
         * 
         * @param ud_id UpDown number
         * @param lane_num lane bank
         * @param offset offset within bank
         * @param size_num_words The number of words to be copied from the scratchpad memory
         * @param data pointer to the top data to be contain values from the scratchpad memory
         */
        void ud2t_memcpy(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0, uint64_t size = 1, ptr_t data = nullptr);

        /**
         * @brief Copy data to the streaming buffers
         *
         * @param ud_id UpDown number
         * @param lane_num lane streaming buffer
         * @param offset offset within streaming buffer
         * @param size_num_words the number of words to be copied to the lane's streamming buffer
         * @param data pointer to the top data to be copied over to the lane's streamming buffer
         */
        void sb_t2ud_memcpy(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0, uint64_t size = 1, ptr_t data = nullptr);

        /**
         * @brief Copy data from the streaming buffers to the top
         * 
         * TODO: This probably does not make sense
         *
         * @param ud_id UpDown number
         * @param lane_num lane streaming buffer
         * @param offset offset within streaming buffer
         * @param size_num_words the number of words to be copied to the lane's streamming buffer
         * @param data pointer to the top data to be copied over to the lane's streamming buffer
         */
        void sb_ud2t_memcpy(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0, uint64_t size = 1, ptr_t data = nullptr);

        /**
         * @brief Test a memory location in the updwon bank for the expected value
         * 
         * Reads the updown scratchpad memory bank, and check if the value is equal to the
         * expected value. Returns true if the values are equal
         * 
         * @param ud_id UpDown number
         * @param lane_num LaneID to check
         * @param offset offset within the memory bank
         * @param expected value that is expected in the memory bank
         * @return word_t 
         */
        bool test_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0, word_t expected = 1);

        /**
         * @brief Test a memory location in the updown bank for the expected value. Wait until it is the expected value
         * 
         * Spinwaiting on a location of the updown scratchpad memory bank until the value read 
         * is the expected value. Uses lane_test_memory. 
         * 
         * @param lane_num LaneID to check
         * @param offset offset within the memory bank
         * @param expected value that is expected in the memory bank
         */
        void test_wait_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0, word_t expected = 1);

              /**
         * @brief Test a memory location in the updwon bank for the expected value
         * 
         * Reads the updown scratchpad memory bank, and check if the value is equal to the
         * expected value. Returns true if the values are equal
         * 
         * @param ud_id UpDown number
         * @param lane_num LaneID to check
         * @param offset offset within the memory bank
         * @param expected value that is expected in the memory bank
         * @return word_t 
         */
        bool test_sb_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0, word_t expected = 1);

        /**
         * @brief Test a memory location in the updown bank for the expected value. Wait until it is the expected value
         * 
         * Spinwaiting on a location of the updown scratchpad memory bank until the value read 
         * is the expected value. Uses lane_test_memory. 
         * 
         * @param lane_num LaneID to check
         * @param offset offset within the memory bank
         * @param expected value that is expected in the memory bank
         */
        void test_wait_sb_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset = 0, word_t expected = 1);

  };


} // Name Space UpDown


#endif

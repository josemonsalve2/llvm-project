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
#include <cstdlib>
#include <cstdint>

typedef uint32_t *ptr;
extern volatile uint32_t *eaddr;  //= (uint32_t *)(UBASE+EBASE);
extern volatile uint32_t *oaddr;  //= (uint32_t *)(UBASE+OBASE);
extern volatile uint32_t *saddr;  //= (uint32_t *)(UBASE+SBASE);
extern volatile uint32_t *sbaddr; //= (uint32_t *)(UBASE+SBASE);
extern volatile uint32_t *exec;   //= (uint32_t *)(UBASE+EXEC);
extern volatile uint32_t *status; //= (uint32_t *)(UBASE+STATBASE);

/**
 * @brief
 *
 * @param num_lanes
 * @param memsize
 */
void calc_addrmap(int num_lanes, uint64_t memsize);

/**
 * @brief Contains information of an event in the UpDown system
 *
 */
struct event {
  uint8_t event_label;
  uint8_t lane_id;
  uint8_t thread_id;
  uint8_t num_operands;
  uint32_t ev_word;

  /**
   * @brief Construct a new empty event object
   *
   */
  event(void) {
    event_label = 0;
    lane_id = 0;
    thread_id = 0xff;
    num_operands = 0;
    ev_word = ((lane_id << 24) & 0xff000000) | ((thread_id << 16) & 0xff0000) |
              ((num_operands << 8) & 0xff00) | (event_label & 0xff);
    UPDOWN_INFOMSG("Creating a new event label = %d, lane_id = %d, "
                   "thread_id = %d, num_operands = %d, ev_word = %X",
                   event_label, lane_id, thread_id, num_operands, ev_word);
  }

  /**
   * @brief Set the event word object with new values
   *
   * @param e_label the ID of the event in the updown
   * @param noperands the number of operands
   * @param lid Lane ID
   * @param tid Thread ID
   */
  void setevent_word(uint8_t e_label, uint8_t noperands, uint8_t lid = 0,
                     uint8_t tid = 0xff) {
    event_label = e_label;
    num_operands = noperands;
    lane_id = lid;
    thread_id = tid;
    ev_word = ((lane_id << 24) & 0xff000000) | ((thread_id << 16) & 0xff0000) |
              ((num_operands << 8) & 0xff00) | (event_label & 0xff);
    UPDOWN_INFOMSG("Setting the event word = %d, lane_id = %d, "
                   "thread_id = %d, num_operands = %d, ev_word = %X",
                   event_label, lane_id, thread_id, num_operands, ev_word);
  }

  /**
   * @brief Get the event word object
   *
   * @return uint32_t with the event word
   */
  uint32_t getevent_word(void) { return ev_word; }
};

/**
 * @brief Struct that holds information about the operands.
 *
 * Contains a pointer to data and the number of operands.
 *
 */
struct operands {
  uint32_t *data;
  uint8_t num_operands;

  /**
   * @brief Set the operands
   *
   * @param num Nunber of operaqnds
   * @param oper Operand value
   * @param cont Continuation event
   */
  void setoperands(uint8_t num, uint32_t *oper, uint32_t cont = 0) {
    num_operands = num;
    data = (uint32_t *)malloc(sizeof(uint32_t) * (num_operands + 1));
    data[0] = cont; // Fake continuation

    // TODO: This should be a memcpy?
    for (uint8_t i = 1; i < num_operands + 1; i++)
      data[i] = oper[i - 1];
  }
};

typedef struct event event_t;
typedef struct operands operands_t;

/**
 * @brief
 *
 * @param lane_num
 * @param ev
 */
void send_event(uint32_t lane_num, event_t ev);

/**
 * @brief
 *
 * @param lane_num
 * @param op
 */
void send_operands(uint32_t lane_num, operands_t op);

/**
 * @brief
 *
 * @param lane_num
 */
void start_exec(uint32_t lane_num);

/**
 * @brief
 *
 * @param lane_num
 * @param offset
 * @param value
 */
void init_lane(uint32_t lane_num, uint32_t offset = 0, uint32_t value = 0);

/**
 * @brief
 *
 * @param lane_num
 * @param offset
 * @param value
 */
void init_lane_sb(uint32_t lane_num, uint32_t offset = 0, uint32_t value = 0);

/**
 * @brief
 *
 * @param lane_num
 * @param offset
 * @return uint32_t
 */
uint32_t check_lane(uint32_t lane_num, uint32_t offset = 0);

/**
 * @brief
 *
 * @param lane_num
 * @param offset
 * @return uint32_t
 */
uint32_t check_lane_sb(uint32_t lane_num, uint32_t offset = 0);

/**
 * @brief
 *
 * @param lane_num
 * @param offset
 * @return uint32_t
 */
uint32_t getresult(uint32_t lane_num, uint32_t offset = 0);

/**
 * @brief Get the result sb object
 *
 * @param lane_num
 * @param offset
 * @return uint32_t
 */
uint32_t getresult_sb(uint32_t lane_num, uint32_t offset = 0);

/**
 * @brief Get the result sb byte object
 *
 * @param lane_num
 * @param offset
 * @return uint32_t
 */
uint32_t getresult_sb_byte(uint32_t lane_num, uint32_t offset = 0);

/**
 * @brief
 *
 * @param num
 * @return uint32_t
 */
uint32_t change_endian(uint32_t num);

/**
 * @brief
 *
 * @param num_operands
 * @param operands
 * @param elabel
 * @param lane_num
 */
void launch_upstream_kernel(uint32_t num_operands, uint32_t *operands,
                            uint8_t elabel, uint32_t lane_num);

#endif

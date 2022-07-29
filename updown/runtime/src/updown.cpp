#include "updown.h"
#include <cstdio>
#include <cstdlib>

void calc_addrmap(int num_lanes, uint64_t memsize) {
  uint64_t ubase = memsize;
  saddr = (uint32_t *)ubase;
  sbaddr = (uint32_t *)(ubase + num_lanes * LMBANK_SIZE);
  eaddr = (uint32_t *)(ubase + 2 * num_lanes * LMBANK_SIZE);
  oaddr = (uint32_t *)(eaddr + 64);
  exec = (uint32_t *)(oaddr + 64);
  status = (uint32_t *)(exec + 64);

  UPDOWN_INFOMSG("calc_addrmap: ubase:%lx\nsaddr:%lx\nsbaddr:%lx\n"
                 "eaddr:%lx\noaddr:%lx\nexec:%lx\nstatus:%lx\n",
                 ubase, saddr, sbaddr, eaddr, oaddr, exec, status);
}

void send_event(uint32_t lane_num, event_t ev) {
  *(eaddr + lane_num) = ev.ev_word;
}

void send_operands(uint32_t lane_num, operands_t op) {
  *(status + lane_num) = 1;
  for (uint8_t i = 0; i < op.num_operands + 1; i++) {
    *(oaddr + lane_num) = op.data[i];
    UPDOWN_INFOMSG("OB[%d]:%d,", i, op.data[i]);
  }
  *(status + lane_num) = 0;
}

void start_exec(uint32_t lane_num) { *(exec + lane_num) = 1; }

void init_lane(uint32_t lane_num, uint32_t offset, uint32_t value) {
  *(saddr + LMBANK_SIZE_4B * lane_num + offset) = value;
}

uint32_t check_lane(uint32_t lane_num, uint32_t offset) {
  return *(saddr + LMBANK_SIZE_4B * lane_num + offset);
}

uint32_t getresult(uint32_t lane_num, uint32_t offset) {
  UPDOWN_INFOMSG("getresult:%lx\n", saddr+LMBANK_SIZE_4B*lane_num+offset);
  return *(saddr + LMBANK_SIZE_4B * lane_num + offset);
}

void init_lane_sb(uint32_t lane_num, uint32_t offset, uint32_t value) {
  // UPDOWN_INFOMSG("sbaddr:%lx, lane_num:%d, value:%d\n");
  *(sbaddr + LMBANK_SIZE_4B * lane_num + offset) = value;
}

uint32_t check_lane_sb(uint32_t lane_num, uint32_t offset) {
  return *(sbaddr + LMBANK_SIZE_4B * lane_num + offset);
}

uint32_t getresult_sb(uint32_t lane_num, uint32_t offset) {
  UPDOWN_INFOMSG("getresult:%lx\n", saddr+LMBANK_SIZE_4B*lane_num+offset);
  return *(sbaddr + LMBANK_SIZE_4B * lane_num + offset);
}

uint32_t getresult_sb_byte(uint32_t lane_num, uint32_t offset) {
  UPDOWN_INFOMSG("getresult:%lx\n", saddr+LMBANK_SIZE_4B*lane_num+offset);
  uint32_t result = *(sbaddr + LMBANK_SIZE_4B * lane_num + offset / 4);
  if ((offset / 4) * 4 == offset)
    return result;
  else if ((offset - (offset / 4) * 4) == 1) {
    UPDOWN_INFOMSG("***1 res: %lx (%d)\n", result,result);
    result = ((result) << 8);
    UPDOWN_INFOMSG("***s res: %lx\n", result);
    uint32_t tmp = *(sbaddr + LMBANK_SIZE_4B * lane_num + (offset / 4) + 1);
    UPDOWN_INFOMSG("***1 temp: %lx (%d)\n", tmp,tmp);
    tmp = (tmp) >> 24;
    UPDOWN_INFOMSG("***s temp : %lx\n", tmp);
    result = tmp | result;
    UPDOWN_INFOMSG("***final : %lx\n", result);
  } else if ((offset - (offset / 4) * 4) == 2) {
    result = ((result) << 16);
    uint32_t tmp = *(sbaddr + LMBANK_SIZE_4B * lane_num + (offset / 4) + 1);
    tmp = (tmp) >> 16;
    result = tmp | result;
  } else if ((offset - (offset / 4) * 4) == 3) {
    result = ((result) << 24);
    uint32_t tmp = *(sbaddr + LMBANK_SIZE_4B * lane_num + (offset / 4) + 1);
    tmp = (tmp) >> 8;
    result = tmp | result;
  } else
    printf("The offset is not currently supported (fix teh program)!\n");
  return result;
}

uint32_t change_endian(uint32_t num) {
  uint32_t result = ((num >> 24) & 0x000000ff) | ((num >> 8) & 0x0000ff00) |
                    ((num << 8) & 0x00ff0000) | ((num << 24) & 0xff000000);
  UPDOWN_INFOMSG("change_endian : %lx\n", result);
  return result;
}

void launch_upstream_kernel(uint32_t num_operands, uint32_t *operands,
                            uint8_t elabel, uint32_t lane_num) {
  init_lane(lane_num, 0, 0);
  init_lane_sb(lane_num, 0, 0);
  operands_t op;
  UPDOWN_INFOMSG("Lane:%d, setting operands\n", lane_num);
  op.setoperands(num_operands, operands);
  event_t ev;
  UPDOWN_INFOMSG("Lane:%d, setting event_word\n", lane_num);
  ev.setevent_word(elabel, num_operands);
  UPDOWN_INFOMSG("Lane:%d, send operands\n", lane_num);
  send_operands(lane_num, op);
  UPDOWN_INFOMSG("Lane:%d, send event\n", lane_num);
  send_event(lane_num, ev);
  UPDOWN_INFOMSG("Lane:%d, start_exec\n", lane_num);
  start_exec(lane_num);
}


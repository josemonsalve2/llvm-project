#include "updown.h"
#include <cstdio>
#include <cstdlib>
namespace UpDown
{

  // TODO: This should not be offset with the number of elements. Best to determine a fixed memory location for
  // each section
  void 
  UDRuntime_t::calc_addrmap() {
    uint64_t ubase = AbstractMachine.MemSize;
    BaseAddrs.saddr = (ptr_t)ubase;
    BaseAddrs.sbaddr = (ptr_t)(ubase + AbstractMachine.NumUDs * AbstractMachine.NumLanes * AbstractMachine.LMBankSize);
    BaseAddrs.eaddr = (ptr_t)(ubase + 2 * AbstractMachine.NumUDs * AbstractMachine.NumLanes * AbstractMachine.LMBankSize);
    BaseAddrs.oaddr = (ptr_t)(BaseAddrs.eaddr + AbstractMachine.NumUDs * AbstractMachine.NumLanes);
    BaseAddrs.exec = (ptr_t)(BaseAddrs.oaddr + AbstractMachine.NumUDs * AbstractMachine.NumLanes);
    BaseAddrs.locks = (ptr_t)(BaseAddrs.exec + AbstractMachine.NumUDs * AbstractMachine.NumLanes);

    UPDOWN_INFOMSG("calc_addrmap: ubase:%lx\nsaddr:%lx\nsbaddr:%lx\n"
                  "eaddr:%lx\noaddr:%lx\nexec:%lx\nstatus:%lx\n",
                  ubase, (uint64_t)BaseAddrs.saddr, (uint64_t)BaseAddrs.sbaddr,
                  (uint64_t)BaseAddrs.eaddr, (uint64_t)BaseAddrs.oaddr, (uint64_t)BaseAddrs.exec,
                  (uint64_t)BaseAddrs.locks);
  }

  void 
  UDRuntime_t::send_event(event_t ev) {
    uint64_t offset = ev.get_UdId()*AbstractMachine.NumLanes + ev.get_LaneId();
    // Locking the lane's queues
    *(BaseAddrs.locks + offset) = 1;
    // Set the event Queue
    *(BaseAddrs.eaddr + offset) = ev.get_EventWord();
    UPDOWN_INFOMSG("Sending Event:%u to [%u,%u,%u],", 
                  ev.get_EventLabel(), ev.get_UdId(), 
                  ev.get_LaneId(), ev.get_ThreadId());

    // TODO: Num Operands should reflect the continuation, this should not be a + 1 in the for
    if (ev.get_NumOperands() != 0)
      for (uint8_t i = 0; i < ev.get_NumOperands() + 1; i++) {
        *(BaseAddrs.oaddr + offset) = ev.get_OperandsData()[i];
        UPDOWN_INFOMSG("OB[%u]:%u,", i, ev.get_OperandsData()[i]);
      }
    *(BaseAddrs.locks + offset) = 0;

    // Set the Operand Queue
  }

  void
  UDRuntime_t::start_exec(uint8_t ud_id, uint8_t lane_num) { 
    uint64_t offset = ud_id*AbstractMachine.NumLanes * lane_num;
    *(BaseAddrs.exec + offset) = 1;
    UPDOWN_INFOMSG("Starting execution UD %u, Lane %u. Signal in %lX", ud_id, lane_num, (uint64_t) BaseAddrs.exec + offset);
  }

  uint64_t
  UDRuntime_t::get_aligned_offset(uint8_t ud_id, uint8_t lane_num, uint32_t offset) {
    auto alignment = sizeof(word_t);
    auto aligned_offset = offset - offset % alignment;
    UPDOWN_WARNING_IF(offset % alignment != 0, "Unaligned offset %u", offset);
    uint64_t returned_offset = ud_id*AbstractMachine.NumLanes*AbstractMachine.LMBankSize4b + // UD offset
                              AbstractMachine.LMBankSize4b * lane_num + // Lane offset
                              aligned_offset;
    return returned_offset;
  }

  void
  UDRuntime_t::t2ud_memcpy(uint8_t ud_id, uint8_t lane_num, uint32_t offset, uint64_t size, ptr_t data) {
    uint64_t apply_offset = get_aligned_offset(ud_id, lane_num, offset);
    std::memcpy(BaseAddrs.saddr + apply_offset, data, size);
    UPDOWN_INFOMSG("Copying %lu bytes from Top to UD %u, Lane %u. Signal in %lX", 
                    size, ud_id, lane_num, (uint64_t) BaseAddrs.saddr + apply_offset);
  }

  void
  UDRuntime_t::ud2t_memcpy(uint8_t ud_id, uint8_t lane_num, uint32_t offset, uint64_t size, ptr_t data) {
    uint64_t apply_offset = get_aligned_offset(ud_id, lane_num, offset);
    std::memcpy(data, BaseAddrs.saddr + apply_offset, size);
    UPDOWN_INFOMSG("Copying %lu bytes from UD %u, Lane %u to Top. Signal in %lX", 
                    size, ud_id, lane_num, (uint64_t) BaseAddrs.saddr + apply_offset);
  }

  void
  UDRuntime_t::sb_t2ud_memcpy(uint8_t ud_id, uint8_t lane_num, uint32_t offset, uint64_t size, ptr_t data) {
    uint64_t apply_offset = get_aligned_offset(ud_id, lane_num, offset);
    std::memcpy(BaseAddrs.sbaddr + apply_offset, data, size);
    UPDOWN_INFOMSG("Copying %lu bytes from Top to UD %u, Lane %u. Signal in %lX", 
                    size, ud_id, lane_num, (uint64_t) BaseAddrs.saddr + apply_offset);
  }

  void
  UDRuntime_t::sb_ud2t_memcpy(uint8_t ud_id, uint8_t lane_num, uint32_t offset, uint64_t size, ptr_t data) {
    uint64_t apply_offset = get_aligned_offset(ud_id, lane_num, offset);
    std::memcpy(data, BaseAddrs.sbaddr + apply_offset, size);
    UPDOWN_INFOMSG("Copying %lu bytes from UD %u, Lane %u to Top. Signal in %lX", 
                    size, ud_id, lane_num, (uint64_t) BaseAddrs.saddr + apply_offset);
  }

  bool
  UDRuntime_t::test_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset, word_t expected) {
    uint64_t apply_offset = get_aligned_offset(ud_id, lane_num, offset);
    return *(BaseAddrs.saddr + apply_offset) == expected;
  }

  void
  UDRuntime_t::test_wait_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset, word_t expected) {
    uint64_t apply_offset = get_aligned_offset(ud_id, lane_num, offset);
    while(*(BaseAddrs.saddr + apply_offset) != expected);
  }

  bool
  UDRuntime_t::test_sb_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset, word_t expected) {
    uint64_t apply_offset = get_aligned_offset(ud_id, lane_num, offset);
    return *(BaseAddrs.sbaddr + apply_offset) == expected;
  }

  void
  UDRuntime_t::test_wait_sb_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset, word_t expected) {
    uint64_t apply_offset = get_aligned_offset(ud_id, lane_num, offset);
    while(*(BaseAddrs.sbaddr + apply_offset) != expected);
  }

  uint32_t
  UDRuntime_t::change_endian(uint32_t num) {
    uint32_t result = ((num >> 24) & 0x000000ff) | ((num >> 8) & 0x0000ff00) |
                      ((num << 8) & 0x00ff0000) | ((num << 24) & 0xff000000);
    UPDOWN_INFOMSG("change_endian : %x\n", result);
    return result;
  }
}
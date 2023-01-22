#include "updown.h"
#include <cstdio>
#include <cstdlib>
namespace UpDown {

// TODO: This should not be offset with the number of elements. Best to
// determine a fixed memory location for each section
void UDRuntime_t::calc_addrmap() {
  BaseAddrs.mmaddr = (ptr_t)MachineConfig.MapMemBase;
  BaseAddrs.spaddr = (ptr_t)MachineConfig.SPMemBase;
  BaseAddrs.ctrlAddr = (ptr_t)MachineConfig.ControlBase;
  UPDOWN_INFOMSG(
      "calc_addrmap: maddr: 0x%lX spaddr: 0x%lX ctrlAddr: 0x%lX",
      reinterpret_cast<uint64_t>(BaseAddrs.mmaddr),
      reinterpret_cast<uint64_t>(BaseAddrs.spaddr),
      reinterpret_cast<uint64_t>(BaseAddrs.ctrlAddr));
}

void UDRuntime_t::send_event(event_t ev) {
  uint64_t offset = ev.get_UdId() * MachineConfig.CapNumLanes *
                        MachineConfig.CapControlPerLane +
                    ev.get_LaneId() * MachineConfig.CapControlPerLane;
  // Convert from bytes to words. the pointers are ptr_t
  offset /= sizeof(word_t);
  // Locking the lane's queues
  auto lock = (BaseAddrs.ctrlAddr + offset + MachineConfig.LockOffset);
  UPDOWN_INFOMSG("Locking 0x%lX", reinterpret_cast<uint64_t>(lock));
  *lock = 1;
  // Set the event Queue
  auto eventQ = (BaseAddrs.ctrlAddr + offset + MachineConfig.EventQueueOffset);
  *eventQ = ev.get_EventWord();
  UPDOWN_INFOMSG("Sending Event:%u to [%u,%u,%u] to queue at  0x%lX", 
                 ev.get_EventLabel(), ev.get_UdId(), ev.get_LaneId(), 
                 ev.get_ThreadId(), reinterpret_cast<uint64_t>(eventQ));

  // TODO: Num Operands should reflect the continuation, this should not be a +
  // 1 in the for
  auto OpsQ = (BaseAddrs.ctrlAddr + offset + MachineConfig.OperandQueueOffset);
  UPDOWN_INFOMSG("Using Operands Queue 0x%lX", reinterpret_cast<uint64_t>(OpsQ));
  if (ev.get_NumOperands() != 0)
    for (uint8_t i = 0; i < ev.get_NumOperands() + 1; i++) {
      *(OpsQ) =
          ev.get_OperandsData()[i];
      UPDOWN_INFOMSG("OB[%u]: %u (0x%X)", i, ev.get_OperandsData()[i], ev.get_OperandsData()[i]);
    }
  UPDOWN_INFOMSG("Unlocking 0x%lX", reinterpret_cast<uint64_t>(lock));
  *(lock) = 0;

  // Set the Operand Queue
}

void UDRuntime_t::start_exec(uint8_t ud_id, uint8_t lane_num) {
  uint64_t offset =
      ud_id * MachineConfig.CapNumLanes * MachineConfig.CapControlPerLane +
      lane_num * MachineConfig.CapControlPerLane;
  // Convert from bytes to words. the pointers are ptr_t
  offset /= sizeof(word_t);
  auto startSig = BaseAddrs.ctrlAddr + offset + MachineConfig.StartExecOffset;
  *(startSig) = 1;
  UPDOWN_INFOMSG(
      "Starting execution UD %u, Lane %u. Signal in  0x%lX", ud_id, lane_num,
      reinterpret_cast<uint64_t>(startSig));
}

uint64_t UDRuntime_t::get_lane_aligned_offset(uint8_t ud_id, uint8_t lane_num,
                                              uint32_t offset) {
  auto alignment = sizeof(word_t);
  auto aligned_offset = offset - offset % alignment;
  UPDOWN_WARNING_IF(offset % alignment != 0, "Unaligned offset %u", offset);
  uint64_t returned_offset =
      ud_id * MachineConfig.CapNumLanes *
          MachineConfig.CapSPmemPerLane +    // UD offset
      MachineConfig.CapSPmemPerLane * lane_num + // Lane offset
      aligned_offset;
  return returned_offset;
}

uint64_t UDRuntime_t::get_lane_physical_memory(uint8_t ud_id, uint8_t lane_num,
                                               uint32_t offset) {
  auto alignment = sizeof(word_t);
  auto aligned_offset = offset - offset % alignment;
  UPDOWN_WARNING_IF(offset % alignment != 0, "Unaligned offset %u", offset);
  uint64_t returned_offset = MachineConfig.SPBankSize * ud_id +
      MachineConfig.SPBankSize * lane_num + // Lane offset
      aligned_offset;
  return returned_offset;
}

void *UDRuntime_t::mm_malloc(uint64_t size) {
  UPDOWN_INFOMSG("Calling mm_malloc %u", size); 
  return MappedMemoryManager->get_region(size);
}

void UDRuntime_t::mm_free(void *ptr) {
  UPDOWN_INFOMSG("Calling mm_free  0x%lX", reinterpret_cast<uint64_t>(ptr)); 
  return MappedMemoryManager->remove_region(ptr);
}

void UDRuntime_t::mm2t_memcpy(uint64_t offset, void* dst, uint64_t size) {
  ptr_t src = BaseAddrs.mmaddr + offset;
  UPDOWN_INFOMSG("Copying %lu bytes from mapped memory (%lX = %d) to top (%lX = %d)",
                 size, reinterpret_cast<uint64_t>(src), *src, reinterpret_cast<uint64_t>(dst), *reinterpret_cast<word_t*>(dst));
  std::memcpy(dst, src, size);
}

void UDRuntime_t::t2mm_memcpy(uint64_t offset, void* src, uint64_t size) {
  ptr_t dst = BaseAddrs.mmaddr + offset;
  UPDOWN_INFOMSG("Copying %lu bytes from top (%lX = %d) to mapped memory (%lX = %d)",
                 size, reinterpret_cast<uint64_t>(src), *reinterpret_cast<word_t*>(src), reinterpret_cast<uint64_t>(dst), *dst);
  std::memcpy(dst, src, size);
}

void UDRuntime_t::t2ud_memcpy(void* data, uint64_t size,  uint8_t ud_id, uint8_t lane_num, uint32_t offset) {
  uint64_t apply_offset = get_lane_aligned_offset(ud_id, lane_num, offset);
  apply_offset /= sizeof(word_t);
  std::memcpy(BaseAddrs.spaddr + apply_offset, data, size);
  UPDOWN_INFOMSG("Copying %lu bytes from Top to UD %u, Lane %u, offset %u, Apply offset %u. Signal in 0x%lX",
                 size, ud_id, lane_num, offset, apply_offset,
                 reinterpret_cast<uint64_t>(BaseAddrs.spaddr + apply_offset));
}

void UDRuntime_t::ud2t_memcpy(void* data, uint64_t size, uint8_t ud_id, uint8_t lane_num, uint32_t offset) {
  uint64_t apply_offset = get_lane_aligned_offset(ud_id, lane_num, offset);
  apply_offset /= sizeof(word_t);
  std::memcpy(data, BaseAddrs.spaddr + apply_offset, size);
  UPDOWN_INFOMSG("Copying %lu bytes from UD %u, Lane %u to Top, offset %u, Apply offset %u. Signal in 0x%lX",
                 size, ud_id, lane_num, offset, apply_offset,
                 reinterpret_cast<uint64_t>(BaseAddrs.spaddr + apply_offset));
}

bool UDRuntime_t::test_addr(uint8_t ud_id, uint8_t lane_num, uint32_t offset,
                            word_t expected) {
  uint64_t apply_offset = get_lane_aligned_offset(ud_id, lane_num, offset);
  apply_offset /= sizeof(word_t);
  UPDOWN_INFOMSG("Testing UD %u, Lane %u to Top, offset %u."
                 " Addr 0x%lX. Expected = %u, read = %u",
                 ud_id, lane_num, offset,
                 reinterpret_cast<uint64_t>(BaseAddrs.spaddr + apply_offset), 
                 expected, *(BaseAddrs.spaddr + apply_offset));
  return *(BaseAddrs.spaddr + apply_offset) == expected;
}

void UDRuntime_t::test_wait_addr(uint8_t ud_id, uint8_t lane_num,
                                 uint32_t offset, word_t expected) {
  uint64_t apply_offset = get_lane_aligned_offset(ud_id, lane_num, offset);
  apply_offset /= sizeof(word_t);
  UPDOWN_INFOMSG("Testing UD %u, Lane %u to Top, offset %u."
                " Addr 0x%lX. Expected = %u, read = %u. (%s)",
                ud_id, lane_num, offset,
                reinterpret_cast<uint64_t>(BaseAddrs.spaddr + apply_offset), 
                expected, *(BaseAddrs.spaddr + apply_offset), 
                *(BaseAddrs.spaddr + apply_offset) != expected ? 
                "Waiting" : "Returning");
  while (*(BaseAddrs.spaddr + apply_offset) != expected);
}

} // namespace UpDown
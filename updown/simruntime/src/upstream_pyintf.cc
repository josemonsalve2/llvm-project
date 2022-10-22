/**
 * @file upstream_obj.cc
 * @author Andronicus
 * @brief Definition of a simple upstream object
 * @version 0.1
 * @date 2021-10-25
 *
 * @copyright Copyright (c) 2021
 * Adapted from downstream_obj.cc by Jose Monsalve Diaz
 * This file is based on the simple_cache.cc
 * example in the learning_gem5 folder.
 * The following Copyright applies:
 * Copyright (c) 2017 Jason Lowe-Power
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
 *
 */

#include <cstring>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>

#include "debug.h"
#include "upstream_pyintf.hh"

Upstream_PyIntf::Upstream_PyIntf() { proc_id = 0; }

void Upstream_PyIntf::addSystemPaths() {
  UPDOWN_INFOMSG("Adding system paths: %s",
                 "\"./emulator:" UPDOWN_INSTALL_DIR
                 "/emulator:" UPDOWN_SOURCE_DIR "/emulator\"");
  PyRun_SimpleString("import sys\nsys.path.append(\".\")\n");
  PyRun_SimpleString("import sys\nsys.path.append(\"./emulator\")\n");
  PyRun_SimpleString("import sys\nsys.path.append(\"" UPDOWN_SOURCE_DIR
                     "/emulator \")\n");
  PyRun_SimpleString("import sys\nsys.path.append(\"" UPDOWN_INSTALL_DIR
                     "/emulator\")\n");
}

Upstream_PyIntf::Upstream_PyIntf(int numlanes, std::string progfile,
                                 std::string efaname, std::string simdir,
                                 int lm_addr_mode, uint32_t lmsize,
                                 std::string perf_log_file) {
  Py_Initialize();

  addSystemPaths();

  pEmulator = PyImport_ImportModule("EfaExecutor_multilane_nothread");
  if (pEmulator == nullptr) {
    PyErr_Print();
    UPDOWN_ERROR("Error when loading pEmulator");
    std::exit(1);
  }

  // def __init__(self, lane_id, numOfGpr, dram_mem, top, perf_file):
  UPDOWN_INFOMSG("Creating UpStream PyIntf with %d lanes %u banksize",
                 numlanes, lmsize);
  pclass_ve = PyObject_GetAttrString(pEmulator, "VirtualEngine");
  if (pclass_ve == nullptr) {
    PyErr_Print();
    UPDOWN_ERROR("Error when loading pclass_ve");
    std::exit(1);
  }
  // TODO: This output should be relative to CWD
  std::string perffile = "output/perf_stats.txt";
  pargs = Py_BuildValue("(isiili)", numlanes, perffile.c_str(), 1, lmsize, 1e9,
                        0);
  pVirtEngine = PyEval_CallObject(pclass_ve, pargs);
  pLM = PyObject_GetAttrString(pVirtEngine, "LM");

  UPDOWN_INFOMSG("Initialized UpStream Python Interface with %s and %s",
                 progfile.c_str(), efaname.c_str());
  const char *pfile = progfile.c_str();
  const char *pname = efaname.c_str();
  const char *simprefix = simdir.c_str();
  pEfafile = PyImport_ImportModule(pfile);

  pefa = PyObject_CallMethod(pEfafile, pname, nullptr);

  if (pefa == nullptr) {
    PyErr_Print();
    UPDOWN_ERROR("Error when loading pefa");
    std::exit(1);
  }
  UPDOWN_INFOMSG("UpStream PyIntf, EFA created ");

  PyObject *res_init;
  res_init = PyObject_CallMethod(pVirtEngine, "setup_sim", "(Osi)", pefa,
                                 simprefix, lm_addr_mode);
  Py_DECREF(res_init);
  UPDOWN_INFOMSG("UpStream Processor Setup_Sim done ");
}

// up_lane_array[lanecnt].OpBuffer.setOp(set_start_addr)
// start_event = Event(0, 9)
// #print("Check Event Queue Size:%d" % len(up_lane_array[lanecnt].EvQ.events))
// up_lane_array[lanecnt].EvQ.pushEvent(start_event)
// property_vec = [Property("event",None)]
void Upstream_PyIntf::insert_event(uint32_t edata, int numOb, int lane_id) {
  PyObject *pclass_ev, *res, *pargs_e, *pstart_event;
  pclass_ev = PyObject_GetAttrString(pEmulator, "Event");
  uint32_t eword = edata;
  int elabel = eword & 0xff;
  int tid = (eword >> 16) & 0xff;
  int lane_num = (eword >> 24) & 0xff;

  pargs_e = Py_BuildValue("(ii)", elabel, numOb);
  pstart_event = PyEval_CallObject(pclass_ev, pargs_e);
  res = PyObject_CallMethod(pstart_event, "setlanenum", "(i)", lane_num);
  res = PyObject_CallMethod(pstart_event, "setthreadid", "(i)", tid);
  res = PyObject_CallMethod(pVirtEngine, "insert_event", "(iO)", lane_id,
                            pstart_event);
  UPDOWN_INFOMSG("Pushed Event:%d, lane:%d, tid:%d numop:%d ", elabel,
                 lane_num, tid, numOb);
  Py_DECREF(res);
  Py_DECREF(pargs_e);
  Py_DECREF(pstart_event);
  Py_DECREF(pclass_ev);
}

void Upstream_PyIntf::insert_operand(uint32_t odata, int lane_id) {
  PyObject *res;
  res = PyObject_CallMethod(pVirtEngine, "insert_operand", "(ii)", lane_id,
                            odata);

  UPDOWN_INFOMSG("Lane:%d Pushed into Operand Buffer: %d", lane_id, odata);
  Py_DECREF(res);
}

void Upstream_PyIntf::set_print_level(int printLvl) {
  PyObject *efautil_ev = PyObject_GetAttrString(pEmulator, "efa_util");
  PyObject_CallMethod(efautil_ev, "printLevel", "(i)", printLvl);
}

void Upstream_PyIntf::insert_scratch(uint32_t saddr, uint32_t sdata) {
  PyObject *res;
  res = PyObject_CallMethod(pVirtEngine, "write_scratch", "(ii)", saddr, sdata);

  UPDOWN_INFOMSG("Entered into ScratchPad %lX %d", saddr, sdata);
  Py_DECREF(res);
}


void Upstream_PyIntf::read_scratch(uint32_t saddr, uint8_t *data,
                                   uint32_t size) {
  PyObject *res_scratch;
  UPDOWN_INFOMSG("Reading %d bytes, from address (%u)0x%X, into pointer 0x%lX",
                  size, saddr, saddr, reinterpret_cast<uint64_t>(data));
  if (size == 1) {
    // data = new uint8_t[1];
    res_scratch =
        PyObject_CallMethod(pVirtEngine, "read_scratch", "(ii)", saddr, size);
    if (res_scratch == nullptr) {
      PyErr_Print();
      UPDOWN_ERROR("Read_scratch Error: Return object NULL");
      exit(1);
    }
    *data = (uint8_t)PyLong_AsLong(res_scratch);
  } else if (size == 2) {
    // data = new uint8_t[2];
    res_scratch =
        PyObject_CallMethod(pVirtEngine, "read_scratch", "(ii)", saddr, size);
    if (res_scratch == nullptr) {
      PyErr_Print();
      UPDOWN_ERROR("Read_scratch Error: Return object NULL");
      exit(1);
    }
    uint16_t temp = (uint16_t)PyLong_AsLong(res_scratch);
    data[0] = temp & 0xff;
    data[1] = (temp >> 8) & 0xff;
  } else if (size == 4) {
    // data = new uint8_t[4];
    res_scratch =
        PyObject_CallMethod(pVirtEngine, "read_scratch", "(ii)", saddr, size);
    if (res_scratch == nullptr) {
      PyErr_Print();
      UPDOWN_ERROR("Read_scratch Error: Return object NULL");
      exit(1);
    }
    // PyObject *res_obj = PyTuple_GetItem(res, 0);
    uint32_t temp = (uint32_t)PyLong_AsLong(res_scratch);
    data[0] = temp & 0xff;
    data[1] = (temp >> 8) & 0xff;
    data[2] = (temp >> 16) & 0xff;
    data[3] = (temp >> 24) & 0xff;

  } else if (size > 4) {
    uint32_t locaddr = saddr;
    int num4bytes = size / 4;
    for (int i = 0; i++; i < num4bytes) {
      res_scratch = PyObject_CallMethod(pVirtEngine, "read_scratch", "(ii)",
                                        locaddr, size);
      if (res_scratch == nullptr) {
        PyErr_Print();
        UPDOWN_ERROR("Read_scratch Error: Return object NULL");
        exit(1);
      }
      uint32_t temp = (uint32_t)PyLong_AsLong(res_scratch);
      data[4 * i + 0] = temp & 0xff;
      data[4 * i + 1] = (temp >> 8) & 0xff;
      data[4 * i + 2] = (temp >> 16) & 0xff;
      data[4 * i + 3] = (temp >> 24) & 0xff;
      locaddr += 4;
    }
  }
}

uint32_t Upstream_PyIntf::getEventQ_Size(int lane_id) {
  PyObject *res_eq;
  res_eq = PyObject_CallMethod(pVirtEngine, "getEventQ_size", "(i)", lane_id);
  if (res_eq == nullptr) {
    UPDOWN_ERROR("EventQ Size: Return object NULL");
    exit(1);
  }
  uint32_t evq_size = (uint32_t)PyLong_AsLong(res_eq);
  Py_DECREF(res_eq);
  return evq_size;
}

int Upstream_PyIntf::execute(int cont_state, struct emulator_stats *em_stats,
                             int lane_id) {
  const char *arg = "O";
  PyObject *res_exec, *num_sends_obj, *return_state_obj, *exec_cycle_obj,
      *actcnt_obj, *return_items[15];
  PyObject *fname = Py_BuildValue("s", "executeEFA_simAPI");
  PyObject *farg = Py_BuildValue("i", lane_id);
  PyObject *ftimestamp = Py_BuildValue("l", 0);
  res_exec =
      PyObject_CallMethodObjArgs(pVirtEngine, fname, farg, ftimestamp, nullptr);
  if (res_exec == nullptr) {
    PyErr_Print();
    UPDOWN_ERROR("Execute Error: Return object NULL");
    exit(1);
  } else {
    int ok;

    for (int i = 0; i < 15; i++) {
      return_items[i] = PyTuple_GetItem(res_exec, i);
      Py_INCREF(return_items[i]);
    }

    // These are borrowed references hence INCREF ! as per pydcos
    num_sends_obj = PyTuple_GetItem(res_exec, 0);
    Py_INCREF(num_sends_obj);
    return_state_obj = PyTuple_GetItem(res_exec, 1);
    Py_INCREF(return_state_obj);
    exec_cycle_obj = PyTuple_GetItem(res_exec, 2);
    Py_INCREF(exec_cycle_obj);
    actcnt_obj = PyTuple_GetItem(res_exec, 3);
    Py_INCREF(actcnt_obj);
    uint32_t return_state = (uint32_t)PyLong_AsLong(return_items[1]);
    em_stats->num_sends = (uint32_t)PyLong_AsLong(return_items[0]);
    em_stats->exec_cycles = (uint32_t)PyLong_AsLong(return_items[2]);
    em_stats->actcnt = (uint32_t)PyLong_AsLong(return_items[3]);
    em_stats->idle_cycles = (uint32_t)PyLong_AsLong(return_items[4]);
    em_stats->uplmreadbytes = (uint32_t)PyLong_AsLong(return_items[5]);
    em_stats->uplmwritebytes = (uint32_t)PyLong_AsLong(return_items[6]);
    em_stats->msg_acts = (uint32_t)PyLong_AsLong(return_items[7]);
    em_stats->mov_acts = (uint32_t)PyLong_AsLong(return_items[8]);
    em_stats->branch_acts = (uint32_t)PyLong_AsLong(return_items[9]);
    em_stats->alu_acts = (uint32_t)PyLong_AsLong(return_items[10]);
    em_stats->yld_acts = (uint32_t)PyLong_AsLong(return_items[11]);
    em_stats->comp_acts = (uint32_t)PyLong_AsLong(return_items[12]);
    em_stats->cmp_swp_acts = (uint32_t)PyLong_AsLong(return_items[13]);
    em_stats->transcnt = (uint32_t)PyLong_AsLong(return_items[14]);
    UPDOWN_INFOMSG(
        "EFA execute output, LaneID:%d, Return State:%d, Num Sends: %d\
                            Exec_cycles:%d, Actcnt:%d ",
        lane_id, return_state, em_stats->num_sends, em_stats->exec_cycles,
        em_stats->actcnt);
    Py_DECREF(res_exec);
    Py_DECREF(num_sends_obj);
    Py_DECREF(return_state_obj);
    Py_DECREF(actcnt_obj);
    for (int i = 0; i < 15; i++) {
      Py_DECREF(return_items[i]);
    }
    Py_DECREF(farg);
    Py_DECREF(fname);
    return return_state;
  }
}

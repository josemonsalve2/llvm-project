#ifndef UPSTREAM_PYINTF_HH
#define UPSTREAM_PYINTF_HH

extern "C" {
#include "Python.h"
}

struct emulator_stats {
  uint32_t actcnt;
  uint32_t num_sends;
  uint32_t exec_cycles;
  uint32_t idle_cycles;
  uint32_t uplmwritebytes;
  uint32_t uplmreadbytes;
  uint32_t msg_acts;
  uint32_t mov_acts;
  uint32_t branch_acts;
  uint32_t alu_acts;
  uint32_t yld_acts;
  uint32_t comp_acts;
  uint32_t cmp_swp_acts;
  uint32_t transcnt;
};
struct Event {
  uint8_t event_id;
  uint8_t num_operands;
  uint8_t event_label;
  uint8_t event_base;
  uint8_t tid;
  uint8_t ptid;
};

class Upstream_PyIntf {
private:
  int proc_id;
  PyObject *pName, *pModule, *pModule2, *pargs, *pclass_ve, *pinst_ve;
  PyObject *pEmulator, *pEfafile, *pVirtEngine;
  PyObject *pinst_eq, *pinst_ob;
  PyObject *pLM, *planes;
  PyObject *pefa, *pefa_prop, *pprop;

  /**
   * @brief Adds system paths for searching the necessary modules
   *
   * This function adds the following system locations to the python
   * system path:
   *
   * - Installation path for updown runtime lib emulator
   * - Source code location for updown runtime lib emulator
   * - A folder named emulator in the current location
   *
   */
  void addSystemPaths();

public:
  Upstream_PyIntf();
  Upstream_PyIntf(int ud_id, int numlanes, std::string progfile, std::string efaname,
                  std::string simdir, int lm_mode, uint32_t lmsize,
                  std::string perf_log_file);
  void insert_event(uint32_t edata, int numOb, int ud_id, int lane_id);
  void insert_operand(uint32_t odata, int lane_id);

  void set_print_level(int printLvl);

  int execute(int cont_state, struct emulator_stats *em_stats, int lane_id);

  void insert_scratch(uint32_t saddr, uint32_t sdata);

  void read_scratch(uint32_t saddr, uint8_t *data, uint32_t size);

  uint32_t getEventQ_Size(int lane_id);
  void dumpEventQueue(int lane_id);

  /*
   * Simple Wrapper for upstream emulator Virtual engine
   */
  ~Upstream_PyIntf() { Py_Finalize(); }
};

#endif // UPSTREAM_LANE_HH

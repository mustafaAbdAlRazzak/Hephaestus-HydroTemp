#include "SystemController.h"
#include "Config.h"
#include "SharedState.h"
#include "PidController.h"
#include "Heater.h"
#include "Pump.h"
#include "ModbusInterface.h"

void systemStopOutputs() {
  pidDisable();
  outputPercent = 0.0;
  heaterOff();
  pumpSet(false);
}

void systemStart() {
  faultCode = FAULT_NONE;
  systemState = STATE_RUNNING;
  outputPercent = 0.0;
  pidEnable();
  pumpSet(true);
}

void systemStop() {
  systemState = STATE_STOPPED;
  systemStopOutputs();
}

void systemTripFault(uint16_t code) {
  faultCode = code;
  systemState = STATE_FAULT;
  systemStopOutputs();
  modbusClearRunRequest();
}

void systemProcessCommands() {
  bool wantRun = modbusRunRequested();
  if (wantRun && systemState != STATE_RUNNING) {
    systemStart();
  } else if (!wantRun && systemState == STATE_RUNNING) {
    systemStop();
  }
}

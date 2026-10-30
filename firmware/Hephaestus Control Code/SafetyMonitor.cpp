#include "SafetyMonitor.h"
#include "Config.h"
#include "SharedState.h"
#include "SystemController.h"

void safetyCheck() {
  if (systemState != STATE_RUNNING) return;
  if (!sensorOk) {
    systemTripFault(FAULT_SENSOR);
  } else if (temperature >= MAX_SAFE_TEMP_C) {
    systemTripFault(FAULT_OVER_TEMPERATURE);
  }
}

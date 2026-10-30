#include "ModbusInterface.h"
#include <ModbusIP_ESP8266.h>
#include "Config.h"
#include "SharedState.h"
#include "PidController.h"
#include "SettingsStorage.h"

static ModbusIP mb;

void modbusPublishSettings() {
  mb.Hreg(HREG_SETPOINT, (uint16_t)lroundf(setpoint * SCALE_TEMPERATURE));
  mb.Hreg(HREG_KP, (uint16_t)lroundf(kp * SCALE_GAIN));
  mb.Hreg(HREG_KI, (uint16_t)lroundf(ki * SCALE_GAIN));
  mb.Hreg(HREG_KD, (uint16_t)lroundf(kd * SCALE_GAIN));
}

void modbusPublishStatus() {
  mb.Ireg(IREG_TEMPERATURE, (uint16_t)(int16_t)lroundf(temperature * SCALE_TEMPERATURE));
  mb.Ireg(IREG_HEATER_OUTPUT, (uint16_t)lroundf(outputPercent * SCALE_OUTPUT));
  mb.Ireg(IREG_SYSTEM_STATE, systemState);
  mb.Ireg(IREG_FAULT_CODE, faultCode);
  mb.Ireg(IREG_SAFE_LIMIT, (uint16_t)lroundf(MAX_SAFE_TEMP_C * SCALE_TEMPERATURE));
  mb.Ireg(IREG_SETPOINT_MIN, (uint16_t)lroundf(SETPOINT_MIN_C * SCALE_TEMPERATURE));
  mb.Ireg(IREG_SETPOINT_MAX, (uint16_t)lroundf(SETPOINT_MAX_C * SCALE_TEMPERATURE));
  mb.Ireg(IREG_GAIN_MAX, (uint16_t)lroundf(GAIN_MAX * SCALE_GAIN));
}

void modbusInit() {
  mb.server(MODBUS_PORT);
  mb.addCoil(COIL_RUN, false);
  mb.addHreg(HREG_SETPOINT);
  mb.addHreg(HREG_KP);
  mb.addHreg(HREG_KI);
  mb.addHreg(HREG_KD);
  mb.addIreg(IREG_TEMPERATURE);
  mb.addIreg(IREG_HEATER_OUTPUT);
  mb.addIreg(IREG_SYSTEM_STATE);
  mb.addIreg(IREG_FAULT_CODE);
  mb.addIreg(IREG_SAFE_LIMIT);
  mb.addIreg(IREG_SETPOINT_MIN);
  mb.addIreg(IREG_SETPOINT_MAX);
  mb.addIreg(IREG_GAIN_MAX);
  mb.addCoil(COIL_MANUAL_MODE, false);
  mb.addHreg(HREG_MANUAL_OUTPUT, 0);
  modbusPublishSettings();
  modbusPublishStatus();
}

void modbusTask() {
  mb.task();
}

bool modbusRunRequested() {
  return mb.Coil(COIL_RUN);
}

void modbusClearRunRequest() {
  mb.Coil(COIL_RUN, false);
}

void modbusReadSettings() {

  manualMode = mb.Coil(COIL_MANUAL_MODE);
  

  float newManualOutput = mb.Hreg(HREG_MANUAL_OUTPUT) / SCALE_OUTPUT;
  if (newManualOutput >= 0.0f && newManualOutput <= 100.0f) {
    manualOutputPercent = newManualOutput;
  }

  float newSetpoint = mb.Hreg(HREG_SETPOINT) / SCALE_TEMPERATURE;
  float newKp = mb.Hreg(HREG_KP) / SCALE_GAIN;
  float newKi = mb.Hreg(HREG_KI) / SCALE_GAIN;
  float newKd = mb.Hreg(HREG_KD) / SCALE_GAIN;
  bool valid = newSetpoint >= SETPOINT_MIN_C && newSetpoint <= SETPOINT_MAX_C &&
               newKp <= GAIN_MAX && newKi <= GAIN_MAX && newKd <= GAIN_MAX;
  if (!valid) {
    modbusPublishSettings();
    return;
  }
  bool changed = fabsf(newSetpoint - setpoint) > 0.001f ||
                 fabsf(newKp - kp) > 0.001f ||
                 fabsf(newKi - ki) > 0.001f ||
                 fabsf(newKd - kd) > 0.001f;
  if (!changed) return;
  setpoint = newSetpoint;
  kp = newKp;
  ki = newKi;
  kd = newKd;
  pidApplyTunings();
  settingsSave();
}

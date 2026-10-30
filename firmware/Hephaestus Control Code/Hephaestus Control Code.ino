#include "Config.h"
#include "Heater.h"
#include "Pump.h"
#include "SettingsStorage.h"
#include "PidController.h"
#include "TemperatureSensor.h"
#include "WifiManager.h"
#include "ModbusInterface.h"
#include "SystemController.h"
#include "SafetyMonitor.h"
#include "StatusPrinter.h"

static uint32_t lastSampleMs = 0;

void setup() {
  Serial.begin(115200);
  heaterInit();
  pumpInit();
  settingsLoad();
  pidInit();
  sensorInit();
  wifiConnect();
  modbusInit();
  lastSampleMs = millis();
}

void loop() {
  modbusTask();
  wifiMaintain();
  heaterUpdate();

  uint32_t now = millis();
  if (now - lastSampleMs >= SAMPLE_TIME_MS) {
    lastSampleMs = now;
    sensorRead();
    modbusReadSettings();
    systemProcessCommands();
    safetyCheck();
    pidCompute();
    modbusPublishStatus();
    statusPrint();
  }

  delay(1);
}

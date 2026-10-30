#include "StatusPrinter.h"
#include <Arduino.h>
#include "SharedState.h"

void statusPrint() {
  Serial.printf("T=%.2f SP=%.1f OUT=%.1f%% STATE=%u FAULT=%u\n",
                temperature, setpoint, outputPercent, systemState, faultCode);
}

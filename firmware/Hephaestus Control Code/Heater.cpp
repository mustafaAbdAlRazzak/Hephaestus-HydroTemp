#include "Heater.h"
#include "Config.h"
#include "SharedState.h"

static uint32_t heaterWindowStartMs = 0;

void heaterInit() {
  pinMode(PIN_HEATER_SSR, OUTPUT);
  digitalWrite(PIN_HEATER_SSR, LOW);
}

void heaterOff() {
  digitalWrite(PIN_HEATER_SSR, LOW);
}

void heaterUpdate() {
  uint32_t now = millis();
  if (now - heaterWindowStartMs >= HEATER_WINDOW_MS) {
    heaterWindowStartMs = now;
  }
  uint32_t onTimeMs = (uint32_t)(outputPercent / 100.0f * HEATER_WINDOW_MS);
  bool on = systemState == STATE_RUNNING && (now - heaterWindowStartMs) < onTimeMs;
  digitalWrite(PIN_HEATER_SSR, on ? HIGH : LOW);
}

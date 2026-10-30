#include "Pump.h"
#include "Config.h"

static void writePumpDuty(uint32_t duty) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(PIN_PUMP_MOSFET, duty);
#else
  ledcWrite(PUMP_PWM_CHANNEL, duty);
#endif
}

void pumpInit() {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttach(PIN_PUMP_MOSFET, PUMP_PWM_FREQUENCY_HZ, PUMP_PWM_RESOLUTION_BITS);
#else
  ledcSetup(PUMP_PWM_CHANNEL, PUMP_PWM_FREQUENCY_HZ, PUMP_PWM_RESOLUTION_BITS);
  ledcAttachPin(PIN_PUMP_MOSFET, PUMP_PWM_CHANNEL);
#endif
  writePumpDuty(0);
}

void pumpSet(bool on) {
  uint32_t maxDuty = (1UL << PUMP_PWM_RESOLUTION_BITS) - 1;
  writePumpDuty(on ? (maxDuty * PUMP_DUTY_PERCENT) / 100 : 0);
}

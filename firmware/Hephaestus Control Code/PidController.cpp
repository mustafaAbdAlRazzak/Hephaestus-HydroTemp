#include "PidController.h"
#include <PID_v1.h>
#include "Config.h"
#include "SharedState.h"

static PID pid(&temperature, &outputPercent, &setpoint, DEFAULT_KP, DEFAULT_KI, DEFAULT_KD, DIRECT);

void pidInit() {
  pid.SetOutputLimits(OUTPUT_MIN_PERCENT, OUTPUT_MAX_PERCENT);
  pid.SetSampleTime(SAMPLE_TIME_MS);
  pid.SetTunings(kp, ki, kd);
  pid.SetMode(MANUAL);
}

void pidEnable() {
  pid.SetMode(AUTOMATIC);
}

void pidDisable() {
  pid.SetMode(MANUAL);
}

void pidApplyTunings() {
  pid.SetTunings(kp, ki, kd);
}

void pidCompute() {
  if (systemState != STATE_RUNNING) {
    outputPercent = 0.0f;
    return;
  }

  if (manualMode) {
    outputPercent = manualOutputPercent;
  } else {
    pid.Compute(); 
  }
}

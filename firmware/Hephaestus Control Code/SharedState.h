#pragma once

#include <Arduino.h>

extern bool manualMode;
extern float manualOutputPercent;
extern double temperature;
extern bool sensorOk;
extern double setpoint;
extern float kp;
extern float ki;
extern float kd;
extern double outputPercent;
extern uint16_t systemState;
extern uint16_t faultCode;

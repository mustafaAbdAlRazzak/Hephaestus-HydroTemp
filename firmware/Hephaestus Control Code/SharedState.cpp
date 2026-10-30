#include "SharedState.h"
#include "Config.h"

double temperature = 0.0;
bool sensorOk = false;
double setpoint = DEFAULT_SETPOINT_C;
float kp = DEFAULT_KP;
float ki = DEFAULT_KI;
float kd = DEFAULT_KD;
bool manualMode = false;
float manualOutputPercent = 0.0f;
double outputPercent = 0.0;
uint16_t systemState = STATE_STOPPED;
uint16_t faultCode = FAULT_NONE;

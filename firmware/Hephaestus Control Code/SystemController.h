#pragma once

#include <Arduino.h>

void systemStart();
void systemStop();
void systemStopOutputs();
void systemTripFault(uint16_t code);
void systemProcessCommands();

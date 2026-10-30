#include "TemperatureSensor.h"
#include <OneWire.h>
#include <DallasTemperature.h>
#include "Config.h"
#include "SharedState.h"

static OneWire oneWire(PIN_TEMP_SENSOR);
static DallasTemperature sensors(&oneWire);

void sensorInit() {
  sensors.begin();
  sensors.setResolution(SENSOR_RESOLUTION_BITS);
  sensors.requestTemperatures();
  sensors.setWaitForConversion(false);
}

void sensorRead() {
  float value = sensors.getTempCByIndex(0);
  sensors.requestTemperatures();
  temperature = value;
  sensorOk = value > SENSOR_VALID_MIN_C && value < SENSOR_VALID_MAX_C;
}

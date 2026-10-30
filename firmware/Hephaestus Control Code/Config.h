#pragma once

#include <Arduino.h>

constexpr uint8_t PIN_TEMP_SENSOR = 4;
constexpr uint8_t PIN_HEATER_SSR = 25;
constexpr uint8_t PIN_PUMP_MOSFET = 27;

constexpr const char* WIFI_SSID = "Tenda_820AB0";
constexpr const char* WIFI_PASSWORD = "19702002";
constexpr uint8_t IP_LOCAL[4] = {192, 168, 0, 150};
constexpr uint8_t IP_GATEWAY[4] = {192, 168, 0, 1};
constexpr uint8_t IP_SUBNET[4] = {255, 255, 255, 0};
constexpr uint8_t IP_DNS[4] = {192, 168, 0, 1};
constexpr uint16_t MODBUS_PORT = 502;
constexpr uint32_t WIFI_CONNECT_TIMEOUT_MS = 15000;
constexpr uint32_t WIFI_RETRY_INTERVAL_MS = 5000;

constexpr uint32_t SAMPLE_TIME_MS = 2000;
constexpr uint32_t HEATER_WINDOW_MS = 2000;
constexpr float OUTPUT_MIN_PERCENT = 0.0f;
constexpr float OUTPUT_MAX_PERCENT = 100.0f;

constexpr float MAX_SAFE_TEMP_C = 60.0f;
constexpr float SETPOINT_MIN_C = 10.0f;
constexpr float SETPOINT_MAX_C = 55.0f;
constexpr float DEFAULT_SETPOINT_C = 30.0f;
constexpr float SENSOR_VALID_MIN_C = -10.0f;
constexpr float SENSOR_VALID_MAX_C = 100.0f;
constexpr uint8_t SENSOR_RESOLUTION_BITS = 11;

constexpr float DEFAULT_KP = 10.0f;
constexpr float DEFAULT_KI = 0.0f;
constexpr float DEFAULT_KD = 0.0f;
constexpr float GAIN_MAX = 600.0f;

constexpr uint8_t PUMP_DUTY_PERCENT = 50;
constexpr uint32_t PUMP_PWM_FREQUENCY_HZ = 20000;
constexpr uint8_t PUMP_PWM_RESOLUTION_BITS = 8;
constexpr uint8_t PUMP_PWM_CHANNEL = 0;

constexpr uint16_t COIL_MANUAL_MODE = 1;
constexpr uint16_t COIL_RUN = 0;
constexpr uint16_t HREG_SETPOINT = 0;
constexpr uint16_t HREG_KP = 1;
constexpr uint16_t HREG_KI = 2;
constexpr uint16_t HREG_KD = 3;
constexpr uint16_t HREG_MANUAL_OUTPUT = 4;
constexpr uint16_t IREG_TEMPERATURE = 0;
constexpr uint16_t IREG_HEATER_OUTPUT = 1;
constexpr uint16_t IREG_SYSTEM_STATE = 2;
constexpr uint16_t IREG_FAULT_CODE = 3;
constexpr uint16_t IREG_SAFE_LIMIT = 4;
constexpr uint16_t IREG_SETPOINT_MIN = 5;
constexpr uint16_t IREG_SETPOINT_MAX = 6;
constexpr uint16_t IREG_GAIN_MAX = 7;

constexpr float SCALE_TEMPERATURE = 10.0f;
constexpr float SCALE_OUTPUT = 10.0f;
constexpr float SCALE_GAIN = 100.0f;

constexpr uint16_t STATE_STOPPED = 0;
constexpr uint16_t STATE_RUNNING = 1;
constexpr uint16_t STATE_FAULT = 2;

constexpr uint16_t FAULT_NONE = 0;
constexpr uint16_t FAULT_OVER_TEMPERATURE = 1;
constexpr uint16_t FAULT_SENSOR = 2;

#pragma once

void modbusInit();
void modbusTask();
void modbusPublishSettings();
void modbusPublishStatus();
void modbusReadSettings();
bool modbusRunRequested();
void modbusClearRunRequest();

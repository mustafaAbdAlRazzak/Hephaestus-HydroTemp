#include "WifiManager.h"
#include <WiFi.h>
#include "Config.h"

static uint32_t lastWifiAttemptMs = 0;

static IPAddress toIp(const uint8_t* a) {
  return IPAddress(a[0], a[1], a[2], a[3]);
}

void wifiConnect() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.config(toIp(IP_LOCAL), toIp(IP_GATEWAY), toIp(IP_SUBNET), toIp(IP_DNS));
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < WIFI_CONNECT_TIMEOUT_MS) {
    delay(100);
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi connected: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi not connected");
  }
}

void wifiMaintain() {
  if (WiFi.status() == WL_CONNECTED) return;
  uint32_t now = millis();
  if (now - lastWifiAttemptMs < WIFI_RETRY_INTERVAL_MS) return;
  lastWifiAttemptMs = now;
  WiFi.reconnect();
}

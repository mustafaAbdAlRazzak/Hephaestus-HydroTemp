#include "SettingsStorage.h"
#include <Preferences.h>
#include "Config.h"
#include "SharedState.h"

static Preferences prefs;

void settingsLoad() {
  prefs.begin("heater", false);
  float sp = prefs.getFloat("sp", DEFAULT_SETPOINT_C);
  float p = prefs.getFloat("kp", DEFAULT_KP);
  float i = prefs.getFloat("ki", DEFAULT_KI);
  float d = prefs.getFloat("kd", DEFAULT_KD);
  bool valid = sp >= SETPOINT_MIN_C && sp <= SETPOINT_MAX_C &&
               p >= 0 && p <= GAIN_MAX &&
               i >= 0 && i <= GAIN_MAX &&
               d >= 0 && d <= GAIN_MAX;
  if (valid) {
    setpoint = sp;
    kp = p;
    ki = i;
    kd = d;
  }
}

void settingsSave() {
  prefs.putFloat("sp", setpoint);
  prefs.putFloat("kp", kp);
  prefs.putFloat("ki", ki);
  prefs.putFloat("kd", kd);
}

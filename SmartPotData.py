import json


class SmartPotData:
    def __init__(self, pi_id, temperature, humidity, soil_moisture, light, measured_at_time):
        self.pi_id = pi_id
        self.temperature = temperature
        self.humidity = humidity
        self.soil_moisture = soil_moisture
        self.light = light
        self.measured_at_time = measured_at_time

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_string(self):
        return ";".join((self.xstr(self.pi_id), self.xstr(self.temperature), self.xstr(self.humidity),
                         self.xstr(self.soil_moisture), self.xstr(self.light),
                         self.xstr(self.measured_at_time)))

    def xstr(self, s):
        if s is None:
            return ''
        else:
            return str(s)
import json


class SmartPotData:
    def __init__(self, pi_id, temperature, humidity, soil_moisture, is_raining):
        self.pi_id = pi_id
        self.temperature = temperature
        self.humidity = humidity
        self.soil_moisture = soil_moisture
        self.is_raining = is_raining

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

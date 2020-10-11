import json

class SmartPotData:
    def __init__(self, temperature, humidity, soil_moisture, is_raining):
        self.temperature = temperature
        self.humidity = humidity
        self.soil_moisture = soil_moisture
        self.is_raining = is_raining

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
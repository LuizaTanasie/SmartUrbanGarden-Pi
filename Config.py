class Config:
    API = "https://sg-func.azurewebsites.net/api/"
    SOIL_VERY_WET = 25000
    SOIL_VERY_DRY = 55000
    DIM_LIGHT = 70000
    STRONG_LIGHT = 0
    BACKUP_FILE = "backup.txt"
    BACKUP_ENTRIES_TO_SEND = 5
    BACKUP_FILE_MAX_SIZE = 10000000  # 10MB
    MEASUREMENT_TIME = 1800.0
    ERROR_MEASUREMENT_TIME = 30.0

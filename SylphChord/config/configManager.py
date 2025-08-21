import json
from config.settings import Config

class ConfigManager:
    def __init__(self):
        self.runTimeConfig = {}
        self.loadUserConfig()
    
    def loadUserConfig(self):
        try:
            with open("config/userConfig.json", "r") as f:
                self.runTimeConfig = json.load(f)
        except FileNotFoundError:
            pass
    
    def saveUserConfig(self):
        with open("config/userConfig.json", "w") as f:
            json.dump(self.runTimeConfig, f, indent = 2)
    
    def getSetting(self, key, default = None):
        return self.runTimeConfig.get(key, getattr(Config, key, default))
    
    def setSetting(self, key, value):
        self.runTimeConfig[key] = value
        self.saveUserConfig()
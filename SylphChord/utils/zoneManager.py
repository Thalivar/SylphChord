import json
import os

class ZoneManager:
    def __init__(self, zoneFiles = "config/zones.json"):
        self.zonesFile = zoneFiles
        self.zones = self.loadZones()

    def loadZones(self):
        basePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        zonesPath = os.path.join(basePath, self.zonesFile)

        try:
            with open(zonesPath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Zones file not found: {zonesPath}")
            return {}
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in zones file: {e}")
            return {}
    
    def isInZone(self, x, y, zoneName):
        if zoneName not in self.zones:
            return False
        
        zone = self.zones[zoneName]
        if not isinstance(zone, dict) or "topLeft" not in zone or "bottomRight" not in zone:
            return False
        
        x1, y1 = zone["topLeft"]
        x2, y2 = zone["bottomRight"]
        return x1 <= x <= x2 and y1 <= y <= y2

    def drawZones(self, frame):
        import cv2
        for name, zone in self.zones.items():
            if not isinstance(zone, dict) or "topLeft" not in zone:
                continue
                
            x1, y1 = zone["topLeft"]
            x2, y2 = zone["bottomRight"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
            cv2.putText(frame, name.capitalize(), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
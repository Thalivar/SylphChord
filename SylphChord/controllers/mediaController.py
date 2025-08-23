import subprocess
import time
from config.settings import Config

class MediaController:
    def __init__(self, player = "spotify"):
        self.player = player
        self.lastTriggered = {
            "playPause": 0,
            "next": 0,
            "prev": 0
        }
    
    def executeCommand(self, command, actionName):
        try:
            playersToTry = list(dict.fromkeys([self.player, "spotify", "%any"]))
            
            for player in playersToTry:
                try:
                    subprocess.run([
                        "playerctl", "-p", player, command
                    ], check = True, timeout = 2)
                    print(f"[MEDIA] {actionName} triggered on {player}")
                    return True
                except subprocess.CalledProcessError:
                    continue
                except subprocess.TimeoutExpired:
                    continue
            
            print(f"[ERROR] Failed to execute {actionName} on any player")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to execute {actionName}: {e}")
            return False
    
    def canTrigger(self, action):
        currentTime = time.monotonic()
        cooldownMap = {
            "playPause": Config.mediaCooldown,
            "next": Config.nextCooldown,
            "prev": Config.prevCooldown
        }

        if action not in cooldownMap:
            print(f"[ERROR] Unknow media action: {action}")
            return False

        cooldown = cooldownMap[action]
            
        return (currentTime - self.lastTriggered.get(action, 0)) >= cooldown
    
    def playPause(self):
        if self.canTrigger("playPause"):
            success = self.executeCommand("play-pause", "Play/Pause")
            if success:
                self.lastTriggered["playPause"] = time.monotonic()
                return True
        return False
    
    def nextSong(self):
        if self.canTrigger("next"):
            success = self.executeCommand("next", "Next Song")
            if success:
                self.lastTriggered["next"] = time.monotonic()
                return True
        return False
    
    def prevSong(self):
        if self.canTrigger("prev"):
            success = self.executeCommand("previous", "Previous Song")
            if success:
                self.lastTriggered["prev"] = time.monotonic()
                return True
        return False
import subprocess
from config.settings import Config

class MediaController:
    def __init__(self, player = "spotify"):
        self.player = player
        self.cooldowns = {
            "playPause": 0,
            "next": 0,
            "prev": 0
        }
        self.triggered = {
            "playPause": False,
            "next": False,
            "prev": False
        }
    
    def executeCommand(self, command, actionName):
        try:
            subprocess.run([
                "playerctl", "-p", self.player, command
            ], check = True)
            print(f"[MEDIA] {actionName} triggered")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to execute {actionName}: {e}")
    
    def playPause(self):
        if not self.triggered["playPause"]:
            self.executeCommand("play-pause", "Play/Pause")
            self.triggered["playPause"] = True
            self.cooldowns["playPause"] = Config.playPauseCooldown
    
    def nextSong(self):
        if not self.triggered["next"]:
            self.executeCommand("next", "Next Song")
            self.triggered["next"] = True
            self.cooldowns["next"] = Config.nextCooldown
    
    def prevSong(self):
        if not self.triggered["prev"]:
            self.executeCommand("previous", "Previous Song")
            self.triggered["prev"] = True
            self.cooldowns["prev"] = Config.prevCooldown
    
    def updateCooldowns(self):
        for action in self.cooldowns:
            if self.cooldowns[action] > 0:
                self.cooldowns[action] -= 1
            elif self.triggered[action]:
                self.triggered[action] = False
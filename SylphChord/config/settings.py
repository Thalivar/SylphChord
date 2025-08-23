class Config:
    
    # Camera Settings
    cameraIndex = 0
    frameWidth = 960
    frameHeight = 700
    minDetectionConfidence = 0.7

    # Performance settings
    minFpsThreshold = 15
    lowFpsThreshold = 10
    frameSkipRatio = 2

    # Volume Control
    defaultVolume = 50
    volumeSensitivity = 1.0
    smootherAlpha = 0.3
    volumeUpdateInterval = 30

    # Media Control
    playPauseCooldown = 3.0
    nextCooldown = 3.0
    prevCooldown = 3.0
    mediaCooldown = 3.0

    # Gesture detection
    fingerDistanceThreshold = 50
    fingerExtensionThreshold = 60
    grabMinFingers = 3
    grabMinGap = 30
    grabMaxGap = 120

    # Gesture settings
    gestureConfidenceThreshold = 0.7
    gestureStabilityFrames = 5
    gestureModeSwitchCooldown = 3.0
    gestureLockDuration = 1.0
    pointingGestureThreshold = 0.7
    buttonHoverTimer = 0.3
    buttonPressDepth = 0.5
    buttonReleaseDepth = 0.25
    pointingStabilityFrames = 3
    pointingConfidenceThreshold = 0.8
    calibrationDuration = 0.7

    # Multi-hand settings
    maxHands = 2
    handAssignmentMethod = "position"
    dominantHandPreference = "Right"

    # Ui Settings
    showLandmarksByDefault = False
    uiOpacity = 0.8
    notificationDuration = 2.0

    # Performace optimization
    enableFrameSkipping = True
    adaptiveProcessing = True
    lowPowerMode = False
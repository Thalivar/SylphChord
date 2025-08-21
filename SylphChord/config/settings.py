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
    playPauseCooldown = 30
    nextCooldown = 30
    prevCooldown = 30

    # Gesture detection
    fingerDistanceThreshold = 40
    fingerExtensionThreshold = 50
    grabMinFingers = 3
    grabMinGap = 30
    grabMaxGap = 120

    # Gesture settings
    gestureConfidenceThreshold = 0.7
    gestureStabilityFrames = 5
    gestureModeSwitchCooldown = 0.5
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
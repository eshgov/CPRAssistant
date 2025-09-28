# Improved CPR Assistant - Executable Version

## Overview
This is an executable version of the Improved CPR Assistant application that provides real-time CPR guidance and feedback using computer vision.

## Features
- 🎯 Improved BPM calculation (last 4 beats)
- 📊 Better compression detection
- ☁️ Cloud upload for model training
- 🔒 Face blurring for privacy
- 📱 Real-time feedback
- 🎵 Visual metronome (flashing)

## System Requirements
- Windows 10 or later
- Webcam/camera
- No additional software installation required

## How to Run
1. Double-click `ImprovedCPRAssistant.exe`
2. Grant camera permissions when prompted
3. Choose your mode:
   - **Walkthrough Mode**: Step-by-step guidance for beginners
   - **Feedback Mode**: Real-time feedback for trained responders

## Controls
- **Q**: Quit the application
- **N**: Next step (in Walkthrough mode)
- **S**: Skip to compressions (in Walkthrough mode)
- **U**: Upload session data to cloud

## Modes

### Walkthrough Mode
Perfect for beginners learning CPR:
1. Check responsiveness and call 911
2. Position victim on firm surface
3. Place hands in center of chest
4. Begin compressions at 100-120 BPM
5. Continue for 30 compressions
6. Give 2 rescue breaths
7. Resume compressions

### Feedback Mode
For trained responders who want real-time feedback:
- Live BPM calculation
- Hand placement scoring
- Compression depth monitoring
- Visual metronome guidance

## Troubleshooting

### Camera Issues
- Ensure your camera is connected and working
- Check that no other applications are using the camera
- Try running as administrator if camera access is denied

### Performance Issues
- Close other applications to free up system resources
- Ensure good lighting for better pose detection
- Position yourself clearly in front of the camera

### Privacy
- The application includes face blurring for privacy
- Session data can be uploaded to cloud for model training (optional)
- No personal data is stored locally

## Technical Details
- Built with Python, OpenCV, and MediaPipe
- Uses pose estimation for hand tracking
- Implements improved BPM calculation algorithms
- Includes privacy protection features

## Support
If you encounter any issues:
1. Check that your camera is working
2. Ensure you have proper lighting
3. Try restarting the application
4. Check system requirements

## Disclaimer
This application is for training purposes only. In real emergency situations, always call 911 and follow certified CPR guidelines.

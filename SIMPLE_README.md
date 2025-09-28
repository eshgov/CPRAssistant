# Simple CPR Assistant App

A simplified CPR guidance application using Python and MediaPipe. **No audio dependencies** - just visual feedback and guidance.

## Features

### 🎯 Core Functionality
- **Real-time pose estimation** using MediaPipe for hand and body tracking
- **Visual feedback only** - no audio dependencies
- **Visual metronome** - flashing screen indicator for rhythm
- **Live performance feedback** on compression depth, rhythm, and hand placement
- **Step-by-step walkthrough** for untrained users
- **Real-time feedback mode** for trained responders

### 🎮 Two Operating Modes

#### Walkthrough Mode
- Step-by-step CPR guidance
- Visual prompts and instructions
- Auto-advancing steps
- "Skip to Compressions" option
- Perfect for untrained bystanders

#### Feedback Mode
- Immediate real-time feedback
- Live camera overlay with pose estimation
- Visual metronome (flashing indicator)
- Compression counting and breath prompts
- Ideal for trained responders

## Installation

### Prerequisites
- Python 3.9 or 3.10
- Webcam or camera device

### Setup

1. **Create conda environment**:
```bash
conda create -n cpr_assistant python=3.9
conda activate cpr_assistant
```

2. **Install dependencies**:
```bash
pip install -r simple_requirements.txt
```

### Dependencies

The simplified app only requires:
- `opencv-python`: Computer vision and camera handling
- `mediapipe`: Pose estimation and hand tracking
- `numpy`: Numerical computations

**No audio packages needed!**

## Usage

### Quick Start

1. **Run the application**:
```bash
python run_simple_cpr.py
```

2. **Or run directly**:
```bash
python simple_cpr_assistant.py
```

3. **Select your mode**:
   - **Walkthrough Mode**: For step-by-step guidance
   - **Feedback Mode**: For real-time feedback

### Controls

During CPR practice:
- **'Q'**: Quit the application
- **'N'**: Next step (Walkthrough mode)
- **'S'**: Skip to compressions (Walkthrough mode)

## Visual Feedback

### Performance Metrics
- **BPM Display**: Real-time compression rate with color coding
- **Hand Placement Score**: Accuracy of hand positioning
- **Compression Depth**: Estimated compression depth
- **Visual Messages**: On-screen feedback and guidance

### Color Coding
- **Green**: Good performance (100-120 BPM, good placement, adequate depth)
- **Red**: Needs improvement (too slow, poor placement, insufficient depth)
- **Orange**: Too fast rhythm

### Visual Metronome
- **Flashing Border**: Screen flashes green at target BPM
- **"BEAT" Indicator**: Large text appears on screen
- **No Audio**: Completely silent operation

## Technical Details

### Pose Estimation
- Uses MediaPipe for real-time pose and hand tracking
- Tracks hand placement relative to chest center
- Monitors compression depth and rhythm
- Provides visual feedback with color-coded indicators

### Performance Metrics
- **BPM Tracking**: Real-time compression rate monitoring
- **Hand Placement Score**: Accuracy of hand positioning (0-100%)
- **Compression Depth**: Estimated compression depth (0-100%)
- **Rhythm Analysis**: Consistency of compression timing

## Troubleshooting

### Common Issues

1. **Camera not detected**:
   - Ensure camera is connected and not used by other applications
   - Check camera permissions

2. **Performance issues**:
   - Close other applications to free up resources
   - Ensure good lighting for pose estimation

### System Requirements
- **OS**: Windows, macOS, or Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Camera**: USB webcam or built-in camera
- **Python**: 3.9 or 3.10

## Project Structure
```
CPRAssistant/
├── simple_cpr_assistant.py      # Main simplified application
├── run_simple_cpr.py           # Launcher script
├── simple_requirements.txt     # Minimal dependencies
└── SIMPLE_README.md            # This file
```

## Advantages of Simplified Version

✅ **Easy Installation**: No complex audio dependencies
✅ **Cross-Platform**: Works on any system with Python
✅ **Lightweight**: Minimal package requirements
✅ **Visual Feedback**: Clear, color-coded performance indicators
✅ **No Audio Issues**: No microphone or speaker requirements
✅ **Quick Setup**: Install and run in minutes

## Safety Features

### Emergency Information
- Persistent "Call 911!" display
- Emergency response guidance
- Safety-first approach to CPR instruction

### Accuracy Measures
- Based on current AHA (American Heart Association) guidelines
- Real-time feedback prevents poor technique
- Visual guidance ensures proper form

## License

This project is licensed under the MIT License.

## Disclaimer

This application is for educational and training purposes only. It is not a substitute for proper CPR certification or professional medical training. Always call 911 in emergency situations and seek proper medical training.

---

**Remember**: This app is designed to assist with CPR training and guidance. In real emergency situations, always call 911 immediately and follow proper emergency protocols.

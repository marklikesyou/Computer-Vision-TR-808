# Virtual TR-808 Finger Drummer

A computer vision-based virtual drum machine that lets you play TR-808 sounds using hand gestures. Built with Python, OpenCV, MediaPipe, and Streamlit.

![TR-808 Finger Drummer](screenshot.jpg)

## Features

- **Hand Gesture Control**: Play drums using natural finger movements
- **TR-808 Sounds**: Classic drum machine sounds including kicks, snares, hi-hats, and more
- **Multiple Modes**:

  - Training: Beginner-friendly with basic sounds
  - Practice: Standard settings for regular practice
  - Performance: Enhanced sensitivity for live playing
  - Expert: Maximum control and sensitivity
  - Custom: User-defined settings

- **Skill Progression System**:

  - Level 1: Basic sounds (Kick, Snare, Hi-Hat)
  - Level 2: Intermediate sounds (Clap, Cymbal, Tom)
  - Level 3: Advanced sounds (All TR-808 sounds)

- **Real-time Controls**:
  - Individual volume controls for each sound
  - Enable/disable specific sounds
  - Visual feedback for triggers
  - Mode and sensitivity adjustments

## Requirements

- Python 3.8+
- Webcam
- Speakers or headphones

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/virtual-tr808-drummer.git
cd virtual-tr808-drummer
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
streamlit run virtual_drumkit.py
```

2. Allow webcam access when prompted

3. Use the sidebar to:

   - Select your mode (Training/Practice/Performance/Expert)
   - Set your skill level (1-3)
   - Adjust individual sound volumes
   - Enable/disable specific sounds

4. Play drums by moving your fingers downward:
   - Right Hand:
     - Thumb: Kick
     - Index: Snare
     - Middle: Hi-Hat
     - Ring: Clap
     - Pinky: Cymbal
   - Left Hand:
     - Thumb: Tom Low
     - Index: Tom Mid
     - Middle: Tom High
     - Ring: Cowbell
     - Pinky: Rimshot

## Tips for Best Performance

1. **Lighting**: Ensure good lighting for better hand tracking
2. **Camera Position**: Position your webcam to clearly see your hands
3. **Hand Movements**: Make clear downward motions for reliable triggering
4. **Start Simple**: Begin with Training mode and basic sounds
5. **Practice**: Progress through skill levels as you get comfortable

## Controls

- **Mode Selection**: Changes sensitivity and available features
- **Skill Level**: Determines available sounds
- **Volume Controls**: Adjust individual sound volumes
- **Sound Toggles**: Enable/disable specific sounds
- **Stop Button**: Ends the session

## Troubleshooting

- If sounds aren't triggering, try adjusting your lighting
- Ensure your hands are clearly visible to the camera
- Start with Training mode to get familiar with the gestures
- Adjust your distance from the camera for optimal tracking

## Notes

- TR-808 samples included in the project
- MediaPipe for hand tracking
- OpenCV for computer vision
- Streamlit for the user interface

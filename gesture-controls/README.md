# AeroTouch Gesture Controller

Control your computer using hand gestures!

## Gestures

| Gesture | Action |
|---------|--------|
| 🖐️ **Open Palm** | Move cursor |
| 👌 **Pinch (Thumb + Index)** | Click |
| 👍 **Thumbs Up** | Scroll up |
| 👎 **Thumbs Down** | Scroll down |

## Installation

1. Make sure you have Python 3.8+ installed

2. Install dependencies:
   ```bash
   cd gesture-controls
   pip install -r requirements.txt
   ```

3. On macOS, you may need to grant camera and accessibility permissions:
   - **Camera**: System Preferences → Privacy & Security → Camera → Allow Terminal/Python
   - **Accessibility**: System Preferences → Privacy & Security → Accessibility → Add Terminal/Python

## Usage

```bash
python gesture_controller.py
```

Press **'q'** to quit the application.

## Tips

- Keep your hand within the camera frame
- Ensure good lighting for better detection
- Hold gestures briefly for recognition
- The cursor follows your index finger when palm is open
- Pinch gesture triggers a single click with cooldown to prevent multiple clicks

## Troubleshooting

- **Camera not working**: Check camera permissions in System Preferences
- **Cursor not moving**: Grant Accessibility permissions to Terminal/Python
- **Gestures not recognized**: Ensure good lighting and keep hand clearly visible

"""
AeroTouch - Hand Gesture Controller
Controls cursor movement, clicking, and scrolling using hand gestures.

Gestures:
- Claw-Open (spread fingers): Move cursor
- Claw-Closed (bunched fingertips): Click
- Thumbs Up: Scroll up
- Thumbs Down: Scroll down
"""

import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# Disable PyAutoGUI fail-safe (optional, but be careful)
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Smoothing factor for cursor movement
SMOOTHING = 3
prev_hand_x, prev_hand_y = None, None
is_palm_open = False  # Track if palm was open in previous frame

# Cursor movement sensitivity (higher = faster cursor movement)
CURSOR_SENSITIVITY = 1.5

# Gesture cooldowns to prevent repeated actions
last_click_time = 0
last_scroll_time = 0
CLICK_COOLDOWN = 0.5  # seconds
SCROLL_COOLDOWN = 0.2  # seconds

# Gesture state tracking
gesture_state = {
    'is_clicking': False,
    'is_scrolling_up': False,
    'is_scrolling_down': False
}


def get_finger_positions(hand_landmarks):
    """Extract key finger landmark positions."""
    landmarks = hand_landmarks.landmark
    
    return {
        'wrist': landmarks[mp_hands.HandLandmark.WRIST],
        'thumb_tip': landmarks[mp_hands.HandLandmark.THUMB_TIP],
        'thumb_ip': landmarks[mp_hands.HandLandmark.THUMB_IP],
        'thumb_mcp': landmarks[mp_hands.HandLandmark.THUMB_MCP],
        'index_tip': landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP],
        'index_pip': landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP],
        'index_mcp': landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP],
        'middle_tip': landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
        'middle_pip': landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP],
        'ring_tip': landmarks[mp_hands.HandLandmark.RING_FINGER_TIP],
        'ring_pip': landmarks[mp_hands.HandLandmark.RING_FINGER_PIP],
        'pinky_tip': landmarks[mp_hands.HandLandmark.PINKY_TIP],
        'pinky_pip': landmarks[mp_hands.HandLandmark.PINKY_PIP],
    }


def calculate_distance(point1, point2):
    """Calculate Euclidean distance between two landmarks."""
    return np.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)


def is_finger_extended(tip, pip):
    """Check if a finger is extended (tip is above pip in y-axis)."""
    return tip.y < pip.y


def is_thumb_extended_up(positions):
    """Check if thumb is pointing up (for thumbs up gesture)."""
    thumb_tip = positions['thumb_tip']
    thumb_mcp = positions['thumb_mcp']
    wrist = positions['wrist']
    
    # Thumb tip should be significantly above thumb base
    return thumb_tip.y < thumb_mcp.y - 0.1 and thumb_tip.y < wrist.y - 0.15


def is_thumb_extended_down(positions):
    """Check if thumb is pointing down (for thumbs down gesture)."""
    thumb_tip = positions['thumb_tip']
    thumb_mcp = positions['thumb_mcp']
    wrist = positions['wrist']
    
    # Thumb tip should be significantly below thumb base
    return thumb_tip.y > thumb_mcp.y + 0.05 and thumb_tip.y > wrist.y


def detect_open_palm(positions):
    """Detect open palm gesture - all fingers extended."""
    index_extended = is_finger_extended(positions['index_tip'], positions['index_pip'])
    middle_extended = is_finger_extended(positions['middle_tip'], positions['middle_pip'])
    ring_extended = is_finger_extended(positions['ring_tip'], positions['ring_pip'])
    pinky_extended = is_finger_extended(positions['pinky_tip'], positions['pinky_pip'])
    
    # Check if thumb is spread out (not tucked in)
    thumb_spread = positions['thumb_tip'].x < positions['index_mcp'].x - 0.05 or \
                   positions['thumb_tip'].x > positions['index_mcp'].x + 0.05
    
    return index_extended and middle_extended and ring_extended and pinky_extended and thumb_spread


def calculate_fingertip_cluster_radius(positions):
    """Calculate the average distance of all fingertips from their centroid."""
    tips = [
        positions['thumb_tip'],
        positions['index_tip'],
        positions['middle_tip'],
        positions['ring_tip'],
        positions['pinky_tip']
    ]
    
    # Calculate centroid
    centroid_x = sum(t.x for t in tips) / 5
    centroid_y = sum(t.y for t in tips) / 5
    
    # Calculate average distance from centroid
    total_distance = 0
    for tip in tips:
        dist = np.sqrt((tip.x - centroid_x)**2 + (tip.y - centroid_y)**2)
        total_distance += dist
    
    return total_distance / 5


def detect_claw_open(positions):
    """
    Detect Claw-Open gesture for moving cursor.
    All fingers curved but separated, visible tips, spread out.
    """
    # Calculate how spread out the fingertips are
    cluster_radius = calculate_fingertip_cluster_radius(positions)
    
    # Check that fingers are somewhat extended (tips visible, not fully curled)
    # Using a relaxed check - tips should be at least somewhat away from palm
    wrist = positions['wrist']
    index_tip = positions['index_tip']
    middle_tip = positions['middle_tip']
    
    # Distance from wrist to fingertips should be reasonable (hand is open-ish)
    index_dist = calculate_distance(wrist, index_tip)
    middle_dist = calculate_distance(wrist, middle_tip)
    
    fingers_visible = index_dist > 0.15 and middle_dist > 0.15
    
    # Claw-open: spread out fingertips (large cluster radius)
    is_spread = cluster_radius > 0.08
    
    return is_spread and fingers_visible


def detect_claw_closed(positions):
    """
    Detect Claw-Closed gesture for clicking.
    All fingertips bunched together, almost touching (tight cluster).
    """
    # Calculate how close the fingertips are to each other
    cluster_radius = calculate_fingertip_cluster_radius(positions)
    
    # Check that fingers are somewhat extended (not a full fist)
    wrist = positions['wrist']
    index_tip = positions['index_tip']
    middle_tip = positions['middle_tip']
    
    index_dist = calculate_distance(wrist, index_tip)
    middle_dist = calculate_distance(wrist, middle_tip)
    
    # Fingers should still be somewhat visible (not a fist)
    fingers_visible = index_dist > 0.12 and middle_dist > 0.12
    
    # Claw-closed: tight cluster of fingertips (small cluster radius)
    is_bunched = cluster_radius < 0.06
    
    return is_bunched and fingers_visible


def detect_pinch(positions, threshold=0.05):
    """Detect pinch gesture - thumb and index finger tips touching."""
    distance = calculate_distance(positions['thumb_tip'], positions['index_tip'])
    return distance < threshold


def detect_thumbs_up(positions):
    """Detect thumbs up gesture - thumb up, other fingers closed."""
    # Thumb should be pointing up
    thumb_up = is_thumb_extended_up(positions)
    
    # Other fingers should be curled (not extended)
    index_curled = not is_finger_extended(positions['index_tip'], positions['index_pip'])
    middle_curled = not is_finger_extended(positions['middle_tip'], positions['middle_pip'])
    ring_curled = not is_finger_extended(positions['ring_tip'], positions['ring_pip'])
    pinky_curled = not is_finger_extended(positions['pinky_tip'], positions['pinky_pip'])
    
    return thumb_up and index_curled and middle_curled and ring_curled and pinky_curled


def detect_thumbs_down(positions):
    """Detect thumbs down gesture - thumb down, other fingers closed."""
    # Thumb should be pointing down
    thumb_down = is_thumb_extended_down(positions)
    
    # Other fingers should be curled (not extended)
    index_curled = not is_finger_extended(positions['index_tip'], positions['index_pip'])
    middle_curled = not is_finger_extended(positions['middle_tip'], positions['middle_pip'])
    ring_curled = not is_finger_extended(positions['ring_tip'], positions['ring_pip'])
    pinky_curled = not is_finger_extended(positions['pinky_tip'], positions['pinky_pip'])
    
    return thumb_down and index_curled and middle_curled and ring_curled and pinky_curled


def move_cursor(positions, frame_width, frame_height):
    """Move cursor based on hand movement (relative movement)."""
    global prev_hand_x, prev_hand_y, is_palm_open
    
    # Use index finger MCP (knuckle at base of index finger) for tracking
    index_mcp = positions['index_mcp']
    current_hand_x = index_mcp.x
    current_hand_y = index_mcp.y
    
    # If palm just opened, store position and wait for next frame
    if not is_palm_open:
        prev_hand_x = current_hand_x
        prev_hand_y = current_hand_y
        is_palm_open = True
        return
    
    # Calculate hand movement delta
    delta_x = (current_hand_x - prev_hand_x) * SCREEN_WIDTH * CURSOR_SENSITIVITY
    delta_y = (current_hand_y - prev_hand_y) * SCREEN_HEIGHT * CURSOR_SENSITIVITY
    
    # Get current cursor position
    current_cursor_x, current_cursor_y = pyautogui.position()
    
    # Apply delta to cursor position
    new_x = current_cursor_x + delta_x
    new_y = current_cursor_y + delta_y
    
    # Clamp to screen bounds
    new_x = max(0, min(SCREEN_WIDTH - 1, new_x))
    new_y = max(0, min(SCREEN_HEIGHT - 1, new_y))
    
    # Move cursor
    pyautogui.moveTo(new_x, new_y)
    
    # Store current hand position for next frame
    prev_hand_x = current_hand_x
    prev_hand_y = current_hand_y


def perform_click():
    """Perform a mouse click."""
    global last_click_time
    
    current_time = time.time()
    if current_time - last_click_time > CLICK_COOLDOWN:
        pyautogui.click()
        last_click_time = current_time
        return True
    return False


def perform_scroll(direction):
    """Perform scroll action."""
    global last_scroll_time
    
    current_time = time.time()
    if current_time - last_scroll_time > SCROLL_COOLDOWN:
        if direction == 'up':
            pyautogui.scroll(3)  # Scroll up
        else:
            pyautogui.scroll(-3)  # Scroll down
        last_scroll_time = current_time
        return True
    return False


def draw_gesture_info(frame, gesture_name, color=(0, 255, 0)):
    """Draw gesture information on frame."""
    cv2.putText(frame, f"Gesture: {gesture_name}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)


def main():
    """Main function to run the gesture controller."""
    global is_palm_open
    
    print("=" * 50)
    print("AeroTouch - Hand Gesture Controller")
    print("=" * 50)
    print("\nGestures:")
    print("  - Claw-Open (spread fingers): Move cursor")
    print("  - Claw-Closed (bunched fingertips): Click")
    print("  - Thumbs Up: Scroll up")
    print("  - Thumbs Down: Scroll down")
    print("\nPress 'q' to quit")
    print("=" * 50)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        max_num_hands=1
    ) as hands:
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Failed to read from camera")
                continue
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            frame_height, frame_width, _ = frame.shape
            
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False
            
            # Process hand detection
            results = hands.process(rgb_frame)
            
            rgb_frame.flags.writeable = True
            frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            
            gesture_detected = "None"
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw hand landmarks
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Get finger positions
                    positions = get_finger_positions(hand_landmarks)
                    
                    # Detect gestures (in priority order)
                    if detect_claw_closed(positions):
                        gesture_detected = "CLICK (Claw-Closed)"
                        if perform_click():
                            cv2.circle(frame, (frame_width // 2, frame_height // 2), 
                                      30, (0, 0, 255), -1)
                        is_palm_open = False
                    
                    elif detect_thumbs_up(positions):
                        gesture_detected = "SCROLL UP (Thumbs Up)"
                        perform_scroll('up')
                        is_palm_open = False
                    
                    elif detect_thumbs_down(positions):
                        gesture_detected = "SCROLL DOWN (Thumbs Down)"
                        perform_scroll('down')
                        is_palm_open = False
                    
                    elif detect_claw_open(positions):
                        gesture_detected = "MOVE CURSOR (Claw-Open)"
                        move_cursor(positions, frame_width, frame_height)
                    else:
                        # No recognized gesture - reset state
                        is_palm_open = False
            else:
                # No hand detected - reset state
                is_palm_open = False
            
            # Draw gesture info
            color = (0, 255, 0) if gesture_detected != "None" else (128, 128, 128)
            draw_gesture_info(frame, gesture_detected, color)
            
            # Draw instructions
            cv2.putText(frame, "Press 'q' to quit", (10, frame_height - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('AeroTouch - Gesture Controller', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nGesture controller stopped.")


if __name__ == "__main__":
    main()

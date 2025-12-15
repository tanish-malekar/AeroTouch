# AeroTouch

**AeroTouch** is a hygienic, accessible, and futuristic hand gesture-controlled user interface designed for public displays, such as self-service kiosks (e.g., McDonald's ordering screens). In a post-pandemic world, minimizing physical contact with public surfaces is crucial. AeroTouch addresses this by allowing users to navigate menus, select items, and scroll through options using simple, intuitive hand gestures without ever touching the screen.

## 🚀 Features

*   **Touchless Interface**: Completely eliminates the need for physical touch, reducing the spread of germs on public screens.
*   **Intuitive Gestures**: Uses natural hand movements (pointing, making a fist) that are easy to learn and execute.
*   **Real-time Response**: Powered by MediaPipe and OpenCV for low-latency hand tracking and immediate cursor response.
*   **Interactive UI**: A fully functional mock-up of a food ordering kiosk designed to demonstrate the gesture control capabilities.
*   **Accessibility**: Provides an alternative interaction method for users who may have difficulty accessing large touchscreens due to physical limitations such as height.

## 📂 Project Structure

The project is divided into two main components:

1.  **`UI/`**: The frontend web application.
    *   Contains the HTML, CSS, and JavaScript for the food ordering kiosk interface.
    *   Features a responsive menu, cart system, and an integrated "How to Operate" guide.
2.  **`gesture-controls/`**: The backend gesture recognition engine.
    *   Written in Python.
    *   Uses **OpenCV** and **MediaPipe** to detect hand landmarks from the webcam.
    *   Uses **PyAutoGUI** to translate hand gestures into system-wide mouse actions (movement, clicks, scrolling).

## 🛠️ Prerequisites

*   **Python 3.8+**
*   **Webcam**: A functional webcam is required for hand tracking.
*   **Web Browser**: To display the UI (Chrome, Firefox, Safari, etc.).

## 📦 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/AeroTouch.git
    cd AeroTouch
    ```

2.  **Set up the Gesture Controller**
    Navigate to the `gesture-controls` directory and install the required dependencies:
    ```bash
    cd gesture-controls
    pip install -r requirements.txt
    ```
    *Note: It is recommended to use a virtual environment.*
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

## 🎮 How to Run

1.  **Start the Gesture Controller**
    Run the Python script to start tracking your hand and controlling the mouse:
    ```bash
    # From the gesture-controls directory
    python gesture_controller.py
    ```
    *Ensure your webcam acts as the active window or is visible. The script will open a window showing the camera feed with gesture diagnostics.*

2.  **Launch the UI**
    Open the `UI/index.html` file in your preferred web browser. You can typically do this by double-clicking the file or running a simple local server:
    ```bash
    # From the UI directory (optional)
    open index.html # on Mac
    # OR
    start index.html # on Windows
    ```

3.  **Operate**
    Stand in front of the webcam. Your hand movements will now control the mouse cursor on the screen!

## 🖐️ Gesture Guide

The system recognizes the following gestures to interact with the UI:

| Action | Gesture | Description |
| :--- | :--- | :--- |
| **Move Cursor** | **Claw-Open** 🖐️ | Spread all fingers slightly apart (like a relaxed open hand). Move your hand to move the cursor. |
| **Select / Click** | **Closed Fist** ✊ | Clench your hand into a fist to perform a click. |
| **Scroll Up** | **Point Up** 👆 | Extend your index finger upwards while keeping other fingers closed. |
| **Scroll Down** | **Point Down** 👇 | Extend your index finger downwards. |

## 🛡️ License

[MIT License](LICENSE) - flree to use and modify for educational and personal projects.

"""
CPR Assistant App - Comprehensive CPR Guidance with MediaPipe and LLM
"""

import cv2
import mediapipe as mp
import numpy as np
import pygame
import threading
import time
import math
import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
import pyttsx3
from typing import Optional, Tuple, List
import queue
import json

class CPRAssistant:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize pose and hands
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize audio
        pygame.mixer.init()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
        # CPR tracking variables
        self.compression_count = 0
        self.current_bpm = 0
        self.target_bpm = 110  # 100-120 BPM range
        self.compression_depth = 0
        self.hand_placement_score = 0
        self.last_compression_time = 0
        self.compression_times = []
        self.metronome_active = False
        self.mode = None  # 'walkthrough' or 'feedback'
        
        # UI variables
        self.camera = None
        self.running = False
        self.current_step = 0
        self.step_timer = 0
        
        # Walkthrough steps
        self.walkthrough_steps = [
            "Check responsiveness and call 911",
            "Position victim on firm surface",
            "Place hands in center of chest",
            "Begin compressions at 100-120 BPM",
            "Continue for 30 compressions",
            "Give 2 rescue breaths",
            "Resume compressions"
        ]
        
        # Audio feedback queue
        self.audio_queue = queue.Queue()
        
    def initialize_camera(self):
        """Initialize camera capture"""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise Exception("Could not open camera")
        
        # Set camera properties for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
    def calculate_bpm(self, compression_times):
        """Calculate BPM from compression timing"""
        if len(compression_times) < 2:
            return 0
        
        # Calculate intervals between compressions
        intervals = []
        for i in range(1, len(compression_times)):
            interval = compression_times[i] - compression_times[i-1]
            intervals.append(interval)
        
        if not intervals:
            return 0
        
        # Calculate average interval and convert to BPM
        avg_interval = sum(intervals) / len(intervals)
        bpm = 60 / avg_interval if avg_interval > 0 else 0
        
        return min(max(bpm, 0), 200)  # Clamp between 0-200 BPM
    
    def detect_hand_placement(self, landmarks):
        """Detect if hands are properly placed for CPR"""
        if not landmarks:
            return 0
        
        # Get key points for hand placement
        left_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        # Calculate chest center (between shoulders)
        chest_center_x = (left_shoulder.x + right_shoulder.x) / 2
        chest_center_y = (left_shoulder.y + right_shoulder.y) / 2
        
        # Calculate hand positions relative to chest center
        left_distance = math.sqrt((left_wrist.x - chest_center_x)**2 + (left_wrist.y - chest_center_y)**2)
        right_distance = math.sqrt((right_wrist.x - chest_center_x)**2 + (right_wrist.y - chest_center_y)**2)
        
        # Score based on how close hands are to chest center
        avg_distance = (left_distance + right_distance) / 2
        score = max(0, 1 - avg_distance * 10)  # Scale factor for distance
        
        return score
    
    def detect_compression_depth(self, landmarks):
        """Detect compression depth based on hand movement"""
        if not landmarks:
            return 0
        
        # This is a simplified depth detection
        # In a real implementation, you'd track hand position over time
        left_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        
        # Calculate vertical movement (simplified)
        hand_y = (left_wrist.y + right_wrist.y) / 2
        depth = 1 - hand_y  # Normalize depth (0-1)
        
        return depth
    
    def start_metronome(self):
        """Start the metronome at target BPM"""
        if self.metronome_active:
            return
        
        self.metronome_active = True
        metronome_thread = threading.Thread(target=self._metronome_loop)
        metronome_thread.daemon = True
        metronome_thread.start()
    
    def stop_metronome(self):
        """Stop the metronome"""
        self.metronome_active = False
    
    def _metronome_loop(self):
        """Metronome audio loop"""
        interval = 60.0 / self.target_bpm
        
        while self.metronome_active:
            # Generate metronome click sound
            self._play_metronome_click()
            time.sleep(interval)
    
    def _play_metronome_click(self):
        """Play metronome click sound"""
        # Generate a simple click sound using pygame
        sample_rate = 22050
        duration = 0.1
        frequency = 1000
        
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            arr[i][0] = np.sin(2 * np.pi * frequency * i / sample_rate) * 0.1
            arr[i][1] = arr[i][0]
        
        sound = pygame.sndarray.make_sound(arr.astype(np.int16))
        sound.play()
    
    def speak(self, text):
        """Convert text to speech"""
        def _speak():
            self.engine.say(text)
            self.engine.runAndWait()
        
        speech_thread = threading.Thread(target=_speak)
        speech_thread.daemon = True
        speech_thread.start()
    
    def get_feedback_color(self, bpm):
        """Get color based on BPM feedback"""
        if 100 <= bpm <= 120:
            return (0, 255, 0)  # Green - good pace
        elif bpm < 100:
            return (0, 0, 255)  # Red - too slow
        else:
            return (0, 165, 255)  # Orange - too fast
    
    def process_frame(self, frame):
        """Process a single frame for CPR feedback"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process pose
        pose_results = self.pose.process(rgb_frame)
        
        # Process hands
        hands_results = self.hands.process(rgb_frame)
        
        # Draw pose landmarks
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )
            
            # Analyze hand placement
            self.hand_placement_score = self.detect_hand_placement(pose_results.pose_landmarks)
            
            # Analyze compression depth
            self.compression_depth = self.detect_compression_depth(pose_results.pose_landmarks)
        
        # Draw hand landmarks
        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
        
        return frame, pose_results, hands_results
    
    def add_overlay_info(self, frame):
        """Add CPR feedback overlay to frame"""
        height, width = frame.shape[:2]
        
        # Background for text
        overlay = frame.copy()
        
        # Current BPM
        bpm_color = self.get_feedback_color(self.current_bpm)
        cv2.rectangle(overlay, (10, 10), (200, 80), (0, 0, 0), -1)
        cv2.putText(frame, f"BPM: {int(self.current_bpm)}", (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, bpm_color, 2)
        
        # Compression count
        cv2.rectangle(overlay, (10, 90), (200, 130), (0, 0, 0), -1)
        cv2.putText(frame, f"Count: {self.compression_count}", (20, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Hand placement score
        placement_color = (0, 255, 0) if self.hand_placement_score > 0.7 else (0, 0, 255)
        cv2.rectangle(overlay, (10, 140), (200, 180), (0, 0, 0), -1)
        cv2.putText(frame, f"Hands: {int(self.hand_placement_score*100)}%", (20, 170), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, placement_color, 2)
        
        # Emergency info
        cv2.rectangle(overlay, (width-200, 10), (width-10, 50), (0, 0, 255), -1)
        cv2.putText(frame, "CALL 911!", (width-190, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Mode indicator
        mode_text = "Walkthrough" if self.mode == "walkthrough" else "Feedback"
        cv2.rectangle(overlay, (width-200, 60), (width-10, 100), (0, 100, 0), -1)
        cv2.putText(frame, mode_text, (width-190, 85), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def run_walkthrough_mode(self):
        """Run step-by-step CPR walkthrough"""
        self.mode = "walkthrough"
        self.current_step = 0
        
        # Start with first step
        self.speak(self.walkthrough_steps[self.current_step])
        
        while self.running and self.current_step < len(self.walkthrough_steps):
            ret, frame = self.camera.read()
            if not ret:
                break
            
            # Process frame
            processed_frame, pose_results, hands_results = self.process_frame(frame)
            
            # Add overlay
            frame_with_overlay = self.add_overlay_info(processed_frame)
            
            # Show current step
            step_text = f"Step {self.current_step + 1}: {self.walkthrough_steps[self.current_step]}"
            cv2.putText(frame_with_overlay, step_text, (10, height-50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show "Skip to Compressions" button
            cv2.rectangle(frame_with_overlay, (width-200, height-80), (width-10, height-20), (0, 255, 0), -1)
            cv2.putText(frame_with_overlay, "Skip to Compressions", (width-190, height-45), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            cv2.imshow('CPR Assistant - Walkthrough Mode', frame_with_overlay)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n'):  # Next step
                self.current_step += 1
                if self.current_step < len(self.walkthrough_steps):
                    self.speak(self.walkthrough_steps[self.current_step])
            elif key == ord('s'):  # Skip to compressions
                self.run_feedback_mode()
                break
    
    def run_feedback_mode(self):
        """Run real-time feedback mode"""
        self.mode = "feedback"
        self.start_metronome()
        
        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                break
            
            # Process frame
            processed_frame, pose_results, hands_results = self.process_frame(frame)
            
            # Update BPM calculation
            current_time = time.time()
            if self.compression_depth > 0.5:  # Detected compression
                if self.last_compression_time > 0:
                    interval = current_time - self.last_compression_time
                    if 0.3 < interval < 1.0:  # Reasonable compression interval
                        self.compression_times.append(current_time)
                        self.compression_count += 1
                        
                        # Keep only recent compression times
                        if len(self.compression_times) > 10:
                            self.compression_times.pop(0)
                        
                        # Calculate BPM
                        self.current_bpm = self.calculate_bpm(self.compression_times)
                
                self.last_compression_time = current_time
            
            # Add overlay
            frame_with_overlay = self.add_overlay_info(processed_frame)
            
            # Provide audio feedback
            if self.current_bpm > 0:
                if self.current_bpm < 100:
                    if not hasattr(self, '_last_slow_warning') or current_time - self._last_slow_warning > 3:
                        self.speak("Go faster")
                        self._last_slow_warning = current_time
                elif self.current_bpm > 120:
                    if not hasattr(self, '_last_fast_warning') or current_time - self._last_fast_warning > 3:
                        self.speak("Go slower")
                        self._last_fast_warning = current_time
                else:
                    if not hasattr(self, '_last_good_pace') or current_time - self._last_good_pace > 5:
                        self.speak("Good pace, keep going!")
                        self._last_good_pace = current_time
            
            cv2.imshow('CPR Assistant - Feedback Mode', frame_with_overlay)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    
    def run(self):
        """Main application loop"""
        try:
            self.initialize_camera()
            self.running = True
            
            # Mode selection
            self.show_mode_selection()
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()
    
    def show_mode_selection(self):
        """Show mode selection window"""
        root = tk.Tk()
        root.title("CPR Assistant - Mode Selection")
        root.geometry("400x300")
        root.configure(bg='#2c3e50')
        
        # Title
        title_label = tk.Label(root, text="CPR Assistant", 
                              font=('Arial', 24, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=20)
        
        # Mode selection buttons
        walkthrough_btn = tk.Button(root, text="Walkthrough Mode\n(Step-by-step guidance)", 
                                  font=('Arial', 14), 
                                  command=lambda: self.start_mode("walkthrough", root),
                                  bg='#3498db', fg='white', 
                                  width=20, height=3)
        walkthrough_btn.pack(pady=10)
        
        feedback_btn = tk.Button(root, text="Feedback Mode\n(For trained responders)", 
                                font=('Arial', 14), 
                                command=lambda: self.start_mode("feedback", root),
                                bg='#e74c3c', fg='white', 
                                width=20, height=3)
        feedback_btn.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(root, 
                               text="Select your mode:\n• Walkthrough: Step-by-step CPR guidance\n• Feedback: Real-time feedback for trained users", 
                               font=('Arial', 10), 
                               fg='white', bg='#2c3e50')
        instructions.pack(pady=20)
        
        root.mainloop()
    
    def start_mode(self, mode, root):
        """Start the selected mode"""
        self.mode = mode
        root.destroy()
        
        if mode == "walkthrough":
            self.run_walkthrough_mode()
        else:
            self.run_feedback_mode()
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
        self.stop_metronome()
        
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = CPRAssistant()
    app.run()

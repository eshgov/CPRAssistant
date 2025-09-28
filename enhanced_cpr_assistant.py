"""
Enhanced CPR Assistant with LLM Integration
Comprehensive CPR guidance with real-time feedback and AI-powered Q&A
"""

import cv2
import mediapipe as mp
import numpy as np
import pygame
import threading
import time
import math
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import speech_recognition as sr
import pyttsx3
from typing import Optional, Tuple, List, Dict
import queue
import json
from llm_cpr_guide import LLMCPRGuide

class EnhancedCPRAssistant:
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
        
        # Initialize LLM guide
        self.llm_guide = LLMCPRGuide()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # CPR tracking variables
        self.compression_count = 0
        self.current_bpm = 0
        self.target_bpm = 110
        self.compression_depth = 0
        self.hand_placement_score = 0
        self.last_compression_time = 0
        self.compression_times = []
        self.metronome_active = False
        self.mode = None
        
        # UI variables
        self.camera = None
        self.running = False
        self.current_step = 0
        self.step_timer = 0
        self.qa_window = None
        
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
        
        # Performance tracking
        self.performance_history = []
        self.session_start_time = time.time()
        
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
        
        intervals = []
        for i in range(1, len(compression_times)):
            interval = compression_times[i] - compression_times[i-1]
            intervals.append(interval)
        
        if not intervals:
            return 0
        
        avg_interval = sum(intervals) / len(intervals)
        bpm = 60 / avg_interval if avg_interval > 0 else 0
        
        return min(max(bpm, 0), 200)
    
    def detect_hand_placement(self, landmarks):
        """Detect if hands are properly placed for CPR"""
        if not landmarks:
            return 0
        
        # Get key points for hand placement
        left_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        left_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        # Calculate chest center
        chest_center_x = (left_shoulder.x + right_shoulder.x) / 2
        chest_center_y = (left_shoulder.y + right_shoulder.y) / 2
        
        # Calculate hand positions relative to chest center
        left_distance = math.sqrt((left_wrist.x - chest_center_x)**2 + (left_wrist.y - chest_center_y)**2)
        right_distance = math.sqrt((right_wrist.x - chest_center_x)**2 + (right_wrist.y - chest_center_y)**2)
        
        avg_distance = (left_distance + right_distance) / 2
        score = max(0, 1 - avg_distance * 10)
        
        return score
    
    def detect_compression_depth(self, landmarks):
        """Detect compression depth based on hand movement"""
        if not landmarks:
            return 0
        
        left_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_WRIST]
        
        hand_y = (left_wrist.y + right_wrist.y) / 2
        depth = 1 - hand_y
        
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
            self._play_metronome_click()
            time.sleep(interval)
    
    def _play_metronome_click(self):
        """Play metronome click sound"""
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
            return (0, 255, 0)  # Green
        elif bpm < 100:
            return (0, 0, 255)  # Red
        else:
            return (0, 165, 255)  # Orange
    
    def process_frame(self, frame):
        """Process a single frame for CPR feedback"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        pose_results = self.pose.process(rgb_frame)
        hands_results = self.hands.process(rgb_frame)
        
        # Draw pose landmarks
        if pose_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
            )
            
            self.hand_placement_score = self.detect_hand_placement(pose_results.pose_landmarks)
            self.compression_depth = self.detect_compression_depth(pose_results.pose_landmarks)
        
        # Draw hand landmarks
        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
        
        return frame, pose_results, hands_results
    
    def add_enhanced_overlay(self, frame):
        """Add enhanced CPR feedback overlay"""
        height, width = frame.shape[:2]
        
        # Background for text areas
        overlay = frame.copy()
        
        # Current BPM with color coding
        bpm_color = self.get_feedback_color(self.current_bpm)
        cv2.rectangle(overlay, (10, 10), (250, 80), (0, 0, 0), -1)
        cv2.putText(frame, f"BPM: {int(self.current_bpm)}", (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, bpm_color, 2)
        
        # Compression count
        cv2.rectangle(overlay, (10, 90), (250, 130), (0, 0, 0), -1)
        cv2.putText(frame, f"Count: {self.compression_count}", (20, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Hand placement score
        placement_color = (0, 255, 0) if self.hand_placement_score > 0.7 else (0, 0, 255)
        cv2.rectangle(overlay, (10, 140), (250, 180), (0, 0, 0), -1)
        cv2.putText(frame, f"Hands: {int(self.hand_placement_score*100)}%", (20, 170), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, placement_color, 2)
        
        # Compression depth
        depth_color = (0, 255, 0) if self.compression_depth > 0.7 else (0, 0, 255)
        cv2.rectangle(overlay, (10, 190), (250, 230), (0, 0, 0), -1)
        cv2.putText(frame, f"Depth: {int(self.compression_depth*100)}%", (20, 220), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, depth_color, 2)
        
        # Emergency info
        cv2.rectangle(overlay, (width-200, 10), (width-10, 50), (0, 0, 255), -1)
        cv2.putText(frame, "CALL 911!", (width-190, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Mode indicator
        mode_text = "Walkthrough" if self.mode == "walkthrough" else "Feedback"
        cv2.rectangle(overlay, (width-200, 60), (width-10, 100), (0, 100, 0), -1)
        cv2.putText(frame, mode_text, (width-190, 85), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Q&A button
        cv2.rectangle(overlay, (width-200, 110), (width-10, 150), (255, 165, 0), -1)
        cv2.putText(frame, "Ask CPR Q&A", (width-190, 135), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return frame
    
    def get_llm_feedback(self):
        """Get LLM-powered feedback on current performance"""
        feedback = self.llm_guide.get_compression_feedback(
            self.current_bpm, 
            self.compression_depth, 
            self.hand_placement_score
        )
        return feedback
    
    def show_qa_window(self):
        """Show Q&A window for CPR questions"""
        if self.qa_window and self.qa_window.winfo_exists():
            self.qa_window.lift()
            return
        
        self.qa_window = tk.Toplevel()
        self.qa_window.title("CPR Q&A Assistant")
        self.qa_window.geometry("600x500")
        self.qa_window.configure(bg='#2c3e50')
        
        # Title
        title_label = tk.Label(self.qa_window, text="CPR Q&A Assistant", 
                              font=('Arial', 18, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=10)
        
        # Question input
        question_frame = tk.Frame(self.qa_window, bg='#2c3e50')
        question_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(question_frame, text="Ask a CPR question:", 
                font=('Arial', 12), fg='white', bg='#2c3e50').pack(anchor='w')
        
        question_entry = tk.Entry(question_frame, font=('Arial', 12), width=50)
        question_entry.pack(pady=5, fill='x')
        
        # Voice input button
        voice_btn = tk.Button(question_frame, text="🎤 Voice Input", 
                            command=lambda: self.voice_input(question_entry),
                            bg='#3498db', fg='white', font=('Arial', 10))
        voice_btn.pack(pady=5)
        
        # Response area
        response_frame = tk.Frame(self.qa_window, bg='#2c3e50')
        response_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        tk.Label(response_frame, text="Response:", 
                font=('Arial', 12), fg='white', bg='#2c3e50').pack(anchor='w')
        
        response_text = scrolledtext.ScrolledText(response_frame, 
                                                font=('Arial', 11), 
                                                height=15, width=60)
        response_text.pack(pady=5, fill='both', expand=True)
        
        # Buttons
        button_frame = tk.Frame(self.qa_window, bg='#2c3e50')
        button_frame.pack(pady=10)
        
        def ask_question():
            question = question_entry.get().strip()
            if question:
                response = self.llm_guide.ask_cpr_question(question)
                response_text.delete(1.0, tk.END)
                response_text.insert(tk.END, response)
                self.speak(response)
        
        ask_btn = tk.Button(button_frame, text="Ask Question", 
                           command=ask_question,
                           bg='#e74c3c', fg='white', font=('Arial', 12))
        ask_btn.pack(side='left', padx=5)
        
        clear_btn = tk.Button(button_frame, text="Clear", 
                             command=lambda: response_text.delete(1.0, tk.END),
                             bg='#95a5a6', fg='white', font=('Arial', 12))
        clear_btn.pack(side='left', padx=5)
        
        # Quick questions
        quick_frame = tk.Frame(self.qa_window, bg='#2c3e50')
        quick_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(quick_frame, text="Quick Questions:", 
                font=('Arial', 10, 'bold'), fg='white', bg='#2c3e50').pack(anchor='w')
        
        quick_questions = [
            "What's the correct compression rate?",
            "How deep should I compress?",
            "Where do I place my hands?",
            "When do I give rescue breaths?",
            "What if I'm alone?"
        ]
        
        for i, q in enumerate(quick_questions):
            btn = tk.Button(quick_frame, text=q, 
                           command=lambda q=q: self.ask_quick_question(q, question_entry, response_text),
                           bg='#34495e', fg='white', font=('Arial', 9),
                           width=30, anchor='w')
            btn.pack(pady=2, fill='x')
        
        # Bind Enter key
        question_entry.bind('<Return>', lambda e: ask_question())
    
    def voice_input(self, entry_widget):
        """Handle voice input for questions"""
        def _voice_input():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio)
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, text)
            except sr.WaitTimeoutError:
                messagebox.showwarning("Timeout", "No speech detected. Please try again.")
            except sr.UnknownValueError:
                messagebox.showwarning("Error", "Could not understand speech. Please try again.")
            except Exception as e:
                messagebox.showerror("Error", f"Voice input error: {e}")
        
        voice_thread = threading.Thread(target=_voice_input)
        voice_thread.daemon = True
        voice_thread.start()
    
    def ask_quick_question(self, question, entry_widget, response_widget):
        """Ask a quick question"""
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, question)
        response = self.llm_guide.ask_cpr_question(question)
        response_widget.delete(1.0, tk.END)
        response_widget.insert(tk.END, response)
        self.speak(response)
    
    def run_walkthrough_mode(self):
        """Run step-by-step CPR walkthrough"""
        self.mode = "walkthrough"
        self.current_step = 0
        
        self.speak(self.walkthrough_steps[self.current_step])
        
        while self.running and self.current_step < len(self.walkthrough_steps):
            ret, frame = self.camera.read()
            if not ret:
                break
            
            processed_frame, pose_results, hands_results = self.process_frame(frame)
            frame_with_overlay = self.add_enhanced_overlay(processed_frame)
            
            # Show current step
            height, width = frame_with_overlay.shape[:2]
            step_text = f"Step {self.current_step + 1}: {self.walkthrough_steps[self.current_step]}"
            cv2.putText(frame_with_overlay, step_text, (10, height-50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show "Skip to Compressions" button
            cv2.rectangle(frame_with_overlay, (width-200, height-80), (width-10, height-20), (0, 255, 0), -1)
            cv2.putText(frame_with_overlay, "Skip to Compressions", (width-190, height-45), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            cv2.imshow('CPR Assistant - Walkthrough Mode', frame_with_overlay)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n'):
                self.current_step += 1
                if self.current_step < len(self.walkthrough_steps):
                    self.speak(self.walkthrough_steps[self.current_step])
            elif key == ord('s'):
                self.run_feedback_mode()
                break
            elif key == ord('a'):  # Ask Q&A
                self.show_qa_window()
    
    def run_feedback_mode(self):
        """Run real-time feedback mode"""
        self.mode = "feedback"
        self.start_metronome()
        
        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                break
            
            processed_frame, pose_results, hands_results = self.process_frame(frame)
            
            # Update BPM calculation
            current_time = time.time()
            if self.compression_depth > 0.5:
                if self.last_compression_time > 0:
                    interval = current_time - self.last_compression_time
                    if 0.3 < interval < 1.0:
                        self.compression_times.append(current_time)
                        self.compression_count += 1
                        
                        if len(self.compression_times) > 10:
                            self.compression_times.pop(0)
                        
                        self.current_bpm = self.calculate_bpm(self.compression_times)
                
                self.last_compression_time = current_time
            
            frame_with_overlay = self.add_enhanced_overlay(processed_frame)
            
            # Provide intelligent feedback
            if self.current_bpm > 0:
                feedback = self.get_llm_feedback()
                
                if self.current_bpm < 100:
                    if not hasattr(self, '_last_slow_warning') or current_time - self._last_slow_warning > 3:
                        self.speak(feedback["bpm_feedback"])
                        self._last_slow_warning = current_time
                elif self.current_bpm > 120:
                    if not hasattr(self, '_last_fast_warning') or current_time - self._last_fast_warning > 3:
                        self.speak(feedback["bpm_feedback"])
                        self._last_fast_warning = current_time
                else:
                    if not hasattr(self, '_last_good_pace') or current_time - self._last_good_pace > 5:
                        self.speak(feedback["overall_feedback"])
                        self._last_good_pace = current_time
            
            cv2.imshow('CPR Assistant - Feedback Mode', frame_with_overlay)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('a'):  # Ask Q&A
                self.show_qa_window()
    
    def show_mode_selection(self):
        """Show enhanced mode selection window"""
        root = tk.Tk()
        root.title("Enhanced CPR Assistant")
        root.geometry("500x400")
        root.configure(bg='#2c3e50')
        
        # Title
        title_label = tk.Label(root, text="Enhanced CPR Assistant", 
                              font=('Arial', 24, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=20)
        
        # Features list
        features_frame = tk.Frame(root, bg='#2c3e50')
        features_frame.pack(pady=10)
        
        features_text = """
        🎯 Real-time pose estimation with MediaPipe
        🤖 AI-powered CPR guidance and Q&A
        🎵 Audio/visual metronome (100-120 BPM)
        📊 Live performance feedback
        🎤 Voice input for questions
        📱 Step-by-step walkthrough mode
        """
        
        features_label = tk.Label(features_frame, text=features_text, 
                                 font=('Arial', 11), fg='white', bg='#2c3e50',
                                 justify='left')
        features_label.pack()
        
        # Mode selection buttons
        walkthrough_btn = tk.Button(root, text="Walkthrough Mode\n(Step-by-step guidance)", 
                                  font=('Arial', 14), 
                                  command=lambda: self.start_mode("walkthrough", root),
                                  bg='#3498db', fg='white', 
                                  width=25, height=3)
        walkthrough_btn.pack(pady=10)
        
        feedback_btn = tk.Button(root, text="Feedback Mode\n(For trained responders)", 
                                font=('Arial', 14), 
                                command=lambda: self.start_mode("feedback", root),
                                bg='#e74c3c', fg='white', 
                                width=25, height=3)
        feedback_btn.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(root, 
                               text="Press 'A' during CPR to ask questions\nPress 'Q' to quit", 
                               font=('Arial', 10), 
                               fg='white', bg='#2c3e50')
        instructions.pack(pady=10)
        
        root.mainloop()
    
    def start_mode(self, mode, root):
        """Start the selected mode"""
        self.mode = mode
        root.destroy()
        
        if mode == "walkthrough":
            self.run_walkthrough_mode()
        else:
            self.run_feedback_mode()
    
    def run(self):
        """Main application loop"""
        try:
            self.initialize_camera()
            self.running = True
            self.show_mode_selection()
            
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"Failed to initialize: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        self.running = False
        self.stop_metronome()
        
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = EnhancedCPRAssistant()
    app.run()

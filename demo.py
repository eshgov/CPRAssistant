#!/usr/bin/env python3
"""
CPR Assistant Demo
Simple demo to test basic functionality without camera
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading

class CPRDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CPR Assistant Demo")
        self.root.geometry("600x500")
        self.root.configure(bg='#2c3e50')
        
        # Demo variables
        self.bpm = 0
        self.compression_count = 0
        self.hand_placement = 0
        self.depth = 0
        self.running = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the demo UI"""
        # Title
        title_label = tk.Label(self.root, text="CPR Assistant Demo", 
                              font=('Arial', 24, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=20)
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#2c3e50')
        status_frame.pack(pady=20)
        
        # BPM display
        self.bpm_label = tk.Label(status_frame, text="BPM: 0", 
                                 font=('Arial', 18, 'bold'), 
                                 fg='white', bg='#2c3e50')
        self.bpm_label.pack(pady=5)
        
        # Compression count
        self.count_label = tk.Label(status_frame, text="Compressions: 0", 
                                   font=('Arial', 16), 
                                   fg='white', bg='#2c3e50')
        self.count_label.pack(pady=5)
        
        # Hand placement
        self.hand_label = tk.Label(status_frame, text="Hand Placement: 0%", 
                                  font=('Arial', 16), 
                                  fg='white', bg='#2c3e50')
        self.hand_label.pack(pady=5)
        
        # Depth
        self.depth_label = tk.Label(status_frame, text="Depth: 0%", 
                                   font=('Arial', 16), 
                                   fg='white', bg='#2c3e50')
        self.depth_label.pack(pady=5)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(pady=20)
        
        self.start_btn = tk.Button(button_frame, text="Start Demo", 
                                  command=self.start_demo,
                                  bg='#27ae60', fg='white', 
                                  font=('Arial', 14), width=15)
        self.start_btn.pack(side='left', padx=10)
        
        self.stop_btn = tk.Button(button_frame, text="Stop Demo", 
                                 command=self.stop_demo,
                                 bg='#e74c3c', fg='white', 
                                 font=('Arial', 14), width=15)
        self.stop_btn.pack(side='left', padx=10)
        
        # Simulate button
        self.simulate_btn = tk.Button(button_frame, text="Simulate CPR", 
                                     command=self.simulate_cpr,
                                     bg='#3498db', fg='white', 
                                     font=('Arial', 14), width=15)
        self.simulate_btn.pack(side='left', padx=10)
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="This is a demo of the CPR Assistant.\n" +
                                    "Click 'Start Demo' to begin simulation.\n" +
                                    "Click 'Simulate CPR' to simulate compressions.\n" +
                                    "The app will show real-time feedback.",
                               font=('Arial', 12), 
                               fg='white', bg='#2c3e50',
                               justify='center')
        instructions.pack(pady=20)
        
        # Feedback area
        self.feedback_text = tk.Text(self.root, height=8, width=60, 
                                    font=('Arial', 10), bg='#34495e', fg='white')
        self.feedback_text.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Add initial feedback
        self.feedback_text.insert(tk.END, "CPR Assistant Demo Ready\n")
        self.feedback_text.insert(tk.END, "Click 'Start Demo' to begin\n")
        self.feedback_text.insert(tk.END, "Click 'Simulate CPR' to simulate compressions\n")
    
    def start_demo(self):
        """Start the demo simulation"""
        self.running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.feedback_text.insert(tk.END, "Demo started! Simulating CPR environment...\n")
        self.feedback_text.see(tk.END)
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self.simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
    
    def stop_demo(self):
        """Stop the demo simulation"""
        self.running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        self.feedback_text.insert(tk.END, "Demo stopped.\n")
        self.feedback_text.see(tk.END)
    
    def simulate_cpr(self):
        """Simulate CPR compressions"""
        if not self.running:
            self.feedback_text.insert(tk.END, "Please start the demo first!\n")
            self.feedback_text.see(tk.END)
            return
        
        # Simulate compression
        self.compression_count += 1
        self.bpm = 110  # Simulate good BPM
        self.hand_placement = 0.85  # Simulate good hand placement
        self.depth = 0.75  # Simulate good depth
        
        # Update displays
        self.update_displays()
        
        # Add feedback
        self.feedback_text.insert(tk.END, f"Compression #{self.compression_count} - Good technique!\n")
        self.feedback_text.see(tk.END)
        
        # Provide feedback based on performance
        if self.bpm >= 100 and self.bpm <= 120:
            self.feedback_text.insert(tk.END, "Excellent rhythm! Keep going.\n")
        elif self.bpm < 100:
            self.feedback_text.insert(tk.END, "Too slow! Speed up to 100-120 BPM.\n")
        else:
            self.feedback_text.insert(tk.END, "Too fast! Slow down to 100-120 BPM.\n")
        
        if self.hand_placement > 0.8:
            self.feedback_text.insert(tk.END, "Perfect hand placement!\n")
        else:
            self.feedback_text.insert(tk.END, "Move hands to center of chest.\n")
        
        if self.depth > 0.7:
            self.feedback_text.insert(tk.END, "Good compression depth!\n")
        else:
            self.feedback_text.insert(tk.END, "Push harder! Compress at least 2 inches.\n")
        
        self.feedback_text.see(tk.END)
    
    def simulation_loop(self):
        """Main simulation loop"""
        while self.running:
            # Simulate some variation in the demo
            if self.compression_count > 0:
                # Gradually decrease BPM to simulate fatigue
                self.bpm = max(100, self.bpm - 0.5)
                
                # Simulate hand placement variation
                self.hand_placement = max(0.6, self.hand_placement - 0.01)
                
                # Simulate depth variation
                self.depth = max(0.5, self.depth - 0.01)
                
                self.update_displays()
            
            time.sleep(0.1)
    
    def update_displays(self):
        """Update the display labels"""
        # Update BPM with color coding
        if 100 <= self.bpm <= 120:
            bpm_color = 'green'
        elif self.bpm < 100:
            bpm_color = 'red'
        else:
            bpm_color = 'orange'
        
        self.bpm_label.config(text=f"BPM: {int(self.bpm)}", fg=bpm_color)
        self.count_label.config(text=f"Compressions: {self.compression_count}")
        self.hand_label.config(text=f"Hand Placement: {int(self.hand_placement*100)}%")
        self.depth_label.config(text=f"Depth: {int(self.depth*100)}%")
    
    def run(self):
        """Run the demo"""
        self.root.mainloop()

if __name__ == "__main__":
    demo = CPRDemo()
    demo.run()

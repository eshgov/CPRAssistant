"""
LLM-Powered CPR Guidance System
Integrates with OpenAI API for intelligent CPR Q&A
"""

import openai
import json
import os
from typing import Dict, List, Optional

class LLMCPRGuide:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM CPR Guide with OpenAI API"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        
        # CPR-specific system prompt
        self.system_prompt = """
        You are a certified CPR instructor and emergency medical expert. 
        Provide accurate, concise, and actionable CPR guidance based on current AHA guidelines.
        
        Key guidelines:
        - Adult CPR: 30 compressions to 2 breaths, 100-120 BPM
        - Hand placement: Center of chest, between nipples
        - Compression depth: At least 2 inches (5 cm)
        - Allow full chest recoil between compressions
        - Call 911 immediately before starting CPR
        
        Always prioritize safety and current medical standards.
        Keep responses concise and actionable for emergency situations.
        """
        
        # CPR knowledge base
        self.cpr_knowledge = {
            "compression_rate": "100-120 compressions per minute",
            "compression_depth": "At least 2 inches (5 cm) for adults",
            "hand_placement": "Center of chest, between nipples",
            "rescue_breaths": "2 breaths after every 30 compressions",
            "emergency_number": "Call 911 immediately",
            "recovery_position": "Place victim on firm, flat surface",
            "aed_usage": "Use AED if available, follow voice prompts"
        }
    
    def ask_cpr_question(self, question: str) -> str:
        """Ask a CPR-related question to the LLM"""
        if not self.api_key:
            return self._fallback_response(question)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"LLM API error: {e}")
            return self._fallback_response(question)
    
    def _fallback_response(self, question: str) -> str:
        """Fallback responses when LLM is not available"""
        question_lower = question.lower()
        
        if "rate" in question_lower or "speed" in question_lower or "bpm" in question_lower:
            return "Compress at 100-120 beats per minute. Use a metronome or count 'one-and-two-and-three' to maintain proper rhythm."
        
        elif "depth" in question_lower or "how deep" in question_lower:
            return "Compress at least 2 inches (5 cm) deep. Push hard and fast, allowing full chest recoil between compressions."
        
        elif "hands" in question_lower or "placement" in question_lower:
            return "Place the heel of one hand in the center of the chest, between the nipples. Place your other hand on top and interlock fingers."
        
        elif "breath" in question_lower or "rescue" in question_lower:
            return "After 30 compressions, give 2 rescue breaths. Tilt head back, pinch nose, and give 1-second breaths until chest rises."
        
        elif "emergency" in question_lower or "911" in question_lower:
            return "Call 911 immediately before starting CPR. If alone, call 911 first, then start CPR."
        
        elif "aed" in question_lower:
            return "Use an AED if available. Turn it on and follow the voice prompts. Continue CPR between shocks."
        
        else:
            return "For CPR: 30 compressions at 100-120 BPM, then 2 rescue breaths. Call 911 immediately. Continue until help arrives or victim recovers."
    
    def get_compression_feedback(self, bpm: float, depth: float, hand_placement: float) -> Dict[str, str]:
        """Get specific feedback based on CPR performance"""
        feedback = {
            "bpm_feedback": "",
            "depth_feedback": "",
            "placement_feedback": "",
            "overall_feedback": ""
        }
        
        # BPM feedback
        if 100 <= bpm <= 120:
            feedback["bpm_feedback"] = "Excellent rhythm! Keep going at this pace."
        elif bpm < 100:
            feedback["bpm_feedback"] = f"Too slow at {bpm:.0f} BPM. Speed up to 100-120 BPM."
        else:
            feedback["bpm_feedback"] = f"Too fast at {bpm:.0f} BPM. Slow down to 100-120 BPM."
        
        # Depth feedback
        if depth >= 0.7:  # Assuming normalized depth
            feedback["depth_feedback"] = "Good compression depth!"
        else:
            feedback["depth_feedback"] = "Push harder! Compress at least 2 inches deep."
        
        # Hand placement feedback
        if hand_placement >= 0.8:
            feedback["placement_feedback"] = "Perfect hand placement!"
        elif hand_placement >= 0.6:
            feedback["placement_feedback"] = "Good placement, try to center hands more."
        else:
            feedback["placement_feedback"] = "Move hands to center of chest, between nipples."
        
        # Overall feedback
        if bpm >= 100 and bpm <= 120 and depth >= 0.7 and hand_placement >= 0.8:
            feedback["overall_feedback"] = "Excellent CPR technique! Keep it up!"
        elif bpm < 100 or depth < 0.7 or hand_placement < 0.6:
            feedback["overall_feedback"] = "Focus on: proper hand placement, adequate depth, and correct rhythm."
        else:
            feedback["overall_feedback"] = "Good effort! Continue with minor adjustments."
        
        return feedback
    
    def get_step_guidance(self, step: int) -> str:
        """Get guidance for specific CPR steps"""
        step_guidance = {
            0: "Check responsiveness: Tap shoulders and shout 'Are you okay?' If no response, call 911 immediately.",
            1: "Position victim: Place on firm, flat surface. Remove clothing from chest area.",
            2: "Hand placement: Place heel of one hand in center of chest, between nipples. Place other hand on top.",
            3: "Begin compressions: Push hard and fast, at least 2 inches deep, 100-120 BPM.",
            4: "Continue compressions: Count out loud, maintain rhythm. Don't stop unless victim recovers.",
            5: "Rescue breaths: After 30 compressions, give 2 rescue breaths. Tilt head, pinch nose, 1-second breaths.",
            6: "Resume compressions: Continue 30 compressions to 2 breaths cycle until help arrives."
        }
        
        return step_guidance.get(step, "Continue with current CPR technique.")
    
    def get_emergency_guidance(self) -> List[str]:
        """Get emergency response guidance"""
        return [
            "1. Check scene safety - ensure it's safe to approach",
            "2. Check responsiveness - tap shoulders, shout",
            "3. Call 911 immediately - provide location and situation",
            "4. Check breathing - look, listen, feel for 10 seconds",
            "5. Begin CPR if no breathing or only gasping",
            "6. Use AED if available - follow voice prompts",
            "7. Continue until help arrives or victim recovers"
        ]

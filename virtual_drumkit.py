import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import pygame
import os
from dataclasses import dataclass
from typing import Dict, Tuple, List
import time
from enum import Enum

pygame.mixer.init(44100, -16, 2, 64)
pygame.mixer.set_num_channels(16)


class Mode(Enum):
    TRAINING = "Training"
    PRACTICE = "Practice"
    PERFORMANCE = "Performance"
    EXPERT = "Expert"
    CUSTOM = "Custom"


@dataclass
class FingerSound:
    name: str
    sound_file: str
    sound: pygame.mixer.Sound = None
    last_trigger_time: float = 0.0
    cooldown: float = 0.15
    last_positions: List[float] = None
    is_moving_down: bool = False
    volume: float = 0.7
    is_active: bool = True
    skill_level: int = 1

    def __post_init__(self):
        self.last_positions = []


class VirtualDrumkit:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.current_mode = Mode.TRAINING
        self.skill_level = 1
        self.last_hand_trigger_time = {"LEFT": 0.0, "RIGHT": 0.0}
        self.hand_cooldown = 0.1

        self.finger_sounds = {
            "RIGHT_INDEX": FingerSound(
                "Snare", "TR-808 Kit/Snare Mid.wav", skill_level=1
            ),
            "RIGHT_MIDDLE": FingerSound(
                "Hi-Hat", "TR-808 Kit/Hihat.wav", skill_level=1
            ),
            "RIGHT_THUMB": FingerSound(
                "Kick", "TR-808 Kit/Kick Basic.wav", skill_level=1
            ),
            "RIGHT_RING": FingerSound("Clap", "TR-808 Kit/Clap.wav", skill_level=2),
            "RIGHT_PINKY": FingerSound(
                "Cymbal", "TR-808 Kit/Cymbal.wav", skill_level=2
            ),
            "LEFT_INDEX": FingerSound(
                "Tom Mid", "TR-808 Kit/Tom Mid.wav", skill_level=2
            ),
            "LEFT_THUMB": FingerSound(
                "Tom Low", "TR-808 Kit/Tom Low.wav", skill_level=3
            ),
            "LEFT_MIDDLE": FingerSound(
                "Tom High", "TR-808 Kit/Tom High.wav", skill_level=3
            ),
            "LEFT_RING": FingerSound(
                "Cowbell", "TR-808 Kit/Cowbell.wav", skill_level=3
            ),
            "LEFT_PINKY": FingerSound(
                "Rimshot", "TR-808 Kit/Rimshot.wav", skill_level=3
            ),
        }

        self.history_size = 4
        self.mode_parameters = {
            Mode.TRAINING: {
                "down_threshold": 0.002,
                "up_threshold": 0.001,
                "hand_cooldown": 0.2,
            },
            Mode.PRACTICE: {
                "down_threshold": 0.0015,
                "up_threshold": 0.001,
                "hand_cooldown": 0.15,
            },
            Mode.PERFORMANCE: {
                "down_threshold": 0.001,
                "up_threshold": 0.0008,
                "hand_cooldown": 0.1,
            },
            Mode.EXPERT: {
                "down_threshold": 0.0008,
                "up_threshold": 0.0005,
                "hand_cooldown": 0.05,
            },
        }

        self.update_mode_parameters()

        for sound in self.finger_sounds.values():
            if os.path.exists(sound.sound_file):
                sound.sound = pygame.mixer.Sound(sound.sound_file)
                if "Kick" in sound.name:
                    sound.volume = 0.8
                elif "Cymbal" in sound.name:
                    sound.volume = 0.6
                sound.sound.set_volume(sound.volume)
            else:
                print(f"Warning: Sound file not found: {sound.sound_file}")

        self.finger_indices = {
            "THUMB": 4,
            "INDEX": 8,
            "MIDDLE": 12,
            "RING": 16,
            "PINKY": 20,
        }

        self.pattern_history = []
        self.pattern_window = 2.0

    def update_mode_parameters(self):
        if self.current_mode in self.mode_parameters:
            params = self.mode_parameters[self.current_mode]
            self.down_threshold = params["down_threshold"]
            self.up_threshold = params["up_threshold"]
            self.hand_cooldown = params["hand_cooldown"]

    def detect_downward_motion(self, positions: List[float]) -> bool:
        if len(positions) < 2:
            return False
        motions = [positions[i] - positions[i - 1] for i in range(1, len(positions))]
        avg_motion = sum(motions) / len(motions)
        return avg_motion > self.down_threshold

    def detect_upward_motion(self, positions: List[float]) -> bool:
        if len(positions) < 2:
            return False
        motions = [positions[i] - positions[i - 1] for i in range(1, len(positions))]
        avg_motion = sum(motions) / len(motions)
        return avg_motion < -self.up_threshold

    def can_trigger_sound(
        self, hand_side: str, sound: FingerSound, current_time: float
    ) -> bool:
        if sound.skill_level > self.skill_level:
            return False

        if current_time - sound.last_trigger_time < sound.cooldown:
            return False

        return True

    def process_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)

        h, w, _ = frame.shape
        current_time = time.time()

        cv2.putText(
            frame,
            f"Mode: {self.current_mode.value}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"Level: {self.skill_level}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        legend_y = 90
        for hand_side in ["RIGHT", "LEFT"]:
            cv2.putText(
                frame,
                f"{hand_side} Hand:",
                (10, legend_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            legend_y += 20

            for finger in ["THUMB", "INDEX", "MIDDLE", "RING", "PINKY"]:
                finger_key = f"{hand_side}_{finger}"
                if finger_key in self.finger_sounds:
                    sound = self.finger_sounds[finger_key]
                    if sound.skill_level <= self.skill_level:
                        color = (255, 255, 255) if sound.is_active else (128, 128, 128)
                        cv2.putText(
                            frame,
                            f"{finger}: {sound.name}",
                            (20, legend_y),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            color,
                            1,
                        )
                        legend_y += 15

        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                hand_side = "LEFT" if hand_idx == 0 else "RIGHT"
                wrist_y = hand_landmarks.landmark[0].y

                for finger_name, tip_idx in self.finger_indices.items():
                    finger_key = f"{hand_side}_{finger_name}"
                    if finger_key in self.finger_sounds:
                        sound = self.finger_sounds[finger_key]

                        if sound.skill_level > self.skill_level:
                            continue

                        tip = hand_landmarks.landmark[tip_idx]
                        relative_y = tip.y - wrist_y
                        tip_pos = (int(tip.x * w), int(tip.y * h))

                        sound.last_positions.append(relative_y)
                        if len(sound.last_positions) > self.history_size:
                            sound.last_positions.pop(0)

                        is_moving_down = self.detect_downward_motion(
                            sound.last_positions
                        )
                        is_moving_up = self.detect_upward_motion(sound.last_positions)

                        if is_moving_down and not sound.is_moving_down:
                            if self.can_trigger_sound(hand_side, sound, current_time):
                                if sound.sound and sound.is_active:
                                    sound.sound.play()
                                    sound.last_trigger_time = current_time
                                    print(f"Triggered {sound.name}")
                            sound.is_moving_down = True
                        elif is_moving_up:
                            sound.is_moving_down = False

                        if sound.skill_level <= self.skill_level:
                            base_color = (
                                (0, 255, 0) if sound.is_moving_down else (0, 255, 255)
                            )
                            color = base_color if sound.is_active else (128, 128, 128)
                            cv2.circle(frame, tip_pos, 8, color, -1)
                            cv2.putText(
                                frame,
                                sound.name,
                                (tip_pos[0] + 10, tip_pos[1]),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.4,
                                color,
                                1,
                            )

        return frame


def main():
    st.title("TR-808 Finger Drummer")

    drumkit = VirtualDrumkit()

    with st.sidebar:
        st.header("Controls")

        mode = st.selectbox("Mode", [mode.value for mode in Mode])
        drumkit.current_mode = Mode(mode)
        drumkit.update_mode_parameters()

        skill_level = st.slider("Skill Level", 1, 3, drumkit.skill_level)
        if skill_level != drumkit.skill_level:
            drumkit.skill_level = skill_level

        st.header("Volume Controls")
        for key, sound in drumkit.finger_sounds.items():
            if sound.skill_level <= drumkit.skill_level:
                volume = st.slider(f"{sound.name} Volume", 0.0, 1.0, sound.volume)
                if volume != sound.volume:
                    sound.volume = volume
                    if sound.sound:
                        sound.sound.set_volume(volume)

        st.header("Enable/Disable Sounds")
        for key, sound in drumkit.finger_sounds.items():
            if sound.skill_level <= drumkit.skill_level:
                sound.is_active = st.checkbox(f"Enable {sound.name}", sound.is_active)

    st.write(f"Current Mode: {drumkit.current_mode.value}")
    st.write(f"Skill Level: {drumkit.skill_level}")
    st.write("Move your fingers down to play sounds!")

    cap = cv2.VideoCapture(0)

    frame_placeholder = st.empty()

    stop_button = st.button("Stop")

    while cap.isOpened() and not stop_button:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to read from webcam")
            break

        frame = cv2.flip(frame, 1)
        processed_frame = drumkit.process_frame(frame)
        rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(rgb_frame, channels="RGB")

    cap.release()


if __name__ == "__main__":
    main()

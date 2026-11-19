"""Small synthesised sound effects, so the game needs no audio files."""

import math
import random
from array import array

import pygame


def _tone(rate, start_freq, end_freq, duration, volume=0.5, noise=0.0):
    """Return 16-bit mono samples for a falling tone mixed with noise."""
    count = int(rate * duration)
    samples = []
    phase = 0.0
    for i in range(count):
        progress = i / count
        freq = start_freq + (end_freq - start_freq) * progress
        phase += 2 * math.pi * freq / rate
        envelope = (1 - progress) ** 2
        value = math.sin(phase) * (1 - noise) + random.uniform(-1, 1) * noise
        samples.append(int(value * envelope * volume * 32767))
    return samples


class SoundBank:
    """Builds the slice, bomb and game-over effects.

    If no audio device is available the game keeps running silently.
    """

    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            rate, _size, channels = pygame.mixer.get_init()
            build = lambda samples: self._make_sound(samples, channels)
            self.sounds = {
                "slice": build(_tone(rate, 900, 300, 0.12, 0.4, noise=0.35)),
                "bomb": build(_tone(rate, 120, 40, 0.6, 0.7, noise=0.8)),
                "game_over": build(
                    _tone(rate, 440, 330, 0.25, 0.4)
                    + _tone(rate, 330, 220, 0.45, 0.4)
                ),
            }
            self.enabled = True
        except (pygame.error, TypeError):
            self.enabled = False

    @staticmethod
    def _make_sound(samples, channels):
        # Duplicate each mono sample across however many channels the
        # mixer was opened with (usually 2 for stereo).
        interleaved = array("h")
        for sample in samples:
            interleaved.extend([sample] * channels)
        return pygame.mixer.Sound(buffer=interleaved.tobytes())

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

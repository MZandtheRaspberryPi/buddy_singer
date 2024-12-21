import math
import os
import time
from typing import List
import struct

import mido
import serial

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
songs = os.listdir(DATA_DIR)
songs.sort()
SONGS_PATHS = [os.path.join(DATA_DIR, song) for song in songs if song.endswith(".mid")]

class SongStep:
    def __init__(self, freq: int, delta_t: int, endiannes: str = "big"):
        self.freq = freq
        self.delta_t = delta_t
        self.endiannes = endiannes
        self.endiannes_char = ">" if endiannes == "big" else "<"

    def to_bytes(self):

        freq_bytes = struct.pack(self.endiannes_char + "I", self.freq)
        delta_t_bytes = struct.pack(self.endiannes_char + "I", self.delta_t)
        return freq_bytes + delta_t_bytes

    def __str__(self):
        return f"freq: {self.freq}, delta_t: {self.delta_t}"


class ParsedSong:

    def __init__(self, frequencies: List[int], delta_times: List[int], endiannes: str = "big"):
        if len(frequencies) != len(delta_times):
            raise ValueError
        for i in range(len(frequencies)):
            if not isinstance(frequencies[i], int):
                raise ValueError
            if not isinstance(delta_times[i], int):
                raise ValueError
        
        self.endiannes = endiannes
        
        self.steps = []
        for i in range(len(frequencies)):
            step = SongStep(frequencies[i], delta_times[i], endiannes=endiannes)
            self.steps.append(step)

        self.num_steps = len(frequencies)
    
    def get_num_steps(self):
        return self.num_steps
    
    def get_step(self, step_num: int):

        if step_num >= self.num_steps or step_num < 0:
            raise ValueError
        return self.steps[step_num]

def midi_note_number_to_freq(note_num: int):
    if note_num < 0 or note_num > 157 or not isinstance(note_num, int):
        raise ValueError
    # https://www.music.mcgill.ca/~gary/307/week1/node28.html
    return 440 * 2**((note_num - 69)/12)

def parse_midi_file(file_path_name: str, target_track: str, target_type: str):
    # Open a MIDI file
    mid = mido.MidiFile(file_path_name)

    print(file_path_name)
    print(f"length: {mid.length}")

    frequencies = []
    delta_ts = []

    notated_32nd_notes_per_beat = None
    # time signature numerator
    numerator = None
    # time signature denominator
    denominator = None
    # clock pulses per quarter note
    clocks_per_click = None
    # microseconds per quarter note
    tempo = None

    # Iterate over tracks
    for i, track in enumerate(mid.tracks):
        print(f'Track {i}: {track.name}')
        for msg in track:
            print(msg)
            if msg.type == "set_tempo":
                tempo = msg.tempo
            elif msg.type == "time_signature":
                numerator = msg.numerator
                denominator = msg.denominator
                clocks_per_click = msg.clocks_per_click
                notated_32nd_notes_per_beat = msg.notated_32nd_notes_per_beat

    print(tempo, numerator, denominator, clocks_per_click, notated_32nd_notes_per_beat)

    # 8 for beat length means each beat has a length of an eighth note
    clocks_per_quarter_note_scaler = 4 / denominator

    milliseconds_per_tick = clocks_per_click * clocks_per_quarter_note_scaler * (tempo / 1000)

    # Iterate over tracks
    for i, track in enumerate(mid.tracks):
        if track.name != target_track:
            continue

        # Iterate over messages in the track
        for msg in track:
            if msg.type != target_type:
                continue
            # time is delta timea
            # velocity is how fast note is struck
            # note is note number, maps to some notes
            if msg.time != 0:
                frequencies.append(int(midi_note_number_to_freq(msg.note)))
                delta_ts.append(msg.time * milliseconds_per_tick)
    
    print(f"parsed song duration seconds: {sum(delta_ts)/1000}")
    parsed_song = ParsedSong(frequencies=frequencies, delta_times=delta_ts)

    return parsed_song


def play_song(serial_port: str, baudrate: int, song: ParsedSong):
    ser = serial.Serial(
        port=serial_port,
        baudrate=baudrate,
        timeout=1
    )
    time.sleep(5)

    while not ser.isOpen():
        time.sleep(0.1)

    num_steps = song.get_num_steps()

    for i in range(num_steps):
        step = song.get_step(i)
        step_bytes = step.to_bytes()
        print(step.freq)
        print(step.delta_t)
        # print(step_bytes)

        ser.write(step_bytes)

        # for byte in step_bytes:
        #     # print(byte)
        #     # print(type(byte))
        #     ser.write(byte.to_bytes(1, "big"))
        
        # freq_bytes = ser.read(4)
        # delta_t_bytes = ser.read(4)

        # # print(freq_bytes)
        # # print(delta_t_bytes)
        # freq = int.from_bytes(freq_bytes, byteorder='big')
        # delta_t = int.from_bytes(delta_t_bytes, byteorder='big')
        # print(freq)
        # print(delta_t)

        time.sleep(step.delta_t/1000)

    ser.close()



if __name__ == "__main__":
    song = parse_midi_file(SONGS_PATHS[0], "Treble", "note_on")

    step = song.get_step(0)
    print(step)
    print(step.to_bytes())

    play_song("COM12", 9600, song)
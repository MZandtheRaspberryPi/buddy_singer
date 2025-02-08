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

def parse_midi_file(file_path_name: str, target_track: int):
    # Open a MIDI file
    mid = mido.MidiFile(file_path_name)

    ticks_per_beat = mid.ticks_per_beat

    print(file_path_name)
    print(f"length: {mid.length}")
    print(f"ticks per beat {ticks_per_beat}")

    frequencies = []
    delta_ts = []

    # if 8, then 8 32nd notes per beat, ie, one quarter note per beat
    # if this with 24 clocks per click, then 24 clocks per quarter note
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

    #  1 / (microseconds/quarter note) * 1 second / 1,000,000 microseconds * 1 minute / 60 seconds = quarter note / minute
    bpm = 60 / (tempo / (1000 * 1000))
    bps = bpm / 60

    print(f"bpm: {bpm}")

    mido_bpm = mido.tempo2bpm(tempo, time_signature=(numerator, denominator))
    print(f"mido bpm: {mido_bpm}")

    mido_ticks_to_second = mido.tick2second(1, ticks_per_beat=ticks_per_beat, tempo=tempo)
    mido_ticks_to_millisecond = mido_ticks_to_second * 1000

    # beats / second  * ticks / beat = ticks / second
    # ticks / second * 1 second / 1000 milliseconds = ticks / millisecond

    milliseconds_per_tick = 1 / (bps * ticks_per_beat / 1000)
    print(f"milliseconds per tick {milliseconds_per_tick}")
    print(f"mido: milliseconds per tick {mido_ticks_to_millisecond}")

    min_note = 255
    max_note = -1

    for i, track in enumerate(mid.tracks):
        if i != target_track:
            continue

        # Iterate over messages in the track
        on_off_msgs = []
        for j in range(len(track)):
            msg = track[j]
            if msg.type not in ["note_on", "note_off"]:
                continue
            # if msg.time == 0:
            #     continue
            on_off_msgs.append(msg)
        for j in range(len(on_off_msgs)):
            msg = on_off_msgs[j]
            freq = None
            if msg.type == "note_on":
                note_num = msg.note
                if note_num < min_note:
                    min_note = note_num
                if note_num > max_note:
                    max_note = note_num
                freq = int(midi_note_number_to_freq(note_num))
            else:
                freq = 0
            ticks = None
            ticks = msg.time
            delta_t = int(ticks * milliseconds_per_tick)
            delta_ts.append(delta_t)
            frequencies.append(freq)
    
    print(f"parsed song duration seconds: {sum(delta_ts)/1000}")
    print(f"min note num: {min_note}, max note num: {max_note}")
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
        time.sleep(step.delta_t/1000)
        print(f"freq: {step.freq}, delta_t: {step.delta_t}")
        ser.write(step_bytes)

        if ser.in_waiting > 0:
            line = ser.readline()
            print(f"robo_msg: {line.decode()}")



    ser.close()



if __name__ == "__main__":
    song = parse_midi_file(SONGS_PATHS[0], 1)
    play_song("COM12", 9600, song)
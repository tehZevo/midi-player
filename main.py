#TODO: transpose
#TODO: bpm override/scale

import glob
import random
import mido
from mido import Message
import yaml
import time

try:
    with open("config.yml") as f:
        config = yaml.safe_load(f)
except:
    config = {}

OUTPUT_DEVICE = config.get("output_device", "loopMIDI Port")
LISTEN_DEVICE = config.get("listen_device", None)
SLEEP_TIME = config.get("sleep_time", 10)
MIDI_DIR = config.get("midi_dir", "songs")

sleep_remaining = 0

def find_device(devices, device):
    device = device.lower()
    for d in devices:
        if device in d.lower():
            return d
    return None

def list_devices():
    print("Input devices:")
    if len(mido.get_input_names()) == 0:
        print("<none>")
    for device in mido.get_input_names():
        print("-", device)

    print("Output devices:")
    if len(mido.get_output_names()) == 0:
        print("<none>")
    for device in mido.get_output_names():
        print("-", device)

def handle_listen_message(message):
    global sleep_remaining
    
    if message.type == "note_on" and message.velocity > 0:
        print("Pausing for", SLEEP_TIME, "seconds...")
        sleep_remaining = SLEEP_TIME

def shhh():
    #sus
    out_port.send(Message("control_change", control=64, value=0, channel=0))
    for n in range(128):
        out_port.send(Message("note_off", note=n))

def play():
    global sleep_remaining
    
    songs = glob.glob(f"{MIDI_DIR}/*.mid")
    song = random.choice(songs)
    print("Playing", song, "...")
    mid = mido.MidiFile(song)
    for msg in mid.play():
        out_port.send(msg)
        if sleep_remaining > 0:
            shhh()
            while sleep_remaining > 0:
                time.sleep(1)
                sleep_remaining -= 1
            print("Resuming...")

def main():
    global out_port

    print("Availalable midi devices:")
    list_devices()

    print(f"Opening output device ({OUTPUT_DEVICE})...")
    out_port = mido.open_output(find_device(mido.get_output_names(), OUTPUT_DEVICE))
    print(out_port)
    
    listen_port = None
    if LISTEN_DEVICE is not None:
        print(f"Opening listen device ({LISTEN_DEVICE})...")
        listen_port = mido.open_input(find_device(mido.get_input_names(), LISTEN_DEVICE), callback=lambda message: handle_listen_message(message))
        print(listen_port)
    
    print("Ready!")
    
    while True:
        #reset sustain
        out_port.send(Message("control_change", control=64, value=0, channel=0))
        play()

if __name__ == "__main__":
    main()

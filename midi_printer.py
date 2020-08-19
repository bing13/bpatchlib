from mido import MidiFile, Message, MidiTrack
import mido
import sys

inf = sys.argv[1]

print ('argv=',inf)

mid=MidiFile(inf)

for i, track in enumerate(mid.tracks):
    print('Track {}: {}'.format(i, track.name))
    for msg in track:
        print(msg)



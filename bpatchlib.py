###https://pysimplegui.readthedocs.io/
import PySimpleGUI as sg
import csv
from mido import MidiFile, Message, MidiTrack
import mido
import sys, pause, threading


AUD_FILES_DIR = '/home/bernard/Documents/python/PySimpleGUI/bpatchlib/Sound_Files/'
AUDITION_FILES = ['bass_cool.mid','lead-spain.mid','Waltz_vamp.mid']
PATCHDIR = '/home/bernard/Documents/python/PySimpleGUI/bpatchlib/Patch_Files/'
def read_audition_files():
    auds = {'simple':''}
    for a in AUDITION_FILES:
        auds[a] =  MidiFile(AUD_FILES_DIR+a) 
    return auds

def read_patch_file(inf):
    voice = {}
    pnames = []
    with open(PATCHDIR+inf, 'r') as INF:
        ireader = csv.reader(INF, delimiter='\t')
        #(num, section, cat, name, msb, lsb, patch)
        for row  in ireader:
            if row[0] != 'num':
                # let's keep an list of patch names in the order they were read in
                #print(row[0],row[3])
                pnames.append(row[3].strip())
                
                if inf == 'RD-800_Final_Sound_List.csv':
                    row[6] = int(row[6]) -1
                else:
                    row[6] = row[6].strip()
                voice[row[3].strip()]={ 'name':row[3], 'num':row[0], 'section':row[1], \
                                        'category':row[2],'msb':row[4],'lsb':row[5],'patch':row[6] }
    return voice,pnames



def build_patch_message(channelx, dv):
    # Bank Select selects the desired Bank for the specified Channel.
    # The first byte listed is the MSB, transmitted on cc#0.
    # The second byte listed is the LSB, transmitted on cc#32.
    out_mess = []
    if dv['msb'] and dv['lsb'] != '':
        # send msb
        out_mess.append(Message('control_change', control =  0, value = int(dv['msb']), channel = channelx))
        # send lsb
        out_mess.append(Message('control_change', control = 32, value = int(dv['lsb']), channel = channelx))
    # send patch
    out_mess.append(Message('program_change', program = int(dv['patch']),             channel = channelx))
    return out_mess


#voice['patchname']['num', 'section', 'category', 'msb', 'lsb', 'patch']
def mido_stuff():
    ## inf = '/home/bernard/Bitwig Studio/Projects/00 coversion experiments/Texas Ideal v2 2019-12.mid'
    ## inf = 'media/bernard/Extreme SSD/20_MIDI_clips/MIDI Library/Groove Monkee/Country/065 Ballad Ride F3 P.mid'
    ports = mido.get_input_names()
    #NOTE: THE PORT NUMBERS ARE DYNAMIC. But the order should be reliable (I hope)
    # ['EDIROL UM-550:EDIROL UM-550 MIDI 1 20:0', 'EDIROL UM-550:EDIROL UM-550 MIDI 2 20:1', 
    #        'EDIROL UM-550:EDIROL UM-550 MIDI 3 20:2', 'EDIROL UM-550:EDIROL UM-550 MIDI 4 20:3',
    #        'EDIROL UM-550:EDIROL UM-550 MIDI 5 20:4', 'EDIROL UM-550:EDIROL UM-550 MIDI 6 20:5',
    #        'Midi Through:Midi Through Port-0 14:0', 'Scarlett 6i6 USB:Scarlett 6i6 USB MIDI 1 28:0']
    return ports

def describe_tracks(midi_file):
    print("\nFile:",midi_file.filename)

def some_notes(chanx):
    notes = [
        Message('note_on', note=67, velocity=45, time=0, channel=chanx),
        Message('note_off', note=67, channel=chanx),
        Message('note_on', note=42, velocity=45, time=0, channel=chanx),
        Message('note_off', note=42, channel=chanx),
        Message('note_on', note=87, velocity=45, time=0, channel=chanx),
        Message('note_off', note=87, channel=chanx),
        Message('note_on', note=27, velocity=45, time=0, channel=chanx),
        Message('note_off', note=27,  channel=chanx)
        ]
    return notes
    

def play_some_notes(portx, channel, dv, aud,auditions ):
    pm = build_patch_message(channel, dv)
    for p in pm:
        portx.send(p)
    
    if aud == 'simple' or aud == '':
        for n in some_notes(channel):
            portx.send(n)
            pause.seconds(0.15)
    else:
        #for msg in MidiFile('song.mid').play():
        for msg in auditions[aud].play():            
            portx.send(msg)


def set_volume(portx,channels,vol):
    for c in channels:
        portx.send(Message('control_change',channel=c,control=7,value=vol))
    return
        
###################################################################################
## port setup
ports = mido_stuff()
rd_port = mido.open_output(ports[1])
prot_port = mido.open_output(ports[2])
mt_port = mido.open_output(ports[3])
## read in patch files for each sound module
mt32_patches = read_patch_file('MT-32_Final_sound_list.csv')
prot_patches = read_patch_file('proteus1_Final_sound_list.csv')
rd800_patches = read_patch_file('RD-800_Final_Sound_List.csv')
dvoice= rd800_patches

auditions = read_audition_files()

# dvoice[0] is the dict, keyed on voice name, for looking up parameters
# dvoice[1] is an array of the simple list of patch names, in the order they appear in the input file
#sg.theme('DarkAmber')

#####
layout = [  
    [sg.Text('Module',size=(8,1),text_color='black'),
     sg.Radio('RD-800', "Module_Selector", default=True, key="rdkey",enable_events=True),
     sg.Radio('Proteus 1', "Module_Selector", key="protkey",enable_events=True),
     sg.Radio('MT-32', "Module_Selector", key="mtkey",enable_events=True)],
    
    [sg.Text('Patch',size=(8,1),text_color='black'),
     sg.Text('Num',size=(4,1),key='num'),
     sg.Text('Name',size=(20,1),key='name')],
    [sg.Text('Section',size=(8,1),text_color='black'), sg.Text(key='section',size=(20,1))],
    
    [sg.Text('Category',size=(8,1),text_color='black'), sg.Text(key='category',size=(20,1))] ,
    
    [sg.Text('MSB',size=(8,1),text_color='black'), sg.Text(key='msb',size=(5,1)),
     sg.Text('LSB',size=(5,1),text_color='black'), sg.Text(key='lsb',size=(5,1)),
     sg.Text('Patch',size=(5,1),text_color='black'), sg.Text(key='patch',size=(5,1)) ],
    
    [sg.Text('Search',size=(8,1),text_color='black'),
     sg.InputText(key='searchx',size=(15,1),enable_events=True)],

    [sg.Text('Audition',size=(8,1),text_color='black'),
     sg.Combo(list(auditions.keys()),key='auditionx',size=(15,1),enable_events=True)], 
    
    [sg.Listbox(values=dvoice[1], size=(40, 30),enable_events=True, key='voice' )],
    [sg.Button('Normalize Volume'), sg.Button('Exit') ] ]

# Create the Window
window = sg.Window('Patch Librarian v.0.2', layout)
## initialize
dvoice = rd800_patches
this_v = 'Concert Grand (*1)'
this_port = rd_port
aud = 'simple'

while True:
    event, values = window.read()
    print("event=",event,"values=",values)
    if event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks cancel
        break
    else:
        if event == 'voice':
            this_v = values['voice'][0]
        elif event in ['searchx']:
            searchx = values['searchx']
            filtered_patches = [ x for x in dvoice[1] if searchx.lower() in x.lower() ]
            window['voice'].update(filtered_patches)
        elif event == 'rdkey':
            dvoice = rd800_patches
            this_v = 'Concert Grand (*1)'
            this_port = rd_port            
            window['voice'].update(dvoice[1])
        elif event == 'protkey':
            dvoice = prot_patches
            this_v = 'Stereo Piano'
            this_port = prot_port
            window['voice'].update(dvoice[1])
        elif event == 'mtkey':
            dvoice = mt32_patches
            this_v = 'Acou Piano 1'
            this_port = mt_port
            window['voice'].update(dvoice[1])
        elif event == 'auditionx':
            aud = values['auditionx']
        elif event == 'Normalize Volume':
            set_volume(rd_port,list(range(0,16)),100)
            set_volume(prot_port,list(range(0,16)),100)            
            set_volume(mt_port,list(range(0,9)),102)
            set_volume(mt_port,[9],102)
        else:
            print("EVENT UNKNOWN........%s " % event)
            
        dv = dvoice[0][this_v]
        window['num'].update(dv['num'])
        window['name'].update(dv['name'])        
        window['section'].update(dv['section'])
        window['category'].update(dv['category'])        
        window['msb'].update(dv['msb'])
        window['lsb'].update(dv['lsb'])
        window['patch'].update(dv['patch'])
        window['auditionx'].update(aud)        
        
        
        if event == 'voice':
            aud = values['auditionx']
            print("dv=",dv)
            play_some_notes(this_port,0,dv,aud,auditions)

window.close()

print("Exiting .........................................")

for p in [rd_port,prot_port,mt_port]:
    p.reset()
    p.close()

#example of sending volume controller value
# mt32=mido.open_output(ports[3])
# mt32.send(Message('control_change',channel=3,control=7,value=110))
#

print("Done.")

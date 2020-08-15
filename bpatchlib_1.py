#https://pysimplegui.readthedocs.io/
import PySimpleGUI as sg
import csv

def read_patch_file(inf):
    voice = {}
    pnames = []
    PATCHDIR = 'Patch_Files/'
    with open(PATCHDIR+inf, 'r') as INF:
        ireader = csv.reader(INF, delimiter='\t')
        #(num, section, cat, name, msb, lsb, patch)
        for row  in ireader:
            if row[0] != 'num':
                # let's keep an list of patch names in the order they were read in
                #print(row[0],row[3])
                pnames.append(row[3].strip())
                voice[row[3].strip()]={ 'name':row[3], 'num':row[0], 'section':row[1], \
                                        'category':row[2],'msb':row[4],'lsb':row[5],'patch':row[6].strip() }
    return voice,pnames

#voice['patchname']['num', 'section', 'category', 'msb', 'lsb', 'patch']

##############################################################
#dvoice, dpatch = read_patch_file()  #v = voice dict, p=patch list
mt32_patches = read_patch_file('MT-32_Final_sound_list.csv')
prot_patches = read_patch_file('proteus1_Final_sound_list.csv')
rd800_patches = read_patch_file('RD-800_Final_Sound_List.csv')

dvoice= rd800_patches
# dvoice[0] is the dict, keyed on voice name, for looking up parameters
# dvoice[1] is an array of the simple list of patch names, in the order they appear in the input file

#sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('Patch Librarian v.0.1')],
            [sg.Radio('RD-800', "Module_Selector", default=True, key="rdkey",enable_events=True),
             sg.Radio('Proteus 1', "Module_Selector", key="protkey",enable_events=True),
             sg.Radio('MT-32', "Module_Selector", key="mtkey",enable_events=True)],
            [sg.Text('Num',size=(5,1)), sg.InputText(key='num',size=(5,1)),
             sg.Text('Section',size=(10,1)), sg.InputText(key='section',size=(20,1)),
             sg.Text('Category',size=(10,1)), sg.InputText(key='category',size=(20,1)) ],

            [sg.Text('MSB',size=(5,1)), sg.InputText(key='msb',size=(5,1)),
             sg.Text('LSB',size=(5,1)), sg.InputText(key='lsb',size=(5,1)),
             sg.Text('Patch',size=(5,1)), sg.InputText(key='patch',size=(5,1))
            ],

            [sg.Listbox(values=dvoice[1], size=(80, 20),enable_events=True,key='voice' )],
            
            [sg.Button('Ok'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Window Title', layout)
# Event Loop to process "events" and get the "values" of the inputs
old_module = 'Nixx'
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    else:
        if values['rdkey'] == True:
            if old_module != 'rd800':
                dvoice = rd800_patches
                old_module='rd800'
                this_v = 'Concert Grand (*1)'
                window['voice'].update(dvoice[1])
            else:
                this_v = values['voice'][0]
        elif values['protkey'] == True:
            if old_module != 'prot':
                dvoice = prot_patches
                old_module = 'prot'
                this_v = 'Stereo Piano'
                window['voice'].update(dvoice[1])
            else:
                this_v = values['voice'][0]
        elif values['mtkey'] == True:
            if old_module != 'mt32':
                dvoice = mt32_patches
                old_module = 'mt32'
                this_v = 'Acou Piano 1'
                window['voice'].update(dvoice[1])
            else:
                this_v = values['voice'][0]
        else:
            print("ERROR! Fail on radio button <===============")
        window['num'].update(dvoice[0][this_v]['num'])
        window['section'].update(dvoice[0][this_v]['section'])
        window['category'].update(dvoice[0][this_v]['category'])        
        window['msb'].update(dvoice[0][this_v]['msb'])
        window['lsb'].update(dvoice[0][this_v]['lsb'])
        window['patch'].update(dvoice[0][this_v]['patch'])
        print('values:',values)

window.close()

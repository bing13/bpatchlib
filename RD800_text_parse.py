# RD800_text_parse.py
# 8/9/2020
##############################

''' ingest hand-wrought sound list, clean, load. 
    prep to generate .ins file. '''


infile='RD-800_Sound_List/Best_Raw_Text_04a.txt'
incats='categories.txt'

notes = []
headings = []
c=0
categories = set()

def pick_out_category(s):
    ok='&+.- ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    accum = ''
    for i in range(len(s)-1,0,-1):
        if s[i] not in ok:
            #print("i=%s s[i]=%s, s=|%s|, accum=|%s|," % (i,s[i],s,accum))
            return(accum.lstrip())
        else:
            #print(i,end='')
            accum = s[i] + accum
## Conflict, shorter form is matching ahead of the proper one
## E.PIANO (TINE E.PIANO) ( and BELL (BELLPAD)
            
cats = []
with open(incats,'r') as INCAT:
    for x in INCAT.readlines():
        cats.append(x.strip())

print("\t".join(['num','section','category','name','bank_MSB','bank_LSB','Patch']))

with open(infile,'r') as INF:
    for line in INF.readlines():
        if line[0] == '*':
            notes.append(line)
        elif '$' in line:
            heading = line[5:-2]
            ###  headings must precede first member item 
            headings.append(heading)
        else:

            if ' 84' not in line:
                print("No 84 in: %s",line)
            else:
                c+=1
                num = line[0:4]
                name =line[5:line.find(' 84')]
                MSB, LSB, Patch =line[line.find(' 84'):-1].split()
                p=pick_out_category(name)
                if p != None:
                    categories.add(p)
                for thiscat in cats:
                    if thiscat in name:
                        break
                #take the cat out of the name string
                newname=name.replace(thiscat,'')
                print("\t".join([num,heading,thiscat,newname,MSB,LSB,Patch]))

print("Notes: %s" % str(notes))
print("Headings: %s" % str(headings))
print("Categories: %s" % str(cats))
print("Number of settings:%s" % c)

#for x in categories:
#    print("+"+x)
#lcat = sorted(list(categories))
#for x in lcat:
#    print(x)

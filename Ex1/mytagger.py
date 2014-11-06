import sys

infile = sys.argv[1]

word_dict = dict()

with open( infile , 'r' ) as input:
    while input.readline():
        line = input.readline()
        if line: 
            inst = line.strip().split(" ")
            if inst[1] == "WORDTAG":
                print float(inst[0]), inst[2], inst[3]
                word_dict[inst[3]] = (float(inst[0]), inst[2])
            

print [ w[0] for w in word_dict.items() ]

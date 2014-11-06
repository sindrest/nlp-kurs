import sys

word_dict = dict()
unigram_dict = dict()

def group_counts( infile ):
    with open( infile , 'r' ) as input:
        for line in input:
            #print line
            if line: 
                inst = line.strip().split(" ")
                #Get all word counts
                cnt = float(inst[0])
                tag = inst[2]
                if inst[1] == "WORDTAG":
                    word = inst[3]
                    tag_count_pairs = word_dict.get( word, [] )
                    tag_count_pairs.append( [ tag, cnt ] )
                    word_dict[ word ] = tag_count_pairs
                    #Get all unigram counts
                elif inst[1] == "1-GRAM":
                    unigram_dict[ tag ] = cnt

def calculate_ratios():
    for word, tag_counts in word_dict.items():
        tag_ratios = list()
        for tag, cnt in tag_counts:
            print word, tag, cnt
            unigram_count = unigram_dict[ tag ]
            tag_ratios.append( [tag, cnt/unigram_count ] ) 
        word_dict[ word ] = tag_ratios

if __name__ == "__main__":
    
    group_counts( sys.argv[1] )

    calculate_ratios()

    #print [ w for w in word_dict ]
    print word_dict["is"]
    
    print unigram_dict.items()


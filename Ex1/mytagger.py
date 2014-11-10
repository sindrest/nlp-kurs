import sys

word_dict = dict()
word_count_dict = dict()
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
        word_count = 0
        for tag, cnt in tag_counts:
            #print word, tag, cnt
            unigram_count = unigram_dict[ tag ]
            word_count += cnt
            tag_ratios.append( [tag, cnt/unigram_count ] ) 
        word_dict[ word ] = tag_ratios
        word_count_dict[ word ] = word_count

def replace_rare_words( infile ):
    outfile = open("gene.train_mod", "w") 
    with open( infile ) as input:
        for line in input:
            if line.strip():
                if word_count_dict.get(line.strip().split(" ")[0],0) < 5:
                    print line.strip(), word_count_dict.get(line.strip().split(" ")[0],0), "_RARE_"
                    outfile.write( "_RARE_ " + line.strip().split(" ")[1] + "\n" )
                else:
                    outfile.write( line )
            else:
                outfile.write( line )
    outfile.close()

def tagger( infile ):

    outfile = open( "gene_dev.p1.out" , "w")

    rare_tag = ""
    rare_ratio = 0
    for tag_ratio in word_dict[ "_RARE_" ]:
        if tag_ratio[1] >= rare_ratio:
            rare_ratio = tag_ratio[1]
            rare_tag = tag_ratio[0]


    with open( infile ) as input:
        for line in input:
            if line.strip():
                if word_count_dict.get( line.strip() ):
                    tag = ""
                    ratio = 0
                    for tag_ratio in word_dict[ line.strip() ]:
                        if tag_ratio[1] >= ratio:
                            ratio = tag_ratio[1]
                            tag = tag_ratio[0]
                    outfile.write( line.strip() + " " + tag + "\n" )
                else:
                    outfile.write( line.strip() + " " + rare_tag + "\n" )
            else:
                outfile.write( line )
    outfile.close()
                

if __name__ == "__main__":
    
    counts_file = "gene.counts_mod"
    dev_file = "gene.dev"
    
    group_counts( counts_file )
    calculate_ratios()

    tagger( dev_file )
    #replace_rare_words( sys.argv[2] ) 

    #print [ w for w in word_dict ]
    #print word_dict["is"]
    
    #print word_count_dict["is"]

    #print unigram_dict.items()


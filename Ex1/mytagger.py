import sys

word_dict = dict()
word_count_dict = dict()
unigram_dict = dict()
bigram_dict = dict()
trigram_dict = dict()

def group_counts( infile ):
    with open( infile , 'r' ) as input:
        for line in input:
            #print line
            if line: 
                inst = line.strip().split(" ")
                #Get all word counts
                cnt = float(inst[0])
                if inst[1] == "WORDTAG":
                    tag = inst[2]
                    word = inst[3]
                    tag_count_pairs = word_dict.get( word, [] )
                    tag_count_pairs.append( [ tag, cnt ] )
                    word_dict[ word ] = tag_count_pairs
                    #Get all unigram counts
                elif inst[1] == "1-GRAM":
                    tag = inst[2]
                    unigram_dict[ tag ] = cnt
                elif inst[1] == "2-GRAM":
                    tag = "_".join( inst[2:4] )
                    bigram_dict[ tag ] = cnt
                elif inst[1] == "3-GRAM":
                    tag = "_".join( inst[2:5] )
                    trigram_dict[ tag ] = cnt


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
    word_dict[ "*" ] = [["*", 1.0]]
    word_dict[ "STOP" ] = [["STOP", 1.0]]

    for trigram, cnt in trigram_dict.items():
        bigram = "_".join( trigram.split("_")[0:2] )
        trigram_dict[ trigram ] = cnt/bigram_dict[ bigram ]

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
    outfile = open( "gene_test.p1.out" , "w")
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

def viterbi_tagger( infile_name ):
    
    infile = open( infile_name )
    outfile = open( "gene_viterbi.p1.out", "w" )

    current_sentence = "* *"
    default = word_dict.get( "_RARE_" )  
    for line in infile:
        if line.strip() == "":
            current_sentence = current_sentence + " STOP"
            sentence_list = current_sentence.split(" ")
            n = len(sentence_list)
            #dynamic programming
            pi = dict()
            bpi = dict()
            pi[ "0 * *" ] = 1.0
            
            for k in xrange(2,n):
                word = sentence_list[k]
                word_prev = sentence_list[k-1]
                word_prev2 = sentence_list[k-2]
                
                word_tag_ratios = word_dict.get( word, default )
                word_prev_tag_ratios = word_dict.get( word_prev, default )
                word_prev2_tag_ratios = word_dict.get( word_prev2, default )
                
                for u in word_tag_ratios:
                    e = u[1] #get transmission prob
                    for v in word_prev_tag_ratios:
                        state = str(k-1)+" "+v[0]+" "+u[0]
                        score_best = 0.0
                        w_best = "0"
                        for w in word_prev2_tag_ratios:
                            #perform calculation
                            state_w = str(k-2)+" "+w[0]+" "+v[0]
                            trigram_prob = trigram_dict.get( w[0]+"_"+v[0]+"_"+u[0] )
                            #print trigram_prob
                            current_score = pi.get( state_w ) * trigram_prob * e
                            if current_score > score_best:
                                score_best = current_score
                                w_best = w[0]
                        pi[ state ] = score_best
                        bpi[ state ] = w_best
                
            y = ["O"]*(n-3)

            word_prev = sentence_list[n-2]
            word_prev2 = sentence_list[n-3]
            word_prev_tag_ratios = word_dict.get( word_prev, default )
            word_prev2_tag_ratios = word_dict.get( word_prev2, default )
            score_best = -0.1
            for u in word_prev_tag_ratios:
                for v in word_prev2_tag_ratios:
                    state = str(n-3)+" "+v[0]+" "+u[0]
                    trigram_prob = trigram_dict.get( v[0]+"_"+u[0]+"_STOP" )
                    print trigram_prob
                    current_score = pi.get( state ) * trigram_prob
                    if current_score > score_best:
                        score_best = current_score
                        y[n-5] = v[0] 
                        y[n-4] = u[0]
            
            for i in xrange(4,n-1):
                idx = n - i
                w = sentence_list[idx]
                k = str(idx+1)+' '+y[idx-1]+' '+y[idx]
                if bpi.has_key(k):
                    y[idx-2] = bpi.get(k)

            #Write to output file:
            for i in xrange( 2, n-1 ):
                outfile.write( sentence_list[i] + " " + y[i-2] + "\n" )
            outfile.write( "\n" )

            current_sentence = "* *"
        else:
            current_sentence = current_sentence + " " + line.strip()
    
    infile.close()
    outfile.close()
                

if __name__ == "__main__":
    
    counts_file = "gene.counts_mod"
    dev_file = "gene.dev"
    
    group_counts( counts_file )
    
    calculate_ratios()
    
    #print trigram_dict
    #print bigram_dict
    #print unigram_dict
    

    tagger( dev_file )
    
    viterbi_tagger( dev_file ) 
    #replace_rare_words( sys.argv[2] ) 

    #print [ w for w in word_dict ]
    #print word_dict["is"]
    
    #print word_count_dict["is"]

    #print unigram_dict.items()


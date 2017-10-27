#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 12:21:48 2017

@author: Isabel et Hermes
"""

import word2vec
import test as tst
import evaluation as eva



e_file = "frWac_postag_no_phrase_700_skip_cut50.bin"
input_file = "lexsubfr_semdis2014_test-1.id_melt"
gold_file = "semdis2014_lexsub_gold.txt"

#dico = {0 : "Fredist", 1: "w2v"}

comb_args = []

#set f
for nb in range(30):
    #set include_word
    for word in [False, True]:
        if word == False:
            word1 = "False"
        else:
            word1 = "True"
        output1 = str(nb) + "_" + word1 + "_False_fredist.txt"
        comb_args.append([output1, nb, word, False, True])
        output2 = str(nb) + "_" + word1 + "_False_w2v.txt"
        comb_args.append([output2, nb, word, False, False])

        
#set all_sent
for word in [False, True]:
    if word == False:
        word1 = "False"
    else:
        word1 = "True"
    output1 = "1_" + word1 + "_True_fredist.txt"
    comb_args.append([output1, 1, word, True, True])
    output2 = "1_" + word1 + "_True_w2v.txt"
    comb_args.append([output2, 1, word, True, False])

print(comb_args)


# Initialize model
model = word2vec.load(e_file)
print("Model loaded...")
    
# Get instances
instances = tst.split(input_file)
print("Instances created...")

for args in comb_args:
    print(args[0])
    tst.subs(model, instances, args[0], args[1], args[2], args[3], args[4])

#    acc = eva.evaluate(gold_file, args[0])
#    print(args[0] + ", acc : " + str(acc) + "%")



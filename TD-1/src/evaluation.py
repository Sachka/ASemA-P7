#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 18:47:23 2017

@author: Isabel et Hermes
"""

import argparse



def evaluate(file1, file2):
    instream1 = open(file1, 'r')
    instream2 = open(file2, 'r')
    line1 = instream1.readline()
    line2 = instream2.readline()
    denom = 0
    acc = 0.0
    while line1:
#        print(denom)
        
        # Take 3 first subsitutes of gold
        s_line1 = line1.split(" ")[4:]
        ele1 = []
        i=0
        while i < len(s_line1):
            ele1.append(s_line1[i])
            i += 2
        ele1 = ele1[:3]
#        print(ele1)
        
        #Take 3 first subsitutes of output
        s_line2 = line2.split(" ")[4:]
        ele2 = []
        j=0
        while j < len(s_line2):
            ele2.append(s_line2[j])
            j += 2
        ele2 = ele2[:3]
#        print(ele2)
        
        #Test if element in common
        curr_acc = 0.
        for ele in ele1:
            if ele in ele2:
                curr_acc = 1
                break
        acc += curr_acc
        denom += 1
        line1 = instream1.readline()
        line2 = instream2.readline()
    
    #Print accuracy

    instream1.close()
    instream2.close()
    
    return acc/denom * 100

    
#########################################   
    
    

#parser = argparse.ArgumentParser(description='Évaluation')
#
#
#parser.add_argument('filename', metavar='FILENAME', help='Filename to compare')
#
#args = parser.parse_args()
#
#
#s1_file = "semdis2014_lexsub_gold.txt"
#
#print(evaluate(s1_file, args.filename))




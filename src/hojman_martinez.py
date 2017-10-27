# encoding: UTF-8
import word2vec
# import xml.etree.ElementTree as ET
import numpy as np
from scipy import spatial
import argparse


"""
Tp 1 : Analyse Sémantique
Isabel Hojman et Hermes Martinez
"""


def split(filename):
    """
    Split file ("nb_inst \t mot \t tag \t pos \t sentence")
    Return list of instances du type : [nb_instance, word, tag, pos, [sentence]]
    """
    tag_convert = {'ADJ': 'a', 'ADJWH': 'a', 'ADV': 'adv', 'ADVWH': 'adv', 'CC': 'c', 'CLO': 'cl',
                   'CLR': 'cl', 'CLS': 'cl', 'CS': 'c', 'DET': 'd', 'ET': 'd', 'I': 'i', 'NC': 'n', 'NPP': 'n',
                   'P': 'p', 'P+D': 'p+d', 'P+PRO': 'p+pro', 'PRO': 'pro', 'PROREL': 'pro', 'PROWH': 'pro',
                   'V': 'v', 'VIMP': 'v', 'VINF': 'v', 'VPP': 'v', 'VPR': 'v', 'VS': 'v', 'PONCT': 'ponct'}
    instance = []
    instances = []
    # tags = set([])
    instream = open(filename, 'r')
    line = instream.readline()
    while line:
        line = line.split("\t")
        if len(line) == 5:
            instance = line[:4]
            instance[3] = int(instance[3]) - 1
            split_sentence = line[4].split()
            sentence = []
            for elt in split_sentence:
                word, tag, lemme = elt.split("/")
                if lemme[0] == '*':
                    lemme = lemme[1:].lower()
                if tag == 'CLO':
                    lemme = word
                # tags.add(tag)
                sentence.append(str(lemme + '_' + tag_convert[tag]))
            instance.append(sentence)
            instances.append(instance)
        line = instream.readline()
    instream.close()
    return instances
    # return sorted(tags)


def phrase2vec(model, instance, f=7, include_word=True, all_sent=False):
    """
    Input: instance [nb_instance, word, tag, pos, [sentence]], long_words_window, include_word, include all word of sent
    Output: vecteur qui est la somme des mots du contexte du mot cible (et du mot cible si c'est le cas)
    """
#    result_vec = np.zeros(model.vectors.shape[1])
    if f == 0:
        include_word = True
        
    result_vec = np.full((1,model.vectors.shape[1]), 0.0000001) #lissage
    key_pos = instance[3]
    
    if all_sent == True: 
        beg_idx = 0
        end_idx = len(instance)
    else:
        key_pos = instance[3]
        beg_idx = max(key_pos - f, 0)
        end_idx = min(key_pos + f, len(instance))
        
#    word_count = 0
    for idx in range(beg_idx, end_idx + 1):
        if include_word is False and idx == key_pos:
            pass
        else:
            if instance[4][idx] in model:
#                word_count += 1
                result_vec = np.add(result_vec, model[instance[4][idx]])
#    result_vec /= word_count
    return result_vec

def create_thesaurus():
    """
    Return dico word : [possible_substitutes] à partir de thesaurus
    """
    dico = {}
    files = [("thesaurus_french_A.txt", "a"), ("thesaurus_french_ADV.txt", "adv"), 
             ("thesaurus_french_N.txt", "n"), ("thesaurus_french_V.txt", "v")]
    for filename, tag in files:
        instream = open(filename, "r")
        line = instream.readline()
        while line:
            line = line.split("\t")
            word = line[0].split("|")[1] + "_" + tag
            subs = []
            for sub in line[1:]:
               sub = sub.split("|")[1]
               s, d = sub.split(":")
               subs.append([s + "_" + tag, d])
            dico[word] = subs
            line = instream.readline()
        instream.close()
    print("Thesaurus loaded.")
    return dico

def find_substitutes(model, instance, f=7, include_word=True, all_sent=False, fredist=False, dico={}):
    """
    Input: instance [nb_instance, word, tag, pos, [sentence]], long_words_window, include_word, include all word of sent
    Output: list of substitute, distance, distance to result vector
    """
    # Solve case where tag in instance[2] don't match tag in sentence
    tag_inst = instance[2]
    tag_w =  instance[4][instance[3]].split("_")[1]  
    if tag_inst == tag_w:    
        target = instance[4][instance[3]]
    else:
        if tag_w == "v":
            target = instance[4][instance[3]]
        else:
            target = instance[1] + "_" + instance[2]
    
    # Calculate result vector
    result_vec = phrase2vec(model, instance, f, include_word, all_sent)
    
    # Find n closer candidates
    if fredist == True:
        if target in dico:
            neigh = dico[target][:100]
        else:
            return None
    else:
        idx, metrics = model.cosine(target, n=60)
        neigh = model.generate_response(idx, metrics).tolist()

    new_neigh = []
    for elt in neigh:
        word, tag = elt[0].rsplit("_", 1)
        if tag == instance[2]:
            if elt[0] in model.vocab:
                candidate = model[elt[0]]
                distance = 1 - spatial.distance.cosine(result_vec, candidate)          
                new_neigh.append((elt[0], elt[1], distance))
    return sorted(new_neigh, key=lambda x: x[2], reverse=True)[:10]

def subs(model, instances, output_file, f=7, include_word=True, all_sent=False, fredist=False):
    """
    Find substitutes for a list of instances.
    """
    solution = []
    if fredist == True:
        dico = create_thesaurus()
    else:
        dico = None
        
    # Parcourt instances
    for instance in instances:
        substitutes = find_substitutes(model, instance, f, include_word, all_sent, fredist, dico)
        if substitutes == None:
            target = instance[1] + "." + instance[2] + " " + instance[0] + " ::  \n"
            solution.append([int(instance[0]), target])
        else:
            enum = ""
#            denom = 0.
#            for j in range(len(substitutes)):
#                denom += 1/abs(substitutes[j][2])
            for i in range(len(substitutes)):
                enum += " " + substitutes[i][0].split("_")[0] + " ;" #+ str((1/abs(substitutes[i][2]))/denom) + ";"
        #        enum += " " + substitutes[i][0].split("_")[0] + " " + str(len(substitutes) - i) + ";"
            target = instance[1] + "." + instance[2] + " " + instance[0] + " ::" + enum[:-2] + "\n"
            solution.append([int(instance[0]), target])
    
    solution = sorted(solution, key=lambda x: x[0])
    
    # Create doc to compare
    sol = open(output_file, "w")
    for elt in solution:
        sol.write(elt[1])
    sol.close()
    return solution  

######################################################
    
#e_file = "frWac_postag_no_phrase_700_skip_cut50.bin"
#
#
#parser = argparse.ArgumentParser(description='Substitution Lexicale')
#
#
#parser.add_argument('filename', metavar='FILENAME', help='Filename with format "nb_inst \t mot \t tag \t pos \t sentence \n"')
#parser.add_argument('output_filename', metavar='OUTPUT', help='Output File name')
#parser.add_argument('-f', default=7, type=int, metavar='F', help='Number of words. Window = 2F')
#parser.add_argument('-include_word', default="True", metavar='I', help='Include the target word. True or False. True par défaut')
#parser.add_argument('-all_sent', default="False", metavar='A', help='Include all sentences. True or False. False par défaut')
#parser.add_argument('-fredist', default="False", metavar='FR', help='Use Fredist to get substitutes')
#
#args = parser.parse_args()
#
#
## Initialize model
#model = word2vec.load(e_file)
#
## Get instances
#instances = split(args.filename)
#subs(model, instances, args.output_filename, args.f, args.include_word in ["True", "true", "TRUE"], args.all_sent in ["True", "true", "TRUE"], args.fredist in ["True", "true", "TRUE"])


######################################################
   

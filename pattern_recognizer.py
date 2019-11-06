"""
Created on Fri Apr 12 20:03:02 2019

Brad Erickson

Pattern Recognizer
"""
#Imports
import csv
import datetime
import logging
import math
import pronouncing
import string
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 

#initialization
date_time = str(datetime.date.today())
date_time = date_time.replace(' ', '_').replace(':', '-')
log_name = date_time + "_music_webscraper.log"
logging.basicConfig(filename=log_name, level=logging.INFO)

alphabet = string.ascii_uppercase + "------------------------------------------------------------------------------"
stop_words = set(stopwords.words('english'))


def get_list_from_csv(file):
    """ Import CSV to list form """
    
    with open(file, 'r') as f:
        reader = csv.reader(f)
        your_list = list(reader)
        
    return your_list


def get_info_list(track_info_list, info_index):
    """ get list of only info at index """
    
    lyric_list = []
    
    for track in track_info_list:
        lyric_list.append(track[info_index])
        
    return lyric_list


def get_list_of_stanzas(lyric):
    """ Take a lyric list and change them to stanzas """
    
    stanza_list = []
    
    lyric_split = lyric.split('////')
    
    for stanza in lyric_split:
        
        if (stanza is not None):
            if (stanza[:1] == '['):
                stanza = stanza[stanza.find(']') + 1:]
            if (stanza != ''):
                stanza_list.append(stanza.split('//'))
        
    return stanza_list


def get_list_of_stanza_patterns(pattern):
    """ Take a pattern strings and switch to stanzas """
    
    stanza_pattern_list = []
    
    pattern_split = pattern.split('////')
    
    for stanza in pattern_split:
        
        if (stanza is not None):
            if (stanza[:1] == '['):
                stanza = stanza[stanza.find(']') + 1:]
            if (stanza != ''):
                stanza_pattern_list.append(stanza.split('//'))
        
    return stanza_pattern_list


def clean_stanza(stanza):
    """ Clean the stanza, remove symbols and stop words """
    
    clean_stanza = []
    for verse in stanza:
        tokenized_verse = word_tokenize(verse)
        filtered_verse = []
        
        for word in tokenized_verse:
            if word.lower() not in stop_words:
                #filtered_verse.append(word)
                pass
            filtered_verse.append(word)
                
        cleaned_verse = ' '.join(filtered_verse)  
        if (verse != ""):
            clean_stanza.append(cleaned_verse)
        
    return clean_stanza
   
    
def compare_verses_with_last_words(clean_stanza):
    """ Compare verses within a stanza for a pattern using only the last rhyme """
    
    verse_phones = []
    
    for verse in clean_stanza:
        verse_split = verse.split()
        verse_rhyme = []
        
        for word in verse_split:
            word_phone = pronouncing.phones_for_word(word)
            try:
                verse_rhyme.extend(pronouncing.rhyming_part(word_phone[0]).split())
            except:
                logging.error(" Unable to extend None type")
            
        verse_phones.append(verse_rhyme)
    
    verse_phones_length = len(verse_phones)
    pattern = [None] * verse_phones_length
    alphabet_index = 0

    for i in range(verse_phones_length - 1):
        
        prediction = [0] * (verse_phones_length - i - 1)
        
        for j in range(i + 1, verse_phones_length):
            
            if (verse_phones[i][len(verse_phones[i]) - 1] == verse_phones[j][len(verse_phones[j]) - 1]):
                prediction[j - i - 1]  += 1
        
        if (pattern[i] is None):
            pattern[i] = alphabet[alphabet_index]
            pattern[prediction.index(max(prediction)) + i + 1] = alphabet[alphabet_index]
            alphabet_index += 1
        
        #print (prediction)
    
    for i in range (len(pattern)):
        if (pattern[i] is None):
            pattern[i] = "?"
        
    return pattern    
    

def compare_verses_with_threshold(clean_stanza, rhyme=True):
    """ Compare verses within a stanza for a pattern using a threshold comparison """
    
    verse_phones = []
    
    for verse in clean_stanza:
        verse_split = verse.split()
        verse_rhyme = []
        
        for word in verse_split:
            word_phone = pronouncing.phones_for_word(word)
            if rhyme:
                try:
                    verse_rhyme.extend(pronouncing.rhyming_part(word_phone[0]).split())
                except:
                    logging.error(" Unable to extend None type")
            else:
                try:
                    verse_rhyme.extend(word_phone[0].split())
                except:
                    logging.error(" Unable to extend None type")
            
        verse_phones.append(verse_rhyme)
    
    verse_phones_length = len(verse_phones)
    pattern = [None] * verse_phones_length
    alphabet_index = 0

    for i in range(verse_phones_length - 1):
        
        prediction = [0] * (verse_phones_length - i - 1)
        
        for j in range(i + 1, verse_phones_length):
            
            for k in range(len(verse_phones[i])):
                
                percentile = k/len(verse_phones[i])
                lower_bound_percentile = (percentile - 0.10) if (percentile - 0.10 >= 0) else 0
                upper_bound_percentile = (percentile + 0.10) if (percentile + 0.10 <= 100) else 1
                lower_bound_index = math.floor(lower_bound_percentile * len(verse_phones[j]))
                upper_bound_index = math.ceil(upper_bound_percentile * len(verse_phones[j]))
                
                if verse_phones[i][k] in verse_phones[j][lower_bound_index:upper_bound_index]:
                    #print ("i:\t" + str(i) + "\tk:\t" + str(k) + "\tj:\t" + str(j) + "\tphone:\t" + verse_phones[i][k])
                    prediction[j - i - 1] += 1
        
        if (pattern[i] is None):
            pattern[i] = alphabet[alphabet_index]
            pattern[prediction.index(max(prediction)) + i + 1] = alphabet[alphabet_index]
            alphabet_index += 1
        
        #print (prediction)
    
    for i in range (len(pattern)):
        if (pattern[i] is None):
            pattern[i] = alphabet[alphabet_index]
            alphabet_index += 1
        
    return pattern
    

def write_to_csv(file_name, headers, content):
    """ Write a list of information to a csv """
    
    logging.info(" Output to csv for " + file_name)
    
    date_time = str(datetime.date.today())
    date_time = date_time.replace(' ', '_').replace(':', '-')
    
    file_name = date_time + "_" + file_name + ".csv"
    
    with open(file_name, 'w', newline='', errors='ignore') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(content)

            

track_info_list = get_list_from_csv("test_data.csv")

name_list = get_info_list(track_info_list,0)
lyric_list = get_info_list(track_info_list,1)
pattern_list = get_info_list(track_info_list,2)
predicted_list = []
correct_percent_list = []
correct_percent_global = []

for i in range(len(name_list)):
    
    stanza_lyric_list = get_list_of_stanzas(lyric_list[i])
    stanza_pattern_list = get_list_of_stanza_patterns(pattern_list[i])
    stanza_pattern_predicted = "////"
    errors_global = 0
    total_length = 0
    stanza_percent_list = []
    
    for j in range(len(stanza_lyric_list)):
        
        cleaned_stanza_lyrics = clean_stanza(stanza_lyric_list[j])
        pattern_actual = stanza_pattern_list[j]
        pattern_predicted = compare_verses_with_last_words(cleaned_stanza_lyrics)
        stanza_pattern_predicted = stanza_pattern_predicted + "//".join(pattern_predicted) + "////"
        
        errors_local = 0
        for k in range(len(pattern_actual)):
            total_length += 1
            if (pattern_actual[k] != pattern_predicted[k]):
                errors_local += 1
                errors_global += 1
        stanza_percent_list.append(str(1 - errors_local/len(pattern_actual)))
    
    stanza_pattern_predicted = stanza_pattern_predicted + "////"
    predicted_list.append(stanza_pattern_predicted)
    correct_percent_list.append(stanza_percent_list)
    correct_percent_global.append(1 - errors_global/total_length)
    
for i in range(len(name_list)):
    overall = []
    headers = []
    overall_single = []
    overall_single.append(name_list[i])
    headers.append("name")
    overall_single.append(lyric_list[i])
    headers.append("lyric")
    overall_single.append(predicted_list[i])
    headers.append("predicted")
    overall_single.append(pattern_list[i])
    headers.append("actual")
    overall_single.append(str(correct_percent_global[i]))
    headers.append("global_correct_percent")
    for j in range(len(correct_percent_list[i])):
        headers.append("stanza_" + str(j) + "_correct_percent")
        overall_single.append(str(correct_percent_list[i][j]))
    overall.append(overall_single)
    
    write_to_csv("predicted_patterns_with_last_words_" + str(i), headers, overall)
    
#write_to_csv("predicted_patterns", ["name", "lyric", "predicted", "actual", "correct_by_stanza", "correct_overall"], overall)
    
    


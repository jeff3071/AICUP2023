from transformers.pipelines.token_classification import TokenClassificationPipeline
from transformers import AutoTokenizer, AutoModelForTokenClassification
import glob
from tqdm import tqdm
from utils import (
    extract_doctors, 
    date_convert_to_iso_format, 
    extract_dates_from_article, 
    extract_phone_number, 
    extract_time_strings, 
    extract_DEPARTMENT_HOSPITAL, 
    extract_patient,
    extract_location_other,
    extract_street_city_state,
    extract_organization,
    extract_duration
)

model_path = "./bert_finetuned_ner/checkpoint_12873/"

model = AutoModelForTokenClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)

token_classifier = TokenClassificationPipeline(
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple", 
    stride=256,
    device=0
)

def is_valid_char(char):
    return ('0' <= char <= '9') or ('a' <= char <= 'z') or ('A' <= char <= 'Z')

def is_valid_num(char):
    return ('0' <= char <= '9')

def post_process(file_name, sentence, token):
    temp_list = []
    if token['entity_group'] in ["DEPARTMENT" ,"HOSPITAL", "DATE" ,"PATIENT", "ORGANIZATION", "CITY", "STATE"]:
        return temp_list
    
    if token['entity_group'] == "MEDICALRECORD":
        token['word'] = token['word'].replace(' ', '')
        temp_list.append(f"{file_name}\t{token['entity_group']}\t{token['start']}\t{token['end']}\t{token['word']}\n")
    
    elif token['entity_group'] == "IDNUM":
        IDNUMS = token['word'].split(',')
        start_idx = token['start']
        for IDNUM in IDNUMS:
            correct_IDNUM = ""
            
            correct_start_idx = 0
            correct_end_idx = len(IDNUM) - 1
            
            while correct_start_idx < len(IDNUM) and not is_valid_char(IDNUM[correct_start_idx]):
                correct_start_idx += 1
            
            while correct_end_idx > 0 and not is_valid_char(IDNUM[correct_end_idx]):
                correct_end_idx -= 1
                
            correct_IDNUM = IDNUM[correct_start_idx:correct_end_idx+1]
            
            if correct_IDNUM != '':
                temp_list.append(f"{file_name}\t{token['entity_group']}\t{start_idx+correct_start_idx}\t{start_idx+correct_start_idx+len(correct_IDNUM)}\t{correct_IDNUM}\n")
            start_idx += start_idx+correct_start_idx+len(correct_IDNUM) + 1
            
    elif token['entity_group'] == "AGE":
        age = token['word']
        correct_start_idx = 0
        correct_end_idx = len(age) - 1
        
        while correct_start_idx < len(age) and not is_valid_num(age[correct_start_idx]):
            correct_start_idx += 1
        
        while correct_end_idx > 0 and not is_valid_num(age[correct_end_idx]):
            correct_end_idx -= 1
        correct_age = age[correct_start_idx:correct_end_idx+1]
        
        if correct_age != '':
            temp_list.append(f"{file_name}\t{token['entity_group']}\t{token['start']+correct_start_idx}\t{token['start']+correct_start_idx+len(correct_age)}\t{correct_age}\n")
    
    else:
        if sentence[token["start"]:token["end"]+1] != token['word']:
            token['word'] = sentence[token["start"]:token["end"]+1].replace('\n','')
            
        temp_list.append(f"{file_name}\t{token['entity_group']}\t{token['start']}\t{token['end']}\t{token['word'].strip()}\n")       
    return temp_list

# date will get time string
def date_post_process(time_list, date_list):
    time_data = []
    filter_date_list = []
    for time in time_list:
        line = time.split('\t')
        time_data.append(f"{line[0]} {line[2]}")
        time_data.append(f"{line[0]} {line[3]}")
    
    for date in date_list:
        line = date.split('\t')
        if f"{line[0]} {line[2]}" not in time_data and f"{line[0]} {line[3]}" not in time_data:
            filter_date_list.append(date)
        
    return filter_date_list


def predict(file_name, sentence):
    res = token_classifier(sentence)
    file_predict = []
    for token in res:
        file_predict += post_process(file_name, sentence, token)
    
    doctor_list = extract_doctors(file_name, sentence)
    for doctor in doctor_list:
        if doctor not in file_predict:
            file_predict.append(doctor)
            
    phone_list = extract_phone_number(file_name, sentence)
    for phone in phone_list:
        if phone not in file_predict:
            file_predict.append(phone)
    
    time_list = extract_time_strings(file_name, sentence)
    file_predict += time_list
    
    date_list = extract_dates_from_article(file_name, sentence)
    date_list = date_post_process(time_list, date_list)
    for date in date_list:
        if date not in file_predict:
            file_predict.append(date)
    
    file_predict += extract_DEPARTMENT_HOSPITAL(file_name, sentence)
    
    medicalrecord_list = []
    idnum_idx = 0
    zip_idx = 0
    
    
    for token in file_predict:
        if token.split('\t')[1] == "MEDICALRECORD":
            medicalrecord_list.append(token.split('\t')[4].replace("\n", ""))
        
        if token.split('\t')[1] == "ZIP":
            zip_idx = int(token.split('\t')[2])
    
    for token in file_predict:
        if token.split('\t')[1] == "IDNUM":
            temp_idx = int(token.split('\t')[3])
            if temp_idx < zip_idx:
                idnum_idx = temp_idx
    
    file_predict += extract_patient(file_name, medicalrecord_list, sentence)
    file_predict += extract_organization(file_name, sentence)
    
    file_predict += extract_location_other(file_name, sentence)
    
    if zip_idx > idnum_idx:
        street_city_state = extract_street_city_state(file_name, sentence, idnum_idx, zip_idx)
        for data in street_city_state:
            if data not in file_predict:
                file_predict.append(data) 
    
    start_idx = []
    for token in file_predict:
        start_idx.append(int(token.split('\t')[2]))
    
    
    durations = extract_duration(file_name, sentence)
    
    for duration in durations:
        if int(duration.split('\t')[2]) not in start_idx:
            file_predict.append(duration)
    
    return file_predict

file_list = glob.glob("./data/First_Phase_Release/Validation_Release/" + '*')

final_result = []

for file in tqdm(file_list):
    file_name = file.split('/')[-1].split('.')[0]
    with open(file, 'r', encoding='utf-8-sig') as f:
        sentence = f.read()
        file_predict = predict(file_name, sentence)
        final_result += file_predict

with open("./temp.txt", 'w', encoding='utf-8-sig') as f:
    f.writelines(final_result)
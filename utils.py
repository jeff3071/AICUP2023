import re
from datetime import datetime
from collections import defaultdict

def find_all_positions(string, sub):
    return [i for i in range(len(string)) if string.startswith(sub, i)]

def extract_doctors(file_name, article):
    pattern = r'\b(?:Prof|DR|Dr|Drs)\.?\s+([A-Z][a-zA-Z.]*(?:[-\s][A-Z][a-zA-Z]*)*)'

    matches = re.finditer(pattern, article)
    
    extracted_names = []
    for match in matches:
        name = match.group(1)
        name = name.split("\n")[0]

        name = name.replace(" at", "")
        name = name.replace(" Drs", " Dr")
        name = name.replace(" and", "")
        name = name.replace(" by" , "")
        
        correct_doctor_name = name.strip()
        start_index = match.start(1)

        answer = f"{file_name}\tDOCTOR\t{start_index}\t{start_index + len(correct_doctor_name)}\t{correct_doctor_name}\n"
        if answer not in extracted_names:
            extracted_names.append(answer)
            
    pattern_1 =  r'(?<=TO:\s)[a-zA-Z;:]+'
    matches_1 = re.finditer(pattern_1, article)
    
    for match_1 in matches_1:
        name = match_1.group(0).strip()
        start_index = match_1.start()
        
        name = name.replace("TO:", "").replace(":", ";").strip()
        names = name.split(";")

        for doctor_name in names:
            if len(doctor_name) > 0:
                correct_doctor_name = doctor_name.strip()
                answer = f"{file_name}\tDOCTOR\t{start_index}\t{start_index + len(correct_doctor_name)}\t{correct_doctor_name}\n"
                start_index += len(correct_doctor_name)+1
                if answer not in extracted_names:
                    extracted_names.append(answer)
                
                
    return extracted_names

def time_convert_to_iso_format(time_str):
    time_str = time_str.replace("\n", "")
    
    try:
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        correct_dt = dt.strftime('%Y-%m-%dT%H:%M:%S')
        return f"{correct_dt}"
    except:
        pass
    
    formats = [
        "%d/%m/%Y at %H:%M",
        "%I%p on %d/%m/%y",
        "%d/%m/%Y at %I:%M",
        "%d/%m/%Yat%H:%M",
        "%d/%m/%Yat %H:%M",
        "%dst of %B %Y at %I:%M%p",
        "%d/%m/%Y at %H:%M",
        "%d.%m.%y @ %I.%M%p",
        "%I:%M%p on %d.%m.%y",
        "%H.%M on %d/%m/%y",
        "%I:%M%p on %d/%m/%y",
        "%d.%m.%Y at %H:%M",
        "%d/%m/%Y at %I:%M%p",
        "%Y-%m-%dT%H:%M",
        "%I:%M%p on %d/%m/%Y",
        "%d.%m.%y at %H:%M",
        "%I:%M on %d/%m/%y",
        "%I:%M%p on %d.%m.%Y",
        "%H:%M on %d/%m/%y",
        "%I:%M%p on %d.%m.%Y",
        "%I:%M%p on %d.%m.%y",
        "%H:%M on %d/%m/%Y",
        "%H.%M on %d.%m.%y",
        "%I:%M%p on %d.%m.%y",
        "%I:%M on %d.%m.%Y",
        "%H:%M on %d.%m.%y",
        "%I:%M%p on %d.%m.%y",
        "%I.%M%p on %d/%m/%y",
        "%I.%M%p on %d.%m.%y",
        "%d/%m/%y at %I.%M%p",
        "%d/%m/%y at %I:%M%p",
        "%d.%m.%y at %I.%M%p",
        "%d.%m.%y at %I:%M%p",
        "%d.%m.%Y at %I.%M%p",
        "%H.%M%p on %d/%m/%y",
        "%H:%M%p on %d/%m/%y",
        "%d/%m/%Y at %H:%M%p",
        "%H:%M%p on %d.%m.%y",
        "%d.%m.%Y at %H.%M%p",
        "%H.%M%p on %d.%m.%y",
        "%d.%m.%Y at %H:%M%p",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            correct_dt = dt.strftime('%Y-%m-%dT%H:%M')
            return f"{correct_dt}"
        except ValueError:
            pass
    return ""

def extract_time_strings(file_name, article):
    formats = [
        r"(\d{2}/\d{2}/\d{4} at \d{2}:\d{2})",
        # r"(\d{1,2}[ap]m on \d{2}/\d{2}/\d{2})",
        r"(\d{2}/\d{2}/\d{4} at \d{1,2}:\d{2})",
        r"(\d{2}/\d{2}/\d{4}at\d{2}:\d{2})",
        r"(\d{2}/\d{2}/\d{4}at \d{2}:\d{2})",
        r"(\d{1,2}st of \w+ \d{4} at \d{1,2}:\d{2}[ap]m)",
        r"(\d{2}/\d{2}/\d{4} at \d{2}:\d{2})",
        r"(\d{2}\.\d{2}\.\d{2} @ \d{1,2}\.\d{2}[ap]m)",
        r"(\d{1,2}:\d{2}[ap]m on \d{2}\.\d{2}\.\d{2})",
        r"(\d{2}\.\d{2} on \d{2}/\d{2}/\d{2})",
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
        r'\b(\d{1,2}:\d{2}[ap]m\s+on\s+\d{1,2}[./]\d{1,2}[./]\d{2,4})\b',
        r'\b(\d{1,2}[./]\d{1,2}[./]\d{2,4}\s+at\s+\d{1,2}:\d{2})\b',
        r'\b(\d{1,2}.\d{1,2}\s+on\s+\d{1,2}.\d{1,2}.\d{2,4})\b',
        r'\b(\d{1,2}:\d{2}[ap]m\s+on\s+\d{1,2}/\d{1,2}/\d{2,4})\b',
        r"(\d{1,2}.\d{2}[ap]m on \d{1,2}/\d{1,2}/\d{2,4})",
        r"(\d{1,2}.\d{2}[ap]m on \d{1,2}.\d{1,2}.\d{2,4})",
        r"(\d{1,2}.\d{1,2}.\d{2,4} at \d{1,2}.\d{2}[ap]m)",
        r"(\d{1,2}.\d{1,2}.\d{2,4} at \d{1,2}:\d{2}[ap]m)",
        r"(\d{1,2}/\d{1,2}/\d{2,4} at \d{1,2}.\d{2}[ap]m)",
        r"(\d{1,2}/\d{1,2}/\d{2,4} at \d{1,2}:\d{2}[ap]m)",
        r"(\d{2}:\d{2} on \d{2}/\d{2}/\d{2})",
        r"(\d{2}:\d{2} on the \d{2}/\d{2}/\d{2})",
        r"(\d{2}:\d{2}\s+[ap]m on the \d{2}/\d{2}/\d{2})",
    ]

    extracted_times = []
    
    time_hash = defaultdict(str)

    for pattern in formats:
        time_matches = re.finditer(pattern, article)
        
        for match in time_matches:
            time_str = match.group(0)
            converted_time = time_convert_to_iso_format(time_str)
            
            # if converted_time:
            start_index = match.start()
            end_index = match.end()
            ans_string =f"{file_name}\tTIME\t{start_index}\t{end_index}\t{time_str}\t{converted_time}\n"
            
            if str(start_index) not in time_hash:
                time_hash[str(start_index)] = ans_string
            else:
                if len(time_hash[str(start_index)]) < len(ans_string):
                    time_hash[str(start_index)] = ans_string
            
            # if ans_string not in extracted_times:
            #     extracted_times.append(ans_string)
    
    for key in time_hash:
        extracted_times.append(time_hash[key])
    
    return extracted_times

def date_convert_to_iso_format(date_str):
    date_str = date_str.replace("\n", "")
    formats = [
        "%d/%m/%Y",
        "%d/%m/%y",
        "%dth of %B %Y",
        "%d.%m.%y",
        "%Y-%m-%d",
        "%d/%m/%Yat",
        "%dst of %B %Y",
        "%d.%m.%y @",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            correct_dt = dt.strftime('%Y-%m-%d')
            
            year = correct_dt.split("-")[0]
            if year.startswith("19") and year not in date_str:
                year = "20" + year[2:]
                correct_dt = year + "-" + correct_dt.split("-")[1] + "-" + correct_dt.split("-")[2]
                
            
            return f"{correct_dt}"
        except ValueError:
            pass
    return None

def extract_dates_from_article(file_name, article_text):
    date_pattern = r'\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b'

    dates_found = [(match.group(), match.start()) for match in re.finditer(date_pattern, article_text)]

    converted_dates = []
    for date_str, start_index in dates_found:
        converted_date = date_convert_to_iso_format(date_str)
        if converted_date:
            converted_dates.append(f"{file_name}\tDATE\t{start_index}\t{start_index + len(date_str)}\t{date_str}\t{converted_date}\n")

    return converted_dates

def extract_phone_number(file_name, text):
    phone_number_pattern = r'\b\d{4} \d{4}\b'
    phone_numbers_with_indices = []
    for match in re.finditer(phone_number_pattern, text):
        phone_number = match.group(0)
        start_index = match.start()
        phone_numbers_with_indices.append(f"{file_name}\tPHONE\t{start_index}\t{start_index + len(phone_number)}\t{phone_number}\n")
    return phone_numbers_with_indices

def split_string(input_string):
    hyphen_index = input_string.find('-')

    if hyphen_index != -1:
        part1 = input_string[:hyphen_index].strip()
        part2 = input_string[hyphen_index + 1:].strip()
        return part1, part2
    else:
        return input_string.strip(), ""

def extract_DEPARTMENT_HOSPITAL(file_name, article):
    pattern = r'Location: .*'
    match = re.search(pattern, article)
    result = []
    if match:
        location_string = match.group(0)
        location_string = location_string.replace("Location: ", "").replace("\n", "")
        location_list = split_string(location_string)
        
        if len(location_list) == 2:
            department = location_list[0].strip()
            if department and len(department) > 0:
                department_start_index = article.find(department)
                department_string = f"{file_name}\tDEPARTMENT\t{department_start_index}\t{department_start_index+len(department)}\t{department}\n"
                result.append(department_string)
        
            hospital = location_list[1].strip()
            if hospital and len(hospital) > 0:
                hospital_start_index = article.find(hospital)
                hospital_string = f"{file_name}\tHOSPITAL\t{hospital_start_index}\t{hospital_start_index+len(hospital)}\t{hospital}\n"
                result.append(hospital_string)
        else:
            location_string = location_string.strip()
            if len(location_string)!=0 and location_string:
                hospital_start_index = article.find(location_string)
                hospital_string = f"{file_name}\tHOSPITAL\t{hospital_start_index}\t{hospital_start_index+len(location_string)}\t{location_string}\n"
                result.append(hospital_string)
                
    sentence_list = article.split("\n")
    for i, sentence in enumerate(sentence_list):
        if sentence.startswith("Site_name:"):
            hospital = sentence.replace("Site_name:", "").strip()
            if hospital and len(hospital) > 0:
                start_index = -1
                while True:
                    hospital_index = article.find(hospital, start_index + 1)
                    hospital_string = f"{file_name}\tHOSPITAL\t{hospital_index}\t{hospital_index+len(hospital)}\t{hospital}\n"
                    result.append(hospital_string)
                    if start_index == -1:
                        break
        elif sentence.startswith("SiteName"):
            hospital = sentence_list[i+1].strip()
            if hospital and len(hospital) > 0:
                start_index = -1
                while True:
                    hospital_index = article.find(hospital, start_index + 1)
                    hospital_string = f"{file_name}\tHOSPITAL\t{hospital_index}\t{hospital_index+len(hospital)}\t{hospital}\n"
                    result.append(hospital_string)
                    if start_index == -1:
                        break
            
    return result

def check_words_capitalization(input_string):
    words = input_string.split()
    for word in words:
        if not word[0].isupper():
            return False
    return True

def extract_patient(file_name, medicalrecord_list, article):
    medicalrecord = None
    if len(medicalrecord_list) >= 0:
        medicalrecord = medicalrecord_list[0]
    
    
    sentence_list = article.split("\n")
    result = []
    for i, sentence in enumerate(sentence_list):
        if sentence == "MiddleName" or sentence == "FirstName" or sentence == "LastName":
            patient = sentence_list[i+1].strip()
            if patient and len(patient) > 0:
                patient_index = article.find(patient)
                patient_string = f"{file_name}\tPATIENT\t{patient_index}\t{patient_index+len(patient)}\t{patient}\n"
                result.append(patient_string)
        if sentence == medicalrecord:
            while i < len(sentence_list):
                if sentence_list[i+1] != "":
                    patient = sentence_list[i+1].strip()
                    if patient == "SpecimenType":
                        break
                    
                    if patient and len(patient) > 0 and check_words_capitalization(patient):
                        patient_index = article.find(patient)
                        patient_string = f"{file_name}\tPATIENT\t{patient_index}\t{patient_index+len(patient)}\t{patient}\n"
                        result.append(patient_string)
                        break
                i += 1
        
    return result

def filter_capital_letters(input_string):
    filtered_string = ''.join(char for char in input_string if char.isupper())
    return filtered_string

def extract_location_other(file_name, article):
    result = []
    
    sentence_list = article.split("\n")
    
    for sentence in sentence_list:
        if filter_capital_letters(sentence).startswith("POBOX"):
            location_other_index = article.find(sentence)
            result.append(f"{file_name}\tLOCATION-OTHER\t{location_other_index}\t{location_other_index+len(sentence)}\t{sentence}\n")
    
    return result

def extract_street_city_state(file_name, article, start_idx, end_idx):
    street_city_state = article[start_idx:end_idx].strip()
    
    temp_list = street_city_state.split("\n")
    street_city_state_list = []
    result = []
    
    if len(temp_list) == 3:
        idnum_start_idx = start_idx
        if "," in temp_list[0]:
            idnum_start_idx += 1
        idnum = temp_list[0].strip().replace(",", "")
        
        result.append(f"{file_name}\tIDNUM\t{idnum_start_idx}\t{idnum_start_idx+len(idnum)}\t{idnum}\n")
        street_city_state_list+= [temp_list[1].strip()]
        street_city_state_list+= temp_list[-1].split("  ")
        
    if len(temp_list) == 2:
        street_city_state_list+= [temp_list[0].strip()]
        street_city_state_list+= temp_list[-1].split("  ")
        
    if len(temp_list) == 1:
        street_city_state_list+= temp_list[0].split("  ")
    
    
    if len(street_city_state_list) == 3:
        street = street_city_state_list[0].strip()
        city = street_city_state_list[1].strip()
        state = street_city_state_list[2].strip()
        
        if street and len(street) > 0:
            street_index = article.find(street)
            street_string = f"{file_name}\tSTREET\t{street_index}\t{street_index+len(street)}\t{street}\n"
            result.append(street_string)
        
        if city and len(city) > 0:
            city_index = article.find(city)
            city_string = f"{file_name}\tCITY\t{city_index}\t{city_index+len(city)}\t{city}\n"
            result.append(city_string)
        
        if state and len(state) > 0:
            state_index = article.find(state)
            state_string = f"{file_name}\tSTATE\t{state_index}\t{state_index+len(state)}\t{state}\n"
            result.append(state_string)
            
    if len(street_city_state_list) == 2:
        city = street_city_state_list[0].strip()
        state = street_city_state_list[1].strip()
        
        if city and len(city) > 0:
            city_index = article.find(city)
            city_string = f"{file_name}\tCITY\t{city_index}\t{city_index+len(city)}\t{city}\n"
            result.append(city_string)
        
        if state and len(state) > 0:
            state_index = article.find(state)
            state_string = f"{file_name}\tSTATE\t{state_index}\t{state_index+len(state)}\t{state}\n"
            result.append(state_string)
            
    return result
    
def extract_organization(file_name, article):
    pattern_1 = r'Performed at ([\w\s.]+?), ([\w\s.]+?),'

    sentence_list = article.split("\n")
    index = 0
    result = []
    
    for i, sentence in enumerate(sentence_list):
        match_1 = re.search(pattern_1, sentence)
        if match_1:
            org = match_1.group(1)
            
            if org.isupper() or "Pathology" in org:
                org_index = sentence.find(org) + index
                org_string = f"{file_name}\tDEPARTMENT\t{org_index}\t{org_index+len(org)}\t{org}\n"
                result.append(org_string)
            else:
                org_index = sentence.find(org) + index
                org_string = f"{file_name}\tORGANIZATION\t{org_index}\t{org_index+len(org)}\t{org}\n"
                result.append(org_string)
                
            temp = match_1.group(2)
            if "hospital" in temp.lower():
                hospital = temp.replace("\n", "").replace("Hospital", "").strip()
                hospital_index = sentence.find(hospital) + index
                hospital_string = f"{file_name}\tHOSPITAL\t{hospital_index}\t{hospital_index+len(hospital)}\t{hospital}\n"
                result.append(hospital_string)
            
            
        index += len(sentence) + 1

    pattern_2 = r'Source of material:\s*([a-zA-Z]+\s*[a-zA-Z\s]*)'

    match = re.search(pattern_2, article)

    if match:
        start_index = match.start(1)
        org = match.group(1).strip()
        org_string = f"{file_name}\tORGANIZATION\t{start_index}\t{start_index+len(org)}\t{org}\n"
        result.append(org_string)

    return result

def extract_duration(file_name, sentence):
    duration_pattern = r'\b(\d+)\s*(hours?|hrs?|minutes?|mins?|days?|weeks?|months?|years?)\b'
    durations_found = re.findall(duration_pattern, sentence, re.IGNORECASE)

    converted_durations = []
    for duration, unit in durations_found:
        origin_duration = f"{duration} {unit}"
        if unit.lower().startswith('hour'):
            converted_durations.append((origin_duration, f'P{duration}H'))
        elif unit.lower().startswith('minute'):
            converted_durations.append((origin_duration, f'PT{duration}M'))
        elif unit.lower().startswith('day'):
            converted_durations.append((origin_duration, f'P{duration}D'))
        elif unit.lower().startswith('week') or unit.lower().startswith('wk'):
            converted_durations.append((origin_duration, f'P{duration}W'))
        elif unit.lower().startswith('month'):
            converted_durations.append((origin_duration, f'P{duration}M'))
        elif unit.lower().startswith('year') or unit.lower().startswith('yr'):
            converted_durations.append((origin_duration, f'P{duration}Y'))
    
    result = []
    
    for duration, converted_duration in converted_durations:
        duration_index = sentence.find(duration)
        duration_string = f"{file_name}\tDURATION\t{duration_index}\t{duration_index+len(duration)}\t{duration}\t{converted_duration}\n"
        result.append(duration_string)
            
    return result

def extract_set(file_name, sentence):
    pattern = r'tested (\w*) with'
    
    matches = re.finditer(pattern, sentence)
    result = []
    for match in matches:
        set_name = match.group(1)
        set_name_index = match.start(1)
        set_string = f"{file_name}\tSET\t{set_name_index}\t{set_name_index+len(set_name)}\t{set_name}\n"
        result.append(set_string)
        
    return result

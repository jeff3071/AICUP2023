from datasets import Dataset, ClassLabel, Sequence, Features, Value, DatasetDict
from collections import defaultdict
import glob

with open('./data/First_Phase_Release/answer.txt', 'r', encoding='utf-8-sig') as f:
    answers = f.read().splitlines()

with open('./data/Second_Phase_Dataset/answer.txt', 'r', encoding='utf-8-sig') as f:
    answers += f.read().splitlines()

with open('./data/Validation_Dataset_Answer/answer.txt', 'r', encoding='utf-8-sig') as f:
    answers += f.read().splitlines()

data_dict = {}
label_dict = defaultdict(list)
class_label = ['O']

filter_label = [
    'DOCTOR',
    'DATE',
    'IDNUM',
    'HOSPITAL',
    'MEDICALRECORD',
    'PATIENT',
    'TIME',
    'DEPARTMENT',
    'CITY',
    'ZIP',
    'STREET',
    'STATE',
    'AGE',
    'ORGANIZATION'
]


for answer in answers:
    line = answer.split("\t")
    
    if line[1] in filter_label:
        label_dict[line[0]].append([line[1], line[4]])
        if f"B-{line[1]}" not in class_label:
            class_label.append(f"B-{line[1]}")
            class_label.append(f"I-{line[1]}")
    
def create_ner_dataset(file_content, label_data):
    labels = {}

    for label_pair in label_data:
        label_type, label_value = label_pair
        labels[label_type] = label_value
    lines = file_content.split('\n')
    
    file_token = []
    file_annotation = []
    
    for line in lines:
        line = line.strip()
        if line:
            tokens = line.split()
            annotations = []
            for token in tokens:
                annotation = class_label.index('O')
                for label_type, label_value in labels.items():
                    if label_value in token:
                        annotation = class_label.index(f"B-{label_type}") 
                        break
                annotations.append(annotation)

            file_token.extend(tokens)
            file_annotation.extend(annotations)

    if len(file_annotation) != len(file_token):
        assert False, "Length of annotation and token is not equal"
    return file_token, file_annotation


def create_dataset(paths):
    file_list = []
    for path in paths:
        file_list += glob.glob(path + '*')

    ids = []
    tokens_list = []
    ner_tags_list = []

    for file in file_list:
        idx = file.split('/')[-1].split('.')[0]
        with open(file, 'r', encoding='utf-8-sig') as f:
            data = f.read()
        tokens, ner_tags = create_ner_dataset(data, label_dict[idx])
        ids.append(idx)
        tokens_list.append(tokens)
        ner_tags_list.append(ner_tags)

    data_dict = {
        'tokens': tokens_list,
        'ner_tags': ner_tags_list,
    }
    
    tags = ClassLabel(num_classes=len(class_label), names=class_label)
    
    dataset_structure = {"ner_tags":Sequence(tags),
                 'tokens': Sequence(feature=Value(dtype='string'))}
    
    return Dataset.from_dict(mapping=data_dict, features=Features(dataset_structure))


def get_train_dataset():
    train_folder_path = ["./data/First_Phase_Release/First_Phase_Text_Dataset/", "./data/Second_Phase_Dataset/Second_Phase_Text_Dataset/"]
    val_folder_path = ["./data/First_Phase_Release/Validation_Release/"]

    train_dataset = create_dataset(train_folder_path)
    val_dataset = create_dataset(val_folder_path)

    raw_datasets = DatasetDict({'train': train_dataset, 'validation': val_dataset})
    return raw_datasets

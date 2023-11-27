from collections import defaultdict
from tabulate import tabulate

def calculate_precision_recall_f1(predict_list, answer_list):
    true_positives = 0
    false_positives = 0
    false_negatives = 0
            
    for predict in predict_list:
        if predict in answer_list:
            true_positives += 1
        else:
            false_positives += 1

    false_negatives = len(answer_list) - true_positives  # Calculate false negatives based on missed predictions

    precision = true_positives / (true_positives + false_positives + 1e-10)  # Adding a small epsilon to avoid division by zero
    recall = true_positives / (true_positives + false_negatives + 1e-10)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-10)

    return precision, recall, f1

answer_path = "./data/Validation_Dataset_Answer/answer.txt"
predict_path = "./temp.txt"

with open(answer_path, 'r', encoding='utf-8-sig') as f:
    answers = f.read().splitlines()

with open(predict_path, 'r', encoding='utf-8-sig') as f:
    predict = f.read().splitlines()

predict_elements = []
predict_dict = defaultdict(list)
convert_iso_pred = defaultdict(list)

for line in predict:
    element = line.split('\t')
    pred = f"{element[0]}\t{element[1]}\t{element[2]}\t{element[3]}"
    if pred not in predict_elements:
        predict_elements.append(pred)
        
    predict_type = element[1]
    pred_value = f"{element[0]}\t{element[2]}\t{element[3]}"
    if pred_value not in predict_dict[predict_type]:
        predict_dict[predict_type].append(pred_value)
    
    if predict_type in ["TIME", "DATE", "DURATION"] and pred_value not in convert_iso_pred[predict_type]:
        if len(element) == 6:
            convert_iso_pred[predict_type].append(f"{element[0]}\t{element[-2]}\t{element[-1]}")

answers_elements = []
answers_dict = defaultdict(list)

convert_iso_answer = defaultdict(list)

for line in answers:
    element = line.split('\t')
    answers_elements.append(f"{element[0]}\t{element[1]}\t{element[2]}\t{element[3]}")
    
    answer_type = element[1]
    answer_value = f"{element[0]}\t{element[2]}\t{element[3]}"
    if answer_value not in answers_dict[answer_type]:
        answers_dict[answer_type].append(answer_value)
        
    if answer_type in ["TIME", "DATE", "DURATION"] and answer_value not in convert_iso_answer[answer_type]:
        convert_iso_answer[answer_type].append(f"{element[0]}\t{element[-2]}\t{element[-1]}")


precision, recall, f1 = calculate_precision_recall_f1(predict_elements, answers_elements)


print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")


all_type = list(set(predict_dict.keys()) | set(answers_dict.keys()))

table_header = [
        "Type",
        "precision",
        "recall",
        "f1",
    ]

eval_res = []

acculmulate_precision = 0
acculmulate_recall = 0
acculmulate_f1 = 0

for t in all_type:
    pred_list = predict_dict[t]
    answer_list = answers_dict[t]
    precision, recall, f1 = calculate_precision_recall_f1(pred_list, answer_list)
    eval_res.append([t, precision, recall, f1])
    
    acculmulate_precision += precision
    acculmulate_recall += recall
    acculmulate_f1 += f1
    
eval_res.append(["Macro", acculmulate_precision/len(all_type), acculmulate_recall/len(all_type), acculmulate_f1/len(all_type)])

print(tabulate(eval_res, headers=table_header, tablefmt="github"))

iso_type = ["TIME", "DATE", "DURATION"]

iso_acculmulate_precision = 0
iso_acculmulate_recall = 0
iso_acculmulate_f1 = 0

iso_eval_res = []

for t in iso_type:
    pred_list = convert_iso_pred[t]
    answer_list = convert_iso_answer[t]
    precision, recall, f1 = calculate_precision_recall_f1(pred_list, answer_list)
    iso_eval_res.append([t, precision, recall, f1])
    
    iso_acculmulate_precision += precision
    iso_acculmulate_recall += recall
    iso_acculmulate_f1 += f1

iso_eval_res.append(["Macro", iso_acculmulate_precision/len(iso_type), iso_acculmulate_recall/len(iso_type), iso_acculmulate_f1/len(iso_type)])
print(tabulate(iso_eval_res, headers=table_header, tablefmt="github"))

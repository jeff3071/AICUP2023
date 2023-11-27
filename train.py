from data import get_train_dataset
from transformers import AutoTokenizer, DataCollatorForTokenClassification, AutoModelForTokenClassification, TrainingArguments, Trainer
import evaluate
import numpy as np
from argparse import ArgumentParser, Namespace

def compute_metrics(eval_preds):
    logits, labels = eval_preds
    predictions = np.argmax(logits, axis=-1)

    true_labels = [[label_names[l] for l in label if l != -100] for label in labels]
    true_predictions = [
        [label_names[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    all_metrics = metric.compute(predictions=true_predictions, references=true_labels, zero_division=0, mode="strict", scheme="IOB2")
    return {
        "precision": all_metrics["overall_precision"],
        "recall": all_metrics["overall_recall"],
        "f1": all_metrics["overall_f1"]
    }

def align_labels_with_tokens(labels, word_ids):
    new_labels = []
    current_word = None
    for word_id in word_ids:
        if word_id != current_word:
            current_word = word_id
            label = -100 if word_id is None else labels[word_id]
            new_labels.append(label)
        elif word_id is None:
            new_labels.append(-100)
        else:
            label = labels[word_id]
            # If the label is B-XXX we change it to I-XXX
            if label % 2 == 1:
                label += 1
            new_labels.append(label)

    return new_labels

def tokenize_and_align_labels(examples, window_size=128, overlap=32):
    tokenized_inputs_list = []
    all_labels_list = []

    for i, example in enumerate(examples["tokens"]):
        tokens = example
        labels = examples["ner_tags"][i]

        for j in range(0, len(tokens), overlap):
            window_tokens = tokens[j:j + window_size]
            window_labels = labels[j:j + window_size]

            tokenized_inputs = tokenizer(
                window_tokens,
                is_split_into_words=True,
                padding="max_length",
                truncation=True
            )

            word_ids = tokenized_inputs.word_ids(0)
            new_labels = align_labels_with_tokens(window_labels, word_ids)

            tokenized_inputs["labels"] = new_labels

            tokenized_inputs_list.append(tokenized_inputs)
            all_labels_list.append(new_labels)

    return {
        "input_ids": [item["input_ids"] for item in tokenized_inputs_list],
        "attention_mask": [item["attention_mask"] for item in tokenized_inputs_list],
        "labels": all_labels_list,
    }



if __name__ == "__main__":
    raw_datasets = get_train_dataset()
    label_names = raw_datasets["train"].features["ner_tags"].feature.names
    model_checkpoint = "bert-base-cased"
    exp_name = "bert_finetuned_ner"
    
    tokenizer = AutoTokenizer.from_pretrained(model_checkpoint, use_fast=True)
    tokenized_datasets = raw_datasets.map(
        tokenize_and_align_labels,
        batched=True,
        remove_columns=raw_datasets["train"].column_names,
    )
    data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

    metric = evaluate.load("seqeval")
    
    id2label = {i: label for i, label in enumerate(label_names)}
    label2id = {v: k for k, v in id2label.items()}
    
    model = AutoModelForTokenClassification.from_pretrained(
        model_checkpoint,
        id2label=id2label,
        label2id=label2id
    )
    
    train_args = TrainingArguments(
        exp_name,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        num_train_epochs=3,
        weight_decay=0.01,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=8,
        fp16=True,
    )
    
    trainer = Trainer(
        model=model,
        args=train_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        tokenizer=tokenizer,
    )
    

    trainer.train()
    
    # if c_args.do_eval:
    #     trainer.evaluate()
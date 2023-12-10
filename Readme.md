# AICUP 2023 - Electronic Medical Record PHI Extraction

## Environment

- OS: Ubuntu 20.04
- Python 3.8.5
- GPU: RTX 3060

## Install

We use [Poetry](https://python-poetry.org/) to manage dependencies.

```bash
poetry init
poetry install
```

We also provide a `requirements.txt` file for those who prefer to use `pip`.

```bash
pip install -r requirements.txt
```

## Data Preparation

Put the data in the `data` folder.
```
data
├── First_Phase_Release
│   ├── First_Phase_Text_Dataset
│   ├── Validation_Release
│   └── answer.txt
├── Second_Phase_Dataset
│   ├── Second_Phase_Text_Dataset
│   └── answer.txt
└── Validation_Dataset_Answer
    └── answer.txt
```

## Training

We use `bert-base-cased` as the pretrained model.

```bash
python train.py
```

The model will be saved in the `bert_finetuned_ner` folder.

```
bert_finetuned_ner
├── checkpoint_12873
├── checkpoint_4291
└── checkpoint_8583
```

You can also download the pretrained model from [here](https://drive.google.com/drive/folders/1_jzEAjbZou-B-9bUfFasIk4kCfLOk2NB?usp=sharing).
> Please put the pretrained model in the `bert_finetuned_ner` folder.

## Inference

```bash
python predict.py
```

The prediction will be `temp.txt`.

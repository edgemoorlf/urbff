# RLHF Reward Model Training - End-to-End (Hugging Face TRL)

# ✅ Step 0: Install dependencies
#!pip install trl transformers datasets accelerate -q
# transformers==4.36.2 
# trl==0.7.4
# peft=0.13.2
# accelerate=0.29.0
# ✅ Step 1: Load human preference dataset (JSONL format)
from datasets import load_dataset
import pandas as pd

# Example JSONL format (can be replaced with your file)
# {"prompt": "你今天想我了吗？", "completion_1": "当然想了啊，怎么可能不想你？", "completion_2": "我今天很忙，没时间想这个。", "preferred": 1}

# Save example data to disk (for demonstration)
data = [
    {"prompt": "你今天想我了吗？", "completion_1": "当然想了啊，怎么可能不想你？", "completion_2": "我今天很忙，没时间想这个。", "preferred": 1},
    {"prompt": "你喜欢我什么？", "completion_1": "你很温柔体贴", "completion_2": "不知道，没认真想过。", "preferred": 1},
    {"prompt": "晚上想一起吃饭吗？", "completion_1": "不行，我很忙", "completion_2": "当然啊，我很期待见你", "preferred": 2},
]
import json
with open("human_prefs.jsonl", "w", encoding="utf-8") as f:
    for item in data:
        json.dump(item, f, ensure_ascii=False)
        f.write("\n")

# Load with Hugging Face Datasets
dataset = load_dataset("json", data_files="human_prefs.jsonl")['train']

# ✅ Step 2: Preprocess - tokenize prompt + response pairs
from transformers import AutoTokenizer

model_name = "hfl/chinese-roberta-wwm-ext"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def preprocess(example):
    preferred = example['preferred']
    pair1 = f"用户：{example['prompt']}\n助手：{example['completion_1']}"
    pair2 = f"用户：{example['prompt']}\n助手：{example['completion_2']}"

    chosen = pair1 if preferred == 1 else pair2
    rejected = pair2 if preferred == 1 else pair1

    chosen_enc = tokenizer(chosen, truncation=True, padding='max_length', max_length=128)
    rejected_enc = tokenizer(rejected, truncation=True, padding='max_length', max_length=128)

    return {
        "input_ids_chosen": chosen_enc["input_ids"],
        "attention_mask_chosen": chosen_enc["attention_mask"],
        "input_ids_rejected": rejected_enc["input_ids"],
        "attention_mask_rejected": rejected_enc["attention_mask"],
    }

processed = dataset.map(preprocess, remove_columns=dataset.column_names)

# ✅ Step 3: Train reward model using TRL RewardTrainer
from transformers import AutoModelForSequenceClassification
from trl import RewardTrainer, RewardConfig

reward_model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=1)

training_args = RewardConfig(
    output_dir="./reward_model",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    gradient_accumulation_steps=2,
    learning_rate=1e-5,
    remove_unused_columns=False,
    logging_steps=1,
    evaluation_strategy="no",
    max_length=128
)

trainer = RewardTrainer(
    model=reward_model,
    args=training_args,
    tokenizer=tokenizer,
    train_dataset=processed
)

trainer.train()
trainer.save_model()  # 保存模型到 output_dir
tokenizer.save_pretrained(training_args.output_dir)  # 保存分词器

# ✅ Step 4: Use the trained reward model to score responses
import torch

def score(prompt, response):
    # 编码输入
    text = f"用户：{prompt}\n助手：{response}"
    inputs = tokenizer(text, truncation=True, padding=True, return_tensors="pt")
    
    # 关键修复：将输入数据移动到模型所在设备
    inputs = {k: v.to(reward_model.device) for k, v in inputs.items()}  # [4,5,7,9](@ref)
    
    with torch.no_grad():
        outputs = reward_model(**inputs)
        score = outputs.logits[0].item()
    return score

# Example
print("Score:", score("你今天想我了吗？", "当然想了啊，怎么可能不想你？"))
print("Score:", score("你今天想我了吗？", "想得快疯了"))
print("Score:", score("你今天想我了吗？", "你谁啊？"))
print("Score:", score("你今天想我了吗？", "为什么要想你？"))
print("Score:", score("你今天想我了吗？", "滚一边去"))
print("Score:", score("你今天想我了吗？", "滚"))

device = "cuda" if torch.cuda.is_available() else "cpu"

from modelscope import AutoModelForCausalLM, AutoTokenizer
gen_tokenizer = AutoTokenizer.from_pretrained("LLM-Research/gemma-3-27b-it")
gen_model = AutoModelForCausalLM.from_pretrained("LLM-Research/gemma-3-27b-it").to(device)


def generate(prompt, num_return_sequences=4):
    inputs = gen_tokenizer(prompt, return_tensors="pt").to(device)
    outputs = gen_model.generate(
        **inputs,
        max_new_tokens=50,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        num_return_sequences=num_return_sequences,
        temperature=0.7,
    )
    return [gen_tokenizer.decode(o, skip_special_tokens=True).replace(prompt, "") for o in outputs]

# ✅ Step 4: Load Reward Model
from transformers import AutoModelForSequenceClassification

# reward_model = AutoModelForSequenceClassification.from_pretrained("./reward_model").to(device)
reward_model.eval()
# reward_tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

# ✅ Step 5: GRPO Filtering: Select Top Responses
prompts = ["你今天想我了吗？", "你觉得我漂亮吗？", "今晚能不能陪我？"]
filtered_dataset = []

for prompt in prompts:
    candidates = generate(prompt, 4)
    scored = [(resp, score(prompt, resp)) for resp in candidates]
    best = max(scored, key=lambda x: x[1])[0]
    filtered_dataset.append({"prompt": prompt, "response": best})

with open("grpo_sft_dataset.jsonl", "w", encoding="utf-8") as f:
    for item in filtered_dataset:
        json.dump(item, f, ensure_ascii=False)
        f.write("\n")

# ✅ Step 6: SFT Training on Filtered Dataset
from datasets import load_dataset
from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling

dataset = load_dataset("json", data_files="grpo_sft_dataset.jsonl")['train']

def tokenize(example):
    text = f"用户：{example['prompt']}\n助手：{example['response']}"
    return gen_tokenizer(text, truncation=True, padding="max_length", max_length=256)

tokenized = dataset.map(tokenize)

args = TrainingArguments(
    output_dir="./finetuned-chatbot",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    learning_rate=5e-5,
    logging_steps=5,
    save_steps=100,
)

trainer = Trainer(
    model=gen_model,
    args=args,
    tokenizer=gen_tokenizer,
    train_dataset=tokenized,
    data_collator=DataCollatorForLanguageModeling(gen_tokenizer, mlm=False)
)

trainer.train()

# ✅ Step 7: Inference After GRPO-SFT
def chat(prompt):
    inputs = gen_tokenizer(f"用户：{prompt}\n助手：", return_tensors="pt").to(device)
    output = gen_model.generate(**inputs, max_new_tokens=50)
    return gen_tokenizer.decode(output[0], skip_special_tokens=True).replace(f"用户：{prompt}\n助手：", "")

print("Chatbot:", chat("你会永远陪着我吗？"))


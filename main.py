import warnings
warnings.filterwarnings("ignore")

import argparse
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM, SFTConfig
from transformers import TrainingArguments
from get_model import *
from get_data import *
import time
import requests


from huggingface_hub.hf_api import HfFolder
HfFolder.save_token('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')

def print_number_of_trainable_model_parameters(model):
    trainable_model_params = 0
    all_model_params = 0
    for _, param in model.named_parameters():
        all_model_params += param.numel()
        if param.requires_grad:
            trainable_model_params += param.numel()
    return f"trainable model parameters: {trainable_model_params}\nall model parameters: {all_model_params}\npercentage of trainable model parameters: {100 * trainable_model_params / all_model_params:.2f}%"


def main(args):
    tokenizer, model  = get_model(args.model_id)
    data = get_data_final()
    
    data = Dataset.from_pandas(data)
    
    training_output_dir = f'./JAIS_original_training-{str(int(time.time()))}'

    print("Number of parameters: ", print_number_of_trainable_model_parameters(model), flush=True)
    
    training_params = TrainingArguments(
    output_dir=training_output_dir,
    save_strategy="steps",
    auto_find_batch_size=True,
    max_steps = -1,
    num_train_epochs=args.epochs,
    save_steps=1,
    logging_steps=500,
    learning_rate=1e-4,
    push_to_hub = True,
    hub_model_id = f"{args.model_id.split('/')[1]}-arabic-text-summarizer",
    push_to_hub_model_id = f"{args.model_id.split('/')[1]}-arabic-text-summarizer"
    )
    
    response_template = """
    ###
        التلخيص:   
        """
    collator = DataCollatorForCompletionOnlyLM(response_template, tokenizer=tokenizer)
    
    
    trainer = SFTTrainer(
    model,
    train_dataset=data,
    formatting_func=preprocess_dataset,
    data_collator=collator,
    )
    
    trainer.train()
    trainer.save_model(f"./{args.model_id.split('/')[1]}")
    trainer.save_tokenzer(f"./{args.model_id.split('/')[1]}")
    
    trainer.push_to_hub(f"omaratef3221/{args.model_id.split('/')[1]}-arabic-text-summarizer")
    
    requests.post("https://ntfy.sh/master_experiment1", data="Experiment 1 Done ".encode(encoding='utf-8'))
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_id", type=str)
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    main(args)
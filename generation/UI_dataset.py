import os
import datasets

# Load the dataset from Hugging Face
dataset = datasets.load_dataset("smirki/UI_REASONING_v1.01", split="train")

# Define the directory where you want to save the dataset
save_dir = "UIdataset"  # Replace with your desired folder path
os.makedirs(save_dir, exist_ok=True)  # Create the folder if it doesn't exist

# Save the dataset as a CSV file
dataset.to_csv(os.path.join(save_dir, "UI_REASONING_train.csv"))

# Alternatively, save the dataset as a JSON file
# dataset.to_json(os.path.join(save_dir, "UI_REASONING_train.json"))

print(f"Dataset saved in: {save_dir}")

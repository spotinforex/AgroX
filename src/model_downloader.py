from huggingface_hub import hf_hub_download


if __name__ == "__main__":
    model_path = hf_hub_download(
        repo_id="sentence-transformers/all-MiniLM-L6-v2",
        filename="config.json")
    print("Any model file path:", model_path)
    








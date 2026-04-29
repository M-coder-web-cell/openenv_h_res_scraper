from huggingface_hub import HfApi, list_spaces
from pathlib import Path
from python_dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

root = Path.cwd() 
base = 'https://huggingface.co/spaces/openenv-community'

hf_api = HfApi(
    endpoint="https://huggingface.co", 
    token=os.getenv("HF_TOKEN"), 
)

spaces = hf_api.list_spaces(filter = ["openenv"], limit = 10)
spaces_id = []
for space in spaces:
    spaces_id.append(space.id)

#EXTRACT THE READMES AND STORE THEM UNDER THE DATA FOLDER FOR FUTURE PROCESSING
root = Path(__file__).resolve().parent
data_folder = root / "data"

for spaceid in spaces_id:
    downloaded_path = hf_api.hf_hub_download(repo_id = spaceid, repo_type="space", filename = "README.md", local_dir = data_folder)
    dst_safe_name = spaceid.replace("/", "_") + ".md"
    dst = data_folder / dst_safe_name 
    Path(downloaded_path).replace(dst)

    

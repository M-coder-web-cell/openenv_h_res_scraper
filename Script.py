from huggingface_hub import HfApi, list_spaces
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
import os

load_dotenv()

root = Path.cwd() 
base = 'https://huggingface.co/spaces/openenv-community'

hf_api = HfApi(
    endpoint="https://huggingface.co", 
    token=os.getenv("HF_TOKEN"), 
)

spaces = hf_api.list_spaces(filter = ["openenv"], limit = 4)

spaces_id = []

threshold_date = datetime(2026, 3, 15, tzinfo=timezone.utc)
hack_finals_date = datetime(2026, 4, 24, tzinfo= timezone.utc)
for space in spaces:
    #fetch all repos spaces created after 15th march
    if(space.created_at > threshold_date and space.last_modified > hack_finals_date):
        spaces_id.append(space.id)

#EXTRACT THE READMES AND STORE THEM UNDER THE DATA FOLDER FOR FUTURE PROCESSING
root = Path(__file__).resolve().parent
data_folder = root / "data"

for spaceid in spaces_id:
    downloaded_path = hf_api.hf_hub_download(repo_id = spaceid, repo_type="space", filename = "README.md", local_dir = data_folder)
    dst_safe_name = spaceid.replace("/", "_") + ".md"
    dst = data_folder / dst_safe_name 
    Path(downloaded_path).replace(dst)


for file_path in data_folder.glob("*.md"):
    with open(file_path, 'r', encoding='utf-8') as f:
        readme_content

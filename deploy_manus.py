import os
import requests
import zipfile
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

API_KEY = os.getenv("MANUS_API_KEY")
APP_NAME = os.getenv("MANUS_APP_NAME")

ZIP_NAME = "deploy_bundle.zip"

def zip_repo():
    with zipfile.ZipFile(ZIP_NAME, "w") as z:
        for root, _, files in os.walk("."):
            for f in files:
                path = os.path.join(root, f)

                # Skip .git, __pycache__, and the zip file itself
                if ".git" in path or "__pycache__" in path or path.endswith(ZIP_NAME):
                    continue

                z.write(path)

def deploy():
    if not API_KEY or not APP_NAME:
        print("ERROR: MANUS_API_KEY or MANUS_APP_NAME not set in environment.")
        return

    url = f"https://manus.space/api/apps/{APP_NAME}/deploy"

    with open(ZIP_NAME, "rb") as f:
        files = {"file": f}

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        try:
            r = requests.post(url, headers=headers, files=files)
            print("STATUS:", r.status_code)
            print("RESPONSE:", r.text)
        except Exception as e:
            print(f"ERROR: Deployment failed: {e}")

if __name__ == "__main__":
    print("Zipping repo...")
    zip_repo()

    print("Deploying to Manus...")
    deploy()

    print("DONE.")

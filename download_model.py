import os
import urllib.request

# Create models directory
# os.makedirs('models', exist_ok=True)

BASE_URL = "https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights"

models = [
    # "tiny_face_detector_model-weights_manifest.json",
    # "tiny_face_detector_model-shard1",
    # "face_landmark_68_model-weights_manifest.json",
    # "face_landmark_68_model-shard1",
    # "face_recognition_model-weights_manifest.json",
    # "face_recognition_model-shard1",
    # "ssd_mobilenetv1_model-weights_manifest.json",
    # "ssd_mobilenetv1_model-shard1",
    # "ssd_mobilenetv1_model-shard2",

    "age_gender_model-weights_manifest.json",
    "age_gender_model-shard1",
    "age_gender_model-shard2"
]

print("Downloading face-api models...")
for model in models:
    url = f"{BASE_URL}/{model}"
    file_path = f"models/{model}"
    
    try:
        print(f"Downloading {model}...", end=" ")
        urllib.request.urlretrieve(url, file_path)
        print("✓ Done")
    except Exception as e:
        print(f"✗ Failed: {e}")

print("\nAll models downloaded successfully!")
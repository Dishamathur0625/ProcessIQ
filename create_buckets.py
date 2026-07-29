import os
from supabase import create_client

# Load variables from .env
from dotenv import load_dotenv
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in your .env file.")
    exit(1)

print("Connecting to Supabase Storage...")
supabase = create_client(url, key)

buckets = [
    "datasets",
    "processed",
    "models",
    "reports",
    "artifacts",
    "visualizations",
    "manifests"
]

for bucket in buckets:
    try:
        # Check if bucket already exists
        supabase.storage.get_bucket(bucket)
        print(f"✅ Bucket '{bucket}' already exists.")
    except Exception:
        # If it does not exist, create it as a public bucket
        try:
            supabase.storage.create_bucket(bucket, options={"public": True})
            print(f"➕ Successfully created bucket '{bucket}'.")
        except Exception as e:
            print(f"❌ Failed to create bucket '{bucket}': {e}")

print("\nDone!")

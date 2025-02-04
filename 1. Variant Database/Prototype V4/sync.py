import os
import hashlib
import json
from datetime import datetime # Timestamps for metadata 

# Calculate MD5 hash of a file
def calculate_file_hash(filepath):
    # MD5 hash detects changes 
    hasher = hashlib.md5() # Calculates the MD5 hash of a file's contect - uniquely identify state
    with open(filepath, 'rb') as file: # 'rb' = reading in binary mode 
        while chunk := file.read(8192): # Reads file in chunks of 8KB
            hasher.update(chunk)
    return hasher.hexdigest()

# Loads metadata to track state of files (including: hash, version, last updated)
def load_metadata(metadata_file):
    # Reads metadata from JSON file to Python dictionary, if JSON file doesn't exist, returns empty dictionary
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return {}

# Makes sure metadata changes, writes it back to JSON file after updating
def save_metadata(metadata, metadata_file):
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=4) 

# Sync files between shared and local drives 
def sync_files(shared_path, local_path, shared_metadata, local_metadata):
    # Compares hash of each file in the shared with the local 
    # Identifies the out of sync files 
    # If file is missing/hash differs, marked for update
    for file, shared_meta in shared_metadata.items():
        shared_file = os.path.join(shared_path, file)
        local_file = os.path.join(local_path, file)

        if file not in local_metadata or local_metadata[file]['hash'] != shared_meta['hash']:
            print(f"Updating file: {file}")
            os.makedirs(os.path.dirname(local_file), exist_ok=True) # Checks if file exists 
            # Copy file from shared to local
            with open(shared_file, 'rb') as src, open(local_file, 'wb') as dest:
                dest.write(src.read())
            # Update local metadata
            local_metadata[file] = {
                "version": shared_meta["version"],
                "hash": calculate_file_hash(local_file),
                "last_updated": datetime.now().isoformat()
            }

    # Save updated metadata
    return local_metadata

# Checks for out of sync data between shared and local drive 
def check_out_of_sync(shared_metadata, local_metadata):
    # Any missing files/mismatched hashses 
    out_of_sync = [] # List of out of sync data 
    for file, shared_meta in shared_metadata.items():
        if file not in local_metadata or local_metadata[file]["hash"] != shared_meta["hash"]:
            out_of_sync.append(file)
    return out_of_sync # Returns a list of file paths that need to be synced 

# Updates metadata of a single file after the file is modified 
def update_file_metadata(filepath, metadata_file):
    # Ensures metadata reflects the latest state of a file after modificatoins 
    # Increments file's version and updates hash + timestamp
    metadata = load_metadata(metadata_file)
    file_hash = calculate_file_hash(filepath)
    file_relpath = os.path.relpath(filepath, os.path.dirname(metadata_file))
    
    if file_relpath in metadata:
        metadata[file_relpath]["version"] += 1
        metadata[file_relpath]["hash"] = file_hash
        metadata[file_relpath]["last_updated"] = datetime.now().isoformat()
    else:
        metadata[file_relpath] = {
            "version": 1,
            "hash": file_hash,
            "last_updated": datetime.now().isoformat()
        }
    save_metadata(metadata, metadata_file)
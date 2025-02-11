import os
import shutil

# Define paths
LOCAL_DRIVE = "Mock_Local_Drive"
SHARED_DRIVE = "Mock_Shared_Drive"
EXTERNAL_DRIVE = os.path.join(SHARED_DRIVE, "External_Drive")
INTERNAL_DRIVE = os.path.join(SHARED_DRIVE, "Internal_Drive")
RESEARCH_DRIVE = os.path.join(SHARED_DRIVE, "Research_Drive")

# Simulate user login
def get_user():
    user = input("Enter username (User1/User2): ").strip()
    if user not in ["User1", "User2"]:
        print("Invalid user. Exiting...")
        exit()
    return user

# Function to copy files from External to Internal Drive
def copy_files(source, destination):
    if not os.path.exists(source):
        print(f"Source {source} does not exist.")
        return
    
    if not os.path.exists(destination):
        os.makedirs(destination)  # Create if not exists

    for file_name in os.listdir(source):
        source_path = os.path.join(source, file_name)
        dest_path = os.path.join(destination, file_name)

        if os.path.isfile(source_path):
            shutil.copy2(source_path, dest_path)
            print(f"Copied: {file_name} -> {destination}")

# Function for User 1
def user1_process():
    print("User 1 detected. Copying files from External_Drive to Internal_Drive...")
    copy_files(EXTERNAL_DRIVE, INTERNAL_DRIVE)

# Function for User 2
def user2_process():
    print("User 2 detected. Accessing files from Internal_Drive...")
    if not os.path.exists(INTERNAL_DRIVE) or not os.listdir(INTERNAL_DRIVE):
        print("No files found in Internal_Drive. User 1 may not have copied them yet.")
        return
    
    print("Files available in Internal_Drive:")
    for file_name in os.listdir(INTERNAL_DRIVE):
        print(f"- {file_name}")

# Main execution
if __name__ == "__main__":
    user = get_user()
    if user == "User1":
        user1_process()
    elif user == "User2":
        user2_process()

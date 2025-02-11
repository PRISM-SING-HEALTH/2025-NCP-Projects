import os
import shutil
import yaml



def sync_files_to_common_folder(config_path):
    """
    Synchronises files from restricted source folders to a shared destination folder.

    Features:
    ---------
    - Copies files from two private source folders (Folder_A and Folder_B) 
      to a common shared folder (Folder_C).
    - Reads folder paths from a YAML configuration file.
    - Ensures the shared folder (Folder_C) exists before copying files.
    - Skips missing or inaccessible source folders.
    - Avoids overwriting existing files in the shared folder.
    - Logs errors encountered during file transfer.

    Parameters:
    -----------
    config_path : str
        Path to the YAML configuration file containing the base directory.

    Returns:
    --------
    None
        This function does not return any value but prints logs of copied and skipped files.

    Raises:
    -------
    FileNotFoundError
        If the configuration file is not found.
    KeyError
        If the expected 'base_path' key is missing in the configuration file.
    Exception
        If an error occurs while copying files.
    """
    # Load the config file
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    base_path = config["base_path"]  # Root shared drive
    folder_a = os.path.join(base_path, "External_Drive")  # Private folder for User 1
    folder_b = os.path.join(base_path, "Research_Drive")  # Private folder for User 2
    folder_c = os.path.join(base_path, "Internal_Drive")  # Shared folder

    # Ensure Folder_C exists
    os.makedirs(folder_c, exist_ok=True)

    def copy_files(source_folder, target_folder):
        # Copies all files from a private folder to Folder_C.
        if not os.path.exists(source_folder):
            print(f"Skipping: {source_folder} does not exist or access denied.")
            return
        
        for filename in os.listdir(source_folder):
            source_file = os.path.join(source_folder, filename)
            destination_file = os.path.join(target_folder, filename)

            if os.path.isfile(source_file):  # Ignore directories
                if not os.path.exists(destination_file):  # Avoid overwriting
                    try:
                        shutil.copy2(source_file, destination_file)
                        print(f"Copied {filename} from {source_folder} to {target_folder}.")
                    except Exception as e:
                        print(f"Error copying {filename}: {e}")
                else:
                    print(f"Skipped {filename}: Already exists in {target_folder}.")

    # Copy from Folder_A to Folder_C
    copy_files(folder_a, folder_c)

    # Copy from Folder_B to Folder_C
    copy_files(folder_b, folder_c)


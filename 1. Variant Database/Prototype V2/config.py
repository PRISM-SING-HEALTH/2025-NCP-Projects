import yaml

def load_config(config_file):
    """
    Loads configuration from a YAML file and validates required keys.

    Args:
        config_file (str): Path to the YAML configuration file.

    Returns:
        dict: Configuration settings.

    Raises:
        FileNotFoundError: If the YAML configuration file is not found.
        ValueError: If the YAML file cannot be parsed or required keys are missing.
    """
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)

        # Validate required keys
        required_keys = ['base_path', 'local_path', 'files']
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

        print("Configuration loaded successfully.")
        return config

    except FileNotFoundError:
        print(f"Error: The configuration file '{config_file}' was not found.")
        raise
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse the YAML configuration file. Details: {e}")
        raise
    except ValueError as e:
        print(f"Error: {e}")
        raise

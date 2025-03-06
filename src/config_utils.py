import os
import yaml

def load_train_config(config_name):
    """
    Loads and merges YAML configuration files required for training.

    This function reads the specified training configuration file along with 
    two method-specific configuration files. The configurations are merged together and returned 
    as a single dictionary.

    Args:
        config_name (str): The name of the training configuration file to be loaded.

    Returns:
        dict: A dictionary containing the merged configurations.
    """
    # Open data config file
    with open(os.path.join("config/train/", config_name)) as file:
        config = yaml.safe_load(file)

    # Open the method config files
    with open(os.path.join("config/train/", "embedding_finetuning.yaml")) as file:
        ft_method_config = yaml.safe_load(file)
    
    # Merge the method config files with the data config file
    config.update(ft_method_config)

    return config

def load_test_config(config_name):
    """
    Loads a YAML configuration file required for testing.

    This function reads the specified testing configuration file and returns its 
    contents as a dictionary.

    Args:
        config_name (str): The name of the testing configuration file to be loaded.

    Returns:
        dict: A dictionary containing the testing configuration.
    """
    with open(os.path.join("config/test/", config_name)) as file:
        config = yaml.safe_load(file)

    return config

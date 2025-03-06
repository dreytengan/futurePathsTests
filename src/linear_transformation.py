import numpy as np
from sentence_transformers import SentenceTransformer
from config_utils import load_train_config
import argparse
from data_classes import Data
import json


def max_frobenius_norm(n, a_min, a_max):
    """
    Computes the maximum possible Frobenius norm for a transformation matrix.

    The Frobenius norm measures the difference between a transformation matrix and 
    the identity matrix. This function calculates the theoretical maximum norm 
    given the matrix size and element range.

    Args:
        n (int): Size of the square transformation matrix (n x n).
        a_min (float): Minimum value in the transformation matrix.
        a_max (float): Maximum value in the transformation matrix.

    Returns:
        float: Maximum possible Frobenius norm for the given matrix size.
    """
    max_diag_deviation = max((a_min - 1) ** 2, (a_max - 1) ** 2)
    max_off_diag_deviation = max(a_min**2, a_max**2)

    num_diag = n
    num_off_diag = n * (n - 1)  # Total elements - diagonal

    max_norm = np.sqrt(
        num_diag * max_diag_deviation + num_off_diag * max_off_diag_deviation
    )
    return max_norm


def train_linear_transformation(model, train_pairs, select_only_different=False):
    """
    Trains a linear transformation matrix T to map career history embeddings to ESCO occupation embeddings.

    This function uses a least squares approach to solve for T in the equation:
        B = A @ T
    where A represents career history embeddings and B represents ESCO occupation embeddings.

    Args:
        model (SentenceTransformer): Pre-trained sentence embedding model.
        train_pairs (list of tuples): List of (career_history_text, esco_occupation_text) pairs.
        select_only_different (bool): If True, removes pairs where the texts are identical.

    Returns:
        np.ndarray: Learned transformation matrix T.
    """
    # Extract text pairs
    career_history_texts, esco_occupation_texts = zip(*train_pairs)
    
    print("Example pair:")
    print("Career History:", career_history_texts[0])
    print("ESCO Occupation:", esco_occupation_texts[0])

    if select_only_different:
        print("Filtering out identical career history and ESCO occupation descriptions...")
        career_history_texts, esco_occupation_texts = zip(
            *[
                (career_history_texts[i], esco_occupation_texts[i])
                for i in range(len(career_history_texts))
                if career_history_texts[i] != esco_occupation_texts[i]
            ]
        )
        print("Remaining pairs:", len(career_history_texts))

    # Encode texts into embeddings
    A = model.encode(career_history_texts)
    B = model.encode(esco_occupation_texts)

    # Solve for transformation matrix T using least squares
    T, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)

    # Compute predicted B values
    B_pred = A @ T

    # Compute Mean Squared Error (MSE) and Root Mean Squared Error (RMSE)
    mse = np.mean(np.sum((B - B_pred) ** 2, axis=1))
    rmse = np.sqrt(mse)

    # Compute Frobenius norm deviation from identity matrix
    identity = np.eye(T.shape[1])
    frobenius_norm = np.linalg.norm(T - identity, "fro")
    max_norm = max_frobenius_norm(T.shape[1], np.min(T), np.max(T))
    normalized_frobenius_norm = frobenius_norm / max_norm

    print(f"Mean Squared Error (MSE): {mse:.3f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.3f}")
    print(f"Frobenius norm between T and identity: {frobenius_norm:.3f}")
    print(f"Normalized Frobenius norm: {normalized_frobenius_norm:.3f}")

    # Save errors to a JSON file
    errors = {"MSE": float(round(mse, 3)), "RMSE": float(round(rmse, 3))}
    with open(config["output"]["path_linear_transformation_errors"], "w") as f:
        json.dump(errors, f)

    return T


def main(config):
    """
    Main function to train a linear transformation matrix for mapping embeddings.

    This function:
    1. Loads the training data for transformation fine-tuning.
    2. Loads a pre-trained sentence embedding model.
    3. Computes and saves the transformation matrix.

    Args:
        config (dict): Configuration dictionary containing paths and parameters.
    """
    print("Loading data...")
    data = Data(
        config["data"]["data_type"]
    )

    train_pairs, _, _ = data.get_data(stage="transformation_finetuning")

    print("Loading model...")
    model = SentenceTransformer(config["model"]["embedding_model_transformation"])

    print("Training transformation matrix...")
    T = train_linear_transformation(model=model, train_pairs=train_pairs)

    print(f"Saving transformation matrix to: {config['output']['path_transformation_matrix']}")
    np.save(config["output"]["path_transformation_matrix"], T)


if __name__ == "__main__":
    """
    Command-line execution entry point.

    This script takes a configuration file as input and trains a transformation matrix 
    to map career history embeddings to ESCO occupation embeddings.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--linear_transformation_config", type=str, help="Path to the configuration YAML file.")
    args = parser.parse_args()

    # Load configuration file
    config = load_train_config(args.linear_transformation_config)

    print("Configuration loaded successfully.")
    print(json.dumps(config, indent=4))

    # Run main function
    main(config)

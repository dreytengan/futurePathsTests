import argparse
from typing import List, Tuple
from config_utils import load_test_config
from predictor import Predictor
from data_classes import Data
from evaluation import mrr, r_at_k
import json
import pickle


def test_model(
    career_histories: List[str],
    predictor: Predictor,
    ground_truth_next_esco_occupations: List[str],
) -> Tuple[dict, List[Tuple[str, List[str]]]]:
    """
    Evaluates the predictor model on test data and computes performance metrics.

    Args:
        career_histories (List[str]): List of career history descriptions.
        predictor (Predictor): The model used for predicting next occupations.
        ground_truth_next_esco_occupations (List[str]): List of ground truth ESCO occupations.

    Returns:
        Tuple[dict, List[Tuple[str, List[str]]]]:
            - A dictionary containing evaluation metrics (MRR, R@5, R@10).
            - A list of tuples where each tuple contains a ground truth occupation and its top 10 predictions.
    """
    print("Predicting next occupations...")

    # Predict next occupations for each career history
    predicted_rank_occupations = predictor.label_predictor.predict(career_histories, top_k=10)

    # Structure the predictions
    predicted = [
        (ground_truth, predicted_ranks)
        for ground_truth, predicted_ranks in zip(
            ground_truth_next_esco_occupations, predicted_rank_occupations
        )
    ]

    # Display sample predictions
    print("\nSample Predictions:")
    for i in range(min(5, len(career_histories))):
        print(f"Test instance {i + 1}:")
        print(f"### Career History:\n{career_histories[i]}")
        print(f"### Ground Truth Next Occupation:\n{ground_truth_next_esco_occupations[i]}")
        print(f"### Top 5 Predicted Occupations:\n{predicted_rank_occupations[i][:5]}")
        print("-" * 80)

    # Compute evaluation metrics
    mrr_score = mrr(predicted)
    r_at_5_score = r_at_k(predicted, k=5)
    r_at_10_score = r_at_k(predicted, k=10)

    print(f"MRR: {mrr_score:.4f}")
    print(f"R@5: {r_at_5_score:.4f}")
    print(f"R@10: {r_at_10_score:.4f}")

    # Prepare results for saving
    scores = {"MRR": round(mrr_score, 4), "R@5": round(r_at_5_score, 4), "R@10": round(r_at_10_score, 4)}
    
    # Retain only the top 10 predictions per tuple
    predicted = [(ground_truth, pred[:10]) for ground_truth, pred in predicted]

    return scores, predicted


def main(config: dict):
    """
    Main function to test the occupation prediction model.

    This function:
    - Loads the test dataset.
    - Initializes the predictor model.
    - Evaluates the model on test data.
    - Saves the results (metrics and predictions) to files.

    Args:
        config (dict): Configuration dictionary containing paths and parameters.
    """
    print("Loading test data...")

    # Load test data
    data = Data(
        config["data"]["data_type"]
    )

    # Retrieve test pairs
    _, _, test_pairs = data.get_data(stage='evaluation')
    print(f"First test pair: {test_pairs[0]}")

    # Extract career history descriptions and ground truth occupations
    career_histories_texts = [exp_doc for exp_doc, _ in test_pairs]
    ground_truth_next_esco_occupation_texts = [esco_doc for _, esco_doc in test_pairs]

    # Determine the transformation model path
    transformation_method = config["model"]["transformation_method"]
    transformation_model_path = (
        config["model"]["transformation_model_path"] if transformation_method == "linear" 
        else config["model"]["path_neural_model"]
    )

    # Initialize predictor
    print("Initializing the predictor model...")
    predictor = Predictor(
        embedding_model_path=config["model"]["embedding_model_path"],
        label_texts=data.labels,
        transformation_model_path=transformation_model_path,
        transformation_method=transformation_method,
    )

    # Evaluate the model
    print("Evaluating model performance...")
    scores, predictions = test_model(career_histories_texts, predictor, ground_truth_next_esco_occupation_texts)

    # Construct file paths for results
    path_scores = f"{config['output']['path_scores']}_{transformation_method}.json"
    path_predictions = f"{config['output']['path_predictions']}_{transformation_method}.pkl"

    print(f"Saving evaluation scores to: {path_scores}")
    print(f"Saving predictions to: {path_predictions}")

    # Save evaluation scores to JSON
    with open(path_scores, "w") as f:
        json.dump(scores, f, indent=4)

    # Save predictions to a pickle file
    with open(path_predictions, "wb") as f:
        pickle.dump(predictions, f)


if __name__ == "__main__":
    """
    Entry point for testing the occupation prediction model.

    This script loads a test configuration file, initializes the predictor, and 
    evaluates the model using the provided test data.
    """
    parser = argparse.ArgumentParser(description="Test the occupation prediction model.")
    parser.add_argument("--test_config", type=str, required=True, help="Path to the test configuration file.")
    args = parser.parse_args()

    # Load test configuration
    config = load_test_config(args.test_config)
    print("Loaded configuration:")
    print(json.dumps(config, indent=4))

    # Run the main testing process
    main(config)

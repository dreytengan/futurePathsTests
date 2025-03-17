# KARRIEREWEGE: A Large-Scale Career Path Prediction Dataset

Welcome to the official repository for the paper [KARRIEREWEGE: A Large-Scale Career Path Prediction Dataset](https://arxiv.org/abs/2412.14612). This repository contains datasets, models, and code for career path prediction research.

## 🚀 Overview
KARRIEREWEGE is a large-scale dataset designed to support career path prediction tasks. It provides rich information on career trajectories, enabling research in career forecasting, job market analysis, and related fields.

The datasets and models are hosted on **Hugging Face**: [Karrierewege Collection](https://huggingface.co/collections/ElenaSenger/karrierewege-67c5bdd7d60a81183b28079d).


## 🔧 Installation & Dependencies
To run the code, ensure you have the necessary dependencies installed. You can set up the environment using:
```bash
pip install -r requirements.txt
```

## 📊 Reproducing Results
To reproduce the results of the **linear transformation approach** for all datasets, run:
```bash
bash src/pipeline.sh
```
This will process the datasets and generate output in the `output/` folder.

## 🧪 Testing with Precomputed Matrices
If you prefer to use the **precomputed matrices** from the linear transformation (stored in the `output` folder), run:
```bash
python src/test.py --test_config "test_config_of_choice.json"
```
Replace `test_config_of_choice.json` with the appropriate configuration file for the dataset you want to test.

## 📬 Contact
For questions or collaborations, feel free to reach out or open an issue in this repository.


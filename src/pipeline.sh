#!/bin/bash

# Define the datasets
DATASETS=( "decorte" "decorte_esco" "karrierewege" "karrierewege_occ" "karrierewege_cp") 

# Log files for output
LOG_DIR="logs"
mkdir -p $LOG_DIR

echo "-----------------------------------------"
# Loop through each dataset
for DATASET in "${DATASETS[@]}"; do
    echo "Processing dataset: $DATASET"

    # Training
    echo "Training with config: ${DATASET}.yaml"
    CUDA_VISIBLE_DEVICES=0 python src/linear_transformation.py --linear_transformation_config "${DATASET}.yaml" > "$LOG_DIR/${DATASET}_train.log" 2>&1
    if [ $? -ne 0 ]; then
        echo "Training failed for $DATASET. Check $LOG_DIR/${DATASET}_train.log for details."
        continue
    fi
    echo "Training completed for $DATASET. Logs saved to $LOG_DIR/${DATASET}_train.log"

    # Testing
    echo "Testing with config: ${DATASET}.yaml"
    CUDA_VISIBLE_DEVICES=0 python src/test.py --test_config "${DATASET}.yaml" > "$LOG_DIR/${DATASET}_test.log" 2>&1
    if [ $? -ne 0 ]; then
        echo "Testing failed for $DATASET. Check $LOG_DIR/${DATASET}_test.log for details."
        continue
    fi
    echo "Testing completed for $DATASET. Logs saved to $LOG_DIR/${DATASET}_test.log"

    echo "Pipeline completed for dataset: $DATASET"
    echo "-----------------------------------------"
done



# CS137 Project 3 Relation Extraction

## Task

With the potential relation mention pairs provided, classify them into the correct relation.

## File Description

- `data`: traning/dev/test instances, POS tagged sentences, constituency/dependency trees
- `lib`: maxent classifier and scripts
- `lists`: world knowledge lists (used for feature extraction)
- `best_records`: the best result trained from `./data/rel-train.gold` and tested on `./data/rel-testset.raw`
- `dependency_tree.py`: a data structure for dependency tree
- `document.py`: some data structures for document and instance representations
- `feature.txt`: feature configuration (currently the best feature combinations)
- `features.py`: all feature functions (for feature-based method)
- `kernels.py`: a pipeline for using scikit-learn SVM
- `pipeline.py`: a pipeline for using maxent
- `tree_kernel.py`: implementation of tree kernels (not successful)
- `util.py`: some utilities for loading data

## Performance

(On tiara.cs.brandeis.edu)

Training: 286.60 sec
Decoding: 221.36 sec

Precision: 61.56
Recall: 34.74
F1: 44.42

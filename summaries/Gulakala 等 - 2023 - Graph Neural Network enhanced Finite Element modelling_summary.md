## Title
Graph Neural Network Enhanced Finite Element Modelling

## Authors
Rutwik Gulakala, Bernd Markert, and Marcus Stoffel
Institute of General Mechanics (IAM), RWTH Aachen University, Aachen, Germany

## Abstract
A Graph Neural Network (GNN)-enhanced Finite Element Method (FEM) framework is proposed to accelerate FE simulations. The approach uses discretized FE geometry as a graph and employs a GNN to solve boundary value problems, taking nodal information, coordinates, edge connections, and boundary conditions as input to predict von-Mises stress distributions at each node.

## Keywords
- Graph Neural Networks (GNN)
- Finite Element Method (FEM)
- Von-Mises stress
- Message-passing
- Elastoplastic materials
- Surrogate modelling

## Research Problem
- FEM simulations are computationally expensive, especially for complex boundary value problems (e.g., crash simulations)
- Existing ML surrogates (e.g., CNNs) are limited to structured rectangular domains, making them unsuitable for unstructured FE meshes
- Prior GNN-based FEM studies use images as input/output, losing direct compatibility with FE pre/post-processors

## Methodology
- **Data generation:** 540 samples from ABAQUS simulations of rectangular aluminium plates with holes at varying locations, sizes, and applied displacements (0.01–0.1 m); elastoplastic Johnson-Cook material model used
- **Graph construction:** FE nodes and elements mapped directly to graph nodes and edges; inputs include nodal coordinates, boundary conditions, and material embeddings
- **Architecture:** Encoder-Decoder GNN using Transformer Convolution layers as aggregation functions and MLPs for message-passing and decoding
- **Training:** 500/540 samples for training, 1000 epochs, Adam optimizer, MSE loss, learning rate 3E-3 with exponential decay from epoch 200
- **Hyperparameter tuning:** Hyperband search algorithm; selected 3 Transformer Convolution layers, 16 latent units, 5 MLP decoder layers

## Key Findings
- MSE of **5.89E-2** achieved on the test set
- Absolute stress errors ranged from **1.7E9–2.9E10 GPa** across different geometry and loading cases
- A computational gain of **12.7%** was observed (including training overhead)
- Strong correlation between GNN-predicted and FEM-computed von-Mises stress distributions

## Contributions
- First GNN-FEM framework that directly interfaces with FE pre/post-processors (VTK format) rather than using images as I/O
- Preserves elemental integrity and mesh structure in the output
- Demonstrates GNN generalization across varied geometries, hole positions, and loading conditions
- Incorporates mechanics knowledge (material data, boundary conditions) as latent embeddings to improve generalization

## Limitations
- Modest computational speedup (12.7%), especially when accounting for training cost
- Tested only on a single material model (aluminium, Johnson-Cook) and relatively simple 2D plate geometries
- Extrapolation performance beyond the trained distribution is not fully characterized (results truncated in paper)
- Dataset size is small (540 samples), which may limit generalizability to more complex geometries

## Conclusion
The proposed GNN-enhanced FEM framework successfully learns to predict von-Mises stress fields directly from FE discretization data, bypassing the image-domain limitation of CNN-based approaches. While the computational gain is currently modest, the architecture demonstrates strong potential for scaling to more complex, unstructured domains and multi-physics problems by leveraging the relational inductive bias of GNNs.
## Title
Graph Neural Network Enhanced Finite Element Modelling

## Authors
Rutwik Gulakala, Bernd Markert, Marcus Stoffel
Institute of General Mechanics (IAM), RWTH Aachen University, Aachen, Germany

## Abstract
A Graph Neural Network (GNN)-enhanced Finite Element Method (FEM) approach is proposed to accelerate FE simulations. The model takes discretized geometry directly from an FE pre-processor (nodal information, edges, coordinates, boundary conditions) and predicts von-Mises stress distributions at each node, with output readable by an FE post-processor — bypassing image-based I/O used in prior work.

## Keywords
- Graph Neural Networks (GNN)
- Finite Element Method (FEM)
- Structural mechanics
- von-Mises stress prediction
- Surrogate modelling
- Message passing

## Research Problem
- FEM simulations are computationally expensive, especially for complex boundary value problems (e.g., crash simulations)
- Existing ML surrogates (CNN-based) are limited to structured rectangular domains and use images as I/O
- No direct graph-based FEM surrogate that consumes and produces native FE mesh data existed

## Methodology
- **Data generation:** 540 samples of rectangular aluminium plates with holes at varying sizes/locations, simulated in ABAQUS with elasto-plastic Johnson-Cook material model; converted to VTK format via ODB2VTK
- **Graph construction:** FE nodes and elements mapped directly to graph nodes and edges (undirected, homogeneous, static graph)
- **Architecture:** Encoder-Decoder GNN using:
  - Transformer convolution layers as aggregation function
  - MLP for message passing and decoding
  - Material data concatenated to the latent vector
- **Training:** 500/540 samples for training, 1000 epochs, Adam optimizer, MSE loss, learning rate 3E-3 with exponential decay from epoch 200
- **Hyperparameter tuning:** Hyperband search algorithm; selected 3 transformer conv layers, 16 latent units, 5 MLP decoder layers

## Key Findings
- Test MSE of **5.89E-2** on the full test batch
- Stress error range: ~1.7E9–2.9E10 GPa across different geometry and loading cases
- GNN results show excellent correlation with FE simulation results
- **12.7% computational gain** observed over standard FEM (inclusive of training cost)
- The model generalises across varying geometries, loads, and boundary conditions

## Contributions
- First GNN-based FEM surrogate that operates directly on native FE mesh data (no image conversion)
- Integration of mechanics knowledge (material properties, boundary conditions) into the graph as node/edge embeddings
- End-to-end pipeline: FE pre-processor → GNN prediction → FE post-processor (VTK-compatible output)
- Demonstrated extrapolation capability beyond training load/geometry limits

## Limitations
- Modest computational gain (12.7%), with training cost included
- Dataset is limited: only 540 samples, one material model (Johnson-Cook aluminium), 2D plate geometries with holes
- Only von-Mises stress is predicted; full displacement/strain fields are not reported
- Generalisation to 3D, non-linear dynamic, or multi-material problems is not demonstrated
- Error magnitudes in GPa range suggest room for accuracy improvement

## Conclusion
The proposed GNN-enhanced FEM framework successfully replaces image-based I/O with native mesh data, enabling direct integration with FE pre- and post-processors. The model replicates FEM stress distributions with high fidelity and achieves a measurable speedup, demonstrating the viability of GNNs as physics-informed surrogates for structural simulations on unstructured domains.
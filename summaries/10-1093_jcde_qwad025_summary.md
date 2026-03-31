## Title
An FEA Surrogate Model with Boundary Oriented Graph Embedding Approach for Rapid Design

## Authors
- Xingyu Fu, Fengfeng Zhou — School of Mechanical Engineering, Purdue University
- Dheeraj Peddireddy, Vaneet Aggarwal — School of Industrial Engineering, Purdue University
- Zhengyang Kang — School of Mechanical and Power Engineering, Nanjing Tech University
- Martin Byung-Guk Jun *(corresponding)* — Purdue University / Indiana Manufacturing Competitiveness Center

## Abstract
The paper proposes a **Boundary Oriented Graph Embedding (BOGE)** approach for Graph Neural Networks (GNN) to serve as a general surrogate model for physical field regression and boundary value problem solving. BOGE provides shortcuts for both boundary elements and local neighbor elements, enabling efficient regression on large-scale triangular-mesh-based FEA results. Applied to the cantilever beam problem, the model predicts stress fields and topological optimization results with high accuracy using a 3-layer Deep GCN.

## Keywords
- Machine learning
- Graph neural network
- Stress field
- Solid mechanics
- Topology optimization

## Research Problem
- FEA is computationally expensive and time-consuming, creating bottlenecks in time-sensitive manufacturing applications (inverse modeling, agile manufacturing, generative design).
- **CNN-based surrogates** are limited to fixed input sizes, Euclidean grids, and uniform meshes — poorly suited for structured triangular meshes.
- **GNN-based surrogates** suffer from the *over-smoothing problem* when stacked deeply, restricting models to ~3 layers with short-range vertex interactions.
- No existing ML approach can handle long-range boundary information propagation in large-scale static boundary value problems in a single forward pass.

## Methodology
- **Graph embedding:** Structured FEA meshes are embedded as undirected graphs G = (V, E), where vertices encode node coordinates, material properties, and boundary conditions.
- **BOGE approach:** Augments standard graph embedding with two types of shortcuts:
  - *Boundary element shortcuts* — direct edges from boundary condition elements to all other elements, enabling long-range information propagation without deep stacking.
  - *Local neighbor shortcuts* — preserve local geometric context for accurate field regression.
- **Backbone model:** 3-layer Deep GCN (Graph Convolutional Network) with the MPNN framework.
- **Tasks evaluated:**
  1. Von Mises stress field prediction for a 2D cantilever beam (with elliptical hole, A36 steel, fixed left edge, 1000 N force on right edge).
  2. Topological optimization result regression.
- **Dataset:** Simulations generated in ABAQUS with triangular meshes (~1.0 mm global mesh size).

## Key Findings
- BOGE + 3-layer Deep GCN achieves:
  - **Stress field prediction:** MSE = 0.011706 (2.41% MAPE)
  - **Topology optimization:** MSE = 0.002735 (only 1.58% of elements with error > 0.01)
- BOGE successfully propagates boundary condition information across large graphs in a single simulation step — a capability unmatched by prior approaches.
- The model generalizes across varying boundary conditions without requiring retraining per case.

## Contributions
- Introduces BOGE, the first graph embedding strategy specifically designed to handle long-range boundary information propagation in static FEA problems.
- Demonstrates GNN applicability to large-scale triangular mesh FEA without over-smoothing, using only 3 GCN layers.
- Extends surrogate modeling beyond field regression to **abstract design tasks** (topology optimization), showing potential for decision-making in generative design.
- Provides a framework compatible with existing GNN architectures as a plug-in embedding strategy.

## Limitations
- Evaluated only on a 2D cantilever beam problem; generalization to 3D geometries and other physical domains (e.g., fluid dynamics, thermal) is not demonstrated.
- The paper is a preprint (arXiv, Aug 2021); results are not yet peer-validated at submission time.
- Accuracy trade-off vs. full FEA is inherent; the model compromises precision for speed.
- Boundary shortcut construction may not trivially scale to highly complex or irregular geometries.

## Conclusion
BOGE addresses a fundamental bottleneck in GNN-based FEA surrogates by introducing direct graph shortcuts from boundary elements, enabling long-range message passing without deep layer stacking or over-smoothing. The approach achieves strong regression accuracy on both stress field prediction and topology optimization for the cantilever beam case, and lays the groundwork for a general, efficient deep-learning FEA simulator applicable to industry and design-related domains.
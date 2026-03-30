## Title
An FEA Surrogate Model with Boundary Oriented Graph Embedding Approach for Rapid Design

## Authors
- Xingyu Fu, Fengfeng Zhou, Martin Byung-Guk Jun — School of Mechanical Engineering, Purdue University
- Dheeraj Peddireddy, Vaneet Aggarwal — School of Industrial Engineering, Purdue University
- Zhengyang Kang — School of Mechanical and Power Engineering, Nanjing Tech University

## Abstract
The paper introduces the Boundary Oriented Graph Embedding (BOGE) approach, combining it with a Graph Neural Network (GNN) to serve as a surrogate model for Finite Element Analysis (FEA). Applied to the cantilever beam problem, it enables stress field prediction and topological optimization in ~10ms. The approach handles unstructured triangular meshes and overcomes limitations of CNN- and conventional GNN-based methods.

## Keywords
- Machine learning
- Graph neural network
- Stress field
- Solid mechanics
- Topology optimization

## Research Problem
- FEA is computationally expensive and time-consuming, creating bottlenecks in time-sensitive manufacturing processes (inverse modeling, agile manufacturing, rapid prototyping)
- CNN-based surrogates require fixed input sizes and struggle with unstructured meshes
- Standard GNN approaches suffer from **over-smoothing** when stacked deeply, limiting message-passing distance and restricting models to ~3 layers
- Existing methods lack a general, end-to-end FEA surrogate capable of handling large-scale unstructured meshes

## Methodology
- **Graph Embedding:** Unstructured FEA mesh elements are embedded into an undirected graph G = (V, E) where vertices represent geometric node points and edges represent neighbor connections
- **BOGE Approach:** Introduces two types of shortcut connections:
  - *Boundary element shortcuts* — directly connects boundary condition elements to all other elements, bypassing multi-hop message passing
  - *Local neighbor element shortcuts* — enhances local neighborhood information aggregation
- **Backbone Model:** 3-layer Deep GCN (Graph Convolutional Network) used as the regression backbone
- **Problem Domain:** 2D cantilever beam (A36 steel, Young's modulus 200 GPa, Poisson's ratio 0.32) with an elliptical hole, fixed left edge, and 1000N point load at the right edge center
- **Simulation Ground Truth:** Generated via ABAQUS with triangular meshes (~1.0mm global mesh size)
- **Tasks:** (1) von Mises stress field prediction, (2) topological optimization

## Key Findings
- Stress field prediction: **MSE = 0.011706** (2.41% mean absolute percentage error)
- Topological optimization: **MSE = 0.002735** (only 1.58% of elements with error > 0.01)
- Inference time: **~10ms**, independent of input model size (within dataset scope)
- BOGE successfully resolves the over-smoothing limitation of deep GNN stacking by providing long-range shortcuts without requiring additional layers

## Contributions
- Proposes BOGE, a novel graph embedding strategy that enables efficient long-range message passing in GNNs without deep stacking
- First method to effectively handle **large-scale unstructured triangular mesh** FEA regression using GNN
- Demonstrates applicability to both **physical field prediction** and **topology optimization** in a single framework
- Establishes a pathway toward a general deep-learning FEA simulator deployable on portable/edge devices
- Supports end-to-end design optimization, reducing reliance on manual design iteration

## Limitations
- Validated only on a single problem type (2D cantilever beam); generalization to other boundary value problems not fully demonstrated
- Performance is bounded to geometries represented within the training dataset
- Training still requires significant time and computational resources upfront
- The paper's scope is limited to 2D triangular meshes; extension to 3D or other mesh types is not evaluated

## Conclusion
The BOGE approach addresses critical shortcomings of existing CNN- and GNN-based FEA surrogate models by enabling efficient, long-range information propagation across unstructured meshes via boundary and neighbor shortcuts. With millisecond-scale inference, high regression accuracy, and applicability to both stress prediction and topology optimization, BOGE presents a practical foundation for general-purpose deep-learning FEA simulators beneficial to CAD, Industry 4.0, and rapid digital prototyping workflows.
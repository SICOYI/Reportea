## Title
An FEA Surrogate Model with Boundary Oriented Graph Embedding Approach for Rapid Design

## Authors
- Xingyu Fu, Fengfeng Zhou — School of Mechanical Engineering, Purdue University
- Dheeraj Peddireddy, Vaneet Aggarwal — School of Industrial Engineering, Purdue University
- Zhengyang Kang — School of Mechanical and Power Engineering, Nanjing Tech University
- Martin Byung-Guk Jun *(corresponding)* — Purdue University & Indiana Manufacturing Competitiveness Center (IN-MaC)

## Abstract
The paper proposes a **Boundary Oriented Graph Embedding (BOGE)** approach for Graph Neural Networks (GNNs) to serve as a general surrogate model for FEA. BOGE provides shortcuts for both boundary and local neighbor elements, enabling efficient regression on large-scale triangular-mesh-based FEA results. Applied to a cantilever beam problem, it predicts stress fields and topological optimization results with high accuracy.

## Keywords
- Machine learning
- Graph neural network
- Stress field
- Solid mechanics
- Topology optimization

## Research Problem
- FEA is computationally expensive, creating bottlenecks for time-sensitive applications (inverse modeling, agile manufacturing, generative design)
- CNN-based surrogates require fixed-size input tensors and Euclidean grids, incompatible with structured (triangular) meshes
- Standard GNNs suffer from **over-smoothing** when stacked deeply enough for long-range boundary information propagation
- No general, ready-to-use ML approach existed for structured-mesh boundary value problems requiring long-range graph-vertex interactions

## Methodology
- **Graph embedding:** FEA mesh nodes mapped to graph vertices; edges encode neighbor connectivity and boundary shortcuts
- **BOGE shortcuts:** Direct edges added from boundary elements (force/fixture) to all other elements, reducing effective propagation distance
- **Backbone model:** 3-layer Deep Graph Convolutional Network (DeepGCN) using the MPNN framework
- **Tasks:**
  - Von Mises stress field regression on a 2D cantilever beam (A36 steel, triangular mesh ~1.0 mm global size, simulated in ABAQUS)
  - Topological optimization result regression
- **Inputs:** Node coordinates, material properties, boundary condition flags
- **Training data:** FEA simulation results with varying geometry (elliptical hole position/size) and load conditions

## Key Findings
- Stress field prediction: **MSE = 0.011706 (MAPE = 2.41%)**
- Topology optimization prediction: **MSE = 0.002735** (only 1.58% of elements with error > 0.01)
- BOGE shortcuts effectively eliminate the over-smoothing problem by reducing required GNN depth
- 3-layer DeepGCN with BOGE matches or outperforms deeper networks without boundary shortcuts
- The model generalizes across varying geometry and boundary conditions without retraining per case

## Contributions
- Novel **BOGE graph embedding scheme** that encodes boundary conditions as direct long-range graph shortcuts
- Demonstrated that a shallow GNN (3 layers) with BOGE achieves accuracy comparable to impractically deep networks
- First approach to handle **static boundary value problems** on large-scale triangular meshes in a single inference pass
- Extended applicability beyond physical field regression to **abstract design tasks** (topology optimization)
- Provides a generalizable framework applicable to other FEA domains beyond solid mechanics

## Limitations
- Evaluated only on a **2D cantilever beam** problem; generalization to 3D or complex geometries not demonstrated
- Dataset scope is limited (single material, single load type, geometric variation only via hole shape/position)
- BOGE shortcut construction assumes identifiable boundary elements, which may be non-trivial for complex multi-boundary problems
- Accuracy trade-off vs. full FEA remains; MAPE ~2.41% may be insufficient for safety-critical applications
- Scalability to very large 3D meshes not assessed

## Conclusion
The BOGE approach addresses the core limitation of GNN-based FEA surrogates — the inability to propagate boundary condition information over long graph distances without over-smoothing. By embedding boundary shortcuts directly into the graph structure, BOGE enables a shallow, efficient DeepGCN to regress both stress fields and topology optimization outputs with high accuracy on structured triangular meshes. This work lays groundwork for a general deep-learning FEA simulator applicable to industrial design workflows.
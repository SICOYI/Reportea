## Title
Multi-Level GNN Preconditioner for Solving Large Scale Problems

## Authors
- Matthieu Nastorg (Université Paris-Saclay, CNRS, Inria, LISN)
- Jean-Marc Gratien (IFP Énergies-Nouvelles)
- Thibault Faney (IFP Énergies-Nouvelles)
- Michele Alessandro Bucci (Safran Tech)
- Guillaume Charpiat (Université Paris-Saclay, CNRS, Inria, LISN)
- Marc Schoenauer (Université Paris-Saclay, CNRS, Inria, LISN)

## Abstract
This paper proposes a novel GNN-based preconditioner that integrates a Graph Neural Network model within a multi-level Domain Decomposition framework. The preconditioner enhances the efficiency of Krylov iterative methods, forming a hybrid solver capable of converging to any desired accuracy. The approach handles large-scale, variably-sized unstructured meshes, leverages GPU parallelism, and is benchmarked against an optimized C++ legacy solver used in real CFD software.

## Keywords
- Graph Neural Networks (GNNs)
- Multi-Level Domain Decomposition
- Partial Differential Equations (PDEs)
- Hybrid Solvers
- Preconditioning
- Krylov Methods
- Additive Schwarz Method (ASM)

## Research Problem
- Traditional iterative solvers (e.g., CG, GMRES) guarantee convergence but rely on CPU computations with limited parallelization and face efficiency/scalability challenges for large problems.
- Data-driven ML/GNN solvers leverage GPU parallelism but suffer from:
  - Poor generalization beyond training distribution
  - Restriction to small, fixed-size meshes
  - No guarantee of convergence to a desired precision
- No existing hybrid approach adequately addresses large-scale, industrially relevant PDE problems while guaranteeing convergence.

## Methodology
- **Problem formulation:** Steady-state Poisson equation with Dirichlet boundary conditions, discretized via Finite Element Method (FEM) into a sparse linear system Au = b.
- **Preconditioner design:** GNN model embedded within a multi-level Additive Schwarz Method (ASM) framework:
  - Domain decomposed into K overlapping sub-domains.
  - GNN models solve local sub-problems in parallel on GPU.
  - A two-level extension adds a coarse problem to improve weak scalability across sub-domains.
- **Two-level ASM preconditioner** combines coarse-level correction with local GNN-based sub-solvers (Eq. 7).
- **Hybrid solver:** The GNN preconditioner is plugged into a Preconditioned Conjugate Gradient (PCG) iteration, ensuring convergence to any target tolerance.
- Sub-problem sizes are adapted to GNN capabilities, enabling inference on meshes of arbitrary size and shape.

## Key Findings
- The GNN preconditioner significantly reduces the number of Krylov iterations needed for convergence compared to unpreconditioned solvers.
- The hybrid solver converges to any desired precision, overcoming the accuracy ceiling of purely data-driven methods.
- GPU execution of batched GNN sub-problems enables competitive wall-clock times against optimized C++ legacy solvers.
- The multi-level (two-level) approach improves weak scalability as the number of sub-domains increases.
- The method generalizes to meshes of varying sizes and shapes, beyond the training distribution.

## Contributions
- A novel GNN-based preconditioner that mirrors the Additive Schwarz structure, enabling large-scale PDE solving with convergence guarantees.
- A multi-level Domain Decomposition design that enforces scalability and adapts sub-problem sizes to GNN capabilities.
- A hybrid solver framework combining the accuracy/convergence of Krylov methods with the GPU efficiency of GNNs.
- Empirical validation of numerical accuracy and performance benchmarking against a state-of-the-art C++ CFD solver.

## Limitations
- The paper is truncated in the provided text; full experimental results and complete performance analysis are not available here.
- The GNN sub-solvers still depend on training quality; out-of-distribution sub-problems may degrade preconditioner quality, increasing iteration counts.
- The approach currently focuses on the Poisson equation; generalization to other PDEs is not explicitly demonstrated.
- Extending to 3D large-scale industrial problems may introduce additional engineering complexity not fully assessed.

## Conclusion
The paper presents a hybrid solver that successfully bridges the gap between traditional iterative solvers and data-driven GNN approaches. By embedding a GNN within a multi-level Additive Schwarz preconditioner, the method achieves GPU-accelerated, scalable preconditioning while retaining the convergence guarantees of Krylov methods. This makes it a promising candidate for large-scale, industrially relevant numerical simulations, particularly in CFD contexts where accuracy and performance are both critical.
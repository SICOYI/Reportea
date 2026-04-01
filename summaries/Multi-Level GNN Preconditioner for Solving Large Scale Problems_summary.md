## Title
Multi-Level GNN Preconditioner for Solving Large Scale Problems

## Authors
- Matthieu Nastorg — Université Paris-Saclay, CNRS, Inria, LISN
- Jean-Marc Gratien — IFP Énergies-Nouvelles
- Thibault Faney — IFP Énergies-Nouvelles
- Michele Alessandro Bucci — Safran Tech
- Guillaume Charpiat — Université Paris-Saclay, CNRS, Inria, LISN
- Marc Schoenauer — Université Paris-Saclay, CNRS, Inria, LISN

## Abstract
This paper proposes a novel GNN-based preconditioner that integrates Graph Neural Networks within a multi-level Domain Decomposition framework to solve large-scale Poisson problems. The preconditioner enhances Krylov iterative methods, forming a hybrid solver that converges to any desired accuracy, runs efficiently on GPUs, and scales to meshes of arbitrary size and shape.

## Keywords
- Graph Neural Networks (GNNs)
- Multi-Level Domain Decomposition
- Partial Differential Equations (PDEs)
- Hybrid Solvers
- Krylov Methods
- Additive Schwarz Method
- Preconditioning

## Research Problem
- Solving large-scale Poisson equations is a major computational bottleneck in numerical simulations (e.g., CFD).
- **Traditional solvers** (CPU-based Krylov methods) guarantee convergence but are limited in parallelism and scalability.
- **ML/GNN-based solvers** leverage GPU parallelism but suffer from:
  - Poor generalization to out-of-distribution or large-scale problems
  - No convergence guarantees
  - Limited accuracy tied to training performance
- Existing hybrid methods remain restricted to small-scale or Cartesian-grid problems.

## Methodology
- **Problem formulation:** Steady-state Poisson equation with Dirichlet boundary conditions, discretized via FEM on unstructured meshes, yielding a sparse linear system `Au = b`.
- **Preconditioner design:** Mirrors the structure of the multi-level Additive Schwarz Method (ASM):
  - The global domain is decomposed into `K` overlapping sub-domains.
  - GNN models solve local sub-problems in parallel on GPU.
  - A two-level extension adds a coarse problem to improve weak scalability.
- **Hybrid solver:** The GNN preconditioner `M⁻¹` is plugged into a Preconditioned Conjugate Gradient (PCG) loop, ensuring convergence to any target tolerance.
- **Scalability:** Sub-domain sizes are adapted to GNN capacity; batched GPU execution handles many sub-domains concurrently.

## Key Findings
- The GNN preconditioner significantly reduces the number of Krylov iterations needed to reach a target accuracy.
- The hybrid solver converges to arbitrary precision, overcoming the fixed-accuracy ceiling of standalone ML solvers.
- The two-level approach improves weak scalability as the number of sub-domains grows.
- The method generalizes to meshes of varying sizes and shapes, not just fixed-size training distributions.
- Performance is competitive against an optimized C++ legacy linear solver used in real CFD software.

## Contributions
- **Novel preconditioner:** First integration of a GNN solver within a multi-level Additive Schwarz preconditioning framework.
- **Scalability to large meshes:** Sub-domain decomposition decouples GNN inference from global mesh size, enabling industrial-scale use.
- **Convergence guarantee:** By embedding the GNN as a preconditioner in a Krylov method, the hybrid solver inherits rigorous convergence properties absent in pure ML approaches.
- **GPU efficiency:** Batched sub-domain solving fully exploits GPU parallelism.
- **Fair benchmarking:** In-depth performance analysis against a production C++ solver provides a realistic evaluation.

## Limitations
- The method is demonstrated primarily on the Poisson equation; extension to other PDEs is not fully explored.
- GNN generalization still depends on training distribution quality; severe out-of-distribution cases may degrade preconditioner quality (though the Krylov method still converges).
- The paper acknowledges that prior hybrid methods using PINNs or Deep Ritz replacements are limited to small Cartesian data — this work improves but does not fully eliminate training-distribution sensitivity.
- Legacy code integration and GPU infrastructure requirements may pose practical adoption barriers.

## Conclusion
The proposed multi-level GNN preconditioner successfully bridges the gap between data-driven GPU-accelerated methods and classical solver guarantees. By embedding GNN inference inside a Domain Decomposition preconditioner for Krylov methods, the hybrid solver achieves convergence to any desired accuracy while benefiting from GPU parallelism and generalization to large, unstructured meshes. Benchmarks against a C++ legacy solver confirm the method's competitiveness for real industrial CFD workflows, with the two-level extension ensuring scalability across increasing sub-domain counts.
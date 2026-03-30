## Title
DiffTaichi: Differentiable Programming for Physical Simulation

## Authors
Yuanming Hu, Luke Anderson, Tzu-Mao Li, Qi Sun, Nathan Carr, Jonathan Ragan-Kelley, Frédéric Durand
(MIT CSAIL, Adobe Research, UC Berkeley)

## Abstract
DiffTaichi is a differentiable programming language designed for high-performance physical simulators. Built on the Taichi imperative language, it uses source code transformations (SCT) within kernels and a lightweight tape for end-to-end backpropagation. It is demonstrated across 10 physical simulators, achieving significant speedups over TensorFlow while matching hand-written CUDA performance with far less code.

## Keywords
- Differentiable programming
- Physical simulation
- Automatic differentiation
- Source code transformation
- Neural network control

## Research Problem
Existing differentiable programming tools (TensorFlow, PyTorch) are poorly suited for physical simulation because they:
- Lack support for imperative, non-element-wise array operations (stencils, particle-grid interactions)
- Cannot efficiently express megakernels, leading to low arithmetic intensity
- Do not naturally support parallel control flow (collisions, boundary conditions, iterative solvers)

## Methodology
- **Two-scale AD system:**
  - *Local (intra-kernel)*: Source code transformation (SCT) with SSA conversion, branch flattening, and reverse-mode AD
  - *Global (inter-kernel)*: Lightweight tape records kernel launches and replays gradient kernels in reverse order
- **Global Data Access Rules** enforce well-defined differentiation semantics under imperative mutation (writes must use atomic adds after the first write; no reads before accumulation completes)
- **Frontend**: Python-embedded DSL compiled via Python AST transformer to Taichi IR, then JIT-compiled to forward and backward executables
- Validated on 10 simulators covering rigid bodies, deformable objects, and fluids

## Key Findings
- A differentiable elastic object simulator in DiffTaichi is **4.2× shorter** than hand-engineered CUDA yet runs at the same speed
- **188× faster** than the equivalent TensorFlow implementation
- Neural network controllers are typically optimized within **tens of iterations** using DiffTaichi gradients
- Controller optimization converges **1–4 orders of magnitude faster** than model-free reinforcement learning

## Contributions
- A new differentiable programming language tailored for physical simulation
- A two-scale AD system combining SCT (performance) with tape-based tracing (flexibility)
- Support for megakernels, imperative parallel programming, and flexible (non-element-wise) indexing
- Open-source implementation with 10 reproducible differentiable simulators

## Limitations
- Global Data Access Rules require programmers to adapt forward simulators (e.g., storing full trajectory history instead of only current state)
- Full trajectory storage increases memory consumption (partially mitigated via checkpointing)
- SCT within kernels requires well-structured, statically analyzable code — complex dynamic control flow may be harder to differentiate

## Conclusion
DiffTaichi demonstrates that a purpose-built differentiable programming language, combining imperative style with a two-scale AD system, can match or exceed the performance of hand-written CUDA while being significantly more productive than general-purpose ML frameworks. It enables practical gradient-based optimization of complex physical simulators integrated with neural network controllers.
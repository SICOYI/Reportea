## Title
**DiffTaichi: Differentiable Programming for Physical Simulation**

---

## Authors
- Yuanming Hu, Luke Anderson, Frédo Durand — MIT CSAIL
- Tzu-Mao Li, Jonathan Ragan-Kelley — UC Berkeley
- Qi Sun, Nathan Carr — Adobe Research

---

## Abstract
DiffTaichi is a differentiable programming language designed for high-performance physical simulation. Built on the imperative Taichi language, it uses source code transformations to generate gradients while preserving arithmetic intensity and parallelism. A lightweight tape records simulation structure for end-to-end backpropagation. The system is demonstrated across 10 physical simulators, achieving up to 188× speedup over TensorFlow and matching hand-written CUDA performance with 4.2× less code.

---

## Keywords
- Differentiable programming
- Physical simulation
- Automatic differentiation
- Source code transformation
- Neural network controllers
- GPU computing

---

## Research Problem
- Existing differentiable programming tools (TensorFlow, PyTorch) are poorly suited for physical simulation due to:
  - Low arithmetic intensity from element-wise linear algebra operators
  - Lack of support for imperative, parallel programming patterns
  - Inability to express flexible, non-element-wise indexing (e.g., stencils, particle-grid interactions)
- Hand-engineering differentiable simulators in CUDA is productive but error-prone and verbose
- No existing tool simultaneously offers high performance, flexibility, and ease of use for differentiable simulation

---

## Methodology
- **Language Design**: DiffTaichi is embedded in Python; a Python AST transformer compiles code to Taichi intermediate representation (IR), which is statically typed, compiled, parallel, and differentiable
- **Two-Scale Automatic Differentiation**:
  - *Local AD*: Source code transformation (SCT) differentiates within individual kernels — preserving megakernel structure and arithmetic intensity
  - *Global AD*: A lightweight tape records kernel function pointers and arguments; gradient kernels are replayed in reverse order during backpropagation
- **Global Data Access Rules**: Two constraints ensure well-defined AD under imperative semantics:
  1. Multiple writes to a tensor element must be atomic additions (accumulations)
  2. No reads occur to an element until its accumulation is complete
- **IR Preprocessing**: Branching is flattened and mutable variables are converted to SSA form before running the AD transform
- **Adjoint Storage Control**: Users specify adjoint tensor layout via Taichi's data structure DSL, or use `ti.root.lazy_grad()` for automatic placement

---

## Key Findings
- A differentiable elastic object simulator in DiffTaichi is:
  - **4.2× shorter** than a hand-engineered CUDA version, with equivalent runtime performance
  - **188× faster** than an equivalent TensorFlow implementation
- Neural network controllers optimized with DiffTaichi-backed simulators converge within **tens of iterations**, vs. thousands for model-free RL
- Controller optimization with differentiable simulators converges **1–4 orders of magnitude faster** than model-free reinforcement learning
- 10 physical simulators (rigid bodies, deformable objects, fluids) were implemented and differentiated successfully

---

## Contributions
- A new **differentiable programming language** tailored for physical simulation, embedded in Python
- A **two-scale AD system** combining SCT (within kernels) and tape-based tracing (across simulation steps)
- Support for **megakernels**, **imperative parallel programming**, and **flexible arbitrary indexing** — all absent in prior differentiable frameworks
- Open-source compiler, language, and 10 simulator implementations with fully reproducible results

---

## Limitations
- The **Global Data Access Rules** require programmers to adjust forward simulators (e.g., storing full state history rather than latest values), increasing memory consumption
- Storing full simulation history for backpropagation can be memory-intensive; checkpointing is discussed as a mitigation but adds complexity
- The language is compiled and statically typed, which may reduce flexibility compared to fully dynamic tracing approaches
- Long compilation times are a known trade-off when using SCT for full-simulator differentiation (mitigated by the two-scale approach)

---

## Conclusion
DiffTaichi demonstrates that a carefully designed two-scale automatic differentiation system — combining source code transformation within kernels and lightweight tape-based recording across timesteps — can deliver both the performance of hand-tuned CUDA and the productivity of high-level differentiable frameworks. By addressing the specific needs of physical simulation (megakernels, imperative style, flexible indexing), DiffTaichi enables rapid development of high-performance differentiable simulators that significantly accelerate gradient-based learning and controller optimization tasks.
## Title
**DiffTaichi: Differentiable Programming for Physical Simulation**

---

## Authors
Yuanming Hu, Luke Anderson (MIT CSAIL), Tzu-Mao Li, Jonathan Ragan-Kelley (UC Berkeley), Qi Sun, Nathan Carr (Adobe Research), Frédéric Durand (MIT CSAIL)

---

## Abstract
DiffTaichi is a differentiable programming language designed for high-performance physical simulation. Built on the imperative Taichi language, it uses source code transformations (SCT) within kernels and a lightweight tape for end-to-end backpropagation. It is demonstrated across 10 physical simulators, achieving significant performance and productivity gains over TensorFlow and hand-written CUDA.

---

## Keywords
- Differentiable programming
- Physical simulation
- Automatic differentiation
- Source code transformation
- Neural network controllers
- GPU/CPU simulation

---

## Research Problem
- Differentiable physical simulators are critical for fast controller optimization, but existing tools (TensorFlow, PyTorch) make it difficult to implement them with high performance.
- Key missing features in existing systems: megakernel support, imperative parallel programming, and flexible (non-element-wise) array indexing.

---

## Methodology
- **Language design**: DiffTaichi is embedded in Python; a Python AST transformer compiles it to Taichi intermediate representation (IR), which is statically typed, compiled, parallel, and differentiable.
- **Two-scale AD system**:
  - *Local (intra-kernel)*: Source code transformation (SCT) differentiates individual kernels — handles branching via flattening and converts to SSA form before applying reverse-mode AD.
  - *Global (inter-kernel)*: A lightweight tape records kernel function pointers and arguments; gradient kernels are replayed in reverse order during backpropagation.
- **Global Data Access Rules**: Constrain imperative kernel writes (second writes must be atomic adds; no reads before accumulation is complete) to make AD well-defined.
- **Adjoint tensor storage**: Users can control layout explicitly or use `ti.root.lazy_grad()` for automatic placement mirroring primal tensors.
- **Megakernels**: Multiple computation stages fused into single kernels, preserving arithmetic intensity through differentiation.

---

## Key Findings
- A differentiable elastic object simulator in DiffTaichi is **4.2× shorter** than a hand-engineered CUDA version, runs at **equivalent speed**, and is **188× faster** than a TensorFlow implementation.
- Neural network controllers optimized via DiffTaichi-based simulators converge within **tens of iterations**, compared to thousands for model-free RL.
- Differentiable controller optimization converges **1–4 orders of magnitude faster** than model-free reinforcement learning.
- 10 simulators were successfully built and differentiated, covering rigid bodies, deformable objects, and fluids.

---

## Contributions
- A new differentiable programming language tailored for physical simulation with imperative style and flexible indexing.
- A two-scale AD system combining SCT (for performance) and tracing via tape (for flexibility).
- Demonstration of high productivity: differentiable simulators written in far fewer lines than CUDA equivalents.
- Open-source language, compiler, and simulator code with fully reproducible results.

---

## Limitations
- **Memory consumption**: Recording full simulation history (all timesteps of state tensors) for AD is memory-intensive; partially mitigated by checkpointing (discussed in Appendix D).
- **Global Data Access Rules**: Programmers must adapt forward simulators to satisfy write/accumulation constraints, which may require non-trivial code restructuring.
- Long simulation horizons (thousands of timesteps) with SCT can lead to long compilation times if applied naively at the whole-program level (motivating the two-scale design).

---

## Conclusion
DiffTaichi demonstrates that a carefully designed differentiable programming language — combining imperative style, megakernels, flexible indexing, and a two-scale AD system — can match hand-tuned CUDA performance while drastically reducing development effort. It enables fast gradient-based optimization of physical systems and seamless integration with neural network controllers, making it a practical tool for physics-based machine learning applications.
## Title
**DiffTaichi: Differentiable Programming for Physical Simulation**

---

## Authors
Yuanming Hu, Luke Anderson (MIT CSAIL), Tzu-Mao Li, Jonathan Ragan-Kelley (UC Berkeley), Qi Sun, Nathan Carr (Adobe Research), Frédéric Durand (MIT CSAIL)

---

## Abstract
DiffTaichi is a differentiable programming language designed for high-performance physical simulation. Built on the Taichi imperative language, it uses source code transformations to generate gradients while preserving arithmetic intensity and parallelism. A lightweight tape records the simulation structure for end-to-end backpropagation. The system is demonstrated across 10 physical simulators, achieving up to 4.2× code reduction vs. hand-written CUDA at equivalent speed, and 188× speedup over TensorFlow.

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
- Existing differentiable programming tools (TensorFlow, PyTorch) are ill-suited for physical simulation due to:
  - Low arithmetic intensity from fine-grained linear algebra operators
  - Lack of support for imperative, parallel control flows
  - Inability to express flexible, non-element-wise indexing patterns (e.g., stencils, particle-grid interactions)
- Hand-engineering differentiable simulators in CUDA is verbose and error-prone
- No existing tool provides both high performance and developer productivity for differentiable simulation

---

## Methodology
- **Two-scale Automatic Differentiation (AD) system:**
  - *Local AD (intra-kernel):* Source Code Transformation (SCT) — differentiates individual kernels with high arithmetic intensity preserved
  - *Global AD (inter-kernel):* Lightweight tape — records kernel function pointers and arguments; replays gradient kernels in reverse order during backpropagation
- **Global Data Access Rules** enforce well-defined AD semantics in imperative programs:
  1. Multiple writes to a tensor element must use atomic adds after the first write
  2. No reads may occur on an element until its accumulation is complete
- **IR preprocessing** before SCT: branch flattening and SSA (Static Single Assignment) conversion
- **Megakernel approach:** multiple computation stages fused into single kernels for efficient differentiation
- **Frontend:** embedded in Python via AST transformation; compiled, statically typed, and parallel at runtime
- Demonstrated on 10 simulators covering rigid bodies, deformable objects, and fluids

---

## Key Findings
- A differentiable elastic object simulator in DiffTaichi is:
  - **4.2× shorter** than a hand-written CUDA equivalent
  - **Equivalent in runtime performance** to the CUDA version
  - **188× faster** than a TensorFlow implementation
- Neural network controllers optimized using DiffTaichi typically converge within **tens of iterations**
- Controller optimization with differentiable simulators converges **1–4 orders of magnitude faster** than model-free RL algorithms
- The two-scale AD design avoids the trade-off between performance (SCT) and flexibility (tracing) by applying each at the appropriate level

---

## Contributions
- A new **differentiable programming language** tailored to physical simulation requirements
- A **two-scale AD system** combining SCT (local) and tape-based tracing (global)
- Support for **megakernels**, **imperative parallel programming**, and **flexible arbitrary indexing**
- Open-source implementation of **10 differentiable physical simulators**
- Empirical demonstration of productivity and performance advantages over CUDA and deep learning frameworks

---

## Limitations
- **Global Data Access Rules** require programmers to restructure code (e.g., storing full simulation history rather than only the latest state), increasing memory consumption
- Memory overhead from storing full trajectory history can be significant — partially mitigated via checkpointing (discussed in Appendix D)
- The language is embedded in Python but operates differently from Python (compiled, statically typed), which may introduce a learning curve
- SCT-based differentiation of entire simulators can result in long compilation times if applied naively at global scale (motivation for the two-scale design)

---

## Conclusion
DiffTaichi demonstrates that a purpose-built differentiable programming language significantly outperforms general-purpose ML frameworks for physical simulation tasks, both in developer productivity and runtime efficiency. Its two-scale AD system elegantly balances performance and flexibility, making it practical to build and optimize complex differentiable simulators with neural network controllers. The work highlights that domain-specific language design is a viable and effective strategy for bridging the gap between machine learning and high-performance simulation.
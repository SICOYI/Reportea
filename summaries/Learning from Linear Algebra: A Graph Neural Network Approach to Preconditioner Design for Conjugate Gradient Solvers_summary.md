## Title
Learning from Linear Algebra: A Graph Neural Network Approach to Preconditioner Design for Conjugate Gradient Solvers

## Authors
- Vladislav Trifonov (Skoltech; Sberbank AI4S Center)
- Alexander Rudikov (Skoltech; AIRI)
- Oleg Iliev (Fraunhofer ITWM)
- Yuri M. Laevsky (Institute of Computational Mathematics SB RAS)
- Ivan Oseledets (Skoltech; AIRI)
- Ekaterina Muravleva (Skoltech; Sberbank AI4S Center)

## Abstract
The paper proposes **PreCorrector**, a GNN-based method for designing preconditioners for the Conjugate Gradient (CG) solver. Rather than learning preconditioners from scratch, PreCorrector learns corrections to classical incomplete Cholesky (IC) factorizations, achieving better spectral conditioning than both classical and prior neural network-based preconditioners. A theoretically motivated loss function emphasizing low-frequency components is proposed and validated experimentally.

## Keywords
- Preconditioner design
- Graph Neural Networks (GNN)
- Conjugate Gradient (CG) method
- Sparse linear systems
- Incomplete Cholesky factorization
- Parametric PDEs
- Condition number
- Krylov subspace methods

## Research Problem
- Large, sparse, ill-conditioned linear systems arising from discretized parametric PDEs are computationally expensive to solve.
- CG convergence rate depends on √κ(A); high condition numbers slow convergence drastically.
- Existing GNN-based preconditioners **cannot outperform classical methods** in terms of CG iteration count or condition number reduction.
- Classical preconditioner construction is a trade-off between approximation quality and storage/inversion cost.

## Methodology
- **Framework:** PreCorrector learns an in-place correction to the sparse factor `L` of the classical IC(0) decomposition using a GNN, keeping the same sparsity pattern.
- **Graph representation:** The SPD matrix `A` is mapped to a graph `G = (V, E)` where off-diagonal entries are edges and right-hand side vector entries are node features.
- **Loss function:** Instead of the standard Frobenius norm `||P − A||²_F`, the authors propose a frequency-weighted objective:
  - `min ||( P − A)A⁻¹||²_F`
  - Rewritten via Hutchinson's estimator and approximated using training pairs `(xᵢ, bᵢ)` as: `L = (1/N) Σ ||L(θ)L(θ)ᵀxᵢ − bᵢ||²₂`
  - This penalizes errors in **low-frequency components** (small eigenvalues), which are most critical for CG convergence.
- **In-place update insight:** Gradient descent on IC(0) factor entries alone (without a GNN) already improves the preconditioner, motivating the GNN parameterization.
- **Dataset:** A novel generation approach with a measurable complexity metric targeting realistic parametric PDE problems.
- **Experiments:** Varying matrix sizes and dataset complexities; comparison against classical IC preconditioners and prior GNN-based methods (Li et al. 2023, Häusner et al. 2023).

## Key Findings
- The proposed loss function preferentially reduces **low-frequency errors**, which are the hardest for CG to eliminate and most physically meaningful.
- PreCorrector achieves `κ((L(θ)L(θ)ᵀ)⁻¹A) ≪ κ((LLᵀ)⁻¹A) ≪ κ(A)`, i.e., condition number reduction strictly better than the classical IC baseline.
- Classical GNN preconditioner approaches (using standard Frobenius loss) minimize high-frequency components and are suboptimal for CG.
- The in-place gradient descent experiment on IC(0) entries provides direct empirical justification for the approach.
- PreCorrector outperforms both classical and neural network-based methods on an important class of parametric PDE problems.

## Contributions
1. **Novel preconditioner design scheme** — learning a GNN-based correction to classical IC factorizations at the same sparsity level.
2. **Theoretically motivated loss function** — frequency-weighted objective emphasizing low-frequency components, with heuristic justification and experimental validation.
3. **Novel dataset generation approach** — includes a measurable complexity metric aligned with real-world parametric PDE scenarios.
4. **Extensive empirical evaluation** — across varying matrix sizes and dataset complexities, demonstrating superiority over classical and prior neural methods.

## Limitations
- The paper acknowledges that prior GNN methods could not surpass classical preconditioners; PreCorrector addresses this but the text is truncated before full experimental details are presented.
- The approach targets SPD matrices specifically (uses IC rather than ILU), limiting direct applicability to non-symmetric systems.
- GNN inference adds upfront computational cost; scalability to very large systems is not fully characterized in the available text.
- The loss function relies on availability of solution pairs `(xᵢ, bᵢ)` from training data, which may be costly to generate for complex PDEs.

## Conclusion
PreCorrector advances GNN-based preconditioner design by reframing the task as **learning a correction to an established classical preconditioner** rather than learning from scratch. The key insight is that the standard Frobenius loss is misaligned with CG's convergence behavior; a frequency-weighted loss targeting low-eigenvalue components yields preconditioners that reduce the condition number more effectively. The approach bridges classical numerical linear algebra and modern deep learning, offering a principled and practically superior alternative for solving parametric PDE-derived linear systems.
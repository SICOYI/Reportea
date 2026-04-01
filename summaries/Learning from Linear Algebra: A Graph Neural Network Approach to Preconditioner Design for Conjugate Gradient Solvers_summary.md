## Title
Learning from Linear Algebra: A Graph Neural Network Approach to Preconditioner Design for Conjugate Gradient Solvers

## Authors
- Vladislav Trifonov (Skoltech, Sberbank AI4S Center)
- Alexander Rudikov (Skoltech, AIRI)
- Oleg Iliev (Fraunhofer ITWM)
- Yuri M. Laevsky (ICM&MG SB RAS)
- Ivan Oseledets (Skoltech, AIRI)
- Ekaterina Muravleva (Skoltech, Sberbank AI4S Center)

## Abstract
The paper proposes **PreCorrector**, a GNN-based framework for preconditioner design targeting symmetric positive definite (SPD) linear systems arising from parametric PDEs. Rather than learning preconditioners from scratch, PreCorrector learns corrections to classical incomplete Cholesky (IC) factorizations, reducing the condition number more than classical or prior neural methods. A heuristic justification for the loss function emphasizing low-frequency components is also provided.

## Keywords
- Preconditioner design
- Conjugate Gradient (CG) method
- Graph Neural Networks (GNN)
- Sparse linear systems
- Incomplete Cholesky factorization
- Parametric PDEs
- Condition number

## Research Problem
- Large, sparse, ill-conditioned linear systems from parametric PDE discretizations are computationally expensive to solve.
- Classical preconditioners (IC, ILU families) reduce the condition number but have inherent limits at a fixed sparsity pattern.
- Existing GNN-based preconditioner approaches **fail to outperform classical methods** in terms of condition number reduction at the same sparsity level.
- Standard loss functions (Frobenius norm) penalize high-frequency components, which are less important for CG convergence; **low-frequency components** are more critical.

## Methodology
- **PreCorrector architecture:** GNN parameterizes corrections to the non-zero entries of a classical IC(0) Cholesky factor `L`, rather than predicting a factorization from scratch.
- **Graph representation:** The SPD matrix `A` is mapped to a graph `G = (V, E)`, where off-diagonal entries are edges and right-hand side entries are vertex features.
- **In-place ILU update:** Demonstrates via gradient descent on individual sparse matrix entries that better preconditioners at the same sparsity exist — motivating learning.
- **Loss function:** Replaces standard Frobenius loss with an A⁻¹-weighted variant:

  `L = (1/N) Σ ‖L(θ)L(θ)ᵀ xᵢ − bᵢ‖²`

  where `A⁻¹bᵢ = xᵢ`, emphasizing low-frequency (small eigenvalue) components.
- **Dataset generation:** Novel approach with a measurable complexity metric reflecting real-world parametric PDE variability (high-contrast coefficients, varying scales).
- **Experiments:** Varying matrix sizes and dataset complexities; compared against classical IC/ILU preconditioners and prior GNN-based methods (Li et al., 2023; Häusner et al., 2023).

## Key Findings
- PreCorrector **outperforms both classical preconditioners and prior GNN methods** in reducing the condition number for the tested class of parametric PDE systems.
- The A⁻¹-weighted loss function produces preconditioners with better spectral properties for CG than the standard Frobenius loss.
- Low-frequency components of the error dominate CG convergence difficulty; the proposed loss aligns training with this structure.
- In-place gradient descent experiments confirm that improved preconditioners at fixed sparsity patterns are achievable, validating the learning objective.
- Results are consistent across varying matrix sizes and dataset complexity levels.

## Contributions
1. **Novel preconditioner correction scheme:** GNN learns additive corrections to classical IC factors rather than constructing factorizations from scratch.
2. **Loss function analysis:** Provides heuristic and experimental justification for an A⁻¹-weighted loss that prioritizes low-frequency spectrum improvement.
3. **Dataset generation methodology:** Introduces a complexity metric for synthetic parametric PDE datasets that reflects real-world difficulty.
4. **Empirical validation:** Extensive experiments demonstrating superiority over classical and neural baselines across problem scales and complexities.

## Limitations
- The paper is focused on **SPD matrices** only; applicability to non-symmetric or indefinite systems is not addressed.
- The approach requires access to an initial classical IC factorization as a starting point.
- Scalability to very large systems may be constrained by GNN inference cost, though a single inference is needed before the iteration loop.
- The loss function justification remains **heuristic** rather than formally proven.
- Results are demonstrated on a specific class of parametric PDE problems; generalization to other problem types is not fully explored.

## Conclusion
PreCorrector demonstrates that combining classical linear algebra preconditioners with GNN-learned corrections is a principled and effective strategy. By initializing from reliable IC factorizations and learning targeted spectral corrections via a low-frequency-aware loss, the method achieves condition number reductions beyond what classical methods can produce at equivalent sparsity. This bridges numerical linear algebra and machine learning in a way that respects the theoretical structure of the CG solver, offering a practical path toward faster convergence in large-scale scientific computing.
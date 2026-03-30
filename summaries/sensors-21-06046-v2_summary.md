## Title
Synthetic Image Generation Using the Finite Element Method and Blender Graphics Program for Modeling of Vision-Based Measurement Systems

## Authors
- Paweł Zdziebko
- Krzysztof Holak
- Department of Robotics and Mechatronics, AGH University of Science and Technology, Krakow, Poland

## Abstract
The paper proposes a simulation pipeline that combines the Finite Element Method (FEM) with the Blender graphics program to generate synthetic images of mechanically loaded structures. The approach replaces costly physical experiments with computationally generated vision data, validated against real experimental results.

## Keywords
- Image-based measurement
- Vision sensor modeling
- Vision system simulation
- Image-based reconstruction
- Finite element method
- Physics-based computer graphics

## Research Problem
- Developing and validating vision-based measurement systems requires large amounts of experimental image data, which is time-consuming, expensive, and resource-intensive
- Damaged structures for training damage-detection algorithms are not readily available
- Existing synthetic image generation tools (game engines, standalone renderers) do not accurately reflect real mechanical deformations under load — no published validation results existed prior to this work

## Methodology
1. **FEM Simulation** — Compute displacements and deformations of the target structure under static or dynamic loads using a finite element model
2. **Blender Rendering** — Import FEM deformation results into Blender; render photorealistic synthetic images using physics-based ray tracing
3. **Custom Numerical Environment** — Authors developed their own toolchain to automate the FEM-to-Blender pipeline, supporting both static and dynamic scenarios
4. **Validation** — Compared synthetic images against real experimental captures for a complex-shaped structure
5. **Additional Test Cases:**
   - 3D reconstruction using a multi-camera system
   - Cantilever beam with simulated damage scenarios

## Key Findings
- Synthetic images generated via the FEM–Blender pipeline reliably replicate images from real experiments
- The approach successfully models both static deformation and dynamic structural behavior
- Multi-camera 3D reconstruction scenarios can be accurately simulated
- Damage scenarios (e.g., cantilever beam defects) are reproducible synthetically without physical test specimens

## Contributions
- Novel integration of FEM deformation results directly into Blender for photorealistic synthetic image generation
- Experimental validation confirming mechanical accuracy of synthetic images — a gap not previously addressed in the literature
- A configurable tool for vision system design and pre-experiment configuration
- Demonstrated applicability to complex-shaped structures, multi-camera setups, and damage detection

## Limitations
- Dense FEM meshes required for complex geometries significantly increase computation time
- Detailed illumination modeling and high-resolution texture rendering increase Blender rendering time
- In extreme cases (complex geometry + complex lighting + large images), synthetic generation may be slower than conducting real experiments

## Conclusion
The proposed FEM–Blender pipeline provides a validated, reliable method for generating synthetic vision data of mechanically loaded structures. It reduces dependence on costly physical experiments, supports controllable and repeatable damage/load scenarios, and can serve as a pre-experiment configuration tool for vision measurement systems. The validation results confirm that the synthetic images faithfully represent real experimental observations.
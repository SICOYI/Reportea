## Title
Synthetic Image Generation Using the Finite Element Method and Blender Graphics Program for Modeling of Vision-Based Measurement Systems

## Authors
- Paweł Zdziebko — Department of Robotics and Mechatronics, AGH University of Science and Technology, Krakow, Poland
- Krzysztof Holak — Department of Robotics and Mechatronics, AGH University of Science and Technology, Krakow, Poland

## Abstract
The paper proposes a simulation-based approach to generate synthetic vision data for mechanical structures under load. Finite Element Method (FEM) computes structural deformations, which are then fed into the Blender graphics program to render realistic synthetic images. The method is validated on a complex-shaped structure and demonstrated on a multi-camera 3D reconstruction scenario and a damaged cantilever beam case.

## Keywords
- Image-based measurement
- Vision sensor modeling
- Vision system simulation
- Image-based reconstruction
- Finite element method
- Physics-based computer graphics

## Research Problem
- Developing and validating image-processing algorithms for structural monitoring requires large amounts of experimental vision data (images/video of loaded, unloaded, and damaged structures).
- Physical experiments are time-consuming, expensive, and require significant human resources.
- Existing synthetic image generation methods (game engines, standalone renderers) focus on visual effects and lack validated mechanical accuracy — no published results confirm that mechanical deformations in synthetic images are physically realistic.

## Methodology
- **FEM simulation**: A finite element model of the target structure is built and solved to compute accurate deformations under static or dynamic loading conditions.
- **Blender rendering**: Computed deformation fields are exported to Blender, where physics-based ray tracing renders photorealistic synthetic images of the deformed structure.
- **Custom numerical environment**: The authors developed their own pipeline to automate the coupling between FEM results and Blender rendering.
- **Validation**: Synthetic images were compared against real experimental images of a complex-shaped structure.
- **Additional cases**:
  - 3D reconstruction using a multi-camera system
  - Structural damage scenario (cantilever beam with damage)

## Key Findings
- Synthetic images generated via the FEM–Blender pipeline reliably replicate the appearance of real experimental images.
- The approach accurately represents both static deformation states and dynamic structural responses.
- The method successfully simulates multi-camera vision configurations, supporting 3D reconstruction workflows.
- Results for damaged structures (cantilever beam) demonstrate the method's ability to model damage scenarios that are difficult or costly to reproduce experimentally.

## Contributions
- Novel integration of FEM-computed deformations with Blender's physics-based rendering for synthetic image generation.
- Experimental validation confirming mechanical realism of synthetic images — a gap not previously addressed in the literature.
- A configurable, automated pipeline enabling controllable loading conditions, damage scenarios, lighting, and camera parameters.
- A tool for pre-experiment vision system configuration, reducing the need for costly physical test setups.

## Limitations
- Complex structural geometries require dense FEM meshes, significantly increasing computation time.
- Detailed illumination modeling and high-resolution texture rendering increase Blender rendering time.
- In extreme cases (complex geometry + detailed lighting + large images), synthetic generation can be more time-consuming than physical experimentation.
- Computational cost scales with scene complexity and image size.

## Conclusion
The proposed FEM–Blender approach provides a reliable and physically accurate method for generating synthetic vision data of mechanical structures. It bridges the gap between structural simulation and vision system modeling, enabling repeatable, controlled experiments at reduced cost. The method shows strong potential as a support tool for configuring vision measurement systems and generating training data for AI-based structural monitoring applications.
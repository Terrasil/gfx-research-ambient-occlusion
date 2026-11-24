# gfx-research-ambient-occlusion

[![C++20](https://img.shields.io/badge/C%2B%2B-20-00599C.svg)](https://en.cppreference.com/w/cpp/20)
[![OpenGL 4.6](https://img.shields.io/badge/OpenGL-4.6-5586A4.svg)](https://www.opengl.org/)
[![CMake](https://img.shields.io/badge/CMake-3.25%2B-064F8C.svg)](https://cmake.org/)

A screen-space ambient occlusion study of local thickness estimation around thin rails, contacts and image borders.

[Method](#method) · [Build](#build) · [Controls](#controls) · [Experiments](#experiments) · [References](#references)

![Thin-rail ambient occlusion preview](docs/preview.png)

## Method

With normal $\mathbf n$, radius $R$ and binary geometric visibility $V_R(\mathbf p,\boldsymbol\omega)$, the reference is cosine-weighted accessibility. For a screen-space probe behind a visible surface, the approximate blocker test accepts a depth gap $\delta_z$ within thickness $T$.

```math
\begin{aligned}
A_R(\mathbf p,\mathbf n)&=\frac{1}{\pi}
  \int_{\mathbf n\cdot\boldsymbol\omega>0}
  V_R(\mathbf p,\boldsymbol\omega)(\mathbf n\cdot\boldsymbol\omega)\,d\boldsymbol\omega,\\
T(c)&=R(0.06+0.69c^2),\qquad 0.002R<\delta_z\le T(c),\\
c_{\rm local}&=\tfrac12\min(h,v),&
c_{\rm pooled}&=\tfrac14(h+v),&
c_{\rm directional}&=\tfrac12\max(h,v,d_+,d_-).
\end{aligned}
```

$h,v,d_+,d_-$ count supporting neighbors in opposite pairs. Each neighbor must satisfy a point-to-plane distance and a normal-similarity test. The geometric reference ray-traces the procedural primitives and averages two independent cosine shifts. The reports include edge and contact errors separately.

## Build

Requirements are CMake 3.25+, a C++20 compiler, Ninja, Python 3.10+ with `venv`, and desktop OpenGL 4.6 Core. Use 64-bit Python with an x64 build. CMake installs the study dependencies from `requirements.txt` in the build directory.

```powershell
cmake -S . -B out/build -G Ninja -DCMAKE_BUILD_TYPE=Release
cmake --build out/build --parallel
ctest --test-dir out/build --output-on-failure
```

Use `-DGFX_RESEARCH_BASE_LOCAL_PATH=../gfx-research-base` for a local checkout of v0.3. The headless Python runner requires desktop OpenGL 4.3. On Linux, omit `.exe` and use EGL for headless runs.

## Controls

Launch `gfx-research-ambient-occlusion.exe` for the Effect, Scene, Camera, Tests and Capture tabs. The suites are available in the viewer or through the same executable without a window. `F9` captures the current view.

## Experiments

```powershell
.\out\build\gfx-research-ambient-occlusion.exe --study run --profile smoke --out results/ao-smoke
.\out\build\gfx-research-ambient-occlusion.exe --study run --profile paper --out results/ao-paper
.\out\build\gfx-research-ambient-occlusion.exe --study analyze results/ao-paper
```

The paper quality profile uses 640 × 360, two reference shifts of 512 rays per pixel, five directional budgets up to 32 and seven scenes. The constant-slab choice is fitted at each budget on contacts and upright slats using edge MAE. Held-out scenes include rails tilted 22° and 47°, a cavity and a frustum-edge scene. Timing includes the identical 640 × 360 view for quality-cost comparison and larger resolutions for scaling.

| Output | Contents |
|---|---|
| `report/calibrated_slabs.csv` | Selection among `0.06R`, `0.25R`, `0.40R`, `0.55R` and `0.75R` |
| `report/held_out_matched_cost.csv` | Edge MAE against the best measured constant or horizon control within the candidate's GPU cost |
| `report/held_out_pareto.csv` | Nondominated measured operating points per scene |
| `quality/` and `timing/` | Raw images, geometry masks, reference shifts and GPU samples |

The horizon control is the local implementation in this project. A matched-cost comparison against the production XeGTAO implementation remains open.

## References

1. Jorge Jimenez et al. [Practical Real-Time Strategies for Accurate Indirect Occlusion](https://research.activision.com/publications/archives/atvi-tr-16-01practical-realtime-strategies-for-accurate-indirect-occlusion). Activision Research, 2016.
2. Intel. [XeGTAO](https://github.com/GameTechDev/XeGTAO). Open-source GTAO reference implementation.

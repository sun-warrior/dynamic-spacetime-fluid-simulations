# Dynamic Spacetime Fluid Cosmology (DSF Framework)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This repository contains the computational implementations accompanying the formal preprint treatise: **"A Treatise on a Novel Cosmological Model: The Dynamic Spacetime Fluid"**. 

The repository is divided into distinct computational architectures designed to mathematically test and visualize fluid-gravitational duality across quantum, stellar, and galactic scales.

---

## Repository Structure

\`\`\`text
├── comparative-surface-simulation/ # Full-stack physics and tensor solver
│   ├── engine/                     # Python core mathematical backend (TensorFlow/NumPy)
│   ├── broker/                     # TypeScript real-time state management and ZeroMQ pipeline
│   └── client/                     # Node.js frontend visualization interface
│
└── 3d-volumetric-model/            # Hardware-accelerated WebGL visualization
    └── index.html                  # Self-contained Three.js / GLSL interactive shader environment
\`\`\`

---

## 1. Running the 3D Volumetric Fluid Dynamics Simulation

The 3D volumetric model requires no backend compilation. It runs natively inside any modern web browser via WebGL, allowing for real-time manipulation of the Higgs Absorption parameter ($\alpha$) and mass density ($\rho_m$).

* **Quick Start:** Navigate to the `3d-volumetric-model/` folder and open `index.html` directly in any modern browser.
* **Live Web Deployment:** [https://sun-warrior.github.io/dynamic-spacetime-fluid-simulations/3d-volumetric-model/]

---

## 2. Running the Comparative Surface Simulation

This simulation establishes the Correspondence Principle by mapping the Dynamic Spacetime Fluid curvature against classical General Relativity. It utilizes a decoupled Python computational core paired with a TypeScript/Node.js architecture to process non-linear gradient descents.

### Prerequisites
* Python 3.9+
* Node.js (v16 or higher) and npm

### Step 1: Initialize the Python Tensor Engine
Open a terminal and navigate to the engine directory:
\`\`\`bash
cd comparative-surface-simulation/engine
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
python main.py
\`\`\`

### Step 2: Initialize the Broker
Open a second terminal window to start the ZeroMQ communication layer:
\`\`\`bash
cd comparative-surface-simulation/broker
npm install
npm run start
\`\`\`

### Step 3: Launch the Client Interface
Open a third terminal window to serve the frontend:
\`\`\`bash
cd comparative-surface-simulation/client
npm install
npm run start
\`\`\`
Access the local environment interface via your browser at `http://localhost:3000` (or the port specified by your client configuration).

---

## Citation & License

* **License:** This computational suite is released under the **Apache License 2.0**. See the `LICENSE` file for details.
* **Software DOI:** [![DOI](https://zenodo.org/badge/1327655726.svg)](https://doi.org/10.5281/zenodo.21851863)
* **Preprint Manuscript:** *(Preprints.org link pending)*

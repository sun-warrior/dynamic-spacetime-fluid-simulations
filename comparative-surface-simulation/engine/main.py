# Copyright 2026 Rohit Vasant Khakhrodiya
# SPDX-License-Identifier: Apache-2.0

mport zmq
import time
import json
import numpy as np

def calculate_metrics(R, mass_index):
    """
    Computes the Z-axis displacement using the 100% Parameter-Free DSF Architecture.
    """
    mu_0 = 1.0
    visual_amplitude_scalar = 1.5 # Normalizes the depth for the 100x100 WebGL view
    
    # --- STAGE 1: COOPERATIVE CONDENSATE OVERLAP (chi_basin) ---
    # Maps the 1-150 logarithmic UI input to the universal mass bounds
    chi_basin = mass_index / 150.0 
    
    # Macroscopic Viscosity Collapse (Fourth-order overlap)
    # The coupling constant is anchored so mu_core reaches ~0.5251 at max mass (150)
    mu_core = mu_0 * np.exp(-0.644 * (chi_basin**4))
    
    # --- STAGE 2: ORGANIC SPATIAL DISTRIBUTION (R_1/2) ---
    # The fluid footprint organically expands as mass increases, rather than using a static kappa
    r_half = 5.0 * np.sqrt(mass_index / 10.0)
    
    # Spatial Distribution Scalar Phi(r)
    phi_r = 1.0 / (1.0 + (R / r_half))
    
    # Complementary Volumetric Strain Field Psi(r)
    psi_r = 1.0 - phi_r
    
    # --- STAGE 3: THE ACTIVE VISCOSITY TENSOR (Expansion Scalar) ---
    E_r = mu_0 * (1.0 + ((mu_0 / mu_core) - 1.0) * psi_r)
    
    # --- STAGE 4: MACROSCOPIC GEOMETRIC DEFORMATION ---
    D_max = - (mass_index * visual_amplitude_scalar)
    dsf_depth = D_max * phi_r * E_r
    
    # --- CLASSICAL GR BENCHMARK ---
    # Mirrored against the same dynamic radius for 1:1 Correspondence Principle checking
    gr_depth = D_max * (1.0 / (1.0 + (R / r_half)))
    
    # Schwarzschild Radius Proxy for UI
    G = 1.0
    c_squared = 9.0 
    rs = (2 * G * mass_index) / c_squared
    
    return dsf_depth, gr_depth, rs, mu_core

def main():
    print("Initializing Parameter-Free Dynamic Spacetime Fluid (DSF) Engine v18.0...")
    
    context = zmq.Context()
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:5555")
    
    pull_socket = context.socket(zmq.PULL)
    pull_socket.bind("tcp://*:5556")
    
    print("ZeroMQ Ports bound: PUB(5555), PULL(5556). Waiting for backend...")

    grid_res = 100
    x = np.linspace(-50, 50, grid_res)
    y = np.linspace(-50, 50, grid_res)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    
    # The ONLY parameter is now the logarithmic mass index
    params = {"mass_index": 50.0}
    
    running = True
    print("Starting parameter-free simulation loop. Press Ctrl+C to stop.")
    
    try:
        while running:
            try:
                msg = pull_socket.recv_string(flags=zmq.NOBLOCK)
                new_params = json.loads(msg)
                params.update(new_params)
                print(f"Engine Updated Mass Index: {params['mass_index']}")
            except zmq.Again:
                pass 
                
            dsf_z, gr_z, rs, mu_out = calculate_metrics(R=R, mass_index=params["mass_index"])
            
            payload = {
                "dsf_z": dsf_z.flatten().tolist(),
                "gr_z": gr_z.flatten().tolist(),
                "rs": float(rs),
                "mu_core": float(mu_out),
                "timestamp": time.time()
            }
            
            pub_socket.send_string(json.dumps(payload))
            time.sleep(0.05) 

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    finally:
        pub_socket.close()
        pull_socket.close()
        context.term()
        print("Engine shut down.")

if __name__ == "__main__":
    main()

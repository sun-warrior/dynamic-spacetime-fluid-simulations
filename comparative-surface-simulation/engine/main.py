# Copyright 2026 Rohit Vasant Khakhrodiya
# SPDX-License-Identifier: Apache-2.0

import tensorflow as tf
import zmq
import time
import json
import numpy as np

def calculate_metrics(R, mass_density, base_viscosity, beta, alpha_higgs):
    """
    Computes the Z-axis displacement for both the GR benchmark and the DSF model.
    """
    # 1. GR Benchmark (Schwarzschild-like potential well)
    G = 1.0 
    rs = (2 * G * mass_density) / (3e8)**2 if mass_density > 0 else 0
    gr_depth = - (mass_density * 10.0) / (R + 2.0)
    
    # 2. Dynamic Spacetime Fluid (DSF) Calculation - DECOUPLED ARCHITECTURE
    
    # A. Absolute Amplitude (Linear Mass Scaling)
    # The maximum potential depth is driven entirely by mass and the fluid coupling constant (beta).
    # (20.0 * beta) ensures that when UI beta=0.5, the scaling perfectly matches GR's 10.0 multiplier.
    amplitude = - (mass_density * 20.0 * beta)
    
    # B. Localized Viscosity Breakdown (Exponential)
    rho_m_local = mass_density * np.exp(-(R**2) / 50.0) 
    vacuum_viscosity = 0.5 
    localized_viscosity = vacuum_viscosity + (base_viscosity - vacuum_viscosity) * np.exp(-(alpha_higgs * rho_m_local) / 10.0)
    
    # C. Spatial Distribution Function (Phi)
    # Blends the 1/R geometric falloff with fluid viscosity dampening.
    # kappa=2.0 ensures that at long ranges (where viscosity returns to 1.0), 
    # the denominator becomes (R + 2.0), perfectly converging with the GR benchmark.
    kappa = 2.0
    phi = 1.0 / (R + (kappa * localized_viscosity))
    
    # D. Final Tensor Calculation
    # Depth is the product of the linear amplitude and the viscosity-shaped spatial gradient.
    dsf_depth = amplitude * phi

    return dsf_depth, gr_depth, rs

def main():
    print("Initializing Dynamic Spacetime Fluid (DSF) Engine...")
    
    context = zmq.Context()
    
    # --- 1. ZMQ Publisher (Sends Tensor Data to Node.js) ---
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:5555")
    
    # --- 2. ZMQ Puller (Receives Parameters from Node.js) ---
    pull_socket = context.socket(zmq.PULL)
    pull_socket.bind("tcp://*:5556")
    
    print("ZeroMQ Ports bound: PUB(5555), PULL(5556). Waiting for backend...")

    # --- 3. Grid Initialization (Must match Three.js 100x100 resolution) ---
    grid_res = 100
    x = np.linspace(-50, 50, grid_res)
    y = np.linspace(-50, 50, grid_res)
    X, Y = np.meshgrid(x, y)
    
    # R is the distance from the center for each point on the grid
    R = np.sqrt(X**2 + Y**2)
    
    # Default parameters (overwritten by frontend)
    params = {
        "mass_density": 50.0,
        "base_viscosity": 1.0,
        "beta": 0.5,
        "alpha_higgs": 0.5
    }
    
    running = True
    print("Starting simulation loop. Press Ctrl+C to stop.")
    
    try:
        while running:
            # A. Non-blocking check for new UI parameters
            try:
                msg = pull_socket.recv_string(flags=zmq.NOBLOCK)
                new_params = json.loads(msg)
                params.update(new_params)
                print(f"Engine Updated Parameters: {params}")
            except zmq.Again:
                pass # No new message, continue simulation
                
            # B. Execute Physics Step
            dsf_z, gr_z, rs = calculate_metrics(
                R=R,
                mass_density=params["mass_density"],
                base_viscosity=params["base_viscosity"],
                beta=params["beta"],
                alpha_higgs=params["alpha_higgs"]
            )
            
            # C. Serialize for Three.js
            # Three.js PlaneGeometry reads data as flat 1D arrays
            payload = {
                "dsf_z": dsf_z.flatten().tolist(),
                "gr_z": gr_z.flatten().tolist(),
                "rs": float(rs),
                "timestamp": time.time()
            }
            
            # Broadcast the pure JSON string
            pub_socket.send_string(json.dumps(payload))
            
            # Throttle the loop (10-15 FPS is sufficient for frontend visualization)
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
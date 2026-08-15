# Copyright 2026 Rohit Vasant Khakhrodiya
# SPDX-License-Identifier: Apache-2.0

"""
Dynamic Spacetime Fluid (DSF) Cosmology - Single Galaxy Diagnostic Engine
Framework Version: 18.0 (Fully Dynamic Geometric Scale)
"""

import numpy as np
import matplotlib.pyplot as plt
import os

def parse_sparc_rotmod_components(filepath):
    try:
        data = np.loadtxt(filepath, comments='#')
        if data.ndim != 2 or data.shape[0] < 2:
            return None, None, None, None, None, None
        r_kpc = data[:, 0]
        V_obs = data[:, 1]
        err_v = data[:, 2]
        v_gas = data[:, 3]
        v_disk = data[:, 4]
        v_bulge = data[:, 5] if data.shape[1] > 5 else np.zeros_like(r_kpc)
        return r_kpc, V_obs, err_v, v_gas, v_disk, v_bulge
    except Exception:
        return None, None, None, None, None, None

def calculate_unified_sps_profiles(r_kpc):
    metallicity_z = 0.02 + 0.01 * np.exp(-r_kpc / 10.0)
    hydrogen_x = 0.70 + 0.05 * (1.0 - np.exp(-r_kpc / 15.0))
    helium_y = 1.0 - hydrogen_x - metallicity_z
    neutron_mass_fraction = (hydrogen_x * 0.0) + (helium_y * 0.5) + (metallicity_z * 0.51)
    upsilon_disk = 0.2 + (15.0 * metallicity_z)
    upsilon_bulge = upsilon_disk + 0.15 
    return neutron_mass_fraction, upsilon_disk, upsilon_bulge

def analyze_single_galaxy(target_file, data_dir="Rotmod_LTG"):
    # --- FUNDAMENTAL PHYSICAL CONSTANTS ---
    G = 6.67430e-11       
    c = 2.99792458e8      
    M_p = 2.17643e-8      
    H_0 = 2.2e-18         
    mu_0 = 1.0            
    hbar = 1.0545718e-34  
    v_higgs = 3.94e-8      
    
    a_cosmic = c * H_0 
    a_boundary = a_cosmic / (2.0 * np.pi)
    kpc_to_m = 3.085677581e19
    
    M_horizon = (c**3) / (G * H_0)
    kappa_q = np.sqrt(2) * (hbar * c) / (v_higgs * M_p**2)
    alpha = (4.0 / (3.0 * np.pi**2)) * np.sqrt(v_higgs / M_p)

    path = os.path.join(data_dir, target_file)
    if not os.path.exists(path):
        print(f"[ERROR] Target file '{path}' not found.")
        return

    print(f"\n[INIT] Executing Parameter-Free Diagnostics for: {target_file}")
    print("=" * 65)

    r_kpc, V_obs, err_v, v_gas, v_disk, v_bulge = parse_sparc_rotmod_components(path)
    if r_kpc is None:
        print("[ERROR] Failed to parse galaxy data.")
        return
        
    r_m = r_kpc * kpc_to_m
    neutron_frac_arr, upsilon_disk, upsilon_bulge = calculate_unified_sps_profiles(r_kpc)
    
    s_disk, s_bulge, s_gas = np.sign(v_disk), np.sign(v_bulge), np.sign(v_gas)
    v_bar_sq = (s_gas * v_gas**2) + (upsilon_disk * s_disk * v_disk**2) + (upsilon_bulge * s_bulge * v_bulge**2)
    v_bar_sq[v_bar_sq < 0] = 0
    V_bar = np.sqrt(v_bar_sq)
    
    M_enc = np.zeros_like(r_m)
    M_enc[1:] = (r_m[1:] * (V_bar[1:] * 1000.0)**2) / G
    M_enc[0] = M_enc[1]
    
    M_total = np.max(M_enc)
    half_mass_idx = np.argmin(np.abs(M_enc - (0.5 * M_total)))
    R_half = r_kpc[half_mass_idx]
    
    if R_half <= 0.0:
        R_half = np.max(r_kpc) * 0.5
        
    chi_basin = np.log(M_total / M_p) / np.log(M_horizon / M_p)
    if chi_basin < 0: 
        chi_basin = 0.0
    
    mu_core = mu_0 * np.exp(-alpha * (chi_basin**4) * kappa_q)
    
    print(f"Total Baryonic Mass (M_total) : {M_total:.4e} kg")
    print(f"Dynamic Half-Mass Rad (R_1/2) : {R_half:.4f} kpc")
    print(f"Cooperative Condensate Ratio  : {chi_basin:.6f} (chi_basin)")
    print(f"Core Viscosity Collapse       : {mu_core:.6f} (mu_core)")
    print("-" * 65)
    
    V_dsf = np.zeros_like(r_m)
    for i in range(len(r_m)):
        if r_m[i] == 0 or M_enc[i] <= 0:
            continue
        
        a_N = (G * M_enc[i]) / (r_m[i]**2)
        intrinsic_shear = np.sqrt(a_N * a_boundary)
        a_base_tensor = np.sqrt(a_N**2 + intrinsic_shear**2)
        V_base_tensor = np.sqrt(a_base_tensor * r_m[i]) / 1000.0
        
        phi_r = 1.0 / (1.0 + (r_kpc[i] / R_half))
        volumetric_strain = 1.0 - phi_r
        
        E_r = mu_0 * (1.0 + ((mu_0 / mu_core) - 1.0) * volumetric_strain)
        
        V_dsf[i] = V_base_tensor * np.sqrt(E_r)

    valid = (V_obs > 0) & (V_dsf > 0) & (~np.isnan(V_obs)) & (~np.isnan(V_dsf))
    residuals = (V_obs[valid] - V_dsf[valid]) / err_v[valid]
    chi2_red = np.sum(residuals**2) / (len(residuals) - 1) if len(residuals) > 1 else 0

    print(f"Radial Datapoints Processed   : {np.sum(valid)}")
    print(f"Reduced Chi-Squared           : {chi2_red:.4f}")
    print("=" * 65)

    # --- PLOT SINGLE ROTATION CURVE ---
    plt.figure(figsize=(10, 6))
    plt.errorbar(r_kpc, V_obs, yerr=err_v, fmt='o', color='blue', label='Observed Data ($V_{obs}$)', markersize=5, alpha=0.7)
    plt.plot(r_kpc, V_dsf, '-', color='red', linewidth=2.5, label='DSF Prediction ($V_{dsf}$)')
    plt.plot(r_kpc, V_bar, '--', color='grey', linewidth=1.5, label='Baryonic Component ($V_{bar}$)')
    
    plt.title(f'{target_file.replace("_rotmod.dat", "")} Rotation Curve\nParameter-Free DSF Engine ($R_{{1/2}}={R_half:.2f}$ kpc, $\mu_{{core}}={mu_core:.4f}$)', fontsize=13, fontweight='bold')
    plt.xlabel('Radius (kpc)', fontsize=11)
    plt.ylabel('Velocity (km/s)', fontsize=11)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    output_filename = f"{target_file.replace('.dat', '')}_DSF_Curve.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"[RENDER] Successfully saved rotation curve to: {output_filename}\n")
    
    plt.show()

if __name__ == "__main__":
    # Change this filename to test any specific galaxy in your folder
    analyze_single_galaxy(target_file="UGC02885_rotmod.dat", data_dir="Rotmod_LTG")
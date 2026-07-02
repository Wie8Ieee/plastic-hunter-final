"""
Plastic Hunter - Eco-Sonar Simulation Engine
IEEE AESS Sustainability Hackathon 2026 — Challenge 3

Implements the active sonar equation, transmission loss (spherical spreading
+ Thorp absorption), Knudsen-Wenz ambient noise, target-strength estimates
for marine plastic debris, and an eco-adaptive duty-cycle management algorithm.

Signal chain:
  Waveform (LFM chirp) → Propagation (TL) → Target (TS) → Reception (NL)
  → Detection (threshold / P_d) → Classification (debris type)
"""

import math
import random
from typing import Any, Dict, List


# ── Physical models ────────────────────────────────────────────────────────────

def sound_speed_ms(temp_c: float = 15.0, salinity_ppt: float = 35.0, depth_m: float = 50.0) -> float:
    """Mackenzie (1981) equation, valid 2–30 °C, 25–40 ppt, 0–8000 m."""
    T, S, D = temp_c, salinity_ppt, depth_m
    return (1448.96 + 4.591 * T - 5.304e-2 * T**2 + 2.374e-4 * T**3
            + 1.340 * (S - 35) + 1.630e-2 * D + 1.675e-7 * D**2
            - 1.025e-2 * T * (S - 35) - 7.139e-13 * T * D**3)


def transmission_loss_dB(range_m: float, freq_kHz: float) -> float:
    """
    Two-way transmission loss (active sonar).
    TL = 40·log10(R) + 2·alpha·R/1000   [dB]
    Thorp absorption coefficient (Thorp 1967, simplified).
    """
    if range_m < 1:
        return 0.0
    f = freq_kHz
    alpha = (0.11 * f**2 / (1 + f**2)
             + 44 * f**2 / (4100 + f**2)
             + 3e-4 * f**2 + 3.3e-3)
    return 40 * math.log10(range_m) + 2 * alpha * range_m / 1000


def ambient_noise_dB(sea_state: int, freq_kHz: float) -> float:
    """
    Knudsen-Wenz ambient noise (dB re 1 uPa^2/Hz).
    Wind/wave noise dominates 0.1–30 kHz.
    """
    wind_noise = 50.0 - 17.0 * math.log10(max(freq_kHz, 0.1)) + 5.0 * sea_state
    thermal_noise = -15.0 + 20.0 * math.log10(freq_kHz)
    return max(thermal_noise, min(90.0, wind_noise))


# ── Debris target strengths ────────────────────────────────────────────────────

DEBRIS_TARGETS = {
    "ghost_net":      {"ts": -10.0, "label": "Ghost Fishing Net",       "color": "#ef4444"},
    "plastic_drum":   {"ts": -15.0, "label": "Large Plastic Drum",      "color": "#f97316"},
    "submerged_bag":  {"ts": -25.0, "label": "Submerged Plastic Bag",   "color": "#f59e0b"},
    "foam_block":     {"ts": -28.0, "label": "Foam / Packaging Block",  "color": "#84cc16"},
    "micro_cluster":  {"ts": -40.0, "label": "Micro-Plastic Cluster",   "color": "#06b6d4"},
}

PASSIVE_BASE_PD = {
    "ghost_net": 0.62,
    "plastic_drum": 0.50,
    "submerged_bag": 0.30,
    "foam_block": 0.24,
    "micro_cluster": 0.08,
}


def _detection_explanation(
    mode: str,
    detected: bool,
    pd: float,
    snr: float | None,
    tl: float | None,
    ts: float,
    nl: float,
    sl: float,
) -> str:
    if mode == "passive":
        if detected:
            return "Passive anomaly probability is high enough for a large/noisy debris class at this range."
        return "Passive listening only: weak anomaly signature and range-dependent spreading reduce detection probability."
    if detected:
        if sl < 195:
            return "Detection succeeded: SNR remains above threshold despite reduced eco source level."
        return "Detection succeeded: enough SNR after transmission loss and ambient noise."
    if snr is not None and snr < 0:
        return "Detection failed: too much transmission loss and ambient noise left negative received SNR."
    if ts <= -30:
        return "Detection failed: weak target strength for small/soft debris produces a low echo."
    if nl > 60:
        return "Detection failed: high ambient noise from sea state masks the echo."
    if sl < 195:
        return "Detection failed: reduced source level trade-off lowered SNR below the detection threshold."
    return "Detection failed: detection probability is below the 50% decision threshold."


# ── Sonar equation ─────────────────────────────────────────────────────────────

def snr_dB(sl: float, tl: float, ts: float, nl: float, ag: float = 0.0) -> float:
    """Active sonar equation: SNR = SL - TL + TS - NL + AG."""
    return sl - tl + ts - nl + ag


def detection_probability(snr: float) -> float:
    """
    P_d sigmoid approximation for P_fa = 1e-4.
    Inflection at SNR ~ 5 dB, slope ~ 0.55 per dB.
    """
    return 1.0 / (1.0 + math.exp(-0.55 * (snr - 5.0)))


def max_range_50pct(sl: float, ts_dB: float, nl: float, freq_kHz: float) -> float:
    """Binary search for range where P_d = 50%."""
    lo, hi = 10.0, 50_000.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        tl = transmission_loss_dB(mid, freq_kHz)
        if detection_probability(snr_dB(sl, tl, ts_dB, nl)) >= 0.50:
            lo = mid
        else:
            hi = mid
    return round(lo, 0)


# ── SEL accounting ─────────────────────────────────────────────────────────────

def sel_per_ping_dB(sl: float, tau_ms: float) -> float:
    """Sound Exposure Level of one ping at 1 m: SEL = SL + 10·log10(tau_s)."""
    return sl + 10.0 * math.log10(tau_ms / 1000.0)


def cumulative_sel_dB(sel_ping: float, n_pings: int) -> float:
    """SEL_cum = SEL_ping + 10·log10(N).  Returns 0 for passive (N=0)."""
    if n_pings <= 0:
        return 0.0
    return sel_ping + 10.0 * math.log10(n_pings)


# ── Energy proxy ───────────────────────────────────────────────────────────────

def energy_reduction_pct(conv_sl: float, eco_sl: float,
                          conv_dc: float, eco_dc: float) -> float:
    """
    Acoustic energy proxy reduction (%).
    Total acoustic energy ∝ 10^(SL/10) × duty_cycle.
    Returns percentage reduction of eco vs conventional.
    """
    conv_e = 10 ** (conv_sl / 10) * max(conv_dc, 1e-9)
    eco_e  = 10 ** (eco_sl  / 10) * max(eco_dc,  1e-9)
    return round((1.0 - eco_e / conv_e) * 100.0, 1)


def trade_off_explanation(metrics: Dict[str, Any]) -> str:
    """Human-readable trade-off summary for judges / evidence sheet."""
    return (
        f"Eco-adaptive sonar achieves {metrics['sel_reduction_pct']}% reduction in "
        f"cumulative Sound Exposure Level ({metrics['sel_reduction_dB']} dB) and cuts "
        f"active-ping duty cycle by {metrics['duty_cycle_reduction_pct']}% while retaining "
        f"{metrics['eco_detection_retention_pct']}% of conventional target detections. "
        f"The accepted trade-off is a reduced max range "
        f"({metrics['eco_max_range_m']/1000:.1f} km vs {metrics['conv_max_range_m']/1000:.1f} km "
        f"conventional), which is acceptable for close-range harbour and coastal patrol."
    )


# ── Scenario runner ────────────────────────────────────────────────────────────

def run_sonar_scenario(
    source_level: float = 200.0,
    frequency_kHz: float = 10.0,
    pulse_ms: float = 100.0,
    ping_interval_s: float = 5.0,
    mission_min: float = 60.0,
    sea_state: int = 3,
    depth_m: float = 50.0,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Run a complete sonar scenario in three modes and return full metrics.

    Modes compared:
      conventional  — max SL, fixed duty cycle, always active
      eco_adaptive  — SL reduced 12 dB, ping interval x3 (67% duty-cycle cut)
      passive       — zero active pings, hydrophone listening only

    Returns JSON-serialisable dict with per-mode metrics, range sweep,
    and target-level detection results.
    """
    rng = random.Random(seed)

    # ── Environment ──────────────────────────────────────────────────────────
    nl = ambient_noise_dB(sea_state, frequency_kHz)
    cs = sound_speed_ms(depth_m=depth_m)

    # ── Conventional parameters ───────────────────────────────────────────────
    conv_dc_pct  = (pulse_ms / 1000.0) / ping_interval_s * 100.0
    conv_n_pings = int(mission_min * 60.0 / ping_interval_s)
    conv_sel_ping = sel_per_ping_dB(source_level, pulse_ms)
    conv_sel_cum  = cumulative_sel_dB(conv_sel_ping, conv_n_pings)

    # ── Eco-Adaptive parameters ───────────────────────────────────────────────
    eco_sl          = source_level - 12.0
    eco_interval    = ping_interval_s * 3.0
    eco_dc_pct      = (pulse_ms / 1000.0) / eco_interval * 100.0
    eco_n_pings     = int(mission_min * 60.0 / eco_interval)
    eco_sel_ping    = sel_per_ping_dB(eco_sl, pulse_ms)
    eco_sel_cum     = cumulative_sel_dB(eco_sel_ping, eco_n_pings)

    # ── Place random targets ──────────────────────────────────────────────────
    debris_keys = list(DEBRIS_TARGETS.keys())
    n_targets = rng.randint(4, 8)
    targets = []
    for i in range(n_targets):
        key = rng.choice(debris_keys)
        r   = round(rng.uniform(150.0, 3800.0), 0)
        angle_deg = rng.uniform(0, 360)
        target_depth = round(rng.uniform(4.0, max(6.0, min(depth_m * 0.9, 80.0))), 1)
        targets.append({
            "idx": i,
            "key": key,
            "label": DEBRIS_TARGETS[key]["label"],
            "color": DEBRIS_TARGETS[key]["color"],
            "range_m": r,
            "depth_m": target_depth,
            "angle_deg": round(angle_deg, 1),
            "ts": DEBRIS_TARGETS[key]["ts"],
        })

    # ── Run each target through sonar equation ────────────────────────────────
    def evaluate_targets(sl_active: float, mode: str) -> List[Dict]:
        out = []
        for t in targets:
            tl = None
            if mode == "passive":
                # Hydrophone-only mode can flag large/noisy debris as an acoustic anomaly,
                # but it cannot actively insonify targets. Keep this conservative and
                # range-dependent so passive listening is not overstated.
                base_pd = PASSIVE_BASE_PD.get(t["key"], 0.10)
                range_factor = math.exp(-t["range_m"] / 1800.0)
                sea_penalty = max(0.35, 1.0 - 0.08 * max(sea_state - 1, 0))
                pd = max(0.02, min(0.65, base_pd * range_factor * sea_penalty))
                s  = None
            else:
                tl = transmission_loss_dB(t["range_m"], frequency_kHz)
                s  = round(snr_dB(sl_active, tl, t["ts"], nl), 1)
                pd = detection_probability(s)
            detected = pd >= 0.50
            echo_time_s = round((2.0 * t["range_m"]) / cs, 4) if mode != "passive" and detected else None
            estimated_range_m = round((echo_time_s * cs) / 2.0, 1) if echo_time_s is not None else None
            explanation = _detection_explanation(
                mode=mode,
                detected=detected,
                pd=pd,
                snr=s,
                tl=tl,
                ts=t["ts"],
                nl=nl,
                sl=sl_active,
            )
            out.append({
                **t,
                "snr_dB": s,
                "pd": round(pd, 3),
                "detected": detected,
                "echo_return_time_s": echo_time_s,
                "estimated_range_m": estimated_range_m,
                "transmission_loss_dB": round(tl, 1) if tl is not None else None,
                "failure_reason": None if detected else explanation,
                "explanation": explanation,
            })
        return out

    conv_res    = evaluate_targets(source_level, "active")
    eco_res     = evaluate_targets(eco_sl,        "active")
    passive_res = evaluate_targets(0.0,            "passive")

    conv_det    = sum(1 for r in conv_res    if r["detected"])
    eco_det     = sum(1 for r in eco_res     if r["detected"])
    passive_det = sum(1 for r in passive_res if r["detected"])

    # ── Max detection ranges (P_d = 50%, ref target: plastic_drum) ──────────
    ref_ts = DEBRIS_TARGETS["plastic_drum"]["ts"]
    conv_maxr = max_range_50pct(source_level, ref_ts, nl, frequency_kHz)
    eco_maxr  = max_range_50pct(eco_sl,       ref_ts, nl, frequency_kHz)

    # ── SEL & duty-cycle reduction metrics ───────────────────────────────────
    sel_red_dB  = round(conv_sel_cum - eco_sel_cum, 1)
    # Energy equivalent reduction: 10^(delta/10) → linear ratio
    sel_red_pct = round((1.0 - 10.0 ** ((eco_sel_cum - conv_sel_cum) / 10.0)) * 100.0, 1)
    dc_red_pct  = round((1.0 - eco_dc_pct / max(conv_dc_pct, 0.001)) * 100.0, 1)
    eco_ret_pct = round(eco_det  / max(conv_det, 1) * 100.0, 1)
    pas_det_pct = round(passive_det / max(n_targets, 1) * 100.0, 1)

    # ── Range sweep: P_d vs range for all three modes ─────────────────────────
    sweep_ranges = [100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000]
    range_sweep = []
    for rm in sweep_ranges:
        tl = transmission_loss_dB(rm, frequency_kHz)
        c_snr = snr_dB(source_level, tl, ref_ts, nl)
        e_snr = snr_dB(eco_sl,       tl, ref_ts, nl)
        # Passive: conservative, range-limited acoustic-anomaly estimate
        sea_penalty = max(0.35, 1.0 - 0.08 * max(sea_state - 1, 0))
        p_pd = max(0.02, min(0.65, PASSIVE_BASE_PD["plastic_drum"] * math.exp(-rm / 1800.0) * sea_penalty))
        range_sweep.append({
            "range_m":    rm,
            "conv_pd":    round(detection_probability(c_snr), 3),
            "eco_pd":     round(detection_probability(e_snr), 3),
            "passive_pd": round(p_pd, 3),
        })

    # ── Multi-case validation (duty cycle sweep) ─────────────────────────────
    dc_sweep = []
    for dc_factor in [1.0, 0.75, 0.50, 0.33, 0.20, 0.10]:
        test_interval = ping_interval_s / dc_factor
        test_n = int(mission_min * 60.0 / test_interval)
        test_sel = cumulative_sel_dB(conv_sel_ping, test_n) if test_n > 0 else 0
        dc_pct = (pulse_ms / 1000.0) / test_interval * 100.0
        dc_sweep.append({
            "duty_cycle_pct": round(dc_pct, 2),
            "sel_cum_dB":     round(test_sel, 1),
            "n_pings":        test_n,
        })

    return {
        "scenario_name": "Custom Scenario",
        "environment": {
            "ambient_noise_dB":  round(nl, 1),
            "sound_speed_ms":    round(cs, 1),
            "sea_state":         sea_state,
            "depth_m":           depth_m,
        },
        "conventional": {
            "source_level_dB":   source_level,
            "duty_cycle_pct":    round(conv_dc_pct, 2),
            "ping_interval_s":   ping_interval_s,
            "n_pings":           conv_n_pings,
            "sel_cum_dB":        round(conv_sel_cum, 1),
            "max_range_m":       conv_maxr,
            "targets_detected":  conv_det,
            "total_targets":     n_targets,
            "results":           conv_res,
        },
        "eco_adaptive": {
            "source_level_dB":   round(eco_sl, 1),
            "duty_cycle_pct":    round(eco_dc_pct, 2),
            "ping_interval_s":   eco_interval,
            "n_pings":           eco_n_pings,
            "sel_cum_dB":        round(eco_sel_cum, 1),
            "max_range_m":       eco_maxr,
            "targets_detected":  eco_det,
            "total_targets":     n_targets,
            "results":           eco_res,
        },
        "passive": {
            "source_level_dB":   0,
            "duty_cycle_pct":    0,
            "n_pings":           0,
            "sel_cum_dB":        0,
            "max_range_m":       None,
            "targets_detected":  passive_det,
            "total_targets":     n_targets,
            "results":           passive_res,
        },
        "metrics": {
            "sel_reduction_dB":             sel_red_dB,
            "sel_reduction_pct":            sel_red_pct,
            "duty_cycle_reduction_pct":     dc_red_pct,
            "eco_detection_retention_pct":  eco_ret_pct,
            "passive_detection_pct":        pas_det_pct,
            "energy_reduction_pct":         energy_reduction_pct(
                                                source_level, eco_sl, conv_dc_pct, eco_dc_pct),
            "n_targets":                    n_targets,
            "conv_max_range_m":             conv_maxr,
            "eco_max_range_m":              eco_maxr,
        },
        "decision_summary": {
            "primary_technical_kpi": "Detection Coverage Retained",
            "primary_sustainability_kpi": "Acoustic Exposure Reduction",
            "conventional_detects": conv_det,
            "eco_adaptive_detects": eco_det,
            "passive_detects": passive_det,
            "what_was_saved": (
                f"{sel_red_pct}% cumulative SEL reduction, {dc_red_pct}% active duty-cycle cut, "
                f"and {energy_reduction_pct(source_level, eco_sl, conv_dc_pct, eco_dc_pct)}% acoustic energy proxy reduction."
            ),
            "what_was_traded_off": (
                f"Eco max range is {eco_maxr} m versus {conv_maxr} m conventional; "
                "some weak or distant targets may be missed under reduced source level."
            ),
            "conventional_detected_labels": [r["label"] for r in conv_res if r["detected"]],
            "eco_detected_labels": [r["label"] for r in eco_res if r["detected"]],
        },
        "range_sweep":  range_sweep,
        "dc_sweep":     dc_sweep,
        "assumptions": [
            "Simulation only: no underwater acoustic hardware has been validated yet.",
            "Transmission loss uses spherical spreading plus Thorp absorption; no bathymetry, multipath, or ray tracing.",
            "Passive mode is a conservative acoustic-anomaly estimate, not active target classification.",
            "Target strengths are representative engineering assumptions for debris classes, not measured object-specific values.",
        ],
        "validation_notes": {
            "reproducible_seed": seed,
            "reference_target": "Large Plastic Drum, TS=-15 dB re 1 m^2",
            "threshold": "P(detect) >= 0.50",
        },
        "config": {
            "source_level":    source_level,
            "frequency_kHz":   frequency_kHz,
            "pulse_ms":        pulse_ms,
            "ping_interval_s": ping_interval_s,
            "mission_min":     mission_min,
        },
    }


# ── Multi-case validation ───────────────────────────────────────────────────────

def run_multi_case_scenarios(
    source_level: float = 200.0,
    frequency_kHz: float = 10.0,
    pulse_ms: float = 100.0,
    ping_interval_s: float = 5.0,
) -> Dict[str, Any]:
    """
    Validate eco-sonar KPIs across multiple operating conditions.
    Returns structured test results ready for chart generation.
    """
    nl_ref = ambient_noise_dB(3, frequency_kHz)
    eco_sl = source_level - 12.0
    eco_interval = ping_interval_s * 3.0
    ref_ts = DEBRIS_TARGETS["plastic_drum"]["ts"]

    # Test 1: Source level sweep (SL robustness)
    sl_sweep = []
    for sl in [160, 170, 180, 190, 200, 210, 220]:
        eco = sl - 12.0
        rconv = max_range_50pct(sl,  ref_ts, nl_ref, frequency_kHz)
        reco  = max_range_50pct(eco, ref_ts, nl_ref, frequency_kHz)
        sl_sweep.append({
            "source_level_dB": sl,
            "conv_max_range_m": rconv,
            "eco_max_range_m":  reco,
            "range_retention_pct": round(reco / max(rconv, 1) * 100.0, 1),
        })

    # Test 2: Sea state (ambient noise) sweep
    ss_sweep = []
    for ss in [1, 2, 3, 4, 5]:
        nl = ambient_noise_dB(ss, frequency_kHz)
        rconv = max_range_50pct(source_level, ref_ts, nl, frequency_kHz)
        reco  = max_range_50pct(eco_sl,       ref_ts, nl, frequency_kHz)
        ss_sweep.append({
            "sea_state": ss,
            "ambient_noise_dB": round(nl, 1),
            "conv_max_range_m": rconv,
            "eco_max_range_m":  reco,
            "range_retention_pct": round(reco / max(rconv, 1) * 100.0, 1),
        })

    # Test 3: Duty cycle / SEL trade-off sweep
    conv_sel_ping = sel_per_ping_dB(source_level, pulse_ms)
    dc_sweep = []
    for factor in [1.0, 0.75, 0.50, 0.33, 0.20, 0.10]:
        interval = ping_interval_s / factor
        dc_pct   = (pulse_ms / 1000.0) / interval * 100.0
        n_pings  = int(60.0 * 60.0 / interval)
        sel      = cumulative_sel_dB(conv_sel_ping, n_pings) if n_pings > 0 else 0.0
        dc_sweep.append({
            "duty_cycle_pct":              round(dc_pct, 2),
            "sel_cum_dB":                  round(sel, 1),
            "n_pings":                     n_pings,
            "dc_reduction_vs_baseline_pct": round((1.0 - factor) * 100.0, 1),
        })

    # Test 4: Energy reduction across SL + DC combined
    energy_table = []
    for sl_delta in [0, -3, -6, -9, -12, -15]:
        for dc_factor in [1.0, 0.67, 0.5, 0.33]:
            conv_e = 10 ** (source_level / 10) * 1.0
            eco_e  = 10 ** ((source_level + sl_delta) / 10) * dc_factor
            e_red  = round((1.0 - eco_e / conv_e) * 100.0, 1)
            energy_table.append({
                "sl_delta_dB":      sl_delta,
                "dc_factor":        dc_factor,
                "energy_reduction_pct": e_red,
            })

    return {
        "source_level_sweep": sl_sweep,
        "sea_state_sweep":    ss_sweep,
        "duty_cycle_sweep":   dc_sweep,
        "energy_table":       energy_table,
        "summary": {
            "eco_sl_delta_dB":       -12.0,
            "eco_dc_factor":         1.0 / 3.0,
            "eco_energy_reduction_pct": round((1.0 - (10 ** (-12.0 / 10)) / 3.0) * 100.0, 1),
            "sea_states_tested":     len(ss_sweep),
            "sl_levels_tested":      len(sl_sweep),
        },
    }

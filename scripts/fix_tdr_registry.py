#!/usr/bin/env python3
"""
fix_tdr_registry.py — Apply Windows TDR registry fix to prevent GPU lost during training.

ROOT CAUSE:
  Windows WDDM Timeout Detection and Recovery (TDR) has a default TdrDelay of 2 seconds.
  During PyTorch fine-tuning (especially at eval time with predict_with_generate=True),
  CUDA kernels can legitimately run for 5-30+ seconds. WDDM interprets this as a GPU
  freeze, fires TDR recovery, and if recovery fails, marks the GPU as "GPU is lost".

  On this machine:
    - GPU 0 (PCIe 01:00.0) = WDDM primary display adapter (TDR fires here first)
    - GPU 1 (PCIe 05:00.0) = secondary compute GPU (caption_images.py runs here)
    - Default TdrDelay = 2 seconds (way too short for training workloads)

REGISTRY FIX:
  Set TdrDelay=60 (seconds) in HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers
  This tells WDDM to wait 60 seconds before declaring a GPU as hung.
  This is the recommended fix for ML training workloads on Windows.

  TdrLevel=3 (default) = attempt recovery
  TdrDelay=60 = wait 60 seconds before recovery attempt
  TdrDdiDelay=60 = wait 60 seconds for DDI command

REQUIRES: Administrator privileges (run as Administrator)
"""

import subprocess
import sys
import ctypes
import os


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def apply_tdr_fix():
    key = r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"

    settings = [
        ("TdrDelay",    "REG_DWORD", "60"),   # seconds before TDR fires (default: 2)
        ("TdrDdiDelay", "REG_DWORD", "60"),   # seconds for DDI command (default: 5)
        ("TdrLevel",    "REG_DWORD", "3"),    # 3=recover (keep default, just set explicitly)
    ]

    print("Applying TDR registry fix for ML training on Windows WDDM...")
    print(f"Key: {key}")
    print()

    for name, typ, val in settings:
        cmd = ["reg", "add", key, "/v", name, "/t", typ, "/d", val, "/f"]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0:
            print(f"  SET {name} = {val}  [OK]")
        else:
            print(f"  FAILED {name}: {r.stderr.strip()}")

    print()
    print("IMPORTANT: Reboot required for TDR settings to take effect.")
    print()
    print("After reboot:")
    print("  1. Verify GPU 0 is accessible: nvidia-smi")
    print("  2. Run finetune with CUDA_VISIBLE_DEVICES=1 to use GPU 1 (compute-only)")
    print("  3. GPU 1 is now protected from TDR via the extended TdrDelay")


def verify_settings():
    key = r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    print("Current TDR registry settings:")
    for name in ["TdrDelay", "TdrDdiDelay", "TdrLevel", "TdrLimitTime", "TdrLimitCount"]:
        cmd = ["reg", "query", key, "/v", name]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0:
            # Parse value from reg query output
            for line in r.stdout.splitlines():
                line = line.strip()
                if name in line:
                    print(f"  {line}")
        else:
            print(f"  {name} = (not set, using Windows default)")


if __name__ == "__main__":
    print("=" * 60)
    print("  Windows TDR Fix for ML Training (GPU Lost Prevention)")
    print("=" * 60)
    print()

    if "--verify" in sys.argv:
        verify_settings()
        sys.exit(0)

    if not is_admin():
        print("ERROR: This script requires Administrator privileges.")
        print()
        print("Run one of:")
        print("  1. Right-click terminal -> Run as Administrator, then run this script")
        print("  2. python scripts/fix_tdr_registry.py  (from an admin terminal)")
        print()
        print("Or apply manually via regedit:")
        print(r"  HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers")
        print("  TdrDelay    REG_DWORD  60")
        print("  TdrDdiDelay REG_DWORD  60")
        sys.exit(1)

    print("Running as Administrator: OK")
    print()
    apply_tdr_fix()
    print()
    print("Verifying applied settings:")
    verify_settings()

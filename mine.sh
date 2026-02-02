#!/bin/bash

# GhostShell Autonomous Mining Script
# Starts simulation, orchestrator, and mining loop.

# Kill any existing processes on ports 5001 (Sim) and 8001 (Orchestrator)
echo "[GhostShell] Clearing previous instances..."
kill $(lsof -t -i :5001) 2>/dev/null
kill $(lsof -t -i :8001) 2>/dev/null

# Start Simulation
echo "[GhostShell] Starting Simulation Kernel..."
cd TrainLLM
python3 full_cyclekernel_buildA_FH_complete.py > logs/sim_kernel.log 2>&1 &
SIM_PID=$!
echo "[GhostShell] Simulation running (PID: $SIM_PID)"
cd ..

# Start Orchestrator
echo "[GhostShell] Starting Unified Orchestrator..."
python3 unified_llm_integration.py > TrainLLM/logs/orchestrator.log 2>&1 &
ORCH_PID=$!
echo "[GhostShell] Orchestrator running (PID: $ORCH_PID)"

# Wait for startup
sleep 5

# Mining Loop
echo "[GhostShell] Entering Autonomous Mining Loop..."
echo "[GhostShell] Entering Autonomous Mining Loop..."
while true; do
    echo "[GhostShell] Mining sequence initiated..."
    cd TrainLLM
    if python3 seed_generator.py >> logs/mining.log 2>&1; then
        echo "[GhostShell] Mining success. Heartbeat updated."
    else
        echo "[WARN] Mining script returned non-zero exit code. Checking logs."
    fi
    cd ..
    
    # Check if simulation is still alive
    if ! kill -0 $SIM_PID 2>/dev/null; then
        echo "[FATAL] Simulation Kernel died! Restarting..."
        cd TrainLLM
        python3 full_cyclekernel_buildA_FH_complete.py > logs/sim_kernel.log 2>&1 &
        SIM_PID=$!
        cd ..
    fi
    
    sleep 30  # Mine every 30 seconds
done

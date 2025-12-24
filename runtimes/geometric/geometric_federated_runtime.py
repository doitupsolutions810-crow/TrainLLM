#!/usr/bin/env python3
# =============================================================================
# Geometric Federated Grokking — Headless Runtime Substrate with API Pipeline Streaming
# Self-evolving, immutable, replayable, container-ready, with generated frontend, Merkle snapshots,
# ZK-proof placeholders, multi-node federation, RedTeam alerts, deterministic replay, and memory compression
# =============================================================================

import os
import json
import time
import hashlib
import threading
import queue
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
from collections import deque
import http.server
import socketserver
import requests  # For multi-node federation
import snappy  # For memory compression

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class IntentChart:
    centroid: np.ndarray
    members: List[np.ndarray]
    radius: float
    id: str

@dataclass
class WorldNode:
    world_id: str
    intent_chart: IntentChart
    activation_strength: float
    last_active: float
    intent_history: deque = field(default_factory=lambda: deque(maxlen=16))
    last_signature: 'WorldSignature' = None  # For phase shift detection

@dataclass
class LoopEvent:
    index: int
    timestamp: float
    user_id: str
    world_id: str
    intent_vector: List[float]
    goal_mode: str
    accepted: bool
    prev_hash: str
    event_hash: str
    zk_proof: str  # Placeholder for ZK-SNARK/STARK proof

@dataclass
class WorldSignature:
    curvature: float
    entropy: float

# =============================================================================
# GEOMETRIC PRIMITIVES
# =============================================================================

def assign_to_charts(intent_vec, charts, max_radius=0.35):
    for chart in charts:
        dist = np.linalg.norm(intent_vec - chart.centroid)
        if dist <= max_radius:
            chart.members.append(intent_vec)
            chart.centroid = np.mean(chart.members, axis=0)
            chart.radius = max(chart.radius, dist)
            return chart

    new_chart = IntentChart(
        centroid=intent_vec,
        members=[intent_vec],
        radius=0.0,
        id=f"chart_{len(charts)+1}"
    )
    charts.append(new_chart)
    return new_chart


def compute_curvature(vectors):
    if len(vectors) < 3:
        return 0.0
    angles = []
    for i in range(2, len(vectors)):
        v1 = vectors[i-1] - vectors[i-2]
        v2 = vectors[i] - vectors[i-1]
        cos = np.dot(v1, v2) / (np.linalg.norm(v1)*np.linalg.norm(v2)+1e-9)
        angles.append(np.arccos(np.clip(cos, -1, 1)))
    return float(np.mean(angles))


def compute_entropy(vectors):
    norms = np.linalg.norm(np.stack(vectors), axis=1)
    p = np.exp(norms) / np.sum(np.exp(norms))
    return float(-np.sum(p * np.log(p + 1e-9)))


def compute_merkle_root(hashes: List[str]) -> str:
    if not hashes:
        return "0"
    current = hashes[:]
    while len(current) > 1:
        new_level = []
        for i in range(0, len(current), 2):
            h1 = current[i]
            h2 = current[i + 1] if i + 1 < len(current) else h1
            combined = h1 + h2
            new_level.append(hashlib.sha256(combined.encode()).hexdigest())
        current = new_level
    return current[0]


def generate_zk_proof(event_data: str) -> str:
    # Placeholder for ZK-SNARK/STARK proof generation
    # In a real implementation, use a ZK library to prove event integrity without revealing details
    # Here, use a simple hash-based "proof" as mock (e.g., SHA256 of event + salt)
    salt = "zk_placeholder_salt_2025"
    proof_input = event_data + salt
    return hashlib.sha256(proof_input.encode()).hexdigest()


def detect_phase_shift(world: WorldNode, new_signature: WorldSignature, threshold=0.1) -> bool:
    if world.last_signature is None:
        return False
    delta_curvature = abs(new_signature.curvature - world.last_signature.curvature)
    delta_entropy = abs(new_signature.entropy - world.last_signature.entropy)
    return delta_curvature > threshold or delta_entropy > threshold

# =============================================================================
# FEDERATED TOPOLOGY ENGINE
# =============================================================================

class FederatedRuntime:
    def __init__(self, log_path="/data/loop_memory.jsonl", epoch_size=10, seed=42, federation_peers=None, redteam_webhook=None):
        self.charts = []
        self.worlds: Dict[str, WorldNode] = {}
        self.signatures: Dict[str, WorldSignature] = {}
        self.loop_index = 0
        self.last_hash = "GENESIS"
        self.log_path = log_path
        self.compressed_log_path = log_path + ".snappy"
        self.stream = queue.Queue()
        self.current_epoch: List[str] = []
        self.epoch_size = epoch_size
        self.epoch_log_path = "epoch_merkle.jsonl"
        self.seed = seed
        self.federation_peers = federation_peers or []  # List of peer URLs, e.g., ['http://peer1:8000', 'http://peer2:8000']
        self.redteam_webhook = redteam_webhook  # Optional webhook URL for RedTeam alerts

        os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
        os.makedirs(os.path.dirname(self.epoch_log_path) or ".", exist_ok=True)

    # -------------------------------------------------------------------------

    def update(self, intent_vec, user_id="agent", goal_mode="default", accepted=True):
        chart = assign_to_charts(intent_vec, self.charts)

        world = self._get_or_create_world(chart)
        world.intent_history.append(intent_vec)
        world.activation_strength += 1.0
        world.last_active = time.time()

        new_signature = WorldSignature(
            curvature=compute_curvature(list(world.intent_history)),
            entropy=compute_entropy(list(world.intent_history))
        )
        self.signatures[world.world_id] = new_signature

        if detect_phase_shift(world, new_signature):
            self._trigger_redteam_alert(world.world_id, new_signature, goal_mode)

        world.last_signature = new_signature

        event = self._commit_event(
            world.world_id,
            intent_vec.tolist(),
            user_id,
            goal_mode,
            accepted
        )

        self.stream.put(event)

        # Federate: Broadcast event to peers
        self._broadcast_to_peers(event)

    # -------------------------------------------------------------------------

    def _get_or_create_world(self, chart):
        for world in self.worlds.values():
            if world.intent_chart.id == chart.id:
                return world

        wid = f"world_{len(self.worlds)+1}"
        world = WorldNode(
            world_id=wid,
            intent_chart=chart,
            activation_strength=1.0,
            last_active=time.time()
        )
        self.worlds[wid] = world
        return world

    # -------------------------------------------------------------------------

    def _commit_event(self, world_id, intent_vec, user_id, goal_mode, accepted):
        payload = {
            "index": self.loop_index,
            "timestamp": time.time(),
            "user_id": user_id,
            "world_id": world_id,
            "intent_vector": intent_vec,
            "goal_mode": goal_mode,
            "accepted": accepted,
            "prev_hash": self.last_hash
        }

        raw = json.dumps(payload, sort_keys=True)
        event_hash = hashlib.sha256(raw.encode()).hexdigest()
        zk_proof = generate_zk_proof(raw)

        event = LoopEvent(
            **payload,
            event_hash=event_hash,
            zk_proof=zk_proof
        )

        with open(self.log_path, "a") as f:
            f.write(json.dumps(event.__dict__) + "\n")

        self.last_hash = event_hash
        self.loop_index += 1

        self.current_epoch.append(event_hash)
        if len(self.current_epoch) == self.epoch_size:
            root = compute_merkle_root(self.current_epoch)
            epoch_data = {
                "epoch": self.loop_index // self.epoch_size,
                "merkle_root": root,
                "timestamp": time.time()
            }
            with open(self.epoch_log_path, "a") as f:
                f.write(json.dumps(epoch_data) + "\n")
            print(f"Merkle root for epoch {epoch_data['epoch']}: {root}")
            self._compress_memory()
            self.current_epoch = []

        return event

    # -------------------------------------------------------------------------

    def _trigger_redteam_alert(self, world_id, signature, goal_mode):
        alert = f"Phase shift detected in {world_id}: curvature={signature.curvature}, entropy={signature.entropy}, goal_mode={goal_mode}"
        print(f"RedTeam Alert: {alert}")
        if self.redteam_webhook:
            try:
                requests.post(self.redteam_webhook, json={"alert": alert})
            except Exception as e:
                print(f"Failed to send RedTeam webhook: {e}")

    # -------------------------------------------------------------------------

    def _broadcast_to_peers(self, event):
        event_data = json.dumps(event.__dict__)
        for peer in self.federation_peers:
            try:
                requests.post(f"{peer}/federate", json={"event": event_data})
            except Exception as e:
                print(f"Failed to broadcast to {peer}: {e}")

    # -------------------------------------------------------------------------

    def receive_federation_event(self, event_data):
        # Converge worlds from peer events
        event = LoopEvent(**event_data)
        # Simplified: Update if hash chain matches or merge charts if compatible
        if event.prev_hash == self.last_hash:
            self.update(np.array(event.intent_vector), event.user_id, event.goal_mode, event.accepted)
        else:
            print(f"Federation mismatch for event {event.index}")

    # -------------------------------------------------------------------------

    def _compress_memory(self):
        # Compress log after epoch: Use snappy to compress jsonl
        with open(self.log_path, "rb") as f:
            data = f.read()
        compressed = snappy.compress(data)
        with open(self.compressed_log_path, "wb") as f:
            f.write(compressed)
        # Summarize: Keep only epoch summaries, truncate full log
        summary = {"epochs": self.loop_index // self.epoch_size, "worlds": len(self.worlds)}
        with open(self.log_path, "w") as f:  # Truncate to summaries
            f.write(json.dumps(summary) + "\n")
        print("Memory compressed and summarized")

    # -------------------------------------------------------------------------

    def replay(self, deterministic=False):
        if deterministic:
            # Deterministic replay: Regenerate history with same seed
            np.random.seed(self.seed)
            self.__init__(self.log_path, self.epoch_size, self.seed, self.federation_peers, self.redteam_webhook)
            for _ in range(self.loop_index):
                self.update(np.random.normal(0, 1, 3))  # Assume dim=3
            print("Deterministic replay completed")
        else:
            # Standard replay from log
            self.__init__(self.log_path, self.epoch_size, self.seed, self.federation_peers, self.redteam_webhook)
            with open(self.log_path, "r") as f:
                for line in f:
                    e = json.loads(line)
                    self.last_hash = e["event_hash"]
                    self.loop_index = e["index"] + 1
                    self.current_epoch.append(e["event_hash"])
                    if len(self.current_epoch) == self.epoch_size:
                        root = compute_merkle_root(self.current_epoch)
                        self.current_epoch = []

    # -------------------------------------------------------------------------

    def stream_events(self):
        while True:
            yield self.stream.get()

# =============================================================================
# RUNTIME LOOP (SELF‑EVOLVING, DETERMINISTIC)
# =============================================================================

def intent_generator(dim=3, seed=42):
    np.random.seed(seed)  # Deterministic for replay and federation
    while True:
        yield np.random.normal(0, 1, dim)

# =============================================================================
# API PIPELINE STREAMING SERVICE WITH GENERATED FRONTEND
# =============================================================================

frontend_html = """
... (truncated for brevity in file)

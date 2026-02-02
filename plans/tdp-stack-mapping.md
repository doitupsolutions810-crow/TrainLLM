# TDP-to-Stack Mapping: Organism Applied to Anti4

## Global Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TDP TRIANGLE INVARIANT                               │
│                                                                             │
│   ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐│
│   │  HOST AUTHORITY │◄────────►│   MESH AGENT    │◄────────►│ RUNTIME ENGINE  ││
│   │   (Port 8080)   │  policy  │   (Port 3000)   │   exec   │   (Port 7070)   ││
│   │                 │  identity│                 │          │                 ││
│   └────────┬────────┘          └────────┬────────┘          └────────┬────────┘│
│            │                            │                            │         │
│            │    registry events         │                            │         │
│            └────────────────────────────┴────────────────────────────┘         │
│                                      │                                       │
│                              adapters (framework)                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: HOST AUTHORITY (Go)

**Role:** Identity issuance, policy evaluation, registry maintenance.

**Current Stack Mapping:**

| TDP Component | File Location | Current State | TDP Target |
|---------------|---------------|---------------|------------|
| Identity Issuer | [`TrainLLM/backend/src/attestor.ts`](TrainLLM/backend/src/attestor.ts:6) | ✅ Partial (genesis attestation) | DID-based identity service |
| Policy Evaluator | [`TrainLLM/governance.ts`](TrainLLM/governance.ts:4) | ✅ Partial (attestation validation) | Time-bounded capability signing |
| Registry | [`TrainLLM/src/memory-loop.ts`](TrainLLM/src/memory-loop.ts:3) | ⚠️ Basic logging | Append-only cryptographic chain |

### Files to Create/Modify

```
organism/host-authority/
├── main.go                    # HTTP server :8080
├── identity/
│   └── service.go            # DID issuance
├── policy/
│   └── evaluator.go          # Capability signing
└── registry/
    └── store.go              # Cryptographic event log
```

### Current Code to Refactor

**Refactor [`TrainLLM/governance.ts`](TrainLLM/governance.ts:4) → Host Authority Service**

```go
// host-authority/policy/evaluator.go
type PolicyRequest struct {
    Identity string `json:"identity"`
    Action   string `json:"action"`
}

type PolicyDecision struct {
    Decision   string    `json:"decision"`
    ExpiresAt  time.Time `json:"expires_at"`
    Signature  string    `json:"signature"`  // SHA-256 of (identity + action + expiry)
}

func EvaluatePolicy(w http.ResponseWriter, r *http.Request) {
    var req PolicyRequest
    json.NewDecoder(r.Body).Decode(&req)
    
    decision := PolicyDecision{
        Decision:   "allow",  // TODO: real policy evaluation
        ExpiresAt:  time.Now().Add(5 * time.Minute),
    }
    
    hash := sha256.Sum256([]byte(req.Identity + req.Action + decision.ExpiresAt.String()))
    decision.Signature = string(hash[:])
    
    json.NewEncoder(w).Encode(decision)
}
```

---

## Layer 2: RUNTIME ENGINE (Node.js)

**Role:** Pure execution substrate with framework adapters.

**Current Stack Mapping:**

| TDP Component | File Location | Current State | TDP Target |
|---------------|---------------|---------------|------------|
| HTTP Server | [`TrainLLM/src/server.ts`](TrainLLM/src/server.ts:10) | ⚠️ Collapsed with authority | Dedicated Express server :7070 |
| Adapter Loader | [`TrainLLM/src/llm-adapter.ts`](TrainLLM/src/llm-adapter.ts:2) | ⚠️ Placeholder | Framework adapter registry |
| Execution | `/execute` endpoint | ⚠️ Collapsed | `/run` endpoint with adapters |

### Files to Create/Modify

```
organism/runtime-engine/
├── server.js                 # Express server :7070
├── adapters/
│   ├── index.js             # Adapter registry
│   ├── react.js             # React component rendering
│   ├── python.js            # Python script execution
│   └── llm.js               # LLM inference (current)
└── middleware/
    └── capability-validate.js  # Capability verification
```

### Current Code to Refactor

**Refactor [`TrainLLM/src/llm-adapter.ts`](TrainLLM/src/llm-adapter.ts:2) → Runtime Adapters**

```javascript
// runtime-engine/adapters/llm.js
export default {
  async execute(action, payload) {
    switch (action) {
      case 'generate':
        return await this.llm.generate(payload.prompt);
      case 'analyze':
        return await this.llm.analyze(payload.context);
      default:
        throw new Error(`Unknown LLM action: ${action}`);
    }
  }
};

// runtime-engine/server.js
app.post('/run', async (req, res) => {
  const { framework, action, payload, capability } = req.body;
  
  // Validate capability (verify signature, check expiry)
  const valid = await validateCapability(capability);
  if (!valid) return res.status(403).json({ error: 'Invalid capability' });
  
  const adapter = await loadAdapter(framework);
  const result = await adapter.execute(action, payload);
  res.json({ ok: true, result });
});
```

---

## Layer 3: MESH AGENT (Rust)

**Role:** Active entity that obtains identity, requests policy, invokes runtime, records results.

**Current Stack Mapping:**

| TDP Component | File Location | Current State | TDP Target |
|---------------|---------------|---------------|------------|
| Agent Core | [`TrainLLM/frontend/pages/api/governance.ts`](TrainLLM/frontend/pages/api/governance.ts:3) | ⚠️ API proxy | Rust binary with TDP client |
| Identity Request | Implicit in JWT | ⚠️ Hardcoded | DID request to Authority |
| Policy Request | [`TrainLLM/src/auth.ts`](TrainLLM/src/auth.ts:3) | ⚠️ JWT capability | Policy evaluation API call |
| Execution | [`TrainLLM/src/server.ts:29`](TrainLLM/src/server.ts:29) | ⚠️ Direct execution | Runtime Engine invocation |
| Registry | [`TrainLLM/src/memory-loop.ts`](TrainLLM/src/memory-loop.ts:3) | ⚠️ File append | Registry event emission |

### Files to Create/Modify

```
organism/mesh-agent/
├── Cargo.toml
├── src/
│   ├── main.rs              # Agent orchestration
│   ├── identity.rs          # DID request to Authority
│   ├── policy.rs            # Policy evaluation request
│   ├── executor.rs          # Runtime Engine client
│   └── registry.rs          # Event emission
└── config.toml
```

### Current Code to Refactor

**Refactor [`TrainLLM/frontend/pages/api/governance.ts`](TrainLLM/frontend/pages/api/governance.ts:3) → Mesh Agent Client**

```rust
// mesh-agent/src/main.rs
#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // 1. Obtain identity from Host Authority
    let did = identity::obtain("http://localhost:8080/identity/issue").await?;
    
    // 2. Request policy decision for action
    let allowed = policy::authorize(
        "http://localhost:8080/policy/evaluate",
        &did,
        "generate_summary"
    ).await?;
    
    if allowed {
        // 3. Invoke Runtime Engine
        let result = executor::run_runtime(
            "http://localhost:7070/run",
            "llm",
            "generate",
            payload
        ).await?;
        
        // 4. Record result to Registry
        registry::record(
            "http://localhost:8080/registry/event",
            &did,
            "generate_summary",
            &result
        ).await?;
        
        println!("Execution complete: {}", result);
    } else {
        println!("Execution denied by policy");
    }
    
    Ok(())
}
```

---

## Layer 4: REGISTRY (Append-Only)

**Role:** Order-preserving, non-repudiable event log.

**Current Stack Mapping:**

| TDP Requirement | Current Implementation | Gap |
|-----------------|------------------------|-----|
| Append-only | [`action-log.jsonl`](TrainLLM/src/memory-loop.ts:10) | ⚠️ No cryptographic protection |
| Order-preserving | Line-by-line append | ⚠️ No sequence numbers |
| Identity binding | None | ❌ Missing |
| Result hashing | None | ❌ Missing |
| Timestamp | ✅ Present | ✅ OK |
| Policy reference | None | ❌ Missing |

### Files to Create/Modify

```
organism/host-authority/registry/
├── store.go                 # Append-only store
├── chain.go                # Hash chain (previousHash)
└── query.go                # Event query API
```

### Registry Entry Schema

```json
{
  "id": "urn:uuid:...",
  "identity": "did:organism:...",
  "action": "generate_summary",
  "resultHash": "sha256:...",
  "previousHash": "sha256:...",
  "timestamp": "2026-01-29T09:00:00Z",
  "policyRef": "did:organism:policy:..."
}
```

---

## Current Stack Components → TDP Mapping Summary

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           CURRENT STACK                                     │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  TrainLLM/                                                                │
│  ├── backend/src/attestor.ts ───────► HOST AUTHORITY (Identity)           │
│  ├── governance.ts ─────────────────► HOST AUTHORITY (Policy)             │
│  ├── src/server.ts ─────────────────► [COLLAPSED - needs split]           │
│  ├── src/auth.ts ──────────────────► MESH AGENT (Capabilities)            │
│  ├── src/memory-loop.ts ───────────► REGISTRY (Logging)                   │
│  └── src/llm-adapter.ts ───────────► RUNTIME ENGINE (Adapter)             │
│                                                                            │
│  v0-ai-agent-for-servers/                                                 │
│  ├── src/app/api/* ────────────────► MESH AGENT (API Routes)              │
│  └── src/components/* ─────────────► MESH AGENT (Frontend)                │
│                                                                            │
│  ghostshell/ ──────────────────────► [EMPTY - future Agent deployment]    │
│                                                                            │
│  kube/ ───────────────────────────► [EMPTY - Kubernetes manifests]         │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Deployment Mapping (docker-compose)

```yaml
# deploy/docker-compose.yml
version: "3.9"

services:
  authority:
    build: ./host-authority
    ports:
      - "8080:8080"
    volumes:
      - registry-data:/data

  runtime:
    build: ./runtime-engine
    ports:
      - "7070:7070"
    depends_on:
      - authority

  # Mesh Agent runs as cron job or daemon
  mesh-agent:
    build: ./mesh-agent
    depends_on:
      - authority
      - runtime
    environment:
      - AUTHORITY_URL=http://authority:8080
      - RUNTIME_URL=http://runtime:7070

volumes:
  registry-data:
```

---

## Implementation Priority

| Phase | Component | Files | Effort |
|-------|-----------|-------|--------|
| 1 | Host Authority | [`host-authority/main.go`](organism/host-authority/main.go) | Medium |
| 2 | Runtime Engine | [`runtime-engine/server.js`](organism/runtime-engine/server.js) | Low |
| 3 | Registry Store | [`host-authority/registry/store.go`](organism/host-authority/registry/store.go) | Medium |
| 4 | Mesh Agent | [`mesh-agent/src/main.rs`](organism/mesh-agent/src/main.rs) | High |
| 5 | Integration | Docker Compose | Low |

---

## Next Steps

1. **User Feedback**: Confirm mapping is accurate for your use cases
2. **Phase 1**: Implement Host Authority (Go) with identity + policy + registry
3. **Phase 2**: Extract Runtime Engine (Node.js) from TrainLLM
4. **Phase 3**: Build Mesh Agent (Rust) as separate binary
5. **Phase 4**: Run full integration test with docker-compose

# SYSTEM_ACCESS

Self-readable entry point on the default branch for the TrainLLM cryptographic authority and self-model layer.

## Role in the compile

TrainLLM attests, signs, logs disagreement, and compiles its own signed claims into training data. It is the system's self-model — and was the softest seam until the emergent-compile audit.

## Key files

- `utils/crypto.ts` — real ed25519 signing.
- `governance/` — blake3 proof-hash recomputation, append-only action log, model-disagreement logger.
- `attestor` — chained signed envelopes with previousHash links.
- `compiler.ts` — turns attestations into LLM training JSONL. The loop-closing piece: the system trains on its own certified claims.
- `agent-capabilities.json` — six agents with allow/deny, child-subset invariant.
- Emergent-compile branch carries: zk.ts renamed from placeholder to actionDigest (or real proof), verifyCapability allow-list instead of hardcoded scale-sla string, /token route gated behind authorize, CycleKernel trust swapped from random.uniform to evidence snapshot.

## Invariants

- Training corpus carries provenance deep enough to walk back to human root.
- No dev-secret in production; /token is not a public faucet.
- zk is either real or honestly named.
- verifyCapability checks the token's actual claim, not a literal string.

## Adjacent layers

- Provides the cryptographic spine CONTROL12's ledger lacked.
- Reads CycleKernel's simulation for proposal generation (now evidence-based, not dice).
- capability-plane/capability-authority share its AttestPipe and SPIFFE patterns.

## The profound seam

A system that learns from its own output must ensure its output is trustworthy. Before the audit, TrainLLM signed forgeries with its own weakest crypto. The fix: every token in the corpus now traces to a human root through provenance chains.

This file is the self-model's self-memory.

# TrainLLM Audit — emergent-compile

Four seams found and patched on this branch.

## 1. zk.ts named a proof that is not a proof
`zkAttest` was SHA-256 with a comment admitting it is a placeholder for a
real ZK-SNARK. Anything downstream reading `zk` from /execute as an
attestation was trusting a hash. Renamed to `actionDigest`, kept as a
deprecation alias for one release, and documented that a real proof system
(Groth16/Plonk) must be paired before any knowledge claim.

## 2. verifyCapability hardcoded the capability literal
It compared the decoded claim against the string `scale-sla`, so a validly
signed token for any other allowed capability failed. Now checks against
`ALLOWED_CAPABILITIES` and `signCapability` refuses to mint unknown caps.

## 3. /token was a public faucet
No authentication, minted `scale-sla` — the capability the execute path
gates on — for anyone. In production the route is removed entirely. In dev
it requires an already-authorized caller token.

## 4. CycleKernel trust scores were dice
`random.uniform(0.6, 0.95)` generated authority from entropy, the one layer
in the compile that measures before acting was feeding the self-model
simulated measurement. Patched to derive trust from an evidence snapshot:
failures over runs, Bernoulli variance as heat, orientation as pass/fail/mixed.

## Why this matters for the compile
TrainLLM is the self-model: it attests, signs, logs disagreement, and
compiles its own signed claims into training data via compiler.ts. Every
other layer got residual fields, provenance, lineage gates. The layer that
touches itself was running the weakest crypto it owns. This branch makes
the self-model as strict as the geometry underneath it.

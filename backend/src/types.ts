export interface Attestation {
  cycle: number;
  artifact: string;
  previousHash: string | null;
  invariants: Record<string, boolean>;
  policyProofs: Record<string, boolean>;
  proofHash?: string;
  signature?: string;
  publicKey?: string;
}

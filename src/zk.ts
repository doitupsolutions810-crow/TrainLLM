import { createHash } from 'crypto';

/**
 * actionDigest replaces zkAttest.
 *
 * The previous name implied a zero-knowledge proof. This is a SHA-256 digest
 * of an action string bound to a secret — a commitment, not a SNARK.
 * Downstream code must not treat the output as an attestation of validity;
 * pair it with a real proof system (Groth16/Plonk) before any claim of
 * knowledge-without-revelation is made.
 */
export function actionDigest(action: string, secret: string): string {
  return createHash('sha256').update(action + secret).digest('hex);
}

/** @deprecated Use actionDigest. Retained for one release for import compatibility. */
export const zkAttest = actionDigest;

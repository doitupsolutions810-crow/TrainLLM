// Lightweight adapter for local LLMs (placeholder)
export async function initializeLLM() {
  // In production, initialize a local model here (e.g., via xenova or a local server)
  return { generate: async (prompt: string) => ({ text: 'stub-response' }) };
}

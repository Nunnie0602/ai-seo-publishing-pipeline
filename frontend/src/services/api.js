const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function generateArticle(payload) {
  const response = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      topic: payload.topic,
      keywords: payload.keywords,
      target_audience: payload.targetAudience,
      call_to_action: payload.callToAction,
    }),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message =
      data?.detail?.message ||
      data?.message ||
      data?.detail ||
      "Generation failed. Please retry.";
    throw new Error(
      typeof message === "string" ? message : "Generation failed. Please retry."
    );
  }

  return data;
}

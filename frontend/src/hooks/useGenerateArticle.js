import { useCallback, useState } from "react";
import { generateArticle } from "../services/api";

const PIPELINE_STEPS = [
  { key: "generating", label: "Generating article..." },
  { key: "validating", label: "Validating JSON..." },
  { key: "sanitizing", label: "Sanitizing HTML..." },
  { key: "publishing", label: "Publishing draft..." },
  { key: "completed", label: "Completed" },
];

export function useGenerateArticle() {
  const [loading, setLoading] = useState(false);
  const [stepIndex, setStepIndex] = useState(-1);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const run = useCallback(async (formData) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setStepIndex(0);

    const stepTimer = setInterval(() => {
      setStepIndex((prev) => (prev < PIPELINE_STEPS.length - 2 ? prev + 1 : prev));
    }, 1200);

    try {
      const data = await generateArticle(formData);
      setStepIndex(PIPELINE_STEPS.length - 1);
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message || "Generation failed. Please retry.");
      setStepIndex(-1);
      throw err;
    } finally {
      clearInterval(stepTimer);
      setLoading(false);
    }
  }, []);

  const currentStep =
    stepIndex >= 0 ? PIPELINE_STEPS[stepIndex]?.label : null;

  const reset = useCallback(() => {
    setError(null);
    setResult(null);
    setStepIndex(-1);
  }, []);

  return {
    loading,
    error,
    result,
    currentStep,
    pipelineSteps: PIPELINE_STEPS.map((s) => s.label),
    stepIndex,
    run,
    reset,
  };
}

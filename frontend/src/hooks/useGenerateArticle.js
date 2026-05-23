import { useCallback, useState } from "react";
import { generateArticle } from "../services/api";
import { PIPELINE_STEP_KEYS } from "../i18n/translations";

export { PIPELINE_STEP_KEYS };

export function useGenerateArticle(getDefaultErrorMessage) {
  const [loading, setLoading] = useState(false);
  const [stepIndex, setStepIndex] = useState(-1);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const run = useCallback(
    async (formData) => {
      setLoading(true);
      setError(null);
      setResult(null);
      setStepIndex(0);

      const stepTimer = setInterval(() => {
        setStepIndex((prev) =>
          prev < PIPELINE_STEP_KEYS.length - 2 ? prev + 1 : prev
        );
      }, 1200);

      try {
        const data = await generateArticle(formData);
        setStepIndex(PIPELINE_STEP_KEYS.length - 1);
        setResult(data);
        return data;
      } catch (err) {
        setError(
          err.message ||
            (getDefaultErrorMessage?.() ?? "Generation failed. Please retry.")
        );
        setStepIndex(-1);
        throw err;
      } finally {
        clearInterval(stepTimer);
        setLoading(false);
      }
    },
    [getDefaultErrorMessage]
  );

  const reset = useCallback(() => {
    setError(null);
    setResult(null);
    setStepIndex(-1);
  }, []);

  return {
    loading,
    error,
    result,
    pipelineStepKeys: PIPELINE_STEP_KEYS,
    stepIndex,
    run,
    reset,
  };
}

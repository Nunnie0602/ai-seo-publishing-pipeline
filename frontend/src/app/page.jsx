import { useCallback } from "react";
import Layout from "./layout";
import SeoForm from "../components/SeoForm";
import LoadingPipeline from "../components/LoadingPipeline";
import HtmlPreview from "../components/HtmlPreview";
import ErrorAlert from "../components/ErrorAlert";
import SuccessToast from "../components/SuccessToast";
import { useGenerateArticle } from "../hooks/useGenerateArticle";

export default function Page() {
  const {
    loading,
    error,
    result,
    pipelineSteps,
    stepIndex,
    run,
    reset,
  } = useGenerateArticle();

  const handleSubmit = useCallback(
    async (formData) => {
      try {
        await run(formData);
      } catch {
        /* error state handled in hook */
      }
    },
    [run]
  );

  return (
    <Layout>
      <div className="page-grid">
        <section className="page-grid__form">
          <SeoForm onSubmit={handleSubmit} loading={loading} />
        </section>

        <section className="page-grid__status">
          <ErrorAlert message={error} onDismiss={reset} />
          <LoadingPipeline steps={pipelineSteps} activeIndex={stepIndex} />
          <SuccessToast
            postId={result?.post_id}
            draftUrl={result?.draft_url}
            onDismiss={reset}
          />
          <HtmlPreview
            title={result?.title}
            html={result?.preview_html}
          />
        </section>
      </div>
    </Layout>
  );
}

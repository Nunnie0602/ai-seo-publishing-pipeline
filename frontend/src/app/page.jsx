import { useCallback } from "react";
import Layout from "./layout";
import SeoForm from "../components/SeoForm";
import LoadingPipeline from "../components/LoadingPipeline";
import HtmlPreview from "../components/HtmlPreview";
import ErrorAlert from "../components/ErrorAlert";
import SuccessToast from "../components/SuccessToast";
import { useLanguage } from "../i18n/LanguageContext";
import { useGenerateArticle } from "../hooks/useGenerateArticle";

export default function Page() {
  const { t } = useLanguage();
  const getDefaultErrorMessage = useCallback(
    () => t.error.defaultMessage,
    [t]
  );

  const {
    loading,
    error,
    result,
    pipelineStepKeys,
    stepIndex,
    run,
    reset,
  } = useGenerateArticle(getDefaultErrorMessage);

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

  const showStatusMessages =
    Boolean(error) || Boolean(result?.post_id || result?.draft_url);

  return (
    <Layout>
      <div className="page-grid">
        <section className="page-grid__form">
          <SeoForm onSubmit={handleSubmit} loading={loading} />
        </section>

        <section className="page-grid__status">
          <LoadingPipeline
            stepKeys={pipelineStepKeys}
            activeIndex={stepIndex}
          />
          {showStatusMessages && (
            <div className="status-messages">
              <ErrorAlert message={error} onDismiss={reset} />
              <SuccessToast
                postId={result?.post_id}
                draftUrl={result?.draft_url}
                onDismiss={reset}
              />
            </div>
          )}
          <HtmlPreview
            title={result?.title}
            html={result?.preview_html}
          />
        </section>
      </div>
    </Layout>
  );
}

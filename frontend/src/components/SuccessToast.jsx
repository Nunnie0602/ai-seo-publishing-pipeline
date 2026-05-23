import { formatMessage } from "../i18n/translations";
import { useLanguage } from "../i18n/LanguageContext";

export default function SuccessToast({ postId, draftUrl, onDismiss }) {
  const { t } = useLanguage();

  if (!postId && !draftUrl) return null;

  return (
    <div className="alert alert--success" role="status">
      <p>{t.success.title}</p>
      {postId && <p>{formatMessage(t.success.postId, { id: postId })}</p>}
      {draftUrl && (
        <p>
          <a href={draftUrl} target="_blank" rel="noreferrer">
            {t.success.openDraft}
          </a>
        </p>
      )}
      {onDismiss && (
        <button type="button" className="alert__dismiss" onClick={onDismiss}>
          {t.success.dismiss}
        </button>
      )}
    </div>
  );
}

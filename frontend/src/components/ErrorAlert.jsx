import { useLanguage } from "../i18n/LanguageContext";

export default function ErrorAlert({ message, onDismiss }) {
  const { t } = useLanguage();

  if (!message) return null;

  return (
    <div className="alert alert--error" role="alert">
      <p>{message}</p>
      {onDismiss && (
        <button type="button" className="alert__dismiss" onClick={onDismiss}>
          {t.error.dismiss}
        </button>
      )}
    </div>
  );
}

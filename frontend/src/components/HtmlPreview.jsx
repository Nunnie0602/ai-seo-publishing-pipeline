import { useLanguage } from "../i18n/LanguageContext";

export default function HtmlPreview({ title, html }) {
  const { t } = useLanguage();

  if (!html) return null;

  return (
    <section className="preview">
      <h3>{t.preview.title}</h3>
      {title && <p className="preview__title">{title}</p>}
      <div
        className="preview__content"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </section>
  );
}

import { useLanguage } from "../i18n/LanguageContext";

export default function HtmlPreview({ title, html }) {
  const { t } = useLanguage();

  if (!html) return null;

  return (
    <section className="preview">
      <h3>{t.preview.title}</h3>
      <div className="preview__content">
        {title && <h1 className="preview__article-title">{title}</h1>}
        <div dangerouslySetInnerHTML={{ __html: html }} />
      </div>
    </section>
  );
}

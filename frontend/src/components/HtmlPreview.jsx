export default function HtmlPreview({ title, html }) {
  if (!html) return null;

  return (
    <section className="preview">
      <h3>HTML Preview</h3>
      {title && <p className="preview__title">{title}</p>}
      <div
        className="preview__content"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </section>
  );
}

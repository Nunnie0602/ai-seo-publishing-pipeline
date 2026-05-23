import { useLanguage } from "../i18n/LanguageContext";

export default function KeywordInput({ value, onChange, disabled }) {
  const { t } = useLanguage();

  return (
    <div className="field">
      <label htmlFor="keywords">
        {t.field.keywords}{" "}
        <span className="field__required">{t.field.required}</span>
      </label>
      <textarea
        id="keywords"
        rows={4}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={t.placeholder.keywords}
        disabled={disabled}
      />
    </div>
  );
}

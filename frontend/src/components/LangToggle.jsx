import { LOCALES } from "../i18n/translations";
import { useLanguage } from "../i18n/LanguageContext";

export default function LangToggle() {
  const { locale, setLocale, t } = useLanguage();

  return (
    <div className="lang-toggle" role="group" aria-label="Language">
      <button
        type="button"
        className={`lang-toggle__btn${locale === LOCALES.en ? " lang-toggle__btn--active" : ""}`}
        onClick={() => setLocale(LOCALES.en)}
      >
        {t.lang.en}
      </button>
      <button
        type="button"
        className={`lang-toggle__btn${locale === LOCALES.zh ? " lang-toggle__btn--active" : ""}`}
        onClick={() => setLocale(LOCALES.zh)}
      >
        {t.lang.zh}
      </button>
    </div>
  );
}

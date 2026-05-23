import { useLanguage } from "../i18n/LanguageContext";

export default function Layout({ children }) {
  const { t } = useLanguage();

  return (
    <div className="layout">
      <header className="layout__header">
        <h1>{t.layout.title}</h1>
        <p>{t.layout.subtitle}</p>
      </header>
      <main className="layout__main">{children}</main>
    </div>
  );
}

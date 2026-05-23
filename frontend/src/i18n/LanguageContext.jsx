import { createContext, useContext, useMemo, useState } from "react";
import { LOCALES, translations } from "./translations";

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [locale, setLocale] = useState(LOCALES.zh);

  const value = useMemo(
    () => ({
      locale,
      setLocale,
      t: translations[locale],
    }),
    [locale]
  );

  return (
    <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return context;
}

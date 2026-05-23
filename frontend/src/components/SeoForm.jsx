import { useState } from "react";
import KeywordInput from "./KeywordInput";
import LangToggle from "./LangToggle";
import { useLanguage } from "../i18n/LanguageContext";
import { formatMessage } from "../i18n/translations";
import { validateSeoForm, CTA_MAX_LENGTH } from "../utils/validators";

const initialForm = {
  topic: "",
  keywords: "",
  targetAudience: "",
  callToAction: "",
};

const REQUIRED_FIELD_KEYS = [
  "topic",
  "keywords",
  "targetAudience",
  "callToAction",
];

function isFieldEmpty(key, form) {
  if (key === "keywords") {
    const lines = form.keywords
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
    return lines.length === 0;
  }
  return !form[key]?.trim();
}

export default function SeoForm({ onSubmit, loading }) {
  const { t } = useLanguage();
  const [form, setForm] = useState(initialForm);

  const update = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    for (const key of REQUIRED_FIELD_KEYS) {
      if (isFieldEmpty(key, form)) {
        window.alert(
          formatMessage(t.alert.empty, { field: t.field[key] })
        );
        return;
      }
    }

    const keywordLines = form.keywords
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    const ctaMaxMessage = formatMessage(t.validation.ctaMax, {
      max: CTA_MAX_LENGTH,
    });

    const { valid, errors: validationErrors, normalized } = validateSeoForm(
      {
        topic: form.topic,
        keywords: keywordLines,
        callToAction: form.callToAction,
      },
      { ctaMaxMessage }
    );

    if (!valid) {
      const firstError = Object.values(validationErrors)[0];
      if (firstError) {
        window.alert(firstError);
      }
      return;
    }

    onSubmit({
      topic: normalized.topic,
      keywords: normalized.keywords,
      targetAudience: form.targetAudience.trim(),
      callToAction: normalized.callToAction,
    });
  };

  return (
    <form className="seo-form" onSubmit={handleSubmit} noValidate>
      <div className="seo-form__header">
        <LangToggle />
      </div>

      <div className="field">
        <label htmlFor="topic">
          {t.field.topic}{" "}
          <span className="field__required">{t.field.required}</span>
        </label>
        <input
          id="topic"
          type="text"
          value={form.topic}
          onChange={(e) => update("topic", e.target.value)}
          placeholder={t.placeholder.topic}
          disabled={loading}
        />
      </div>

      <KeywordInput
        value={form.keywords}
        onChange={(keywords) => update("keywords", keywords)}
        disabled={loading}
      />

      <div className="field">
        <label htmlFor="targetAudience">
          {t.field.targetAudience}{" "}
          <span className="field__required">{t.field.required}</span>
        </label>
        <input
          id="targetAudience"
          type="text"
          value={form.targetAudience}
          onChange={(e) => update("targetAudience", e.target.value)}
          placeholder={t.placeholder.targetAudience}
          disabled={loading}
        />
      </div>

      <div className="field">
        <label htmlFor="callToAction">
          {t.field.callToAction}{" "}
          <span className="field__required">{t.field.required}</span>
        </label>
        <input
          id="callToAction"
          type="text"
          value={form.callToAction}
          onChange={(e) => update("callToAction", e.target.value)}
          placeholder={t.placeholder.callToAction}
          maxLength={CTA_MAX_LENGTH}
          disabled={loading}
        />
      </div>

      <button type="submit" className="btn btn--primary" disabled={loading}>
        {loading ? t.button.processing : t.button.generate}
      </button>
    </form>
  );
}

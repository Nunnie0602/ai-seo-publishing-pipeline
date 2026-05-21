import { useState } from "react";
import KeywordInput from "./KeywordInput";
import { validateSeoForm } from "../utils/validators";

const initialForm = {
  topic: "",
  keywords: [],
  targetAudience: "",
  callToAction: "",
};

export default function SeoForm({ onSubmit, loading }) {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});

  const update = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const { valid, errors: validationErrors, normalized } = validateSeoForm({
      topic: form.topic,
      keywords: form.keywords,
      callToAction: form.callToAction,
    });

    if (!valid) {
      setErrors(validationErrors);
      return;
    }

    onSubmit({
      topic: normalized.topic,
      keywords: normalized.keywords,
      targetAudience: form.targetAudience.trim(),
      callToAction: normalized.callToAction || form.callToAction.trim(),
    });
  };

  return (
    <form className="seo-form" onSubmit={handleSubmit} noValidate>
      <div className="field">
        <label htmlFor="topic">Topic</label>
        <input
          id="topic"
          type="text"
          value={form.topic}
          onChange={(e) => update("topic", e.target.value)}
          placeholder="Tainan Food Travel Guide"
          disabled={loading}
        />
        {errors.topic && <span className="field__error">{errors.topic}</span>}
      </div>

      <KeywordInput
        keywords={form.keywords}
        onChange={(keywords) => update("keywords", keywords)}
        error={errors.keywords}
      />

      <div className="field">
        <label htmlFor="targetAudience">Target Audience</label>
        <input
          id="targetAudience"
          type="text"
          value={form.targetAudience}
          onChange={(e) => update("targetAudience", e.target.value)}
          placeholder="Foreign tourists visiting Taiwan"
          disabled={loading}
        />
      </div>

      <div className="field">
        <label htmlFor="callToAction">Call To Action</label>
        <input
          id="callToAction"
          type="text"
          value={form.callToAction}
          onChange={(e) => update("callToAction", e.target.value)}
          placeholder="Book your Tainan trip today"
          disabled={loading}
        />
        {errors.callToAction && (
          <span className="field__error">{errors.callToAction}</span>
        )}
      </div>

      <button type="submit" className="btn btn--primary" disabled={loading}>
        {loading ? "Processing..." : "Generate & Publish Draft"}
      </button>
    </form>
  );
}

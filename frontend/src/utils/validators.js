import { CTA_MAX_LENGTH } from "../i18n/translations";

export { CTA_MAX_LENGTH };

export function validateSeoForm(
  { topic, keywords, callToAction },
  { ctaMaxMessage } = {}
) {
  const errors = {};
  const validKeywords = (keywords || []).filter((k) => k?.trim());
  const cta = callToAction ?? "";

  if (cta.length > CTA_MAX_LENGTH && ctaMaxMessage) {
    errors.callToAction = ctaMaxMessage;
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
    normalized: {
      topic: topic?.trim() ?? "",
      keywords: validKeywords.map((k) => k.trim()),
      callToAction: cta.trim(),
    },
  };
}

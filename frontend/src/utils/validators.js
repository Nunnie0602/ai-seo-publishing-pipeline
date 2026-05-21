const CTA_MAX_LENGTH = 200;

export function validateSeoForm({ topic, keywords, callToAction }) {
  const errors = {};

  if (!topic?.trim()) {
    errors.topic = "Topic is required.";
  }

  const validKeywords = (keywords || []).filter((k) => k?.trim());
  if (validKeywords.length === 0) {
    errors.keywords = "Please enter at least one keyword.";
  }

  if (callToAction && callToAction.length > CTA_MAX_LENGTH) {
    errors.callToAction = `Call to action must be ${CTA_MAX_LENGTH} characters or less.`;
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
    normalized: {
      topic: topic?.trim() ?? "",
      keywords: validKeywords.map((k) => k.trim()),
      callToAction: callToAction?.trim() ?? "",
    },
  };
}

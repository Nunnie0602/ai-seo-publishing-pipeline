export const CTA_MAX_LENGTH = 200;

export const LOCALES = {
  en: "en",
  zh: "zh",
};

export const translations = {
  en: {
    lang: { en: "En", zh: "繁中" },
    layout: {
      title: "AI SEO Content Generator",
      subtitle: "Generate SEO articles to WordPress drafts",
    },
    field: {
      topic: "Topic",
      keywords: "Keywords (one per line)",
      targetAudience: "Target Audience",
      callToAction: "Call To Action",
      required: "(Required)*",
    },
    placeholder: {
      topic: "Kaohsiung Food Travel Guide",
      keywords: "Kaohsiung food\nTaiwan travel",
      targetAudience: "Foreign tourists visiting Taiwan",
      callToAction: "Book your Kaohsiung trip today",
    },
    button: {
      generate: "Generate Draft to WordPress",
      processing: "Processing...",
    },
    alert: {
      empty: "{field} is empty. Please enter the required text.",
    },
    validation: {
      ctaMax: "Call to action must be {max} characters or less.",
    },
    pipeline: {
      title: "Pipeline Status",
      steps: {
        generating: "Generating article...",
        validating: "Validating JSON...",
        sanitizing: "Sanitizing HTML...",
        publishing: "Publishing draft...",
        completed: "Completed",
      },
    },
    error: {
      dismiss: "Dismiss",
      defaultMessage: "Generation failed. Please retry.",
    },
    success: {
      title: "Draft created successfully!",
      postId: "Post ID: {id}",
      openDraft: "Open draft in WordPress",
      dismiss: "Dismiss",
    },
    preview: {
      title: "HTML Preview",
    },
  },
  zh: {
    lang: { en: "En", zh: "繁中" },
    layout: {
      title: "AI SEO 內容產生器",
      subtitle: "產生 SEO 文章並發佈為 WordPress 草稿",
    },
    field: {
      topic: "主題",
      keywords: "關鍵字(每列一個)",
      targetAudience: "目標受眾",
      callToAction: "行動呼籲",
      required: "(必填)*",
    },
    placeholder: {
      topic: "高雄美食旅遊指南",
      keywords: "高雄美食\n台灣旅遊",
      targetAudience: "來台灣旅遊的外國遊客",
      callToAction: "立即預訂您的高雄之旅",
    },
    button: {
      generate: "產生草稿並發佈至 WordPress",
      processing: "處理中...",
    },
    alert: {
      empty: "{field}為空白請輸入需求文字",
    },
    validation: {
      ctaMax: "行動呼籲不得超過 {max} 字元。",
    },
    pipeline: {
      title: "流程狀態",
      steps: {
        generating: "正在產生文章...",
        validating: "正在驗證 JSON...",
        sanitizing: "正在清理 HTML...",
        publishing: "正在發佈草稿...",
        completed: "已完成",
      },
    },
    error: {
      dismiss: "關閉",
      defaultMessage: "產生失敗，請重試。",
    },
    success: {
      title: "草稿建立成功！",
      postId: "文章 ID：{id}",
      openDraft: "在 WordPress 中開啟草稿",
      dismiss: "關閉",
    },
    preview: {
      title: "HTML 預覽",
    },
  },
};

export const PIPELINE_STEP_KEYS = [
  "generating",
  "validating",
  "sanitizing",
  "publishing",
  "completed",
];

export function formatMessage(template, vars = {}) {
  return Object.entries(vars).reduce(
    (text, [key, value]) => text.replaceAll(`{${key}}`, String(value)),
    template
  );
}

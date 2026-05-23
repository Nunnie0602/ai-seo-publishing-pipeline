import { useLanguage } from "../i18n/LanguageContext";

export default function LoadingPipeline({ stepKeys, activeIndex }) {
  const { t } = useLanguage();

  if (activeIndex < 0) return null;

  return (
    <div className="pipeline" role="status" aria-live="polite">
      <h3>{t.pipeline.title}</h3>
      <ol className="pipeline__bar">
        {stepKeys.map((key, index) => {
          const state =
            index < activeIndex
              ? "done"
              : index === activeIndex
                ? "active"
                : "pending";
          return (
            <li
              key={key}
              className={`pipeline__segment pipeline__segment--${state}`}
              aria-current={state === "active" ? "step" : undefined}
            >
              <span className="pipeline__track" aria-hidden="true" />
              <span className="pipeline__label">{t.pipeline.steps[key]}</span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

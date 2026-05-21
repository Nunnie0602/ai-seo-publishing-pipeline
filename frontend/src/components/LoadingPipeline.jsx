export default function LoadingPipeline({ steps, activeIndex }) {
  if (activeIndex < 0) return null;

  return (
    <div className="pipeline" role="status" aria-live="polite">
      <h3>Pipeline Status</h3>
      <ol className="pipeline__list">
        {steps.map((label, index) => {
          const state =
            index < activeIndex
              ? "done"
              : index === activeIndex
                ? "active"
                : "pending";
          return (
            <li key={label} className={`pipeline__item pipeline__item--${state}`}>
              {label}
            </li>
          );
        })}
      </ol>
    </div>
  );
}

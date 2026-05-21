export default function ErrorAlert({ message, onDismiss }) {
  if (!message) return null;

  return (
    <div className="alert alert--error" role="alert">
      <p>{message}</p>
      {onDismiss && (
        <button type="button" className="alert__dismiss" onClick={onDismiss}>
          Dismiss
        </button>
      )}
    </div>
  );
}

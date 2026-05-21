export default function SuccessToast({ postId, draftUrl, onDismiss }) {
  if (!postId && !draftUrl) return null;

  return (
    <div className="alert alert--success" role="status">
      <p>Draft created successfully!</p>
      {postId && <p>Post ID: {postId}</p>}
      {draftUrl && (
        <p>
          <a href={draftUrl} target="_blank" rel="noreferrer">
            Open draft in WordPress
          </a>
        </p>
      )}
      {onDismiss && (
        <button type="button" className="alert__dismiss" onClick={onDismiss}>
          Dismiss
        </button>
      )}
    </div>
  );
}

export default function KeywordInput({ keywords, onChange, error }) {
  const value = keywords.join("\n");

  const handleChange = (e) => {
    const lines = e.target.value
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
    onChange(lines);
  };

  return (
    <div className="field">
      <label htmlFor="keywords">Keywords (one per line)</label>
      <textarea
        id="keywords"
        rows={4}
        value={value}
        onChange={handleChange}
        placeholder="Tainan food&#10;Taiwan travel"
        disabled={false}
      />
      {error && <span className="field__error">{error}</span>}
    </div>
  );
}

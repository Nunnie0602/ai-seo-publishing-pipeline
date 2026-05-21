export default function Layout({ children }) {
  return (
    <div className="layout">
      <header className="layout__header">
        <h1>AI SEO Content Publishing Pipeline</h1>
        <p>Generate SEO articles and publish WordPress drafts</p>
      </header>
      <main className="layout__main">{children}</main>
    </div>
  );
}

export function Footer() {
  const commitSha = process.env.NEXT_PUBLIC_COMMIT_SHA;
  const buildTimestamp = process.env.NEXT_PUBLIC_BUILD_TIMESTAMP;
  const showCommit = commitSha && commitSha !== "onbekend";

  return (
    <footer className="border-t border-gray-200 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <p className="text-sm text-gray-500">
            &copy; {new Date().getFullYear()} VNG Realisatie &mdash; Softwarecatalogus
            <span className="ml-2 font-mono text-xs text-gray-400" title="Build-versie">
              {showCommit ? `v${commitSha}` : ""}{showCommit && buildTimestamp ? " · " : ""}{buildTimestamp ?? ""}
            </span>
          </p>
          <div className="flex gap-6">
            <a
              href="https://www.vngrealisatie.nl/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-gray-500 hover:text-primary-500"
            >
              VNG Realisatie
            </a>
            <a
              href="https://www.gemmaonline.nl/"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-gray-500 hover:text-primary-500"
            >
              GEMMA Online
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

"use client";

import React from "react";

/**
 * Eenvoudige inline Markdown-renderer zonder externe dependencies.
 *
 * Ondersteunde syntax:
 *   ## Heading 2
 *   ### Heading 3
 *   **bold**
 *   *italic*
 *   - ongeordende lijst
 *   1. geordende lijst
 *   > blockquote
 *   `inline code`
 *   [tekst](url)
 *   | tabel | rijen |
 */
export function MiniMarkdown({ content }: { content: string }) {
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Lege regel
    if (!line.trim()) {
      i++;
      continue;
    }

    // Heading 2
    if (line.startsWith("## ")) {
      elements.push(
        <h3
          key={i}
          className="mb-2 mt-4 text-sm font-semibold text-gray-900 first:mt-0"
        >
          {renderInline(line.slice(3))}
        </h3>
      );
      i++;
      continue;
    }

    // Heading 3
    if (line.startsWith("### ")) {
      elements.push(
        <h4 key={i} className="mb-1 mt-3 text-sm font-medium text-gray-800">
          {renderInline(line.slice(4))}
        </h4>
      );
      i++;
      continue;
    }

    // Blockquote
    if (line.startsWith("> ")) {
      elements.push(
        <blockquote
          key={i}
          className="my-2 border-l-2 border-primary-300 bg-primary-50 py-1 pl-3 pr-2 text-xs text-primary-800"
        >
          {renderInline(line.slice(2))}
        </blockquote>
      );
      i++;
      continue;
    }

    // Ongeordende lijst
    if (line.startsWith("- ")) {
      const items: string[] = [];
      while (i < lines.length && lines[i].startsWith("- ")) {
        items.push(lines[i].slice(2));
        i++;
      }
      elements.push(
        <ul key={`ul-${i}`} className="my-2 space-y-1 pl-4">
          {items.map((item, idx) => (
            <li key={idx} className="flex gap-1.5 text-xs text-gray-700">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary-400" />
              <span>{renderInline(item)}</span>
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // Geordende lijst
    if (/^\d+\. /.test(line)) {
      const items: string[] = [];
      while (i < lines.length && /^\d+\. /.test(lines[i])) {
        items.push(lines[i].replace(/^\d+\. /, ""));
        i++;
      }
      elements.push(
        <ol key={`ol-${i}`} className="my-2 space-y-1.5 pl-4">
          {items.map((item, idx) => (
            <li key={idx} className="flex gap-2 text-xs text-gray-700">
              <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-primary-100 text-[10px] font-semibold text-primary-700">
                {idx + 1}
              </span>
              <span>{renderInline(item)}</span>
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // Tabelrij (eenvoudig)
    if (line.startsWith("|")) {
      const rows: string[][] = [];
      let isFirst = true;
      while (i < lines.length && lines[i].startsWith("|")) {
        const row = lines[i]
          .split("|")
          .slice(1, -1)
          .map((c) => c.trim());
        // Sla scheidingslijn over (|---|---|)
        if (!row.every((c) => /^-+$/.test(c))) {
          rows.push(row);
        }
        isFirst = false;
        i++;
      }
      if (rows.length > 0) {
        elements.push(
          <table key={`tbl-${i}`} className="my-2 w-full text-xs">
            <thead>
              <tr className="border-b border-gray-200">
                {rows[0].map((cell, j) => (
                  <th
                    key={j}
                    className="py-1 pr-3 text-left font-medium text-gray-700"
                  >
                    {renderInline(cell)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.slice(1).map((row, ridx) => (
                <tr
                  key={ridx}
                  className="border-b border-gray-100 last:border-0"
                >
                  {row.map((cell, j) => (
                    <td key={j} className="py-1 pr-3 text-gray-600">
                      {renderInline(cell)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        );
      }
      continue;
    }

    // Gewone alinea
    elements.push(
      <p key={i} className="text-xs text-gray-700 leading-relaxed">
        {renderInline(line)}
      </p>
    );
    i++;
  }

  return <div className="space-y-0.5">{elements}</div>;
}

/** Verwerk inline markdown (bold, italic, code, links). */
function renderInline(text: string): React.ReactNode {
  // Splits op **bold**, *italic*, `code` en [link](url)
  const parts: React.ReactNode[] = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    // Bold
    const boldMatch = remaining.match(/\*\*(.+?)\*\*/);
    // Italic
    const italicMatch = remaining.match(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/);
    // Code
    const codeMatch = remaining.match(/`(.+?)`/);
    // Link
    const linkMatch = remaining.match(/\[([^\]]+)\]\(([^)]+)\)/);

    // Kies de vroegste match
    const candidates: { idx: number; match: RegExpMatchArray; type: string }[] =
      [];
    if (boldMatch?.index !== undefined)
      candidates.push({ idx: boldMatch.index, match: boldMatch, type: "bold" });
    if (italicMatch?.index !== undefined)
      candidates.push({
        idx: italicMatch.index,
        match: italicMatch,
        type: "italic",
      });
    if (codeMatch?.index !== undefined)
      candidates.push({ idx: codeMatch.index, match: codeMatch, type: "code" });
    if (linkMatch?.index !== undefined)
      candidates.push({ idx: linkMatch.index, match: linkMatch, type: "link" });

    if (candidates.length === 0) {
      parts.push(remaining);
      break;
    }

    candidates.sort((a, b) => a.idx - b.idx);
    const { idx, match, type } = candidates[0];

    // Tekst voor de match
    if (idx > 0) {
      parts.push(remaining.slice(0, idx));
    }

    if (type === "bold") {
      parts.push(
        <strong key={key++} className="font-semibold text-gray-900">
          {match[1]}
        </strong>
      );
      remaining = remaining.slice(idx + match[0].length);
    } else if (type === "italic") {
      parts.push(
        <em key={key++} className="italic">
          {match[1]}
        </em>
      );
      remaining = remaining.slice(idx + match[0].length);
    } else if (type === "code") {
      parts.push(
        <code
          key={key++}
          className="rounded bg-gray-100 px-1 py-0.5 font-mono text-[10px] text-gray-700"
        >
          {match[1]}
        </code>
      );
      remaining = remaining.slice(idx + match[0].length);
    } else if (type === "link") {
      const isExternal = match[2].startsWith("http");
      parts.push(
        <a
          key={key++}
          href={match[2]}
          className="text-primary-600 underline underline-offset-2 hover:text-primary-800"
          target={isExternal ? "_blank" : undefined}
          rel={isExternal ? "noopener noreferrer" : undefined}
        >
          {match[1]}
        </a>
      );
      remaining = remaining.slice(idx + match[0].length);
    }
  }

  return <>{parts}</>;
}

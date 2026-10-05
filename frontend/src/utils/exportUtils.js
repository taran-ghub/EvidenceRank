// exportUtils.js - Utility functions for exporting audit and ranking data

export function downloadJsonReport(results, filename = "EvidenceRank_audit_report.json") {
  if (!results) return;
  const jsonString = JSON.stringify(results, null, 2);
  const blob = new Blob([jsonString], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function downloadCsvShortlist(results, filename = "EvidenceRank_candidate_shortlist.csv") {
  if (!results || !results.rankings) return;

  const headers = [
    "Rank",
    "Candidate Filename",
    "Evidence Fit Score",
    "Required Coverage (%)",
    "Preferred Coverage (%)",
    "Mandatory Gaps Count",
    "Missing Requirements",
    "Strong Matches Count",
    "Evidence Spans Total"
  ];

  const rows = results.rankings.map((c) => [
    c.rank ?? "-",
    `"${(c.filename || "").replace(/"/g, '""')}"`,
    Number(c.final_score || 0).toFixed(1),
    Math.round((c.required_coverage || 0) * 100),
    Math.round((c.preferred_coverage || 0) * 100),
    c.missing_required?.length || 0,
    `"${(c.missing_required || []).join("; ").replace(/"/g, '""')}"`,
    c.strong_matches?.length || (c.status_counts?.strong ?? 0),
    c.evidence_span_count ?? 0
  ]);

  const csvContent = [headers.join(","), ...rows.map((row) => row.join(","))].join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export async function copySummaryToClipboard(results, candidate) {
  if (!results || !candidate) return false;

  const summaryText = `
=== EvidenceRank Candidate Audit ===
Candidate: ${candidate.filename}
Rank: #${candidate.rank} of ${results.rankings?.length || 1}
Evidence Fit Score: ${Number(candidate.final_score || 0).toFixed(1)} / 100
Must-Have Coverage: ${Math.round((candidate.required_coverage || 0) * 100)}%
Preferred Coverage: ${Math.round((candidate.preferred_coverage || 0) * 100)}%
Mandatory Gaps: ${candidate.missing_required?.length ? candidate.missing_required.join(", ") : "None detected"}
Strong Matches: ${candidate.strong_matches?.join(", ") || "None"}
Audit Trail: Generated through local hybrid semantic and lexical analysis.
====================================
`.trim();

  try {
    await navigator.clipboard.writeText(summaryText);
    return true;
  } catch (err) {
    console.error("Failed to copy summary to clipboard", err);
    return false;
  }
}

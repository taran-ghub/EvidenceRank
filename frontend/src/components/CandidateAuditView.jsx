import { useState } from "react";
import {
  Paper,
  Box,
  Typography,
  Stack,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Divider,
  LinearProgress,
  Tooltip,
  IconButton,
  Snackbar
} from "@mui/material";
import {
  ExpandMoreRounded,
  ContentCopyRounded,
  WorkspacePremiumRounded,
  FormatQuoteRounded,
  WarningAmberRounded,
  CheckCircleRounded,
  TrendingDownRounded
} from "@mui/icons-material";
import { copySummaryToClipboard } from "../utils/exportUtils";

const statusColorMap = {
  strong: { label: "STRONG FIT", border: "#c7d8c5", bg: "#e8f0e8", text: "#365d3e", dot: "#56805f" },
  partial: { label: "PARTIAL", border: "#d5dfcc", bg: "#edf0e8", text: "#4f5b40", dot: "#657153" },
  weak: { label: "WEAK", border: "#ead2a4", bg: "#fbf0dc", text: "#8c5c20", dot: "#c18436" },
  missing: { label: "MISSING", border: "#edcbc5", bg: "#faece9", text: "#84362f", dot: "#b85145" }
};

const priorityWeightMap = {
  required: { label: "Must-Have", color: "#84362f", bg: "#faece9", border: "#edcbc5" },
  preferred: { label: "Preferred", color: "#93441f", bg: "#faeee7", border: "#dfbca8" },
  contextual: { label: "Contextual", color: "#70675e", bg: "#f3eee7", border: "#e5ddd1" }
};

function LargeScoreGauge({ score, size = 84 }) {
  const value = Math.max(0, Math.min(100, Number(score || 0)));
  const strokeColor = "#b4532a";

  return (
    <Box
      sx={{
        width: size,
        height: size,
        borderRadius: "50%",
        flexShrink: 0,
        background: `conic-gradient(${strokeColor} ${value * 3.6}deg, #ede6dc 0)`,
        p: "5px"
      }}
    >
      <Box
        sx={{
          width: "100%",
          height: "100%",
          borderRadius: "50%",
          bgcolor: "#fffdf9",
          display: "grid",
          placeItems: "center",
          boxShadow: "inset 0 1px 3px rgba(0,0,0,0.06)"
        }}
      >
        <Box sx={{ textAlign: "center" }}>
          <Typography fontWeight={850} fontSize={size * 0.28} color="#29231e" sx={{ lineHeight: 1 }}>
            {value.toFixed(1)}
          </Typography>
          <Typography sx={{ fontSize: 9, color: "#70675e", letterSpacing: 1, fontWeight: 700, mt: 0.3 }}>
            SCORE
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}

function PillarMeter({ label, value, color = "#b4532a", description }) {
  const pct = Math.round((value || 0) * 100);
  return (
    <Tooltip title={description || ""}>
      <Box sx={{ p: 1.2, bgcolor: "#fffdf9", borderRadius: 2, border: "1px solid #e5ddd1" }}>
        <Stack direction="row" sx={{ justifyContent: "space-between", mb: 0.5 }}>
          <Typography variant="caption" color="#70675e" fontWeight={650}>
            {label}
          </Typography>
          <Typography variant="caption" fontWeight={750} color="#29231e">
            {pct}%
          </Typography>
        </Stack>
        <LinearProgress
          variant="determinate"
          value={pct}
          sx={{
            height: 5,
            borderRadius: 3,
            bgcolor: "#ede6dc",
            "& .MuiLinearProgress-bar": { bgcolor: color, borderRadius: 3 }
          }}
        />
      </Box>
    </Tooltip>
  );
}

export default function CandidateAuditView({
  candidate,
  requirementsById = {},
  allResults
}) {
  const [filterMode, setFilterMode] = useState("all");
  const [copySuccess, setCopySuccess] = useState(false);

  if (!candidate) {
    return (
      <Paper variant="outlined" sx={{ p: 6, textAlign: "center", borderRadius: 3, bgcolor: "#fffdf9", borderColor: "#e5ddd1" }}>
        <Typography variant="body1" color="text.secondary">
          Select a candidate from the leaderboard to inspect detailed evidence.
        </Typography>
      </Paper>
    );
  }

  const requiredCoverage = Math.round((candidate.required_coverage || 0) * 100);
  const preferredCoverage = Math.round((candidate.preferred_coverage || 0) * 100);
  const gapsCount = candidate.missing_required?.length || 0;

  const matches = candidate.requirement_matches || [];
  const filteredMatches = matches.filter((match) => {
    const req = requirementsById[match.requirement_id];
    if (filterMode === "required") return req?.priority === "required";
    if (filterMode === "preferred") return req?.priority === "preferred";
    if (filterMode === "gaps") return match.status === "missing";
    if (filterMode === "strong") return match.status === "strong";
    return true;
  });

  const handleCopy = async () => {
    const ok = await copySummaryToClipboard(allResults, candidate);
    if (ok) setCopySuccess(true);
  };

  // Summarize model output without turning it into an automated hiring decision.
  let verdictType;
  if (gapsCount > 0) {
    verdictType = "gap";
  } else if (candidate.rank === 1) {
    verdictType = "leading";
  } else if (candidate.normalization_warnings?.length > 0) {
    verdictType = "warning";
  } else {
    verdictType = "complete";
  }

  return (
    <Box>
      {/* Candidate Dossier Header */}
      <Paper
        elevation={0}
        sx={{
          p: { xs: 2.5, md: 3 },
          bgcolor: "#fffdf9",
          border: "1px solid #e5ddd1",
          borderRadius: 3.5,
          boxShadow: "0 18px 42px -34px rgba(73, 51, 35, 0.7)"
        }}
      >
        <Stack direction="row" spacing={2} sx={{ alignItems: "center", justifyContent: "space-between" }}>
          <Stack direction="row" spacing={{ xs: 1.5, sm: 2 }} sx={{ alignItems: "center", minWidth: 0 }}>
            <LargeScoreGauge score={candidate.final_score} size={74} />

            <Box sx={{ minWidth: 0 }}>
              <Stack direction="row" spacing={0.8} sx={{ alignItems: "center", mb: 0.6, flexWrap: "wrap", rowGap: 0.6 }}>
                {candidate.rank === 1 ? (
                  <Chip
                    icon={<WorkspacePremiumRounded sx={{ fontSize: 14, color: "#fffdf9 !important" }} />}
                    label="Rank #1 • Highest score"
                    sx={{
                      height: 22,
                      fontSize: 11,
                      fontWeight: 750,
                      bgcolor: "#56805f",
                      color: "#fffdf9"
                    }}
                  />
                ) : (
                  <Chip
                    label={`Rank #${candidate.rank}`}
                    size="small"
                    sx={{ height: 22, fontSize: 11, fontWeight: 650, bgcolor: "#f3eee7", color: "#70675e" }}
                  />
                )}
                <Chip
                  label={candidate.file_type || ".pdf"}
                  size="small"
                  sx={{ height: 22, fontSize: 10.5, textTransform: "uppercase", bgcolor: "#faeee7", color: "#93441f", fontWeight: 600 }}
                />
              </Stack>

              <Typography
                variant="h6"
                fontWeight={800}
                color="#29231e"
                title={candidate.filename}
                sx={{ overflowWrap: "break-word", wordBreak: "normal", lineHeight: 1.25, fontSize: { xs: 17, sm: 20 } }}
              >
                {candidate.filename}
              </Typography>

              <Typography variant="caption" color="text.secondary" mt={0.2} display="block">
                {candidate.evidence_span_count || 0} normalized resume spans • Processed locally
              </Typography>
            </Box>
          </Stack>
          <Tooltip title="Copy candidate audit summary">
            <IconButton
              onClick={handleCopy}
              sx={{
                bgcolor: "#f8f4ee",
                border: "1px solid #e5ddd1",
                color: "#70675e",
                flexShrink: 0,
                "&:hover": { bgcolor: "#f3eee7", color: "#29231e" }
              }}
            >
              <ContentCopyRounded sx={{ fontSize: 17 }} />
            </IconButton>
          </Tooltip>
        </Stack>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
            gap: 1,
            mt: 2.25
          }}
        >
          {[
            ["Must-have", `${requiredCoverage}%`, requiredCoverage >= 80 ? "#56805f" : "#c18436", "#f2eee8"],
            ["Preferred", `${preferredCoverage}%`, "#b4532a", "#faeee7"],
            ["Required gaps", gapsCount, gapsCount === 0 ? "#56805f" : "#b85145", gapsCount === 0 ? "#e8f0e8" : "#faece9"]
          ].map(([label, value, color, background]) => (
            <Box
              key={label}
              sx={{
                px: { xs: 1, sm: 1.5 },
                py: 1.25,
                bgcolor: background,
                borderRadius: 2,
                minWidth: 0
              }}
            >
              <Typography sx={{ color, fontSize: { xs: 18, sm: 22 }, fontWeight: 820, lineHeight: 1.1 }}>
                {value}
              </Typography>
              <Typography variant="caption" sx={{ color: "#746a60", fontWeight: 700, display: "block", mt: 0.45 }}>
                {label}
              </Typography>
            </Box>
          ))}
        </Box>

        {/* HIGH IMPACT DECISION VERDICT (The Convincing Proof Box) */}
        <Box mt={1.25}>
          {verdictType === "leading" && (
            <Paper
              elevation={0}
              sx={{
                p: 1.6,
                bgcolor: "#e8f0e8",
                border: "1px solid #c7d8c5",
                borderRadius: 2.5
              }}
            >
              <Stack direction="row" spacing={1.25} sx={{ alignItems: "flex-start" }}>
                <CheckCircleRounded sx={{ color: "#56805f", fontSize: 20, mt: 0.15, flexShrink: 0 }} />
                <Box>
                  <Typography variant="subtitle2" fontWeight={800} color="#365d3e">
                    Highest-ranked by model score
                  </Typography>
                  <Typography variant="body2" color="#4d694f" fontSize={13} sx={{ lineHeight: 1.45, mt: 0.25 }}>
                    {requiredCoverage}% must-have coverage, supported by {candidate.evidence_span_count || 0} traceable resume spans. Human review is still required.
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          )}

          {verdictType === "gap" && (
            <Paper
              elevation={0}
              sx={{
                p: 1.6,
                bgcolor: "#faece9",
                border: "1px solid #edcbc5",
                borderRadius: 2.5
              }}
            >
              <Stack direction="row" spacing={1.25} sx={{ alignItems: "flex-start" }}>
                <WarningAmberRounded sx={{ color: "#b85145", fontSize: 20, mt: 0.15, flexShrink: 0 }} />
                <Box sx={{ minWidth: 0 }}>
                  <Typography variant="subtitle2" fontWeight={800} color="#84362f">
                    Review required · {gapsCount} mandatory gap{gapsCount === 1 ? "" : "s"}
                  </Typography>
                  <Typography variant="body2" color="#965047" fontSize={13} sx={{ lineHeight: 1.45, mt: 0.25, overflowWrap: "anywhere" }}>
                    Missing: {candidate.missing_required?.join(", ")}. The required-skill penalty is reflected in the final score.
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          )}

          {verdictType === "warning" && (
            <Paper
              elevation={0}
              sx={{
                p: 1.6,
                bgcolor: "#fbf0dc",
                border: "1px solid #ead2a4",
                borderRadius: 2.5
              }}
            >
              <Stack direction="row" spacing={1.25} sx={{ alignItems: "flex-start" }}>
                <TrendingDownRounded sx={{ color: "#c18436", fontSize: 20, mt: 0.15, flexShrink: 0 }} />
                <Box>
                  <Typography variant="subtitle2" fontWeight={800} color="#8c5c20">
                    Processing notes available
                  </Typography>
                  <Typography variant="body2" color="#9c6c32" fontSize={13} sx={{ lineHeight: 1.45, mt: 0.25 }}>
                    {candidate.normalization_warnings.length} normalization warning
                    {candidate.normalization_warnings.length === 1 ? " was" : "s were"} recorded. Review the extracted evidence where needed.
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          )}
        </Box>

        {/* Section Evidence Breakdown Chips */}
        {candidate.section_counts && (
          <Stack direction="row" spacing={0.7} sx={{ flexWrap: "wrap", mt: 1.5, pt: 1.5, borderTop: "1px solid #f0e9df", rowGap: 0.7 }}>
            <Typography variant="caption" color="#7b7168" fontWeight={700} sx={{ alignSelf: "center", mr: 0.35 }}>
              Evidence sources
            </Typography>
            {Object.entries(candidate.section_counts).map(([section, count]) => (
              <Chip
                key={section}
                size="small"
                label={`${section}: ${count}`}
                sx={{
                  height: 21,
                  fontSize: 10.25,
                  textTransform: "capitalize",
                  bgcolor: "#f8f4ee",
                  border: "1px solid #e5ddd1",
                  color: "#514941",
                  fontWeight: 500
                }}
              />
            ))}
          </Stack>
        )}
      </Paper>

      {/* Requirement Ledger Controls */}
      <Paper
        variant="outlined"
        sx={{
          mt: 2,
          mb: 1.25,
          p: { xs: 1.5, sm: 1.75 },
          bgcolor: "rgba(255, 253, 249, 0.78)",
          borderColor: "#e5ddd1",
          borderRadius: 2.5
        }}
      >
        <Box>
          <Typography variant="subtitle1" fontWeight={780} color="#29231e" sx={{ lineHeight: 1.25 }}>
            Evidence ledger
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Open a requirement to inspect the source sentence and score breakdown.
          </Typography>
        </Box>

        <Stack direction="row" spacing={0.7} sx={{ flexWrap: "wrap", mt: 1.25, rowGap: 0.7 }}>
          {[
            ["all", `All (${matches.length})`],
            ["required", "Must-Have"],
            ["preferred", "Preferred"],
            ["gaps", `Gaps (${gapsCount})`],
            ["strong", "Strong Fits"]
          ].map(([key, label]) => (
            <Chip
              key={key}
              size="small"
              clickable
              label={label}
              onClick={() => setFilterMode(key)}
              sx={{
                height: 27,
                fontWeight: 700,
                fontSize: 11.5,
                bgcolor: filterMode === key ? "#faeee7" : "#fffdf9",
                color: filterMode === key ? "#93441f" : "#70675e",
                border: filterMode === key ? "1px solid #dfbca8" : "1px solid #e5ddd1"
              }}
            />
          ))}
        </Stack>
      </Paper>

      {/* Requirement Cards */}
      <Stack spacing={1}>
        {filteredMatches.map((match) => {
          const req = requirementsById[match.requirement_id];
          const evidence = match.best_evidence;
          const statusStyle = statusColorMap[match.status] || statusColorMap.weak;
          const priorityInfo = priorityWeightMap[req?.priority] || priorityWeightMap.required;
          const combinedPercent = Math.round((match.combined_score || 0) * 100);

          return (
            <Accordion
              key={match.requirement_id}
              disableGutters
              sx={{
                bgcolor: "#fffdf9",
                borderColor: "#e5ddd1",
                borderWidth: 1,
                borderStyle: "solid",
                borderRadius: 2,
                boxShadow: "0 1px 2px 0 rgba(0, 0, 0, 0.03)",
                "&:before": { display: "none" },
                "&.Mui-expanded": { borderColor: "#cdbdad" }
              }}
            >
              <AccordionSummary expandIcon={<ExpandMoreRounded sx={{ color: "#70675e" }} />} sx={{ minHeight: 56, px: 2.2 }}>
                <Stack direction="row" spacing={1.5} sx={{ alignItems: "center", width: "100%", pr: 1, minWidth: 0 }}>
                  {/* Status indicator dot */}
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      flexShrink: 0,
                      bgcolor: statusStyle.dot
                    }}
                  />

                  {/* Requirement Name & Priority */}
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Typography fontWeight={700} fontSize={14} color="#29231e" noWrap>
                      {match.requirement_label}
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ alignItems: "center", mt: 0.2 }}>
                      <Chip
                        size="small"
                        label={priorityInfo.label}
                        sx={{
                          height: 18,
                          fontSize: 9.5,
                          fontWeight: 700,
                          bgcolor: priorityInfo.bg,
                          color: priorityInfo.color,
                          border: `1px solid ${priorityInfo.border}`
                        }}
                      />
                      {req?.category && (
                        <Typography variant="caption" color="#70675e" fontSize={11} sx={{ textTransform: "capitalize" }}>
                          {req.category.replace("_", " ")}
                        </Typography>
                      )}
                    </Stack>
                  </Box>

                  {/* Match status chip */}
                  <Chip
                    size="small"
                    label={statusStyle.label}
                    sx={{
                      height: 22,
                      fontSize: 10,
                      fontWeight: 700,
                      bgcolor: statusStyle.bg,
                      color: statusStyle.text,
                      border: `1px solid ${statusStyle.border}`
                    }}
                  />

                  {/* Combined Score Pill */}
                  <Box sx={{ textAlign: "right", width: 44 }}>
                    <Typography fontWeight={800} fontSize={14.5} color="#29231e">
                      {combinedPercent}%
                    </Typography>
                  </Box>
                </Stack>
              </AccordionSummary>

              <AccordionDetails sx={{ px: 2.2, pt: 0, pb: 2 }}>
                <Divider sx={{ mb: 1.8, borderColor: "#f3eee7" }} />

                {/* Source Evidence Box with Left Accent Stripe */}
                {evidence ? (
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2,
                      bgcolor: "#f8f4ee",
                      border: "1px solid #e5ddd1",
                      borderLeft: "3.5px solid #b4532a",
                      borderRadius: 2
                    }}
                  >
                    <Stack direction="row" spacing={1} sx={{ alignItems: "center", mb: 0.6 }}>
                      <FormatQuoteRounded sx={{ color: "#b4532a", fontSize: 18 }} />
                      <Typography variant="caption" color="#93441f" fontWeight={750} letterSpacing={0.5}>
                        SUPPORTING RESUME EVIDENCE
                      </Typography>
                    </Stack>

                    <Typography
                      variant="body2"
                      color="#3d352e"
                      sx={{ fontStyle: "italic", fontSize: 13.5, lineHeight: 1.65 }}
                    >
                      “{evidence.original_text}”
                    </Typography>

                    <Stack direction="row" gap={0.8} sx={{ flexWrap: "wrap", mt: 1.5 }}>
                      <Chip
                        size="small"
                        label={`Page ${evidence.page_number}`}
                        sx={{ height: 20, fontSize: 10.5, bgcolor: "#fffdf9", border: "1px solid #cdbdad", color: "#514941" }}
                      />
                      <Chip
                        size="small"
                        label={`Section: ${evidence.section}`}
                        sx={{ height: 20, fontSize: 10.5, bgcolor: "#faeee7", border: "1px solid #dfbca8", color: "#93441f" }}
                      />
                      {evidence.contains_action_verb && (
                        <Chip
                          size="small"
                          label="⚡ Action Verb"
                          sx={{ height: 20, fontSize: 10.5, bgcolor: "#e8f0e8", border: "1px solid #c7d8c5", color: "#365d3e", fontWeight: 650 }}
                        />
                      )}
                      {evidence.contains_number && (
                        <Chip
                          size="small"
                          label="📊 Metric Included"
                          sx={{ height: 20, fontSize: 10.5, bgcolor: "#fbf0dc", border: "1px solid #ead2a4", color: "#8c5c20", fontWeight: 650 }}
                        />
                      )}
                      {(match.matched_terms || []).map((term) => (
                        <Chip
                          key={term}
                          size="small"
                          label={`Term: ${term}`}
                          sx={{ height: 20, fontSize: 10.5, bgcolor: "#f3eee7", border: "1px solid #cdbdad", color: "#29231e", fontWeight: 600 }}
                        />
                      ))}
                    </Stack>
                  </Paper>
                ) : (
                  <Alert
                    severity="warning"
                    sx={{
                      borderRadius: 1.5,
                      bgcolor: "#fbf0dc",
                      borderColor: "#ead2a4",
                      color: "#92400e"
                    }}
                  >
                    No supporting evidence found in candidate's resume for this requirement.
                  </Alert>
                )}

                {/* 4 Pillars Scoring Meters */}
                <Box
                  sx={{
                    display: "grid",
                    gridTemplateColumns: { xs: "1fr 1fr", md: "repeat(4, 1fr)" },
                    gap: 1.2,
                    mt: 1.8
                  }}
                >
                  <PillarMeter
                    label="BM25 Lexical"
                    value={match.keyword_score}
                    color="#657153"
                    description="Exact term frequency & lexical relevance (weight: 35%)"
                  />
                  <PillarMeter
                    label="SBERT Semantic"
                    value={match.semantic_score}
                    color="#b4532a"
                    description="MiniLM local vector similarity score (weight: 45%)"
                  />
                  <PillarMeter
                    label="Alias Relations"
                    value={match.relation_score}
                    color="#56805f"
                    description="Domain synonym & technology alternative match (weight: 20%)"
                  />
                  <PillarMeter
                    label="Evidence Quality"
                    value={match.evidence_quality}
                    color="#c18436"
                    description="Multiplier based on proven experience, metrics, and action verbs"
                  />
                </Box>
              </AccordionDetails>
            </Accordion>
          );
        })}

        {filteredMatches.length === 0 && (
          <Paper variant="outlined" sx={{ p: 4, textAlign: "center", bgcolor: "#fffdf9", borderColor: "#e5ddd1" }}>
            <Typography variant="body2" color="text.secondary">
              No requirements match the active filter.
            </Typography>
          </Paper>
        )}
      </Stack>

      <Snackbar
        open={copySuccess}
        autoHideDuration={3000}
        onClose={() => setCopySuccess(false)}
        message="Candidate audit summary copied to clipboard!"
      />
    </Box>
  );
}

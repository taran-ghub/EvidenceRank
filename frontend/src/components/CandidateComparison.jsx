import {
  Paper,
  Box,
  Typography,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  IconButton
} from "@mui/material";
import {
  CompareArrowsRounded,
  CheckCircleRounded,
  CloseRounded
} from "@mui/icons-material";

export default function CandidateComparison({
  rankings = [],
  comparedIds = [],
  onRemoveCompare,
  onClearCompare,
  requirementsById = {}
}) {
  const comparedCandidates = rankings.filter((c) => comparedIds.includes(c.candidate_id));

  if (comparedCandidates.length === 0) {
    return (
      <Paper
        variant="outlined"
        sx={{
          p: 6,
          textAlign: "center",
          borderRadius: 3,
          bgcolor: "#fffdf9",
          borderColor: "#e5ddd1",
          boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.04)"
        }}
      >
        <CompareArrowsRounded sx={{ fontSize: 40, color: "#b4532a", mb: 1 }} />
        <Typography variant="h6" fontWeight={750} color="#29231e">
          No Candidates Selected for Comparison
        </Typography>
        <Typography variant="body2" color="text.secondary" maxWidth={500} mx="auto" mt={0.5}>
          Check the comparison boxes on any 2 or 3 candidates in the leaderboard to see a side-by-side head-to-head breakdown.
        </Typography>
      </Paper>
    );
  }

  const allReqIds = Object.keys(requirementsById);

  return (
    <Paper
      variant="outlined"
      sx={{
        p: 3,
        bgcolor: "#fffdf9",
        borderColor: "#e5ddd1",
        borderRadius: 3,
        boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.04)"
      }}
    >
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2.5}>
        <Box>
          <Stack direction="row" spacing={1.5} alignItems="center">
            <Typography variant="h6" fontWeight={750} color="#29231e">
              Head-to-Head Candidate Matrix
            </Typography>
            <Chip
              size="small"
              label={`${comparedCandidates.length} Selected`}
              sx={{ fontWeight: 650, bgcolor: "#faeee7", color: "#93441f", border: "1px solid #dfbca8" }}
            />
          </Stack>
          <Typography variant="caption" color="text.secondary">
            Side-by-side requirement fulfillment matrix to resolve candidate trade-offs.
          </Typography>
        </Box>

        <Button
          size="small"
          onClick={onClearCompare}
          sx={{ color: "#70675e", textTransform: "none", fontSize: 12.5 }}
        >
          Clear Selection
        </Button>
      </Stack>

      <TableContainer sx={{ borderRadius: 2, border: "1px solid #e5ddd1" }}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead sx={{ bgcolor: "#f8f4ee" }}>
            <TableRow>
              <TableCell sx={{ color: "#70675e", fontWeight: 750, width: "28%", borderColor: "#e5ddd1" }}>
                REQUIREMENT
              </TableCell>
              {comparedCandidates.map((c) => (
                <TableCell key={c.candidate_id} sx={{ color: "#29231e", fontWeight: 750, borderColor: "#e5ddd1" }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Box minWidth={0}>
                      <Typography variant="subtitle2" fontWeight={750} noWrap color="#29231e">
                        #{c.rank} {c.filename}
                      </Typography>
                      <Typography variant="caption" color="#b4532a" fontWeight={650}>
                        Score: {Number(c.final_score || 0).toFixed(1)}
                      </Typography>
                    </Box>
                    <IconButton
                      size="small"
                      onClick={() => onRemoveCompare(c.candidate_id)}
                      sx={{ color: "#9b8e81", "&:hover": { color: "#b85145" } }}
                    >
                      <CloseRounded sx={{ fontSize: 16 }} />
                    </IconButton>
                  </Stack>
                </TableCell>
              ))}
            </TableRow>
          </TableHead>

          <TableBody>
            {/* Top Metrics Row: Final Score */}
            <TableRow sx={{ bgcolor: "#faf5ff" }}>
              <TableCell sx={{ color: "#581c87", fontWeight: 700, borderColor: "#e5ddd1" }}>
                Overall Evidence Fit Score
              </TableCell>
              {comparedCandidates.map((c) => (
                <TableCell key={c.candidate_id} sx={{ borderColor: "#e5ddd1" }}>
                  <Typography variant="h6" fontWeight={800} color="#b4532a">
                    {Number(c.final_score || 0).toFixed(1)}
                  </Typography>
                </TableCell>
              ))}
            </TableRow>

            {/* Must-Have Coverage Row */}
            <TableRow>
              <TableCell sx={{ color: "#70675e", fontWeight: 650, borderColor: "#e5ddd1" }}>
                Must-Have Coverage
              </TableCell>
              {comparedCandidates.map((c) => {
                const cov = Math.round((c.required_coverage || 0) * 100);
                return (
                  <TableCell key={c.candidate_id} sx={{ borderColor: "#e5ddd1" }}>
                    <Typography fontWeight={750} color={cov === 100 ? "#56805f" : "#c18436"}>
                      {cov}%
                    </Typography>
                  </TableCell>
                );
              })}
            </TableRow>

            {/* Mandatory Gaps Row */}
            <TableRow>
              <TableCell sx={{ color: "#70675e", fontWeight: 650, borderColor: "#e5ddd1" }}>
                Mandatory Gaps
              </TableCell>
              {comparedCandidates.map((c) => {
                const gaps = c.missing_required || [];
                return (
                  <TableCell key={c.candidate_id} sx={{ borderColor: "#e5ddd1" }}>
                    {gaps.length === 0 ? (
                      <Chip
                        size="small"
                        icon={<CheckCircleRounded sx={{ fontSize: 13, color: "#56805f !important" }} />}
                        label="Zero Gaps"
                        sx={{ bgcolor: "#e8f0e8", color: "#365d3e", border: "1px solid #c7d8c5", fontWeight: 650 }}
                      />
                    ) : (
                      <Stack spacing={0.5}>
                        <Chip
                          size="small"
                          label={`${gaps.length} Gaps`}
                          sx={{ bgcolor: "#faece9", color: "#84362f", border: "1px solid #edcbc5", fontWeight: 650, width: "fit-content" }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {gaps.join(", ")}
                        </Typography>
                      </Stack>
                    )}
                  </TableCell>
                );
              })}
            </TableRow>

            {/* Requirements rows */}
            {allReqIds.map((reqId) => {
              const req = requirementsById[reqId];
              return (
                <TableRow key={reqId} sx={{ "&:hover": { bgcolor: "#f8f4ee" } }}>
                  <TableCell sx={{ verticalAlign: "top", borderColor: "#e5ddd1" }}>
                    <Typography variant="body2" fontWeight={700} color="#29231e">
                      {req?.canonical_label || req?.original_text || reqId}
                    </Typography>
                    <Chip
                      size="small"
                      label={req?.priority || "required"}
                      sx={{
                        height: 18,
                        fontSize: 9.5,
                        textTransform: "uppercase",
                        fontWeight: 700,
                        mt: 0.5,
                        bgcolor: req?.priority === "required" ? "#faece9" : "#faeee7",
                        color: req?.priority === "required" ? "#84362f" : "#93441f",
                        border: req?.priority === "required" ? "1px solid #edcbc5" : "1px solid #dfbca8"
                      }}
                    />
                  </TableCell>

                  {comparedCandidates.map((c) => {
                    const match = (c.requirement_matches || []).find((m) => m.requirement_id === reqId);
                    if (!match) {
                      return (
                        <TableCell key={c.candidate_id} sx={{ verticalAlign: "top", borderColor: "#e5ddd1" }}>
                          <Typography variant="caption" color="text.secondary">
                            Not evaluated
                          </Typography>
                        </TableCell>
                      );
                    }

                    const statusStyles = {
                      strong: { bg: "#e8f0e8", color: "#365d3e", border: "#c7d8c5", label: "STRONG" },
                      partial: { bg: "#edf0e8", color: "#4f5b40", border: "#d5dfcc", label: "PARTIAL" },
                      weak: { bg: "#fbf0dc", color: "#8c5c20", border: "#ead2a4", label: "WEAK" },
                      missing: { bg: "#faece9", color: "#84362f", border: "#edcbc5", label: "MISSING" }
                    };
                    const sc = statusStyles[match.status] || statusStyles.weak;

                    return (
                      <TableCell key={c.candidate_id} sx={{ verticalAlign: "top", borderColor: "#e5ddd1" }}>
                        <Stack direction="row" spacing={1} alignItems="center" mb={0.5}>
                          <Chip
                            size="small"
                            label={sc.label}
                            sx={{ height: 20, fontSize: 9.5, fontWeight: 700, bgcolor: sc.bg, color: sc.color, border: `1px solid ${sc.border}` }}
                          />
                          <Typography variant="caption" fontWeight={750} color="#29231e">
                            {Math.round((match.combined_score || 0) * 100)}%
                          </Typography>
                        </Stack>

                        {match.best_evidence ? (
                          <Typography
                            variant="caption"
                            color="#70675e"
                            lineHeight={1.4}
                            display="-webkit-box"
                            sx={{
                              WebkitLineClamp: 2,
                              WebkitBoxOrient: "vertical",
                              overflow: "hidden",
                              fontStyle: "italic"
                            }}
                            title={match.best_evidence.original_text}
                          >
                            “{match.best_evidence.original_text}”
                          </Typography>
                        ) : (
                          <Typography variant="caption" color="text.secondary" fontStyle="italic">
                            No evidence found
                          </Typography>
                        )}
                      </TableCell>
                    );
                  })}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}

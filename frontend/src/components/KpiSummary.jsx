import { Box, Paper, Typography, Stack, Chip } from "@mui/material";
import {
  GroupsOutlined,
  DescriptionOutlined,
  WorkspacePremiumOutlined,
  VerifiedUserOutlined
} from "@mui/icons-material";

const metrics = {
  candidates: { icon: GroupsOutlined, color: "#b4532a", soft: "#faeee7" },
  requirements: { icon: DescriptionOutlined, color: "#657153", soft: "#edf0e8" },
  topFit: { icon: WorkspacePremiumOutlined, color: "#56805f", soft: "#e8f0e8" },
  integrity: { icon: VerifiedUserOutlined, color: "#c18436", soft: "#fbf0dc" }
};

function MetricCell({ icon: Icon, label, value, detail, tone, children, index }) {
  return (
    <Box
      sx={{
        p: { xs: 2, md: 2.25 },
        minWidth: 0,
        borderLeft: {
          xs: index % 2 ? "1px solid #e9e1d7" : 0,
          lg: index ? "1px solid #e9e1d7" : 0
        },
        borderTop: {
          xs: index > 1 ? "1px solid #e9e1d7" : 0,
          lg: 0
        }
      }}
    >
      <Stack direction="row" spacing={1.25} sx={{ alignItems: "center", mb: 1.35 }}>
        <Box
          sx={{
            width: 32,
            height: 32,
            borderRadius: 2,
            display: "grid",
            placeItems: "center",
            bgcolor: tone.soft,
            color: tone.color,
            flexShrink: 0
          }}
        >
          <Icon sx={{ fontSize: 17 }} />
        </Box>
        <Typography
          variant="caption"
          sx={{ color: "#776d63", fontWeight: 750, letterSpacing: 0.45, lineHeight: 1.2 }}
        >
          {label}
        </Typography>
      </Stack>

      <Typography
        title={typeof value === "string" ? value : undefined}
        sx={{
          color: "#29231e",
          fontWeight: 800,
          fontSize: typeof value === "string" ? { xs: 17, xl: 18 } : 28,
          letterSpacing: "-0.025em",
          lineHeight: 1.15,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap"
        }}
      >
        {value}
      </Typography>

      {children || (
        <Typography
          variant="caption"
          sx={{ color: "#70675e", display: "block", mt: 0.8, lineHeight: 1.4 }}
        >
          {detail}
        </Typography>
      )}
    </Box>
  );
}

export default function KpiSummary({ results }) {
  if (!results) return null;

  const totalCandidates = results.summary?.ranked_resumes ?? results.rankings?.length ?? 0;
  const jd = results.job_description;
  const topCandidate = results.rankings?.[0];
  const uploadedCandidates = results.summary?.uploaded_resumes ?? totalCandidates;
  const rejectedCandidates = results.summary?.rejected_resumes ?? results.rejected_files?.length ?? 0;

  let totalMatches = 0;
  let highQualityMatches = 0;
  (results.rankings || []).forEach((candidate) => {
    (candidate.requirement_matches || []).forEach((match) => {
      totalMatches += 1;
      if (
        match.evidence_quality >= 0.75 ||
        (match.best_evidence && ["experience", "projects"].includes(match.best_evidence.section))
      ) {
        highQualityMatches += 1;
      }
    });
  });
  const workProjectEvidenceRate = totalMatches
    ? Math.round((highQualityMatches / totalMatches) * 100)
    : 0;

  return (
    <Paper
      variant="outlined"
      sx={{
        display: "grid",
        gridTemplateColumns: { xs: "repeat(2, minmax(0, 1fr))", lg: "repeat(4, minmax(0, 1fr))" },
        mt: 2.25,
        mb: 2.25,
        overflow: "hidden",
        bgcolor: "rgba(255, 253, 249, 0.94)",
        borderColor: "#e5ddd1",
        borderRadius: 3.5,
        boxShadow: "0 14px 38px -32px rgba(73, 51, 35, 0.65)"
      }}
    >
      <MetricCell
        index={0}
        icon={metrics.candidates.icon}
        tone={metrics.candidates}
        label="CANDIDATES RANKED"
        value={totalCandidates}
      >
        <Typography variant="caption" sx={{ color: "#4f6b50", display: "block", mt: 0.8, fontWeight: 700 }}>
          {uploadedCandidates} uploaded · {rejectedCandidates} rejected
        </Typography>
      </MetricCell>

      <MetricCell
        index={1}
        icon={metrics.requirements.icon}
        tone={metrics.requirements}
        label="JOB REQUIREMENTS"
        value={jd?.requirement_count ?? 0}
      >
        <Stack direction="row" spacing={0.7} sx={{ mt: 0.8, flexWrap: "wrap", rowGap: 0.6 }}>
          <Chip
            size="small"
            label={`${jd?.required_count ?? 0} must-have`}
            sx={{ height: 21, fontSize: 10.5, bgcolor: "#faece9", color: "#84362f" }}
          />
          <Chip
            size="small"
            label={`${jd?.preferred_count ?? 0} preferred`}
            sx={{ height: 21, fontSize: 10.5, bgcolor: "#faeee7", color: "#93441f" }}
          />
        </Stack>
      </MetricCell>

      <MetricCell
        index={2}
        icon={metrics.topFit.icon}
        tone={metrics.topFit}
        label="TOP CANDIDATE"
        value={topCandidate?.filename?.replace(/\.[^/.]+$/, "") || "None"}
        detail={`${Number(topCandidate?.final_score || 0).toFixed(1)} score · ${Math.round(
          (topCandidate?.required_coverage || 0) * 100
        )}% must-have coverage`}
      />

      <MetricCell
        index={3}
        icon={metrics.integrity.icon}
        tone={metrics.integrity}
        label="HIGH-QUALITY EVIDENCE"
        value={`${workProjectEvidenceRate}%`}
        detail="Matches with strong evidence quality or work/project context"
      />
    </Paper>
  );
}

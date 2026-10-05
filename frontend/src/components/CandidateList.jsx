import { useState } from "react";
import {
  Paper,
  Box,
  Typography,
  Stack,
  TextField,
  InputAdornment,
  Chip,
  Checkbox,
  Tooltip,
  LinearProgress
} from "@mui/material";
import { SearchRounded, CompareArrowsRounded, EmojiEventsRounded } from "@mui/icons-material";

const colors = {
  ink: "#29231e",
  muted: "#70675e",
  line: "#e5ddd1",
  paper: "#fffdf9",
  terracotta: "#b4532a",
  terracottaSoft: "#faeee7",
  sage: "#657153",
  sageSoft: "#edf0e8",
  danger: "#b85145",
  dangerSoft: "#faece9"
};

function getScoreTone(score) {
  if (score >= 80) return { color: "#4f7758", bg: "#e8f0e8", label: "Strong" };
  if (score >= 65) return { color: "#9a5a28", bg: "#f7eadc", label: "Good" };
  if (score >= 50) return { color: "#a06b2b", bg: "#fbf0dc", label: "Review" };
  return { color: "#a4473d", bg: "#fae9e6", label: "Low" };
}

function CandidateCard({ candidate, selected, compared, onSelect, onToggleCompare }) {
  const score = Number(candidate.final_score || 0);
  const coverage = Math.round((candidate.required_coverage || 0) * 100);
  const gaps = candidate.missing_required?.length || 0;
  const tone = getScoreTone(score);

  return (
    <Paper
      component="article"
      variant="outlined"
      onClick={onSelect}
      sx={{
        p: 1.75,
        cursor: "pointer",
        borderRadius: 2.5,
        borderColor: selected ? colors.terracotta : colors.line,
        bgcolor: selected ? "#fff8f2" : colors.paper,
        boxShadow: selected
          ? "0 12px 30px -22px rgba(126, 57, 28, 0.8)"
          : "0 8px 22px -24px rgba(73, 51, 35, 0.65)",
        transition: "border-color 160ms ease, transform 160ms ease, box-shadow 160ms ease",
        position: "relative",
        overflow: "hidden",
        "&:before": selected
          ? {
              content: '""',
              position: "absolute",
              inset: "0 auto 0 0",
              width: 4,
              bgcolor: colors.terracotta
            }
          : {},
        "&:hover": {
          borderColor: selected ? colors.terracotta : "#cdbdad",
          transform: "translateY(-1px)",
          boxShadow: "0 14px 28px -22px rgba(73, 51, 35, 0.62)"
        }
      }}
    >
      <Box sx={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) auto", gap: 1.5, alignItems: "start" }}>
        <Box sx={{ minWidth: 0 }}>
          <Stack direction="row" gap={0.75} sx={{ alignItems: "center", flexWrap: "wrap", mb: 0.8 }}>
            <Chip
              size="small"
              icon={candidate.rank === 1 ? <EmojiEventsRounded /> : undefined}
              label={`Rank ${candidate.rank}`}
              sx={{
                height: 22,
                bgcolor: candidate.rank === 1 ? "#f6e7ca" : "#f1ece5",
                color: candidate.rank === 1 ? "#8a5a16" : colors.muted,
                border: `1px solid ${candidate.rank === 1 ? "#e6cc98" : colors.line}`,
                fontSize: 10.5,
                fontWeight: 800,
                "& .MuiChip-icon": { color: "inherit", fontSize: 13 }
              }}
            />
            <Typography variant="caption" sx={{ color: tone.color, fontWeight: 750 }}>
              {tone.label} match
            </Typography>
          </Stack>

          <Typography
            variant="body2"
            title={candidate.filename}
            sx={{
              color: colors.ink,
              fontWeight: 750,
              fontSize: 13.5,
              lineHeight: 1.4,
              overflowWrap: "anywhere",
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden"
            }}
          >
            {candidate.filename}
          </Typography>
        </Box>

        <Box
          sx={{
            minWidth: 62,
            px: 1.1,
            py: 0.8,
            borderRadius: 2,
            textAlign: "center",
            bgcolor: tone.bg,
            color: tone.color,
            border: "1px solid rgba(91, 67, 48, 0.08)"
          }}
        >
          <Typography sx={{ fontSize: 19, lineHeight: 1, fontWeight: 850, letterSpacing: "-0.04em" }}>
            {score.toFixed(0)}
          </Typography>
          <Typography sx={{ fontSize: 9, mt: 0.35, fontWeight: 800, letterSpacing: 0.7 }}>
            SCORE
          </Typography>
        </Box>
      </Box>

      <Box mt={1.5}>
        <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center", mb: 0.65 }}>
          <Typography variant="caption" sx={{ color: colors.muted, fontWeight: 650 }}>
            Must-have coverage
          </Typography>
          <Typography variant="caption" sx={{ color: colors.ink, fontWeight: 800 }}>
            {coverage}%
          </Typography>
        </Stack>
        <LinearProgress
          variant="determinate"
          value={coverage}
          sx={{
            height: 6,
            borderRadius: 4,
            bgcolor: "#ede6dc",
            "& .MuiLinearProgress-bar": {
              bgcolor: coverage >= 80 ? colors.sage : coverage >= 60 ? "#c18436" : colors.danger,
              borderRadius: 4
            }
          }}
        />
      </Box>

      <Stack direction="row" gap={1} sx={{ justifyContent: "space-between", alignItems: "center", mt: 1.35 }}>
        <Chip
          size="small"
          label={gaps === 0 ? "No required gaps" : `${gaps} required gap${gaps > 1 ? "s" : ""}`}
          sx={{
            maxWidth: "calc(100% - 86px)",
            height: 23,
            fontSize: 10.5,
            fontWeight: 750,
            bgcolor: gaps === 0 ? colors.sageSoft : colors.dangerSoft,
            color: gaps === 0 ? "#4c643f" : colors.danger,
            border: `1px solid ${gaps === 0 ? "#d5dfcc" : "#edcbc5"}`
          }}
        />

        <Tooltip title={compared ? "Remove from comparison" : "Add to comparison"}>
          <Stack
            component="label"
            direction="row"
            spacing={0.15}
            onClick={(event) => event.stopPropagation()}
            sx={{ alignItems: "center", cursor: "pointer", color: compared ? colors.terracotta : colors.muted, flexShrink: 0 }}
          >
            <Checkbox
              size="small"
              checked={compared}
              onChange={() => onToggleCompare(candidate.candidate_id)}
              sx={{ p: 0.35, color: "#c9beb2", "&.Mui-checked": { color: colors.terracotta } }}
            />
            <Typography variant="caption" fontWeight={700}>Compare</Typography>
          </Stack>
        </Tooltip>
      </Stack>
    </Paper>
  );
}

export default function CandidateList({
  rankings = [],
  selectedId,
  onSelectCandidate,
  comparedIds = [],
  onToggleCompare
}) {
  const [filterMode, setFilterMode] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = rankings.filter((candidate) => {
    const matchesSearch = (candidate.filename || "").toLowerCase().includes(searchQuery.toLowerCase());
    if (!matchesSearch) return false;
    if (filterMode === "no-gaps") return !candidate.missing_required?.length;
    if (filterMode === "gaps") return candidate.missing_required?.length > 0;
    return true;
  });

  const filterOptions = [
    ["all", `All ${rankings.length}`],
    ["no-gaps", "No required gaps"],
    ["gaps", "Has gaps"]
  ];

  return (
    <Paper
      variant="outlined"
      sx={{
        p: { xs: 1.75, sm: 2.25 },
        bgcolor: "rgba(255, 253, 249, 0.94)",
        borderColor: colors.line,
        borderRadius: 3.5,
        boxShadow: "0 18px 45px -36px rgba(73, 51, 35, 0.75)",
        position: { lg: "sticky" },
        top: { lg: 82 },
        maxHeight: { lg: "calc(100vh - 102px)" },
        minWidth: 0,
        display: "flex",
        flexDirection: "column"
      }}
    >
      <Stack direction="row" gap={1.5} sx={{ justifyContent: "space-between", alignItems: "flex-start", mb: 1.75 }}>
        <Box sx={{ minWidth: 0 }}>
          <Typography variant="subtitle1" fontWeight={800} color={colors.ink} sx={{ lineHeight: 1.25 }}>
            Candidate ranking
          </Typography>
          <Typography variant="caption" color={colors.muted}>
            {rankings.length} resumes scored by evidence
          </Typography>
        </Box>
        <Chip
          size="small"
          icon={<CompareArrowsRounded />}
          label={`${comparedIds.length} selected`}
          sx={{
            flexShrink: 0,
            height: 25,
            fontSize: 10.5,
            fontWeight: 750,
            border: `1px solid ${comparedIds.length ? "#d8b7a4" : colors.line}`,
            color: comparedIds.length ? "#93441f" : colors.muted,
            bgcolor: comparedIds.length ? colors.terracottaSoft : "#f5f1eb",
            "& .MuiChip-icon": { fontSize: 14, color: "inherit" }
          }}
        />
      </Stack>

      <TextField
        size="small"
        fullWidth
        placeholder="Search candidate files"
        value={searchQuery}
        onChange={(event) => setSearchQuery(event.target.value)}
        sx={{
          mb: 1.25,
          "& .MuiOutlinedInput-root": {
            bgcolor: "#f8f4ee",
            borderRadius: 2.25,
            fontSize: 13,
            color: colors.ink,
            "& fieldset": { borderColor: colors.line },
            "&:hover fieldset": { borderColor: "#cdbdad" },
            "&.Mui-focused fieldset": { borderColor: colors.terracotta }
          }
        }}
        slotProps={{
          input: {
            startAdornment: (
              <InputAdornment position="start">
                <SearchRounded sx={{ fontSize: 18, color: "#9b8e81" }} />
              </InputAdornment>
            )
          }
        }}
      />

      <Stack direction="row" gap={0.75} sx={{ flexWrap: "wrap", mb: 1.5 }}>
        {filterOptions.map(([key, label]) => (
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
              bgcolor: filterMode === key ? colors.terracottaSoft : "#f3eee7",
              color: filterMode === key ? "#93441f" : colors.muted,
              border: `1px solid ${filterMode === key ? "#dfbca8" : colors.line}`
            }}
          />
        ))}
      </Stack>

      <Box sx={{ overflowY: "auto", flex: 1, minHeight: 0, pr: { lg: 0.5 } }}>
        <Stack spacing={1.15}>
          {filtered.map((candidate) => (
            <CandidateCard
              key={candidate.candidate_id}
              candidate={candidate}
              selected={selectedId === candidate.candidate_id}
              compared={comparedIds.includes(candidate.candidate_id)}
              onSelect={() => onSelectCandidate(candidate.candidate_id)}
              onToggleCompare={onToggleCompare}
            />
          ))}
          {filtered.length === 0 && (
            <Box sx={{ textAlign: "center", py: 4, px: 2 }}>
              <Typography variant="body2" color={colors.muted}>
                No candidates match this view.
              </Typography>
            </Box>
          )}
        </Stack>
      </Box>
    </Paper>
  );
}

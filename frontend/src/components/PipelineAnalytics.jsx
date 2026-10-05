import {
  Paper,
  Box,
  Typography,
  Stack,
  Chip
} from "@mui/material";
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  Cell,
  Legend
} from "recharts";
import { AnalyticsOutlined, InsightsOutlined } from "@mui/icons-material";

export default function PipelineAnalytics({ results }) {
  if (!results || !results.rankings || results.rankings.length === 0) return null;

  const rankings = results.rankings;
  const requirements = results.job_description?.requirements || [];

  const barChartData = rankings.map((c) => ({
    name: (c.filename || "").replace(/\.[^/.]+$/, "").substring(0, 16),
    score: Number((c.final_score || 0).toFixed(1)),
    coverage: Math.round((c.required_coverage || 0) * 100),
    rank: c.rank
  }));

  const topCandidate = rankings[0];
  const secondCandidate = rankings[1] || rankings[0];

  const radarData = requirements.slice(0, 6).map((req) => {
    const topMatch = (topCandidate.requirement_matches || []).find((m) => m.requirement_id === req.requirement_id);
    const secondMatch = (secondCandidate.requirement_matches || []).find((m) => m.requirement_id === req.requirement_id);

    return {
      subject: req.canonical_label ? req.canonical_label.substring(0, 18) : req.original_text.substring(0, 18),
      topCandidate: Math.round((topMatch?.combined_score || 0) * 100),
      secondCandidate: Math.round((secondMatch?.combined_score || 0) * 100),
      fullMark: 100
    };
  });

  const reqDifficultyData = requirements.map((req) => {
    let strong = 0;
    let partial = 0;
    let missing = 0;

    rankings.forEach((c) => {
      const match = (c.requirement_matches || []).find((m) => m.requirement_id === req.requirement_id);
      if (!match || match.status === "missing") missing++;
      else if (match.status === "strong") strong++;
      else partial++;
    });

    return {
      label: req.canonical_label || req.original_text.substring(0, 22),
      priority: req.priority,
      strong,
      partial,
      missing,
      total: rankings.length,
      fulfillmentRate: Math.round((strong / rankings.length) * 100)
    };
  });

  return (
    <Box>
      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", lg: "1.2fr 1fr" }, gap: 3, mb: 3 }}>
        {/* Chart 1: Candidate Score Leaderboard */}
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
          <Stack direction="row" spacing={1.5} alignItems="center" mb={0.5}>
            <InsightsOutlined sx={{ color: "#b4532a" }} />
            <Typography variant="subtitle1" fontWeight={750} color="#29231e">
              Score Distribution Across Applicants
            </Typography>
          </Stack>
          <Typography variant="caption" color="text.secondary" display="block" mb={2}>
            Overall evidence fit scores across all ranked candidates.
          </Typography>

          <Box sx={{ width: "100%", height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barChartData} margin={{ top: 10, right: 20, left: -20, bottom: 20 }}>
                <XAxis
                  dataKey="name"
                  stroke="#70675e"
                  fontSize={11}
                  tickLine={false}
                  interval={0}
                  angle={-15}
                  textAnchor="end"
                />
                <YAxis stroke="#70675e" fontSize={11} domain={[0, 100]} />
                <RechartsTooltip
                  contentStyle={{
                    backgroundColor: "#fffdf9",
                    borderColor: "#cdbdad",
                    borderRadius: 8,
                    fontSize: 12,
                    boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
                    color: "#29231e"
                  }}
                  formatter={(value, name) => [
                    `${value}%`,
                    name === "score" ? "Evidence Fit Score" : "Must-Have Coverage"
                  ]}
                />
                <Bar dataKey="score" radius={[5, 5, 0, 0]}>
                  {barChartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={
                        entry.rank === 1
                          ? "#56805f"
                          : entry.rank === 2
                          ? "#657153"
                          : entry.rank === 3
                          ? "#b4532a"
                          : "#c18436"
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </Paper>

        {/* Chart 2: Competency Radar Chart */}
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
          <Stack direction="row" spacing={1.5} alignItems="center" mb={0.5}>
            <AnalyticsOutlined sx={{ color: "#657153" }} />
            <Typography variant="subtitle1" fontWeight={750} color="#29231e">
              Competency Radar (Top Candidates)
            </Typography>
          </Stack>
          <Typography variant="caption" color="text.secondary" display="block" mb={2}>
            Head-to-head domain overlay between Rank #1 and Rank #2.
          </Typography>

          <Box sx={{ width: "100%", height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid stroke="#e5ddd1" />
                <PolarAngleAxis dataKey="subject" stroke="#70675e" fontSize={10} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#cdbdad" fontSize={9} />
                <Radar
                  name={topCandidate.filename ? topCandidate.filename.substring(0, 15) : "Rank #1"}
                  dataKey="topCandidate"
                  stroke="#56805f"
                  fill="#56805f"
                  fillOpacity={0.25}
                />
                {rankings.length > 1 && (
                  <Radar
                    name={secondCandidate.filename ? secondCandidate.filename.substring(0, 15) : "Rank #2"}
                    dataKey="secondCandidate"
                    stroke="#657153"
                    fill="#657153"
                    fillOpacity={0.2}
                  />
                )}
                <Legend
                  wrapperStyle={{ fontSize: 11, paddingTop: 10 }}
                  formatter={(value) => <span style={{ color: "#514941" }}>{value}</span>}
                />
              </RadarChart>
            </ResponsiveContainer>
          </Box>
        </Paper>
      </Box>

      {/* Requirement Difficulty / Scarcity Matrix */}
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
        <Typography variant="subtitle1" fontWeight={750} color="#29231e" mb={0.3}>
          Requirement Fulfillment Distribution
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block" mb={2.5}>
          Distribution of applicant qualifications across each job requirement.
        </Typography>

        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "repeat(2, 1fr)" }, gap: 2 }}>
          {reqDifficultyData.map((item, idx) => (
            <Box
              key={idx}
              sx={{
                p: 1.8,
                bgcolor: "#f8f4ee",
                border: "1px solid #e5ddd1",
                borderRadius: 2
              }}
            >
              <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" fontWeight={700} color="#29231e" noWrap title={item.label}>
                  {item.label}
                </Typography>
                <Chip
                  size="small"
                  label={item.priority}
                  sx={{
                    height: 18,
                    fontSize: 9.5,
                    textTransform: "uppercase",
                    fontWeight: 700,
                    bgcolor: item.priority === "required" ? "#faece9" : "#faeee7",
                    color: item.priority === "required" ? "#84362f" : "#93441f",
                    border: item.priority === "required" ? "1px solid #edcbc5" : "1px solid #dfbca8"
                  }}
                />
              </Stack>

              {/* Progress stack */}
              <Box sx={{ display: "flex", height: 7, borderRadius: 4, overflow: "hidden", bgcolor: "#e5ddd1", mb: 1 }}>
                <Box sx={{ width: `${(item.strong / item.total) * 100}%`, bgcolor: "#56805f" }} />
                <Box sx={{ width: `${(item.partial / item.total) * 100}%`, bgcolor: "#657153" }} />
                <Box sx={{ width: `${(item.missing / item.total) * 100}%`, bgcolor: "#b85145" }} />
              </Box>

              <Stack direction="row" justifyContent="space-between" fontSize={11}>
                <Typography variant="caption" color="#365d3e" fontWeight={600}>
                  {item.strong} Strong
                </Typography>
                <Typography variant="caption" color="#4f5b40" fontWeight={600}>
                  {item.partial} Partial
                </Typography>
                <Typography variant="caption" color="#84362f" fontWeight={600}>
                  {item.missing} Missing
                </Typography>
              </Stack>
            </Box>
          ))}
        </Box>
      </Paper>
    </Box>
  );
}

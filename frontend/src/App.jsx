import { useMemo, useState } from "react";
import axios from "axios";
import {
  Accordion, AccordionDetails, AccordionSummary, Alert, Avatar, Box, Button,
  Chip, CircularProgress, Container, CssBaseline, Divider, LinearProgress,
  Paper, Stack, ThemeProvider, Typography, createTheme,
} from "@mui/material";
import {
  ArrowForwardRounded, CheckCircleRounded, CloudUploadRounded, DescriptionRounded,
  DownloadRounded, ExpandMoreRounded, FactCheckRounded, GroupsRounded,
  SearchRounded, ShieldRounded, WorkspacePremiumRounded,
} from "@mui/icons-material";

const API_URL = "http://127.0.0.1:8000";
const statusColor = { strong: "success", partial: "primary", weak: "warning", missing: "error" };
const priorityOrder = { required: 0, preferred: 1, contextual: 2 };

const theme = createTheme({
  palette: {
    mode: "dark", primary: { main: "#8b5cf6", light: "#a78bfa" },
    secondary: { main: "#22d3ee" }, background: { default: "#070913", paper: "#101626" },
    success: { main: "#2dd4bf" }, warning: { main: "#fbbf24" }, error: { main: "#fb7185" },
  },
  typography: {
    fontFamily: 'Inter, "Segoe UI", sans-serif',
    h3: { fontWeight: 850, letterSpacing: "-0.045em" }, h4: { fontWeight: 800 },
    h5: { fontWeight: 750 }, h6: { fontWeight: 700 }, button: { textTransform: "none", fontWeight: 750 },
  },
  shape: { borderRadius: 14 },
  components: {
    MuiPaper: { styleOverrides: { root: { backgroundImage: "none" } } },
    MuiButton: { styleOverrides: { root: { borderRadius: 10 } } },
  },
});

function UploadTile({ title, files, multiple, onChange }) {
  return <Button component="label" variant="outlined" fullWidth sx={{ justifyContent: "flex-start", p: 1.5,
    color: "text.primary", borderColor: files.length ? "rgba(45,212,191,.5)" : "rgba(255,255,255,.12)",
    background: files.length ? "rgba(45,212,191,.05)" : "rgba(255,255,255,.025)" }}>
    <Avatar variant="rounded" sx={{ mr: 1.5, width: 38, height: 38, bgcolor: "rgba(139,92,246,.16)", color: "primary.light" }}>
      {files.length ? <CheckCircleRounded /> : <CloudUploadRounded />}
    </Avatar>
    <Box textAlign="left" minWidth={0} flex={1}>
      <Typography variant="body2" fontWeight={750}>{title}</Typography>
      <Typography variant="caption" color="text.secondary" noWrap display="block">
        {files.length ? (multiple ? `${files.length} resumes selected` : files[0].name) : "PDF, DOCX, TXT or XML"}
      </Typography>
    </Box>
    <input hidden type="file" multiple={multiple} accept=".pdf,.docx,.txt,.xml"
      onChange={(event) => onChange(Array.from(event.target.files))} />
  </Button>;
}

function Stat({ icon, value, label, accent }) {
  return <Stack direction="row" spacing={1.3} alignItems="center" sx={{ minWidth: 0 }}>
    <Avatar sx={{ width: 38, height: 38, bgcolor: `${accent}18`, color: accent }}>{icon}</Avatar>
    <Box minWidth={0}><Typography variant="h6" noWrap>{value}</Typography>
      <Typography variant="caption" color="text.secondary">{label}</Typography></Box>
  </Stack>;
}

function ScoreRing({ score, size = 72 }) {
  const value = Math.max(0, Math.min(100, Number(score || 0)));
  return <Box sx={{ width: size, height: size, borderRadius: "50%", flexShrink: 0,
    background: `conic-gradient(#22d3ee ${value * 3.6}deg, rgba(255,255,255,.08) 0)`, p: "5px" }}>
    <Box sx={{ width: "100%", height: "100%", borderRadius: "50%", bgcolor: "#0c1220", display: "grid", placeItems: "center" }}>
      <Box textAlign="center"><Typography fontWeight={850} fontSize={size * .25}>{value.toFixed(1)}</Typography>
        <Typography sx={{ fontSize: 8, color: "text.secondary", letterSpacing: 1 }}>SCORE</Typography></Box>
    </Box>
  </Box>;
}

function CandidateRow({ candidate, selected, onSelect }) {
  const coverage = Math.round((candidate.required_coverage || 0) * 100);
  return <Paper onClick={onSelect} variant="outlined" sx={{ p: 1.7, cursor: "pointer", transition: ".18s ease",
    borderColor: selected ? "primary.main" : "rgba(255,255,255,.08)",
    bgcolor: selected ? "rgba(139,92,246,.10)" : "rgba(255,255,255,.018)",
    boxShadow: selected ? "0 0 0 1px rgba(139,92,246,.22)" : "none",
    "&:hover": { borderColor: "rgba(139,92,246,.65)", transform: "translateY(-1px)" } }}>
    <Stack direction="row" spacing={1.4} alignItems="center">
      <Avatar sx={{ width: 38, height: 38, fontWeight: 850, fontSize: 14,
        background: candidate.rank === 1 ? "linear-gradient(135deg,#8b5cf6,#22d3ee)" : "rgba(255,255,255,.07)" }}>
        {candidate.rank}
      </Avatar>
      <Box flex={1} minWidth={0}><Typography fontWeight={700} noWrap title={candidate.filename}>{candidate.filename}</Typography>
        <Stack direction="row" spacing={1} alignItems="center" mt={.4}>
          <Typography variant="caption" color="text.secondary">{coverage}% required</Typography>
          <Typography variant="caption" color="error.main">{candidate.missing_required?.length || 0} gaps</Typography>
        </Stack>
      </Box>
      <Box textAlign="right"><Typography variant="h6" color="secondary.main">{Number(candidate.final_score || 0).toFixed(1)}</Typography>
        <Typography sx={{ fontSize: 9, color: "text.secondary" }}>EVIDENCE</Typography></Box>
    </Stack>
  </Paper>;
}

function MiniScore({ label, value }) {
  const percent = Math.round((value || 0) * 100);
  return <Box><Stack direction="row" justifyContent="space-between" mb={.5}>
    <Typography variant="caption" color="text.secondary">{label}</Typography><Typography variant="caption">{percent}%</Typography>
  </Stack><LinearProgress variant="determinate" value={percent} sx={{ height: 4, borderRadius: 4 }} /></Box>;
}

function EvidenceDecision({ match, requirement }) {
  const evidence = match.best_evidence;
  return <Accordion disableGutters sx={{ mb: 1, bgcolor: "rgba(255,255,255,.018)",
    border: "1px solid rgba(255,255,255,.075)", "&:before": { display: "none" } }}>
    <AccordionSummary expandIcon={<ExpandMoreRounded />} sx={{ minHeight: 58 }}>
      <Stack direction="row" alignItems="center" width="100%" spacing={1.2} pr={1} minWidth={0}>
        <Box sx={{ width: 8, height: 8, borderRadius: "50%", flexShrink: 0,
          bgcolor: match.status === "strong" ? "success.main" : match.status === "partial" ? "primary.main" :
            match.status === "weak" ? "warning.main" : "error.main" }} />
        <Box flex={1} minWidth={0}><Typography fontWeight={650} noWrap>{match.requirement_label}</Typography>
          <Typography variant="caption" color="text.secondary">{requirement?.priority || "unknown"} requirement</Typography></Box>
        <Chip size="small" label={match.status} color={statusColor[match.status]} variant="outlined" />
        <Typography fontWeight={850} width={34} textAlign="right">{Math.round((match.combined_score || 0) * 100)}</Typography>
      </Stack>
    </AccordionSummary>
    <AccordionDetails sx={{ pt: 0 }}><Divider sx={{ mb: 2 }} />
      {evidence ? <Paper variant="outlined" sx={{ p: 2, bgcolor: "rgba(34,211,238,.035)", borderColor: "rgba(34,211,238,.18)" }}>
        <Typography variant="caption" color="secondary.main" fontWeight={800}>SOURCE EVIDENCE</Typography>
        <Typography mt={.8} lineHeight={1.65}>“{evidence.original_text}”</Typography>
        <Stack direction="row" gap={.7} flexWrap="wrap" mt={1.2}>
          <Chip size="small" label={`Page ${evidence.page_number}`} /> <Chip size="small" label={evidence.section} />
          {(match.matched_terms || []).map((term) => <Chip key={term} size="small" color="secondary" variant="outlined" label={term} />)}
        </Stack>
      </Paper> : <Alert severity="warning">No supporting evidence found in this resume.</Alert>}
      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr 1fr", md: "repeat(4,1fr)" }, gap: 1.5, mt: 2 }}>
        <MiniScore label="Keyword" value={match.keyword_score} /><MiniScore label="Semantic" value={match.semantic_score} />
        <MiniScore label="Relations" value={match.relation_score} /><MiniScore label="Evidence quality" value={match.evidence_quality} />
      </Box>
    </AccordionDetails>
  </Accordion>;
}

function CandidateWorkspace({ candidate, requirementsById }) {
  const [filter, setFilter] = useState("all");
  if (!candidate) return null;
  const coverage = Math.round((candidate.required_coverage || 0) * 100);
  const matches = [...(candidate.requirement_matches || [])].sort((a, b) =>
    (priorityOrder[requirementsById[a.requirement_id]?.priority] ?? 3) -
    (priorityOrder[requirementsById[b.requirement_id]?.priority] ?? 3));
  const visible = matches.filter((m) => filter === "all" || (filter === "required"
    ? requirementsById[m.requirement_id]?.priority === "required" : m.status === "missing"));

  return <Box>
    <Paper sx={{ p: { xs: 2, md: 3 }, border: "1px solid rgba(255,255,255,.08)",
      background: "linear-gradient(145deg,rgba(18,26,46,.98),rgba(10,15,28,.98))" }}>
      <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" gap={2}>
        <Stack direction="row" spacing={2} alignItems="center"><ScoreRing score={candidate.final_score} />
          <Box minWidth={0}>{candidate.rank === 1 && <Chip size="small" icon={<WorkspacePremiumRounded />} label="Recommended shortlist" color="success" sx={{ mb: 1 }} />}
            <Typography variant="h5" noWrap title={candidate.filename}>{candidate.filename}</Typography>
            <Typography variant="body2" color="text.secondary">Rank #{candidate.rank} • {candidate.evidence_span_count} evidence spans</Typography></Box>
        </Stack>
        <Stack direction="row" gap={2} alignItems="center"><Box textAlign="center"><Typography variant="h5">{coverage}%</Typography>
          <Typography variant="caption" color="text.secondary">REQUIRED</Typography></Box><Divider orientation="vertical" flexItem />
          <Box textAlign="center"><Typography variant="h5" color="error.main">{candidate.missing_required?.length || 0}</Typography>
            <Typography variant="caption" color="text.secondary">GAPS</Typography></Box></Stack>
      </Stack>
      <Box mt={2.5}><Stack direction="row" justifyContent="space-between" mb={.7}><Typography variant="body2">Must-have coverage</Typography>
        <Typography variant="body2" fontWeight={750}>{coverage}%</Typography></Stack>
        <LinearProgress variant="determinate" value={coverage} sx={{ height: 8, borderRadius: 8 }} /></Box>
      <Stack direction="row" gap={.8} flexWrap="wrap" mt={2}>
        {Object.entries(candidate.status_counts || {}).map(([key, count]) => <Chip key={key} size="small" variant="outlined"
          color={statusColor[key]} label={`${count} ${key}`} />)}
      </Stack>
      {!!candidate.missing_required?.length && <Alert severity="warning" sx={{ mt: 2 }}>
        <strong>Mandatory gaps:</strong> {candidate.missing_required.join(", ")}
      </Alert>}
    </Paper>

    <Stack direction={{ xs: "column", sm: "row" }} justifyContent="space-between" alignItems={{ sm: "center" }} mt={3} mb={1.5} gap={1}>
      <Box><Typography variant="h6">Evidence ledger</Typography><Typography variant="body2" color="text.secondary">
        Every decision is traceable to the original resume.</Typography></Box>
      <Stack direction="row" gap={.7}>{[["all","All"],["required","Required"],["gaps","Gaps"]].map(([key,label]) =>
        <Chip key={key} clickable onClick={() => setFilter(key)} color={filter === key ? "primary" : "default"}
          variant={filter === key ? "filled" : "outlined"} label={label} />)}</Stack>
    </Stack>
    {visible.length ? visible.map((match) => <EvidenceDecision key={match.requirement_id} match={match}
      requirement={requirementsById[match.requirement_id]} />) : <Alert severity="success">No missing requirements.</Alert>}
  </Box>;
}

export default function App() {
  const [jobFile, setJobFile] = useState([]); const [resumeFiles, setResumeFiles] = useState([]);
  const [results, setResults] = useState(null); const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  const requirementsById = useMemo(() => Object.fromEntries(
    (results?.job_description?.requirements || []).map((r) => [r.requirement_id, r])), [results]);
  const selected = results?.rankings?.find((c) => c.candidate_id === selectedId) || results?.rankings?.[0];

  async function analyze() {
    if (!jobFile.length || !resumeFiles.length) return;
    setLoading(true); setError(""); setResults(null);
    const body = new FormData(); body.append("job_description", jobFile[0]);
    resumeFiles.forEach((file) => body.append("resumes", file));
    try { const data = (await axios.post(`${API_URL}/rank`, body)).data; setResults(data); setSelectedId(data.rankings[0]?.candidate_id); }
    catch (e) { const detail = e.response?.data?.detail; setError(typeof detail === "string" ? detail : detail?.message || "Analysis failed. Check FastAPI."); }
    finally { setLoading(false); }
  }

  function downloadJSON() {
    const url = URL.createObjectURL(new Blob([JSON.stringify(results, null, 2)], { type: "application/json" }));
    const a = document.createElement("a"); a.href = url; a.download = "EvidenceRank_audit.json"; a.click(); URL.revokeObjectURL(url);
  }

  return <ThemeProvider theme={theme}><CssBaseline /><Box sx={{ minHeight: "100vh", background:
    "radial-gradient(circle at 12% -10%,rgba(124,58,237,.28),transparent 35%),#070913" }}>
    <Box component="header" sx={{ borderBottom: "1px solid rgba(255,255,255,.07)", bgcolor: "rgba(7,9,19,.82)", backdropFilter: "blur(16px)" }}>
      <Container maxWidth={false} sx={{ maxWidth: 1500 }}><Stack direction="row" justifyContent="space-between" alignItems="center" py={1.7}>
        <Stack direction="row" spacing={1.2} alignItems="center"><Avatar variant="rounded" sx={{ bgcolor: "primary.main" }}><SearchRounded /></Avatar>
          <Box><Typography variant="h6" lineHeight={1}>EvidenceRank</Typography><Typography sx={{ fontSize: 9, color: "secondary.main", letterSpacing: 1.5 }}>DECISION INTELLIGENCE</Typography></Box></Stack>
        <Chip icon={<ShieldRounded />} label="On-device • Private" color="success" variant="outlined" />
      </Stack></Container>
    </Box>

    <Container maxWidth={false} sx={{ maxWidth: 1500, py: 4 }}>
      {!results && <Box mb={4} textAlign="center"><Typography variant="overline" color="secondary.main" letterSpacing={2.5}>Evidence-first hiring</Typography>
        <Typography variant="h3" mt={.5}>Shortlist with confidence.</Typography><Typography color="text.secondary" mt={1}>
          Transparent candidate ranking backed by exact resume evidence.</Typography></Box>}

      <Paper sx={{ p: 2, border: "1px solid rgba(255,255,255,.08)", bgcolor: "rgba(16,22,38,.88)" }}>
        <Stack direction={{ xs: "column", md: "row" }} spacing={1.5} alignItems="stretch">
          <Box flex={1}><UploadTile title="Job description" files={jobFile} onChange={setJobFile} /></Box>
          <Box flex={1.35}><UploadTile title="Candidate resumes" multiple files={resumeFiles} onChange={setResumeFiles} /></Box>
          <Button variant="contained" disabled={!jobFile.length || !resumeFiles.length || loading} onClick={analyze}
            endIcon={!loading && <ArrowForwardRounded />} sx={{ px: 4, minHeight: 62, background: "linear-gradient(100deg,#7c3aed,#0891b2)" }}>
            {loading ? <><CircularProgress size={18} color="inherit" sx={{ mr: 1 }} />Ranking evidence…</> : "Analyze candidates"}
          </Button>
        </Stack>{error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      </Paper>

      {results && <>
        <Paper sx={{ mt: 2, px: 2.5, py: 1.8, border: "1px solid rgba(255,255,255,.07)", bgcolor: "rgba(16,22,38,.72)" }}>
          <Stack direction={{ xs: "column", md: "row" }} spacing={4} justifyContent="space-between" alignItems={{ md: "center" }}>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={4}>
              <Stat icon={<GroupsRounded />} value={results.summary.ranked_resumes} label="Candidates ranked" accent="#8b5cf6" />
              <Stat icon={<DescriptionRounded />} value={results.job_description.requirement_count} label="Requirements" accent="#22d3ee" />
              <Stat icon={<FactCheckRounded />} value={`${results.job_description.required_count} / ${results.job_description.preferred_count}`}
                label="Required / preferred" accent="#2dd4bf" />
            </Stack>
            <Button onClick={downloadJSON} startIcon={<DownloadRounded />}>Download audit report</Button>
          </Stack>
        </Paper>

        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", lg: "350px minmax(0,1fr)" }, gap: 2, mt: 2, alignItems: "start" }}>
          <Paper sx={{ p: 2, border: "1px solid rgba(255,255,255,.08)", bgcolor: "rgba(16,22,38,.82)",
            position: { lg: "sticky" }, top: { lg: 20 }, maxHeight: { lg: "calc(100vh - 40px)" }, overflow: "auto" }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1.5}><Box>
              <Typography variant="h6">Candidate ranking</Typography><Typography variant="caption" color="text.secondary">Select a candidate to audit</Typography></Box>
              <Chip size="small" label={`${results.rankings.length} total`} /></Stack>
            <Stack spacing={1}>{results.rankings.map((candidate) => <CandidateRow key={candidate.candidate_id} candidate={candidate}
              selected={selected?.candidate_id === candidate.candidate_id} onSelect={() => setSelectedId(candidate.candidate_id)} />)}</Stack>
          </Paper>
          <CandidateWorkspace candidate={selected} requirementsById={requirementsById} />
        </Box>
      </>}
    </Container>
  </Box></ThemeProvider>;
}

import { lazy, Suspense, useState, useEffect, useMemo } from "react";
import axios from "axios";
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  Container,
  Stack,
  Tabs,
  Tab,
  Typography,
  Button,
  Paper,
  Collapse,
  Alert,
  CircularProgress
} from "@mui/material";
import {
  FactCheckRounded,
  CompareArrowsRounded,
  AnalyticsRounded,
  TuneRounded,
  KeyboardArrowUpRounded,
  KeyboardArrowDownRounded
} from "@mui/icons-material";

// Components
import Navbar from "./components/Navbar";
import HeroBanner from "./components/HeroBanner";
import UploadStudio from "./components/UploadStudio";
import KpiSummary from "./components/KpiSummary";
import CandidateList from "./components/CandidateList";
import CandidateAuditView from "./components/CandidateAuditView";
import ArchitectureModal from "./components/ArchitectureModal";

// Demo Data
import { DEMO_RESULTS } from "./data/demoData";

const CandidateComparison = lazy(() => import("./components/CandidateComparison"));
const PipelineAnalytics = lazy(() => import("./components/PipelineAnalytics"));

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function ViewLoadingFallback() {
  return (
    <Paper variant="outlined" sx={{ p: 5, textAlign: "center", borderRadius: 3 }}>
      <CircularProgress size={26} />
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1.5 }}>
        Loading this view…
      </Typography>
    </Paper>
  );
}

const theme = createTheme({
  palette: {
    mode: "light",
    primary: { main: "#b4532a", light: "#d97745", dark: "#813718" },
    secondary: { main: "#657153", light: "#879374", dark: "#465039" },
    background: { default: "#f5f0e8", paper: "#fffdf9" },
    success: { main: "#56805f", light: "#76a27e", dark: "#365d3e" },
    warning: { main: "#c18436", light: "#dda75a", dark: "#8c5c20" },
    error: { main: "#b85145", light: "#d3776c", dark: "#84362f" },
    text: { primary: "#29231e", secondary: "#70675e" },
    divider: "#e5ddd1"
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Inter", -apple-system, sans-serif',
    h3: { fontWeight: 800, letterSpacing: "-0.035em", lineHeight: 1.08 },
    h4: { fontWeight: 800, letterSpacing: "-0.025em", lineHeight: 1.12 },
    h5: { fontWeight: 750, letterSpacing: "-0.02em", lineHeight: 1.2 },
    h6: { fontWeight: 700, letterSpacing: "-0.015em", lineHeight: 1.25 },
    body1: { lineHeight: 1.65 },
    body2: { lineHeight: 1.6 },
    button: { textTransform: "none", fontWeight: 700, letterSpacing: 0 }
  },
  shape: { borderRadius: 10 },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          borderColor: "#e5ddd1"
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          boxShadow: "none",
          "&:hover": { boxShadow: "none" }
        }
      }
    },
    MuiChip: {
      styleOverrides: {
          root: { borderRadius: 8 }
      }
    }
  }
});

export default function App() {
  const [jobFile, setJobFile] = useState([]);
  const [resumeFiles, setResumeFiles] = useState([]);
  const [results, setResults] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [comparedIds, setComparedIds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [backendOnline, setBackendOnline] = useState(false);
  const [isDemoActive, setIsDemoActive] = useState(false);
  const [activeTab, setActiveTab] = useState("audit"); // "audit", "compare", "analytics"
  const [architectureOpen, setArchitectureOpen] = useState(false);
  const [showUploadStudio, setShowUploadStudio] = useState(true);

  // Ping backend health on mount
  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await axios.get(`${API_URL}/health`, { timeout: 2500 });
        if (res.data && res.data.status === "healthy") {
          setBackendOnline(true);
        }
      } catch {
        setBackendOnline(false);
      }
    }
    checkHealth();
  }, []);

  // Quick lookup dictionary for requirements by ID
  const requirementsById = useMemo(() => {
    return Object.fromEntries(
      (results?.job_description?.requirements || []).map((r) => [r.requirement_id, r])
    );
  }, [results]);

  // Selected candidate object
  const selectedCandidate = useMemo(() => {
    if (!results || !results.rankings) return null;
    return results.rankings.find((c) => c.candidate_id === selectedId) || results.rankings[0];
  }, [results, selectedId]);

  // Trigger analysis against FastAPI backend
  async function handleAnalyze(finalJobFile, finalResumeFiles) {
    setLoading(true);
    setError("");
    setIsDemoActive(false);

    const body = new FormData();
    body.append("job_description", finalJobFile);
    finalResumeFiles.forEach((file) => body.append("resumes", file));

    try {
      const response = await axios.post(`${API_URL}/rank`, body);
      const data = response.data;
      setBackendOnline(true);
      setResults(data);
      if (data.rankings && data.rankings.length > 0) {
        setSelectedId(data.rankings[0].candidate_id);
        // Pre-select top 2 for comparison
        setComparedIds(data.rankings.slice(0, 2).map((c) => c.candidate_id));
      }
      setShowUploadStudio(false);
    } catch (e) {
      console.error("API error", e);
      const detail = e.response?.data?.detail;
      const errorMsg =
        typeof detail === "string"
          ? detail
          : detail?.message || "Analysis failed. Please check if FastAPI backend is running on port 8000.";
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  }

  // Load sample demo dataset for instant walkthrough
  function handleLoadDemo() {
    setResults(DEMO_RESULTS);
    setSelectedId(DEMO_RESULTS.rankings[0].candidate_id);
    setComparedIds([DEMO_RESULTS.rankings[0].candidate_id, DEMO_RESULTS.rankings[1].candidate_id]);
    setIsDemoActive(true);
    setError("");
    setShowUploadStudio(false);
  }

  // Reset to initial state
  function handleReset() {
    setResults(null);
    setSelectedId(null);
    setComparedIds([]);
    setIsDemoActive(false);
    setError("");
    setShowUploadStudio(true);
  }

  // Toggle candidate comparison
  function handleToggleCompare(candidateId) {
    setComparedIds((prev) => {
      if (prev.includes(candidateId)) {
        return prev.filter((id) => id !== candidateId);
      } else {
        if (prev.length >= 3) {
          return [prev[1], prev[2], candidateId];
        }
        return [...prev, candidateId];
      }
    });
  }

  function handleRemoveCompare(candidateId) {
    setComparedIds((prev) => prev.filter((id) => id !== candidateId));
  }

  function handleClearCompare() {
    setComparedIds([]);
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "100vh",
          bgcolor: "#f5f0e8",
          backgroundImage: `
            radial-gradient(ellipse 75% 42% at 8% -8%, rgba(191, 112, 65, 0.13), transparent 68%),
            radial-gradient(ellipse 55% 34% at 96% 8%, rgba(101, 113, 83, 0.10), transparent 66%),
            linear-gradient(180deg, #f8f4ed 0%, #f2ece3 100%)
          `,
          pb: 10
        }}
      >
        {/* Navigation Bar */}
        <Navbar
          backendOnline={backendOnline}
          isDemoActive={isDemoActive}
          onLoadDemo={handleLoadDemo}
          onReset={handleReset}
          onOpenArchitecture={() => setArchitectureOpen(true)}
          results={results}
        />

        <Container maxWidth={false} sx={{ maxWidth: 1600, px: { xs: 2, sm: 3, md: 4 } }}>
          {/* Hero Banner if no results loaded yet */}
          {!results && <HeroBanner />}

          {/* Upload Studio Collapsible Section */}
          <Box mt={results ? 2.25 : 2} mb={results ? 2.25 : 3}>
            {results && (
              <Paper
                variant="outlined"
                sx={{
                  px: { xs: 1.5, sm: 2 },
                  py: 1.35,
                  mb: showUploadStudio ? 1.5 : 0,
                  bgcolor: "rgba(255, 253, 249, 0.86)",
                  borderColor: "#e5ddd1",
                  borderRadius: 2.75,
                  boxShadow: "0 10px 28px -28px rgba(73, 51, 35, 0.7)"
                }}
              >
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  gap={{ xs: 1.25, sm: 2 }}
                  sx={{ justifyContent: "space-between", alignItems: { xs: "stretch", sm: "center" } }}
                >
                  <Stack direction="row" spacing={1.25} sx={{ alignItems: "center", minWidth: 0 }}>
                    <Box
                      sx={{
                        width: 34,
                        height: 34,
                        borderRadius: 2,
                        display: "grid",
                        placeItems: "center",
                        bgcolor: "#faeee7",
                        color: "#b4532a",
                        flexShrink: 0
                      }}
                    >
                      <TuneRounded sx={{ fontSize: 18 }} />
                    </Box>
                    <Box sx={{ minWidth: 0 }}>
                      <Typography
                        variant="caption"
                        sx={{ color: "#7b7066", fontWeight: 750, letterSpacing: 0.45, display: "block" }}
                      >
                        ACTIVE ROLE
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ color: "#29231e", fontWeight: 750, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}
                      >
                        {isDemoActive ? "Senior Full-Stack Cloud Engineer" : "Current ranking configuration"}
                      </Typography>
                    </Box>
                  </Stack>

                  <Button
                    size="small"
                    onClick={() => setShowUploadStudio(!showUploadStudio)}
                    endIcon={showUploadStudio ? <KeyboardArrowUpRounded /> : <KeyboardArrowDownRounded />}
                    sx={{
                      color: "#7b4c32",
                      fontSize: 12.5,
                      flexShrink: 0,
                      justifyContent: { xs: "space-between", sm: "center" },
                      bgcolor: "#f7f0e9",
                      border: "1px solid #e7d9cc",
                      px: 1.5,
                      "&:hover": { bgcolor: "#f1e5da", borderColor: "#d9c1af" }
                    }}
                  >
                    {showUploadStudio ? "Hide input settings" : "Change role or resumes"}
                  </Button>
                </Stack>
              </Paper>
            )}

            <Collapse in={showUploadStudio}>
              <UploadStudio
                jobFile={jobFile}
                setJobFile={setJobFile}
                resumeFiles={resumeFiles}
                setResumeFiles={setResumeFiles}
                loading={loading}
                error={error}
                onAnalyze={handleAnalyze}
                onLoadDemo={handleLoadDemo}
              />
            </Collapse>
          </Box>

          {/* Results Dashboard */}
          {results && (
            <Box className="animate-fade-in">
              {/* Executive KPI Summary Cards */}
              <KpiSummary results={results} />

              {results.rejected_files?.length > 0 && (
                <Alert severity="warning" sx={{ mb: 2.25, borderRadius: 2.5 }}>
                  {results.rejected_files.length} uploaded resume
                  {results.rejected_files.length === 1 ? " was" : "s were"} not ranked. {" "}
                  {results.rejected_files.map((file) => file.filename).join(", ")}
                </Alert>
              )}

              {/* View Switcher Tabs */}
              <Paper
                variant="outlined"
                sx={{
                  mb: 3,
                  px: 1.5,
                  py: 0.5,
                  bgcolor: "rgba(255, 253, 249, 0.92)",
                  borderColor: "#e5ddd1",
                  borderRadius: 3,
                  boxShadow: "0 10px 30px -24px rgba(73, 51, 35, 0.45)"
                }}
              >
                <Tabs
                  value={activeTab}
                  onChange={(_, val) => setActiveTab(val)}
                  sx={{
                    minHeight: 44,
                    "& .MuiTabs-indicator": { bgcolor: "#b4532a", height: 3, borderRadius: 3 }
                  }}
                >
                  <Tab
                    value="audit"
                    icon={<FactCheckRounded sx={{ fontSize: 18 }} />}
                    iconPosition="start"
                    label="Candidate Audit Ledger"
                    sx={{
                      textTransform: "none",
                      fontWeight: 650,
                      fontSize: 13.5,
                      minHeight: 44,
                      color: activeTab === "audit" ? "#9a431f" : "#70675e"
                    }}
                  />
                  <Tab
                    value="compare"
                    icon={<CompareArrowsRounded sx={{ fontSize: 18 }} />}
                    iconPosition="start"
                    label={`Head-to-Head Compare (${comparedIds.length})`}
                    sx={{
                      textTransform: "none",
                      fontWeight: 650,
                      fontSize: 13.5,
                      minHeight: 44,
                      color: activeTab === "compare" ? "#9a431f" : "#70675e"
                    }}
                  />
                  <Tab
                    value="analytics"
                    icon={<AnalyticsRounded sx={{ fontSize: 18 }} />}
                    iconPosition="start"
                    label="Pipeline & Radar Analytics"
                    sx={{
                      textTransform: "none",
                      fontWeight: 650,
                      fontSize: 13.5,
                      minHeight: 44,
                      color: activeTab === "analytics" ? "#9a431f" : "#70675e"
                    }}
                  />
                </Tabs>
              </Paper>

              {/* Tab 1: Candidate Audit Ledger */}
              {activeTab === "audit" && (
                <Box
                  sx={{
                    display: "grid",
                    gridTemplateColumns: { xs: "minmax(0, 1fr)", lg: "410px minmax(0, 1fr)" },
                    gap: { xs: 2, lg: 3 },
                    alignItems: "start"
                  }}
                >
                  {/* Left Leaderboard Column */}
                  <CandidateList
                    rankings={results.rankings}
                    selectedId={selectedCandidate?.candidate_id}
                    onSelectCandidate={(id) => setSelectedId(id)}
                    comparedIds={comparedIds}
                    onToggleCompare={handleToggleCompare}
                  />

                  {/* Right Candidate Audit Inspector */}
                  <CandidateAuditView
                    candidate={selectedCandidate}
                    requirementsById={requirementsById}
                    allResults={results}
                  />
                </Box>
              )}

              {/* Tab 2: Head-to-Head Comparison */}
              {activeTab === "compare" && (
                <Suspense fallback={<ViewLoadingFallback />}>
                  <CandidateComparison
                    rankings={results.rankings}
                    comparedIds={comparedIds}
                    onRemoveCompare={handleRemoveCompare}
                    onClearCompare={handleClearCompare}
                    requirementsById={requirementsById}
                  />
                </Suspense>
              )}

              {/* Tab 3: Pipeline Visual Analytics */}
              {activeTab === "analytics" && (
                <Suspense fallback={<ViewLoadingFallback />}>
                  <PipelineAnalytics results={results} />
                </Suspense>
              )}
            </Box>
          )}
        </Container>

        {/* Explainer Architecture Modal */}
        <ArchitectureModal
          open={architectureOpen}
          onClose={() => setArchitectureOpen(false)}
        />
      </Box>
    </ThemeProvider>
  );
}

import { useState } from "react";
import {
  Paper,
  Box,
  Typography,
  Stack,
  Button,
  Tabs,
  Tab,
  TextField,
  Chip,
  Alert,
  CircularProgress,
  Divider
} from "@mui/material";
import {
  CloudUploadOutlined,
  DescriptionOutlined,
  CloseRounded,
  ArrowForwardRounded,
  ContentPasteRounded,
  UploadFileRounded,
  LibraryBooksRounded,
  AutoAwesomeRounded,
  CheckCircleRounded
} from "@mui/icons-material";
import { SAMPLE_JOB_DESCRIPTION_TEXT } from "../data/demoData";

export default function UploadStudio({
  jobFile,
  setJobFile,
  resumeFiles,
  setResumeFiles,
  loading,
  error,
  onAnalyze,
  onLoadDemo
}) {
  const [jdInputMode, setJdInputMode] = useState("file"); // "file" or "paste"
  const [jdText, setJdText] = useState("");

  const handleJobFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setJobFile([e.target.files[0]]);
    }
  };

  const handleResumeFilesChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setResumeFiles((prev) => {
        const prevNames = new Set(prev.map((f) => f.name));
        const filtered = newFiles.filter((f) => !prevNames.has(f.name));
        return [...prev, ...filtered];
      });
    }
  };

  const removeResume = (index) => {
    setResumeFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const clearAllResumes = () => {
    setResumeFiles([]);
  };

  const handleLoadSampleJd = () => {
    setJdText(SAMPLE_JOB_DESCRIPTION_TEXT);
    setJdInputMode("paste");
  };

  const handleAnalyzeClick = () => {
    let finalJobFile = jobFile[0];
    if (jdInputMode === "paste") {
      if (!jdText.trim()) return;
      finalJobFile = new File([jdText], "job_description.txt", { type: "text/plain" });
    }
    if (!finalJobFile || resumeFiles.length === 0) return;
    onAnalyze(finalJobFile, resumeFiles);
  };

  const isReady =
    (jdInputMode === "file" ? jobFile.length > 0 : jdText.trim().length > 20) &&
    resumeFiles.length > 0;

  return (
    <Paper
      elevation={0}
      sx={{
        p: { xs: 2.5, md: 3.5 },
        bgcolor: "#fffdf9",
        border: "1px solid #e5ddd1",
        borderRadius: 3,
        boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.05)"
      }}
    >
      <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", lg: "1fr 1.3fr" }, gap: 3.5 }}>
        {/* Left Column: Job Description Input */}
        <Box>
          <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center", mb: 1.5 }}>
            <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
              <Box
                sx={{
                  width: 28,
                  height: 28,
                  borderRadius: 1.5,
                  bgcolor: "#faeee7",
                  color: "#b4532a",
                  display: "grid",
                  placeItems: "center"
                }}
              >
                <DescriptionOutlined sx={{ fontSize: 17 }} />
              </Box>
              <Typography variant="subtitle1" fontWeight={750} color="#29231e">
                1. Job Description
              </Typography>
            </Stack>

            {/* Mode Switcher */}
            <Tabs
              value={jdInputMode}
              onChange={(_, val) => setJdInputMode(val)}
              sx={{
                minHeight: 28,
                "& .MuiTabs-indicator": { bgcolor: "#b4532a", height: 2 }
              }}
            >
              <Tab
                value="file"
                label="File Upload"
                icon={<UploadFileRounded sx={{ fontSize: 15 }} />}
                iconPosition="start"
                sx={{ minHeight: 28, py: 0, px: 1.2, fontSize: 12, textTransform: "none", color: "#70675e" }}
              />
              <Tab
                value="paste"
                label="Paste Text"
                icon={<ContentPasteRounded sx={{ fontSize: 15 }} />}
                iconPosition="start"
                sx={{ minHeight: 28, py: 0, px: 1.2, fontSize: 12, textTransform: "none", color: "#70675e" }}
              />
            </Tabs>
          </Stack>

          {jdInputMode === "file" ? (
            <Box>
              <Button
                component="label"
                fullWidth
                variant="outlined"
                sx={{
                  height: 155,
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                  alignItems: "center",
                  gap: 0.8,
                  borderRadius: 2.5,
                  borderStyle: "dashed",
                  borderWidth: 1.5,
                  borderColor: jobFile.length ? "#56805f" : "#cdbdad",
                  bgcolor: jobFile.length ? "#e8f0e8" : "#f8f4ee",
                  transition: "all 0.2s ease",
                  "&:hover": {
                    borderColor: "#b4532a",
                    bgcolor: "#f3eee7"
                  }
                }}
              >
                <input
                  type="file"
                  hidden
                  accept=".pdf,.docx,.txt,.xml"
                  onChange={handleJobFileChange}
                />
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: "50%",
                    bgcolor: jobFile.length ? "#d1fae5" : "#faeee7",
                    color: jobFile.length ? "#56805f" : "#b4532a",
                    display: "grid",
                    placeItems: "center"
                  }}
                >
                  {jobFile.length ? <CheckCircleRounded sx={{ fontSize: 22 }} /> : <CloudUploadOutlined sx={{ fontSize: 22 }} />}
                </Box>
                <Typography variant="body2" fontWeight={700} color="#29231e">
                  {jobFile.length ? jobFile[0].name : "Upload Job Description document"}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {jobFile.length
                    ? `${(jobFile[0].size / 1024).toFixed(1)} KB • Document loaded`
                    : "Supports PDF, DOCX, TXT or XML formats"}
                </Typography>
              </Button>

              <Box sx={{ mt: 1.2, display: "flex", justifyContent: "flex-end" }}>
                <Button
                  size="small"
                  onClick={handleLoadSampleJd}
                  startIcon={<AutoAwesomeRounded sx={{ fontSize: 14 }} />}
                  sx={{ color: "#b4532a", textTransform: "none", fontSize: 12, fontWeight: 600 }}
                >
                  Or paste sample Senior Full-Stack role
                </Button>
              </Box>
            </Box>
          ) : (
            <Box>
              <TextField
                multiline
                rows={5}
                fullWidth
                placeholder="Paste job description requirements text (e.g. MUST-HAVE SKILLS, GOOD-TO-HAVE SKILLS)..."
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                sx={{
                  "& .MuiOutlinedInput-root": {
                    bgcolor: "#f8f4ee",
                    borderRadius: 2,
                    fontSize: 13,
                    color: "#29231e",
                    "& fieldset": { borderColor: "#cdbdad" },
                    "&:hover fieldset": { borderColor: "#9b8e81" },
                    "&.Mui-focused fieldset": { borderColor: "#b4532a" }
                  }
                }}
              />
              <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center", mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {jdText.length} characters
                </Typography>
                <Button
                  size="small"
                  onClick={handleLoadSampleJd}
                  startIcon={<LibraryBooksRounded sx={{ fontSize: 14 }} />}
                  sx={{ color: "#b4532a", textTransform: "none", fontSize: 12, fontWeight: 600 }}
                >
                  Load sample JD text
                </Button>
              </Stack>
            </Box>
          )}
        </Box>

        {/* Right Column: Candidate Resumes Input */}
        <Box>
          <Stack direction="row" sx={{ justifyContent: "space-between", alignItems: "center", mb: 1.5 }}>
            <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
              <Box
                sx={{
                  width: 28,
                  height: 28,
                  borderRadius: 1.5,
                  bgcolor: "#edf0e8",
                  color: "#657153",
                  display: "grid",
                  placeItems: "center"
                }}
              >
                <CloudUploadOutlined sx={{ fontSize: 17 }} />
              </Box>
              <Typography variant="subtitle1" fontWeight={750} color="#29231e">
                2. Candidate Resumes
              </Typography>
            </Stack>

            {resumeFiles.length > 0 && (
              <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
                <Chip
                  size="small"
                  label={`${resumeFiles.length} files queued`}
                  sx={{ height: 22, fontSize: 11, fontWeight: 650, bgcolor: "#faeee7", color: "#93441f" }}
                />
                <Button
                  size="small"
                  onClick={clearAllResumes}
                  sx={{ color: "#b85145", textTransform: "none", fontSize: 11.5, fontWeight: 600 }}
                >
                  Clear All
                </Button>
              </Stack>
            )}
          </Stack>

          {/* Drag and Drop Zone */}
          <Button
            component="label"
            fullWidth
            variant="outlined"
            sx={{
              p: 2,
              minHeight: resumeFiles.length ? 75 : 120,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              gap: 0.8,
              borderRadius: 2.5,
              borderStyle: "dashed",
              borderWidth: 1.5,
              borderColor: resumeFiles.length ? "#657153" : "#cdbdad",
              bgcolor: resumeFiles.length ? "#edf0e8" : "#f8f4ee",
              transition: "all 0.2s ease",
              "&:hover": {
                borderColor: "#657153",
                bgcolor: "#f3eee7"
              }
            }}
          >
            <input
              type="file"
              hidden
              multiple
              accept=".pdf,.docx,.txt,.xml"
              onChange={handleResumeFilesChange}
            />
            <Stack direction="row" spacing={1.5} sx={{ alignItems: "center" }}>
              <CloudUploadOutlined sx={{ color: "#657153", fontSize: 22 }} />
              <Typography variant="body2" fontWeight={700} color="#29231e">
                Select or drag applicant resumes (batch upload)
              </Typography>
            </Stack>
            <Typography variant="caption" color="text.secondary">
              Automatically parses PDF (with OCR fallback), DOCX, TXT, XML into verifiable evidence spans
            </Typography>
          </Button>

          {/* Uploaded Files Chips */}
          {resumeFiles.length > 0 && (
            <Box
              sx={{
                maxHeight: 120,
                overflowY: "auto",
                mt: 1.5,
                p: 1.2,
                bgcolor: "#f8f4ee",
                borderRadius: 2,
                border: "1px solid #e5ddd1"
              }}
            >
              <Stack direction="row" gap={0.8} flexWrap="wrap">
                {resumeFiles.map((file, idx) => (
                  <Chip
                    key={`${file.name}-${idx}`}
                    size="small"
                    label={`${file.name} (${(file.size / 1024).toFixed(0)} KB)`}
                    onDelete={() => removeResume(idx)}
                    deleteIcon={<CloseRounded sx={{ fontSize: 14 }} />}
                    sx={{
                      bgcolor: "#fffdf9",
                      color: "#514941",
                      border: "1px solid #cdbdad",
                      fontSize: 11.5,
                      fontWeight: 500
                    }}
                  />
                ))}
              </Stack>
            </Box>
          )}

          {resumeFiles.length === 0 && (
            <Box sx={{ mt: 1.2, display: "flex", justifyContent: "flex-end" }}>
              <Button
                size="small"
                onClick={onLoadDemo}
                startIcon={<AutoAwesomeRounded sx={{ fontSize: 14 }} />}
                sx={{ color: "#657153", textTransform: "none", fontSize: 12, fontWeight: 600 }}
              >
                Or preview with 4 pre-ranked candidate profiles
              </Button>
            </Box>
          )}
        </Box>
      </Box>

      {/* Action Bar & Error Banner */}
      <Divider sx={{ my: 2.5, borderColor: "#e5ddd1" }} />

      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={2}
        sx={{ justifyContent: "space-between", alignItems: { sm: "center" } }}
      >
        <Typography variant="caption" color="#70675e" fontWeight={500}>
          🔒 100% on-device local execution • Zero candidate data is transmitted outside your environment
        </Typography>

        <Button
          variant="contained"
          disabled={!isReady || loading}
          onClick={handleAnalyzeClick}
          endIcon={!loading && <ArrowForwardRounded sx={{ fontSize: 18 }} />}
          sx={{
            minWidth: 220,
            py: 1.2,
            px: 3.5,
            fontSize: 13.5,
            fontWeight: 700,
            borderRadius: 2,
            bgcolor: isReady ? "#b4532a" : "#e5ddd1",
            color: isReady ? "#fffdf9" : "#9b8e81",
            "&:hover": {
              bgcolor: isReady ? "#93441f" : "#e5ddd1"
            }
          }}
        >
          {loading ? (
            <Stack direction="row" spacing={1.5} sx={{ alignItems: "center" }}>
              <CircularProgress size={16} color="inherit" />
              <span>Analyzing Resumes…</span>
            </Stack>
          ) : (
            `Analyze ${resumeFiles.length > 0 ? `${resumeFiles.length} Candidates` : "Candidates"}`
          )}
        </Button>
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mt: 2, borderRadius: 2 }}>
          {error}
        </Alert>
      )}
    </Paper>
  );
}

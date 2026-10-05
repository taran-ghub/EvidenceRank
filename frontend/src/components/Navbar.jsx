import {
  AppBar,
  Toolbar,
  Box,
  Typography,
  Button,
  Stack,
  Chip,
  Tooltip,
  Container
} from "@mui/material";
import {
  SearchRounded,
  FileDownloadRounded,
  TableChartRounded,
  HelpOutlineRounded,
  AutoAwesomeRounded,
  RefreshRounded
} from "@mui/icons-material";
import { downloadJsonReport, downloadCsvShortlist } from "../utils/exportUtils";

export default function Navbar({
  backendOnline,
  isDemoActive,
  onLoadDemo,
  onReset,
  onOpenArchitecture,
  results
}) {
  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: "rgba(255, 253, 249, 0.96)",
        borderBottom: "1px solid #e5ddd1",
        boxShadow: "0 8px 24px -24px rgba(73, 51, 35, 0.8)",
        zIndex: 1100
      }}
    >
      <Container maxWidth={false} sx={{ maxWidth: 1600, px: { xs: 2, sm: 3, md: 4 } }}>
        <Toolbar disableGutters sx={{ minHeight: 64, justifyContent: "space-between" }}>
          {/* Logo & Brand Identity */}
          <Stack direction="row" spacing={{ xs: 0.8, sm: 1.5 }} sx={{ alignItems: "center", minWidth: 0, flexShrink: 1 }}>
            <Box
              sx={{
                width: 38,
                height: 38,
                borderRadius: 2,
                background: "linear-gradient(145deg, #c76d42, #93411f)",
                display: "grid",
                placeItems: "center",
                color: "#ffffff"
              }}
            >
              <SearchRounded sx={{ fontSize: 22 }} />
            </Box>
            <Box>
              <Stack direction="row" spacing={1} sx={{ alignItems: "center" }}>
                <Typography
                  variant="h6"
                  fontWeight={800}
                  letterSpacing="-0.03em"
                  sx={{ color: "#29231e" }}
                >
                  EvidenceRank
                </Typography>
                <Chip
                  size="small"
                  label="Enterprise Local"
                  sx={{
                    display: { xs: "none", md: "inline-flex" },
                    height: 20,
                    fontSize: 10.5,
                    fontWeight: 650,
                    bgcolor: "#f3eee7",
                    color: "#70675e",
                    border: "1px solid #e5ddd1"
                  }}
                />
              </Stack>
              <Typography
                variant="caption"
                sx={{
                  color: "#70675e",
                  fontSize: 10,
                  letterSpacing: 1,
                  fontWeight: 650,
                  display: { xs: "none", sm: "block" }
                }}
              >
                AUDITABLE TALENT INTELLIGENCE
              </Typography>
            </Box>
          </Stack>

          {/* Center / Right controls */}
          <Stack direction="row" spacing={{ xs: 0.6, sm: 1 }} sx={{ alignItems: "center", flexShrink: 0 }}>
            {/* Backend status badge */}
            <Tooltip title={backendOnline ? "FastAPI local service active on port 8000" : "Running on client demo dataset"}>
              <Chip
                icon={
                  <Box
                    sx={{
                      width: 7,
                      height: 7,
                      borderRadius: "50%",
                      bgcolor: backendOnline ? "#56805f" : "#657153"
                    }}
                  />
                }
                label={backendOnline ? "Local Engine: Online" : "Mode: Benchmark Demo"}
                variant="outlined"
                size="small"
                sx={{
                  borderColor: "#e5ddd1",
                  bgcolor: "#fffdf9",
                  color: "#514941",
                  fontSize: 11.5,
                  fontWeight: 600,
                  display: { xs: "none", lg: "flex" }
                }}
              />
            </Tooltip>

            {/* Architecture Explainer */}
            <Button
              onClick={onOpenArchitecture}
              size="small"
              startIcon={<HelpOutlineRounded sx={{ fontSize: 16 }} />}
              sx={{
                display: { xs: "none", md: "inline-flex" },
                color: "#70675e",
                textTransform: "none",
                fontWeight: 600,
                fontSize: 13,
                px: 1.5,
                "&:hover": { color: "#29231e", bgcolor: "#f3eee7" }
              }}
            >
              How It Works
            </Button>

            {/* Demo Button */}
            {!isDemoActive ? (
              <Button
                onClick={onLoadDemo}
                variant="outlined"
                size="small"
                startIcon={<AutoAwesomeRounded sx={{ fontSize: 15 }} />}
                sx={{
                  borderColor: "#d2c4b6",
                  color: "#514941",
                  textTransform: "none",
                  fontWeight: 650,
                  fontSize: 12.5,
                  bgcolor: "#fffdf9",
                  "&:hover": {
                    borderColor: "#bda998",
                    bgcolor: "#f8f4ee"
                  }
                }}
              >
                Load Live Demo
              </Button>
            ) : (
              <Button
                onClick={onReset}
                variant="outlined"
                size="small"
                startIcon={<RefreshRounded sx={{ fontSize: 15 }} />}
                sx={{
                  borderColor: "#fecdd3",
                  color: "#be123c",
                  textTransform: "none",
                  fontWeight: 650,
                  fontSize: 12.5,
                  bgcolor: "#fff1f2",
                  "&:hover": {
                    borderColor: "#fda4af",
                    bgcolor: "#ffe4e6"
                  }
                }}
              >
                Reset
              </Button>
            )}

            {/* Export Actions if results present */}
            {results && (
              <Stack direction="row" spacing={1}>
                <Tooltip title="Download complete JSON audit log">
                  <Button
                    onClick={() => downloadJsonReport(results)}
                    variant="outlined"
                    size="small"
                    startIcon={<FileDownloadRounded sx={{ fontSize: 16 }} />}
                    sx={{
                      borderColor: "#e5ddd1",
                      color: "#514941",
                      bgcolor: "#fffdf9",
                      textTransform: "none",
                      fontWeight: 650,
                      fontSize: 12,
                      "&:hover": { bgcolor: "#f8f4ee", borderColor: "#cdbdad" }
                    }}
                  >
                    JSON Audit
                  </Button>
                </Tooltip>

                <Tooltip title="Export candidate shortlist to CSV">
                  <Button
                    onClick={() => downloadCsvShortlist(results)}
                    variant="contained"
                    size="small"
                    startIcon={<TableChartRounded sx={{ fontSize: 16 }} />}
                    sx={{
                      bgcolor: "#56805f",
                      color: "#ffffff",
                      textTransform: "none",
                      fontWeight: 650,
                      fontSize: 12,
                      "&:hover": { bgcolor: "#365d3e" },
                      display: { xs: "none", md: "inline-flex" }
                    }}
                  >
                    Export CSV
                  </Button>
                </Tooltip>
              </Stack>
            )}
          </Stack>
        </Toolbar>
      </Container>
    </AppBar>
  );
}

import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Stack,
  Chip,
  Paper,
  IconButton
} from "@mui/material";
import {
  CloseRounded,
  ShieldOutlined,
  CheckCircleRounded,
  CancelRounded
} from "@mui/icons-material";

export default function ArchitectureModal({ open, onClose }) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          bgcolor: "#fffdf9",
          border: "1px solid #e5ddd1",
          borderRadius: 3,
          p: 1,
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)"
        }
      }}
    >
      <DialogTitle sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", pb: 1 }}>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <Box
            sx={{
              width: 38,
              height: 38,
              borderRadius: 2,
              display: "grid",
              placeItems: "center",
              bgcolor: "#faeee7",
              color: "#b4532a"
            }}
          >
            <ShieldOutlined sx={{ fontSize: 22 }} />
          </Box>
          <Box>
            <Typography variant="h6" fontWeight={800} color="#29231e">
              The EvidenceRank Architecture
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Auditable, privacy-first talent intelligence system
            </Typography>
          </Box>
        </Stack>
        <IconButton onClick={onClose} size="small" sx={{ color: "#70675e" }}>
          <CloseRounded sx={{ fontSize: 18 }} />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers sx={{ borderColor: "#e5ddd1", py: 3 }}>
        {/* Comparison Matrix */}
        <Typography variant="caption" color="#b4532a" fontWeight={750} letterSpacing={1} display="block" mb={1.5}>
          HOW EVIDENCERANK COMPARES
        </Typography>

        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" }, gap: 2, mb: 3.5 }}>
          {/* Legacy ATS */}
          <Paper
            variant="outlined"
            sx={{
              p: 2,
              bgcolor: "#f8f4ee",
              borderColor: "#e5ddd1",
              borderRadius: 2
            }}
          >
            <Typography variant="subtitle2" fontWeight={750} color="#70675e" mb={1}>
              Legacy ATS Keyword Filters
            </Typography>
            <Stack spacing={1.2} fontSize={13}>
              <Box display="flex" gap={1}>
                <CancelRounded sx={{ fontSize: 17, color: "#b85145" }} />
                <Typography variant="caption" color="#70675e">
                  Primarily relies on literal term matching.
                </Typography>
              </Box>
              <Box display="flex" gap={1}>
                <CancelRounded sx={{ fontSize: 17, color: "#b85145" }} />
                <Typography variant="caption" color="#70675e">
                  Synonyms require explicit configuration (for example, Postgres and PostgreSQL).
                </Typography>
              </Box>
              <Box display="flex" gap={1}>
                <CancelRounded sx={{ fontSize: 17, color: "#b85145" }} />
                <Typography variant="caption" color="#70675e">
                  Often provides limited context about where a matched term appeared.
                </Typography>
              </Box>
            </Stack>
          </Paper>

          {/* Cloud Black-box LLMs */}
          <Paper
            variant="outlined"
            sx={{
              p: 2,
              bgcolor: "#f8f4ee",
              borderColor: "#e5ddd1",
              borderRadius: 2
            }}
          >
            <Typography variant="subtitle2" fontWeight={750} color="#70675e" mb={1}>
              Cloud Black-Box LLMs
            </Typography>
            <Stack spacing={1.2} fontSize={13}>
              <Box display="flex" gap={1}>
                <CancelRounded sx={{ fontSize: 17, color: "#b85145" }} />
                <Typography variant="caption" color="#70675e">
                  May send resume data to an external provider, depending on deployment.
                </Typography>
              </Box>
              <Box display="flex" gap={1}>
                <CancelRounded sx={{ fontSize: 17, color: "#b85145" }} />
                <Typography variant="caption" color="#70675e">
                  Results can vary with the selected model and generation settings.
                </Typography>
              </Box>
              <Box display="flex" gap={1}>
                <CancelRounded sx={{ fontSize: 17, color: "#b85145" }} />
                <Typography variant="caption" color="#70675e">
                  Introduces network, provider, latency, and usage-cost considerations.
                </Typography>
              </Box>
            </Stack>
          </Paper>

          {/* EvidenceRank */}
          <Paper
            variant="outlined"
            sx={{
              p: 2,
              bgcolor: "#faeee7",
              borderColor: "#dfbca8",
              borderRadius: 2,
              position: "relative"
            }}
          >
            <Chip
              size="small"
              label="Current approach"
              sx={{ position: "absolute", top: 10, right: 10, height: 20, fontSize: 10, fontWeight: 700, bgcolor: "#b4532a", color: "#fffdf9" }}
            />
            <Typography variant="subtitle2" fontWeight={750} color="#813718" mb={1}>
              EvidenceRank
            </Typography>
            <Stack spacing={1.2} fontSize={13}>
              <Box display="flex" gap={1}>
                <CheckCircleRounded sx={{ fontSize: 17, color: "#56805f" }} />
                <Typography variant="caption" color="#1e1b4b">
                  Resume analysis runs locally after the required models and dependencies are installed.
                </Typography>
              </Box>
              <Box display="flex" gap={1}>
                <CheckCircleRounded sx={{ fontSize: 17, color: "#56805f" }} />
                <Typography variant="caption" color="#1e1b4b">
                  Hybrid BM25 + SBERT Semantic vectors with exact alias resolution.
                </Typography>
              </Box>
              <Box display="flex" gap={1}>
                <CheckCircleRounded sx={{ fontSize: 17, color: "#56805f" }} />
                <Typography variant="caption" color="#1e1b4b">
                  Evidence-aware: weights projects, experience, action verbs, and metrics.
                </Typography>
              </Box>
            </Stack>
          </Paper>
        </Box>

        {/* Scoring Pipeline Explanation */}
        <Typography variant="caption" color="#b4532a" fontWeight={750} letterSpacing={1} display="block" mb={1.5}>
          4-PILLAR DETERMINISTIC SCORING FORMULA
        </Typography>

        <Paper
          variant="outlined"
          sx={{
            p: 2.2,
            bgcolor: "#f8f4ee",
            borderColor: "#e5ddd1",
            borderRadius: 2
          }}
        >
          <Box
            sx={{
              p: 1.5,
              mb: 2,
              bgcolor: "#fffdf9",
              border: "1px solid #cdbdad",
              borderRadius: 1.5,
              fontFamily: "JetBrains Mono, monospace",
              fontSize: 12.5,
              color: "#93441f",
              fontWeight: 600
            }}
          >
            Requirement Score = Evidence Quality × [ 0.45(Semantic) + 0.35(BM25 Keyword) + 0.20(Related Terms) ]
          </Box>

          <Stack spacing={1.5}>
            <Box display="flex" alignItems="flex-start" gap={1.5}>
              <Chip label="1" size="small" sx={{ bgcolor: "#faeee7", color: "#93441f", fontWeight: 700, height: 22 }} />
              <Box>
                <Typography variant="body2" fontWeight={700} color="#29231e">
                  Semantic Similarity (45%)
                </Typography>
                <Typography variant="caption" color="#70675e">
                  Sentence-transformers (all-MiniLM-L6-v2) computes vector embeddings locally to match conceptual experience across different phrasing.
                </Typography>
              </Box>
            </Box>

            <Box display="flex" alignItems="flex-start" gap={1.5}>
              <Chip label="2" size="small" sx={{ bgcolor: "#edf0e8", color: "#4f5b40", fontWeight: 700, height: 22 }} />
              <Box>
                <Typography variant="body2" fontWeight={700} color="#29231e">
                  BM25 Lexical Matching (35%)
                </Typography>
                <Typography variant="caption" color="#70675e">
                  Checks whether requested technologies, libraries, and frameworks appear in candidate documents.
                </Typography>
              </Box>
            </Box>

            <Box display="flex" alignItems="flex-start" gap={1.5}>
              <Chip label="3" size="small" sx={{ bgcolor: "#e8f0e8", color: "#365d3e", fontWeight: 700, height: 22 }} />
              <Box>
                <Typography variant="body2" fontWeight={700} color="#29231e">
                  Curated Alias Graph (20%)
                </Typography>
                <Typography variant="caption" color="#70675e">
                  Resolves domain synonyms and alternatives (e.g. Postgres ↔ PostgreSQL, K8s ↔ Kubernetes, React.js ↔ React).
                </Typography>
              </Box>
            </Box>

            <Box display="flex" alignItems="flex-start" gap={1.5}>
              <Chip label="4" size="small" sx={{ bgcolor: "#fbf0dc", color: "#8c5c20", fontWeight: 700, height: 22 }} />
              <Box>
                <Typography variant="body2" fontWeight={700} color="#29231e">
                  Evidence Quality Multiplier
                </Typography>
                <Typography variant="caption" color="#70675e">
                  Weights evidence using its resume section, action verbs, and quantifiable metrics.
                </Typography>
              </Box>
            </Box>
          </Stack>
        </Paper>
      </DialogContent>

      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} variant="contained" sx={{ px: 3, bgcolor: "#b4532a", color: "#fffdf9" }}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
}

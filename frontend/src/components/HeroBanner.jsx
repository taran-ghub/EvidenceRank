import { Box, Typography, Paper, Chip } from "@mui/material";
import {
  ShieldOutlined,
  VerifiedUserOutlined,
  FactCheckOutlined,
  LockOutlined
} from "@mui/icons-material";

export default function HeroBanner() {
  return (
    <Box sx={{ pt: { xs: 3.5, md: 5 }, pb: 2, textAlign: "center" }}>
      {/* Pill Badge */}
      <Box sx={{ display: "inline-flex", alignItems: "center", gap: 1, mb: 2 }}>
        <Chip
          icon={<LockOutlined sx={{ fontSize: 13, color: "#b4532a !important" }} />}
          label="Local analysis • Reproducible scoring • Source audit"
          size="small"
          sx={{
            px: 1,
            py: 0.4,
            fontSize: 12,
            fontWeight: 700,
            bgcolor: "#faeee7",
            color: "#93441f",
            border: "1px solid #dfbca8",
            boxShadow: "0 1px 2px rgba(126, 57, 28, 0.08)"
          }}
        />
      </Box>

      {/* Main Punchy Headline */}
      <Typography
        variant="h3"
        fontWeight={850}
        letterSpacing="-0.035em"
        sx={{
          fontSize: { xs: "2.1rem", sm: "2.8rem", md: "3.4rem" },
          lineHeight: 1.15,
          color: "#29231e",
          maxWidth: 820,
          mx: "auto"
        }}
      >
        Rank with traceable evidence.{" "}
        <Box
          component="span"
          sx={{
            background: "linear-gradient(120deg, #b4532a 0%, #c18436 52%, #657153 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent"
          }}
        >
          Not keyword tricks.
        </Box>
      </Typography>

      {/* Concise Subtitle (1 line, no wall of text) */}
      <Typography
        variant="body1"
        sx={{
          color: "#70675e",
          maxWidth: 620,
          mx: "auto",
          mt: 1.5,
          fontSize: { xs: 15, sm: 16.5 },
          lineHeight: 1.5,
          fontWeight: 500
        }}
      >
        Inspect the exact sentence, page, and hybrid score components behind every candidate ranking.
      </Typography>

      {/* 3 Clean Bento Metric Pills (Concise, high-impact) */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "1fr", sm: "repeat(3, 1fr)" },
          gap: 2,
          maxWidth: 880,
          mx: "auto",
          mt: 3.5
        }}
      >
        <Paper
          elevation={0}
          sx={{
            p: 2,
            textAlign: "left",
            bgcolor: "#fffdf9",
            border: "1px solid #e5ddd1",
            borderRadius: 2.5,
            boxShadow: "0 2px 8px -2px rgba(15, 23, 42, 0.05)",
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            transition: "all 0.15s ease",
            "&:hover": { borderColor: "#cdbdad", transform: "translateY(-1px)" }
          }}
        >
          <Box
            sx={{
              width: 38,
              height: 38,
              borderRadius: 2,
              bgcolor: "#faeee7",
              color: "#b4532a",
              display: "grid",
              placeItems: "center",
              flexShrink: 0
            }}
          >
            <ShieldOutlined sx={{ fontSize: 20 }} />
          </Box>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="subtitle2" fontWeight={750} color="#29231e" sx={{ lineHeight: 1.2 }}>
              Local Processing
            </Typography>
            <Typography variant="caption" color="#70675e" display="block" mt={0.3}>
              Files are analyzed by your configured local API.
            </Typography>
          </Box>
        </Paper>

        <Paper
          elevation={0}
          sx={{
            p: 2,
            textAlign: "left",
            bgcolor: "#fffdf9",
            border: "1px solid #e5ddd1",
            borderRadius: 2.5,
            boxShadow: "0 2px 8px -2px rgba(15, 23, 42, 0.05)",
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            transition: "all 0.15s ease",
            "&:hover": { borderColor: "#cdbdad", transform: "translateY(-1px)" }
          }}
        >
          <Box
            sx={{
              width: 38,
              height: 38,
              borderRadius: 2,
              bgcolor: "#e8f0e8",
              color: "#56805f",
              display: "grid",
              placeItems: "center",
              flexShrink: 0
            }}
          >
            <FactCheckOutlined sx={{ fontSize: 20 }} />
          </Box>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="subtitle2" fontWeight={750} color="#29231e" sx={{ lineHeight: 1.2 }}>
              Evidence Depth
            </Typography>
            <Typography variant="caption" color="#70675e" display="block" mt={0.3}>
              Rewards project and work context.
            </Typography>
          </Box>
        </Paper>

        <Paper
          elevation={0}
          sx={{
            p: 2,
            textAlign: "left",
            bgcolor: "#fffdf9",
            border: "1px solid #e5ddd1",
            borderRadius: 2.5,
            boxShadow: "0 2px 8px -2px rgba(15, 23, 42, 0.05)",
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            transition: "all 0.15s ease",
            "&:hover": { borderColor: "#cdbdad", transform: "translateY(-1px)" }
          }}
        >
          <Box
            sx={{
              width: 38,
              height: 38,
              borderRadius: 2,
              bgcolor: "#edf0e8",
              color: "#657153",
              display: "grid",
              placeItems: "center",
              flexShrink: 0
            }}
          >
            <VerifiedUserOutlined sx={{ fontSize: 20 }} />
          </Box>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="subtitle2" fontWeight={750} color="#29231e" sx={{ lineHeight: 1.2 }}>
              Sentence-Level Evidence
            </Typography>
            <Typography variant="caption" color="#70675e" display="block" mt={0.3}>
              Page & section citations.
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Box>
  );
}

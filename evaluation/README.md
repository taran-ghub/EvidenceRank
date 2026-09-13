# EvidenceRank evaluation

This package measures whether EvidenceRank's ordering agrees with independent
human judgments. It is separate from the normal product test suite: regression
tests ask whether code behaves consistently, while evaluation asks whether the
ranking is useful.

## Current pilot

The first pilot uses 30 real mixed-format resumes for a junior full-stack role.
The sample contains 10 resumes from each of three broad keyword-coverage groups
so that it includes likely matches, borderline candidates, and clear negatives.
The final EvidenceRank score is not used to select the sample.

One reviewer labels each resume before model ranking:

- `3`: strong fit with clear project or work evidence
- `2`: reasonable fit with meaningful gaps
- `1`: weak fit with limited relevant evidence
- `0`: little or no support for the role

Confidence is recorded separately as `high`, `medium`, or `low`.

## Workflow

Run all commands from the repository root:

```bash
python -m evaluation.profile_dataset
python -m evaluation.create_pilot
python -m evaluation.blind_pilot
python -m evaluation.validate_labels
python -m evaluation.run_pilot
```

The scripts create private working files under:

```text
data/cache/evaluation/full_stack_pilot/
```

That directory is excluded from Git. Do not commit resumes, candidate mappings,
human labels, detailed ranking results, or extracted resume contents.

## Metrics

- **NDCG@K** rewards placing the most relevant candidates nearer the top.
- **Precision@K** measures how many candidates in the top K have labels 2 or 3.
- **Recall@K** measures how many of all candidates labelled 2 or 3 appear in the
  top K.
- **Pairwise accuracy** measures how often two candidates with different human
  labels are ordered in the same direction by EvidenceRank.

## First local baseline

The private 30-resume pilot produced:

| Metric | Result |
|---|---:|
| NDCG@5 | 1.0000 |
| NDCG@10 | 0.9579 |
| Precision@5 | 1.0000 |
| Precision@10 | 0.6000 |
| Recall@5 | 0.7143 |
| Recall@10 | 0.8571 |
| Pairwise accuracy | 0.9024 |

These results are encouraging but are not a general accuracy claim. They come
from one role, one reviewer, 30 sampled resumes, and only seven candidates
labelled relevant. The sampling method also uses the same curated skill catalog
that contributes to EvidenceRank matching.

## Privacy and evaluation limits

The blinded folder replaces filenames with evaluation IDs, but resume contents
are not redacted. Reviewers must ignore names, photos, colleges, gender, and
other protected or personal characteristics and judge only job-relevant written
evidence.

Before treating the metrics as product evidence, expand to multiple job types,
use a locked holdout set, collect a second independent review for a subset, and
report label agreement as well as ranking quality.

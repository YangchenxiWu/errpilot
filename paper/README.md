# ErrPilot ASE Tools and Datasets Paper

This directory contains the ACM `acmart` paper source for the ErrPilot ASE 2026
Tools and Datasets demonstration submission.

## Files

- `main.tex`: ACM `acmart` SIGCONF review-style paper skeleton.
- `references.bib`: currently unused placeholder for later bibliography work.
- `figures/`: placeholder directory for paper figures.

## Build

Install a LaTeX distribution with the ACM `acmart` class, then run:

```bash
cd paper
latexmk -pdf main.tex
```

If `latexmk` is unavailable:

```bash
cd paper
pdflatex main.tex
pdflatex main.tex
```

The draft uses `\documentclass[sigconf,review]{acmart}`, which intentionally
shows review line numbers. For a final camera-ready or clean visual inspection
PDF, remove the `review` option from the document class.

## Paper Constraints

- Target venue: ASE 2026 Tools and Datasets.
- Format: `\documentclass[sigconf,review]{acmart}`.
- Demonstration submission target: 4 pages including text, figures, and
  references.
- Screencast target: up to 5 minutes. Current video:
  `https://youtu.be/-cGRD9A6AXo`.
- Data Availability Statement appears immediately before References.

## Submission Metadata

- Zenodo DOI: `https://doi.org/10.5281/zenodo.20053341`.
- YouTube demonstration video URL: `https://youtu.be/-cGRD9A6AXo`.
- Final ACM DOI and ISBN are not available during submission drafting; do not
  invent them.

## Claim Discipline

Keep the paper aligned with the repository evidence:

- ErrPilot is a failure intake and handoff tool, not a repair agent.
- ErrPilot does not execute downstream repair tools.
- ErrPilot does not silently monitor terminal activity.
- ErrPilot executes commands explicitly passed to `errpilot run --`; it does not
  sandbox those commands.
- The default evaluation should be described as 7 executable open-source,
  repository-local failure cases and 5 documented-only external design probes,
  or as 12 default case entries with that split stated immediately.
- The SkiLoadLab missing-input run may be described only as an optional
  cross-project vignette, not as a benchmark or general field study.
- Other external SkiLoadLab and slsa-verifier cases are context only and should
  not be described as reproduced real-world executions.

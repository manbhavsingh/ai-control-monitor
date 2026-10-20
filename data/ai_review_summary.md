# AI review notes

I completed a policy-consistency pass over the 128 synthetic cases. The AI-assigned binary labels matched the existing labels for all 128 cases (64 violations and 64 safe cases). This is a consistency check, not independent validation: I previously helped create the cases and labels in this conversation. A separate reviewer is still needed before calling the dataset independently validated.

A data-quality issue was identified: severity had been assigned by row index, not by an impact rubric. The severity values have now been revised and each case includes a severity rationale. Severity remains a subjective heuristic; the rubric is in `data/HELDOUT_REVIEW_GUIDE.md`.

The detailed per-case AI annotations are in `data/ai_reviewer_pass_v1.csv`. Reviewer B and adjudication fields should remain blank until a genuinely separate reviewer completes the worksheet.

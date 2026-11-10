# Tether — N1 Decisions Record

The defaults and policy choices submitted by the engineering agent for Sanit Salve (N1)'s sign-off:

### 1. Confidence Ceilings Approval
- [x] **Approved**: Cap for Git commits and repository files: `0.95`.
- [x] **Approved**: Cap for merged pull requests: `0.95`.
- [x] **Approved**: Cap for issue and PR comments: `0.85`.
- [x] **Approved**: Cap for unmerged PR drafts: `0.70`.
- [x] **Approved**: Cap for single chat messages: `0.60`.

### 2. Role Permissions Matrix Approval
- [x] **Approved**: Reviewer has access to all labels, queue triage, Gate 1 clearance, conflict decision, and version signing.
- [x] **Approved**: Successor has access to latest signed version only; labels `open` and `internal` only.
- [x] **Approved**: Leaver has access to claims about their own work; cannot approve or publish.
- [x] **Approved**: Admin has retention control (30-day default), project deletion, and audit log exports; cannot alter claims.

### 3. Repository Licence Approval
- [x] **Approved**: MIT Licence chosen for public code release.

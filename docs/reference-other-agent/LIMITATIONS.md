# Tether — Product Limitations

An honest account of boundaries, approximations, and deliberate exclusions in the Round 2 prototype.

## What Does Not Work
- **Automatic Audio/Video Meeting Transcription**: Audio recordings of meetings must be transcribed to text or Markdown notes before ingestion.
- **Bi-directional Live Git Push**: Tether is strictly read-only with respect to source repositories; it never modifies commit trees or opens PRs automatically.
- **Dynamic Multi-Organization SSO**: In this prototype, role switching is simulated locally via the role selector and JWT headers rather than enterprise Okta/SAML providers.

## What Is Approximated
- **Risk Score**: The successor priority score is an explicit formula estimate (`calculateRiskEstimate`), combining claim type weights, author commit concentration, open issue links, and nearby conflicts/gaps. It is explicitly labeled *"estimate"* in the UI and documentation.
- **Truck Factor Concentration**: Evaluated based on author commit percentage threshold (>= 80% of module commits) rather than iterative degree-centrality graph decomposition.

## What Was Not Tested
- **Repositories exceeding 100,000 commits**: The synthetic demo project contains ~60 commits. Repositories with multi-gigabyte commit trees have not been benchmarked for memory footprint.
- **Multi-language Chat Exports**: Tokenization and quote matching are currently optimized for UTF-8 English text sources.

## What the Product Refuses to Claim
- **No Knowledge Loss Rate**: Tether never claims to calculate a "percentage of knowledge captured" or "loss rate". As Galan (2023) established, loss is well described but cannot be reliably counted as a universal ratio.
- **No People Scoring**: We evaluate work items, tasks, and system components, never individual developer competence, mood, or likelihood to quit (House Rule HR-5).
- **No Machine Conflict Resolution**: When two team records contradict each other, Tether surfaces both sides and refuses to pick a winner without human intervention (House Rule HR-3).

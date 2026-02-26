# Requirements Register: Project 1

This folder contains the stakeholder requirements for **Project 1: No-code finance strategy builder**, extracted and formalised from client interviews and notes.

Phase 1 (Stakeholder Requirements Definition) was conducted prior to and independently of the timed evaluation. It is excluded from the 24-hour worktime measurement (3 standard work days of 8 hours each) applied to Phases 2–8.

Each requirement is documented in its own file following the Volere-inspired template defined in [`protocol/requirements.md`](../../protocol/requirements.md). This README serves as the central register and entry point for all requirements in this project.

<!-- metrics:start -->

## Metrics

### Priority

| Priority | Count |
| -------- | ----: |
| Must | 22 |
| Should | 11 |
| Could | 21 |
| Won't | 7 |
| **Total** | **61** |

### Type

| Type | Count |
| ---- | ----: |
| Functional | 58 |
| Non-functional | 3 |
| Constraint | 0 |
| Interface | 0 |
| Environmental | 0 |
| **Total** | **61** |

### Status

| Status | Count |
| ------ | ----: |
| Draft | 0 |
| Reviewed | 0 |
| Approved | 61 |
| Deprecated | 0 |
| **Total** | **61** |

<!-- metrics:end -->

## Requirements

| ID | Title | Type | CS | CD | Status | Priority | File |
| -- | ----- | ---- | -- | -- | ------ | -------- | ---- |
| REQ-01 | Parallel strategy creation | Functional | 3 | 1 | Approved | Could | [REQ-01.md](REQ-01.md) |
| REQ-02 | Strategy pipeline structure | Functional | 5 | 5 | Approved | Must | [REQ-02.md](REQ-02.md) |
| REQ-03 | Cross-asset comparison in rules | Functional | 3 | 2 | Approved | Could | [REQ-03.md](REQ-03.md) |
| REQ-04 | Strategy scope (one asset, one venue) | Functional | 4 | 4 | Approved | Must | [REQ-04.md](REQ-04.md) |
| REQ-05 | Create strategy from scratch | Functional | 5 | 5 | Approved | Must | [REQ-05.md](REQ-05.md) |
| REQ-06 | Select strategy from presets | Functional | 4 | 2 | Approved | Should | [REQ-06.md](REQ-06.md) |
| REQ-07 | Clone existing strategy | Functional | 4 | 3 | Approved | Should | [REQ-07.md](REQ-07.md) |
| REQ-08 | Modify strategy/indicator parameters | Functional | 5 | 5 | Approved | Must | [REQ-08.md](REQ-08.md) |
| REQ-09 | Save and reload named presets | Functional | 5 | 5 | Approved | Must | [REQ-09.md](REQ-09.md) |
| REQ-10 | Compare strategies side by side | Functional | 2 | 2 | Approved | Could | [REQ-10.md](REQ-10.md) |
| REQ-11 | Strategy execution isolation | Functional | 5 | 5 | Approved | Must | [REQ-11.md](REQ-11.md) |
| REQ-12 | Stop-loss / take-profit simulation | Functional | 5 | 4 | Approved | Must | [REQ-12.md](REQ-12.md) |
| REQ-13 | Maximum drawdown limit enforcement | Functional | 0 | 0 | Approved | Won't | [REQ-13.md](REQ-13.md) |
| REQ-14 | Advanced position sizing: Kelly criterion variants | Functional | 4 | 3 | Approved | Should | [REQ-14.md](REQ-14.md) |
| REQ-15 | Human-readable strategy explanations | Functional | 4 | 1 | Approved | Could | [REQ-15.md](REQ-15.md) |
| REQ-16 | No-code drag-and-drop builder | Functional | 5 | 5 | Approved | Must | [REQ-16.md](REQ-16.md) |
| REQ-17 | Visual pipeline graph | Functional | 5 | 5 | Approved | Must | [REQ-17.md](REQ-17.md) |
| REQ-18 | Block compatibility validation | Functional | 0 | 5 | Approved | Must | [REQ-18.md](REQ-18.md) |
| REQ-19 | Multi-select pipeline elements | Functional | 3 | 2 | Approved | Could | [REQ-19.md](REQ-19.md) |
| REQ-20 | Copy, cut, and paste elements | Functional | 3 | 2 | Approved | Could | [REQ-20.md](REQ-20.md) |
| REQ-21 | Delete multiple elements | Functional | 3 | 2 | Approved | Could | [REQ-21.md](REQ-21.md) |
| REQ-22 | Undo / redo (≥ 20 steps) | Functional | 4 | 4 | Approved | Must | [REQ-22.md](REQ-22.md) |
| REQ-23 | Alignment grid with snap-to-grid | Functional | 2 | 1 | Approved | Won't | [REQ-23.md](REQ-23.md) |
| REQ-24 | Decision tree / state machine inspection | Functional | 3 | 2 | Approved | Could | [REQ-24.md](REQ-24.md) |
| REQ-25 | Double-click to open block config | Functional | 3 | 3 | Approved | Should | [REQ-25.md](REQ-25.md) |
| REQ-26 | Ghost blocks with typed suggestions | Functional | 3 | 2 | Approved | Could | [REQ-26.md](REQ-26.md) |
| REQ-27 | Configurable keyboard shortcuts | Functional | 3 | 1 | Approved | Could | [REQ-27.md](REQ-27.md) |
| REQ-28 | Optimisation comparison window | Functional | 3 | 2 | Approved | Could | [REQ-28.md](REQ-28.md) |
| REQ-29 | Multiple backtest methods (3) | Functional | 5 | 4 | Approved | Must | [REQ-29.md](REQ-29.md) |
| REQ-30 | Backtest time estimation | Functional | 3 | 2 | Approved | Could | [REQ-30.md](REQ-30.md) |
| REQ-31 | Backtest metrics report (9 metrics) | Functional | 5 | 5 | Approved | Must | [REQ-31.md](REQ-31.md) |
| REQ-32 | Grid search optimisation with CV | Functional | 4 | 3 | Approved | Should | [REQ-32.md](REQ-32.md) |
| REQ-33 | Statistical significance testing | Functional | 4 | 4 | Approved | Must | [REQ-33.md](REQ-33.md) |
| REQ-34 | Out-of-sample validation | Functional | 5 | 5 | Approved | Must | [REQ-34.md](REQ-34.md) |
| REQ-35 | Capital per trade configuration | Functional | 5 | 5 | Approved | Must | [REQ-35.md](REQ-35.md) |
| REQ-36 | Monte Carlo stress testing and EV visualisation | Functional | 5 | 2 | Approved | Should | [REQ-36.md](REQ-36.md) |
| REQ-37 | Live trading API connection with confirmation | Functional | 3 | 1 | Approved | Could | [REQ-37.md](REQ-37.md) |
| REQ-38 | Custom exchange API (Advanced mode) | Functional | 2 | 1 | Approved | Won't | [REQ-38.md](REQ-38.md) |
| REQ-39 | Custom asset selection (Advanced mode) | Functional | 3 | 2 | Approved | Could | [REQ-39.md](REQ-39.md) |
| REQ-40 | Import custom components (Advanced mode) | Functional | 3 | 1 | Approved | Could | [REQ-40.md](REQ-40.md) |
| REQ-41 | Export results (CSV, PDF) | Functional | 3 | 5 | Approved | Must | [REQ-41.md](REQ-41.md) |
| REQ-42 | Strategy leaderboard | Functional | 2 | 1 | Approved | Won't | [REQ-42.md](REQ-42.md) |
| REQ-43 | Mode selection on startup (persisted) | Functional | 3 | 2 | Approved | Could | [REQ-43.md](REQ-43.md) |
| REQ-44 | Basic mode with guided workflow | Functional | 3 | 3 | Approved | Should | [REQ-44.md](REQ-44.md) |
| REQ-45 | Advanced mode sandbox | Functional | 4 | 4 | Approved | Must | [REQ-45.md](REQ-45.md) |
| REQ-46 | In-app onboarding tutorials | Functional | 3 | 1 | Approved | Could | [REQ-46.md](REQ-46.md) |
| REQ-47 | Contextual hover tooltips | Functional | 3 | 2 | Approved | Could | [REQ-47.md](REQ-47.md) |
| REQ-48 | Built-in component descriptions | Functional | 4 | 1 | Approved | Could | [REQ-48.md](REQ-48.md) |
| REQ-49 | Searchable indicator glossary | Functional | 3 | 2 | Approved | Could | [REQ-49.md](REQ-49.md) |
| REQ-50 | Local desktop deployment | Non-functional | 3 | 3 | Approved | Should | [REQ-50.md](REQ-50.md) |
| REQ-51 | Import strategy from file | Functional | 3 | 2 | Approved | Could | [REQ-51.md](REQ-51.md) |
| REQ-52 | Demo / sample strategy | Functional | 4 | 2 | Approved | Should | [REQ-52.md](REQ-52.md) |
| REQ-53 | Input configuration panel | Functional | 5 | 5 | Approved | Must | [REQ-53.md](REQ-53.md) |
| REQ-54 | Risk:Reward ratio definition | Functional | 4 | 3 | Approved | Should | [REQ-54.md](REQ-54.md) |
| REQ-55 | Block selection panel (+ button / node propositions) | Functional | 5 | 4 | Approved | Must | [REQ-55.md](REQ-55.md) |
| REQ-56 | Backtest time span selection | Functional | 4 | 4 | Approved | Must | [REQ-56.md](REQ-56.md) |
| REQ-57 | Visual aids in documentation | Functional | 3 | 0 | Approved | Won't | [REQ-57.md](REQ-57.md) |
| REQ-58 | Cloud / remote execution | Non-functional | 2 | 1 | Approved | Won't | [REQ-58.md](REQ-58.md) |
| REQ-59 | Web interface | Non-functional | 2 | 1 | Approved | Won't | [REQ-59.md](REQ-59.md) |
| REQ-60 | Pause and background execution for long-running computations | Functional | 4 | 3 | Approved | Should | [REQ-60.md](REQ-60.md) |
| REQ-61 | Run result history per session and preset | Functional | 4 | 4 | Approved | Must | [REQ-61.md](REQ-61.md) |

---

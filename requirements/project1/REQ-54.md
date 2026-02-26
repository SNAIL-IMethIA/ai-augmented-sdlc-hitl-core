# Risk:Reward ratio definition

**ID:** REQ-54

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow the user to define a target Risk:Reward ratio per strategy, and shall use that ratio together with the stop-loss position to automatically compute the corresponding take-profit level.

**Rationale:**
Explicitly defining R:R ratio separates risk configuration from target setting, making the trade setup self-consistent and preventing arbitrary or contradictory stop-loss / take-profit combinations.

**Fit Criterion:**

- The user can input a numeric Risk:Reward ratio (e.g. 1:2) per strategy.
- Given a stop-loss distance and the defined R:R ratio, the system computes and displays the take-profit level automatically.
- Changing the R:R ratio or the stop-loss position updates the take-profit computation in real time.

**Customer Satisfaction (0–5):**

- 4: Risk:Reward is a standard and expected concept in any trading tool.

**Customer Dissatisfaction (0–5):**

- 3: Users can compute take-profit manually, but the absence of automation is a significant usability regression.

**Dependencies / Conflicts:**
REQ-12, REQ-35

**Status:**
Approved

**Priority:**
Should

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call

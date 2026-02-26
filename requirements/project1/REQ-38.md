# Custom exchange API (Advanced mode)

**ID:** REQ-38

**Type:** Functional

**Originator:** Stakeholder / Client Interview

**Description:**
The system shall allow users in Advanced mode to add and configure custom exchange API integrations by supplying API credentials and endpoint details.

**Rationale:**
Supporting custom exchange integrations allows advanced users to connect to any compatible exchange beyond the default list, maximising the addressable market of tradable assets.

**Fit Criterion:**

- A custom exchange API can be added by entering credentials (API key, secret) and endpoint URL via the settings interface.
- After configuration, the system successfully connects to the exchange and retrieves live market data within 10 seconds.
- The custom exchange is available for selection in the strategy input settings.

**Customer Satisfaction (0–5):**

- 2: Value for users trading on non-standard exchanges.

**Customer Dissatisfaction (0–5):**

- 1: Users limited to default exchanges cannot access preferred trading venues.

**Dependencies / Conflicts:**
REQ-45, REQ-37

**Status:**
Approved

**Priority:**
Won't

**History:**

- 2026-02-16 | Kevin Schweitzer | Created | Formalised from client interviews and notes
- 2026-02-25 | Client / Stakeholder | Approved | Validated during client call

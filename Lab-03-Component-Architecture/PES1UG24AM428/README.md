# Lab 3: Component Modelling & Architecture — Dharshini V (PES1UG24AM428)

**System:** Digital Campus Library Reservation Gateway (Problem Statement #08)  
**Assigned Use Case:** `UC-04: Pay Overdue Fine` (and FR-003: Overdue Fine Calculation & Settlement)  
**Selected Architectural Style:** **Layered Architecture**

---

## Architecture Summary
- **Presentation Layer:** Student Member UI Component
- **Business Layer:**
  - Authentication & Session Component
  - Fine Management Component (UC-04)
  - Notification Service Component
- **Data & External Services Layer:**
  - Payment Gateway Adapter (External Gateway integration)
  - Library Database Component
  - External Campus SMTP Server
- **Connectors (Ball-and-Socket notation):** `IAuthentication`, `IFineService`, `IPaymentGateway`, `IFineData / SQL`, `INotification`, `ISMTPRelay`.

---

## Deliverables in this Directory
- `Lab3_FINAL_Submission_Dharshini_V_PES1UG24AM428.pdf`: Complete compiled submission report with architectural justifications and component diagram.
- `Lab3_FINAL_UC04_Dharshini_V_PES1UG24AM428.pdf`: Detailed 2-page UC-04 specific architectural evaluation.
- `Lab3_Architecture_Justification_Dharshini_V_PES1UG24AM428.docx`: Editable Word source report.
- `Digital_Campus_Library_Component_Diagram.png`: High-resolution component diagram export.
- `Digital_Campus_Library_Component_Diagram.svg`: Scalable vector graphics export.
- `Digital_Campus_Library_Component_Diagram.drawio`: Editable Draw.io source diagram.

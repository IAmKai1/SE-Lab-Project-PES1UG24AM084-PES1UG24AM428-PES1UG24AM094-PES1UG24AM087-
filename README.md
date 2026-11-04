# Software Engineering Lab — Team Collaboration Project

Collaborative repository for Software Engineering Lab (SE Lab) group deliverables.

## 👥 Team Members

| Student Name | SRN | Assigned Use Case / Role |
| :--- | :--- | :--- |
| **Dharshini V** | **PES1UG24AM428** | UC-04: Pay Overdue Fine & Fine Management |
| Dhareen G | **PES1UG24AM084** | Group Partner | 
| Divyansh Badaya | **PES1UG24AM094** | Group Partner | 
| Dhruv Talavat | **PES1UG24AM087** | Group Partner | 

---

## 📁 Repository Structure & Organization

This repository is organized by lab unit, with dedicated subdirectories for each teammate's individual contributions to ensure zero git merge conflicts during collaboration:

```text
SE-Lab-Project/
├── .gitignore
├── README.md
│
├── Lab-01-Requirements-and-UML/
│   ├── README.md
│   ├── PES1UG24AM428/                  <-- Dharshini V's deliverables
│   ├── PES1UG24AM084/                  <-- Dhareen G's deliverables
│   ├── PES1UG24AM094/                  <-- Divyansh's deliverables
│   └── PES1UG24AM087/                  <-- Dhruv's deliverables
│
├── Lab-02-Jira-Agile/
│   ├── README.md
│   ├── PES1UG24AM428/                  <-- Dharshini V's deliverables
│   ├── PES1UG24AM084/                  <-- Dhareen G's deliverables
│   ├── PES1UG24AM094/                  <-- Divyansh's deliverables
│   └── PES1UG24AM087/                  <-- Dhruv's deliverables
│
├── Lab-03-Component-Architecture/
│   ├── README.md
│   ├── PES1UG24AM428/                  <-- Dharshini V's deliverables (Updated to Library Architecture)
│   ├── PES1UG24AM084/                  <-- Dhareen G's deliverables
│   ├── PES1UG24AM094/                  <-- Divyansh's deliverables
│   └── PES1UG24AM087/                  <-- Dhruv's deliverables
│
├── Lab-04-SRS-SAD-STP/                 <-- Group Specifications & Testing
│   ├── README.md
│   ├── SRS_Library_Reservation_Gateway (1).pdf
│   ├── SAD_Library_Reservation_Gateway (1).pdf
│   └── Test_Plan_Library_Reservation_Gateway.docx
│
├── Lab-04-VibeCoding/                  <-- Individual VibeCoding Game
│   └── PES1UG24AM428/
│       ├── README.md
│       ├── source_code/
│       ├── videos/
│       └── documentation/
│
└── src/                                <-- Digital Campus Library Reservation Gateway Source Implementation
    ├── audit.py
    ├── auth.py
    ├── catalog_search.py
    ├── database.py
    ├── fine_manager.py                 <-- Dharshini V (UC-04)
    ├── notification.py
    └── security.py
```

---

## 📋 Deliverables Summary (PES1UG24AM428 — Dharshini V)

### Lab 1: Requirements Engineering & UML Use-Case Modelling
- **Problem Statement**: #08 — Digital Campus Library Reservation Gateway
- **Assigned Use Case**: `UC-04: Pay Overdue Fine`
- **Key Files**:
  - Full Report PDF: `UC04_Pay_Overdue_Fine_Submission_Dharshini_V_PES1UG24AM428.pdf`
  - Requirements Table: `Requirements_Table.docx` (FR-001 to FR-005, NFR-001, NFR-002)
  - Flow Specification: `Use_Case_Flow_Specification.docx`
  - Diagram: `UML_Use_Case_Diagram.png` & `.svg`

### Lab 2: Jira Agile — Backlog Creation, Story Point Estimation & Sprint Execution
- **Epic**: `EPIC-01: Overdue Fine Payment & Settlement`
- **Total Backlog**: 6 user stories (`DCLRG-2` to `DCLRG-7`), 21 story points
- **Sprint 1**: 4 stories (`DCLRG-2`, `DCLRG-3`, `DCLRG-4`, `DCLRG-5`), 13 story points (100% burndown)
- **Key Files**:
  - Full Final Report PDF: `Jira_Lab2_Final_Submission_Dharshini_V_PES1UG24AM428.pdf`
  - Editable Report Document: `Jira_Lab2_UC04_Individual_Report_Dharshini_V.docx`

### Lab 3: Component Modelling & Architecture (Updated)
- **System**: Digital Campus Library Reservation Gateway (`UC-04: Pay Overdue Fine`)
- **Architectural Style**: Layered Architecture (Presentation, Business, Data/Hardware Services)
- **Key Files**:
  - Final Report PDF: `Lab3_FINAL_Submission_Dharshini_V_PES1UG24AM428.pdf` & `Lab3_FINAL_UC04_Dharshini_V_PES1UG24AM428.pdf`
  - Editable Word Report: `Lab3_Architecture_Justification_Dharshini_V_PES1UG24AM428.docx`
  - Component Diagram: `Digital_Campus_Library_Component_Diagram.png` & `.svg`
  - Diagram Model: `Digital_Campus_Library_Component_Diagram.drawio`

### Lab 4: Project Specifications & VibeCoding
- **Lab-04-SRS-SAD-STP**: Software Requirements Specification (SRS), Software Architecture and Design (SAD), and Software Test Plan (STP) for the Digital Campus Library Reservation Gateway.
- **Lab-04-VibeCoding**: Tug of War Python game repairs and enhancements (`source_code/`, before/after demonstration videos, chat history log, and final test verification report).

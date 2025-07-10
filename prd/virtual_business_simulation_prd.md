# Product Requirements Document (PRD)

## Virtual Business Simulation Extension for TinyTroupe

---

### Overview

This document outlines the high-level features and requirements for extending TinyTroupe into a virtual business simulation platform. The goal is to enable users to simulate a fully functioning business, with agents acting as employees, a management hierarchy, automated task assignment, and internal communication, all while building on top of TinyTroupe's existing architecture.

---

## Features

### 1. Employee Agent Repository
- **Purpose:** Maintain a structured directory (`employees/`) where each employee is represented as a separate JSON file.
- **Contents:** Each file contains all agent attributes (name, skills, department, role, etc.).
- **Benefit:** Enables easy management, onboarding, and ingestion of employee agents into simulations.

### 2. Hiring Database
- **Purpose:** Track all hiring events and maintain a record of current and past employees.
- **Contents:** Stores job title, skills, department, date of hire, and other relevant metadata.
- **Benefit:** Provides a historical and operational view of the organization's workforce.

### 3. Automated Assignment & Task Management
- **Purpose:** Automatically assign employees (individually or in groups) to simulations, meetings, or business tasks.
- **Features:**
  - Task assignment logic (manual and auto)
  - Support for branching from meetings into other business activities
  - Employees can be scheduled for daily tasks or ad-hoc projects
- **Benefit:** Simulates real business operations and workflow delegation.

### 4. Managerial Hierarchy
- **Purpose:** Model a management structure within the virtual business.
- **Features:**
  - Define managers, teams, and reporting lines
  - Enable hierarchical task delegation and escalation
- **Benefit:** Reflects real-world organizational dynamics and supports complex simulations.

### 5. Internal Communication System (Planned)
- **Purpose:** Allow employees to communicate via simulated email or messaging.
- **Features:**
  - Messaging system for agent-to-agent communication
  - Can be used for coordination, updates, or informal chat
- **Benefit:** Adds realism and supports richer, asynchronous business scenarios.

### 6. Business Day Simulation
- **Purpose:** Simulate a full business day, tracking what each employee does.
- **Features:**
  - Daily schedules, task logs, and activity summaries
  - Option for CEO (user) oversight and intervention
- **Benefit:** Enables end-to-end business process simulation and analytics.

### 7. CEO Oversight
- **Purpose:** You, as the user, act as the CEO—able to view, direct, and intervene in business operations.
- **Features:**
  - Dashboard for monitoring employees and tasks
  - Ability to assign, reassign, or review work

### 8. Non-Intrusive Extension
- **Purpose:** All features are built on top of TinyTroupe's existing architecture, leveraging async/sync capabilities.
- **Benefit:** Ensures maintainability and compatibility with future TinyTroupe updates.

---

## Summary Table

| Feature                        | Description                                                      | Status      |
|------------------------------- |------------------------------------------------------------------|-------------|
| Employee Agent Repository      | JSON files for each employee in a dedicated folder                | Planned     |
| Hiring Database                | Central record of all hires, roles, and skills                    | Planned     |
| Automated Assignment           | Auto/manual assignment of employees to tasks/simulations          | Planned     |
| Managerial Hierarchy           | Management structure and reporting lines                          | Planned     |
| Internal Communication System  | Simulated email/messaging between agents                          | Planned     |
| Business Day Simulation        | Track and simulate daily activities for all employees             | Planned     |
| CEO Oversight                  | User acts as CEO, with dashboard and intervention capabilities    | Planned     |
| Non-Intrusive Extension        | All features as add-ons, not core changes to TinyTroupe           | Planned     |

---

## Next Steps (Optional)
- Define data schemas for employee JSON files and hiring database.
- Design assignment and scheduling logic.
- Plan for communication system and dashboard UI.
- Identify integration points with existing TinyTroupe features. 
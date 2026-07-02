# Museo Sicano Portal 🏛️
🚀 A Full-Stack Python & Flask Web Application for Cultural Heritage Management

**Museo Sicano** is a purpose-driven digital portal designed to catalogue, preserve, and showcase historical artifacts and archaeological findings for local communities. 

The platform features a robust role-based access control system, allowing everyday citizens ("Abitanti") to browse approved collections, while verified researchers ("Operatori") and managers ("Amministratori") can catalog new items, upload field photos, and manage secure activation codes.

---

## 🛠️ Tech Stack & Architecture

- **Backend:** Python 3, Flask Framework
- **Database:** SQLite3 (Relational Database Management)
- **Security:** Password hashing, session-based authentication, and secure file upload validation
- **Frontend:** HTML5, CSS3, JavaScript

The project is developed using a modular architecture, splitting the core routing logic from the database managers and user authorization modules.

---

## 💡 Key Features Implemented

*   **Role-Based Access Control (RBAC):** Dynamic user dashboards tailored to three distinct roles (Abitante, Operatore, Amministratore).
*   **Artifact Cataloging Workflow:** Form validation to process technical archaeological data (GPS coordinates, preservation status, ICCD codes).
*   **Secure File Processing:** Images are validated against allowed extensions (`.png`, `.jpg`, `.jpeg`, `.gif`) and sanitized using `werkzeug.utils.secure_filename` before deployment.
*   **Administrative Panel:** Private tools for generating unique, single-use registration tokens to onboard new team members securely.

---



## 🧑‍💻 Collaboration & AI Prompt Engineering
This project highlights my ability to leverage **AI modern development tools** as a coding co-pilot. I effectively used advanced prompting to accelerate database modeling, debug HTTP route structures, and implement security middleware, while maintaining total ownership over the business logic and final refactoring.

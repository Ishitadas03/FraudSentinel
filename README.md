# FraudSentinel 🛡️

**FraudSentinel** is an AI-powered banking fraud detection and real-time transaction risk monitoring dashboard. It features a sleek dark-slate interface designed for fraud analysts, providing real-time KPI metrics, transaction volume trends, machine learning alerts, and seamless responsive design.

🔗 **Live Production URL**: [https://fraudsentinel-ai.vercel.app](https://fraudsentinel-ai.vercel.app)

![FraudSentinel Dashboard](https://img.shields.io/badge/Status-Active-brightgreen)
[![Vercel Deployment](https://img.shields.io/badge/Deployed%20with-Vercel-black?logo=vercel)](https://fraudsentinel-ai.vercel.app)
![React](https://img.shields.io/badge/React-18.3.0-blue?logo=react)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4.0-38B2AC?logo=tailwind-css)
![Vite](https://img.shields.io/badge/Vite-5.4.0-646CFF?logo=vite)
![Recharts](https://img.shields.io/badge/Recharts-2.12.7-22c55e)

---

## 🚀 Key Features

- **Executive KPI Cards**: Real-time stats for *Transactions Processed*, *Fraud Alerts Triggered*, and model *Accuracy* with positive/negative trend deltas.
- **Real-Time Transaction Monitoring**:
  - **Transaction Volume Chart**: Smooth Recharts `<LineChart>` without cluttered axis lines.
  - **Fraudulent Transactions Chart**: Hourly distribution bar chart with rounded tops.
- **Machine Learning Fraud Alerts Table**:
  - 5-column transaction alert records (Transaction ID, Amount, User, Timestamp, Status).
  - Neutral gray pill badges matching reference aesthetics (`Flagged`, `Under Review`, `Cleared`).
  - Subtle hairline borders and row hover highlights.
- **Two-Column Responsive Layout**:
  - Fixed dark sidebar (`#0B0E14`, `~240px`) with high-contrast active dashboard state.
  - Collapses into a clean icon-rail below `900px` for tablet screens.
  - Pinned actions: "New Transaction" primary button and "Help and Docs".
- **Accessible & Pixel-Matched**: Keyboard focus rings, aria-labels, and high-contrast typography.

---

## 📁 Repository Structure

```text
FraudSentinel/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx                  # Fixed navigation sidebar with responsive rail
│   │   │   ├── StatCard.jsx                 # KPI metric card with trend deltas
│   │   │   ├── TransactionVolumeChart.jsx   # Line chart for 24h volume
│   │   │   ├── FraudulentTransactionsChart.jsx # Bar chart for flagged volume
│   │   │   ├── FraudAlertsTable.jsx         # ML Alerts table with hairline dividers
│   │   │   └── StatusBadge.jsx              # Pill badge component
│   │   ├── pages/
│   │   │   └── Dashboard.jsx                # Main dashboard page layout
│   │   ├── data/
│   │   │   └── mockDashboard.js             # Centralized mock data store
│   │   ├── App.jsx                          # Root layout container
│   │   ├── index.css                        # Tailwind directives & scrollbar styles
│   │   └── main.jsx                         # React entrypoint
│   ├── index.html                           # HTML template with Inter font
│   ├── package.json                         # Pinned dependencies
│   ├── postcss.config.js                    # PostCSS config
│   ├── tailwind.config.js                   # Custom brand colors & theme
│   └── vite.config.js                       # Vite configuration
├── .gitignore
└── README.md
```

---

## 🛠️ Quickstart Guide

### Prerequisites
- Node.js (v18+ or v20+)
- npm / pnpm / yarn

### Installation & Run

1. Clone the repository:
   ```bash
   git clone https://github.com/RimiD162/FraudSentinel.git
   cd FraudSentinel/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173/` in your browser.

4. Production build:
   ```bash
   npm run build
   ```

---

## 🎨 Color System

| Token | Hex Value | Role |
| :--- | :--- | :--- |
| **Page Background** | `#0B0E14` | Main page canvas |
| **Alt Surface** | `#0D1017` | Secondary dark surface |
| **Card Surface** | `#161A22` | Cards, tables, and panels |
| **Hairline Borders** | `#222734` | 1px subtle divider lines |
| **Status Badge** | `#282E3E` | Neutral gray pill background |
| **Brand Blue** | `#2563EB` | Primary interactive buttons |

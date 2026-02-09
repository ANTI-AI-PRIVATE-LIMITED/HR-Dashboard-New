#  HR Management Dashboard (Supabase Powered)

A modern HR Management Dashboard built using **Flask**, **Supabase**, and **PostgreSQL** that helps HR teams manage job postings, candidate applications, resume storage, and contact requests efficiently.

---

##  Features

###  Job Management
- Create new job postings
- Edit existing jobs
- Delete job postings
- Department-based job categorization
- Automatic job posting timestamps

---

###  Application Tracking System (ATS)
- Candidate job applications management
- Resume upload & storage via Supabase Storage
- Resume preview via public URL
- Job-based application filtering
- Excel export for applications

---

###  Contact Request Management
- View all incoming contact form messages
- Internal testing form for adding contact requests
- Organized message tracking

---

###  Authentication
- HR Admin login system
- Session-based authentication
- Protected dashboard routes

---

### ☁️ Supabase Integration
- PostgreSQL database via Supabase
- Secure cloud resume storage
- Public storage bucket integration
- Row-level security supported

---

##  Tech Stack

### Backend
- Flask
- Python
- Supabase Python Client
- PostgreSQL

### Frontend
- HTML
- CSS
- Jinja Templates

### Storage
- Supabase Storage Buckets

---

## 📂 Database Schema

### Jobs Table
| Column | Type |
|----------|------------|
| id | UUID |
| title | Text |
| location | Text |
| department | Text |
| description | Text |
| is_active | Boolean |
| created_at | Timestamp |

---

### Applications Table
| Column | Type |
|----------|------------|
| id | UUID |
| job_id | UUID |
| name | Text |
| email | Text |
| phone | Text |
| resume_url | Text |
| cover_letter | Text |
| created_at | Timestamp |

---

### Contact Us Table
| Column | Type |
|----------|------------|
| id | UUID |
| full_name | Text |
| company | Text |
| message | Text |
| email | Text |
| phone | Text |
| created_at | Timestamp |

---

##  Installation & Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/ANTI-AI-PRIVATE-LIMITED/HR-Dashboard-New.git
cd HR-Dashboard-New

# 🧩 Dynamic Form Management Platform

A flexible **Form and Process Management System** built with **Django**, **Django REST Framework**, and **GraphQL**, designed for creating dynamic multi-step forms, managing user-driven workflows, and generating analytical reports — all powered by **Celery**, **Redis**, and **PostgreSQL** for scalability and performance.

---

## 🚀 Features

- 🧠 **Dynamic Process Builder:** Create customizable processes with ordered form sequences.
- 📄 **Form Management:** Define forms, questions, and relationships between them.
- 📊 **Report Generation:** Automatically compute and export analytics for completed processes.
- 🔐 **Authentication System:** Secure registration, OTP-based verification via email.
- ⚙️ **Asynchronous Task Queue:** Email delivery and background operations handled with **Celery** + **Redis**.
- 🧬 **GraphQL API:** Query forms, processes, and reports via Graphene-Django.
- 🐳 **Dockerized Deployment:** Ready-to-run setup for local and production environments.

---

## 🏗️ Project Structure

```bash
Dynamic_Form_Management/
├── apps/
│ ├── account/ # User accounts, OTP, email, and authentication logic
│ ├── core/ # Django core, Celery setup, GraphQL schema, and settings
│ ├── form/ # Dynamic forms, questions, and permission logic
│ ├── report/ # Analytics, reporting, and export logic
│ ├── Dockerfile # Development Dockerfile
│ ├── Dockerfile.prod # Production Dockerfile
│ ├── entrypoint.sh # Dev entrypoint script
│ ├── entrypoint.prod.sh
│ ├── manage.py
│ ├── requirements.txt # Python dependencies
│ └── schema.yml # API schema (for documentation)
├── docker-compose.yml # Local development orchestration
├── docker-compose.prod.yml # Production orchestration
├── documents/
│ ├── ERD.pdf # Entity-Relationship Diagram
│ └── README.md # Documentation notes
├── nginx/
│ ├── Dockerfile
│ └── nginx.conf
└── venv/ # Local virtual environment
```

---

## 🧠 Tech Stack

| Category          | Technology                        |
| ----------------- | --------------------------------- |
| Backend Framework | Django 5.x, Django REST Framework |
| API Layer         | Graphene-Django (GraphQL)         |
| Task Queue        | Celery                            |
| Message Broker    | Redis                             |
| Database          | PostgreSQL                        |
| Web Server (Prod) | Nginx + Gunicorn                  |
| Containerization  | Docker, Docker Compose            |
| Caching           | Redis                             |

---

## ⚙️ Setup Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/AmirmahdiGolahmar/Dynamic_Form_Management.git
cd Dynamic_Form_Management
```

### 2️⃣ Create and Configure Environment

```env
# Django
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*

# Database
POSTGRES_DB=dynamic_form_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email (Gmail SMTP example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

### 3️⃣ Run with Docker Compose

```bash
sudo docker compose up --build
```

#### This spins up:

- web: Django app
- db: PostgreSQL
- redis: Redis broker
- celery: Celery worker

#### You’ll then have:

- Django API -> [http://localhost:8000](http://localhost:8000)
- GraphQL Playground -> [http://localhost:8000/graphql](http://localhost:8000/graphql)

## 📨 Asynchronous Email Example

### Task Definition (account/tasks.py)

```python
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email_task(to_email, code):
    subject = "Your verification code"
    message = f"Your verification code is: {code}\nThis code expires in 2 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
```

### Usage

```python
from account.tasks import send_otp_email_task
send_otp_email_task.delay("user@example.com", "1234")
```

## 🧬 GraphQL Example

```graphql
query {
  allProcessesByUserId(userId: "1") {
    id
    name
    description
    forms {
      id
      title
    }
  }
}
```

### Schema (core/schema.py)

```python
import graphene
from graphene_django import DjangoObjectType
from form.models import Process, Form

class ProcessType(DjangoObjectType):
    class Meta:
        model = Process
        fields = ('id', 'name', 'description', 'creator', 'forms')

class Query(graphene.ObjectType):
    all_processes_by_user_id = graphene.List(ProcessType, user_id=graphene.String(required=True))

    def resolve_all_processes_by_user_id(root, info, user_id):
        return Process.objects.filter(creator=user_id)

schema = graphene.Schema(query=Query)
```

---

## 🧾 Useful Commands

| Command                            | Description                |
| ---------------------------------- | -------------------------- |
| python manage.py makemigrations    | Create migrations          |
| python manage.py migrate           | Apply migrations           |
| python manage.py createsuperuser   | Create admin user          |
| celery -A core worker -l info      | Run Celery worker manually |
| sudo docker compose logs -f celery | Tail Celery logs           |

---

## 🧱 Architecture Overview

```scss
┌──────────────────────────────────────┐
│              Django API              │
│  (DRF + GraphQL endpoints + models)  │
└────────────────┬─────────────────────┘
                 │
                 ▼
         Celery Task Queue
     (Email, reports, background jobs)
                 │
                 ▼
         Redis Message Broker
                 │
                 ▼
         PostgreSQL Database
```

## 🧰 Development Notes

- All configurations are environment-driven (.env.dev or .env.prod).
- Use entrypoint.sh to ensure DB and Redis are ready before Django/Celery start.
- For production, see docker-compose.prod.yml and Dockerfile.prod (Gunicorn + Nginx setup).

## 📜 License

### This project is licensed under the MIT License — feel free to modify and adapt it.

“Dynamic processes. Smart forms. Scalable architecture.”

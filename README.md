# OpenW
### AI-driven CRM with native WhatsApp integration

OpenW is an open-source, self-hostable CRM platform built around WhatsApp. It lets teams manage customer conversations at scale, track interactions with AI assistance, and store everything securely — without paying a monthly fee to a third-party SaaS.

---

## The Problematic

WhatsApp CRM solutions are not new. The market is full of platforms offering contact management, automated responses, and conversation tracking built on top of WhatsApp. The problem? Almost every single one of them comes with a recurring subscription tied to a startup's infrastructure — infrastructure you have no control over.

Companies that want this kind of business solution are forced to depend on third parties, accept their pricing tiers, and trust that the service won't go down, pivot, or raise rates. This is an unnecessary constraint.

OpenW addresses this directly: with a basic understanding of the WhatsApp Open API and a self-guided setup, developers can deploy their own instance, swap in their own credentials, and be live. No middleman. No subscription. Just your stack, your data, and your rules.

---

## Key Features

- **WhatsApp Open API integration** — send and receive messages, handle webhooks natively
- **AI-powered conversation tracking** — semantic similarity search via pgVector to surface relevant context and assist responses
- **Open-source CRM dashboard** — contact management, conversation history, pipeline stages, and tagging
- **Secure data layer** — PostgreSQL 17 with pgVector for both relational and vector data storage
- **Multi-user support** — role-based access control for teams
- **Self-hostable** — fully containerized, runs anywhere Docker does

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, Tailwind CSS v4, TypeScript |
| Backend | Python, Flask |
| Database | PostgreSQL 17 + pgVector |
| Containerization | Docker, Docker Compose |

---

## Getting Started

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- A WhatsApp Business account with access to the [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/OpenW.git
   cd OpenW
   ```

2. **Configure your environment**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and fill in your credentials (see [Environment Variables](#environment-variables) below).

3. **Start the application**
   ```bash
   docker compose up --build
   ```

4. **Open the app**
   - Frontend: [http://localhost:1111](http://localhost:1111)
   - Backend API: [http://localhost:2222](http://localhost:2222)

---

## Environment Variables

Copy `.env.example` to `.env` and configure the following:

| Variable | Description | Required |
|---|---|---|
| `FLASK_MODE` | Flask environment (`development` / `production`) | Yes |
| `SECRET_KEY` | Flask secret key for session signing | Yes |
| `DB_USER` | PostgreSQL username | Yes |
| `DB_PASSWORD` | PostgreSQL password | Yes |
| `DB_NAME` | PostgreSQL database name | Yes |
| `DB_HOST` | Database host (use `db` inside Docker) | Yes |
| `DB_PORT` | Database port (default: `5432`) | Yes |
| `BACKEND_PORT` | Port the Flask API listens on (default: `2222`) | Yes |
| `FRONTEND_PORT` | Port the Next.js app listens on (default: `1111`) | Yes |
| `DB_EXPOSED_PORT` | Host-side port mapped to PostgreSQL (default: `5432`) | Yes |

---

## Architecture

```
Browser
   │
   ▼
Next.js  (port 1111)
   │
   ▼
Flask API  (port 2222)
   │
   ▼
PostgreSQL + pgVector  (port 5432)
```

---

## Roadmap

- [ ] WhatsApp webhook integration
- [ ] AI conversation summarization
- [ ] Contact tagging and pipeline stages
- [ ] JWT / OAuth authentication system
- [ ] Multi-tenant support
- [ ] `.env.example` template file

---

## Contributing

1. Fork the repository and create a feature branch
2. Run the stack locally with `docker compose up --build`
3. Submit a pull request with a clear description of the change

---

## License

This project is open-source. License TBD.

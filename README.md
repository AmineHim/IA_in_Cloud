# Analyse de Conformité Contractuelle - Agent Vocal Intelligent

Système multi-agents d'analyse de conformité contractuelle internationale, avec interface vocale et traçabilité complète.

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────┐
│  Streamlit   │────▶│              FastAPI Backend              │
│  (Frontend)  │◀────│                                          │
│  :8501       │     │  ┌──────────┐  ┌─────────┐  ┌────────┐  │
└─────────────┘     │  │ LangGraph│  │ChromaDB │  │ SQLite │  │
                    │  │  Agents  │  │  (RAG)  │  │ (Audit)│  │
┌─────────────┐     │  └──────────┘  └─────────┘  └────────┘  │
│     n8n      │────▶│              :8000                       │
│  :5678       │     └──────────────────────────────────────────┘
└─────────────┘
```

### Agents LangGraph

| Agent | Role |
|-------|------|
| **Retrieval** | Recherche les clauses contractuelles et réglementations pertinentes via ChromaDB |
| **Analyse Juridique** | Analyse la conformité, identifie les non-conformités |
| **Validation** | Vérifie les affirmations contre les sources, évalue le niveau de risque |
| **Synthèse** | Produit la réponse finale argumentée avec citations |

### Stack technique

- **LLM** : Llama 3.3 70B via Groq API (gratuit)
- **RAG** : LangChain + ChromaDB + embeddings all-MiniLM-L6-v2
- **Backend** : FastAPI
- **Frontend** : Streamlit
- **Orchestration** : LangGraph (agents) + n8n (workflow)
- **Audio** : Groq Whisper (STT) + gTTS (TTS)
- **Audit** : SQLite
- **Conteneurisation** : Docker Compose

## Prérequis

- Docker et Docker Compose
- Clé API Groq gratuite (https://console.groq.com)

## Installation et lancement

1. **Cloner le projet**
```bash
git clone <repo-url>
cd projet_ia_cloud
```

2. **Configurer l'environnement**
```bash
cp .env.example .env
# Editer .env et ajouter votre clé GROQ_API_KEY
```

3. **Lancer les services**
```bash
docker-compose up --build
```

4. **Indexer les documents** (premier lancement)
```bash
curl -X POST http://localhost:8000/reindex
```

5. **Accéder aux interfaces**
- Frontend Streamlit : http://localhost:8501
- API Backend : http://localhost:8000/docs
- n8n : http://localhost:5678

## Utilisation

### Via l'interface Streamlit
1. Se connecter avec le mot de passe (par défaut : `conformite2026`)
2. Sélectionner un contrat ou "Tous les contrats"
3. Poser une question (texte ou audio)
4. Consulter la synthèse, l'analyse détaillée, les sources
5. Ecouter la réponse vocale
6. Accéder au journal d'audit

### Via n8n
1. Importer le workflow depuis `n8n/workflow_compliance_analysis.json`
2. Activer le workflow
3. Envoyer une requête POST au webhook

### Via l'API directement
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Ce contrat respecte-t-il le RGPD ?", "contract_name": null}'
```

## Données incluses

### Réglementations
- AI Act (UE 2024/1689)
- RGPD (UE 2016/679)
- NIST AI Risk Management Framework
- Loi Informatique et Libertés (France)

### Contrats (SEC EDGAR)
- Master Service Agreements
- Supply Agreements
- Data Processing Agreements
- Registration Statements

## Journal d'audit

Chaque analyse est tracée dans SQLite avec :
- ID de session unique
- Timestamp
- Agent ayant effectué l'action
- Input / Output
- Sources utilisées
- Raisonnement

## Structure du projet

```
projet_ia_cloud/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py          # API FastAPI
│   ├── agents.py        # Orchestration LangGraph
│   ├── ingest.py        # Ingestion documents + ChromaDB
│   ├── audit.py         # Journal d'audit SQLite
│   └── config.py        # Configuration
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py           # Interface Streamlit
├── n8n/
│   └── workflow_compliance_analysis.json
├── data/
│   ├── regulations/     # PDF réglementaires
│   └── contracts/       # Contrats HTML/PDF
├── logs/                # Audit logs
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md
```

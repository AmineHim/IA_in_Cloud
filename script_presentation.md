# Script de Présentation — Analyse de Conformité Contractuelle

**Durée estimée : 20-25 minutes**
**4 présentateurs**

---

## SLIDE 1 — Page de titre
**Présentateur 1** (30 sec)

> Bonjour à tous. Nous sommes [Présentateur 1], [Présentateur 2], [Présentateur 3] et [Présentateur 4]. Aujourd'hui, nous allons vous présenter notre projet : un système d'analyse de conformité contractuelle basé sur l'intelligence artificielle, avec une interface vocale intelligente et une architecture multi-agents.

---

## SLIDE 2 — Sommaire
**Présentateur 1** (30 sec)

> Voici le plan de notre présentation. Nous commencerons par le contexte et la problématique, puis nous détaillerons l'architecture technique et le pipeline multi-agents. Ensuite, nous vous ferons une démonstration des fonctionnalités, avant de présenter l'infrastructure de déploiement. Nous conclurons ensemble avec le bilan et les perspectives.

---

## SLIDE 3 — Contexte & Problématique
**Présentateur 1** (2 min)

> Parlons d'abord du constat qui nous a motivés. Aujourd'hui, les entreprises font face à une multiplication des réglementations internationales : le RGPD en Europe, l'AI Act adopté en 2024, le cadre NIST aux États-Unis, la loi Informatique et Libertés en France. Vérifier qu'un contrat est conforme à l'ensemble de ces textes est un travail considérable.
>
> L'analyse manuelle est lente, coûteuse, et surtout sujette aux erreurs humaines. Un juriste peut passer des heures sur un seul contrat, et il est difficile de garantir qu'aucune clause problématique n'a été manquée. De plus, les auditeurs exigent une traçabilité complète du processus d'analyse.
>
> Notre solution : un système multi-agents IA qui automatise cette analyse. Le système utilise le RAG — Retrieval Augmented Generation — pour fournir des réponses sourcées et argumentées, citant les articles de loi précis. Il intègre aussi une interface vocale pour rendre l'outil accessible au plus grand nombre, et un audit trail complet pour répondre aux exigences de traçabilité.

---

## SLIDE 4 — Réglementations couvertes
**Présentateur 1** (1 min 30)

> Notre système couvre quatre corpus réglementaires majeurs.
>
> Le **RGPD**, règlement européen de 2016, qui encadre la protection des données personnelles, les droits des personnes et les transferts internationaux de données.
>
> L'**AI Act**, le tout nouveau règlement européen de 2024, qui classifie les systèmes d'IA par niveau de risque et impose des obligations de conformité et de transparence algorithmique.
>
> Le **NIST AI Risk Management Framework**, le cadre américain de gestion des risques liés à l'IA, qui couvre la gouvernance, la fiabilité et la sécurité.
>
> Et enfin la **Loi Informatique et Libertés**, le droit français applicable via la CNIL, qui couvre les données sensibles, le consentement et le droit d'accès.
>
> Tous ces textes sont indexés dans notre base vectorielle et consultables automatiquement par nos agents.

*[Transition vers Présentateur 2]*

---

## SLIDE 5 — Architecture Globale
**Présentateur 2** (2 min)

> Passons à l'architecture technique. Notre système repose sur trois services conteneurisés orchestrés par Docker Compose.
>
> Le **Frontend Streamlit** sur le port 8501 : c'est l'interface utilisateur qui permet la saisie de questions en texte ou par la voix.
>
> Le **Backend FastAPI** sur le port 8000 : c'est le cœur du système. Il orchestre les 4 agents IA, gère l'ingestion des documents, les appels au LLM, la transcription audio et la synthèse vocale. C'est lui qui expose l'API REST complète.
>
> Le service **n8n** sur le port 5678 : il permet l'automatisation des workflows, notamment le routage des alertes par niveau de risque via des webhooks.
>
> En externe, nous utilisons l'**API Groq** qui nous donne accès au modèle Llama 3.3 70B pour l'analyse juridique, ainsi qu'au modèle Whisper pour la transcription audio.
>
> En bas, la couche données : **ChromaDB** comme base vectorielle pour le RAG avec des embeddings MiniLM-L6-v2, **SQLite** pour les logs d'audit, et les volumes persistants pour les réglementations et contrats.

---

## SLIDE 6 — Pipeline Multi-Agents (LangGraph)
**Présentateur 2** (2 min 30)

> Le cœur de notre système, c'est le pipeline multi-agents orchestré par LangGraph. Quatre agents spécialisés travaillent en séquence.
>
> **Agent 1 — Retrieval** : quand l'utilisateur pose une question, cet agent effectue une recherche sémantique dans ChromaDB. Il récupère les 5 extraits de contrat les plus pertinents et les 8 articles réglementaires les plus proches de la question. C'est le RAG en action.
>
> **Agent 2 — Analyse Juridique** : il reçoit les documents récupérés et effectue une analyse croisée entre les clauses du contrat et les textes réglementaires. Il identifie les non-conformités potentielles et cite les articles de loi précis.
>
> **Agent 3 — Validation** : c'est notre couche de vérification. Il relit l'analyse juridique, vérifie la cohérence des conclusions, effectue un contrôle multi-juridictionnel et attribue un niveau de risque : faible, moyen, élevé ou critique.
>
> **Agent 4 — Synthèse** : il produit la réponse finale argumentée, avec des citations précises, un résumé des non-conformités détectées et des recommandations concrètes.
>
> Point important : chaque étape est enregistrée dans notre audit trail. Session ID unique, timestamp, entrées et sorties de chaque agent, sources utilisées et raisonnement complet. C'est essentiel pour la traçabilité réglementaire.

---

## SLIDE 7 — Stack Technique
**Présentateur 2** (1 min)

> Un rapide tour de notre stack technique.
>
> Côté **IA et NLP** : LangChain et LangGraph pour l'orchestration des agents, Groq avec Llama 3.3 70B comme LLM, ChromaDB avec les embeddings MiniLM-L6-v2 pour la recherche sémantique, Whisper pour la transcription et gTTS pour la synthèse vocale.
>
> Côté **Backend** : Python 3.11, FastAPI comme framework web asynchrone, Pydantic pour la validation des données, PyMuPDF pour l'extraction de texte des PDF et BeautifulSoup pour le HTML.
>
> Côté **Frontend** : Streamlit pour l'interface web rapide et interactive, avec un composant d'enregistrement audio intégré.
>
> L'**infrastructure** repose entièrement sur Docker et Docker Compose, avec n8n pour les workflows automatisés et SQLite pour l'audit.

*[Transition vers Présentateur 3]*

---

## SLIDE 8 — Fonctionnalités Clés
**Présentateur 3** (2 min)

> Voici les six fonctionnalités principales de notre système.
>
> **Interface Vocale** : l'utilisateur peut poser sa question au micro ou uploader un fichier audio. La transcription est automatique via Whisper, et la conclusion de l'analyse est lue à voix haute en français.
>
> **Analyse Multi-Contrats** : on peut analyser un contrat spécifique ou l'ensemble du corpus en une seule requête. La sélection se fait directement dans l'interface.
>
> **Conformité Argumentée** : chaque réponse cite précisément les articles de loi concernés. Le système ne donne pas juste un "oui" ou "non", il argumente avec des sources.
>
> **RAG Intelligent** : la recherche sémantique retrouve les passages les plus pertinents dans les contrats et les réglementations, même si la question est formulée différemment du texte original.
>
> **Audit Complet** : chaque analyse génère un journal complet consultable via l'API, avec toutes les étapes du raisonnement.
>
> **Automatisation n8n** : les workflows permettent de déclencher des alertes automatiques quand un risque critique est détecté.

---

## SLIDE 9 — Parcours Utilisateur
**Présentateur 3** (2 min)

> Voyons le parcours utilisateur en 5 étapes.
>
> **Étape 1** : l'utilisateur se connecte via un mot de passe sur l'interface Streamlit.
>
> **Étape 2** : il saisit sa question, soit en texte, soit en utilisant le micro pour poser sa question à voix haute.
>
> **Étape 3** : il sélectionne le périmètre d'analyse — un contrat spécifique ou l'ensemble du corpus.
>
> **Étape 4** : le pipeline de 4 agents s'exécute en séquence — retrieval, analyse, validation, synthèse.
>
> **Étape 5** : les résultats s'affichent avec l'analyse complète, les niveaux de risque, les citations réglementaires, et la possibilité d'écouter la conclusion en audio.
>
> Par exemple, on peut demander : "Ce contrat est-il conforme au RGPD si les données sont hébergées aux États-Unis ?" ou "L'AI Act impose-t-il des obligations de validation pour les systèmes IA de ce contrat ?"
>
> *[Si une démo live est prévue, la faire ici]*

*[Transition vers Présentateur 4]*

---

## SLIDE 10 — Infrastructure & Déploiement
**Présentateur 4** (2 min)

> Passons à l'infrastructure. Notre application est entièrement conteneurisée avec Docker Compose et comprend 3 services.
>
> Le **compliance-backend** en Python 3.11 sur le port 8000, avec des health checks configurés et une politique de redémarrage automatique.
>
> Le **compliance-frontend** en Streamlit sur le port 8501, qui dépend du backend et attend qu'il soit opérationnel avant de démarrer.
>
> Le **compliance-n8n** qui utilise l'image officielle n8n sur le port 5678, avec son propre volume persistant pour les workflows.
>
> Côté **sécurité** : toutes les clés et mots de passe sont gérés via des variables d'environnement dans un fichier `.env`. L'accès Streamlit est protégé par mot de passe, n8n a son authentification basique, et la clé API Groq est sécurisée. Les données restent stockées localement, on-premise.
>
> Le **déploiement** se fait en 3 commandes : cloner le repo et configurer le `.env`, lancer Docker Compose, puis déclencher l'indexation des documents. En quelques minutes, le système est opérationnel.

---

## SLIDE 11 — API REST
**Présentateur 4** (1 min 30)

> Notre backend expose une API REST complète, documentée automatiquement via Swagger sur `/docs`.
>
> Les endpoints principaux : `/analyze` pour lancer une analyse de conformité, `/upload-contract` pour ajouter un nouveau contrat qui sera automatiquement vectorisé, `/contracts` pour lister les contrats disponibles.
>
> Pour l'audio : `/tts` pour la synthèse vocale et `/stt` pour la transcription.
>
> Pour l'audit : on peut consulter les logs par session avec `/audit/{session_id}` ou récupérer l'historique complet avec `/audit`.
>
> Et `/reindex` permet de reconstruire la base vectorielle quand de nouveaux documents sont ajoutés.
>
> Tous les endpoints sont testables directement via l'interface Swagger.

*[Transition vers conclusion commune]*

---

## SLIDE 12 — Bilan & Perspectives
**Tous les présentateurs** (3 min)

**Présentateur 1** :
> Pour conclure, faisons le bilan. Nous avons réalisé un système multi-agents fonctionnel avec 4 agents spécialisés qui travaillent en séquence via LangGraph. L'interface vocale complète avec transcription et synthèse est opérationnelle. Le RAG fonctionne sur les 4 réglementations indexées, et la traçabilité d'audit est complète.

**Présentateur 2** :
> En termes de perspectives, le système pourrait être déployé sur le cloud — AWS, GCP ou Azure — pour le rendre accessible en production. On pourrait ajouter de nouvelles réglementations, proposer une interface multi-langues, et intégrer un pipeline CI/CD complet.

**Présentateur 3** :
> Ce projet nous a beaucoup appris. L'orchestration multi-agents avec LangGraph demande de bien penser la gestion de l'état partagé entre agents. Le RAG appliqué au domaine juridique nous a montré l'importance du chunking et de la qualité des embeddings — un mauvais découpage des textes dégrade fortement les résultats.

**Présentateur 4** :
> L'intégration vocale en temps réel pose des défis de latence et de qualité de transcription. Et la conteneurisation multi-services nous a appris à bien gérer la communication inter-containers et les dépendances de démarrage entre services.

---

## SLIDE 13 — Merci / Questions
**Présentateur 1** (30 sec)

> Merci pour votre attention. Notre application est accessible sur les ports que vous voyez à l'écran. Nous sommes prêts à répondre à vos questions, et si vous le souhaitez, nous pouvons vous faire une démonstration en direct.

---

## Notes pratiques

- **Remplacer** "Présentateur 1/2/3/4" par vos vrais noms dans les slides et ce script
- **Timing** : chaque présentateur parle environ 5 minutes
- **Démo live** : préparer Docker lancé en avance pour éviter l'attente du build
- **Questions fréquentes à anticiper** :
  - Pourquoi Groq et pas OpenAI ? → Accès gratuit, modèle performant (Llama 3.3 70B)
  - Comment gérer les hallucinations du LLM ? → Le RAG source les réponses, l'agent de validation vérifie
  - Scalabilité ? → Architecture Docker prête pour le cloud, ChromaDB supporte le scaling
  - Quid de la confidentialité des contrats ? → Données locales, seule la requête LLM passe par Groq

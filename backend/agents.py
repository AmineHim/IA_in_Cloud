"""Multi-agent orchestration with LangGraph.

Agents:
1. Retrieval Agent  - finds relevant contract clauses and regulations
2. Legal Analysis Agent - analyzes compliance issues
3. Validation Agent - cross-checks findings across jurisdictions
4. Synthesis Agent - produces final argued response with citations
"""

import uuid
from typing import TypedDict, Annotated

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from config import GROQ_API_KEY, GROQ_MODEL
from ingest import get_vectorstore
from audit import log_step


llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name=GROQ_MODEL,
    temperature=0.1,
)


class AgentState(TypedDict):
    session_id: str
    query: str
    contract_name: str
    contract_chunks: list[str]
    regulation_chunks: list[str]
    retrieval_result: str
    legal_analysis: str
    validation_result: str
    final_response: str
    sources: list[str]


# --- Agent 1: Retrieval ---
def retrieval_agent(state: AgentState) -> AgentState:
    vs = get_vectorstore()

    # Search contract clauses
    contract_results = vs.similarity_search(
        state["query"], k=5,
        filter={"type": "contract"} if state.get("contract_name") is None
        else {"source": state["contract_name"]},
    )
    contract_chunks = [doc.page_content for doc in contract_results]
    contract_sources = [doc.metadata.get("source", "") for doc in contract_results]

    # Search regulations
    reg_results = vs.similarity_search(state["query"], k=8, filter={"type": "regulation"})
    regulation_chunks = [doc.page_content for doc in reg_results]
    reg_sources = [doc.metadata.get("source", "") for doc in reg_results]

    retrieval_text = (
        "=== CLAUSES CONTRACTUELLES ===\n"
        + "\n---\n".join(contract_chunks)
        + "\n\n=== RÉGLEMENTATIONS ===\n"
        + "\n---\n".join(regulation_chunks)
    )

    all_sources = list(set(contract_sources + reg_sources))

    log_step(
        state["session_id"], "retrieval", "search",
        state["query"], f"Found {len(contract_chunks)} contract chunks, {len(regulation_chunks)} regulation chunks",
        all_sources, "Similarity search on vectorstore"
    )

    return {
        **state,
        "contract_chunks": contract_chunks,
        "regulation_chunks": regulation_chunks,
        "retrieval_result": retrieval_text,
        "sources": all_sources,
    }


# --- Agent 2: Legal Analysis ---
def legal_analysis_agent(state: AgentState) -> AgentState:
    prompt = f"""Tu es un expert juridique international spécialisé en conformité contractuelle.

Analyse les clauses contractuelles suivantes au regard des réglementations fournies.

QUESTION DE L'UTILISATEUR : {state["query"]}

{state["retrieval_result"]}

Tu dois :
1. Identifier les clauses critiques du contrat (hébergement données, sous-traitance, responsabilité, audit, IA)
2. Pour chaque clause, identifier les réglementations applicables
3. Détecter les potentielles non-conformités
4. Citer précisément les articles de loi concernés

Réponds en français de manière structurée."""

    response = llm.invoke(prompt)

    log_step(
        state["session_id"], "legal_analysis", "analyze",
        state["query"], response.content[:500],
        state["sources"], "Cross-referencing contract clauses with regulations"
    )

    return {**state, "legal_analysis": response.content}


# --- Agent 3: Validation ---
def validation_agent(state: AgentState) -> AgentState:
    prompt = f"""Tu es un agent de validation juridique. Tu vérifies l'analyse de conformité suivante.

QUESTION : {state["query"]}

ANALYSE JURIDIQUE :
{state["legal_analysis"]}

SOURCES RÉGLEMENTAIRES :
{chr(10).join(state["regulation_chunks"][:3])}

Tu dois :
1. Vérifier que chaque affirmation est soutenue par une source réglementaire
2. Identifier les contradictions ou erreurs potentielles
3. Vérifier la cohérence multi-juridictionnelle (si plusieurs pays sont concernés)
4. Attribuer un niveau de risque : FAIBLE / MOYEN / ÉLEVÉ / CRITIQUE

Réponds en français."""

    response = llm.invoke(prompt)

    log_step(
        state["session_id"], "validation", "validate",
        state["legal_analysis"][:300], response.content[:500],
        state["sources"], "Validating legal analysis against source regulations"
    )

    return {**state, "validation_result": response.content}


# --- Agent 4: Synthesis ---
def synthesis_agent(state: AgentState) -> AgentState:
    prompt = f"""Tu es un agent de synthèse pour un service de conformité juridique.

QUESTION INITIALE : {state["query"]}

ANALYSE JURIDIQUE :
{state["legal_analysis"]}

VALIDATION :
{state["validation_result"]}

SOURCES UTILISÉES : {", ".join(state["sources"])}

Produis une synthèse finale qui :
1. Répond directement à la question posée
2. Résume les non-conformités détectées avec leur niveau de risque
3. Cite les articles et sources précis utilisés (entre crochets [Source: ...])
4. Propose des recommandations concrètes
5. Est formulée de manière claire pour un responsable conformité
6. Se termine par une section "Conclusion" qui résume en 2-3 phrases l'essentiel

IMPORTANT : Ne commence PAS ta réponse par un titre comme "Synthèse finale" ou "Synthèse". Commence directement par le contenu.
La réponse doit être professionnelle, argumentée et directement actionnable.
Réponds en français."""

    response = llm.invoke(prompt)

    log_step(
        state["session_id"], "synthesis", "synthesize",
        state["query"], response.content[:500],
        state["sources"], "Producing final argued synthesis"
    )

    return {**state, "final_response": response.content}


# --- Build the graph ---
def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("agent_retrieval", retrieval_agent)
    workflow.add_node("agent_legal", legal_analysis_agent)
    workflow.add_node("agent_validation", validation_agent)
    workflow.add_node("agent_synthesis", synthesis_agent)

    workflow.set_entry_point("agent_retrieval")
    workflow.add_edge("agent_retrieval", "agent_legal")
    workflow.add_edge("agent_legal", "agent_validation")
    workflow.add_edge("agent_validation", "agent_synthesis")
    workflow.add_edge("agent_synthesis", END)

    return workflow.compile()


# Main entry point
graph = build_graph()


def analyze_contract(query: str, contract_name: str = None) -> dict:
    session_id = str(uuid.uuid4())
    initial_state: AgentState = {
        "session_id": session_id,
        "query": query,
        "contract_name": contract_name,
        "contract_chunks": [],
        "regulation_chunks": [],
        "retrieval_result": "",
        "legal_analysis": "",
        "validation_result": "",
        "final_response": "",
        "sources": [],
    }

    result = graph.invoke(initial_state)

    return {
        "session_id": result["session_id"],
        "response": result["final_response"],
        "legal_analysis": result["legal_analysis"],
        "validation": result["validation_result"],
        "sources": result["sources"],
    }

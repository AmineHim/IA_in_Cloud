"""Streamlit frontend for the Compliance Analysis System."""

import streamlit as st
import requests
import json
import os

API_URL = os.getenv("API_URL", "http://backend:8000")

CUSTOM_CSS = """
<style>
    .block-container { max-width: 900px; padding-top: 2rem; }

    .app-header {
        padding: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    .app-header h1 { margin: 0; font-size: 1.8rem; color: #e0e0e0; }
    .app-header p { margin: 0.3rem 0 0 0; color: #aaa; font-size: 0.95rem; }

    .result-card {
        background: rgba(74, 108, 247, 0.1);
        border-left: 4px solid #5b9aff;
        padding: 1.2rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #e0e0e0;
    }

    .source-tag {
        display: inline-block;
        background: rgba(74, 108, 247, 0.15);
        color: #7dacff;
        padding: 0.25rem 0.7rem;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 0.2rem;
        border: 1px solid rgba(91, 154, 255, 0.3);
    }

    .contract-item {
        padding: 0.5rem 0;
        border-bottom: 1px solid #e8eaed;
        font-size: 0.9rem;
        color: #333;
    }
    .contract-item:last-child { border-bottom: none; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    [data-testid="stSidebar"] { background: #1a1a2e; }
    [data-testid="stSidebar"] .stRadio label { color: #fff; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fff; }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label p { color: #ccc; }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] button { color: #aaa; font-weight: 500; }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] { color: #fff; font-weight: 600; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #5b9aff; }

    /* Contract list */
    .contract-item { color: #e0e0e0; font-weight: 500; font-size: 0.95rem; }
</style>
"""

EXAMPLE_QUESTIONS = {
    "Conformite RGPD pour hebergement aux Etats-Unis":
        "Ce contrat prevoit un hebergement des donnees aux Etats-Unis. Est-ce conforme au RGPD si les donnees concernent des clients europeens ?",
    "Compatibilite avec la loi marocaine 09-08":
        "L'hebergement aux Etats-Unis est-il compatible avec la loi marocaine 09-08 si les donnees concernent un fournisseur marocain ?",
    "Validation humaine et AI Act":
        "L'absence de validation humaine est-elle compatible avec l'AI Act ?",
    "Localisation des donnees dans le contrat":
        "Ou les donnees sont-elles hebergees selon ce contrat ?",
    "Responsabilite en cas d'erreur d'IA (droit francais)":
        "Qui est juridiquement responsable en cas d'erreur d'interpretation automatisee selon la reglementation francaise ?",
}


def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
        st.markdown("")
        st.markdown("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Analyse de Conformite")
            st.markdown("Connectez-vous pour acceder au systeme.")
            password = st.text_input("Mot de passe", type="password", label_visibility="collapsed", placeholder="Mot de passe")
            if st.button("Se connecter", use_container_width=True, type="primary"):
                if password == os.getenv("STREAMLIT_PASSWORD", "conformite2026"):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Mot de passe incorrect")
        st.stop()


def main():
    st.set_page_config(
        page_title="Analyse de Conformite",
        layout="wide",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    check_auth()

    with st.sidebar:
        st.markdown("### Conformite AI")
        st.markdown("---")
        page = st.radio(
            "Navigation",
            ["Analyse", "Contrats"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.markdown(
            "<small style='color:#888'>Multi-agents LangGraph<br>RAG + Groq LLM</small>",
            unsafe_allow_html=True,
        )

    if page == "Analyse":
        page_analysis()
    elif page == "Contrats":
        page_contracts()


def page_analysis():
    st.markdown(
        '<div class="app-header"><h1>Analyse de conformite</h1>'
        "<p>Interrogez vos contrats au regard des reglementations internationales</p></div>",
        unsafe_allow_html=True,
    )

    # Contract selector
    try:
        resp = requests.get(f"{API_URL}/contracts", timeout=5)
        contracts = resp.json().get("contracts", [])
    except Exception:
        contracts = []
        st.error("Backend non disponible.")
        return

    selected_contract = st.selectbox(
        "Contrat a analyser",
        ["Tous les contrats"] + contracts,
    )

    # Question input
    tab_text, tab_voice = st.tabs(["Question ecrite", "Question vocale"])

    with tab_text:
        # Example question selector
        selected_example = st.selectbox(
            "Questions types",
            ["Ecrire ma propre question..."] + list(EXAMPLE_QUESTIONS.keys()),
        )

        if selected_example != "Ecrire ma propre question...":
            default_query = EXAMPLE_QUESTIONS[selected_example]
        else:
            default_query = st.session_state.get("query_input", "")

        query = st.text_area(
            "Votre question",
            value=default_query,
            height=80,
            placeholder="Posez votre question juridique ici...",
            label_visibility="collapsed",
        )

    with tab_voice:
        from st_audiorec import st_audiorec

        st.markdown("**Enregistrer depuis le micro**")
        audio_bytes = st_audiorec()

        if audio_bytes:
            if st.button("Transcrire l'enregistrement"):
                with st.spinner("Transcription..."):
                    files = {"file": ("recording.wav", audio_bytes, "audio/wav")}
                    try:
                        resp = requests.post(f"{API_URL}/stt", files=files, timeout=30)
                        if resp.status_code == 200:
                            transcription = resp.json().get("text", "")
                            st.session_state.query_input = transcription
                            query = transcription
                            st.success(f"Transcription : {transcription}")
                        else:
                            st.error(f"Erreur: {resp.text}")
                    except Exception as e:
                        st.error(str(e))

        st.markdown("---")
        st.markdown("**Ou importer un fichier audio**")
        audio_file = st.file_uploader(
            "Fichier audio",
            type=["wav", "mp3", "m4a", "webm"],
            label_visibility="collapsed",
        )
        if audio_file is not None:
            st.audio(audio_file)
            if st.button("Transcrire le fichier"):
                with st.spinner("Transcription..."):
                    files = {"file": (audio_file.name, audio_file.getvalue(), audio_file.type)}
                    try:
                        resp = requests.post(f"{API_URL}/stt", files=files, timeout=30)
                        if resp.status_code == 200:
                            transcription = resp.json().get("text", "")
                            st.session_state.query_input = transcription
                            query = transcription
                            st.success(f"Transcription : {transcription}")
                        else:
                            st.error(f"Erreur: {resp.text}")
                    except Exception as e:
                        st.error(str(e))

    # Analyze
    if st.button("Lancer l'analyse", type="primary", use_container_width=True):
        if not query:
            st.warning("Veuillez entrer une question.")
            return

        contract_name = None if selected_contract == "Tous les contrats" else selected_contract

        with st.spinner("Analyse en cours..."):
            try:
                resp = requests.post(
                    f"{API_URL}/analyze",
                    json={"query": query, "contract_name": contract_name},
                    timeout=120,
                )
                if resp.status_code != 200:
                    st.error("Erreur lors de l'analyse.")
                    return
                result = resp.json()
            except Exception as e:
                st.error(f"Connexion impossible : {e}")
                return

        st.session_state.last_session_id = result["session_id"]

        # --- Results ---
        st.markdown("---")

        st.markdown("#### Synthese")
        st.markdown(
            f'<div class="result-card">{result["response"]}</div>',
            unsafe_allow_html=True,
        )

        # Audio
        with st.spinner("Generation de la reponse vocale..."):
            try:
                tts_resp = requests.post(
                    f"{API_URL}/tts",
                    json={"query": result["response"]},
                    timeout=60,
                )
                if tts_resp.status_code == 200:
                    st.markdown("**Reponse vocale (conclusion)**")
                    st.audio(tts_resp.content, format="audio/mpeg")
            except Exception as e:
                st.warning(f"Audio indisponible : {e}")

        # Sources
        if result.get("sources"):
            st.markdown("#### Sources")
            tags = " ".join(f'<span class="source-tag">{s}</span>' for s in result["sources"])
            st.markdown(tags, unsafe_allow_html=True)

        # Detailed tabs
        st.markdown("")
        detail_tab1, detail_tab2 = st.tabs(["Analyse juridique", "Validation"])

        with detail_tab1:
            st.markdown(result["legal_analysis"])

        with detail_tab2:
            st.markdown(result["validation"])


def page_contracts():
    st.markdown(
        '<div class="app-header"><h1>Contrats</h1>'
        "<p>Gerez et indexez vos documents contractuels</p></div>",
        unsafe_allow_html=True,
    )

    # Upload
    st.markdown("#### Deposer un contrat")
    uploaded = st.file_uploader(
        "fichier",
        type=["pdf", "html", "htm"],
        label_visibility="collapsed",
    )
    if uploaded and st.button("Uploader et indexer", type="primary"):
        with st.spinner("Indexation en cours..."):
            files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
            try:
                resp = requests.post(f"{API_URL}/upload-contract", files=files, timeout=120)
                if resp.status_code == 200:
                    st.success(f"**{uploaded.name}** indexe avec succes.")
                else:
                    st.error("Erreur lors de l'upload.")
            except Exception as e:
                st.error(str(e))

    # List
    st.markdown("#### Documents disponibles")
    try:
        resp = requests.get(f"{API_URL}/contracts", timeout=5)
        contracts = resp.json().get("contracts", [])
        if contracts:
            for c in contracts:
                st.markdown(f'<div class="contract-item">{c}</div>', unsafe_allow_html=True)
        else:
            st.markdown("Aucun contrat disponible.")
    except Exception:
        st.error("Backend non disponible.")


if __name__ == "__main__":
    main()

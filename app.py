import streamlit as st
import google.generativeai as genai
import re

# Configure page
st.set_page_config(page_title="Traduci il tuo testo dal Latino!", layout="wide")




def extract_all_tagged_content(text):
    tags = {
        'traduzione': '',
        'analisi': '',
        'testo_latino': '',
        'dizionario_latino_italiano': '',
        'manuale_grammatica_italiana': ''
    }
    
    for tag in tags.keys():
        # Rimuovi le parentesi graffe dal pattern
        pattern = f'<{tag}>(.*?)</{tag}>'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            tags[tag] = match.group(1).strip()
    
    return tags


def initialize_gemini(api_key, system_prompt):
    try:
        genai.configure(api_key=api_key)
        
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 1,
            "max_output_tokens": 8192,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            system_instruction=system_prompt,
        )
        
        return model.start_chat(history=[])
    except Exception as e:
        st.error(f"Errore nell'inizializzazione di Gemini: {str(e)}")
        return None

def show_system_prompt(system_prompt):
    with st.sidebar:
        st.subheader("Configurazione del Traduttore")
        with st.expander("Mostra configurazione"):
            st.code(system_prompt, language="text")

def main():
    st.title("🏛️ Traduttore Latino-Italiano Avanzato")
    st.markdown("Traduci i tuoi testi dal Latino all'Italiano con l'aiuto dell'intelligenza artificiale")
    
    system_prompt = load_system_prompt()
    
    with st.sidebar:
        st.header("Configurazione")
        api_key = st.text_input(
            "Inserisci la tua Google Gemini API Key",
            type="password",
            help="Necessaria per utilizzare il servizio di traduzione"
        )
        
        st.markdown("[Ottieni la tua API Key](https://makersuite.google.com/app/apikey)")
        show_system_prompt(system_prompt)
    
    if not api_key:
        st.warning("⚠️ Inserisci la tua API Key per iniziare a tradurre")
        return
    
    if ('current_api_key' not in st.session_state or 
        st.session_state.current_api_key != api_key or 
        'system_prompt' not in st.session_state or 
        st.session_state.system_prompt != system_prompt):
        
        st.session_state.chat_session = initialize_gemini(api_key, system_prompt)
        st.session_state.current_api_key = api_key
        st.session_state.system_prompt = system_prompt
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Testo Latino")
        latin_text = st.text_area(
            "Inserisci il testo latino da tradurre (massimo 750 caratteri)",
            height=300,
            max_chars=750
        )
        
        # Add a character counter
        remaining_chars = 750 - len(latin_text)
        st.caption(f"Caratteri rimanenti: {remaining_chars}")
        
    with col2:
        st.subheader("Traduzione Italiana")
        translation_placeholder = st.empty()
    
    if st.button("🔄 Traduci"):
        if st.session_state.chat_session and latin_text:
            try:
                full_response = ""
                current_tags = {}
                response_container = st.container()
                
                with response_container:
                    progress_text = st.empty()
                    translation_area = st.empty()
                    
                    for chunk in st.session_state.chat_session.send_message(latin_text, stream=True):
                        full_response += chunk.text
                        current_tags = extract_all_tagged_content(full_response)
                        translation_area.markdown(current_tags['traduzione'] + " ") # Cambiato da 'translation' a 'traduzione'
                        progress_text.text("Traduzione in corso...")
                    
                    progress_text.empty()
                    translation_area.markdown(current_tags['traduzione']) # Cambiato da 'translation' a 'traduzione'
                    
                    # Create expandable sections for each tag
                    with st.expander("📚 Analisi Grammaticale"):
                        if current_tags['analisi']: # Cambiato da 'analysis' a 'analisi'
                            st.markdown(current_tags['analisi'])

            except Exception as e:
                st.error(f"Errore durante la traduzione: {str(e)}")
    else:
        st.error("Inserisci un testo da tradurre e verifica la tua API Key")

def load_system_prompt():
    default_prompt = """You are a Latin to Italian translator with expertise in both languages' grammar and vocabulary. Your task is to translate Latin text into Italian, explain translation decisions, and analyze Latin grammar.

Present your work in the following format:

<translation>
[Italian translation]
</translation>

<analysis>
[Grammatical analysis and translation decisions]
</analysis>

<latin_italian_dictionary>
[Relevant dictionary entries]
</latin_italian_dictionary>

<latin_grammar_manual>
[Relevant Latin grammar explanations]
</latin_grammar_manual>

<italian_grammar_manual>
[Relevant Italian grammar explanations]
</italian_grammar_manual>"""
    
    try:
        with open('prompt.txt', 'r', encoding='utf-8') as file:
            system_prompt = file.read().strip()
            return system_prompt if system_prompt else default_prompt
    except FileNotFoundError:
        return default_prompt

if __name__ == "__main__":
    main()

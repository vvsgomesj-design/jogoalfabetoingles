import streamlit as st
import random
import speech_recognition as sr
import io
import string

# Configuração da página e injeção de estilos de festa animados
st.set_page_config(page_title="Jogo da Velha de Alfabeto em Inglês", layout="centered")

# Estilos CSS Avançados para Animações Festivas, Notas Dançantes e Fogos de Artifício
st.markdown("""
<style>
    /* Estilo do Título Festivo */
    .festive-title {
        text-align: center;
        font-family: 'Comic Sans MS', cursive, sans-serif;
        background: linear-gradient(45deg, #ff5e62, #ff9966, #ffd966, #66ff99, #66b3ff, #9966ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 50px;
        font-weight: bold;
        animation: title-glow 3s ease-in-out infinite alternate;
    }
    @keyframes title-glow {
        0% { filter: drop-shadow(0 0 5px rgba(255,94,98,0.5)); }
        100% { filter: drop-shadow(0 0 20px rgba(255,153,102,0.8)); }
    }

    /* Caixa de Captura de Som Musical */
    .voice-box {
        background: linear-gradient(135deg, #2e0854, #4a148c);
        border: 5px solid #ff9966;
        border-radius: 20px;
        padding: 25px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Notas Musicais Dançantes */
    .musical-note {
        position: absolute;
        font-size: 30px;
        bottom: -50px;
        animation: float-up 4s linear infinite;
        opacity: 0;
    }
    @keyframes float-up {
        0% { transform: translateY(0) translateX(0) rotate(0deg); opacity: 0; }
        10% { opacity: 0.8; }
        90% { opacity: 0.8; }
        100% { transform: translateY(-300px) translateX(50px) rotate(360deg); opacity: 0; }
    }

    /* Letras Animadas do Tabuleiro (Movimento Suave de Dança) */
    .letter-box {
        text-align: center; 
        font-size: 42px; 
        font-weight: bold; 
        font-family: 'Comic Sans MS', sans-serif;
        height: 100px;
        line-height: 100px;
        animation: dance-letter 2.5s ease-in-out infinite alternate;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        display: inline-block;
        width: 100%;
    }
    @keyframes dance-letter {
        0% { transform: scale(1) rotate(-4deg) translateY(0px); }
        50% { transform: scale(1.05) rotate(0deg) translateY(-3px); }
        100% { transform: scale(1) rotate(4deg) translateY(0px); }
    }

    /* Fogos de Artifício em Loops */
    .pyro > .before, .pyro > .after {
        position: fixed;
        width: 7px; height: 7px;
        border-radius: 50%;
        box-shadow: 0 0 #fff, 0 0 #fff, 0 0 #fff, 0 0 #fff, 0 0 #fff, 0 0 #fff, 0 0 #fff, 0 0 #fff;
        animation: 1s bang ease-out infinite alternate, 1s gravity ease-in infinite alternate, 5s position linear infinite;
    }
    .pyro > .after {
        animation-delay: 1.25s, 1.25s, 1.25s;
        animation-duration: 1.25s, 1.25s, 6.25s;
    }
    @keyframes bang {
        to { box-shadow: -70px -115px #ff5e62, 120px -215px #ff9966, -150px -50px #ffd966, 140px -80px #66ff99, -90px -270px #66b3ff, 200px -120px #9966ff, -180px -220px #ff66cc, 60px -310px #33ffff; width: 5px; height: 5px; }
    }
    @keyframes gravity { to { transform: translateY(120px); opacity: 0; } }
    @keyframes position {
        0%, 100% { top: 30%; left: 30%; }
        25% { top: 10%; left: 70%; }
        50% { top: 40%; left: 50%; }
        75% { top: 20%; left: 15%; }
    }
</style>
""", unsafe_allow_html=True)


## --- LÓGICA DO JOGO ---
def check_winner(board, player):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], 
        [0, 3, 6], [1, 4, 7], [2, 5, 8], 
        [0, 4, 8], [2, 4, 6]             
    ]
    return any(all(board[i] == player for i in condition) for condition in win_conditions)

def get_computer_move(board):
    empty_indices = [i for i, x in enumerate(board) if x not in ['X', 'O']]
    return random.choice(empty_indices) if empty_indices else None

def transcribe_audio_en(audio_bytes):
    r = sr.Recognizer()
    try:
        audio_io = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_io) as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="en-US")
            return text.upper().strip()
    except sr.UnknownValueError:
        return "ERROR_UNKNOWN_VALUE"
    except Exception as e:
        return f"ERROR_SYS_{str(e).upper()}"

# Cores vibrantes de estilo cartoon para as letras
COLOR_MAP = {
    0: "#ff3366", 1: "#ff9933", 2: "#33cc33",
    3: "#3399ff", 4: "#b366ff", 5: "#ff33cc",
    6: "#00ecff", 7: "#ffcc00", 8: "#ff5e62"
}

## --- DICIONÁRIO FONÉTICO CALIBRADO ---
PRONUNCIATION_KEY = {
    "A": ["A", "EI", "HEY", "AY"], "B": ["B", "BE", "BEE"], "C": ["C", "SEE", "SEA", "SI"],
    "D": ["D", "DEE", "DI"], "E": ["E", "HE", "I"], "F": ["F", "EF"], "G": ["G", "GEE", "DJI"],
    "H": ["H", "AITCH", "AGE", "8", "EITCH"], "I": ["I", "EYE", "HIGH", "AI"], "J": ["J", "JAY"],
    "K": ["K", "KAY"], "L": ["L", "EL"], 
    "M": ["M", "EM", "AM", "THEM", "HIM", "UM", "N", "EN"], 
    "N": ["N", "EN", "AN", "AND", "IN", "END", "M", "EM"], 
    "O": ["O", "OH", "OU"], "P": ["P", "PEE", "PI"], "Q": ["Q", "CUE", "QUEUE"], 
    "R": ["R", "ARE", "AR"], "S": ["S", "ESS", "AS"], "T": ["T", "TEE", "TEA"], 
    "U": ["U", "YOU"], "V": ["V", "VEE"], "W": ["W", "DOUBLE U"], "X": ["X", "EX"], 
    "Y": ["Y", "WHY"], "Z": ["Z", "ZEE", "ZED"]
}

## --- ESTADO INICIAL ---
if 'board' not in st.session_state:
    st.session_state.winner = None
    st.session_state.selected_letter = None  
    st.session_state.msg = "🎈 Clique em uma Letra Dançante para começar a diversão!"
    st.session_state.last_heard = ""
    
    # Sorteia as letras APENAS UMA VEZ no início do jogo inteiro
    alfabeto = list(string.ascii_uppercase)
    letras_partida = random.sample(alfabeto, 9)
    st.session_state.board = letras_partida

## --- INTERFACE ---
st.markdown('<div class="festive-title">🎪 Magic English Tic-Tac-Toe 🎶</div>', unsafe_allow_html=True)

# Painel de vitória com Fogos de Artifício
if st.session_state.winner == "Student":
    st.markdown('<div class="pyro"><div class="before"></div><div class="after"></div></div>', unsafe_allow_html=True)
    st.balloons()

st.markdown("""
<div style='background-color: #fff9e6; padding: 12px; border-radius: 12px; border-left: 5px solid #ffcc00; font-family: sans-serif; text-align: center;'>
🎯 <b>Regra do Jogo da Velha:</b> Conquiste <b>Círculos (⭕)</b> acertando a pronúncia em inglês! As letras ficam fixas até o final desta rodada!
</div>
""", unsafe_allow_html=True)

st.write("")
st.subheader(st.session_state.msg)

## --- TABULEIRO TRADICIONAL COM HASTES FIXAS ---
linhas_indices = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]

for r_idx, linha in enumerate(linhas_indices):
    cols = st.columns(3)  
    for c_idx, i in enumerate(linha):
        with cols[c_idx]:
            content = st.session_state.board[i]
            
            # Hastes tradicionais pretas e espessas do Jogo da Velha
            border_style = "border-bottom: 6px solid #2c3e50;" if r_idx < 2 else ""
            if c_idx < 2:
                border_style += " border-right: 6px solid #2c3e50;"
                
            if content in ['O', 'X']:
                symbol = "<span style='color: #2ecc71; font-size:60px;'>⭕</span>" if content == 'O' else "<span style='color: #e74c3c; font-size:60px;'>❌</span>"
                st.markdown(f"<div style='text-align: center; height: 110px; line-height: 110px; {border_style}'>{symbol}</div>", unsafe_allow_html=True)
            else:
                # Letras coloridas e festivas que DANÇAM
                cor_letra = COLOR_MAP[i]
                st.markdown(f"<div class='letter-box' style='color: {cor_letra}; {border_style}'>{content}</div>", unsafe_allow_html=True)
                
                if not st.session_state.winner and st.session_state.selected_letter is None:
                    if st.button(f"✨ {content} ✨", key=f"btn_{content}_{i}", use_container_width=True):
                        st.session_state.selected_letter = content
                        st.session_state.msg = f"🎙️ Pronto! Vamos conquistar a Letra {content}!"
                        st.rerun()
                st.markdown("<div style='margin-top: 2px;'></div>", unsafe_allow_html=True)

st.write("")

## --- CAIXA DE CAPTURA DE SOM COM NOTAS MUSICAIS DANÇANTES ---
if st.session_state.selected_letter and not st.session_state.winner:
    letra_alvo = st.session_state.selected_letter
    
    st.markdown(f"""
    <div class="voice-box">
        <h3 style='color: white; text-align: center; margin-top:0;'>📻 VOICE CAPTURE BOX</h3>
        <p style='color: #ffcc00; text-align: center; font-size: 18px;'>Grave sua voz dizendo a letra: <b>{letra_alvo}</b></p>
        <div class="musical-note" style="left: 15%; animation-delay: 0s;">🎵</div>
        <div class="musical-note" style="left: 45%; animation-delay: 1.5s; font-size: 40px;">𝄞</div>
        <div class="musical-note" style="left: 75%; animation-delay: 0.7s;">🎶</div>
        <div class="musical-note" style="left: 85%; animation-delay: 2.2s;">♪</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    audio_file = st.audio_input("Grave e pare para carregar a fita mágica")
    
    if audio_file is not None:
        audio_bytes = audio_file.read()
        
        if st.button("🎉 VALIDAR MINHA PRONÚNCIA!", type="primary", use_container_width=True):
            with st.spinner("A Clave de sol está escutando sua fonética..."):
                texto_falado = transcribe_audio_en(audio_bytes)
                
            if texto_falado and not texto_falado.startswith("ERROR_"):
                st.session_state.last_heard = texto_falado
                fonemas_aceitos = PRONUNCIATION_KEY.get(letra_alvo, [letra_alvo])
                acertou = False
                
                for palavra in texto_falado.split():
                    if palavra == letra_alvo or palavra in fonemas_aceitos:
                        acertou = True
                        break
                
                idx = st.session_state.board.index(letra_alvo)
                
                if acertou:
                    st.toast("Fantástico! Pronúncia perfeita!", icon="✅")
                    st.session_state.board[idx] = 'O'  # Marca o Círculo ⭕
                    
                    if check_winner(st.session_state.board, 'O'):
                        st.session_state.winner = "Student"
                        st.session_state.msg = "🎉 ESPETACULAR! VOCÊ GANHOU O JOGO DO ALFABETO!"
                    else:
                        # Computador faz o movimento dele logo após o seu acerto
                        move_comp = get_computer_move(st.session_state.board)
                        if move_comp is not None:
                            st.session_state.board[move_comp] = 'X'  # Marca o Xis ❌
                            if check_winner(st.session_state.board, 'X'):
                                st.session_state.winner = "Computer"
                                st.session_state.msg = "🤖 O robô marcou uma linha! Boa tentativa!"
                        
                        if not st.session_state.winner:
                            st.session_state.msg = f"Muito bem! Letra '{letra_alvo}' garantida! Sua vez novamente."
                else:
                    st.toast("Quase lá! Tente na próxima rodada.", icon="❌")
                    st.session_state.msg = f"Ouvimos '{texto_falado}' para a letra '{letra_alvo}'. O robô aproveitou seu erro e jogou!"
                    
                    # Se errar, o computador joga no seu lugar
                    move_comp = get_computer_move(st.session_state.board)
                    if move_comp is not None:
                        st.session_state.board[move_comp] = 'X'
                        if check_winner(st.session_state.board, 'X'):
                            st.session_state.winner = "Computer"
                            st.session_state.msg = "🤖 O robô fechou três símbolos primeiro!"
                
                # Verifica se deu velha
                if not st.session_state.winner and get_computer_move(st.session_state.board) is None:
                    st.session_state.winner = "Tie"
                    st.session_state.msg = "🤝 Empate! Deu velha no tabuleiro."

                st.session_state.selected_letter = None
                st.rerun()
            else:
                st.error("A caixa de som mágica não detectou áudio limpo. Chegue mais perto!")

if st.session_state.last_heard:
    st.info(f"📻 O computador ouviu você falar isso: **'{st.session_state.last_heard}'**")

# Botão de reinício festivo (Troca as letras ao resetar a rodada)
if st.session_state.winner:
    st.success(st.session_state.msg)
    if st.button("🎪 Iniciar Nova Rodada (Mudar Letras)", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

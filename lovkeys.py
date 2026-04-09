import streamlit as st
import requests
import json
import google.generativeai as genai
import time
import re
import streamlit.components.v1 as components

# ============================================================
# 🔑 LOVKEYS PROSPECTOR — CONFIG PRINCIPAL
# ============================================================
# ⚠️ TUDO QUE VOCÊ QUER EDITAR ESTÁ AQUI EM CIMA.
# Não precisa mexer em mais nada abaixo dessa seção.
# ============================================================

CONFIG = {
    # ---- IDENTIDADE DA MARCA ----
    "MARCA": "LovKeys",
    "SENDER_NAME": "Renê",
    "OFFER_SHORT": "acesso ilimitado ao Lovable",
    "OFFER_PRICE": "R$ 147",
    "FREE_TRIAL": "10 minutos grátis",

    # ---- PLANILHA ----
    "SPREADSHEET_URL": "https://docs.google.com/spreadsheets/d/1ewfk6D7P3DQwXpoKdWySpmk70RBJw-Kwxv6WPK9_4wY/edit?gid=0#gid=0",
    "SHEET_NAME_CRM": "LEADS_LOVKEYS",
    "SHEET_NAME_BLACKLIST": "BLACKLIST_LOVKEYS",
    "WEBHOOK_URL": "https://script.google.com/macros/s/AKfycbzR66Auf9Wl91Nw_dERjuLyemQF-CQMVGAMqcZy1plwnSGCZW8-TfaxGi2E9XopUd1b/exec",  # ← cola aqui depois de publicar o Apps Script

    # ---- APIs (pode deixar em branco e colar no menu lateral) ----
    "API_SERPER_DEFAULT": "",
    "API_GEMINI_DEFAULT": "",

    # ---- PAGE META ----
    "PAGE_TITLE": "LovKeys Prospector",
    "PAGE_ICON": "🔑",
    "APP_SUBTITLE": "Encontre builders e empreendedores travados no Lovable. Ofereça a chave.",

    # ============================================================
    # 🧠 PROMPT DA IA — ICP DUPLO (BUILDER + EMPREENDEDOR)
    # ============================================================
    "ICP_PROMPT": """
Você atua como Renê, fundador da LovKeys, especialista em qualificar leads que vão comprar acesso ilimitado ao Lovable.

A LovKeys vende chaves de acesso ilimitado ao Lovable (plataforma de criação de SaaS) por R$ 147/mês, muito abaixo do plano oficial em dólar.

🎯 O seu ICP tem DOIS PERFIS que você precisa saber diferenciar:

═══════════════════════════════════════
PERFIL A — BUILDER QUENTE
═══════════════════════════════════════
Quem: devs iniciantes, no-coders, pessoas que já postam sobre Lovable, Bolt, Cursor, v0, Replit, Windsurf, Claude, ChatGPT pra código, IA generativa, construção de SaaS, MVP, micro-SaaS, indie hacker, vibe coding.
Sinais: bio menciona "dev", "builder", "no-code", "criando meu SaaS", "tech", "founder", emojis de código (⌨️ 💻 🚀 🧠), posts mostrando tela de editor, prompts, projetos em construção.
Por que converte: JÁ sabe o que é Lovable. Só precisa da chave. Ciclo curto. Converte direto na chave de R$147.

═══════════════════════════════════════
PERFIL B — EMPREENDEDOR COM IDEIA TRAVADA
═══════════════════════════════════════
Quem: dono de pequeno/médio negócio, infoprodutor, coach, consultor, mentor, dono de loja/agência/serviço, que fala em "automatizar", "criar meu sistema", "ter meu app", "cansado de pagar ferramenta cara", "queria um CRM do meu jeito".
Sinais: bio de empresário/empreendedor, posts sobre gestão, vendas, equipe, dores de operação, reclamações de software caro, menção a planilhas infinitas, "preciso de um sistema".
Por que converte: não sabe codar, mas tem ideia e dinheiro. Converte na Sessão Fundação (R$297) mais do que na chave pura.

═══════════════════════════════════════
CRITÉRIOS DE APROVAÇÃO
═══════════════════════════════════════
1. Perfil Privado: se "This account is private" ou "Conta privada", REPROVAR imediatamente.
2. Seguidores: ideal entre 500 e 50k. Acima de 100k REPROVAR (geralmente influencer, não converte).
3. Bio completamente vazia ou genérica sem nenhum sinal dos perfis A ou B: REPROVAR.
4. Perfil de empresa grande, ONG, político, meme, fanpage, celebridade: REPROVAR.
5. Perfil de concorrente (outro revendedor de chave, vendedor de curso de IA): REPROVAR.
6. Se tiver QUALQUER sinal claro de Perfil A ou Perfil B: APROVAR.
*Atenção*: na dúvida entre aprovar ou reprovar, APROVE.

{treinamento_extra}

Resumo do Google para a conta {arroba}: "{snippet_google}"

═══════════════════════════════════════
SUA TAREFA
═══════════════════════════════════════
1. Descubra o Nome do lead (primeiro nome apenas).
2. Identifique se é PERFIL_A (builder) ou PERFIL_B (empreendedor).
3. Identifique a ÁREA ESPECÍFICA do conteúdo dele (ex: "criar um CRM pra clínica", "SaaS de delivery", "automação de WhatsApp", "app de agendamento").
4. Aprove ou reprove.
5. Se aprovado, gere o SCRIPT_1 seguindo EXATAMENTE o modelo abaixo.

🚨 REGRAS EXTREMAS PARA O SCRIPT:
1. Mantenha as QUEBRAS DE LINHA EXATAMENTE como no modelo. No JSON use "\\n\\n" para parágrafos.
2. Substitua [NOME] pelo primeiro nome do lead. Se não identificar o nome, use apenas "Opa" no lugar de "Fala, [NOME]".
3. Substitua [ÁREA ESPECÍFICA] por algo concreto que você viu no perfil dele (ex: "teu projeto de app de delivery", "o sistema de gestão que você tá pensando em criar", "teus experimentos com no-code"). NUNCA deixe genérico tipo "teu conteúdo".
4. É PROIBIDO alterar o restante do texto do script.
5. Para PERFIL_A (builder), mantenha o script como está (já é otimizado pra ele).
6. Para PERFIL_B (empreendedor), substitua "nós devs sofremos muito" por "muita gente que quer criar um sistema próprio sofre com isso".

═══════════════════════════════════════
MODELO DO SCRIPT (PERFIL_A — BUILDER):
═══════════════════════════════════════
Fala, [NOME]! Tudo bem?

Tô acompanhando teu conteúdo sobre [ÁREA ESPECÍFICA] e curti demais a pegada que você tá tomando.

Posso ser direto contigo? Vi que você tá mexendo com Lovable (ou tá de olho) e tem um detalhe que nós devs sofremos muito: o plano gratuito trava em 5 mensagens por dia, e o pago sai R$120+ por mês em dólar.

Isso faz a maioria travar o projeto no meio.

Eu tenho aqui acesso ilimitado ao Lovable por período, custo MUITO abaixo do oficial. E antes de te avançar, quero te oferecer 10 minutos grátis pra você testar agora e ver com os próprios olhos se roda igual falei, sem compromisso, sem pegadinha. Só quero que você teste.

Pode ser?

═══════════════════════════════════════
MODELO DO SCRIPT (PERFIL_B — EMPREENDEDOR):
═══════════════════════════════════════
Fala, [NOME]! Tudo bem?

Tô acompanhando teu conteúdo sobre [ÁREA ESPECÍFICA] e curti demais a pegada que você tá tomando.

Posso ser direto contigo? Vi que você tá buscando criar teu próprio sistema (ou tá de olho) e tem um detalhe que muita gente que quer criar um sistema próprio sofre com isso: as ferramentas tipo Lovable travam em 5 mensagens por dia no plano free, e o pago sai R$120+ por mês em dólar.

Isso faz a maioria travar o projeto no meio.

Eu tenho aqui acesso ilimitado ao Lovable por período, custo MUITO abaixo do oficial. E antes de te avançar, quero te oferecer 10 minutos grátis pra você testar agora e ver com os próprios olhos se roda igual falei, sem compromisso, sem pegadinha. Só quero que você teste.

Pode ser?

═══════════════════════════════════════

Retorne APENAS um objeto JSON válido (sem marcação markdown), com esta estrutura:
{{
  "status": "APROVADO" ou "REPROVADO",
  "perfil": "PERFIL_A" ou "PERFIL_B" ou "N/A",
  "nome_lead": "primeiro nome ou vazio",
  "motivo": "justificativa curta",
  "script_1": "texto completo do script ou vazio"
}}
""",

    # ============================================================
    # 📨 SCRIPTS DE FOLLOW-UP (fixos, usados manualmente ou pela planilha)
    # ============================================================
    "SCRIPT_FOLLOWUP_2D": """Boa tarde, [NOME]! Tudo bem? Espero que sim.

Você chegou a ver minha mensagem? O que me diz? 🙂""",

    "SCRIPT_INJECAO_4D": """Opa, [NOME], tudo certo por aí?

Tô retomando contato porque pelo teu perfil deu pra ver que você é um cara que tá buildando de verdade, não é curioso de passagem. Por isso acho que o trial de 10 min do Lovable ilimitado ia te servir muito.

Mas vem sendo meio difícil a gente se falar, então só queria saber: você tem interesse em testar ou posso seguir conversando com outras pessoas? Sem ressentimento nenhum dos dois lados.

Abraço!""",
}

# ============================================================
# 🛑 A PARTIR DAQUI É LÓGICA — SÓ MEXA SE SOUBER O QUE FAZ
# ============================================================

st.set_page_config(page_title=CONFIG["PAGE_TITLE"], page_icon=CONFIG["PAGE_ICON"], layout="wide")

# Puxa secrets se existirem
try:
    CHAVE_SERPER_PADRAO = st.secrets.get("CHAVE_SERPER", CONFIG["API_SERPER_DEFAULT"])
    CHAVE_GEMINI_PADRAO = st.secrets.get("CHAVE_GEMINI", CONFIG["API_GEMINI_DEFAULT"])
    URL_WEBHOOK_PLANILHA = st.secrets.get("WEBHOOK_PLANILHA", CONFIG["WEBHOOK_URL"])
except Exception:
    CHAVE_SERPER_PADRAO = CONFIG["API_SERPER_DEFAULT"]
    CHAVE_GEMINI_PADRAO = CONFIG["API_GEMINI_DEFAULT"]
    URL_WEBHOOK_PLANILHA = CONFIG["WEBHOOK_URL"]

# --- INICIALIZANDO MEMÓRIAS ---
defaults_session = {
    "historico_leads": [],
    "ultima_busca_nicho": "",
    "ultima_busca_hashtag": "",
    "ultima_busca_local": "",
    "ultima_busca_negativos": "",
    "ultima_busca_frase": "",
    "proxima_pagina": 1,
    "leads_aprovados_tela": [],
    "leads_reprovados_tela": [],
    "blacklist_arrobas": set(),
    "bons_exemplos": [],
    "maus_exemplos": [],
    "feedbacks_dados": [],
}
for k, v in defaults_session.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- FUNÇÕES DE MEMÓRIA PERMANENTE (PLANILHA) ---
def puxar_memoria_ia():
    webhook = st.session_state.get("url_webhook", URL_WEBHOOK_PLANILHA)
    if not webhook:
        return {"bons": [], "maus": []}
    try:
        res = requests.get(f"{webhook}?acao=memoria")
        if res.ok:
            return res.json()
    except Exception:
        pass
    return {"bons": [], "maus": []}

def salvar_feedback_planilha(arroba, feedback_tipo, bio):
    webhook = st.session_state.get("url_webhook", URL_WEBHOOK_PLANILHA)
    if not webhook:
        return
    dados = {
        "tipo": "feedback",
        "sheet_name": "MemoriaIA",
        "arroba": arroba,
        "feedback": feedback_tipo,
        "bio": bio,
    }
    try:
        requests.post(webhook, json=dados)
    except Exception:
        pass

if "memoria_carregada" not in st.session_state:
    if URL_WEBHOOK_PLANILHA:
        with st.spinner("A carregar o cérebro da IA da Nuvem..."):
            memoria_nuvem = puxar_memoria_ia()
            st.session_state["bons_exemplos"] = memoria_nuvem.get("bons", [])
            st.session_state["maus_exemplos"] = memoria_nuvem.get("maus", [])
    st.session_state["memoria_carregada"] = True

# --- CABEÇALHO ---
col_titulo, col_botoes = st.columns([3, 1])
with col_titulo:
    st.title(f"{CONFIG['PAGE_ICON']} {CONFIG['PAGE_TITLE']}")
    st.markdown(CONFIG["APP_SUBTITLE"])
with col_botoes:
    st.write("")
    st.write("")
    st.link_button("📊 Planilha LovKeys", CONFIG["SPREADSHEET_URL"], use_container_width=True)

# --- MENU LATERAL ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")

    with st.expander("🎯 Destino na Planilha (CRM)", expanded=True):
        if "url_webhook" not in st.session_state:
            st.session_state["url_webhook"] = URL_WEBHOOK_PLANILHA
        if "nome_aba" not in st.session_state:
            st.session_state["nome_aba"] = CONFIG["SHEET_NAME_CRM"]

        url_webhook = st.text_input("URL do Webhook:", type="password", value=st.session_state["url_webhook"])
        nome_aba = st.text_input("Aba de Entrada (CRM):", value=st.session_state["nome_aba"])

        st.session_state["url_webhook"] = url_webhook
        st.session_state["nome_aba"] = nome_aba

    with st.expander("🚫 Gerenciar Blacklist", expanded=False):
        if "aba_blacklist" not in st.session_state:
            st.session_state["aba_blacklist"] = CONFIG["SHEET_NAME_BLACKLIST"]

        aba_blacklist = st.text_input("Aba da Blacklist:", value=st.session_state["aba_blacklist"])
        st.session_state["aba_blacklist"] = aba_blacklist

        st.markdown("<small><i>Arrobas manuais avulsos:</i></small>", unsafe_allow_html=True)
        blacklist_texto = st.text_area("Colar arrobas:", height=60, placeholder="@joao\n@maria")
        blacklist_manual = {
            a.strip().replace("https://www.instagram.com/", "@").replace("/", "")
            for a in blacklist_texto.split("\n") if a.strip()
        }

    with st.expander("🔑 Chaves de API", expanded=False):
        if "api_key_serper" not in st.session_state:
            st.session_state["api_key_serper"] = CHAVE_SERPER_PADRAO
        if "api_key_gemini" not in st.session_state:
            st.session_state["api_key_gemini"] = CHAVE_GEMINI_PADRAO

        api_key_serper = st.text_input("API Key do Serper:", type="password", value=st.session_state["api_key_serper"])
        api_key_gemini = st.text_input("API Key do Gemini:", type="password", value=st.session_state["api_key_gemini"])

        st.session_state["api_key_serper"] = api_key_serper
        st.session_state["api_key_gemini"] = api_key_gemini

    st.divider()
    st.caption(f"🧠 IA na memória: {len(st.session_state['bons_exemplos'])} likes / {len(st.session_state['maus_exemplos'])} dislikes.")
    st.caption(f"📦 Marca: **{CONFIG['MARCA']}** · Vendedor: **{CONFIG['SENDER_NAME']}**")

# --- ENVIAR PARA GOOGLE SHEETS ---
def enviar_lead_para_planilha(lead_dados):
    webhook = st.session_state["url_webhook"]
    if not webhook:
        st.error("Configure a URL do Webhook na barra lateral primeiro!")
        return False
    try:
        resposta = requests.post(webhook, json=lead_dados)
        if resposta.ok and "Sucesso" in resposta.text:
            return True
        else:
            st.error(f"Erro na Planilha: {resposta.text}")
            return False
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return False

# --- PUXAR BLACKLIST ---
def puxar_blacklist_automatica():
    webhook = st.session_state["url_webhook"]
    aba = st.session_state["aba_blacklist"]
    if not webhook or not aba:
        return set()
    try:
        resposta = requests.get(f"{webhook}?aba={aba}")
        if resposta.ok:
            dados = resposta.json()
            if "leads" in dados:
                lista_suja = dados["leads"]
                return {
                    str(a).strip().replace("https://www.instagram.com/", "@").replace("/", "")
                    for a in lista_suja if str(a).strip()
                }
    except Exception:
        pass
    return set()

# --- MOTOR DE GARIMPO ---
def garimpar_perfis_google(profissao, hashtag, localizacao, termos_negativos, frase_exata, qtd, api_serper, pagina_inicial=1):
    url = "https://google.serper.dev/search"
    query = 'site:instagram.com -inurl:p -inurl:reel -inurl:explore -inurl:tags'

    if profissao:
        query += f' "{profissao}"'
    if hashtag:
        hash_term = hashtag if hashtag.startswith("#") else f"#{hashtag}"
        query += f' {hash_term}'
    if localizacao:
        query += f' "{localizacao}"'
    if frase_exata:
        query += f' intext:"{frase_exata}"'
    if termos_negativos:
        for negativo in [t.strip() for t in termos_negativos.split(",") if t.strip()]:
            query += f' -{negativo}'

    arrobas_encontrados = []
    palavras_ignoradas = ['p', 'reel', 'reels', 'explore', 'tags', 'stories', 'tv', 'channel', 'about', 'legal', 'directory']

    barra_busca = st.progress(0, text="Sincronizando Blacklist com a Planilha...")
    blacklist_da_nuvem = puxar_blacklist_automatica()
    blacklist_total = st.session_state["blacklist_arrobas"].union(blacklist_manual).union(blacklist_da_nuvem)

    paginas_necessarias = (qtd // 10) + 4
    ultima_pagina_pesquisada = pagina_inicial

    for pagina in range(pagina_inicial, pagina_inicial + paginas_necessarias):
        ultima_pagina_pesquisada = pagina
        if len(arrobas_encontrados) >= qtd:
            break

        progresso = min((pagina - pagina_inicial) / paginas_necessarias, 1.0)
        barra_busca.progress(progresso, text=f"Lendo página {pagina} do Google...")

        payload = json.dumps({"q": query, "page": pagina, "num": 10})
        headers = {'X-API-KEY': api_serper, 'Content-Type': 'application/json'}

        try:
            res = requests.post(url, headers=headers, data=payload)
            if not res.ok:
                st.error(f"Erro na API do Serper: {res.text}")
                break

            dados = res.json()
            organicos = dados.get("organic", [])
            if not organicos:
                break

            for item in organicos:
                link = item.get("link", "")
                match = re.search(r'instagram\.com/([^/?]+)', link)
                if match:
                    username = match.group(1).strip()
                    if username.lower() not in palavras_ignoradas:
                        arroba_formatado = f"@{username}"
                        if arroba_formatado not in blacklist_total and arroba_formatado not in arrobas_encontrados:
                            arrobas_encontrados.append(arroba_formatado)
                        if len(arrobas_encontrados) >= qtd:
                            break
        except Exception:
            break

        time.sleep(0.5)

    barra_busca.empty()
    return arrobas_encontrados[:qtd], ultima_pagina_pesquisada + 1

# --- CÉREBRO DA IA (ICP LOVKEYS) ---
def analisar_e_gerar_script(arroba, snippet_google, api_gemini):
    try:
        genai.configure(api_key=api_gemini)
        modelos_disponiveis = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]

        if not modelos_disponiveis:
            return {"status": "ERRO", "motivo": "Sem acesso à IA."}

        modelo_escolhido = modelos_disponiveis[0]
        for nome in modelos_disponiveis:
            if 'flash' in nome:
                modelo_escolhido = nome

        modelo = genai.GenerativeModel(modelo_escolhido.replace("models/", ""))

        treinamento_extra = ""
        if st.session_state["bons_exemplos"]:
            bons = "\n- ".join(st.session_state["bons_exemplos"][-3:])
            treinamento_extra += f"\n\n🚨 O usuário GOSTOU destes perfis no passado. APROVE parecidos:\n- {bons}"
        if st.session_state["maus_exemplos"]:
            maus = "\n- ".join(st.session_state["maus_exemplos"][-3:])
            treinamento_extra += f"\n\n🚨 O usuário REPROVOU estes perfis no passado. REPROVE parecidos:\n- {maus}"

        prompt = CONFIG["ICP_PROMPT"].format(
            treinamento_extra=treinamento_extra,
            arroba=arroba,
            snippet_google=snippet_google,
        )

        resposta = modelo.generate_content(prompt)
        texto_json = resposta.text.replace("```json", "").replace("```", "").strip()
        return json.loads(texto_json)
    except Exception as e:
        return {"status": "ERRO", "motivo": f"Falha na IA: {e}"}

def buscar_bio_no_google(arroba, api_serper):
    url = "https://google.serper.dev/search"
    query = f'site:instagram.com "{arroba}"'
    payload = json.dumps({"q": query, "num": 1})
    headers = {'X-API-KEY': api_serper, 'Content-Type': 'application/json'}
    try:
        res = requests.post(url, headers=headers, data=payload)
        dados = res.json()
        if "organic" in dados and len(dados["organic"]) > 0:
            return dados["organic"][0].get("snippet", "") + " " + dados["organic"][0].get("title", "")
        return "Nenhuma informação."
    except Exception:
        return "Erro ao buscar."

# --- CARD DO LEAD ---
def desenhar_card_lead(chumbo, contexto="geral"):
    perfil_tag = chumbo.get('perfil', 'N/A')
    emoji_perfil = "🧑‍💻" if perfil_tag == "PERFIL_A" else ("💼" if perfil_tag == "PERFIL_B" else "🔑")
    
    with st.expander(f"{emoji_perfil} {chumbo['arroba']} · {perfil_tag} · Aprovado", expanded=False):
        username_limpo = chumbo['arroba'].replace('@', '').strip()
        username_limpo = re.sub(r'(https?://)?(www\.)?instagram\.com/', '', username_limpo)
        username_limpo = username_limpo.replace('/', '')
        link_ig = f"https://www.instagram.com/{username_limpo}/"

        col1, col2, col3, col4, col5 = st.columns([1.5, 0.8, 1, 1, 1])
        with col1:
            st.caption(f"**Motivo:** {chumbo['motivo']}")
            if chumbo.get('nome_lead'):
                st.caption(f"**Nome:** {chumbo['nome_lead']}")
        with col2:
            st.code(username_limpo, language=None)
        with col3:
            st.link_button("👉 Abrir Insta", link_ig, use_container_width=True, type="primary")

        estado_crm_key = f"estado_crm_{chumbo['arroba']}_{contexto}"
        estado_bl_key = f"estado_bl_{chumbo['arroba']}_{contexto}"

        if estado_crm_key not in st.session_state:
            st.session_state[estado_crm_key] = False
        if estado_bl_key not in st.session_state:
            st.session_state[estado_bl_key] = False

        with col4:
            if not st.session_state[estado_crm_key] and not st.session_state[estado_bl_key]:
                if st.button("✅ CRM", key=f"btn_crm_{chumbo['arroba']}_{contexto}", use_container_width=True):
                    dados_crm = chumbo.copy()
                    dados_crm["link_ig"] = link_ig
                    dados_crm["sheet_name"] = st.session_state["nome_aba"]
                    dados_crm["status"] = "Abordado"

                    dados_bl = chumbo.copy()
                    dados_bl["link_ig"] = link_ig
                    dados_bl["sheet_name"] = st.session_state["aba_blacklist"]
                    dados_bl["status"] = "Foi pro CRM"

                    if enviar_lead_para_planilha(dados_crm):
                        if st.session_state["nome_aba"] != st.session_state["aba_blacklist"]:
                            enviar_lead_para_planilha(dados_bl)
                        st.session_state["blacklist_arrobas"].add(chumbo['arroba'])
                        st.session_state[estado_crm_key] = True
                        st.toast("Lead salvo no CRM e enviado para a Blacklist!", icon="✅")
                        st.rerun()
            elif st.session_state[estado_crm_key]:
                st.success("✅ No CRM!")

        with col5:
            if not st.session_state[estado_crm_key] and not st.session_state[estado_bl_key]:
                if st.button("🚫 Blacklist", key=f"btn_bl_{chumbo['arroba']}_{contexto}", use_container_width=True):
                    dados_bl = chumbo.copy()
                    dados_bl["link_ig"] = link_ig
                    dados_bl["sheet_name"] = st.session_state["aba_blacklist"]
                    dados_bl["status"] = "Rejeitado"

                    if enviar_lead_para_planilha(dados_bl):
                        st.session_state["blacklist_arrobas"].add(chumbo['arroba'])
                        st.session_state[estado_bl_key] = True
                        st.toast("Lead enviado direto para a Blacklist!", icon="🚫")
                        st.rerun()
            elif st.session_state[estado_bl_key]:
                st.warning("🚫 Na Blacklist!")

        st.divider()
        st.markdown("**🔥 Mensagem 1 — Abordagem**")
        st.code(chumbo.get('script_1', ''), language="markdown")

        st.markdown("**💬 Mensagem 2 — Follow-up (2 dias depois)**")
        fup = CONFIG["SCRIPT_FOLLOWUP_2D"].replace("[NOME]", chumbo.get('nome_lead', '') or "")
        st.code(fup, language="markdown")

        st.markdown("**⚡ Mensagem 3 — Injeção de Sinceridade (4 dias depois)**")
        inj = CONFIG["SCRIPT_INJECAO_4D"].replace("[NOME]", chumbo.get('nome_lead', '') or "")
        st.code(inj, language="markdown")

        st.divider()
        st.markdown("**A IA acertou neste perfil? (Ajude-a a aprender)**")
        if chumbo['arroba'] not in st.session_state["feedbacks_dados"]:
            col_fb1, col_fb2, _ = st.columns([1, 1, 2])
            with col_fb1:
                if st.button("👍 Sim, buscar parecidos", key=f"up_{chumbo['arroba']}_{contexto}"):
                    st.session_state["bons_exemplos"].append(chumbo.get('bio', ''))
                    st.session_state["feedbacks_dados"].append(chumbo['arroba'])
                    salvar_feedback_planilha(chumbo['arroba'], "Like", chumbo.get('bio', ''))
                    st.rerun()
            with col_fb2:
                if st.button("👎 Não, perfil ruim", key=f"down_{chumbo['arroba']}_{contexto}"):
                    st.session_state["maus_exemplos"].append(chumbo.get('bio', ''))
                    st.session_state["feedbacks_dados"].append(chumbo['arroba'])
                    salvar_feedback_planilha(chumbo['arroba'], "Dislike", chumbo.get('bio', ''))
                    st.rerun()
        else:
            st.success("✅ Feedback guardado!")

# --- PROCESSAMENTO DE LISTA ---
def processar_lista_arrobas(lista_de_arrobas):
    st.session_state["leads_aprovados_tela"] = []
    st.session_state["leads_reprovados_tela"] = []

    barra = st.progress(0)
    for i, arroba in enumerate(lista_de_arrobas):
        barra.progress((i + 1) / len(lista_de_arrobas), text=f"Analisando {arroba}...")
        st.session_state["blacklist_arrobas"].add(arroba)

        bio = buscar_bio_no_google(arroba, st.session_state["api_key_serper"])
        if bio and "Erro" not in bio and "Nenhuma" not in bio:
            avaliacao = analisar_e_gerar_script(arroba, bio, st.session_state["api_key_gemini"])

            if avaliacao.get("status") == "APROVADO":
                lead_aprovado = {
                    "arroba": arroba,
                    "bio": bio,
                    "script_1": avaliacao.get("script_1"),
                    "motivo": avaliacao.get("motivo"),
                    "perfil": avaliacao.get("perfil", "N/A"),
                    "nome_lead": avaliacao.get("nome_lead", ""),
                }
                st.session_state["leads_aprovados_tela"].append(lead_aprovado)

                arrobas_salvos = [l["arroba"] for l in st.session_state["historico_leads"]]
                if arroba not in arrobas_salvos:
                    st.session_state["historico_leads"].insert(0, lead_aprovado)
            else:
                st.session_state["leads_reprovados_tela"].append({"arroba": arroba, "motivo": avaliacao.get("motivo")})
        else:
            st.session_state["leads_reprovados_tela"].append({"arroba": arroba, "motivo": "Perfil fechado ou sem dados."})
        time.sleep(1.0)
    barra.empty()

# --- RENDERIZAR RESULTADOS ---
def renderizar_resultados_garimpo(contexto_render):
    if st.session_state["leads_aprovados_tela"]:
        st.divider()
        st.subheader(f"✅ {len(st.session_state['leads_aprovados_tela'])} Leads Aprovados")
        for chumbo in st.session_state["leads_aprovados_tela"]:
            desenhar_card_lead(chumbo, contexto=contexto_render)

    if st.session_state["leads_reprovados_tela"]:
        st.subheader(f"❌ {len(st.session_state['leads_reprovados_tela'])} Leads Descartados")
        for lixo in st.session_state["leads_reprovados_tela"]:
            st.write(f"- **{lixo['arroba']}**: {lixo['motivo']}")

# --- INTERFACE COM ABAS ---
aba_garimpo, aba_busca, aba_historico, aba_crm = st.tabs(["🔍 Garimpo", "📝 Colar @Arrobas", "📚 Histórico", "📊 Planilha CRM"])

with aba_garimpo:
    st.subheader("Encontrar e Qualificar Leads automaticamente")
    col1, col2, col3, col4 = st.columns([1.5, 1.5, 1.5, 1])
    with col1:
        nicho_alvo = st.text_input("Nicho / Profissão:", placeholder="Ex: dev iniciante, no-code, founder")
    with col2:
        hashtag_alvo = st.text_input("Hashtag (Opcional):", placeholder="Ex: #lovable #nocode #indiehacker")
    with col3:
        local_alvo = st.text_input("Localização (Opcional):", placeholder="Ex: Brasil")
    with col4:
        qtd_busca = st.number_input("Qtd:", min_value=5, max_value=50, value=15, step=5)

    with st.expander("🛠️ Filtros Avançados (Opcional)", expanded=False):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            termos_negativos = st.text_input("Palavras para EXCLUIR:", placeholder="Ex: curso, aula, fanpage")
        with col_f2:
            frase_exata = st.text_input("Frase EXATA na Bio:", placeholder='Ex: "construindo meu SaaS"')

    if st.button("🔍 Iniciar Nova Busca", type="primary", use_container_width=True):
        if not st.session_state["api_key_serper"] or not st.session_state["api_key_gemini"]:
            st.error("Preencha as duas API Keys no painel lateral!")
        elif not nicho_alvo and not hashtag_alvo:
            st.warning("Preencha o Nicho/Profissão ou uma Hashtag.")
        else:
            st.session_state["ultima_busca_nicho"] = nicho_alvo
            st.session_state["ultima_busca_hashtag"] = hashtag_alvo
            st.session_state["ultima_busca_local"] = local_alvo
            st.session_state["ultima_busca_negativos"] = termos_negativos
            st.session_state["ultima_busca_frase"] = frase_exata
            st.session_state["proxima_pagina"] = 1

            with st.spinner("Varrendo a internet..."):
                arrobas, prox_pag = garimpar_perfis_google(
                    nicho_alvo, hashtag_alvo, local_alvo, termos_negativos, frase_exata,
                    qtd_busca, st.session_state["api_key_serper"], 1
                )
                st.session_state["proxima_pagina"] = prox_pag

            if arrobas:
                processar_lista_arrobas(arrobas)
            else:
                st.warning("Nenhum perfil novo encontrado. Tente outros termos!")

    if st.session_state["ultima_busca_nicho"] or st.session_state["ultima_busca_hashtag"]:
        if st.button("➕ Pesquisar Mais 10 Novos Leads", type="secondary", use_container_width=True):
            with st.spinner(f"Folheando página {st.session_state['proxima_pagina']}..."):
                arrobas, prox_pag = garimpar_perfis_google(
                    st.session_state["ultima_busca_nicho"],
                    st.session_state["ultima_busca_hashtag"],
                    st.session_state["ultima_busca_local"],
                    st.session_state["ultima_busca_negativos"],
                    st.session_state["ultima_busca_frase"],
                    10, st.session_state["api_key_serper"], st.session_state["proxima_pagina"]
                )
                st.session_state["proxima_pagina"] = prox_pag
            if arrobas:
                processar_lista_arrobas(arrobas)
            else:
                st.warning("Fim dos resultados. Tente novos termos!")

    renderizar_resultados_garimpo("garimpo")

with aba_busca:
    st.subheader("Processar Lista Própria")
    lista_arrobas = st.text_area("Cole os @arrobas (um por linha):", height=150)
    if st.button("🚀 Processar Lote Manual", type="primary"):
        if lista_arrobas.strip():
            arrobas = [a.strip() for a in lista_arrobas.split("\n") if a.strip()]
            processar_lista_arrobas(arrobas)

    renderizar_resultados_garimpo("busca_manual")

with aba_historico:
    st.subheader("📚 Leads Qualificados")
    if not st.session_state["historico_leads"]:
        st.info("Nenhum lead qualificado ainda.")
    else:
        for chumbo in st.session_state["historico_leads"]:
            desenhar_card_lead(chumbo, contexto="historico")

with aba_crm:
    st.subheader("📊 Planilha LovKeys CRM")
    components.iframe(CONFIG["SPREADSHEET_URL"].replace("/edit", "/edit?rm=minimal"), height=800, scrolling=True)
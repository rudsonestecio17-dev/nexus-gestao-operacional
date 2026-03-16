import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import time

# 1. SETUP E DESIGN CTRL
st.set_page_config(page_title="CTRL | Gestão de Produção", layout="wide", initial_sidebar_state="expanded")

# Conexão Supabase
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

LOGO_URL = "https://i.ibb.co/6Lr0QZY/nexus-2.png" 

SETORES = [
    "Tecnologia e Marketing", "Diretoria", "Gerência", 
    "Operações Manutenção", "Projetos", "Comercial", 
    "Compras", "Engenharia", "Orçamentos"
]

# 2. DESIGN EMPRESARIAL (Correção de flashes e Identidade Solluz)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Previne o fundo branco entre trocas de abas */
    .stApp { background-color: #FFFFFF; color: #1e293b; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Identidade CTRL */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important; 
        border-right: 1px solid #e2e8f0; 
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Estilização dos Submenus na Lateral */
    .stSidebar .stExpander { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 10px !important;
        margin-bottom: 8px !important;
    }
    
    .stSidebar button {
        background-color: transparent !important; border: none !important; color: #FFFFFF !important;
        text-align: left !important; width: 100% !important; padding: 12px 15px !important;
        font-size: 11px !important; text-transform: uppercase !important; font-weight: 600 !important;
    }
    .stSidebar button:hover { background-color: #4f46e5 !important; border-radius: 5px; }

    /* Cards e UI Empresarial */
    .ticket-card { background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 6px solid #6366f1; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .row-monitor { background: #f8fafc; border-radius: 12px; padding: 25px; margin-bottom: 15px; border: 1px solid #e2e8f0; border-left: 10px solid #6366f1; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .dot { height: 20px; width: 20px; border-radius: 50%; display: inline-block; margin: 4px auto; border: 3px solid #FFF; }
    .bg-success { background-color: #10b981; }
    .bg-danger { background-color: #ef4444; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES TÉCNICAS ---
def registrar_log(acao, detalhe):
    u = st.session_state.get('user_name', 'Sistema')
    try: supabase.table("logs_sistema").insert({"usuario": u, "acao": acao, "detalhe": detalhe}).execute()
    except: pass

def calcular_duracao(inicio, fim):
    if inicio and fim:
        try:
            fmt = "%Y-%m-%dT%H:%M:%S"
            diff = datetime.strptime(fim[:19], fmt) - datetime.strptime(inicio[:19], fmt)
            return round(diff.total_seconds() / 3600, 2)
        except: return 0
    return 0

def get_proxima_os():
    try:
        res = supabase.table("pedidos").select("numero_pedido").order("id", desc=True).limit(1).execute()
        return str(int(res.data[0]['numero_pedido']) + 1) if res.data else "1001"
    except: return "1001"

# --- FLUXO DE ACESSO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<div style='text-align: center; padding-top: 100px;'><h1 style='color: #1e1b4b; font-size: 5em;'>CTRL</h1><p>GESTÃO DE PRODUÇÃO | SOLLUZ SYSTEMS</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("login"):
            u, s = st.text_input("Usuário"), st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO COMANDO"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.update({
                        "autenticado": True, "perfil": res.data[0]['perfil'], 
                        "setor_user": res.data[0].get('setor', 'Operações Manutenção'), "user_name": res.data[0]['login']
                    })
                    st.rerun()
                else: st.error("Acesso negado.")
else:
    # --- BARRA LATERAL (MENU COMPLETO) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>CTRL</h2>", unsafe_allow_html=True)
        st.write(f"<p style='text-align:center; font-size:10px;'>{st.session_state.setor_user.upper()}</p>", unsafe_allow_html=True)
        st.divider()
        if 'pg' not in st.session_state: st.session_state.pg = "dash"

        with st.expander("CHAMADOS INTERNOS", expanded=True):
            if st.button("CENTRAL DE TICKETS"): st.session_state.pg = "tickets"; st.rerun()

        with st.expander("CONTROLE OPERACIONAL"):
            if st.button("DASHBOARD"): st.session_state.pg = "dash"; st.rerun()
            if st.button("RELATÓRIOS"): st.session_state.pg = "rel"; st.rerun()
            if st.button("MONITORAMENTO"): st.session_state.pg = "tv"; st.rerun()
        
        with st.expander("LOGÍSTICA E FINANCEIRO"):
            if st.button("RECEITA TOTAL"): st.session_state.pg = "fin"; st.rerun()
            if st.button("VALIDAÇÃO"): st.session_state.pg = "val"; st.rerun()
            if st.button("ENTREGA"): st.session_state.pg = "ent"; st.rerun()

        with st.expander("ADMINISTRAÇÃO"):
            if st.button("CADASTROS"): st.session_state.pg = "cad"; st.rerun()
            if st.button("GESTÃO EQUIPE"): st.session_state.pg = "adm"; st.rerun()

        with st.expander("PROJETOS E ENGENHARIA", expanded=True):
            if st.button("COMERCIAL (PV/PO)"): st.session_state.pg = "com"; st.rerun()
            if st.button("WORKFLOW OS"): st.session_state.pg = "work"; st.rerun()
            if st.button("CHÃO DE FÁBRICA"): st.session_state.pg = "fab"; st.rerun()

        st.divider()
        if st.button("LOGOUT"): st.session_state.autenticado = False; st.rerun()

    # --- RENDERIZAÇÃO ---
    p = st.session_state.pg

    # PÁGINA: CENTRAL DE TICKETS
    if p == "tickets":
        st.title("Central de Chamados Internos")
        t1, t2 = st.tabs(["Tickets para meu Setor", "Abrir Novo Chamado"])
        with t2:
            with st.form("new_ticket"):
                c1, c2 = st.columns(2)
                dest = c1.selectbox("Delegar para o Setor", SETORES)
                urg = c1.select_slider("Urgência", options=["Baixa", "Média", "Alta", "Crítica"])
                tit = c2.text_input("Assunto")
                desc = st.text_area("Descrição do Problema")
                if st.form_submit_button("ENVIAR CHAMADO"):
                    supabase.table("chamados").insert({
                        "titulo": tit, "descricao": desc, "setor_destino": dest,
                        "solicitante": st.session_state.user_name, "setor_origem": st.session_state.setor_user,
                        "status": "Aberto", "urgencia": urg
                    }).execute()
                    st.success("Chamado registrado!")
        with t1:
            tickets = supabase.table("chamados").select("*").eq("setor_destino", st.session_state.setor_user).order("id", desc=True).execute()
            if tickets.data:
                for tk in tickets.data:
                    with st.container():
                        st.markdown(f"<div class='ticket-card'><b>[{tk['status']}] {tk['titulo']}</b><br><small>Urgência: {tk['urgencia']} | Por: {tk['solicitante']}</small><p>{tk['descricao']}</p></div>", unsafe_allow_html=True)
                        if tk['status'] == "Aberto":
                            if st.button("ASSUMIR CHAMADO", key=f"tk_{tk['id']}"):
                                supabase.table("chamados").update({"status": "Em Atendimento", "responsavel_tecnico": st.session_state.user_name}).eq("id", tk['id']).execute()
                                st.rerun()
            else: st.info("Nenhum chamado pendente para você.")

    # PÁGINA: COMERCIAL (FLUXO PV/PO)
    elif p == "com":
        st.title("Projetos | Comercial")
        with st.expander("Gerar Novo Pedido", expanded=True):
            p_db = supabase.table("projetos").select("id, nome_projeto").execute()
            l_p = {x['nome_projeto']: x['id'] for x in p_db.data}
            with st.form("f_com"):
                c1, c2 = st.columns(2)
                no = c1.text_input("Nº OS", value=get_proxima_os())
                po_sel = c1.selectbox("Projeto", list(l_p.keys()))
                vo = c2.number_input("Valor R$", min_value=0.0)
                prazo = c2.date_input("Prazo de Entrega")
                if st.form_submit_button("LANÇAR NO SISTEMA"):
                    r = supabase.table("pedidos").insert({"numero_pedido": no, "id_projeto": l_p[po_sel], "valor_orcamento": vo, "prazo_entrega": str(prazo), "status_geral": "EXECUTANDO ORÇAMENTO"}).execute()
                    if r.data:
                        supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                        st.success("Salvo!"); st.rerun()
        st.divider()
        pedidos = supabase.table("pedidos").select("*").neq("status_geral", "CONCLUÍDO").execute()
        for i in pedidos.data:
            with st.expander(f"OS: {i['numero_pedido']} | {i['status_geral']}"):
                c1, c2 = st.columns(2)
                pv = c1.text_input("Nº Pedido Venda (PV)", value=i.get('num_pv', ''), key=f"pv_{i['id']}")
                po = c2.text_input("Nº Ordem Compra (PO)", value=i.get('num_po', ''), key=f"po_{i['id']}")
                if st.button("AVANÇAR PARA WORKFLOW", key=f"up_{i['id']}"):
                    ns = "EM PRODUÇÃO" if po else ("ORÇAMENTO APROVADO" if pv else i['status_geral'])
                    supabase.table("pedidos").update({"num_pv": pv, "num_po": po, "status_geral": ns}).eq("id", i['id']).execute()
                    st.rerun()

    # PÁGINA: WORKFLOW (UPLOAD DE DESENHOS)
    elif p == "work":
        st.title("Projetos | Engenharia e Workflow")
        p_wf = supabase.table("pedidos").select("*").eq("status_geral", "EM PRODUÇÃO").execute()
        if p_wf.data:
            sel = st.selectbox("Selecione a OS:", [x['numero_pedido'] for x in p_wf.data])
            id_w = next(x['id'] for x in p_wf.data if x['numero_pedido'] == sel)
            with st.form("f_wf"):
                arq = st.file_uploader("Subir Desenho Técnico (PDF/IMG)")
                st.write("Configurar Roteiro:")
                e1, e2 = st.columns(2)
                h1, h2, h3, h4 = e1.checkbox("Corte"), e1.checkbox("Dobra"), e1.checkbox("Solda"), e1.checkbox("Metaleira")
                h5, h6, h7 = e2.checkbox("Calandragem"), e2.checkbox("Galvanização"), e2.checkbox("Pintura")
                if st.form_submit_button("DEFINIR FLUXO"):
                    url = ""
                    if arq:
                        path = f"pedidos/{sel}/{arq.name}"
                        supabase.storage.from_("desenhos").upload(path, arq.getvalue(), {"upsert": "true"})
                        url = supabase.storage.from_("desenhos").get_public_url(path)
                    supabase.table("pedidos").update({
                        "arquivo_url": url, "has_corte_laser": h1, "has_dobra_cnc": h2, "has_solda": h3, 
                        "has_metaleira": h4, "has_calandragem": h5, "has_galvanizacao": h6, "has_pintura": h7
                    }).eq("id", id_w).execute()
                    st.success("Workflow Configurado!")

    # PÁGINA: CHÃO DE FÁBRICA (7 ETAPAS + MÉTRICAS)
    elif p == "fab":
        st.title("Produção | Chão de Fábrica")
        atv = supabase.table("pedidos").select("*, linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        if atv.data:
            sel = st.selectbox("OS:", [x['numero_pedido'] for x in atv.data])
            item = next(x for x in atv.data if x['numero_pedido'] == sel)
            prod = item['linha_producao'][0]
            if item['arquivo_url']: st.link_button("📂 DESENHO TÉCNICO", item['arquivo_url'], use_container_width=True)

            def render_etapa(label, campo, hab):
                if hab:
                    with st.expander(f"⚙️ {label.upper()}", expanded=True):
                        c1, c2, c3 = st.columns([1, 1, 2])
                        i, f = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                        if not i:
                            if c1.button("INICIAR", key=f"i_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", item['id']).execute()
                                st.rerun()
                        elif not f:
                            c1.info(f"Início: {i[11:16]}")
                            obs = c3.text_input("Observação", key=f"o_{campo}")
                            if c2.button("FINALIZAR", key=f"f_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", item['id']).execute()
                                # Gatilho Fiscalização
                                r_check = supabase.table("pedidos").select("*, linha_producao(*)").eq("id", item['id']).single().execute().data
                                lp = r_check['linha_producao'][0]
                                checklist = {"has_corte_laser": "corte_fim", "has_dobra_cnc": "dobra_fim", "has_solda": "solda_fim", "has_metaleira": "metaleira_fim", "has_calandragem": "calandragem_fim", "has_galvanizacao": "galvanizacao_fim", "has_pintura": "pintura_fim"}
                                concluido = True
                                for ch, cf in checklist.items():
                                    if r_check.get(ch) == True and not lp.get(cf): concluido = False; break
                                if concluido: supabase.table("pedidos").update({"status_geral": "EM FISCALIZAÇÃO"}).eq("id", item['id']).execute()
                                st.rerun()
                        else: st.success(f"Duração: {calcular_duracao(i, f)}h | {i[11:16]} - {f[11:16]}")

            render_etapa("Corte", "corte", item['has_corte_laser'])
            render_etapa("Dobra", "dobra", item['has_dobra_cnc'])
            render_etapa("Solda", "solda", item['has_solda'])
            render_etapa("Metaleira", "metaleira", item['has_metaleira'])
            render_etapa("Calandragem", "calandragem", item['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", item['has_galvanizacao'])
            render_etapa("Pintura", "pintura", item['has_pintura'])

    # PÁGINA: LOGÍSTICA (VALIDAÇÃO E ENTREGA)
    elif p == "val":
        st.title("Logística | Fiscalização")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "EM FISCALIZAÇÃO").execute()
        for os in res.data:
            st.markdown(f"<div class='row-monitor'><b>OS: {os['numero_pedido']}</b> | {os['projetos']['nome_projeto']}</div>", unsafe_allow_html=True)
            if st.button("APROVAR PARA DESPACHO", key=f"v_{os['id']}"):
                supabase.table("pedidos").update({"status_geral": "AGUARDANDO ENTREGA"}).eq("id", os['id']).execute()
                st.rerun()

    elif p == "ent":
        st.title("Logística | Entrega e Frete")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "AGUARDANDO ENTREGA").execute()
        if res.data:
            sel = st.selectbox("OS:", [x['numero_pedido'] for x in res.data])
            os_data = next(x for x in res.data if x['numero_pedido'] == sel)
            with st.form("f_ent"):
                c1, c2 = st.columns(2)
                t, f = c1.text_input("Transportadora"), c1.number_input("Valor Frete")
                dr, de = c2.date_input("Data Retirada"), c2.date_input("Previsão Entrega")
                if st.form_submit_button("CONCLUIR OS"):
                    supabase.table("pedidos").update({"status_geral": "CONCLUÍDO", "transportadora": t, "valor_frete": f}).eq("id", os_data['id']).execute()
                    st.success("Concluído!"); st.rerun()

    # PÁGINA: CADASTROS (RESTAURADA COMPLETA)
    elif p == "cad":
        st.title("Administração | Cadastros de Base")
        c1, c2 = st.columns(2)
        with c1:
            with st.form("f_cli"):
                st.subheader("Cliente/Solicitante")
                n, e, t, o = st.text_input("Responsável"), st.text_input("Empresa"), st.text_input("Telefone"), st.text_area("Endereço Completo")
                if st.form_submit_button("CADASTRAR CLIENTE"):
                    supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t, "info_adicional": o}).execute()
                    st.success("Salvo!")
        with c2:
            s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
            l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
            with st.form("f_proj"):
                st.subheader("Projeto/Obra")
                np, sid = st.text_input("Título"), st.selectbox("Cliente", list(l_s.keys()))
                cid, rua, num, cep = st.text_input("Cidade"), st.text_input("Rua"), st.text_input("Nº"), st.text_input("CEP")
                if st.form_submit_button("VINCULAR PROJETO"):
                    supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": rua, "numero": num, "cep": cep}).execute()
                    st.success("Vinculado!")

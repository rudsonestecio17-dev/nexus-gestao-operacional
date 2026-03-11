import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# 1. CONFIGURAÇÕES DO SISTEMA
st.set_page_config(page_title="CTRL | Gestão de Produção", layout="wide", initial_sidebar_state="expanded")

# 2. CONEXÃO SUPABASE
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# LOGO CTRL (Identidade Visual Solluz Systems)
LOGO_URL = "https://i.ibb.co/6Lr0QZY/nexus-2.png" 

# 3. CSS CUSTOMIZADO (Identidade Visual Violeta Tecnológico)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    .stApp { background-color: #FFFFFF !important; color: #1e293b !important; font-family: 'Inter', sans-serif !important; }
    
    /* Barra Lateral CTRL */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #202c65 0%, #35337a 100%) !important; 
        border-right: 1px solid #e2e8f0; 
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Botões da Sidebar */
    .stSidebar .stExpander { background-color: transparent !important; border: none !important; padding: 0px !important; }
    .stSidebar button {
        background-color: transparent !important; border: none !important; color: #FFFFFF !important;
        text-align: left !important; width: 100% !important; padding: 10px 15px !important;
        font-size: 11px !important; text-transform: uppercase !important; font-weight: 600 !important;
        letter-spacing: 0.8px; margin-bottom: -5px !important;
    }
    .stSidebar button:hover { background-color: #3b82f6 !important; color: white !important; }

    /* Estilo de Tabelas e Cards */
    .row-monitor { 
        background: #f8fafc; border-radius: 12px; padding: 20px; margin-bottom: 12px; 
        border: 1px solid #e2e8f0; border-left: 8px solid #3b82f6; 
        display: flex; justify-content: space-between; align-items: center;
    }
    .dot { height: 18px; width: 18px; border-radius: 50%; display: inline-block; margin: 4px auto; border: 2px solid #FFF; }
    .bg-success { background-color: #22c55e; }
    .bg-danger { background-color: #ef4444; }
    
    .stButton>button { border-radius: 6px; font-weight: 700; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def registrar_log(acao, detalhe):
    usuario = st.session_state.get('user_name', 'Sistema')
    try: supabase.table("logs_sistema").insert({"usuario": usuario, "acao": acao, "detalhe": detalhe}).execute()
    except: pass

def calcular_horas(inicio, fim):
    if inicio and fim:
        try:
            fmt = "%Y-%m-%dT%H:%M:%S"
            diff = datetime.strptime(fim[:19], fmt) - datetime.strptime(inicio[:19], fmt)
            return round(diff.total_seconds() / 3600, 2)
        except: return 0
    return 0

# --- CONTROLE DE ACESSO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<div style='text-align: center; padding-top: 100px;'><h1 style='color: #202c65; font-size: 4em;'>CTRL</h1><p style='color: #64748b; font-weight: 600;'>GESTÃO DE PRODUÇÃO | SOLLUZ SYSTEMS</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("login_ctrl"):
            u, s = st.text_input("Usuário"), st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR TERMINAL"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.update({"autenticado": True, "perfil": res.data[0]['perfil'], "user_name": res.data[0]['login']})
                    registrar_log("ACESSO", "Login realizado")
                    st.rerun()
                else: st.error("Acesso negado.")
else:
    # --- MENU LATERAL ESTRUTURADO ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>CTRL</h2>", unsafe_allow_html=True)
        st.write(f"<p style='text-align:center; font-size: 11px;'>SOLLUZ SYSTEMS</p>", unsafe_allow_html=True)
        st.divider()

        if 'pagina_ativa' not in st.session_state: st.session_state.pagina_ativa = "dash"

        if st.session_state.perfil == "admin":
            with st.expander("CONTROLE OPERACIONAL", expanded=True):
                if st.button("DASHBOARD"): st.session_state.pagina_ativa = "dash"; st.rerun()
                if st.button("RELATÓRIOS"): st.session_state.pagina_ativa = "rel"; st.rerun()
                if st.button("MONITORAMENTO"): st.session_state.pagina_ativa = "tv"; st.rerun()
            with st.expander("FINANCEIRO"):
                if st.button("RECEITA TOTAL"): st.session_state.pagina_ativa = "fin"; st.rerun()
            with st.expander("LOGÍSTICA"):
                if st.button("VALIDAÇÃO"): st.session_state.pagina_ativa = "log_val"; st.rerun()
                if st.button("ENTREGA"): st.session_state.pagina_ativa = "log_ent"; st.rerun()
            with st.expander("ADMINISTRAÇÃO"):
                if st.button("CADASTROS"): st.session_state.pagina_ativa = "cad"; st.rerun()
                if st.button("GESTÃO SISTEMA"): st.session_state.pagina_ativa = "adm"; st.rerun()
            with st.expander("PROJETOS"):
                if st.button("COMERCIAL"): st.session_state.pagina_ativa = "com"; st.rerun()
                if st.button("WORKFLOW OS"): st.session_state.pagina_ativa = "work"; st.rerun()

        with st.expander("PRODUÇÃO", expanded=True):
            if st.button("CHÃO DE FÁBRICA"): st.session_state.pagina_ativa = "fab"; st.rerun()

        st.divider()
        if st.button("SAIR"): st.session_state.autenticado = False; st.rerun()

    # --- PÁGINAS ---
    p = st.session_state.pagina_ativa

    # DASHBOARD
    if p == "dash":
        st.title("Indicadores Operacionais")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").execute()
        if res.data:
            df = pd.DataFrame([{"OS": i['numero_pedido'], "Projeto": i['projetos']['nome_projeto'] if i['projetos'] else "-", "Status": i['status_geral'], "Prazo": i['prazo_entrega']} for i in res.data])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # FINANCEIRO
    elif p == "fin":
        st.title("Financeiro | Receita Total")
        res_fin = supabase.table("pedidos").select("valor_orcamento").execute()
        total = sum([float(x['valor_orcamento']) for x in res_fin.data if x['valor_orcamento']])
        st.metric("Receita Bruta Total", f"R$ {total:,.2f}")

    # COMERCIAL (TRATAMENTO DE APIERROR)
    elif p == "com":
        st.title("Projetos | Comercial")
        with st.expander("Novo Orçamento", expanded=True):
            p_db = supabase.table("projetos").select("id, nome_projeto").execute()
            l_p = {x['nome_projeto']: x['id'] for x in p_db.data}
            with st.form("f_com"):
                c1, c2 = st.columns(2)
                no, po = c1.text_input("Nº OS"), c1.selectbox("Projeto", list(l_p.keys()))
                vo, de = c2.number_input("Valor R$", min_value=0.0), c2.date_input("Prazo")
                if st.form_submit_button("REGISTRAR"):
                    try:
                        r = supabase.table("pedidos").insert({"numero_pedido": no, "id_projeto": l_p[po], "valor_orcamento": vo, "prazo_entrega": str(de), "status_geral": "EXECUTANDO ORÇAMENTO"}).execute()
                        if r.data:
                            supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                            st.success("Orçamento Registrado!")
                            st.rerun()
                    except: st.error("Erro: Verifique se a OS já existe.")

    # CHÃO DE FÁBRICA (CORREÇÃO KEYERROR)
    elif p == "fab":
        st.title("Produção | Chão de Fábrica")
        atv = supabase.table("pedidos").select("*, linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        if atv.data:
            sel = st.selectbox("OS:", [x['numero_pedido'] for x in atv.data])
            item = next(x for x in atv.data if x['numero_pedido'] == sel)
            prod = item['linha_producao'][0]

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
                            obs = c3.text_input("Obs", key=f"o_{campo}")
                            if c2.button("FINALIZAR", key=f"f_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", item['id']).execute()
                                # Lógica de Fiscalização
                                r_check = supabase.table("pedidos").select("*, linha_producao(*)").eq("id", item['id']).single().execute().data
                                lp = r_check['linha_producao'][0]
                                checklist = {"has_corte_laser": "corte_fim", "has_dobra_cnc": "dobra_fim", "has_solda": "solda_fim", "has_metaleira": "metaleira_fim", "has_calandragem": "calandragem_fim", "has_galvanizacao": "galvanizacao_fim", "has_pintura": "pintura_fim"}
                                concluido = True
                                for ch, cf in checklist.items():
                                    if r_check.get(ch) == True and not lp.get(cf): concluido = False; break
                                if concluido: supabase.table("pedidos").update({"status_geral": "EM FISCALIZAÇÃO"}).eq("id", item['id']).execute()
                                st.rerun()
                        else: st.success(f"Finalizado: {i[11:16]} - {f[11:16]}")

            render_etapa("Corte", "corte", item['has_corte_laser'])
            render_etapa("Dobra", "dobra", item['has_dobra_cnc'])
            render_etapa("Solda", "solda", item['has_solda'])
            render_etapa("Metaleira", "metaleira", item['has_metaleira'])
            render_etapa("Calandragem", "calandragem", item['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", item['has_galvanizacao'])
            render_etapa("Pintura", "pintura", item['has_pintura'])

    # LOGÍSTICA - VALIDAÇÃO E ENTREGA
    elif p == "log_val":
        st.title("Logística | Fiscalização")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "EM FISCALIZAÇÃO").execute()
        for os in res.data:
            if st.button(f"LIBERAR OS: {os['numero_pedido']}", key=f"ap_{os['id']}"):
                supabase.table("pedidos").update({"status_geral": "AGUARDANDO ENTREGA"}).eq("id", os['id']).execute()
                st.rerun()

    elif p == "log_ent":
        st.title("Logística | Entrega")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "AGUARDANDO ENTREGA").execute()
        if res.data:
            sel_e = st.selectbox("OS:", [x['numero_pedido'] for x in res.data])
            with st.form("f_ent"):
                t, f = st.text_input("Transportadora"), st.number_input("Frete")
                if st.form_submit_button("CONCLUIR"):
                    supabase.table("pedidos").update({"status_geral": "CONCLUÍDO"}).eq("numero_pedido", sel_e).execute()
                    st.rerun()

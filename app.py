import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONFIGURAÇÕES SOLLUZ SYSTEMS
st.set_page_config(page_title="Solluz systems | ERP", layout="wide", initial_sidebar_state="collapsed")

# 2. CONEXÃO SUPABASE
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# URL DA LOGO OFICIAL
LOGO_URL = "https://i.ibb.co/6Lr0QZY/nexus-2.png"

# CSS PREMIUM SOLLUZ (Barra Lateral #202c65 e Fundo Branco)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Fundo Principal Branco */
    .stApp { background-color: #FFFFFF !important; color: #1e293b !important; font-family: 'Inter', sans-serif !important; }
    
    /* BARRA LATERAL SOLLUZ (Sua correção aplicada com ajuste de cor de texto) */
    [data-testid="stSidebar"] { 
        background-color: #202c65 !important; 
        border-right: 1px solid #e2e8f0; 
    }
    /* Garantindo que o texto na sidebar seja BRANCO para não sumir no azul escuro */
    [data-testid="stSidebar"] * { 
        color: #FFFFFF !important; 
    }
    
    /* Abas Customizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #f1f5f9; padding: 10px 10px 0 10px; border-radius: 12px 12px 0 0; }
    .stTabs [data-baseweb="tab"] { height: 55px; background-color: #FFFFFF; border: 1px solid #e2e8f0; color: #64748b; border-radius: 8px 8px 0 0; padding: 0 25px; font-size: 11px; text-transform: uppercase; font-weight: 700; }
    .stTabs [aria-selected="true"] { background-color: #FFFFFF !important; color: #3b82f6 !important; border: 1px solid #3b82f6 !important; border-bottom: 2px solid #FFFFFF !important; }

    /* Monitor TV Estilo Solluz */
    .row-monitor {
        background: #f8fafc; border-radius: 14px; padding: 25px; margin-bottom: 15px; 
        border: 1px solid #e2e8f0; border-left: 8px solid #3b82f6; 
        display: flex; justify-content: space-between; align-items: center; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    .dot { height: 20px; width: 20px; border-radius: 50%; display: inline-block; margin: 6px auto; border: 3px solid #FFFFFF; }
    .bg-success { background-color: #238636; box-shadow: 0 0 10px rgba(35, 134, 54, 0.4); }
    .bg-danger { background-color: #da3633; box-shadow: 0 0 8px rgba(218, 54, 51, 0.3); }
    
    /* Botões Solluz */
    .stButton>button { width: 100%; border-radius: 8px; height: 48px; background-color: #f1f5f9; color: #1e293b; font-weight: 700; text-transform: uppercase; border: 1px solid #e2e8f0; transition: 0.2s; }
    .stButton>button:hover { background-color: #3b82f6; border-color: #3b82f6; color: #ffffff; }
    
    /* Inputs */
    .stExpander { background-color: #f8fafc !important; border-color: #e2e8f0 !important; border-radius: 10px !important; }
    input, select, textarea { background-color: #FFFFFF !important; color: #1e293b !important; border: 1px solid #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

def tela_login():
    st.markdown(f"<div style='text-align: center; margin-bottom: 30px;'><h1 style='color: #202c65; font-size: 2.8em;'>Solluz systems</h1><caption style='color: #64748b;'>CENTRO DE CONTROLE INDUSTRIAL</caption></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("CONECTAR À FÁBRICA"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.autenticado, st.session_state.perfil, st.session_state.user_name = True, res.data[0]['perfil'], res.data[0]['login']
                    st.rerun()
                else: st.error("Acesso negado.")

if not st.session_state.autenticado:
    tela_login()
else:
    # --- INTERFACE PRINCIPAL ---
    with st.sidebar:
        st.image(LOGO_URL, use_container_width=True)
        st.write(f"Operador: **{st.session_state.user_name.upper()}**")
        if st.button("Logout"):
            st.session_state.autenticado = False
            st.rerun()

    st.title("Solluz systems | Gestão Industrial")
    st.divider()

    if st.session_state.perfil == "admin":
        tab_dash, tab_comercial, tab_pedido, tab_fabrica, tab_tv, tab_admin = st.tabs(["Dashboard", "Comercial", "Workflow OS", "Chão de Fábrica", "Monitor TV", "ADMIN"])
    else:
        tab_fabrica = st.tabs(["CHÃO DE FÁBRICA"])[0]
        tab_dash = tab_comercial = tab_pedido = tab_tv = tab_admin = None

    # --- COMERCIAL ---
    if tab_comercial:
        with tab_comercial:
            st.subheader("Gestão de Orçamentos")
            with st.expander("📝 Novo Lançamento", expanded=True):
                p_db = supabase.table("projetos").select("id, nome_projeto").execute()
                l_p = {p['nome_projeto']: p['id'] for p in p_db.data}
                with st.form("f_com"):
                    c1, c2 = st.columns(2)
                    n_o, p_o = c1.text_input("Identificador"), c1.selectbox("Projeto", options=list(l_p.keys()))
                    v_o, d_e = c2.number_input("Valor R$", min_value=0.0), c2.date_input("Prazo")
                    if st.form_submit_button("CADASTRAR"):
                        d_ins = {"numero_pedido": n_o, "id_projeto": l_p[p_o], "valor_orcamento": v_o, "prazo_entrega": str(d_e), "status_geral": "EXECUTANDO ORÇAMENTO"}
                        r = supabase.table("pedidos").insert(d_ins).execute()
                        supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                        st.success("Salvo!")

            st.divider()
            st.subheader("⚙️ Aprovações PV/PO")
            p_com = supabase.table("pedidos").select("*").neq("status_geral", "CONCLUÍDO").execute()
            for p in p_com.data:
                with st.expander(f"OS: {p['numero_pedido']} | {p['status_geral']}"):
                    c1, c2 = st.columns(2)
                    pv = c1.text_input("Nº PV", value=p.get('num_pv', ''), key=f"pv_{p['id']}")
                    po = c2.text_input("Nº PO", value=p.get('num_po', ''), key=f"po_{p['id']}")
                    if st.button("ATUALIZAR STATUS", key=f"u_{p['id']}"):
                        n_s = p['status_geral']
                        if pv and not po: n_s = "ORÇAMENTO APROVADO"
                        if po: n_s = "EM PRODUÇÃO"
                        supabase.table("pedidos").update({"num_pv": pv, "num_po": po, "status_geral": n_s}).eq("id", p['id']).execute()
                        st.rerun()

    # --- CHÃO DE FÁBRICA (AS 7 ETAPAS) ---
    with tab_fabrica:
        st.subheader("Operação Industrial Solluz")
        atv = supabase.table("pedidos").select("id, numero_pedido, arquivo_url").eq("status_geral", "EM PRODUÇÃO").execute()
        l_atv = {p['numero_pedido']: p for p in atv.data}
        if l_atv:
            escolha = st.selectbox("OS Ativa:", list(l_atv.keys()))
            item = l_atv[escolha]
            if item['arquivo_url']: st.link_button("📂 ABRIR DESENHO", item['arquivo_url'], use_container_width=True)
            
            det = supabase.table("pedidos").select("*").eq("id", item['id']).single().execute().data
            prod = supabase.table("linha_producao").select("*").eq("id_pedido", item['id']).single().execute().data
            
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
                            obs = c3.text_input("Obs Técnica", key=f"o_{campo}")
                            if c2.button("FINALIZAR", key=f"f_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", item['id']).execute()
                                st.rerun()
                        else: st.success(f"OK | {i[11:16]}-{f[11:16]}")

            render_etapa("Corte a Laser", "corte", det['has_corte_laser'])
            render_etapa("Dobra CNC", "dobra", det['has_dobra_cnc'])
            render_etapa("Soldagem", "solda", det['has_solda'])
            render_etapa("Metaleira", "metaleira", det['has_metaleira'])
            render_etapa("Calandragem", "calandragem", det['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", det['has_galvanizacao'])
            render_etapa("Pintura", "pintura", det['has_pintura'])
        else: st.info("Sem ordens ativa.")

    # --- ADMIN (DADOS MESTRES COMPLETOS) ---
    if tab_admin:
        with tab_admin:
            c1, c2 = st.columns(2)
            with c1:
                with st.expander("Registro de Solicitante", expanded=True):
                    with st.form("c_s"):
                        n, e, t = st.text_input("Responsável Solluz"), st.text_input("Empresa"), st.text_input("Telefone")
                        obs = st.text_area("Informações Adicionais")
                        if st.form_submit_button("SALVAR"):
                            supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t, "info_adicional": obs}).execute()
            with c2:
                with st.expander("Registro de Projeto", expanded=True):
                    s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
                    l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
                    with st.form("c_p"):
                        np, sid, cid = st.text_input("Título"), st.selectbox("Solicitante", options=list(l_s.keys())), st.text_input("Cidade")
                        end, num, cep = st.text_input("Endereço"), st.text_input("Nº"), st.text_input("CEP")
                        if st.form_submit_button("VINCULAR"):
                            supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": end, "numero": num, "cep": cep}).execute()

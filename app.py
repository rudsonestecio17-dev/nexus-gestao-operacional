import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONFIGURAÇÕES DE INTERFACE - MODO CLARO PROFISSIONAL
st.set_page_config(page_title="NEXUS ERP", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #334155; }
    .main { background-color: #ffffff; }
    
    /* Cabeçalhos */
    h1, h2, h3 { color: #0f172a; font-weight: 700; }
    
    /* Botões */
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        height: 42px;
        background-color: #1e293b;
        color: #ffffff;
        font-weight: 500;
        border: none;
        font-size: 13px;
        letter-spacing: 0.02em;
    }
    .stButton>button:hover { background-color: #334155; border: none; color: #fff; }
    
    /* Estilização das Abas (Branco com borda sutil) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 2px; 
        background-color: #f1f5f9; 
        padding: 5px 5px 0 5px; 
        border-radius: 8px 8px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #f1f5f9;
        border: none;
        padding: 10px 25px;
        color: #64748b;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-weight: 600;
        border-radius: 6px 6px 0 0;
    }

    /* Cards e Inputs */
    .stExpander { border: 1px solid #e2e8f0 !important; box-shadow: none !important; }
    .stTextInput>div>div>input { background-color: #f8fafc; border: 1px solid #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Header
st.title("NEXUS | Gestão de Produção")
st.caption("Ambiente Corporativo de Monitoramento Industrial")
st.divider()

# 3. NAVEGAÇÃO
tab_dash, tab_pedido, tab_fabrica, tab_admin = st.tabs([
    "DASHBOARD", "ORDENS DE PRODUÇÃO", "CHÃO DE FÁBRICA", "CADASTROS"
])

# --- DASHBOARD ---
with tab_dash:
    st.subheader("Status das Operações")
    try:
        res = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").execute()
        if res.data:
            df_lista = []
            for item in res.data:
                lp = item['linha_producao'][0] if item.get('linha_producao') else {}
                df_lista.append({
                    "Ordem": item['numero_pedido'],
                    "Projeto": item['projetos']['nome_projeto'] if item.get('projetos') else "Indefinido",
                    "Entrega": item['prazo_entrega'],
                    "Corte": "CONCLUÍDO" if lp.get('corte_fim') else ("EM CURSO" if lp.get('corte_inicio') else "-"),
                    "Solda": "CONCLUÍDO" if lp.get('solda_fim') else ("EM CURSO" if lp.get('solda_inicio') else "-"),
                    "Pintura": "CONCLUÍDO" if lp.get('pintura_fim') else ("EM CURSO" if lp.get('pintura_inicio') else "-")
                })
            st.dataframe(pd.DataFrame(df_lista), use_container_width=True, hide_index=True)
    except:
        st.info("Aguardando sincronização de dados.")

# --- ORDENS DE PRODUÇÃO ---
with tab_pedido:
    st.subheader("Nova Ordem Industrial")
    p_db = supabase.table("projetos").select("id, nome_projeto").execute()
    l_p = {p['nome_projeto']: p['id'] for p in p_db.data}
    
    with st.form("f_pedido"):
        c1, c2 = st.columns(2)
        n_ped = c1.text_input("Identificador do Pedido")
        p_sel = c1.selectbox("Vincular ao Projeto", options=list(l_p.keys()))
        prazo = c2.date_input("Data Prazo")
        doc = st.file_uploader("Upload de Desenho Técnico", type=['pdf', 'dwg', 'jpg', 'png'])
        
        st.markdown("---")
        st.markdown("**Roteiro de Produção**")
        e1, e2, e3 = st.columns(3)
        h_corte = e1.checkbox("Corte a Laser")
        h_dobra = e1.checkbox("Dobra CNC")
        h_solda = e2.checkbox("Soldagem")
        h_meta = e2.checkbox("Metaleira")
        h_calan = e3.checkbox("Calandragem")
        h_galva = e3.checkbox("Galvanização")
        h_pint = e3.checkbox("Pintura")
        
        if st.form_submit_button("VALIDAR E LANÇAR ORDEM"):
            url_f = ""
            if doc:
                path = f"pedidos/{n_ped}_{doc.name}"
                supabase.storage.from_("desenhos").upload(path, doc.getvalue())
                url_f = supabase.storage.from_("desenhos").get_public_url(path)

            dados = {
                "numero_pedido": n_ped, "id_projeto": l_p[p_sel], "prazo_entrega": str(prazo), "arquivo_url": url_f,
                "has_corte_laser": h_corte, "has_dobra_cnc": h_dobra, "has_solda": h_solda,
                "has_metaleira": h_meta, "has_calandragem": h_calan, "has_galvanizacao": h_galva, "has_pintura": h_pint
            }
            res_p = supabase.table("pedidos").insert(dados).execute()
            supabase.table("linha_producao").insert({"id_pedido": res_p.data[0]['id']}).execute()
            st.success("Ordem registrada no sistema.")

# --- CHÃO DE FÁBRICA ---
with tab_fabrica:
    st.subheader("Execução de Processos")
    ativos = supabase.table("pedidos").select("id, numero_pedido, arquivo_url").eq("status_geral", "Em Produção").execute()
    l_a = {p['numero_pedido']: p for p in ativos.data}
    
    if l_a:
        escolha = st.selectbox("Selecione a Ordem:", options=list(l_a.keys()))
        item = l_a[escolha]
        if item['arquivo_url']:
            st.link_button("Visualizar Desenho Técnico", item['arquivo_url'])
        
        det = supabase.table("pedidos").select("*").eq("id", item['id']).single().execute().data
        prod = supabase.table("linha_producao").select("*").eq("id_pedido", item['id']).single().execute().data

        def render(label, campo, hab):
            if hab:
                with st.expander(f"Processo: {label}", expanded=True):
                    c_i, c_f, c_o = st.columns([1, 1, 2])
                    i, f = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                    if not i:
                        if c_i.button(f"Iniciar", key=f"i_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", item['id']).execute()
                            st.rerun()
                    elif not f:
                        c_i.warning(f"Iniciado: {i[11:16]}")
                        obs = c_o.text_input("Notas", key=f"o_{campo}")
                        if c_f.button(f"Concluir", key=f"f_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", item['id']).execute()
                            st.rerun()
                    else:
                        st.success(f"Finalizado: {i[11:16]} - {f[11:16]}")

        render("Corte a Laser", "corte", det['has_corte_laser'])
        render("Soldagem", "solda", det['has_solda'])
        render("Pintura", "pintura", det['has_pintura'])
    else:
        st.info("Nenhuma ordem em andamento.")

# --- CADASTROS ---
with tab_admin:
    st.subheader("Configurações de Dados")
    c1, c2 = st.columns(2)
    with c1:
        with st.form("c_sol"):
            st.markdown("**Novo Solicitante**")
            n = st.text_input("Nome Responsável")
            e = st.text_input("Empresa / Entidade")
            if st.form_submit_button("Cadastrar"):
                supabase.table("solicitantes").insert({"nome": n, "empresa": e}).execute()
                st.success("Registrado.")
    with c2:
        s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
        l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
        with st.form("c_proj"):
            st.markdown("**Novo Projeto**")
            np = st.text_input("Título do Projeto")
            sid = st.selectbox("Solicitante", options=list(l_s.keys()))
            if st.form_submit_button("Vincular"):
                supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid]}).execute()
                st.success("Vinculado.")



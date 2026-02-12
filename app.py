import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONFIGURAÇÕES DE INTERFACE PROFISSIONAL (ENTERPRISE)
st.set_page_config(page_title="NEXUS | Enterprise Resource Planning", layout="wide", initial_sidebar_state="collapsed")

# Injeção de CSS para Visual Corporativo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Configuração Global */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
    .main { background-color: #f8fafc; }
    
    /* Cabeçalhos */
    h1, h2, h3 { color: #0f172a; font-weight: 700; letter-spacing: -0.02em; }
    
    /* Botões Padrão Corporativo */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        height: 45px;
        background-color: #0f172a;
        color: #ffffff;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 0.05em;
    }
    .stButton>button:hover { background-color: #334155; border: none; color: #fff; }
    
    /* Tabelas e Dataframes */
    [data-testid="stDataFrame"] { border: 1px solid #e2e8f0; border-radius: 8px; }
    
    /* Abas de Navegação */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #f8fafc; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px 6px 0 0;
        padding: 10px 30px;
        font-weight: 500;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #0f172a !important;
    }
    
    /* Cards de Informação */
    .stExpander {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cabeçalho Limpo
col_logo, col_title = st.columns([1, 4])
with col_title:
    st.title("NEXUS | Gestão Industrial")
    st.caption("Painel de Controle de Operações e Processos")

# 3. NAVEGAÇÃO ORGANIZADA
tab_dash, tab_pedido, tab_fabrica, tab_cadastro = st.tabs([
    "DASHBOARD", "ORDENS DE PRODUÇÃO", "CHÃO DE FÁBRICA", "ADMINISTRAÇÃO"
])

# --- MÓDULO: DASHBOARD ---
with tab_dash:
    st.subheader("Visão Geral das Operações")
    try:
        res = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").execute()
        if res.data:
            df_lista = []
            for item in res.data:
                lp = item['linha_producao'][0] if item.get('linha_producao') else {}
                df_lista.append({
                    "Pedido": item['numero_pedido'],
                    "Projeto": item['projetos']['nome_projeto'] if item.get('projetos') else "N/A",
                    "Prazo": item['prazo_entrega'],
                    "Status": "CONCLUÍDO" if lp.get('pintura_fim') else "EM CURSO",
                    "Laser": "OK" if lp.get('corte_fim') else ("PEND" if lp.get('corte_inicio') else "-"),
                    "Dobra": "OK" if lp.get('dobra_fim') else ("PEND" if lp.get('dobra_inicio') else "-"),
                    "Solda": "OK" if lp.get('solda_fim') else ("PEND" if lp.get('solda_inicio') else "-"),
                    "Pintura": "OK" if lp.get('pintura_fim') else ("PEND" if lp.get('pintura_inicio') else "-")
                })
            st.dataframe(pd.DataFrame(df_lista), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro ao sincronizar dados: {e}")

# --- MÓDULO: ORDENS DE PRODUÇÃO ---
with tab_pedido:
    st.subheader("Nova Solicitação de Produção")
    projs_db = supabase.table("projetos").select("id, nome_projeto").execute()
    lista_p = {p['nome_projeto']: p['id'] for p in projs_db.data}
    
    with st.form("form_novo_pedido", clear_on_submit=True):
        c1, c2 = st.columns(2)
        num_p = c1.text_input("Identificação do Pedido")
        proj_vinc = c1.selectbox("Projeto de Referência", options=list(lista_p.keys()))
        prazo_e = c2.date_input("Data Limite de Entrega")
        arq = st.file_uploader("Documentação Técnica (PDF/DWG)", type=['pdf', 'jpg', 'png', 'dwg'])
        desc_p = st.text_area("Notas e Especificações")
        
        st.markdown("**Definição de Workflow**")
        e1, e2, e3 = st.columns(3)
        h_corte = e1.checkbox("Corte a Laser")
        h_dobra = e1.checkbox("Dobra CNC")
        h_solda = e2.checkbox("Solda TIG/MIG")
        h_meta = e2.checkbox("Metaleira")
        h_calan = e3.checkbox("Calandragem")
        h_galva = e3.checkbox("Galvanização")
        h_pint = e3.checkbox("Pintura Epóxi")
        
        if st.form_submit_button("REGISTRAR ORDEM"):
            url_final = ""
            if arq:
                path = f"pedidos/{num_p}_{arq.name}"
                supabase.storage.from_("desenhos").upload(path, arq.getvalue())
                url_final = supabase.storage.from_("desenhos").get_public_url(path)

            dados_ins = {
                "numero_pedido": num_p, "id_projeto": lista_p[proj_vinc], "descricao_pedido": desc_p,
                "prazo_entrega": str(prazo_e), "arquivo_url": url_final,
                "has_corte_laser": h_corte, "has_dobra_cnc": h_dobra, "has_solda": h_solda,
                "has_metaleira": h_meta, "has_calandragem": h_calan, "has_galvanizacao": h_galva, "has_pintura": h_pint
            }
            res = supabase.table("pedidos").insert(dados_ins).execute()
            supabase.table("linha_producao").insert({"id_pedido": res.data[0]['id']}).execute()
            st.success("Ordem de produção registrada com sucesso.")

# --- MÓDULO: CHÃO DE FÁBRICA ---
with tab_fabrica:
    st.subheader("Controle de Execução Industrial")
    ativos = supabase.table("pedidos").select("id, numero_pedido, arquivo_url").eq("status_geral", "Em Produção").execute()
    l_ativos = {p['numero_pedido']: p for p in ativos.data}
    
    if l_ativos:
        escolha = st.selectbox("Ordem em Execução:", options=list(l_ativos.keys()))
        dados_f = l_ativos[escolha]
        
        if dados_f['arquivo_url']:
            st.link_button("ACESSAR DOCUMENTAÇÃO TÉCNICA", dados_f['arquivo_url'])
        
        det = supabase.table("pedidos").select("*").eq("id", dados_f['id']).single().execute().data
        prod = supabase.table("linha_producao").select("*").eq("id_pedido", dados_f['id']).single().execute().data

        def render_etapa(label, campo, hab):
            if hab:
                with st.expander(f"Etapa: {label.upper()}", expanded=True):
                    c_i, c_f, c_o = st.columns([1, 1, 2])
                    i, f = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                    if not i:
                        if c_i.button(f"REGISTRAR INÍCIO", key=f"i_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", dados_f['id']).execute()
                            st.rerun()
                    elif not f:
                        c_i.info(f"Iniciado: {i[11:16]}")
                        o_txt = c_o.text_input("Observações de Processo", key=f"o_{campo}")
                        if c_f.button(f"REGISTRAR TÉRMINO", key=f"f_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": o_txt}).eq("id_pedido", dados_f['id']).execute()
                            st.rerun()
                    else:
                        st.success(f"CONCLUÍDO | Ciclo: {i[11:16]} - {f[11:16]}")

        render_etapa("Corte a Laser", "corte", det['has_corte_laser'])
        render_etapa("Dobra CNC", "dobra", det['has_dobra_cnc'])
        render_etapa("Solda", "solda", det['has_solda'])
        render_etapa("Metaleira", "metaleira", det['has_metaleira'])
        render_etapa("Calandragem", "calandragem", det['has_calandragem'])
        render_etapa("Galvanização", "galvanizacao", det['has_galvanizacao'])
        render_etapa("Pintura", "pintura", det['has_pintura'])
    else:
        st.info("Nenhuma ordem ativa no sistema.")

# --- MÓDULO: ADMINISTRAÇÃO ---
with tab_cadastro:
    st.subheader("Gestão de Dados Mestres")
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("Cadastro de Solicitantes", expanded=True):
            with st.form("f_s"):
                n = st.text_input("Nome Responsável")
                e = st.text_input("Entidade / Empresa")
                t = st.text_input("Contato Direto")
                if st.form_submit_button("EFETUAR REGISTRO"):
                    supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t}).execute()
                    st.success("Registro efetuado.")
    with c2:
        with st.expander("Cadastro de Projetos", expanded=True):
            s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
            l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
            with st.form("f_p"):
                np = st.text_input("Título do Projeto")
                sid = st.selectbox("Solicitante Vinculado", options=list(l_s.keys()))
                cid = st.text_input("Localidade / Cidade")
                if st.form_submit_button("VINCULAR PROJETO"):
                    supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid}).execute()
                    st.success("Projeto vinculado.")


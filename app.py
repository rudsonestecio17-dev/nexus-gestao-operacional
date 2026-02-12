import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONFIGURAÇÕES DE INTERFACE PROFISSIONAL (MODO CLARO ENTERPRISE)
st.set_page_config(page_title="NEXUS | ERP", layout="wide", initial_sidebar_state="collapsed")

# CSS para Visual Corporativo Clean
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Configuração Global */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #334155; }
    .main { background-color: #ffffff; }
    
    /* Cabeçalhos */
    h1, h2, h3 { color: #0f172a; font-weight: 700; letter-spacing: -0.02em; }
    
    /* Botões Padrão Corporativo - Azul Marinho */
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        height: 45px;
        background-color: #1e293b;
        color: #ffffff;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 0.05em;
    }
    .stButton>button:hover { background-color: #334155; color: #fff; border: none; }
    
    /* Abas de Navegação - Estilo Moderno Claro */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 10px; 
        background-color: #f8fafc; 
        padding: 10px 10px 0 10px;
        border-bottom: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        padding: 10px 30px;
        font-weight: 500;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
        font-weight: 700;
        border: 1px solid #e2e8f0 !important;
        border-bottom: 2px solid #ffffff !important;
    }
    
    /* Inputs e Cards */
    .stExpander {
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="input"] { background-color: #fcfcfc; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cabeçalho
st.title("NEXUS | Gestão Industrial")
st.caption("Controle Operacional de Processos")
st.divider()

# 3. NAVEGAÇÃO
tab_dash, tab_pedido, tab_fabrica, tab_admin = st.tabs([
    "DASHBOARD", "ORDENS DE PRODUÇÃO", "CHÃO DE FÁBRICA", "ADMINISTRAÇÃO"
])

# --- MÓDULO: DASHBOARD ---
with tab_dash:
    st.subheader("Painel de Acompanhamento")
    try:
        res = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").execute()
        if res.data:
            df_lista = []
            for item in res.data:
                lp = item['linha_producao'][0] if item.get('linha_producao') else {}
                df_lista.append({
                    "Ordem": item['numero_pedido'],
                    "Projeto": item['projetos']['nome_projeto'] if item.get('projetos') else "N/A",
                    "Entrega": item['prazo_entrega'],
                    "Status": "CONCLUÍDO" if lp.get('pintura_fim') else "EM PRODUÇÃO",
                    "Laser": "OK" if lp.get('corte_fim') else ("PROG" if lp.get('corte_inicio') else "-"),
                    "Dobra": "OK" if lp.get('dobra_fim') else ("PROG" if lp.get('dobra_inicio') else "-"),
                    "Solda": "OK" if lp.get('solda_fim') else ("PROG" if lp.get('solda_inicio') else "-"),
                    "Pintura": "OK" if lp.get('pintura_fim') else ("PROG" if lp.get('pintura_inicio') else "-")
                })
            st.dataframe(pd.DataFrame(df_lista), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Erro na sincronização: {e}")

# --- MÓDULO: ORDENS DE PRODUÇÃO ---
with tab_pedido:
    st.subheader("Nova Ordem de Serviço")
    projs_db = supabase.table("projetos").select("id, nome_projeto").execute()
    lista_p = {p['nome_projeto']: p['id'] for p in projs_db.data}
    
    with st.form("form_novo_pedido", clear_on_submit=True):
        c1, c2 = st.columns(2)
        num_p = c1.text_input("Nº da Ordem")
        proj_vinc = c1.selectbox("Projeto de Destino", options=list(lista_p.keys()))
        prazo_e = c2.date_input("Data Prazo")
        arq = st.file_uploader("Documentação Técnica", type=['pdf', 'jpg', 'png', 'dwg'])
        desc_p = st.text_area("Especificações do Pedido")
        
        st.markdown("**Workflow de Produção**")
        e1, e2, e3 = st.columns(3)
        h_corte = e1.checkbox("Corte a Laser")
        h_dobra = e1.checkbox("Dobra CNC")
        h_solda = e2.checkbox("Soldagem")
        h_meta = e2.checkbox("Metaleira")
        h_calan = e3.checkbox("Calandragem")
        h_galva = e3.checkbox("Galvanização")
        h_pint = e3.checkbox("Pintura")
        
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
            st.success("Ordem registrada com sucesso.")

# --- MÓDULO: CHÃO DE FÁBRICA ---
with tab_fabrica:
    st.subheader("Controle de Processos")
    ativos = supabase.table("pedidos").select("id, numero_pedido, arquivo_url").eq("status_geral", "Em Produção").execute()
    l_ativos = {p['numero_pedido']: p for p in ativos.data}
    
    if l_ativos:
        escolha = st.selectbox("Ordem em Operação:", options=list(l_ativos.keys()))
        dados_f = l_ativos[escolha]
        
        if dados_f['arquivo_url']:
            st.link_button("ACESSAR DESENHO TÉCNICO", dados_f['arquivo_url'])
        
        det = supabase.table("pedidos").select("*").eq("id", dados_f['id']).single().execute().data
        prod = supabase.table("linha_producao").select("*").eq("id_pedido", dados_f['id']).single().execute().data

        def render_etapa(label, campo, hab):
            if hab:
                with st.expander(f"PROCESSO: {label.upper()}", expanded=True):
                    c_i, c_f, c_o = st.columns([1, 1, 2])
                    i, f = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                    if not i:
                        if c_i.button(f"INICIAR", key=f"i_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", dados_f['id']).execute()
                            st.rerun()
                    elif not f:
                        c_i.info(f"Início: {i[11:16]}")
                        o_txt = c_o.text_input("Obs Técnica", key=f"o_{campo}")
                        if c_f.button(f"FINALIZAR", key=f"f_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": o_txt}).eq("id_pedido", dados_f['id']).execute()
                            st.rerun()
                    else:
                        st.success(f"CONCLUÍDO | {i[11:16]} - {f[11:16]}")

        render_etapa("Corte a Laser", "corte", det['has_corte_laser'])
        render_etapa("Dobra CNC", "dobra", det['has_dobra_cnc'])
        render_etapa("Solda", "solda", det['has_solda'])
        render_etapa("Metaleira", "metaleira", det['has_metaleira'])
        render_etapa("Calandragem", "calandragem", det['has_calandragem'])
        render_etapa("Galvanização", "galvanizacao", det['has_galvanizacao'])
        render_etapa("Pintura", "pintura", det['has_pintura'])
    else:
        st.info("Nenhuma ordem ativa para execução.")

# --- MÓDULO: ADMINISTRAÇÃO ---
with tab_admin:
    st.subheader("Dados Mestres")
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("Registro de Solicitante", expanded=True):
            with st.form("f_s"):
                n = st.text_input("Responsável")
                e = st.text_input("Empresa")
                t = st.text_input("Telefone")
                if st.form_submit_button("REGISTRAR"):
                    supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t}).execute()
                    st.success("Salvo.")
    with c2:
        with st.expander("Registro de Projeto", expanded=True):
            s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
            l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
            with st.form("f_p"):
                np = st.text_input("Título do Projeto")
                sid = st.selectbox("Solicitante", options=list(l_s.keys()))
                cid = st.text_input("Cidade")
                if st.form_submit_button("VINCULAR"):
                    supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid}).execute()
                    st.success("Vinculado.")


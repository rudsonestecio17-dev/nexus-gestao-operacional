import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# 1. CONFIGURAÇÕES DE INTERFACE PROFISSIONAL
st.set_page_config(page_title="NEXUS OPERACIONAL", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #0f172a; color: white; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #1e293b; transform: translateY(-1px); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    div[data-testid="stExpander"] { border: 1px solid #e2e8f0; border-radius: 12px; background-color: white; margin-bottom: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f5f9; border-radius: 8px 8px 0 0; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #0f172a !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO COM O SUPABASE
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🏗️ NEXUS | Gestão de Produção Industrial")
st.caption("Sistema Integrado de Controle de Fluxo e Chão de Fábrica")

# 3. NAVEGAÇÃO POR ABAS
tab_dash, tab_pedido, tab_fabrica, tab_cadastro = st.tabs([
    "📊 DASHBOARD GERAL", "📝 NOVO PEDIDO", "🏭 CHÃO DE FÁBRICA", "👥 CADASTROS BASE"
])

# --- ABA 1: DASHBOARD ---
with tab_dash:
    st.subheader("📊 Monitoramento de Pedidos")
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
                    "Status": "Finalizado" if lp.get('pintura_fim') else "Em Produção",
                    "Corte": "✅" if lp.get('corte_fim') else ("⏳" if lp.get('corte_inicio') else "-"),
                    "Dobra": "✅" if lp.get('dobra_fim') else ("⏳" if lp.get('dobra_inicio') else "-"),
                    "Solda": "✅" if lp.get('solda_fim') else ("⏳" if lp.get('solda_inicio') else "-"),
                    "Pintura": "✅" if lp.get('pintura_fim') else ("⏳" if lp.get('pintura_inicio') else "-"),
                })
            st.dataframe(pd.DataFrame(df_lista), use_container_width=True, hide_index=True)
        else:
            st.info("Aguardando inserção de pedidos.")
    except Exception as e:
        st.error(f"Erro ao carregar Dashboard: {e}")

# --- ABA 2: NOVO PEDIDO ---
with tab_pedido:
    st.subheader("📝 Abertura de Ordem de Produção")
    projs_db = supabase.table("projetos").select("id, nome_projeto").execute()
    lista_p = {p['nome_projeto']: p['id'] for p in projs_db.data}
    
    if not lista_p:
        st.warning("Cadastre um Projeto na aba 'Cadastros' antes de gerar um pedido.")
    else:
        with st.form("form_novo_pedido", clear_on_submit=True):
            col1, col2 = st.columns(2)
            num_p = col1.text_input("Número do Pedido (Ex: PED-100)")
            proj_vinc = col1.selectbox("Projeto Responsável", options=list(lista_p.keys()))
            prazo_e = col2.date_input("Prazo de Entrega Estimado")
            arq = st.file_uploader("📁 Anexar Desenho Técnico", type=['pdf', 'jpg', 'png', 'dwg'])
            desc_p = st.text_area("Descrição Geral do Pedido")
            
            st.markdown("#### ⚙️ Definir Roteiro de Produção")
            c1, c2, c3 = st.columns(3)
            h_corte = c1.checkbox("Corte a Laser")
            h_dobra = c1.checkbox("Dobra CNC")
            h_solda = c2.checkbox("Solda")
            h_meta = c2.checkbox("Metaleira")
            h_calan = c3.checkbox("Calandragem")
            h_galva = c3.checkbox("Galvanização")
            h_pint = c3.checkbox("Pintura")
            
            if st.form_submit_button("🚀 LANÇAR NA PRODUÇÃO"):
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
                st.success(f"Pedido {num_p} cadastrado e enviado para a fábrica!")

# --- ABA 3: CHÃO DE FÁBRICA ---
with tab_fabrica:
    st.subheader("🏭 Painel do Operador")
    ativos = supabase.table("pedidos").select("id, numero_pedido, arquivo_url").eq("status_geral", "Em Produção").execute()
    l_ativos = {p['numero_pedido']: p for p in ativos.data}
    
    if l_ativos:
        escolha = st.selectbox("Selecione o Pedido em Execução", options=list(l_ativos.keys()))
        dados_f = l_ativos[escolha]
        
        if dados_f['arquivo_url']:
            st.link_button("📂 VISUALIZAR DESENHO TÉCNICO", dados_f['arquivo_url'])
        
        det = supabase.table("pedidos").select("*").eq("id", dados_f['id']).single().execute().data
        prod = supabase.table("linha_producao").select("*").eq("id_pedido", dados_f['id']).single().execute().data

        def render_etapa(label, campo, hab):
            if hab:
                with st.expander(f"🛠️ {label}", expanded=True):
                    c_i, c_f, c_o = st.columns([1, 1, 2])
                    i, f = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                    if not i:
                        if c_i.button(f"Iniciar", key=f"btn_i_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", dados_f['id']).execute()
                            st.rerun()
                    elif not f:
                        c_i.warning(f"Iniciado: {i[11:16]}")
                        o_txt = c_o.text_input("Observação técnica", key=f"o_{campo}")
                        if c_f.button(f"Finalizar", key=f"btn_f_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": o_txt}).eq("id_pedido", dados_f['id']).execute()
                            st.rerun()
                    else:
                        st.success(f"Concluído ({i[11:16]} - {f[11:16]})")
                        if prod.get(f"{campo}_obs"): st.caption(f"Nota: {prod.get(f'{campo}_obs')}")

        render_etapa("Corte a Laser", "corte", det['has_corte_laser'])
        render_etapa("Dobra CNC", "dobra", det['has_dobra_cnc'])
        render_etapa("Solda", "solda", det['has_solda'])
        render_etapa("Metaleira", "metaleira", det['has_metaleira'])
        render_etapa("Calandragem", "calandragem", det['has_calandragem'])
        render_etapa("Galvanização", "galvanizacao", det['has_galvanizacao'])
        render_etapa("Pintura", "pintura", det['has_pintura'])
    else:
        st.info("Nenhum pedido ativo na linha de produção.")

# --- ABA 4: CADASTROS BASE ---
with tab_cadastro:
    st.subheader("👥 Gestão de Clientes e Projetos")
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("👤 Cadastrar Solicitante", expanded=True):
            with st.form("f_s"):
                n = st.text_input("Nome")
                e = st.text_input("Empresa")
                t = st.text_input("WhatsApp")
                obs_s = st.text_area("Info Adicional")
                if st.form_submit_button("SALVAR"):
                    supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t, "info_adicional": obs_s}).execute()
                    st.success("Cadastrado!")
    with c2:
        with st.expander("📍 Cadastrar Projeto", expanded=True):
            s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
            l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
            with st.form("f_p"):
                np = st.text_input("Nome do Projeto")
                sid = st.selectbox("Solicitante", options=list(l_s.keys()))
                cid = st.text_input("Cidade")
                end = st.text_input("Endereço")
                if st.form_submit_button("VINCULAR"):
                    supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": end}).execute()
                    st.success("Projeto Ativo!")


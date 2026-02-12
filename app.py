import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONFIGURAÇÕES DE LAYOUT E ESTILO (VIBE EMPRESARIAL)
st.set_page_config(page_title="NEXUS OPERACIONAL", layout="wide", initial_sidebar_state="collapsed")

# Injeção de CSS para um visual limpo e moderno
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #0f172a; color: white; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #1e293b; transform: translateY(-2px); }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { border-radius: 8px !important; }
    div[data-testid="stExpander"] { border: 1px solid #e2e8f0; border-radius: 12px; background-color: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .status-card { padding: 20px; border-radius: 10px; background-color: white; border-left: 5px solid #0f172a; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO SUPABASE
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("🏗️ NEXUS | Gestão de Produção")
st.markdown("---")

# 3. NAVEGAÇÃO POR ABAS (ORGANIZAÇÃO PROFISSIONAL)
tab_dash, tab_pedido, tab_fabrica, tab_cadastro = st.tabs([
    "📊 Dashboard", "📝 Novo Pedido", "🏭 Chão de Fábrica", "👥 Cadastros"
])

# --- ABA: DASHBOARD ---
with tab_dash:
    st.subheader("📊 Monitoramento em Tempo Real")
    try:
        res = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").execute()
        if res.data:
            df_lista = []
            for item in res.data:
                lp = item['linha_producao'][0] if item.get('linha_producao') else {}
                nome_proj = item['projetos']['nome_projeto'] if item.get('projetos') else "N/A"
                status_atual = "Finalizado" if lp.get('pintura_fim') else "Em Produção"
                
                df_lista.append({
                    "Pedido": item['numero_pedido'],
                    "Projeto": nome_proj,
                    "Prazo": item['prazo_entrega'],
                    "Status": status_atual,
                    "Corte": "✅" if lp.get('corte_fim') else ("⏳" if lp.get('corte_inicio') else "-"),
                    "Dobra": "✅" if lp.get('dobra_fim') else ("⏳" if lp.get('dobra_inicio') else "-"),
                    "Solda": "✅" if lp.get('solda_fim') else ("⏳" if lp.get('solda_inicio') else "-"),
                    "Pintura": "✅" if lp.get('pintura_fim') else ("⏳" if lp.get('pintura_inicio') else "-")
                })
            st.dataframe(pd.DataFrame(df_lista), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum pedido encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

# --- ABA: NOVO PEDIDO ---
with tab_pedido:
    st.subheader("📋 Lançar Nova Ordem")
    projs_db = supabase.table("projetos").select("id, nome_projeto").execute()
    lista_p = {p['nome_projeto']: p['id'] for p in projs_db.data}
    
    with st.form("form_pedido_novo"):
        c1, c2 = st.columns(2)
        n_ped = c1.text_input("Número do Pedido")
        p_sel = c1.selectbox("Projeto Vinculado", options=list(lista_p.keys()))
        prazo = c2.date_input("Prazo de Entrega")
        desc = c2.text_area("Descrição do Pedido")
        
        st.markdown("#### 🛠️ Etapas do Fluxo")
        e1, e2, e3 = st.columns(3)
        h_corte = e1.checkbox("Corte a Laser")
        h_dobra = e1.checkbox("Dobra CNC")
        h_solda = e2.checkbox("Solda")
        h_meta = e2.checkbox("Metaleira")
        h_calan = e3.checkbox("Calandragem")
        h_galva = e3.checkbox("Galvanização")
        h_pint = e3.checkbox("Pintura")
        
        if st.form_submit_button("🚀 GERAR ORDEM DE PRODUÇÃO"):
            dados_p = {
                "numero_pedido": n_ped, "id_projeto": lista_p[p_sel], "descricao_pedido": desc, "prazo_entrega": str(prazo),
                "has_corte_laser": h_corte, "has_dobra_cnc": h_dobra, "has_solda": h_solda,
                "has_metaleira": h_meta, "has_calandragem": h_calan, "has_galvanizacao": h_galva, "has_pintura": h_pint
            }
            res_p = supabase.table("pedidos").insert(dados_p).execute()
            supabase.table("linha_producao").insert({"id_pedido": res_p.data[0]['id']}).execute()
            st.success("✅ Pedido enviado com sucesso!")

# --- ABA: CHÃO DE FÁBRICA ---
with tab_fabrica:
    st.subheader("🏭 Painel de Execução")
    ativos = supabase.table("pedidos").select("id, numero_pedido").eq("status_geral", "Em Produção").execute()
    l_ativos = {p['numero_pedido']: p['id'] for p in ativos.data}
    
    if l_ativos:
        p_foco = st.selectbox("Selecione o Pedido", options=list(l_ativos.keys()))
        id_f = l_ativos[p_foco]
        det = supabase.table("pedidos").select("*").eq("id", id_f).single().execute().data
        prod = supabase.table("linha_producao").select("*").eq("id_pedido", id_f).single().execute().data

        def render_etapa(label, campo, habilitado):
            if habilitado:
                with st.expander(f"⚙️ {label}", expanded=True):
                    c_i, c_f, c_o = st.columns([1, 1, 2])
                    ini, fim = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                    if not ini:
                        if c_i.button(f"Iniciar", key=f"btn_i_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", id_f).execute()
                            st.rerun()
                    elif not fim:
                        c_i.info(f"⏳ {ini[11:16]}")
                        obs = c_o.text_input("Observação", key=f"obs_{campo}")
                        if c_f.button(f"Concluir", key=f"btn_f_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", id_f).execute()
                            st.rerun()
                    else:
                        st.success(f"✅ Finalizado às {fim[11:16]}")

        # Listagem das 7 etapas conforme original
        render_etapa("Corte a Laser", "corte", det['has_corte_laser'])
        render_etapa("Dobra CNC", "dobra", det['has_dobra_cnc'])
        render_etapa("Solda", "solda", det['has_solda'])
        render_etapa("Metaleira", "metaleira", det['has_metaleira'])
        render_etapa("Calandragem", "calandragem", det['has_calandragem'])
        render_etapa("Galvanização", "galvanizacao", det['has_galvanizacao'])
        render_etapa("Pintura", "pintura", det['has_pintura'])
    else:
        st.info("Nenhum pedido em produção.")

# --- ABA: CADASTROS ---
with tab_cadastro:
    st.subheader("👥 Gestão de Cadastros")
    c1, c2 = st.columns(2)
    
    with c1:
        with st.expander("👤 Solicitantes", expanded=True):
            with st.form("f_sol"):
                n = st.text_input("Nome")
                e = st.text_input("Empresa")
                t = st.text_input("WhatsApp")
                if st.form_submit_button("Salvar Solicitante"):
                    supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t}).execute()
                    st.success("Salvo!")
                    
    with c2:
        with st.expander("📍 Projetos", expanded=True):
            s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
            l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
            with st.form("f_proj"):
                np = st.text_input("Nome do Projeto")
                sel_s = st.selectbox("Solicitante", options=list(l_s.keys()))
                if st.form_submit_button("Vincular Projeto"):
                    supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sel_s]}).execute()
                    st.success("Vinculado!")


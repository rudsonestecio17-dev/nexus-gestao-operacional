import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONFIGURAÇÕES SOLLUZ SYSTEMS (DESIGN PREMIUM DARK)
st.set_page_config(page_title="Solluz systems | ERP", layout="wide", initial_sidebar_state="collapsed")

# 2. CONEXÃO SUPABASE
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# URL DA LOGO OFICIAL (Conforme enviado)
LOGO_URL = "https://i.ibb.co/6Lr0QZY/nexus-2.png"

# CSS PREMIUM SOLLUZ (Azul Cyan & Deep Dark)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    .stApp { background-color: #0d1117 !important; color: #e6edf3 !important; font-family: 'Inter', sans-serif !important; }
    
    /* Abas Customizadas Solluz */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px; background-color: #161b22; padding: 10px 10px 0 10px; border-radius: 12px 12px 0 0; 
        border: 1px solid #30363d; border-bottom: none; 
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px; background-color: #21262d; border: 1px solid #30363d; color: #8b949e; 
        border-radius: 8px 8px 0 0; padding: 0 25px; font-size: 11px; text-transform: uppercase; font-weight: 700; 
    }
    .stTabs [aria-selected="true"] {
        background-color: #0d1117 !important; color: #3b82f6 !important; 
        border: 1px solid #3b82f6 !important; border-bottom: 2px solid #0d1117 !important; 
    }

    /* Cards Monitor TV Estilo Painel de Comando */
    .row-monitor {
        background: #161b22; border-radius: 14px; padding: 25px; margin-bottom: 15px; 
        border: 1px solid #30363d; border-left: 8px solid #3b82f6; 
        display: flex; justify-content: space-between; align-items: center; 
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
    }
    
    .id-site { font-size: 1.5em; font-weight: 800; color: #ffffff; margin: 0; }
    .dot { height: 18px; width: 18px; border-radius: 50%; display: inline-block; margin: 5px auto; border: 2px solid #0d1117; }
    .bg-success { background-color: #238636; box-shadow: 0 0 14px rgba(35, 134, 54, 0.7); }
    .bg-danger { background-color: #da3633; box-shadow: 0 0 10px rgba(218, 54, 51, 0.4); }
    .label-etapa { font-size: 10px; color: #8b949e; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; }
    
    /* Botões Premium Solluz */
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 48px; background-color: #1e293b; 
        color: white; font-weight: 700; text-transform: uppercase; border: 1px solid #30363d; transition: 0.2s; 
    }
    .stButton>button:hover { background-color: #3b82f6; border-color: #3b82f6; color: #ffffff; }
    
    /* Expander e Inputs */
    .stExpander { background-color: #161b22 !important; border-color: #30363d !important; border-radius: 10px !important; }
    input, select, textarea { background-color: #161b22 !important; color: white !important; border: 1px solid #30363d !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE SESSÃO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

def tela_login():
    st.markdown(f"<div style='text-align: center; margin-bottom: 30px;'><h1 style='color: #3b82f6; font-size: 2.8em;'>Solluz systems</h1><caption style='color: #8b949e;'>CENTRO DE CONTROLE INDUSTRIAL</caption></div>", unsafe_allow_html=True)
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
        st.image(LOGO_URL, width=180)
        st.write(f"Conectado: **{st.session_state.user_name.upper()}**")
        if st.button("Sair do Sistema"):
            st.session_state.autenticado = False
            st.rerun()

    st.title("Solluz systems | Gestão Industrial")
    st.divider()

    # ABAS ADMIN (6 ABAS COMPLETAS)
    if st.session_state.perfil == "admin":
        tab_dash, tab_comercial, tab_pedido, tab_fabrica, tab_tv, tab_admin = st.tabs([
            "📊 Dashboard", "💰 Comercial", "🏗️ Workflow OS", "⚙️ Chão de Fábrica", "📺 Monitor TV", "👥 ADMIN"
        ])
    else:
        tab_fabrica = st.tabs(["CHÃO DE FÁBRICA"])[0]
        tab_dash = tab_comercial = tab_pedido = tab_tv = tab_admin = None

    # --- MÓDULO: DASHBOARD ---
    if tab_dash:
        with tab_dash:
            st.subheader("Painel de Indicadores Gerais")
            res = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").execute()
            if res.data:
                df_l = []
                for i in res.data:
                    lp = i['linha_producao'][0] if i.get('linha_producao') else {}
                    df_l.append({
                        "Ordem": i['numero_pedido'], "Projeto": i['projetos']['nome_projeto'] if i.get('projetos') else "N/A",
                        "Entrega": i['prazo_entrega'], "Status": i['status_geral'],
                        "Corte": "OK" if lp.get('corte_fim') else ("..." if lp.get('corte_inicio') else "-"),
                        "Solda": "OK" if lp.get('solda_fim') else ("..." if lp.get('solda_inicio') else "-"),
                        "Pintura": "OK" if lp.get('pintura_fim') else ("..." if lp.get('pintura_inicio') else "-")
                    })
                st.dataframe(pd.DataFrame(df_l), use_container_width=True, hide_index=True)

    # --- MÓDULO: COMERCIAL ---
    if tab_comercial:
        with tab_comercial:
            st.subheader("Gestão Comercial e Orçamentos")
            with st.expander("📝 Cadastrar Novo Orçamento", expanded=True):
                p_db = supabase.table("projetos").select("id, nome_projeto").execute()
                l_p = {p['nome_projeto']: p['id'] for p in p_db.data}
                with st.form("form_comercial"):
                    c1, c2 = st.columns(2)
                    n_o = c1.text_input("Identificador do Orçamento")
                    p_o = c1.selectbox("Projeto Vinculado", options=list(l_p.keys()))
                    v_o = c2.number_input("Valor Estimado (R$)", min_value=0.0, format="%.2f")
                    d_e = c2.date_input("Prazo de Entrega Estimado")
                    if st.form_submit_button("CADASTRAR ORÇAMENTO"):
                        dados = {"numero_pedido": n_o, "id_projeto": l_p[p_o], "valor_orcamento": v_o, "prazo_entrega": str(d_e), "status_geral": "EXECUTANDO ORÇAMENTO"}
                        r = supabase.table("pedidos").insert(dados).execute()
                        supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                        st.success("Orçamento Cadastrado com Sucesso!")

            st.divider()
            st.subheader("⚙️ Fluxo Comercial e Aprovações")
            p_com = supabase.table("pedidos").select("*").neq("status_geral", "CONCLUÍDO").execute()
            for p in p_com.data:
                with st.expander(f"Pedido: {p['numero_pedido']} | Status: {p['status_geral']}"):
                    col1, col2 = st.columns(2)
                    pv_in = col1.text_input("Nº PV (Pedido de Venda)", value=p.get('num_pv', ''), key=f"pv_{p['id']}")
                    po_in = col2.text_input("Nº PO (Ordem de Compra)", value=p.get('num_po', ''), key=f"po_{p['id']}")
                    if st.button("ATUALIZAR STATUS COMERCIAL", key=f"upd_{p['id']}"):
                        n_stat = p['status_geral']
                        if pv_in and not po_in: n_stat = "ORÇAMENTO APROVADO"
                        if po_in: n_stat = "EM PRODUÇÃO"
                        supabase.table("pedidos").update({"num_pv": pv_in, "num_po": po_in, "status_geral": n_stat}).eq("id", p['id']).execute()
                        st.rerun()

    # --- MÓDULO: ORDENS DE PRODUÇÃO (WORKFLOW) ---
    if tab_pedido:
        with tab_pedido:
            st.subheader("Configuração de Workflow Técnico")
            p_wf = supabase.table("pedidos").select("*").eq("status_geral", "EM PRODUÇÃO").execute()
            if p_wf.data:
                sel = st.selectbox("Selecione a Ordem para configurar", options=[p['numero_pedido'] for p in p_wf.data])
                id_w = next(item['id'] for item in p_wf.data if item['numero_pedido'] == sel)
                with st.form("f_workflow"):
                    arq = st.file_uploader("Documentação Técnica", type=['pdf', 'jpg', 'png', 'dwg'])
                    st.markdown("**Checklist de Etapas Industriais**")
                    e1, e2, e3 = st.columns(3)
                    h_c, h_d = e1.checkbox("Corte a Laser"), e1.checkbox("Dobra CNC")
                    h_s, h_m = e2.checkbox("Soldagem"), e2.checkbox("Metaleira")
                    h_ca, h_g, h_pi = e3.checkbox("Calandragem"), e3.checkbox("Galvanização"), e3.checkbox("Pintura")
                    if st.form_submit_button("REGISTRAR CONFIGURAÇÃO"):
                        url = ""
                        if arq:
                            path = f"pedidos/{sel}_{arq.name}"
                            supabase.storage.from_("desenhos").upload(path, arq.getvalue(), {"upsert": "true"})
                            url = supabase.storage.from_("desenhos").get_public_url(path)
                        upd = {"arquivo_url": url, "has_corte_laser": h_c, "has_dobra_cnc": h_d, "has_solda": h_s, "has_metaleira": h_m, "has_calandragem": h_ca, "has_galvanizacao": h_g, "has_pintura": h_pi}
                        supabase.table("pedidos").update(upd).eq("id", id_w).execute()
                        st.success("Workflow Configurado!")
            else: st.info("Nenhuma OS em produção pendente de configuração.")

    # --- MÓDULO: CHÃO DE FÁBRICA (7 ETAPAS COMPLETAS) ---
    with tab_fabrica:
        st.subheader("Controle de Processos Industrial")
        atv = supabase.table("pedidos").select("id, numero_pedido, arquivo_url").eq("status_geral", "EM PRODUÇÃO").execute()
        l_atv = {p['numero_pedido']: p for p in atv.data}
        if l_atv:
            escolha = st.selectbox("OS em Execução:", list(l_atv.keys()))
            item = l_atv[escolha]
            if item['arquivo_url']: st.link_button("📂 VISUALIZAR DESENHO TÉCNICO", item['arquivo_url'], use_container_width=True)
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
                            c1.info(f"Iniciado: {i[11:16]}")
                            obs = c3.text_input("Obs Técnica", key=f"o_{campo}")
                            if c2.button("FINALIZAR", key=f"f_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", item['id']).execute()
                                st.rerun()
                        else: st.success(f"CONCLUÍDO | {i[11:16]} - {f[11:16]}")

            # AS 7 ETAPAS RESTAURADAS
            render_etapa("Corte a Laser", "corte", det['has_corte_laser'])
            render_etapa("Dobra CNC", "dobra", det['has_dobra_cnc'])
            render_etapa("Soldagem", "solda", det['has_solda'])
            render_etapa("Metaleira", "metaleira", det['has_metaleira'])
            render_etapa("Calandragem", "calandragem", det['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", det['has_galvanizacao'])
            render_etapa("Pintura", "pintura", det['has_pintura'])
        else: st.info("Sem ordens ativas.")

    # --- MONITOR TV ---
    if tab_tv:
        with tab_tv:
            res_tv = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
            for obra in res_tv.data:
                lp = obra['linha_producao'][0] if obra.get('linha_producao') else {}
                st.markdown(f"<div class='row-monitor'><div style='flex: 1;'><div class='id-site'>{obra['numero_pedido']}</div><div style='font-size: 0.8em; color: #8b949e;'>{obra['projetos']['nome_projeto']}</div></div><div style='flex: 2; display: flex; justify-content: space-around;'><div class='step-unit'><div class='label-etapa'>Corte</div><div class='dot {'bg-success' if lp.get('corte_fim') else 'bg-danger'}'></div></div><div class='step-unit'><div class='label-etapa'>Dobra</div><div class='dot {'bg-success' if lp.get('dobra_fim') else 'bg-danger'}'></div></div><div class='step-unit'><div class='label-etapa'>Solda</div><div class='dot {'bg-success' if lp.get('solda_fim') else 'bg-danger'}'></div></div><div class='step-unit'><div class='label-etapa'>Pintura</div><div class='dot {'bg-success' if lp.get('pintura_fim') else 'bg-danger'}'></div></div></div></div>", unsafe_allow_html=True)

    # --- ADMINISTRAÇÃO (DADOS MESTRES COMPLETOS) ---
    if tab_admin:
        with tab_admin:
            c1, c2 = st.columns(2)
            with c1:
                with st.expander("Registro de Solicitante", expanded=True):
                    with st.form("c_sol"):
                        n, e, t = st.text_input("Responsável Solluz"), st.text_input("Empresa Cliente"), st.text_input("Telefone")
                        obs = st.text_area("Notas Adicionais (Endereços, etc)")
                        if st.form_submit_button("SALVAR"):
                            supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t, "info_adicional": obs}).execute()
                            st.success("Salvo!")
            with c2:
                with st.expander("Registro de Projeto", expanded=True):
                    s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
                    l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
                    with st.form("c_proj"):
                        np, sid, cid = st.text_input("Título"), st.selectbox("Solicitante", options=list(l_s.keys())), st.text_input("Cidade")
                        end, num, cep = st.text_input("Endereço Completo"), st.text_input("Nº"), st.text_input("CEP")
                        if st.form_submit_button("VINCULAR PROJETO"):
                            supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": end, "numero": num, "cep": cep}).execute()
                            st.success("Vinculado!")



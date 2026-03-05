import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONFIGURAÇÕES SOLLUZ SYSTEMS (DESIGN PREMIUM DARK)
st.set_page_config(page_title="Solluz systems | ERP", layout="wide", initial_sidebar_state="collapsed")

# 2. CONEXÃO SUPABASE
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# URL DA LOGO (Substitua pelo link direto da sua imagem da Solluz)
LOGO_URL = "https://i.ibb.co/6Lr0QZY/nexus-2.png" # Se não tiver link, manteremos o texto.

# CSS AVANÇADO SOLLUZ (Deep Dark & Cyan Control)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Global Deep Dark */
    .stApp { background-color: #0d1117 !important; color: #e6edf3 !important; font-family: 'Inter', sans-serif !important; }
    h1, h2, h3, h4 { color: #ffffff !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
    
    /* Abas Customizadas Solluz (Glassmorphism Control) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 8px; background-color: #161b22; padding: 10px 10px 0 10px; border-radius: 12px 12px 0 0; 
        border: 1px solid #30363d; border-bottom: none; 
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px; background-color: #21262d; border: 1px solid #30363d; color: #8b949e; 
        border-radius: 8px 8px 0 0; padding: 0 25px; transition: 0.2s; font-size: 11px; text-transform: uppercase; font-weight: 700; 
    }
    .stTabs [aria-selected="true"] {
        background-color: #0d1117 !important; color: #3b82f6 !important; 
        border: 1px solid #3b82f6 !important; border-bottom: 2px solid #0d1117 !important; 
    }
    .stTabs [data-baseweb="tab"]:hover { border-color: #3b82f6; color: white; }

    /* Cards do Monitor TV (Estilo Painel de Comando) */
    .row-monitor {
        background: #161b22; border-radius: 14px; padding: 25px; margin-bottom: 15px; 
        border: 1px solid #30363d; border-left: 8px solid #3b82f6; 
        display: flex; justify-content: space-between; align-items: center; 
        box-shadow: 0 6px 15px rgba(0,0,0,0.3); transition: transform 0.2s; 
    }
    .row-monitor:hover { border-color: #3b82f6; transform: translateY(-2px); }
    
    .id-site { font-size: 1.5em; font-weight: 800; color: #ffffff; margin: 0; }
    .os-label { color: #3b82f6; font-family: 'Courier New', monospace; font-weight: bold; font-size: 0.9em; }
    
    /* Dots e Linhas de Fluxo com Brilho (Glow) */
    .step-unit { text-align: center; position: relative; min-width: 65px; }
    .dot { 
        height: 20px; width: 20px; border-radius: 50%; display: inline-block; 
        margin: 6px auto; border: 3px solid #0d1117; 
    }
    .bg-success { background-color: #238636; box-shadow: 0 0 14px rgba(35, 134, 54, 0.7); }
    .bg-danger { background-color: #da3633; box-shadow: 0 0 10px rgba(218, 54, 51, 0.4); }
    .label-etapa { font-size: 11px; color: #8b949e; text-transform: uppercase; font-weight: 700; letter-spacing: 1.2px; }
    
    /* Botões Premium Solluz */
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 48px; 
        background-color: #1e293b; color: white; font-weight: 700; 
        text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; 
        border: 1px solid #30363d; transition: all 0.2s; 
    }
    .stButton>button:hover { background-color: #3b82f6; border-color: #3b82f6; color: #0d1117; }
    
    /* Formulários e Inputs Dark */
    .stExpander { background-color: #161b22 !important; border-color: #30363d !important; border-radius: 10px !important; }
    input, select, textarea { background-color: #161b22 !important; color: white !important; border: 1px solid #30363d !important; border-radius: 6px !important; }
    input:focus, select:focus, textarea:focus { border-color: #3b82f6 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE SESSÃO E LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

def tela_login():
    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1 style='color: #3b82f6; font-size: 2.8em;'>Solluz systems</h1>
            <caption style='color: #8b949e;'>CENTRO DE CONTROLE DE PRODUÇÃO</caption>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("Usuário Mestre")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("CONECTAR"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.perfil = res.data[0]['perfil']
                    st.session_state.user_name = res.data[0]['login']
                    st.rerun()
                else: st.error("Acesso bloqueado. Verifique as credenciais.")

if not st.session_state.autenticado:
    tela_login()
else:
    # --- INTERFACE PRINCIPAL ---
    # Menu Lateral com Logo
    with st.sidebar:
        if LOGO_URL == "https://i.ibb.co/6Lr0QZY/nexus-2.png":
            st.markdown("<h2 style='text-align: center; color: #3b82f6;'>SOLLUZ</h2>", unsafe_allow_html=True)
        else:
            st.image(LOGO_URL, width=150)
            
        st.markdown("<h4 style='text-align: center; margin-bottom: 0;'>Solluz</h4>", unsafe_allow_html=True)
        st.caption(f"<div style='text-align: center; color: #8b949e; margin-top: -5px;'>Usuário: {st.session_state.user_name.upper()} ({st.session_state.perfil})</div>", unsafe_allow_html=True)
        if st.button("Logout da Fábrica"):
            st.session_state.autenticado = False
            st.rerun()

    st.title("Solluz systems | Gestão Industrial")
    st.caption("Controle Operacional e Monitoramento de Produção C-Metal")
    st.divider()

    # Define visibilidade das abas conforme perfil
    if st.session_state.perfil == "admin":
        tab_dash, tab_comercial, tab_pedido, tab_fabrica, tab_tv, tab_admin = st.tabs([
            "Dashboard", "Comercial", "Workflow OS", "Chão de Fábrica", "Monitor TV", "ADMIN"
        ])
    else:
        # Perfil Produção cai direto no Chão de Fábrica
        tab_fabrica = st.tabs(["CHÃO DE FÁBRICA"])[0]
        tab_dash = tab_comercial = tab_pedido = tab_tv = tab_admin = None

    # --- MÓDULO: DASHBOARD ---
    if tab_dash:
        with tab_dash:
            st.subheader("Painel de Indicadores Gerais")
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
                            "Status": item['status_geral'],
                            "Corte": "OK" if lp.get('corte_fim') else ("PROG" if lp.get('corte_inicio') else "-"),
                            "Solda": "OK" if lp.get('solda_fim') else ("PROG" if lp.get('solda_inicio') else "-"),
                            "Pintura": "OK" if lp.get('pintura_fim') else ("PROG" if lp.get('pintura_inicio') else "-")
                        })
                    st.dataframe(pd.DataFrame(df_lista), use_container_width=True, hide_index=True)
            except Exception as e: st.error(f"Erro no Dashboard: {e}")

    # --- MÓDULO: COMERCIAL ---
    if tab_comercial:
        with tab_comercial:
            st.subheader("Gestão de Orçamentos e Aprovações")
            with st.expander("📝 Lançar Novo Orçamento", expanded=True):
                projs_db = supabase.table("projetos").select("id, nome_projeto").execute()
                lista_p = {p['nome_projeto']: p['id'] for p in projs_db.data}
                with st.form("form_comercial"):
                    c1, c2 = st.columns(2)
                    n_orc = c1.text_input("Identificador")
                    p_orc = c1.selectbox("Vincular ao Projeto", options=list(lista_p.keys()))
                    v_orc = c2.number_input("Valor Estimado (R$)", min_value=0.0, format="%.2f")
                    p_est = c2.date_input("Prazo de Entrega Estimado")
                    if st.form_submit_button("CADASTRAR ORÇAMENTO COMERCIAL"):
                        dados_c = {"numero_pedido": n_orc, "id_projeto": lista_p[p_orc], "valor_orcamento": v_orc, "prazo_entrega": str(p_est), "status_geral": "EXECUTANDO ORÇAMENTO"}
                        res_c = supabase.table("pedidos").insert(dados_c).execute()
                        supabase.table("linha_producao").insert({"id_pedido": res_c.data[0]['id']}).execute()
                        st.success("Orçamento Cadastrado com Status 'EXECUTANDO ORÇAMENTO'!")

            st.divider()
            st.subheader("⚙️ Atualização do Fluxo de Status (Gatilhos)")
            pedidos_com = supabase.table("pedidos").select("*").neq("status_geral", "CONCLUÍDO").execute()
            for p in pedidos_com.data:
                with st.expander(f"Orçamento: {p['numero_pedido']} | Status: {p['status_geral']}"):
                    col1, col2 = st.columns(2)
                    pv_in = col1.text_input("Nº PV (Pedido de Venda)", value=p.get('num_pv', ''), key=f"pv_{p['id']}")
                    po_in = col2.text_input("Nº PO (Ordem de Produção)", value=p.get('num_po', ''), key=f"po_{p['id']}")
                    if st.button("CONFIRMAR ATUALIZAÇÃO", key=f"upd_{p['id']}"):
                        n_stat = p['status_geral']
                        if pv_in and not po_in: n_stat = "ORÇAMENTO APROVADO"
                        if po_in: n_stat = "EM PRODUÇÃO"
                        supabase.table("pedidos").update({"num_pv": pv_in, "num_po": po_in, "status_geral": n_stat}).eq("id", p['id']).execute()
                        st.rerun()

    # --- MÓDULO: ORDENS DE PRODUÇÃO (CONFIGURAÇÃO DE WORKFLOW) ---
    if tab_pedido:
        with tab_pedido:
            st.subheader("Definição de Roteiro e Documentos")
            pedidos_workflow = supabase.table("pedidos").select("*").eq("status_geral", "EM PRODUÇÃO").execute()
            if pedidos_workflow.data:
                sel_w = st.selectbox("Selecione a Ordem para definir Workflow", options=[p['numero_pedido'] for p in pedidos_workflow.data])
                id_w = next(item['id'] for item in pedidos_workflow.data if item['numero_pedido'] == sel_w)
                with st.form("f_workflow"):
                    arq = st.file_uploader("Documentação Técnica", type=['pdf', 'jpg', 'png', 'dwg'])
                    st.markdown("**Checklist de Etapas (Roteiro Industrial C-Metal)**")
                    e1, e2, e3 = st.columns(3)
                    h_corte, h_dobra = e1.checkbox("Corte"), e1.checkbox("Dobra CNC")
                    h_solda, h_meta = e2.checkbox("Solda"), e2.checkbox("Metaleira")
                    h_calan, h_galva, h_pint = e3.checkbox("Calandra"), e3.checkbox("Galva"), e3.checkbox("Pintura")
                    if st.form_submit_button("REGISTRAR WORKFLOW DE PRODUÇÃO"):
                        url_f = ""
                        if arq:
                            path = f"pedidos/{sel_w}_{arq.name}"
                            supabase.storage.from_("desenhos").upload(path, arq.getvalue(), file_options={"upsert": "true"})
                            url_f = supabase.storage.from_("desenhos").get_public_url(path)
                        upd_w = {"arquivo_url": url_f, "has_corte_laser": h_corte, "has_dobra_cnc": h_dobra, "has_solda": h_solda, "has_metaleira": h_meta, "has_calandragem": h_calan, "has_galvanizacao": h_galva, "has_pintura": h_pint}
                        supabase.table("pedidos").update(upd_w).eq("id", id_w).execute()
                        st.success("Workflow Configurado!")
            else: st.info("Nenhum pedido no status 'EM PRODUÇÃO' disponível para configuração.")

    # --- MÓDULO: CHÃO DE FÁBRICA ---
    with tab_fabrica:
        st.subheader("Execução Industrial Industrial (Operadores Solluz)")
        ativos = supabase.table("pedidos").select("id, numero_pedido, arquivo_url").eq("status_geral", "EM PRODUÇÃO").execute()
        l_ativos = {p['numero_pedido']: p for p in ativos.data}
        if l_ativos:
            escolha = st.selectbox("OS em Operação Ativa:", options=list(l_ativos.keys()))
            item_f = l_ativos[escolha]
            if item_f['arquivo_url']:
                st.link_button("📂 ABRIR DOCUMENTAÇÃO TÉCNICA", item_f['arquivo_url'], use_container_width=True)
            st.divider()
            
            det = supabase.table("pedidos").select("*").eq("id", item_f['id']).single().execute().data
            prod = supabase.table("linha_producao").select("*").eq("id_pedido", item_f['id']).single().execute().data
            
            def render_etapa(label, campo, hab):
                if hab:
                    with st.expander(f"PROCESSO: {label.upper()}", expanded=True):
                        c_i, c_f, c_o = st.columns([1, 1, 2])
                        i, f = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                        if not i:
                            if c_i.button(f"INICIAR", key=f"i_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", item_f['id']).execute()
                                st.rerun()
                        elif not f:
                            c_i.info(f"Iniciado: {i[11:16]}")
                            obs = c_o.text_input("Obs Técnica / Notas de Execução", key=f"o_{campo}")
                            if c_f.button(f"FINALIZAR", key=f"f_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", item_f['id']).execute()
                                st.rerun()
                        else: st.success(f"CONCLUÍDO | {i[11:16]} - {f[11:16]}")

            # As 7 etapas completas
            render_etapa("Corte", "corte", det['has_corte_laser'])
            render_etapa("Dobra", "dobra", det['has_dobra_cnc'])
            render_etapa("Solda", "solda", det['has_solda'])
            render_etapa("Metaleira", "metaleira", det['has_metaleira'])
            render_etapa("Calandragem", "calandragem", det['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", det['has_galvanizacao'])
            render_etapa("Pintura", "pintura", det['has_pintura'])
        else: st.info("Sem ordens em produção ativa.")

    # --- MONITOR TV (PAINEL DE LUMINOSIDADE) ---
    if tab_tv:
        with tab_tv:
            st.subheader("Painel Monitor de Luminosidade Serralheria")
            res_tv = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
            for obra in res_tv.data:
                lp = obra['linha_producao'][0] if obra.get('linha_producao') else {}
                st.markdown(f"""
                    <div class='row-monitor'>
                        <div style='flex: 1;'>
                            <div class='id-site'>{obra['numero_pedido']}</div>
                            <div class='os-label'>Atividade Solluz</div>
                        </div>
                        <div style='flex: 2; display: flex; justify-content: space-around;'>
                            <div class='step-unit'>
                                <div class='label-etapa'>Corte</div>
                                <div class='dot {"bg-success" if lp.get("corte_fim") else "bg-danger"}'></div>
                            </div>
                            <div class='step-unit'>
                                <div class='label-etapa'>Dobra</div>
                                <div class='dot {"bg-success" if lp.get("dobra_fim") else "bg-danger"}'></div>
                            </div>
                            <div class='step-unit'>
                                <div class='label-etapa'>Solda</div>
                                <div class='dot {"bg-success" if lp.get("solda_fim") else "bg-danger"}'></div>
                            </div>
                            <div class='step-unit'>
                                <div class='label-etapa'>Pintura</div>
                                <div class='dot {"bg-success" if lp.get("pintura_fim") else "bg-danger"}'></div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    # --- ADMINISTRAÇÃO (DADOS MESTRES COMPLETOS RESTAURADOS) ---
    if tab_admin:
        with tab_admin:
            st.subheader("Configurações Globais de Cadastro")
            c1, c2 = st.columns(2)
            with c1:
                with st.expander("Registro de Solicitante Cliente", expanded=True):
                    with st.form("c_sol"):
                        n_s, e_s, t_s = st.text_input("Responsável Solluz"), st.text_input("Empresa Cliente"), st.text_input("Telefone")
                        info_s = st.text_area("Notas Adicionais")
                        if st.form_submit_button("REGISTRAR NOVO SOLICITANTE"):
                            supabase.table("solicitantes").insert({"nome": n_s, "empresa": e_s, "telefone": t_s, "info_adicional": info_s}).execute()
                            st.success("Salvo!")
            with c2:
                with st.expander("Registro de Projeto", expanded=True):
                    s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
                    l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
                    with st.form("c_proj"):
                        np, sid, cid = st.text_input("Título"), st.selectbox("Solicitante", options=list(l_s.keys())), st.text_input("Cidade")
                        end, num, cep = st.text_input("Endereço Completo"), st.text_input("Nº"), st.text_input("CEP")
                        if st.form_submit_button("VINCULAR PROJETO À Solluz"):
                            supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": end, "numero": num, "cep": cep}).execute()
                            st.success("Vinculado com Sucesso!")



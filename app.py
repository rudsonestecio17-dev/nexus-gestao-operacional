import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONFIGURAÇÕES DE INTERFACE PROFISSIONAL (DARK ENTERPRISE)
st.set_page_config(page_title="NEXUS | ERP", layout="wide", initial_sidebar_state="collapsed")

# 2. CONEXÃO SUPABASE
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# CSS PROFISSIONAL (Modo Escuro Industrial)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    .stApp { background-color: #0d1117; color: #e6edf3; font-family: 'Inter', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #161b22; padding: 10px 10px 0 10px; border-radius: 10px 10px 0 0; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #21262d; border: 1px solid #30363d; color: #8b949e; border-radius: 8px 8px 0 0; padding: 0 25px; }
    .stTabs [aria-selected="true"] { background-color: #0d1117 !important; color: #f39c12 !important; border: 1px solid #f39c12 !important; border-bottom: 2px solid #0d1117 !important; }
    .row-monitor { background: #161b22; border-radius: 12px; padding: 25px; margin-bottom: 15px; border-left: 6px solid #f39c12; border: 1px solid #30363d; display: flex; justify-content: space-between; align-items: center; }
    .id-site { font-size: 1.4em; font-weight: 800; color: #ffffff; margin: 0; }
    .dot { height: 18px; width: 18px; border-radius: 50%; display: inline-block; margin: 5px auto; border: 2px solid #0d1117; }
    .bg-success { background-color: #238636; box-shadow: 0 0 12px rgba(35, 134, 54, 0.6); }
    .bg-danger { background-color: #da3633; box-shadow: 0 0 8px rgba(218, 54, 51, 0.3); }
    .label-etapa { font-size: 10px; color: #8b949e; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; }
    .stExpander { background-color: #161b22 !important; border-color: #30363d !important; }
    input, select, textarea { background-color: #0d1117 !important; color: white !important; border: 1px solid #30363d !important; }
    .stButton>button { width: 100%; border-radius: 6px; height: 45px; background-color: #1e293b; color: white; font-weight: 600; text-transform: uppercase; font-size: 12px; border: none; }
    .stButton>button:hover { background-color: #334155; color: #f39c12; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE SESSÃO E LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

def tela_login():
    st.markdown("<h1 style='text-align: center; color: #f39c12;'>NEXUS | ACESSO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("CONECTAR"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.perfil = res.data[0]['perfil']
                    st.session_state.user_name = res.data[0]['login']
                    st.rerun()
                else:
                    st.error("Credenciais Inválidas.")

if not st.session_state.autenticado:
    tela_login()
else:
    # --- INTERFACE PRINCIPAL ---
    st.sidebar.write(f"Usuário: **{st.session_state.user_name.upper()}**")
    if st.sidebar.button("Sair do Sistema"):
        st.session_state.autenticado = False
        st.rerun()

    st.title("NEXUS | Gestão Industrial")
    st.caption("Controle Operacional e Monitoramento")
    st.divider()

    # Define visibilidade das abas conforme perfil
    if st.session_state.perfil == "admin":
        tab_dash, tab_pedido, tab_fabrica, tab_tv, tab_admin = st.tabs([
            "DASHBOARD", "ORDENS DE PRODUÇÃO", "CHÃO DE FÁBRICA", "MONITOR TV", "ADMINISTRAÇÃO"
        ])
    else:
        # Perfil Produção cai direto no Chão de Fábrica
        tab_fabrica = st.tabs(["CHÃO DE FÁBRICA"])[0]
        tab_dash = tab_pedido = tab_tv = tab_admin = None

    # --- MÓDULO: DASHBOARD ---
    if tab_dash:
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
                st.error(f"Erro ao carregar Dashboard: {e}")

    # --- MÓDULO: ORDENS DE PRODUÇÃO ---
    if tab_pedido:
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
                desc_p = st.text_area("Especificações")
                st.markdown("**Fluxo de Produção**")
                e1, e2, e3 = st.columns(3)
                h_corte = e1.checkbox("Corte a Laser")
                h_dobra = e1.checkbox("Dobra CNC")
                h_solda = e2.checkbox("Soldagem")
                h_meta = e2.checkbox("Metaleira")
                h_calan = e3.checkbox("Calandragem")
                h_galva = e3.checkbox("Galvanização")
                h_pint = e3.checkbox("Pintura")
                if st.form_submit_button("REGISTRAR ORDEM"):
                    url_f = ""
                    if arq:
                        path = f"pedidos/{num_p}_{arq.name}"
                        supabase.storage.from_("desenhos").upload(path, arq.getvalue())
                        url_f = supabase.storage.from_("desenhos").get_public_url(path)
                    dados_ins = {
                        "numero_pedido": num_p, "id_projeto": lista_p[proj_vinc], "descricao_pedido": desc_p,
                        "prazo_entrega": str(prazo_e), "arquivo_url": url_f,
                        "has_corte_laser": h_corte, "has_dobra_cnc": h_dobra, "has_solda": h_solda,
                        "has_metaleira": h_meta, "has_calandragem": h_calan, "has_galvanizacao": h_galva, "has_pintura": h_pint
                    }
                    res_ins = supabase.table("pedidos").insert(dados_ins).execute()
                    supabase.table("linha_producao").insert({"id_pedido": res_ins.data[0]['id']}).execute()
                    st.success("Ordem registrada!")

    # --- MÓDULO: CHÃO DE FÁBRICA ---
   # --- MÓDULO: CHÃO DE FÁBRICA ---
    with tab_fabrica:
        st.subheader("Controle de Processos")
        
        # 1. Busca os pedidos ativos
        ativos = supabase.table("pedidos").select("id, numero_pedido, arquivo_url").eq("status_geral", "Em Produção").execute()
        l_ativos = {p['numero_pedido']: p for p in ativos.data}
        
        if l_ativos:
            escolha = st.selectbox("Ordem em Operação:", options=list(l_ativos.keys()))
            dados_f = l_ativos[escolha]
            
            # --- NOVO: FUNÇÃO DE VER ARQUIVO ANEXADO ---
            st.markdown("### 📄 Documentação do Projeto")
            if dados_f['arquivo_url']:
                col_btn, col_info = st.columns([1, 2])
                with col_btn:
                    st.link_button("📂 ABRIR DESENHO TÉCNICO", dados_f['arquivo_url'], use_container_width=True)
                
                # Preview simples se for imagem
                if any(ext in dados_f['arquivo_url'].lower() for ext in ['.jpg', '.png', '.jpeg']):
                    with st.expander("👁️ Visualizar Miniatura"):
                        st.image(dados_f['arquivo_url'], use_container_width=True)
            else:
                st.warning("⚠️ Nenhum arquivo anexado a esta Ordem de Serviço.")
            
            st.divider()
            # --- FIM DA NOVA FUNÇÃO ---

            # Busca os detalhes técnicos para as etapas
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
            
            # Renderização das 7 etapas
            render_etapa("Corte a Laser", "corte", det['has_corte_laser'])
            render_etapa("Dobra CNC", "dobra", det['has_dobra_cnc'])
            render_etapa("Solda", "solda", det['has_solda'])
            render_etapa("Metaleira", "metaleira", det['has_metaleira'])
            render_etapa("Calandragem", "calandragem", det['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", det['has_galvanizacao'])
            render_etapa("Pintura", "pintura", det['has_pintura'])
        else:
            st.info("Sem ordens ativas.")
    # --- MÓDULO: MONITOR TV ---
    if tab_tv:
        with tab_tv:
            st.subheader("Monitor de Produção Industrial")
            res_tv = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").execute()
            if res_tv.data:
                for obra in res_tv.data:
                    lp = obra['linha_producao'][0] if obra.get('linha_producao') else {}
                    st.markdown(f"""
                        <div class='row-monitor'>
                            <div style='flex: 1;'><div class='id-site'>{obra['numero_pedido']}</div>
                            <div style='font-size: 0.85em; color: #8b949e;'>{obra['projetos']['nome_projeto']}</div></div>
                            <div style='flex: 2; display: flex; justify-content: space-around;'>
                                <div class='step-unit'><div class='label-etapa'>Corte</div><div class='dot {"bg-success" if lp.get("corte_fim") else "bg-danger"}'></div></div>
                                <div class='step-unit'><div class='label-etapa'>Dobra</div><div class='dot {"bg-success" if lp.get("dobra_fim") else "bg-danger"}'></div></div>
                                <div class='step-unit'><div class='label-etapa'>Solda</div><div class='dot {"bg-success" if lp.get("solda_fim") else "bg-danger"}'></div></div>
                                <div class='step-unit'><div class='label-etapa'>Pintura</div><div class='dot {"bg-success" if lp.get("pintura_fim") else "bg-danger"}'></div></div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    # --- MÓDULO: ADMINISTRAÇÃO ---
    if tab_admin:
        with tab_admin:
            st.subheader("Dados Mestres")
            c1, c2 = st.columns(2)
            with c1:
                with st.expander("Registro de Solicitante", expanded=True):
                    with st.form("cad_sol"):
                        n_s = st.text_input("Responsável")
                        e_s = st.text_input("Empresa")
                        t_s = st.text_input("Telefone")
                        info_s = st.text_area("Informações Adicionais")
                        if st.form_submit_button("REGISTRAR SOLICITANTE"):
                            supabase.table("solicitantes").insert({"nome": n_s, "empresa": e_s, "telefone": t_s, "info_adicional": info_s}).execute()
                            st.success("Salvo!")
            with c2:
                with st.expander("Registro de Projeto", expanded=True):
                    s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
                    l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
                    with st.form("cad_proj"):
                        np = st.text_input("Título do Projeto")
                        sid = st.selectbox("Solicitante", options=list(l_s.keys()))
                        cid = st.text_input("Cidade")
                        end = st.text_input("Endereço")
                        num = st.text_input("Número")
                        cep = st.text_input("CEP")
                        if st.form_submit_button("VINCULAR PROJETO"):
                            supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": end, "numero": num, "cep": cep}).execute()
                            st.success("Vinculado!")


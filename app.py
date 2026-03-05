import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# 1. CONFIGURAÇÕES SOLLUZ SYSTEMS
st.set_page_config(page_title="Solluz SYSTEMS | ERP", layout="wide", initial_sidebar_state="expanded")

# 2. CONEXÃO SUPABASE
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# URL DA LOGO OFICIAL
LOGO_URL = "https://i.ibb.co/6Lr0QZY/nexus-2.png"

# 3. CSS PREMIUM (Cores Solluz, Sidebar #202c65, Sem Emojis, Botão Ativo Corrigido)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    .stApp { background-color: #FFFFFF !important; color: #1e293b !important; font-family: 'Inter', sans-serif !important; }
    
    /* Barra Lateral Solluz */
    [data-testid="stSidebar"] { background-color: #202c65 !important; border-right: 1px solid #e2e8f0; }
    
    /* Botões da Sidebar - Estilo Profissional */
    .stSidebar div[data-testid="stVerticalBlock"] > div [data-testid="stButton"] button {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        width: 100% !important;
        text-align: left !important;
        padding: 12px 15px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 11px !important;
        letter-spacing: 0.5px !important;
        margin-bottom: -10px !important;
        transition: 0.3s;
    }

    .stSidebar div[data-testid="stVerticalBlock"] > div [data-testid="stButton"] button:hover {
        background-color: #3b82f6 !important;
        border-color: #3b82f6 !important;
        color: #FFFFFF !important;
    }

    /* Cards e Monitor TV */
    .row-monitor {
        background: #f8fafc; border-radius: 12px; padding: 20px; margin-bottom: 12px; 
        border: 1px solid #e2e8f0; border-left: 8px solid #3b82f6; 
        display: flex; justify-content: space-between; align-items: center;
    }
    .dot { height: 18px; width: 18px; border-radius: 50%; display: inline-block; margin: 4px auto; border: 2px solid #FFF; }
    .bg-success { background-color: #238636; box-shadow: 0 0 10px rgba(35, 134, 54, 0.4); }
    .bg-danger { background-color: #da3633; box-shadow: 0 0 8px rgba(218, 54, 51, 0.3); }
    
    /* Inputs e Expanders */
    .stExpander { background-color: #f8fafc !important; border-color: #e2e8f0 !important; }
    input, select, textarea { background-color: #FFFFFF !important; color: #1e293b !important; border: 1px solid #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def registrar_log(acao, detalhe):
    usuario = st.session_state.get('user_name', 'Sistema')
    try:
        supabase.table("logs_sistema").insert({"usuario": usuario, "acao": acao, "detalhe": detalhe}).execute()
    except: pass

def calcular_horas(inicio, fim):
    if inicio and fim:
        fmt = "%Y-%m-%dT%H:%M:%S"
        try:
            d_ini = datetime.strptime(inicio[:19], fmt)
            d_fim = datetime.strptime(fim[:19], fmt)
            diff = d_fim - d_ini
            return round(diff.total_seconds() / 3600, 2)
        except: return 0
    return 0

# --- CONTROLE DE ACESSO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<div style='text-align: center; padding-top: 100px;'><h1 style='color: #202c65;'>Solluz SYSTEMS</h1><p>CENTRO DE CONTROLE INDUSTRIAL</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.update({"autenticado": True, "perfil": res.data[0]['perfil'], "user_name": res.data[0]['login']})
                    registrar_log("LOGIN", "Acesso ao painel")
                    st.rerun()
                else: st.error("Acesso bloqueado.")
else:
    # --- BARRA LATERAL ---
    with st.sidebar:
        st.image(LOGO_URL, width=180)
        st.markdown(f"<p style='color:white; text-align:center;'>{st.session_state.user_name.upper()}</p>", unsafe_allow_html=True)
        st.divider()
        
        if st.session_state.perfil == "admin":
            menu = {
                "Dashboard": "dash",
                "Comercial": "com",
                "Financeiro": "fin",
                "Cadastros": "cad",
                "Workflow OS": "work",
                "Chão de Fábrica": "fab",
                "Relatorios": "rel",
                "Monitor TV": "tv",
                "Administração": "adm"
            }
        else:
            menu = {"Chão de Fábrica": "fab"}

        if 'pagina_ativa' not in st.session_state:
            st.session_state.pagina_ativa = "dash" if st.session_state.perfil == "admin" else "fab"

        for label, code in menu.items():
            if st.button(label, key=f"nav_{code}"):
                st.session_state.pagina_ativa = code
                st.rerun()
        
        st.divider()
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()

    # --- PÁGINAS ---
    p = st.session_state.pagina_ativa

    if p == "dash":
        st.title("Indicadores Gerais")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").execute()
        if res.data:
            df = []
            for i in res.data:
                lp = i['linha_producao'][0] if i.get('linha_producao') else {}
                df.append({"OS": i['numero_pedido'], "Projeto": i['projetos']['nome_projeto'] if i['projetos'] else "-", "Status": i['status_geral'], "Prazo": i['prazo_entrega']})
            st.dataframe(pd.DataFrame(df), use_container_width=True, hide_index=True)

    elif p == "com":
        st.title("Comercial")
        with st.expander("Novo Orçamento", expanded=True):
            p_db = supabase.table("projetos").select("id, nome_projeto").execute()
            l_p = {x['nome_projeto']: x['id'] for x in p_db.data}
            with st.form("f_com"):
                c1, c2 = st.columns(2)
                no, po = c1.text_input("Nº Orçamento"), c1.selectbox("Projeto", list(l_p.keys()))
                vo, de = c2.number_input("Valor R$", min_value=0.0), c2.date_input("Prazo")
                if st.form_submit_button("SALVAR"):
                    r = supabase.table("pedidos").insert({"numero_pedido": no, "id_projeto": l_p[po], "valor_orcamento": vo, "prazo_entrega": str(de), "status_geral": "EXECUTANDO ORÇAMENTO"}).execute()
                    supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                    st.success("Salvo!")

    elif p == "fin":
        st.title("Financeiro")
        res_fin = supabase.table("pedidos").select("numero_pedido, valor_orcamento, status_geral").execute()
        total = sum([float(x['valor_orcamento']) for x in res_fin.data if x['valor_orcamento']])
        st.metric("Receita Total Bruta", f"R$ {total:,.2f}")
        st.dataframe(pd.DataFrame(res_fin.data), use_container_width=True)

    elif p == "cad":
        st.title("Cadastros")
        c1, c2 = st.columns(2)
        with c1:
            with st.expander("Cliente", expanded=True):
                with st.form("f_s"):
                    n, e, t, o = st.text_input("Responsável"), st.text_input("Empresa"), st.text_input("Telefone"), st.text_area("Notas/Endereço")
                    if st.form_submit_button("CADASTRAR CLIENTE"):
                        supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t, "info_adicional": o}).execute()
                        st.success("Salvo!")
        with c2:
            with st.expander("Projeto", expanded=True):
                s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
                l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
                with st.form("f_p"):
                    np, sid, cid = st.text_input("Título"), st.selectbox("Cliente", list(l_s.keys())), st.text_input("Cidade")
                    end, num, cep = st.text_input("Endereço"), st.text_input("Nº"), st.text_input("CEP")
                    if st.form_submit_button("VINCULAR PROJETO"):
                        supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": end, "numero": num, "cep": cep}).execute()
                        st.success("Vinculado!")

    elif p == "work":
        st.title("Workflow")
        p_wf = supabase.table("pedidos").select("*").eq("status_geral", "EM PRODUÇÃO").execute()
        if p_wf.data:
            sel = st.selectbox("OS", [x['numero_pedido'] for x in p_wf.data])
            id_w = next(x['id'] for x in p_wf.data if x['numero_pedido'] == sel)
            with st.form("f_wf"):
                arq = st.file_uploader("Upload Desenho", type=['pdf','jpg','png'])
                e1, e2, e3 = st.columns(3)
                h1, h2, h3, h4, h5, h6, h7 = e1.checkbox("Corte"), e1.checkbox("Dobra"), e2.checkbox("Solda"), e2.checkbox("Metaleira"), e3.checkbox("Calandra"), e3.checkbox("Galva"), e3.checkbox("Pintura")
                if st.form_submit_button("SALVAR"):
                    url = ""
                    if arq:
                        path = f"pedidos/{sel}_{arq.name}"
                        supabase.storage.from_("desenhos").upload(path, arq.getvalue(), {"upsert": "true"})
                        url = supabase.storage.from_("desenhos").get_public_url(path)
                    supabase.table("pedidos").update({"arquivo_url": url, "has_corte_laser": h1, "has_dobra_cnc": h2, "has_solda": h3, "has_metaleira": h4, "has_calandragem": h5, "has_galvanizacao": h6, "has_pintura": h7}).eq("id", id_w).execute()
                    st.success("Workflow Definido!")

    elif p == "fab":
        st.title("Chão de Fábrica")
        atv = supabase.table("pedidos").select("id, numero_pedido, arquivo_url").eq("status_geral", "EM PRODUÇÃO").execute()
        if atv.data:
            sel = st.selectbox("Ordem:", [x['numero_pedido'] for x in atv.data])
            item = next(x for x in atv.data if x['numero_pedido'] == sel)
            if item['arquivo_url']: st.link_button("VER DESENHO", item['arquivo_url'])
            det = supabase.table("pedidos").select("*").eq("id", item['id']).single().execute().data
            prod = supabase.table("linha_producao").select("*").eq("id_pedido", item['id']).single().execute().data
            
            def render_etapa(label, campo, hab):
                if hab:
                    with st.expander(f"PROCESSO: {label.upper()}", expanded=True):
                        c1, c2, c3 = st.columns([1, 1, 2])
                        i, f = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                        if not i:
                            if c1.button("INICIAR", key=f"i_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", item['id']).execute()
                                registrar_log("FÁBRICA", f"Iniciou {label} OS {sel}")
                                st.rerun()
                        elif not f:
                            obs = c3.text_input("Obs", key=f"o_{campo}")
                            if c2.button("FINALIZAR", key=f"f_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", item['id']).execute()
                                registrar_log("FÁBRICA", f"Finalizou {label} OS {sel}")
                                st.rerun()
                        else: st.success(f"Concluído: {i[11:16]} - {f[11:16]}")

            render_etapa("Corte", "corte", det['has_corte_laser'])
            render_etapa("Dobra", "dobra", det['has_dobra_cnc'])
            render_etapa("Solda", "solda", det['has_solda'])
            render_etapa("Metaleira", "metaleira", det['has_metaleira'])
            render_etapa("Calandragem", "calandragem", det['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", det['has_galvanizacao'])
            render_etapa("Pintura", "pintura", det['has_pintura'])

    elif p == "rel":
        st.title("Relatórios de Produtividade")
        res_rel = supabase.table("linha_producao").select("*, pedidos(numero_pedido)").execute()
        if res_rel.data:
            dados = []
            for r in res_rel.data:
                dados.append({
                    "OS": r['pedidos']['numero_pedido'] if r['pedidos'] else "-",
                    "Corte (h)": calcular_horas(r.get('corte_inicio'), r.get('corte_fim')),
                    "Solda (h)": calcular_horas(r.get('solda_inicio'), r.get('solda_fim')),
                    "Pintura (h)": calcular_horas(r.get('pintura_inicio'), r.get('pintura_fim'))
                })
            df_rel = pd.DataFrame(dados)
            st.bar_chart(df_rel.set_index("OS"))
            st.dataframe(df_rel, use_container_width=True)

    elif p == "tv":
        st.title("Monitor")
        res_tv = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        for obra in res_tv.data:
            lp = obra['linha_producao'][0] if obra.get('linha_producao') else {}
            st.markdown(f"<div class='row-monitor'><div style='flex: 1;'><div class='id-site'>{obra['numero_pedido']}</div><div style='color: #64748b;'>{obra['projetos']['nome_projeto']}</div></div><div style='flex: 2; display: flex; justify-content: space-around;'><div class='step-unit'><div class='label-etapa'>Corte</div><div class='dot {'bg-success' if lp.get('corte_fim') else 'bg-danger'}'></div></div><div class='step-unit'><div class='label-etapa'>Dobra</div><div class='dot {'bg-success' if lp.get('dobra_fim') else 'bg-danger'}'></div></div><div class='step-unit'><div class='label-etapa'>Solda</div><div class='dot {'bg-success' if lp.get('solda_fim') else 'bg-danger'}'></div></div><div class='step-unit'><div class='label-etapa'>Pintura</div><div class='dot {'bg-success' if lp.get('pintura_fim') else 'bg-danger'}'></div></div></div></div>", unsafe_allow_html=True)

    elif p == "adm":
        st.title("Administração")
        sub_u, sub_l = st.tabs(["EQUIPE", "LOGS"])
        with sub_u:
            u_db = supabase.table("usuarios").select("*").execute()
            st.dataframe(pd.DataFrame(u_db.data)[['login', 'perfil']], use_container_width=True)
            with st.form("new_user"):
                nl, ns, np = st.text_input("Login"), st.text_input("Senha"), st.selectbox("Perfil", ["admin", "producao"])
                if st.form_submit_button("CADASTRAR"):
                    supabase.table("usuarios").insert({"login": nl, "senha": ns, "perfil": np}).execute()
                    st.rerun()
        with sub_l:
            l_db = supabase.table("logs_sistema").select("*").order("data_hora", desc=True).limit(50).execute()
            if l_db.data: st.table(pd.DataFrame(l_db.data)[['data_hora', 'usuario', 'acao', 'detalhe']])

import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# 1. CONFIGURAÇÕES CTRL
st.set_page_config(page_title="CTRL | Gestão de Produção", layout="wide", initial_sidebar_state="expanded")

# 2. CONEXÃO SUPABASE
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

LOGO_URL = "https://i.ibb.co/6Lr0QZY/nexus-2.png" 

# 3. DESIGN E IDENTIDADE VISUAL CTRL (Violeta Tecnológico)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    .stApp { background-color: #FFFFFF; color: #1e293b; font-family: 'Inter', sans-serif; }
    
    /* Sidebar CTRL */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important; 
        border-right: 1px solid #e2e8f0; 
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Botões da Sidebar */
    .stSidebar button {
        background-color: transparent !important; border: none !important; color: #FFFFFF !important;
        text-align: left !important; width: 100% !important; padding: 12px 15px !important;
        font-size: 11px !important; text-transform: uppercase !important; font-weight: 600 !important;
        transition: 0.3s;
    }
    .stSidebar button:hover { background-color: #4f46e5 !important; border-radius: 5px; }

    /* Cards e Monitoramento */
    .row-monitor { 
        background: #f8fafc; border-radius: 12px; padding: 20px; margin-bottom: 12px; 
        border: 1px solid #e2e8f0; border-left: 8px solid #6366f1; 
        display: flex; justify-content: space-between; align-items: center;
    }
    .dot { height: 18px; width: 18px; border-radius: 50%; display: inline-block; margin: 4px auto; border: 2px solid #FFF; }
    .bg-success { background-color: #10b981; }
    .bg-danger { background-color: #ef4444; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES CORE ---
def registrar_log(acao, detalhe):
    usuario = st.session_state.get('user_name', 'Sistema')
    try: supabase.table("logs_sistema").insert({"usuario": usuario, "acao": acao, "detalhe": detalhe}).execute()
    except: pass

def calcular_horas(inicio, fim):
    if inicio and fim:
        try:
            fmt = "%Y-%m-%dT%H:%M:%S"
            diff = datetime.strptime(fim[:19], fmt) - datetime.strptime(inicio[:19], fmt)
            return round(diff.total_seconds() / 3600, 2)
        except: return 0
    return 0

def get_proxima_os():
    try:
        res = supabase.table("pedidos").select("numero_pedido").order("id", desc=True).limit(1).execute()
        return str(int(res.data[0]['numero_pedido']) + 1) if res.data else "1001"
    except: return "1001"

# --- ACESSO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<div style='text-align: center; padding-top: 100px;'><h1>CTRL</h1><p>GESTÃO DE PRODUÇÃO | SOLLUZ SYSTEMS</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("login_form"):
            u, s = st.text_input("Usuário"), st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.update({"autenticado": True, "perfil": res.data[0]['perfil'], "user_name": res.data[0]['login']})
                    st.rerun()
                else: st.error("Acesso Negado.")
else:
    # --- SIDEBAR COMPLETA ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>CTRL</h2>", unsafe_allow_html=True)
        st.divider()
        if 'pg' not in st.session_state: st.session_state.pg = "dash"

        with st.expander("CONTROLE OPERACIONAL", expanded=True):
            if st.button("DASHBOARD"): st.session_state.pg = "dash"; st.rerun()
            if st.button("RELATÓRIOS"): st.session_state.pg = "rel"; st.rerun()
            if st.button("MONITORAMENTO"): st.session_state.pg = "tv"; st.rerun()
        with st.expander("FINANCEIRO"):
            if st.button("RECEITA TOTAL"): st.session_state.pg = "fin"; st.rerun()
        with st.expander("LOGÍSTICA"):
            if st.button("VALIDAÇÃO"): st.session_state.pg = "val"; st.rerun()
            if st.button("ENTREGA"): st.session_state.pg = "ent"; st.rerun()
        with st.expander("ADMINISTRAÇÃO"):
            if st.button("CADASTROS"): st.session_state.pg = "cad"; st.rerun()
            if st.button("GESTÃO SISTEMA"): st.session_state.pg = "adm"; st.rerun()
        with st.expander("PROJETOS"):
            if st.button("COMERCIAL"): st.session_state.pg = "com"; st.rerun()
            if st.button("WORKFLOW OS"): st.session_state.pg = "work"; st.rerun()
        with st.expander("PRODUÇÃO", expanded=True):
            if st.button("CHÃO DE FÁBRICA"): st.session_state.pg = "fab"; st.rerun()
        st.divider()
        if st.button("SAIR"): st.session_state.autenticado = False; st.rerun()

    # --- NAVEGAÇÃO ---
    p = st.session_state.pg

    # DASHBOARD
    if p == "dash":
        st.title("Indicadores de Produção")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").execute()
        if res.data:
            df = pd.DataFrame([{"OS": i['numero_pedido'], "Projeto": i['projetos']['nome_projeto'] if i['projetos'] else "-", "Status": i['status_geral'], "Prazo": i['prazo_entrega']} for i in res.data])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # RELATÓRIOS (TEMPO MÉDIO POR ETAPA)
    elif p == "rel":
        st.title("Relatórios de Produtividade")
        res = supabase.table("linha_producao").select("*, pedidos(numero_pedido)").execute()
        if res.data:
            dados = [{"OS": r['pedidos']['numero_pedido'], 
                      "Corte (h)": calcular_horas(r.get('corte_inicio'), r.get('corte_fim')),
                      "Solda (h)": calcular_horas(r.get('solda_inicio'), r.get('solda_fim')),
                      "Pintura (h)": calcular_horas(r.get('pintura_inicio'), r.get('pintura_fim'))} for r in res.data if r['pedidos']]
            df_rel = pd.DataFrame(dados)
            st.bar_chart(df_rel.set_index("OS"))
            st.dataframe(df_rel, use_container_width=True)

    # FINANCEIRO
    elif p == "fin":
        st.title("Financeiro | Receita Total")
        res_fin = supabase.table("pedidos").select("valor_orcamento").execute()
        total = sum([float(x['valor_orcamento']) for x in res_fin.data if x['valor_orcamento']])
        st.metric("Receita Total Bruta", f"R$ {total:,.2f}")

    # LOGÍSTICA - VALIDAÇÃO (FISCALIZAÇÃO)
    elif p == "val":
        st.title("Logística | Fiscalização")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "EM FISCALIZAÇÃO").execute()
        if res.data:
            for os in res.data:
                with st.container():
                    st.markdown(f"<div class='row-monitor'><b>OS: {os['numero_pedido']}</b> | {os['projetos']['nome_projeto']}</div>", unsafe_allow_html=True)
                    if st.button(f"APROVAR PARA ENTREGA: {os['numero_pedido']}", key=f"ap_{os['id']}"):
                        supabase.table("pedidos").update({"status_geral": "AGUARDANDO ENTREGA"}).eq("id", os['id']).execute()
                        st.rerun()
        else: st.info("Sem OS para fiscalizar.")

    # LOGÍSTICA - ENTREGA
    elif p == "ent":
        st.title("Logística | Entrega")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "AGUARDANDO ENTREGA").execute()
        if res.data:
            sel = st.selectbox("OS:", [x['numero_pedido'] for x in res.data])
            os_data = next(x for x in res.data if x['numero_pedido'] == sel)
            with st.form("f_ent"):
                t, f = st.text_input("Transportadora"), st.number_input("Frete")
                dr, de = st.date_input("Retirada"), st.date_input("Previsão Entrega")
                if st.form_submit_button("FINALIZAR"):
                    supabase.table("pedidos").update({"status_geral": "CONCLUÍDO"}).eq("id", os_data['id']).execute()
                    st.success("Concluído!"); st.rerun()

    # CADASTROS (DADOS MESTRES COMPLETOS)
    elif p == "cad":
        st.title("Administração | Cadastros")
        c1, c2 = st.columns(2)
        with c1:
            with st.form("c_cli"):
                n, e, t, o = st.text_input("Responsável"), st.text_input("Empresa"), st.text_input("Telefone"), st.text_area("Endereço/Notas")
                if st.form_submit_button("SALVAR CLIENTE"):
                    supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t, "info_adicional": o}).execute()
                    st.success("Salvo!")
        with c2:
            s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
            l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
            with st.form("c_p"):
                np, sid = st.text_input("Projeto"), st.selectbox("Cliente", list(l_s.keys()))
                cid, rua, num, cep = st.text_input("Cidade"), st.text_input("Rua"), st.text_input("Nº"), st.text_input("CEP")
                if st.form_submit_button("VINCULAR PROJETO"):
                    supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": rua, "numero": num, "cep": cep}).execute()
                    st.success("Vinculado!")

    # COMERCIAL (FLUXO PV/PO)
    elif p == "com":
        st.title("Projetos | Comercial")
        with st.expander("Novo Orçamento", expanded=True):
            p_db = supabase.table("projetos").select("id, nome_projeto").execute()
            l_p = {x['nome_projeto']: x['id'] for x in p_db.data}
            with st.form("f_com"):
                no = st.text_input("Nº OS", value=get_proxima_os())
                po_sel = st.selectbox("Projeto", list(l_p.keys()))
                vo = st.number_input("Valor R$", min_value=0.0)
                if st.form_submit_button("CADASTRAR"):
                    r = supabase.table("pedidos").insert({"numero_pedido": no, "id_projeto": l_p[po_sel], "valor_orcamento": vo, "status_geral": "EXECUTANDO ORÇAMENTO"}).execute()
                    if r.data: supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                    st.rerun()
        st.divider()
        p_p = supabase.table("pedidos").select("*").neq("status_geral", "CONCLUÍDO").execute()
        for i in p_p.data:
            with st.expander(f"OS: {i['numero_pedido']} | {i['status_geral']}"):
                pv = st.text_input("Nº PV", value=i.get('num_pv', ''), key=f"pv_{i['id']}")
                po_val = st.text_input("Nº PO", value=i.get('num_po', ''), key=f"po_{i['id']}")
                if st.button("ATUALIZAR STATUS", key=f"u_{i['id']}"):
                    ns = "EM PRODUÇÃO" if po_val else ("ORÇAMENTO APROVADO" if pv else i['status_geral'])
                    supabase.table("pedidos").update({"num_pv": pv, "num_po": po_val, "status_geral": ns}).eq("id", i['id']).execute()
                    st.rerun()

    # WORKFLOW (UPLOAD DE ARQUIVO)
    elif p == "work":
        st.title("Projetos | Workflow OS")
        p_wf = supabase.table("pedidos").select("*").eq("status_geral", "EM PRODUÇÃO").execute()
        if p_wf.data:
            sel = st.selectbox("OS", [x['numero_pedido'] for x in p_wf.data])
            id_w = next(x['id'] for x in p_wf.data if x['numero_pedido'] == sel)
            with st.form("f_wf"):
                arq = st.file_uploader("Subir Desenho Técnico")
                e1, e2 = st.columns(2)
                h1, h2, h3, h4 = e1.checkbox("Corte"), e1.checkbox("Dobra"), e1.checkbox("Solda"), e1.checkbox("Metaleira")
                h5, h6, h7 = e2.checkbox("Calandra"), e2.checkbox("Galva"), e2.checkbox("Pintura")
                if st.form_submit_button("SALVAR"):
                    url = ""
                    if arq:
                        path = f"pedidos/{sel}/{arq.name}"
                        supabase.storage.from_("desenhos").upload(path, arq.getvalue(), {"upsert": "true"})
                        url = supabase.storage.from_("desenhos").get_public_url(path)
                    supabase.table("pedidos").update({"arquivo_url": url, "has_corte_laser": h1, "has_dobra_cnc": h2, "has_solda": h3, "has_metaleira": h4, "has_calandragem": h5, "has_galvanizacao": h6, "has_pintura": h7}).eq("id", id_w).execute()
                    st.success("Configurado!")

    # CHÃO DE FÁBRICA (7 ETAPAS + TEMPO REAL)
    elif p == "fab":
        st.title("Produção | Chão de Fábrica")
        atv = supabase.table("pedidos").select("*, linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        if atv.data:
            sel = st.selectbox("OS:", [x['numero_pedido'] for x in atv.data])
            item = next(x for x in atv.data if x['numero_pedido'] == sel)
            prod = item['linha_producao'][0]
            if item['arquivo_url']: st.link_button("📂 DESENHO TÉCNICO", item['arquivo_url'])

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
                            obs = c3.text_input("Obs", key=f"o_{campo}")
                            if c2.button("FINALIZAR", key=f"f_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", item['id']).execute()
                                # Gatilho Fiscalização
                                r_check = supabase.table("pedidos").select("*, linha_producao(*)").eq("id", item['id']).single().execute().data
                                lp = r_check['linha_producao'][0]
                                checklist = {"has_corte_laser": "corte_fim", "has_dobra_cnc": "dobra_fim", "has_solda": "solda_fim", "has_metaleira": "metaleira_fim", "has_calandragem": "calandragem_fim", "has_galvanizacao": "galvanizacao_fim", "has_pintura": "pintura_fim"}
                                concluido = True
                                for ch, cf in checklist.items():
                                    if r_check.get(ch) == True and not lp.get(cf): concluido = False; break
                                if concluido: supabase.table("pedidos").update({"status_geral": "EM FISCALIZAÇÃO"}).eq("id", item['id']).execute()
                                st.rerun()
                        else: st.success(f"Duração: {calcular_horas(i, f)}h | {i[11:16]} - {f[11:16]}")

            render_etapa("Corte", "corte", item['has_corte_laser'])
            render_etapa("Dobra", "dobra", item['has_dobra_cnc'])
            render_etapa("Solda", "solda", item['has_solda'])
            render_etapa("Metaleira", "metaleira", item['has_metaleira'])
            render_etapa("Calandragem", "calandragem", item['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", item['has_galvanizacao'])
            render_etapa("Pintura", "pintura", item['has_pintura'])

import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# 1. SETUP E DESIGN CTRL
st.set_page_config(page_title="CTRL | Gestão de Produção", layout="wide", initial_sidebar_state="expanded")

# Conexão Supabase
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SETORES = ["Tecnologia e Marketing", "Diretoria", "Gerência", "Operações Manutenção", "Projetos", "Comercial", "Compras", "Engenharia", "Orçamentos"]

# 2. CSS EMPRESARIAL (Identidade Solluz Systems)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    .stApp { background-color: #FFFFFF; color: #1e293b; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .stSidebar .stExpander { background-color: rgba(255, 255, 255, 0.08) !important; border: none !important; border-radius: 10px !important; margin-bottom: 5px !important; }
    .stSidebar button { background-color: transparent !important; border: none !important; color: #FFFFFF !important; text-align: left !important; width: 100% !important; padding: 12px 15px !important; font-size: 11px !important; text-transform: uppercase !important; font-weight: 600 !important; }
    .stSidebar button:hover { background-color: #4f46e5 !important; border-radius: 5px; }
    .ticket-card { background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 6px solid #6366f1; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .row-monitor { background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 10px solid #6366f1; border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
    .bg-success { background-color: #10b981; color: white; padding: 2px 8px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES CORE ---
def registrar_log(acao, detalhe):
    u = st.session_state.get('user_name', 'Sistema')
    try: supabase.table("logs_sistema").insert({"usuario": u, "acao": acao, "detalhe": detalhe}).execute()
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
    st.markdown("<div style='text-align: center; padding-top: 100px;'><h1>CTRL</h1><p>SOLLUZ SYSTEMS</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("login"):
            u, s = st.text_input("Usuário"), st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.update({"autenticado": True, "perfil": res.data[0]['perfil'], "setor_user": res.data[0].get('setor', 'Operações'), "user_name": res.data[0]['login']})
                    st.rerun()
                else: st.error("Acesso Negado.")
else:
    # --- SIDEBAR COMPLETA ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>CTRL</h2>", unsafe_allow_html=True)
        st.write(f"<p style='text-align:center; font-size:10px;'>SETOR: {st.session_state.setor_user.upper()}</p>", unsafe_allow_html=True)
        st.divider()
        if 'pg' not in st.session_state: st.session_state.pg = "dash"

        with st.expander("CHAMADOS INTERNOS", expanded=True):
            if st.button("CENTRAL DE TICKETS"): st.session_state.pg = "tickets"; st.rerun()
        with st.expander("CONTROLE OPERACIONAL"):
            if st.button("DASHBOARD"): st.session_state.pg = "dash"; st.rerun()
            if st.button("RELATÓRIOS"): st.session_state.pg = "rel"; st.rerun()
            if st.button("MONITORAMENTO"): st.session_state.pg = "tv"; st.rerun()
        with st.expander("FINANCEIRO / LOGÍSTICA"):
            if st.button("RECEITA TOTAL"): st.session_state.pg = "fin"; st.rerun()
            if st.button("VALIDAÇÃO"): st.session_state.pg = "val"; st.rerun()
            if st.button("ENTREGA"): st.session_state.pg = "ent"; st.rerun()
        with st.expander("ADMINISTRAÇÃO"):
            if st.button("CADASTROS"): st.session_state.pg = "cad"; st.rerun()
            if st.button("GESTÃO EQUIPE"): st.session_state.pg = "adm"; st.rerun()
        with st.expander("PROJETOS / PRODUÇÃO", expanded=True):
            if st.button("COMERCIAL"): st.session_state.pg = "com"; st.rerun()
            if st.button("WORKFLOW OS"): st.session_state.pg = "work"; st.rerun()
            if st.button("CHÃO DE FÁBRICA"): st.session_state.pg = "fab"; st.rerun()
        st.divider()
        if st.button("LOGOUT"): st.session_state.autenticado = False; st.rerun()

    p = st.session_state.pg

    # --- 1. CENTRAL DE TICKETS (ALTERAÇÃO E FINALIZAÇÃO) ---
    if p == "tickets":
        st.title("Central de Chamados Internos")
        t1, t2 = st.tabs(["Tickets para meu Setor", "Abrir Novo Chamado"])
        with t2:
            with st.form("new_ticket"):
                c1, c2 = st.columns(2)
                dest, urg = c1.selectbox("Destino", SETORES), c1.select_slider("Urgência", options=["Baixa", "Média", "Alta", "Crítica"])
                tit, dsc = c2.text_input("Assunto"), st.text_area("Descrição")
                if st.form_submit_button("ABRIR CHAMADO"):
                    supabase.table("chamados").insert({"titulo": tit, "descricao": dsc, "setor_destino": dest, "solicitante": st.session_state.user_name, "setor_origem": st.session_state.setor_user, "status": "Aberto", "urgencia": urg}).execute()
                    st.success("Ticket Criado!"); st.rerun()
        with t1:
            res_tk = supabase.table("chamados").select("*").eq("setor_destino", st.session_state.setor_user).neq("status", "Concluído").execute()
            if res_tk.data:
                for tk in res_tk.data:
                    with st.container():
                        st.markdown(f"<div class='ticket-card'><b>[{tk['status']}] {tk['titulo']}</b><br><small>De: {tk['solicitante']} | Urgência: {tk['urgencia']}</small><p>{tk['descricao']}</p></div>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        if tk['status'] == "Aberto":
                            if c1.button("ASSUMIR ATENDIMENTO", key=f"as_{tk['id']}"):
                                supabase.table("chamados").update({"status": "Em Atendimento", "responsavel_tecnico": st.session_state.user_name}).eq("id", tk['id']).execute()
                                st.rerun()
                        if tk['status'] == "Em Atendimento":
                            if c2.button("FINALIZAR CHAMADO", key=f"fn_{tk['id']}"):
                                supabase.table("chamados").update({"status": "Concluído"}).eq("id", tk['id']).execute()
                                st.rerun()
            else: st.info("Sem chamados pendentes.")

    # --- 2. COMERCIAL (FLUXO PV/PO) ---
    elif p == "com":
        st.title("Projetos | Comercial")
        with st.expander("Gerar Novo Pedido/OS", expanded=True):
            p_db = supabase.table("projetos").select("id, nome_projeto").execute()
            l_p = {x['nome_projeto']: x['id'] for x in p_db.data}
            with st.form("f_com"):
                c1, c2 = st.columns(2)
                no, po_sel = c1.text_input("Nº OS", value=get_proxima_os()), c1.selectbox("Projeto", list(l_p.keys()))
                vo, prazo = c2.number_input("Valor R$"), c2.date_input("Prazo")
                if st.form_submit_button("LANÇAR"):
                    r = supabase.table("pedidos").insert({"numero_pedido": no, "id_projeto": l_p[po_sel], "valor_orcamento": vo, "prazo_entrega": str(prazo), "status_geral": "EXECUTANDO ORÇAMENTO"}).execute()
                    if r.data: supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                    st.rerun()
        st.divider()
        ped = supabase.table("pedidos").select("*").neq("status_geral", "CONCLUÍDO").execute()
        for i in ped.data:
            with st.expander(f"OS: {i['numero_pedido']} | {i['status_geral']}"):
                c1, c2 = st.columns(2)
                pv, po = c1.text_input("PV", value=i.get('num_pv', ''), key=f"pv_{i['id']}"), c2.text_input("PO", value=i.get('num_po', ''), key=f"po_{i['id']}")
                if st.button("AVANÇAR STATUS", key=f"u_{i['id']}"):
                    ns = "EM PRODUÇÃO" if po else ("ORÇAMENTO APROVADO" if pv else i['status_geral'])
                    supabase.table("pedidos").update({"num_pv": pv, "num_po": po, "status_geral": ns}).eq("id", i['id']).execute()
                    st.rerun()

    # --- 3. WORKFLOW (UPLOAD E ROTEIRO) ---
    elif p == "work":
        st.title("Projetos | Engenharia e Workflow")
        p_wf = supabase.table("pedidos").select("*").eq("status_geral", "EM PRODUÇÃO").execute()
        if p_wf.data:
            sel = st.selectbox("Selecione a OS:", [x['numero_pedido'] for x in p_wf.data])
            id_w = next(x['id'] for x in p_wf.data if x['numero_pedido'] == sel)
            with st.form("f_wf"):
                arq = st.file_uploader("Arquivo do Projeto (PDF/IMG/DXF)")
                st.write("Defina as etapas necessárias para esta OS:")
                e1, e2 = st.columns(2)
                h1, h2, h3, h4 = e1.checkbox("Corte Laser"), e1.checkbox("Dobra CNC"), e1.checkbox("Solda"), e1.checkbox("Metaleira")
                h5, h6, h7 = e2.checkbox("Calandragem"), e2.checkbox("Galvanização"), e2.checkbox("Pintura")
                if st.form_submit_button("CONFIRMAR FLUXO"):
                    url = ""
                    if arq:
                        path = f"desenhos/{sel}/{arq.name}"
                        supabase.storage.from_("desenhos").upload(path, arq.getvalue(), {"upsert": "true"})
                        url = supabase.storage.from_("desenhos").get_public_url(path)
                    supabase.table("pedidos").update({"arquivo_url": url, "has_corte_laser": h1, "has_dobra_cnc": h2, "has_solda": h3, "has_metaleira": h4, "has_calandragem": h5, "has_galvanizacao": h6, "has_pintura": h7}).eq("id", id_w).execute()
                    st.success("Workflow Configurado!")

    # --- 4. CHÃO DE FÁBRICA (7 ETAPAS + MÉTRICAS) ---
    elif p == "fab":
        st.title("Produção | Chão de Fábrica")
        atv = supabase.table("pedidos").select("*, linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        if atv.data:
            sel = st.selectbox("Operar OS:", [x['numero_pedido'] for x in atv.data])
            item = next(x for x in atv.data if x['numero_pedido'] == sel)
            prod = item['linha_producao'][0]
            if item['arquivo_url']: st.link_button("📂 DESENHO TÉCNICO", item['arquivo_url'], use_container_width=True)

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
                            obs = c3.text_input("Observação", key=f"o_{campo}")
                            if c2.button("FINALIZAR", key=f"f_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", item['id']).execute()
                                # Lógica Fiscalização Automática
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

    # --- 5. LOGÍSTICA (VALIDAÇÃO E ENTREGA) ---
    elif p == "val":
        st.title("Logística | Fiscalização")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "EM FISCALIZAÇÃO").execute()
        for os in res.data:
            st.markdown(f"<div class='row-monitor'><b>OS: {os['numero_pedido']}</b> | {os['projetos']['nome_projeto']}</div>", unsafe_allow_html=True)
            if st.button("APROVAR PARA DESPACHO", key=f"v_{os['id']}"):
                supabase.table("pedidos").update({"status_geral": "AGUARDANDO ENTREGA"}).eq("id", os['id']).execute()
                st.rerun()

    elif p == "ent":
        st.title("Logística | Entrega e Frete")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "AGUARDANDO ENTREGA").execute()
        if res.data:
            sel = st.selectbox("OS:", [x['numero_pedido'] for x in res.data])
            os_data = next(x for x in res.data if x['numero_pedido'] == sel)
            with st.form("f_ent"):
                c1, c2 = st.columns(2)
                t, f = c1.text_input("Transportadora"), c1.number_input("Frete")
                dr, de = c2.date_input("Saída"), c2.date_input("Previsão Entrega")
                if st.form_submit_button("CONCLUIR OS"):
                    supabase.table("pedidos").update({"status_geral": "CONCLUÍDO", "transportadora": t, "valor_frete": f}).eq("id", os_data['id']).execute()
                    st.success("Concluído!"); st.rerun()

    # --- 6. DASHBOARD (KPIs) ---
    elif p == "dash":
        st.title("Dashboard de Produção")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").execute()
        if res.data:
            df = pd.DataFrame([{"OS": i['numero_pedido'], "Projeto": i['projetos']['nome_projeto'] if i['projetos'] else "-", "Status": i['status_geral'], "Prazo": i['prazo_entrega']} for i in res.data])
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Pedidos", len(res.data))
            c2.metric("Em Produção", len(df[df['Status'] == 'EM PRODUÇÃO']))
            c3.metric("Finalizados", len(df[df['Status'] == 'CONCLUÍDO']))
            st.dataframe(df, use_container_width=True, hide_index=True)

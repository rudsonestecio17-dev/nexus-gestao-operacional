import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import plotly.express as px

# 1. SETUP E DESIGN CTRL
st.set_page_config(page_title="CTRL | Gestão de Produção", layout="wide", initial_sidebar_state="expanded")

# Conexão Supabase
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SETORES = ["Tecnologia e Marketing", "Diretoria", "Gerência", "Operações Manutenção", "Projetos", "Comercial", "Compras", "Engenharia", "Orçamentos"]

# 2. CSS EMPRESARIAL (Identidade Solluz Systems - Fim do Bug Branco)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    .stApp { background-color: #FFFFFF; color: #1e293b; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Fixa Violeta */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important; 
        border-right: 1px solid #e2e8f0; 
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Submenus Sidebar */
    .stSidebar .stExpander { 
        background-color: rgba(255, 255, 255, 0.08) !important; 
        border: none !important; border-radius: 10px !important; margin-bottom: 5px !important; 
    }
    .stSidebar button {
        background-color: transparent !important; border: none !important; color: #FFFFFF !important;
        text-align: left !important; width: 100% !important; padding: 12px 15px !important;
        font-size: 11px !important; text-transform: uppercase !important; font-weight: 600 !important;
    }
    .stSidebar button:hover { background-color: #4f46e5 !important; border-radius: 5px; }

    /* Cards Estilizados */
    .metric-card { background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; }
    .ticket-card { background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 6px solid #6366f1; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .row-monitor { background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 10px solid #6366f1; border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;}
    .dot { height: 18px; width: 18px; border-radius: 50%; display: inline-block; margin: 4px auto; border: 2px solid #FFF; }
    .bg-success { background-color: #10b981; }
    .bg-danger { background-color: #ef4444; }
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
    st.markdown("<div style='text-align: center; padding-top: 100px;'><h1>CTRL</h1><p>GESTÃO DE PRODUÇÃO | SOLLUZ SYSTEMS</p></div>", unsafe_allow_html=True)
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
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>CTRL</h2>", unsafe_allow_html=True)
        st.write(f"<p style='text-align:center; font-size:10px;'>{st.session_state.setor_user.upper()}</p>", unsafe_allow_html=True)
        st.divider()
        if 'pg' not in st.session_state: st.session_state.pg = "dash"

        with st.expander("CHAMADOS INTERNOS", expanded=True):
            if st.button("CENTRAL DE TICKETS"): st.session_state.pg = "tickets"; st.rerun()
        with st.expander("CONTROLE OPERACIONAL"):
            if st.button("DASHBOARD"): st.session_state.pg = "dash"; st.rerun()
            if st.button("RELATÓRIOS"): st.session_state.pg = "rel"; st.rerun()
            if st.button("MONITORAMENTO"): st.session_state.pg = "tv"; st.rerun()
        with st.expander("LOGÍSTICA / FINANCEIRO"):
            if st.button("RECEITA TOTAL"): st.session_state.pg = "fin"; st.rerun()
            if st.button("VALIDAÇÃO"): st.session_state.pg = "val"; st.rerun()
            if st.button("ENTREGA"): st.session_state.pg = "ent"; st.rerun()
        with st.expander("ADMINISTRAÇÃO"):
            if st.button("CADASTROS"): st.session_state.pg = "cad"; st.rerun()
            if st.button("GESTÃO EQUIPE"): st.session_state.pg = "adm"; st.rerun()
        with st.expander("PRODUÇÃO", expanded=True):
            if st.button("COMERCIAL"): st.session_state.pg = "com"; st.rerun()
            if st.button("WORKFLOW OS"): st.session_state.pg = "work"; st.rerun()
            if st.button("CHÃO DE FÁBRICA"): st.session_state.pg = "fab"; st.rerun()
        st.divider()
        if st.button("LOGOUT"): st.session_state.autenticado = False; st.rerun()

    p = st.session_state.pg

    # --- PÁGINA: CENTRAL DE TICKETS ---
    if p == "tickets":
        st.title("Central de Tickets Internos")
        t1, t2 = st.tabs(["Tickets do meu Setor", "Abrir Novo Chamado"])
        with t2:
            with st.form("nt"):
                c1, c2 = st.columns(2)
                dest, urg = c1.selectbox("Destino", SETORES), c1.select_slider("Urgência", options=["Baixa", "Média", "Alta", "Crítica"])
                tit, dsc = c2.text_input("Assunto"), st.text_area("Descrição")
                if st.form_submit_button("ABRIR CHAMADO"):
                    supabase.table("chamados").insert({"titulo": tit, "descricao": dsc, "setor_destino": dest, "solicitante": st.session_state.user_name, "setor_origem": st.session_state.setor_user, "status": "Aberto", "urgencia": urg}).execute()
                    st.success("Chamado Aberto!")
        with t1:
            res_tk = supabase.table("chamados").select("*").eq("setor_destino", st.session_state.setor_user).neq("status", "Concluído").execute()
            for tk in res_tk.data:
                with st.container():
                    st.markdown(f"<div class='ticket-card'><b>[{tk['status']}] {tk['titulo']}</b><br><small>Solicitante: {tk['solicitante']} | Urgência: {tk['urgencia']}</small><p>{tk['descricao']}</p></div>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    if tk['status'] == "Aberto" and c1.button("ASSUMIR", key=f"as_{tk['id']}"):
                        supabase.table("chamados").update({"status": "Em Atendimento", "responsavel_tecnico": st.session_state.user_name}).eq("id", tk['id']).execute(); st.rerun()
                    if tk['status'] == "Em Atendimento" and c2.button("FINALIZAR", key=f"fn_{tk['id']}"):
                        supabase.table("chamados").update({"status": "Concluído"}).eq("id", tk['id']).execute(); st.rerun()

    # --- PÁGINA: DASHBOARD ---
    elif p == "dash":
        st.title("Dashboard de Atividades")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").execute()
        if res.data:
            df = pd.DataFrame([{"OS": i['numero_pedido'], "Status": i['status_geral'], "Valor": i['valor_orcamento']} for i in res.data])
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total OS", len(df))
            c2.metric("Em Produção", len(df[df['Status'] == 'EM PRODUÇÃO']))
            c3.metric("Fiscalização", len(df[df['Status'] == 'EM FISCALIZAÇÃO']))
            c4.metric("Concluídas", len(df[df['Status'] == 'CONCLUÍDO']))
            st.plotly_chart(px.pie(df, names='Status', title="Distribuição de Atividades"), use_container_width=True)

    # --- PÁGINA: RELATÓRIOS (TEMPOS) ---
    elif p == "rel":
        st.title("Relatórios de Produtividade")
        res = supabase.table("linha_producao").select("*, pedidos(numero_pedido)").execute()
        if res.data:
            dados = []
            for r in res.data:
                if r['pedidos']:
                    dados.append({
                        "OS": r['pedidos']['numero_pedido'],
                        "Corte (h)": calcular_horas(r.get('corte_inicio'), r.get('corte_fim')),
                        "Dobra (h)": calcular_horas(r.get('dobra_inicio'), r.get('dobra_fim')),
                        "Solda (h)": calcular_horas(r.get('solda_inicio'), r.get('solda_fim')),
                        "Pintura (h)": calcular_horas(r.get('pintura_inicio'), r.get('pintura_fim'))
                    })
            st.dataframe(pd.DataFrame(dados), use_container_width=True)
            st.bar_chart(pd.DataFrame(dados).set_index("OS"))

    # --- PÁGINA: MONITORAMENTO ---
    elif p == "tv":
        st.title("Monitoramento de Fluxo")
        res_tv = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").neq("status_geral", "CONCLUÍDO").execute()
        for o in res_tv.data:
            lp = o['linha_producao'][0] if o['linha_producao'] else {}
            st.markdown(f"""
            <div class='row-monitor'>
                <div style='flex:1;'><b>OS: {o['numero_pedido']}</b><br><small>Status: {o['status_geral']}</small></div>
                <div style='flex:2; display:flex; justify-content: space-around;'>
                    <div>PV <div class='dot {'bg-success' if o.get('num_pv') else 'bg-danger'}'></div></div>
                    <div>PO <div class='dot {'bg-success' if o.get('num_po') else 'bg-danger'}'></div></div>
                    <div>Corte <div class='dot {'bg-success' if lp.get('corte_fim') else 'bg-danger'}'></div></div>
                    <div>Solda <div class='dot {'bg-success' if lp.get('solda_fim') else 'bg-danger'}'></div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- PÁGINA: RECEITA TOTAL ---
    elif p == "fin":
        st.title("Financeiro | Receita Total")
        res = supabase.table("pedidos").select("valor_orcamento").execute()
        total = sum([float(x['valor_orcamento']) for x in res.data if x['valor_orcamento']])
        st.metric("Faturamento Total Bruto", f"R$ {total:,.2f}")

    # --- PÁGINA: VALIDAÇÃO (FISCALIZAÇÃO) ---
    elif p == "val":
        st.title("Logística | Validação")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "EM FISCALIZAÇÃO").execute()
        if res.data:
            for os in res.data:
                with st.container():
                    st.write(f"**OS: {os['numero_pedido']}** - {os['projetos']['nome_projeto']}")
                    if st.button("APROVAR PARA ENTREGA", key=f"val_{os['id']}"):
                        supabase.table("pedidos").update({"status_geral": "AGUARDANDO ENTREGA"}).eq("id", os['id']).execute(); st.rerun()
        else: st.info("Nada para validar.")

    # --- PÁGINA: ENTREGA (MAPA + FRETE) ---
    elif p == "ent":
        st.title("Logística | Entrega")
        res = supabase.table("pedidos").select("*, projetos(*)").eq("status_geral", "AGUARDANDO ENTREGA").execute()
        if res.data:
            sel = st.selectbox("OS:", [x['numero_pedido'] for x in res.data])
            os_data = next(x for x in res.data if x['numero_pedido'] == sel)
            with st.form("f_ent"):
                c1, c2 = st.columns(2)
                transp, valor = c1.text_input("Transportadora"), c1.number_input("Valor Frete R$")
                if st.form_submit_button("FINALIZAR ENTREGA"):
                    supabase.table("pedidos").update({"status_geral": "CONCLUÍDO", "transportadora": transp, "valor_frete": valor}).eq("id", os_data['id']).execute(); st.rerun()
            # Mapa (Simulação baseada nos cadastros de cidade/projeto)
            st.subheader("Mapa de Entregas Pendentes")
            st.map(pd.DataFrame({"lat": [-22.56], "lon": [-47.41]})) # Exemplo Limeira
        else: st.info("Sem entregas pendentes.")

    # --- PÁGINA: CADASTROS ---
    elif p == "cad":
        st.title("Cadastros | Clientes e Projetos")
        c1, c2 = st.columns(2)
        with c1:
            with st.form("f_cli"):
                n, e, t = st.text_input("Responsável"), st.text_input("Empresa"), st.text_input("Telefone")
                if st.form_submit_button("CADASTRAR CLIENTE"):
                    supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t}).execute(); st.success("Salvo")
        with c2:
            s_db = supabase.table("solicitantes").select("id, nome").execute()
            l_s = {x['nome']: x['id'] for x in s_db.data}
            with st.form("f_proj"):
                np, sid = st.text_input("Título Obra"), st.selectbox("Cliente", list(l_s.keys()))
                cid, end = st.text_input("Cidade"), st.text_input("Rua/Endereço")
                if st.form_submit_button("SALVAR OBRA"):
                    supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": end}).execute(); st.success("Salvo")

    # --- PÁGINA: GESTÃO EQUIPE ---
    elif p == "adm":
        st.title("Gestão de Equipe e Logs")
        t1, t2 = st.tabs(["Usuários", "Auditoria de Logs"])
        with t1:
            u_db = supabase.table("usuarios").select("*").execute()
            st.dataframe(pd.DataFrame(u_db.data)[['login', 'perfil', 'setor']], use_container_width=True)
            with st.form("nu"):
                nl, ns, nset = st.text_input("Login"), st.text_input("Senha"), st.selectbox("Setor", SETORES)
                if st.form_submit_button("CRIAR"):
                    supabase.table("usuarios").insert({"login": nl, "senha": ns, "setor": nset, "perfil": "producao"}).execute(); st.rerun()
        with t2:
            logs = supabase.table("logs_sistema").select("*").order("data_hora", desc=True).limit(50).execute()
            if logs.data: st.table(pd.DataFrame(logs.data)[['data_hora', 'usuario', 'acao', 'detalhe']])

    # --- PÁGINA: COMERCIAL (OS -> PV -> PO) ---
    elif p == "com":
        st.title("Projetos | Comercial")
        with st.expander("Gerar Novo Orçamento/OS", expanded=True):
            p_db = supabase.table("projetos").select("id, nome_projeto").execute()
            l_p = {x['nome_projeto']: x['id'] for x in p_db.data}
            with st.form("f_com"):
                no = st.text_input("Nº OS", value=get_proxima_os())
                po_sel = st.selectbox("Projeto", list(l_p.keys()))
                vo = st.number_input("Valor R$")
                if st.form_submit_button("LANÇAR OS"):
                    r = supabase.table("pedidos").insert({"numero_pedido": no, "id_projeto": l_p[po_sel], "valor_orcamento": vo, "status_geral": "EXECUTANDO ORÇAMENTO"}).execute()
                    if r.data: supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                    st.rerun()
        st.divider()
        ped = supabase.table("pedidos").select("*").neq("status_geral", "CONCLUÍDO").execute()
        for i in ped.data:
            with st.expander(f"OS: {i['numero_pedido']} | {i['status_geral']}"):
                c1, c2 = st.columns(2)
                pv, po = c1.text_input("Nº PV", value=i.get('num_pv', ''), key=f"pv_{i['id']}"), c2.text_input("Nº PO", value=i.get('num_po', ''), key=f"po_{i['id']}")
                if st.button("AVANÇAR PARA WORKFLOW", key=f"u_{i['id']}"):
                    ns = "EM PRODUÇÃO" if po else ("ORÇAMENTO APROVADO" if pv else i['status_geral'])
                    supabase.table("pedidos").update({"num_pv": pv, "num_po": po, "status_geral": ns}).eq("id", i['id']).execute(); st.rerun()

    # --- PÁGINA: WORKFLOW ---
    elif p == "work":
        st.title("Projetos | Workflow")
        p_wf = supabase.table("pedidos").select("*").eq("status_geral", "EM PRODUÇÃO").execute()
        if p_wf.data:
            sel = st.selectbox("OS:", [x['numero_pedido'] for x in p_wf.data])
            id_w = next(x['id'] for x in p_wf.data if x['numero_pedido'] == sel)
            with st.form("f_wf"):
                arq = st.file_uploader("Subir Projeto")
                h1, h2, h3, h4 = st.checkbox("Corte"), st.checkbox("Dobra"), st.checkbox("Solda"), st.checkbox("Pintura")
                if st.form_submit_button("CONFIGURAR"):
                    url = ""
                    if arq:
                        path = f"desenhos/{sel}/{arq.name}"
                        supabase.storage.from_("desenhos").upload(path, arq.getvalue(), {"upsert": "true"})
                        url = supabase.storage.from_("desenhos").get_public_url(path)
                    supabase.table("pedidos").update({"arquivo_url": url, "has_corte_laser": h1, "has_dobra_cnc": h2, "has_solda": h3, "has_pintura": h4}).eq("id", id_w).execute(); st.success("Salvo")

    # --- PÁGINA: CHÃO DE FÁBRICA ---
    elif p == "fab":
        st.title("Produção | Chão de Fábrica")
        atv = supabase.table("pedidos").select("*, linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        if atv.data:
            sel = st.selectbox("OS:", [x['numero_pedido'] for x in atv.data])
            item = next(x for x in atv.data if x['numero_pedido'] == sel)
            prod = item['linha_producao'][0]

            def render_etapa(label, campo, hab):
                if hab:
                    with st.expander(f"⚙️ {label.upper()}", expanded=True):
                        c1, c2, c3 = st.columns([1, 1, 2])
                        i, f = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                        if not i and c1.button("INICIAR", key=f"i_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", item['id']).execute(); st.rerun()
                        elif not f and c2.button("FINALIZAR", key=f"f_{campo}"):
                            supabase.table("linha_producao").update({f"{campo}_fim": "now()"}).eq("id_pedido", item['id']).execute()
                            # Checagem Fiscalização
                            r_check = supabase.table("pedidos").select("*, linha_producao(*)").eq("id", item['id']).single().execute().data
                            lp = r_check['linha_producao'][0]
                            checklist = {"has_corte_laser": "corte_fim", "has_dobra_cnc": "dobra_fim", "has_solda": "solda_fim", "has_pintura": "pintura_fim"}
                            concluido = True
                            for ch, cf in checklist.items():
                                if r_check.get(ch) == True and not lp.get(cf): concluido = False; break
                            if concluido: supabase.table("pedidos").update({"status_geral": "EM FISCALIZAÇÃO"}).eq("id", item['id']).execute()
                            st.rerun()
                        elif f: st.success(f"Duração: {calcular_horas(i, f)}h")

            render_etapa("Corte", "corte", item['has_corte_laser'])
            render_etapa("Dobra", "dobra", item['has_dobra_cnc'])
            render_etapa("Solda", "solda", item['has_solda'])
            render_etapa("Pintura", "pintura", item['has_pintura'])

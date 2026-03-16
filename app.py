import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# 1. SETUP E DESIGN CTRL (Proteção contra Flash Branco)
st.set_page_config(page_title="CTRL | Gestão de Produção", layout="wide", initial_sidebar_state="expanded")

# Conexão Supabase
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SETORES = ["Tecnologia e Marketing", "Diretoria", "Gerência", "Operações Manutenção", "Projetos", "Comercial", "Compras", "Engenharia", "Orçamentos"]

# 2. CSS PROFISSIONAL (Identidade Violeta Solluz Systems)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Previne fundo branco indesejado */
    .stApp { background-color: #FFFFFF; color: #1e293b; font-family: 'Inter', sans-serif; }
    
    /* Sidebar CTRL */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important; 
        border-right: 1px solid #e2e8f0; 
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Botões da Sidebar - Correção do Bug Branco */
    .stSidebar .stExpander { 
        background-color: rgba(255, 255, 255, 0.08) !important; 
        border: none !important; 
        border-radius: 10px !important;
        margin-bottom: 5px !important;
    }
    
    .stSidebar button {
        background-color: transparent !important; border: none !important; color: #FFFFFF !important;
        text-align: left !important; width: 100% !important; padding: 12px 15px !important;
        font-size: 11px !important; text-transform: uppercase !important; font-weight: 600 !important;
    }
    .stSidebar button:hover { background-color: #4f46e5 !important; border-radius: 5px; }

    /* UI de Cards e Tickets */
    .ticket-card { background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 6px solid #6366f1; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .row-monitor { background: #f8fafc; border-radius: 12px; padding: 20px; border-left: 10px solid #6366f1; border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
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
    st.markdown("<div style='text-align: center; padding-top: 100px;'><h1>CTRL</h1><p>SOLLUZ SYSTEMS</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("login_form"):
            u, s = st.text_input("Usuário"), st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO COMANDO"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.update({
                        "autenticado": True, "perfil": res.data[0]['perfil'], 
                        "setor_user": res.data[0].get('setor', 'Operações'), "user_name": res.data[0]['login']
                    })
                    st.rerun()
                else: st.error("Acesso Negado.")
else:
    # --- SIDEBAR PROFISSIONAL (NAVEGAÇÃO COMPLETA) ---
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

    # --- RENDERIZAÇÃO DAS PÁGINAS ---
    p = st.session_state.pg

    # 1. CENTRAL DE TICKETS (RESTAURADO)
    if p == "tickets":
        st.title("Central de Chamados Internos")
        t1, t2 = st.tabs(["Tickets para meu Setor", "Abrir Novo Chamado"])
        with t2:
            with st.form("new_ticket"):
                c1, c2 = st.columns(2)
                dest = c1.selectbox("Setor Destino", SETORES)
                urg = c1.select_slider("Urgência", options=["Baixa", "Média", "Alta", "Crítica"])
                tit, dsc = c2.text_input("Assunto"), st.text_area("Descrição")
                if st.form_submit_button("ABRIR CHAMADO"):
                    supabase.table("chamados").insert({"titulo": tit, "descricao": dsc, "setor_destino": dest, "solicitante": st.session_state.user_name, "setor_origem": st.session_state.setor_user, "status": "Aberto", "urgencia": urg}).execute()
                    st.success("Ticket Criado!"); st.rerun()
        with t1:
            res_tk = supabase.table("chamados").select("*").eq("setor_destino", st.session_state.setor_user).order("id", desc=True).execute()
            for tk in res_tk.data:
                with st.container():
                    st.markdown(f"<div class='ticket-card'><b>[{tk['status']}] {tk['titulo']}</b><br><small>Urgência: {tk['urgencia']} | De: {tk['solicitante']}</small><p>{tk['descricao']}</p></div>", unsafe_allow_html=True)
                    if tk['status'] == "Aberto":
                        if st.button("ASSUMIR", key=f"tk_{tk['id']}"):
                            supabase.table("chamados").update({"status": "Em Atendimento", "responsavel_tecnico": st.session_state.user_name}).eq("id", tk['id']).execute()
                            st.rerun()

    # 2. DASHBOARD (KPIs RESTAURADOS)
    elif p == "dash":
        st.title("Dashboard de Produção")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").execute()
        if res.data:
            df = pd.DataFrame([{"OS": i['numero_pedido'], "Projeto": i['projetos']['nome_projeto'] if i['projetos'] else "-", "Status": i['status_geral'], "Prazo": i['prazo_entrega']} for i in res.data])
            c1, c2, c3 = st.columns(3)
            c1.metric("Carteira Total", len(res.data))
            c2.metric("Em Produção", len(df[df['Status'] == 'EM PRODUÇÃO']))
            c3.metric("Fiscalização", len(df[df['Status'] == 'EM FISCALIZAÇÃO']))
            st.dataframe(df, use_container_width=True, hide_index=True)

    # 3. FINANCEIRO (RECEITA RESTAURADO)
    elif p == "fin":
        st.title("Financeiro | Receita Total")
        res = supabase.table("pedidos").select("numero_pedido, valor_orcamento").execute()
        total = sum([float(x['valor_orcamento']) for x in res.data if x['valor_orcamento']])
        st.metric("Receita Bruta Acumulada", f"R$ {total:,.2f}")
        st.dataframe(pd.DataFrame(res.data), use_container_width=True)

    # 4. LOGÍSTICA - VALIDAÇÃO (FISCALIZAÇÃO RESTAURADO)
    elif p == "val":
        st.title("Logística | Validação (Fiscalização)")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "EM FISCALIZAÇÃO").execute()
        if res.data:
            for os in res.data:
                st.markdown(f"<div class='row-monitor'><b>OS: {os['numero_pedido']}</b> | {os['projetos']['nome_projeto']}</div>", unsafe_allow_html=True)
                if st.button(f"LIBERAR PARA ENTREGA: {os['numero_pedido']}", key=f"v_{os['id']}"):
                    supabase.table("pedidos").update({"status_geral": "AGUARDANDO ENTREGA"}).eq("id", os['id']).execute()
                    st.rerun()
        else: st.info("Nada para fiscalizar.")

    # 5. LOGÍSTICA - ENTREGA (FRETE RESTAURADO)
    elif p == "ent":
        st.title("Logística | Programação de Entrega")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "AGUARDANDO ENTREGA").execute()
        if res.data:
            sel = st.selectbox("OS:", [x['numero_pedido'] for x in res.data])
            os_d = next(x for x in res.data if x['numero_pedido'] == sel)
            with st.form("f_ent"):
                c1, c2 = st.columns(2)
                t, f = c1.text_input("Transportadora"), c1.number_input("Valor Frete R$")
                dr, de = c2.date_input("Saída"), c2.date_input("Previsão Entrega")
                if st.form_submit_button("FINALIZAR LOGÍSTICA"):
                    supabase.table("pedidos").update({"status_geral": "CONCLUÍDO"}).eq("id", os_d['id']).execute()
                    st.success("OS Concluída!"); st.rerun()

    # 6. CHÃO DE FÁBRICA (7 ETAPAS + MÉTRICAS)
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
                                # Gatilho Fiscalização Automática
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

    # 7. COMERCIAL (AUTO OS + PV/PO)
    elif p == "com":
        st.title("Projetos | Comercial")
        with st.expander("Novo Orçamento", expanded=True):
            p_db = supabase.table("projetos").select("id, nome_projeto").execute()
            l_p = {x['nome_projeto']: x['id'] for x in p_db.data}
            with st.form("f_c"):
                no = st.text_input("Nº OS", value=get_proxima_os())
                po_sel = st.selectbox("Projeto", list(l_p.keys()))
                vo = st.number_input("Valor R$")
                if st.form_submit_button("CADASTRAR"):
                    r = supabase.table("pedidos").insert({"numero_pedido": no, "id_projeto": l_p[po_sel], "valor_orcamento": vo, "status_geral": "EXECUTANDO ORÇAMENTO"}).execute()
                    if r.data: supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                    st.rerun()
        st.divider()
        ped = supabase.table("pedidos").select("*").neq("status_geral", "CONCLUÍDO").execute()
        for i in ped.data:
            with st.expander(f"OS: {i['numero_pedido']} | {i['status_geral']}"):
                pv, po = st.text_input("Nº PV", value=i.get('num_pv', ''), key=f"pv_{i['id']}"), st.text_input("Nº PO", value=i.get('num_po', ''), key=f"po_{i['id']}")
                if st.button("ATUALIZAR STATUS", key=f"u_{i['id']}"):
                    ns = "EM PRODUÇÃO" if po else ("ORÇAMENTO APROVADO" if pv else i['status_geral'])
                    supabase.table("pedidos").update({"num_pv": pv, "num_po": po, "status_geral": ns}).eq("id", i['id']).execute()
                    st.rerun()

    # 8. CADASTROS (DADOS MESTRES RESTAURADOS)
    elif p == "cad":
        st.title("Administração | Cadastros de Base")
        c1, c2 = st.columns(2)
        with c1:
            with st.form("f_cli"):
                n, e, t, o = st.text_input("Responsável"), st.text_input("Empresa"), st.text_input("Telefone"), st.text_area("Endereço Completo")
                if st.form_submit_button("SALVAR CLIENTE"):
                    supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t, "info_adicional": o}).execute()
                    st.success("Salvo!")
        with c2:
            s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
            l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
            with st.form("f_proj"):
                np, sid = st.text_input("Título Projeto"), st.selectbox("Cliente", list(l_s.keys()))
                cid, rua, num, cep = st.text_input("Cidade"), st.text_input("Rua"), st.text_input("Nº"), st.text_input("CEP")
                if st.form_submit_button("VINCULAR PROJETO"):
                    supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": rua, "numero": num, "cep": cep}).execute()
                    st.success("Vinculado!")

    # 9. GESTÃO EQUIPE (SETORES RESTAURADO)
    elif p == "adm":
        st.title("Gestão de Equipe e Auditoria")
        t1, t2 = st.tabs(["Usuários", "Logs"])
        with t1:
            u_db = supabase.table("usuarios").select("*").execute()
            st.dataframe(pd.DataFrame(u_db.data)[['login', 'perfil', 'setor']], use_container_width=True)
            with st.form("nu"):
                nl, ns = st.text_input("Login"), st.text_input("Senha")
                np = st.selectbox("Perfil", ["admin", "producao"])
                nset = st.selectbox("Setor", SETORES)
                if st.form_submit_button("CRIAR"):
                    supabase.table("usuarios").insert({"login": nl, "senha": ns, "perfil": np, "setor": nset}).execute()
                    st.rerun()

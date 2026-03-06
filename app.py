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

LOGO_URL = "https://i.ibb.co/6Lr0QZY/nexus-2.png"

# 3. CSS PREMIUM (Sidebar #202c65 e Fundo Branco)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    .stApp { background-color: #FFFFFF !important; color: #1e293b !important; font-family: 'Inter', sans-serif !important; }
    [data-testid="stSidebar"] { background-color: #202c65 !important; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .stSidebar .stExpander { background-color: transparent !important; border: none !important; padding: 0px !important; }
    .stSidebar button {
        background-color: transparent !important; border: none !important; color: #FFFFFF !important;
        text-align: left !important; width: 100% !important; padding: 8px 15px !important;
        font-size: 11px !important; text-transform: uppercase !important; font-weight: 500 !important;
    }
    .stSidebar button:hover { background-color: #3b82f6 !important; }
    .row-monitor { background: #f8fafc; border-radius: 12px; padding: 20px; margin-bottom: 12px; border-left: 8px solid #3b82f6; border: 1px solid #e2e8f0; }
    .dot { height: 18px; width: 18px; border-radius: 50%; display: inline-block; margin: 4px auto; border: 2px solid #FFF; }
    .bg-success { background-color: #238636; box-shadow: 0 0 10px rgba(35, 134, 54, 0.4); }
    .bg-danger { background-color: #da3633; box-shadow: 0 0 8px rgba(218, 54, 51, 0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
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

# --- LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<div style='text-align: center; padding-top: 100px;'><h1 style='color: #202c65;'>Solluz systems</h1></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("login"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.update({"autenticado": True, "perfil": res.data[0]['perfil'], "user_name": res.data[0]['login']})
                    st.rerun()
                else: st.error("Erro de acesso.")
else:
    # --- BARRA LATERAL ESTRUTURADA ---
    with st.sidebar:
        st.image(LOGO_URL, width=180)
        st.write(f"Solluz | **{st.session_state.user_name.upper()}**")
        st.divider()

        if 'pagina_ativa' not in st.session_state:
            st.session_state.pagina_ativa = "dash"

        if st.session_state.perfil == "admin":
            with st.expander("CONTROLE OPERACIONAL", expanded=True):
                if st.button("DASHBOARD"): st.session_state.pagina_ativa = "dash"; st.rerun()
                if st.button("RELATÓRIOS"): st.session_state.pagina_ativa = "rel"; st.rerun()
                if st.button("MONITORAMENTO"): st.session_state.pagina_ativa = "tv"; st.rerun()
            
            with st.expander("FINANCEIRO"):
                if st.button("RECEITA TOTAL"): st.session_state.pagina_ativa = "fin"; st.rerun()

            with st.expander("LOGÍSTICA"):
                if st.button("VALIDAÇÃO"): st.session_state.pagina_ativa = "log_val"; st.rerun()
                if st.button("ENTREGA"): st.session_state.pagina_ativa = "log_ent"; st.rerun()

            with st.expander("ADMINISTRAÇÃO"):
                if st.button("CADASTROS"): st.session_state.pagina_ativa = "cad"; st.rerun()
                if st.button("GESTÃO SISTEMA"): st.session_state.pagina_ativa = "adm"; st.rerun()

            with st.expander("PROJETOS"):
                if st.button("COMERCIAL"): st.session_state.pagina_ativa = "com"; st.rerun()
                if st.button("WORKFLOW OS"): st.session_state.pagina_ativa = "work"; st.rerun()

        with st.expander("PRODUÇÃO", expanded=True):
            if st.button("CHÃO DE FÁBRICA"): st.session_state.pagina_ativa = "fab"; st.rerun()

        st.divider()
        if st.button("SAIR"):
            st.session_state.autenticado = False
            st.rerun()

    # --- RENDERIZAÇÃO DE PÁGINAS ---
    p = st.session_state.pagina_ativa

    # PAGINA: DASHBOARD
    if p == "dash":
        st.title("Indicadores Operacionais")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").execute()
        if res.data:
            df = pd.DataFrame([{"OS": i['numero_pedido'], "Projeto": i['projetos']['nome_projeto'] if i['projetos'] else "-", "Status": i['status_geral'], "Prazo": i['prazo_entrega']} for i in res.data])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # PAGINA: RELATÓRIOS
    elif p == "rel":
        st.title("Relatórios de Produtividade")
        res_rel = supabase.table("linha_producao").select("*, pedidos(numero_pedido)").execute()
        if res_rel.data:
            dados = [{"OS": r['pedidos']['numero_pedido'], 
                      "Corte (h)": calcular_horas(r.get('corte_inicio'), r.get('corte_fim')),
                      "Solda (h)": calcular_horas(r.get('solda_inicio'), r.get('solda_fim')),
                      "Pintura (h)": calcular_horas(r.get('pintura_inicio'), r.get('pintura_fim'))} for r in res_rel.data if r['pedidos']]
            df_rel = pd.DataFrame(dados)
            st.bar_chart(df_rel.set_index("OS"))
            st.dataframe(df_rel, use_container_width=True)

    # PAGINA: MONITOR TV
    elif p == "tv":
        st.title("Monitoramento Industrial")
        res_tv = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        for o in res_tv.data:
            lp = o['linha_producao'][0] if o['linha_producao'] else {}
            st.markdown(f"<div class='row-monitor'><div style='flex: 1;'><b>{o['numero_pedido']}</b><br>{o['projetos']['nome_projeto'] if o['projetos'] else ''}</div><div style='flex: 2; display: flex; justify-content: space-around;'>Corte <div class='dot {'bg-success' if lp.get('corte_fim') else 'bg-danger'}'></div> Solda <div class='dot {'bg-success' if lp.get('solda_fim') else 'bg-danger'}'></div> Pintura <div class='dot {'bg-success' if lp.get('pintura_fim') else 'bg-danger'}'></div></div></div>", unsafe_allow_html=True)

    # PAGINA: FINANCEIRO
    elif p == "fin":
        st.title("Financeiro | Receita Bruta")
        res_fin = supabase.table("pedidos").select("valor_orcamento").execute()
        total = sum([float(x['valor_orcamento']) for x in res_fin.data if x['valor_orcamento']])
        st.metric("Receita Total Acumulada", f"R$ {total:,.2f}")

    # PAGINA: CHÃO DE FÁBRICA (CORREÇÃO KEYERROR)
    elif p == "fab":
        st.title("Produção | Chão de Fábrica")
        atv = supabase.table("pedidos").select("*, linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        
        if atv.data:
            sel = st.selectbox("Selecione a OS:", [x['numero_pedido'] for x in atv.data])
            item = next(x for x in atv.data if x['numero_pedido'] == sel)
            prod = item['linha_producao'][0]

            def render_etapa(label, campo, hab):
                if hab:
                    with st.expander(f"PROCESSO: {label.upper()}", expanded=True):
                        c1, c2, c3 = st.columns([1, 1, 2])
                        i, f = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                        if not i:
                            if c1.button("INICIAR", key=f"i_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", item['id']).execute()
                                registrar_log("PRODUCAO", f"Iniciou {label} na OS {sel}")
                                st.rerun()
                        elif not f:
                            obs = c3.text_input("Observação", key=f"o_{campo}")
                            if c2.button("FINALIZAR ETAPA", key=f"f_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_fim": "now()", f"{campo}_obs": obs}).eq("id_pedido", item['id']).execute()
                                
                                # Verificação para Fiscalização
                                r_check = supabase.table("pedidos").select("*, linha_producao(*)").eq("id", item['id']).single().execute().data
                                lp = r_check['linha_producao'][0]
                                
                                # Mapeamento explícito para evitar KeyError
                                checklist = {
                                    "has_corte_laser": "corte_fim", "has_dobra_cnc": "dobra_fim",
                                    "has_solda": "solda_fim", "has_metaleira": "metaleira_fim",
                                    "has_calandragem": "calandragem_fim", "has_galvanizacao": "galvanizacao_fim",
                                    "has_pintura": "pintura_fim"
                                }
                                
                                concluido_geral = True
                                for col_has, col_fim in checklist.items():
                                    if r_check.get(col_has) == True and not lp.get(col_fim):
                                        concluido_geral = False
                                        break
                                
                                if concluido_geral:
                                    supabase.table("pedidos").update({"status_geral": "EM FISCALIZAÇÃO"}).eq("id", item['id']).execute()
                                    registrar_log("SISTEMA", f"OS {sel} enviada para fiscalização")
                                st.rerun()
                        else: st.success(f"{label} Concluído")

            render_etapa("Corte", "corte", item['has_corte_laser'])
            render_etapa("Dobra", "dobra", item['has_dobra_cnc'])
            render_etapa("Solda", "solda", item['has_solda'])
            render_etapa("Metaleira", "metaleira", item['has_metaleira'])
            render_etapa("Calandragem", "calandragem", item['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", item['has_galvanizacao'])
            render_etapa("Pintura", "pintura", item['has_pintura'])
        else:
            st.info("Nenhuma OS em produção.")

    # PAGINA: LOGÍSTICA - VALIDAÇÃO
    elif p == "log_val":
        st.title("Logística | Fiscalização")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "EM FISCALIZAÇÃO").execute()
        if res.data:
            for os in res.data:
                with st.container():
                    st.markdown(f"<div class='row-monitor'><b>OS: {os['numero_pedido']}</b> - {os['projetos']['nome_projeto'] if os['projetos'] else ''}</div>", unsafe_allow_html=True)
                    if st.button(f"APROVAR PARA ENTREGA: {os['numero_pedido']}", key=f"ap_{os['id']}"):
                        supabase.table("pedidos").update({"status_geral": "AGUARDANDO ENTREGA"}).eq("id", os['id']).execute()
                        st.rerun()
        else: st.info("Nada para fiscalizar.")

    # PAGINA: LOGÍSTICA - ENTREGA
    elif p == "log_ent":
        st.title("Logística | Programação de Entrega")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "AGUARDANDO ENTREGA").execute()
        if res.data:
            sel_ent = st.selectbox("OS:", [x['numero_pedido'] for x in res.data])
            os_d = next(x for x in res.data if x['numero_pedido'] == sel_ent)
            with st.form("f_ent"):
                c1, c2 = st.columns(2)
                transp = c1.text_input("Transportadora")
                frete = c1.number_input("Frete R$", min_value=0.0)
                d_ret = c2.date_input("Data Retirada")
                d_ent = c2.date_input("Data Entrega")
                if st.form_submit_button("FINALIZAR"):
                    supabase.table("pedidos").update({"status_geral": "CONCLUÍDO"}).eq("id", os_d['id']).execute()
                    st.success("Entrega registrada!")
                    st.rerun()

    # PAGINA: CADASTROS
    elif p == "cad":
        st.title("Administração | Cadastros")
        c1, c2 = st.columns(2)
        with c1:
            with st.form("f_sol"):
                n, e, t, o = st.text_input("Responsável"), st.text_input("Empresa"), st.text_input("Telefone"), st.text_area("Notas")
                if st.form_submit_button("SALVAR CLIENTE"):
                    supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t, "info_adicional": o}).execute()
                    st.success("Salvo")
        with c2:
            s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
            l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
            with st.form("f_proj"):
                np, sid, cid = st.text_input("Título"), st.selectbox("Cliente", list(l_s.keys())), st.text_input("Cidade")
                end, num, cep = st.text_input("Endereço"), st.text_input("Nº"), st.text_input("CEP")
                if st.form_submit_button("VINCULAR PROJETO"):
                    supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": end, "numero": num, "cep": cep}).execute()
                    st.success("Vinculado")

    # PAGINA: GESTÃO SISTEMA
    elif p == "adm":
        st.title("Gestão de Equipe e Logs")
        t1, t2 = st.tabs(["EQUIPE", "AUDITORIA"])
        with t1:
            users = supabase.table("usuarios").select("*").execute()
            st.dataframe(pd.DataFrame(users.data)[['login', 'perfil']], use_container_width=True)
            with st.form("nu"):
                nl, ns, np = st.text_input("Login"), st.text_input("Senha"), st.selectbox("Perfil", ["admin", "producao"])
                if st.form_submit_button("CADASTRAR"):
                    supabase.table("usuarios").insert({"login": nl, "senha": ns, "perfil": np}).execute()
                    st.rerun()
        with t2:
            logs = supabase.table("logs_sistema").select("*").order("data_hora", desc=True).limit(50).execute()
            if logs.data: st.table(pd.DataFrame(logs.data)[['data_hora', 'usuario', 'acao', 'detalhe']])

    # PAGINA: COMERCIAL
    elif p == "com":
        st.title("Projetos | Comercial")
        with st.expander("Novo Orçamento", expanded=True):
            p_db = supabase.table("projetos").select("id, nome_projeto").execute()
            l_p = {x['nome_projeto']: x['id'] for x in p_db.data}
            with st.form("f_c"):
                c1, c2 = st.columns(2)
                no, po = c1.text_input("Nº Orçamento"), c1.selectbox("Projeto", list(l_p.keys()))
                vo, de = c2.number_input("Valor R$", min_value=0.0), c2.date_input("Prazo")
                if st.form_submit_button("CADASTRAR"):
                    r = supabase.table("pedidos").insert({"numero_pedido": no, "id_projeto": l_p[po], "valor_orcamento": vo, "prazo_entrega": str(de), "status_geral": "EXECUTANDO ORÇAMENTO"}).execute()
                    supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                    st.rerun()
        st.divider()
        p_p = supabase.table("pedidos").select("*").neq("status_geral", "CONCLUÍDO").execute()
        for i in p_p.data:
            with st.expander(f"OS: {i['numero_pedido']} | {i['status_geral']}"):
                c1, c2 = st.columns(2)
                pv, po = c1.text_input("PV", value=i.get('num_pv', ''), key=f"pv_{i['id']}"), c2.text_input("PO", value=i.get('num_po', ''), key=f"po_{i['id']}")
                if st.button("ATUALIZAR", key=f"u_{i['id']}"):
                    ns = "ORÇAMENTO APROVADO" if pv and not po else ("EM PRODUÇÃO" if po else i['status_geral'])
                    supabase.table("pedidos").update({"num_pv": pv, "num_po": po, "status_geral": ns}).eq("id", i['id']).execute()
                    st.rerun()

    # PAGINA: WORKFLOW
    elif p == "work":
        st.title("Workflow OS")
        p_wf = supabase.table("pedidos").select("*").eq("status_geral", "EM PRODUÇÃO").execute()
        if p_wf.data:
            sel = st.selectbox("OS", [x['numero_pedido'] for x in p_wf.data])
            id_w = next(x['id'] for x in p_wf.data if x['numero_pedido'] == sel)
            with st.form("f_wf"):
                arq = st.file_uploader("Desenho")
                e1, e2 = st.columns(2)
                h1, h2, h3, h4, h5, h6, h7 = e1.checkbox("Corte"), e1.checkbox("Dobra"), e1.checkbox("Solda"), e1.checkbox("Meta"), e2.checkbox("Calan"), e2.checkbox("Galva"), e2.checkbox("Pint")
                if st.form_submit_button("SALVAR"):
                    supabase.table("pedidos").update({"has_corte_laser": h1, "has_dobra_cnc": h2, "has_solda": h3, "has_metaleira": h4, "has_calandragem": h5, "has_galvanizacao": h6, "has_pintura": h7}).eq("id", id_w).execute()
                    st.success("Workflow Configurado")

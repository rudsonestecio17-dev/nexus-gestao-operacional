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

# 3. CSS "CTRL BRANDING" (Violeta Tecnológico + Fundo Branco)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    .stApp { background-color: #FFFFFF !important; color: #1e293b !important; font-family: 'Inter', sans-serif !important; }
    
    /* Sidebar Identidade Solluz Systems */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #202c65 0%, #35337a 100%) !important; 
        border-right: 1px solid #e2e8f0; 
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Submenus e Botões Lateral */
    .stSidebar .stExpander { background-color: transparent !important; border: none !important; padding: 0px !important; }
    .stSidebar button {
        background-color: transparent !important; border: none !important; color: #FFFFFF !important;
        text-align: left !important; width: 100% !important; padding: 10px 15px !important;
        font-size: 11px !important; text-transform: uppercase !important; font-weight: 600 !important;
    }
    .stSidebar button:hover { background-color: #3b82f6 !important; }

    /* Monitor e Cards */
    .row-monitor { 
        background: #f8fafc; border-radius: 12px; padding: 20px; margin-bottom: 12px; 
        border: 1px solid #e2e8f0; border-left: 8px solid #3b82f6; 
        display: flex; justify-content: space-between; align-items: center;
    }
    .dot { height: 18px; width: 18px; border-radius: 50%; display: inline-block; margin: 4px auto; border: 2px solid #FFF; }
    .bg-success { background-color: #22c55e; }
    .bg-danger { background-color: #ef4444; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES TÉCNICAS ---
def registrar_log(acao, detalhe):
    usuario = st.session_state.get('user_name', 'Sistema')
    try: supabase.table("logs_sistema").insert({"usuario": usuario, "acao": acao, "detalhe": detalhe}).execute()
    except: pass

def get_proxima_os():
    try:
        res = supabase.table("pedidos").select("numero_pedido").order("id", desc=True).limit(1).execute()
        return str(int(res.data[0]['numero_pedido']) + 1) if res.data else "1001"
    except: return "1001"

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
    st.markdown("<div style='text-align: center; padding-top: 100px;'><h1 style='color: #202c65; font-size: 4em;'>CTRL</h1><p>GESTÃO DE PRODUÇÃO</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("login"):
            u, s = st.text_input("Usuário"), st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.update({"autenticado": True, "perfil": res.data[0]['perfil'], "user_name": res.data[0]['login']})
                    st.rerun()
                else: st.error("Acesso Negado.")
else:
    # --- SIDEBAR ESTRUTURADA (O "CÉREBRO" DO MENU) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>CTRL</h2>", unsafe_allow_html=True)
        st.caption(f"<p style='text-align:center; color:white;'>{st.session_state.user_name.upper()}</p>", unsafe_allow_html=True)
        st.divider()
        if 'p' not in st.session_state: st.session_state.p = "dash"

        with st.expander("CONTROLE OPERACIONAL", expanded=True):
            if st.button("DASHBOARD"): st.session_state.p = "dash"; st.rerun()
            if st.button("RELATÓRIOS"): st.session_state.p = "rel"; st.rerun()
            if st.button("MONITORAMENTO"): st.session_state.p = "tv"; st.rerun()
        with st.expander("FINANCEIRO"):
            if st.button("RECEITA TOTAL"): st.session_state.p = "fin"; st.rerun()
        with st.expander("LOGÍSTICA"):
            if st.button("VALIDAÇÃO"): st.session_state.p = "val"; st.rerun()
            if st.button("ENTREGA"): st.session_state.p = "ent"; st.rerun()
        with st.expander("ADMINISTRAÇÃO"):
            if st.button("CADASTROS"): st.session_state.p = "cad"; st.rerun()
            if st.button("GESTÃO SISTEMA"): st.session_state.p = "adm"; st.rerun()
        with st.expander("PROJETOS"):
            if st.button("COMERCIAL"): st.session_state.p = "com"; st.rerun()
            if st.button("WORKFLOW OS"): st.session_state.p = "work"; st.rerun()
        with st.expander("PRODUÇÃO", expanded=True):
            if st.button("CHÃO DE FÁBRICA"): st.session_state.p = "fab"; st.rerun()

        st.divider()
        if st.button("LOGOUT"): st.session_state.autenticado = False; st.rerun()

    # --- RENDERIZAÇÃO DAS PÁGINAS ---
    pg = st.session_state.p

    if pg == "dash":
        st.title("Dashboard de Produção")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").execute()
        if res.data:
            df_dash = []
            for i in res.data:
                lp = i['linha_producao'][0] if i['linha_producao'] else {}
                df_dash.append({
                    "OS": i['numero_pedido'], "Projeto": i['projetos']['nome_projeto'] if i['projetos'] else "-",
                    "Prazo": i['prazo_entrega'], "Status": i['status_geral'],
                    "Corte": "OK" if lp.get('corte_fim') else "...", "Solda": "OK" if lp.get('solda_fim') else "..."
                })
            st.dataframe(pd.DataFrame(df_dash), use_container_width=True, hide_index=True)

    elif pg == "rel":
        st.title("Relatórios de Produtividade")
        res = supabase.table("linha_producao").select("*, pedidos(numero_pedido)").execute()
        if res.data:
            dados = [{"OS": r['pedidos']['numero_pedido'], 
                      "Corte (h)": calcular_horas(r.get('corte_inicio'), r.get('corte_fim')),
                      "Solda (h)": calcular_horas(r.get('solda_inicio'), r.get('solda_fim'))} for r in res.data if r['pedidos']]
            df_rel = pd.DataFrame(dados)
            st.bar_chart(df_rel.set_index("OS"))
            st.dataframe(df_rel, use_container_width=True)

    elif pg == "tv":
        st.title("Monitoramento Industrial")
        res_tv = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        for o in res_tv.data:
            lp = o['linha_producao'][0] if o['linha_producao'] else {}
            st.markdown(f"<div class='row-monitor'><div style='flex: 1;'><b>{o['numero_pedido']}</b><br>{o['projetos']['nome_projeto'] if o['projetos'] else ''}</div><div style='flex: 2; display: flex; justify-content: space-around;'>Corte <div class='dot {'bg-success' if lp.get('corte_fim') else 'bg-danger'}'></div> Solda <div class='dot {'bg-success' if lp.get('solda_fim') else 'bg-danger'}'></div> Pintura <div class='dot {'bg-success' if lp.get('pintura_fim') else 'bg-danger'}'></div></div></div>", unsafe_allow_html=True)

    elif pg == "fin":
        st.title("Financeiro | Receita Bruta")
        res_fin = supabase.table("pedidos").select("numero_pedido, valor_orcamento").execute()
        total = sum([float(x['valor_orcamento']) for x in res_fin.data if x['valor_orcamento']])
        st.metric("Receita Acumulada R$", f"{total:,.2f}")
        st.dataframe(pd.DataFrame(res_fin.data), use_container_width=True)

    elif pg == "val":
        st.title("Logística | Validação (Fiscalização)")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "EM FISCALIZAÇÃO").execute()
        for os in res.data:
            with st.container():
                st.write(f"**OS: {os['numero_pedido']}** | Projeto: {os['projetos']['nome_projeto'] if os['projetos'] else '-'}")
                if st.button(f"LIBERAR PARA ENTREGA: {os['numero_pedido']}", key=f"v_{os['id']}"):
                    supabase.table("pedidos").update({"status_geral": "AGUARDANDO ENTREGA"}).eq("id", os['id']).execute()
                    st.rerun()

    elif pg == "ent":
        st.title("Logística | Entrega e Frete")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").eq("status_geral", "AGUARDANDO ENTREGA").execute()
        if res.data:
            sel = st.selectbox("Selecione a OS:", [x['numero_pedido'] for x in res.data])
            os_d = next(x for x in res.data if x['numero_pedido'] == sel)
            with st.form("f_ent"):
                t, f = st.text_input("Transportadora"), st.number_input("Frete R$")
                dr, de = st.date_input("Saída"), st.date_input("Entrega")
                if st.form_submit_button("FINALIZAR"):
                    supabase.table("pedidos").update({"status_geral": "CONCLUÍDO"}).eq("id", os_d['id']).execute()
                    st.success("OS Concluída!")
                    st.rerun()

    elif pg == "cad":
        st.title("Administração | Cadastros")
        c1, c2 = st.columns(2)
        with c1:
            with st.form("f_c"):
                st.subheader("Novo Cliente")
                n, e, t, o = st.text_input("Responsável"), st.text_input("Empresa"), st.text_input("Telefone"), st.text_area("Endereço/Obs")
                if st.form_submit_button("CADASTRAR CLIENTE"):
                    supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t, "info_adicional": o}).execute()
                    st.success("Salvo!")
        with c2:
            s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
            l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
            with st.form("f_p"):
                st.subheader("Novo Projeto")
                np, sid = st.text_input("Título"), st.selectbox("Cliente", list(l_s.keys()))
                cid, rua, num, cep = st.text_input("Cidade"), st.text_input("Rua"), st.text_input("Nº"), st.text_input("CEP")
                if st.form_submit_button("VINCULAR PROJETO"):
                    supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": rua, "numero": num, "cep": cep}).execute()
                    st.success("Vinculado!")

    elif pg == "adm":
        st.title("Administração | Equipe e Logs")
        t1, t2 = st.tabs(["Usuários", "Auditoria"])
        with t1:
            u_db = supabase.table("usuarios").select("*").execute()
            st.dataframe(pd.DataFrame(u_db.data)[['login', 'perfil']], use_container_width=True)
            with st.form("nu"):
                nl, ns, np = st.text_input("Login"), st.text_input("Senha"), st.selectbox("Perfil", ["admin", "producao"])
                if st.form_submit_button("CRIAR"):
                    supabase.table("usuarios").insert({"login": nl, "senha": ns, "perfil": np}).execute()
                    st.rerun()
        with t2:
            logs = supabase.table("logs_sistema").select("*").order("data_hora", desc=True).limit(50).execute()
            if logs.data: st.table(pd.DataFrame(logs.data)[['data_hora', 'usuario', 'acao', 'detalhe']])

    elif pg == "com":
        st.title("Projetos | Comercial")
        with st.expander("Novo Orçamento", expanded=True):
            p_db = supabase.table("projetos").select("id, nome_projeto").execute()
            l_p = {x['nome_projeto']: x['id'] for x in p_db.data}
            with st.form("f_com"):
                no, po = st.text_input("Nº OS", value=get_proxima_os()), st.selectbox("Projeto", list(l_p.keys()))
                vo, de = st.number_input("Valor R$"), st.date_input("Prazo")
                if st.form_submit_button("SALVAR"):
                    r = supabase.table("pedidos").insert({"numero_pedido": no, "id_projeto": l_p[po], "valor_orcamento": vo, "prazo_entrega": str(de), "status_geral": "EXECUTANDO ORÇAMENTO"}).execute()
                    supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                    st.rerun()

    elif pg == "work":
        st.title("Projetos | Workflow OS")
        p_wf = supabase.table("pedidos").select("*").eq("status_geral", "EM PRODUÇÃO").execute()
        if p_wf.data:
            sel = st.selectbox("OS", [x['numero_pedido'] for x in p_wf.data])
            id_w = next(x['id'] for x in p_wf.data if x['numero_pedido'] == sel)
            with st.form("f_wf"):
                h1, h2, h3, h4, h5, h6, h7 = st.checkbox("Corte"), st.checkbox("Dobra"), st.checkbox("Solda"), st.checkbox("Meta"), st.checkbox("Calan"), st.checkbox("Galva"), st.checkbox("Pint")
                if st.form_submit_button("CONFIGURAR"):
                    supabase.table("pedidos").update({"has_corte_laser": h1, "has_dobra_cnc": h2, "has_solda": h3, "has_metaleira": h4, "has_calandragem": h5, "has_galvanizacao": h6, "has_pintura": h7}).eq("id", id_w).execute()
                    st.success("Salvo!")

    elif pg == "fab":
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
                        if not i:
                            if c1.button("INICIAR", key=f"i_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", item['id']).execute()
                                st.rerun()
                        elif not f:
                            obs = c3.text_input("Obs", key=f"o_{campo}")
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
                        else: st.success(f"Finalizado: {i[11:16]} - {f[11:16]}")

            render_etapa("Corte", "corte", item['has_corte_laser'])
            render_etapa("Dobra", "dobra", item['has_dobra_cnc'])
            render_etapa("Solda", "solda", item['has_solda'])
            render_etapa("Metaleira", "metaleira", item['has_metaleira'])
            render_etapa("Calandragem", "calandragem", item['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", item['has_galvanizacao'])
            render_etapa("Pintura", "pintura", item['has_pintura'])

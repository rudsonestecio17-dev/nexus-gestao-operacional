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

# LISTA DE SETORES CTRL
SETORES = ["Tecnologia e Marketing", "Diretoria", "Gerência", "Operações Manutenção", "Projetos", "Comercial", "Compras", "Engenharia", "Orçamentos"]

# 2. CSS EMPRESARIAL (Violeta Tecnológico + Correção de Interface)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    .stApp { background-color: #FFFFFF; color: #1e293b; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .stSidebar .stExpander { background-color: rgba(255, 255, 255, 0.05) !important; border-radius: 10px !important; margin-bottom: 8px !important; border: none !important; }
    .stSidebar button { background-color: transparent !important; border: none !important; color: #FFFFFF !important; text-align: left !important; width: 100% !important; padding: 12px 15px !important; font-size: 11px !important; text-transform: uppercase !important; font-weight: 600 !important; }
    .stSidebar button:hover { background-color: #4f46e5 !important; border-radius: 5px; }
    .row-monitor { background: #f8fafc; border-radius: 12px; padding: 25px; margin-bottom: 15px; border: 1px solid #e2e8f0; border-left: 10px solid #6366f1; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .dot { height: 20px; width: 20px; border-radius: 50%; display: inline-block; margin: 4px auto; border: 3px solid #FFF; }
    .bg-success { background-color: #10b981; }
    .bg-danger { background-color: #ef4444; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES CORE ---
def calcular_horas(inicio, fim):
    if inicio and fim:
        try:
            fmt = "%Y-%m-%dT%H:%M:%S"
            diff = datetime.strptime(fim[:19], fmt) - datetime.strptime(inicio[:19], fmt)
            return round(diff.total_seconds() / 3600, 2)
        except: return 0
    return 0

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
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>CTRL</h2>", unsafe_allow_html=True)
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

        with st.expander("PROJETOS / PRODUÇÃO"):
            if st.button("COMERCIAL"): st.session_state.pg = "com"; st.rerun()
            if st.button("WORKFLOW OS"): st.session_state.pg = "work"; st.rerun()
            if st.button("CHÃO DE FÁBRICA"): st.session_state.pg = "fab"; st.rerun()

        st.divider()
        if st.button("LOGOUT"): st.session_state.autenticado = False; st.rerun()

    p = st.session_state.pg

    # 1. PÁGINA DASHBOARD (RESTAURADA E FUNCIONAL)
    if p == "dash":
        st.title("Dashboard de Produção")
        res = supabase.table("pedidos").select("*, projetos(nome_projeto)").execute()
        if res.data:
            df = pd.DataFrame([{"OS": i['numero_pedido'], "Projeto": i['projetos']['nome_projeto'] if i['projetos'] else "-", "Status": i['status_geral'], "Prazo": i['prazo_entrega']} for i in res.data])
            c1, c2, c3 = st.columns(3)
            c1.metric("Total de Pedidos", len(res.data))
            c2.metric("Em Produção", len(df[df['Status'] == 'EM PRODUÇÃO']))
            c3.metric("Concluídos", len(df[df['Status'] == 'CONCLUÍDO']))
            st.dataframe(df, use_container_width=True, hide_index=True)

    # 2. PÁGINA FINANCEIRO (RECEITA TOTAL RESTAURADA)
    elif p == "fin":
        st.title("Financeiro | Receita Total")
        res_fin = supabase.table("pedidos").select("numero_pedido, valor_orcamento, status_geral").execute()
        if res_fin.data:
            total = sum([float(x['valor_orcamento']) for x in res_fin.data if x['valor_orcamento']])
            st.metric("Receita Bruta Total em Carteira", f"R$ {total:,.2f}")
            df_fin = pd.DataFrame(res_fin.data)
            st.table(df_fin)

    # 3. PÁGINA GESTÃO EQUIPE (RESTAURADA E FUNCIONAL)
    elif p == "adm":
        st.title("Gestão de Equipe e Auditoria")
        t1, t2 = st.tabs(["Usuários", "Logs do Sistema"])
        with t1:
            u_db = supabase.table("usuarios").select("*").execute()
            if u_db.data:
                st.dataframe(pd.DataFrame(u_db.data)[['login', 'perfil', 'setor']], use_container_width=True)
            with st.form("novo_usuario"):
                st.subheader("Cadastrar Novo Membro")
                nl, ns = st.text_input("Login"), st.text_input("Senha")
                np = st.selectbox("Perfil", ["admin", "producao"])
                nset = st.selectbox("Setor", SETORES)
                if st.form_submit_button("CADASTRAR"):
                    supabase.table("usuarios").insert({"login": nl, "senha": ns, "perfil": np, "setor": nset}).execute()
                    st.success("Usuário cadastrado!"); st.rerun()

    # 4. MONITORAMENTO (TV/PAINEL RESTAURADO)
    elif p == "tv":
        st.title("Monitoramento Industrial em Tempo Real")
        res_tv = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        if res_tv.data:
            for o in res_tv.data:
                lp = o['linha_producao'][0] if o['linha_producao'] else {}
                st.markdown(f"""
                <div class='row-monitor'>
                    <div style='flex: 1;'><b>OS: {o['numero_pedido']}</b><br>{o['projetos']['nome_projeto'] if o['projetos'] else ''}</div>
                    <div style='flex: 2; display: flex; justify-content: space-around;'>
                        <div>Corte <div class='dot {'bg-success' if lp.get('corte_fim') else 'bg-danger'}'></div></div>
                        <div>Solda <div class='dot {'bg-success' if lp.get('solda_fim') else 'bg-danger'}'></div></div>
                        <div>Pintura <div class='dot {'bg-success' if lp.get('pintura_fim') else 'bg-danger'}'></div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 5. RELATÓRIOS (PRODUTIVIDADE RESTAURADO)
    elif p == "rel":
        st.title("Relatórios de Produtividade")
        res_rel = supabase.table("linha_producao").select("*, pedidos(numero_pedido)").execute()
        if res_rel.data:
            dados = [{"OS": r['pedidos']['numero_pedido'], 
                      "Corte (h)": calcular_horas(r.get('corte_inicio'), r.get('corte_fim')),
                      "Solda (h)": calcular_horas(r.get('solda_inicio'), r.get('solda_fim'))} for r in res_rel.data if r['pedidos']]
            df_rel = pd.DataFrame(dados)
            st.bar_chart(df_rel.set_index("OS"))

    # 6. CHÃO DE FÁBRICA E RESTANTE DO CÓDIGO (FISCALIZAÇÃO, WORKFLOW, COMERCIAL)
    elif p == "fab":
        st.title("Produção | Chão de Fábrica")
        atv = supabase.table("pedidos").select("*, linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        if atv.data:
            sel = st.selectbox("Selecione a OS:", [x['numero_pedido'] for x in atv.data])
            item = next(x for x in atv.data if x['numero_pedido'] == sel)
            prod = item['linha_producao'][0]
            if item['arquivo_url']: st.link_button("📂 DESENHO TÉCNICO", item['arquivo_url'])

            def render_etapa(label, campo, hab):
                if hab:
                    with st.expander(f"ETAPA: {label.upper()}", expanded=True):
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
                                st.rerun()
                        else: st.success(f"Finalizado em {calcular_horas(i, f)}h")

            render_etapa("Corte", "corte", item['has_corte_laser'])
            render_etapa("Dobra", "dobra", item['has_dobra_cnc'])
            render_etapa("Solda", "solda", item['has_solda'])
            render_etapa("Pintura", "pintura", item['has_pintura'])

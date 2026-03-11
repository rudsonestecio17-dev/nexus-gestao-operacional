import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import time

# 1. CONFIGURAÇÕES TÉCNICAS E PERFORMANCE
st.set_page_config(
    page_title="CTRL | Gestão de Produção", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Conexão Supabase
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. DESIGN EMPRESARIAL CTRL (CSS OTIMIZADO)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    /* Global e Performance (Evita flashes brancos) */
    .stApp { background-color: #FFFFFF; color: #1e293b; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Identidade CTRL (Violeta/Lavanda) */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important; 
        border-right: 1px solid #e2e8f0; 
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Submenus (Correção do erro visual branco) */
    .stSidebar .stExpander { 
        background-color: rgba(255, 255, 255, 0.05) !important; 
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        border-radius: 8px !important;
        margin-bottom: 10px !important;
    }
    
    /* Botões de Navegação (Feedback Visual) */
    .stSidebar button {
        background-color: transparent !important; border: none !important; color: #FFFFFF !important;
        text-align: left !important; width: 100% !important; padding: 12px 15px !important;
        font-size: 11px !important; text-transform: uppercase !important; font-weight: 600 !important;
        transition: 0.3s;
    }
    .stSidebar button:hover { background-color: #4f46e5 !important; border-radius: 5px; }

    /* Cards Estilo Enterprise */
    .row-monitor { 
        background: #f8fafc; border-radius: 12px; padding: 25px; margin-bottom: 15px; 
        border: 1px solid #e2e8f0; border-left: 8px solid #6366f1; 
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    .dot { height: 20px; width: 20px; border-radius: 50%; display: inline-block; margin: 4px auto; border: 3px solid #FFF; }
    .bg-success { background-color: #10b981; }
    .bg-danger { background-color: #ef4444; }
    
    /* Botões de Ação Chão de Fábrica */
    .stButton>button { border-radius: 6px; font-weight: 700; height: 45px; transition: 0.2s; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES CORE ---
def registrar_log(acao, detalhe):
    usuario = st.session_state.get('user_name', 'Sistema')
    try: supabase.table("logs_sistema").insert({"usuario": usuario, "acao": acao, "detalhe": detalhe}).execute()
    except: pass

def calcular_produtividade(inicio, fim):
    if inicio and fim:
        try:
            fmt = "%Y-%m-%dT%H:%M:%S"
            diff = datetime.strptime(fim[:19], fmt) - datetime.strptime(inicio[:19], fmt)
            horas = diff.total_seconds() / 3600
            return round(horas, 2)
        except: return 0
    return 0

def get_proxima_os():
    try:
        res = supabase.table("pedidos").select("numero_pedido").order("id", desc=True).limit(1).execute()
        return str(int(res.data[0]['numero_pedido']) + 1) if res.data else "1001"
    except: return "1001"

# --- LÓGICA DE LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<div style='text-align: center; padding-top: 100px;'><h1 style='color: #1e1b4b; font-size: 4em;'>CTRL</h1><p>GESTÃO DE PRODUÇÃO</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        with st.form("login_form"):
            u, s = st.text_input("Usuário"), st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR TERMINAL"):
                res = supabase.table("usuarios").select("*").eq("login", u).eq("senha", s).execute()
                if res.data:
                    st.session_state.update({"autenticado": True, "perfil": res.data[0]['perfil'], "user_name": res.data[0]['login']})
                    st.rerun()
                else: st.error("Acesso negado.")
else:
    # --- SIDEBAR ESTRUTURADA (Fiel à Imagem enviada) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>CTRL</h2>", unsafe_allow_html=True)
        st.caption(f"<p style='text-align:center;'>Operador: {st.session_state.user_name.upper()}</p>", unsafe_allow_html=True)
        st.divider()

        if 'pg' not in st.session_state: st.session_state.pg = "dash"

        if st.session_state.perfil == "admin":
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

    # 1. COMERCIAL (FLUXO PV/PO)
    if p == "com":
        st.title("Projetos | Comercial")
        with st.expander("Lançar Orçamento", expanded=True):
            p_db = supabase.table("projetos").select("id, nome_projeto").execute()
            l_p = {x['nome_projeto']: x['id'] for x in p_db.data}
            with st.form("f_com"):
                no, po = st.text_input("Nº OS", value=get_proxima_os()), st.selectbox("Projeto", list(l_p.keys()))
                vo, de = st.number_input("Valor"), st.date_input("Prazo")
                if st.form_submit_button("REGISTRAR"):
                    r = supabase.table("pedidos").insert({"numero_pedido": no, "id_projeto": l_p[po], "valor_orcamento": vo, "prazo_entrega": str(de), "status_geral": "EXECUTANDO ORÇAMENTO"}).execute()
                    if r.data:
                        supabase.table("linha_producao").insert({"id_pedido": r.data[0]['id']}).execute()
                        st.success("Salvo!"); st.rerun()

        st.divider()
        st.subheader("Aprovações e Gatilhos PV/PO")
        p_pend = supabase.table("pedidos").select("*").neq("status_geral", "CONCLUÍDO").execute()
        for i in p_pend.data:
            with st.expander(f"OS: {i['numero_pedido']} | {i['status_geral']}"):
                c1, c2 = st.columns(2)
                pv = c1.text_input("Nº Pedido Venda (PV)", value=i.get('num_pv', ''), key=f"pv_{i['id']}")
                po = c2.text_input("Nº Ordem Compra (PO)", value=i.get('num_po', ''), key=f"po_{i['id']}")
                if st.button("ATUALIZAR E ENVIAR PARA WORKFLOW", key=f"up_{i['id']}"):
                    ns = "ORÇAMENTO APROVADO" if pv and not po else ("EM PRODUÇÃO" if po else i['status_geral'])
                    supabase.table("pedidos").update({"num_pv": pv, "num_po": po, "status_geral": ns}).eq("id", i['id']).execute()
                    st.rerun()

    # 2. WORKFLOW (UPLOAD DE ARQUIVO)
    elif p == "work":
        st.title("Projetos | Workflow e Engenharia")
        p_wf = supabase.table("pedidos").select("*").eq("status_geral", "EM PRODUÇÃO").execute()
        if p_wf.data:
            sel = st.selectbox("Selecione a OS para configurar", [x['numero_pedido'] for x in p_wf.data])
            id_w = next(x['id'] for x in p_wf.data if x['numero_pedido'] == sel)
            with st.form("f_wf"):
                arq = st.file_uploader("Subir Desenho Técnico (PDF/DWG/IMG)", type=['pdf','jpg','png','zip'])
                st.write("Selecione as etapas necessárias:")
                e1, e2 = st.columns(2)
                h1, h2, h3, h4 = e1.checkbox("Corte"), e1.checkbox("Dobra"), e1.checkbox("Solda"), e1.checkbox("Metaleira")
                h5, h6, h7 = e2.checkbox("Calandragem"), e2.checkbox("Galvanização"), e2.checkbox("Pintura")
                if st.form_submit_button("CONFIGURAR ROTEIRO"):
                    url = ""
                    if arq:
                        path = f"pedidos/{sel}/{arq.name}"
                        supabase.storage.from_("desenhos").upload(path, arq.getvalue(), {"upsert": "true"})
                        url = supabase.storage.from_("desenhos").get_public_url(path)
                    supabase.table("pedidos").update({
                        "arquivo_url": url, "has_corte_laser": h1, "has_dobra_cnc": h2, "has_solda": h3, 
                        "has_metaleira": h4, "has_calandragem": h5, "has_galvanizacao": h6, "has_pintura": h7
                    }).eq("id", id_w).execute()
                    st.success("Workflow definido com sucesso!")

    # 3. CHÃO DE FÁBRICA (TEMPO REAL E PRODUTIVIDADE)
    elif p == "fab":
        st.title("Produção | Chão de Fábrica")
        atv = supabase.table("pedidos").select("*, linha_producao(*)").eq("status_geral", "EM PRODUÇÃO").execute()
        if atv.data:
            sel = st.selectbox("OS em execução:", [x['numero_pedido'] for x in atv.data])
            item = next(x for x in atv.data if x['numero_pedido'] == sel)
            prod = item['linha_producao'][0]
            if item['arquivo_url']: st.link_button("📂 ABRIR DESENHO TÉCNICO", item['arquivo_url'], use_container_width=True)

            def render_etapa(label, campo, hab):
                if hab:
                    with st.expander(f"ETAPA: {label.upper()}", expanded=True):
                        c1, c2, c3 = st.columns([1, 1, 2])
                        i, f = prod.get(f"{campo}_inicio"), prod.get(f"{campo}_fim")
                        if not i:
                            if c1.button("INICIAR", key=f"i_{campo}"):
                                supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", item['id']).execute()
                                registrar_log("PRODUÇÃO", f"Iniciou {label} na OS {sel}")
                                st.rerun()
                        elif not f:
                            c1.info(f"Início: {i[11:16]}")
                            obs = c3.text_input("Notas", key=f"o_{campo}")
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
                        else: 
                            tempo = calcular_produtividade(i, f)
                            st.success(f"CONCLUÍDO | Duração: {tempo}h | {i[11:16]} - {f[11:16]}")

            render_etapa("Corte", "corte", item['has_corte_laser'])
            render_etapa("Dobra", "dobra", item['has_dobra_cnc'])
            render_etapa("Solda", "solda", item['has_solda'])
            render_etapa("Metaleira", "metaleira", item['has_metaleira'])
            render_etapa("Calandragem", "calandragem", item['has_calandragem'])
            render_etapa("Galvanização", "galvanizacao", item['has_galvanizacao'])
            render_etapa("Pintura", "pintura", item['has_pintura'])

    # 4. RELATÓRIOS (MÉTRICAS DE TEMPO)
    elif p == "rel":
        st.title("Relatórios de Produtividade")
        res_rel = supabase.table("linha_producao").select("*, pedidos(numero_pedido)").execute()
        if res_rel.data:
            dados = []
            for r in res_rel.data:
                if r['pedidos']:
                    dados.append({
                        "OS": r['pedidos']['numero_pedido'],
                        "Corte (h)": calcular_produtividade(r.get('corte_inicio'), r.get('corte_fim')),
                        "Solda (h)": calcular_horas(r.get('solda_inicio'), r.get('solda_fim')),
                        "Pintura (h)": calcular_horas(r.get('pintura_inicio'), r.get('pintura_fim'))
                    })
            df_rel = pd.DataFrame(dados)
            st.bar_chart(df_rel.set_index("OS"))
            st.dataframe(df_rel, use_container_width=True)

    # 5. CADASTROS (DADOS MESTRES COMPLETOS)
    elif p == "cad":
        st.title("Cadastros de Base")
        c1, c2 = st.columns(2)
        with c1:
            with st.expander("Cadastrar Solicitante", expanded=True):
                with st.form("f_sol"):
                    n, e, t, o = st.text_input("Responsável"), st.text_input("Empresa"), st.text_input("Telefone"), st.text_area("Endereço/Notas")
                    if st.form_submit_button("SALVAR CLIENTE"):
                        supabase.table("solicitantes").insert({"nome": n, "empresa": e, "telefone": t, "info_adicional": o}).execute()
                        st.success("Salvo!")
        with c2:
            with st.expander("Cadastrar Projeto", expanded=True):
                s_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
                l_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in s_db.data}
                with st.form("f_proj"):
                    np, sid, cid = st.text_input("Título"), st.selectbox("Cliente", list(l_s.keys())), st.text_input("Cidade")
                    end, num, cep = st.text_input("Rua"), st.text_input("Nº"), st.text_input("CEP")
                    if st.form_submit_button("VINCULAR PROJETO"):
                        supabase.table("projetos").insert({"nome_projeto": np, "id_solicitante": l_s[sid], "cidade": cid, "endereco": end, "numero": num, "cep": cep}).execute()
                        st.success("Vinculado!")

import streamlit as st
import pandas as pd
from supabase import create_client

# 1. CONFIGURAÇÕES INICIAIS E DESIGN
st.set_page_config(page_title="NEXUS OPERACIONAL", layout="wide")

# Injeção de CSS para um visual empresarial
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Estilização da Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        color: white;
    }
    
    /* Botões Padrão */
    div.stButton > button {
        border-radius: 8px;
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #1d4ed8;
        border-color: #1d4ed8;
    }

    /* Cards do Dashboard */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO B BANCO
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. NAVEGAÇÃO LATERAL
st.sidebar.title("🛠️ NEXUS CELL")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "MENU PRINCIPAL",
    ["📊 Dashboard de Gestão", "📝 Gerar Pedidos", "🏭 Chão de Fábrica", "👥 Cadastros Base"]
)
st.sidebar.markdown("---")
st.sidebar.info("Logado como: Operacional")

# --- MÓDULO: CADASTROS BASE ---
if menu == "👥 Cadastros Base":
    st.title("👥 Gestão de Cadastros")
    
    aba_sol, aba_proj = st.tabs(["👤 Solicitantes", "📍 Projetos/Endereços"])
    
    with aba_sol:
        with st.form("form_sol"):
            nome = st.text_input("Nome do Solicitante")
            empresa = st.text_input("Empresa")
            tel = st.text_input("WhatsApp")
            email = st.text_input("Email")
            if st.form_submit_button("CADASTRAR SOLICITANTE"):
                dados = {"nome": nome, "empresa": empresa, "telefone": tel, "email": email, "status": "Ativo"}
                supabase.table("solicitantes").insert(dados).execute()
                st.success("Cadastrado!")

    with aba_proj:
        sols = supabase.table("solicitantes").select("id, nome, empresa").execute()
        lista_s = {f"{s['nome']} ({s['empresa']})": s['id'] for s in sols.data}
        with st.form("form_proj"):
            nome_p = st.text_input("Nome do Projeto")
            escolha = st.selectbox("Vincular a", options=list(lista_s.keys()))
            c1, c2 = st.columns(2)
            end = c1.text_input("Endereço")
            cid = c2.text_input("Cidade")
            if st.form_submit_button("VINCULAR PROJETO"):
                d_p = {"nome_projeto": nome_p, "id_solicitante": lista_s[escolha], "endereco": end, "cidade": cid}
                supabase.table("projetos").insert(d_p).execute()
                st.success("Projeto Vinculado!")

# --- MÓDULO: GERAR PEDIDOS ---
elif menu == "📝 Gerar Pedidos":
    st.title("📝 Nova Ordem de Produção")
    projs = supabase.table("projetos").select("id, nome_projeto").execute()
    lista_p = {p['nome_projeto']: p['id'] for p in projs.data}
    
    with st.form("form_ped"):
        c1, c2 = st.columns(2)
        num = c1.text_input("Nº do Pedido")
        proj = c1.selectbox("Projeto", options=list(lista_p.keys()))
        prazo = c2.date_input("Prazo")
        desc = c2.text_area("Descrição")
        
        st.write("🔧 Etapas Necessárias")
        e1, e2, e3 = st.columns(3)
        l_c = e1.checkbox("Corte a Laser")
        l_d = e1.checkbox("Dobra CNC")
        l_s = e2.checkbox("Solda")
        l_m = e2.checkbox("Metaleira")
        l_ca = e3.checkbox("Calandragem")
        l_g = e3.checkbox("Galvanização")
        l_p = e3.checkbox("Pintura")
        
        if st.form_submit_button("LANÇAR PRODUÇÃO"):
            d_ped = {
                "numero_pedido": num, "id_projeto": lista_p[proj], "prazo_entrega": str(prazo),
                "has_corte_laser": l_c, "has_dobra_cnc": l_d, "has_solda": l_s,
                "has_metaleira": l_m, "has_calandragem": l_ca, "has_galvanizacao": l_g, "has_pintura": l_p
            }
            res = supabase.table("pedidos").insert(d_ped).execute()
            supabase.table("linha_producao").insert({"id_pedido": res.data[0]['id']}).execute()
            st.success("Pedido enviado para a fábrica!")

# --- MÓDULO: CHÃO DE FÁBRICA ---
elif menu == "🛠️ Chão de Fábrica":
    st.title("🏭 Controle de Produção")
    ativos = supabase.table("pedidos").select("id, numero_pedido").eq("status_geral", "Em Produção").execute()
    lista_a = {p['numero_pedido']: p['id'] for p in ativos.data}
    
    if lista_a:
        p_sel = st.selectbox("Selecione o Pedido em Mãos", options=list(lista_a.keys()))
        id_f = lista_a[p_sel]
        det = supabase.table("pedidos").select("*").eq("id", id_f).single().execute().data
        prod = supabase.table("linha_producao").select("*").eq("id_pedido", id_f).single().execute().data

        def render_etapa(label, campo, habilitado):
            if habilitado:
                st.markdown(f"### {label}")
                c_i, c_f = st.columns(2)
                ini = prod.get(f"{campo}_inicio")
                fim = prod.get(f"{campo}_fim")
                
                if not ini:
                    if c_i.button(f"Iniciar {label}", key=f"i_{campo}"):
                        supabase.table("linha_producao").update({f"{campo}_inicio": "now()"}).eq("id_pedido", id_f).execute()
                        st.rerun()
                elif ini and not fim:
                    c_i.warning(f"Em andamento desde: {ini[11:16]}")
                    if c_f.button(f"Concluir {label}", key=f"f_{campo}"):
                        supabase.table("linha_producao").update({f"{campo}_fim": "now()"}).eq("id_pedido", id_f).execute()
                        st.rerun()
                else:
                    st.success(f"Finalizado às {fim[11:16]}")

        render_etapa("Corte a Laser", "corte", det['has_corte_laser'])
        render_etapa("Solda", "solda", det['has_solda'])
        render_etapa("Pintura", "pintura", det['has_pintura'])
    else:
        st.info("Nenhum pedido na fila.")

# --- MÓDULO: DASHBOARD ---
elif menu == "📊 Dashboard de Gestão":
    st.title("📊 Visão Geral da Fábrica")
    res = supabase.table("pedidos").select("*, projetos(nome_projeto), linha_producao(*)").execute()
    
    if res.data:
        df_l = []
        for i in res.data:
            lp = i['linha_producao'][0] if i['linha_producao'] else {}
            df_l.append({
                "Pedido": i['numero_pedido'],
                "Projeto": i['projetos']['nome_projeto'],
                "Prazo": i['prazo_entrega'],
                "Corte": "✅" if lp.get('corte_fim') else ("⏳" if lp.get('corte_inicio') else "-"),
                "Solda": "✅" if lp.get('solda_fim') else ("⏳" if lp.get('solda_inicio') else "-"),
                "Pintura": "✅" if lp.get('pintura_fim') else ("⏳" if lp.get('pintura_inicio') else "-")
            })
        st.table(pd.DataFrame(df_l))



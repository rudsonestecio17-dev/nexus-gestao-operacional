import streamlit as st
from supabase import create_client

# Configurações do Supabase (Substitua pelos seus dados)
SUPABASE_URL = "https://olwwfoiiiyfhpakyftxt.supabase.co"
SUPABASE_KEY = "sb_publishable_llZ8M4D7zp8Dk1XBVXfBlg_SXTTzFa7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="NEXUS - Cadastro", layout="centered")

st.title("🏗️ Cadastro de Solicitantes e Projetos")

# --- ABA 1: CADASTRO DE SOLICITANTE ---
with st.expander("👤 Novo Solicitante", expanded=True):
    with st.form("form_solicitante"):
        nome = st.text_input("Nome do Solicitante")
        empresa = st.text_input("Empresa")
        tel = st.text_input("Telemóvel/WhatsApp")
        email = st.text_input("Email")
        info = st.text_area("Informações Adicionais")
        
        btn_solicitante = st.form_submit_button("Guardar Solicitante")
        
        if btn_solicitante:
            dados = {
                "nome": nome,
                "empresa": empresa,
                "telefone": tel,
                "email": email,
                "info_adicional": info,
                "status": "Ativo"
            }
            res = supabase.table("solicitantes").insert(dados).execute()
            st.success(f"Solicitante {nome} cadastrado com sucesso!")

# --- ABA 2: TIPO DE PROJETO (ENDEREÇO) ---
st.divider()
with st.expander("📍 Novo Projeto / Endereço"):
    # Procurar solicitantes já cadastrados para vincular
    solicitantes_db = supabase.table("solicitantes").select("id, nome, empresa").execute()
    lista_solicitantes = {f"{s['nome']} ({s['empresa']})": s['id'] for s in solicitantes_db.data}
    
    with st.form("form_projeto"):
        nome_proj = st.text_input("Nome do Projeto (Ex: Obra Centro)")
        escolha_sol = st.selectbox("Vincular a Solicitante/Empresa", options=list(lista_solicitantes.keys()))
        end = st.text_input("Endereço")
        cidade = st.text_input("Cidade")
        num = st.text_input("Número")
        cep = st.text_input("CEP")
        
        btn_projeto = st.form_submit_button("Guardar Projeto")
        
        if btn_projeto:
            id_sol = lista_solicitantes[escolha_sol]
            dados_proj = {
                "nome_projeto": nome_proj,
                "id_solicitante": id_sol,
                "endereco": end,
                "cidade": cidade,
                "numero": num,
                "cep": cep
            }
            supabase.table("projects").insert(dados_proj).execute()
            st.success(f"Projeto '{nome_proj}' vinculado com sucesso!")
st.divider()
st.header("📋 Cadastro de Novo Pedido")

# 1. BUSCAR PROJETOS PARA VINCULAR
projetos_db = supabase.table("projetos").select("id, nome_projeto").execute()
lista_projs = {p['nome_projeto']: p['id'] for p in projetos_db.data}

with st.form("form_pedido"):
    col1, col2 = st.columns(2)
    
    with col1:
        num_pedido = st.text_input("Número do Pedido (Ex: PED-2024-001)")
        proj_selecionado = st.selectbox("Selecione o Projeto", options=list(lista_projs.keys()))
        prazo = st.date_input("Prazo de Entrega")
        
    with col2:
        desc = st.text_area("Descrição do Pedido")
        arquivo = st.file_uploader("Subir Desenho Técnico (PDF/DWG)", type=['pdf', 'dwg', 'png', 'jpg'])

    st.subheader("🛠️ Selecione as Etapas de Produção")
    c1, c2, c3 = st.columns(3)
    etapa_corte = c1.checkbox("Corte a Laser")
    etapa_dobra = c1.checkbox("Dobra CNC")
    etapa_solda = c2.checkbox("Solda")
    etapa_metaleira = c2.checkbox("Metaleira")
    etapa_calandra = c3.checkbox("Calandragem")
    etapa_galva = c3.checkbox("Galvanização")
    etapa_pintura = c3.checkbox("Pintura")

    btn_pedido = st.form_submit_button("GERAR ORDEM DE PRODUÇÃO")

    if btn_pedido:
        # Salva o Pedido
        dados_pedido = {
            "numero_pedido": num_pedido,
            "id_projeto": lista_projs[proj_selecionado],
            "descricao_pedido": desc,
            "prazo_entrega": str(prazo),
            "has_corte_laser": etapa_corte,
            "has_dobra_cnc": etapa_dobra,
            "has_solda": etapa_solda,
            "has_metaleira": etapa_metaleira,
            "has_calandragem": etapa_calandra,
            "has_galvanizacao": etapa_galva,
            "has_pintura": etapa_pintura
        }
        
        # Insere no Banco e cria a Linha de Produção vinculada
        res_pedido = supabase.table("pedidos").insert(dados_pedido).execute()
        id_novo_pedido = res_pedido.data[0]['id']
        
        supabase.table("linha_producao").insert({"id_pedido": id_novo_pedido}).execute()
        
        st.success(f"✅ Pedido {num_pedido} enviado para a Linha de Produção!")

st.divider()
st.header("🏭 Painel de Execução - Chão de Fábrica")

# 1. Selecionar Pedido Ativo
pedidos_ativos = supabase.table("pedidos").select("id, numero_pedido").eq("status_geral", "Em Produção").execute()
lista_pedidos_ativos = {p['numero_pedido']: p['id'] for p in pedidos_ativos.data}

if lista_pedidos_ativos:
    pedido_foco = st.selectbox("Selecione o Pedido para Trabalhar", options=list(lista_pedidos_ativos.keys()))
    id_foco = lista_pedidos_ativos[pedido_foco]

    # Buscar dados do pedido e da linha de produção
    detalhes = supabase.table("pedidos").select("*").eq("id", id_foco).single().execute().data
    producao = supabase.table("linha_producao").select("*").eq("id_pedido", id_foco).single().execute().data

    # Função para criar os botões de Check
    def gerenciar_etapa(nome_label, campo_db, habilitado):
        if habilitado:
            st.subheader(f"🛠️ {nome_label}")
            col_ini, col_fim, col_obs = st.columns([1, 1, 2])
            
            # Status atual
            inicio = producao.get(f"{campo_db}_inicio")
            fim = producao.get(f"{campo_db}_fim")

            if not inicio:
                if col_ini.button(f"Iniciar {nome_label}", key=f"ini_{campo_db}"):
                    supabase.table("linha_producao").update({f"{campo_db}_inicio": "now()"}).eq("id_pedido", id_foco).execute()
                    st.rerun()
            elif inicio and not fim:
                col_ini.info(f"Iniciado em: {inicio[11:16]}")
                if col_fim.button(f"Finalizar {nome_label}", key=f"fim_{campo_db}"):
                    obs = st.session_state.get(f"obs_{campo_db}", "")
                    supabase.table("linha_producao").update({f"{campo_db}_fim": "now()", f"{campo_db}_obs": obs}).eq("id_pedido", id_foco).execute()
                    st.rerun()
                st.text_input("Observação técnica:", key=f"obs_{campo_db}")
            else:
                st.success(f"✅ {nome_label} Concluído às {fim[11:16]}")

    # Exibir apenas as etapas marcadas no cadastro do pedido
    gerenciar_etapa("Corte a Laser", "corte", detalhes['has_corte_laser'])
    gerenciar_etapa("Dobra CNC", "dobra", detalhes['has_dobra_cnc'])
    gerenciar_etapa("Solda", "solda", detalhes['has_solda'])
    gerenciar_etapa("Metaleira", "metaleira", detalhes['has_metaleira'])
    gerenciar_etapa("Calandragem", "calandragem", detalhes['has_calandragem'])
    gerenciar_etapa("Galvanização", "galvanizacao", detalhes['has_galvanizacao'])
    gerenciar_etapa("Pintura", "pintura", detalhes['has_pintura'])

else:
    st.info("Nenhum pedido em produção no momento.")
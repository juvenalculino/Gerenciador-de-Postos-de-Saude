import streamlit as st
#from database import create_tables # Presumo que create_tables está em database.py
from open_crud import (
    create_hospital, get_all_hospitals, get_hospital_by_id, update_hospital, delete_hospital,
    create_posto_saude, get_all_postos_saude, get_posto_saude_by_id, update_posto_saude, delete_posto_saude,
    create_funcionario, get_all_funcionarios, get_funcionario_by_id, update_funcionario, delete_funcionario, check_password, get_funcionario_by_email,
    create_paciente, get_all_pacientes, get_paciente_by_id, update_paciente, delete_paciente,
    create_medicamento, get_all_medicamentos, get_medicamento_by_id, update_medicamento, delete_medicamento,
    create_estoque_medicamento_posto, get_all_estoque_medicamento_posto, get_estoque_medicamento_posto_by_id, update_estoque_medicamento_posto, delete_estoque_medicamento_posto,
    create_atendimento, get_all_atendimentos, get_atendimento_by_id, update_atendimento, delete_atendimento,
    create_prescricao, get_all_prescricoes, get_prescricao_by_id, update_prescricao, delete_prescricao,
    create_distribuicao_medicamento, get_all_distribuicoes_medicamento, get_distribuicao_medicamento_by_id,
    get_atendimentos_by_type, get_atendimentos_by_posto, get_pacientes_by_genero, get_pacientes_by_idade_group,
    get_top_distribui_medicamentos, get_top_diagnosticos
)
from datetime import datetime, date
import pandas as pd
import matplotlib.pyplot as plt

# --- Configurações Iniciais --- #
st.set_page_config(layout="wide", page_title="Sistema de Gerenciamento de Posto de Saúde")

# Garante que as tabelas do banco de dados sejam criadas ao iniciar o app
# create_tables() # Esta chamada provavelmente deve estar em um script de inicialização do banco de dados,
                # ou você pode mantê-la aqui, mas cuidado para não recriar tabelas a cada execução
                # se elas já existirem e você não quiser perder dados.
                # Se for para usar com o script generate_data.py, execute generate_data.py uma vez.


# Inicializa o estado da sessão para login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# --- Funções Auxiliares para Exibição de Mensagens --- #
def show_success(message):
    st.success(message)

def show_error(message):
    st.error(message)

def show_info(message):
    st.info(message)

# --- Página de Login --- #
def login_page():
    st.title("Login no Sistema de Gerenciamento")

    email = st.text_input("E-mail do Funcionário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if email and password:
            user_data = get_funcionario_by_email(email)
            if user_data["success"] and user_data["data"]:
                user = user_data["data"]
                if check_password(password, user["senha_hash"]):
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    show_success(f"Bem-vindo, {user["nome_funcionario"]}!")
                    st.rerun() # Usar st.rerun()
                else:
                    show_error("Senha incorreta.")
            else:
                show_error("E-mail não encontrado.")
        else:
            show_error("Por favor, insira seu e-mail e senha.")
    st.write("Juvenal Culino")

# --- Seção de Gerenciamento de Hospitais --- #
def hospital_management_section():
    st.header("Gerenciamento de Hospitais")

    tab1, tab2 = st.tabs(["Cadastrar Novo Hospital", "Visualizar / Editar / Excluir Hospitais"])

    with tab1:
        st.subheader("Cadastrar Novo Hospital")
        with st.form("form_create_hospital", clear_on_submit=True):
            nome = st.text_input("Nome do Hospital *", key="h_nome_c")
            cnpj = st.text_input("CNPJ", key="h_cnpj_c")
            endereco = st.text_area("Endereço", key="h_endereco_c")
            telefone = st.text_input("Telefone", key="h_telefone_c")
            email = st.text_input("E-mail", key="h_email_c")

            submitted = st.form_submit_button("Cadastrar Hospital")
            if submitted:
                result = create_hospital(nome, cnpj, endereco, telefone, email)
                if result["success"]:
                    show_success(result["message"])
                else:
                    show_error(result["message"])

    with tab2:
        st.subheader("Hospitais Cadastrados")
        
        search_term_hospital = st.text_input("Buscar Hospital por Nome ou CNPJ", key="search_hospital")
        
        hospitais_data = get_all_hospitals(search_term=search_term_hospital)
        if hospitais_data["success"] and hospitais_data["data"]:
            df_hospitais = st.dataframe(hospitais_data["data"], use_container_width=True, hide_index=True)

            st.subheader("Editar / Excluir Hospital")
            hospital_ids = {h["nome_hospital"]: h["id_hospital"] for h in hospitais_data["data"]}
            selected_hospital_name = st.selectbox("Selecione um Hospital para Editar/Excluir", list(hospital_ids.keys()), key="h_select_u_d")

            if selected_hospital_name:
                selected_hospital_id = hospital_ids[selected_hospital_name]
                hospital_info = get_hospital_by_id(selected_hospital_id)["data"]

                with st.form("form_update_hospital", clear_on_submit=False):
                    st.write(f"Editando Hospital: **{hospital_info["nome_hospital"]}** (ID: {hospital_info["id_hospital"]})")
                    upd_nome = st.text_input("Nome do Hospital *", value=hospital_info["nome_hospital"], key="h_nome_u")
                    upd_cnpj = st.text_input("CNPJ", value=hospital_info["cnpj_hospital"], key="h_cnpj_u")
                    upd_endereco = st.text_area("Endereço", value=hospital_info["endereco_hospital"], key="h_endereco_u")
                    upd_telefone = st.text_input("Telefone", value=hospital_info["telefone_hospital"], key="h_telefone_u")
                    upd_email = st.text_input("E-mail", value=hospital_info["email_hospital"], key="h_email_u")

                    col_upd, col_del = st.columns(2)
                    with col_upd:
                        update_submitted = st.form_submit_button("Atualizar Hospital")
                        if update_submitted:
                            result = update_hospital(selected_hospital_id, upd_nome, upd_cnpj, upd_endereco, upd_telefone, upd_email)
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
                    with col_del:
                        delete_submitted = st.form_submit_button("Excluir Hospital", help="Cuidado! A exclusão é irreversível e só é possível se não houver postos de saúde vinculados.")
                        if delete_submitted:
                            result = delete_hospital(selected_hospital_id)
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
            else:
                show_info("Nenhum hospital cadastrado para exibir ou editar.")
        else:
            show_info("Nenhum hospital cadastrado ainda.")

# --- Seção de Gerenciamento de Postos de Saúde --- #
def posto_saude_management_section():
    st.header("Gerenciamento de Postos de Saúde")

    tab1, tab2 = st.tabs(["Cadastrar Novo Posto", "Visualizar / Editar / Excluir Postos"])

    with tab1:
        st.subheader("Cadastrar Novo Posto de Saúde")
        hospitais_disponiveis = get_all_hospitals()
        if hospitais_disponiveis["success"] and hospitais_disponiveis["data"]:
            hospital_options = {h["nome_hospital"]: h["id_hospital"] for h in hospitais_disponiveis["data"]}
            selected_hospital_name = st.selectbox("Vincular ao Hospital *", list(hospital_options.keys()), key="ps_hospital_c")
            id_hospital_vinculado = hospital_options[selected_hospital_name] if selected_hospital_name else None

            with st.form("form_create_posto_saude", clear_on_submit=True):
                nome = st.text_input("Nome do Posto *", key="ps_nome_c")
                endereco = st.text_area("Endereço *", key="ps_endereco_c")
                telefone = st.text_input("Telefone", key="ps_telefone_c")
                email = st.text_input("E-mail", key="ps_email_c")

                submitted = st.form_submit_button("Cadastrar Posto de Saúde")
                if submitted:
                    if id_hospital_vinculado:
                        result = create_posto_saude(nome, endereco, id_hospital_vinculado, telefone, email)
                        if result["success"]:
                            show_success(result["message"])
                        else:
                            show_error(result["message"])
                    else:
                        show_error("Por favor, selecione um hospital para vincular o posto.")
        else:
            show_info("Nenhum hospital cadastrado. Cadastre um hospital primeiro para vincular um posto de saúde.")

    with tab2:
        st.subheader("Postos de Saúde Cadastrados")
        
        col1, col2 = st.columns(2)
        with col1:
            search_term_posto = st.text_input("Buscar Posto por Nome ou Endereço", key="search_posto")
        with col2:
            hospitais_disponiveis_filter = get_all_hospitals()
            hospital_filter_options = {"Todos os Hospitais": None}
            if hospitais_disponiveis_filter["success"] and hospitais_disponiveis_filter["data"]:
                hospital_filter_options.update({h["nome_hospital"]: h["id_hospital"] for h in hospitais_disponiveis_filter["data"]})
            selected_hospital_filter = st.selectbox("Filtrar por Hospital", list(hospital_filter_options.keys()), key="filter_posto_hospital")
            id_hospital_filter = hospital_filter_options[selected_hospital_filter]

        postos_data = get_all_postos_saude(search_term=search_term_posto, id_hospital_vinculado=id_hospital_filter)
        if postos_data["success"] and postos_data["data"]:
            df_postos = st.dataframe(postos_data["data"], use_container_width=True, hide_index=True)

            st.subheader("Editar / Excluir Posto de Saúde")
            posto_ids = {ps["nome_posto"]: ps["id_posto"] for ps in postos_data["data"]}
            selected_posto_name = st.selectbox("Selecione um Posto para Editar/Excluir", list(posto_ids.keys()), key="ps_select_u_d")

            if selected_posto_name:
                selected_posto_id = posto_ids[selected_posto_name]
                posto_info = get_posto_saude_by_id(selected_posto_id)["data"]

                with st.form("form_update_posto_saude", clear_on_submit=False):
                    st.write(f"Editando Posto: **{posto_info["nome_posto"]}** (ID: {posto_info["id_posto"]})")
                    upd_nome = st.text_input("Nome do Posto *", value=posto_info["nome_posto"], key="ps_nome_u")
                    upd_endereco = st.text_area("Endereço *", value=posto_info["endereco_posto"], key="ps_endereco_u")
                    upd_telefone = st.text_input("Telefone", value=posto_info["telefone_posto"], key="ps_telefone_u")
                    upd_email = st.text_input("E-mail", value=posto_info["email_posto"], key="ps_email_u")

                    hospitais_disponiveis_upd = get_all_hospitals()
                    hospital_options_upd = {h["nome_hospital"]: h["id_hospital"] for h in hospitais_disponiveis_upd["data"]}
                    current_hospital_name = posto_info["nome_hospital"]
                    current_hospital_index = list(hospital_options_upd.keys()).index(current_hospital_name) if current_hospital_name in hospital_options_upd else 0

                    selected_hospital_name_upd = st.selectbox("Vincular ao Hospital *", list(hospital_options_upd.keys()), index=current_hospital_index, key="ps_hospital_u")
                    upd_id_hospital_vinculado = hospital_options_upd[selected_hospital_name_upd] if selected_hospital_name_upd else None

                    col_upd, col_del = st.columns(2)
                    with col_upd:
                        update_submitted = st.form_submit_button("Atualizar Posto de Saúde")
                        if update_submitted:
                            if upd_id_hospital_vinculado:
                                result = update_posto_saude(selected_posto_id, upd_nome, upd_endereco, upd_id_hospital_vinculado, upd_telefone, upd_email)
                                if result["success"]:
                                    show_success(result["message"])
                                    st.rerun() # Usar st.rerun()
                                else:
                                    show_error(result["message"])
                            else:
                                show_error("Por favor, selecione um hospital para vincular o posto.")
                    with col_del:
                        delete_submitted = st.form_submit_button("Excluir Posto de Saúde", help="Cuidado! A exclusão é irreversível e só é possível se não houver funcionários, pacientes, atendimentos ou estoque vinculados.")
                        if delete_submitted:
                            result = delete_posto_saude(selected_posto_id)
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
            else:
                show_info("Nenhum posto de saúde cadastrado para exibir ou editar.")
        else:
            show_info("Nenhum posto de saúde cadastrado ainda.")

# --- Seção de Gerenciamento de Funcionários --- #
def funcionario_management_section():
    st.header("Gerenciamento de Funcionários")

    tab1, tab2 = st.tabs(["Cadastrar Novo Funcionário", "Visualizar / Editar / Excluir Funcionários"])

    with tab1:
        st.subheader("Cadastrar Novo Funcionário")
        postos_disponiveis = get_all_postos_saude()
        posto_options = {"Selecione um Posto": None}
        if postos_disponiveis["success"] and postos_disponiveis["data"]:
            posto_options.update({ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis["data"]})

        with st.form("form_create_funcionario", clear_on_submit=True):
            nome = st.text_input("Nome do Funcionário *", key="f_nome_c")
            cpf = st.text_input("CPF *", key="f_cpf_c")
            cargo = st.selectbox("Cargo *", ["Selecione", "Médico", "Enfermeiro", "Recepcionista", "Farmacêutico", "Agente de Saúde", "Administrativo", "Técnico de Enfermagem"], key="f_cargo_c")
            especialidade = st.text_input("Especialidade (se Médico)", key="f_especialidade_c")
            registro_profissional = st.text_input("Registro Profissional (CRM, COREN, etc.)", key="f_registro_c")
            telefone = st.text_input("Telefone", key="f_telefone_c")
            email = st.text_input("E-mail *", key="f_email_c")
            senha = st.text_input("Senha *", type="password", key="f_senha_c")
            selected_posto_name = st.selectbox("Posto de Lotação *", list(posto_options.keys()), key="f_posto_c")
            id_posto_lotacao = posto_options[selected_posto_name] if selected_posto_name != "Selecione" else None

            submitted = st.form_submit_button("Cadastrar Funcionário")
            if submitted:
                if id_posto_lotacao is None:
                    show_error("Por favor, selecione um posto de lotação válido.")
                elif cargo == "Selecione":
                    show_error("Por favor, selecione um cargo para o funcionário.")
                else:
                    result = create_funcionario(nome, cpf, cargo, email, senha, id_posto_lotacao, especialidade, registro_profissional, telefone)
                    if result["success"]:
                        show_success(result["message"])
                    else:
                        show_error(result["message"])

    with tab2:
        st.subheader("Funcionários Cadastrados")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term_funcionario = st.text_input("Buscar Funcionário por Nome, CPF ou E-mail", key="search_funcionario")
        with col2:
            cargo_filter = st.selectbox("Filtrar por Cargo", ["Todos os Cargos", "Médico", "Enfermeiro", "Recepcionista", "Farmacêutico", "Agente de Saúde", "Administrativo", "Técnico de Enfermagem"], key="filter_funcionario_cargo")
            if cargo_filter == "Todos os Cargos":
                cargo_filter = None
        with col3:
            postos_disponiveis_filter = get_all_postos_saude()
            posto_filter_options = {"Todos os Postos": None}
            if postos_disponiveis_filter["success"] and postos_disponiveis_filter["data"]:
                posto_filter_options.update({ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis_filter["data"]})
            selected_posto_filter = st.selectbox("Filtrar por Posto de Lotação", list(posto_filter_options.keys()), key="filter_funcionario_posto")
            id_posto_filter = posto_filter_options[selected_posto_filter]

        funcionarios_data = get_all_funcionarios(search_term=search_term_funcionario, cargo=cargo_filter, id_posto_lotacao=id_posto_filter)
        if funcionarios_data["success"] and funcionarios_data["data"]:
            df_funcionarios = st.dataframe(funcionarios_data["data"], use_container_width=True, hide_index=True)

            st.subheader("Editar / Excluir Funcionário")
            funcionario_ids = {f["nome_funcionario"]: f["id_funcionario"] for f in funcionarios_data["data"]}
            selected_funcionario_name = st.selectbox("Selecione um Funcionário para Editar/Excluir", list(funcionario_ids.keys()), key="f_select_u_d")

            if selected_funcionario_name:
                selected_funcionario_id = funcionario_ids[selected_funcionario_name]
                funcionario_info = get_funcionario_by_id(selected_funcionario_id)["data"]

                with st.form("form_update_funcionario", clear_on_submit=False):
                    st.write(f"Editando Funcionário: **{funcionario_info["nome_funcionario"]}** (ID: {funcionario_info["id_funcionario"]})")
                    upd_nome = st.text_input("Nome do Funcionário *", value=funcionario_info["nome_funcionario"], key="f_nome_u")
                    upd_cpf = st.text_input("CPF *", value=funcionario_info["cpf_funcionario"], key="f_cpf_u")
                    upd_cargo = st.selectbox("Cargo *", ["Médico", "Enfermeiro", "Recepcionista", "Farmacêutico", "Agente de Saúde", "Administrativo", "Técnico de Enfermagem"], index=["Médico", "Enfermeiro", "Recepcionista", "Farmacêutico", "Agente de Saúde", "Administrativo", "Técnico de Enfermagem"].index(funcionario_info["cargo_funcionario"]), key="f_cargo_u")
                    upd_especialidade = st.text_input("Especialidade (se Médico)", value=funcionario_info["especialidade_medica"], key="f_especialidade_u")
                    upd_registro_profissional = st.text_input("Registro Profissional (CRM, COREN, etc.)", value=funcionario_info["registro_profissional"], key="f_registro_u")
                    upd_telefone = st.text_input("Telefone", value=funcionario_info["telefone_funcionario"], key="f_telefone_u")
                    upd_email = st.text_input("E-mail *", value=funcionario_info["email_funcionario"], key="f_email_u")
                    upd_senha = st.text_input("Nova Senha (deixe em branco para não alterar)", type="password", key="f_senha_u")

                    postos_disponiveis_upd = get_all_postos_saude()
                    posto_options_upd = {ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis_upd["data"]}
                    current_posto_name = funcionario_info["nome_posto"]
                    current_posto_index = list(posto_options_upd.keys()).index(current_posto_name) if current_posto_name in posto_options_upd else 0

                    selected_posto_name_upd = st.selectbox("Posto de Lotação *", list(posto_options_upd.keys()), index=current_posto_index, key="f_posto_u")
                    upd_id_posto_lotacao = posto_options_upd[selected_posto_name_upd] if selected_posto_name_upd else None

                    col_upd, col_del = st.columns(2)
                    with col_upd:
                        update_submitted = st.form_submit_button("Atualizar Funcionário")
                        if update_submitted:
                            if upd_id_posto_lotacao is None:
                                show_error("Por favor, selecione um posto de lotação válido.")
                            else:
                                result = update_funcionario(selected_funcionario_id, upd_nome, upd_cpf, upd_cargo, upd_especialidade, upd_registro_profissional, upd_telefone, upd_email, upd_senha if upd_senha else None, upd_id_posto_lotacao)
                                if result["success"]:
                                    show_success(result["message"])
                                    st.rerun() # Usar st.rerun()
                                else:
                                    show_error(result["message"])
                    with col_del:
                        delete_submitted = st.form_submit_button("Excluir Funcionário", help="Cuidado! A exclusão é irreversível e só é possível se não houver atendimentos ou distribuições vinculadas.")
                        if delete_submitted:
                            result = delete_funcionario(selected_funcionario_id)
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
            else:
                show_info("Nenhum funcionário cadastrado para exibir ou editar.")
        else:
            show_info("Nenhum funcionário cadastrado ainda.")

# --- Seção de Gerenciamento de Pacientes --- #
def paciente_management_section():
    st.header("Gerenciamento de Pacientes")

    tab1, tab2 = st.tabs(["Cadastrar Novo Paciente", "Visualizar / Editar / Excluir Pacientes"])

    with tab1:
        st.subheader("Cadastrar Novo Paciente")
        postos_disponiveis = get_all_postos_saude()
        posto_options = {"Selecione um Posto": None}
        if postos_disponiveis["success"] and postos_disponiveis["data"]:
            posto_options.update({ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis["data"]})

        with st.form("form_create_paciente", clear_on_submit=True):
            nome = st.text_input("Nome do Paciente *", key="p_nome_c")
            cpf = st.text_input("CPF *", key="p_cpf_c")
            cartao_sus = st.text_input("Cartão SUS", key="p_sus_c")
            data_nascimento = st.date_input("Data de Nascimento *", key="p_data_nasc_c")
            genero = st.selectbox("Gênero *", ["Selecione", "Masculino", "Feminino", "Outro"], key="p_genero_c")
            endereco = st.text_area("Endereço *", help="Rua, Número, Complemento, Bairro, Cidade, UF, CEP", key="p_endereco_c")
            telefone = st.text_input("Telefone", key="p_telefone_c")
            email = st.text_input("E-mail", key="p_email_c")
            selected_posto_name = st.selectbox("Posto de Referência *", list(posto_options.keys()), key="p_posto_c")
            id_posto_referencia = posto_options[selected_posto_name] if selected_posto_name != "Selecione" else None

            submitted = st.form_submit_button("Cadastrar Paciente")
            if submitted:
                if id_posto_referencia is None:
                    show_error("Por favor, selecione um posto de referência válido.")
                elif genero == "Selecione":
                    show_error("Por favor, selecione o gênero do paciente.")
                else:
                    result = create_paciente(nome, cpf, data_nascimento.strftime("%Y-%m-%d"), genero, endereco, id_posto_referencia, cartao_sus, telefone, email)
                    if result["success"]:
                        show_success(result["message"])
                    else:
                        show_error(result["message"])

    with tab2:
        st.subheader("Pacientes Cadastrados")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term_paciente = st.text_input("Buscar Paciente por Nome, CPF ou Cartão SUS", key="search_paciente")
        with col2:
            genero_filter = st.selectbox("Filtrar por Gênero", ["Todos os Gêneros", "Masculino", "Feminino", "Outro"], key="filter_paciente_genero")
            if genero_filter == "Todos os Gêneros":
                genero_filter = None
        with col3:
            postos_disponiveis_filter = get_all_postos_saude()
            posto_filter_options = {"Todos os Postos": None}
            if postos_disponiveis_filter["success"] and postos_disponiveis_filter["data"]:
                posto_filter_options.update({ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis_filter["data"]})
            selected_posto_filter = st.selectbox("Filtrar por Posto de Referência", list(posto_filter_options.keys()), key="filter_paciente_posto")
            id_posto_filter = posto_filter_options[selected_posto_filter]

        pacientes_data = get_all_pacientes(search_term=search_term_paciente, genero=genero_filter, id_posto_referencia=id_posto_filter)
        if pacientes_data["success"] and pacientes_data["data"]:
            df_pacientes = st.dataframe(pacientes_data["data"], use_container_width=True, hide_index=True)

            st.subheader("Editar / Excluir Paciente")
            paciente_ids = {p["nome_paciente"]: p["id_paciente"] for p in pacientes_data["data"]}
            selected_paciente_name = st.selectbox("Selecione um Paciente para Editar/Excluir", list(paciente_ids.keys()), key="p_select_u_d")

            if selected_paciente_name:
                selected_paciente_id = paciente_ids[selected_paciente_name]
                paciente_info = get_paciente_by_id(selected_paciente_id)["data"]

                with st.form("form_update_paciente", clear_on_submit=False):
                    st.write(f"Editando Paciente: **{paciente_info["nome_paciente"]}** (ID: {paciente_info["id_paciente"]})")
                    upd_nome = st.text_input("Nome do Paciente *", value=paciente_info["nome_paciente"], key="p_nome_u")
                    upd_cpf = st.text_input("CPF *", value=paciente_info["cpf_paciente"], key="p_cpf_u")
                    upd_cartao_sus = st.text_input("Cartão SUS", value=paciente_info["cartao_sus"], key="p_sus_u")
                    upd_data_nascimento = st.date_input("Data de Nascimento *", value=datetime.strptime(paciente_info["data_nascimento_paciente"], "%Y-%m-%d").date(), key="p_data_nasc_u")
                    upd_genero = st.selectbox("Gênero *", ["Masculino", "Feminino", "Outro"], index=["Masculino", "Feminino", "Outro"].index(paciente_info["genero_paciente"]), key="p_genero_u")
                    upd_endereco = st.text_area("Endereço *", value=paciente_info["endereco_paciente"], help="Rua, Número, Complemento, Bairro, Cidade, UF, CEP", key="p_endereco_u")
                    upd_telefone = st.text_input("Telefone", value=paciente_info["telefone_paciente"], key="p_telefone_u")
                    upd_email = st.text_input("E-mail", value=paciente_info["email_paciente"], key="p_email_u")

                    postos_disponiveis_upd = get_all_postos_saude()
                    posto_options_upd = {ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis_upd["data"]}
                    current_posto_name = paciente_info["nome_posto"]
                    current_posto_index = list(posto_options_upd.keys()).index(current_posto_name) if current_posto_name in posto_options_upd else 0

                    selected_posto_name_upd = st.selectbox("Posto de Referência *", list(posto_options_upd.keys()), index=current_posto_index, key="p_posto_u")
                    upd_id_posto_referencia = posto_options_upd[selected_posto_name_upd] if selected_posto_name_upd else None

                    col_upd, col_del = st.columns(2)
                    with col_upd:
                        update_submitted = st.form_submit_button("Atualizar Paciente")
                        if update_submitted:
                            if upd_id_posto_referencia is None:
                                show_error("Por favor, selecione um posto de referência válido.")
                            else:
                                result = update_paciente(selected_paciente_id, upd_nome, upd_cpf, upd_cartao_sus, upd_data_nascimento.strftime("%Y-%m-%d"), upd_genero, upd_endereco, upd_telefone, upd_email, upd_id_posto_referencia)
                                if result["success"]:
                                    show_success(result["message"])
                                    st.rerun() # Usar st.rerun()
                                else:
                                    show_error(result["message"])
                    with col_del:
                        delete_submitted = st.form_submit_button("Excluir Paciente", help="Cuidado! A exclusão é irreversível e só é possível se não houver atendimentos vinculados.")
                        if delete_submitted:
                            result = delete_paciente(selected_paciente_id)
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
            else:
                show_info("Nenhum paciente cadastrado para exibir ou editar.")
        else:
            show_info("Nenhum paciente cadastrado ainda.")

# --- Seção de Gerenciamento de Medicamentos --- #
def medicamento_management_section():
    st.header("Gerenciamento de Medicamentos")

    tab1, tab2 = st.tabs(["Cadastrar Novo Medicamento", "Visualizar / Editar / Excluir Medicamentos"])

    with tab1:
        st.subheader("Cadastrar Novo Medicamento")
        with st.form("form_create_medicamento", clear_on_submit=True):
            nome_comercial = st.text_input("Nome Comercial *", key="med_nome_c")
            principio_ativo = st.text_input("Princípio Ativo *", key="med_principio_c")
            apresentacao = st.text_input("Apresentação (Ex: Comprimido 500mg)", key="med_apresentacao_c")
            fabricante = st.text_input("Fabricante", key="med_fabricante_c")
            tipo_medicamento = st.selectbox("Tipo de Medicamento", ["Selecione", "Comum", "Controlado", "Antibiótico", "Vacina"], key="med_tipo_c")

            submitted = st.form_submit_button("Cadastrar Medicamento")
            if submitted:
                if tipo_medicamento == "Selecione":
                    tipo_medicamento = None
                result = create_medicamento(nome_comercial, principio_ativo, apresentacao, fabricante, tipo_medicamento)
                if result["success"]:
                    show_success(result["message"])
                else:
                    show_error(result["message"])

    with tab2:
        st.subheader("Medicamentos Cadastrados")
        
        col1, col2 = st.columns(2)
        with col1:
            search_term_medicamento = st.text_input("Buscar Medicamento por Nome ou Princípio Ativo", key="search_medicamento")
        with col2:
            tipo_medicamento_filter = st.selectbox("Filtrar por Tipo de Medicamento", ["Todos os Tipos", "Comum", "Controlado", "Antibiótico", "Vacina"], key="filter_medicamento_tipo")
            if tipo_medicamento_filter == "Todos os Tipos":
                tipo_medicamento_filter = None

        medicamentos_data = get_all_medicamentos(search_term=search_term_medicamento, tipo_medicamento=tipo_medicamento_filter)
        if medicamentos_data["success"] and medicamentos_data["data"]:
            df_medicamentos = st.dataframe(medicamentos_data["data"], use_container_width=True, hide_index=True)

            st.subheader("Editar / Excluir Medicamento")
            medicamento_ids = {m["nome_comercial_medicamento"]: m["id_medicamento"] for m in medicamentos_data["data"]}
            selected_medicamento_name = st.selectbox("Selecione um Medicamento para Editar/Excluir", list(medicamento_ids.keys()), key="med_select_u_d")

            if selected_medicamento_name:
                selected_medicamento_id = medicamento_ids[selected_medicamento_name]
                medicamento_info = get_medicamento_by_id(selected_medicamento_id)["data"]

                with st.form("form_update_medicamento", clear_on_submit=False):
                    st.write(f"Editando Medicamento: **{medicamento_info["nome_comercial_medicamento"]}** (ID: {medicamento_info["id_medicamento"]})")
                    upd_nome_comercial = st.text_input("Nome Comercial *", value=medicamento_info["nome_comercial_medicamento"], key="med_nome_u")
                    upd_principio_ativo = st.text_input("Princípio Ativo *", value=medicamento_info["principio_ativo"], key="med_principio_u")
                    upd_apresentacao = st.text_input("Apresentação", value=medicamento_info["apresentacao"], key="med_apresentacao_u")
                    upd_fabricante = st.text_input("Fabricante", value=medicamento_info["fabricante"], key="med_fabricante_u")
                    upd_tipo_medicamento = st.selectbox("Tipo de Medicamento", ["Comum", "Controlado", "Antibiótico", "Vacina"], index=["Comum", "Controlado", "Antibiótico", "Vacina"].index(medicamento_info["tipo_medicamento"]) if medicamento_info["tipo_medicamento"] else 0, key="med_tipo_u")

                    col_upd, col_del = st.columns(2)
                    with col_upd:
                        update_submitted = st.form_submit_button("Atualizar Medicamento")
                        if update_submitted:
                            result = update_medicamento(selected_medicamento_id, upd_nome_comercial, upd_principio_ativo, upd_apresentacao, upd_fabricante, upd_tipo_medicamento)
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
                    with col_del:
                        delete_submitted = st.form_submit_button("Excluir Medicamento", help="Cuidado! A exclusão é irreversível e só é possível se não houver estoque vinculado.")
                        if delete_submitted:
                            result = delete_medicamento(selected_medicamento_id)
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
            else:
                show_info("Nenhum medicamento cadastrado para exibir ou editar.")
        else:
            show_info("Nenhum medicamento cadastrado ainda.")

# --- Seção de Gerenciamento de Estoque de Medicamentos por Posto --- #
def estoque_medicamento_management_section():
    st.header("Gerenciamento de Estoque de Medicamentos")

    tab1, tab2 = st.tabs(["Adicionar/Atualizar Estoque", "Visualizar / Excluir Estoque"])

    with tab1:
        st.subheader("Adicionar/Atualizar Estoque de Medicamento")
        medicamentos_disponiveis = get_all_medicamentos()
        postos_disponiveis = get_all_postos_saude()

        medicamento_options = {"Selecione um Medicamento": None}
        if medicamentos_disponiveis["success"] and medicamentos_disponiveis["data"]:
            medicamento_options.update({m["nome_comercial_medicamento"]: m["id_medicamento"] for m in medicamentos_disponiveis["data"]})

        posto_options = {"Selecione um Posto": None}
        if postos_disponiveis["success"] and postos_disponiveis["data"]:
            posto_options.update({ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis["data"]})

        if not medicamento_options or not posto_options:
            show_info("Cadastre medicamentos e postos de saúde antes de gerenciar o estoque.")
            return

        with st.form("form_create_update_estoque", clear_on_submit=True):
            selected_medicamento_name = st.selectbox("Medicamento *", list(medicamento_options.keys()), key="emp_med_c")
            id_medicamento = medicamento_options[selected_medicamento_name] if selected_medicamento_name != "Selecione um Medicamento" else None

            selected_posto_name = st.selectbox("Posto de Saúde *", list(posto_options.keys()), key="emp_posto_c")
            id_posto = posto_options[selected_posto_name] if selected_posto_name != "Selecione um Posto" else None

            lote = st.text_input("Lote *", key="emp_lote_c")
            data_validade = st.date_input("Data de Validade *", key="emp_data_validade_c")
            quantidade_atual = st.number_input("Quantidade Atual", min_value=0, value=0, key="emp_qtd_c")
            quantidade_minima_alerta = st.number_input("Quantidade Mínima para Alerta", min_value=0, value=10, key="emp_qtd_min_c")

            submitted = st.form_submit_button("Salvar Estoque")
            if submitted:
                if not all([id_medicamento, id_posto, lote, data_validade]):
                    show_error("Por favor, preencha todos os campos obrigatórios (Medicamento, Posto, Lote, Data de Validade).")
                else:
                    result = create_estoque_medicamento_posto(id_medicamento, id_posto, lote, data_validade.strftime("%Y-%m-%d"), quantidade_atual, quantidade_minima_alerta)
                    if result["success"]:
                        show_success(result["message"])
                    else:
                        if "UNIQUE constraint failed" in result["message"]:
                            # Esta parte do código depende de 'get_db_connection' em oper_crud ou database
                            # Se 'get_db_connection' não estiver importado aqui, isso causará um NameError.
                            # Para manter a compatibilidade com a estrutura original, assumimos que existe.
                            try:
                                from oper_crud import get_db_connection # Tenta importar de oper_crud
                            except ImportError:
                                try:
                                    from database import get_db_connection # Tenta importar de database
                                except ImportError:
                                    show_error("Erro: get_db_connection não encontrada. Certifique-se de que está acessível.")
                                    return
                            
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT id_estoque FROM EstoqueMedicamentoPosto WHERE id_medicamento = ? AND id_posto = ? AND lote = ?", (id_medicamento, id_posto, lote))
                            existing_estoque = cursor.fetchone()
                            conn.close()
                            if existing_estoque:
                                existing_estoque_id = existing_estoque["id_estoque"]
                                update_result = update_estoque_medicamento_posto(existing_estoque_id, quantidade_atual, quantidade_minima_alerta, lote, data_validade.strftime("%Y-%m-%d"))
                                if update_result["success"]:
                                    show_success(f"Estoque existente atualizado com sucesso! (ID: {existing_estoque_id})")
                                else:
                                    show_error(f"Erro ao atualizar estoque existente: {update_result["message"]}")
                            else:
                                show_error(result["message"])
                        else:
                            show_error(result["message"])

    with tab2:
        st.subheader("Estoque de Medicamentos Cadastrados")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term_estoque = st.text_input("Buscar Estoque por Medicamento ou Lote", key="search_estoque")
        with col2:
            medicamentos_disponiveis_filter = get_all_medicamentos()
            medicamento_filter_options = {"Todos os Medicamentos": None}
            if medicamentos_disponiveis_filter["success"] and medicamentos_disponiveis_filter["data"]:
                medicamento_filter_options.update({m["nome_comercial_medicamento"]: m["id_medicamento"] for m in medicamentos_disponiveis_filter["data"]})
            selected_medicamento_filter = st.selectbox("Filtrar por Medicamento", list(medicamento_filter_options.keys()), key="filter_estoque_medicamento")
            id_medicamento_filter = medicamento_filter_options[selected_medicamento_filter]
        with col3:
            postos_disponiveis_filter = get_all_postos_saude()
            posto_filter_options = {"Todos os Postos": None}
            if postos_disponiveis_filter["success"] and postos_disponiveis_filter["data"]:
                posto_filter_options.update({ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis_filter["data"]})
            selected_posto_filter = st.selectbox("Filtrar por Posto", list(posto_filter_options.keys()), key="filter_estoque_posto")
            id_posto_filter = posto_filter_options[selected_posto_filter]
        
        col4, col5 = st.columns(2)
        with col4:
            validade_proxima_dias = st.number_input("Validade Próxima (dias, 0 para desativar)", min_value=0, value=0, key="filter_estoque_validade")
            if validade_proxima_dias == 0:
                validade_proxima_dias = None
        with col5:
            estoque_baixo_filter = st.checkbox("Mostrar Apenas Estoque Baixo", key="filter_estoque_baixo")

        estoque_data = get_all_estoque_medicamento_posto(search_term=search_term_estoque, id_medicamento=id_medicamento_filter, id_posto=id_posto_filter, validade_proxima_dias=validade_proxima_dias, estoque_baixo=estoque_baixo_filter)
        if estoque_data["success"] and estoque_data["data"]:
            df_estoque = st.dataframe(estoque_data["data"], use_container_width=True, hide_index=True)

            st.subheader("Excluir Registro de Estoque")
            estoque_options = {f"{e["nome_comercial_medicamento"]} - Lote: {e["lote"]} ({e["nome_posto"]})": e["id_estoque"] for e in estoque_data["data"]}
            selected_estoque_display = st.selectbox("Selecione um Registro de Estoque para Excluir", list(estoque_options.keys()), key="emp_select_d")

            if selected_estoque_display:
                selected_estoque_id = estoque_options[selected_estoque_display]

                delete_submitted = st.button("Excluir Registro de Estoque", key="emp_delete_btn", help="Cuidado! A exclusão é irreversível e só é possível se não houver prescrições vinculadas.")
                if delete_submitted:
                    result = delete_estoque_medicamento_posto(selected_estoque_id)
                    if result["success"]:
                        show_success(result["message"])
                        st.rerun() # Usar st.rerun()
                    else:
                        show_error(result["message"])
            else:
                show_info("Nenhum registro de estoque cadastrado para exibir ou excluir.")
        else:
            show_info("Nenhum registro de estoque cadastrado ainda.")

# --- Seção de Gerenciamento de Atendimentos --- #
def atendimento_management_section():
    st.header("Gerenciamento de Atendimentos")

    tab1, tab2 = st.tabs(["Registrar Novo Atendimento", "Visualizar / Editar / Excluir Atendimentos"])

    with tab1:
        st.subheader("Registrar Novo Atendimento")
        pacientes_disponiveis = get_all_pacientes()
        funcionarios_disponiveis = get_all_funcionarios()
        postos_disponiveis = get_all_postos_saude()

        paciente_options = {"Selecione um Paciente": None}
        if pacientes_disponiveis["success"] and pacientes_disponiveis["data"]:
            paciente_options.update({p["nome_paciente"]: p["id_paciente"] for p in pacientes_disponiveis["data"]})

        funcionario_options = {"Selecione um Funcionário": None}
        if funcionarios_disponiveis["success"] and funcionarios_disponiveis["data"]:
            funcionario_options.update({f["nome_funcionario"]: f["id_funcionario"] for f in funcionarios_disponiveis["data"]})

        posto_options = {"Selecione um Posto": None}
        if postos_disponiveis["success"] and postos_disponiveis["data"]:
            posto_options.update({ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis["data"]})

        if not paciente_options or not funcionario_options or not posto_options:
            show_info("Cadastre pacientes, funcionários e postos de saúde antes de registrar atendimentos.")
            return

        with st.form("form_create_atendimento", clear_on_submit=True):
            selected_paciente_name = st.selectbox("Paciente *", list(paciente_options.keys()), key="at_paciente_c")
            id_paciente = paciente_options[selected_paciente_name] if selected_paciente_name != "Selecione um Paciente" else None

            selected_funcionario_name = st.selectbox("Funcionário Responsável *", list(funcionario_options.keys()), key="at_funcionario_c")
            id_funcionario_responsavel = funcionario_options[selected_funcionario_name] if selected_funcionario_name != "Selecione um Funcionário" else None

            selected_posto_name = st.selectbox("Posto de Atendimento *", list(posto_options.keys()), key="at_posto_c")
            id_posto_atendimento = posto_options[selected_posto_name] if selected_posto_name != "Selecione um Posto" else None

            tipo_atendimento = st.selectbox("Tipo de Atendimento *", ["Selecione", "Consulta Médica", "Curativo", "Vacinação", "Triagem", "Exame", "Outro"], key="at_tipo_c")
            descricao_sintomas_queixa = st.text_area("Descrição dos Sintomas/Queixa *", key="at_sintomas_c")
            diagnostico = st.text_area("Diagnóstico", key="at_diagnostico_c")
            cid10 = st.text_input("CID-10", help="Código da Classificação Internacional de Doenças", key="at_cid10_c")
            grau_doenca_observado = st.selectbox("Grau da Doença Observado", ["Selecione", "Leve", "Moderado", "Grave", "Crônico", "Agudo"], key="at_grau_c")
            observacoes_gerais = st.text_area("Observações Gerais", key="at_obs_c")

            data_hora_inicio = st.date_input("Data de Início", value=date.today(), key="at_data_inicio_c")
            hora_inicio = st.time_input("Hora de Início", value=datetime.now().time(), key="at_hora_inicio_c")
            data_hora_fim = st.date_input("Data de Fim (opcional)", value=None, key="at_data_fim_c")
            hora_fim = st.time_input("Hora de Fim (opcional)", value=None, key="at_hora_fim_c")

            submitted = st.form_submit_button("Registrar Atendimento")
            if submitted:
                if not all([id_paciente, id_funcionario_responsavel, id_posto_atendimento, tipo_atendimento != "Selecione", descricao_sintomas_queixa]):
                    show_error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    dt_inicio_str = f"{data_hora_inicio.strftime("%Y-%m-%d")} {hora_inicio.strftime("%H:%M:%S")}"
                    dt_fim_str = None
                    if data_hora_fim and hora_fim:
                        dt_fim_str = f"{data_hora_fim.strftime("%Y-%m-%d")} {hora_fim.strftime("%H:%M:%S")}"

                    result = create_atendimento(
                        id_paciente, id_funcionario_responsavel, id_posto_atendimento, tipo_atendimento,
                        descricao_sintomas_queixa, dt_inicio_str, dt_fim_str, diagnostico, cid10,
                        grau_doenca_observado if grau_doenca_observado != "Selecione" else None, observacoes_gerais
                    )
                    if result["success"]:
                        show_success(result["message"])
                    else:
                        show_error(result["message"])

    with tab2:
        st.subheader("Atendimentos Registrados")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term_atendimento = st.text_input("Buscar Atendimento por Paciente, Funcionário, Sintomas ou Diagnóstico", key="search_atendimento")
        with col2:
            pacientes_disponiveis_filter = get_all_pacientes()
            paciente_filter_options = {"Todos os Pacientes": None}
            if pacientes_disponiveis_filter["success"] and pacientes_disponiveis_filter["data"]:
                paciente_filter_options.update({p["nome_paciente"]: p["id_paciente"] for p in pacientes_disponiveis_filter["data"]})
            selected_paciente_filter = st.selectbox("Filtrar por Paciente", list(paciente_filter_options.keys()), key="filter_atendimento_paciente")
            id_paciente_filter = paciente_filter_options[selected_paciente_filter]
        with col3:
            funcionarios_disponiveis_filter = get_all_funcionarios()
            funcionario_filter_options = {"Todos os Funcionários": None}
            if funcionarios_disponiveis_filter["success"] and funcionarios_disponiveis_filter["data"]:
                funcionario_filter_options.update({f["nome_funcionario"]: f["id_funcionario"] for f in funcionarios_disponiveis_filter["data"]})
            selected_funcionario_filter = st.selectbox("Filtrar por Funcionário Responsável", list(funcionario_filter_options.keys()), key="filter_atendimento_funcionario")
            id_funcionario_filter = funcionario_filter_options[selected_funcionario_filter]
        
        col4, col5, col6 = st.columns(3)
        with col4:
            posto_filter_options = {"Todos os Postos": None}
            postos_disponiveis_filter = get_all_postos_saude()
            if postos_disponiveis_filter["success"] and postos_disponiveis_filter["data"]:
                posto_filter_options.update({ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis_filter["data"]})
            selected_posto_filter = st.selectbox("Filtrar por Posto de Atendimento", list(posto_filter_options.keys()), key="filter_atendimento_posto")
            id_posto_filter = posto_filter_options[selected_posto_filter]
        with col5:
            tipo_atendimento_filter = st.selectbox("Filtrar por Tipo de Atendimento", ["Todos os Tipos", "Consulta Médica", "Curativo", "Vacinação", "Triagem", "Exame", "Outro"], key="filter_atendimento_tipo")
            if tipo_atendimento_filter == "Todos os Tipos":
                tipo_atendimento_filter = None
        with col6:
            cid10_filter = st.text_input("Filtrar por CID-10", key="filter_atendimento_cid10")
        
        col7, col8, col9 = st.columns(3)
        with col7:
            grau_doenca_filter = st.selectbox("Filtrar por Grau da Doença", ["Todos os Graus", "Leve", "Moderado", "Grave", "Crônico", "Agudo"], key="filter_atendimento_grau")
            if grau_doenca_filter == "Todos os Graus":
                grau_doenca_filter = None
        with col8:
            start_date_filter = st.date_input("Data de Início (filtro)", value=None, key="filter_atendimento_start_date")
            if start_date_filter:
                start_date_filter = start_date_filter.strftime("%Y-%m-%d")
        with col9:
            end_date_filter = st.date_input("Data de Fim (filtro)", value=None, key="filter_atendimento_end_date")
            if end_date_filter:
                end_date_filter = end_date_filter.strftime("%Y-%m-%d")

        atendimentos_data = get_all_atendimentos(
            search_term=search_term_atendimento,
            id_paciente=id_paciente_filter,
            id_funcionario=id_funcionario_filter,
            id_posto=id_posto_filter,
            tipo_atendimento=tipo_atendimento_filter,
            cid10=cid10_filter,
            grau_doenca=grau_doenca_filter,
            start_date=start_date_filter,
            end_date=end_date_filter
        )
        if atendimentos_data["success"] and atendimentos_data["data"]:
            df_atendimentos = st.dataframe(atendimentos_data["data"], use_container_width=True, hide_index=True)

            st.subheader("Editar / Excluir Atendimento")
            atendimento_options = {f"ID: {a["id_atendimento"]} - {a["nome_paciente"]} ({a["data_hora_inicio_atendimento"]})": a["id_atendimento"] for a in atendimentos_data["data"]}
            selected_atendimento_display = st.selectbox("Selecione um Atendimento para Editar/Excluir", list(atendimento_options.keys()), key="at_select_u_d")

            if selected_atendimento_display:
                selected_atendimento_id = atendimento_options[selected_atendimento_display]
                atendimento_info = get_atendimento_by_id(selected_atendimento_id)["data"]

                with st.form("form_update_atendimento", clear_on_submit=False):
                    st.write(f"Editando Atendimento: **ID {atendimento_info["id_atendimento"]} - {atendimento_info["nome_paciente"]}**")

                    pacientes_disponiveis_upd = get_all_pacientes()
                    paciente_options_upd = {p["nome_paciente"]: p["id_paciente"] for p in pacientes_disponiveis_upd["data"]}
                    current_paciente_name = atendimento_info["nome_paciente"]
                    current_paciente_index = list(paciente_options_upd.keys()).index(current_paciente_name) if current_paciente_name in paciente_options_upd else 0
                    upd_id_paciente = st.selectbox("Paciente *", list(paciente_options_upd.keys()), index=current_paciente_index, key="at_paciente_u")
                    upd_id_paciente = paciente_options_upd[upd_id_paciente]

                    funcionarios_disponiveis_upd = get_all_funcionarios()
                    funcionario_options_upd = {f["nome_funcionario"]: f["id_funcionario"] for f in funcionarios_disponiveis_upd["data"]}
                    current_funcionario_name = atendimento_info["nome_funcionario"]
                    current_funcionario_index = list(funcionario_options_upd.keys()).index(current_funcionario_name) if current_funcionario_name in funcionario_options_upd else 0
                    upd_id_funcionario_responsavel = st.selectbox("Funcionário Responsável *", list(funcionario_options_upd.keys()), index=current_funcionario_index, key="at_funcionario_u")
                    upd_id_funcionario_responsavel = funcionario_options_upd[upd_id_funcionario_responsavel]

                    postos_disponiveis_upd = get_all_postos_saude()
                    posto_options_upd = {ps["nome_posto"]: ps["id_posto"] for ps in postos_disponiveis_upd["data"]}
                    current_posto_name = atendimento_info["nome_posto"]
                    current_posto_index = list(posto_options_upd.keys()).index(current_posto_name) if current_posto_name in posto_options_upd else 0
                    upd_id_posto_atendimento = st.selectbox("Posto de Atendimento *", list(posto_options_upd.keys()), index=current_posto_index, key="at_posto_u")
                    upd_id_posto_atendimento = posto_options_upd[upd_id_posto_atendimento]

                    upd_tipo_atendimento = st.selectbox("Tipo de Atendimento *", ["Consulta Médica", "Curativo", "Vacinação", "Triagem", "Exame", "Outro"], index=["Consulta Médica", "Curativo", "Vacinação", "Triagem", "Exame", "Outro"].index(atendimento_info["tipo_atendimento"]), key="at_tipo_u")
                    upd_descricao_sintomas_queixa = st.text_area("Descrição dos Sintomas/Queixa *", value=atendimento_info["descricao_sintomas_queixa"], key="at_sintomas_u")
                    upd_diagnostico = st.text_area("Diagnóstico", value=atendimento_info["diagnostico"], key="at_diagnostico_u")
                    upd_cid10 = st.text_input("CID-10", value=atendimento_info["cid10"], key="at_cid10_u")
                    upd_grau_doenca_observado = st.selectbox("Grau da Doença Observado", ["Leve", "Moderado", "Grave", "Crônico", "Agudo"], index=["Leve", "Moderado", "Grave", "Crônico", "Agudo"].index(atendimento_info["grau_doenca_observado"]) if atendimento_info["grau_doenca_observado"] else 0, key="at_grau_u")
                    upd_observacoes_gerais = st.text_area("Observações Gerais", value=atendimento_info["observacoes_gerais"], key="at_obs_u")

                    dt_inicio_obj = datetime.strptime(atendimento_info["data_hora_inicio_atendimento"], "%Y-%m-%d %H:%M:%S")
                    upd_data_hora_inicio = st.date_input("Data de Início", value=dt_inicio_obj.date(), key="at_data_inicio_u")
                    upd_hora_inicio = st.time_input("Hora de Início", value=dt_inicio_obj.time(), key="at_hora_inicio_u")

                    dt_fim_obj = None
                    if atendimento_info["data_hora_fim_atendimento"]:
                        dt_fim_obj = datetime.strptime(atendimento_info["data_hora_fim_atendimento"], "%Y-%m-%d %H:%M:%S")
                    upd_data_hora_fim = st.date_input("Data de Fim (opcional)", value=dt_fim_obj.date() if dt_fim_obj else None, key="at_data_fim_u")
                    upd_hora_fim = st.time_input("Hora de Fim (opcional)", value=dt_fim_obj.time() if dt_fim_obj else None, key="at_hora_fim_u")

                    col_upd, col_del = st.columns(2)
                    with col_upd:
                        update_submitted = st.form_submit_button("Atualizar Atendimento")
                        if update_submitted:
                            upd_dt_inicio_str = f"{upd_data_hora_inicio.strftime("%Y-%m-%d")} {upd_hora_inicio.strftime("%H:%M:%S")}"
                            upd_dt_fim_str = None
                            if upd_data_hora_fim and upd_hora_fim:
                                upd_dt_fim_str = f"{upd_data_hora_fim.strftime("%Y-%m-%d")} {upd_hora_fim.strftime("%H:%M:%S")}"

                            result = update_atendimento(
                                selected_atendimento_id, upd_id_paciente, upd_id_funcionario_responsavel, upd_id_posto_atendimento,
                                upd_dt_inicio_str, upd_dt_fim_str, upd_tipo_atendimento, upd_descricao_sintomas_queixa,
                                upd_diagnostico, upd_cid10, upd_grau_doenca_observado, upd_observacoes_gerais
                            )
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
                    with col_del:
                        delete_submitted = st.form_submit_button("Excluir Atendimento", help="Cuidado! A exclusão é irreversível e só é possível se não houver prescrições vinculadas.")
                        if delete_submitted:
                            result = delete_atendimento(selected_atendimento_id)
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
            else:
                show_info("Nenhum atendimento registrado para exibir ou editar.")
        else:
            show_info("Nenhum atendimento registrado ainda.")

# --- Seção de Gerenciamento de Prescrições --- #
def prescricao_management_section():
    st.header("Gerenciamento de Prescrições")

    tab1, tab2 = st.tabs(["Registrar Nova Prescrição", "Visualizar / Editar / Excluir Prescrições"])

    with tab1:
        st.subheader("Registrar Nova Prescrição")
        atendimentos_disponiveis = get_all_atendimentos()
        estoque_disponivel = get_all_estoque_medicamento_posto()

        atendimento_options = {"Selecione um Atendimento": None}
        if atendimentos_disponiveis["success"] and atendimentos_disponiveis["data"]:
            atendimento_options.update({f"ID: {a["id_atendimento"]} - {a["nome_paciente"]} ({a["data_hora_inicio_atendimento"]})": a["id_atendimento"] for a in atendimentos_disponiveis["data"]})

        medicamento_estoque_options = {"Selecione um Medicamento em Estoque": None}
        if estoque_disponivel["success"] and estoque_disponivel["data"]:
            medicamento_estoque_options.update({f"{e["nome_comercial_medicamento"]} (Lote: {e["lote"]}) - Qtd: {e["quantidade_atual"]} ({e["nome_posto"]})": e["id_estoque"] for e in estoque_disponivel["data"]})

        if not atendimento_options or not medicamento_estoque_options:
            show_info("Cadastre atendimentos e medicamentos em estoque antes de registrar prescrições.")
            return

        with st.form("form_create_prescricao", clear_on_submit=True):
            selected_atendimento_display = st.selectbox("Atendimento *", list(atendimento_options.keys()), key="pr_atendimento_c")
            id_atendimento = atendimento_options[selected_atendimento_display] if selected_atendimento_display != "Selecione um Atendimento" else None

            selected_medicamento_estoque_display = st.selectbox("Medicamento em Estoque *", list(medicamento_estoque_options.keys()), key="pr_medicamento_estoque_c")
            id_medicamento_estoque = medicamento_estoque_options[selected_medicamento_estoque_display] if selected_medicamento_estoque_display != "Selecione um Medicamento em Estoque" else None

            posologia = st.text_area("Posologia *", help="Ex: 1 comprimido a cada 8 horas por 7 dias", key="pr_posologia_c")
            quantidade_prescrita = st.number_input("Quantidade Prescrita *", min_value=1, value=1, key="pr_qtd_c")

            submitted = st.form_submit_button("Registrar Prescrição")
            if submitted:
                if not all([id_atendimento, id_medicamento_estoque, posologia, quantidade_prescrita]):
                    show_error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    result = create_prescricao(id_atendimento, id_medicamento_estoque, posologia, quantidade_prescrita)
                    if result["success"]:
                        show_success(result["message"])
                    else:
                        show_error(result["message"])

    with tab2:
        st.subheader("Prescrições Registradas")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term_prescricao = st.text_input("Buscar Prescrição por Paciente, Medicamento ou Posologia", key="search_prescricao")
        with col2:
            atendimentos_disponiveis_filter = get_all_atendimentos()
            atendimento_filter_options = {"Todos os Atendimentos": None}
            if atendimentos_disponiveis_filter["success"] and atendimentos_disponiveis_filter["data"]:
                atendimento_filter_options.update({f"ID: {a["id_atendimento"]} - {a["nome_paciente"]}": a["id_atendimento"] for a in atendimentos_disponiveis_filter["data"]})
            selected_atendimento_filter = st.selectbox("Filtrar por Atendimento", list(atendimento_filter_options.keys()), key="filter_prescricao_atendimento")
            id_atendimento_filter = atendimento_filter_options[selected_atendimento_filter]
        with col3:
            medicamentos_disponiveis_filter = get_all_medicamentos()
            medicamento_filter_options = {"Todos os Medicamentos": None}
            if medicamentos_disponiveis_filter["success"] and medicamentos_disponiveis_filter["data"]:
                medicamento_filter_options.update({m["nome_comercial_medicamento"]: m["id_medicamento"] for m in medicamentos_disponiveis_filter["data"]})
            selected_medicamento_filter = st.selectbox("Filtrar por Medicamento", list(medicamento_filter_options.keys()), key="filter_prescricao_medicamento")
            id_medicamento_filter = medicamento_filter_options[selected_medicamento_filter]
        
        status_distribuicao_filter = st.selectbox("Filtrar por Status de Distribuição", ["Todos os Status", "Pendente", "Distribuido Parcialmente", "Distribuido Totalmente", "Cancelado"], key="filter_prescricao_status")
        if status_distribuicao_filter == "Todos os Status":
            status_distribuicao_filter = None

        prescricoes_data = get_all_prescricoes(
            search_term=search_term_prescricao,
            id_atendimento=id_atendimento_filter,
            id_medicamento=id_medicamento_filter,
            status_distribuicao=status_distribuicao_filter
        )
        if prescricoes_data["success"] and prescricoes_data["data"]:
            df_prescricoes = st.dataframe(prescricoes_data["data"], use_container_width=True, hide_index=True)

            st.subheader("Editar / Excluir Prescrição")
            prescricao_options = {f"ID: {pr["id_prescricao"]} - {pr["nome_comercial_medicamento"]} para {pr["nome_paciente"]}": pr["id_prescricao"] for pr in prescricoes_data["data"]}
            selected_prescricao_display = st.selectbox("Selecione uma Prescrição para Editar/Excluir", list(prescricao_options.keys()), key="pr_select_u_d")

            if selected_prescricao_display:
                selected_prescricao_id = prescricao_options[selected_prescricao_display]
                prescricao_info = get_prescricao_by_id(selected_prescricao_id)["data"]

                with st.form("form_update_prescricao", clear_on_submit=False):
                    st.write(f"Editando Prescrição: **ID {prescricao_info["id_prescricao"]}**")

                    atendimentos_disponiveis_upd = get_all_atendimentos()
                    atendimento_options_upd = {f"ID: {a["id_atendimento"]} - {a["nome_paciente"]} ({a["data_hora_inicio_atendimento"]})": a["id_atendimento"] for a in atendimentos_disponiveis_upd["data"]}
                    current_atendimento_display = f"ID: {prescricao_info["id_atendimento"]} - {prescricao_info["nome_paciente"]} ({prescricao_info["data_hora_inicio_atendimento"]})"
                    current_atendimento_index = list(atendimento_options_upd.keys()).index(current_atendimento_display) if current_atendimento_display in atendimento_options_upd else 0
                    upd_id_atendimento = st.selectbox("Atendimento *", list(atendimento_options_upd.keys()), index=current_atendimento_index, key="pr_atendimento_u")
                    upd_id_atendimento = atendimento_options_upd[upd_id_atendimento]

                    estoque_disponivel_upd = get_all_estoque_medicamento_posto()
                    medicamento_estoque_options_upd = {f"{e["nome_comercial_medicamento"]} (Lote: {e["lote"]}) - Qtd: {e["quantidade_atual"]} ({e["nome_posto"]})": e["id_estoque"] for e in estoque_disponivel_upd["data"]}
                    
                    # Crie a string de exibição para o medicamento em estoque atual da prescrição
                    # Certifique-se de que todas as chaves esperadas existam em prescricao_info antes de tentar formatar.
                    # As chaves 'nome_comercial_medicamento', 'lote', 'quantidade_atual', 'nome_posto'
                    # devem vir da sua função get_prescricao_by_id em oper_crud.py (após o JOIN).
                    current_medicamento_estoque_display = (
                        f"{prescricao_info.get("nome_comercial_medicamento", "N/A")} "
                        f"(Lote: {prescricao_info.get("lote", "N/A")}) - "
                        f"Qtd: {prescricao_info.get("quantidade_atual", "N/A")} "
                        f"({prescricao_info.get("nome_posto", "N/A")})"
                    )

                    current_medicamento_estoque_index = 0
                    if current_medicamento_estoque_display in medicamento_estoque_options_upd:
                        current_medicamento_estoque_index = list(medicamento_estoque_options_upd.keys()).index(current_medicamento_estoque_display)
                    
                    upd_id_medicamento_estoque = st.selectbox("Medicamento em Estoque *", list(medicamento_estoque_options_upd.keys()), index=current_medicamento_estoque_index, key="pr_medicamento_estoque_u")
                    upd_id_medicamento_estoque = medicamento_estoque_options_upd[upd_id_medicamento_estoque]

                    upd_posologia = st.text_area("Posologia *", value=prescricao_info["posologia"], key="pr_posologia_u")
                    upd_quantidade_prescrita = st.number_input("Quantidade Prescrita *", min_value=1, value=prescricao_info["quantidade_prescrita"], key="pr_qtd_u")
                    upd_status_distribuicao = st.selectbox("Status de Distribuição", ["Pendente", "Distribuido Parcialmente", "Distribuido Totalmente", "Cancelado"], index=["Pendente", "Distribuido Parcialmente", "Distribuido Totalmente", "Cancelado"].index(prescricao_info["status_distribuicao"]), key="pr_status_u")

                    col_upd, col_del = st.columns(2)
                    with col_upd:
                        update_submitted = st.form_submit_button("Atualizar Prescrição")
                        if update_submitted:
                            result = update_prescricao(selected_prescricao_id, upd_id_atendimento, upd_id_medicamento_estoque, upd_posologia, upd_quantidade_prescrita, upd_status_distribuicao)
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
                    with col_del:
                        delete_submitted = st.form_submit_button("Excluir Prescrição", help="Cuidado! A exclusão é irreversível e só é possível se não houver distribuições vinculadas.")
                        if delete_submitted:
                            result = delete_prescricao(selected_prescricao_id)
                            if result["success"]:
                                show_success(result["message"])
                                st.rerun() # Usar st.rerun()
                            else:
                                show_error(result["message"])
            else:
                show_info("Nenhuma prescrição registrada para exibir ou editar.")
        else:
            show_info("Nenhuma prescrição registrada ainda.")

# --- Seção de Gerenciamento de Distribuição de Medicamentos --- #
def distribuicao_medicamento_management_section():
    st.header("Gerenciamento de Distribuição de Medicamentos")

    tab1, tab2 = st.tabs(["Registrar Nova Distribuição", "Visualizar Distribuições"])

    with tab1:
        st.subheader("Registrar Nova Distribuição")
        prescricoes_pendentes = get_all_prescricoes()
        funcionarios_disponiveis = get_all_funcionarios()

        prescricao_options = {"Selecione uma Prescrição Pendente": None}
        if prescricoes_pendentes["success"] and prescricoes_pendentes["data"]:
            filtered_prescricoes = [pr for pr in prescricoes_pendentes["data"] if pr["status_distribuicao"] in ["Pendente", "Distribuida Parcialmente"]]
            prescricao_options.update({f"ID: {pr["id_prescricao"]} - {pr["nome_comercial_medicamento"]} para {pr["nome_paciente"]} (Qtd: {pr["quantidade_prescrita"]})": pr["id_prescricao"] for pr in filtered_prescricoes})

        funcionario_options = {"Selecione um Funcionário Distribuidor": None}
        if funcionarios_disponiveis["success"] and funcionarios_disponiveis["data"]:
            filtered_funcionarios = [f for f in funcionarios_disponiveis["data"] if f["cargo_funcionario"] in ["Farmacêutico", "Enfermeiro"]]
            funcionario_options.update({f["nome_funcionario"]: f["id_funcionario"] for f in filtered_funcionarios})

        if not prescricao_options or not funcionario_options:
            show_info("Não há prescrições pendentes ou funcionários aptos para distribuição. Cadastre-os primeiro.")
            return

        with st.form("form_create_distribuicao", clear_on_submit=True):
            selected_prescricao_display = st.selectbox("Prescrição *", list(prescricao_options.keys()), key="disp_prescricao_c")
            id_prescricao = prescricao_options[selected_prescricao_display] if selected_prescricao_display != "Selecione uma Prescrição Pendente" else None

            selected_funcionario_display = st.selectbox("Funcionário Distribuidor *", list(funcionario_options.keys()), key="disp_funcionario_c")
            id_funcionario_distribuidor = funcionario_options[selected_funcionario_display] if selected_funcionario_display != "Selecione um Funcionário Distribuidor" else None

            quantidade_prescrita_default = 1
            if id_prescricao:
                prescricao_info = get_prescricao_by_id(id_prescricao)
                if prescricao_info["success"]:
                    quantidade_prescrita_default = prescricao_info["data"]["quantidade_prescrita"]

            quantidade_distribuida = st.number_input("Quantidade a Distribuir *", min_value=1, value=quantidade_prescrita_default, key="disp_qtd_c")
            observacao = st.text_area("Observações", key="disp_obs_c")

            submitted = st.form_submit_button("Registrar Distribuição")
            if submitted:
                if not all([id_prescricao, id_funcionario_distribuidor, quantidade_distribuida]):
                    show_error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    result = create_distribuicao_medicamento(id_prescricao, id_funcionario_distribuidor, quantidade_distribuida, observacao)
                    if result["success"]:
                        show_success(result["message"])
                    else:
                        show_error(result["message"])

    with tab2:
        st.subheader("Distribuições Registradas")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term_distribuicao = st.text_input("Buscar Distribuição por Paciente, Medicamento ou Funcionário", key="search_distribuicao")
        with col2:
            prescricoes_disponiveis_filter = get_all_prescricoes()
            prescricao_filter_options = {"Todas as Prescrições": None}
            if prescricoes_disponiveis_filter["success"] and prescricoes_disponiveis_filter["data"]:
                prescricao_filter_options.update({f"ID: {pr["id_prescricao"]} - {pr["nome_comercial_medicamento"]} para {pr["nome_paciente"]}": pr["id_prescricao"] for pr in prescricoes_disponiveis_filter["data"]})
            selected_prescricao_filter = st.selectbox("Filtrar por Prescrição", list(prescricao_filter_options.keys()), key="filter_distribuicao_prescricao")
            id_prescricao_filter = prescricao_filter_options[selected_prescricao_filter]
        with col3:
            funcionarios_disponiveis_filter = get_all_funcionarios()
            funcionario_filter_options = {"Todos os Funcionários": None}
            if funcionarios_disponiveis_filter["success"] and funcionarios_disponiveis_filter["data"]:
                funcionario_filter_options.update({f["nome_funcionario"]: f["id_funcionario"] for f in funcionarios_disponiveis_filter["data"]})
            selected_funcionario_filter = st.selectbox("Filtrar por Funcionário Distribuidor", list(funcionario_filter_options.keys()), key="filter_distribuicao_funcionario")
            id_funcionario_filter = funcionario_filter_options[selected_funcionario_filter]
        
        col4, col5 = st.columns(2)
        with col4:
            start_date_filter = st.date_input("Data de Início (filtro)", value=None, key="filter_distribuicao_start_date")
            if start_date_filter:
                start_date_filter = start_date_filter.strftime("%Y-%m-%d")
        with col5:
            end_date_filter = st.date_input("Data de Fim (filtro)", value=None, key="filter_distribuicao_end_date")
            if end_date_filter:
                end_date_filter = end_date_filter.strftime("%Y-%m-%d")

        distribuicoes_data = get_all_distribuicoes_medicamento(
            search_term=search_term_distribuicao,
            id_prescricao=id_prescricao_filter,
            id_funcionario_distribuidor=id_funcionario_filter,
            start_date=start_date_filter,
            end_date=end_date_filter
        )
        if distribuicoes_data["success"] and distribuicoes_data["data"]:
            df_distribuicoes = st.dataframe(distribuicoes_data["data"], use_container_width=True, hide_index=True)
        else:
            show_info("Nenhuma distribuição registrada ainda.")

# --- Seção de Relatórios e Análises --- #
def reports_section():
    st.header("Relatórios e Análises")

    st.subheader("Filtros de Período para Relatórios")
    col_start, col_end = st.columns(2)
    with col_start:
        report_start_date = st.date_input("Data de Início do Período", value=None, key="report_start_date")
        if report_start_date:
            report_start_date = report_start_date.strftime("%Y-%m-%d")
    with col_end:
        report_end_date = st.date_input("Data de Fim do Período", value=None, key="report_end_date")
        if report_end_date:
            report_end_date = report_end_date.strftime("%Y-%m-%d")

    st.markdown("--- ")

    st.subheader("1. Atendimentos por Tipo")
    atendimentos_tipo_data = get_atendimentos_by_type(report_start_date, report_end_date)
    if atendimentos_tipo_data["success"] and atendimentos_tipo_data["data"]:
        df_atendimentos_tipo = pd.DataFrame(atendimentos_tipo_data["data"])
        st.dataframe(df_atendimentos_tipo, use_container_width=True, hide_index=True)
        st.bar_chart(df_atendimentos_tipo.set_index("tipo_atendimento"))
    else:
        show_info("Nenhum dado de atendimento por tipo para o período selecionado.")

    st.markdown("--- ")

    st.subheader("2. Atendimentos por Posto de Saúde")
    atendimentos_posto_data = get_atendimentos_by_posto(report_start_date, report_end_date)
    if atendimentos_posto_data["success"] and atendimentos_posto_data["data"]:
        df_atendimentos_posto = pd.DataFrame(atendimentos_posto_data["data"])
        st.dataframe(df_atendimentos_posto, use_container_width=True, hide_index=True)
        st.bar_chart(df_atendimentos_posto.set_index("nome_posto"))
    else:
        show_info("Nenhum dado de atendimento por posto para o período selecionado.")

    st.markdown("--- ")

    st.subheader("3. Pacientes por Gênero")
    pacientes_genero_data = get_pacientes_by_genero()
    if pacientes_genero_data["success"] and pacientes_genero_data["data"]:
        df_pacientes_genero = pd.DataFrame(pacientes_genero_data["data"])
        st.dataframe(df_pacientes_genero, use_container_width=True, hide_index=True)
        fig, ax = plt.subplots()
        ax.pie(df_pacientes_genero["total"], labels=df_pacientes_genero["genero_paciente"], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)
    else:
        show_info("Nenhum dado de paciente por gênero.")

    st.markdown("--- ")

    st.subheader("4. Pacientes por Faixa Etária")
    pacientes_idade_data = get_pacientes_by_idade_group()
    if pacientes_idade_data["success"] and pacientes_idade_data["data"]:
        df_pacientes_idade = pd.DataFrame(pacientes_idade_data["data"])
        st.dataframe(df_pacientes_idade, use_container_width=True, hide_index=True)
        st.bar_chart(df_pacientes_idade.set_index("faixa_etaria"))
    else:
        show_info("Nenhum dado de paciente por faixa etária.")

    st.markdown("--- ")

    st.subheader("5. Medicamentos Mais Distribuidos")
    top_medicamentos_data = get_top_distribui_medicamentos(report_start_date, report_end_date, limit=10)
    if top_medicamentos_data["success"] and top_medicamentos_data["data"]:
        df_top_medicamentos = pd.DataFrame(top_medicamentos_data["data"])
        st.dataframe(df_top_medicamentos, use_container_width=True, hide_index=True)
        st.bar_chart(df_top_medicamentos.set_index("nome_comercial_medicamento"))
    else:
        show_info("Nenhum dado de medicamentos distribuido para o período selecionado.")

    st.markdown("--- ")

    st.subheader("6. Diagnósticos Mais Comuns (CID-10)")
    top_diagnosticos_data = get_top_diagnosticos(report_start_date, report_end_date, limit=10)
    if top_diagnosticos_data["success"] and top_diagnosticos_data["data"]:
        df_top_diagnosticos = pd.DataFrame(top_diagnosticos_data["data"])
        st.dataframe(df_top_diagnosticos, use_container_width=True, hide_index=True)
        st.bar_chart(df_top_diagnosticos.set_index("cid10"))
    else:
        show_info("Nenhum dado de diagnósticos para o período selecionado.")

# --- Navegação Principal --- #
def main():
    st.sidebar.title("Navegação")

    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.write(f"Logado como: {st.session_state.current_user["nome_funcionario"]}")
        if st.sidebar.button("Sair"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun() # Usar st.rerun()

        selection = st.sidebar.radio("Ir para", [
            "Hospitais",
            "Postos de Saúde",
            "Funcionários",
            "Pacientes",
            "Medicamentos",
            "Estoque de Medicamentos",
            "Atendimentos",
            "Prescrições",
            "Distribuição de Medicamentos",
            "Relatórios"
        ])

        if selection == "Hospitais":
            hospital_management_section()
        elif selection == "Postos de Saúde":
            posto_saude_management_section()
        elif selection == "Funcionários":
            funcionario_management_section()
        elif selection == "Pacientes":
            paciente_management_section()
        elif selection == "Medicamentos":
            medicamento_management_section()
        elif selection == "Estoque de Medicamentos":
            estoque_medicamento_management_section()
        elif selection == "Atendimentos":
            atendimento_management_section()
        elif selection == "Prescrições":
            prescricao_management_section()
        elif selection == "Distribuição de Medicamentos":
            distribuicao_medicamento_management_section()
        elif selection == "Relatórios":
            reports_section()

if __name__ == "__main__":
    main()

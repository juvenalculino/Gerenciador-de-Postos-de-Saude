import sqlite3
import bcrypt
from datetime import datetime, date, timedelta

DATABASE_NAME = 'hospital_db.sqlite'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Permite acessar colunas por nome
    return conn

# --- Funções de Hashing de Senha ---

def hash_password(password):
    """Gera o hash de uma senha usando bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(password, hashed_password):
    """Verifica se uma senha corresponde ao hash armazenado."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

# --- Funções CRUD para Hospital ---

def create_hospital(nome, cnpj=None, endereco=None, telefone=None, email=None):
    """Cria um novo registro de hospital no banco de dados."""
    if not nome:
        return {"success": False, "message": "Nome do hospital é obrigatório."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Hospital (nome_hospital, cnpj_hospital, endereco_hospital, telefone_hospital, email_hospital) VALUES (?, ?, ?, ?, ?)",
            (nome, cnpj, endereco, telefone, email)
        )
        conn.commit()
        return {"success": True, "message": "Hospital cadastrado com sucesso!", "id": cursor.lastrowid}
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: Hospital.cnpj_hospital" in str(e):
            return {"success": False, "message": "CNPJ já cadastrado para outro hospital."}
        return {"success": False, "message": f"Erro ao cadastrar hospital: {e}"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {e}"}
    finally:
        conn.close()

def get_all_hospitals(search_term=None):
    """Retorna todos os hospitais cadastrados, com opção de busca por nome ou CNPJ."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM Hospital"
        params = []
        if search_term:
            query += " WHERE nome_hospital LIKE ? OR cnpj_hospital LIKE ?"
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        
        cursor.execute(query, tuple(params))
        hospitais = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in hospitais]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar hospitais: {e}"}
    finally:
        conn.close()

def get_hospital_by_id(hospital_id):
    """Retorna um hospital pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Hospital WHERE id_hospital = ?", (hospital_id,))
        hospital = cursor.fetchone()
        if hospital:
            return {"success": True, "data": dict(hospital)}
        return {"success": False, "message": "Hospital não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar hospital: {e}"}
    finally:
        conn.close()

def update_hospital(hospital_id, nome=None, cnpj=None, endereco=None, telefone=None, email=None):
    """Atualiza um registro de hospital."""
    if not hospital_id:
        return {"success": False, "message": "ID do hospital é obrigatório para atualização."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Construir a query dinamicamente para atualizar apenas os campos fornecidos
        updates = []
        params = []
        if nome is not None: updates.append("nome_hospital = ?"); params.append(nome)
        if cnpj is not None: updates.append("cnpj_hospital = ?"); params.append(cnpj)
        if endereco is not None: updates.append("endereco_hospital = ?"); params.append(endereco)
        if telefone is not None: updates.append("telefone_hospital = ?"); params.append(telefone)
        if email is not None: updates.append("email_hospital = ?"); params.append(email)

        if not updates:
            return {"success": False, "message": "Nenhum campo fornecido para atualização."}

        query = f"UPDATE Hospital SET {', '.join(updates)} WHERE id_hospital = ?"
        params.append(hospital_id)

        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Hospital atualizado com sucesso!"}
        return {"success": False, "message": "Hospital não encontrado ou nenhum dado alterado."}
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: Hospital.cnpj_hospital" in str(e):
            return {"success": False, "message": "CNPJ já cadastrado para outro hospital."}
        return {"success": False, "message": f"Erro ao atualizar hospital: {e}"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {e}"}
    finally:
        conn.close()

def delete_hospital(hospital_id):
    """Deleta um registro de hospital."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar se existem postos de saúde vinculados
        cursor.execute("SELECT COUNT(*) FROM PostoSaude WHERE id_hospital_vinculado = ?", (hospital_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o hospital. Existem postos de saúde vinculados a ele."}

        cursor.execute("DELETE FROM Hospital WHERE id_hospital = ?", (hospital_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Hospital excluído com sucesso!"}
        return {"success": False, "message": "Hospital não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao deletar hospital: {e}"}
    finally:
        conn.close()

# --- Funções CRUD para PostoSaude ---

def create_posto_saude(nome, endereco, id_hospital_vinculado, telefone=None, email=None):
    """Cria um novo registro de posto de saúde."""
    if not all([nome, endereco, id_hospital_vinculado]):
        return {"success": False, "message": "Nome, endereço e hospital vinculado são obrigatórios."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO PostoSaude (nome_posto, endereco_posto, id_hospital_vinculado, telefone_posto, email_posto) VALUES (?, ?, ?, ?, ?)",
            (nome, endereco, id_hospital_vinculado, telefone, email)
        )
        conn.commit()
        return {"success": True, "message": "Posto de saúde cadastrado com sucesso!", "id": cursor.lastrowid}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao cadastrar posto de saúde: {e}"}
    finally:
        conn.close()

def get_all_postos_saude(search_term=None, id_hospital_vinculado=None):
    """Retorna todos os postos de saúde, com opção de busca e filtro por hospital."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT ps.*, h.nome_hospital FROM PostoSaude ps JOIN Hospital h ON ps.id_hospital_vinculado = h.id_hospital WHERE 1=1"""
        params = []
        conditions = []

        if search_term:
            conditions.append("(ps.nome_posto LIKE ? OR ps.endereco_posto LIKE ?)")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        if id_hospital_vinculado:
            conditions.append("ps.id_hospital_vinculado = ?")
            params.append(id_hospital_vinculado)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)

        cursor.execute(query, tuple(params))
        postos = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in postos]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar postos de saúde: {e}"}
    finally:
        conn.close()

def get_posto_saude_by_id(posto_id):
    """Retorna um posto de saúde pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ps.*, h.nome_hospital FROM PostoSaude ps JOIN Hospital h ON ps.id_hospital_vinculado = h.id_hospital WHERE ps.id_posto = ?", (posto_id,))
        posto = cursor.fetchone()
        if posto:
            return {"success": True, "data": dict(posto)}
        return {"success": False, "message": "Posto de saúde não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar posto de saúde: {e}"}
    finally:
        conn.close()

def update_posto_saude(posto_id, nome=None, endereco=None, id_hospital_vinculado=None, telefone=None, email=None):
    """Atualiza um registro de posto de saúde."""
    if not posto_id:
        return {"success": False, "message": "ID do posto de saúde é obrigatório para atualização."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        if nome is not None: updates.append("nome_posto = ?"); params.append(nome)
        if endereco is not None: updates.append("endereco_posto = ?"); params.append(endereco)
        if id_hospital_vinculado is not None: updates.append("id_hospital_vinculado = ?"); params.append(id_hospital_vinculado)
        if telefone is not None: updates.append("telefone_posto = ?"); params.append(telefone)
        if email is not None: updates.append("email_posto = ?"); params.append(email)

        if not updates:
            return {"success": False, "message": "Nenhum campo fornecido para atualização."}

        query = f"UPDATE PostoSaude SET {', '.join(updates)} WHERE id_posto = ?"
        params.append(posto_id)

        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Posto de saúde atualizado com sucesso!"}
        return {"success": False, "message": "Posto de saúde não encontrado ou nenhum dado alterado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao atualizar posto de saúde: {e}"}
    finally:
        conn.close()

def delete_posto_saude(posto_id):
    """Deleta um registro de posto de saúde."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar se existem funcionários, pacientes, atendimentos ou estoque vinculados
        cursor.execute("SELECT COUNT(*) FROM Funcionario WHERE id_posto_lotacao = ?", (posto_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o posto. Existem funcionários vinculados a ele."}
        cursor.execute("SELECT COUNT(*) FROM Paciente WHERE id_posto_referencia = ?", (posto_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o posto. Existem pacientes vinculados a ele."}
        cursor.execute("SELECT COUNT(*) FROM Atendimento WHERE id_posto_atendimento = ?", (posto_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o posto. Existem atendimentos vinculados a ele."}
        cursor.execute("SELECT COUNT(*) FROM EstoqueMedicamentoPosto WHERE id_posto = ?", (posto_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o posto. Existem registros de estoque vinculados a ele."}

        cursor.execute("DELETE FROM PostoSaude WHERE id_posto = ?", (posto_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Posto de saúde excluído com sucesso!"}
        return {"success": False, "message": "Posto de saúde não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao deletar posto de saúde: {e}"}
    finally:
        conn.close()

# --- Funções CRUD para Funcionario ---

def create_funcionario(nome, cpf, cargo, email, senha, id_posto_lotacao, especialidade=None, registro_profissional=None, telefone=None):
    """Cria um novo registro de funcionário."""
    if not all([nome, cpf, cargo, email, senha, id_posto_lotacao]):
        return {"success": False, "message": "Nome, CPF, cargo, email, senha e posto de lotação são obrigatórios."}

    hashed_password = hash_password(senha)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Funcionario (nome_funcionario, cpf_funcionario, cargo_funcionario, email_funcionario, senha_hash, id_posto_lotacao, especialidade_medica, registro_profissional, telefone_funcionario) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nome, cpf, cargo, email, hashed_password, id_posto_lotacao, especialidade, registro_profissional, telefone)
        )
        conn.commit()
        return {"success": True, "message": "Funcionário cadastrado com sucesso!", "id": cursor.lastrowid}
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: Funcionario.cpf_funcionario" in str(e):
            return {"success": False, "message": "CPF já cadastrado para outro funcionário."}
        if "UNIQUE constraint failed: Funcionario.email_funcionario" in str(e):
            return {"success": False, "message": "E-mail já cadastrado para outro funcionário."}
        return {"success": False, "message": f"Erro ao cadastrar funcionário: {e}"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {e}"}
    finally:
        conn.close()

def get_all_funcionarios(search_term=None, cargo=None, id_posto_lotacao=None):
    """Retorna todos os funcionários, com opção de busca e filtros."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT f.*, ps.nome_posto FROM Funcionario f JOIN PostoSaude ps ON f.id_posto_lotacao = ps.id_posto WHERE 1=1"""
        params = []
        conditions = []

        if search_term:
            conditions.append("(f.nome_funcionario LIKE ? OR f.cpf_funcionario LIKE ? OR f.email_funcionario LIKE ?)")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        if cargo:
            conditions.append("f.cargo_funcionario = ?")
            params.append(cargo)
        if id_posto_lotacao:
            conditions.append("f.id_posto_lotacao = ?")
            params.append(id_posto_lotacao)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)

        cursor.execute(query, tuple(params))
        funcionarios = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in funcionarios]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar funcionários: {e}"}
    finally:
        conn.close()

def get_funcionario_by_id(funcionario_id):
    """Retorna um funcionário pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT f.*, ps.nome_posto FROM Funcionario f JOIN PostoSaude ps ON f.id_posto_lotacao = ps.id_posto WHERE f.id_funcionario = ?", (funcionario_id,))
        funcionario = cursor.fetchone()
        if funcionario:
            return {"success": True, "data": dict(funcionario)}
        return {"success": False, "message": "Funcionário não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar funcionário: {e}"}
    finally:
        conn.close()

def get_funcionario_by_email(email):
    """Retorna um funcionário pelo email (para login)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Funcionario WHERE email_funcionario = ?", (email,))
        funcionario = cursor.fetchone()
        if funcionario:
            return {"success": True, "data": dict(funcionario)}
        return {"success": False, "message": "Funcionário não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar funcionário por email: {e}"}
    finally:
        conn.close()

def update_funcionario(funcionario_id, nome=None, cpf=None, cargo=None, especialidade=None, registro_profissional=None, telefone=None, email=None, senha=None, id_posto_lotacao=None):
    """Atualiza um registro de funcionário."""
    if not funcionario_id:
        return {"success": False, "message": "ID do funcionário é obrigatório para atualização."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        if nome is not None: updates.append("nome_funcionario = ?"); params.append(nome)
        if cpf is not None: updates.append("cpf_funcionario = ?"); params.append(cpf)
        if cargo is not None: updates.append("cargo_funcionario = ?"); params.append(cargo)
        if especialidade is not None: updates.append("especialidade_medica = ?"); params.append(especialidade)
        if registro_profissional is not None: updates.append("registro_profissional = ?"); params.append(registro_profissional)
        if telefone is not None: updates.append("telefone_funcionario = ?"); params.append(telefone)
        if email is not None: updates.append("email_funcionario = ?"); params.append(email)
        if senha is not None: updates.append("senha_hash = ?"); params.append(hash_password(senha))
        if id_posto_lotacao is not None: updates.append("id_posto_lotacao = ?"); params.append(id_posto_lotacao)

        if not updates:
            return {"success": False, "message": "Nenhum campo fornecido para atualização."}

        query = f"UPDATE Funcionario SET {', '.join(updates)} WHERE id_funcionario = ?"
        params.append(funcionario_id)

        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Funcionário atualizado com sucesso!"}
        return {"success": False, "message": "Funcionário não encontrado ou nenhum dado alterado."}
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: Funcionario.cpf_funcionario" in str(e):
            return {"success": False, "message": "CPF já cadastrado para outro funcionário."}
        if "UNIQUE constraint failed: Funcionario.email_funcionario" in str(e):
            return {"success": False, "message": "E-mail já cadastrado para outro funcionário."}
        return {"success": False, "message": f"Erro ao atualizar funcionário: {e}"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {e}"}
    finally:
        conn.close()

def delete_funcionario(funcionario_id):
    """Deleta um registro de funcionário."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar se existem atendimentos ou distribuições vinculadas
        cursor.execute("SELECT COUNT(*) FROM Atendimento WHERE id_funcionario_responsavel = ?", (funcionario_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o funcionário. Existem atendimentos vinculados a ele."}
        cursor.execute("SELECT COUNT(*) FROM DistribuicaoMedicamento WHERE id_funcionario_distribuidor = ?", (funcionario_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o funcionário. Existem distribuições de medicamento vinculadas a ele."}

        cursor.execute("DELETE FROM Funcionario WHERE id_funcionario = ?", (funcionario_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Funcionário excluído com sucesso!"}
        return {"success": False, "message": "Funcionário não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao deletar funcionário: {e}"}
    finally:
        conn.close()

# --- Funções CRUD para Paciente ---

def create_paciente(nome, cpf, data_nascimento, genero, endereco, id_posto_referencia, cartao_sus=None, telefone=None, email=None):
    """Cria um novo registro de paciente."""
    if not all([nome, cpf, data_nascimento, genero, endereco, id_posto_referencia]):
        return {"success": False, "message": "Nome, CPF, data de nascimento, gênero, endereço e posto de referência são obrigatórios."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Paciente (nome_paciente, cpf_paciente, cartao_sus, data_nascimento_paciente, genero_paciente, endereco_paciente, telefone_paciente, email_paciente, id_posto_referencia) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (nome, cpf, cartao_sus, data_nascimento, genero, endereco, telefone, email, id_posto_referencia)
        )
        conn.commit()
        return {"success": True, "message": "Paciente cadastrado com sucesso!", "id": cursor.lastrowid}
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: Paciente.cpf_paciente" in str(e):
            return {"success": False, "message": "CPF já cadastrado para outro paciente."}
        if "UNIQUE constraint failed: Paciente.cartao_sus" in str(e):
            return {"success": False, "message": "Cartão SUS já cadastrado para outro paciente."}
        return {"success": False, "message": f"Erro ao cadastrar paciente: {e}"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {e}"}
    finally:
        conn.close()

def get_all_pacientes(search_term=None, genero=None, id_posto_referencia=None):
    """Retorna todos os pacientes, com opção de busca e filtros."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT p.*, ps.nome_posto FROM Paciente p JOIN PostoSaude ps ON p.id_posto_referencia = ps.id_posto WHERE 1=1"""
        params = []
        conditions = []

        if search_term:
            conditions.append("(p.nome_paciente LIKE ? OR p.cpf_paciente LIKE ? OR p.cartao_sus LIKE ?)")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        if genero:
            conditions.append("p.genero_paciente = ?")
            params.append(genero)
        if id_posto_referencia:
            conditions.append("p.id_posto_referencia = ?")
            params.append(id_posto_referencia)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)

        cursor.execute(query, tuple(params))
        pacientes = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in pacientes]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar pacientes: {e}"}
    finally:
        conn.close()

def get_paciente_by_id(paciente_id):
    """Retorna um paciente pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT p.*, ps.nome_posto FROM Paciente p JOIN PostoSaude ps ON p.id_posto_referencia = ps.id_posto WHERE p.id_paciente = ?", (paciente_id,))
        paciente = cursor.fetchone()
        if paciente:
            return {"success": True, "data": dict(paciente)}
        return {"success": False, "message": "Paciente não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar paciente: {e}"}
    finally:
        conn.close()

def update_paciente(paciente_id, nome=None, cpf=None, cartao_sus=None, data_nascimento=None, genero=None, endereco=None, telefone=None, email=None, id_posto_referencia=None):
    """Atualiza um registro de paciente."""
    if not paciente_id:
        return {"success": False, "message": "ID do paciente é obrigatório para atualização."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        if nome is not None: updates.append("nome_paciente = ?"); params.append(nome)
        if cpf is not None: updates.append("cpf_paciente = ?"); params.append(cpf)
        if cartao_sus is not None: updates.append("cartao_sus = ?"); params.append(cartao_sus)
        if data_nascimento is not None: updates.append("data_nascimento_paciente = ?"); params.append(data_nascimento)
        if genero is not None: updates.append("genero_paciente = ?"); params.append(genero)
        if endereco is not None: updates.append("endereco_paciente = ?"); params.append(endereco)
        if telefone is not None: updates.append("telefone_paciente = ?"); params.append(telefone)
        if email is not None: updates.append("email_paciente = ?"); params.append(email)
        if id_posto_referencia is not None: updates.append("id_posto_referencia = ?"); params.append(id_posto_referencia)

        if not updates:
            return {"success": False, "message": "Nenhum campo fornecido para atualização."}

        query = f"UPDATE Paciente SET {', '.join(updates)} WHERE id_paciente = ?"
        params.append(paciente_id)

        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Paciente atualizado com sucesso!"}
        return {"success": False, "message": "Paciente não encontrado ou nenhum dado alterado."}
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: Paciente.cpf_paciente" in str(e):
            return {"success": False, "message": "CPF já cadastrado para outro paciente."}
        if "UNIQUE constraint failed: Paciente.cartao_sus" in str(e):
            return {"success": False, "message": "Cartão SUS já cadastrado para outro paciente."}
        return {"success": False, "message": f"Erro ao atualizar paciente: {e}"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {e}"}
    finally:
        conn.close()

def delete_paciente(paciente_id):
    """Deleta um registro de paciente."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar se existem atendimentos vinculados
        cursor.execute("SELECT COUNT(*) FROM Atendimento WHERE id_paciente = ?", (paciente_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o paciente. Existem atendimentos vinculados a ele."}

        cursor.execute("DELETE FROM Paciente WHERE id_paciente = ?", (paciente_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Paciente excluído com sucesso!"}
        return {"success": False, "message": "Paciente não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao deletar paciente: {e}"}
    finally:
        conn.close()

# --- Funções CRUD para Medicamento ---

def create_medicamento(nome_comercial, principio_ativo, apresentacao=None, fabricante=None, tipo_medicamento=None):
    """Cria um novo registro de medicamento."""
    if not all([nome_comercial, principio_ativo]):
        return {"success": False, "message": "Nome comercial e princípio ativo são obrigatórios."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Medicamento (nome_comercial_medicamento, principio_ativo, apresentacao, fabricante, tipo_medicamento) VALUES (?, ?, ?, ?, ?)",
            (nome_comercial, principio_ativo, apresentacao, fabricante, tipo_medicamento)
        )
        conn.commit()
        return {"success": True, "message": "Medicamento cadastrado com sucesso!", "id": cursor.lastrowid}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao cadastrar medicamento: {e}"}
    finally:
        conn.close()

def get_all_medicamentos(search_term=None, tipo_medicamento=None):
    """Retorna todos os medicamentos, com opção de busca e filtro por tipo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM Medicamento WHERE 1=1"
        params = []
        conditions = []

        if search_term:
            conditions.append("(nome_comercial_medicamento LIKE ? OR principio_ativo LIKE ?)")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        if tipo_medicamento:
            conditions.append("tipo_medicamento = ?")
            params.append(tipo_medicamento)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)

        cursor.execute(query, tuple(params))
        medicamentos = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in medicamentos]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar medicamentos: {e}"}
    finally:
        conn.close()

def get_medicamento_by_id(medicamento_id):
    """Retorna um medicamento pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Medicamento WHERE id_medicamento = ?", (medicamento_id,))
        medicamento = cursor.fetchone()
        if medicamento:
            return {"success": True, "data": dict(medicamento)}
        return {"success": False, "message": "Medicamento não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar medicamento: {e}"}
    finally:
        conn.close()

def update_medicamento(medicamento_id, nome_comercial=None, principio_ativo=None, apresentacao=None, fabricante=None, tipo_medicamento=None):
    """Atualiza um registro de medicamento."""
    if not medicamento_id:
        return {"success": False, "message": "ID do medicamento é obrigatório para atualização."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        if nome_comercial is not None: updates.append("nome_comercial_medicamento = ?"); params.append(nome_comercial)
        if principio_ativo is not None: updates.append("principio_ativo = ?"); params.append(principio_ativo)
        if apresentacao is not None: updates.append("apresentacao = ?"); params.append(apresentacao)
        if fabricante is not None: updates.append("fabricante = ?"); params.append(fabricante)
        if tipo_medicamento is not None: updates.append("tipo_medicamento = ?"); params.append(tipo_medicamento)

        if not updates:
            return {"success": False, "message": "Nenhum campo fornecido para atualização."}

        query = f"UPDATE Medicamento SET {', '.join(updates)} WHERE id_medicamento = ?"
        params.append(medicamento_id)

        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Medicamento atualizado com sucesso!"}
        return {"success": False, "message": "Medicamento não encontrado ou nenhum dado alterado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao atualizar medicamento: {e}"}
    finally:
        conn.close()

def delete_medicamento(medicamento_id):
    """Deleta um registro de medicamento."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar se existem registros de estoque vinculados
        cursor.execute("SELECT COUNT(*) FROM EstoqueMedicamentoPosto WHERE id_medicamento = ?", (medicamento_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o medicamento. Existem registros de estoque vinculados a ele."}

        cursor.execute("DELETE FROM Medicamento WHERE id_medicamento = ?", (medicamento_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Medicamento excluído com sucesso!"}
        return {"success": False, "message": "Medicamento não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao deletar medicamento: {e}"}
    finally:
        conn.close()

# --- Funções CRUD para EstoqueMedicamentoPosto ---

def create_estoque_medicamento_posto(id_medicamento, id_posto, lote, data_validade, quantidade_atual, quantidade_minima_alerta=0):
    """Cria um novo registro de estoque de medicamento por posto."""
    if not all([id_medicamento, id_posto, lote, data_validade, quantidade_atual is not None]):
        return {"success": False, "message": "Medicamento, posto, lote, data de validade e quantidade atual são obrigatórios."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO EstoqueMedicamentoPosto (id_medicamento, id_posto, lote, data_validade, quantidade_atual, quantidade_minima_alerta) VALUES (?, ?, ?, ?, ?, ?)",
            (id_medicamento, id_posto, lote, data_validade, quantidade_atual, quantidade_minima_alerta)
        )
        conn.commit()
        return {"success": True, "message": "Estoque de medicamento cadastrado com sucesso!", "id": cursor.lastrowid}
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: EstoqueMedicamentoPosto.id_medicamento, EstoqueMedicamentoPosto.id_posto, EstoqueMedicamentoPosto.lote" in str(e):
            return {"success": False, "message": "Já existe um registro de estoque para este medicamento, posto e lote. Considere atualizar o registro existente."}
        return {"success": False, "message": f"Erro ao cadastrar estoque de medicamento: {e}"}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro de banco de dados: {e}"}
    finally:
        conn.close()

def get_all_estoque_medicamento_posto(search_term=None, id_medicamento=None, id_posto=None, validade_proxima_dias=None, estoque_baixo=False):
    """Retorna todos os registros de estoque de medicamento por posto, com opções de busca e filtros."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT emp.*, m.nome_comercial_medicamento, m.principio_ativo, ps.nome_posto
            FROM EstoqueMedicamentoPosto emp
            JOIN Medicamento m ON emp.id_medicamento = m.id_medicamento
            JOIN PostoSaude ps ON emp.id_posto = ps.id_posto
            WHERE 1=1
            """
        params = []
        conditions = []

        if search_term:
            conditions.append("(m.nome_comercial_medicamento LIKE ? OR emp.lote LIKE ?)")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        if id_medicamento:
            conditions.append("emp.id_medicamento = ?")
            params.append(id_medicamento)
        if id_posto:
            conditions.append("emp.id_posto = ?")
            params.append(id_posto)
        if validade_proxima_dias is not None and validade_proxima_dias > 0:
            # Calcula a data limite para validade próxima
            future_date = date.today() + timedelta(days=validade_proxima_dias)
            conditions.append("emp.data_validade <= ?")
            params.append(future_date.strftime("%Y-%m-%d"))
        if estoque_baixo:
            conditions.append("emp.quantidade_atual <= emp.quantidade_minima_alerta")
        
        if conditions:
            query += " AND " + " AND ".join(conditions)

        cursor.execute(query, tuple(params))
        estoque = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in estoque]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar estoque de medicamento: {e}"}
    finally:
        conn.close()

def get_estoque_medicamento_posto_by_id(estoque_id):
    """Retorna um registro de estoque de medicamento por posto pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT emp.*, m.nome_comercial_medicamento, m.principio_ativo, ps.nome_posto FROM EstoqueMedicamentoPosto emp JOIN Medicamento m ON emp.id_medicamento = m.id_medicamento JOIN PostoSaude ps ON emp.id_posto = ps.id_posto WHERE emp.id_estoque = ?", (estoque_id,))
        estoque = cursor.fetchone()
        if estoque:
            return {"success": True, "data": dict(estoque)}
        return {"success": False, "message": "Registro de estoque não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar registro de estoque: {e}"}
    finally:
        conn.close()

def update_estoque_medicamento_posto(estoque_id, quantidade_atual=None, quantidade_minima_alerta=None, lote=None, data_validade=None):
    """Atualiza um registro de estoque de medicamento por posto."""
    if not estoque_id:
        return {"success": False, "message": "ID do estoque é obrigatório para atualização."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        if quantidade_atual is not None: updates.append("quantidade_atual = ?"); params.append(quantidade_atual)
        if quantidade_minima_alerta is not None: updates.append("quantidade_minima_alerta = ?"); params.append(quantidade_minima_alerta)
        if lote is not None: updates.append("lote = ?"); params.append(lote)
        if data_validade is not None: updates.append("data_validade = ?"); params.append(data_validade)

        if not updates:
            return {"success": False, "message": "Nenhum campo fornecido para atualização."}

        query = f"UPDATE EstoqueMedicamentoPosto SET {', '.join(updates)} WHERE id_estoque = ?"
        params.append(estoque_id)

        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Estoque de medicamento atualizado com sucesso!"}
        return {"success": False, "message": "Registro de estoque não encontrado ou nenhum dado alterado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao atualizar estoque de medicamento: {e}"}
    finally:
        conn.close()

def delete_estoque_medicamento_posto(estoque_id):
    """Deleta um registro de estoque de medicamento por posto."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar se existem prescrições vinculadas a este item de estoque
        cursor.execute("SELECT COUNT(*) FROM Prescricao WHERE id_medicamento_estoque = ?", (estoque_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o registro de estoque. Existem prescrições vinculadas a ele."}

        cursor.execute("DELETE FROM EstoqueMedicamentoPosto WHERE id_estoque = ?", (estoque_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Registro de estoque excluído com sucesso!"}
        return {"success": False, "message": "Registro de estoque não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao deletar registro de estoque: {e}"}
    finally:
        conn.close()

# --- Funções CRUD para Atendimento ---

def create_atendimento(id_paciente, id_funcionario_responsavel, id_posto_atendimento, tipo_atendimento, descricao_sintomas_queixa, data_hora_inicio=None, data_hora_fim=None, diagnostico=None, cid10=None, grau_doenca_observado=None, observacoes_gerais=None):
    """Cria um novo registro de atendimento no banco de dados."""
    if not all([id_paciente, id_funcionario_responsavel, id_posto_atendimento, tipo_atendimento, descricao_sintomas_queixa]):
        return {"success": False, "message": "Paciente, funcionário, posto, tipo e descrição dos sintomas são obrigatórios."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Define data_hora_inicio se não for fornecida
        if data_hora_inicio is None:
            data_hora_inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO Atendimento (id_paciente, id_funcionario_responsavel, id_posto_atendimento, data_hora_inicio_atendimento, data_hora_fim_atendimento, tipo_atendimento, descricao_sintomas_queixa, diagnostico, cid10, grau_doenca_observado, observacoes_gerais) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (id_paciente, id_funcionario_responsavel, id_posto_atendimento, data_hora_inicio, data_hora_fim, tipo_atendimento, descricao_sintomas_queixa, diagnostico, cid10, grau_doenca_observado, observacoes_gerais)
        )
        conn.commit()
        return {"success": True, "message": "Atendimento registrado com sucesso!", "id": cursor.lastrowid}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao registrar atendimento: {e}"}
    finally:
        conn.close()

def get_all_atendimentos(search_term=None, id_paciente=None, id_funcionario=None, id_posto=None, tipo_atendimento=None, cid10=None, grau_doenca=None, start_date=None, end_date=None):
    """Retorna todos os atendimentos, com opções de busca e filtros."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT a.*, p.nome_paciente, f.nome_funcionario, ps.nome_posto
            FROM Atendimento a
            JOIN Paciente p ON a.id_paciente = p.id_paciente
            JOIN Funcionario f ON a.id_funcionario_responsavel = f.id_funcionario
            JOIN PostoSaude ps ON a.id_posto_atendimento = ps.id_posto
            WHERE 1=1
            """
        params = []
        conditions = []

        if search_term:
            conditions.append("(p.nome_paciente LIKE ? OR f.nome_funcionario LIKE ? OR a.descricao_sintomas_queixa LIKE ? OR a.diagnostico LIKE ?)")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        if id_paciente:
            conditions.append("a.id_paciente = ?")
            params.append(id_paciente)
        if id_funcionario:
            conditions.append("a.id_funcionario_responsavel = ?")
            params.append(id_funcionario)
        if id_posto:
            conditions.append("a.id_posto_atendimento = ?")
            params.append(id_posto)
        if tipo_atendimento:
            conditions.append("a.tipo_atendimento = ?")
            params.append(tipo_atendimento)
        if cid10:
            conditions.append("a.cid10 LIKE ?")
            params.append(f"%{cid10}%")
        if grau_doenca:
            conditions.append("a.grau_doenca_observado = ?")
            params.append(grau_doenca)
        if start_date:
            conditions.append("DATE(a.data_hora_inicio_atendimento) >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("DATE(a.data_hora_inicio_atendimento) <= ?")
            params.append(end_date)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)

        query += " ORDER BY a.data_hora_inicio_atendimento DESC"

        cursor.execute(query, tuple(params))
        atendimentos = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in atendimentos]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar atendimentos: {e}"}
    finally:
        conn.close()

def get_atendimento_by_id(atendimento_id):
    """Retorna um atendimento pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT a.*, p.nome_paciente, f.nome_funcionario, ps.nome_posto
            FROM Atendimento a
            JOIN Paciente p ON a.id_paciente = p.id_paciente
            JOIN Funcionario f ON a.id_funcionario_responsavel = f.id_funcionario
            JOIN PostoSaude ps ON a.id_posto_atendimento = ps.id_posto
            WHERE a.id_atendimento = ?"""
        cursor.execute(query, (atendimento_id,))
        atendimento = cursor.fetchone()
        if atendimento:
            return {"success": True, "data": dict(atendimento)}
        return {"success": False, "message": "Atendimento não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar atendimento: {e}"}
    finally:
        conn.close()

def update_atendimento(atendimento_id, id_paciente=None, id_funcionario_responsavel=None, id_posto_atendimento=None, data_hora_inicio=None, data_hora_fim=None, tipo_atendimento=None, descricao_sintomas_queixa=None, diagnostico=None, cid10=None, grau_doenca=None, observacoes_gerais=None):
    """Atualiza um registro de atendimento."""
    if not atendimento_id:
        return {"success": False, "message": "ID do atendimento é obrigatório para atualização."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        if id_paciente is not None: updates.append("id_paciente = ?"); params.append(id_paciente)
        if id_funcionario_responsavel is not None: updates.append("id_funcionario_responsavel = ?"); params.append(id_funcionario_responsavel)
        if id_posto_atendimento is not None: updates.append("id_posto_atendimento = ?"); params.append(id_posto_atendimento)
        if data_hora_inicio is not None: updates.append("data_hora_inicio_atendimento = ?"); params.append(data_hora_inicio)
        if data_hora_fim is not None: updates.append("data_hora_fim_atendimento = ?"); params.append(data_hora_fim)
        if tipo_atendimento is not None: updates.append("tipo_atendimento = ?"); params.append(tipo_atendimento)
        if descricao_sintomas_queixa is not None: updates.append("descricao_sintomas_queixa = ?"); params.append(descricao_sintomas_queixa)
        if diagnostico is not None: updates.append("diagnostico = ?"); params.append(diagnostico)
        if cid10 is not None: updates.append("cid10 = ?"); params.append(cid10)
        if grau_doenca is not None: updates.append("grau_doenca_observado = ?"); params.append(grau_doenca)
        if observacoes_gerais is not None: updates.append("observacoes_gerais = ?"); params.append(observacoes_gerais)

        if not updates:
            return {"success": False, "message": "Nenhum campo fornecido para atualização."}

        query = f"UPDATE Atendimento SET {', '.join(updates)} WHERE id_atendimento = ?"
        params.append(atendimento_id)

        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Atendimento atualizado com sucesso!"}
        return {"success": False, "message": "Atendimento não encontrado ou nenhum dado alterado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao atualizar atendimento: {e}"}
    finally:
        conn.close()

def delete_atendimento(atendimento_id):
    """Deleta um registro de atendimento."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar se existem prescrições vinculadas
        cursor.execute("SELECT COUNT(*) FROM Prescricao WHERE id_atendimento = ?", (atendimento_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir o atendimento. Existem prescrições vinculadas a ele."}

        cursor.execute("DELETE FROM Atendimento WHERE id_atendimento = ?", (atendimento_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Atendimento excluído com sucesso!"}
        return {"success": False, "message": "Atendimento não encontrado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao deletar atendimento: {e}"}
    finally:
        conn.close()

# --- Funções CRUD para Prescricao ---

def create_prescricao(id_atendimento, id_medicamento_estoque, posologia, quantidade_prescrita):
    """Cria um novo registro de prescrição."""
    if not all([id_atendimento, id_medicamento_estoque, posologia, quantidade_prescrita is not None]):
        return {"success": False, "message": "Atendimento, medicamento em estoque, posologia e quantidade prescrita são obrigatórios."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Prescricao (id_atendimento, id_medicamento_estoque, posologia, quantidade_prescrita) VALUES (?, ?, ?, ?)",
            (id_atendimento, id_medicamento_estoque, posologia, quantidade_prescrita)
        )
        conn.commit()
        return {"success": True, "message": "Prescrição registrada com sucesso!", "id": cursor.lastrowid}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao registrar prescrição: {e}"}
    finally:
        conn.close()

def get_all_prescricoes(search_term=None, id_atendimento=None, id_medicamento=None, status_distribuicao=None):
    """Retorna todas as prescrições, com opções de busca e filtros."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT pr.*, a.data_hora_inicio_atendimento, p.nome_paciente, m.nome_comercial_medicamento, emp.lote, emp.quantidade_atual as estoque_atual, ps.nome_posto
            FROM Prescricao pr
            JOIN Atendimento a ON pr.id_atendimento = a.id_atendimento
            JOIN Paciente p ON a.id_paciente = p.id_paciente
            JOIN EstoqueMedicamentoPosto emp ON pr.id_medicamento_estoque = emp.id_estoque
            JOIN Medicamento m ON emp.id_medicamento = m.id_medicamento
            JOIN PostoSaude ps ON emp.id_posto = ps.id_posto
            WHERE 1=1
            """
        params = []
        conditions = []

        if search_term:
            conditions.append("(p.nome_paciente LIKE ? OR m.nome_comercial_medicamento LIKE ? OR pr.posologia LIKE ?)")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        if id_atendimento:
            conditions.append("pr.id_atendimento = ?")
            params.append(id_atendimento)
        if id_medicamento:
            conditions.append("m.id_medicamento = ?")
            params.append(id_medicamento)
        if status_distribuicao:
            conditions.append("pr.status_distribuicao = ?")
            params.append(status_distribuicao)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)

        query += " ORDER BY pr.data_hora_prescricao DESC"

        cursor.execute(query, tuple(params))
        prescricoes = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in prescricoes]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar prescrições: {e}"}
    finally:
        conn.close()

def get_prescricao_by_id(prescricao_id):
    """Retorna uma prescrição pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT pr.*, a.data_hora_inicio_atendimento, p.nome_paciente, m.nome_comercial_medicamento, emp.lote, emp.quantidade_atual as estoque_atual, ps.nome_posto
            FROM Prescricao pr
            JOIN Atendimento a ON pr.id_atendimento = a.id_atendimento
            JOIN Paciente p ON a.id_paciente = p.id_paciente
            JOIN EstoqueMedicamentoPosto emp ON pr.id_medicamento_estoque = emp.id_estoque
            JOIN Medicamento m ON emp.id_medicamento = m.id_medicamento
            JOIN PostoSaude ps ON emp.id_posto = ps.id_posto
            WHERE pr.id_prescricao = ?"""
        cursor.execute(query, (prescricao_id,))
        prescricao = cursor.fetchone()
        if prescricao:
            return {"success": True, "data": dict(prescricao)}
        return {"success": False, "message": "Prescrição não encontrada."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar prescrição: {e}"}
    finally:
        conn.close()

def update_prescricao(prescricao_id, id_atendimento=None, id_medicamento_estoque=None, posologia=None, quantidade_prescrita=None, status_distribuicao=None):
    """Atualiza um registro de prescrição."""
    if not prescricao_id:
        return {"success": False, "message": "ID da prescrição é obrigatório para atualização."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updates = []
        params = []
        if id_atendimento is not None: updates.append("id_atendimento = ?"); params.append(id_atendimento)
        if id_medicamento_estoque is not None: updates.append("id_medicamento_estoque = ?"); params.append(id_medicamento_estoque)
        if posologia is not None: updates.append("posologia = ?"); params.append(posologia)
        if quantidade_prescrita is not None: updates.append("quantidade_prescrita = ?"); params.append(quantidade_prescrita)
        if status_distribuicao is not None: updates.append("status_distribuicao = ?"); params.append(status_distribuicao)

        if not updates:
            return {"success": False, "message": "Nenhum campo fornecido para atualização."}

        query = f"UPDATE Prescricao SET {', '.join(updates)} WHERE id_prescricao = ?"
        params.append(prescricao_id)

        cursor.execute(query, tuple(params))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Prescrição atualizada com sucesso!"}
        return {"success": False, "message": "Prescrição não encontrada ou nenhum dado alterado."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao atualizar prescrição: {e}"}
    finally:
        conn.close()

def delete_prescricao(prescricao_id):
    """Deleta um registro de prescrição."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar se existem distribuições vinculadas
        cursor.execute("SELECT COUNT(*) FROM DistribuicaoMedicamento WHERE id_prescricao = ?", (prescricao_id,))
        if cursor.fetchone()[0] > 0:
            return {"success": False, "message": "Não é possível excluir a prescrição. Existem distribuições de medicamento vinculadas a ela."}

        cursor.execute("DELETE FROM Prescricao WHERE id_prescricao = ?", (prescricao_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return {"success": True, "message": "Prescrição excluída com sucesso!"}
        return {"success": False, "message": "Prescrição não encontrada."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao deletar prescrição: {e}"}
    finally:
        conn.close()

# --- Funções CRUD para distribuicaoMedicamento ---

def create_distribuicao_medicamento(id_prescricao, id_funcionario_distribuidor, quantidade_distribuida, observacao=None):
    """Cria um novo registro de distribuição de medicamento e atualiza o estoque e status da prescrição."""
    if not all([id_prescricao, id_funcionario_distribuidor, quantidade_distribuida is not None]):
        return {"success": False, "message": "Prescrição, funcionário distribuidor e quantidade distribuida são obrigatórios."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Obter informações da prescrição e do estoque
        prescricao_info = get_prescricao_by_id(id_prescricao)
        if not prescricao_info["success"]:
            return {"success": False, "message": "Prescrição não encontrada."}
        prescricao = prescricao_info["data"]

        estoque_info = get_estoque_medicamento_posto_by_id(prescricao["id_medicamento_estoque"])
        if not estoque_info["success"]:
            return {"success": False, "message": "Estoque do medicamento da prescrição não encontrado."}
        estoque = estoque_info["data"]

        # 2. Validar quantidade
        if quantidade_distribuida <= 0:
            return {"success": False, "message": "Quantidade a distribuir deve ser maior que zero."}
        if quantidade_distribuida > estoque["quantidade_atual"]:
            return {"success": False, "message": "Quantidade a distribuir excede o estoque disponível."}
        
        # Calcular quantidade já distribuida para esta prescrição
        cursor.execute("SELECT SUM(quantidade_distribuida) FROM DistribuicaoMedicamento WHERE id_prescricao = ?", (id_prescricao,))
        total_distribuido_anteriormente = cursor.fetchone()[0] or 0
        
        quantidade_restante_prescricao = prescricao["quantidade_prescrita"] - total_distribuido_anteriormente

        if quantidade_distribuida > quantidade_restante_prescricao:
            return {"success": False, "message": f"Quantidade a distribuir excede a quantidade restante na prescrição ({quantidade_restante_prescricao})."}

        # 3. Registrar a distribuição
        cursor.execute(
            "INSERT INTO DistribuicaoMedicamento (id_prescricao, id_funcionario_distribuidor, quantidade_distribuida, observacao) VALUES (?, ?, ?, ?)",
            (id_prescricao, id_funcionario_distribuidor, quantidade_distribuida, observacao)
        )

        # 4. Atualizar o estoque
        nova_quantidade_estoque = estoque["quantidade_atual"] - quantidade_distribuida
        cursor.execute("UPDATE EstoqueMedicamentoPosto SET quantidade_atual = ? WHERE id_estoque = ?",
                       (nova_quantidade_estoque, estoque["id_estoque"]))

        # 5. Atualizar o status da prescrição
        novo_total_distribuido = total_distribuido_anteriormente + quantidade_distribuida
        if novo_total_distribuido == prescricao["quantidade_prescrita"]:
            novo_status_prescricao = "Distribuido Totalmente"
        elif novo_total_distribuido > 0 and novo_total_distribuido < prescricao["quantidade_prescrita"]:
            novo_status_prescricao = "Distribuido Parcialmente"
        else:
            novo_status_prescricao = "Pendente" # Caso a quantidade distribuida seja 0 ou negativa, o que já foi validado

        cursor.execute("UPDATE Prescricao SET status_distribuicao = ? WHERE id_prescricao = ?",
                       (novo_status_prescricao, id_prescricao))

        conn.commit()
        return {"success": True, "message": "Distribuição registrada e estoque/prescrição atualizados com sucesso!", "id": cursor.lastrowid}
    except sqlite3.Error as e:
        conn.rollback() # Em caso de erro, desfaz todas as operações
        return {"success": False, "message": f"Erro ao registrar distribuição: {e}"}
    finally:
        conn.close()

def get_all_distribuicoes_medicamento(search_term=None, id_prescricao=None, id_funcionario_distribuidor=None, start_date=None, end_date=None):
    """Retorna todas as distribuição de medicamento, com opções de busca e filtros."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT dm.*, pr.quantidade_prescrita, pr.posologia, p.nome_paciente, f.nome_funcionario, m.nome_comercial_medicamento, emp.lote, ps.nome_posto
            FROM DistribuicaoMedicamento dm
            JOIN Prescricao pr ON dm.id_prescricao = pr.id_prescricao
            JOIN Atendimento a ON pr.id_atendimento = a.id_atendimento
            JOIN Paciente p ON a.id_paciente = p.id_paciente
            JOIN Funcionario f ON dm.id_funcionario_distribuidor = f.id_funcionario
            JOIN EstoqueMedicamentoPosto emp ON pr.id_medicamento_estoque = emp.id_estoque
            JOIN Medicamento m ON emp.id_medicamento = m.id_medicamento
            JOIN PostoSaude ps ON emp.id_posto = ps.id_posto
            WHERE 1=1
            """
        params = []
        conditions = []

        if search_term:
            conditions.append("(p.nome_paciente LIKE ? OR m.nome_comercial_medicamento LIKE ? OR f.nome_funcionario LIKE ?)")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
            params.append(f"%{search_term}%")
        if id_prescricao:
            conditions.append("dm.id_prescricao = ?")
            params.append(id_prescricao)
        if id_funcionario_distribuidor:
            conditions.append("dm.id_funcionario_distribuidor = ?")
            params.append(id_funcionario_distribuidor)
        if start_date:
            conditions.append("DATE(dm.data_hora_distribuicao) >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("DATE(dm.data_hora_distribuicao) <= ?")
            params.append(end_date)
        
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        query += " ORDER BY dm.data_hora_distribuicao DESC"

        cursor.execute(query, tuple(params))
        distribuicao = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in distribuicao]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar distribuições de medicamento: {e}"}
    finally:
        conn.close()

def get_distribuicao_medicamento_by_id(distribuicao_id):
    """Retorna uma distribuição de medicamento pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT dm.*, pr.quantidade_prescrita, pr.posologia, p.nome_paciente, f.nome_funcionario, m.nome_comercial_medicamento, emp.lote, ps.nome_posto
            FROM DistribuicaoMedicamento dm
            JOIN Prescricao pr ON dm.id_prescricao = pr.id_prescricao
            JOIN Atendimento a ON pr.id_atendimento = a.id_atendimento
            JOIN Paciente p ON a.id_paciente = p.id_paciente
            JOIN Funcionario f ON dm.id_funcionario_distribuidor = f.id_funcionario
            JOIN EstoqueMedicamentoPosto emp ON pr.id_medicamento_estoque = emp.id_estoque
            JOIN Medicamento m ON emp.id_medicamento = m.id_medicamento
            JOIN PostoSaude ps ON emp.id_posto = ps.id_posto
            WHERE dm.id_distribuicao = ?"""
        cursor.execute(query, (distribuicao_id,))
        distribuicao = cursor.fetchone()
        if distribuicao:
            return {"success": True, "data": dict(distribuicao)}
        return {"success": False, "message": "distribuição de medicamento não encontrada."}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar distribuição de medicamento: {e}"}
    finally:
        conn.close()

# --- Funções de Relatório ---

def get_atendimentos_by_type(start_date=None, end_date=None):
    """Retorna a contagem de atendimentos por tipo em um período específico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT tipo_atendimento, COUNT(*) as total
            FROM Atendimento
            WHERE 1=1
            """
        params = []
        if start_date:
            query += " AND DATE(data_hora_inicio_atendimento) >= ?"
            params.append(start_date)
        if end_date:
            query += " AND DATE(data_hora_inicio_atendimento) <= ?"
            params.append(end_date)
        query += " GROUP BY tipo_atendimento ORDER BY total DESC"
        
        cursor.execute(query, tuple(params))
        data = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in data]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar atendimentos por tipo: {e}"}
    finally:
        conn.close()

def get_atendimentos_by_posto(start_date=None, end_date=None):
    """Retorna a contagem de atendimentos por posto de saúde em um período específico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT ps.nome_posto, COUNT(a.id_atendimento) as total
            FROM Atendimento a
            JOIN PostoSaude ps ON a.id_posto_atendimento = ps.id_posto
            WHERE 1=1
            """
        params = []
        if start_date:
            query += " AND DATE(a.data_hora_inicio_atendimento) >= ?"
            params.append(start_date)
        if end_date:
            query += " AND DATE(a.data_hora_inicio_atendimento) <= ?"
            params.append(end_date)
        query += " GROUP BY ps.nome_posto ORDER BY total DESC"
        
        cursor.execute(query, tuple(params))
        data = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in data]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar atendimentos por posto: {e}"}
    finally:
        conn.close()

def get_pacientes_by_genero():
    """Retorna a contagem de pacientes por gênero."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT genero_paciente, COUNT(*) as total FROM Paciente GROUP BY genero_paciente ORDER BY total DESC"
        cursor.execute(query)
        data = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in data]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar pacientes por gênero: {e}"}
    finally:
        conn.close()

def get_pacientes_by_idade_group():
    """Retorna a contagem de pacientes por faixa etária (simplificado)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT data_nascimento_paciente FROM Paciente"
        cursor.execute(query)
        data = cursor.fetchall()
        
        ages = []
        today = datetime.now().date()
        for row in data:
            dob_str = row["data_nascimento_paciente"]
            if dob_str:
                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                ages.append(age)
        
        # Agrupamento por faixa etária (ex: 0-10, 11-20, etc.)
        age_groups = {"0-10": 0, "11-20": 0, "21-30": 0, "31-40": 0, "41-50": 0, "51-60": 0, "61+": 0}
        for age in ages:
            if age <= 10: age_groups["0-10"] += 1
            elif age <= 20: age_groups["11-20"] += 1
            elif age <= 30: age_groups["21-30"] += 1
            elif age <= 40: age_groups["31-40"] += 1
            elif age <= 50: age_groups["41-50"] += 1
            elif age <= 60: age_groups["51-60"] += 1
            else: age_groups["61+"] += 1
            
        # Converter para o formato de lista de dicionários
        formatted_data = [{"faixa_etaria": k, "total": v} for k, v in age_groups.items()]
        
        return {"success": True, "data": formatted_data}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar pacientes por faixa etária: {e}"}
    finally:
        conn.close()

def get_top_distribui_medicamentos(start_date=None, end_date=None, limit=10):
    """Retorna os medicamentos mais distribuidos em um período específico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT m.nome_comercial_medicamento, SUM(dm.quantidade_distribuida) as total_distribuido
            FROM DistribuicaoMedicamento dm
            JOIN Prescricao pr ON dm.id_prescricao = pr.id_prescricao
            JOIN EstoqueMedicamentoPosto emp ON pr.id_medicamento_estoque = emp.id_estoque
            JOIN Medicamento m ON emp.id_medicamento = m.id_medicamento
            WHERE 1=1
            """
        params = []
        if start_date:
            query += " AND DATE(dm.data_hora_distribuicao) >= ?"
            params.append(start_date)
        if end_date:
            query += " AND DATE(dm.data_hora_distribuicao) <= ?"
            params.append(end_date)
        query += " GROUP BY m.nome_comercial_medicamento ORDER BY total_distribuido DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        data = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in data]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar medicamentos mais distribuidos: {e}"}
    finally:
        conn.close()

def get_top_diagnosticos(start_date=None, end_date=None, limit=10):
    """Retorna os diagnósticos (CID-10) mais comuns em um período específico."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = """SELECT cid10, COUNT(*) as total
            FROM Atendimento
            WHERE cid10 IS NOT NULL AND cid10 != ''
            """
        params = []
        if start_date:
            query += " AND DATE(data_hora_inicio_atendimento) >= ?"
            params.append(start_date)
        if end_date:
            query += " AND DATE(data_hora_inicio_atendimento) <= ?"
            params.append(end_date)
        query += " GROUP BY cid10 ORDER BY total DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        data = cursor.fetchall()
        return {"success": True, "data": [dict(row) for row in data]}
    except sqlite3.Error as e:
        return {"success": False, "message": f"Erro ao buscar diagnósticos mais comuns: {e}"}
    finally:
        conn.close()

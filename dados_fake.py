import sqlite3
import hashlib
from faker import Faker
from datetime import datetime, timedelta
import random
import bcrypt # Importa a biblioteca bcrypt

# Inicializa o Faker para o Brasil
fake = Faker('pt_BR')

# --- Funções customizadas para gerar dados de saúde ---
def generate_registro_profissional(cargo):
    """Gera um registro profissional fictício baseado no cargo."""
    if cargo == "Médico":
        # Exemplo: CRM/SP123456
        return f"CRM/{fake.estado_sigla()}{random.randint(100000, 999999)}"
    elif cargo == "Enfermeiro" or cargo == "Técnico de Enfermagem":
        # Exemplo: COREN/MG654321
        return f"COREN/{fake.estado_sigla()}{random.randint(100000, 999999)}"
    return None

def generate_cid10_code():
    """Gera um código CID-10 fictício de uma lista predefinida."""
    common_cid10 = [
        "J00", "J11.1", "R51", "I10", "E11.9", "K21.9", "M54.5", "G43.9", "A09", "N39.0"
    ]
    return random.choice(common_cid10)
# --- Fim das funções customizadas ---


DATABASE_NAME = 'hospital_db.sqlite'

def create_tables(conn):
    """
    Cria as tabelas no banco de dados se elas não existirem,
    usando o script SQL fornecido.
    """
    cursor = conn.cursor()
    sql_script = """
    CREATE TABLE IF NOT EXISTS Hospital (
        id_hospital INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_hospital TEXT NOT NULL,
        cnpj_hospital TEXT UNIQUE,
        endereco_hospital TEXT,
        telefone_hospital TEXT,
        email_hospital TEXT
    );

    CREATE TABLE IF NOT EXISTS PostoSaude (
        id_posto INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_posto TEXT NOT NULL,
        endereco_posto TEXT NOT NULL,
        telefone_posto TEXT,
        email_posto TEXT,
        id_hospital_vinculado INTEGER NOT NULL,
        FOREIGN KEY (id_hospital_vinculado) REFERENCES Hospital(id_hospital)
    );

    CREATE TABLE IF NOT EXISTS Funcionario (
        id_funcionario INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_funcionario TEXT NOT NULL,
        cpf_funcionario TEXT UNIQUE NOT NULL,
        cargo_funcionario TEXT NOT NULL,
        especialidade_medica TEXT,
        registro_profissional TEXT,
        telefone_funcionario TEXT,
        email_funcionario TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        id_posto_lotacao INTEGER NOT NULL,
        FOREIGN KEY (id_posto_lotacao) REFERENCES PostoSaude(id_posto)
    );

    CREATE TABLE IF NOT EXISTS Paciente (
        id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_paciente TEXT NOT NULL,
        cpf_paciente TEXT UNIQUE NOT NULL,
        cartao_sus TEXT UNIQUE,
        data_nascimento_paciente TEXT NOT NULL,
        genero_paciente TEXT NOT NULL,
        endereco_paciente TEXT NOT NULL,
        telefone_paciente TEXT,
        email_paciente TEXT,
        id_posto_referencia INTEGER NOT NULL,
        FOREIGN KEY (id_posto_referencia) REFERENCES PostoSaude(id_posto)
    );

    CREATE TABLE IF NOT EXISTS Medicamento (
        id_medicamento INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_comercial_medicamento TEXT NOT NULL,
        principio_ativo TEXT NOT NULL,
        apresentacao TEXT,
        fabricante TEXT,
        tipo_medicamento TEXT
    );

    CREATE TABLE IF NOT EXISTS EstoqueMedicamentoPosto (
        id_estoque INTEGER PRIMARY KEY AUTOINCREMENT,
        id_medicamento INTEGER NOT NULL,
        id_posto INTEGER NOT NULL,
        lote TEXT NOT NULL,
        data_validade TEXT NOT NULL,
        quantidade_atual INTEGER NOT NULL,
        quantidade_minima_alerta INTEGER NOT NULL DEFAULT 0,
        UNIQUE(id_medicamento, id_posto, lote),
        FOREIGN KEY (id_medicamento) REFERENCES Medicamento(id_medicamento),
        FOREIGN KEY (id_posto) REFERENCES PostoSaude(id_posto)
    );

    CREATE TABLE IF NOT EXISTS Atendimento (
        id_atendimento INTEGER PRIMARY KEY AUTOINCREMENT,
        id_paciente INTEGER NOT NULL,
        id_funcionario_responsavel INTEGER NOT NULL,
        id_posto_atendimento INTEGER NOT NULL,
        data_hora_inicio_atendimento TEXT NOT NULL,
        data_hora_fim_atendimento TEXT,
        tipo_atendimento TEXT NOT NULL,
        descricao_sintomas_queixa TEXT NOT NULL,
        diagnostico TEXT,
        cid10 TEXT,
        grau_doenca_observado TEXT,
        observacoes_gerais TEXT,
        FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente),
        FOREIGN KEY (id_funcionario_responsavel) REFERENCES Funcionario(id_funcionario),
        FOREIGN KEY (id_posto_atendimento) REFERENCES PostoSaude(id_posto)
    );

    CREATE TABLE IF NOT EXISTS Prescricao (
        id_prescricao INTEGER PRIMARY KEY AUTOINCREMENT,
        id_atendimento INTEGER NOT NULL,
        id_medicamento_estoque INTEGER NOT NULL,
        posologia TEXT NOT NULL,
        quantidade_prescrita INTEGER NOT NULL,
        data_hora_prescricao TEXT DEFAULT CURRENT_TIMESTAMP,
        status_distribuicao TEXT DEFAULT 'Pendente',
        FOREIGN KEY (id_atendimento) REFERENCES Atendimento(id_atendimento),
        FOREIGN KEY (id_medicamento_estoque) REFERENCES EstoqueMedicamentoPosto(id_estoque)
    );

    CREATE TABLE IF NOT EXISTS DistribuicaoMedicamento (
        id_distribuicao INTEGER PRIMARY KEY AUTOINCREMENT,
        id_prescricao INTEGER NOT NULL,
        id_funcionario_distribuidor INTEGER NOT NULL,
        data_hora_distribuicao TEXT DEFAULT CURRENT_TIMESTAMP,
        quantidade_distribuicao INTEGER NOT NULL,
        observacao TEXT,
        FOREIGN KEY (id_prescricao) REFERENCES Prescricao(id_prescricao),
        FOREIGN KEY (id_funcionario_distribuidor) REFERENCES Funcionario(id_funcionario)
    );
    """
    cursor.executescript(sql_script)
    conn.commit()
    print("Tabelas verificadas/criadas com sucesso.")

def generate_hashed_password(password):
    """
    Gera um hash bcrypt para a senha.
    O salt é gerado automaticamente pelo bcrypt.gensalt().
    """
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8') # Decodifica para string para salvar no banco

def generate_and_insert_data(conn, num_hospitals=3, num_postos_per_hospital=5,
                             num_funcionarios_per_posto=10, num_pacientes_per_posto=30,
                             num_medicamentos=50, num_atendimentos_per_paciente=3,
                             num_prescricoes_per_atendimento=2):
    """
    Gera e insere dados fictícios nas tabelas.
    """
    cursor = conn.cursor()

    # --- Hospital ---
    hospital_ids = []
    print("\nInserindo Hospitais...")
    for _ in range(num_hospitals):
        nome = fake.company() + " Hospital"
        cnpj = fake.cnpj()
        endereco = fake.address()
        telefone = fake.phone_number()
        email = fake.email()
        cursor.execute("INSERT INTO Hospital (nome_hospital, cnpj_hospital, endereco_hospital, telefone_hospital, email_hospital) VALUES (?, ?, ?, ?, ?)",
                       (nome, cnpj, endereco, telefone, email))
        hospital_ids.append(cursor.lastrowid)
    conn.commit()
    print(f"Inseridos {len(hospital_ids)} hospitais.")

    # --- PostoSaude ---
    posto_ids = []
    print("\nInserindo Postos de Saúde...")
    for h_id in hospital_ids:
        for _ in range(num_postos_per_hospital):
            nome = fake.company() + " Posto de Saúde"
            endereco = fake.address()
            telefone = fake.phone_number()
            email = fake.email()
            cursor.execute("INSERT INTO PostoSaude (nome_posto, endereco_posto, telefone_posto, email_posto, id_hospital_vinculado) VALUES (?, ?, ?, ?, ?)",
                           (nome, endereco, telefone, email, h_id))
            posto_ids.append(cursor.lastrowid)
    conn.commit()
    print(f"Inseridos {len(posto_ids)} postos de saúde.")

    # --- Funcionario ---
    funcionario_ids = []
    print("\nInserindo Funcionários Fictícios...")
    cargos = ["Médico", "Enfermeiro", "Técnico de Enfermagem", "Administrativo", "Recepcionista"]
    especialidades = ["Clínica Geral", "Pediatria", "Cardiologia", "Dermatologia", "Ginecologia"]
    for p_id in posto_ids:
        for _ in range(num_funcionarios_per_posto):
            nome = fake.name()
            cpf = fake.cpf()
            cargo = random.choice(cargos)
            especialidade = random.choice(especialidades) if cargo == "Médico" else None
            # Usa a função customizada para gerar o registro profissional
            registro = generate_registro_profissional(cargo)
            telefone = fake.phone_number()
            email = fake.unique.email()
            senha_hash = generate_hashed_password("senha123") # Senha padrão para dados fictícios
            cursor.execute("INSERT INTO Funcionario (nome_funcionario, cpf_funcionario, cargo_funcionario, especialidade_medica, registro_profissional, telefone_funcionario, email_funcionario, senha_hash, id_posto_lotacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (nome, cpf, cargo, especialidade, registro, telefone, email, senha_hash, p_id))
            funcionario_ids.append(cursor.lastrowid)
    conn.commit()
    print(f"Inseridos {len(funcionario_ids)} funcionários fictícios.")

    # --- Inserção de Funcionários Padrão ---
    print("\nInserindo Funcionários Padrão...")
    default_employees = [
        {
            "nome": "Admin Geral",
            "cpf": "000.000.000-00",
            "cargo": "Administrativo",
            "email": "admin@hospital.com",
            "senha": "admin123",
            "especialidade": None,
            "registro_profissional": None
        },
        {
            "nome": "Dr. Joao Medico",
            "cpf": "111.111.111-11",
            "cargo": "Médico",
            "email": "joao.medico@hospital.com",
            "senha": "medico123",
            "especialidade": "Clínica Geral",
            "registro_profissional": generate_registro_profissional("Médico") # Usa a função customizada
        },
        {
            "nome": "Enf. Maria Enfermeira",
            "cpf": "222.222.222-22",
            "cargo": "Enfermeiro",
            "email": "maria.enf@hospital.com",
            "senha": "enfermeira123",
            "especialidade": None,
            "registro_profissional": generate_registro_profissional("Enfermeiro") # Usa a função customizada
        }
    ]

    for emp_data in default_employees:
        nome = emp_data["nome"]
        cpf = emp_data["cpf"]
        cargo = emp_data["cargo"]
        email = emp_data["email"]
        senha_hash = generate_hashed_password(emp_data["senha"]) # Agora usa bcrypt
        especialidade = emp_data["especialidade"]
        registro = emp_data["registro_profissional"]
        telefone = fake.phone_number() # Gera um telefone aleatório para os fixos também
        
        # Usa o ID do primeiro posto de saúde criado para a lotação do funcionário padrão
        posto_lotacao = posto_ids[0] if posto_ids else 1 # Fallback para 1 se não houver postos

        try:
            cursor.execute("INSERT INTO Funcionario (nome_funcionario, cpf_funcionario, cargo_funcionario, especialidade_medica, registro_profissional, telefone_funcionario, email_funcionario, senha_hash, id_posto_lotacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (nome, cpf, cargo, especialidade, registro, telefone, email, senha_hash, posto_lotacao))
            funcionario_ids.append(cursor.lastrowid)
            conn.commit()
            print(f"Funcionário padrão '{nome}' ({email}) inserido com a senha '{emp_data['senha']}'.")
        except sqlite3.IntegrityError as e:
            print(f"Aviso: Funcionário padrão '{nome}' com e-mail '{email}' ou CPF '{cpf}' já existe. Ignorando inserção. Erro: {e}")
        except Exception as e:
            print(f"Erro ao inserir funcionário padrão '{nome}': {e}")
    print(f"Inseridos {len(default_employees)} funcionários padrão.")


    # --- Paciente ---
    paciente_ids = []
    print("\nInserindo Pacientes...")
    generos = ["Masculino", "Feminino", "Outro"]
    for p_id in posto_ids:
        for _ in range(num_pacientes_per_posto):
            nome = fake.name()
            cpf = fake.cpf()
            cartao_sus = fake.random_number(digits=15, fix_len=True) # Cartão SUS fictício
            data_nascimento = fake.date_of_birth(minimum_age=1, maximum_age=90).strftime('%Y-%m-%d')
            genero = random.choice(generos)
            endereco = fake.address()
            telefone = fake.phone_number()
            email = fake.email()
            cursor.execute("INSERT INTO Paciente (nome_paciente, cpf_paciente, cartao_sus, data_nascimento_paciente, genero_paciente, endereco_paciente, telefone_paciente, email_paciente, id_posto_referencia) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (nome, cpf, cartao_sus, data_nascimento, genero, endereco, telefone, email, p_id))
            paciente_ids.append(cursor.lastrowid)
    conn.commit()
    print(f"Inseridos {len(paciente_ids)} pacientes.")

    # --- Medicamento ---
    medicamento_ids = []
    print("\nInserindo Medicamentos...")
    tipos_medicamento = ["Comprimido", "Xarope", "Injetável", "Pomada", "Cápsula"]
    for _ in range(num_medicamentos):
        nome_comercial = fake.word().capitalize() + " " + fake.word().capitalize() + " Plus"
        principio_ativo = fake.word().capitalize() + " " + fake.word().capitalize()
        apresentacao = random.choice(["20mg", "500mg", "100ml", "10ml", "30 comprimidos"])
        fabricante = fake.company()
        tipo_medicamento = random.choice(tipos_medicamento)
        cursor.execute("INSERT INTO Medicamento (nome_comercial_medicamento, principio_ativo, apresentacao, fabricante, tipo_medicamento) VALUES (?, ?, ?, ?, ?)",
                       (nome_comercial, principio_ativo, apresentacao, fabricante, tipo_medicamento))
        medicamento_ids.append(cursor.lastrowid)
    conn.commit()
    print(f"Inseridos {len(medicamento_ids)} medicamentos.")

    # --- EstoqueMedicamentoPosto ---
    estoque_medicamento_posto_ids = []
    print("\nInserindo Estoques de Medicamentos por Posto...")
    # Garante que cada posto tenha estoque de alguns medicamentos
    for p_id in posto_ids:
        # Pega um subconjunto de medicamentos para cada posto
        medicamentos_para_posto = random.sample(medicamento_ids, min(10, len(medicamento_ids)))
        for m_id in medicamentos_para_posto:
            lote = fake.bothify(text='Lote-###-????')
            data_validade = fake.date_between(start_date='today', end_date='+2y').strftime('%Y-%m-%d')
            quantidade_atual = random.randint(100, 1000)
            quantidade_minima_alerta = random.randint(10, 50)
            try:
                cursor.execute("INSERT INTO EstoqueMedicamentoPosto (id_medicamento, id_posto, lote, data_validade, quantidade_atual, quantidade_minima_alerta) VALUES (?, ?, ?, ?, ?, ?)",
                               (m_id, p_id, lote, data_validade, quantidade_atual, quantidade_minima_alerta))
                estoque_medicamento_posto_ids.append(cursor.lastrowid)
            except sqlite3.IntegrityError:
                # Tratar caso de lote duplicado para o mesmo medicamento e posto (UNIQUE constraint)
                # Faker pode gerar duplicatas, neste caso, apenas ignoramos
                pass
    conn.commit()
    print(f"Inseridos {len(estoque_medicamento_posto_ids)} registros de estoque.")

    # --- Atendimento ---
    atendimento_ids = []
    print("\nInserindo Atendimentos...")
    tipos_atendimento = ["Consulta", "Emergência", "Triagem", "Retorno", "Exame"]
    diagnosticos = ["Resfriado Comum", "Hipertensão", "Diabetes Tipo 2", "Dor de Cabeça", "Infecção Urinária", "Gripe"]
    graus_doenca = ["Leve", "Moderado", "Grave"]
    
    # Obter apenas funcionários que são médicos
    cursor.execute("SELECT id_funcionario FROM Funcionario WHERE cargo_funcionario = 'Médico'")
    medico_ids = [row[0] for row in cursor.fetchall()]

    for p_id in paciente_ids:
        # Encontra o posto de referência do paciente para garantir atendimentos no posto certo
        cursor.execute("SELECT id_posto_referencia FROM Paciente WHERE id_paciente = ?", (p_id,))
        posto_referencia_paciente = cursor.fetchone()[0]

        # Encontra funcionários médicos lotados no posto de referência do paciente
        funcionarios_no_posto = [f for f in medico_ids if f in [func[0] for func in cursor.execute("SELECT id_funcionario FROM Funcionario WHERE id_posto_lotacao = ?", (posto_referencia_paciente,)).fetchall()]]
        
        if not funcionarios_no_posto:
            print(f"Aviso: Nenhum médico encontrado para o posto {posto_referencia_paciente}. Pulando atendimentos para paciente {p_id}.")
            continue

        for _ in range(num_atendimentos_per_paciente):
            data_hora_inicio = fake.date_time_between(start_date='-1y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
            data_hora_fim = (datetime.strptime(data_hora_inicio, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=random.randint(15, 120))).strftime('%Y-%m-%d %H:%M:%S')
            tipo_atendimento = random.choice(tipos_atendimento)
            descricao_sintomas = fake.text(max_nb_chars=100)
            diagnostico = random.choice(diagnosticos)
            # Usa a função customizada para gerar o CID-10
            cid10 = generate_cid10_code()
            grau_doenca = random.choice(graus_doenca)
            observacoes = fake.paragraph(nb_sentences=2)
            
            # Escolhe um funcionário responsável aleatório do posto do paciente
            funcionario_responsavel = random.choice(funcionarios_no_posto)

            cursor.execute("INSERT INTO Atendimento (id_paciente, id_funcionario_responsavel, id_posto_atendimento, data_hora_inicio_atendimento, data_hora_fim_atendimento, tipo_atendimento, descricao_sintomas_queixa, diagnostico, cid10, grau_doenca_observado, observacoes_gerais) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (p_id, funcionario_responsavel, posto_referencia_paciente, data_hora_inicio, data_hora_fim, tipo_atendimento, descricao_sintomas, diagnostico, cid10, grau_doenca, observacoes))
            atendimento_ids.append(cursor.lastrowid)
    conn.commit()
    print(f"Inseridos {len(atendimento_ids)} atendimentos.")

    # --- Prescricao ---
    prescricao_ids = []
    print("\nInserindo Prescrições...")
    posologias = ["1 comprimido a cada 8 horas por 7 dias", "10ml a cada 6 horas", "Uso tópico 2x ao dia"]
    for a_id in atendimento_ids:
        # Obter o id_posto_atendimento do atendimento para filtrar o estoque
        cursor.execute("SELECT id_posto_atendimento FROM Atendimento WHERE id_atendimento = ?", (a_id,))
        posto_atendimento_id = cursor.fetchone()[0]

        # Obter id_estoque de medicamentos disponíveis no posto do atendimento
        cursor.execute("SELECT id_estoque FROM EstoqueMedicamentoPosto WHERE id_posto = ?", (posto_atendimento_id,))
        estoque_ids_no_posto = [row[0] for row in cursor.fetchall()]

        if not estoque_ids_no_posto:
            print(f"Aviso: Nenhum medicamento em estoque encontrado para o posto {posto_atendimento_id}. Pulando prescrições para atendimento {a_id}.")
            continue

        for _ in range(num_prescricoes_per_atendimento):
            id_medicamento_estoque = random.choice(estoque_ids_no_posto)
            posologia = random.choice(posologias)
            quantidade_prescrita = random.randint(1, 30)
            cursor.execute("INSERT INTO Prescricao (id_atendimento, id_medicamento_estoque, posologia, quantidade_prescrita) VALUES (?, ?, ?, ?)",
                           (a_id, id_medicamento_estoque, posologia, quantidade_prescrita))
            prescricao_ids.append(cursor.lastrowid)
    conn.commit()
    print(f"Inseridas {len(prescricao_ids)} prescrições.")

    # --- DistribuicaoMedicamento ---
    print("\nInserindo Dispensações de Medicamentos...")
    # Obter todos os IDs de funcionários que podem dispensar (ex: enfermeiros, técnicos de enfermagem)
    cursor.execute("SELECT id_funcionario FROM Funcionario WHERE cargo_funcionario IN ('Enfermeiro', 'Técnico de Enfermagem', 'Farmacêutico', 'Administrativo')")
    dispensador_ids = [row[0] for row in cursor.fetchall()]

    if not dispensador_ids:
        print("Aviso: Nenhum funcionário apto para dispensação encontrado. Nenhuma dispensação será inserida.")
    else:
        for p_id in prescricao_ids:
            # Obter a quantidade prescrita para a dispensação
            cursor.execute("SELECT quantidade_prescrita FROM Prescricao WHERE id_prescricao = ?", (p_id,))
            quantidade_prescrita = cursor.fetchone()[0]

            id_funcionario_dispensador = random.choice(dispensador_ids)
            quantidade_dispensada = random.randint(1, quantidade_prescrita) # Não pode dispensar mais do que o prescrito
            observacao = fake.text(max_nb_chars=50) if random.random() > 0.5 else None # Opcional
            
            cursor.execute("INSERT INTO DistribuicaoMedicamento (id_prescricao, id_funcionario_dispensador, quantidade_dispensada, observacao) VALUES (?, ?, ?, ?)",
                           (p_id, id_funcionario_dispensador, quantidade_dispensada, observacao))
            
            # Atualizar o status da prescrição para 'Dispensado'
            cursor.execute("UPDATE Prescricao SET status_distribuicao = 'Dispensado' WHERE id_prescricao = ?", (p_id,))
    conn.commit()
    print(f"Distribuicao de medicamentos inseridas.")


def main():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        print(f"Conectado ao banco de dados: {DATABASE_NAME}")

        create_tables(conn)
        generate_and_insert_data(conn)
        print("\nDados fictícios inseridos com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro no banco de dados: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    main()
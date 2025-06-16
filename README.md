Com certeza\! Adicionarei o link do site hospedado de forma destacada no `README.md`.

-----

# Gerenciador de Postos de Saúde 🏥🩺

Um sistema de gerenciamento completo para postos de saúde, desenvolvido em Python com Streamlit para a interface e SQLite como banco de dados. Este projeto visa otimizar a administração de hospitais, postos de saúde, funcionários, pacientes, medicamentos, atendimentos e prescrições.

## 🔗 Acesse a Aplicação Online\!

Você pode explorar o sistema em funcionamento diretamente pelo navegador:

**[https://gerenciadorpostos.streamlit.app](https://gerenciadorpostos.streamlit.app)**

## ✨ Funcionalidades Principais

  * **Gestão de Entidades:** Cadastre e gerencie hospitais, postos de saúde, funcionários, pacientes e medicamentos.
  * **Controle de Estoque:** Mantenha o controle do estoque de medicamentos por posto, com alertas de quantidade mínima e validade próxima.
  * **Registro de Atendimentos:** Registre atendimentos detalhados com informações de paciente, funcionário responsável, tipo de atendimento, diagnóstico (CID-10) e observações.
  * **Prescrições e Distribuição:** Crie prescrições médicas e acompanhe a distribuição de medicamentos, com atualização automática do estoque.
  * **Relatórios e Análises:** Acesse relatórios visuais sobre tipos de atendimento, atendimentos por posto, perfil de pacientes (gênero e idade), medicamentos mais distribuídos e diagnósticos mais comuns.
  * **Sistema de Login:** Acesso seguro com autenticação de funcionários.

## 🚀 Como Rodar o Projeto Localmente

Siga estes passos para configurar e executar o sistema na sua máquina:

1.  **Clone o Repositório:**

    ```bash
    git clone https://github.com/juvenalculino/Gerenciador-de-Postos-de-Saude.git
    cd Gerenciador-de-Postos-de-Saude/aplicacao
    ```

2.  **Crie e Ative um Ambiente Virtual (Recomendado):**

    ```bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**

    ```bash
    pip install -r requirements.txt
    ```

      * Este projeto utiliza bibliotecas como `streamlit`, `pandas`, `matplotlib`, `bcrypt`, `Faker`, entre outras.

4.  **Popule o Banco de Dados (Opcional, mas Recomendado):**
    Para ter dados de exemplo e testar todas as funcionalidades, execute o script de dados fake:

    ```bash
    python dados_fake.py
    ```

      * Este script cria um banco de dados SQLite (`hospital_db.sqlite`) e popula-o com informações fictícias de hospitais, postos, funcionários (incluindo usuários padrão para login), pacientes, medicamentos, estoque e atendimentos.

5.  **Inicie a Aplicação Streamlit:**

    ```bash
    streamlit run app.py
    ```

    O aplicativo será aberto automaticamente no seu navegador.

## 🔑 Credenciais de Login Padrão (para o Banco de Dados Fictício)

  * **Email:** `admin@hospital.com`
  * **Senha:** `admin123`

## 🛠️ Tecnologias Utilizadas

  * **Backend/Lógica:** Python
  * **Interface do Usuário (UI):** Streamlit
  * **Banco de Dados:** SQLite
  * **Geração de Dados Fake:** Faker
  * **Criptografia de Senha:** `bcrypt`
  * **Manipulação de Dados:** Pandas
  * **Visualização de Dados:** Matplotlib

## 📁 Estrutura do Projeto

  * `aplicacao/app.py`: O arquivo principal da aplicação Streamlit, onde toda a interface e integração com as funções CRUD ocorrem.
  * `aplicacao/open_crud.py`: Contém todas as funções de `CREATE`, `READ`, `UPDATE`, `DELETE` e relatórios para interagir com o banco de dados SQLite.
  * `aplicacao/dados_fake.py`: Script para criar as tabelas do banco de dados e popular com dados de exemplo.
  * `aplicacao/requirements.txt`: Lista de todas as dependências Python necessárias.
  * `aplicacao/styles.css`: Arquivo CSS para estilização personalizada da interface do Streamlit.

## 🤝 Contribuições

Sinta-se à vontade para abrir issues, sugerir melhorias ou enviar pull requests\! Toda contribuição é bem-vinda.

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` (a ser criado no repositório) para mais detalhes.

Ótima ideia\! Adicionarei uma seção de "Próximos Passos" no `README.md` com essas sugestões.

-----

# Gerenciador de Postos de Saúde 🏥🩺

Um sistema de gerenciamento completo para postos de saúde, desenvolvido em Python com Streamlit para a interface e SQLite como banco de dados. Este projeto visa otimizar a administração de hospitais, postos de saúde, funcionários, pacientes, medicamentos, atendimentos e prescrições.

<img src="https://github.com/juvenalculino/Gerenciador-de-Postos-de-Saude/blob/master/2025-06-16_19-12.png">

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

## 💡 Próximos Passos e Ideias para Melhoria

Este projeto é uma base sólida e pode ser expandido com as seguintes melhorias:

  * **Inclusão de Inteligência Artificial/Machine Learning:**
      * **Previsão de Estoque:** Implementar modelos para prever a demanda de medicamentos, otimizando o estoque e evitando faltas ou excessos.
      * **Análise Preditiva de Doenças:** Utilizar dados de atendimento para identificar padrões e prever surtos de doenças em regiões específicas.
      * **Recomendação de Tratamentos:** Sugerir tratamentos com base em diagnósticos e históricos de pacientes.
  * **Modularização Avançada:**
      * **Serviços RESTful:** Transformar as funções CRUD em uma API RESTful (com Flask, FastAPI ou Django REST Framework) para desacoplar o backend do frontend.
      * **Separação de Componentes UI:** Organizar a interface do Streamlit em componentes reutilizáveis para melhor manutenção e escalabilidade.
  * **Outras Ideias:**
      * **Notificações em Tempo Real:** Implementar alertas para estoque baixo ou validades próximas via e-mail ou SMS.
      * **Integração com Prontuários Eletrônicos:** Conectar o sistema a prontuários eletrônicos de pacientes para uma visão 360º.
      * **Dashboards Interativos:** Aprimorar os relatórios com dashboards mais complexos e filtros dinâmicos.
      * **Suporte a Múltiplos Usuários/Perfis:** Detalhar permissões de acesso baseadas em cargos (médico só vê pacientes, administrativo gerencia hospitais, etc.).
      * **Auditoria de Ações:** Registrar logs de todas as operações realizadas no sistema para rastreabilidade.
      * **Sistema de Agendamento de Consultas:** Adicionar funcionalidade para agendamento e gerenciamento de consultas.

## 🤝 Contribuições

Sinta-se à vontade para abrir issues, sugerir melhorias ou enviar pull requests\! Toda contribuição é bem-vinda.

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` (a ser criado no repositório) para mais detalhes.

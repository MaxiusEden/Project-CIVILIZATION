# Project CIVILIZATION

Um jogo de estratégia baseado em turnos inspirado no Sid Meier's Civilization, com interface gráfica 3D (PyQt5 + PyOpenGL), arquitetura robusta e sistema de dados seguro e customizável.

## Descrição

Este projeto recria a experiência do Civilization em uma interface gráfica moderna. Os jogadores podem construir um império, desenvolver tecnologias, fundar cidades, construir melhorias, treinar unidades militares e interagir diplomaticamente com outras civilizações, tudo em um ambiente 3D.

## Características

- Interface gráfica 3D (PyQt5 + PyOpenGL)
- Mapa gerado proceduralmente
- Várias civilizações para escolher
- Sistema de tecnologias
- Construção de cidades e melhorias
- Unidades militares e combate
- Diplomacia com outras civilizações
- Sistema de salvamento seguro (JSON + hash)
- Autosave configurável
- Internacionalização (i18n) e textos customizáveis
- Logger avançado com rotação
- Estrutura modular e extensível (MVC)

## Requisitos

- Python 3.8 ou superior
- PyQt5
- PyOpenGL
- numpy
- pydantic

## Instalação

1. Clone o repositório:
```powershell
git clone https://github.com/MaxiusEden/Project-CIVILIZATION.git
cd Project-CIVILIZATION
```

2. Instale as dependências principais:
```powershell
pip install -r requirements.txt
```

3. (Opcional) Instale dependências de desenvolvimento:
```powershell
pip install -r requirements-dev.txt
```

4. Execute o jogo:
```powershell
python main.py
```

## Estrutura do Projeto

```
Project-CIVILIZATION/
├── main.py                  # Ponto de entrada do jogo
├── config.py                # Configurações globais
├── README.md
├── LICENSE
├── requirements.txt         # Dependências principais
├── requirements-dev.txt     # Dependências de desenvolvimento
├── TODO_INTEGRACOES.txt     # Tarefas de integração pendentes
├── REGISTRO_ALTERACOES_2025-05-21.txt # Registro de alterações
├── data/                    # Dados do jogo (JSON)
│   ├── buildings.json
│   ├── city_states.json
│   ├── civilizations.json
│   ├── game_settings.json
│   ├── game_text.json
│   ├── game_text.multilang.example.json
│   ├── game_text.user.example.json
│   ├── great_people.json
│   ├── improvements.json
│   ├── policies.json
│   ├── promotions.json
│   ├── religions.json
│   ├── religious_beliefs.json
│   ├── resources.json
│   ├── technologies.json
│   ├── terrains.json
│   ├── ui_settings.json
│   ├── units.json
│   └── wonders.json
├── game/                    # Código-fonte principal
│   ├── __init__.py
│   ├── controllers/         # Controladores do jogo (MVC)
│   ├── gui/                 # Interface gráfica (PyQt5)
│   ├── models/              # Modelos de dados do jogo
│   └── utils/               # Utilitários e infraestrutura
├── logs/                    # Arquivos de log (rotacionados automaticamente)
├── saves/                   # Jogos salvos (JSON seguro)
└── tests/                   # Testes automatizados
```

## Como jogar

### Menu Principal
- **Novo Jogo**: Inicia uma nova partida
- **Carregar Jogo**: Carrega um jogo salvo
- **Configurações**: Ajusta as configurações do jogo
- **Sobre**: Exibe informações sobre o jogo
- **Sair**: Encerra o jogo

### Controles na interface gráfica
- Use o mouse para selecionar unidades, cidades e tiles do mapa
- Utilize os botões e menus da interface para ações como mover, atacar, construir, pesquisar tecnologias, diplomacia, etc.
- Atalhos de teclado podem ser implementados na interface gráfica (consulte tooltips ou documentação in-game)

## Novas Funcionalidades e Integrações

### 1. Validação e Customização de Configurações
- O jogo valida automaticamente o arquivo `data/game_settings.json` ao iniciar.
- O usuário pode criar um arquivo `data/game_settings.user.json` para sobrescrever configurações específicas.
- Erros de configuração são exibidos de forma amigável.

### 2. Logger Avançado
- O sistema de logs suporta rotação automática e configuração de nível via variável de ambiente `LOG_LEVEL`.
- Todos os logs são salvos em `logs/game.log` por padrão.
- Para customizar, edite o início do `main.py` ou use variáveis de ambiente.

### 3. Internacionalização (i18n)
- O arquivo `data/game_text.json` pode ser estruturado para múltiplos idiomas (exemplo em `data/game_text.multilang.example.json`).
- O idioma pode ser definido em `config.py` (ex: `LANG = 'pt-BR'`).
- O usuário pode sobrescrever textos em `data/game_text.user.json`.
- Para adicionar um novo idioma, siga o exemplo e adicione uma nova chave de idioma no JSON.

### 4. Salvamento Seguro e Autosave
- O sistema de salvamento utiliza JSON seguro, com verificação de integridade por hash.
- O autosave pode ser ativado e configurado no código.
- Os saves ficam na pasta `saves/`.

### 5. Tipagem e Validação de Dados
- Dados carregados do JSON podem ser validados com Pydantic.
- Modelos de dados principais suportam serialização/deserialização robusta.

### 6. Separação de Dependências
- Dependências principais estão em `requirements.txt`.
- Dependências de desenvolvimento estão em `requirements-dev.txt`.
- Instale ambas para desenvolvimento completo:
```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 7. Como customizar textos e configurações
- Edite ou crie `data/game_text.user.json` para textos.
- Edite ou crie `data/game_settings.user.json` para configurações.
- Consulte os exemplos de estrutura nos arquivos `.example.json`.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
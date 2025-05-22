# Project CIVILIZATION

Um jogo de estratégia baseado em turnos inspirado no Sid Meier's Civilization, agora com interface gráfica 3D utilizando PyQt5 e PyOpenGL.

## Descrição

Este projeto recria a experiência do jogo Civilization em uma interface gráfica moderna. Os jogadores podem construir um império, desenvolver tecnologias, fundar cidades, construir melhorias, treinar unidades militares e interagir diplomaticamente com outras civilizações, tudo em um ambiente 3D.

## Características

- Interface gráfica 3D (PyQt5 + PyOpenGL)
- Mapa gerado proceduralmente
- Várias civilizações para escolher
- Sistema de tecnologias
- Construção de cidades e melhorias
- Unidades militares e combate
- Diplomacia com outras civilizações
- Sistema de salvamento e carregamento de jogos

## Requisitos

- Python 3.6 ou superior
- PyQt5
- PyOpenGL
- numpy

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/MaxiusEden/Project-CIVILIZATION.git
cd Project-CIVILIZATION
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o jogo:
```bash
python main.py
```

## Opções de linha de comando

- `--debug`: Ativa o modo de depuração
- `--load NOME`: Carrega um jogo salvo específico

Exemplo:
```bash
python main.py --debug
python main.py --load meu_jogo
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
- Atalhos de teclado podem ser implementados na interface gráfica (consulte a documentação in-game ou tooltips)

## Estrutura do Projeto

```
Project-CIVILIZATION/
├── main.py                 # Arquivo principal do jogo
├── game/                   # Módulos do jogo
│   ├── controllers/        # Controladores
│   ├── models/             # Modelos de dados
│   └── views/              # Visualizações
├── data/                   # Dados do jogo
│   ├── buildings.json      # Dados de edifícios
│   ├── civilizations.json  # Dados de civilizações
│   ├── technologies.json   # Árvore de tecnologias
│   └── units.json          # Dados de unidades
└── saves/                  # Jogos salvos
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

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

### 7. Como customizar textos e configurações
- Edite ou crie `data/game_text.user.json` para textos.
- Edite ou crie `data/game_settings.user.json` para configurações.
- Consulte os exemplos de estrutura nos arquivos `.example.json`.

## Dependências

- Dependências principais estão em `requirements.txt`.
- Dependências de desenvolvimento estão em `requirements-dev.txt`.
- Instale ambas para desenvolvimento completo:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```
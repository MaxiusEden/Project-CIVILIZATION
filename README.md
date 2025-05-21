# Project CIVILIZATION

Um jogo de estratégia baseado em turnos inspirado no Sid Meier's Civilization, implementado em modo texto para terminal.

## Descrição

Este projeto recria a experiência do jogo Civilization em um formato de texto para terminal. Os jogadores podem construir um império, desenvolver tecnologias, fundar cidades, construir melhorias, treinar unidades militares e interagir diplomaticamente com outras civilizações.

## Características

- Interface de texto para terminal
- Mapa gerado proceduralmente
- Várias civilizações para escolher
- Sistema de tecnologias
- Construção de cidades e melhorias
- Unidades militares e combate
- Diplomacia com outras civilizações
- Sistema de salvamento e carregamento de jogos

## Requisitos

- Python 3.6 ou superior

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/MaxiusEden/Project-CIVILIZATION.git
cd Project-CIVILIZATION
```

2. Execute o jogo:
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

### Controles no jogo

- **m**: Mover unidade
- **a**: Atacar
- **b**: Construir melhoria
- **c**: Gerenciar cidade
- **u**: Listar unidades
- **t**: Tecnologias
- **d**: Diplomacia
- **i**: Informações do tile
- **v**: Ver minimapa
- **s**: Salvar jogo
- **e**: Encerrar turno
- **q**: Sair para o menu

## Estrutura do Projeto

```
Project-CIVILIZATION/
├── main.py                 # Arquivo principal do jogo
├── config.py               # Arquivo de configurações do projeto
├── requirements.txt        # Dependências do projeto
├── LICENSE                 # Licença do projeto
├── README.md               # Descrição e instruções
├── game/                   # Módulos do jogo
│   ├── __init__.py
│   ├── controllers/        # Controladores do jogo
│   │   ├── __init__.py
│   │   ├── city_controller.py
│   │   ├── civ_controller.py
│   │   ├── game_controller.py
│   │   ├── unit_controller.py
│   │   ├── world_controller.py
│   ├── models/             # Modelos de dados do jogo
│   │   ├── __init__.py
│   │   ├── building.py
│   │   ├── city.py
│   │   ├── civilization.py
│   │   ├── diplomacy.py
│   │   ├── game_state.py
│   │   ├── tech.py
│   │   ├── unit.py
│   │   ├── world.py
│   ├── utils/              # Utilitários e ferramentas auxiliares
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   ├── logger.py
│   │   ├── perlin_noise.py
│   │   ├── save_manager.py
│   ├── views/              # Visualizações de interface
│   │   ├── __init__.py
│   │   ├── base_view.py
│   │   ├── city_view.py
│   │   ├── game_view.py
│   │   ├── menu_view.py
│   │   ├── tech_view.py
│   │   ├── unit_view.py
│   │   ├── world_view.py
├── data/                   # Arquivos de dados do jogo
│   ├── buildings.json
│   ├── civilizations.json
│   ├── city_states.json
│   ├── game_settings.json
│   ├── game_text.json
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
│   ├── Wonders.json
└── saves/                  # Jogos salvos (sugestão de pasta futura se ainda não existir)

```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
```

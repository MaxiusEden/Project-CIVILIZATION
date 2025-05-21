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
│   config.py
│   LICENSE
│   main.py
│   README.md
│   requirements.txt
│
├───data/
│   buildings.json
│   city_states.json
│   civilizations.json
│   game_settings.json
│   game_text.json
│   great_people.json
│   improvements.json
│   policies.json
│   promotions.json
│   religions.json
│   religious_beliefs.json
│   resources.json
│   technologies.json
│   terrains.json
│   ui_settings.json
│   units.json
│   wonders.json
│
├───game/
│   __init__.py
│
│   ├───controllers/
│   │   city_controller.py
│   │   civ_controller.py
│   │   game_controller.py
│   │   unit_controller.py
│   │   world_controller.py
│   │   __init__.py
│   │
│   ├───gui/
│   │   info_panel.py
│   │   main_window.py
│   │   map_view.py
│   │   minimap_panel.py
│   │   __init__.py
│   │   # (adicione aqui outros painéis/diálogos conforme implementar)
│   │
│   ├───models/
│   │   building.py
│   │   city.py
│   │   civilization.py
│   │   diplomacy.py
│   │   game_state.py
│   │   tech.py
│   │   unit.py
│   │   world.py
│   │   __init__.py
│   │
│   └───utils/
│       data_loader.py
│       logger.py
│       perlin_noise.py
│       save_manager.py
│       __init__.py
│
├───logs/
├───saves/
└───tests/
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
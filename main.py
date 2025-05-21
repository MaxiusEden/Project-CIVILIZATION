from PyQt5.QtWidgets import QApplication
from game.controllers.game_controller import GameController
from game.gui.main_window import MainWindow

def main():
    app = QApplication([])
    game_controller = GameController()
    window = MainWindow(game_controller)
    window.show()
    game_controller.new_game()  # ou game_controller.load_game(...) se desejar
    app.exec_()

if __name__ == "__main__":
    main()
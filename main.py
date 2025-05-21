import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox

# Configurar o logger
from game.utils.logger import setup_logger
logger = setup_logger(log_file="logs/game.log")

def main():
    """
    Função principal que inicializa o jogo.
    Gerencia a inicialização da aplicação e captura exceções.
    """
    try:
        # Inicializar a aplicação Qt
        app = QApplication(sys.argv)
        
        # Importações feitas aqui para evitar problemas de importação circular
        # e para que erros de importação sejam capturados pelo try-except
        from game.controllers.game_controller import GameController
        from game.gui.main_window import MainWindow
        
        # Inicializar o controlador do jogo
        logger.info("Inicializando o controlador do jogo")
        game_controller = GameController()
        
        # Inicializar a janela principal
        logger.info("Inicializando a interface gráfica")
        window = MainWindow(game_controller)
        window.show()
        
        # Iniciar um novo jogo
        logger.info("Iniciando um novo jogo")
        game_controller.new_game()  # ou game_controller.load_game(...) se desejar
        
        # Iniciar o loop de eventos (usando a versão não obsoleta)
        return app.exec()
    
    except ImportError as e:
        logger.critical(f"Erro de importação: {e}")
        show_error_message("Erro de Importação", 
                          f"Não foi possível importar um módulo necessário: {e}\n"
                          "Verifique se todas as dependências estão instaladas.")
        return 1
    
    except Exception as e:
        logger.critical(f"Erro crítico: {e}", exc_info=True)
        show_error_message("Erro Crítico", 
                          f"Ocorreu um erro inesperado: {e}\n"
                          "Verifique os logs para mais detalhes.")
        return 1

def show_error_message(title, message):
    """
    Exibe uma mensagem de erro em uma caixa de diálogo.
    
    Args:
        title (str): Título da caixa de diálogo
        message (str): Mensagem de erro
    """
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Critical)
    error_box.setWindowTitle(title)
    error_box.setText(message)
    error_box.exec()

if __name__ == "__main__":
    sys.exit(main())

from PyQt5.QtWidgets import QDockWidget, QAction, QMenu, QToolBar, QMessageBox, QPushButton, QDialog
from PyQt5.QtCore import Qt
from typing import Callable, Optional, Any, List, Type, Dict, Union

class GUIFactory:
    """
    Fábrica para criar componentes da GUI de forma padronizada.
    
    Esta classe fornece métodos estáticos para criar diversos componentes
    da interface gráfica, garantindo consistência visual e comportamental.
    Implementa o padrão Factory para desacoplar a criação de componentes da sua utilização.
    """
    
    @staticmethod
    def create_dock_widget(title: str, widget: Any, parent: Any = None,
                          allowed_areas: int = Qt.AllDockWidgetAreas) -> QDockWidget:
        """
        Cria um widget de dock com configurações padronizadas.
        
        Args:
            title: Título do dock
            widget: Widget a ser colocado no dock
            parent: Widget pai
            allowed_areas: Áreas permitidas para o dock
            
        Returns:
            QDockWidget: O dock widget criado
        """
        dock = QDockWidget(title, parent)
        dock.setWidget(widget)
        dock.setAllowedAreas(allowed_areas)
        dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable)
        return dock
    
    @staticmethod
    def create_action(parent: Any, text: str, slot: Optional[Callable] = None,
                     shortcut: Optional[str] = None, icon: Any = None,
                     tip: Optional[str] = None, checkable: bool = False,
                     checked: bool = False, enabled: bool = True) -> QAction:
        """
        Cria uma ação com configurações padronizadas.
        
        Args:
            parent: Widget pai
            text: Texto da ação
            slot: Função a ser chamada quando a ação for acionada
            shortcut: Atalho de teclado
            icon: Ícone da ação
            tip: Texto de dica
            checkable: Se a ação pode ser marcada/desmarcada
            checked: Estado inicial da ação (se checkable=True)
            enabled: Se a ação está habilitada inicialmente
            
        Returns:
            QAction: A ação criada
        """
        action = QAction(text, parent)
        
        if icon:
            action.setIcon(icon)
        if shortcut:
            action.setShortcut(shortcut)
        if tip:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot:
            action.triggered.connect(slot)
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)
            
        action.setEnabled(enabled)

        return action
    
    @staticmethod
    def create_menu(parent: Any, title: str, actions: Optional[List[Union[QAction, None]]] = None) -> QMenu:
        """
        Cria um menu com ações.
        
        Args:
            parent: Widget pai
            title: Título do menu
            actions: Lista de ações ou None (separadores são representados por None)
        Returns:
            QMenu: O menu criado
        """
        menu = QMenu(title, parent)
        
        if actions:
            for action in actions:
                if action is None:
                    menu.addSeparator()
                else:
                    menu.addAction(action)
                    
        return menu

    @staticmethod
    def create_toolbar(parent: Any, name: str, actions: Optional[List[Union[QAction, None]]] = None) -> QToolBar:
        """
        Cria uma barra de ferramentas.

        Args:
            parent: Widget pai
            name: Nome da barra de ferramentas
            actions: Lista de ações ou None (separadores são representados por None)

        Returns:
            QToolBar: A barra de ferramentas criada
        """
        toolbar = QToolBar(name, parent)
        toolbar.setMovable(True)
        toolbar.setFloatable(True)

        if actions:
            for action in actions:
                if action is None:
                    toolbar.addSeparator()
                else:
                    toolbar.addAction(action)

        return toolbar

    @staticmethod
    def create_message_box(parent: Any, title: str, text: str,
                          icon: int = QMessageBox.Information,
                          buttons: int = QMessageBox.Ok) -> int:
        """
        Cria e exibe uma caixa de mensagem.

        Args:
            parent: Widget pai
            title: Título da caixa de mensagem
            text: Texto da mensagem
            icon: Ícone da caixa de mensagem (QMessageBox.Icon)
            buttons: Botões a serem exibidos (QMessageBox.StandardButtons)

        Returns:
            int: O botão clicado (QMessageBox.StandardButton)
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(buttons)
        return msg_box.exec_()

    @staticmethod
    def create_button(parent: Any, text: str, slot: Optional[Callable] = None,
                     icon: Any = None, tip: Optional[str] = None,
                     enabled: bool = True) -> QPushButton:
        """
        Cria um botão.

        Args:
            parent: Widget pai
            text: Texto do botão
            slot: Função a ser chamada quando o botão for clicado
            icon: Ícone do botão
            tip: Texto de dica
            enabled: Se o botão está habilitado inicialmente

        Returns:
            QPushButton: O botão criado
        """
        button = QPushButton(text, parent)

        if icon:
            button.setIcon(icon)
        if tip:
            button.setToolTip(tip)
            button.setStatusTip(tip)
        if slot:
            button.clicked.connect(slot)

        button.setEnabled(enabled)

        return button

    @staticmethod
    def create_dialog(dialog_class: Type[QDialog], game_controller: Any,
                     parent: Any = None, *args: Any, **kwargs: Any) -> int:
        """
        Cria e exibe um diálogo.

        Args:
            dialog_class: Classe do diálogo a ser criado
            game_controller: Controlador do jogo
            parent: Widget pai
            *args, **kwargs: Argumentos adicionais para o diálogo

        Returns:
            int: O resultado da execução do diálogo
        """
        dialog = dialog_class(game_controller, parent, *args, **kwargs)
        return dialog.exec_()

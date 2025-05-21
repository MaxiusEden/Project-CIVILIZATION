from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QMouseEvent


class MinimapPanel(QWidget):
    """Panel displaying a minimap of the game world."""
    
    # Signal emitted when a location on the minimap is clicked
    location_clicked = pyqtSignal(int, int)
    
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.game_controller = game_controller
        self.setMinimumSize(200, 150)
        self.setMaximumSize(300, 200)
        
        # Camera view rectangle
        self.camera_rect = QRect(0, 0, 0, 0)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def paintEvent(self, event):
        """Paint the minimap."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get world data
        world = self.game_controller.get_world()
        if not world:
            # Draw placeholder if world not available
            painter.fillRect(self.rect(), QColor(0, 0, 0))
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(self.rect(), Qt.AlignCenter, "No Map Data")
            return
        
        # Calculate tile size
        width = self.width()
        height = self.height()
        tile_width = width / world.width
        tile_height = height / world.height
        
        # Draw each tile
        for x in range(world.width):
            for y in range(world.height):
                tile = world.get_tile(x, y)
                if not tile:
                    continue
                
                # Set color based on terrain type
                color = self.get_terrain_color(tile.terrain_type)
                
                # Draw tile
                rect = QRect(
                    int(x * tile_width),
                    int(y * tile_height),
                    int(tile_width + 1),  # +1 to avoid gaps
                    int(tile_height + 1)
                )
                painter.fillRect(rect, color)
                
                # Draw resource indicator if present
                if tile.resource:
                    painter.setPen(Qt.white)
                    painter.drawPoint(
                        int(x * tile_width + tile_width / 2),
                        int(y * tile_height + tile_height / 2)
                    )
        
        # Draw cities
        cities = self.game_controller.get_all_cities()
        for city in cities:
            x, y = city.position
            
            # Set color based on owner
            civ_id = city.owner.id if city.owner else 0
            color = self.get_civilization_color(civ_id)
            
            # Draw city as a circle
            painter.setPen(Qt.black)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(
                int(x * tile_width + tile_width / 4),
                int(y * tile_height + tile_height / 4),
                int(tile_width / 2),
                int(tile_height / 2)
            )
        
        # Draw units (simplified as dots)
        units = self.game_controller.get_all_units()
        for unit in units:
            x, y = unit.x, unit.y
            
            # Set color based on owner
            civ_id = unit.owner.id if unit.owner else 0
            color = self.get_civilization_color(civ_id)
            
            # Draw unit as a small square
            painter.setPen(Qt.black)
            painter.setBrush(QBrush(color))
            painter.drawRect(
                int(x * tile_width + tile_width / 3),
                int(y * tile_height + tile_height / 3),
                int(tile_width / 3),
                int(tile_height / 3)
            )
        
        # Draw camera view rectangle
        if self.camera_rect.isValid():
            painter.setPen(QPen(Qt.white, 2))
            painter.setBrush(QBrush())  # No fill
            painter.drawRect(self.camera_rect)
    
    def get_terrain_color(self, terrain_type):
        """Get color for a terrain type."""
        if terrain_type == "ocean":
            return QColor(0, 50, 200)
        elif terrain_type == "plains":
            return QColor(210, 210, 50)
        elif terrain_type == "grassland":
            return QColor(50, 200, 50)
        elif terrain_type == "desert":
            return QColor(230, 230, 130)
        elif terrain_type == "tundra":
            return QColor(230, 230, 230)
        elif terrain_type == "snow":
            return QColor(255, 255, 255)
        elif terrain_type == "mountain":
            return QColor(130, 130, 130)
        elif terrain_type == "hills":
            return QColor(150, 100, 50)
        elif terrain_type == "forest":
            return QColor(0, 130, 0)
        elif terrain_type == "jungle":
            return QColor(0, 100, 0)
        else:
            return QColor(128, 128, 128)  # Default gray
    
    def get_civilization_color(self, civ_id):
        colors = [
            QColor(255, 0, 0),    # Red
            QColor(0, 0, 255),    # Blue
            QColor(0, 255, 0),    # Green
            QColor(255, 255, 0),  # Yellow
            QColor(255, 0, 255),  # Magenta
            QColor(0, 255, 255),  # Cyan
            QColor(255, 128, 0),  # Orange
            QColor(128, 0, 255),  # Purple
        ]
        index = hash(civ_id) % len(colors) if civ_id else 0
        return colors[index]
    
    def update_minimap(self):
        """Update the minimap when the game state changes."""
        self.update()
    
    def update_camera_rect(self, x, y, width, height):
        """Update the camera view rectangle."""
        world = self.game_controller.get_world()
        if not world:
            return
        
        # Convert world coordinates to minimap coordinates
        minimap_width = self.width()
        minimap_height = self.height()
        
        tile_width = minimap_width / world.width
        tile_height = minimap_height / world.height
        
        self.camera_rect = QRect(
            int(x * tile_width),
            int(y * tile_height),
            int(width * tile_width),
            int(height * tile_height)
        )
        
        self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press events to navigate to clicked location."""
        if event.button() == Qt.LeftButton:
            world = self.game_controller.get_world()
            if not world:
                return
            
            # Convert click position to world coordinates
            x = int(event.x() * world.width / self.width())
            y = int(event.y() * world.height / self.height())
            
            # Emit signal with clicked location
            self.location_clicked.emit(x, y)

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QWheelEvent

from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

import config
from game.utils.perlin_noise import PerlinNoise


class MapGLWidget(QOpenGLWidget):
    """OpenGL widget for rendering the 3D game map."""
    
    # Signals
    tile_clicked = pyqtSignal(int, int)  # x, y coordinates
    
    def __init__(self, game_controller, parent=None):
        super().__init__(parent)
        self.game_controller = game_controller
        
        # Camera settings
        self.camera_x = 0
        self.camera_y = 0
        self.camera_height = config.CAMERA_START_HEIGHT
        self.camera_angle = 45  # degrees
        self.camera_rotation = 0  # degrees
        
        # Rendering settings
        self.show_grid = True
        self.show_resources = True
        self.show_improvements = True
        self.show_units = True
        
        # Mouse tracking
        self.setMouseTracking(True)
        self.last_mouse_pos = None
        self.is_dragging = False
        
        # Textures
        self.textures = {}
        
        # Tile highlighting
        self.highlighted_tile = None
        self.selected_tile = None
    
    def initializeGL(self):
        """Initialize OpenGL settings."""
        glClearColor(0.0, 0.0, 0.3, 1.0)  # Dark blue background (ocean)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Load textures
        self.load_textures()
    
    def resizeGL(self, width, height):
        """Handle widget resize events."""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / height
        gluPerspective(45, aspect, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        """Render the scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        gluLookAt(
            self.camera_x, self.camera_y, self.camera_height,  # Camera position
            self.camera_x, self.camera_y, 0,                   # Look at point
            math.sin(math.radians(self.camera_rotation)),      # Up vector
            math.cos(math.radians(self.camera_rotation)), 
            0
        )
        
        # Rotate the world based on camera rotation
        glRotatef(self.camera_rotation, 0, 0, 1)
        
        # Get world data from game controller
        world = self.game_controller.get_world()
        if not world:
            return
        
        # Render terrain
        self.render_terrain(world)
        
        # Render grid if enabled
        if self.show_grid:
            self.render_grid(world)
        
        # Render resources if enabled
        if self.show_resources:
            self.render_resources(world)
        
        # Render improvements if enabled
        if self.show_improvements:
            self.render_improvements(world)
        
        # Render units if enabled
        if self.show_units:
            self.render_units(world)
        
        # Render cities
        self.render_cities(world)
        
        # Render selection/highlighting
        self.render_selection(world)
    
    def render_terrain(self, world):
        """Render the terrain of the world."""
        for x in range(world.width):
            for y in range(world.height):
                tile = world.get_tile(x, y)
                if not tile:
                    continue
                
                # Set tile color based on terrain type
                terrain_type = tile.terrain_type
                if terrain_type == "ocean":
                    glColor3f(0.0, 0.2, 0.8)
                elif terrain_type == "plains":
                    glColor3f(0.8, 0.8, 0.2)
                elif terrain_type == "grassland":
                    glColor3f(0.2, 0.8, 0.2)
                elif terrain_type == "desert":
                    glColor3f(0.9, 0.9, 0.5)
                elif terrain_type == "tundra":
                    glColor3f(0.9, 0.9, 0.9)
                elif terrain_type == "snow":
                    glColor3f(1.0, 1.0, 1.0)
                elif terrain_type == "mountain":
                    glColor3f(0.5, 0.5, 0.5)
                elif terrain_type == "hills":
                    glColor3f(0.6, 0.4, 0.2)
                elif terrain_type == "forest":
                    glColor3f(0.0, 0.5, 0.0)
                elif terrain_type == "jungle":
                                        glColor3f(0.0, 0.4, 0.0)
                else:
                    glColor3f(0.5, 0.5, 0.5)  # Default gray
                
                # Calculate elevation
                elevation = 0.0
                if terrain_type == "hills":
                    elevation = 0.3
                elif terrain_type == "mountain":
                    elevation = 0.8
                
                # Draw the tile as a quad with appropriate elevation
                self.draw_hex_tile(x, y, elevation)
    
    def draw_hex_tile(self, x, y, elevation=0.0):
        """Draw a hexagonal tile at the given coordinates."""
        # Hexagon geometry
        hex_size = 1.0
        hex_height = hex_size * math.sqrt(3)
        
        # Offset for hex grid
        offset_x = 0 if y % 2 == 0 else hex_size * 1.5
        
        # Calculate center position
        center_x = x * hex_size * 3 + offset_x
        center_y = y * hex_height
        
        # Draw hexagon
        glBegin(GL_POLYGON)
        for i in range(6):
            angle = 2 * math.pi / 6 * i
            vertex_x = center_x + hex_size * math.cos(angle)
            vertex_y = center_y + hex_size * math.sin(angle)
            glVertex3f(vertex_x, vertex_y, elevation)
        glEnd()
    
    def render_grid(self, world):
        """Render grid lines on the map."""
        glColor3f(0.3, 0.3, 0.3)  # Dark gray for grid lines
        glLineWidth(1.0)
        
        for x in range(world.width):
            for y in range(world.height):
                # Calculate hex center
                hex_size = 1.0
                hex_height = hex_size * math.sqrt(3)
                offset_x = 0 if y % 2 == 0 else hex_size * 1.5
                center_x = x * hex_size * 3 + offset_x
                center_y = y * hex_height
                
                # Get tile elevation
                tile = world.get_tile(x, y)
                elevation = 0.0
                if tile:
                    if tile.terrain_type == "hills":
                        elevation = 0.3
                    elif tile.terrain_type == "mountain":
                        elevation = 0.8
                
                # Draw hexagon outline
                glBegin(GL_LINE_LOOP)
                for i in range(6):
                    angle = 2 * math.pi / 6 * i
                    vertex_x = center_x + hex_size * math.cos(angle)
                    vertex_y = center_y + hex_size * math.sin(angle)
                    glVertex3f(vertex_x, vertex_y, elevation + 0.01)  # Slightly above terrain
                glEnd()
    
    def render_resources(self, world):
        """Render resource icons on the map."""
        for x in range(world.width):
            for y in range(world.height):
                tile = world.get_tile(x, y)
                if not tile or not tile.resource:
                    continue
                
                # Calculate hex center
                hex_size = 1.0
                hex_height = hex_size * math.sqrt(3)
                offset_x = 0 if y % 2 == 0 else hex_size * 1.5
                center_x = x * hex_size * 3 + offset_x
                center_y = y * hex_height
                
                # Get tile elevation
                elevation = 0.0
                if tile.terrain_type == "hills":
                    elevation = 0.3
                elif tile.terrain_type == "mountain":
                    elevation = 0.8
                
                # Draw resource icon (simplified as colored cube)
                resource_type = tile.resource
                if resource_type == "iron":
                    glColor3f(0.6, 0.6, 0.6)  # Gray
                elif resource_type == "horses":
                    glColor3f(0.8, 0.6, 0.2)  # Brown
                elif resource_type == "oil":
                    glColor3f(0.1, 0.1, 0.1)  # Black
                elif resource_type == "wheat":
                    glColor3f(1.0, 0.8, 0.0)  # Yellow
                elif resource_type == "cattle":
                    glColor3f(0.8, 0.4, 0.0)  # Brown
                else:
                    glColor3f(1.0, 0.0, 1.0)  # Magenta (for unknown resources)
                
                # Draw a small cube to represent the resource
                self.draw_cube(center_x, center_y, elevation + 0.1, 0.2)
    
    def draw_cube(self, x, y, z, size):
        """Draw a cube at the given position with the given size."""
        half_size = size / 2
        
        # Front face
        glBegin(GL_QUADS)
        glVertex3f(x - half_size, y - half_size, z + half_size)
        glVertex3f(x + half_size, y - half_size, z + half_size)
        glVertex3f(x + half_size, y + half_size, z + half_size)
        glVertex3f(x - half_size, y + half_size, z + half_size)
        glEnd()
        
        # Back face
        glBegin(GL_QUADS)
        glVertex3f(x - half_size, y - half_size, z - half_size)
        glVertex3f(x - half_size, y + half_size, z - half_size)
        glVertex3f(x + half_size, y + half_size, z - half_size)
        glVertex3f(x + half_size, y - half_size, z - half_size)
        glEnd()
        
        # Top face
        glBegin(GL_QUADS)
        glVertex3f(x - half_size, y + half_size, z - half_size)
        glVertex3f(x - half_size, y + half_size, z + half_size)
        glVertex3f(x + half_size, y + half_size, z + half_size)
        glVertex3f(x + half_size, y + half_size, z - half_size)
        glEnd()
        
        # Bottom face
        glBegin(GL_QUADS)
        glVertex3f(x - half_size, y - half_size, z - half_size)
        glVertex3f(x + half_size, y - half_size, z - half_size)
        glVertex3f(x + half_size, y - half_size, z + half_size)
        glVertex3f(x - half_size, y - half_size, z + half_size)
        glEnd()
        
        # Right face
        glBegin(GL_QUADS)
        glVertex3f(x + half_size, y - half_size, z - half_size)
        glVertex3f(x + half_size, y + half_size, z - half_size)
        glVertex3f(x + half_size, y + half_size, z + half_size)
        glVertex3f(x + half_size, y - half_size, z + half_size)
        glEnd()
        
        # Left face
        glBegin(GL_QUADS)
        glVertex3f(x - half_size, y - half_size, z - half_size)
        glVertex3f(x - half_size, y - half_size, z + half_size)
        glVertex3f(x - half_size, y + half_size, z + half_size)
        glVertex3f(x - half_size, y + half_size, z - half_size)
        glEnd()
    
    def render_improvements(self, world):
        """Render tile improvements on the map."""
        for x in range(world.width):
            for y in range(world.height):
                tile = world.get_tile(x, y)
                if not tile or not tile.improvement:
                    continue
                
                # Calculate hex center
                hex_size = 1.0
                hex_height = hex_size * math.sqrt(3)
                offset_x = 0 if y % 2 == 0 else hex_size * 1.5
                center_x = x * hex_size * 3 + offset_x
                center_y = y * hex_height
                
                # Get tile elevation
                elevation = 0.0
                if tile.terrain_type == "hills":
                    elevation = 0.3
                elif tile.terrain_type == "mountain":
                    elevation = 0.8
                
                # Draw improvement (simplified as colored pyramid)
                improvement_type = tile.improvement
                if improvement_type == "farm":
                    glColor3f(0.8, 0.8, 0.0)  # Yellow
                elif improvement_type == "mine":
                    glColor3f(0.5, 0.5, 0.5)  # Gray
                elif improvement_type == "trading_post":
                    glColor3f(0.8, 0.4, 0.0)  # Brown
                else:
                    glColor3f(0.0, 1.0, 1.0)  # Cyan (for unknown improvements)
                
                # Draw a small pyramid to represent the improvement
                self.draw_pyramid(center_x, center_y, elevation + 0.1, 0.3)
    
    def draw_pyramid(self, x, y, z, size):
        """Draw a pyramid at the given position with the given size."""
        half_size = size / 2
        height = size
        
        # Base
        glBegin(GL_QUADS)
        glVertex3f(x - half_size, y - half_size, z)
        glVertex3f(x + half_size, y - half_size, z)
        glVertex3f(x + half_size, y + half_size, z)
        glVertex3f(x - half_size, y + half_size, z)
        glEnd()
        
        # Front face
        glBegin(GL_TRIANGLES)
        glVertex3f(x - half_size, y - half_size, z)
        glVertex3f(x + half_size, y - half_size, z)
        glVertex3f(x, y, z + height)
        glEnd()
        
        # Right face
        glBegin(GL_TRIANGLES)
        glVertex3f(x + half_size, y - half_size, z)
        glVertex3f(x + half_size, y + half_size, z)
        glVertex3f(x, y, z + height)
        glEnd()
        
        # Back face
        glBegin(GL_TRIANGLES)
        glVertex3f(x + half_size, y + half_size, z)
        glVertex3f(x - half_size, y + half_size, z)
        glVertex3f(x, y, z + height)
        glEnd()
        
        # Left face
        glBegin(GL_TRIANGLES)
        glVertex3f(x - half_size, y + half_size, z)
        glVertex3f(x - half_size, y - half_size, z)
        glVertex3f(x, y, z + height)
        glEnd()
    
    def render_units(self, world):
        """Render units on the map."""
        units = self.game_controller.get_all_units()
        for unit in units:
            x, y = unit.x, unit.y
            
            # Calculate hex center
            hex_size = 1.0
            hex_height = hex_size * math.sqrt(3)
            offset_x = 0 if y % 2 == 0 else hex_size * 1.5
            center_x = x * hex_size * 3 + offset_x
            center_y = y * hex_height
            
            # Get tile elevation
            tile = world.get_tile(x, y)
            elevation = 0.0
            if tile:
                if tile.terrain_type == "hills":
                    elevation = 0.3
                elif tile.terrain_type == "mountain":
                    elevation = 0.8
            
            # Set color based on unit owner
            civ_id = unit.owner.id if unit.owner else 0
            colors = [
                (1.0, 0.0, 0.0),  # Red
                (0.0, 0.0, 1.0),  # Blue
                (0.0, 1.0, 0.0),  # Green
                (1.0, 1.0, 0.0),  # Yellow
                (1.0, 0.0, 1.0),  # Magenta
                (0.0, 1.0, 1.0),  # Cyan
                (1.0, 0.5, 0.0),  # Orange
                (0.5, 0.0, 1.0),  # Purple
            ]
            index = hash(civ_id) % len(colors) if civ_id else 0
            color = colors[index]
            glColor3f(*color)
            
            # Draw unit based on type
            unit_type = unit.type
            if unit_type == "warrior" or unit_type == "swordsman":
                self.draw_cylinder(center_x, center_y, elevation + 0.1, 0.3, 0.5)
            elif unit_type == "archer" or unit_type == "crossbowman":
                self.draw_cone(center_x, center_y, elevation + 0.1, 0.3, 0.5)
            elif unit_type == "settler":
                self.draw_sphere(center_x, center_y, elevation + 0.3, 0.3)
            elif unit_type == "worker":
                self.draw_torus(center_x, center_y, elevation + 0.3, 0.3, 0.1)
            else:
                # Default unit representation
                self.draw_sphere(center_x, center_y, elevation + 0.3, 0.25)
    
    def draw_cylinder(self, x, y, z, radius, height):
        """Draw a cylinder at the given position."""
        slices = 12

        # Draw the sides
        glBegin(GL_QUAD_STRIP)
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            glVertex3f(x + radius * math.cos(angle), y + radius * math.sin(angle), z)
            glVertex3f(x + radius * math.cos(angle), y + radius * math.sin(angle), z + height)
        glEnd()

        # Draw the top
        glBegin(GL_POLYGON)
        for i in range(slices):
            angle = 2 * math.pi * i / slices
            glVertex3f(x + radius * math.cos(angle), y + radius * math.sin(angle), z + height)
        glEnd()

        # Draw the bottom
        glBegin(GL_POLYGON)
        for i in range(slices):
            angle = 2 * math.pi * i / slices
            glVertex3f(x + radius * math.cos(angle), y + radius * math.sin(angle), z)
        glEnd()
    
    def draw_cone(self, x, y, z, radius, height):
        """Draw a cone at the given position."""
        slices = 12

        # Draw the sides
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x, y, z + height)  # Apex
        for i in range(slices + 1):
            angle = 2 * math.pi * i / slices
            glVertex3f(x + radius * math.cos(angle), y + radius * math.sin(angle), z)
        glEnd()

        # Draw the base
        glBegin(GL_POLYGON)
        for i in range(slices):
            angle = 2 * math.pi * i / slices
            glVertex3f(x + radius * math.cos(angle), y + radius * math.sin(angle), z)
        glEnd()
    
    def draw_sphere(self, x, y, z, radius):
        """Draw a sphere at the given position."""
        slices = 12
        stacks = 12

        for i in range(stacks):
            lat0 = math.pi * (-0.5 + (i / stacks))
            z0 = radius * math.sin(lat0)
            zr0 = radius * math.cos(lat0)

            lat1 = math.pi * (-0.5 + ((i + 1) / stacks))
            z1 = radius * math.sin(lat1)
            zr1 = radius * math.cos(lat1)

            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * (j / slices)
                x0 = zr0 * math.cos(lng)
                y0 = zr0 * math.sin(lng)
                x1 = zr1 * math.cos(lng)
                y1 = zr1 * math.sin(lng)

                glVertex3f(x + x0, y + y0, z + z0)
                glVertex3f(x + x1, y + y1, z + z1)
            glEnd()
    
    def draw_torus(self, x, y, z, radius, tube_radius):
        """Draw a torus at the given position."""
        sides = 12
        rings = 12

        for i in range(rings):
            angle1 = 2 * math.pi * i / rings
            angle2 = 2 * math.pi * (i + 1) / rings

            glBegin(GL_QUAD_STRIP)
            for j in range(sides + 1):
                angle3 = 2 * math.pi * j / sides

                x1 = (radius + tube_radius * math.cos(angle3)) * math.cos(angle1)
                y1 = (radius + tube_radius * math.cos(angle3)) * math.sin(angle1)
                z1 = tube_radius * math.sin(angle3)

                x2 = (radius + tube_radius * math.cos(angle3)) * math.cos(angle2)
                y2 = (radius + tube_radius * math.cos(angle3)) * math.sin(angle2)
                z2 = tube_radius * math.sin(angle3)

                glVertex3f(x + x1, y + y1, z + z1)
                glVertex3f(x + x2, y + y2, z + z2)
            glEnd()
    
    def render_cities(self, world):
        """Render cities on the map."""
        cities = self.game_controller.get_all_cities()
        for city in cities:
            x, y = city.position

            # Calculate hex center
            hex_size = 1.0
            hex_height = hex_size * math.sqrt(3)
            offset_x = 0 if y % 2 == 0 else hex_size * 1.5
            center_x = x * hex_size * 3 + offset_x
            center_y = y * hex_height

            # Get tile elevation
            tile = world.get_tile(x, y)
            elevation = 0.0
            if tile:
                if tile.terrain_type == "hills":
                    elevation = 0.3
                elif tile.terrain_type == "mountain":
                    elevation = 0.8

            # Set color based on city owner
            civ_id = city.owner.id if city.owner else 0
            colors = [
                (1.0, 0.0, 0.0),  # Red
                (0.0, 0.0, 1.0),  # Blue
                (0.0, 1.0, 0.0),  # Green
                (1.0, 1.0, 0.0),  # Yellow
                (1.0, 0.0, 1.0),  # Magenta
                (0.0, 1.0, 1.0),  # Cyan
                (1.0, 0.5, 0.0),  # Orange
                (0.5, 0.0, 1.0),  # Purple
            ]
            color = colors[civ_id % len(colors)]
            glColor3f(*color)

            # Draw city as a collection of buildings
            self.draw_city(center_x, center_y, elevation, city.size)

    def draw_city(self, x, y, z, size):
        """Draw a city at the given position with the given size."""
        # Main building (center)
        self.draw_cube(x, y, z + 0.2, 0.5)

        # Surrounding buildings based on city size
        building_positions = [
            (0.4, 0.4), (-0.4, 0.4), (0.4, -0.4), (-0.4, -0.4),
            (0.0, 0.6), (0.6, 0.0), (0.0, -0.6), (-0.6, 0.0)
        ]

        for i in range(min(size, len(building_positions))):
            bx, by = building_positions[i]
            building_size = 0.3
            building_height = 0.1 + (i % 3) * 0.1  # Vary heights
            self.draw_cube(x + bx, y + by, z + building_height, building_size)

    def render_selection(self, world):
        """Render selection and highlighting on the map."""
        # Render highlighted tile
        if self.highlighted_tile:
            x, y = self.highlighted_tile
            tile = world.get_tile(x, y)
            if tile:
                # Calculate hex center
                hex_size = 1.0
                hex_height = hex_size * math.sqrt(3)
                offset_x = 0 if y % 2 == 0 else hex_size * 1.5
                center_x = x * hex_size * 3 + offset_x
                center_y = y * hex_height

                # Get tile elevation
                elevation = 0.0
                if tile.terrain_type == "hills":
                    elevation = 0.3
                elif tile.terrain_type == "mountain":
                    elevation = 0.8

                # Draw highlight
                glColor4f(1.0, 1.0, 1.0, 0.3)  # Semi-transparent white
                glLineWidth(2.0)

                # Draw hexagon outline slightly above terrain
                glBegin(GL_LINE_LOOP)
                for i in range(6):
                    angle = 2 * math.pi / 6 * i
                    vertex_x = center_x + hex_size * math.cos(angle)
                    vertex_y = center_y + hex_size * math.sin(angle)
                    glVertex3f(vertex_x, vertex_y, elevation + 0.02)
                glEnd()

        # Render selected tile
        if self.selected_tile:
            x, y = self.selected_tile
            tile = world.get_tile(x, y)
            if tile:
                # Calculate hex center
                hex_size = 1.0
                hex_height = hex_size * math.sqrt(3)
                offset_x = 0 if y % 2 == 0 else hex_size * 1.5
                center_x = x * hex_size * 3 + offset_x
                center_y = y * hex_height

                # Get tile elevation
                elevation = 0.0
                if tile.terrain_type == "hills":
                    elevation = 0.3
                elif tile.terrain_type == "mountain":
                    elevation = 0.8

                # Draw selection
                glColor4f(1.0, 1.0, 0.0, 0.5)  # Semi-transparent yellow
                glLineWidth(3.0)

                # Draw hexagon outline slightly above terrain
                glBegin(GL_LINE_LOOP)
                for i in range(6):
                    angle = 2 * math.pi / 6 * i
                    vertex_x = center_x + hex_size * math.cos(angle)
                    vertex_y = center_y + hex_size * math.sin(angle)
                    glVertex3f(vertex_x, vertex_y, elevation + 0.03)
                glEnd()

    def load_textures(self):
        """Load textures for terrain, units, etc."""
        # This would normally load textures from files
        # For now, we'll use simple colored polygons instead
        pass

    def toggle_grid(self):
        """Toggle grid visibility."""
        self.show_grid = not self.show_grid
        self.update()

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        self.last_mouse_pos = event.pos()

        if event.button() == Qt.LeftButton:
            # Convert screen coordinates to world coordinates and select tile
            world_pos = self.screen_to_world(event.pos())
            if world_pos:
                self.selected_tile = world_pos
                self.tile_clicked.emit(world_pos[0], world_pos[1])
                self.update()
        elif event.button() == Qt.RightButton:
            self.is_dragging = True

    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.RightButton:
            self.is_dragging = False

    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return

        # Handle camera panning with right mouse button
        if self.is_dragging:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()

            # Adjust camera position
            speed = 0.02 * self.camera_height
            self.camera_x -= dx * speed * math.cos(math.radians(self.camera_rotation))
            self.camera_x -= dy * speed * math.sin(math.radians(self.camera_rotation))
            self.camera_y -= dx * speed * math.sin(math.radians(self.camera_rotation))
            self.camera_y += dy * speed * math.cos(math.radians(self.camera_rotation))

            self.update()
        else:
            # Update highlighted tile
            world_pos = self.screen_to_world(event.pos())
            if world_pos != self.highlighted_tile:
                self.highlighted_tile = world_pos
                self.update()

        self.last_mouse_pos = event.pos()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        delta = event.angleDelta().y()
        zoom_factor = 1.0 + (delta / 1200.0)

        # Adjust camera height (zoom)
        self.camera_height /= zoom_factor

        # Clamp camera height
        self.camera_height = max(config.CAMERA_MIN_HEIGHT, 
                                min(config.CAMERA_MAX_HEIGHT, self.camera_height))

        self.update()

    def keyPressEvent(self, event):
        """Handle key press events."""
        # Camera rotation with Q and E keys
        if event.key() == Qt.Key_Q:
            self.camera_rotation = (self.camera_rotation + 15) % 360
            self.update()
        elif event.key() == Qt.Key_E:
            self.camera_rotation = (self.camera_rotation - 15) % 360
            self.update()

    def screen_to_world(self, screen_pos):
        """Convert screen coordinates to world coordinates (tile x, y)."""
        # This is a complex calculation for hexagonal grids
        # Simplified version for prototype
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)

        # Get window coordinates
        winX = float(screen_pos.x())
        winY = float(viewport[3] - screen_pos.y())
        winZ = glReadPixels(int(winX), int(winY), 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]

        # Unproject to get world coordinates
        world_coords = gluUnProject(winX, winY, winZ, modelview, projection, viewport)

        # Convert world coordinates to tile coordinates
        # This is an approximation and would need refinement for actual hexagonal grid
        hex_size = 1.0
        hex_height = hex_size * math.sqrt(3)

        # Rotate coordinates based on camera rotation
        rot_rad = math.radians(self.camera_rotation)
        rot_x = world_coords[0] * math.cos(rot_rad) + world_coords[1] * math.sin(rot_rad)
        rot_y = -world_coords[0] * math.sin(rot_rad) + world_coords[1] * math.cos(rot_rad)

        # Convert to tile coordinates
        y = int(round(rot_y / hex_height))
        offset_x = 0 if y % 2 == 0 else hex_size * 1.5
        x = int(round((rot_x - offset_x) / (hex_size * 3)))

        # Check if coordinates are valid
        world = self.game_controller.get_world()
        if world and 0 <= x < world.width and 0 <= y < world.height:
            return (x, y)
        return None

    def update_map(self):
        """Update the map display when the game state changes."""
        self.update()



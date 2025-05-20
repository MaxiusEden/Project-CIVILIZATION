# game/utils/perlin_noise.py
import math
import random

class PerlinNoise:
    """
    Implementação do algoritmo de Ruído de Perlin para geração de terreno.
    
    Esta classe fornece métodos para gerar mapas de altura usando o algoritmo
    de Ruído de Perlin, que produz padrões naturais e orgânicos.
    """
    
    def __init__(self, seed=None):
        """
        Inicializa o gerador de ruído.
        
        Args:
            seed (int): Semente para o gerador de números aleatórios.
                        Se None, usa uma semente aleatória.
        """
        if seed is None:
            seed = random.randint(0, 1000000)
        
        self.seed = seed
        random.seed(seed)
        
        # Gera uma grade de vetores gradientes aleatórios
        self.gradients = {}
    
    def _get_gradient(self, x, y):
        """
        Obtém um vetor gradiente para as coordenadas especificadas.
        
        Args:
            x (int): Coordenada X.
            y (int): Coordenada Y.
            
        Returns:
            tuple: Vetor gradiente (x, y).
        """
        # Usa um hash consistente para as coordenadas
        key = (x, y)
        
        if key not in self.gradients:
            # Gera um vetor unitário aleatório
            angle = random.uniform(0, 2 * math.pi)
            self.gradients[key] = (math.cos(angle), math.sin(angle))
            
        return self.gradients[key]
    
    def _dot_product(self, ix, iy, x, y):
        """
        Calcula o produto escalar entre o vetor gradiente e o vetor de distância.
        
        Args:
            ix (int): Coordenada X do ponto da grade.
            iy (int): Coordenada Y do ponto da grade.
            x (float): Coordenada X do ponto a ser avaliado.
            y (float): Coordenada Y do ponto a ser avaliado.
            
        Returns:
            float: Produto escalar.
        """
        # Obtém o vetor gradiente
        gradient = self._get_gradient(ix, iy)
        
        # Calcula o vetor de distância
        dx = x - ix
        dy = y - iy
        
        # Retorna o produto escalar
        return dx * gradient[0] + dy * gradient[1]
    
    def _smoothstep(self, t):
        """
        Função de suavização para interpolação.
        
        Args:
            t (float): Valor a ser suavizado (entre 0 e 1).
            
        Returns:
            float: Valor suavizado.
        """
        # Função de suavização de Perlin: 3t^2 - 2t^3
        return t * t * (3 - 2 * t)
    
    def noise(self, x, y):
        """
        Calcula o valor de ruído de Perlin para as coordenadas especificadas.
        
        Args:
            x (float): Coordenada X.
            y (float): Coordenada Y.
            
        Returns:
            float: Valor de ruído entre -1 e 1.
        """
        # Determina os pontos da grade que cercam o ponto (x, y)
        x0 = math.floor(x)
        y0 = math.floor(y)
        x1 = x0 + 1
        y1 = y0 + 1
        
        # Calcula os produtos escalares para os quatro cantos
        dot00 = self._dot_product(x0, y0, x, y)
        dot01 = self._dot_product(x0, y1, x, y)
        dot10 = self._dot_product(x1, y0, x, y)
        dot11 = self._dot_product(x1, y1, x, y)
        
        # Calcula os pesos para interpolação
        sx = self._smoothstep(x - x0)
        sy = self._smoothstep(y - y0)
        
        # Interpola ao longo do eixo x
        nx0 = dot00 * (1 - sx) + dot10 * sx
        nx1 = dot01 * (1 - sx) + dot11 * sx
        
        # Interpola ao longo do eixo y
        n = nx0 * (1 - sy) + nx1 * sy
        
        # Normaliza o resultado para o intervalo [-1, 1]
        return n
    
    def generate_noise_map(self, width, height, scale=1.0, octaves=1, persistence=0.5, lacunarity=2.0):
        """
        Gera um mapa de ruído 2D.
        
        Args:
            width (int): Largura do mapa.
            height (int): Altura do mapa.
            scale (float): Escala do ruído. Valores maiores produzem padrões mais suaves.
            octaves (int): Número de camadas de ruído a serem combinadas.
            persistence (float): Quanto cada octave contribui para o ruído total.
            lacunarity (float): Quanto a frequência aumenta para cada octave.
            
        Returns:
            list: Matriz 2D com valores de ruído entre 0 e 1.
        """
        if scale <= 0:
            scale = 0.0001
            
        # Inicializa o mapa de ruído
        noise_map = [[0 for _ in range(width)] for _ in range(height)]
        
        # Valores para normalização
        min_noise = float('inf')
        max_noise = float('-inf')
        
        # Gera o ruído para cada ponto
        for y in range(height):
            for x in range(width):
                amplitude = 1.0
                frequency = 1.0
                noise_value = 0.0
                
                # Soma várias camadas de ruído
                for i in range(octaves):
                    # Calcula as coordenadas de amostragem
                    sample_x = x / scale * frequency
                    sample_y = y / scale * frequency
                    
                    # Adiciona o ruído ponderado pela amplitude
                    noise_value += self.noise(sample_x, sample_y) * amplitude
                    
                    # Atualiza amplitude e frequência para a próxima octave
                    amplitude *= persistence
                    frequency *= lacunarity
                
                # Atualiza os valores mínimo e máximo
                min_noise = min(min_noise, noise_value)
                max_noise = max(max_noise, noise_value)
                
                # Armazena o valor de ruído
                noise_map[y][x] = noise_value
        
        # Normaliza o mapa de ruído para o intervalo [0, 1]
        for y in range(height):
            for x in range(width):
                # Evita divisão por zero
                if max_noise - min_noise > 0:
                    noise_map[y][x] = (noise_map[y][x] - min_noise) / (max_noise - min_noise)
                else:
                    noise_map[y][x] = 0
        
        return noise_map

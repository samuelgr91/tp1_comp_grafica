# TP1 - Visualização de Árvore Arterial 2D

## Como Executar

### Execução Básica
```bash
python src/main.py
```

### Escolher Dataset Específico
```bash
# Para árvore com 64 segmentos terminais:
python src/main.py "TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP1_2D\Nterm_064"

# Para árvore com 128 segmentos terminais:
python src/main.py "TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP1_2D\Nterm_128"

# Para árvore com 256 segmentos terminais:
python src/main.py "TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP1_2D\Nterm_256"
```

## Controles

### Mouse
- **Botão Esquerdo + Arrastar**: Mover a visualização (pan)
- **Botão Direito + Arrastar**: Girar a árvore
- **Rodinha do Mouse**: Zoom in/out

### Teclado
- **Seta Direita (→)**: Avançar para próximo arquivo
- **Seta Esquerda (←)**: Voltar para arquivo anterior
- **Espaço**: Iniciar/pausar animação automática
- **Seta Cima (↑)**: Aumentar velocidade da animação
- **Seta Baixo (↓)**: Diminuir velocidade da animação
- **R**: Resetar animação
- **ESC**: Sair do programa

## Funcionalidades Implementadas

1. **Leitura de Arquivos VTK**: Carrega coordenadas dos vértices, conexões entre segmentos e raios
2. **Visualização 2D Interativa**: Renderização com OpenGL usando projeção ortográfica
3. **Transformações Geométricas**:
   - Translação (pan)
   - Rotação (2D em torno do eixo Z)
   - Escala (zoom)
4. **Visualização Incremental**: Navegação entre arquivos parciais mostrando crescimento da árvore
5. **Auto-detecção de Datasets**: Sistema detecta automaticamente os parâmetros de qualquer dataset

## Estrutura do Código

- `src/main.py`: Ponto de entrada do programa
- `src/app.py`: Lógica principal da aplicação e controles de interação
- `src/renderer.py`: Renderização OpenGL da árvore
- `src/vtk_loader.py`: Parser de arquivos VTK
- `src/model.py`: Estrutura de dados do modelo 2D
- `src/dataset_utils.py`: Utilitários para auto-detecção de datasets

## Observações

- O sistema detecta automaticamente o número de segmentos terminais e o incremento entre arquivos
- A visualização usa gradiente de cores verde (escuro para ramos finos, brilhante para ramos grossos)
- A árvore é exibida com a raiz no topo, crescendo para baixo

---

# TP2 - Visualização 3D de Árvore Arterial

## Como Executar

```bash
python src/main3d.py
```

### Escolher Dataset 3D
```bash
python src/main3d.py "TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP2_3D\Nterm_128"
python src/main3d.py "TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP2_3D\Nterm_256"
python src/main3d.py "TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP2_3D\Nterm_512"
```

## Controles TP2 (igual TP1 + extras 3D)

### Mouse
- **Botão Esquerdo**: Arrastar = orbita a câmera (árvore no centro)
- **Botão Direito** ou **Shift+Esquerdo**: Arrastar = pan (move a cena lateralmente)
- **Clique** (sem arrastar) = selecionar segmento
- **Rodinha**: Zoom suave (aproxima/afasta)

### Teclado (navegação como TP1)
- **Seta Direita/Esquerda**: Próximo/anterior arquivo (step)
- **Seta Cima/Baixo**: Velocidade da animação
- **Espaço**: Play/pause animação
- **0**: Reset animação (começar do início)

### Teclado (opções TP2)
- **R**: Raio fixo ↔ variável
- **1**: Iluminação Flat
- **2**: Iluminação Smooth
- **T**: Transparência
- **C**: Coloração por depth ↔ radius
- **ESC**: Sair

## Funcionalidades TP2

1. **Estrutura de árvore explícita**: parent_of, children_of, root. Validação (acíclico, 1 pai por nó)
2. **Tubos 3D**: Cada ramo = cilindro (raio fixo) ou frustum (raio variável). Caps só na raiz e folhas (continuidade nas bifurcações)
3. **Mesma lógica do TP1**: raiz → tronco → galhos → ramificações → folhas. Troca de arquivo = mais/menos ramos
4. **Projeção perspectiva** + câmera orbitante
5. **Iluminação** Flat/Smooth, coloração por depth/radius
6. **Animação**: crescimento por ordem BFS (raiz primeiro, galhos surgindo progressivamente)

## Estrutura do Código TP2

- `src/main3d.py`: Ponto de entrada TP2
- `src/app3d.py`: App 3D com câmera orbitante e controles
- `src/renderer3d.py`: Renderização de tubos, iluminação, perspectiva
- `src/vtk_loader_3d.py`: Loader VTK para modelo 3D
- `src/model3d.py`: Modelo 3D com Segment e depth (BFS)
- `src/picking.py`: Ray cast para seleção de segmentos

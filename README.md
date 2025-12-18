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

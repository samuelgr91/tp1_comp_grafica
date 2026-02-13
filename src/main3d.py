"""
TP2 - Visualização 3D de Árvore Arterial
Mesma lógica do TP1, usando dataset TP2_3D.
"""
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app3d import App3D
from src.dataset_utils import auto_detect_dataset


def main():
    base_path = os.path.join("TP_CCO_Pacote_Dados", "TP_CCO_Pacote_Dados", "TP2_3D", "Nterm_128")

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        base_path = sys.argv[1]
        print(f"Usando: {base_path}")

    if not os.path.exists(base_path):
        print(f"Erro: Diretório não encontrado: {base_path}")
        return

    try:
        n_term, initial_step, step_inc = auto_detect_dataset(base_path)
        app = App3D(base_path, n_term_str=n_term, initial_step=initial_step, step_inc=step_inc)
    except Exception as e:
        print(f"Erro ao detectar dataset: {e}")
        app = App3D(base_path, n_term_str="128", initial_step=16, step_inc=16)

    if app.init_gl():
        app.run()
    else:
        print("Falha ao inicializar OpenGL/GLFW")


if __name__ == "__main__":
    main()

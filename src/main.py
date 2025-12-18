import os
import sys


# Garante que a raiz do projeto está no sys.path para importar os módulos corretamente
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app import App

def main():
    # Caminho padrão para os dados
    # Pode ser alterado via linha de comando
    
    base_data_path = r"C:\Users\samuk\OneDrive\Documentos\trabalho_comp_grafica\TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP1_2D\Nterm_256"
    
    # Verifica se foi passado um caminho via linha de comando
    if len(sys.argv) > 1:
        arg_path = sys.argv[1]
        if os.path.exists(arg_path):
            base_data_path = arg_path
            print(f"Usando caminho fornecido: {base_data_path}")
        else:
            print(f"Aviso: Caminho {arg_path} não existe. Usando padrão.")

    if not os.path.exists(base_data_path):
        print(f"Erro: Diretório de dados não encontrado em {base_data_path}")
        print("Verifique os caminhos.")
        # Tenta caminho relativo se estiver rodando da raiz do projeto
        relative_path = os.path.join("TP_CCO_Pacote_Dados", "TP_CCO_Pacote_Dados", "TP1_2D", "Nterm_256")
        if os.path.exists(relative_path):
            base_data_path = relative_path
            print(f"Encontrado em caminho relativo: {base_data_path}")
    
    # Detecta automaticamente os parâmetros do dataset
    from src.dataset_utils import auto_detect_dataset
    try:
        n_term, initial_step, step_inc = auto_detect_dataset(base_data_path)
        app = App(base_data_path, n_term_str=n_term, initial_step=initial_step, step_inc=step_inc)
    except Exception as e:
        print(f"Erro ao detectar dataset automaticamente: {e}")
        print("Usando parâmetros padrão...")
        app = App(base_data_path, n_term_str="064", initial_step=8, step_inc=8)
    
    if app.init_gl():
        app.run()
    else:
        print("Falha ao inicializar OpenGL/GLFW")

if __name__ == "__main__":
    main()

import os
import sys


# Ensure project root is in sys.path for correct module resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app import App

def main():
    # Hardcoded base path for simplicity, but could be arg.
    # User's path: C:\Users\samuk\OneDrive\Documentos\trabalho_comp_grafica\TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP1_2D\Nterm_064
    
    # We try to find the data relative to where we are or use absolute.
    # Let's try to locate the Nterm_064 folder.
    
    base_data_path = r"C:\Users\samuk\OneDrive\Documentos\trabalho_comp_grafica\TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP1_2D\Nterm_256"
    
    # Parse command line arguments for data path
    if len(sys.argv) > 1:
        arg_path = sys.argv[1]
        if os.path.exists(arg_path):
            base_data_path = arg_path
            print(f"Using data path from argument: {base_data_path}")
        else:
            print(f"Warning: Argument path {arg_path} does not exist. Using default.")

    if not os.path.exists(base_data_path):
        print(f"Error: Data directory not found at {base_data_path}")
        print("Please check paths.")
        # Fallback for relative path if running from project root
        relative_path = os.path.join("TP_CCO_Pacote_Dados", "TP_CCO_Pacote_Dados", "TP1_2D", "Nterm_256")
        if os.path.exists(relative_path):
            base_data_path = relative_path
            print(f"Found at relative path: {base_data_path}")
    
    # Nterm_256: steps are 32, 64, 96, ..., 256 (increment of 32)
    app = App(base_data_path, n_term_str="256", initial_step=32, step_inc=32)
    
    if app.init_gl():
        app.run()
    else:
        print("Failed to initialize OpenGL/GLFW")

if __name__ == "__main__":
    main()

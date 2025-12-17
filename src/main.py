import os
import sys
from src.app import App

def main():
    # Hardcoded base path for simplicity, but could be arg.
    # User's path: C:\Users\samuk\OneDrive\Documentos\trabalho_comp_grafica\TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP1_2D\Nterm_064
    
    # We try to find the data relative to where we are or use absolute.
    # Let's try to locate the Nterm_064 folder.
    
    base_data_path = r"C:\Users\samuk\OneDrive\Documentos\trabalho_comp_grafica\TP_CCO_Pacote_Dados\TP_CCO_Pacote_Dados\TP1_2D\Nterm_064"
    
    # If the user wants to switch dataset (e.g. 128), they can change this or we can add argv support.
    
    if not os.path.exists(base_data_path):
        print(f"Error: Data directory not found at {base_data_path}")
        print("Please check paths.")
        # Fallback for relative path if running from project root
        relative_path = os.path.join("TP_CCO_Pacote_Dados", "TP_CCO_Pacote_Dados", "TP1_2D", "Nterm_064")
        if os.path.exists(relative_path):
            base_data_path = relative_path
            print(f"Found at relative path: {base_data_path}")
    
    app = App(base_data_path, n_term_str="064")
    
    if app.init_gl():
        app.run()
    else:
        print("Failed to initialize OpenGL/GLFW")

if __name__ == "__main__":
    main()

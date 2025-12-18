import os
import glob
import re

def auto_detect_dataset(data_dir):
    """
    Detecta automaticamente os arquivos VTK em um diretório e determina:
    - n_term (do nome da pasta ou padrão do arquivo)
    - initial_step (primeiro número de step)
    - step_increment (diferença entre steps consecutivos)
    
    Retorna: (n_term_str, initial_step, step_increment)
    """
    # Encontra todos os arquivos VTK
    vtk_files = glob.glob(os.path.join(data_dir, "*.vtk"))
    
    if not vtk_files:
        raise ValueError(f"Nenhum arquivo VTK encontrado em {data_dir}")
    
    # Extrai números de step dos nomes dos arquivos
    # Padrão: tree2D_Nterm0064_step0008.vtk
    step_numbers = []
    n_term_from_file = None
    
    for filepath in vtk_files:
        filename = os.path.basename(filepath)
        # Procura padrão: Nterm####_step####
        match = re.search(r'Nterm(\d+)_step(\d+)', filename)
        if match:
            if n_term_from_file is None:
                n_term_from_file = match.group(1)
            step_numbers.append(int(match.group(2)))
    
    if not step_numbers:
        raise ValueError(f"Não foi possível interpretar os nomes dos arquivos VTK em {data_dir}")
    
    # Ordena os números de step
    step_numbers.sort()
    
    # Determina o incremento (diferença entre os dois primeiros steps)
    if len(step_numbers) >= 2:
        step_increment = step_numbers[1] - step_numbers[0]
    else:
        step_increment = step_numbers[0]  # Só um arquivo
    
    initial_step = step_numbers[0]
    
    # Tenta pegar n_term do nome da pasta primeiro
    folder_name = os.path.basename(data_dir)
    match = re.search(r'Nterm_(\d+)', folder_name)
    if match:
        n_term_str = match.group(1)
    elif n_term_from_file:
        n_term_str = n_term_from_file
    else:
        # Fallback: usa o número máximo de step
        n_term_str = str(max(step_numbers))
    
    print(f"Auto-detectado: n_term={n_term_str}, initial_step={initial_step}, incremento={step_increment}")
    print(f"Encontrados {len(step_numbers)} arquivos: {step_numbers}")
    
    return n_term_str, initial_step, step_increment

from shiny import App, render, reactive, ui
import shutil
from pathlib import Path

app_ui = ui.page_fluid(
    ui.input_file("file", "Sube un archivo CSV", multiple=False),
    ui.input_text("directory", "Especifica la carpeta de destino", placeholder="Escribe la ruta de la carpeta"),
    ui.output_text_verbatim("test"),
)

def server(input, output, session):
    # Obtiene la ruta del archivo en la carpeta especificada
    @reactive.Calc
    def data_path():
        uploaded_file = input.file()
        selected_directory = input.directory()
        
        if uploaded_file and selected_directory:
            # Convertimos a Path y resolvemos para obtener la ruta absoluta
            try:
                selected_directory_path = Path(selected_directory).resolve(strict=False)
                
                # Verificamos si el directorio existe
                if selected_directory_path.is_dir():
                    destination_path = selected_directory_path / "historic_data.csv"
                    shutil.copy(uploaded_file[0]["datapath"], destination_path)
                    return str(destination_path)
                else:
                    print("La ruta proporcionada no es un directorio válido.")
                    return None
            except Exception as e:
                print(f"Error al procesar la ruta: {e}")
                return None
        return None
    
    @render.text
    def test():
        path = data_path()
        return path

app = App(app_ui, server)
app.run()
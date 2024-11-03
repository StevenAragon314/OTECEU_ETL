import pandas as pd
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

# Interfaz de usuario
app_ui = ui.page_fluid(
    ui.input_file("file_upload", "Selecciona un archivo CSV", accept=[".csv"]),
    ui.input_date_range("daterange", "Selecciona un rango de fechas"),
    ui.output_text("file_status"),
    ui.output_text("file_preview"),
    ui.output_action_button("action_suma", "Siguiente"),
    ui.output_action_button("action_resta", "Anterior"),
    ui.output_text("text_resumen"),
    ui.output_text("text_autor"),
    ui.output_text("text_fecha"),
    ui.output_text("text_title"),
    ui.output_text("text_link_notice"),
    ui.output_text("text_link_img"),
    ui.output_ui("image_output"),
    # ui.output_text("counter")
)

# Función del servidor
def server(input: Inputs, output: Outputs, session: Session):
    index = reactive.Value(0)

    @reactive.Calc
    def data():
        # Verifica si se ha subido un archivo
        if input.file_upload() is not None:
            file_path = input.file_upload()[0]["datapath"]
            try:
                # Cargar el archivo CSV
                df = pd.read_csv(file_path)
                # Filtrar datos
                df = df.loc[df["n_by_text"] >= 4, :]
                if input.daterange()[0] and input.daterange()[1]:
                    df = df.loc[(df["fecha_publicacion_CD"] <= input.daterange()[1]) &
                                (df["fecha_publicacion_CD"] >= input.daterange()[0]), :]
                l_df = len(df)
                print(f"CSV cargado exitosamente con {l_df} registros.")
                return df, l_df, file_path
            except FileNotFoundError:
                print(f"Error: No se encontró el archivo en la ruta {file_path}.")
                return pd.DataFrame(), 0, ""
            except Exception as e:
                print(f"Error al cargar el archivo CSV: {e}")
                return pd.DataFrame(), 0, ""
        else:
            return pd.DataFrame(), 0, ""

    @output
    @render.text
    def file_status():
        _, l_df, _ = data()
        if input.file_upload() is not None and l_df > 0:
            return "Archivo cargado y filtrado exitosamente."
        elif input.file_upload() is not None:
            return "El archivo no contiene registros después del filtrado."
        return "No se ha cargado ningún archivo."

    @output
    @render.text
    def file_preview():
        df, _, _ = data()
        if not df.empty:
            return df.head().to_string()  # Muestra las primeras filas del DataFrame
        return "No hay datos para mostrar."

    # Incrementar el índice
    @reactive.Effect
    @reactive.event(input.action_suma)
    def _aumentar_index():
        if data()[1] > 0:
            nuevo_index = (index() + 1) % data()[1]
            index.set(nuevo_index)

    # Decrementar el índice
    @reactive.Effect
    @reactive.event(input.action_resta)
    def _disminuir_index():
        if data()[1] > 0:
            nuevo_index = (index() - 1) % data()[1]
            index.set(nuevo_index)

    # Función para obtener la fila actual
    def get_current_row():
        if data()[1] > 0:
            return data()[0].iloc[index()]
        else:
            return pd.Series()

    # Salida de imagen
    @output
    @render.ui
    def image_output():
        row = get_current_row()
        imagen_url = row.get('imagen_url', '')
        if imagen_url:
            return ui.HTML(f'<img src="{imagen_url}" alt="Imagen no disponible" style="width:100%; height:100%;" />')
        return ui.HTML("No image available.")

    # Salida de resumen
    @output
    @render.text
    def text_resumen():
        row = get_current_row()
        return row.get('resumen_art', '')

    # Salida de autor
    @output
    @render.text
    def text_autor():
        row = get_current_row()
        return row.get('autor_redacta', '')

    # Salida de fecha
    @output
    @render.text
    def text_fecha():
        row = get_current_row()
        return row.get('fecha_publicacion', '').upper()

    # Salida de título
    @output
    @render.text
    def text_title():
        row = get_current_row()
        return row.get('titulo_articulo', '')

    # Salida de enlace de la noticia
    @output
    @render.text
    def text_link_notice():
        row = get_current_row()
        return row.get('notice_url', '')

    # Salida de enlace de la imagen
    @output
    @render.text
    def text_link_img():
        row = get_current_row()
        return row.get('imagen_url', '')

    # # Salida de actualización de datos
    # @output
    # @render.text
    # @reactive.event(input.action_button)
    # def counter():
    #     try:
    #         ws.scrape_data(data()[2])
    #         return "Datos actualizados exitosamente."
    #     except Exception as e:
    #         return f"Error durante la actualización: {str(e)}"

# Crear la aplicación
app = App(app_ui, server)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run()

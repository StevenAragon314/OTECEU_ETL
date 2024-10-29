from code.app_shiny import run_app
import webbrowser
import threading


def open_browser():
    webbrowser.open_new("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("iniciando aplicación")
    threading.Timer(1, open_browser).start()
    run_app()
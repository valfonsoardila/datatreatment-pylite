from pathlib import Path
import subprocess
import pandas as pd
from tqdm import tqdm
from src.models.platformsSys import PlatformsSys
from src.config import getTypeData
from src.app.logs.logsManager import saveLog

# Función principal para depurar los datos de un DataFrame
def debug(dataframe, path):
    try:
        # Verificar que dataframe sea un DataFrame de pandas
        if not isinstance(dataframe, pd.DataFrame):
            message = "El parámetro dataframe debe ser un DataFrame de pandas🚫"
            return None, message
        else:
            # Si la ruta no contiene al final _clean.csv
            if not path.endswith('_clean.csv'):
                # Obtener la ruta del archivo actual
                ruta_actual = Path(__file__).parent
                # Subir dos niveles
                ruta_dos_niveles_arriba = ruta_actual.parent.parent
                platformsSys = PlatformsSys()
                operatingSystem = platformsSys.get_operatingSystem()
                ruta_exe = (ruta_dos_niveles_arriba / 'app' / 'exe' / 'windows' / 'menuDebug.bat') if operatingSystem == "Windows" else (
                    ruta_dos_niveles_arriba / 'app' / 'exe' / 'linux' / 'menuDebug.sh')
                proceso = subprocess.Popen(ruta_exe, creationflags=subprocess.CREATE_NEW_CONSOLE) if operatingSystem == "Windows" else subprocess.Popen(
                    [f'x-terminal-emulator -e "{ruta_exe}"'], shell=True)
                proceso.wait()
                # obtener la lista de procesos seleccionados por el usuario en el archivo .bat
                ruta = ruta_exe.parent
                with open(ruta / 'selectedProcesses.txt', 'r') as file:
                    lines = file.read().splitlines()
                # Filtrar solo los procesos seleccionados, omitiendo la primera línea y líneas vacías
                selectedProcesses = [line for line in lines if line not in ("Procesos seleccionados:", "")]
                # borrar el archivo temporal selectedProcesses.txt
                (ruta / 'selectedProcesses.txt').unlink()
                # Si el usuario seleccionó alguna opción
                if selectedProcesses:
                    # lista de funciones a ejecutar
                    functions = {
                        "quitar_caracteres_especiales": quitar_caracteres_especiales, # Se toma de tercero
                        "eliminar_filas_duplicadas": eliminar_filas_duplicadas,
                        "eliminar_columnas_duplicadas": eliminar_columnas_duplicadas, # Se toma de primero
                        "eliminar_filas_nulas": eliminar_filas_nulas, # Se toma de segundo
                        "eliminar_columnas_nulas": eliminar_columnas_nulas,
                        "llenar_celdas_vacias": llenar_celdas_vacias,
                        "formatear_fecha": formatear_fecha, # Se toma de cuarto
                        "convertir_a_valor_absoluto": convertir_a_valor_absoluto,
                        "formatear_a_entero": formatear_a_entero
                    }
                    totalProgress = 100
                    # Crear una barra de progreso
                    with tqdm(total=totalProgress, desc="Depurando datos", unit="proceso", bar_format='{desc}: {percentage:.1f}%|{bar}|') as progress_bar:
                        # Iterar sobre cada proceso seleccionado por el usuario
                        for proceso in selectedProcesses:
                            # Obtener la función a ejecutar por su nombre
                            funcion = functions[proceso]
                            # Ejecutar la función
                            dataframe = funcion(dataframe)
                            # Actualizar la barra de progreso
                            progress_bar.update(totalProgress // len(selectedProcesses))
                    message = "Datos depurados con éxito✅🧹"
                    return dataframe, message
            else:
                dataframeDebug = dataframe
                message = "El archivo ya ha sido depurado con anterioridad🕒🧹"
                return dataframeDebug, message
    except Exception as e:
        message = f"Ha ocurrido un error al depurar los datos del DataFrame {e}🚫"
        return None, message

# Formatear valores a enteros
def formatear_a_entero(dataframe):
    """
    Formatea los valores de las columnas especificadas a enteros.

    Parámetros:
        dataframe: El dataframe de Pandas que contiene los datos.
        Diccionario con el tipo de datos y las columnas a formatear.

    Retorno:
        Un nuevo dataframe con los valores de las columnas especificadas formateados a enteros.
    """
    try:
            columns=[]
            keys, values = getTypeData()
            columns = [key for key, value in zip(keys, values) if value == "INT" or value == "BIGINT"]
            logs = []
            for col in columns:
                for i in range(len(dataframe[col])):
                    try:
                        dataframe[col].iloc[i] = int(dataframe[col].iloc[i])
                    except Exception as e:
                        # Guardar posiciones de los valores que no se pudieron formatear y el valor en una lista
                        error = {
                            "message": "Invalid value in column",
                            "column": col,
                            "value": dataframe[col].iloc[i]
                        }
                        logs.append(error)
                        dataframe[col].iloc[i] = 0
            # Guardar los logs en un archivo de texto
            saveLog(logs)
            return dataframe
    except Exception as e:
        print(f"Ha ocurrido un error al formatear los valores a enteros {e}🚫")
        return None

def convert_date(date_str):
    try:
        if 'AM' in date_str or 'PM' in date_str:
            return pd.to_datetime(date_str, format='%d/%m/%Y %I:%M:%S %p', errors='coerce')
        # validar si la fecha tiene solo horas y minutos en formato 24 horas
        elif len(date_str.split(':')) == 2 and '/' in date_str:
            return pd.to_datetime(date_str, format='%d/%m/%Y %H:%M', errors='coerce')
        # validar si la fecha tiene solo horas en formato 24 horas
        elif len(date_str.split(':')) == 1 and '/' in date_str:
            return pd.to_datetime(date_str, format='%d/%m/%Y %H', errors='coerce')
        else:
            return pd.to_datetime(date_str, format='%d/%m/%Y %H:%M:%S', errors='coerce')
    except Exception as e:
        message = f"Error al formatear la fecha: {e}"
        print(message)
        return pd.NaT  # Retorna NaT si hay un error para manejar fechas inválidas en el DataFrame
    
# Formatea las fechas en el dataframe
def formatear_fecha(dataframe):
    """
    Recorre todo el dataframe en busca de columnas con fechas y las formatea al formato timestamp compatible con Cassandra.

    Parámetros:
        dataframe: El dataframe de Pandas que contiene los datos.

    Retorno:
        Un nuevo dataframe con las fechas formateadas como timestamp de Cassandra.
    """
    dataframe['fecha'] = dataframe['fecha'].str.replace(' a. m.', ' AM', regex=False)
    dataframe['fecha'] = dataframe['fecha'].str.replace(' p. m.', ' PM', regex=False)
    dataframe['fecha'] = dataframe['fecha'].apply(convert_date)
    # Convertir a formato ISO 8601 compatible con Cassandra
    dataframe['fecha'] = dataframe['fecha'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    print("Fechas formateadas en el dataframe:", dataframe)
    return dataframe

# Quito caracteres especiales como paréntesis 
def quitar_caracteres_especiales(dataframe):
    """
    Recorre todo el dataframe en busca de caracteres especiales y los elimina, como paréntesis.

    Parámetros:
        dataframe: El dataframe de Pandas que contiene los datos.

    Retorno:
        Un nuevo dataframe con los caracteres especiales eliminados.
    """
    # Eliminar paréntesis si están presentes
    for columna in dataframe.columns:
        if dataframe[columna].dtype == 'object':
            # Quitar paréntesis
            if any(dataframe[columna].str.contains(r'\(|\)')):
                dataframe[columna] = dataframe[columna].str.replace(r'\(|\)', '', regex=True)
            # Quitar tildes y diéresis
            elif any(dataframe[columna].str.contains(r'[áéíóúÁÉÍÓÚ]')):
                dataframe[columna] = dataframe[columna].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    return dataframe

# Elimina filas duplicadas
def eliminar_filas_duplicadas(dataframe):
  """
  Elimina las filas duplicadas del dataframe.

  Parámetros:
    dataframe: El dataframe de Pandas que contiene los datos.

  Retorno:
    Un nuevo dataframe con las filas duplicadas eliminadas.
  """
  return dataframe.drop_duplicates()

# Elimina columnas duplicadas
def eliminar_columnas_duplicadas(dataframe):
    """
    Elimina las columnas duplicadas del dataframe, dejando solo una, la que toma para comparar.

    Parámetros:
      dataframe: El dataframe de Pandas que contiene los datos.

    Retorno:
      Un nuevo dataframe con las columnas duplicadas eliminadas.
    """
    # Transponer el DataFrame para poder comparar las columnas como filas
    transposed_df = dataframe.T

    # Eliminar filas duplicadas en el DataFrame transpuesto
    transposed_df_sin_duplicados = transposed_df.drop_duplicates()

    # Volver a transponer el DataFrame para obtener el formato original
    dataframe_sin_columnas_duplicadas = transposed_df_sin_duplicados.T

    return dataframe_sin_columnas_duplicadas

# Elimina filas con valores nulos
def eliminar_filas_nulas(dataframe):
    """
    Elimina las filas con valores nulos del dataframe.
    
    Parámetros:
        dataframe: El dataframe de Pandas que contiene los datos.
    
    Retorno:
        Un nuevo dataframe con las filas con valores nulos eliminadas.
    """
    return dataframe.dropna()

# Elimina columnas con valores nulos
def eliminar_columnas_nulas(dataframe):
    """
    Elimina las columnas con valores nulos del dataframe.
    
    Parámetros:
        dataframe: El dataframe de Pandas que contiene los datos.
    
    Retorno:
        Un nuevo dataframe con las columnas con valores nulos eliminadas.
    """
    return dataframe.dropna(axis=1)

# Llenar celdas vacías
def llenar_celdas_vacias(dataframe):
    """
    Llenar las celdas vacías en el DataFrame con un valor predeterminado.

    Parámetros:
        dataframe: El DataFrame de Pandas que contiene los datos.

    Retorno:
        Un nuevo DataFrame con las celdas vacías llenas con un valor predeterminado.
    """
    for columna in dataframe.columns:
        if dataframe[columna].isnull().any():
            if dataframe[columna].dtype == 'object':
                dataframe[columna].fillna('', inplace=True)
            elif dataframe[columna].dtype in ['int64', 'float64']:
                dataframe[columna].fillna(0, inplace=True)
    return dataframe

# Cambiar valores inconsistentes
def cambiar_valores_inconsistentes(dataframe, columna, valor_incorrecto, valor_correcto):
    """
    Cambia los valores inconsistentes de una columna específica del dataframe.
    
    Parámetros:
        dataframe: El dataframe de Pandas que contiene los datos.
        columna: El nombre de la columna que se modificará.
        valor_incorrecto: El valor incorrecto que se reemplazará.
        valor_correcto: El valor correcto con el que se reemplazará.
    
    Retorno:
        Un nuevo dataframe con los valores inconsistentes modificados.
    """
    dataframe[columna] = dataframe[columna].replace(valor_incorrecto, valor_correcto)
    return dataframe

# formatear celdas con valores de fechas incorrectas a un formato específico
def formatear_fechas(dataframe, columna, formato):
    """
    Formatea las celdas con valores de fechas incorrectas a un formato específico.
    
    Parámetros:
        dataframe: El dataframe de Pandas que contiene los datos.
        columna: El nombre de la columna que se formateará.
        formato: El formato de fecha al que se convertirán los valores.
    
    Retorno:
        Un nuevo dataframe con las fechas formateadas.
    """
    dataframe[columna] = pd.to_datetime(dataframe[columna], format=formato, errors='coerce')
    return dataframe

# convertir a valor absoluto los valores negativos de una columna
def convertir_a_valor_absoluto(dataframe, columna):
    """
    Convierte a valor absoluto los valores negativos de una columna específica del dataframe.
    
    Parámetros:
        dataframe: El dataframe de Pandas que contiene los datos.
        columna: El nombre de la columna que se modificará.
    
    Retorno:
        Un nuevo dataframe con los valores negativos convertidos a valor absoluto.
    """
    dataframe[columna] = dataframe[columna].abs()
    return dataframe
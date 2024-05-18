# Backend PyLite Cassandra
Backend hecho en python para apache cassandra 

![cassandra](https://github.com/VictorArdila/backend-PyLite-Cassandra/assets/89551043/e0b6e198-ee48-4d2a-a965-38903eebfe81)
# Requisitos para ejecutar el backend de Python

Este proyecto de backend está desarrollado en Python y requiere ciertas dependencias y la versión específica de Python para ejecutarse correctamente.

## Version de python:  `Python 3.11.5`

## Estrucutra del proyecto

El proyecto está estructurado de la siguiente manera:

```bash
backend/
├── apache-cassandra-local/
├── app/
│  ├── bat/
│  │   ├── path_file.bat
│  │   ├── startCassandra.bat
│  ├── dbOperations/
│  │   ├── drop.py
│  │   ├── insert.py
│  │   ├── keyspace.py
│  │   ├── select.py
│  │   ├── table.py
│  │   ├── update.py
│  ├── scripts/
│  │   ├── csvManager.py
│  │   ├── debugCSV.py
│  │   ├── postProcessing.py
├── .env/
├── routes/
│  ├── close.connection.py
│  ├── create.keyspace.py
│  ├── create.table.py
│  ├── delete.table.py
│  ├── insert.data.py
│  ├── select.data.py
│  ├── update.data.py
├── .gitignore
├── config.py
├── connection.py
├── database.py
├── estructuras-cassandra.txt
├── main.py
├── Readme.md
├── requirements.txt
└── server.py
```

## Base de datos local
## `Apache Cassandra 3.11.10`

La base de datos local se encuentra en la carpeta `apache-cassandra-local` y se debe ejecutar en un entorno local para que el backend pueda conectarse a ella.

`Nota: Si la carpeta no existe, debe crearla y descargar la base de datos de Apache Cassandra 3.11.10 en ella.` 
### Enlace de descarga: [Apache Cassandra](https://archive.apache.org/dist/cassandra/3.11.10/)
## Crea un entorno virtual
Se crea un entorno virtual para instalar las dependencias del proyecto. Ejecute los siguientes comandos en la terminal:
```bash
python -m venv venv
```
Activar el entorno virtual
```bash
env/Scripts/activate
```
## Dependencias

Las dependencias del proyecto pueden instalarse utilizando pip. Ejecute el siguiente comando en su entorno virtual:

```bash
pip install -r requeriments.txt
```

## Comandos de ayuda

### Lista de utilidades: <img src="https://github.com/VictorArdila/VictorArdila/assets/89551043/25d307e3-ef06-41e0-8cb1-a979f4f130ac" alt="GitFlow" width="25" height="25"> [Git flow](https://github.com/VictorArdila/VictorArdila/blob/main/doc/GitFlow.md)

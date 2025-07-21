import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================
#  CONEXAO COM MYSQL
# =============================================================
def criar_conexao():
    try:
        conexao = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            port=int(os.getenv("MYSQL_PORT", 3306))
        )
        if conexao.is_connected():
            print("Conexão realizada")
            return conexao
    except mysql.connector.Error as err:
        print(f"Erro ao conectar: {err}")
        return None

# services/sql_sync.py
import pyodbc
import pandas as pd


class SQLServerSync:
    def __init__(self, backup_path):
        self.backup_path = backup_path

    def restore_backup(self):
        # Restaura backup temporariamente
        pass

    def get_responsaveis(self):
        # Query para buscar responsáveis
        query = """
        SELECT CPF, Nome, CodigoAluno 
        FROM ResponsaveisFinanceiros
        """
        return pd.read_sql(query, self.conn)

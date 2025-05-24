import os
import logging

logger = logging.getLogger(__name__)

def load_sql_file(sql_dir: str,  query_name: str) -> str:
        sql_path = os.path.join(sql_dir, f"{query_name}.sql")

        if not os.path.exists(sql_path):
            logger.warning(f"SQL script not found: {sql_path}")

            raise FileNotFoundError(f"SQL script '{query_name}.sql' not found")
        
        try:
            with open(sql_path, encoding="utf-8") as f:
                sql_text = f.read()

                logger.info(f"Loaded SQL script: {sql_path}")

                return sql_text
        except Exception as e:
            logger.error(f"Error reading SQL script {sql_path}: {e}")
            raise
"""Database client."""
from typing import List
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from clients.log import LOGGER


class Database:
    """Database client."""

    def __init__(self, uri: str, args: dict):
        self.engines = {
            'analytics': create_engine(
                f'{uri}/analytics',
                connect_args=args,
                echo=False
            ),
            'blog': create_engine(
                f'{uri}/hackers_prod',
                connect_args=args,
                echo=False
            )
        }

    def _table(self, table_name: str, database_name='analytics') -> Table:
        return Table(
            table_name,
            MetaData(bind=self.engines[database_name]),
            autoload=True
        )

    @LOGGER.catch
    def execute_queries(self, queries: dict, database_name='blog') -> dict:
        """Execute SQL query."""
        results = {}
        for k, v in queries.items():
            query_result = self.engines[database_name].execute(v)
            results[k] = f'{query_result.rowcount} rows affected.'
        return results

    @LOGGER.catch
    def execute_query(self, query: str, database_name='blog'):
        """Execute single SQL query."""
        result = self.engines[database_name].execute(query)
        return result

    @LOGGER.catch
    def execute_query_from_file(self, sql_file: str, database_name='blog'):
        """Execute single SQL query."""
        query = open(sql_file, 'r').read()
        result = self.engines[database_name].execute(query)
        return result

    @LOGGER.catch
    def fetch_records(self, query, table_name='analytics', database_name=None) -> List[str]:
        """Fetch all rows via query."""
        rows = self.engines[database_name].execute(query).fetchall()
        return [row.items() for row in rows]

    @LOGGER.catch
    def fetch_record(self, query, table_name='analytics', database_name=None) -> str:
        """Fetch row via query."""
        return self.engines[database_name].execute(query).fetch()

    @LOGGER.catch
    def insert_records(self, rows, table_name=None, database_name=None, replace=None):
        """Insert rows into table."""
        if replace:
            self.engines[database_name].execute(f'TRUNCATE TABLE {table_name}')
        table = self._table(table_name)
        self.engines[database_name].execute(table.insert(), rows)
        return f'Inserted {len(rows)} into {table.name}.'

    @LOGGER.catch
    def update_post_image(self, image: str, post: str) -> dict:
        """Set post feature image to desired image."""
        sql = f"UPDATE posts SET feature_image = '{image}' WHERE id = '{post}';"
        self.execute_query(sql)
        return {post: image}

    def insert_dataframe(self, df, table_name=None, database_name='analytics', exists_action='append'):
        df.to_sql(table_name, self.engines[database_name], if_exists=exists_action)
        return df.to_json(orient='records')

    @staticmethod
    def _construct_response(affected_rows) -> str:
        """Summarize results of an executed query."""
        return f'Modified {affected_rows} rows.'

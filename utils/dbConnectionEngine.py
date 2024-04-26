from sqlalchemy import create_engine
import os


class dbConnectionEngine:
    def get_engine(self):
        url = os.getenv("URL")
        engine = create_engine(url, pool_size=50, echo=False)
        return engine
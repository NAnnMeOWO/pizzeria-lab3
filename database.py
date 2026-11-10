from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///pizzeria.db"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    #Создаёт все таблицы по моделям.
    SQLModel.metadata.create_all(engine)


def get_session():
    #Открывает сессию для запросов.
    with Session(engine) as session:
        yield session
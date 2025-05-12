from sqlalchemy import create_engine, Column, Integer, Boolean, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Настройка базы данных SQLite и ORM
engine = create_engine("sqlite:///eetk_event.db", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Code(Base):
    __tablename__ = 'codes'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False)
    code = Column(String, nullable=False)
    is_used = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Code(telegram_id={self.telegram_id}, code={self.code}, is_used={self.is_used})>"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    count_stars = Column(Integer, default=0)
    is_apocalypse_quiz_complete = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, is_admin={self.is_admin}, count_stars={self.count_stars})>"


# Инициализация базы
def init_db():
    Base.metadata.create_all(engine)


#-----------------------------------------------------------------------------------------------------------------------
# USER CRUD
#-----------------------------------------------------------------------------------------------------------------------

def add_user(telegram_id: int, is_admin=False, count_stars=0,is_apocalypse_quiz_complete=False):
    session = Session()
    existing = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not existing:
        user = User(telegram_id=telegram_id, is_admin=is_admin, count_stars=count_stars,is_apocalypse_quiz_complete = is_apocalypse_quiz_complete)
        session.add(user)
        session.commit()
    session.close()

def update_user(telegram_id: int, is_admin=None, count_stars=None,is_apocalypse_quiz_complete=None):
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        if is_admin is not None:
            user.is_admin = is_admin
        if count_stars is not None:
            user.count_stars = count_stars
        if count_stars is not None:
            user.is_apocalypse_quiz_complete = is_apocalypse_quiz_complete
        session.commit()
    session.close()

def get_user(telegram_id: int):
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    session.close()
    return user

def delete_user(telegram_id: int):
    session = Session()
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if user:
        session.delete(user)
        session.commit()
    session.close()

def get_all_users():
    session = Session()
    users = session.query(User).all()
    session.close()
    return users

#-----------------------------------------------------------------------------------------------------------------------
# CODE CRUD
#-----------------------------------------------------------------------------------------------------------------------

def update_code(code_id: int, is_used: bool):
    session = Session()
    code = session.query(Code).filter_by(id=code_id).first()
    if code:
        code.is_used = is_used
        session.commit()
    session.close()

def get_code(code_id: int):
    session = Session()
    code = session.query(Code).filter_by(id=code_id).first()
    session.close()
    return code

def delete_code(code_id: int):
    session = Session()
    code = session.query(Code).filter_by(id=code_id).first()
    if code:
        session.delete(code)
        session.commit()
    session.close()

def add_code(telegram_id: int, code: str, is_used: bool = False):
    session = Session()
    new_code = Code(telegram_id=telegram_id, code=code, is_used=is_used)
    session.add(new_code)
    session.commit()
    session.close()
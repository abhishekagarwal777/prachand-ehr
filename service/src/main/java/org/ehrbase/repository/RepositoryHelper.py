from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert

class RepositoryHelper:
    @staticmethod
    def execute_bulk_insert(session: Session, record_stream: iter, table: Table):
        try:
            # Collect records to be inserted
            records = list(record_stream)

            # Using the insert statement to perform a bulk insert
            stmt = insert(table).values(records)
            session.execute(stmt)

            # Commit the transaction
            session.commit()
        except SQLAlchemyError as e:
            # Rollback in case of error
            session.rollback()
            raise InternalServerException(str(e))

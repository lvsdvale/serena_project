"""Implement updata stock tool"""

import json

from langchain.tools import tool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@tool
def update_compartment_stock(
    database_url: str, stock_id: int, quantity_used: int
) -> str:
    """
    Updates the stock amount for a given stock_id by subtracting the used quantity.

    Parameters:
        database_url (str): SQLAlchemy database connection URL.
        stock_id (int): ID of the stock compartment to update.
        quantity_used (int): The quantity of medication to subtract from the current stock.

    Returns:
        str: A success message with the new stock amount, or an error message if the operation fails.
    """
    try:
        engine = create_engine(database_url, echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()

        select_query = text("SELECT amount FROM compartment WHERE stock_id = :stock_id")
        result = session.execute(select_query, {"stock_id": stock_id}).fetchone()

        if result is None:
            return json.dumps(
                {"error": f"Stock ID {stock_id} not found"}, ensure_ascii=False
            )

        current_amount = result[0]
        new_amount = current_amount - quantity_used

        if new_amount < 0:
            return json.dumps(
                {
                    "error": f"Not enough stock: current amount is {current_amount}, tried to subtract {quantity_used}"
                },
                ensure_ascii=False,
            )

        update_query = text(
            "UPDATE compartment SET amount = :new_amount WHERE stock_id = :stock_id"
        )
        session.execute(update_query, {"new_amount": new_amount, "stock_id": stock_id})
        session.commit()

        return json.dumps(
            {
                "message": "Stock updated successfully",
                "stock_id": stock_id,
                "previous_amount": current_amount,
                "new_amount": new_amount,
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        return json.dumps(
            {"error": f"Error updating stock: {str(e)}"}, ensure_ascii=False
        )

    finally:
        session.close()


from enum import Enum



class TransactionType(Enum):
    TOPUP = "TOPUP"
    SPEND = "SPEND"
    BONUS = "BONUS"

    # SYSTEM
    SYSTEM_CREDIT = "SYSTEM_CREDIT"
    SYSTEM_DEBIT = "SYSTEM_DEBIT"
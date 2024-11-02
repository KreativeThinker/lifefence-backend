from tortoise import fields, models
from typing import Optional
from pydantic import BaseModel, condecimal
from datetime import datetime
from enum import Enum

class ExpenseCategory(str, Enum):
    FOOD = "food"
    TRANSPORTATION = "transportation"
    ACCOMMODATION = "accommodation"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    OTHER = "other"

class Expense(models.Model):
    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField()
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    category = fields.CharEnumField(ExpenseCategory)
    description = fields.CharField(max_length=255)
    location = fields.JSONField(null=True)  # Store latitude and longitude
    date = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "expenses"

class Budget(models.Model):
    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField()
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    start_date = fields.DateField()
    end_date = fields.DateField()
    category = fields.CharEnumField(ExpenseCategory, null=True)  # Optional category-specific budget
    
    class Meta:
        table = "budgets"
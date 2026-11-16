import pytest
from app.sql_guard import validate_readonly_sql

def test_select_allowlisted(): assert "LIMIT" in validate_readonly_sql("SELECT * FROM business_metrics")
def test_blocks_delete():
    with pytest.raises(ValueError): validate_readonly_sql("DELETE FROM business_metrics")
def test_blocks_other_tables():
    with pytest.raises(ValueError): validate_readonly_sql("SELECT * FROM users")
def test_blocks_multiple_statements():
    with pytest.raises(ValueError): validate_readonly_sql("SELECT * FROM business_metrics; DROP TABLE business_metrics")

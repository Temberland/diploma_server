def test_upload_success(auth_client):
    response = auth_client.post("/sync/upload", json={
        "operations": [
            {
                "id": 1,
                "sum": "1500.00",
                "operation_type": "expense",
                "account_id": 1,
                "is_deleted": 0,
                "version": 1
            }
        ],
        "accounts": [
            {
                "id": 1,
                "name": "Основной счёт",
                "balance": "50000.00",
                "currency": "R",
                "account_type": "debit"
            }
        ],
        "categories": [],
        "limits": [],
        "patterns": [],
        "fixed_expenses": []
    })
    assert response.status_code == 200


def test_restore_success(auth_client):
    # Сначала загружаем данные
    auth_client.post("/sync/upload", json={
        "accounts": [{"id": 1, "name": "Счёт", "balance": "1000.00", "currency": "R", "account_type": "debit"}],
        "operations": [], "categories": [], "limits": [], "patterns": [], "fixed_expenses": []
    })
    # Потом восстанавливаем
    response = auth_client.get("/sync/restore")
    assert response.status_code == 200
    data = response.json()
    assert "accounts" in data
    assert len(data["accounts"]) == 1
    assert data["accounts"][0]["name"] == "Счёт"
    assert data["accounts"][0]["balance"] == "1000.00"  # расшифрованное


def test_soft_delete(auth_client):
    """Удалённые операции не возвращаются при восстановлении"""
    auth_client.post("/sync/upload", json={
        "operations": [
            {"id": 1, "sum": "500.00", "operation_type": "expense", "account_id": 1, "is_deleted": 0, "version": 1},
            {"id": 2, "sum": "300.00", "operation_type": "expense", "account_id": 1, "is_deleted": 1, "version": 1},
        ],
        "accounts": [], "categories": [], "limits": [], "patterns": [], "fixed_expenses": []
    })
    response = auth_client.get("/sync/restore")
    operations = response.json()["operations"]
    assert len(operations) == 1
    assert operations[0]["id"] == 1


def test_conflict_resolution(auth_client):
    """Запись с большей версией побеждает"""
    auth_client.post("/sync/upload", json={
        "operations": [{"id": 1, "sum": "100.00", "operation_type": "expense", "account_id": 1, "is_deleted": 0, "version": 1}],
        "accounts": [], "categories": [], "limits": [], "patterns": [], "fixed_expenses": []
    })
    # Отправляем ту же операцию с большей версией и другой суммой
    auth_client.post("/sync/upload", json={
        "operations": [{"id": 1, "sum": "999.00", "operation_type": "expense", "account_id": 1, "is_deleted": 0, "version": 5}],
        "accounts": [], "categories": [], "limits": [], "patterns": [], "fixed_expenses": []
    })
    response = auth_client.get("/sync/restore")
    ops = response.json()["operations"]
    assert ops[0]["sum"] == "999.00"


def test_upload_unauthorized(client):
    response = client.post("/sync/upload", json={})
    assert response.status_code == 401


def test_restore_unauthorized(client):
    response = client.get("/sync/restore")
    assert response.status_code == 401

def test_list_tasks_loads_tags_without_n_plus_one(db_session):
    from sqlalchemy import event
    from app.services.task_service import list_tasks
    from app.models import Tag, Task

    for i in range(3):
        tag = Tag(name=f"tag{i}")
        task = Task(title=f"할 일 {i}", tags=[tag])
        db_session.add(task)
    db_session.commit()

    queries = []

    @event.listens_for(db_session.bind, "before_cursor_execute")
    def record(conn, cursor, statement, *args):
        queries.append(statement)

    list_tasks(db_session)

    # tasks 쿼리 1회 + tags IN 쿼리 1회 = 2회 이하
    assert len(queries) <= 2


def test_create_and_list(client):
    res = client.post("/tasks", json={"title": "테스트 할 일", "tags": ["개인", "긴급"]})
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "테스트 할 일"
    assert {t["name"] for t in body["tags"]} == {"개인", "긴급"}

    res = client.get("/tasks")
    assert res.status_code == 200
    tasks = res.json()
    assert len(tasks) == 1
    assert tasks[0]["tags"]

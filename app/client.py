from typing import Any

import httpx


class PlankaClient:
    def __init__(self, base_url: str, token: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._client = httpx.Client(timeout=30.0)

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _get(self, path: str) -> dict[str, Any]:
        response = self._client.get(f"{self.base_url}{path}", headers=self._headers())
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def _post(self, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self._client.post(f"{self.base_url}{path}", json=data or {}, headers=self._headers())
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def _patch(self, path: str, data: dict[str, Any]) -> dict[str, Any]:
        response = self._client.patch(f"{self.base_url}{path}", json=data, headers=self._headers())
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def _delete(self, path: str) -> dict[str, Any]:
        response = self._client.delete(f"{self.base_url}{path}", headers=self._headers())
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def _upload(self, path: str, file_path: str) -> dict[str, Any]:
        with open(file_path, "rb") as f:
            files = {"file": f}
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            response = self._client.post(f"{self.base_url}{path}", files=files, headers=headers)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    # Authentication
    def login(self, email_or_username: str, password: str) -> str:
        response = self._client.post(
            f"{self.base_url}/api/access-tokens",
            json={"emailOrUsername": email_or_username, "password": password},
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        self.token = response.json()["item"]
        return self.token  # type: ignore[return-value]

    def logout(self) -> dict[str, Any]:
        return self._delete("/api/access-tokens/me")

    # Projects
    def get_projects(self) -> list[dict[str, Any]]:
        return self._get("/api/projects")["items"]  # type: ignore[no-any-return]

    def get_project(self, project_id: str) -> dict[str, Any]:
        return self._get(f"/api/projects/{project_id}")

    def create_project(self, name: str) -> dict[str, Any]:
        return self._post("/api/projects", {"name": name})["item"]

    def update_project(self, project_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/projects/{project_id}", kwargs)["item"]

    def delete_project(self, project_id: str) -> dict[str, Any]:
        return self._delete(f"/api/projects/{project_id}")

    # Boards
    def create_board(self, project_id: str, name: str, position: float) -> dict[str, Any]:
        return self._post(f"/api/projects/{project_id}/boards", {"name": name, "position": position})["item"]

    def get_board(self, board_id: str) -> dict[str, Any]:
        return self._get(f"/api/boards/{board_id}")

    def update_board(self, board_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/boards/{board_id}", kwargs)["item"]

    def delete_board(self, board_id: str) -> dict[str, Any]:
        return self._delete(f"/api/boards/{board_id}")

    # Lists
    def create_list(self, board_id: str, name: str, position: float) -> dict[str, Any]:
        return self._post(f"/api/boards/{board_id}/lists", {"name": name, "position": position})["item"]

    def get_list(self, list_id: str) -> dict[str, Any]:
        return self._get(f"/api/lists/{list_id}")

    def update_list(self, list_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/lists/{list_id}", kwargs)["item"]

    def delete_list(self, list_id: str) -> dict[str, Any]:
        return self._delete(f"/api/lists/{list_id}")

    def sort_list(self, list_id: str) -> dict[str, Any]:
        return self._post(f"/api/lists/{list_id}/sort")

    # Cards
    def create_card(self, list_id: str, name: str, position: float, **kwargs: Any) -> dict[str, Any]:
        return self._post(f"/api/lists/{list_id}/cards", {"name": name, "position": position, **kwargs})["item"]

    def get_cards(self, list_id: str) -> list[dict[str, Any]]:
        return self._get(f"/api/lists/{list_id}/cards")["items"]  # type: ignore[no-any-return]

    def get_card(self, card_id: str) -> dict[str, Any]:
        return self._get(f"/api/cards/{card_id}")["item"]

    def update_card(self, card_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/cards/{card_id}", kwargs)["item"]

    def delete_card(self, card_id: str) -> dict[str, Any]:
        return self._delete(f"/api/cards/{card_id}")

    def duplicate_card(self, card_id: str, position: float) -> dict[str, Any]:
        return self._post(f"/api/cards/{card_id}/duplicate", {"position": position})["item"]

    def move_card(self, card_id: str, list_id: str, position: float) -> dict[str, Any]:
        return self.update_card(card_id, listId=list_id, position=position)

    # Labels
    def create_label(self, board_id: str, name: str, color: str, position: float) -> dict[str, Any]:
        return self._post(f"/api/boards/{board_id}/labels", {"name": name, "color": color, "position": position})[
            "item"
        ]

    def update_label(self, label_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/labels/{label_id}", kwargs)["item"]

    def delete_label(self, label_id: str) -> dict[str, Any]:
        return self._delete(f"/api/labels/{label_id}")

    def add_label_to_card(self, card_id: str, label_id: str) -> dict[str, Any]:
        return self._post(f"/api/cards/{card_id}/card-labels", {"labelId": label_id})["item"]

    def remove_label_from_card(self, card_id: str, label_id: str) -> dict[str, Any]:
        return self._delete(f"/api/cards/{card_id}/card-labels/labelId:{label_id}")

    # Task Lists
    def create_task_list(self, card_id: str, name: str, position: float) -> dict[str, Any]:
        return self._post(f"/api/cards/{card_id}/task-lists", {"name": name, "position": position})["item"]

    def get_task_list(self, task_list_id: str) -> dict[str, Any]:
        return self._get(f"/api/task-lists/{task_list_id}")

    def update_task_list(self, task_list_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/task-lists/{task_list_id}", kwargs)["item"]

    def delete_task_list(self, task_list_id: str) -> dict[str, Any]:
        return self._delete(f"/api/task-lists/{task_list_id}")

    # Tasks
    def create_task(self, task_list_id: str, name: str, position: float) -> dict[str, Any]:
        return self._post(f"/api/task-lists/{task_list_id}/tasks", {"name": name, "position": position})["item"]

    def update_task(self, task_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/tasks/{task_id}", kwargs)["item"]

    def delete_task(self, task_id: str) -> dict[str, Any]:
        return self._delete(f"/api/tasks/{task_id}")

    # Comments
    def create_comment(self, card_id: str, text: str) -> dict[str, Any]:
        return self._post(f"/api/cards/{card_id}/comments", {"text": text})["item"]

    def get_comments(self, card_id: str) -> list[dict[str, Any]]:
        return self._get(f"/api/cards/{card_id}/comments")["items"]  # type: ignore[no-any-return]

    def update_comment(self, comment_id: str, text: str) -> dict[str, Any]:
        return self._patch(f"/api/comments/{comment_id}", {"text": text})["item"]

    def delete_comment(self, comment_id: str) -> dict[str, Any]:
        return self._delete(f"/api/comments/{comment_id}")

    # Attachments
    def create_attachment(self, card_id: str, file_path: str) -> dict[str, Any]:
        return self._upload(f"/api/cards/{card_id}/attachments", file_path)["item"]

    def update_attachment(self, attachment_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/attachments/{attachment_id}", kwargs)["item"]

    def delete_attachment(self, attachment_id: str) -> dict[str, Any]:
        return self._delete(f"/api/attachments/{attachment_id}")

    # Card Memberships
    def add_member_to_card(self, card_id: str, user_id: str) -> dict[str, Any]:
        return self._post(f"/api/cards/{card_id}/card-memberships", {"userId": user_id})["item"]

    def remove_member_from_card(self, card_id: str, user_id: str) -> dict[str, Any]:
        return self._delete(f"/api/cards/{card_id}/card-memberships/userId:{user_id}")

    # Board Memberships
    def add_member_to_board(self, board_id: str, user_id: str, role: str = "editor") -> dict[str, Any]:
        return self._post(f"/api/boards/{board_id}/board-memberships", {"userId": user_id, "role": role})["item"]

    def update_board_membership(self, membership_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/board-memberships/{membership_id}", kwargs)["item"]

    def remove_board_membership(self, membership_id: str) -> dict[str, Any]:
        return self._delete(f"/api/board-memberships/{membership_id}")

    # Users
    def get_users(self) -> list[dict[str, Any]]:
        return self._get("/api/users")["items"]  # type: ignore[no-any-return]

    def get_user(self, user_id: str) -> dict[str, Any]:
        return self._get(f"/api/users/{user_id}")["item"]

    def create_user(self, email: str, password: str, name: str, username: str | None = None) -> dict[str, Any]:
        data: dict[str, Any] = {"email": email, "password": password, "name": name}
        if username:
            data["username"] = username
        return self._post("/api/users", data)["item"]

    def update_user(self, user_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/users/{user_id}", kwargs)["item"]

    def delete_user(self, user_id: str) -> dict[str, Any]:
        return self._delete(f"/api/users/{user_id}")

    # Notifications
    def get_notifications(self) -> list[dict[str, Any]]:
        return self._get("/api/notifications")["items"]  # type: ignore[no-any-return]

    def get_notification(self, notification_id: str) -> dict[str, Any]:
        return self._get(f"/api/notifications/{notification_id}")["item"]

    def update_notification(self, notification_id: str, **kwargs: Any) -> dict[str, Any]:
        return self._patch(f"/api/notifications/{notification_id}", kwargs)["item"]

    def read_all_notifications(self) -> dict[str, Any]:
        return self._post("/api/notifications/read-all")

    # Actions/Activity
    def get_board_actions(self, board_id: str) -> list[dict[str, Any]]:
        return self._get(f"/api/boards/{board_id}/actions")["items"]  # type: ignore[no-any-return]

    def get_card_actions(self, card_id: str) -> list[dict[str, Any]]:
        return self._get(f"/api/cards/{card_id}/actions")["items"]  # type: ignore[no-any-return]

    # Config
    def get_config(self) -> dict[str, Any]:
        return self._get("/api/config")

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "PlankaClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

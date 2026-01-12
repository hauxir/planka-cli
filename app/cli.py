import os
from typing import Any

import click
from rich.console import Console
from rich.table import Table

from app import config
from app.client import PlankaClient

console = Console()


def get_client() -> PlankaClient:
    base_url = os.environ.get("PLANKA_URL") or config.get_url()
    if not base_url:
        console.print("[red]Error: No Planka URL configured. Run 'planka login' first.[/red]")
        raise SystemExit(1)
    token = os.environ.get("PLANKA_TOKEN") or config.get_token()
    return PlankaClient(base_url, token)


@click.group()
def main() -> None:
    """Planka CLI - Manage your Planka boards from the command line."""


# === Authentication ===


@main.command()
@click.option("--url", "-s", help="Planka server URL")
@click.option("--username", "-u", help="Email or username")
@click.option("--password", "-p", help="Password", hide_input=True)
def login(url: str | None, username: str | None, password: str | None) -> None:
    """Login and save credentials."""
    # Prompt for URL if not provided
    if not url:
        current_url = config.get_url()
        if current_url:
            url = click.prompt("Planka URL", default=current_url)
        else:
            url = click.prompt("Planka URL (e.g. https://planka.example.com)")
    config.set_url(url)

    # Prompt for credentials
    if not username:
        username = click.prompt("Username/Email")
    if not password:
        password = click.prompt("Password", hide_input=True)

    client = PlankaClient(url)
    token = client.login(username, password)
    client.close()

    config.set_token(token)
    console.print(f"[green]Login successful![/green]")
    console.print(f"Config saved to {config.CONFIG_FILE}")


@main.command()
def logout() -> None:
    """Clear saved credentials."""
    config.clear_config()
    console.print("[green]Logged out - credentials cleared[/green]")


@main.command("config-show")
def config_show() -> None:
    """Show current configuration."""
    console.print(f"[bold]Config file:[/bold] {config.CONFIG_FILE}")
    url = config.get_url()
    console.print(f"[bold]URL:[/bold] {url or '[dim]not set[/dim]'}")
    token = config.get_token()
    if token:
        console.print(f"[bold]Token:[/bold] {token[:20]}...")
    else:
        console.print("[bold]Token:[/bold] [dim]not set[/dim]")


@main.command("config-set-url")
@click.argument("url")
def config_set_url(url: str) -> None:
    """Set the Planka server URL."""
    config.set_url(url)
    console.print(f"[green]URL set to:[/green] {url}")


# === Projects ===


@main.command()
def projects() -> None:
    """List all projects."""
    with get_client() as client:
        projects_list = client.get_projects()
        table = Table(title="Projects")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        for project in projects_list:
            table.add_row(str(project.get("id")), str(project.get("name")))
        console.print(table)


@main.command("project-create")
@click.argument("name")
def project_create(name: str) -> None:
    """Create a new project."""
    with get_client() as client:
        project = client.create_project(name)
        console.print(f"[green]Created project:[/green] {project.get('name')} (ID: {project.get('id')})")


# === Boards ===


@main.command()
@click.argument("board_id")
def board(board_id: str) -> None:
    """Show board details with lists and cards."""
    with get_client() as client:
        data = client.get_board(board_id)
        included: dict[str, Any] = data.get("included", {})
        lists_data: list[dict[str, Any]] = included.get("lists", [])
        cards_data: list[dict[str, Any]] = included.get("cards", [])

        for lst in sorted(lists_data, key=lambda x: x.get("position") or 0):
            list_id = lst.get("id")
            list_name = lst.get("name") or "Unnamed"
            list_cards = [c for c in cards_data if c.get("listId") == list_id]

            table = Table(title=f"[bold]{list_name}[/bold] ({len(list_cards)} cards)")
            table.add_column("ID", style="dim")
            table.add_column("Name", style="green")

            for crd in sorted(list_cards, key=lambda x: x.get("position") or 0):
                table.add_row(str(crd.get("id")), str(crd.get("name")))

            console.print(table)
            console.print()


@main.command("board-create")
@click.argument("project_id")
@click.argument("name")
@click.option("--position", "-p", default=65535.0, help="Position in project")
def board_create(project_id: str, name: str, position: float) -> None:
    """Create a new board in a project."""
    with get_client() as client:
        board_data = client.create_board(project_id, name, position)
        console.print(f"[green]Created board:[/green] {board_data.get('name')} (ID: {board_data.get('id')})")


# === Lists ===


@main.command("list-create")
@click.argument("board_id")
@click.argument("name")
@click.option("--position", "-p", default=65535.0, help="Position in board")
def list_create(board_id: str, name: str, position: float) -> None:
    """Create a new list in a board."""
    with get_client() as client:
        list_data = client.create_list(board_id, name, position)
        console.print(f"[green]Created list:[/green] {list_data.get('name')} (ID: {list_data.get('id')})")


@main.command("list-update")
@click.argument("list_id")
@click.option("--name", "-n", help="New list name")
@click.option("--position", "-p", type=float, help="New position")
def list_update(list_id: str, name: str | None, position: float | None) -> None:
    """Update a list."""
    with get_client() as client:
        kwargs: dict[str, Any] = {}
        if name:
            kwargs["name"] = name
        if position is not None:
            kwargs["position"] = position
        if not kwargs:
            console.print("[yellow]No updates provided[/yellow]")
            return
        list_data = client.update_list(list_id, **kwargs)
        console.print(f"[green]Updated list:[/green] {list_data.get('name')}")


@main.command("list-delete")
@click.argument("list_id")
@click.confirmation_option(prompt="Are you sure you want to delete this list?")
def list_delete(list_id: str) -> None:
    """Delete a list."""
    with get_client() as client:
        client.delete_list(list_id)
        console.print("[green]List deleted[/green]")


# === Cards ===


@main.command()
@click.argument("card_id")
def card(card_id: str) -> None:
    """Show card details."""
    with get_client() as client:
        card_data = client.get_card(card_id)
        console.print(f"[bold cyan]Card: {card_data.get('name')}[/bold cyan]")
        console.print(f"ID: {card_data.get('id')}")
        console.print(f"List ID: {card_data.get('listId')}")
        if card_data.get("dueDate"):
            console.print(f"Due: {card_data.get('dueDate')}")
        description = card_data.get("description")
        if description:
            console.print(f"\n[bold]Description:[/bold]")
            console.print(str(description))


@main.command("card-create")
@click.argument("list_id")
@click.argument("name")
@click.option("--position", "-p", default=65535.0, help="Position in list")
@click.option("--description", "-d", help="Card description")
def card_create(list_id: str, name: str, position: float, description: str | None) -> None:
    """Create a new card in a list."""
    with get_client() as client:
        kwargs: dict[str, Any] = {}
        if description:
            kwargs["description"] = description
        card_data = client.create_card(list_id, name, position, **kwargs)
        console.print(f"[green]Created card:[/green] {card_data.get('name')} (ID: {card_data.get('id')})")


@main.command("card-update")
@click.argument("card_id")
@click.option("--name", "-n", help="New card name")
@click.option("--description", "-d", help="New card description")
@click.option("--list-id", "-l", help="Move to list ID")
@click.option("--position", "-p", type=float, help="New position")
@click.option("--due-date", help="Due date (ISO format)")
def card_update(
    card_id: str,
    name: str | None,
    description: str | None,
    list_id: str | None,
    position: float | None,
    due_date: str | None,
) -> None:
    """Update a card."""
    with get_client() as client:
        kwargs: dict[str, Any] = {}
        if name:
            kwargs["name"] = name
        if description:
            kwargs["description"] = description
        if list_id:
            kwargs["listId"] = list_id
        if position is not None:
            kwargs["position"] = position
        if due_date:
            kwargs["dueDate"] = due_date
        if not kwargs:
            console.print("[yellow]No updates provided[/yellow]")
            return
        card_data = client.update_card(card_id, **kwargs)
        console.print(f"[green]Updated card:[/green] {card_data.get('name')}")


@main.command("card-move")
@click.argument("card_id")
@click.argument("list_id")
@click.option("--position", "-p", default=65535.0, help="Position in new list")
def card_move(card_id: str, list_id: str, position: float) -> None:
    """Move a card to a different list."""
    with get_client() as client:
        card_data = client.move_card(card_id, list_id, position)
        console.print(f"[green]Moved card:[/green] {card_data.get('name')}")


@main.command("card-delete")
@click.argument("card_id")
@click.confirmation_option(prompt="Are you sure you want to delete this card?")
def card_delete(card_id: str) -> None:
    """Delete a card."""
    with get_client() as client:
        client.delete_card(card_id)
        console.print("[green]Card deleted[/green]")


@main.command("card-duplicate")
@click.argument("card_id")
@click.option("--position", "-p", default=65535.0, help="Position for duplicate")
def card_duplicate(card_id: str, position: float) -> None:
    """Duplicate a card."""
    with get_client() as client:
        card_data = client.duplicate_card(card_id, position)
        console.print(f"[green]Duplicated card:[/green] {card_data.get('name')} (ID: {card_data.get('id')})")


# === Comments ===


@main.command()
@click.argument("card_id")
def comments(card_id: str) -> None:
    """List comments on a card."""
    with get_client() as client:
        comments_list = client.get_comments(card_id)
        if not comments_list:
            console.print("[dim]No comments[/dim]")
            return
        for comment in comments_list:
            console.print(f"[cyan]{comment.get('id')}[/cyan]: {comment.get('text')}")


@main.command("comment-add")
@click.argument("card_id")
@click.argument("text")
def comment_add(card_id: str, text: str) -> None:
    """Add a comment to a card."""
    with get_client() as client:
        comment = client.create_comment(card_id, text)
        console.print(f"[green]Added comment[/green] (ID: {comment.get('id')})")


@main.command("comment-delete")
@click.argument("comment_id")
@click.confirmation_option(prompt="Are you sure you want to delete this comment?")
def comment_delete(comment_id: str) -> None:
    """Delete a comment."""
    with get_client() as client:
        client.delete_comment(comment_id)
        console.print("[green]Comment deleted[/green]")


# === Labels ===


@main.command("label-create")
@click.argument("board_id")
@click.argument("name")
@click.option("--color", "-c", default="berry-red", help="Label color")
@click.option("--position", "-p", default=65535.0, help="Position")
def label_create(board_id: str, name: str, color: str, position: float) -> None:
    """Create a label on a board."""
    with get_client() as client:
        label = client.create_label(board_id, name, color, position)
        console.print(f"[green]Created label:[/green] {label.get('name')} (ID: {label.get('id')})")


@main.command("label-add")
@click.argument("card_id")
@click.argument("label_id")
def label_add(card_id: str, label_id: str) -> None:
    """Add a label to a card."""
    with get_client() as client:
        client.add_label_to_card(card_id, label_id)
        console.print("[green]Label added to card[/green]")


@main.command("label-remove")
@click.argument("card_id")
@click.argument("label_id")
def label_remove(card_id: str, label_id: str) -> None:
    """Remove a label from a card."""
    with get_client() as client:
        client.remove_label_from_card(card_id, label_id)
        console.print("[green]Label removed from card[/green]")


# === Tasks ===


@main.command("tasklist-create")
@click.argument("card_id")
@click.argument("name")
@click.option("--position", "-p", default=65535.0, help="Position")
def tasklist_create(card_id: str, name: str, position: float) -> None:
    """Create a task list on a card."""
    with get_client() as client:
        tasklist = client.create_task_list(card_id, name, position)
        console.print(f"[green]Created task list:[/green] {tasklist.get('name')} (ID: {tasklist.get('id')})")


@main.command("task-create")
@click.argument("tasklist_id")
@click.argument("name")
@click.option("--position", "-p", default=65535.0, help="Position")
def task_create(tasklist_id: str, name: str, position: float) -> None:
    """Create a task in a task list."""
    with get_client() as client:
        task = client.create_task(tasklist_id, name, position)
        console.print(f"[green]Created task:[/green] {task.get('name')} (ID: {task.get('id')})")


@main.command("task-complete")
@click.argument("task_id")
@click.option("--undo", is_flag=True, help="Mark as incomplete")
def task_complete(task_id: str, undo: bool) -> None:
    """Mark a task as complete."""
    with get_client() as client:
        task = client.update_task(task_id, isCompleted=not undo)
        status = "incomplete" if undo else "complete"
        console.print(f"[green]Marked task as {status}:[/green] {task.get('name')}")


@main.command("task-delete")
@click.argument("task_id")
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
def task_delete(task_id: str) -> None:
    """Delete a task."""
    with get_client() as client:
        client.delete_task(task_id)
        console.print("[green]Task deleted[/green]")


# === Users ===


@main.command()
def users() -> None:
    """List all users."""
    with get_client() as client:
        users_list = client.get_users()
        table = Table(title="Users")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Username", style="dim")
        table.add_column("Email", style="dim")
        for user in users_list:
            table.add_row(
                str(user.get("id")),
                str(user.get("name")),
                str(user.get("username") or ""),
                str(user.get("email") or ""),
            )
        console.print(table)


# === Notifications ===


@main.command()
def notifications() -> None:
    """List notifications."""
    with get_client() as client:
        notifs = client.get_notifications()
        if not notifs:
            console.print("[dim]No notifications[/dim]")
            return
        table = Table(title="Notifications")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Read", style="dim")
        for notif in notifs:
            table.add_row(
                str(notif.get("id")),
                str(notif.get("type")),
                "Yes" if notif.get("isRead") else "No",
            )
        console.print(table)


@main.command("notifications-read-all")
def notifications_read_all() -> None:
    """Mark all notifications as read."""
    with get_client() as client:
        client.read_all_notifications()
        console.print("[green]All notifications marked as read[/green]")


# === Activity ===


@main.command("activity")
@click.argument("board_id")
@click.option("--limit", "-l", default=20, help="Number of actions to show")
def activity(board_id: str, limit: int) -> None:
    """Show board activity."""
    with get_client() as client:
        actions = client.get_board_actions(board_id)
        table = Table(title="Board Activity")
        table.add_column("Type", style="cyan")
        table.add_column("User", style="green")
        table.add_column("Data", style="dim", max_width=50)
        for action in actions[:limit]:
            table.add_row(
                str(action.get("type")),
                str(action.get("userId")),
                str(action.get("data", {}))[:50],
            )
        console.print(table)


if __name__ == "__main__":
    main()

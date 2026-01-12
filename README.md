# planka-cli

A command-line interface for [Planka](https://planka.app) - the open-source Trello alternative.

## Installation

```bash
pip install .
```

Or for development:

```bash
pip install -e .
```

## Quick Start

```bash
# Login (prompts for URL, username, password)
planka login

# List projects
planka projects

# Show a board with all lists and cards
planka board <board_id>

# View a card
planka card <card_id>
```

## Configuration

Credentials are stored in `~/.config/planka/config.json` with restricted permissions (600).

```bash
# Show current config
planka config-show

# Change server URL
planka config-set-url https://planka.example.com

# Clear credentials
planka logout
```

Environment variables override the config file:
- `PLANKA_URL` - Server URL
- `PLANKA_TOKEN` - Access token

## Commands

### Authentication

| Command | Description |
|---------|-------------|
| `planka login` | Login and save credentials |
| `planka logout` | Clear saved credentials |
| `planka config-show` | Show current configuration |
| `planka config-set-url <url>` | Set the server URL |

### Projects

| Command | Description |
|---------|-------------|
| `planka projects` | List all projects |
| `planka project-create <name>` | Create a new project |

### Boards

| Command | Description |
|---------|-------------|
| `planka board <board_id>` | Show board with lists and cards |
| `planka board-create <project_id> <name>` | Create a new board |

### Lists

| Command | Description |
|---------|-------------|
| `planka list-create <board_id> <name>` | Create a new list |
| `planka list-update <list_id> [--name] [--position]` | Update a list |
| `planka list-delete <list_id>` | Delete a list |

### Cards

| Command | Description |
|---------|-------------|
| `planka card <card_id>` | Show card details |
| `planka card-create <list_id> <name> [-d description]` | Create a card |
| `planka card-update <card_id> [--name] [--description] [--list-id] [--due-date]` | Update a card |
| `planka card-move <card_id> <list_id>` | Move card to another list |
| `planka card-duplicate <card_id>` | Duplicate a card |
| `planka card-delete <card_id>` | Delete a card |

### Comments

| Command | Description |
|---------|-------------|
| `planka comments <card_id>` | List comments on a card |
| `planka comment-add <card_id> <text>` | Add a comment |
| `planka comment-delete <comment_id>` | Delete a comment |

### Labels

| Command | Description |
|---------|-------------|
| `planka label-create <board_id> <name> [--color]` | Create a label |
| `planka label-add <card_id> <label_id>` | Add label to card |
| `planka label-remove <card_id> <label_id>` | Remove label from card |

### Tasks

| Command | Description |
|---------|-------------|
| `planka tasklist-create <card_id> <name>` | Create a task list |
| `planka task-create <tasklist_id> <name>` | Create a task |
| `planka task-complete <task_id> [--undo]` | Mark task complete/incomplete |
| `planka task-delete <task_id>` | Delete a task |

### Users & Notifications

| Command | Description |
|---------|-------------|
| `planka users` | List all users |
| `planka notifications` | List notifications |
| `planka notifications-read-all` | Mark all as read |

### Activity

| Command | Description |
|---------|-------------|
| `planka activity <board_id> [--limit]` | Show board activity |

## Examples

```bash
# Create a card with description
planka card-create 123456 "Fix login bug" -d "Users can't login on mobile"

# Move card to "Done" list
planka card-move 789012 345678

# Add a comment
planka comment-add 789012 "Fixed in commit abc123"

# Create a task checklist
planka tasklist-create 789012 "QA Checklist"
planka task-create 111222 "Test on iOS"
planka task-create 111222 "Test on Android"
planka task-complete 333444
```

## License

MIT

# Import markdown notes to Github Issues

This tool allows you to convert local Markdown notes into GitHub Issues, assign
labels and users, and add them to a GitHub Projects **V2** board. Each note
becomes an issue and is moved to an `imported/` folder after successful import.

## Suggested Directory Structure

```
notes/
├── imported/           # Automatically created and used for moved files
├── my-note-1.md        # Notes that will be turned into GitHub issues
├── another-task.md
created_issues.md       # Auto-generated index of created issues
import_issues.py        # The main script
```

## Note Format

Each `.md` file in the `notes/` folder should follow this format:

````markdown
# Issue Title Here

labels: bug, urgent
assignees: alice, bob

This is the body of the issue. You can describe the problem, provide context, and use Markdown.
````

- The first line (starting with `#`) is used as the **issue title**.
- `labels:` and `assign:` lines are optional.
- Everything else is treated as the **issue body**.

## Setup

1. Clone the repo or copy the script into your project.

2. Install Python dependencies (if you don’t have `requests`):

   ```bash
   pip install requests
   ```

3. Create a GitHub personal access token with the following scopes:
   - `repo`
   - `project` (for Projects V2 API)

4. Create an environment file (e.g. `.env`) and add:

   ```bash
   export GITHUB_TOKEN = "your_token"
   epoxrt ORG = "your-org"
   epoxrt REPO = "your-repo"
   export PROJECT_NUMBER= "your_project_number"
   export NOTES_DIR="notes"
   export INDEX_FILE="created_issues.md"
   ```

> You can find the `PROJECT_NUMBER` in the URI of your project eg: https://github.com/orgs/your-org/projects/<number>

## Running the Script

From your terminal, run:

```bash
python import_issues.py
```

- Issues will be created in the specified repo.
- Each issue will be assigned labels and assignees (if specified).
- The issue will be **added to your Projects V2 board**.
- The note will be moved to `notes/imported/`.
- A link will be added to `created_issues.md`.

---

## Features

- Creates GitHub issues from Markdown notes
- Supports:
  - Title and body
  - Labels
  - Assignees
  - Adding issues to GitHub Projects V2
- Keeps a Markdown index of created issues
- Moves imported notes to `notes/imported/`

## Troubleshooting

- **"GraphQL returned errors"**: Ensure your `PROJECT_NUMBER` is correct and
  that your GitHub token has the right permissions.
- **Assign not working**: Make sure usernames are correct and are collaborators in the repo.
- **No issues created?**: Check if the `.md` files contain both a title and body.

## To Do

- [ ] Add support for custom project fields (status, priority, etc.)
- [ ] Support milestones or due dates

## License

Apache-2.0 License

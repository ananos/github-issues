import os
import sys
import requests
import shutil

# CONFIGURATION
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
print(GITHUB_TOKEN)
ORG = os.getenv("ORG")
REPO = os.getenv("REPO")
PROJECT_NUMBER = int(os.getenv("PROJECT_NUMBER"))
NOTES_DIR = os.getenv("NOTES_DIR")
IMPORTED_DIR = os.path.join(NOTES_DIR, "imported")
os.makedirs(IMPORTED_DIR, exist_ok=True)
INDEX_FILE = os.getenv("INDEX_FILE")

# HEADERS
REST_HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}
GRAPHQL_HEADERS = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# Initialize the index file if not exists
if not os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "w") as index:
        index.write("# Created Issues\n\n")

def graphql_request(query, variables):
    response = requests.post("https://api.github.com/graphql", headers=GRAPHQL_HEADERS,
                             json={"query": query, "variables": variables})
    if response.status_code != 200:
        print(f"GraphQL HTTP error: {response.status_code}")
        print(response.text)
        return None

    result = response.json()
    if "errors" in result:
        print("GraphQL returned errors:")
        for err in result["errors"]:
            print(f" - {err['message']}")
        return None
    return result["data"]

# STEP 1: Get Org ID by login
def get_org_id(org_login):
    query = """
    query($login: String!) {
      organization(login: $login) {
        id
      }
    }
    """
    variables = {"login": org_login}
    data = graphql_request(query, variables)
    if data and data["organization"]:
        return data["organization"]["id"]
    print("Could not fetch organization ID.")
    return None

# STEP 2: Get Project ID by project number
def get_project_id(org_login, project_number):
    query = """
    query($login: String!, $number: Int!) {
      organization(login: $login) {
        projectV2(number: $number) {
          id
        }
      }
    }
    """
    variables = {"login": org_login, "number": project_number}
    data = graphql_request(query, variables)
    if data and data["organization"] and data["organization"]["projectV2"]:
        return data["organization"]["projectV2"]["id"]
    print("Could not fetch project ID.")
    return None

# STEP 3: Create Issue via REST
def create_issue(title, body, labels=None, assignees=None):
    url = f"https://api.github.com/repos/{ORG}/{REPO}/issues"
    payload = {
        "title": title,
        "body": body,
        "labels": labels or [],
        "assignees": assignees or []
    }
    response = requests.post(url, json=payload, headers=REST_HEADERS)
    if response.status_code == 201:
        print(f"Created issue: {title}")
        return response.json()["node_id"], response.json()["html_url"]
    else:
        print(f"Failed to create issue: {title}")
        print(f"    {response.status_code}: {response.text}")
        return None, None

# STEP 4: Add issue to project (GraphQL)
def add_issue_to_project(project_id, issue_node_id):
    mutation = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {
        projectId: $projectId,
        contentId: $contentId
      }) {
        item {
          id
        }
      }
    }
    """
    variables = {"projectId": project_id, "contentId": issue_node_id}
    data = graphql_request(mutation, variables)
    if data and data["addProjectV2ItemById"]:
        print("Issue added to project.")
    else:
        print("Failed to add issue to project.")

# MAIN
if __name__ == "__main__":
    print("Resolving organization and project IDs...")
    org_id = get_org_id(ORG)
    if not org_id:
        sys.exit(1)

    project_id = get_project_id(ORG, PROJECT_NUMBER)
    if not project_id:
        sys.exit(1)

    print(f"Project ID: {project_id}")
    print("Starting issue import...")

    for filename in os.listdir(NOTES_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(NOTES_DIR, filename)
            with open(filepath, "r") as f:
                lines = f.readlines()
                if len(lines) < 2:
                    print(f"⚠️ Skipping {filename} (not enough content).")
                    continue

                # Extract title
                title = lines[0].strip().lstrip("#").strip()

                # Extract labels (if any)
                label_line = next((line for line in lines if line.lower().startswith("labels:")), None)
                if label_line:
                    labels = [l.strip() for l in label_line[len("labels:"):].split(",")]
                    lines.remove(label_line)
                else:
                    labels = []

                # Extract assignees (if any)
                assignee_line = next((line for line in lines if line.lower().startswith("assign:")), None)
                if assignee_line:
                    assignees = [a.strip() for a in assignee_line[len("assign:"):].split(",")]
                    lines.remove(assignee_line)
                else:
                    assignees = []

                # Body is the rest of the file
                body = "".join(lines[1:]).strip()

                # Create Issue
                issue_node_id, issue_url = create_issue(title, body, labels, assignees)
                if issue_node_id:
                    add_issue_to_project(project_id, issue_node_id)

                    # Move the file to imported/
                    imported_path = os.path.join(IMPORTED_DIR, filename)
                    shutil.move(filepath, imported_path)
                    print(f"Moved {filename} to imported/")

                    # Add checkbox to title to mark as imported
                    with open(imported_path, "a") as f:
                        f.write("\n\n- [x] Imported to GitHub Issue: " + issue_url)

                    # Add to index file
                    with open(INDEX_FILE, "a") as index:
                        index.write(f"- [{title}]({issue_url})\n")


# Website: https://devpod.sh
# Install DevPod
curl -fsSL https://get.devpod.sh | bash

# Initialize a new workspace from a Git repo
devpod up https://github.com/your/repo

# Reconnect to an existing workspace
devpod connect your-repo

# List workspaces
devpod list

# Destroy a workspace
devpod rm your-repo


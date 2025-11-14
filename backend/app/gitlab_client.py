import gitlab
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from git import Repo
from .config import config


class GitLabClient:
    """Client for interacting with GitLab API and Git repositories"""
    
    def __init__(self, group_token: str, gitlab_url: str = "https://code.swisscom.com"):
        """
        Initialize GitLab client
        
        Args:
            group_token: GitLab group access token for repo operations
            gitlab_url: GitLab instance URL
        """
        self.gitlab_url = gitlab_url
        self.group_token = group_token
        
        # Use group token for all repo operations
        self.gl = gitlab.Gitlab(self.gitlab_url, private_token=self.group_token)
    
    def get_repo_path(self, repo_url: str) -> Path:
        """Get local path for cached repository"""
        # Extract repo name from URL
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        return Path(config.git_cache_dir) / repo_name
    
    def _find_services_csv(self, repo_path: Path, stage: str) -> Optional[Path]:
        """
        Dynamically find services.csv in the repository
        
        Args:
            repo_path: Path to repository
            stage: Stage name to search in
            
        Returns:
            Path to services.csv or None if not found
        """
        # Search pattern: {stage}/*/sif/instance/stage/*/instance/config/services.csv
        stage_dir = repo_path / stage
        
        if not stage_dir.exists():
            return None
        
        # Try to find services.csv in common patterns
        patterns = [
            f"{stage}/*/sif/instance/stage/*/instance/config/services.csv",
            f"{stage}/*/sif/instance/stage/*/config/services.csv",
        ]
        
        for pattern in patterns:
            matches = list(repo_path.glob(pattern))
            if matches:
                # Return the first match
                return matches[0]
        
        return None
    
    def clone_or_update_repo(self, repo_url: str) -> Repo:
        """
        Clone repository or update if already exists
        
        Args:
            repo_url: Git repository URL
            
        Returns:
            GitPython Repo object
        """
        repo_path = self.get_repo_path(repo_url)
        
        # Add authentication to URL
        auth_url = self._add_auth_to_url(repo_url, self.group_token)
        
        if repo_path.exists():
            # Repository exists, fetch latest
            repo = Repo(repo_path)
            origin = repo.remote('origin')
            origin.fetch()
            # Reset to origin/main (or master)
            try:
                repo.git.checkout('main')
                repo.git.reset('--hard', 'origin/main')
            except:
                repo.git.checkout('master')
                repo.git.reset('--hard', 'origin/master')
        else:
            # Clone repository
            repo = Repo.clone_from(auth_url, repo_path)
        
        return repo
    
    def read_services_csv(self, repo_url: str, stage: str, csv_path_template: str) -> str:
        """
        Read services.csv file from repository
        
        Args:
            repo_url: Git repository URL
            stage: Stage name (dev, tst, prd, etc.)
            csv_path_template: Path template with {stage} placeholder
            
        Returns:
            Content of services.csv file
        """
        repo = self.clone_or_update_repo(repo_url)
        
        # Replace {stage} placeholder in template
        csv_path_str = csv_path_template.replace("{stage}", stage)
        csv_path = Path(repo.working_dir) / csv_path_str
        
        # If configured path doesn't exist, try to find it dynamically
        if not csv_path.exists():
            csv_path = self._find_services_csv(Path(repo.working_dir), stage)
            if not csv_path:
                raise FileNotFoundError(
                    f"services.csv not found at configured path {csv_path_str} "
                    f"and could not be found dynamically in stage '{stage}'"
                )
        
        with open(csv_path, 'r') as f:
            return f.read()
    
    def save_services_csv(
        self, 
        repo_url: str, 
        stage: str, 
        content: str, 
        username: str,
        csv_path_template: str,
        jira_ticket: Optional[str] = None,
        message: Optional[str] = None
    ) -> str:
        """
        Save services.csv, create branch, commit, push, and create merge request
        
        Args:
            repo_url: Git repository URL
            stage: Stage name
            content: New content for services.csv
            username: Username for branch and commit
            csv_path_template: Path template with {stage} placeholder
            jira_ticket: Optional Jira ticket number (e.g. "FOP-1234")
            message: Optional commit message (default: "Updated services")
            
        Returns:
            URL of created merge request
        """
        repo = self.clone_or_update_repo(repo_url)
        
        # Create feature branch with optional Jira ticket
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        if jira_ticket:
            branch_name = f"fil-deploy/{username}/{jira_ticket}/{timestamp}"
        else:
            branch_name = f"fil-deploy/{username}/{timestamp}"
        
        # Ensure we're on main/master before creating branch
        try:
            repo.git.checkout('main')
        except:
            repo.git.checkout('master')
        
        # Create and checkout new branch
        repo.git.checkout('-b', branch_name)
        
        # Replace {stage} placeholder and find the correct path
        csv_path_str = csv_path_template.replace("{stage}", stage)
        csv_path = Path(repo.working_dir) / csv_path_str
        
        # If configured path doesn't exist, try to find it dynamically
        if not csv_path.exists():
            csv_path = self._find_services_csv(Path(repo.working_dir), stage)
            if not csv_path:
                raise FileNotFoundError(
                    f"services.csv not found at configured path {csv_path_str} "
                    f"and could not be found dynamically in stage '{stage}'"
                )
        
        with open(csv_path, 'w') as f:
            f.write(content)
        
        # Commit changes
        repo.index.add([str(csv_path.relative_to(repo.working_dir))])
        
        # Build commit message with optional Jira ticket and custom message
        user_message = message if message else "Updated services"
        if jira_ticket:
            commit_message = f"[{jira_ticket}] {user_message} for {stage} by {username}"
        else:
            commit_message = f"{user_message} for {stage} by {username}"
        
        repo.index.commit(commit_message)
        
        # Push branch
        auth_url = self._add_auth_to_url(repo_url, self.group_token)
        origin = repo.remote('origin')
        origin.set_url(auth_url)
        origin.push(refspec=f'{branch_name}:{branch_name}')
        
        # Create merge request via GitLab API
        mr_url = self._create_merge_request(
            repo_url, 
            branch_name, 
            stage, 
            username,
            jira_ticket,
            message
        )
        
        return mr_url
    
    def _add_auth_to_url(self, url: str, token: str) -> str:
        """Add authentication token to Git URL"""
        if url.startswith('https://'):
            # Insert token after https://
            return url.replace('https://', f'https://oauth2:{token}@')
        return url
    
    def _create_merge_request(
        self, 
        repo_url: str, 
        branch_name: str, 
        stage: str, 
        username: str,
        jira_ticket: Optional[str] = None,
        message: Optional[str] = None
    ) -> str:
        """
        Create merge request via GitLab API
        
        Args:
            repo_url: Git repository URL
            branch_name: Source branch name
            stage: Stage name
            username: Username
            jira_ticket: Optional Jira ticket number
            message: Optional custom message
            
        Returns:
            URL of created merge request
        """
        # Extract project path from URL
        # Format: https://code.swisscom.com/group/subgroup/project.git
        project_path = repo_url.replace(self.gitlab_url + '/', '')
        project_path = project_path.replace('.git', '')
        
        # Get project
        project = self.gl.projects.get(project_path)
        
        # Determine target branch
        try:
            target_branch = 'main'
            project.branches.get('main')
        except:
            target_branch = 'master'
        
        # Build MR title and description
        user_message = message if message else "Updated services"
        if jira_ticket:
            mr_title = f'[{jira_ticket}] {user_message} for {stage}'
            mr_description = f'Jira Ticket: {jira_ticket}\n\n{user_message}\n\nDeployed by {username} for stage {stage}'
        else:
            mr_title = f'{user_message} for {stage}'
            mr_description = f'{user_message}\n\nDeployed by {username} for stage {stage}'
        
        # Create merge request
        mr = project.mergerequests.create({
            'source_branch': branch_name,
            'target_branch': target_branch,
            'title': mr_title,
            'description': mr_description,
            'remove_source_branch': True
        })
        
        return mr.web_url
    
    def get_project_id(self, repo_url: str) -> str:
        """Get GitLab project ID from repository URL"""
        project_path = repo_url.replace(self.gitlab_url + '/', '')
        project_path = project_path.replace('.git', '')
        project = self.gl.projects.get(project_path)
        return str(project.id)


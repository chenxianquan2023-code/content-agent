"""
Team collaboration features for Content Agent.
Multi-user support with roles, approvals, and audit trails.
"""

import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class Role(Enum):
    """User roles in the team."""
    OWNER = "owner"           # Full control
    ADMIN = "admin"           # Can manage users and approve
    EDITOR = "editor"         # Can create and edit content
    REVIEWER = "reviewer"     # Can review and comment
    VIEWER = "viewer"         # Read-only access


class Permission(Enum):
    """Permissions for actions."""
    CREATE_CONTENT = "create_content"
    EDIT_CONTENT = "edit_content"
    PUBLISH_CONTENT = "publish_content"
    APPROVE_CONTENT = "approve_content"
    DELETE_CONTENT = "delete_content"
    MANAGE_USERS = "manage_users"
    VIEW_ANALYTICS = "view_analytics"
    CONFIGURE_SETTINGS = "configure_settings"


ROLE_PERMISSIONS = {
    Role.OWNER: list(Permission),
    Role.ADMIN: [
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.PUBLISH_CONTENT,
        Permission.APPROVE_CONTENT,
        Permission.DELETE_CONTENT,
        Permission.MANAGE_USERS,
        Permission.VIEW_ANALYTICS,
        Permission.CONFIGURE_SETTINGS
    ],
    Role.EDITOR: [
        Permission.CREATE_CONTENT,
        Permission.EDIT_CONTENT,
        Permission.VIEW_ANALYTICS
    ],
    Role.REVIEWER: [
        Permission.APPROVE_CONTENT,
        Permission.VIEW_ANALYTICS
    ],
    Role.VIEWER: [
        Permission.VIEW_ANALYTICS
    ]
}


@dataclass
class TeamMember:
    """A team member."""
    id: str
    name: str
    email: str
    role: Role
    created_at: str
    created_by: str
    active: bool = True


@dataclass
class ContentApproval:
    """Content approval workflow item."""
    content_id: str
    content_type: str
    title: str
    content: str
    platforms: List[str]
    submitted_by: str
    submitted_at: str
    status: str  # pending, approved, rejected, published
    reviewers: List[str]
    approvals: List[Dict]  # List of {user_id, decision, comment, timestamp}
    scheduled_time: Optional[str] = None


class TeamManager:
    """
    Manages team members, permissions, and approval workflows.
    """
    
    def __init__(self, memory_manager, owner_id: str = None):
        self.memory = memory_manager
        self.owner_id = owner_id or "default_owner"
        self._ensure_owner_exists()
    
    def _ensure_owner_exists(self):
        """Ensure at least one owner exists."""
        members = self._load_members()
        
        if not members:
            # Create default owner
            owner = TeamMember(
                id=self.owner_id,
                name="Owner",
                email="owner@example.com",
                role=Role.OWNER,
                created_at=datetime.now().isoformat(),
                created_by="system"
            )
            self._save_member(owner)
    
    def _load_members(self) -> Dict[str, TeamMember]:
        """Load all team members."""
        data = self.memory.warm("team_members")
        if not data:
            return {}
        
        return {
            k: TeamMember(**v) for k, v in data.items()
        }
    
    def _save_member(self, member: TeamMember):
        """Save a team member."""
        members = self._load_members()
        members[member.id] = member
        
        self.memory.warm("team_members", {
            k: {
                "id": m.id,
                "name": m.name,
                "email": m.email,
                "role": m.role.value,
                "created_at": m.created_at,
                "created_by": m.created_by,
                "active": m.active
            }
            for k, m in members.items()
        })
    
    def add_member(self, user_id: str, name: str, email: str,
                   role: Role, added_by: str) -> TeamMember:
        """
        Add a new team member.
        
        Args:
            user_id: Unique user ID
            name: Display name
            email: Email address
            role: User role
            added_by: ID of user adding this member
            
        Returns:
            Created member
        """
        # Check if adder has permission
        if not self.has_permission(added_by, Permission.MANAGE_USERS):
            raise PermissionError("User does not have permission to add members")
        
        # Check if user already exists
        members = self._load_members()
        if user_id in members:
            raise ValueError(f"User {user_id} already exists")
        
        member = TeamMember(
            id=user_id,
            name=name,
            email=email,
            role=role,
            created_at=datetime.now().isoformat(),
            created_by=added_by,
            active=True
        )
        
        self._save_member(member)
        
        # Log action
        self._log_audit("member_added", added_by, {"new_member": user_id, "role": role.value})
        
        return member
    
    def remove_member(self, user_id: str, removed_by: str):
        """Remove a team member."""
        if not self.has_permission(removed_by, Permission.MANAGE_USERS):
            raise PermissionError("User does not have permission to remove members")
        
        if user_id == self.owner_id:
            raise ValueError("Cannot remove owner")
        
        members = self._load_members()
        if user_id in members:
            members[user_id].active = False
            self._save_member(members[user_id])
            
            self._log_audit("member_removed", removed_by, {"removed_member": user_id})
    
    def update_role(self, user_id: str, new_role: Role, updated_by: str):
        """Update a member's role."""
        if not self.has_permission(updated_by, Permission.MANAGE_USERS):
            raise PermissionError("User does not have permission to update roles")
        
        if user_id == self.owner_id and new_role != Role.OWNER:
            raise ValueError("Cannot demote owner")
        
        members = self._load_members()
        if user_id not in members:
            raise ValueError(f"User {user_id} not found")
        
        old_role = members[user_id].role
        members[user_id].role = new_role
        self._save_member(members[user_id])
        
        self._log_audit("role_updated", updated_by, {
            "user": user_id,
            "old_role": old_role.value,
            "new_role": new_role.value
        })
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has a specific permission."""
        members = self._load_members()
        
        if user_id not in members:
            return False
        
        member = members[user_id]
        if not member.active:
            return False
        
        return permission in ROLE_PERMISSIONS.get(member.role, [])
    
    def get_members(self) -> List[Dict]:
        """Get all team members."""
        members = self._load_members()
        return [
            {
                "id": m.id,
                "name": m.name,
                "email": m.email,
                "role": m.role.value,
                "active": m.active,
                "created_at": m.created_at
            }
            for m in members.values()
        ]
    
    def _log_audit(self, action: str, user_id: str, details: Dict):
        """Log an audit event."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details
        }
        
        # Append to audit log
        audit_log = self.memory.cold("team_audit_log") or []
        audit_log.append(audit_entry)
        
        # Keep last 1000 entries
        if len(audit_log) > 1000:
            audit_log = audit_log[-1000:]
        
        self.memory.cold("team_audit_log", audit_log)
    
    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """Get recent audit log entries."""
        audit_log = self.memory.cold("team_audit_log") or []
        return audit_log[-limit:]


class ApprovalWorkflow:
    """
    Content approval workflow management.
    """
    
    def __init__(self, memory_manager, team_manager: TeamManager):
        self.memory = memory_manager
        self.team = team_manager
    
    def submit_content(self, content_id: str, title: str, content: str,
                      content_type: str, platforms: List[str],
                      submitted_by: str,
                      scheduled_time: Optional[str] = None) -> str:
        """
        Submit content for approval.
        
        Returns:
            Approval ID
        """
        if not self.team.has_permission(submitted_by, Permission.CREATE_CONTENT):
            raise PermissionError("User cannot create content")
        
        # Find reviewers (admins and reviewers)
        reviewers = []
        for member in self.team.get_members():
            if member["role"] in ["admin", "reviewer"] and member["active"]:
                reviewers.append(member["id"])
        
        approval = ContentApproval(
            content_id=content_id,
            content_type=content_type,
            title=title,
            content=content,
            platforms=platforms,
            submitted_by=submitted_by,
            submitted_at=datetime.now().isoformat(),
            status="pending",
            reviewers=reviewers,
            approvals=[],
            scheduled_time=scheduled_time
        )
        
        approval_id = f"approval_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{content_id}"
        
        self._save_approval(approval_id, approval)
        
        self.team._log_audit("content_submitted", submitted_by, {
            "content_id": content_id,
            "approval_id": approval_id
        })
        
        return approval_id
    
    def _save_approval(self, approval_id: str, approval: ContentApproval):
        """Save approval to memory."""
        data = {
            "content_id": approval.content_id,
            "content_type": approval.content_type,
            "title": approval.title,
            "content": approval.content,
            "platforms": approval.platforms,
            "submitted_by": approval.submitted_by,
            "submitted_at": approval.submitted_at,
            "status": approval.status,
            "reviewers": approval.reviewers,
            "approvals": approval.approvals,
            "scheduled_time": approval.scheduled_time
        }
        
        self.memory.warm(f"approval_{approval_id}", data)
    
    def _load_approval(self, approval_id: str) -> Optional[ContentApproval]:
        """Load approval from memory."""
        data = self.memory.warm(f"approval_{approval_id}")
        if not data:
            return None
        
        return ContentApproval(**data)
    
    def review_content(self, approval_id: str, reviewer_id: str,
                      decision: str, comment: str = ""):
        """
        Review and approve/reject content.
        
        Args:
            approval_id: Approval workflow ID
            reviewer_id: Reviewer user ID
            decision: "approved" or "rejected"
            comment: Optional comment
        """
        if not self.team.has_permission(reviewer_id, Permission.APPROVE_CONTENT):
            raise PermissionError("User cannot review content")
        
        approval = self._load_approval(approval_id)
        if not approval:
            raise ValueError("Approval not found")
        
        if approval.status != "pending":
            raise ValueError("Content already reviewed")
        
        # Add review
        approval.approvals.append({
            "user_id": reviewer_id,
            "decision": decision,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if approved by all required reviewers or rejected
        if decision == "rejected":
            approval.status = "rejected"
        elif len([a for a in approval.approvals if a["decision"] == "approved"]) >= 1:
            approval.status = "approved"
        
        self._save_approval(approval_id, approval)
        
        self.team._log_audit("content_reviewed", reviewer_id, {
            "approval_id": approval_id,
            "decision": decision
        })
    
    def get_pending_approvals(self, reviewer_id: Optional[str] = None) -> List[Dict]:
        """Get pending approvals for a reviewer."""
        # In real implementation, scan all approval_* keys
        # For now, return empty list
        return []
    
    def get_approval_status(self, approval_id: str) -> Optional[Dict]:
        """Get status of an approval."""
        approval = self._load_approval(approval_id)
        if not approval:
            return None
        
        return {
            "approval_id": approval_id,
            "content_id": approval.content_id,
            "title": approval.title,
            "status": approval.status,
            "submitted_by": approval.submitted_by,
            "submitted_at": approval.submitted_at,
            "approvals": approval.approvals,
            "scheduled_time": approval.scheduled_time
        }

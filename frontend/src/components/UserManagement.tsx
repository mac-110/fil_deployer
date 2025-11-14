import { useState, useEffect } from 'react';
import { UserInfo, UserCreate } from '../types';
import { userAPI } from '../services/api';
import './UserManagement.css';

export default function UserManagement() {
  const [users, setUsers] = useState<UserInfo[]>([]);
  const [isAdding, setIsAdding] = useState(false);
  const [message, setMessage] = useState('');
  const [newUser, setNewUser] = useState<UserCreate>({
    username: '',
    password: '',
    full_name: '',
    email: '',
    is_admin: false,
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await userAPI.listUsers();
      setUsers(data);
    } catch (error) {
      showMessage('Error loading users');
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await userAPI.createUser(newUser);
      showMessage('User created successfully!');
      setIsAdding(false);
      setNewUser({
        username: '',
        password: '',
        full_name: '',
        email: '',
        is_admin: false,
      });
      loadUsers();
    } catch (error: any) {
      showMessage(error.response?.data?.detail || 'Error creating user');
    }
  };

  const handleDeleteUser = async (username: string) => {
    if (!confirm(`Delete user ${username}?`)) return;

    try {
      await userAPI.deleteUser(username);
      showMessage('User deleted successfully!');
      loadUsers();
    } catch (error: any) {
      showMessage(error.response?.data?.detail || 'Error deleting user');
    }
  };

  const showMessage = (msg: string) => {
    setMessage(msg);
    setTimeout(() => setMessage(''), 3000);
  };

  return (
    <div className="user-management">
      <div className="section-header">
        <h2>User Management</h2>
        {!isAdding && (
          <button className="btn btn-add" onClick={() => setIsAdding(true)}>
            + Add User
          </button>
        )}
      </div>

      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {isAdding && (
        <form onSubmit={handleCreateUser} className="user-form">
          <h3>Create New User</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Username *</label>
              <input
                type="text"
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Password *</label>
              <input
                type="password"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Full Name *</label>
              <input
                type="text"
                value={newUser.full_name}
                onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Email *</label>
              <input
                type="email"
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                required
              />
            </div>
          </div>
          <div className="form-group checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={newUser.is_admin}
                onChange={(e) => setNewUser({ ...newUser, is_admin: e.target.checked })}
              />
              Administrator privileges
            </label>
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={() => setIsAdding(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Create User
            </button>
          </div>
        </form>
      )}

      <div className="users-table">
        <div className="table-header">
          <div>Username</div>
          <div>Full Name</div>
          <div>Email</div>
          <div>Role</div>
          <div>Actions</div>
        </div>
        <div className="table-body">
          {users.map((user) => (
            <div key={user.username} className="table-row">
              <div>{user.username}</div>
              <div>{user.full_name}</div>
              <div>{user.email}</div>
              <div>
                <span className={`role-badge ${user.is_admin ? 'admin' : 'user'}`}>
                  {user.is_admin ? 'Admin' : 'User'}
                </span>
              </div>
              <div>
                {user.username !== 'admin' && (
                  <button
                    className="btn btn-small btn-danger"
                    onClick={() => handleDeleteUser(user.username)}
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


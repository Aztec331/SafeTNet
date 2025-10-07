import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Button,
  Grid,
  Alert,
} from '@mui/material';
import { SubAdminProfile, SubAdminCreateRequest, SubAdminUpdateRequest } from '../types';

interface SubAdminFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: SubAdminCreateRequest | SubAdminUpdateRequest) => void;
  subAdmin?: SubAdminProfile | null;
}

const SubAdminForm: React.FC<SubAdminFormProps> = ({
  open,
  onClose,
  onSubmit,
  subAdmin,
}) => {
  const [formData, setFormData] = useState<SubAdminCreateRequest>({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    permissions: 'READ_ONLY',
    assigned_scope: 'LOCAL',
    is_active: true,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const isEditing = !!subAdmin;

  useEffect(() => {
    if (subAdmin) {
      setFormData({
        username: subAdmin.user_username,
        email: subAdmin.user_email,
        password: '',
        password_confirm: '',
        first_name: '',
        last_name: '',
        permissions: subAdmin.permissions,
        assigned_scope: subAdmin.assigned_scope,
        is_active: subAdmin.is_active,
      });
    } else {
      setFormData({
        username: '',
        email: '',
        password: '',
        password_confirm: '',
        first_name: '',
        last_name: '',
        permissions: 'READ_ONLY',
        assigned_scope: 'LOCAL',
        is_active: true,
      });
    }
    setErrors({});
  }, [subAdmin, open]);

  const handleChange = (field: keyof SubAdminCreateRequest) => (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement> | any
  ) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: '',
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!isEditing) {
      if (!formData.username.trim()) {
        newErrors.username = 'Username is required';
      }
      if (!formData.email.trim()) {
        newErrors.email = 'Email is required';
      } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = 'Email is invalid';
      }
      if (!formData.password) {
        newErrors.password = 'Password is required';
      } else if (formData.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters';
      }
      if (formData.password !== formData.password_confirm) {
        newErrors.password_confirm = 'Passwords do not match';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      if (isEditing) {
        const updateData: SubAdminUpdateRequest = {
          permissions: formData.permissions,
          assigned_scope: formData.assigned_scope,
          is_active: formData.is_active,
        };
        onSubmit(updateData);
      } else {
        onSubmit(formData);
      }
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {isEditing ? 'Edit SubAdmin' : 'Create New SubAdmin'}
      </DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <Grid container spacing={2}>
            {!isEditing && (
              <>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Username"
                    value={formData.username}
                    onChange={handleChange('username')}
                    error={!!errors.username}
                    helperText={errors.username}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange('email')}
                    error={!!errors.email}
                    helperText={errors.email}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Password"
                    type="password"
                    value={formData.password}
                    onChange={handleChange('password')}
                    error={!!errors.password}
                    helperText={errors.password}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Confirm Password"
                    type="password"
                    value={formData.password_confirm}
                    onChange={handleChange('password_confirm')}
                    error={!!errors.password_confirm}
                    helperText={errors.password_confirm}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="First Name"
                    value={formData.first_name}
                    onChange={handleChange('first_name')}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    value={formData.last_name}
                    onChange={handleChange('last_name')}
                  />
                </Grid>
              </>
            )}
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Permissions</InputLabel>
                <Select
                  value={formData.permissions}
                  onChange={handleChange('permissions')}
                  label="Permissions"
                >
                  <MenuItem value="READ_ONLY">Read Only</MenuItem>
                  <MenuItem value="READ_WRITE">Read & Write</MenuItem>
                  <MenuItem value="FULL_ACCESS">Full Access</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Assigned Scope</InputLabel>
                <Select
                  value={formData.assigned_scope}
                  onChange={handleChange('assigned_scope')}
                  label="Assigned Scope"
                >
                  <MenuItem value="LOCAL">Local</MenuItem>
                  <MenuItem value="REGIONAL">Regional</MenuItem>
                  <MenuItem value="GLOBAL">Global</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={handleChange('is_active')}
                  />
                }
                label="Active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Saving...' : (isEditing ? 'Update' : 'Create')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default SubAdminForm;

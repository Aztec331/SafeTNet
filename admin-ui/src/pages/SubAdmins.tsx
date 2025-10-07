import React, { useState, useEffect } from 'react';
import {
  Container,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Pagination,
  Alert,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { subAdminService } from '../services/subAdminService';
import { SubAdminProfile, SubAdminCreateRequest, SubAdminUpdateRequest } from '../types';
import SubAdminForm from '../components/SubAdminForm';

const SubAdmins: React.FC = () => {
  const { user, logout } = useAuth();
  const [subAdmins, setSubAdmins] = useState<SubAdminProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [search, setSearch] = useState('');
  const [filterPermission, setFilterPermission] = useState('');
  const [filterScope, setFilterScope] = useState('');
  const [filterActive, setFilterActive] = useState<boolean | null>(null);
  
  // Dialog states
  const [openDialog, setOpenDialog] = useState(false);
  const [editingSubAdmin, setEditingSubAdmin] = useState<SubAdminProfile | null>(null);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  // Check if user is SUPER_ADMIN
  const isSuperAdmin = user?.role === 'SUPER_ADMIN';

  useEffect(() => {
    if (isSuperAdmin) {
      fetchSubAdmins();
    }
  }, [isSuperAdmin, page, search, filterPermission, filterScope, filterActive]);

  const fetchSubAdmins = async () => {
    setLoading(true);
    setError('');
    try {
      const params: any = {
        page,
        page_size: 10,
      };
      
      if (search) params.search = search;
      if (filterPermission) params.permissions = filterPermission;
      if (filterScope) params.assigned_scope = filterScope;
      if (filterActive !== null) params.is_active = filterActive;

      const response = await subAdminService.getSubAdmins(params);
      setSubAdmins(response.results);
      setTotalCount(response.count);
      setTotalPages(Math.ceil(response.count / 10));
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to fetch SubAdmins');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingSubAdmin(null);
    setOpenDialog(true);
  };

  const handleEdit = (subAdmin: SubAdminProfile) => {
    setEditingSubAdmin(subAdmin);
    setOpenDialog(true);
  };

  const handleDelete = (id: number) => {
    setDeletingId(id);
    setDeleteDialog(true);
  };

  const confirmDelete = async () => {
    if (!deletingId) return;
    
    try {
      await subAdminService.deleteSubAdmin(deletingId);
      setSuccess('SubAdmin deleted successfully');
      fetchSubAdmins();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to delete SubAdmin');
    } finally {
      setDeleteDialog(false);
      setDeletingId(null);
    }
  };

  const handleFormSubmit = async (data: SubAdminCreateRequest | SubAdminUpdateRequest) => {
    try {
      if (editingSubAdmin) {
        await subAdminService.updateSubAdmin(editingSubAdmin.id, data as SubAdminUpdateRequest);
        setSuccess('SubAdmin updated successfully');
      } else {
        await subAdminService.createSubAdmin(data as SubAdminCreateRequest);
        setSuccess('SubAdmin created successfully');
      }
      setOpenDialog(false);
      fetchSubAdmins();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to save SubAdmin');
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  const getPermissionColor = (permission: string) => {
    switch (permission) {
      case 'FULL_ACCESS': return 'error';
      case 'READ_WRITE': return 'warning';
      case 'READ_ONLY': return 'info';
      default: return 'default';
    }
  };

  const getScopeColor = (scope: string) => {
    switch (scope) {
      case 'GLOBAL': return 'error';
      case 'REGIONAL': return 'warning';
      case 'LOCAL': return 'info';
      default: return 'default';
    }
  };

  if (!isSuperAdmin) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <Alert severity="error">
          Access denied. Only SUPER_ADMIN can access this page.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Sub-Admins Management
          </Typography>
          <Typography variant="body1" sx={{ mr: 2 }}>
            Welcome, {user?.username} ({user?.role})
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Success/Error Messages */}
        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Filters and Search */}
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
            <TextField
              size="small"
              placeholder="Search SubAdmins..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
              sx={{ minWidth: 200 }}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Permission</InputLabel>
              <Select
                value={filterPermission}
                onChange={(e) => setFilterPermission(e.target.value)}
                label="Permission"
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="READ_ONLY">Read Only</MenuItem>
                <MenuItem value="READ_WRITE">Read & Write</MenuItem>
                <MenuItem value="FULL_ACCESS">Full Access</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Scope</InputLabel>
              <Select
                value={filterScope}
                onChange={(e) => setFilterScope(e.target.value)}
                label="Scope"
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="LOCAL">Local</MenuItem>
                <MenuItem value="REGIONAL">Regional</MenuItem>
                <MenuItem value="GLOBAL">Global</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterActive === null ? '' : filterActive}
                onChange={(e) => setFilterActive(e.target.value === '' ? null : e.target.value === 'true')}
                label="Status"
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="true">Active</MenuItem>
                <MenuItem value="false">Inactive</MenuItem>
              </Select>
            </FormControl>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleCreate}
              sx={{ ml: 'auto' }}
            >
              Add SubAdmin
            </Button>
          </Box>
        </Paper>

        {/* SubAdmins Table */}
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Username</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Full Name</TableCell>
                  <TableCell>Permissions</TableCell>
                  <TableCell>Scope</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Created By</TableCell>
                  <TableCell>Created At</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : subAdmins.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center">
                      No SubAdmins found
                    </TableCell>
                  </TableRow>
                ) : (
                  subAdmins.map((subAdmin) => (
                    <TableRow key={subAdmin.id}>
                      <TableCell>{subAdmin.user_username}</TableCell>
                      <TableCell>{subAdmin.user_email}</TableCell>
                      <TableCell>{subAdmin.user_full_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={subAdmin.permissions.replace('_', ' ')}
                          color={getPermissionColor(subAdmin.permissions) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={subAdmin.assigned_scope}
                          color={getScopeColor(subAdmin.assigned_scope) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={subAdmin.is_active ? 'Active' : 'Inactive'}
                          color={subAdmin.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{subAdmin.created_by_username}</TableCell>
                      <TableCell>
                        {new Date(subAdmin.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            onClick={() => handleEdit(subAdmin)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDelete(subAdmin.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>

        {/* Pagination */}
        {totalPages > 1 && (
          <Box display="flex" justifyContent="center" mt={2}>
            <Pagination
              count={totalPages}
              page={page}
              onChange={(_, newPage) => setPage(newPage)}
              color="primary"
            />
          </Box>
        )}

        {/* SubAdmin Form Dialog */}
        <SubAdminForm
          open={openDialog}
          onClose={() => setOpenDialog(false)}
          onSubmit={handleFormSubmit}
          subAdmin={editingSubAdmin}
        />

        {/* Delete Confirmation Dialog */}
        <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
          <DialogTitle>Confirm Delete</DialogTitle>
          <DialogContent>
            Are you sure you want to delete this SubAdmin? This action cannot be undone.
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
            <Button onClick={confirmDelete} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default SubAdmins;

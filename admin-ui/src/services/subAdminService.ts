import api from './api';
import { 
  SubAdminProfile, 
  SubAdminCreateRequest, 
  SubAdminUpdateRequest, 
  PaginatedResponse 
} from '../types';

export const subAdminService = {
  // Get paginated list of SubAdmins
  getSubAdmins: async (params?: {
    page?: number;
    page_size?: number;
    search?: string;
    permissions?: string;
    assigned_scope?: string;
    is_active?: boolean;
    ordering?: string;
  }): Promise<PaginatedResponse<SubAdminProfile>> => {
    const response = await api.get('/auth/admin/subadmins/', { params });
    return response.data;
  },

  // Get single SubAdmin by ID
  getSubAdmin: async (id: number): Promise<SubAdminProfile> => {
    const response = await api.get(`/auth/admin/subadmins/${id}/`);
    return response.data;
  },

  // Create new SubAdmin
  createSubAdmin: async (data: SubAdminCreateRequest): Promise<SubAdminProfile> => {
    const response = await api.post('/auth/admin/subadmins/', data);
    return response.data;
  },

  // Update SubAdmin
  updateSubAdmin: async (id: number, data: SubAdminUpdateRequest): Promise<SubAdminProfile> => {
    const response = await api.put(`/auth/admin/subadmins/${id}/`, data);
    return response.data;
  },

  // Delete SubAdmin
  deleteSubAdmin: async (id: number): Promise<void> => {
    await api.delete(`/auth/admin/subadmins/${id}/`);
  },
};

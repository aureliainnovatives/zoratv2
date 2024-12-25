import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { environment } from 'src/environments/environment';
import { AuthService } from '../../../core/services/auth.service';

export interface RolePermission {
  _id?: string;
  permissionId: string | {
    _id: string;
    name: string;
    description: string;
  };
  moduleId: string | {
    _id: string;
    name: string;
    description: string;
  };
}

export interface Role {
  _id: string;
  name: string;
  description: string;
  permissions: RolePermission[];
  createdAt: string;
  updatedAt: string;
  [key: string]: any;
}

interface ApiResponse<T> {
  data: T;
}

@Injectable({
  providedIn: 'root'
})
export class RolesService {
  private apiUrl = `${environment.apiUrl}/roles`;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getRoles(): Observable<Role[]> {
    return this.http.get<ApiResponse<Role[]>>(this.apiUrl, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.data)
    );
  }

  getRole(id: string): Observable<Role> {
    return this.http.get<ApiResponse<Role>>(`${this.apiUrl}/${id}`, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.data)
    );
  }

  createRole(role: Partial<Role>): Observable<Role> {
    return this.http.post<ApiResponse<Role>>(this.apiUrl, role, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.data)
    );
  }

  updateRole(id: string, role: Partial<Role>): Observable<Role> {
    return this.http.put<ApiResponse<Role>>(`${this.apiUrl}/${id}`, role, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.data)
    );
  }

  deleteRole(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, {
      headers: this.getHeaders()
    });
  }
} 
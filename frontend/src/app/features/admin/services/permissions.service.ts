import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { AuthService } from '../../../core/services/auth.service';

export interface Permission {
  _id: string;
  name: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  [key: string]: string;
}

@Injectable({
  providedIn: 'root'
})
export class PermissionsService {
  private apiUrl = `${environment.apiUrl}/permissions`;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getPermissions(): Observable<Permission[]> {
    return this.http.get<Permission[]>(this.apiUrl, {
      headers: this.getHeaders()
    });
  }

  getPermission(id: string): Observable<Permission> {
    return this.http.get<Permission>(`${this.apiUrl}/${id}`, {
      headers: this.getHeaders()
    });
  }

  createPermission(permission: Partial<Permission>): Observable<Permission> {
    return this.http.post<Permission>(this.apiUrl, permission, {
      headers: this.getHeaders()
    });
  }

  updatePermission(id: string, permission: Partial<Permission>): Observable<Permission> {
    return this.http.put<Permission>(`${this.apiUrl}/${id}`, permission, {
      headers: this.getHeaders()
    });
  }

  deletePermission(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, {
      headers: this.getHeaders()
    });
  }
} 
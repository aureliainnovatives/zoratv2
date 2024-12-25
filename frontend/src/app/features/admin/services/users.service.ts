import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { AuthService } from '../../../core/services/auth.service';
import { Role } from './roles.service';
import { Permission } from './permissions.service';
import { map } from 'rxjs/operators';

export interface User {
  _id: string;
  name: string;
  email: string;
  role: string | Role;  // Can be either role ID or populated Role object
  createdAt: string;
  updatedAt: string;
}

interface ApiResponse<T> {
  data: T;
}

@Injectable({
  providedIn: 'root'
})
export class UsersService {
  private apiUrl = `${environment.apiUrl}/users`;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getUsers(): Observable<User[]> {
    return this.http.get<ApiResponse<User[]>>(this.apiUrl, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.data)
    );
  }

  getUser(id: string): Observable<User> {
    return this.http.get<ApiResponse<User>>(`${this.apiUrl}/${id}`, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.data)
    );
  }

  createUser(user: Partial<User>): Observable<User> {
    return this.http.post<ApiResponse<User>>(this.apiUrl, user, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.data)
    );
  }

  updateUser(id: string, user: Partial<User>): Observable<User> {
    // Ensure password is not sent in update if it's not changed
    const { password, ...userData } = user as any;
    
    return this.http.put<ApiResponse<User>>(`${this.apiUrl}/${id}`, userData, {
      headers: this.getHeaders()
    }).pipe(
      map(response => response.data)
    );
  }

  deleteUser(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, {
      headers: this.getHeaders()
    });
  }
} 
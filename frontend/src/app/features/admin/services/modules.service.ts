import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { AuthService } from '../../../core/services/auth.service';

export interface Module {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  [key: string]: string;
}

@Injectable({
  providedIn: 'root'
})
export class ModulesService {
  private apiUrl = `${environment.apiUrl}/modules`;

  constructor(
    private http: HttpClient,
    private authService: AuthService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders().set('Authorization', `Bearer ${token}`);
  }

  getModules(): Observable<Module[]> {
    return this.http.get<Module[]>(this.apiUrl, {
      headers: this.getHeaders()
    });
  }

  getModule(id: string): Observable<Module> {
    return this.http.get<Module>(`${this.apiUrl}/${id}`, {
      headers: this.getHeaders()
    });
  }

  createModule(module: Partial<Module>): Observable<Module> {
    return this.http.post<Module>(this.apiUrl, module, {
      headers: this.getHeaders()
    });
  }

  updateModule(id: string, module: Partial<Module>): Observable<Module> {
    return this.http.put<Module>(`${this.apiUrl}/${id}`, module, {
      headers: this.getHeaders()
    });
  }

  deleteModule(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`, {
      headers: this.getHeaders()
    });
  }
} 
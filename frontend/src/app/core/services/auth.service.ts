import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, of, throwError } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { JwtHelperService } from '@auth0/angular-jwt';

export interface User {
  _id: string;
  name: string;
  email: string;
  role: {
    _id: string;
    name: string;
    permissions: Array<{
      permissionId: string;
      moduleId: string;
    }>;
  };
}

export interface AuthResponse {
  token: string;
  refreshToken: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser$: Observable<User | null>;
  private jwtHelper: JwtHelperService = new JwtHelperService();
  private refreshTokenTimeout?: any;

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.currentUserSubject = new BehaviorSubject<User | null>(this.getUserFromToken());
    this.currentUser$ = this.currentUserSubject.asObservable();
    this.startRefreshTokenTimer();
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  login(credentials: { email: string; password: string }): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${environment.apiUrl}/auth/login`, credentials)
      .pipe(
        tap(response => this.handleAuthentication(response)),
        catchError(error => {
          console.error('Login error:', error);
          return throwError(() => error);
        })
      );
  }

  signup(userData: { name: string; email: string; password: string }): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${environment.apiUrl}/auth/signup`, userData)
      .pipe(
        tap(response => this.handleAuthentication(response)),
        catchError(error => {
          console.error('Signup error:', error);
          return throwError(() => error);
        })
      );
  }

  logout(): void {
    localStorage.removeItem(environment.auth.tokenKey);
    localStorage.removeItem(environment.auth.refreshTokenKey);
    localStorage.removeItem(environment.auth.tokenExpiryKey);
    this.stopRefreshTokenTimer();
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  refreshToken(): Observable<AuthResponse> {
    const refreshToken = localStorage.getItem(environment.auth.refreshTokenKey);
    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    return this.http.post<AuthResponse>(`${environment.apiUrl}/auth/refresh-token`, { refreshToken })
      .pipe(
        tap(response => this.handleAuthentication(response)),
        catchError(error => {
          console.error('Token refresh error:', error);
          this.logout();
          return throwError(() => error);
        })
      );
  }

  isAuthenticated(): boolean {
    const token = localStorage.getItem(environment.auth.tokenKey);
    return !!token && !this.jwtHelper.isTokenExpired(token);
  }

  hasPermission(moduleId: string, permission: string): boolean {
    const user = this.currentUserValue;
    if (!user || !user.role || !user.role.permissions) {
      return false;
    }

    return user.role.permissions.some(p => 
      p.moduleId === moduleId && 
      p.permissionId === permission
    );
  }

  hasRole(roleName: string): boolean {
    const user = this.currentUserValue;
    return user?.role?.name === roleName;
  }

  // OAuth Methods
  loginWithGoogle(): void {
    window.location.href = `${environment.apiUrl}/auth/google`;
  }

  loginWithFacebook(): void {
    window.location.href = `${environment.apiUrl}/auth/facebook`;
  }

  loginWithGithub(): void {
    window.location.href = `${environment.apiUrl}/auth/github`;
  }

  loginWithLinkedIn(): void {
    window.location.href = `${environment.apiUrl}/auth/linkedin`;
  }

  loginWithX(): void {
    window.location.href = `${environment.apiUrl}/auth/x`;
  }

  // Private helper methods
  private handleAuthentication(response: AuthResponse): void {
    localStorage.setItem(environment.auth.tokenKey, response.token);
    localStorage.setItem(environment.auth.refreshTokenKey, response.refreshToken);
    
    const tokenExpiry = this.jwtHelper.getTokenExpirationDate(response.token);
    if (tokenExpiry) {
      localStorage.setItem(environment.auth.tokenExpiryKey, tokenExpiry.toISOString());
    }

    this.currentUserSubject.next(response.user);
    this.startRefreshTokenTimer();
  }

  private getUserFromToken(): User | null {
    try {
      const token = localStorage.getItem(environment.auth.tokenKey);
      if (!token) {
        return null;
      }

      const decodedToken = this.jwtHelper.decodeToken(token);
      if (!decodedToken) {
        return null;
      }

      return decodedToken.user;
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }

  private startRefreshTokenTimer(): void {
    const token = localStorage.getItem(environment.auth.tokenKey);
    if (!token) {
      return;
    }

    const expires = this.jwtHelper.getTokenExpirationDate(token);
    if (!expires) {
      return;
    }

    const timeout = expires.getTime() - Date.now() - (60 * 1000); // Refresh 1 minute before expiry
    this.refreshTokenTimeout = setTimeout(() => this.refreshToken().subscribe(), timeout);
  }

  private stopRefreshTokenTimer(): void {
    if (this.refreshTokenTimeout) {
      clearTimeout(this.refreshTokenTimeout);
    }
  }
} 
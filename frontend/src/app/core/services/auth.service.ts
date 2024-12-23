import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { JwtHelperService } from '@auth0/angular-jwt';
import { Router } from '@angular/router';

export interface User {
  id: string;
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

export interface LoginResponse {
  token: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSubject: BehaviorSubject<User | null>;
  public currentUser$: Observable<User | null>;
  private jwtHelper = new JwtHelperService();
  private initialized = false;

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.currentUserSubject = new BehaviorSubject<User | null>(null);
    this.currentUser$ = this.currentUserSubject.asObservable();
    this.initializeUser();
  }

  private initializeUser(): void {
    if (this.initialized) return;
    
    try {
      const user = this.getCurrentUser();
      if (user) {
        this.currentUserSubject.next(user);
      }
    } catch (error) {
      console.error('Error initializing user:', error);
      // Don't logout here, just log the error
    }
    
    this.initialized = true;
  }

  public get currentUserValue(): User | null {
    return this.currentUserSubject.value;
  }

  getToken(): string | null {
    const token = localStorage.getItem(environment.auth.tokenKey);
    if (!token) return null;
    
    try {
      // Only check expiration if we can decode the token
      if (this.jwtHelper.isTokenExpired(token)) {
        this.silentLogout();
        return null;
      }
      return token;
    } catch (error) {
      console.error('Error checking token expiration:', error);
      // Don't remove token if we just can't decode it
      return token;
    }
  }

  getCurrentUser(): User | null {
    const token = this.getToken();
    if (!token) return null;

    try {
      const userStr = localStorage.getItem('current_user');
      if (!userStr) {
        // If no user data but we have a valid token, try to decode user from token
        const decodedToken = this.jwtHelper.decodeToken(token);
        if (decodedToken && this.isValidDecodedToken(decodedToken)) {
          const user: User = {
            id: decodedToken.id,
            name: decodedToken.name,
            email: decodedToken.email,
            role: decodedToken.role
          };
          // Store user data for future use
          localStorage.setItem('current_user', JSON.stringify(user));
          return user;
        }
        return null;
      }

      const user = JSON.parse(userStr);
      if (!this.isValidUser(user)) {
        // If user data is invalid but token is valid, just clear user data
        localStorage.removeItem('current_user');
        return null;
      }
      return user;
    } catch (error) {
      console.error('Error getting current user:', error);
      // Don't logout on parse error, just return null
      return null;
    }
  }

  private isValidDecodedToken(decodedToken: any): boolean {
    return decodedToken 
      && typeof decodedToken.id === 'string'
      && typeof decodedToken.name === 'string'
      && typeof decodedToken.email === 'string'
      && decodedToken.role;
  }

  private isValidUser(user: any): user is User {
    return user 
      && typeof user.id === 'string'
      && typeof user.name === 'string'
      && typeof user.email === 'string'
      && user.role
      && typeof user.role._id === 'string'
      && typeof user.role.name === 'string'
      && Array.isArray(user.role.permissions);
  }

  private silentLogout(): void {
    localStorage.removeItem(environment.auth.tokenKey);
    localStorage.removeItem('current_user');
    if (this.currentUserSubject) {
      this.currentUserSubject.next(null);
    }
  }

  logout(): void {
    this.silentLogout();
    this.router.navigate(['/auth/login']);
  }

  login(credentials: { email: string; password: string }): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${environment.apiUrl}/auth/login`, credentials)
      .pipe(
        tap(response => {
          if (response.token) {
            localStorage.setItem(environment.auth.tokenKey, response.token);
            localStorage.setItem('current_user', JSON.stringify(response.user));
            this.currentUserSubject.next(response.user);
          }
        })
      );
  }

  signup(userData: { name: string; email: string; password: string }): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${environment.apiUrl}/auth/signup`, userData)
      .pipe(
        tap(response => {
          if (response.token) {
            localStorage.setItem(environment.auth.tokenKey, response.token);
            localStorage.setItem('current_user', JSON.stringify(response.user));
            this.currentUserSubject.next(response.user);
          }
        })
      );
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
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
} 
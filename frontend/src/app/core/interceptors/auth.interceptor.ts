import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, filter, take, switchMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { environment } from '../../../environments/environment';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);

  constructor(private authService: AuthService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Skip token for certain endpoints
    if (this.shouldSkipToken(request.url)) {
      return next.handle(request);
    }

    // Add auth header with JWT if available
    const token = localStorage.getItem(environment.auth.tokenKey);
    if (token) {
      request = this.addToken(request, token);
    }

    // Add CSRF token if enabled
    if (environment.security.enableCSRF) {
      const csrfToken = this.getCsrfToken();
      if (csrfToken) {
        request = request.clone({
          headers: request.headers.set(environment.security.csrfHeaderName, csrfToken)
        });
      }
    }

    return next.handle(request).pipe(
      catchError(error => {
        if (error instanceof HttpErrorResponse && error.status === 401) {
          return this.handle401Error(request, next);
        }
        return throwError(() => error);
      })
    );
  }

  private addToken(request: HttpRequest<any>, token: string): HttpRequest<any> {
    return request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  private handle401Error(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);

      return this.authService.refreshToken().pipe(
        switchMap(response => {
          this.isRefreshing = false;
          this.refreshTokenSubject.next(response.token);
          return next.handle(this.addToken(request, response.token));
        }),
        catchError(error => {
          this.isRefreshing = false;
          this.authService.logout();
          return throwError(() => error);
        })
      );
    }

    return this.refreshTokenSubject.pipe(
      filter(token => token !== null),
      take(1),
      switchMap(token => next.handle(this.addToken(request, token)))
    );
  }

  private shouldSkipToken(url: string): boolean {
    // Skip token for auth endpoints and public APIs
    const skipUrls = [
      `${environment.apiUrl}/auth/login`,
      `${environment.apiUrl}/auth/signup`,
      `${environment.apiUrl}/auth/refresh-token`
    ];
    return skipUrls.some(skipUrl => url.includes(skipUrl));
  }

  private getCsrfToken(): string | null {
    // Get CSRF token from cookie if enabled
    if (environment.security.enableCSRF) {
      const name = environment.security.csrfCookieName + '=';
      const decodedCookie = decodeURIComponent(document.cookie);
      const cookieArray = decodedCookie.split(';');
      
      for (let cookie of cookieArray) {
        cookie = cookie.trim();
        if (cookie.indexOf(name) === 0) {
          return cookie.substring(name.length, cookie.length);
        }
      }
    }
    return null;
  }
} 
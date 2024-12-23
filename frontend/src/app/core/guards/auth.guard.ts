import { inject } from '@angular/core';
import { Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard = (route: ActivatedRouteSnapshot, state: RouterStateSnapshot) => {
  const router = inject(Router);
  const authService = inject(AuthService);

  if (!authService.isAuthenticated()) {
    router.navigate(['/login'], { queryParams: { returnUrl: state.url }});
    return false;
  }

  // Check for required permissions
  const requiredPermissions = route.data['permissions'] as Array<{ moduleId: string, permission: string }>;
  if (requiredPermissions) {
    const hasAllPermissions = requiredPermissions.every(({ moduleId, permission }) => 
      authService.hasPermission(moduleId, permission)
    );

    if (!hasAllPermissions) {
      router.navigate(['/']);
      return false;
    }
  }

  // Check for required roles
  const requiredRoles = route.data['roles'] as string[];
  if (requiredRoles) {
    const hasRequiredRole = requiredRoles.some(role => 
      authService.hasRole(role)
    );

    if (!hasRequiredRole) {
      router.navigate(['/']);
      return false;
    }
  }

  return true;
}; 
import { Component, computed, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { ThemeService } from '../../core/services/theme.service';
import { AuthService } from '../../core/services/auth.service';

interface MenuItem {
  label: string;
  icon: string;
  route?: string;
  children?: MenuItem[];
  expanded?: boolean;
}

@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './main-layout.component.html'
})
export class MainLayoutComponent {
  isDarkMode = computed(() => this.themeService.theme() === 'dark');
  currentUser = computed(() => this.authService.currentUserValue);
  isSidebarCollapsed = signal<boolean>(false);

  menuItems: MenuItem[] = [
    {
      icon: 'dashboard',
      label: 'Dashboard',
      route: '/dashboard'
    },
    {
      icon: 'science',
      label: 'Playground',
      route: '/playground'
    },
    {
      icon: 'admin_panel_settings',
      label: 'Admin',
      expanded: false,
      children: [
        { icon: 'group', label: 'Users', route: '/admin/users' },
        { icon: 'badge', label: 'Roles', route: '/admin/roles' },
        { icon: 'key', label: 'Permissions', route: '/admin/permissions' },
        { icon: 'extension', label: 'Modules', route: '/admin/modules' }
      ]
    },
    {
      icon: 'smart_toy',
      label: 'Agents',
      route: '/agents'
    },
    {
      icon: 'account_tree',
      label: 'Workflows',
      route: '/workflows'
    },
    {
      icon: 'integration_instructions',
      label: 'Integrations',
      route: '/integrations'
    },
    {
      icon: 'settings',
      label: 'Settings',
      expanded: false,
      children: [
        { icon: 'security', label: 'Authentication', route: '/settings/auth' },
        { icon: 'api', label: 'API Keys', route: '/settings/api-keys' },
        { icon: 'notifications', label: 'Notifications', route: '/settings/notifications' }
      ]
    }
  ];

  constructor(
    private themeService: ThemeService,
    private authService: AuthService,
    private router: Router
  ) {}

  toggleTheme() {
    this.themeService.toggleTheme();
  }

  toggleSidebar() {
    this.isSidebarCollapsed.update(v => !v);
  }

  toggleMenuItem(item: MenuItem) {
    item.expanded = !item.expanded;
  }

  isMenuActive(item: MenuItem): boolean {
    if (item.route) {
      return this.router.isActive(item.route, {
        paths: 'exact',
        queryParams: 'exact',
        fragment: 'ignored',
        matrixParams: 'ignored'
      });
    }
    return item.children?.some(child => 
      this.router.isActive(child.route!, {
        paths: 'exact',
        queryParams: 'exact',
        fragment: 'ignored',
        matrixParams: 'ignored'
      })
    ) || false;
  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
} 
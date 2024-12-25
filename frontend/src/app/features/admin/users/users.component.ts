import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { User, UsersService } from '../services/users.service';
import { environment } from 'src/environments/environment';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog/confirm-dialog.component';
import { LanguageService } from '../../../core/services/language.service';
import { NotificationService } from '../../../core/services/notification.service';

interface SortConfig {
  column: string;
  direction: 'asc' | 'desc';
}

interface Role {
  _id: string;
  name: string;
  description: string;
  permissions: any[];
}

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
    MatDialogModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './users.component.html'
})
export class UsersComponent implements OnInit {
  users: User[] = [];
  filteredUsers: User[] = [];
  loading = false;
  searchTerm = '';
  currentPage = 1;
  pageSize = environment.table.defaultItemsPerPage;
  totalItems = 0;
  sortConfig: SortConfig = {
    column: 'createdAt',
    direction: 'desc'
  };
  Math = Math;
  originalUsers: User[] = [];

  constructor(
    private usersService: UsersService,
    private router: Router,
    private dialog: MatDialog,
    public languageService: LanguageService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  get startIndex(): number {
    return (this.currentPage - 1) * this.pageSize;
  }

  get endIndex(): number {
    return Math.min(this.startIndex + this.pageSize, this.totalItems);
  }

  get totalPages(): number {
    return Math.ceil(this.totalItems / this.pageSize);
  }

  isObjectRole(role: string | Role): role is Role {
    return typeof role === 'object' && role !== null;
  }

  getRoleName(role: Role): string {
    return role.name;
  }

  private async loadUsers(): Promise<void> {
    this.loading = true;
    try {
      const users = await this.usersService.getUsers().toPromise();
      if (users) {
        this.originalUsers = users;
        this.totalItems = this.originalUsers.length;
        this.applyFilters();
      }
    } catch (error) {
      console.error('Error loading users:', error);
      this.notificationService.error(
        this.languageService.translate('common.status.error')
      );
    } finally {
      this.loading = false;
    }
  }

  onSearch(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onSort(column: string): void {
    this.sortConfig = {
      column,
      direction: this.sortConfig.column === column && this.sortConfig.direction === 'asc' ? 'desc' : 'asc'
    };
    this.applyFilters();
  }

  getSortIcon(column: string): string {
    if (this.sortConfig.column !== column) {
      return 'unfold_more';
    }
    return this.sortConfig.direction === 'asc' ? 'expand_less' : 'expand_more';
  }

  getSerialNumber(index: number): number {
    const baseNumber = this.startIndex + index + 1;
    if (this.sortConfig.column === 'no' && this.sortConfig.direction === 'desc') {
      return this.totalItems - (this.startIndex + index);
    }
    return baseNumber;
  }

  onPageChange(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.applyFilters();
    }
  }

  onPageSizeChange(size: number): void {
    this.pageSize = size;
    this.currentPage = 1;
    this.applyFilters();
  }

  private applyFilters(): void {
    let filtered = [...this.originalUsers];

    // Apply search
    if (this.searchTerm) {
      const term = this.searchTerm.toLowerCase();
      filtered = filtered.filter(user =>
        user.name.toLowerCase().includes(term) ||
        user.email.toLowerCase().includes(term) ||
        (this.isObjectRole(user.role) && user.role.name.toLowerCase().includes(term))
      );
    }

    // Apply sort
    filtered.sort((a, b) => {
      if (this.sortConfig.column === 'no') {
        // Get the original indices
        const aIndex = this.originalUsers.indexOf(a);
        const bIndex = this.originalUsers.indexOf(b);
        // Sort by index
        return this.sortConfig.direction === 'asc' 
          ? aIndex - bIndex
          : bIndex - aIndex;
      }

      let aValue = this.getSortValue(a, this.sortConfig.column);
      let bValue = this.getSortValue(b, this.sortConfig.column);

      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = (bValue as string).toLowerCase();
      }

      return this.sortConfig.direction === 'asc'
        ? aValue < bValue ? -1 : aValue > bValue ? 1 : 0
        : aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
    });

    this.totalItems = filtered.length;

    // Apply pagination
    const start = this.startIndex;
    const end = start + this.pageSize;
    this.filteredUsers = filtered.slice(start, end);
  }

  private getSortValue(user: User, column: string): any {
    switch (column) {
      case 'role':
        return this.isObjectRole(user.role) ? user.role.name : user.role;
      default:
        return (user as any)[column];
    }
  }

  showRoleDetails(user: User): void {
    const roleId = typeof user.role === 'string' ? user.role : user.role['_id'];
    import('./role-details-dialog/role-details-dialog.component').then(m => {
      this.dialog.open(m.RoleDetailsDialogComponent, {
        data: { roleId },
        width: '600px'
      });
    });
  }

  async onDelete(user: User): Promise<void> {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: this.languageService.translate('users.delete.title'),
        message: this.languageService.translate('users.delete.message', { name: user.name }),
        confirmText: this.languageService.translate('common.actions.delete'),
        cancelText: this.languageService.translate('common.actions.cancel')
      }
    });

    const result = await dialogRef.afterClosed().toPromise();
    if (result) {
      try {
        await this.usersService.deleteUser(user._id).toPromise();
        this.notificationService.success(
          this.languageService.translate('users.messages.deleteSuccess')
        );
        this.loadUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
        this.notificationService.error(
          this.languageService.translate('common.status.error')
        );
      }
    }
  }

  onAdd(): void {
    this.router.navigate(['/admin/users/add']);
  }

  onEdit(user: User): void {
    this.router.navigate([`/admin/users/edit/${user._id}`]);
  }
} 
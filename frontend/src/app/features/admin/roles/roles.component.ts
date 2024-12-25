import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { Role, RolesService } from '../services/roles.service';
import { environment } from 'src/environments/environment';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog/confirm-dialog.component';
import { LanguageService } from '../../../core/services/language.service';
import { NotificationService } from '../../../core/services/notification.service';

interface SortConfig {
  column: string;
  direction: 'asc' | 'desc';
}

@Component({
  selector: 'app-roles',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, MatDialogModule],
  templateUrl: './roles.component.html'
})
export class RolesComponent implements OnInit {
  roles: Role[] = [];
  searchTerm: string = '';
  currentPage: number = 1;
  itemsPerPage = environment.table.defaultItemsPerPage;
  itemsPerPageOptions = environment.table.itemsPerPageOptions;
  totalItems: number = 0;
  sortConfig: SortConfig = {
    column: 'name',
    direction: 'asc'
  };
  loading: boolean = false;
  originalRoles: Role[] = [];

  constructor(
    private rolesService: RolesService,
    private router: Router,
    private route: ActivatedRoute,
    private dialog: MatDialog,
    private languageService: LanguageService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadRoles();
  }

  get startIndex(): number {
    return (this.currentPage - 1) * this.itemsPerPage;
  }

  get endIndex(): number {
    return Math.min(this.startIndex + this.itemsPerPage, this.totalItems);
  }

  get totalPages(): number {
    return Math.ceil(this.totalItems / this.itemsPerPage);
  }

  loadRoles(): void {
    this.loading = true;
    this.rolesService.getRoles().subscribe({
      next: (response: Role[]) => {
        this.originalRoles = response;
        this.totalItems = this.originalRoles.length;
        this.applyFilters();
        this.loading = false;
      },
      error: (error: any) => {
        console.error('Error loading roles:', error);
        this.loading = false;
      }
    });
  }

  onSearch(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onItemsPerPageChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.applyFilters();
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.applyFilters();
    }
  }

  sort(column: string): void {
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

  private applyFilters(): void {
    let filteredRoles = [...this.originalRoles];

    // Apply search
    if (this.searchTerm) {
      const searchLower = this.searchTerm.toLowerCase();
      filteredRoles = filteredRoles.filter(role =>
        role.name.toLowerCase().includes(searchLower) ||
        role.description.toLowerCase().includes(searchLower)
      );
    }

    // Apply sort
    filteredRoles.sort((a, b) => {
      if (this.sortConfig.column === 'no') {
        // Get the original indices
        const aIndex = this.originalRoles.indexOf(a);
        const bIndex = this.originalRoles.indexOf(b);
        // Sort by index
        return this.sortConfig.direction === 'asc' 
          ? aIndex - bIndex
          : bIndex - aIndex;
      }

      const aValue = String(a[this.sortConfig.column]).toLowerCase();
      const bValue = String(b[this.sortConfig.column]).toLowerCase();
      return this.sortConfig.direction === 'asc'
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    });

    this.totalItems = filteredRoles.length;
    
    // Apply pagination
    const start = this.startIndex;
    const end = this.startIndex + this.itemsPerPage;
    this.roles = filteredRoles.slice(start, end);
  }

  editRole(role: Role): void {
    this.router.navigate(['edit', role._id], { relativeTo: this.route });
  }

  deleteRole(role: Role): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: this.languageService.translate('roles.delete.title'),
        message: this.languageService.translate('roles.delete.message', { name: role.name }),
        confirmText: this.languageService.translate('common.actions.delete'),
        cancelText: this.languageService.translate('common.actions.cancel')
      }
    });

    dialogRef.afterClosed().subscribe(async (confirmed: boolean) => {
      if (confirmed) {
        try {
          await this.rolesService.deleteRole(role._id).toPromise();
          this.notificationService.success(
            this.languageService.translate('roles.messages.deleteSuccess')
          );
          this.loadRoles(); // Refresh the list
        } catch (error: any) {
          console.error('Error deleting role:', error);
          this.notificationService.error(
            this.languageService.translate('common.status.error')
          );
        }
      }
    });
  }
} 